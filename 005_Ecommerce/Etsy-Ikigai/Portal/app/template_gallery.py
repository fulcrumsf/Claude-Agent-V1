"""Templates tab (read-only): every room template under ../Room_Templates/Portrait_Templates as a visual gallery.

The folder tree IS the library and the build plan (Tony, 2026-11-08). Tony's master folders, numbered NNN_ (three digits):
    Portrait_Templates/<NNN_Ratio_X>/<NNN_Room_Type>/[<NNN_Style>/...]/<Template>/<files>
    e.g. 002_Ratio_2x3/001_Living_Rooms/002_Modern/Teak_Sideboard/
- Ratio = level 1 (001_Ratio_ISO = the ISO / 5x7 / A-series bucket; 005_Ratio_11x14 is its own bucket), room type =
  level 2, decor style = any folder level between room and template (e.g. 001_Japandi_Minimalist), else the Directory
  `Style` column, else a keyword in the template name / description, else "Unstyled". Display names drop the leading
  number and underscores ('001_Living_Rooms' -> 'Living Rooms').
- Anything in an `Archive/` sub-folder is not approved (old versions, `Original_` backups): ignored, only counted.
- A template = a folder holding a PSD that is not an `Original_` backup (rooms with a room.json: one tile per active
  light PSD listed in it; Retired/ and Scripts/ are skipped). Any depth works.
- An EMPTY leaf folder in the NNN_ tree = a missing template that must be built (a "gap"), at its real depth
  (ratio / room / style). Never removed or renamed by agents. Empty folders outside the NNN_ naming (e.g. the emptied
  2026-11-08 duplicates 01_Ratio_2x3 ...) are listed separately for Tony to delete.
Tile metadata (SO px, nearest standard, room/look text) is read from the tables in ../Room_Templates/Directory.md,
matched by PSD file name.

Each tile is the template rendered with a neutral test card (photocraft-cli replaceContents on "Place Artwork Here",
the same recipe as the contact sheets) and cropped 4:3 landscape centred on the art, the shape Etsy shows listing
thumbnails in search and shop grids (assumed: Rules_And_Policies/Etsy_Rules_Bible.md and Mockup_Docs/Mockup_Style_Guide.md do not state a thumbnail
crop; 4:3 is also the shape the old room pipeline used, 2733x2050). Thumbnails are cached in data/rooms/ (git-ignored)
as Gallery_<key>_t.jpg / _l.jpg, keyed by path + PSD size + mtime, so a changed PSD re-renders.

CLI:  python -m app.template_gallery --gaps     (list empty leaf folders = templates still to build)
      python -m app.template_gallery --build    (render every missing thumbnail now)
"""
import hashlib
import json
import re
import subprocess
import tempfile
import threading
from pathlib import Path

from .db import ROOT

DEFAULTS = {"room_templates_dir": "../Room_Templates", "photocraft_bin": "photocraft-cli",
            "gallery_cache": "data/rooms", "room_render_timeout_s": 300}
LIBRARY = "Portrait_Templates"
ART = "Place Artwork Here"
ART_MAT = "Place Artwork Here (Mat)"
# Archive = "do not use but kept" (Tony 2026-11-08): never a template, never a gap; only counted.
SKIP_DIRS = {"Archive", "Retired", "Scripts", "Caches", "Plates_And_Masks", "Light_Prompts", "PSD_Templates", "__pycache__",
             "Untemplated_Scenes"}
# bucket id -> chip label, in buyer-popularity order (Mockup_Docs/Mockup_Style_Guide.md picker weighting)
BUCKETS = {"2x3": "2x3", "3x4": "3x4", "4x5": "4x5", "11x14": "11x14", "iso": "ISO / 5x7", "other": "Other"}
RATIO_ALIASES = {"2x3": "2x3", "3x4": "3x4", "4x5": "4x5", "11x14": "11x14", "5x7": "iso", "iso": "iso",
                 "a_series": "iso", "all_ratios": "other", "other": "other"}
