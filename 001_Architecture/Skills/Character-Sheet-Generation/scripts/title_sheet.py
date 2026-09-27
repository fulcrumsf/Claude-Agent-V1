#!/usr/bin/env python3
"""Add the standard dark title bar to a finished character / creature / prop sheet (GLOBAL template, approved 2026-09-20).
Usage: python3 title_sheet.py <sheet.png> --kind character|creature|prop --name "Alexander the Great" --out <titled.png> [--subtitle "..."]
The sheet must already exist (generated in ONE prompt by the skill's own script). --name is the subject's name, e.g. 'Pistol Shrimp 1'."""
import argparse, os, sys, tempfile, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_reference_sheet import render
KINDS = {"character": ("CHARACTER SHEET", "MULTI-ANGLE REFERENCE"), "creature": ("CREATURE SHEET", "MULTI-ANGLE REFERENCE"), "prop": ("PROP SHEET", "PROP REFERENCE")}
ap = argparse.ArgumentParser(); ap.add_argument("sheet"); ap.add_argument("--kind", required=True, choices=KINDS)
ap.add_argument("--name", required=True); ap.add_argument("--out", required=True); ap.add_argument("--subtitle", default="")
a = ap.parse_args(); title, panel = KINDS[a.kind]; img = os.path.abspath(a.sheet)
spec = {"title": title, "headline": a.name.upper(), "subtitle": a.subtitle, "rows": [{"items": [{"type": "panel", "num": 1, "title": panel, "image": img}]}]}
print(render(spec, os.path.dirname(img), a.out))
