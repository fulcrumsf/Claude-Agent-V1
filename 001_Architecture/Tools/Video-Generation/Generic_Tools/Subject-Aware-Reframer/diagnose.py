#!/usr/bin/env python3
"""Gate 2 detection/tracking diagnostics. No camera planner or vertical renderer."""
from __future__ import annotations

import argparse
import bisect
import errno
import hashlib
import importlib.metadata
import json
import math
import os
import resource
import shutil
import socket
import subprocess
import time
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"
COLORS = {0: (100, 240, 100), 21: (255, 180, 60)}
ANIMAL_CLASSES = frozenset(range(14, 24))


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_json(path, data):
    with Path(path).open("x") as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write("\n")


def disk_check(path):
    if shutil.disk_usage(path).free < 10 * 1024**3:
        raise RuntimeError("Less than 10 GiB free disk; stopping without deleting anything")


def offline_check():
    """Fail before loading third-party code if the OS permits even a loopback connection."""
    for name, value in {"YOLO_AUTOINSTALL": "0", "YOLO_OFFLINE": "1",
                        "ULTRALYTICS_SAFE_LOAD": "1", "TORCH_FORCE_WEIGHTS_ONLY_LOAD": "1"}.items():
        if os.environ.get(name) != value:
            raise RuntimeError(f"Use run_offline.py; required {name}={value}")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            result = sock.connect_ex(("127.0.0.1", 9))
    except OSError as exc:
        result = exc.errno
    if result not in (errno.EPERM, errno.EACCES):
        raise RuntimeError(f"OS network-denial check failed (errno={result})")
    return {"os_network_denial": True, "loopback_errno": result, "clean_environment_launcher": True}


def validate_shots(shots):
    if not shots or len({s["id"] for s in shots}) != len(shots):
        raise ValueError("Shot IDs must be nonempty and unique")
    for i, shot in enumerate(shots):
        if shot["end_pts"] <= shot["start_pts"]:
            raise ValueError("Shot has an empty or reversed interval")
        if i and shots[i - 1]["end_pts"] != shot["start_pts"]:
            raise ValueError("Shot intervals must be contiguous")


def shot_for_pts(shots, pts):
    for shot in shots:
        if shot["start_pts"] <= pts < shot["end_pts"]:
            return shot
    raise ValueError(f"Timestamp {pts} is outside the approved interval")


def load_config(path):
    cfg = json.loads(Path(path).read_text())
    validate_shots(cfg["shots"])
    source = Path(cfg["source"]).resolve(strict=True)
    if sha256(source) != cfg["source_sha256"]:
        raise ValueError("Source master fingerprint changed; reapprove source before analysis")
    cfg["source"] = str(source)
    if not set(cfg["classes"]) <= ({0} | ANIMAL_CLASSES) or 0 not in cfg["classes"]:
        raise ValueError("Gate 2 tracking is restricted to people and COCO animal classes")
    if cfg["inference_size"] > 1280 or not 0 < cfg["confidence"] < 1:
        raise ValueError("Invalid inference configuration")
    return cfg


def probe(cfg):
    args = [FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_streams", "-show_frames",
            "-show_entries", "stream=width,height,time_base:frame=pts", "-of", "json", cfg["source"]]
    info = json.loads(subprocess.run(args, capture_output=True, check=True, text=True).stdout)
    stream = info["streams"][0]
    if stream["time_base"] != cfg["time_base"]:
        raise ValueError("Source time base differs from approved configuration")
    lo, hi = cfg["shots"][0]["start_pts"], cfg["shots"][-1]["end_pts"]
    frames = [{"source_frame": i, "pts": f["pts"]} for i, f in enumerate(info["frames"]) if lo <= f["pts"] < hi]
    if len(frames) != cfg["expected_source_frames"]:
        raise ValueError(f"Expected {cfg['expected_source_frames']} source frames; got {len(frames)}")
    pts = [f["pts"] for f in frames]
    if any(b <= a for a, b in zip(pts, pts[1:])):
        raise ValueError("Source presentation timestamps are not strictly increasing")
    if any(s["start_pts"] not in pts for s in cfg["shots"]):
        raise ValueError("A shot boundary does not coincide with a decoded source frame")
    return stream, frames


