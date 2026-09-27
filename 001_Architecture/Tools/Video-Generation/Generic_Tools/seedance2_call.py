#!/usr/bin/env python3
"""GLOBAL gate + runner for EVERY Seedance 2 video call (2.0 standard, 2.0 Fast, 2.0 Mini) in every channel/pipeline.
Locked 2026-09-20 (Tony): anytime Seedance 2 runs, it follows the winning process. Not for anything below Seedance 2 (start/end frame only, never references). Enforced only for channels enabled in seedance2_gate_config.json.

The reference list is BUILT HERE from the clip's Data/Video_Reference_Set.json (final approved, LABELED assets), never hand-listed:
  {"storyboard": "Storyboard_v3.png",
   "environment_sheet": "Character_Sheets/Environment_Sheet_v2.png",
   "character_sheets": [{"file": "..._LabeledClean.png", "label": "BICYCLE COURIER"}],
   "prop_sheets": [{"file": "...", "label": "..."}],
   "not_sent": [{"glob": "Character_Sheets/*_v1*", "reason": "superseded version"}]}
Upload order is fixed: storyboard, environment sheet, character/creature sheets, prop sheets.

KEYFRAME FALLBACK (--keyframes, Tony 2026-09-26): used only after a storyboard-reference video tiled/split and an edge crop could not
save it. The storyboard is NOT sent (it stays saved). Its panels, cut out by Channels/Neon_Parcel/extract_storyboard_keyframes.py,
are listed in the manifest as "keyframes": ["Storyboard_v3_Keyframe_01.png", ...]. Slots are filled in priority order up to the
provider's reference-image limit (Kie Seedance 2 / Mini: 9): all keyframes, then character/creature sheets, then the environment
sheet, then prop sheets. Anything that doesn't fit is listed as dropped for the slot limit. The prompt must say
"Use @Image 1 through @Image N as keyframes in this order" (official Seedance keyframe wording).

MISSING-SHEET RULE: a character or prop sheet may be left out ONLY if none was built for this clip. The tool scans the clip folder for
every file with 'sheet' in its name (skipping Archived/, Rejected/, Panels/); each must either be sent or matched by a 'not_sent' entry
with a reason (superseded, wrong clip, ...). An unaccounted sheet blocks the call. Storyboard and environment sheet are always required.

SCALE HARD STOP (Tony, 2026-09-26; channels listed in SCALE_CHECK_CHANNELS): the storyboard must have a PASSING measured scale check
(Channels/Neon_Parcel/check_storyboard_scale.py -> Data/Scale_Check_<storyboard stem>.json) made on this exact storyboard file
(sha256 match). Missing, failed or stale = blocked, with the failures printed as a warning. Applies in --keyframes mode too.

Also blocks (no paid call) if: a sheet is not the labeled version, a printed label is not quoted in the prompt, the @Image tag check fails
(check_seedance_prompt_refs.py), or the five sections (Camera Lock, Scene Continuity, Action Timeline, Audio, Hard Constraints) are out of order.

Usage: python3 seedance2_call.py <clip_dir> <prompt.md> --channel Neon_Parcel --version v8 --shot-id ID --out Data/X.mp4 [--model mini|standard|fast]
       [--resolution 480p] [--duration 14] [--manifest path] [--dry-run] [--retry-reason tony_revision:...]
Execution is wired and tested for --model mini (kie_market_api.py). standard/fast go through kie-cli and are UNTESTED here."""
import argparse, fnmatch, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Character-Sheet-Generation/scripts")
from check_seedance_prompt_refs import lint  # noqa: E402

SCALE_CHECK_CHANNELS = {"Neon_Parcel"}
SECTIONS = ["1. CAMERA LOCK", "2. SCENE CONTINUITY", "3. ACTION TIMELINE", "4. AUDIO", "5. HARD CONSTRAINTS"]
LABEL_HINTS = ("labeled", "titled", "environment_sheet")
SKIP_DIRS = {"archived", "rejected", "panels"}
IMG = {".png", ".jpg", ".jpeg", ".webp"}


def channel_enabled(channel: str) -> bool:
    cfg = json.loads((HERE / "seedance2_gate_config.json").read_text())["channels"]
    if channel not in cfg:
        raise SystemExit(f"BLOCKED: channel '{channel}' is not listed in seedance2_gate_config.json. Add it (true/false) first.")
    return bool(cfg[channel])


