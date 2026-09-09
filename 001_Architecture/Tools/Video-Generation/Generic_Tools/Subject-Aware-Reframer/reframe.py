#!/usr/bin/env python3
"""Local, versioned plan/render interface for Gate 3. No automatic clip selection."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import re
import shutil
from pathlib import Path

from camera_plan import build_plan, settings_for
from diagnose import ROOT, disk_check, offline_check, probe, save_json, sha256


def read_json(path):
    return json.loads(Path(path).read_text(), parse_constant=lambda s: (_ for _ in ()).throw(ValueError(f"Nonfinite JSON: {s}")))


def resource_check(output_root):
    disk_check(output_root)
    seen, total = set(), 0
    for root in (ROOT, Path(output_root)):
        for path in root.rglob("*"):
            if path.is_file():
                st = path.stat()
                identity = (st.st_dev, st.st_ino)
                if identity not in seen:
                    total += st.st_blocks * 512
                    seen.add(identity)
    if total >= 5 * 1024**3:
        raise RuntimeError("The 5 GiB experiment budget is exhausted; preserve outputs and review scope")
    return {"allocated_bytes": total, "free_bytes": shutil.disk_usage(output_root).free}


def checked_file(path, expected):
    path = Path(path).resolve(strict=True)
    if not path.is_file() or sha256(path) != expected:
        raise ValueError(f"File fingerprint changed: {path}")
    return path


def load_job(path):
    path = Path(path).resolve(strict=True)
    job = read_json(path)
    required = {"schema_version", "job_id", "approval", "source", "source_sha256",
                "analysis", "analysis_sha256", "profile_file", "profile_sha256",
                "output_root", "output_stem", "output", "variants", "protected_media"}
    if set(job) != required or job["schema_version"] != 1:
        raise ValueError("Unknown or missing job fields; expected Job Contract v1")
    if job["approval"].get("gate") != 3 or job["approval"].get("approved") is not True:
        raise ValueError("A Gate 3 approval record is required")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", job["job_id"]) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", job["output_stem"]):
        raise ValueError("Job ID and output stem must be safe filename components")
    for name in ("source", "analysis", "profile_file", "output_root"):
        if not Path(job[name]).is_absolute():
            raise ValueError(f"{name} must be an absolute local path")
    source = checked_file(job["source"], job["source_sha256"])
    analysis = checked_file(job["analysis"], job["analysis_sha256"])
    profiles = read_json(checked_file(job["profile_file"], job["profile_sha256"]))
    cache = read_json(analysis)
    if profiles["schema_version"] != 1 or cache["schema_version"] != 1:
        raise ValueError("Unsupported profile or analysis schema")
    if Path(cache["config"]["source"]).resolve() != source or cache["config"]["source_sha256"] != job["source_sha256"]:
        raise ValueError("The analysis belongs to a different source")
    output = job["output"]
    if set(output) != {"width", "height", "fps"} or any(type(v) is not int for v in output.values()):
        raise ValueError("Output requires integer width, height, fps")
    if not (180 <= output["width"] <= 1080 and output["width"] < output["height"] <= 1920
            and output["width"] % 2 == output["height"] % 2 == 0 and output["fps"] == 30):
        raise ValueError("Gate 3 supports even vertical dimensions up to 1080x1920 at 30 fps")
    if not 1 <= len(job["variants"]) <= 3:
        raise ValueError("Choose one through three variants")
    for name, variant in job["variants"].items():
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", name) or set(variant) != {"profile", "settings", "shot_overrides"}:
            raise ValueError("Invalid variant name or fields")
        settings_for(profiles["defaults"], profiles["profiles"][variant["profile"]], variant["settings"])
    for media, fingerprint in job["protected_media"].items():
        checked_file(media, fingerprint)
    root = Path(job["output_root"]).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Output root must be an existing directory")
    return path, job, cache, profiles


def new_output(path, job):
    out = Path(path).resolve()
    root = Path(job["output_root"]).resolve(strict=True)
    if out.parent != root:
        raise ValueError("A run must be a direct new child of the declared production output root")
    resource_check(root)
    out.mkdir(exist_ok=False)
    return out


def verify_cache(cache):
    stream, frames = probe(cache["config"])
    if stream != cache["stream"] or len(frames) != len(cache["frames"]):
        raise ValueError("Cached geometry/count differs from source")
    for current, cached in zip(frames, cache["frames"]):
        if any(current[k] != cached[k] for k in ("pts", "source_frame")):
            raise ValueError("Cached source timing is inconsistent")


def create_plan(job_path, out):
    job_path, job, cache, profiles = load_job(job_path)
    verify_cache(cache)
    out = new_output(out, job)
    save_json(out/"Run-Started-v1.json", {"job_id": job["job_id"], "gate": 3,
              "completion_marker": "Run-Report-v1.json", "job": job})
    variants = {}
    for name, variant in job["variants"].items():
        settings = settings_for(profiles["defaults"], profiles["profiles"][variant["profile"]], variant["settings"])
        variants[name] = build_plan(cache, settings, variant["shot_overrides"], job["output"])
    plan = {"schema_version": 1, "stage": "camera_plan", "job_file": str(job_path),
            "job_sha256": sha256(job_path), "job": job, "variants": variants,
            "transition_style": "cuts between subjects/layouts; smoothed pan and zoom within a crop",
            "limitations": "Visual tracking plus configured switching; no narration or semantic identity recognition."}
    validate_plan(plan, cache)
    save_json(out/"Crop-Plan-v1.json", plan)
    return plan, cache, out


def validate_plan(plan, cache):
    from camera_plan import area, intersection
    width, height = cache["stream"]["width"], cache["stream"]["height"]
    for variant in plan["variants"].values():
        frames, output = variant["frames"], variant["output"]
        if len(frames) != len(variant["source_record_per_output_frame"]):
            raise ValueError("Plan frame mapping length mismatch")
        for i, f in enumerate(frames):
            source = cache["frames"][variant["source_record_per_output_frame"][i]]
            if f["output_frame"] != i or f["source_pts"] != source["pts"] or f["shot"] != source["shot"]:
                raise ValueError("Plan frame/shot mapping is inconsistent")
            box = f["crop_xyxy"]
            if not all(math.isfinite(v) for v in box) or not (0 <= box[0] < box[2] <= width+1e-5 and 0 <= box[1] < box[3] <= height+1e-5):
                raise ValueError("Camera leaves source bounds")
            if f["layout"] == "crop":
                if abs((box[2]-box[0])/(box[3]-box[1])-output["width"]/output["height"]) > 1e-5:
                    raise ValueError("Incorrect crop aspect ratio")
                if intersection(box, f["focus"]["box"])/area(f["focus"]["box"]) < 0.999:
                    raise ValueError("Selected subject is clipped")
            elif f["layout"] != "fit_blur" or box != [0, 0, width, height]:
                raise ValueError("Invalid group layout")
            if i and f["shot"] != frames[i-1]["shot"] and not f["cut"]:
                raise ValueError("Camera state crosses a source cut")


def verify_packages():
    for line in (ROOT/"requirements-approved.txt").read_text().splitlines():
        if line and not line.startswith("#"):
            name, expected = line.split("==")
            if importlib.metadata.version(name) != expected:
                raise RuntimeError(f"Unapproved installed package: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["plan", "render", "reframe"])
    parser.add_argument("--job", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    security = offline_check()
    verify_packages()
    if args.command in {"plan", "reframe"}:
        if args.job is None or args.plan is not None:
            parser.error("plan/reframe requires --job and no --plan")
        plan, cache, out = create_plan(args.job, args.out)
    else:
        if args.plan is None or args.job is not None:
            parser.error("render requires --plan and no --job")
        plan = read_json(args.plan)
        checked_file(plan["job_file"], plan["job_sha256"])
        _, job, cache, _ = load_job(plan["job_file"])
        if plan["job"] != job:
            raise ValueError("Plan job differs from the approved job file")
        verify_cache(cache)
        validate_plan(plan, cache)
        out = new_output(args.out, job)
        save_json(out/"Crop-Plan-v1.json", plan)
        save_json(out/"Run-Started-v1.json", {"gate": 3, "rendered_plan_sha256": sha256(args.plan),
                  "completion_marker": "Run-Report-v1.json", "job": job})
    if args.command != "plan":
        from render_reframe import render
        render(plan, cache, out, security)
    else:
        print(json.dumps({"status": "plan_ready", "path": str(out/"Crop-Plan-v1.json")}))


if __name__ == "__main__":
    main()
