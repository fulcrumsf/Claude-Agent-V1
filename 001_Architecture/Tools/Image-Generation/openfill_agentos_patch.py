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
  5. Object growth for prompted local fills (setting grow_object_percent, label "Allow object to grow (%)",
     default 40; preremove_object, default on): LaMa first removes the old object inside the selection,
     the model may paint up to that percent past it, and the layer mask keeps only what changed out
     there (difference mask), so a bigger new object is not clipped and no old object shows behind it.
  6. Room for the new shadow (setting shadow_reach_percent, label "Room for new shadow (%)", default 100):
     the brightest area (window) gives the light direction; the model may paint up to that far past the
     selection on the side away from the light, but only darkening of the same colour (a shadow) is kept
     there, applied to the original pixels, so nothing else nearby moves. 0 = off.
  7. Generative Fill (2026-11-15, Photoshop-style): Filter > Plug-ins > "Generative Fill…" (keyboard Ctrl+G,
     set by the installer when free) opens the panel on Fill with "Nano Banana 2.1 - Generative Fill" picked
     and the cursor in the text box; the Model menu lists local "Qwen Edit 2511 Lightning" second as backup.
     Any Nano Banana engine runs the wide-crop flow (app.py _agentos_wide_fill): a crop of an exact model
     ratio around the selection plus its growth and shadow side (at least 1024 px), the typed instruction
     plus a fixed shadow/keep-everything-else suffix, and the answer composited back through a wide soft
     mask (selection; model pixels where they changed inside the object's room and on plain wall/floor;
     only the light change on textured things such as wood grain, marble or a frame). Pixels outside the
     mask are the original. The last raw answer is kept in openfill/tmp/agentos_wide_last_0.png.
     Test driver: photocraft_genfill_test.py (next to this script).

usage:
  python3 openfill_agentos_patch.py            # check, then apply to the installed copy
  python3 openfill_agentos_patch.py --check    # only say whether it applies / is applied
  python3 openfill_agentos_patch.py --make <pristine release folder>   # rebuild the .patch file
      (no pristine folder? copy the installed app somewhere and reverse the current patch in it:
       patch -p1 -R -d <copy> -i OpenFill_AgentOS_Engines.patch)
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
    "openfill/config.py",
    "openfill/catalog.py",
    "openfill/geometry.py",
    "openfill/workflow.py",
    "openfill/backends/comfy.py",
    "openfill/backends/cloud.py",
    "openfill_photocraft/service.py",
    "openfill_photocraft/menu.py",
    "openfill_photocraft/bar.py",
    "openfill_photocraft/panels.py",
    "openfill_photocraft/web.py",
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


def hide_panel_key() -> None:
    """OpenFill prints the panel address WITH its local key into companion.log; print it without the key
    (the full address is already in page-url.txt). Safe to run every time."""
    f = APP / "openfill_photocraft/__main__.py"
    old = 'print(f"OpenFill for PhotoCraft is running: {url}")'
    new = 'print(f"OpenFill for PhotoCraft is running: {base}/ (address with its key is in page-url.txt)")  # Agent-OS: never log the key'
    try:
        t = f.read_text(encoding="utf-8")
        if old in t:
            f.write_text(t.replace(old, new), encoding="utf-8")
    except OSError:
        pass


def main() -> int:
    if len(sys.argv) > 2 and sys.argv[1] == "--make":
        return make(Path(sys.argv[2]))
    hide_panel_key()
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
