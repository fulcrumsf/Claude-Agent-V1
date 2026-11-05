"""Stage 3 of the funnel: approved art -> upscale -> the 5 print JPGs (the Art tab).

  1. Tony approves the art (stage 2). In the Art tab (or the Details panel) he clicks "Run upscale + resize"
     (or `prints_auto_run` starts it on approval; default off).
  2. A listing row is made for the idea with the next design number (after the highest Drive/design number,
     `design_seq_floor`, the local Designs/ folders and earlier listings) and a design name from the idea title.
  3. Pipeline steps run in a worker (app/pipeline, tracked in `steps`): generate_art (done when art is approved),
     upscale (Upscayl CLI `upscayl-ncnn`, model `upscale_model`), resize (5 sizes at 300 DPI, JPG).
     The pipeline stops after resize; production steps (mockups, package, listing text, Etsy draft) are not built.

Files:
  - upscaled master (intermediate, big PNG): <db folder>/upscaled/<idea_id>/<Name>_upscaled_<model>.png
    (data/ is git-ignored; made at runtime)
  - finals: <designs_root>/<NNNNN>-<Name>/01-Printables/<Name>_<ratio>_<size>.jpg (Tony's 00120 format;
    *.jpg is git-ignored repo-wide). Only 01-Printables is made at this stage.

Resize = crop to each ratio, then Lanczos to the exact pixel size; never stretched, never padded. The crop is
placed so it cuts the fewest rows (or columns) that hold the subject: rows are compared with the quietest
background rows of the painting; ties go to the most centred crop. Every size reports how much was cut, from
which side, and whether subject was cut (then Tony should check it by eye).
"""
import json
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

from .db import DB_LOCK as LOCK
from .db import ROOT, load_config
from .pipeline.base import NotConfigured

STAGE_STEPS = ("generate_art", "upscale", "resize")
DEFAULTS = {"designs_root": "../Designs", "design_seq_floor": 120, "upscale_model": "remacri-4x",
            "upscayl_bin": "upscayl-ncnn", "upscayl_models_dir": "/Applications/Upscayl.app/Contents/Resources/models",
            "upscale_passes": 1, "upscale_timeout_s": 900, "jpg_quality": 95, "prints_auto_run": False}
STOPWORDS = {"a", "an", "the", "on", "in", "of", "for", "and", "with", "under", "at", "to", "by", "from", "among",
             "over", "into", "beside", "print", "poster", "wall", "art", "printable", "digital", "download"}
MAX_NAME_WORDS = 4


class PrintError(Exception):
    """Plain reason a print action was refused (shown to Tony)."""


def cfg(settings, key):
    return (settings or {}).get(key, DEFAULTS.get(key))


# ---------- names, numbers, paths ----------

def _words(text):
    return [w for w in re.split(r"[^A-Za-z0-9]+", text) if w]


def design_name(title):
    """Short Title Case name, no punctuation: 'Cat ... lamp: book-club cat print' -> 'Book Club Cat'.
    Prefers the part after a colon when it is short enough, else the start of the title."""
    head, _, tail = (title or "").partition(":")
    for part in (tail, head):
        ws = [w for w in _words(part) if w.lower() not in STOPWORDS]
        if ws and (len(ws) <= MAX_NAME_WORDS or part is head):
            return " ".join(w[:1].upper() + w[1:].lower() if not w.isupper() else w for w in ws[:MAX_NAME_WORDS])
    return "Untitled"


def clean_name(name):
    ws = _words(name or "")
    if not ws:
        raise PrintError("the design name needs at least one letter or number")
    return " ".join(w[:1].upper() + w[1:] for w in ws)[:60].strip()


def _abs(p):
    p = Path(p)
    return p if p.is_absolute() else (ROOT / p).resolve()


def designs_root(settings):
    return _abs(cfg(settings, "designs_root"))


def next_seq(con, settings):
    """Next design number: after the highest of the Drive floor (`design_seq_floor`, 00120 on 2026-11-05),
    the local NNNNN-Name folders in Designs/ and every listing already numbered. Gaps are not reused."""
    from .drive import next_sequence
    names = [f"{int(cfg(settings, 'design_seq_floor')):05d}-floor"]
    root = designs_root(settings)
    if root.is_dir():
        names += [p.name for p in root.iterdir()]
    names += [f"{r[0]:05d}-db" for r in con.execute("SELECT folder_seq FROM listings WHERE folder_seq IS NOT NULL")]
    return next_sequence(names)


def design_dir(settings, seq, name):
    return designs_root(settings) / f"{seq:05d}-{name}"