def load_manifest(clip: Path, override):
    m = Path(override) if override else clip / "Data" / "Video_Reference_Set.json"
    if not m.is_file():
        raise SystemExit(f"BLOCKED: {m} is missing. Record the final approved assets there first.")
    return json.loads(m.read_text())


def build_refs(clip: Path, d: dict):
    for k in ("storyboard", "environment_sheet"):
        if not d.get(k):
            raise SystemExit(f"BLOCKED: manifest has no '{k}'. Storyboard and environment sheet are always required.")
    items = [("storyboard", d["storyboard"], None), ("environment sheet", d["environment_sheet"], None)]
    items += [("character/creature sheet", c["file"], c["label"]) for c in d.get("character_sheets", [])]
    items += [("prop sheet", c["file"], c["label"]) for c in d.get("prop_sheets", [])]
    for role, f, _ in items:
        if not (clip / f).is_file():
            raise SystemExit(f"BLOCKED: {role} file missing: {f}")
        if role.endswith("sheet") and not any(h in f.lower() for h in LABEL_HINTS):
            raise SystemExit(f"BLOCKED: {role} '{f}' is not the final LABELED version (name must contain Labeled/Titled). Never send a naked sheet.")
    return items


def build_keyframe_refs(clip: Path, d: dict, limit: int):
    """Keyframe fallback: keyframes > character sheets > environment sheet > prop sheets, capped at the reference limit."""
    kfs = d.get("keyframes") or []
    if not kfs:
        raise SystemExit("BLOCKED: --keyframes needs a 'keyframes' list in the manifest (run extract_storyboard_keyframes.py first).")
    if len(kfs) > limit:
        raise SystemExit(f"BLOCKED: {len(kfs)} keyframes exceed the {limit}-image reference limit.")
    ranked = [("keyframe", f, None) for f in kfs]
    ranked += [("character/creature sheet", c["file"], c["label"]) for c in d.get("character_sheets", [])]
    if d.get("environment_sheet"):
        ranked.append(("environment sheet", d["environment_sheet"], None))
    ranked += [("prop sheet", c["file"], c["label"]) for c in d.get("prop_sheets", [])]
    for role, f, _ in ranked:
        if not (clip / f).is_file():
            raise SystemExit(f"BLOCKED: {role} file missing: {f}")
        if role.endswith("sheet") and not any(h in f.lower() for h in LABEL_HINTS):
            raise SystemExit(f"BLOCKED: {role} '{f}' is not the final LABELED version (name must contain Labeled/Titled). Never send a naked sheet.")
    return ranked[:limit], ranked[limit:]


def scale_gate(clip: Path, d: dict):
    """Hard stop unless Data/Scale_Check_<storyboard stem>.json passed on this exact storyboard. Returns failure strings."""
    import hashlib
    sb = clip / d.get("storyboard", "")
    rep = clip / "Data" / f"Scale_Check_{sb.stem}.json"
    fix = "run Channels/Neon_Parcel/check_storyboard_scale.py <clip_dir> and fix the storyboard until it passes"
    if not rep.is_file():
        return [f"SCALE: no measured scale check for {sb.name} ({fix})"]
    r = json.loads(rep.read_text())
    if r.get("storyboard_sha256") != hashlib.sha256(sb.read_bytes()).hexdigest():
        return [f"SCALE: {rep.name} was made on a different version of {sb.name} ({fix})"]
    if not r.get("passed"):
        return [f"SCALE WARNING: {x}" for x in r.get("failures", [])] + [f"SCALE: storyboard failed the scale check ({fix})"]
    return []


