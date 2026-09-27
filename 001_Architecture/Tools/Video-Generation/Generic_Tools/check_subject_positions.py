#!/usr/bin/env python3
"""Deterministic subject-position check for a storyboard grid image. Channel-
agnostic, global tool -- lives here (not under a channel folder) so any video
pipeline can use it, same convention as check_body_orientation.py.

Built after real, repeated failures on Neon Parcel Test Shot 03 (2026-09-18):
visual review alone missed or misjudged (a) whether a subject's on-screen
position advanced or retreated between frames, and (b) whether two subjects'
silhouettes actually collided. This tool replaces eyeballing those two
specific questions with measured pixel data. It does NOT replace visual
review generally -- it answers three narrow, previously-unreliable questions:

1. Bounding-box detection (Ultralytics YOLO, COCO classes: person, car, dog,
   etc.) -- coarse position and confidence per subject per panel.
2. Pose keypoints (Ultralytics YOLO-pose, COCO 17-point skeleton) -- precise
   ankle/foot location for a person, since a whole-body bounding-box center
   is too noisy (it shifts with arm/bag position) to answer "which exact
   spot is he standing in."
3. Instance segmentation (Ultralytics YOLO-seg) -- real pixel silhouettes,
   for collision/overlap checks between two subjects (e.g. "does the
   kangaroo's body actually touch the letterbox") that a bounding-box
   overlap test gets wrong in both directions (false positive when boxes
   overlap but shapes don't touch; false negative when shapes visually
   merge but boxes barely overlap).

Real, honest limitation, not fixed by any of the above: none of these models
know scene geography ("steps," "driveway," "sidewalk" are not trained
classes). The only way to check "is this subject's foot on the steps or the
driveway" is to mark that region once, by hand, as a fixed polygon -- doable
here specifically because a locked/fixed-mount camera shot never changes
its geometry between panels, so one polygon map applies to every panel.
Pass it with --zones.

USAGE GATE -- do not run this on a first-draft storyboard. It costs real
compute (up to 3 YOLO models across every panel) and most drafts have
issues visual review catches faster and more cheaply on its own. Run this
only as an escalation: after the SAME shot has already failed visual review
at least twice on a position/collision-type defect (not a style or prompt-
adherence defect -- this tool has nothing to say about those). See each
pipeline's storyboard review policy for where this gate is enforced.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from PIL import Image


def split_grid(image_path: str, rows: int, cols: int, caption_band_frac: float = 0.0) -> list[Image.Image]:
    """Split a storyboard sheet into its panel images, left-to-right, top-to-bottom.
    caption_band_frac trims a bottom strip (0-1 of each row's height) if a caption
    band is baked inside each cell rather than in a separate row."""
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    cell_w, cell_h = w / cols, h / rows
    panels = []
    for r in range(rows):
        for c in range(cols):
            x0, y0 = c * cell_w, r * cell_h
            x1, y1 = x0 + cell_w, y0 + cell_h * (1 - caption_band_frac)
            panels.append(img.crop((int(x0), int(y0), int(x1), int(y1))))
    return panels


def save_panels_full_size(image_path: str, rows: int, cols: int, caption_band_frac: float,
                           out_dir: Path) -> list[Path]:
    """Save each panel as its own full-resolution file, native panel resolution
    (not shrunk to fit inside a thumbnail of the whole sheet). Real failure this
    fixes (2026-09-18): reviewing panels inside the full 6-panel sheet at a
    reduced display size caused repeated misjudgment of exactly which ground
    surface (step tile vs. porch concrete vs. driveway gravel) a subject's feet
    were on -- a distinction only visible when each panel is inspected at its
    own full native resolution, on its own, not as one-sixth of a compressed
    overview image."""
    out_dir.mkdir(parents=True, exist_ok=True)
    panels = split_grid(image_path, rows, cols, caption_band_frac)
    paths = []
    for i, panel in enumerate(panels, start=1):
        p = out_dir / f"panel_{i}.png"
        panel.save(p)
        paths.append(p)
    return paths


def onion_skin(panel_a_path: Path, panel_b_path: Path, out_path: Path) -> Path:
    """Animator's onion-skin overlay between two consecutive panels: panel A
    tinted red, panel B tinted cyan, blended 50/50. Anything that stayed in
    the exact same place across both panels reads as neutral gray; anything
    that moved, appeared, or disappeared shows up as a distinct red or cyan
    ghost -- the same technique traditional animators use to check a
    subject's position hasn't drifted (or silently reversed) frame to frame,
    made explicit and measurable instead of eyeballed from two separate
    thumbnails that were never directly compared against each other."""
    import numpy as np

    a = Image.open(panel_a_path).convert("L")
    b = Image.open(panel_b_path).convert("L")
    if a.size != b.size:
        b = b.resize(a.size)
    a_arr, b_arr = np.array(a), np.array(b)
    overlay = np.zeros((*a_arr.shape, 3), dtype=np.uint8)
    overlay[..., 0] = a_arr  # panel A -> red channel
    overlay[..., 1] = b_arr  # panel B -> green channel
    overlay[..., 2] = b_arr  # panel B -> blue channel (green+blue = cyan)
    Image.fromarray(overlay).save(out_path)
    return out_path


def detect_positions(panels: list[Image.Image], classes: list[str]) -> list[dict]:
    from ultralytics import YOLO

    model = YOLO("yolo11n.pt")
    names = model.names
    wanted = {v for k, v in names.items() if v in classes}
    results = []
    for i, panel in enumerate(panels, start=1):
        w, h = panel.size
        preds = model.predict(panel, verbose=False)[0]
        detections = []
        for box in preds.boxes:
            cls_name = names[int(box.cls[0])]
            if cls_name not in wanted:
                continue
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append({
                "class": cls_name,
                "confidence": round(float(box.conf[0]), 3),
                "x_center_frac": round(((x1 + x2) / 2) / w, 4),
                "y_center_frac": round(((y1 + y2) / 2) / h, 4),
                "bbox_frac": [round(x1 / w, 4), round(y1 / h, 4), round(x2 / w, 4), round(y2 / h, 4)],
            })
        results.append({"panel": i, "detections": detections})
    return results


def detect_person_ankles(panels: list[Image.Image]) -> list[dict]:
    """YOLO-pose ankle keypoints per person per panel -- the precise reference
    point for "which spot is he standing in," not a whole-body bbox center."""
    from ultralytics import YOLO

    model = YOLO("yolo11n-pose.pt")
    # COCO keypoint indices: 15=left_ankle, 16=right_ankle
    results = []
    for i, panel in enumerate(panels, start=1):
        w, h = panel.size
        preds = model.predict(panel, verbose=False)[0]
        people = []
        if preds.keypoints is not None:
            for person_kpts, conf in zip(preds.keypoints.xy, preds.keypoints.conf):
                l_ankle, r_ankle = person_kpts[15], person_kpts[16]
                l_conf, r_conf = float(conf[15]), float(conf[16])
                pts = [(pt, c) for pt, c in ((l_ankle, l_conf), (r_ankle, r_conf)) if c > 0.3]
                if not pts:
                    continue
                ax = sum(float(p[0][0]) for p in pts) / len(pts)
                ay = sum(float(p[0][1]) for p in pts) / len(pts)
                people.append({
                    "foot_x_frac": round(ax / w, 4),
                    "foot_y_frac": round(ay / h, 4),
                    "ankle_confidence": round(sum(p[1] for p in pts) / len(pts), 3),
                })
        results.append({"panel": i, "people": people})
    return results


def detect_segmentation_overlap(panels: list[Image.Image], class_a: str, class_b: str) -> list[dict]:
    """Pixel-level mask overlap between two classes per panel -- for real
    collision checks a bounding-box test gets wrong in both directions."""
    from ultralytics import YOLO
    import numpy as np

    model = YOLO("yolo11n-seg.pt")
    names = model.names
    results = []
    for i, panel in enumerate(panels, start=1):
        preds = model.predict(panel, verbose=False)[0]
        mask_a = mask_b = None
        if preds.masks is not None:
            for box, mask in zip(preds.boxes, preds.masks.data):
                cls_name = names[int(box.cls[0])]
                m = mask.cpu().numpy().astype(bool)
                if cls_name == class_a and mask_a is None:
                    mask_a = m
                elif cls_name == class_b and mask_b is None:
                    mask_b = m
        if mask_a is not None and mask_b is not None:
            # masks may differ in resolution from slight model internals; align by resizing b to a's shape
            if mask_a.shape != mask_b.shape:
                mb_img = Image.fromarray(mask_b.astype("uint8") * 255).resize(
                    (mask_a.shape[1], mask_a.shape[0]))
                mask_b = np.array(mb_img) > 127
            overlap_px = int(np.logical_and(mask_a, mask_b).sum())
            results.append({"panel": i, class_a: True, class_b: True, "overlap_pixels": overlap_px,
                             "colliding": overlap_px > 0})
        else:
            results.append({"panel": i, class_a: mask_a is not None, class_b: mask_b is not None,
                             "overlap_pixels": None, "colliding": False})
    return results


def point_in_polygon(x: float, y: float, polygon: list[list[float]]) -> bool:
    """Standard ray-casting point-in-polygon test, fractional coordinates."""
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def classify_zones(foot_points: list[dict], zones: dict[str, list[list[float]]]) -> list[dict]:
    """For each panel's detected foot point(s), report which named zone (if
    any) contains it. zones: {"steps": [[x,y],...], "driveway": [[x,y],...]}
    in fractional panel coordinates -- valid only for a locked/fixed camera
    where the same polygon map applies to every panel."""
    results = []
    for panel in foot_points:
        panel_result = {"panel": panel["panel"], "people_zones": []}
        for person in panel["people"]:
            fx, fy = person["foot_x_frac"], person["foot_y_frac"]
            matched = [name for name, poly in zones.items() if point_in_polygon(fx, fy, poly)]
            panel_result["people_zones"].append({
                "foot_x_frac": fx, "foot_y_frac": fy,
                "zone": matched[0] if matched else "unmatched",
            })
        results.append(panel_result)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", help="Path to the storyboard grid image")
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--cols", type=int, required=True)
    parser.add_argument("--caption-band-frac", type=float, default=0.0)
    parser.add_argument("--classes", nargs="+", default=["person", "car"])
    parser.add_argument("--pose", action="store_true", help="Also extract precise ankle/foot keypoints for each person")
    parser.add_argument("--zones", type=Path, help="JSON file: {zone_name: [[x_frac,y_frac], ...]} -- requires --pose")
    parser.add_argument("--seg-overlap", nargs=2, metavar=("CLASS_A", "CLASS_B"),
                         help="Check pixel-level mask overlap between two classes, e.g. --seg-overlap kangaroo letterbox "
                              "(only works for classes YOLO-seg's COCO training actually knows)")
    parser.add_argument("--save-panels", type=Path,
                         help="Save each panel as its own full-resolution file in this directory "
                              "(panel_1.png, panel_2.png, ...) for direct one-at-a-time inspection, "
                              "not viewed shrunk inside the whole sheet")
    parser.add_argument("--onion-skin", nargs=2, type=int, metavar=("PANEL_A", "PANEL_B"),
                         help="Generate a red/cyan onion-skin overlay between two panel numbers (1-indexed) "
                              "-- unchanged elements read neutral gray, anything that moved, appeared, or "
                              "disappeared shows as a red or cyan ghost. Requires --save-panels (or panels "
                              "are extracted fresh if not already saved).")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    default_panel_dir = Path(tempfile.gettempdir()) / "storyboard_panels"
    panel_paths: list[Path] = []
    if args.save_panels or args.onion_skin:
        save_dir = args.save_panels or default_panel_dir
        panel_paths = save_panels_full_size(args.image, args.rows, args.cols, args.caption_band_frac, save_dir)

    panels = split_grid(args.image, args.rows, args.cols, args.caption_band_frac)
    output: dict = {"detections": detect_positions(panels, args.classes)}

    if args.pose:
        ankles = detect_person_ankles(panels)
        output["ankles"] = ankles
        if args.zones:
            zones = json.loads(args.zones.read_text(encoding="utf-8"))
            output["zone_classification"] = classify_zones(ankles, zones)

    if args.seg_overlap:
        output["segmentation_overlap"] = detect_segmentation_overlap(panels, *args.seg_overlap)

    if args.save_panels:
        output["saved_panels"] = [str(p) for p in panel_paths]

    if args.onion_skin:
        a_num, b_num = args.onion_skin
        onion_out = (args.save_panels or default_panel_dir) / f"onion_{a_num}_{b_num}.png"
        onion_skin(panel_paths[a_num - 1], panel_paths[b_num - 1], onion_out)
        output["onion_skin"] = str(onion_out)

    rendered = json.dumps(output, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
