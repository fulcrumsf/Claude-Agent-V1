"""G0 stand-in gate (Pipeline_Docs/Slot_Set_Planner_Plan.md section 12 + Tony's decision 2026-11-19): before the
planner relies on TIGHT shots, existing scenes are cropped so the frame fills 55% / 65% of a 4:3 picture (plus one
"small in wide" at 18%) and run through the REAL builder: build_psd (SAM 2) -> render_psd (PhotoCraft) -> guard_quad
-> art-area gate -> template checker. A warm-wall stand-in with the insert RECOLOURED blue (and its bounce turned
blue) runs the blue-marker path: builder + despill + gate. Free: no kie.ai, no Gemini (the SAM box comes from the
source template), nothing is written into the template library.

Slow (SAM + PhotoCraft, about a minute per stand-in) and machine-bound, so it only runs with PORTAL_G0=1 and the SAM
venv + photocraft-cli present:  PORTAL_G0=1 PORTAL_G0_OUT=<folder> pytest -q -s tests/test_g0_standins.py"""
import json
import math
import os
import shutil
from pathlib import Path

import numpy as np
import pytest

from app import production, room_templates as rt, scene_templates as stp, template_checker as tc
from app.scene_templates import card_verify as REAL_CARD_VERIFY, sam_detect as REAL_SAM_DETECT
from app.template_checker import sam_opening as REAL_SAM_OPENING

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "Room_Templates" / "Portrait_Templates"
PRINTS = ROOT / "Designs" / "00121-Book Club Cat" / "01-Printables"
SOURCES = {
    "office_canvas": "005_Ratio_11x14/005_Office/001_Scandinavian/AI_Office_Scandinavian_20261118_225742",
    "bedroom_canvas": "005_Ratio_11x14/002_Bedroom/001_Boho_Colorful/AI_Bedroom_Boho_20261118_002116",
    "office_mat": "002_Ratio_2x3/005_Office/001_Mid_Century/AI_Office_Mid_Century_20261119_174105"}
FRAME_K = {"canvas": 1.08, "mat": 1.35, "frame": 1.1}     # outer frame height / art quad height (estimate)
CASES = [(src, frac, None) for src in SOURCES for frac in (0.55, 0.65)] + [("office_mat", 0.18, None),
                                                                          ("bedroom_canvas", 0.55, "blue"),
                                                                          ("office_mat", 0.55, "blue")]
W_OUT, H_OUT = 2400, 1792

needs = pytest.mark.skipif(
    os.environ.get("PORTAL_G0") != "1" or not Path(os.path.expanduser("~/.cache/ikigai-sam/bin/python")).is_file()
    or not shutil.which("photocraft-cli") or not LIB.is_dir() or not PRINTS.is_dir(),
    reason="G0 stand-ins run only with PORTAL_G0=1, the SAM venv, photocraft-cli and the live template library")


