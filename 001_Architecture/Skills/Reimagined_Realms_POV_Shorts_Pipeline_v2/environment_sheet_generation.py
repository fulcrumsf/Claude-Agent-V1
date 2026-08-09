# environment_sheet_generation.py
#
# v2 revision (2026-08-08): rebuilt from a single production-wide sheet to one
# sheet per LOCATION, with exactly one panel per SCENE that takes place there —
# never merged, never reused, even for scenes in the same room. Confirmed
# failures from the round-1 version: merging two scenes into one shared panel
# silently dropped one scene's actual action (a door-push scene got skipped
# entirely when merged with the "already inside" scene next to it); and a
# panel meant to just be an empty room reference had crowd figures and hands
# creep in. Both are fixed here — panels are strictly one-per-scene and
# strictly people-less, enforced directly in the prompt.
import argparse
import json
from pathlib import Path

from image_generation import generate_image


def build_environment_sheet_prompt(location_name: str, scene_angles: list[dict]) -> str:
    """scene_angles: list of {"scene": int, "description": str}, one entry per scene that
    takes place in this location. Every scene gets its own panel — no merging, no reuse,
    even for scenes in the same room doing similar things (a real human eye never holds
    the exact same framing twice, so two scenes here still need visibly distinct panels).
    """
    panel_lines = "\n".join(
        f"SCENE {sa['scene']}: {sa['description']}" for sa in scene_angles
    )
    return (
        f"A spatial environment reference sheet for {location_name}, full color, photorealistic, "
        f"consistent architectural style and lighting across all {len(scene_angles)} panels as if "
        f"genuinely the same physical location. {len(scene_angles)} panels, each labeled beneath with "
        f"only its scene number in plain text, in a reserved blank margin strip beneath each panel — the "
        f"label must never overlap or cover any part of the panel's own image content. Each panel must "
        f"be a distinct first-person POV moment — "
        f"even scenes that share the same general space must show a visibly different angle, zoom, or "
        f"height, the way a real human eye never holds the exact same framing twice. No panel may reuse "
        f"another panel's exact framing, and no panel may skip ahead to the aftermath of an action instead "
        f"of showing the action's actual physical moment (e.g. a door being pulled/pushed open must show "
        f"the door itself mid-motion, not the already-open room beyond it).\n"
        f"{panel_lines}\n"
        f"CRITICAL: these are pure empty-location camera references. NO people, NO hands, NO arms, NO "
        f"fingers, NO held objects of any kind may appear in ANY panel — not even distant, background, or "
        f"crowd figures. Practice dummies/mannequins are not people and are fine. No watermark."
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
                     "people-less panel per scene that takes place there — never merged, never reused."
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
