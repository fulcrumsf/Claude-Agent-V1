"""Render variants from a v2 template PSD. python render_v2.py <tpl_dir> <art> <out_prefix> <variants.json>
variant: {"name", "frame": oak|walnut|black|white, "mat": bool, "wall": null|"Sage"|..., "glass": bool, "soft": bool}"""
import json, subprocess, sys, time
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Portal"))   # Etsy-Ikigai/Portal
from app.mockups import fit_art  # noqa: E402

def c(cmd, p): return ["--cmd", cmd, "--params", json.dumps(p)]
def vis(n, on): return c("layer.setProps", {"layer": n, "visible": bool(on)})

def variant_args(v, meta):
    a = []
    for f in ("Oak", "Walnut", "Black", "White"):
        a += vis(f"Frame {f}", v["frame"].lower() == f.lower())
    a += vis("MAT", v["mat"]) + vis("Place Artwork Here (Mat)", v["mat"]) + vis("Place Artwork Here", not v["mat"])
    for p in meta["paints"]:
        a += vis(f"Wall {p}", v.get("wall") == p)
    if meta.get("soft"):
        a += vis("Soft cast shadow", v.get("soft", False))
    a += vis("GLASS", v.get("glass", True))
    return a

def main():
    tpl, art, prefix = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    variants = json.loads(Path(sys.argv[4]).read_text())
    meta = json.loads((tpl / "template.json").read_text())
    fitted = tpl / "art_fitted.png"
    fit_art(art, tuple(meta["smart_object_px"]), fitted)
    filled = tpl / "Room_Template_filled.psd"
    r = subprocess.run(["photocraft-cli", "run", str(tpl / "Room_Template.psd"), *c("layer.select", {"name": "Place Artwork Here"}),
                        *c("layer.smartObjects.replaceContents", {"path": str(fitted.resolve())}), "--out", str(filled)], capture_output=True, text=True)
    if r.returncode: print(r.stderr[-500:])
    for v in variants:
        png = prefix.parent / f"{prefix.name}{v['name']}.png"
        t = time.time()
        r = subprocess.run(["photocraft-cli", "run", str(filled), *variant_args(v, meta), "--out", str(png)], capture_output=True, text=True)
        if r.returncode: print(v["name"], "FAILED", r.stderr[-500:]); continue
        Image.open(png).convert("RGB").save(png.with_suffix(".jpg"), "JPEG", quality=92)
        print(v["name"], round(time.time() - t, 1), "s")

if __name__ == "__main__":
    main()
