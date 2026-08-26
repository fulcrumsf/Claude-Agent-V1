# environment_sheet_generation.py
#
# Generalized from Reimagined_Realms_POV_Shorts_Pipeline_v2's production-proven
# v2 revision (2026-08-08): one sheet per LOCATION, with exactly one panel per
# SCENE that takes place there — never merged, never reused, even for scenes
# in the same room. Confirmed failures from the round-1 version: merging two
# scenes into one shared panel silently dropped one scene's actual action (a
# door-push scene got skipped entirely when merged with the "already inside"
# scene next to it); and a panel meant to just be an empty room reference had
# crowd figures and hands creep in. Both are fixed here — panels are strictly
# one-per-scene and strictly people-less, enforced directly in the prompt.
import argparse
import json
from pathlib import Path

from image_generation import generate_image


def build_environment_sheet_prompt(location_name: str, scene_angles: list[dict]) -> str:
    """scene_angles: list of {"scene": int, "description": str}, one entry per scene that
    takes place in this location. Every scene gets its own panel — no merging, no reuse,
    even for scenes in the same location doing similar things (a real camera never holds
    the exact same framing twice, so two scenes here still need visibly distinct panels).
    """
    panel_lines = "\n".join(
        f"SCENE {sa['scene']}: {sa['description']}" for sa in scene_angles
    )
    return (
        f"A spatial environment reference sheet for {location_name}, full color, photorealistic, "
        f"consistent style and lighting across all {len(scene_angles)} panels as if genuinely the same "
        f"physical location. {len(scene_angles)} panels, each labeled beneath with only its scene number "
        f"in plain text, in a reserved blank margin strip beneath each panel — the label must never "
        f"overlap or cover any part of the panel's own image content. Each panel must be a distinct "
        f"camera moment — even scenes that share the same general space must show a visibly different "
        f"angle, zoom, or height, the way a real camera never holds the exact same framing twice. No "
        f"panel may reuse another panel's exact framing, and no panel may skip ahead to the aftermath of "
        f"an action instead of showing the action's actual physical moment (e.g. a door being pulled/"
        f"pushed open must show the door itself mid-motion, not the already-open room beyond it).\n"
        f"{panel_lines}\n"
        f"CRITICAL: these are pure empty-location camera references. NO people, NO hands, NO arms, NO "
        f"fingers, NO held objects, and NO animals/creatures may appear in ANY panel — not even distant, "
        f"background, or crowd figures — unless the location reference is itself meant to include a "
        f"stationary environmental creature (e.g. background reef life for an underwater scene); state "
        f"that explicitly per-panel if so, otherwise assume none. Practice dummies/mannequins are not "
        f"people and are fine. No watermark."
    )


def generate_environment_sheet(
    location_name: str,
    scene_angles: list[dict],
    output_path: Path,
    aspect_ratio: str = "16:9",
    resolution: str = "4K",
    input_urls: list[str] | None = None,
) -> Path:
    prompt = build_environment_sheet_prompt(location_name, scene_angles)
    return generate_image(prompt, Path(output_path), aspect_ratio, resolution, input_urls)


def main(
    location_json_path: str,
    out: str,
    aspect_ratio: str = "16:9",
    resolution: str = "4K",
    input_urls: list[str] | None = None,
) -> None:
    data = json.loads(Path(location_json_path).read_text())
    generate_environment_sheet(
        data["location"], data["scenes"], Path(out), aspect_ratio, resolution, input_urls,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a spatial environment reference sheet for ONE location, with exactly one "
                     "people/creature-less panel per scene that takes place there — never merged, never "
                     "reused."
    )
    parser.add_argument(
        "location_json_path",
        help='Path to a JSON file: {"location": "<name>", "scenes": [{"scene": 1, "description": "..."}, ...]}',
    )
    parser.add_argument("--out", required=True, help="Output image file path")
    parser.add_argument("--aspect_ratio", default="16:9", choices=["auto", "1:1", "9:16", "16:9", "4:3", "3:4"])
    parser.add_argument("--resolution", default="4K", choices=["1K", "2K", "4K"])
    parser.add_argument(
        "--input_urls", nargs="*", default=None,
        help="Optional reference image URLs to guide the environment's look (image-to-image mode)",
    )
    args = parser.parse_args()
    main(args.location_json_path, args.out, args.aspect_ratio, args.resolution, args.input_urls)