def unaccounted_sheets(clip: Path, d: dict, items, dropped=()):
    sent = {f for _, f, _ in items} | {f for _, f, _ in dropped}; globs = [g["glob"] for g in d.get("not_sent", []) if g.get("reason")]
    out = []
    for p in clip.rglob("*"):
        if p.suffix.lower() not in IMG or "sheet" not in p.name.lower():
            continue
        rel = p.relative_to(clip).as_posix()
        if any(part.lower() in SKIP_DIRS for part in p.relative_to(clip).parts[:-1]):
            continue
        if rel in sent or any(fnmatch.fnmatch(rel, g) for g in globs):
            continue
        out.append(rel)
    return sorted(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip_dir"); ap.add_argument("prompt"); ap.add_argument("--channel", required=True, help="e.g. Neon_Parcel; must be enabled in seedance2_gate_config.json"); ap.add_argument("--version", required=True); ap.add_argument("--shot-id", required=True)
    ap.add_argument("--out"); ap.add_argument("--retry-reason"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--manifest")
    ap.add_argument("--model", default="mini", choices=["mini", "standard", "fast"]); ap.add_argument("--resolution", default="480p", choices=["480p", "720p"])
    ap.add_argument("--duration", type=int, default=14)
    ap.add_argument("--keyframes", action="store_true", help="keyframe fallback: send the manifest's keyframes instead of the storyboard")
    ap.add_argument("--ref-limit", type=int, default=9, help="provider reference-image limit (Kie Seedance 2 / Mini: 9)")
    a = ap.parse_args(); clip = Path(a.clip_dir).resolve(); pf = Path(a.prompt)
    if not channel_enabled(a.channel):
        print(f"NOT ENFORCED for channel '{a.channel}' (disabled in seedance2_gate_config.json). Nothing checked, nothing submitted.")
        return
    d = load_manifest(clip, a.manifest); dropped = []
    if a.keyframes:
        items, dropped = build_keyframe_refs(clip, d, a.ref_limit)
    else:
        items = build_refs(clip, d)
    text = pf.read_text(); body = text.split("---\n", 2)[2] if text.startswith("---") else text
    fails = lint(body, len(items))
    pos = [body.find(s) for s in SECTIONS]
    if -1 in pos or pos != sorted(pos):
        fails.append("winning-formula sections missing or out of order: " + " > ".join(SECTIONS))
    for _, f, label in items:
        if label and label.lower() not in body.lower():
            fails.append(f"printed sheet label '{label}' ({f}) is not quoted in the reference block")
    if a.keyframes:
        n_kf = sum(1 for r, _, _ in items if r == "keyframe")
        if f"use @image 1 through @image {n_kf} as keyframes in this order" not in " ".join(body.lower().split()):
            fails.append(f"keyframe mode: prompt must say 'Use @Image 1 through @Image {n_kf} as keyframes in this order'")
    elif len(items) > a.ref_limit:
        fails.append(f"{len(items)} references exceed the {a.ref_limit}-image limit")
    if a.channel in SCALE_CHECK_CHANNELS:
        fails += scale_gate(clip, d)
    for rel in unaccounted_sheets(clip, d, items, dropped):
        fails.append(f"sheet exists for this clip but was neither sent nor listed in not_sent with a reason: {rel}")
    print(f"MODEL: Seedance 2 {a.model}   REFERENCES (fixed upload order):")
    for i, (role, f, label) in enumerate(items, 1):
        print(f"  @Image {i} = {role}: {f}" + (f"  [label: {label}]" if label else ""))
    if a.keyframes:
        print(f"  NOT SENT: storyboard {d.get('storyboard')} (keyframe fallback; file kept)")
        for role, f, _ in dropped:
            print(f"  NOT SENT: {role} {f} (over the {a.ref_limit}-image limit; lowest priority)")
    if fails:
        print("BLOCKED, no paid call made:"); [print(" -", x) for x in fails]; sys.exit(1)
    print("Passes: references complete, tags used in every beat, sections in order, no unaccounted sheets.")
    if a.dry_run:
        print("DRY RUN: nothing submitted."); return
    sys.path.insert(0, "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Character-Sheet-Generation/scripts")
    from image_generation import _resolve_to_public_url as up
    urls = [up(str(clip / f)) for _, f, _ in items]
    if a.model == "mini":
        import kie_market_api as k
        out = k.generate_seedance_mini(body.strip(), clip / a.out, resolution=a.resolution, aspect_ratio="16:9", duration=a.duration, generate_audio=True,
            generation_log=clip / "Data" / "Generation_Log.json", shot_id=a.shot_id, version=a.version, prompt_file=pf, reference_image_urls=urls, retry_reason=a.retry_reason)
        print("OUT", out)
    else:  # UNTESTED path
        cmd = ["kie-cli", "bytedance_seedance_video", "--prompt", body.strip(), "--mode", a.model, "--resolution", a.resolution, "--duration", str(a.duration), "--aspect_ratio", "16:9", "--json"]
        for u in urls:
            cmd += ["--reference_image_urls", u]
        print(subprocess.run(cmd, capture_output=True, text=True).stdout)


if __name__ == "__main__":
    main()
