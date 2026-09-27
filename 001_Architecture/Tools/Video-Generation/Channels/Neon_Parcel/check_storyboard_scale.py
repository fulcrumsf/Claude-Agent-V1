#!/usr/bin/env python3
"""Measured scale check for a Neon Parcel storyboard (Tony, 2026-09-26). Local YOLOE detection, no paid calls.

Why: Shot 07 went to video with the van growing ~55% while parked and the van/man oversized vs the harbour, which is
obvious by eye and cost the shot its A. This measures it on the storyboard, before any video money is spent.
Only differences you'd notice by eye fail; a few pixels pass.

Reads <clip>/Data/Scale_Spec.json (written per shot from the prompt + shot description):
  {"storyboard": "Storyboard_Clip1_v2.png", "panels": 6,
   "horizon_row_frac": 0.08,                      # optional: where the ground would meet the horizon (fraction of panel height)
   "anchors":  [{"name": "parked car", "height_m": 1.5, "prompts": ["car"]}],          # fixed objects of known size
   "subjects": [{"name": "van", "height_m": 2.0, "prompts": ["truck", "van"], "static_from_panel": 3},
                {"name": "fishmonger", "height_m": 1.75, "prompts": ["man", "person"]},
                {"name": "walrus", "height_m": 1.0, "prompts": ["large animal", "walrus"], "exaggerated": true,
                 "pose_varies": true, "why": "prompt says 'large walrus'"}],
   "rules": [{"a": "walrus", "b": "van", "max_ratio": 0.6, "why": "must fit in the van's cargo box"}],
   "tolerances": {"same_ground": 0.04, "size_change": 0.15, "pair_ratio": 0.25, "vs_environment": 0.25}}
Heights are REAL-WORLD heights as the prompt states them ("a 7-foot man" -> 2.13). "exaggerated" subjects skip the realism
checks but must still obey every rule (e.g. the walrus may be huge but must fit in the van). "pose_varies" skips the SIZE CHANGE
check for a subject whose box height changes with posture (an animal sitting up vs lying flat); it is still measured otherwise.

Checks (a panel fails when any is broken):
  1. SIZE CHANGE  - the same subject standing on the same ground line in two panels changes height by more than size_change.
     A subject marked static_from_panel (e.g. a parked van) also fails if it moves toward/away from the camera after that panel.
  2. VS ENVIRONMENT - a realistic subject's height vs what the anchors say that spot of ground should show (perspective:
     pixels-per-metre grows linearly from the horizon down). Needs 2+ anchor distances or horizon_row_frac, else a warning.
  3. PAIR RATIO   - two realistic subjects on the same ground line in one panel: measured height ratio vs real ratio.
  4. RULES        - max_ratio rules (a's height / b's height in the same panel) always apply, exaggerated or not.
  Subjects YOLOE can't find are listed as warnings ("not measured"), never as passes.

Writes <clip>/Data/Scale_Check_<storyboard stem>.json (pass/fail + the storyboard's sha256, which seedance2_call.py checks
before any paid call) and <clip>/Data/Scale_Check_<storyboard stem>.png (boxes + heights, for Tony's storyboard review).
Usage: python3 check_storyboard_scale.py <clip_dir> [--spec Data/Scale_Spec.json]   (exit 1 = fail)"""
import argparse, hashlib, json, sys
from itertools import combinations
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from extract_storyboard_keyframes import find_panels  # noqa: E402

MODELS = HERE.parents[1] / "Generic_Tools" / "Subject-Aware-Reframer" / "Models"
YOLOE_WEIGHTS = MODELS / "yoloe-11l-seg.pt"
DEFAULT_TOL = {"same_ground": 0.04, "size_change": 0.15, "pair_ratio": 0.25, "vs_environment": 0.25}
CONF = 0.2


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def detect(panels, entries):
    """One YOLOE pass per panel with every prompt word; keep the most confident box per named entry."""
    import os
    from ultralytics import YOLOE
    cwd = os.getcwd(); os.chdir(MODELS)          # YOLOE looks for its text encoder in the working directory
    try:
        m = YOLOE(str(YOLOE_WEIGHTS))
        words, owner = [], []
        for e in entries:
            for w in e["prompts"]:
                words.append(w); owner.append(e["name"])
        m.set_classes(words, m.get_text_pe(words))
        out = []
        for im in panels:
            r = m.predict(im, verbose=False, conf=CONF)[0]
            best = {}
            for b in r.boxes:
                name = owner[int(b.cls)]; c = float(b.conf)
                x0, y0, x1, y1 = [int(v) for v in b.xyxy[0]]
                if name not in best or c > best[name]["conf"]:
                    best[name] = {"box": [x0, y0, x1, y1], "h": y1 - y0, "bottom": y1, "conf": round(c, 2)}
            out.append(best)
        return out
    finally:
        os.chdir(cwd)


