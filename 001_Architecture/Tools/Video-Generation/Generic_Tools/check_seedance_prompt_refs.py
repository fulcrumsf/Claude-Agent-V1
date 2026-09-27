#!/usr/bin/env python3
"""Hard gate: every reference image sent to Seedance must be tagged AND used by tag in the action text.

Rules (Tony, 2026-09-20; also in Seedance-Prompting-Guide 'Use the tag as the subject'):
  1. Every uploaded image N has a mapping line near the top: "@Image N = <what it is>" (or "is").
  2. Every timestamped action beat "[00:00-00:03] ..." names its subject(s) by tag, e.g. "@Image 3 walks to the counter".
  3. Every character/creature/prop sheet tag appears in at least one action beat.
  4. The storyboard tag and the environment tag each appear again outside the mapping block (e.g. the scene takes place at @Image 2).
     Keyframe tags (keyframe fallback mode) follow the same rule: each keyframe is referred to again, e.g. in the beat it anchors.
Usage: python3 check_seedance_prompt_refs.py <prompt.md> --refs N
Also called automatically by kie_market_api.generate_seedance_mini() when reference_image_urls are sent."""
import argparse, re, sys
from pathlib import Path

TAG = re.compile(r"@Image\s*(\d+)")
MAP = re.compile(r"^\s*@Image\s*(\d+)\s*(?:=|is)\s*(.+)$", re.IGNORECASE)
BEAT = re.compile(r"^\s*\[\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}\]")


def lint(prompt: str, n_refs: int) -> list[str]:
    lines = prompt.splitlines(); fails = []
    mapping = {}
    for ln in lines:
        m = MAP.match(ln)
        if m and int(m.group(1)) not in mapping:
            mapping[int(m.group(1))] = m.group(2).lower()
    for n in range(1, n_refs + 1):
        if n not in mapping:
            fails.append(f"@Image {n} has no mapping line ('@Image {n} = ...') but {n_refs} images are uploaded")
    beats = [ln for ln in lines if BEAT.match(ln)]
    if not beats:
        fails.append("no timestamped action beats ([00:00-00:03] ...) found")
    for ln in beats:
        if not TAG.search(ln):
            fails.append(f"action beat names no subject by @Image tag: {ln.strip()[:90]}")
    used_in_beats = {int(t) for ln in beats for t in TAG.findall(ln)}
    for n, role in mapping.items():
        if any(k in role for k in ("character", "creature", "prop", "courier", "monkey")) and "storyboard" not in role and "keyframe" not in role and n not in used_in_beats:
            fails.append(f"@Image {n} ({role[:50]}...) is a subject sheet but no action beat uses it")
    body = "\n".join(ln for ln in lines if not MAP.match(ln))
    for n, role in mapping.items():
        if ("storyboard" in role or "environment" in role or "keyframe" in role) and str(n) not in {t for t in TAG.findall(body)}:
            fails.append(f"@Image {n} ({role[:40]}...) is never referred to again outside its mapping line")
    return fails


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("prompt"); ap.add_argument("--refs", type=int, required=True)
    a = ap.parse_args(); text = Path(a.prompt).read_text()
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    f = lint(text, a.refs)
    print("PASS" if not f else "FAIL"); [print(" -", x) for x in f]; sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