MASTER = re.compile(r"^\d{3}_")             # Tony's master folders: three-digit number prefix (NNN_)
STYLE_WORDS = [  # first match wins; checked on the template name first, then on the description
    ("Japandi", r"japandi"), ("Wabi_Sabi", r"wabi"), ("Boho", r"boho"), ("Mid_Century", r"mid.?century|teak"),
    ("Victorian", r"victorian"), ("Trendy", r"trendy|girl"), ("Moody", r"moody|dark"), ("Scandinavian", r"scandi"),
    ("Industrial", r"industrial|loft"), ("Retro", r"retro"), ("Colorful", r"colou?rful"),
    ("Minimal", r"minimal"), ("Modern", r"modern"),
]
_lock = threading.Lock()
_state = {"running": False, "error": ""}


def _cfg(settings, key):
    return (settings or {}).get(key, DEFAULTS[key])


def _abs(p):
    p = Path(p)
    return p if p.is_absolute() else (ROOT / p).resolve()


def root(settings=None):
    return _abs(_cfg(settings, "room_templates_dir"))


def cache_dir(settings=None):
    return _abs(_cfg(settings, "gallery_cache"))


def _norm(seg):
    return re.sub(r"^\d+_", "", seg).strip().lower().replace(" ", "_").replace("-", "_")


def label(seg):
    """Display name of a numbered folder: '001_Living_Rooms' -> 'Living Rooms', '001_Japandi_Minimalist' ->
    'Japandi Minimalist'."""
    return re.sub(r"\s+", " ", re.sub(r"^\d+_", "", seg).replace("_", " ")).strip()


def number(seg):
    m = re.match(r"^(\d+)_", seg)
    return int(m.group(1)) if m else 999


def ratio_of(seg):
    m = re.search(r"ratio_(.+)$", _norm(seg))
    return RATIO_ALIASES.get(m.group(1), "other") if m else None


def style_from_text(*texts):
    for t in texts:
        for name, pat in STYLE_WORDS:
            if t and re.search(pat, t, re.I):
                return name
    return None


# ---------- Directory.md tables ----------

def directory_rows(settings=None):
    """PSD file name -> row dict from every table in Room_Templates/Directory.md whose first column is a `.psd` path."""
    f = root(settings) / "Directory.md"
    rows, header = {}, None
    for line in f.read_text().splitlines() if f.is_file() else []:
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        m = re.match(r"`([^`]+\.psd)`", cells[0])
        if m and len(cells) == len(header):
            rows[Path(m.group(1)).name] = dict(zip(header, cells), path=m.group(1))
    return rows


def _col(row, *names):
    for k, v in (row or {}).items():
        if any(k.startswith(n) for n in names):
            return v
    return ""


# ---------- scan the tree ----------

def scan(settings=None):
    """(templates, gaps, stray_empty). Templates: dicts with rel path, ratio, room, style, name, desc... Any depth.
    gaps = every empty leaf folder in Tony's NNN_ tree (ratio / room / style): the build plan. stray_empty = empty
    folders outside the NNN_ naming (e.g. the 2026-11-08 duplicates emptied into the masters); Tony decides whether to
    delete them. Agents never remove or rename either."""
    base = root(settings) / LIBRARY
    rows = directory_rows(settings)
    templates, gaps, stray = [], [], []
    if not base.is_dir():
        return templates, gaps, stray
    for d in sorted(p for p in base.rglob("*") if p.is_dir()):
        rel = d.relative_to(base)
        parts = rel.parts
        if any(p in SKIP_DIRS for p in parts):
            continue
        ratio = ratio_of(parts[0])
        if ratio is None:
            continue
        kids = [c for c in d.iterdir() if c.name != ".DS_Store"]
        if not MASTER.match(parts[0]):                      # not one of Tony's NNN_ ratio folders
            if not any(f.is_file() and f.name != ".DS_Store" for f in d.rglob("*")):
                stray.append({"rel": rel.as_posix()})
            continue
        if not kids:                                          # empty leaf folder = a template still to build
            room = label(parts[1]) if len(parts) > 1 else "Any Room"
            style = " / ".join(label(p) for p in parts[2:]) or "Unstyled"
            gaps.append({"rel": rel.as_posix(), "ratio": ratio, "room": room, "room_n": number(parts[1]) if len(parts) > 1
                         else 999, "style": style})
            continue
        if len(parts) < 3:
            continue
        man = d / "room.json"
        psds = []
        if man.is_file():
            room_json = json.loads(man.read_text())
            psds = [(d / l["psd"], l) for l in room_json.get("lights", []) if (d / l["psd"]).is_file()]
        else:
            psds = [(p, None) for p in sorted(d.glob("*.psd")) if not p.name.startswith("Original_")]
        for psd, light in psds:
            row = rows.get(psd.name, {})
            name = (f"{room_json['name']} - {light['label'].replace('_', ' ')}" if light else psd.stem)
            desc = _col(row, "room / look") or (light or {}).get("kind", "")
            mid = parts[2:-1]                                   # optional style level(s) between room and template
            style = (" / ".join(label(p) for p in mid) if mid else None) \
                or label(_col(row, "style") or style_from_text(name, desc) or "Unstyled")
            templates.append({
                "rel": psd.relative_to(base).as_posix(), "psd": psd, "name": name, "folder": parts[-1],
                "ratio": ratio, "room": label(parts[1]), "room_n": number(parts[1]), "style": style, "desc": desc,
                "nearest": _col(row, "nearest") or BUCKETS[ratio], "so_px": _col(row, "so px"),
                "status": _col(row, "status"), "wired": bool(light),
                "light": light, "room_dir": d})
    return templates, gaps, stray


