# character_sheet_generation.py
import argparse
from pathlib import Path

from image_generation import generate_image


def build_character_sheet_prompt(character_description: str, role: str = "the main character") -> str:
    return (
        f"Character consistency reference sheet for {role}, 3x3 grid of studio-lit photos of the same "
        f"person: {character_description}. Top row: front view, side profile, back view, full body. "
        f"Middle row: neutral expression, focused/exertion expression, close-up on face. "
        f"Bottom row: close-up on hands and forearms, close-up on feet and footwear, close-up on any "
        f"recurring clothing/props/jewelry. Identical lighting, identical skin tone, identical build "
        f"in every panel — this is a consistency reference for a video production, not a narrative scene. "
        f"No text, no labels, no watermark, no panel borders."
    )


def generate_character_sheet(
    character_description: str,
    output_path: Path,
    role: str = "the main character",
    aspect_ratio: str = "1:1",
    resolution: str = "2K",
    input_urls: list[str] | None = None,
) -> Path:
    prompt = build_character_sheet_prompt(character_description, role)
    return generate_image(prompt, Path(output_path), aspect_ratio, resolution, input_urls)


def main(
    character_description: str,
    out: str,
    role: str = "the main character",
    aspect_ratio: str = "1:1",
    resolution: str = "2K",
    input_urls: list[str] | None = None,
) -> None:
    generate_character_sheet(character_description, Path(out), role, aspect_ratio, resolution, input_urls)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a POV character consistency reference sheet (one per distinct character "
                     "per production — main character AND every distinct background/supporting character "
                     "each need their own sheet, or Seedance will duplicate the only face it has across "
                     "everyone in a multi-person shot). Name the output file for what it is, e.g. "
                     "Main_Character_Sheet.png, Background_Worker_Sheet.png — the filename is not "
                     "enforced by this script, it's a naming convention for the human/agent calling it."
    )
    parser.add_argument(
        "character_description",
        help="Description of the character: build, skin tone, era-appropriate clothing/props",
    )
    parser.add_argument("--out", required=True, help="Output image file path — name it for the role, e.g. Main_Character_Sheet.png")
    parser.add_argument("--role", default="the main character", help="e.g. 'the main character', 'a background worker'")
    parser.add_argument("--aspect_ratio", default="1:1", choices=["auto", "1:1", "9:16", "16:9", "4:3", "3:4"])
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    parser.add_argument(
        "--input_urls", nargs="*", default=None,
        help="Optional reference photo URLs of a real person to base the character on (image-to-image mode)",
    )
    args = parser.parse_args()
    main(args.character_description, args.out, args.role, args.aspect_ratio, args.resolution, args.input_urls)