def decode(cfg, stream):
    import numpy as np
    lo, hi = cfg["shots"][0]["start_pts"], cfg["shots"][-1]["end_pts"]
    args = [FFMPEG, "-nostdin", "-v", "error", "-noautorotate", "-i", cfg["source"],
            "-an", "-vf", f"trim=start_pts={lo}:end_pts={hi}", "-fps_mode", "passthrough",
            "-f", "rawvideo", "-pix_fmt", "bgr24", "pipe:1"]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    count = stream["width"] * stream["height"] * 3
    finished = False
    try:
        while True:
            raw = proc.stdout.read(count)
            if not raw:
                break
            if len(raw) != count:
                raise RuntimeError("Incomplete decoded frame")
            yield np.frombuffer(raw, dtype=np.uint8).reshape(stream["height"], stream["width"], 3)
        error = proc.stderr.read().decode()
        if proc.wait() != 0:
            raise RuntimeError(f"Source decode failed: {error}")
        finished = True
    finally:
        if not finished and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        proc.stdout.close()
        proc.stderr.close()


def load_model():
    security = offline_check()
    versions = {}
    for line in (ROOT / "requirements-approved.txt").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        name, expected = line.split("==")
        versions[name] = importlib.metadata.version(name)
        if versions[name] != expected:
            raise RuntimeError(f"Unapproved installed version: {name}=={versions[name]}")
    import torch
    torch.set_num_threads(4)
    torch.set_num_interop_threads(2)
    from ultralytics import YOLO, settings
    from ultralytics.nn.tasks import _SafeLoad
    if not _SafeLoad.SUPPORTED:
        raise RuntimeError("Restricted model loading unavailable; no unsafe fallback permitted")
    settings.update({k: False for k, v in settings.items() if isinstance(v, bool)})
    receipt = json.loads((ROOT / "Models/Model-Receipt-v1.json").read_text())
    model_path = (ROOT / "Models" / receipt["file"]).resolve(strict=True)
    if model_path.parent != (ROOT / "Models").resolve() or sha256(model_path) != receipt["sha256"]:
        raise ValueError("Model fingerprint mismatch")
    model = YOLO(str(model_path), task="detect")
    if model.names.get(0) != "person" or model.names.get(21) != "bear":
        raise ValueError("Model class mapping does not match the approved COCO classes")
    security.update(restricted_loading=True, force_weights_only=True,
                    auto_install=False, integrations_enabled=False)
    return model, {"security": security, "packages": versions, "model": receipt,
                   "mps_available": torch.backends.mps.is_available(), "torch_threads": torch.get_num_threads()}


def new_tracker():
    # The pinned API takes a buffer in processed frames (24 is about one second).
    from ultralytics.trackers.byte_tracker import BYTETracker
    return BYTETracker(SimpleNamespace(track_high_thresh=0.25, track_low_thresh=0.1,
                                      new_track_thresh=0.25, track_buffer=24,
                                      match_thresh=0.8, fuse_score=True))


def predict(model, frame, cfg, device):
    return model.predict(frame, classes=cfg["classes"], conf=cfg["confidence"],
                         imgsz=cfg["inference_size"], device=device, verbose=False,
                         quantize=32, save=False)[0]


def suppress_duplicate_animals(data, threshold=0.7):
    """Keep the strongest overlapping animal label; retain original raw labels in the cache."""
    import numpy as np
    order = list(np.argsort(-data[:, 4]))
    keep = []
    while order:
        i = order.pop(0)
        keep.append(i)
        remaining = []
        a = data[i, :4]
        for j in order:
            b = data[j, :4]
            overlap = np.maximum(0, np.minimum(a[2:], b[2:]) - np.maximum(a[:2], b[:2])).prod()
            union = max(0, a[2] - a[0]) * max(0, a[3] - a[1]) + max(0, b[2] - b[0]) * max(0, b[3] - b[1]) - overlap
            if not union or overlap / union <= threshold:
                remaining.append(j)
        order = remaining
    return keep


