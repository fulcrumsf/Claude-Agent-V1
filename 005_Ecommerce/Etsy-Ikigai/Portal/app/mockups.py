"""Production step 1: listing images (slots 1-7 and 20) from Tony's mockup PSDs, headless via photocraft-cli.

Per design (written to <design folder>/03-Etsy Images/, file number = slot number):
  01_Main_Mockup, 02_Poster_Mockup, 07_Detail  - the art is swapped into each PSD's "Place Artwork Here"
                                                  smart object (`layer.smartObjects.replaceContents`)
  03, 04, 05, 06, 20                           - fixed shared images, copied from the template folder
Room mockups 08-19: the Production tab (app/production.py, app/scene_templates.py), one card at a time; the old
`mockup_rooms` path (app/room_templates.py, Teak computed frames) stays off. Not built: the video(s).

Why the art is pre-fitted: replaceContents places the new file at its own pixel size, it does not scale it to
the smart object. So the smart object's native size is read (exportContents) and the art is cover-cropped
(centre, never stretched) and resized to exactly that size first. Proven on Book Club Cat 2026-11-05.
The source art is the ISO A1 print JPG (ratio 0.707, the same shape as the main and poster frames).
"""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from .db import ROOT
from .pipeline.base import NotConfigured

DEFAULTS = {"mockup_templates": "../001-Standard Package", "photocraft_bin": "photocraft-cli",
            "mockup_art_size": "ISO_A1", "mockup_timeout_s": 300, "smart_object_layer": "Place Artwork Here"}
GENERATED = [("01_Main_Mockup", "01_Main_Mockup.psd"), ("02_Poster_Mockup", "02_Poster_Mockup.psd"),
             ("07_Detail", "07_Detail.psd")]
# fixed shared images: output name (= slot number) <- file in the template folder
FIXED = [("03_Instant_Download.png", "03_Instant_Download.png"),
         ("04_Download_Contents.png", "04_Download_Contents.png"),
         ("05_Wall_Size_Guide.png", "06_Wall_Art_Size_Guide.png"),
         ("06_Important_Notes.png", "05_Important_Notes.png"),
         ("20_Customer_Reviews.png", "06A_Customer_Reviews.png")]
STILL_TO_BUILD = "room images 8-19 are made per card in the Production tab; the videos are not built yet"


def _cfg(settings, key):
    return (settings or {}).get(key, DEFAULTS[key])


def _abs(p):
    p = Path(p)
    return p if p.is_absolute() else (ROOT / p).resolve()


def _cli(settings, *args, timeout=None):
    bin_ = _cfg(settings, "photocraft_bin")
    if not shutil.which(bin_):
        raise NotConfigured(f"mockups: {bin_} is not on PATH.")
    try:
        r = subprocess.run([bin_, *args], capture_output=True, text=True,
                           timeout=timeout or int(_cfg(settings, "mockup_timeout_s")))
    except subprocess.TimeoutExpired:
        raise RuntimeError("PhotoCraft took too long on a mockup; run the step again.")
    if r.returncode != 0:
        raise RuntimeError(f"PhotoCraft failed: {(r.stderr or r.stdout).strip()[-300:]}")
    return r.stdout


def smart_object_size(psd, settings):
    """Native pixel size of the PSD's art smart object (exported to a temp PNG and measured)."""
    from PIL import Image
    layer = _cfg(settings, "smart_object_layer")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "so.png"
        _cli(settings, "run", str(psd), "--cmd", "layer.select", "--params", json.dumps({"name": layer}),
             "--cmd", "layer.smartObjects.exportContents", "--params", json.dumps({"path": str(out)}))
        if not out.is_file():
            raise RuntimeError(f"Could not read the '{layer}' smart object in {psd.name}.")
        with Image.open(out) as im:
            return im.size