# ---------- render one tile ----------

def _key(t):
    st = t["psd"].stat()
    return hashlib.sha1(f"{t['rel']}|{st.st_size}|{st.st_mtime_ns}|v1".encode()).hexdigest()[:16]


def thumb_paths(t, settings=None):
    k = _key(t)
    c = cache_dir(settings)
    return c / f"Gallery_{k}_t.jpg", c / f"Gallery_{k}_l.jpg"


def test_card(w, h, path):
    """Neutral test card: warm light grey, faint grid, a mid-grey disc and a darker inner border (no colour cast)."""
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (w, h), (214, 210, 203))
    d = ImageDraw.Draw(im)
    s = max(8, max(w, h) // 8)
    lw = max(1, w // 400)
    for x in range(0, w, s):
        d.line([(x, 0), (x, h)], fill=(198, 194, 187), width=lw)
    for y in range(0, h, s):
        d.line([(0, y), (w, y)], fill=(198, 194, 187), width=lw)
    r = min(w, h) // 4
    d.ellipse([w // 2 - r, h // 2 - r, w // 2 + r, h // 2 + r], fill=(150, 146, 140))
    b = max(3, w // 70)
    d.rectangle([b, b, w - 1 - b, h - 1 - b], outline=(120, 117, 112), width=b)
    im.save(path)


def _run(settings, args):
    r = subprocess.run([_cfg(settings, "photocraft_bin"), *args], capture_output=True, text=True,
                       timeout=int(_cfg(settings, "room_render_timeout_s")))
    if r.returncode != 0:
        raise RuntimeError(f"PhotoCraft failed: {(r.stderr or r.stdout).strip()[-300:]}")
    return r.stdout


def _cmd(c, p=None):
    return ["--cmd", c, "--params", json.dumps(p or {})]


def _find(layers, name):
    for l in layers or []:
        if l.get("name") == name:
            return l
        hit = _find(l.get("children") or l.get("layers"), name)
        if hit:
            return hit
    return None


def info(psd, settings=None):
    return json.loads(_run(settings, ["info", str(psd)]))


def so_size(t, inf, settings, work):
    m = re.match(r"(\d+)x(\d+)", t.get("so_px") or "")
    if m:
        return int(m.group(1)), int(m.group(2))
    if t.get("light"):
        return tuple(json.loads((t["room_dir"] / t["light"]["json"]).read_text())["smart_object_px"])
    out = Path(work) / "so.png"
    _run(settings, ["run", str(t["psd"]), *_cmd("layer.select", {"name": ART}),
                    *_cmd("layer.smartObjects.exportContents", {"path": str(out)})])
    from PIL import Image
    with Image.open(out) as im:
        return im.size


def crop_box(canvas_w, canvas_h, art_bounds, aspect=4 / 3):
    """Largest `aspect` rectangle inside the canvas, centred on the art, clamped to the canvas."""
    if canvas_w / canvas_h >= aspect:
        ch = canvas_h
        cw = round(ch * aspect)
    else:
        cw = canvas_w
        ch = round(cw / aspect)
    x, y, w, h = art_bounds or (0, 0, canvas_w, canvas_h)
    cx, cy = x + w / 2, y + h / 2
    left = int(min(max(cx - cw / 2, 0), canvas_w - cw))
    top = int(min(max(cy - ch / 2, 0), canvas_h - ch))
    return left, top, left + cw, top + ch


def render(t, settings=None):
    """Render one template with the test card, crop 4:3 on the art, write the cached thumb + large JPGs."""
    from PIL import Image
    tp, lp = thumb_paths(t, settings)
    if tp.is_file() and lp.is_file():
        return tp, lp
    with tempfile.TemporaryDirectory() as work:
        inf = info(t["psd"], settings)
        art = _find(inf.get("layers"), ART)
        if art is None:
            raise RuntimeError(f"no '{ART}' layer")
        w, h = so_size(t, inf, settings, work)
        card = Path(work) / "card.png"
        test_card(w, h, card)
        args = _cmd("layer.select", {"name": ART}) + _cmd("layer.smartObjects.replaceContents", {"path": str(card)})
        if t.get("light"):                       # wired room PSD: plain oak frame, no mat, reference wall paint
            if _find(inf.get("layers"), ART_MAT):
                args += _cmd("layer.select", {"name": ART_MAT}) + _cmd("layer.smartObjects.replaceContents",
                                                                        {"path": str(card)})
            for f in ("Oak", "Walnut", "Black", "White"):
                if _find(inf.get("layers"), f"Frame {f}"):
                    args += _cmd("layer.setProps", {"layer": f"Frame {f}", "visible": f == "Oak"})
            for nm, on in (("MAT", False), (ART_MAT, False), (ART, True), ("Wall Greige", True)):
                if _find(inf.get("layers"), nm):
                    args += _cmd("layer.setProps", {"layer": nm, "visible": on})
        out = Path(work) / "render.png"
        _run(settings, ["run", str(t["psd"]), *args, "--out", str(out)])
        with Image.open(out) as im0:
            im = im0.convert("RGB")
        box = crop_box(im.width, im.height, art.get("bounds"))
        c = im.crop(box)
        c.resize((640, 480), Image.LANCZOS).save(tp, quality=86)
        lw = min(1800, c.width)
        c.resize((lw, round(lw * 3 / 4)), Image.LANCZOS).save(lp, quality=90)
    return tp, lp


def build_all(settings=None):
    """Render every missing thumbnail (one at a time; failures are recorded per template, never stop the rest)."""
    errors = {}
    for t in scan(settings)[0]:
        try:
            render(t, settings)
        except Exception as e:  # noqa: BLE001
            errors[t["rel"]] = str(e)[:300]
    return errors


def start_build(settings=None):
    with _lock:
        if _state["running"]:
            return
        _state["running"] = True

    def work():
        try:
            _state["errors"] = build_all(settings)
        except Exception as e:  # noqa: BLE001
            _state["error"] = str(e)[:300]
        finally:
            _state["running"] = False
    threading.Thread(target=work, daemon=True).start()


# ---------- API payload ----------

def overview(settings=None, prefix="/ikigai", build=True, styles_path=None, classify=None, auto=True):
    """Tab payload. `style` = the room's decor style (folder level / Directory / name keyword); `styles` = the Etsy
    shop styles (manual wins over auto, app/template_styles.py)."""
    from . import template_styles as ts
    templates, gaps, stray = scan(settings)
    sdata = ts.load(styles_path)
    items, missing, to_classify = [], 0, []
    errs = _state.get("errors") or {}
    for t in templates:
        tp, lp = thumb_paths(t, settings)
        ready = tp.is_file() and lp.is_file()
        missing += not ready
        st = ts.resolve(sdata, t["rel"])
        if ready and t["rel"] not in (sdata.get("manual") or {}) \
                and ((sdata.get("auto") or {}).get(t["rel"]) or {}).get("key") != tp.stem[8:24]:
            to_classify.append((t["rel"], tp, tp.stem[8:24]))
        items.append({k: t[k] for k in ("rel", "name", "folder", "ratio", "room", "style", "desc", "nearest", "so_px",
                                         "status", "wired", "room_n")}
                     | {"ratio_label": BUCKETS[t["ratio"]], "ready": ready, "error": errs.get(t["rel"], ""),
                        "styles": st["styles"], "styles_source": st["source"], "auto_styles": st["auto"],
                        "thumb": f"{prefix}/api/templates/file/{tp.name}" if ready else None,
                        "large": f"{prefix}/api/templates/file/{lp.name}" if ready else None})
    if missing and build:
        start_build(settings)
    if to_classify and auto:
        ts.start_auto(to_classify, classify)
    for g in gaps:
        g["ratio_label"] = BUCKETS[g["ratio"]]
    return {"items": items, "gaps": gaps, "stray_empty": stray, "building": _state["running"] or bool(missing and build),
            "classifying": ts.job()["running"] or bool(to_classify and auto), "vocabulary": ts.labels(sdata),
            "shop_sections": {v["label"]: v["section"] for v in sdata.get("vocabulary", [])},
            "archived": archived_count(settings), "buckets": BUCKETS, "crop": "4:3"}


def archived_count(settings=None):
    base = root(settings) / LIBRARY
    return sum(1 for a in base.rglob("Archive") if a.is_dir() for f in a.rglob("*")
               if f.is_file() and f.name != ".DS_Store") if base.is_dir() else 0


def thumb_file(name, settings=None):
    if not re.fullmatch(r"Gallery_[0-9a-f]{16}_[tl]\.jpg", name):
        return None
    f = cache_dir(settings) / name
    return f if f.is_file() else None


if __name__ == "__main__":
    import sys
    from .db import load_config
    s = load_config("settings")
    if "--gaps" in sys.argv:
        _, gaps, stray = scan(s)
        print(f"{len(gaps)} library gap(s): empty folders in Tony's NNN_ tree = templates to build (Portrait_Templates/...):")
        for g in sorted(gaps, key=lambda g: (list(BUCKETS).index(g["ratio"]), g["room_n"], g["style"])):
            print(f"  [{BUCKETS[g['ratio']]}] {g['room']} / {g['style']}: {g['rel']}")
        print(f"{len(stray)} empty folder(s) outside the NNN_ layout (Tony may delete them):")
        for g in stray:
            print(f"  {g['rel']}")
    if "--build" in sys.argv:
        print(json.dumps(build_all(s), indent=1) or "{}")


def mount(app, settings, prefix="/ikigai", styles_path=None, classify=None, auto=True):
    """Routes for the Templates tab: the gallery is read-only (no generating or editing templates); the only write
    is Tony's style assignment into config/template_styles.json. styles_path / classify / auto are for tests."""
    from fastapi import APIRouter, Body, HTTPException
    from fastapi.responses import FileResponse, JSONResponse
    from . import template_styles as ts
    r = APIRouter(prefix=prefix, tags=["templates"])

    @r.get("/api/templates")
    def api_templates():
        return JSONResponse(overview(settings, prefix, styles_path=styles_path, classify=classify, auto=auto),
                            headers={"Cache-Control": "no-store"})

    def known(rel):
        if rel not in {t["rel"] for t in scan(settings)[0]}:
            raise HTTPException(404, "no such template")

    @r.post("/api/templates/styles")
    def api_set_styles(body: dict = Body(...)):
        """{rel, styles: [...]} = Tony's choice; {rel, action: "confirm"} = accept the auto guess;
        {rel, action: "auto"} = drop the manual choice (back to auto)."""
        rel = str(body.get("rel") or "")
        known(rel)
        try:
            if body.get("action") == "confirm":
                return ts.confirm_auto(rel, styles_path)
            if body.get("action") == "auto":
                return ts.clear_manual(rel, styles_path)
            return ts.set_manual(rel, list(body.get("styles") or []), styles_path)
        except ValueError as e:
            raise HTTPException(422, str(e))

    @r.get("/api/templates/file/{name}")
    def api_template_file(name: str):
        f = thumb_file(name, settings)
        if f is None:
            raise HTTPException(404, "no such thumbnail")
        return FileResponse(f, headers={"Cache-Control": "no-cache"})   # name is content-keyed; revalidate is cheap

    app.include_router(r)