def family_tracks(boxes, frame, trackers, shot, seen, frame_index):
    """Separate people/animal association. Species labels never determine subject family identity."""
    import numpy as np
    from ultralytics.engine.results import Boxes
    output = []
    for family, family_code in (("person", 0), ("animal", 1)):
        mask = boxes.cls == 0 if family == "person" else np.isin(boxes.cls, list(ANIMAL_CLASSES))
        data = boxes.data[mask].copy()
        if len(data) and family == "animal":
            data = data[suppress_duplicate_animals(data)]
        actual_classes = data[:, 5].copy()
        data[:, 5] = family_code
        tracked = trackers[family].update(Boxes(data, frame.shape[:2]), frame)
        for row in tracked:
            identity = f"{shot['id']}:{family}:{int(row[4])}"
            prior, streak = seen.get(identity, (-2, 0))
            streak = streak + 1 if prior == frame_index - 1 else 1
            seen[identity] = frame_index, streak
            # Four consecutive frames suppress brief person false positives on moving animals.
            confirmed = streak >= 4
            source_class = int(actual_classes[int(row[7])])
            output.append({"id": identity, "local_id": int(row[4]), "family": family,
                           "confirmed": confirmed, "consecutive_observations": streak,
                           "class_id": source_class, "bbox_xyxy": [round(float(v), 3) for v in row[:4]],
                           "confidence": round(float(row[5]), 5)})
    return output


def audit_classes(cfg, out, device):
    """Inspect every COCO class at selected frames to explain class-filter misses."""
    out = Path(out).resolve()
    disk_check(out.parent)
    out.mkdir(exist_ok=False)
    model, runtime = load_model()
    stream, frames = probe(cfg)
    picks = set()
    for shot in cfg["shots"]:
        ids = [i for i, f in enumerate(frames) if shot["start_pts"] <= f["pts"] < shot["end_pts"]]
        picks.update(ids[round((len(ids) - 1) * f)] for f in (0, 0.25, 0.5, 0.75, 1))
    observations = []
    for i, frame in enumerate(decode(cfg, stream)):
        if i not in picks:
            continue
        result = predict(model, frame, {**cfg, "classes": list(model.names), "confidence": 0.05}, device)
        row = {**frames[i], "source_seconds": float(frames[i]["pts"] * Fraction(cfg["time_base"])),
               "shot": shot_for_pts(cfg["shots"], frames[i]["pts"])["id"],
               "detections": [{"bbox_xyxy": [round(float(x), 3) for x in b[:4]],
                               "confidence": round(float(b[4]), 5), "class_id": int(b[5]),
                               "class_name": model.names[int(b[5])]} for b in result.boxes.cpu().data.tolist()]}
        observations.append(row)
        print(json.dumps(row), flush=True)
    save_json(out / "All-Class-Audit-v1.json", {"stage": "diagnostic_class_audit_only", "runtime": runtime,
        "config": cfg, "audit_confidence": 0.05, "observations": observations,
        "note": "Explains filtering and misclassification; does not relabel subjects or change the baseline."})


