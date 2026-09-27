#!/usr/bin/env python3
"""Detect each visible person's body-facing direction in an image via YOLO
pose keypoints - a deterministic, non-LLM-judgment check for the orientation-
continuity defect found on Neon Parcel Test Shot 02 (a mover silently flipped
from facing-backward to facing-forward between storyboard panels, and no
review pass caught it because visual QA was being asked to hold a running
judgment across panels instead of measuring something concrete).

Uses Ultralytics YOLO-pose (PyTorch backend) rather than MediaPipe - MediaPipe's
pip-packaged pose models on macOS hard-crash ("DrishtiMetalHelper... Service is
unavailable") because a Metal graph service isn't reachable in some execution
contexts. Confirmed on both a sandboxed shell and a real M3 Max MacBook Pro, on
both the full and lite model variants - a genuine MediaPipe/macOS packaging
issue, not fixable via delegate/model-size flags. YOLO-pose runs on PyTorch's
own CPU/MPS backends and has no such dependency.

Usage:
    python3 check_body_orientation.py <image_path> [<image_path> ...]

Trade-off vs MediaPipe: YOLO-pose keypoints are 2D only (no depth), so
orientation is estimated from shoulder-keypoint mirroring plus nose-keypoint
visibility rather than true 3D shoulder depth. Coarser, but it actually runs.
"""
import argparse
from pathlib import Path

MODELS = Path(__file__).resolve().parent / "models"  # one shared copy of the weights; a bare name makes YOLO download into the cwd

from ultralytics import YOLO

# COCO keypoint indices (YOLO-pose convention)
NOSE, L_SHOULDER, R_SHOULDER = 0, 5, 6


def classify_orientation(keypoints_xy, keypoints_conf) -> str:
    """Coarse facing-direction estimate from 2D shoulder + nose keypoints.

    In image coordinates, a person's own right shoulder appears on the
    image's LEFT side when facing the camera (mirrored), and flips to the
    image's RIGHT side when facing away. A large shoulder x-span means
    roughly front/back-on to the camera; a small span means turned to a
    profile, in which case the nose's x-position relative to the shoulder
    midpoint indicates which way they're turned.
    """
    nose_x, nose_conf = keypoints_xy[NOSE][0], keypoints_conf[NOSE]
    l_x = keypoints_xy[L_SHOULDER][0]
    r_x = keypoints_xy[R_SHOULDER][0]

    shoulder_span = abs(r_x - l_x)
    shoulder_mid = (l_x + r_x) / 2

    if shoulder_span < 15:  # near-zero span in pixels -> full profile turn
        return "RIGHT" if nose_x > shoulder_mid else "LEFT"

    facing_camera_mirrored = r_x < l_x  # right shoulder on image-left = facing camera
    if facing_camera_mirrored:
        return "TOWARD_CAMERA" if nose_conf > 0.5 else "SLIGHTLY_TURNED_TOWARD"
    else:
        return "AWAY_FROM_CAMERA" if nose_conf < 0.5 else "SLIGHTLY_TURNED_AWAY"


def analyze_image(path: Path, model: YOLO) -> list[dict]:
    results = model(str(path), verbose=False)
    r = results[0]
    people = []
    if r.keypoints is None or len(r.keypoints) == 0:
        return people

    for i in range(len(r.keypoints)):
        kp_xy = r.keypoints.xy[i]
        kp_conf = r.keypoints.conf[i] if r.keypoints.conf is not None else [1.0] * len(kp_xy)
        box = r.boxes.xyxy[i].tolist() if r.boxes is not None else None
        orientation = classify_orientation(kp_xy, kp_conf)
        people.append({
            "orientation": orientation,
            "bbox_xyxy": [round(v, 1) for v in box] if box else None,
        })
    return people


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("images", nargs="+", type=Path)
    args = parser.parse_args()

    model = YOLO(str(MODELS / "yolo11n-pose.pt"))

    for img_path in args.images:
        if not img_path.exists():
            print(f"{img_path}: FILE NOT FOUND")
            continue
        people = analyze_image(img_path, model)
        if not people:
            print(f"{img_path}: no person detected")
        else:
            for i, p in enumerate(people, 1):
                print(f"{img_path}: person_{i} orientation={p['orientation']} bbox={p['bbox_xyxy']}")


if __name__ == "__main__":
    main()
