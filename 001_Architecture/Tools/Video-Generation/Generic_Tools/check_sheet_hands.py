#!/usr/bin/env python3
"""Deterministic (non-LLM) hand checker for generated sheets / storyboard panels.

Finds every human hand in an image and reports which hand it is (left/right) with a
confidence score, plus an annotated overlay. Built because a vision-language model
cannot reliably tell left from right hands; this measures it instead.

Runs MediaPipe's palm-detection + hand-landmark models through OpenCV DNN (ONNX from
opencv/palm_detection_mediapipe and opencv/handpose_estimation_mediapipe on Hugging Face).
Do NOT use the mediapipe package for this on macOS: its hand model hard-crashes
("DrishtiMetalHelper ... Service is unavailable"), same as its pose model.

Scans the full image plus overlapping tiles, so small hands inside a big multi-panel
sheet are still found.

Usage:
    python3 check_sheet_hands.py <image> [<image> ...] [--overlay-dir DIR] [--json]
    python3 check_sheet_hands.py <image> --mirror-test     # flips the image; labels must swap

Handedness convention: for this ONNX build the raw label is the real hand (no mirror flip needed; HANDEDNESS_FLIP=False,
calibrated on known-answer images). Limits: cannot count fingers (landmarks are always 21 points, so a sixth
finger is not detected); false positives possible (a toe was read as a hand); animal hands are not supported.
"""
import argparse, json, sys
from pathlib import Path
import cv2 as cv
import numpy as np

MODELS = Path(__file__).resolve().parent / "models"
sys.path.insert(0, str(MODELS))
from mp_palmdet import MPPalmDet          # noqa: E402
from mp_handpose import MPHandPose        # noqa: E402

# Calibrated 2026-09-20 on known-answer hands (rider-POV bike grips + front/side/back standing panels): raw label is the person's real hand, so no flip. Flip=True is WRONG for this ONNX build.
HANDEDNESS_FLIP = False
CONFIG_PATH = Path(__file__).resolve().parent / "sheet_checker_config.json"


def load_config():
    """Scope + gate settings live in sheet_checker_config.json (edit it, not the code).
    global_for_human_characters=true turns this into a check for EVERY pipeline; otherwise only
    pipelines listed in enabled_pipelines run it (others are reported as SKIPPED)."""
    d = {"global_for_human_characters": False, "enabled_pipelines": ["Neon_Parcel"], "pass_threshold": 0.8, "foot_filter": True}
    try:
        d.update(json.loads(CONFIG_PATH.read_text()))
    except Exception:
        pass
    return d
MIN_HAND_CONF = 0.6
FINGER_TIPS = [4, 8, 12, 16, 20]


def _load():
    palm = MPPalmDet(str(MODELS / "palm_detection_mediapipe_2023feb.onnx"), scoreThreshold=0.3)
    hand = MPHandPose(str(MODELS / "handpose_estimation_mediapipe_2023feb.onnx"), confThreshold=MIN_HAND_CONF)
    return palm, hand


def _tiles(w, h):
    yield 0, 0, w, h
    for cols, rows in ((2, 2), (3, 2), (3, 3)):
        tw, th = int(w / cols * 1.35), int(h / rows * 1.35)
        for r in range(rows):
            for c in range(cols):
                x0 = min(max(int(c * w / cols - (tw - w / cols) / 2), 0), w - tw)
                y0 = min(max(int(r * h / rows - (th - h / rows) / 2), 0), h - th)
                yield x0, y0, tw, th


def _iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy; u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / u if u > 0 else 0


