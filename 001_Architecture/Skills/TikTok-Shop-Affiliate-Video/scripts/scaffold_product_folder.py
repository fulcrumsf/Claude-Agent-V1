#!/usr/bin/env python3
"""
scaffold_product_folder.py — Neon Parcel TikTok Shop Creator per-product scaffolder.

Creates the folder tree for one product under
005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Videos/
per the approved design spec (2026-07-11-Neon-Parcel-Tiktok-Shop-Creator-Pipeline-Design.md).

Usage:
  python3 scaffold_product_folder.py <videos_dir> <product_number> "<Product Name>"
"""
import re
import sys
from pathlib import Path

TYPED_FOLDERS = [
    "Edit",
    "Compliance/Vision-Scan",
    "Compliance/Transcript-Scan",
    "Package",
]

INTAKE_TEMPLATE = """---
title: "{product_name} — Intake"
type: intake
created: {created_date}
---

# {product_name}

- **Source Ingest folder:** {ingest_folder}
- **Pipeline:** TikTok Shop Creator (vertical, NeonParcel TikTok account)
- **Number of TikTok cuts planned:** 3 (distinct edits, shared footage pool)
- **Restricted category (Health/Beauty/Weight-Management)?:** TBD — confirm before Phase 1 compliance scan
"""


def slugify(name: str) -> str:
    collapsed = re.sub(r"\s+", " ", name.strip())
    return collapsed.replace(" ", "-")


def scaffold(base_dir: Path, product_number: int, product_name: str, ingest_folder: str = "TBD") -> Path:
    from datetime import date

    product_dir = base_dir / f"{product_number:04d}_{slugify(product_name)}"
    product_dir.mkdir(parents=True, exist_ok=True)
    for folder in TYPED_FOLDERS:
        (product_dir / folder).mkdir(parents=True, exist_ok=True)

    intake_path = product_dir / "Intake.md"
    if not intake_path.exists():
        intake_path.write_text(INTAKE_TEMPLATE.format(
            product_name=product_name,
            created_date=date.today().isoformat(),
            ingest_folder=ingest_folder,
        ))

    return product_dir


def main():
    if len(sys.argv) < 4:
        sys.exit('Usage: scaffold_product_folder.py <videos_dir> <product_number> "<Product Name>" [ingest_folder]')
    videos_dir = Path(sys.argv[1]).resolve()
    number = int(sys.argv[2])
    name = sys.argv[3]
    ingest_folder = sys.argv[4] if len(sys.argv) > 4 else "TBD"
    product_dir = scaffold(videos_dir, number, name, ingest_folder)
    print(f"Scaffolded {product_dir}")


if __name__ == "__main__":
    main()
