#!/usr/bin/env python3
"""Open-vocabulary landmark-position check across two images. Channel-
agnostic, global tool -- lives here (not under a channel folder) so any
video pipeline can use it, same convention as check_subject_positions.py
and check_body_orientation.py.

Built after real, repeated failures on Neon Parcel Test Shot 03
(2026-09-19): verifying whether a landmark (water tank, clothesline,
mailbox, hedge, etc.) sits on the same or opposite side across two related
images -- a top-down diagram, a photoreal POV, a reverse-angle view -- was
being done by looking at screenshots and describing what seemed visible in
prose. That process produced wrong answers three times in a row on the
same shot, including after "careful" re-checking. The actual defect: none
of those landmarks are COCO classes, so `check_subject_positions.py`'s
YOLO backend (person/car/dog/etc.) can't see them at all -- there was no
tool capable of detecting them, only a human eyeballing pixels.

This tool uses an OPEN-VOCABULARY detector (OWL-ViT, via Hugging Face
transformers) instead of a fixed class list -- it takes arbitrary text
labels ("water tank", "rotary clothesline", "mailbox on a post") and
returns real bounding boxes for them, even though none of those are
trained COCO classes. This is what closes the actual gap: not "look more
carefully," but "have a tool that can see the specific things being asked
about at all."

USAGE GATE -- same discipline as check_subject_positions.py: this is an
escalation tool, not a first-pass habit. Use it specifically for "does
landmark X sit on the same/opposite side across these two images" style
questions, after a text-only description has already gotten it wrong once,
not as a blanket replacement for visual review.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def detect_landmarks(image_path: str, labels: list[str], threshold: float = 0.08) -> list[dict]:
    """Zero-shot object detection via OWL-ViT: takes arbitrary text labels,
    not a fixed class list. Returns the highest-confidence box per label
    (if found above threshold)."""
    from transformers import pipeline

    detector = pipeline("zero-shot-object-detection", model="google/owlvit-base-patch32")
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    candidate_labels = [label if label.strip().endswith((".", "!")) else label.strip() for label in labels]
    preds = detector(img, candidate_labels=candidate_labels, threshold=threshold)

    best_per_label: dict[str, dict] = {}
    for p in preds:
        label = p["label"]
        if label not in best_per_label or p["score"] > best_per_label[label]["score"]:
            box = p["box"]
            x_center = (box["xmin"] + box["xmax"]) / 2
            y_center = (box["ymin"] + box["ymax"]) / 2
            best_per_label[label] = {
                "label": label,
                "score": round(float(p["score"]), 3),
                "bbox_px": [box["xmin"], box["ymin"], box["xmax"], box["ymax"]],
                "x_center_frac": round(x_center / w, 4),
                "y_center_frac": round(y_center / h, 4),
            }

    results = [best_per_label[label] for label in labels if label in best_per_label]
    missing = [label for label in labels if label not in best_per_label]
    return {"image": str(image_path), "size": [w, h], "detections": results, "not_found": missing}


def side_of_center(x_center_frac: float) -> str:
    if x_center_frac < 0.48:
        return "left"
    if x_center_frac > 0.52:
        return "right"
    return "center"


def compare_positions(det_a: dict, det_b: dict, expected: str) -> dict:
    """expected: 'same' (landmark should be on the same screen side in both
    images) or 'mirrored' (landmark should be on the opposite screen side
    -- e.g. comparing a doorbell POV against a reverse-facing view).

    Checks x (left/right) automatically -- this transfers cleanly between
    a top-down plan and a perspective shot because horizontal position is
    preserved (mod mirroring) across viewpoint changes for a roughly-planar
    scene. Depth/y is reported as raw data, NOT auto-pass/failed -- real
    limitation, stated honestly (2026-09-19): a top-down plan's y-axis
    (literal distance from the house) and a perspective camera's y-axis
    (vertical pixel position, driven by apparent height/distance under
    that camera's specific lens and angle) are not the same measurement
    and don't map to each other by a simple rule. Cross-reference the
    reported y values against the site plan's own stated depth for that
    landmark by eye -- this tool surfaces the number instead of silently
    dropping the depth axis entirely (the actual prior failure), it does
    not claim to auto-validate it the way it does for x."""
    by_label_a = {d["label"]: d for d in det_a["detections"]}
    by_label_b = {d["label"]: d for d in det_b["detections"]}
    common = sorted(set(by_label_a) & set(by_label_b))

    checks = []
    for label in common:
        side_a = side_of_center(by_label_a[label]["x_center_frac"])
        side_b = side_of_center(by_label_b[label]["x_center_frac"])
        if expected == "mirrored":
            passed = (
                (side_a == "left" and side_b == "right")
                or (side_a == "right" and side_b == "left")
                or side_a == "center" or side_b == "center"
            )
        else:
            passed = side_a == side_b or side_a == "center" or side_b == "center"
        checks.append({
            "label": label,
            "side_in_image_a": side_a,
            "side_in_image_b": side_b,
            "x_center_frac_a": by_label_a[label]["x_center_frac"],
            "x_center_frac_b": by_label_b[label]["x_center_frac"],
            "expected_relationship": expected,
            "x_passed": passed,
            "y_center_frac_a": by_label_a[label]["y_center_frac"],
            "y_center_frac_b": by_label_b[label]["y_center_frac"],
            "y_note": "NOT auto-validated -- cross-reference against this landmark's stated "
                      "depth (near house / mid-yard / near street) in the site plan by eye",
        })

    return {
        "expected_relationship": expected,
        "checks": checks,
        "all_x_passed": all(c["x_passed"] for c in checks) if checks else None,
        "labels_missing_in_a": det_a["not_found"],
        "labels_missing_in_b": det_b["not_found"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image_a", help="First image path")
    parser.add_argument("image_b", help="Second image path")
    parser.add_argument("--labels", nargs="+", required=True,
                         help="Arbitrary text labels to detect in both images, e.g. "
                              "--labels \"water tank\" \"rotary clothesline\" \"mailbox\" \"car\"")
    parser.add_argument("--expect", choices=["same", "mirrored"], required=True,
                         help="'same' if the two images should show a landmark on the same screen "
                              "side (e.g. two diagrams facing the same direction); 'mirrored' if they "
                              "face opposite directions (e.g. a POV shot vs. its reverse-angle view)")
    parser.add_argument("--threshold", type=float, default=0.08)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    det_a = detect_landmarks(args.image_a, args.labels, args.threshold)
    det_b = detect_landmarks(args.image_b, args.labels, args.threshold)
    comparison = compare_positions(det_a, det_b, args.expect)

    output = {"image_a_detections": det_a, "image_b_detections": det_b, "comparison": comparison}
    rendered = json.dumps(output, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