def detect_hands(img_bgr, palm, hand):
    h, w = img_bgr.shape[:2]; found = []
    for x0, y0, tw, th in _tiles(w, h):
        tile = img_bgr[y0:y0 + th, x0:x0 + tw]
        try:
            palms = palm.infer(tile)
        except Exception:
            continue
        for p in palms:
            res = hand.infer(tile, p)
            if res is None:
                continue
            lm = res[4:67].reshape(21, 3).copy(); lm[:, 0] += x0; lm[:, 1] += y0
            xs, ys = lm[:, 0], lm[:, 1]
            box = [float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max())]
            raw = float(res[130]); conf = float(res[131])
            found.append({"box": box, "raw_right_score": raw, "conf": conf, "landmarks": lm[:, :2].tolist()})
    found.sort(key=lambda d: -d["conf"]); kept = []
    for d in found:
        if all(_iou(d["box"], k["box"]) < 0.3 for k in kept):
            kept.append(d)
    return kept


_POSE = None


def _pose_model():
    global _POSE
    if _POSE is None:
        from ultralytics import YOLO
        _POSE = YOLO(str(MODELS / "yolo11n-pose.pt"))
    return _POSE


def pose_people(img_bgr):
    """Every person found by YOLO-pose across tiles: [{'kp': 17x2 array, 'cf': 17 array, 'box': (x0,y0,x1,y1)}], de-duplicated."""
    h, w = img_bgr.shape[:2]; found = []
    model = _pose_model()
    for x0, y0, tw, th in _tiles(w, h):
        r = model.predict(img_bgr[y0:y0 + th, x0:x0 + tw], imgsz=1280, conf=0.25, verbose=False)[0]
        if r.keypoints is None:
            continue
        for kp, cf, bx in zip(r.keypoints.xy.cpu().numpy(), r.keypoints.conf.cpu().numpy(), r.boxes.xyxy.cpu().numpy()):
            kp = kp + np.array([x0, y0]); box = (bx[0] + x0, bx[1] + y0, bx[2] + x0, bx[3] + y0)
            if all(_iou(box, f["box"]) < 0.5 for f in found):
                found.append({"kp": kp, "cf": cf, "box": box})
    return found


def foot_zones(people):
    """Rectangles covering each person's lower legs/feet from knee+ankle keypoints (COCO 13-16). A 'hand' centred in one is a foot misread."""
    zones = []
    for p in people:
        kp, cf = p["kp"], p["cf"]
        for knee, ank in ((13, 15), (14, 16)):
            if cf[ank] < 0.3:
                continue
            ax, ay = kp[ank]; kx, ky = kp[knee] if cf[knee] > 0.3 else (ax, ay - 200)
            reach = max(abs(ay - ky), 60) * 0.5
            zones.append((ax - reach, (ky + ay) / 2, ax + reach, ay + reach))
    return zones


def wrist_hands(img_bgr, people, palm, hand):
    """Recall booster: crop a zoomed square around every detected wrist (COCO 9,10) and run the hand model there.
    Finds the small hanging hands the whole-sheet tiles miss."""
    h, w = img_bgr.shape[:2]; out = []
    for p in people:
        ph = p["box"][3] - p["box"][1]
        for idx in (9, 10):
            if p["cf"][idx] < 0.3:
                continue
            cx, cy = p["kp"][idx]; side = int(max(0.22 * ph, 96)); half = side // 2
            x0, y0 = int(max(cx - half, 0)), int(max(cy - half, 0)); x1, y1 = int(min(cx + half, w)), int(min(cy + half, h))
            crop = img_bgr[y0:y1, x0:x1]
            if crop.shape[0] < 32 or crop.shape[1] < 32:
                continue
            sc = 384 / max(crop.shape[:2]); big = cv.resize(crop, None, fx=sc, fy=sc, interpolation=cv.INTER_CUBIC)
            try:
                palms = palm.infer(big)
            except Exception:
                continue
            for pl in palms:
                res = hand.infer(big, pl)
                if res is None:
                    continue
                lm = res[4:67].reshape(21, 3).copy(); lm[:, 0] = lm[:, 0] / sc + x0; lm[:, 1] = lm[:, 1] / sc + y0
                xs, ys = lm[:, 0], lm[:, 1]
                out.append({"box": [float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max())], "raw_right_score": float(res[130]),
                            "conf": float(res[131]), "landmarks": lm[:, :2].tolist()})
    return out


