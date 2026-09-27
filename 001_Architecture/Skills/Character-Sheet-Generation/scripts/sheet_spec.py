#!/usr/bin/env python3
"""JSON-spec-driven sheet builder for CHARACTER, CREATURE and PROP sheets (GLOBAL template, 2026-09-21).

One JSON spec drives one prompt. The fixed style/structure wording lives in the skill scripts (unchanged, approved 2026-09-20);
the spec only fills the per-subject parts, so every sheet in every channel is built the same way. Extra panels the shot's ACTION needs
are added on top of the locked minimum panel set, never instead of it.

Usage:
  python3 sheet_spec.py <spec.json> --validate         # check the spec
  python3 sheet_spec.py <spec.json> --print-prompt     # show the exact prompt (also saves it to spec.prompt_out if set)
  python3 sheet_spec.py <spec.json> --generate         # save prompt FIRST, generate ONE sheet, add the title bar (paid call)

Spec (see Sheet_Spec_Example_*.json in the skill folder):
  sheet_type      "character" | "creature" | "prop"
  name            printed title, e.g. "Bicycle Courier", "Pistol Shrimp 1", "Alexander the Great"
  role            what the subject is ("the bicycle parcel courier")             [character/creature]
  subject_description   look, build, clothing, countable features, props from the beats  [character/creature]
  anatomy_notes   baked-in countable-anatomy paragraph (recommended for creatures)
  hands           "both" (default, person only): two separate close-ups, the character's own LEFT and RIGHT hand+forearm
  extra_panels    [{"title","description"}]  panels this shot's action needs (e.g. holding the battle axe)
  references      [{"file","role"}]  labeled reference images (each role is stated in the prompt)
  props           [{"name","front","back?","held_left?","held_right?"}]           [prop]
  holder_reference {"file","role"}  REQUIRED when any prop has held_left/held_right: the holder's character sheet
  out, prompt_out, title_out   output paths (relative paths resolve from the spec's folder)
"""
import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SK = HERE.parent.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(SK / "Prop-Sheet-Generation" / "scripts"))
from character_sheet_generation import build_character_sheet_prompt  # noqa: E402
from prop_sheet_generation import build_prop_sheet_prompt  # noqa: E402
from image_generation import generate_image  # noqa: E402

TYPES = ("character", "creature", "prop")
HAND_SENTENCE = (" Hands panel: replace the single hands close-up with TWO clearly separate close-ups, the character's own LEFT hand and forearm and "
                 "the character's own RIGHT hand and forearm, each identified by the character's own side, never the picture's left or right (no text on the sheet).")


def validate(s: dict) -> list[str]:
    f = []
    t = s.get("sheet_type")
    if t not in TYPES:
        f.append(f"sheet_type must be one of {TYPES}")
    if not str(s.get("name", "")).strip():
        f.append("name (the printed title) is required")
    if t in ("character", "creature"):
        for k in ("role", "subject_description"):
            if not str(s.get(k, "")).strip():
                f.append(f"{k} is required for a {t} sheet")
        if t == "creature" and not str(s.get("anatomy_notes", "")).strip():
            f.append("WARNING: creature sheets should carry anatomy_notes (countable anatomy)")
    if t == "prop":
        props = s.get("props")
        if not props or not all(p.get("name") and p.get("front") for p in props):
            f.append("prop sheet needs props: [{name, front, ...}]")
        held = any(p.get("held_left") or p.get("held_right") for p in props or [])
        if held and not (s.get("holder_reference") or {}).get("file"):
            f.append("a held panel shows a hand: holder_reference (the holder's character sheet) is REQUIRED so the hand matches the character")
    for r in s.get("references", []) + ([s["holder_reference"]] if s.get("holder_reference") else []):
        if not r.get("file") or not r.get("role"):
            f.append("every reference needs file AND role (its role is stated in the prompt)")
    for p in s.get("extra_panels", []):
        if not p.get("title") or not p.get("description"):
            f.append("every extra panel needs title and description")
    return f


def refs_of(s):
    r = list(s.get("references", []))
    if s.get("holder_reference"):
        r.append(s["holder_reference"])
    return r


def render_prompt(s: dict) -> str:
    refs = refs_of(s)
    pre = "".join(f"Reference image {i} is {r['role']}. " for i, r in enumerate(refs, 1))
    if s["sheet_type"] == "prop":
        props = json.loads(json.dumps(s["props"]))
        if s.get("holder_reference"):
            i = len(refs)
            pre += (f"Every panel that shows a hand, arm or foot must show THIS exact holder from reference image {i} (same skin tone, build, sleeve), not a generic person. ")
        body = build_prop_sheet_prompt(props)
        if not any(pr.get("held_left") or pr.get("held_right") for pr in props):
            # the base prop prompt describes 'held from POV' panels in general terms, and the model invents them (with a generic hand); forbid them when none were asked for
            body += " Do NOT include any panel that shows a hand, arm, glove or person, and no held-from-POV panels: object-only panels."
    else:
        body = build_character_sheet_prompt(s["subject_description"], s["role"], "creature" if s["sheet_type"] == "creature" else "person", s.get("anatomy_notes", ""))
        if s["sheet_type"] == "character" and s.get("hands", "both") == "both":
            body += HAND_SENTENCE
    if s.get("extra_panels"):
        body += " Additional required panels this shot's action needs, in addition to every panel above: " + "; ".join(
            f"({i}) {p['title']}: {p['description']}" for i, p in enumerate(s["extra_panels"], 1)) + "."
    return pre + body


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path); ap.add_argument("--validate", action="store_true"); ap.add_argument("--print-prompt", action="store_true"); ap.add_argument("--generate", action="store_true"); ap.add_argument("--save-prompt", action="store_true", help="also save the prompt file without generating")
    a = ap.parse_args(); base = a.spec.resolve().parent; s = json.loads(a.spec.read_text())
    fails = validate(s)
    for x in fails:
        print(("WARN " if x.startswith("WARNING") else "FAIL ") + x)
    if any(not x.startswith("WARNING") for x in fails):
        sys.exit(1)
    if a.validate and not (a.print_prompt or a.generate):
        print("spec OK"); return
    prompt = render_prompt(s)
    if s.get("prompt_out") and (a.generate or a.save_prompt):
        pp = base / s["prompt_out"]
        if not pp.parent.is_dir():
            sys.exit(f"BLOCKED: folder {pp.parent} does not exist; this tool never creates folders. Create it (with Tony's OK) or fix prompt_out.")
        pp.write_text(f"---\nspec: {a.spec.name}\nsheet_type: {s['sheet_type']}\nname: {s['name']}\nreferences: {[r['file'] for r in refs_of(s)]}\n---\n{prompt}\n")
    if a.print_prompt or not a.generate:
        print(prompt)
    if a.generate:
        out = base / s["out"]
        if out.exists():
            sys.exit(f"BLOCKED: {out} exists; never overwrite. Change 'out'.")
        urls = [str(base / r["file"]) for r in refs_of(s)] or None
        generate_image(prompt, out, "16:9", "2K", urls)  # ONE call with the FULL spec prompt (hands, extra panels, reference roles included)
        print("generated", out)
        if s.get("title_out"):
            kind = {"character": "character", "creature": "creature", "prop": "prop"}[s["sheet_type"]]
            subprocess.run([sys.executable, str(HERE / "title_sheet.py"), str(out), "--kind", kind, "--name", s["name"], "--out", str(base / s["title_out"])], check=True)


if __name__ == "__main__":
    main()