def upscaled_root(con):
    path = con.execute("PRAGMA database_list").fetchone()[2]
    return (Path(path).parent if path else ROOT / "data") / "upscaled"


def sizes():
    c = load_config("print_sizes")
    dpi = int(c["dpi"])
    out = []
    for s in c["sizes"]:
        out.append({**s, "w_px": round(s["w_in"] * dpi), "h_px": round(s["h_in"] * dpi), "dpi": dpi})
    return out


def file_name(name, s):
    return f"{name}_{s['ratio']}_{s['size']}.jpg"


# ---------- listing rows + steps ----------

def _record(con, lid):
    r = con.execute("SELECT record FROM listings WHERE id=?", (lid,)).fetchone()
    return json.loads(r[0] or "{}") if r else {}


def _save_record(con, lid, rec):
    con.execute("UPDATE listings SET record=? WHERE id=?", (json.dumps(rec, ensure_ascii=False), lid))
    con.commit()


def listing_for(con, idea_id):
    return con.execute("SELECT * FROM listings WHERE idea_id=? ORDER BY id DESC LIMIT 1", (idea_id,)).fetchone()


def step_map(con, lid):
    return {r["name"]: {"status": r["status"], "message": r["message"]}
            for r in con.execute("SELECT name, status, message FROM steps WHERE listing_id=?", (lid,))}


def busy(con, lid):
    return any(s["status"] in ("queued", "running") for n, s in step_map(con, lid).items() if n in STAGE_STEPS)


def start(con, settings, idea_id, name=None, redo=()):
    """Make (or reuse) the idea's listing row and queue its stage-3 steps. Returns the listing id;
    the caller runs `run` in a worker. `redo` ('upscale', 'resize') re-runs steps that are already done
    (files are overwritten in place; the design number and name stay)."""
    with LOCK:
        idea = con.execute("SELECT * FROM ideas WHERE id=?", (idea_id,)).fetchone()
        if not idea:
            raise PrintError(f"no idea #{idea_id}")
        if idea["art_state"] != "approved" or not idea["art_image_id"]:
            raise PrintError("approve the art first (Details panel), then run upscale + resize")
        lst = listing_for(con, idea_id)
        if lst and busy(con, lst["id"]):
            raise PrintError("upscale + resize is already running for this idea")
        if lst is None:
            nm = clean_name(name) if name else design_name(idea["title"])
            seq = next_seq(con, settings)
            cur = con.execute("INSERT INTO listings(idea_id, image_id, folder_seq, title, price) VALUES (?,?,?,?,?)",
                              (idea_id, idea["art_image_id"], seq, nm, settings.get("price_default")))
            lid = cur.lastrowid
        else:
            lid = lst["id"]
            if lst["image_id"] != idea["art_image_id"]:          # art re-approved: redo both steps
                con.execute("UPDATE listings SET image_id=? WHERE id=?", (idea["art_image_id"], lid))
                con.execute("UPDATE steps SET status='pending' WHERE listing_id=? AND name IN ('upscale','resize')",
                            (lid,))
        bad = set(redo) - {"upscale", "resize"}
        if bad:
            raise PrintError(f"only upscale and resize can be redone, not {', '.join(sorted(bad))}")
        for n in redo:
            con.execute("UPDATE steps SET status='pending' WHERE listing_id=? AND name=?", (lid, n))
        have = step_map(con, lid)
        for n in STAGE_STEPS:
            con.execute("INSERT OR IGNORE INTO steps(listing_id, name) VALUES (?,?)", (lid, n))
            if have.get(n, {}).get("status") != "done":
                con.execute("UPDATE steps SET status='queued', message='' WHERE listing_id=? AND name=?", (lid, n))
        con.commit()
        return lid


def run(con, settings, lid, upscayl=None):
    """Worker: the shared pipeline runner, stopped after resize. `upscayl` is injectable for tests."""
    from .pipeline import run_listing
    config = load_config("pipeline")
    extra = {"settings": settings}
    if upscayl:
        extra["upscayl"] = upscayl
    return run_listing(con, lid, config, lock=LOCK, stop_after="resize", extra=extra)


def spawn(fn, *args):
    threading.Thread(target=fn, args=args, daemon=True).start()


def recover(con):
    """On startup: steps left running by a restart are marked failed (their threads are gone)."""
    with LOCK:
        con.execute("UPDATE steps SET status='failed', message='stopped by a Portal restart; run it again' "
                    "WHERE status IN ('running','queued')")
        con.commit()


