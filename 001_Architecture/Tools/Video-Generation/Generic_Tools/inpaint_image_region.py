#!/usr/bin/env python3
"""Masked inpainting for a specific image region, via OpenAI's direct
images.edit endpoint (gpt-image-2). Channel-agnostic, global tool -- lives
here (not under a channel folder) so any pipeline can use it, same
convention as the other check_*.py tools.

Built after a real, repeated pattern this session: a generated image is
correct everywhere except one localized defect (an over-extended hedge, a
deformed hand, a stray object), and full regeneration keeps risking new
defects in the parts that were already right. `kie-cli`'s GPT-Image-2
wrapper does not expose a mask parameter (confirmed: `kie-cli gpt_image_2
--help` has no mask/edit option, image-to-image only) -- true masked
editing requires OpenAI's own direct API, not the kie.ai relay.

Region is specified as a fractional bounding box (0-1, matching this
workspace's other coordinate conventions) rather than a hand-drawn mask,
so it stays scriptable and reproducible instead of a one-off manual
Photoshop-style edit.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image


def build_mask(image_path: str, region_frac: tuple[float, float, float, float]) -> Image.Image:
    """region_frac: (x0, y0, x1, y1) in 0-1 fractions of image size -- this
    region is what gets edited (transparent = editable, opaque = preserved),
    matching OpenAI's images.edit mask convention."""
    img = Image.open(image_path)
    w, h = img.size
    mask = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    x0, y0, x1, y1 = (int(region_frac[0] * w), int(region_frac[1] * h),
                       int(region_frac[2] * w), int(region_frac[3] * h))
    editable = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    mask.paste(editable, (x0, y0))
    return mask


def inpaint(image_path: str, prompt: str, region_frac: tuple[float, float, float, float],
            output_path: Path, model: str = "gpt-image-2") -> Path:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    mask = build_mask(image_path, region_frac)
    mask_path = Path("/tmp") / f"_mask_{Path(image_path).stem}.png"
    mask.save(mask_path)

    with open(image_path, "rb") as image_file, open(mask_path, "rb") as mask_file:
        result = client.images.edit(
            model=model,
            image=image_file,
            mask=mask_file,
            prompt=prompt,
        )

    import base64
    image_b64 = result.data[0].b64_json
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(image_b64))
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", help="Path to the source image")
    parser.add_argument("--region", nargs=4, type=float, required=True, metavar=("X0", "Y0", "X1", "Y1"),
                         help="Fractional bounding box (0-1) of the region to edit -- only this area changes")
    parser.add_argument("--prompt", required=True, help="What the edited region should show")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", default="gpt-image-2")
    args = parser.parse_args()

    out = inpaint(args.image, args.prompt, tuple(args.region), args.out, args.model)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
