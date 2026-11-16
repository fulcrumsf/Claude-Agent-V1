#!/usr/bin/env python3
"""Re-apply Agent-OS's small patch to OpenFill for PhotoCraft (after every OpenFill update).

The patch (OpenFill_AgentOS_Engines.patch, next to this script) adds, on top of OpenFill 0.2.6:
  1. "Qwen Edit 2511 Lightning - fast, 4 steps (local)" in the Model menu: the Lightning 4-step LoRA
     at 4 steps, cfg 1.0 (catalog entry + app.py sampling() + workflow.py build_qwen_edit()).
  2. The current Hugging Face size/SHA-256 of qwen-image-edit-2511-Q4_K_M.gguf (unsloth re-uploaded it;
     OpenFill 0.2.6's catalog still has the old one and would call the file wrong).
  3. "FLUX.2 klein 4B - fastest local edit, 4 steps (local)" (Apache-2.0): a new flux2_klein_edit
     template (catalog.py, geometry.py, workflow.py, app.py sampling, comfy.py timeout).
  4. Cloud engines in the same Model menu, per job (kie.ai Nano Banana Pro / 2.1 / Ideogram 3 Edit,
     fal.ai Qwen inpaint / Nano Banana Pro). Keys are read from ~/.env-secrets (KIE_API_KEY,
     FAL_AI_API_KEY), never printed. The result is always put back through the selection mask.

usage:
  python3 openfill_agentos_patch.py            # check, then apply to the installed copy
  python3 openfill_agentos_patch.py --check    # only say whether it applies / is applied
  python3 openfill_agentos_patch.py --make <pristine release folder>   # rebuild the .patch file
After applying: quit and reopen "PhotoCraft with OpenFill" (the companion reads the code at start).
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PATCH = HERE / "OpenFill_AgentOS_Engines.patch"
APP = Path.home() / "Library/Application Support/OpenFill for PhotoCraft/app"
FILES = [
    "models/catalog.json",
    "openfill/app.py",
    "openfill/catalog.py",
    "openfill/geometry.py",
    "openfill/workflow.py",
    "openfill/backends/comfy.py",
    "openfill/backends/cloud.py",
    "openfill_photocraft/service.py",
    "openfill_photocraft/bar.py",
    "openfill_photocraft/static/index.html",
]


def run_patch(*extra):
    return subprocess.run(["patch", "-p1", "-N", "-d", str(APP), *extra, "-i", str(PATCH)],
                          capture_output=True, text=True)


def make(pristine: Path) -> int:
    out = []
    for f in FILES:
        r = subprocess.run(["diff", "-u", "--label", f"a/{f}", "--label", f"b/{f}", str(pristine / f), str(APP / f)],
                           capture_output=True, text=True)
        out.append(r.stdout)
    PATCH.write_text("".join(out), encoding="utf-8")
    print(f"wrote {PATCH} ({sum(1 for o in out if o)} files changed)")
    return 0


def main() -> int:
    if len(sys.argv) > 2 and sys.argv[1] == "--make":
        return make(Path(sys.argv[2]))
    if not APP.is_dir():
        print(f"OpenFill is not installed at {APP}")
        return 1
    if "Agent-OS patch" in (APP / "openfill/app.py").read_text(encoding="utf-8"):
        print("already applied")
        return 0
    dry = run_patch("--dry-run")
    if dry.returncode != 0:
        print("the patch does not apply cleanly to this OpenFill version; nothing was changed:\n" + dry.stdout[-2000:])
        return 2
    if "--check" in sys.argv:
        print("applies cleanly")
        return 0
    r = run_patch("-b", "-z", ".pre-agentos")  # keeps each original as <file>.pre-agentos
    print(r.stdout[-2000:] or "applied")
    print('Now quit and reopen "PhotoCraft with OpenFill".')
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
