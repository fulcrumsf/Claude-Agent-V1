#!/usr/bin/env python3
"""Cut an approved Neon Parcel storyboard sheet into clean keyframe images (Tony, 2026-09-26). No generation, no cost.

Fallback use: when a video made from the storyboard reproduces its grid/tiling (and an edge crop can't save it), the same shot is
re-run with these keyframes as reference images INSTEAD of the storyboard (see seedance2_call.py --keyframes).

How it finds the panels: the Neon Parcel storyboard template puts a white caption band under every frame. Rows that are
near-white across the whole sheet are caption bands/gutters; the image areas are the rows between them. Inside a caption band the
vertical panel dividers are the columns that stay non-white for (almost) the full band height; caption text never does.
If a sheet has no divider lines (pictures touch), each column edge is found from the sharpest left/right jump near the even split point.
Each panel is cut at its own border and keeps its own native ratio (never forced to 16:9). Leftover border lines are shaved off.

Non-destructive: the storyboard is never modified; outputs go beside it as <storyboard stem>_Keyframe_NN.png and existing
outputs are never overwritten. A record of the crop boxes is written to <clip>/Data/<storyboard stem>_Keyframes.json.

Usage: python3 extract_storyboard_keyframes.py <storyboard.png> [--expect 6] [--dry-run]"""
import argparse, json, sys
from pathlib import Path

import numpy as np
from PIL import Image

WHITE = 235          # grayscale value treated as caption-band white
MIN_BAND = 12        # a caption band / gutter is at least this many rows tall
MIN_PANEL = 150      # an image area is at least this many px in each direction


def runs(mask: np.ndarray, min_len: int):
    """Return (start, end_inclusive) runs of True in a 1-D mask that are at least min_len long."""
    out, start = [], None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= min_len:
                out.append((start, i - 1))
            start = None
    if start is not None and len(mask) - start >= min_len:
        out.append((start, len(mask) - 1))
    return out


def shave(g: np.ndarray, box):
    """Shrink a box while its outer row/column is a flat border line (low variance) or white."""
    x0, y0, x1, y1 = box
    for _ in range(12):
        changed = False
        if g[y0, x0:x1].std() < 6 or g[y0, x0:x1].mean() > WHITE: y0 += 1; changed = True
        if g[y1 - 1, x0:x1].std() < 6 or g[y1 - 1, x0:x1].mean() > WHITE: y1 -= 1; changed = True
        if g[y0:y1, x0].std() < 6 or g[y0:y1, x0].mean() > WHITE: x0 += 1; changed = True
        if g[y0:y1, x1 - 1].std() < 6 or g[y0:y1, x1 - 1].mean() > WHITE: x1 -= 1; changed = True
        if not changed:
            break
    return x0 + 1, y0 + 1, x1 - 1, y1 - 1  # 1 px safety margin against anti-aliased border edges


def seam_columns(g: np.ndarray, row_ranges, w: int, n: int):
    """No divider lines (panels touch): near each even split point, pick the column with the biggest left/right jump
    in the image areas. That jump is where one picture ends and the next begins."""
    rows = np.concatenate([np.arange(r0, r1 + 1) for r0, r1 in row_ranges])
    jump = np.abs(np.diff(g[rows], axis=1)).mean(axis=0)   # jump[x] = difference between column x and x+1
    cuts = []
    for k in range(1, n):
        guess = round(k * w / n); lo, hi = max(1, guess - w // 30), min(w - 2, guess + w // 30)
        cuts.append(lo + int(np.argmax(jump[lo:hi])))
    bounds = [0] + [c + 1 for c in cuts] + [w]
    return [(bounds[i] + (2 if i else 0), bounds[i + 1] - 1 - (2 if i < n - 1 else 0)) for i in range(n)]


def find_panels(img: Image.Image, expect: int = 6):
    g = np.asarray(img.convert("L")).astype(float)
    h, w = g.shape
    white_rows = (g > WHITE).mean(axis=1) > 0.55          # caption bands are mostly white across the whole sheet
    bands = runs(white_rows, MIN_BAND)
    # image-area row ranges = gaps between bands (and sheet edges)
    edges = [(-1, -1)] + bands + [(h, h)]
    row_ranges = [(a[1] + 1, b[0] - 1) for a, b in zip(edges, edges[1:]) if (b[0] - 1) - (a[1] + 1) >= MIN_PANEL]
    if not row_ranges or not bands:
        raise SystemExit("Could not find caption bands: this does not look like the Neon Parcel storyboard template.")
    expect_cols = expect // len(row_ranges) if expect % len(row_ranges) == 0 else 1
    # dividers: columns that are non-white through (almost) the full height of the tallest caption band
    b0, b1 = max(bands, key=lambda r: r[1] - r[0])
    nonwhite = (g[b0:b1 + 1] <= WHITE).mean(axis=0) > 0.9
    dividers = runs(nonwhite, 1)
    col_edges = [(-1, -1)] + dividers + [(w, w)]
    col_ranges = [(a[1] + 1, b[0] - 1) for a, b in zip(col_edges, col_edges[1:]) if (b[0] - 1) - (a[1] + 1) >= MIN_PANEL]
    if len(col_ranges) == 1 and expect_cols > 1:
        col_ranges = seam_columns(g, row_ranges, w, expect_cols)
    panels = []
    for (r0, r1) in row_ranges:          # reading order: left to right, top to bottom
        for (c0, c1) in col_ranges:
            panels.append(shave(g, (c0, r0, c1 + 1, r1 + 1)))
    return panels


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("storyboard"); ap.add_argument("--expect", type=int, default=6, help="expected panel count (default 6)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sb = Path(a.storyboard).resolve()
    img = Image.open(sb).convert("RGB")
    panels = find_panels(img, a.expect)
    if len(panels) != a.expect:
        raise SystemExit(f"Found {len(panels)} panels, expected {a.expect}. Nothing written. Check the sheet by eye.")
    outs = [sb.with_name(f"{sb.stem}_Keyframe_{i:02d}.png") for i in range(1, len(panels) + 1)]
    record = {"storyboard": sb.name, "sheet_size": list(img.size), "keyframes": []}
    for p, box in zip(outs, panels):
        x0, y0, x1, y1 = box
        record["keyframes"].append({"file": p.name, "box_xyxy": [x0, y0, x1, y1], "size": [x1 - x0, y1 - y0],
                                    "ratio": round((x1 - x0) / (y1 - y0), 3)})
        print(f"{p.name}: box {box}  {x1 - x0}x{y1 - y0}  ratio {(x1 - x0) / (y1 - y0):.2f}")
    if a.dry_run:
        print("DRY RUN: nothing written."); return
    existing = [p.name for p in outs if p.exists()]
    if existing:
        raise SystemExit(f"Refusing to overwrite existing keyframes: {existing}. Move them to a Rejected/ folder first.")
    for p, box in zip(outs, panels):
        img.crop(box).save(p)
    data = sb.parent / "Data"
    rec = (data if data.is_dir() else sb.parent) / f"{sb.stem}_Keyframes.json"
    if not rec.exists():
        rec.write_text(json.dumps(record, indent=1))
    print(f"Wrote {len(outs)} keyframes beside the storyboard; record: {rec}")


if __name__ == "__main__":
    main()
