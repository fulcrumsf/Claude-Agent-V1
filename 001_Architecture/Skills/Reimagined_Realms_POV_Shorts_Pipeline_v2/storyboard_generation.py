# storyboard_generation.py
#
# v2 revision (2026-08-06): storyboard panels are now generated individually,
# one 9:16 image per beat, instead of one combined multi-panel grid image.
# Reasons: (1) a single AI-generated grid can't be reliably sliced into clean
# per-shot images afterward (unpredictable panel boundaries, resolution loss),
# (2) each panel is now full-resolution and directly usable as that shot's own
# starting image for video generation, not just a planning reference, (3) image
# models render illegible/gibberish text, so panel numbers/captions are never
# baked into the AI-generated image — they're composited on deterministically
# afterward via PIL, in compose_contact_sheet(), for human review only.
#
# POV lock is a parameter, not hardcoded: this channel (Reimagined Realms POV
# Shorts) always wants pov_lock=True, but this pipeline will be duplicated for
# other channels that may want conventional third-person storyboards (static
# cameras, dolly moves) — the lock must stay a per-call choice, not a rule
# baked into this shared function.
#
# v2 revision (2026-08-08): each panel now combines whatever sheets that scene
# actually needs — Main Character Sheet, Featured Extra Character Sheet(s),
# Environment Sheet (a specific location, one labeled SCENE panel used as the
# angle reference), Prop Sheet (front/back/held panels) — attached WHOLE as
# input_urls and named by label in the prompt text. Confirmed via 2 real test
# productions: cropping a panel out of a sheet is unreliable (unpredictable
# boundaries, resolution loss); attaching the full sheet and naming the label
# in text is the only approach that actually worked. A scene's needed sheets
# vary shot to shot (a new location's Environment Sheet, a new named extra's
# Character Sheet, a prop only some scenes carry) so sheet_labels/input_urls
# can be set per-beat in Beat_Table.json, overriding the production-wide
# defaults passed into generate_storyboard.
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from image_generation import generate_image

POV_LOCK_CLAUSE = (
    "Strict first-person POV: the camera IS the character's own eyes, exactly like a body-worn "
    "camera — the character's own face must never be visible in frame. Only their hands, forearms, "
    "and body from the chest down are visible, matching what they themselves would actually see."
)


def build_reference_sheet_note(sheet_labels: list[str] | None) -> str:
    """sheet_labels: plain-text names of the attached reference sheets/panels this scene needs,
    e.g. ["Main Character Sheet", "Ludus Interior Environment Sheet, panel labeled SCENE 3",
    "Scutum Shield — Held from POV panel on the Prop Sheet"]. Never crop a panel out of a sheet —
    the whole sheet image is attached as a reference; this note tells the model which labeled
    part of each attached sheet to actually use.
    """
    if not sheet_labels:
        return ""
    labels = "; ".join(sheet_labels)
    return (
        f" Reference images are attached in full, uncropped. Use them as follows: {labels}."
    )


def build_panel_prompt(
    scene_description: str,
    pov_lock: bool = True,
    world_note: str = "",
    sheet_labels: list[str] | None = None,
) -> str:
    consistency_note = (
        " Match the character's appearance and the environment/world style exactly as shown "
        "in the attached reference image(s)."
        if world_note == ""
        else f" {world_note}"
    )
    reference_note = build_reference_sheet_note(sheet_labels)
    pov_clause = f"{POV_LOCK_CLAUSE} " if pov_lock else ""
    return (
        f"{pov_clause}{scene_description}. A single storyboard frame, vertical 9:16 composition, "
        f"consistent art style and lighting with the rest of this production. "
        f"No text, no numbers, no labels, no captions, no watermark rendered in the image — "
        f"this is a clean visual reference only."
        f"{consistency_note}{reference_note}"
    )


def generate_storyboard_panel(
    scene_description: str,
    output_path: Path,
    pov_lock: bool = True,
    resolution: str = "2K",
    input_urls: list[str] | None = None,
    sheet_labels: list[str] | None = None,
) -> Path:
    prompt = build_panel_prompt(scene_description, pov_lock, sheet_labels=sheet_labels)
    return generate_image(prompt, Path(output_path), "9:16", resolution, input_urls)


