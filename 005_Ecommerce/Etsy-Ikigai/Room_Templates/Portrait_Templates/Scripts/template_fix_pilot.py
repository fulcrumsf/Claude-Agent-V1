"""Pilot of the spec's auto-fix on ONE existing template (0 credits, original PSD untouched).

  python pilot_fix.py <rel under Portrait_Templates> <out_dir> [--name <stem>]

1. renders the template's scene (every layer except the art, shadows/glare and foreground) = what the photo shows
2. scene_templates.build_psd on that scene: SAM opening (frame's hard inner edge) + 1.5 px pad, measured black-fill
   shadows with layer masks, glass sheen, card test (raises on failure)
3. writes <out_dir>/<stem>_PROPOSED_FIX_<date>.psd + .json (build facts)
4. runs template_checker.check_psd on the new PSD (results only into that json, not the Portal's results file)
"""
import json
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

PORTAL = Path("/Users/tonymacbook2025/Documents/Agent-OS/005_Ecommerce/Etsy-Ikigai/Portal")
sys.path.insert(0, str(PORTAL))

import numpy as np  # noqa: E402

from app import scene_templates as stp  # noqa: E402
from app import template_checker as tc  # noqa: E402
from app import template_gallery as tg  # noqa: E402
from app.db import load_config  # noqa: E402

DATE = "2026-11-15"

# Pilot guard (proposed code change, NOT in the Portal yet): a "sun line" found without SAM's wall mask is often a
# prop edge (Leather: a fiddle-leaf plant leaf), so it is not trusted; and when the insert is not blank paper (old
# templates whose photo still holds the sample print) its light falloff cannot be measured either -> no Light Shadow.
_orig_key = stp.key_light
_orig_sun = stp.sun_shade


def key_light_guarded(img, insert_q, wall=None):
    if wall is not None:
        return _orig_key(img, insert_q, wall)
    from app import sam_frames as sf
    stp.sun_shade = lambda *a, **k: (None, None)
    try:
        alpha, meta = _orig_key(img, insert_q, None)
    finally:
        stp.sun_shade = _orig_sun
    H, W = img.shape[:2]
    q = np.float32(insert_q)
    Y = img @ stp.W709
    m = sf.poly_coverage(stp._expand(q, -0.08), W, H) > 0.99
    ys, xs = np.nonzero(m)
    A = np.c_[xs + 0.5, ys + 0.5, np.ones_like(xs)].astype("float64")
    coef, *_ = np.linalg.lstsq(A, Y[ys, xs].astype("float64"), rcond=None)
    resid = float(np.std(Y[ys, xs] - A @ coef))
    meta = dict(meta, insert_texture=round(resid, 4), sun_line="not trusted (no SAM wall mask)")
    if resid > 0.03:
        return np.zeros((H, W), "float32"), dict(meta, kind="none", opacity=0.0,
                                                  why="the insert is not blank paper (sample print in the photo)")
    return alpha, meta


stp.key_light = key_light_guarded

if "--relaxed" in sys.argv:
    # pilot of a proposed rule change: SAM's paper edge may sit up to 3 px past the frame's hard inner edge
    # (it ran onto the frame lip); the opening is still the measured hard edge. Uses a scratch copy of sam_frames.py.
    from app import sam_frames as _sf
    _src = Path(_sf.__file__).read_text()
    _old = "        if o < -1.0 or o > reach + 1.0:"
    assert _old in _src, "sam_frames.opening_quad changed; update the --relaxed patch"
    _dir = Path(tempfile.mkdtemp(prefix="samx_"))
    (_dir / "sam_frames.py").write_text(_src.replace(_old, "        if o < -3.0 or o > reach + 1.0:"))
    _sf.__file__ = str(_dir / "sam_frames.py")


def main():
    rel = sys.argv[1]
    out_dir = Path(sys.argv[2])
    s = load_config("settings")
    if "--pad" in sys.argv:
        s["opening_pad_px"] = float(sys.argv[sys.argv.index("--pad") + 1])   # in memory only
    t = next(x for x in tg.scan(s)[0] if x["rel"] == rel)
    psd = t["psd"]
    stem = sys.argv[sys.argv.index("--name") + 1] if "--name" in sys.argv else psd.stem
    st0 = psd.stat()
    work = Path(tempfile.mkdtemp(prefix="pilot_"))
    inf = tc.info(psd, s)
    r = tc.roles(tc.flatten(inf.get("layers")))
    if r["foreground"]:
        print("NOTE foreground layers:", [l["name"] for l in r["foreground"]])
    art_id = r["art"]["id"]
    hide = [l["id"] for l in r["overlays"]] + [l["id"] for l in r["foreground"] if l["shown"]]
    scene = work / "scene.png"
    tc.render(psd, scene, s, hide=hide, art_hidden=True, art_id=art_id)
    # SAM box = the current visible art + 4% (as the checker does)
    so = tc.so_size(psd, s, work)
    from PIL import Image
    for nm, v in (("blk", 0), ("wht", 255)):
        Image.new("RGB", tuple(so), (v, v, v)).save(work / f"c_{nm}.png")
    blk = tc.render(psd, work / "blk.png", s, hide=hide, card=work / "c_blk.png")
    wht = tc.render(psd, work / "wht.png", s, hide=hide, card=work / "c_wht.png")
    V = tc.quad_from_mask((wht - blk).mean(2) > 40)
    x0, y0 = V.min(0)
    x1, y1 = V.max(0)
    pad = 0.04 * max(x1 - x0, y1 - y0)
    box = [x0 - pad, y0 - pad, x1 + pad, y1 + pad]
    (work / "b").mkdir()
    built = stp.build_psd(scene, t["ratio"], work / "b", s, box=box)
    new_psd = out_dir / f"Pilot_Fix_{stem}_{DATE}.psd"
    shutil.copy2(built["psd_tmp"], new_psd)
    shutil.copy2(scene, out_dir / f"Pilot_Fix_{stem}_{DATE}_Scene.png")
    man = {"name": stem, "kind": "rebuilt_from_scene", "psd": new_psd.name, "fixed_from": rel,
           "smart_object_layer": stp.ART, "ratio": t["ratio"],
           **{k: built[k] for k in ("so_px", "so_ratio", "quad_insert", "quad_art", "quad_paper", "opening_pad_px",
                                    "mode", "canvas", "light_from", "insert", "shadows", "card_test")},
           "layers_verified": "black-fill shadows built by scene_templates.make_layers (measured, masked)",
           "base_layer": stp.BASE_NAME, "credits": 0, "approved": False, "pilot": DATE,
           "created": datetime.now().isoformat(timespec="seconds")}
    chk = tc.check_psd(new_psd, t["ratio"], s, so_px=built["so_px"], manifest=man)
    man["checker"] = chk
    (out_dir / f"Pilot_Fix_{stem}_{DATE}.json").write_text(json.dumps(man, indent=1, default=str) + "\n")
    st1 = psd.stat()
    assert (st0.st_size, st0.st_mtime_ns) == (st1.st_size, st1.st_mtime_ns), "ORIGINAL CHANGED"
    print(json.dumps({"new_psd": str(new_psd), "status": chk["status"], "reasons": chk["reasons"],
                      "opening_offsets": chk["measured"].get("opening_offsets"),
                      "card_test": built["card_test"], "work": str(work),
                      "shadows": built["shadows"]}, indent=1, default=str))


if __name__ == "__main__":
    main()