def anomaly_flags(d):
    """Review flags from landmark geometry (NOT finger counting: the landmark model always draws 5 fingers, so a 6th finger is invisible to it).
    Flags unusual hands so a human looks: low landmark confidence, or finger/palm proportions far outside normal."""
    lm = np.array(d["landmarks"]); flags = []
    if d["conf"] < 0.85:
        flags.append("low_landmark_confidence")
    bw, bh = d["box"][2] - d["box"][0], d["box"][3] - d["box"][1]
    if min(bw, bh) < 60:   # too few pixels for a meaningful proportion measurement: only the confidence flag applies
        return flags
    palm_w = np.linalg.norm(lm[5] - lm[17]) + 1e-6
    for name, mcp, tip in (("index", 5, 8), ("middle", 9, 12), ("ring", 13, 16), ("pinky", 17, 20)):
        r = np.linalg.norm(lm[tip] - lm[mcp]) / palm_w
        if r > 2.2:
            flags.append(f"{name}_finger_very_long")
    thumb = np.linalg.norm(lm[4] - lm[2]) / palm_w
    if thumb > 2.0:
        flags.append("thumb_very_long")
    return flags


def merge_hands(base, extra):
    kept = list(base)
    for d in sorted(extra, key=lambda x: -x["conf"]):
        if all(_iou(d["box"], k["box"]) < 0.3 for k in kept):
            kept.append(d)
    return kept


def label_hands(found):
    out = []
    for d in found:
        right_score = 1 - d["raw_right_score"] if HANDEDNESS_FLIP else d["raw_right_score"]
        d["hand"] = "RIGHT" if right_score >= 0.5 else "LEFT"
        d["hand_confidence"] = round(abs(right_score - 0.5) * 2, 2)
        d["detect_conf"] = round(d["conf"], 2)
        d["review_flags"] = anomaly_flags(d)
        out.append(d)
    return out


def drop_feet(hands, zones):
    kept, dropped = [], []
    for d in hands:
        cx, cy = (d["box"][0] + d["box"][2]) / 2, (d["box"][1] + d["box"][3]) / 2
        (dropped if any(z[0] <= cx <= z[2] and z[1] <= cy <= z[3] for z in zones) else kept).append(d)
    return kept, dropped


def gate(hands, expects, threshold):
    """expects: list of (LEFT|RIGHT, (x0,y0,x1,y1)). An expectation passes if a detected hand whose centre
    is inside the region has the expected label. Returns (score, per-item results)."""
    res = []
    for want, (x0, y0, x1, y1) in expects:
        inside = [d for d in hands if x0 <= (d["box"][0] + d["box"][2]) / 2 <= x1 and y0 <= (d["box"][1] + d["box"][3]) / 2 <= y1]
        got = inside[0]["hand"] if inside else "NOT FOUND"
        res.append({"expected": want, "got": got, "region": [x0, y0, x1, y1], "pass": got == want,
                    "hard_fail": bool(inside) and got != want and inside[0]["hand_confidence"] >= 0.9})
    score = sum(r["pass"] for r in res) / len(res) if res else None
    return score, res, (score is not None and score >= threshold and not any(r["hard_fail"] for r in res))