def standin(src, frac, out_png):
    """Crop / pad the source scene so the estimated frame fills `frac` of a 4:3 picture; resample to 2400x1792.
    Returns (manifest, quad in the stand-in, SAM box in the stand-in)."""
    import cv2
    from PIL import Image
    tdir = LIB / SOURCES[src]
    man = json.loads((tdir / "template.json").read_text())
    rgb = np.asarray(Image.open(tdir / man["scene"]).convert("RGB"))
    q = np.float32(man["quad_art"])
    frame_h = (q[:, 1].max() - q[:, 1].min()) * FRAME_K.get(man.get("presentation") or "frame", 1.1)
    ch = frame_h / frac
    cw = ch * 4 / 3
    cx, cy = q[:, 0].mean(), q[:, 1].mean()
    x0, y0 = int(round(cx - cw / 2)), int(round(cy - ch / 2))
    x1, y1 = int(round(cx + cw / 2)), int(round(cy + ch / 2))
    H, W = rgb.shape[:2]
    pad = [max(0, -y0), max(0, y1 - H), max(0, -x0), max(0, x1 - W)]
    big = cv2.copyMakeBorder(rgb, pad[0], pad[1], pad[2], pad[3], cv2.BORDER_REPLICATE) if any(pad) else rgb
    crop = big[y0 + pad[0]:y1 + pad[0], x0 + pad[2]:x1 + pad[2]]
    s = W_OUT / crop.shape[1]
    out = cv2.resize(crop, (W_OUT, H_OUT), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    Image.fromarray(out).save(out_png)
    sx, sy = W_OUT / crop.shape[1], H_OUT / crop.shape[0]
    tq = (q - np.float32([x0, y0])) * np.float32([sx, sy])
    box = (man.get("insert") or {}).get("sam", {}).get("box")
    tb = None if box is None else [(box[0] - x0) * sx, (box[1] - y0) * sy, (box[2] - x0) * sx, (box[3] - y0) * sy]
    return man, tq, tb


def recolour_blue(png, quad, warm=(1.0, 0.70, 0.52)):
    """Turn the stand-in into a warm-wall, BLUE-marker scene: the orange face rotated to the pale sky blue (lightness
    and chroma kept), the orange bounce next to it turned into the same amount of blue bounce, and the wall / room
    beyond the frame tinted terracotta."""
    import cv2
    from PIL import Image
    rgb = np.asarray(Image.open(png).convert("RGB")).astype("float32") / 255.0
    H, W = rgb.shape[:2]
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2Lab)
    q = np.float32(quad)
    core = tc.poly_mask(tc.offset_quad(q, -6.0), W, H) > 0.5
    F = np.median(lab[core][:, 1:], 0)
    uF = F / max(float(np.linalg.norm(F)), 1e-6)
    ang = math.radians(261.0)
    uB = np.float32([math.cos(ang), math.sin(ang)])
    ys, xs = np.mgrid[0:H, 0:W].astype("float32")
    P = np.stack([xs + 0.5, ys + 0.5], -1)
    d = np.max(np.stack([(P - a) @ n for a, b, n in (tc._outward(q, s) for s in range(4))], 0), 0)   # + outside
    ab = lab[..., 1:]
    p = ab @ uF
    ring = (d > 14) & (d < 30)
    p_ref = float(np.median(p[ring])) if ring.any() else 0.0
    face = d <= 1.0
    band = (d > 1.0) & (d <= 14.0)
    excess = np.where(face, np.maximum(p, 0), np.where(band, np.maximum(p - p_ref, 0), 0.0))
    ab2 = ab - excess[..., None] * uF + excess[..., None] * uB
    lab2 = np.concatenate([lab[..., :1], ab2], -1)
    out = np.clip(cv2.cvtColor(lab2.astype("float32"), cv2.COLOR_Lab2RGB), 0, 1)
    side = float(np.mean([np.linalg.norm(q[(i + 1) % 4] - q[i]) for i in range(4)]))
    t = np.clip((d - 0.30 * side) / 40.0, 0, 1)[..., None]                              # feathered, past the frame
    out = out * (1 - t) + out * np.float32(warm) * t
    Image.fromarray(np.uint8(np.round(out * 255))).save(png)


def small_print(ratio, work):
    """A quick copy of the Book Club Cat print for this ratio (long side 2400 px)."""
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    tag = {"2x3": "2x3", "3x4": "3x4", "4x5": "4x5", "iso": "ISO_A1", "11x14": "11x14"}[ratio]
    src = next(PRINTS.glob(f"*_{tag}_*.jpg"))
    dst = Path(work) / f"art_{ratio}.jpg"
    if not dst.is_file():
        with Image.open(src) as im:
            im = im.convert("RGB")
            im.thumbnail((2400, 2400))
            im.save(dst, quality=92)
    return dst


