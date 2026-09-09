#!/usr/bin/env python3
"""Launch the diagnostic CLI with OS-enforced network denial and a clean environment."""
import os
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    if sys.argv[1:] == ["--help"]:
        print("Diagnostics: run_offline.py {runtime,analyze,audit-classes} --config FILE [--out NEW_DIR] [--device cpu|mps]")
        print("Framing: run_offline.py {plan,reframe} --job FILE --out NEW_DIR")
        print("Render a saved plan: run_offline.py render --plan FILE --out NEW_DIR")
        return
    cache = root / ".cache"
    for name in ("tmp", "yolo", "torch", "matplotlib"):
        (cache / name).mkdir(parents=True, exist_ok=True)
    env = {
        "HOME": os.environ["HOME"],
        "PATH": "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "LANG": "en_US.UTF-8",
        "TMPDIR": str(cache / "tmp"),
        "XDG_CACHE_HOME": str(cache),
        "MPLCONFIGDIR": str(cache / "matplotlib"),
        "TORCH_HOME": str(cache / "torch"),
        "YOLO_CONFIG_DIR": str(cache / "yolo"),
        "YOLO_OFFLINE": "1",
        "YOLO_AUTOINSTALL": "0",
        "ULTRALYTICS_SAFE_LOAD": "1",
        "TORCH_FORCE_WEIGHTS_ONLY_LOAD": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
    }
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    script = "reframe.py" if command in {"plan", "render", "reframe"} else "diagnose.py"
    args = ["/usr/bin/sandbox-exec", "-f", str(root / "Offline.sb"),
            str(root / ".venv/bin/python"), "-B", str(root / script), *sys.argv[1:]]
    os.execve(args[0], args, env)


if __name__ == "__main__":
    main()
