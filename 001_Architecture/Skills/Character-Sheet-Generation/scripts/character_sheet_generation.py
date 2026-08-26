# character_sheet_generation.py
#
# Generalized from Reimagined_Realms_POV_Shorts_Pipeline_v2's production-proven
# version (built 2026-08-06, confirmed working across multiple productions) to
# also cover non-human recurring subjects — animals/creatures for channels like
# Anomalous Wild, not just POV human characters.
#
# Revised 2026-08-16 after Tony's direct feedback on the first real Anomalous
# Wild test (Mantis_Shrimp_Main_Character_Sheet.png): the original rigid 1:1
# 3x3 grid clipped the full-body panels — a square cell isn't wide/tall enough
# to fit an elongated subject's whole body without cropping it. Fixed by:
# (a) defaulting to 16:9 instead of 1:1, and (b) instructing the model that
# panels do not need to be uniform equal-sized grid cells — panels needing a
# full body shown in full should get more room than a tight close-up panel.
# This was not sourced from any external research (no reference found on
# character-sheet layout/aspect-ratio conventions specifically) — it's a
# direct correction from real output review, now locked in as the default.
#
# Revised 2026-08-17 after a full storyboard set kept collapsing into
# near-identical close-ups on one feature: the original sheet had no
# environment/movement/context poses at all, only static studio-style
# turnaround + close-up panels — giving Storyboard-Generation nothing to draw
# on for the wide/establishing/b-roll shots its shot-variety rule now
# requires. Added an environment/movement pose panel for creature subjects.
# Also added `anatomy_notes` — a written paragraph baked directly into the
# sheet image (not just the metadata description), inspired by professional
# game-style character reference sheets that pair visual turnarounds with a
# written attributes block. Confirmed on this project that GPT-Image-2 renders
# baked-in text cleanly, so putting the countable-anatomy facts (e.g. "two
# independently-rotating eyestalks") directly on the reference image itself
# gives later generations that reference this sheet textual grounding, not
# just a visual one, for exactly the anatomy the earlier storyboard set kept
# getting wrong (dropped eyes, uncertain limb counts).
import argparse
from pathlib import Path

from image_generation import generate_image


def build_character_sheet_prompt(
    subject_description: str,
    role: str = "the main character",
    subject_type: str = "person",
    anatomy_notes: str = "",
) -> str:
    """subject_type: 'person' (default, matches original RR wording) or 'creature'
    (adapts the row descriptions to what actually needs to stay consistent on an
    animal — markings/coloration/anatomy instead of skin tone/clothing).

    anatomy_notes: a short written paragraph of countable/key anatomical facts
    (e.g. "Two independently-rotating compound eyestalks, each on its own
    movable joint. One pair of raptorial claws folded beneath the body at
    rest.") — baked into the sheet image as real text, not just passed as
    prompt context that disappears after this one call. Strongly recommended
    for any subject_type='creature' sheet; required if the subject has any
    paired/repeated feature a later generation could drop or miscount."""
    if subject_type == "creature":
        middle_row = (
            "Middle row: resting/neutral pose, active/alert pose, close-up on the eyes "
            "and face."
        )
        bottom_row = (
            "Bottom row: close-up on any distinguishing markings or coloration, close-up "
            "on the key anatomical feature relevant to this production (e.g. claw, fin, "
            "lure), close-up on skin/scale/fur texture."
        )
        context_row = (
            "Additional row: a movement/environment pose showing the full subject in "
            "motion within its natural setting (e.g. swimming, walking, crawling across "
            "its substrate) — this exists specifically to give later storyboard "
            "generations real wide/establishing/b-roll reference material, not just "
            "close-up study panels."
        )
        consistency_line = "Identical lighting, identical coloration and markings, identical proportions in every panel"
    else:
        middle_row = (
            "Middle row: neutral expression, focused/exertion expression, close-up on face."
        )
        bottom_row = (
            "Bottom row: close-up on hands and forearms, close-up on feet and footwear, "
            "close-up on any recurring clothing/props/jewelry."
        )
        context_row = (
            "Additional row: a full-body pose in a natural setting/environment relevant "
            "to this production — wide/establishing reference material, not just "
            "close-up study panels."
        )
        consistency_line = "Identical lighting, identical skin tone, identical build in every panel"

    if anatomy_notes:
        anatomy_block = (
            f" In a reserved text panel on the sheet (clean white background, legible "
            f"printed text, does not overlap any image panel), write the following "
            f"anatomy notes exactly as given, as a short paragraph: \"{anatomy_notes}\" "
            f"No other text, labels, or watermark anywhere else on the sheet."
        )
    else:
        anatomy_block = " No text, no labels, no watermark."

    return (
        f"Character consistency reference sheet for {role}, a grid of studio-lit photos of the same "
        f"subject: {subject_description}, laid out in a 16:9 frame. Top row: front view, side profile, "
        f"back view, full body — give the full-body panel enough width/height to show the ENTIRE body "
        f"uncropped; do not force it into a small square cell if that would clip any part of the subject. "
        f"Panels do not need to be uniform equal-sized grid squares — vary each panel's size to fit what "
        f"it actually needs to show. "
        f"{middle_row} "
        f"{bottom_row} "
        f"{context_row} "
        f"{consistency_line} — this is a consistency reference for a video production, not a narrative "
        f"scene.{anatomy_block} No panel borders."
    )