def analyze(cfg, out, device):
    out = Path(out).resolve()
    disk_check(out.parent)
    out.mkdir(exist_ok=False)
    started = time.monotonic()
    save_json(out / "Run-Started.json", {"gate": 2, "completion_marker": "Run-Report-v1.json",
                                       "device": device, "config": cfg})
    protected = {p: sha256(p) for p in cfg["protected_media"]}
    model, runtime = load_model()
    stream, frames = probe(cfg)
    records, tracker, previous_shot, seen = [], None, None, {}
    tb = Fraction(cfg["time_base"])
    for i, frame in enumerate(decode(cfg, stream)):
        if i >= len(frames):
            raise RuntimeError("Decoder produced extra source frames")
        meta = frames[i]
        shot = shot_for_pts(cfg["shots"], meta["pts"])
        if shot["id"] != previous_shot:
            tracker = {f: new_tracker() for f in ("person", "animal")} if cfg.get("family_tracking") else new_tracker()
            previous_shot, seen = shot["id"], {}
        result = predict(model, frame, cfg, device)
        boxes = result.boxes.cpu().numpy()
        detections = [{"bbox_xyxy": [round(float(v), 3) for v in row[:4]],
                       "confidence": round(float(row[4]), 5), "class_id": int(row[5])}
                      for row in boxes.data]
        if cfg.get("family_tracking"):
            tracks = family_tracks(boxes, frame, tracker, shot, seen, i)
        else:
            tracked = tracker.update(boxes, frame)
            tracks = [{"id": f"{shot['id']}:{int(row[4])}", "local_id": int(row[4]),
                       "bbox_xyxy": [round(float(v), 3) for v in row[:4]],
                       "confidence": round(float(row[5]), 5), "class_id": int(row[6])}
                      for row in tracked]
        records.append({**meta, "source_seconds": float(meta["pts"] * tb), "shot": shot["id"],
                        "detections": detections, "tracks": tracks})
        if i % 48 == 0:
            disk_check(out)
            print(f"Analyzed {i + 1}/{len(frames)} source frames ({shot['id']})", flush=True)
    if len(records) != len(frames):
        raise RuntimeError(f"Decoded {len(records)} frames; expected {len(frames)}")
    cache = {"schema_version": 1, "stage": "detection_tracking_only", "config": cfg,
             "stream": stream, "runtime": runtime, "frames": records}
    save_json(out / "Detections-And-Tracks-v1.json", cache)
    report = {"stage": "gate_2", "device": device, "source_frames": len(records),
              "analysis_seconds": round(time.monotonic() - started, 3), "shots": []}
    for shot in cfg["shots"]:
        selected = [r for r in records if r["shot"] == shot["id"]]
        report["shots"].append({"id": shot["id"], "frames": len(selected),
            "raw_person_present_frames": sum(any(d["class_id"] == 0 for d in r["detections"]) for r in selected),
            "raw_bear_present_frames": sum(any(d["class_id"] == 21 for d in r["detections"]) for r in selected),
            "raw_animal_present_frames": sum(any(d["class_id"] in ANIMAL_CLASSES for d in r["detections"]) for r in selected),
            "confirmed_animal_present_frames": sum(any(t.get("family") == "animal" and t.get("confirmed") for t in r["tracks"]) for r in selected),
            "person_track_ids": sorted({t["id"] for r in selected for t in r["tracks"] if t["class_id"] == 0}),
            "bear_track_ids": sorted({t["id"] for r in selected for t in r["tracks"] if t["class_id"] == 21}),
            "confirmed_animal_track_ids": sorted({t["id"] for r in selected for t in r["tracks"] if t.get("family") == "animal" and t.get("confirmed")})})
    report["metric_note"] = "Presence counts describe model output, not measured accuracy. Human review is required."
    render_debug(cache, out)
    after = {p: sha256(p) for p in protected}
    report["protected_media_unchanged"] = after == protected
    report["source_hash_unchanged"] = sha256(cfg["source"]) == cfg["source_sha256"]
    report["protected_media_sha256"] = after
    if not report["protected_media_unchanged"] or not report["source_hash_unchanged"]:
        raise RuntimeError("Protected media fingerprint changed during analysis")
    report["status"] = "diagnostics_complete_awaiting_human_review"
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    report["peak_process_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    save_json(out / "Run-Report-v1.json", report)
    print(json.dumps(report, indent=2), flush=True)


def output_indices(records, start_pts, end_pts, time_base, fps=30):
    tb = Fraction(time_base)
    start, duration = start_pts * tb, (end_pts - start_pts) * tb
    pts = [r["pts"] for r in records]
    count = math.ceil(duration * fps)
    return [max(0, bisect.bisect_right(pts, (start + Fraction(i, fps)) / tb) - 1) for i in range(count)]


def annotated(frame, record, target_width=1280):
    import cv2
    import numpy as np
    height = round(frame.shape[0] * target_width / frame.shape[1])
    pic = cv2.resize(frame, (target_width, height), interpolation=cv2.INTER_AREA)
    scale = target_width / frame.shape[1]
    # Thin grey boxes: raw detections. Colored boxes: active track identities.
    for d in record["detections"]:
        p = [int(v * scale) for v in d["bbox_xyxy"]]
        cv2.rectangle(pic, tuple(p[:2]), tuple(p[2:]), (180, 180, 180), 1)
    for t in record["tracks"]:
        if not t.get("confirmed", True):
            continue
        x1, y1, x2, y2 = [int(v * scale) for v in t["bbox_xyxy"]]
        family = t.get("family", "person" if t["class_id"] == 0 else "animal")
        color = COLORS[0 if family == "person" else 21]
        cv2.rectangle(pic, (x1, y1), (x2, y2), color, 2)
        text = f"{family} #{t['local_id']} {t['confidence']:.2f}"
        cv2.putText(pic, text, (max(0, min(x1, target_width - 180)), max(20, y1 - 7)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(pic, text, (max(0, min(x1, target_width - 180)), max(20, y1 - 7)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv2.LINE_AA)
    canvas = np.zeros((height + 80, target_width, 3), dtype=np.uint8)
    canvas[:height] = pic
    for y, text in [(height + 27, f"{record['shot']} | master {record['source_seconds']:.3f}s | frame {record['source_frame']}"),
                    (height + 56, "Gate 2: detections + tracks only | grey: detection | green: person | blue: animal")]:
        cv2.putText(canvas, text, (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (235, 235, 235), 1, cv2.LINE_AA)
    return canvas


def render_debug(cache, out):
    import cv2
    import numpy as np
    cfg, records, stream = cache["config"], cache["frames"], cache["stream"]
    lo, hi = cfg["shots"][0]["start_pts"], cfg["shots"][-1]["end_pts"]
    indices = output_indices(records, lo, hi, cfg["time_base"])
    counts = {i: indices.count(i) for i in set(indices)}
    picks = []
    for shot in cfg["shots"]:
        ids = [i for i, r in enumerate(records) if r["shot"] == shot["id"]]
        picks.extend(ids[round((len(ids) - 1) * f)] for f in (0, 0.25, 0.5, 0.75, 1))
    width, height = 1280, round(stream["height"] * 1280 / stream["width"]) + 80
    duration = len(indices) / 30
    partial, final = out / "Part-3-Detection-Debug-v1.incomplete.mp4", out / "Part-3-Detection-Debug-v1.mp4"
    if partial.exists() or final.exists():
        raise FileExistsError("Debug output already exists")
    args = [FFMPEG, "-nostdin", "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "bgr24",
            "-s", f"{width}x{height}", "-r", "30", "-i", "pipe:0", "-ss", str(float(lo * Fraction(cfg["time_base"]))),
            "-t", str(float((hi - lo) * Fraction(cfg["time_base"]))), "-i", cfg["source"],
            "-map", "0:v:0", "-map", "1:a:0", "-af", "asetpts=PTS-STARTPTS,apad",
            "-t", str(duration), "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k", "-movflags", "+faststart", str(partial)]
    thumbs = {}
    with (out / "FFmpeg-Encode.log").open("x") as log:
        encoder = subprocess.Popen(args, stdin=subprocess.PIPE, stderr=log)
        try:
            n = 0
            for i, frame in enumerate(decode(cfg, stream)):
                pic = annotated(frame, records[i])
                if i in picks:
                    thumbs[i] = cv2.resize(pic, (480, 300), interpolation=cv2.INTER_AREA)
                raw = pic.tobytes()
                for _ in range(counts.get(i, 0)):
                    encoder.stdin.write(raw)
                    n += 1
            encoder.stdin.close()
            if encoder.wait() != 0 or n != len(indices):
                raise RuntimeError("Diagnostic encode failed; retained incomplete output and log")
        finally:
            if encoder.poll() is None:
                encoder.terminate()
                encoder.wait()
    partial.rename(final)
    sheet = np.zeros((math.ceil(len(picks) / 3) * 300, 3 * 480, 3), dtype=np.uint8)
    for j, i in enumerate(picks):
        sheet[(j // 3) * 300:(j // 3 + 1) * 300, (j % 3) * 480:(j % 3 + 1) * 480] = thumbs[i]
    contact = out / "Part-3-Detection-Contact-Sheet-v1.jpg"
    if contact.exists() or not cv2.imwrite(str(contact), sheet, [cv2.IMWRITE_JPEG_QUALITY, 95]):
        raise RuntimeError("Could not create new contact sheet")
    save_json(out / "Debug-Timeline-v1.json", {"fps": 30, "frames": len(indices), "duration_seconds": duration,
        "source_record_per_output_frame": indices, "contact_sheet_source_records": picks,
        "tail_padding_seconds": duration - float((hi - lo) * Fraction(cfg["time_base"]))})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["runtime", "analyze", "audit-classes"])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--device", choices=["cpu", "mps"], default="cpu")
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.command in ("analyze", "audit-classes"):
        if args.out is None:
            parser.error("analyze requires --out pointing to a new run directory")
        (analyze if args.command == "analyze" else audit_classes)(cfg, args.out, args.device)
    else:
        model, report = load_model()
        stream, frames = probe(cfg)
        generator = decode(cfg, stream)
        try:
            frame = next(generator)
            started = time.monotonic()
            result = predict(model, frame, cfg, args.device)
        finally:
            generator.close()
        report.update(device=args.device, source_frames=len(frames),
                      first_frame_detections=result.boxes.cpu().data.tolist(),
                      first_inference_seconds=round(time.monotonic() - started, 3))
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
