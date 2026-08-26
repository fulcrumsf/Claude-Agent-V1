#!/usr/bin/env python3
"""
scaffold_new_production.py — Anomalous Wild new-production folder scaffolder.

Matches Reimagined Realms' actual Pompeii folder structure (confirmed from
disk 2026-07-06): Scripts/, Production/, Images/, Video_Clips/, Narration_Audio/,
Audio_Stems/, Assembly/ (versions live INSIDE Assembly as V1/, V2/... not as
a sibling folder), Package/.

Anomalos_Wild_End-Card_Hero.mp4 is a FIXED, hardcoded asset for every
Anomalous Wild video — never generated or chosen per-video.

Usage:
  python3 scaffold_new_production.py <new_production_folder>
"""
import sys
from pathlib import Path

END_CARD_PATH = Path(
    "/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/"
    "002_Channels/001_Anomalous-Wild/Brand_Assets/End_Card/Anomalos_Wild_End-Card_Hero.mp4"
)

TYPED_FOLDERS = [
    "Scripts", "Production", "Images", "Video_Clips",
    "Narration_Audio", "Audio_Stems", "Assembly", "Package", "Data",
]

GENERATION_LOG_TEMPLATE = """{
  "production": "",
  "channel": "Anomalous Wild",
  "assets": []
}
"""

REPORT_CARD_TEMPLATE = """---
title: "Video Report Card"
type: report
domain: video-production
tags: [report, video-production, content-creation]
---

# Video Report Card
**Channel:**
**Video:**
**Grade:**
**Previous Grade:**
**Review Date:**

---

## Critique Notes

(Filled in after Tony reviews the finished video.)
"""


def scaffold(production_root: Path):
    if not END_CARD_PATH.exists():
        raise FileNotFoundError(f"Locked end card asset missing: {END_CARD_PATH}")
    production_root.mkdir(parents=True, exist_ok=True)
    for folder in TYPED_FOLDERS:
        (production_root / folder).mkdir(exist_ok=True)
    (production_root / "Production" / "end_card_reference.txt").write_text(str(END_CARD_PATH))
    data_dir = production_root / "Data"
    generation_log = data_dir / "Generation_Log.json"
    if not generation_log.exists():
        generation_log.write_text(GENERATION_LOG_TEMPLATE)
    report_card = data_dir / "Report_Card.md"
    if not report_card.exists():
        report_card.write_text(REPORT_CARD_TEMPLATE)


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: scaffold_new_production.py <new_production_folder>")
    scaffold(Path(sys.argv[1]).resolve())
    print(f"Scaffolded {sys.argv[1]} with {len(TYPED_FOLDERS)} typed folders + locked end card reference")


if __name__ == "__main__":
    main()