def generate_character_sheet(
    subject_description: str,
    output_path: Path,
    role: str = "the main character",
    subject_type: str = "person",
    aspect_ratio: str = "16:9",
    resolution: str = "2K",
    input_urls: list[str] | None = None,
    anatomy_notes: str = "",
) -> Path:
    prompt = build_character_sheet_prompt(subject_description, role, subject_type, anatomy_notes)
    return generate_image(prompt, Path(output_path), aspect_ratio, resolution, input_urls)


def main(
    subject_description: str,
    out: str,
    role: str = "the main character",
    subject_type: str = "person",
    aspect_ratio: str = "16:9",
    resolution: str = "2K",
    input_urls: list[str] | None = None,
    anatomy_notes: str = "",
) -> None:
    generate_character_sheet(
        subject_description, Path(out), role, subject_type, aspect_ratio, resolution, input_urls, anatomy_notes
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a character/creature consistency reference sheet (one per distinct "
                     "recurring subject per production — every distinct main AND background/supporting "
                     "character or creature needs its own sheet, or the video model will duplicate the "
                     "only identity it has across everyone/everything in a multi-subject shot). Name the "
                     "output file for what it is, e.g. Main_Character_Sheet.png, Shark_1_Character_Sheet.png "
                     "— the filename is not enforced by this script, it's a naming convention for the "
                     "human/agent calling it."
    )
    parser.add_argument(
        "subject_description",
        help="Description of the subject: for a person — build, skin tone, era-appropriate clothing/props; "
             "for a creature — species, coloration, markings, size, distinguishing anatomy",
    )
    parser.add_argument("--out", required=True, help="Output image file path — name it for the role")
    parser.add_argument("--role", default="the main character", help="e.g. 'the main character', 'a background worker', 'the recurring shark'")
    parser.add_argument("--subject_type", default="person", choices=["person", "creature"])
    parser.add_argument("--aspect_ratio", default="16:9", choices=["auto", "1:1", "9:16", "16:9", "4:3", "3:4"])
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    parser.add_argument(
        "--input_urls", nargs="*", default=None,
        help="Optional reference photo URLs (a real person, or a real reference photo of the species) to base the sheet on (image-to-image mode)",
    )
    parser.add_argument(
        "--anatomy_notes", default="",
        help="Short written paragraph of countable/key anatomical facts, baked into the sheet as real "
             "text (e.g. 'Two independently-rotating compound eyestalks, each on its own movable joint.'). "
             "Strongly recommended for subject_type=creature; leave blank to fall back to the old "
             "no-text-on-sheet behavior.",
    )
    args = parser.parse_args()
    main(args.subject_description, args.out, args.role, args.subject_type, args.aspect_ratio, args.resolution, args.input_urls, args.anatomy_notes)