def px_per_metre(anchor_obs, horizon_row, ph):
    """Fit pixels-per-metre as a straight line of the ground row: s(y) = k * (y - y_h). Returns a function or None."""
    if not anchor_obs:
        return None
    rows = [y for y, _ in anchor_obs]
    if max(rows) - min(rows) > 0.1 * ph:      # anchors at 2+ distances: least-squares line through them
        n = len(anchor_obs); my = sum(rows) / n; ms = sum(s for _, s in anchor_obs) / n
        var = sum((y - my) ** 2 for y in rows)
        k = sum((y - my) * (s - ms) for y, s in anchor_obs) / var
        return lambda y: ms + k * (y - my)
    if horizon_row is not None:              # one anchor distance + known horizon
        k = sum(s / (y - horizon_row) for y, s in anchor_obs if y > horizon_row) / len(anchor_obs)
        return lambda y: k * (y - horizon_row)
    return None


def check(spec, dets, ph):
    tol = {**DEFAULT_TOL, **spec.get("tolerances", {})}
    subs = {s["name"]: s for s in spec["subjects"]}
    fails, warns = [], []
    same = lambda a, b: abs(a["bottom"] - b["bottom"]) <= tol["same_ground"] * ph

    # 1. size change / static subjects moving
    for name, s in subs.items():
        if s.get("pose_varies"):
            continue
        seen = [(i + 1, d[name]) for i, d in enumerate(dets) if name in d]
        for (pi, a), (pj, b) in combinations(seen, 2):
            static = s.get("static_from_panel") and pi >= s["static_from_panel"]
            if same(a, b) or static:
                ch = b["h"] / a["h"] - 1
                if abs(ch) > tol["size_change"]:
                    fails.append(f"SIZE CHANGE: {name} is {a['h']}px in P{pi} and {b['h']}px in P{pj} ({ch:+.0%})"
                                 + (" while parked" if static else " standing at the same distance"))
            if static and not same(a, b):
                fails.append(f"MOVED: {name} should stay put from P{s['static_from_panel']} but its base moves from row "
                             f"{a['bottom']} (P{pi}) to {b['bottom']} (P{pj}), i.e. toward/away from the camera")

    # 2. vs environment
    anchor_obs = [(d[a["name"]]["bottom"], d[a["name"]]["h"] / a["height_m"]) for d in dets for a in spec.get("anchors", []) if a["name"] in d]
    hr = spec.get("horizon_row_frac"); s_of = px_per_metre(anchor_obs, hr * ph if hr is not None else None, ph)
    if s_of is None:
        warns.append("VS ENVIRONMENT not checked: no anchor found, or anchors at only one distance and no horizon_row_frac")
    else:
        for i, d in enumerate(dets):
            for name, m in d.items():
                s = subs.get(name)
                if not s or s.get("exaggerated"):
                    continue
                exp = s["height_m"] * s_of(m["bottom"])
                if exp <= 0:
                    continue
                r = m["h"] / exp - 1
                m["expected_px"] = round(exp)
                if abs(r) > tol["vs_environment"]:
                    fails.append(f"VS ENVIRONMENT: {name} in P{i + 1} is {m['h']}px; the anchors say {s['height_m']} m at that spot "
                                 f"should be about {exp:.0f}px ({r:+.0%} {'too big' if r > 0 else 'too small'})")

    # 3. pair ratio + 4. rules
    for i, d in enumerate(dets):
        real = [n for n in d if n in subs and not subs[n].get("exaggerated")]
        for a, b in combinations(real, 2):
            if same(d[a], d[b]):
                meas = d[a]["h"] / d[b]["h"]; want = subs[a]["height_m"] / subs[b]["height_m"]; r = meas / want - 1
                if abs(r) > tol["pair_ratio"]:
                    fails.append(f"PAIR RATIO: in P{i + 1} {a} is {meas:.0%} of {b}'s height; real life is {want:.0%} "
                                 f"({a} {'too big' if r > 0 else 'too small'} next to {b} by {abs(r):.0%})")
        for rule in spec.get("rules", []):
            if rule["a"] in d and rule["b"] in d:
                meas = d[rule["a"]]["h"] / d[rule["b"]]["h"]
                if meas > rule["max_ratio"]:
                    fails.append(f"RULE: in P{i + 1} {rule['a']} is {meas:.0%} of {rule['b']}'s height, max {rule['max_ratio']:.0%} "
                                 f"({rule.get('why', '')})")

    for name, s in subs.items():
        want = s.get("in_panels") or range(1, len(dets) + 1)
        missing = [p for p in want if name not in dets[p - 1]]
        if missing:
            warns.append(f"NOT MEASURED: {name} not found in P{', P'.join(map(str, missing))} (not visible, or detector missed it)")
    return fails, warns


