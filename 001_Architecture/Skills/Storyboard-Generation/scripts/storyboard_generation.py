# storyboard_generation.py
#
# Locked 2026-08-16 after two real production tests on 0002_Mantis_Shrimp_Color_Vision:
# - Test 1 (Scene_01, a near-static macro-eye shot): worked, but every frame looked
#   too similar to prove the template out on real motion.
# - Test 2 (Scene_07, the 12-frame strike sequence): confirmed the template — clean,
#   legible text in every panel, correct frame-number badges, real per-frame visual
#   progression (wind-up -> release -> cavitation -> flash -> aftermath), shot-type
#   variety actually visible (wide vs extreme close-up), consistent character/color
#   throughout. Tony approved this as the locked template.
#
# Key design decision, confirmed by direct A/B comparison against a real YouTube
# tutorial's prompt: structure the prompt as three separate labeled blocks (Scene /
# Visual style / Storyboard sequence) plus a closing consistency directive, rather
# than repeating style+content+camera instructions inside every frame line. The
# repetitive per-frame approach produced frozen, near-identical panels; the
# three-block approach produced real per-frame motion and shot variety.
#
# CRITICAL — this file locks the STRUCTURE only. `scene_description` and
# `visual_style` are always caller-supplied, per-production/per-channel fields —
# never hardcode a specific channel's look into this script. Reimagined Realms,
# Anomalous Wild, and any future channel all call this the same way, each with
# their own scene_description/visual_style content.
import argparse
import json
from pathlib import Path

from image_generation import generate_image


def compute_frame_count(duration_s: float, min_frames: int = 6, max_frames: int = 12, seconds_per_frame: float = 1.25) -> int:
    """Frame count is derived from the scene's actual duration, never guessed or
    fixed — roughly one frame per 1.25s of scene, clamped to [6, 12]. A short
    scene gets the 6-frame floor; a long, high-motion scene gets the 12-frame
    ceiling."""
    raw = round(duration_s / seconds_per_frame)
    return max(min_frames, min(max_frames, raw))


def build_storyboard_prompt(spec: dict) -> str:
    """spec keys: frame_count, panel_convention, scene_description, visual_style,
    frames (list of {"frame": int, "action": str}), consistency_directive.
    scene_description and visual_style are always caller-supplied — this function
    never invents or defaults them, since they're channel-specific by design."""
    lines = [
        f"Create a storyboard grid with {spec['frame_count']} frames total, {spec['panel_convention']}",
        "",
        f"Scene: {spec['scene_description']}",
        "",
        f"Visual style: {spec['visual_style']}",
        "",
        "Storyboard sequence:",
        "",
    ]
    for f in spec["frames"]:
        lines.append(f["action"])
    lines.append("")
    lines.append(spec["consistency_directive"])
    return "\n".join(lines)


DEFAULT_PANEL_CONVENTION = (
    "clean professional storyboard grid, thin black borders separating panels, "
    "bold sans-serif frame number badge in the top-left corner of each panel, "
    "short one-line caption in a plain white strip beneath each panel."
)

DEFAULT_CONSISTENCY_DIRECTIVE = (
    "Keep the storyboard readable and visually consistent. Every panel must show "
    "the same subject with identical coloring, markings, and proportions, as if "
    "part of one continuous shot. Use clean composition and precise detail. The "
    "sequence should read as one continuous event from start to finish."
)


def build_spec(
    scene_id: str,
    duration_s: float,
    scene_description: str,
    visual_style: str,
    frame_actions: list[str],
    panel_convention: str = DEFAULT_PANEL_CONVENTION,
    consistency_directive: str = DEFAULT_CONSISTENCY_DIRECTIVE,
) -> dict:
    """Build a full spec dict. frame_actions must already be sized to
    compute_frame_count(duration_s) — this function does not silently pad or
    truncate a mismatched list, since getting the beat count right per scene is
    the caller's job (derived from the shot list), not something to paper over."""
    frame_count = compute_frame_count(duration_s)
    if len(frame_actions) != frame_count:
        raise ValueError(
            f"{scene_id}: expected {frame_count} frame actions for a {duration_s}s scene "
            f"(per compute_frame_count), got {len(frame_actions)}. Fix the caller's frame list."
        )
    return {
        "scene_id": scene_id,
        "scene_duration_s": duration_s,
        "frame_count": frame_count,
        "scene_description": scene_description,
        "visual_style": visual_style,
        "panel_convention": panel_convention,
        "frames": [{"frame": i + 1, "action": a} for i, a in enumerate(frame_actions)],
        "consistency_directive": consistency_directive,
    }


def generate_storyboard(
    spec: dict,
    output_path: Path,
    reference_image_urls: list[str] | None = None,
    aspect_ratio: str = "16:9",
    resolution: str = "4K",
) -> Path:
    prompt = build_storyboard_prompt(spec)
    return generate_image(prompt, Path(output_path), aspect_ratio, resolution, reference_image_urls)


def main(spec_json_path: str, out: str, reference_image_urls: list[str] | None = None) -> None:
    spec = json.loads(Path(spec_json_path).read_text())
    generate_storyboard(spec, Path(out), reference_image_urls)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a channel-agnostic storyboard sheet from a JSON spec (see build_spec()). "
                     "The prompt STRUCTURE is fixed (Scene / Visual style / Sequence / consistency "
                     "directive blocks) — scene_description and visual_style are always caller-supplied "
                     "so this works for any channel."
    )
    parser.add_argument("spec_json_path", help="Path to a JSON spec (see build_spec() for the schema)")
    parser.add_argument("--out", required=True, help="Output image file path")
    parser.add_argument(
        "--reference_image_urls", nargs="*", default=None,
        help="Reference image URLs (e.g. the production's character sheet) for consistency",
    )
    args = parser.parse_args()
    main(args.spec_json_path, args.out, args.reference_image_urls)
