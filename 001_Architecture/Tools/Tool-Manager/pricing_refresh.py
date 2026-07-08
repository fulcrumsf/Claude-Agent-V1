#!/usr/bin/env python3
"""
Pricing Refresh — runs monthly via cron.
Fetches current pricing from all APIs in pricing_cache.json.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

TOOL_MANAGER = Path(__file__).parent / "tool_manager.py"

def main():
    print(f"[{datetime.now().isoformat()}] Tool Manager — monthly pricing refresh")
    result = subprocess.run(
        [sys.executable, str(TOOL_MANAGER), "refresh"],
        capture_output=False
    )
    if result.returncode == 0:
        print("✅ Refresh complete.")
    else:
        print("✗ Refresh failed — check output above.")

if __name__ == "__main__":
    main()