def annotate(img, hands):
    im = img.copy()
    for d in hands:
        x0, y0, x1, y1 = map(int, d["box"]); col = (0, 200, 0) if d["hand"] == "RIGHT" else (0, 140, 255)
        cv.rectangle(im, (x0, y0), (x1, y1), col, max(3, im.shape[1] // 500))
        cv.putText(im, f'{d["hand"]} {d["hand_confidence"]}', (x0, max(30, y0 - 10)), cv.FONT_HERSHEY_SIMPLEX,
                   max(1.0, im.shape[1] / 1600), col, max(2, im.shape[1] // 800))
        for x, y in d["landmarks"]:
            cv.circle(im, (int(x), int(y)), max(3, im.shape[1] // 600), (255, 0, 255), -1)
    return im


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("images", nargs="+"); ap.add_argument("--overlay-dir")
    ap.add_argument("--json", action="store_true"); ap.add_argument("--mirror-test", action="store_true")
    ap.add_argument("--pipeline", help="pipeline name, e.g. Neon_Parcel; skipped unless enabled in sheet_checker_config.json")
    ap.add_argument("--expect", action="append", default=[], metavar="HAND:x0,y0,x1,y1",
                    help="expected hand in a region, e.g. LEFT:2200,380,2450,520 (repeatable). Enables the pass/fail gate.")
    ap.add_argument("--no-foot-filter", action="store_true"); ap.add_argument("--no-wrist-seed", action="store_true", help="skip the pose-seeded wrist crops (faster, finds fewer small hands)")
    a = ap.parse_args(); cfg = load_config()
    if a.pipeline and not cfg["global_for_human_characters"] and a.pipeline not in cfg["enabled_pipelines"]:
        print(f"SKIPPED: hand checker is not enabled for pipeline '{a.pipeline}' (set global_for_human_characters=true in {CONFIG_PATH.name} to enable everywhere)")
        return
    palm, hand = _load(); report = {}
    for f in a.images:
        img = cv.imread(f)
        if img is None:
            print(f"cannot read {f}", file=sys.stderr); continue
        if a.mirror_test:
            img = cv.flip(img, 1)
        hands = detect_hands(img, palm, hand); dropped = []
        people = pose_people(img) if (cfg["foot_filter"] and not a.no_foot_filter) or not a.no_wrist_seed else []
        if not a.no_wrist_seed:
            hands = merge_hands(hands, wrist_hands(img, people, palm, hand))
        hands = label_hands(hands)
        if cfg["foot_filter"] and not a.no_foot_filter:
            hands, dropped = drop_feet(hands, foot_zones(people))
        report[f] = [{k: v for k, v in d.items() if k not in ("landmarks", "raw_right_score", "conf")} for d in hands]
        if a.expect:
            ex = []
            for e in a.expect:
                w_, r_ = e.split(":"); ex.append((w_.upper(), tuple(float(v) for v in r_.split(","))))
            score, items, ok = gate(hands, ex, cfg["pass_threshold"])
            report[f + "#gate"] = {"score": score, "threshold": cfg["pass_threshold"], "PASS": ok, "items": items}
        if dropped:
            report[f + "#dropped_as_feet"] = [[int(v) for v in d["box"]] for d in dropped]
        if a.overlay_dir:
            Path(a.overlay_dir).mkdir(parents=True, exist_ok=True)
            cv.imwrite(str(Path(a.overlay_dir) / (Path(f).stem + ("_mirrored" if a.mirror_test else "") + "_hands.jpg")), annotate(img, hands))
    if a.json:
        print(json.dumps(report, indent=1))
    else:
        for f, hs in report.items():
            if f.endswith("#gate"):
                print(f"   GATE: {'PASS' if hs['PASS'] else 'FAIL'} score={hs['score']} (need {hs['threshold']}) " + "; ".join(f"{i['expected']}->{i['got']}{' HARD-FAIL' if i['hard_fail'] else ''}" for i in hs['items'])); continue
            if f.endswith("#dropped_as_feet"):
                print(f"   dropped as feet (not hands): {hs}"); continue
            print(f"{Path(f).name}: {len(hs)} hand(s)" + (" [MIRRORED]" if a.mirror_test else ""))
            for d in hs:
                print(f"   {d['hand']:5s} hand_conf={d['hand_confidence']} detect_conf={d['detect_conf']} box={[int(v) for v in d['box']]}" + (f"  REVIEW:{','.join(d['review_flags'])}" if d['review_flags'] else ""))


if __name__ == "__main__":
    main()