def generate_storyboard(
    beats: list[dict],
    output_dir: Path,
    pov_lock: bool = True,
    resolution: str = "2K",
    input_urls: list[str] | None = None,
) -> list[Path]:
    """Each beat may optionally carry its own 'input_urls' (the sheet image URLs this specific
    scene needs) and 'sheet_labels' (plain-text names of which labeled part of each attached
    sheet to use) — these override the production-wide input_urls default per-scene, since a
    new location or a newly-introduced named extra only enters partway through a production.

    Panel images are written into a 'Scenes' subfolder of output_dir, not output_dir directly —
    keeps the many per-scene images separated from the production's reference sheets (character/
    prop/environment sheets) and the compiled Contact_Sheet.png, which stay at output_dir's root.
    Any one-off/manual regeneration of a single scene (e.g. fixing a specific shot after review)
    should target Assets/Images/Scenes/ directly to match this convention.
    """
    output_dir = Path(output_dir)
    scenes_dir = output_dir / "Scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)

    panel_paths = []
    for beat in beats:
        panel_path = scenes_dir / f"Panel_{beat['index']:02d}.png"
        beat_input_urls = beat.get("input_urls", input_urls)
        beat_sheet_labels = beat.get("sheet_labels")
        generate_storyboard_panel(
            beat["description"], panel_path, pov_lock, resolution, beat_input_urls, beat_sheet_labels,
        )
        panel_paths.append(panel_path)
    return panel_paths


def compose_contact_sheet(
    panel_paths: list[Path],
    captions: list[str],
    output_path: Path,
    columns: int = 4,
    panel_width: int = 270,
    caption_height: int = 50,
) -> Path:
    if len(panel_paths) != len(captions):
        raise ValueError(f"panel_paths ({len(panel_paths)}) and captions ({len(captions)}) must be the same length")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    panel_height = int(panel_width * 16 / 9)
    cell_height = panel_height + caption_height
    rows = -(-len(panel_paths) // columns)  # ceil division

    sheet = Image.new("RGB", (columns * panel_width, rows * cell_height), color="white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for i, (panel_path, caption) in enumerate(zip(panel_paths, captions)):
        col = i % columns
        row = i // columns
        x = col * panel_width
        y = row * cell_height

        with Image.open(panel_path) as panel_img:
            panel_img = panel_img.convert("RGB").resize((panel_width, panel_height))
            sheet.paste(panel_img, (x, y))

        text_bbox = draw.textbbox((0, 0), caption, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = x + max(0, (panel_width - text_width) // 2)
        text_y = y + panel_height + (caption_height - (text_bbox[3] - text_bbox[1])) // 2
        draw.text((text_x, text_y), caption, fill="black", font=font)

    sheet.save(output_path)
    return output_path


def main(
    beats_json_path: str,
    out_dir: str,
    pov_lock: bool = True,
    resolution: str = "2K",
    input_urls: list[str] | None = None,
) -> None:
    beats = json.loads(Path(beats_json_path).read_text())
    panel_paths = generate_storyboard(beats, Path(out_dir), pov_lock, resolution, input_urls)
    captions = [f"Scene {b['index']}: {b.get('caption', b['description'][:40])}" for b in beats]
    compose_contact_sheet(panel_paths, captions, Path(out_dir) / "Contact_Sheet.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate one POV-locked 9:16 storyboard panel per beat (individually, not as a "
                     "single combined grid image), plus a deterministically-composited contact sheet "
                     "with captions underneath each panel for review — captions are never baked into "
                     "the AI-generated image itself."
    )
    parser.add_argument(
        "beats_json_path",
        help="Path to a JSON file containing a list of beat dicts, each with 'index' and 'description' "
             "fields (same shape as Beat_Table.json), and optionally a short 'caption' field",
    )
    parser.add_argument("--out_dir", required=True, help="Output directory — Panel_NN.png files are written to out_dir/Scenes/, Contact_Sheet.png stays at out_dir's root")
    parser.add_argument("--no_pov_lock", action="store_true", help="Disable the first-person POV lock (for non-POV channels)")
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    parser.add_argument(
        "--input_urls", nargs="*", default=None,
        help="Optional reference image URLs (character sheet, environment sheet) for consistency",
    )
    args = parser.parse_args()
    main(args.beats_json_path, args.out_dir, not args.no_pov_lock, args.resolution, args.input_urls)
