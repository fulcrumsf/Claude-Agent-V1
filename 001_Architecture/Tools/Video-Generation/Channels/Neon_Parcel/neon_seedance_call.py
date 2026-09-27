#!/usr/bin/env python3
"""Neon Parcel entry point. Delegates to the GLOBAL Seedance 2 gate (Generic_Tools/seedance2_call.py), which every channel uses.
Usage is identical: python3 neon_seedance_call.py <shot_dir> <prompt.md> --version vN --shot-id ID --out Data/X.mp4 [--dry-run]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "Generic_Tools"))
from seedance2_call import main  # noqa: E402

if __name__ == "__main__":
    if "--channel" not in sys.argv:
        sys.argv += ["--channel", "Neon_Parcel"]
    main()