def fit_art(src, size, dest):
    """Cover-crop (centre) then Lanczos to exactly `size`; returns how much of the art was cropped off."""
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    with Image.open(src) as im0:
        im = im0.convert("RGB")
    w, h = im.size
    tw, th = size
    scale = max(tw / w, th / h)
    cw, ch = round(tw / scale), round(th / scale)
    box = ((w - cw) // 2, (h - ch) // 2, (w - cw) // 2 + cw, (h - ch) // 2 + ch)
    im.crop(box).resize(size, Image.LANCZOS).save(dest)
    return round(1 - (cw * ch) / (w * h), 3)


def swap_art(psd, art_png, out_png, settings):
    layer = _cfg(settings, "smart_object_layer")
    _cli(settings, "run", str(psd), "--cmd", "layer.select", "--params", json.dumps({"name": layer}),
         "--cmd", "layer.smartObjects.replaceContents", "--params", json.dumps({"path": str(art_png)}),
         "--out", str(out_png))
    if not out_png.is_file() or out_png.stat().st_size < 10_000:
        raise RuntimeError(f"{out_png.name} was not written.")


ETSY_MAX_MB = 19   # Etsy rejects listing images over 20 MB


def _place(rendered, dest):
    """Save a rendered PNG into the design folder as a JPG (the only format uploaded to Etsy), quality 95,
    lowered only if the file would pass Etsy's size limit. `dest` may end in .png; the result is .jpg.
    The render lives in a temp folder, so nothing is ever deleted."""
    from PIL import Image
    jpg = dest.with_suffix(".jpg")
    with Image.open(rendered) as im:
        rgb = im.convert("RGB")
        for q in (95, 92, 88, 84, 80):
            rgb.save(jpg, "JPEG", quality=q, dpi=(72, 72), optimize=True)
            if jpg.stat().st_size <= ETSY_MAX_MB * 1e6:
                break
    return jpg


def build(folder, settings, adapter=None, rooms=None, design=None):
    """Make slots 1, 2, 7 and copy the fixed images into <folder>/03-Etsy Images. Returns the record dict."""
    templates = _abs(_cfg(settings, "mockup_templates"))
    if not templates.is_dir():
        raise NotConfigured(f"The mockup templates folder is missing ({templates}); see Mockup_Docs/Mockup_Originals_Locations.md.")
    missing = [n for _, n in GENERATED if not (templates / n).is_file()]
    missing += [n for _, n in FIXED if not (templates / n).is_file()]
    if missing:
        raise NotConfigured("Mockup template files missing: " + ", ".join(missing))
    size_tag = _cfg(settings, "mockup_art_size")
    arts = sorted((folder / "01-Printables").glob(f"*_{size_tag}_*.jpg"))
    if not arts:
        raise NotConfigured(f"The {size_tag} print JPG is missing in {folder.name}/01-Printables; run resize first.")
    out_dir = folder / "03-Etsy Images"
    out_dir.mkdir(parents=True, exist_ok=True)
    made, notes = [], []
    with tempfile.TemporaryDirectory() as td:
        for stem, psd_name in GENERATED:
            psd = templates / psd_name
            size = smart_object_size(psd, settings)
            fit = Path(td) / f"{stem}_art.png"
            cropped = fit_art(arts[0], size, fit)
            rendered = Path(td) / f"{stem}.png"
            swap_art(psd, fit, rendered, settings)
            out = _place(rendered, out_dir / f"{stem}.png")
            made.append({"file": out.name, "slot": int(stem[:2]), "smart_object_px": list(size),
                         "art_cropped": cropped, "mb": round(out.stat().st_size / 1e6, 1)})
            if cropped > 0.03:
                notes.append(f"{out.name}: {cropped:.0%} of the art was cropped to fit; check it by eye")
    for out_name, src_name in FIXED:
        shutil.copy2(templates / src_name, out_dir / out_name)
        made.append({"file": out_name, "slot": int(out_name[:2]), "fixed": True})
    if rooms is None:
        rooms = bool((settings or {}).get("mockup_rooms", False))   # off until Tony approves the room recipe
    if rooms:
        # v2 rooms (2026-11-07): PhotoCraft room templates in ../Room_Templates, frame/wall/light chosen per print
        # (app/room_templates.py). The v1 AI-scene rooms (app/rooms.build_rooms) were rejected by Tony.
        from . import room_templates
        design = design or {"title": folder.name.split("-", 1)[-1]}
        all_prints = sorted((folder / "01-Printables").glob("*.jpg"))
        r_made, r_notes, failed = room_templates.build_rooms(out_dir, all_prints, settings, design)
        made += r_made
        notes += r_notes
        if not r_made:
            raise NotConfigured("No room mockups could be made: " + "; ".join(r_notes))
    return {"folder": str(out_dir), "files": made, "pending": STILL_TO_BUILD, "notes": notes}