# ---------- step bodies (called from app/pipeline/steps.py) ----------

def _ctx_listing(ctx):
    con, lid = ctx["con"], ctx["listing_id"]
    with LOCK:
        lst = con.execute("SELECT * FROM listings WHERE id=?", (lid,)).fetchone()
        idea = con.execute("SELECT * FROM ideas WHERE id=?", (lst["idea_id"],)).fetchone()
        img = con.execute("SELECT * FROM images WHERE id=?", (lst["image_id"],)).fetchone()
    return con, lid, lst, idea, img


def source_path(con, img):
    from .art import art_root
    return art_root(con) / img["path"]


def check_art(ctx):
    con, lid, lst, idea, img = _ctx_listing(ctx)
    if idea["art_state"] != "approved" or not img:
        raise NotConfigured("The art is not approved yet. Approve an image in the Details panel first.")
    if not source_path(con, img).is_file():
        raise NotConfigured(f"The approved image file is missing ({img['path']}).")
    return f"Art approved (image #{img['id']})."


def _open(path):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None             # 7200x10800 finals are far above Pillow's bomb guard
    return Image.open(path)


def crop_dims(w, h, ratio):
    """Largest crop of w x h with width/height = ratio (one side kept whole)."""
    if w / h > ratio:
        return round(h * ratio), h
    return w, round(w / ratio)


def needed_scale(w, h):
    """How much the source must grow so every size's crop reaches its 300 DPI pixel size."""
    need = 0.0
    for s in sizes():
        cw, ch = crop_dims(w, h, s["w_in"] / s["h_in"])
        need = max(need, s["w_px"] / cw, s["h_px"] / ch)
    return need


def run_upscayl(src, out, settings):
    """One Upscayl pass (4x). Raises NotConfigured with a plain reason when Upscayl is not usable."""
    exe = shutil.which(cfg(settings, "upscayl_bin"))
    if not exe:
        raise NotConfigured("Upscayl is not installed on this Mac (upscayl-ncnn not found; see TOOLBOX.md).")
    models = Path(cfg(settings, "upscayl_models_dir"))
    model = cfg(settings, "upscale_model")
    if not (models / f"{model}.param").is_file():
        raise NotConfigured(f"The Upscayl model {model} is missing (expected in {models}).")
    try:
        p = subprocess.run([exe, "-i", str(src), "-o", str(out), "-m", str(models), "-n", model, "-s", "4"],
                           capture_output=True, text=True, timeout=int(cfg(settings, "upscale_timeout_s")))
    except subprocess.TimeoutExpired:
        raise NotConfigured("Upscayl took too long and was stopped. Try again with the Mac awake.")
    if p.returncode != 0 or not Path(out).is_file():
        tail = (p.stderr or p.stdout or "").strip().splitlines()[-1:] or ["no output"]
        raise NotConfigured(f"Upscayl could not upscale the image ({tail[0][:160]}).")


def upscale(ctx):
    con, lid, lst, idea, img = _ctx_listing(ctx)
    settings = ctx.get("settings") or {}
    run_one = ctx.get("upscayl") or run_upscayl
    src = source_path(con, img)
    if not src.is_file():
        raise NotConfigured(f"The approved image file is missing ({img['path']}).")
    with _open(src) as im:
        w, h = im.size
    model = cfg(settings, "upscale_model")
    out_dir = upscaled_root(con) / str(idea["id"])
    out_dir.mkdir(parents=True, exist_ok=True)
    rec = {"source": img["path"], "source_px": [w, h], "model": model, "needed_scale": round(needed_scale(w, h), 2)}
    t0 = time.time()
    if needed_scale(w, h) <= 1:
        path, passes = src, 0
    else:
        cur, passes = src, 0
        for k in range(max(1, int(cfg(settings, "upscale_passes")))):
            nxt = out_dir / f"{lst['title']}_upscaled_{model}{'' if k == 0 else f'_x{k + 1}'}.png"
            run_one(cur, nxt, settings)
            cur, passes = nxt, passes + 1
            with _open(cur) as im:
                if needed_scale(*im.size) <= 1:
                    break
        path = cur
    with _open(path) as im:
        ow, oh = im.size
    rec |= {"path": str(path), "px": [ow, oh], "passes": passes, "seconds": round(time.time() - t0, 1),
            "short_of_300dpi": round(needed_scale(ow, oh), 2) if needed_scale(ow, oh) > 1 else None}
    with LOCK:
        r = _record(con, lid)
        r["upscale"] = rec
        _save_record(con, lid, r)
    if passes == 0:
        return f"Source is already {w}x{h}, large enough for every size at 300 DPI; no upscale needed."
    msg = f"Upscaled {w}x{h} to {ow}x{oh} with {model} ({passes} pass{'es' if passes > 1 else ''}, {rec['seconds']:.0f} s)."
    if rec["short_of_300dpi"]:
        msg += f" Resize adds the last {rec['short_of_300dpi']:.2f}x with a smooth resample."
    return msg


