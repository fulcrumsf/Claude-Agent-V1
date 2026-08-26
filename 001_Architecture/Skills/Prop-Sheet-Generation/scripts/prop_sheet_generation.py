# prop_sheet_generation.py
#
# Generalized from Reimagined_Realms_POV_Shorts_Pipeline_v2's production-proven
# version, built 2026-08-08 after a confirmed failure on the Roman Gladiator
# production: a Prop Sheet showing only a shield's decorative front face caused
# every scene needing that shield in-hand to render it backwards, because a
# held shield's front always faces AWAY from the person carrying it — true POV
# only ever sees the back/strap side with the forearm threaded through it. The
# model had no other reference to work from.
#
# Fix: every prop that could appear on screen needs every orientation that
# could actually appear, explicitly labeled — front, back (for any prop with
# an asymmetric front/back), and a "held from POV" panel showing the actual
# grip/carry position with a hand/arm in frame (the one deliberate exception
# to the "no hands" rule below).
#
# Revised (round 2): a single generic "held" panel produced a wrong thumb
# orientation on a shield's held panel — the shield is always carried in the
# left hand, but the panel gave no hand explicitly, so the model had a 50/50
# chance of rendering right-hand grip anatomy on a left-hand grip. Fixed by
# splitting "held" into "held_left"/"held_right" so a prop's actual carry hand
# is always explicit, never guessed. Also added an explicit margin instruction
# so panel labels never overlap the image content itself.
import argparse
import json
from pathlib import Path

from image_generation import generate_image


def build_prop_sheet_prompt(props: list[dict]) -> str:
    """Each prop dict: {"name": str, "front": str, "back": str | None,
    "held_left": str | None, "held_right": str | None}.
    "back" is omitted only for props with no meaningful distinct back (e.g. a flat coin).
    "held_left"/"held_right" are omitted for whichever hand never actually carries this prop
    on screen — most props are carried in exactly one specific hand by convention (e.g. a
    shield in the left hand, a sword in the right), so only that one hand's panel is needed,
    but it must always say which hand explicitly rather than leaving it generic.
    Front/back panels show the object alone, no hands — the "held" panels are the one
    deliberate exception, showing the object gripped/worn by a hand/arm matching the
    production's character sheet, since that's the actual on-screen carry reference.
    """
    panel_lines = []
    for prop in props:
        panel_lines.append(f"{prop['name']} — Front: {prop['front']}")
        if prop.get("back"):
            panel_lines.append(f"{prop['name']} — Back: {prop['back']}")
        if prop.get("held_left"):
            panel_lines.append(f"{prop['name']} — Held from POV (Left Hand): {prop['held_left']}")
        if prop.get("held_right"):
            panel_lines.append(f"{prop['name']} — Held from POV (Right Hand): {prop['held_right']}")

    panel_block = "\n".join(panel_lines)
    return (
        f"A prop consistency reference sheet for a video production, full color, photorealistic, "
        f"studio-lit, plain neutral grey background. Each panel labeled beneath it in plain text with "
        f"exactly the label given below, in a reserved blank margin strip beneath each panel — the "
        f"label must never overlap or cover any part of the panel's own image content. Front and Back "
        f"panels show the object alone — no hands, no people. Held from POV panels show the object "
        f"gripped or worn by the specific hand named in its label, matching a first-person point-of-view "
        f"exactly as the person carrying it would actually see it — this is the deliberate exception to "
        f"the no-hands rule, since it's establishing the real carry/grip orientation for that exact hand.\n"
        f"{panel_block}\n"
        f"All panels for the same object must be visually consistent with each other in material, wear, "
        f"and color grade, as if genuinely the same physical item. No watermark, no panel borders."
    )


def generate_prop_sheet(
    props: list[dict],
    output_path: Path,
    aspect_ratio: str = "16:9",
    resolution: str = "2K",
    input_urls: list[str] | None = None,
) -> Path:
    prompt = build_prop_sheet_prompt(props)
    return generate_image(prompt, Path(output_path), aspect_ratio, resolution, input_urls)


def main(
    props_json_path: str,
    out: str,
    aspect_ratio: str = "16:9",
    resolution: str = "2K",
    input_urls: list[str] | None = None,
) -> None:
    props = json.loads(Path(props_json_path).read_text())
    generate_prop_sheet(props, Path(out), aspect_ratio, resolution, input_urls)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a prop consistency reference sheet — front/back/held-from-POV panels per "
                     "prop, for any recurring handheld/worn item a character carries, or any recurring "
                     "object a creature interacts with. Never generate only a single 'hero' angle for an "
                     "asymmetric prop (e.g. a shield) — that was a confirmed failure mode."
    )
    parser.add_argument(
        "props_json_path",
        help="Path to a JSON file containing a list of prop dicts, each with 'name', 'front', "
             "optional 'back', and optional 'held_left'/'held_right' description fields — always name "
             "the specific hand, never a generic 'held' field",
    )
    parser.add_argument("--out", required=True, help="Output image file path")
    parser.add_argument("--aspect_ratio", default="16:9", choices=["auto", "1:1", "9:16", "16:9", "4:3", "3:4"])
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    parser.add_argument(
        "--input_urls", nargs="*", default=None,
        help="Optional reference image URLs (e.g. the production's character sheet, for consistent hand/arm in held panels)",
    )
    args = parser.parse_args()
    main(args.props_json_path, args.out, args.aspect_ratio, args.resolution, args.input_urls)