def run_case(src, frac, marker, out_dir, settings):
    name = f"{src}_{int(frac * 100)}" + (f"_{marker}" if marker else "")
    work = Path(out_dir) / name
    work.mkdir(parents=True, exist_ok=True)
    png = work / "standin.png"
    man, tq, box = standin(src, frac, png)
    if marker == "blue":
        recolour_blue(png, tq)
    base = (tc.load().get("results") or {})
    src_chk = next((v for k, v in base.items() if SOURCES[src] in k), None)
    res = {"case": name, "source": SOURCES[src], "frac_target": frac, "marker": marker or "orange", "stages": {},
           "source_checker": (src_chk or {}).get("status", "unchecked")}
    st = res["stages"]
    try:
        (work / "build").mkdir(exist_ok=True)
        built = stp.build_psd(png, man["ratio"], work / "build", settings, box=box,
                              presentation=man.get("presentation"), **({"marker": marker} if marker else {}))
        st["build"] = {"pass": True, "despill": (built.get("despill") or {}).get("applied", False),
                       "despill_px": (built.get("despill") or {}).get("changed_px"), "marker": built.get("marker")}
    except Exception as e:  # noqa: BLE001
        st["build"] = {"pass": False, "why": str(e)[:300]}
        return res
    psd = work / "Standin_Template.psd"
    shutil.copy2(built["psd_tmp"], psd)
    shutil.copy2(png, work / "Standin_Scene.png")
    m = {"name": name, "psd": psd.name, "scene": "Standin_Scene.png", "ratio": man["ratio"],
         "layers_verified": "black-fill shadows built by scene_templates.make_layers (measured, masked)",
         **{k: built[k] for k in ("so_px", "so_ratio", "quad_insert", "quad_art", "mode", "canvas", "light_from")},
         **{k: built[k] for k in ("quad_paper", "opening_pad_px", "presentation", "wrap_strips", "despill", "marker")
            if k in built}}
    (work / "template.json").write_text(json.dumps(m, indent=1) + "\n")
    meta = stp.shot_meta(m, work / "Standin_Scene.png")
    st["shot"] = {"art_h_frac": meta.get("art_h_frac"), "shot": meta.get("shot"), "camera_side": meta.get("camera_side")}
    try:
        art = small_print(man["ratio"], out_dir)
        render = work / "render.png"
        r = stp.render_psd(psd, m["so_px"], art, render, settings, work / "r", manifest=m)
        st["render"] = {"pass": True, "cropped": r["cropped"]}
        g = rt.guard_quad(render, r["fitted"], m["quad_art"], work / "Standin_Scene.png", None, settings)
        st["guard"] = {"pass": g["pass"], "why": g["why"]}
        ag = production._real_art_gate(settings, psd, m, render, work / "g")
        st["gate"] = {"pass": ag["pass"], "why": ag["why"]}
    except Exception as e:  # noqa: BLE001
        st["render"] = {"pass": False, "why": str(e)[:300]}
        return res
    try:
        chk = tc.check_psd(psd, man["ratio"], settings, manifest=m)
        st["checker"] = {"pass": chk.get("status") == "PASS", "status": chk.get("status"),
                         "why": chk.get("reasons") or []}
    except Exception as e:  # noqa: BLE001
        st["checker"] = {"pass": False, "status": "error", "why": [str(e)[:300]]}
    return res


@needs
@pytest.mark.parametrize("src,frac,marker", CASES, ids=[f"{s}-{int(f * 100)}-{m or 'orange'}" for s, f, m in CASES])
def test_g0_standin(src, frac, marker, tmp_path, monkeypatch):
    from app.db import load_config
    monkeypatch.setattr(stp, "sam_detect", REAL_SAM_DETECT)
    monkeypatch.setattr(stp, "card_verify", REAL_CARD_VERIFY)
    monkeypatch.setattr(tc, "sam_opening", REAL_SAM_OPENING)
    settings = load_config("settings")
    out = Path(os.environ.get("PORTAL_G0_OUT") or tmp_path)
    res = run_case(src, frac, marker, out, settings)
    with open(out / "g0_results.jsonl", "a") as f:
        f.write(json.dumps(res) + "\n")
    print("\nG0", json.dumps(res, indent=1))
    assert res["stages"]["build"]["pass"], res