def draw(panels, dets, out: Path):
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
    pal = [(255, 40, 40), (40, 160, 255), (180, 90, 255), (255, 200, 0), (0, 220, 120), (255, 120, 0)]
    names = sorted({n for d in dets for n in d}); col = {n: pal[i % len(pal)] for i, n in enumerate(names)}
    tiles = []
    for i, (im, d) in enumerate(zip(panels, dets)):
        im = im.copy(); dr = ImageDraw.Draw(im)
        for n, m in d.items():
            x0, y0, x1, y1 = m["box"]; dr.rectangle(m["box"], outline=col[n], width=4)
            t = f"{n} {m['h']}px" + (f" (exp {m['expected_px']})" if "expected_px" in m else "")
            tw = dr.textlength(t, font=font); dr.rectangle([x0, y0 - 26, x0 + tw + 8, y0], fill=col[n]); dr.text((x0 + 4, y0 - 25), t, fill=(0, 0, 0), font=font)
        dr.rectangle([0, 0, 70, 40], fill=(0, 0, 0)); dr.text((10, 6), f"P{i + 1}", fill=(255, 255, 255), font=font)
        tiles.append(im)
    w = max(t.width for t in tiles); h = max(t.height for t in tiles); cols = 3 if len(tiles) > 2 else len(tiles)
    rows = -(-len(tiles) // cols); sheet = Image.new("RGB", (cols * w + 10 * (cols + 1), rows * h + 10 * (rows + 1)), "white")
    for i, t in enumerate(tiles):
        sheet.paste(t, (10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 10)))
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip_dir"); ap.add_argument("--spec")
    a = ap.parse_args(); clip = Path(a.clip_dir).resolve()
    sp = Path(a.spec) if a.spec else clip / "Data" / "Scale_Spec.json"
    if not sp.is_file():
        raise SystemExit(f"No scale spec at {sp}. Write it from the prompt/shot description first (see this file's header).")
    spec = json.loads(sp.read_text()); sb = clip / spec["storyboard"]
    img = Image.open(sb).convert("RGB")
    boxes = find_panels(img, spec.get("panels", 6))
    if len(boxes) != spec.get("panels", 6):
        raise SystemExit(f"Found {len(boxes)} panels, expected {spec.get('panels', 6)}; can't measure this storyboard.")
    panels = [img.crop(b) for b in boxes]
    ph = sum(p.height for p in panels) / len(panels)
    dets = detect(panels, spec.get("anchors", []) + spec["subjects"])
    fails, warns = check(spec, dets, ph)
    stem = sb.stem; data = clip / "Data"
    report = {"storyboard": spec["storyboard"], "storyboard_sha256": sha256(sb), "spec": sp.name, "passed": not fails,
              "failures": fails, "warnings": warns, "measurements": [{"panel": i + 1, **d} for i, d in enumerate(dets)]}
    (data / f"Scale_Check_{stem}.json").write_text(json.dumps(report, indent=1))
    draw(panels, dets, data / f"Scale_Check_{stem}.png")
    print(("PASS" if not fails else "FAIL") + f": scale check on {spec['storyboard']}")
    for f in fails:
        print("  FAIL -", f)
    for w in warns:
        print("  WARN -", w)
    print(f"Report: Data/Scale_Check_{stem}.json   Picture: Data/Scale_Check_{stem}.png")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