# ---------- smart crop ----------

SUBJECT_DIFF = 45        # grey levels away from the background colour = paint that is not background
SUBJECT_SHARE = 0.01     # a row holds subject when at least 1% of it is such paint (catches thin lines)
SUBJECT_MARGIN = 0.015   # keep this much breathing room (of the side) around the subject


def subject_profile(im, axis):
    """Per row (axis 'y') or column ('x'): True where the row holds subject, not just background paint.
    Background = the colour most of the picture shares (median grey of a lightly blurred 200 px thumbnail,
    so canvas/impasto texture is not mistaken for subject). Rows next to subject are marked too (margin)."""
    from PIL import ImageFilter
    g = im.convert("L")
    tw = 200
    th = max(1, round(g.height * tw / g.width))
    g = g.resize((tw, th)).filter(ImageFilter.GaussianBlur(1))
    px = list(g.getdata())
    med = sorted(px)[len(px) // 2]
    hit = [abs(v - med) > SUBJECT_DIFF for v in px]
    if axis == "y":
        n, m = th, tw
        counts = [sum(hit[y * tw:(y + 1) * tw]) for y in range(th)]
    else:
        n, m = tw, th
        counts = [sum(hit[y * tw + x] for y in range(th)) for x in range(tw)]
    flags = [c >= max(1, SUBJECT_SHARE * m) for c in counts]
    pad = max(1, round(SUBJECT_MARGIN * n))
    return [any(flags[max(0, i - pad):i + pad + 1]) for i in range(n)]


def place_crop(flags, keep_frac):
    """Pick how much to cut from the start (top/left) so the fewest subject rows are cut; ties -> most centred.
    Returns (start_frac, cut_subject_frac_start, cut_subject_frac_end)."""
    n = len(flags)
    keep = round(n * keep_frac)
    cut = n - keep
    pre = [0]
    for f in flags:
        pre.append(pre[-1] + int(f))
    best = None
    for o in range(cut + 1):
        lost_a, lost_b = pre[o], pre[n] - pre[o + keep]
        key = (lost_a + lost_b, abs(o - cut / 2))
        if best is None or key < best[0]:
            best = (key, o, lost_a, lost_b)
    _, o, la, lb = best
    return (o / n if n else 0.0), la / n, lb / n


def crop_box(w, h, ratio, profiles):
    """Crop box in full-size pixels plus a report of what it cut."""
    cw, ch = crop_dims(w, h, ratio)
    if cw == w and ch == h:
        return (0, 0, w, h), {"cut": 0.0, "sides": "none", "subject_cut": 0.0}
    if ch < h:
        start, la, lb = place_crop(profiles["y"], ch / h)
        top = min(h - ch, round(start * h))
        box, names, total = (0, top, w, top + ch), ("top", "bottom"), h
        a, b = top / total, (h - ch - top) / total
    else:
        start, la, lb = place_crop(profiles["x"], cw / w)
        left = min(w - cw, round(start * w))
        box, names, total = (left, 0, left + cw, h), ("left", "right"), w
        a, b = left / total, (w - cw - left) / total
    rep = {"cut": round(a + b, 4), "sides": f"{names[0]} {a:.1%}, {names[1]} {b:.1%}",
           "subject_cut": round(la + lb, 4),
           "subject_cut_sides": f"{names[0]} {la:.1%}, {names[1]} {lb:.1%}"}
    return box, rep


def resize(ctx):
    con, lid, lst, idea, img = _ctx_listing(ctx)
    settings = ctx.get("settings") or {}
    up = _record(con, lid).get("upscale") or {}
    src = Path(up.get("path") or "")
    if not src.is_file():
        raise NotConfigured("The upscaled image is missing. Run the upscale step again.")
    root = designs_root(settings)
    if not root.is_dir():
        raise NotConfigured(f"The Designs folder is missing ({root}). It is not created automatically.")
    folder = design_dir(settings, lst["folder_seq"], lst["title"])
    out_dir = folder / "01-Printables"
    out_dir.mkdir(parents=True, exist_ok=True)
    quality = int(cfg(settings, "jpg_quality"))
    files, notes = [], []
    with _open(src) as im0:
        im = im0.convert("RGB")
        icc = im0.info.get("icc_profile")
    w, h = im.size
    profiles = {"y": subject_profile(im, "y"), "x": subject_profile(im, "x")}
    for s in sizes():
        box, rep = crop_box(w, h, s["w_in"] / s["h_in"], profiles)
        cropped = im.crop(box)
        detail_ppi = min(cropped.width / s["w_in"], cropped.height / s["h_in"])
        out = cropped.resize((s["w_px"], s["h_px"]), resample=_lanczos()) if cropped.size != (s["w_px"], s["h_px"]) else cropped
        path = out_dir / file_name(lst["title"], s)
        tmp = path.with_name(path.stem + ".part.jpg")
        kw = {"quality": quality, "dpi": (s["dpi"], s["dpi"])}
        if icc:
            kw["icc_profile"] = icc
        out.save(tmp, "JPEG", **kw)
        tmp.replace(path)
        with _open(path) as chk:
            got, dpi = chk.size, tuple(round(float(d)) for d in chk.info.get("dpi", (0, 0)))
        ok = got == (s["w_px"], s["h_px"]) and dpi == (s["dpi"], s["dpi"])
        if not ok:
            raise RuntimeError(f"{path.name} came out {got} at {dpi} DPI, expected {s['w_px']}x{s['h_px']} at {s['dpi']}")
        f = {"file": path.name, "ratio": s["ratio"], "size_in": s["size"], "px": list(got), "dpi": dpi[0],
             "mb": round(path.stat().st_size / 1e6, 1), "crop_box": list(box), "detail_ppi": round(detail_ppi),
             **rep}
        files.append(f)
        if rep["subject_cut"] > 0.005:
            notes.append(f"{s['ratio']} cuts {rep['subject_cut']:.0%} of the picture that holds subject "
                         f"({rep['subject_cut_sides']}); check it by eye")
    with LOCK:
        r = _record(con, lid)
        r["resize"] = {"folder": str(folder), "printables": str(out_dir), "files": files,
                       "source_px": [w, h], "quality": quality}
        _save_record(con, lid, r)
    low = min(f["detail_ppi"] for f in files)
    msg = f"5 JPGs at 300 DPI in {folder.name}/01-Printables (real detail about {low}-{max(f['detail_ppi'] for f in files)} ppi)."
    if notes:
        msg += " " + "; ".join(notes) + "."
    return msg


def _lanczos():
    from PIL import Image
    return Image.LANCZOS


# ---------- views ----------

def status(con, idea_id, settings, prefix="/ikigai"):
    from .art import file_url
    with LOCK:
        idea = con.execute("SELECT * FROM ideas WHERE id=?", (idea_id,)).fetchone()
        if not idea:
            raise PrintError(f"no idea #{idea_id}")
        img = con.execute("SELECT * FROM images WHERE id=?", (idea["art_image_id"],)).fetchone() if idea["art_image_id"] else None
        lst = listing_for(con, idea_id)
        steps = step_map(con, lst["id"]) if lst else {}
        rec = _record(con, lst["id"]) if lst else {}
    name = lst["title"] if lst else design_name(idea["title"])
    seq = lst["folder_seq"] if lst else None
    folder = design_dir(settings, seq, name) if seq else None
    view = {n: steps.get(n, {"status": "not started", "message": ""}) for n in ("upscale", "resize")}
    if lst and steps.get("generate_art", {}).get("status") == "blocked":
        view["upscale"] = {"status": "blocked", "message": steps["generate_art"]["message"]}
    running = any(v["status"] in ("queued", "running") for v in view.values())
    done = all(v["status"] == "done" for v in view.values())
    return {"idea_id": idea_id, "title": idea["title"], "art_state": idea["art_state"],
            "image_url": file_url(prefix, img["path"]) if img else None,
            "name": name, "folder_seq": seq, "folder": str(folder) if folder else None,
            "folder_rel": f"Designs/{folder.name}/01-Printables" if folder else None,
            "steps": view, "busy": running, "done": done,
            "upscale": rec.get("upscale"), "files": (rec.get("resize") or {}).get("files", []),
            "can_run": idea["art_state"] == "approved" and not running and not done}


def gallery(con, settings, prefix="/ikigai"):
    with LOCK:
        ids = [r[0] for r in con.execute("SELECT id FROM ideas WHERE art_state='approved' ORDER BY decided_at DESC, id DESC")]
    return [status(con, i, settings, prefix) for i in ids]
