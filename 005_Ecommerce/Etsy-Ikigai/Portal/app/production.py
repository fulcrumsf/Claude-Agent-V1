"""Production tab (stage 4, rebuilt 2026-11-08 to Tony's spec; slot map 2026-11-10): the ROOM images for each upscaled
design (slot 3 and slots 9-19, app/room_slots.ROOM_SLOTS), one card per slot, nothing else.

  - Only designs whose upscale is done appear (thumbnail row on top; click opens the big panel).
  - Panel: up to 5 room check boxes (Etsy's Room list only) and the shop-style tick list; blank styles = the agent
    decides from the art (the Templates tab's cheap Gemini vision guess, app/template_styles.classify_art). The ticks
    are saved as TAGS on the design (listing record `design_tags`, read later by etsy_draft via the crosswalk).
  - Slot plan: app/room_slots.plan (Tony's rooms first in slots 3, 9, 10, 11, 12, then the agent's by the art-to-room
    compatibility rule; fewer cards rather than padding). Only slots that need building get a card.
  - Card: Generate / Regenerate (ONE job at a time, global; one click = cost approval), result in the card,
    Approve / Deny, and "+" to pick any library template. Source per click: a matching library template not used
    yet in this listing (free), else a NEW AI scene (kie.ai credits; auto-saved as a template, app/scene_templates.py).
  - Files (Designs/<design>/03-Etsy Images): slot images are JPGs named NN_Room_<Room>_<Decor>[_vK].jpg. Nothing is
    ever overwritten or deleted: a regenerated slot's old image moves to 03-Etsy Images/Archive/ (new version beside),
    a denied image moves to Archive (Undo / Approve moves it back), a render the accuracy guard flags is written to
    Archive and shown on the card with the reason (Approve moves it in). Denying an image whose template was made
    for it also moves that template folder into its style folder's Archive/ (Tony's rule for denied looks).
  - Slots 1, 2, 8 and the fixed 4-7, 20 are made by Run upscale + resize and are never shown here.
  - Fit rule (Tony 2026-11-10): art is cover-fit and centre-cropped to the opening, never stretched, never a white
    border (scene_templates.fit_cover); mats exist only as template layers.
Decisions live in the listing record (`mockup_approvals`: file -> approved | denied)."""
import re
import shutil
import tempfile
import threading
from datetime import datetime
from pathlib import Path

from . import mockups, prints
from . import room_slots as rs
from . import room_templates as rt
from . import scene_templates as stp
from .db import DB_LOCK as LOCK

FIXED_NAMES = {n for n, _ in mockups.FIXED}
TEMPLATED_SLOTS = {int(stem[:2]) for stem, _ in mockups.GENERATED}     # 1, 2, 8: art in a PSD, not reviewed here
ROOM_SLOTS = set(rs.ROOM_SLOTS)                                          # 3, 9-19
DECISIONS = ("approved", "denied", "pending")
LABELS = {1: "Main", 2: "Poster", 8: "Detail"}
ARCHIVE = "Archive"
_job = {"running": False, "idea_id": None, "slot": None, "stage": "", "started": None}
_job_lock = threading.Lock()


class ProductionError(Exception):
    """Plain reason a Production action was refused (shown to Tony)."""


def _label(name):
    stem = Path(name).stem
    slot = int(stem[:2])
    return LABELS.get(slot) or stem[3:].replace("_", " ")


def _images_dir(settings, lst):
    return prints.design_dir(settings, lst["folder_seq"], lst["title"]) / "03-Etsy Images"


def _prod(rec):
    p = rec.setdefault("production", {})
    p.setdefault("slots", {})
    p.setdefault("archived", {})
    return p


def _is_slot_image(name):
    return (name.lower().endswith(".jpg") and name[:2].isdigit() and name not in FIXED_NAMES
            and int(name[:2]) in ROOM_SLOTS)


def _archive_file(folder, name, rec):
    """Where an archived image actually is (Archive may already hold an older file of the same name)."""
    info = (_prod(rec)["archived"]).get(name) or {}
    return folder / ARCHIVE / info.get("file", name)


def _to_archive(folder, name, rec, was):
    """Move a listing image into 03-Etsy Images/Archive (never overwrites: a taken name gets a _N suffix)."""
    arch = folder / ARCHIVE
    arch.mkdir(exist_ok=True)                      # Archive folders are pre-approved by Tony (2026-11-08)
    dest = arch / name
    k = 2
    while dest.exists():
        dest = arch / f"{Path(name).stem}_{k}{Path(name).suffix}"
        k += 1
    shutil.move(str(folder / name), str(dest))
    _prod(rec)["archived"][name] = {"file": dest.name, "was": was, "at": datetime.now().isoformat(timespec="seconds")}
    return dest


def _from_archive(folder, name, rec):
    src = _archive_file(folder, name, rec)
    dest = folder / name
    if dest.exists():
        raise ProductionError(f"{name} already exists in the listing folder")
    shutil.move(str(src), str(dest))
    _prod(rec)["archived"].pop(name, None)
    return dest


def _url(prefix, idea_id, p, name):
    fs = p.stat()
    # version stamp: a file made again under the same name gets a new URL, so the browser can never show the old
    # picture from its cache (bug 2026-11-08)
    return f"{prefix}/api/production/{idea_id}/file/{name}?v={fs.st_mtime_ns:x}{fs.st_size:x}"


# ---------- the design's images (all room images, used for counts and the old flat view) ----------

def design(con, settings, idea_id, prefix="/ikigai"):
    st = prints.status(con, idea_id, settings, prefix)
    with LOCK:
        lst = prints.listing_for(con, idea_id)
        rec = prints._record(con, lst["id"]) if lst else {}
    out = {"idea_id": idea_id, "name": st["name"], "title": st["title"], "image_url": st["image_url"],
           "folder_rel": f"Designs/{Path(st['folder']).name}/03-Etsy Images" if st["folder"] else None,
           "prints": len(st["files"]), "images": [], "counts": {"approved": 0, "denied": 0, "pending": 0}}
    if not lst or not lst["folder_seq"]:
        return out
    folder = _images_dir(settings, lst)
    approvals = rec.get("mockup_approvals") or {}
    archived = _prod(rec)["archived"]
    found = [(p.name, p, "folder") for p in sorted(folder.glob("*.jpg")) if _is_slot_image(p.name)] \
        if folder.is_dir() else []
    for name, info in sorted(archived.items()):         # our denied / flagged images (not older Archive files)
        p = _archive_file(folder, name, rec)
        if p.is_file() and not (folder / name).exists():
            found.append((name, p, "flagged" if info.get("was") == "flagged" else "archive"))
    made = {f["file"]: f for f in (rec.get("mockups") or {}).get("files", [])}
    if any(f.get("slot", 0) in ROOM_SLOTS and f.get("room") for f in made.values()):
        # once the old room-template step made rooms, older room files nobody made (e.g. the rejected v1 AI rooms)
        # are hidden, never deleted; images the Production cards made always show
        ours = set(made) | set(_prod(rec)["archived"])
        for s in _prod(rec)["slots"].values():
            ours |= {s.get("file")} | set(s.get("history") or [])
        found = [f for f in found if f[0] in ours]
    for name, p, where in sorted(found):
        mb = round(p.stat().st_size / 1e6, 1)
        status = approvals.get(name, "pending")
        info = made.get(name, {})
        out["images"].append({"file": name, "slot": int(name[:2]), "label": _label(name), "mb": mb,
                              "status": status, "print": info.get("print"), "where": where,
                              "look": ({k: info.get(k) for k in ("room", "light", "frame", "mat", "paint")}
                                       if info.get("room") else None),
                              "url": _url(prefix, idea_id, p, name), "over_limit": mb > 19.5})
        out["counts"][status] += 1
    return out


def upscaled(con, idea_id):
    lst = prints.listing_for(con, idea_id)
    return bool(lst and prints.step_map(con, lst["id"]).get("upscale", {}).get("status") == "done")


def overview(con, settings, prefix="/ikigai"):
    """Designs for the thumbnail row: only those whose upscale is done (Tony 2026-11-08)."""
    with LOCK:
        ids = [r[0] for r in con.execute("SELECT id FROM ideas WHERE art_state='approved' ORDER BY decided_at DESC, id DESC")]
        ids = [i for i in ids if upscaled(con, i)]
    return [design(con, settings, i, prefix) for i in ids]


def image_path(con, settings, idea_id, name):
    """Safe path of one listing image (listing folder, or its Archive for our denied / flagged ones), or None."""
    with LOCK:
        lst = prints.listing_for(con, idea_id)
        rec = prints._record(con, lst["id"]) if lst else {}
    if not lst or not lst["folder_seq"] or Path(name).name != name or Path(name).suffix.lower() not in (".jpg", ".png"):
        return None
    folder = _images_dir(settings, lst)
    p = folder / name
    if p.is_file():
        return p
    if name in _prod(rec)["archived"]:
        a = _archive_file(folder, name, rec)
        return a if a.is_file() else None
    return None


def decide(con, settings, idea_id, name, decision):
    """approved | denied | pending (= undo). Denied -> Archive; approving or undoing brings it back. Never deletes."""
    if decision not in DECISIONS:
        raise ValueError("decision must be approved, denied or pending")
    if image_path(con, settings, idea_id, name) is None or not _is_slot_image(name):
        raise KeyError(name)
    with LOCK:
        lst = prints.listing_for(con, idea_id)
        rec = prints._record(con, lst["id"])
        folder = _images_dir(settings, lst)
        prod = _prod(rec)
        ap = rec.setdefault("mockup_approvals", {})
        in_folder = (folder / name).is_file()
        info = prod["archived"].get(name) or {}
        slot = next((s for s in prod["slots"].values() if s.get("file") == name), None)
        if decision == "denied":
            if in_folder:
                _to_archive(folder, name, rec, "folder")
            ap[name] = "denied"
            if slot and slot.get("new_template") and not slot.get("template_archived"):
                _archive_template(settings, slot)
        elif decision == "approved":
            if not in_folder:
                _from_archive(folder, name, rec)
            ap[name] = "approved"
            if slot and slot.get("template_archived"):
                _restore_template(settings, slot)
        else:
            if not in_folder and info.get("was") == "folder":
                _from_archive(folder, name, rec)
            if slot and slot.get("template_archived"):
                _restore_template(settings, slot)
            ap.pop(name, None)
        prints._save_record(con, lst["id"], rec)


def _archive_template(settings, slot):
    tdir = (stp.library(settings) / slot["new_template"]).parent
    if not tdir.is_dir():
        return
    arch = tdir.parent / ARCHIVE
    arch.mkdir(exist_ok=True)
    dest = arch / tdir.name
    if dest.exists():
        return
    shutil.move(str(tdir), str(dest))
    slot["template_archived"] = str(dest.relative_to(stp.library(settings)))


def _restore_template(settings, slot):
    src = stp.library(settings) / slot["template_archived"]
    dest = (stp.library(settings) / slot["new_template"]).parent
    if src.is_dir() and not dest.exists():
        shutil.move(str(src), str(dest))
    slot.pop("template_archived", None)


# ---------- the panel: tags, plan, cards ----------

def _vocab():
    from . import template_styles as ts
    try:
        v = ts.labels(ts.load())
        return v or list(rs.SHOP_STYLES)
    except Exception:  # noqa: BLE001
        return list(rs.SHOP_STYLES)


def _ctx(con, settings, idea_id):
    with LOCK:
        idea = con.execute("SELECT * FROM ideas WHERE id=?", (idea_id,)).fetchone()
        lst = prints.listing_for(con, idea_id)
        if not idea or not lst or not lst["folder_seq"]:
            raise ProductionError("run upscale + resize first (Art tab)")
        rec = prints._record(con, lst["id"])
    design_dir = prints.design_dir(settings, lst["folder_seq"], lst["title"])
    arts = sorted((design_dir / "01-Printables").glob("*.jpg"))
    return idea, lst, rec, design_dir / "03-Etsy Images", arts


def _analysis(rec, arts):
    """Value key + accents of the print (rooms.analyze_print), cached in the record per print file."""
    if not arts:
        return {}
    a = next((x for x in arts if "_ISO_" in x.name), arts[0])
    key = f"{a.name}|{a.stat().st_mtime_ns}"
    cache = _prod(rec).get("analysis") or {}
    if cache.get("key") == key:
        return cache
    from .rooms import analyze_print
    try:
        res = analyze_print(a)
    except Exception:  # noqa: BLE001
        res = {}
    _prod(rec)["analysis"] = dict(res, key=key)
    return _prod(rec)["analysis"]


def effective_styles(tags):
    if tags.get("styles"):
        return tags["styles"], "tony"
    auto = (tags.get("auto_styles") or {}).get("styles") or []
    return auto, ("auto" if auto else "none")


def _current_image(folder, slot, srec, rec):
    """The slot's image: the one this slot made (folder or Archive), else the newest JPG with that slot number."""
    name = srec.get("file")
    if name:
        if (folder / name).is_file():
            return name, folder / name, "folder"
        if name in _prod(rec)["archived"] and _archive_file(folder, name, rec).is_file():
            info = _prod(rec)["archived"][name]
            return name, _archive_file(folder, name, rec), ("flagged" if info.get("was") == "flagged" else "archive")
    hits = sorted((p for p in folder.glob(f"{slot:02d}_*.jpg") if _is_slot_image(p.name)),
                  key=lambda p: p.stat().st_mtime) if folder.is_dir() else []
    if hits:
        return hits[-1].name, hits[-1], "folder"
    return None, None, None


def _plan(con, settings, idea, rec, folder, arts):
    tags = rec.get("design_tags") or {}
    styles, _ = effective_styles(tags)
    an = _analysis(rec, arts)
    approvals = rec.get("mockup_approvals") or {}
    locked = {}
    for k, s in _prod(rec)["slots"].items():
        name, _, _ = _current_image(folder, int(k), s, rec)
        if name and approvals.get(name) == "approved" and s.get("room"):
            locked[int(k)] = {"room": s["room"], "decor": s.get("decor"), "ratio": s.get("ratio")}
    avail = stp.available_rooms(settings)
    text = f"{idea['title']}. {idea['description'] or ''}"
    return rs.plan(tags.get("rooms") or [], styles, text, an.get("value_key"), rs.room_slots(settings), avail,
                   settings.get("room_ratio_weights"), locked), avail


def _engine(settings):
    eng = settings.get("room_scene_engine", stp.DEFAULTS["room_scene_engine"])
    cr = stp.SCENE_CREDITS.get(eng)
    return {"id": eng, "credits_per_scene": cr, "usd_per_scene": round(cr * 0.005, 3) if cr else None,
            "resolution": settings.get("room_scene_resolution", "2K")}


def checker_fails(settings=None):
    """Templates the template checker FAILED (app/template_checker.py results; a PSD changed since its check counts
    as unchecked). They are never picked automatically; Tony can still pick one with "+"."""
    from . import template_checker as tc
    data = tc.load((settings or {}).get("template_checks_path"))
    return {rel for rel, r in (data.get("results") or {}).items() if r.get("status") == "FAIL"}


def library_picks(plan, slots, lib, fails=frozenset()):
    """Which library template each card's next click uses, decided in slot order so no two cards (and no template
    already used in this listing) share one; a template a slot already tried, or one the checker FAILED, is skipped.
    {slot: template or None}."""
    used = {s.get("template") for s in slots.values() if s.get("template")}
    out = {}
    for c in sorted(plan, key=lambda c: c["slot"]):
        srec = slots.get(str(c["slot"])) or {}
        mine = srec.get("template")
        cands = [t for t in lib if stp.matches(t, c["room"], c["decor"], c["ratio"]) and t["rel"] not in fails
                 and t["rel"] not in used and t["rel"] != mine and t["rel"] not in (srec.get("tried") or [])]
        out[c["slot"]] = cands[0] if cands else None
        if cands:
            used.add(cands[0]["rel"])
    return out


def _next_source(card, pick, avail, engine):
    if pick:
        return {"kind": "library", "label": f"library template {pick['name']}", "rel": pick["rel"], "credits": 0}
    if card["ratio"] in (avail.get(card["room"]) or []):
        cr = engine["credits_per_scene"]
        return {"kind": "new", "label": "generating new template", "credits": cr}
    return {"kind": "none", "credits": 0,
            "label": f"no {card['room']} folder in Room_Templates for {rs.RATIO_LABEL[card['ratio']]} "
                     "(Tony makes room folders); pick a template with +"}


def panel(con, settings, idea_id, prefix="/ikigai", start_auto=None):
    """Everything the big middle panel shows for one design."""
    idea, lst, rec, folder, arts = _ctx(con, settings, idea_id)
    tags = rec.get("design_tags") or {}
    if start_auto and not tags.get("styles") and tags.get("auto_for") != idea["art_image_id"]:
        start_auto(idea_id)
        with LOCK:
            rec = prints._record(con, lst["id"])
        tags = rec.get("design_tags") or {}
    plan, avail = _plan(con, settings, idea, rec, folder, arts)
    with LOCK:                                           # analysis cache
        r2 = prints._record(con, lst["id"])
        if _prod(r2).get("analysis") != _prod(rec).get("analysis"):
            _prod(r2)["analysis"] = _prod(rec).get("analysis")
            prints._save_record(con, lst["id"], r2)
    lib = stp.library_templates(settings)
    names = {t["rel"]: t["name"] for t in lib}
    engine = _engine(settings)
    approvals = rec.get("mockup_approvals") or {}
    slots = _prod(rec)["slots"]
    job = job_state()
    cards = []
    planned = {c["slot"] for c in plan}
    extra = [{"slot": int(k), "room": s.get("room") or "Room", "decor": s.get("decor") or "Modern",
              "ratio": s.get("ratio") or "2x3", "by": "earlier", "reason": "not in the current plan",
              "ratio_label": rs.RATIO_LABEL.get(s.get("ratio") or "2x3")}
             for k, s in slots.items() if int(k) not in planned and (s.get("file") or s.get("state"))]
    picks = library_picks(plan + extra, slots, lib, checker_fails(settings))
    for c in sorted(plan + extra, key=lambda c: c["slot"]):
        srec = slots.get(str(c["slot"])) or {}
        name, p, where = _current_image(folder, c["slot"], srec, rec)
        img = None
        if name:
            img = {"file": name, "url": _url(prefix, idea_id, p, name), "status": approvals.get(name, "pending"),
                   "where": where, "flagged": where == "flagged", "guard": srec.get("guard") if srec.get("file") == name
                   else None, "mb": round(p.stat().st_size / 1e6, 1), "print": srec.get("print")
                   if srec.get("file") == name else None}
        running = job["running"] and job["idea_id"] == idea_id and job["slot"] == c["slot"]
        state = "running" if running else (srec.get("state") if srec.get("state") in ("failed",) else "idle")
        made_for = None
        if srec.get("file") == name and srec.get("room") and (srec.get("room"), srec.get("decor")) != (c["room"], c["decor"]):
            made_for = f"{srec.get('room')} · {srec.get('decor')}"
        cards.append({**c, "image": img, "state": state, "message": srec.get("message", ""),
                      "stage": job["stage"] if running else "",
                      "source": srec.get("source"), "template": srec.get("template"),
                      "template_name": names.get(srec.get("template")) or (srec.get("template") or "").split("/")[-1],
                      "made_for": made_for,
                      "next": _next_source(c, picks.get(c["slot"]), avail, engine),
                      "credits_spent": srec.get("credits")})
    styles, source = effective_styles(tags)
    return {"idea_id": idea_id, "name": lst["title"], "title": idea["title"],
            "image_url": prints.status(con, idea_id, settings, prefix)["image_url"],
            "folder_rel": f"Designs/{folder.parent.name}/03-Etsy Images",
            "rooms_all": rs.ETSY_ROOMS, "max_rooms": rs.MAX_PICKS, "styles_all": _vocab(),
            "room_slots": rs.room_slots(settings),
            "rooms": tags.get("rooms") or [], "styles": tags.get("styles") or [],
            "styles_auto": (tags.get("auto_styles") or {}).get("styles") or [],
            "styles_auto_error": (tags.get("auto_styles") or {}).get("error"),
            "styles_used": styles, "styles_source": source, "slots": cards, "job": job, "engine": engine,
            "prints": len(arts)}


def save_tags(con, settings, idea_id, rooms, styles):
    """Tony's ticks -> TAGS on the design (listing record `design_tags`). Rooms: Etsy's list only, max 5, his order."""
    rooms = [r for r in rooms or []]
    bad = [r for r in rooms if r not in rs.ETSY_ROOMS]
    if bad:
        raise ProductionError(f"not an Etsy room: {', '.join(bad)}")
    if len(rooms) > rs.MAX_PICKS:
        raise ProductionError(f"pick up to {rs.MAX_PICKS} rooms")
    if len(set(rooms)) != len(rooms):
        raise ProductionError("each room once")
    vocab = _vocab()
    bad = [s for s in styles or [] if s not in vocab]
    if bad:
        raise ProductionError(f"not a shop style: {', '.join(bad)}")
    with LOCK:
        lst = prints.listing_for(con, idea_id)
        if not lst:
            raise ProductionError("run upscale + resize first (Art tab)")
        rec = prints._record(con, lst["id"])
        tags = rec.setdefault("design_tags", {})
        tags["rooms"] = rooms
        tags["styles"] = [s for s in vocab if s in (styles or [])]
        tags["updated"] = datetime.now().isoformat(timespec="seconds")
        prints._save_record(con, lst["id"], rec)


def auto_styles(con, settings, idea_id, classify=None):
    """Background: the design's shop styles from the art (cheap Gemini vision call), only when Tony ticked none.
    Runs once per approved art image; a failure is recorded (shown small) and not retried until the art changes."""
    from . import template_styles as ts
    classify = classify or ts.classify_art
    with LOCK:
        idea = con.execute("SELECT * FROM ideas WHERE id=?", (idea_id,)).fetchone()
        lst = prints.listing_for(con, idea_id)
        img = con.execute("SELECT * FROM images WHERE id=?", (idea["art_image_id"],)).fetchone() if idea else None
        if not lst or not img:
            return
        rec = prints._record(con, lst["id"])
        tags = rec.setdefault("design_tags", {})
        if tags.get("styles") or tags.get("auto_for") == idea["art_image_id"]:
            return
        tags["auto_for"] = idea["art_image_id"]
        prints._save_record(con, lst["id"], rec)
        path = prints.source_path(con, img)
    try:
        styles, tokens = classify(path, _vocab())
        res = {"styles": styles, "tokens": tokens, "model": ts.MODEL}
    except Exception as e:  # noqa: BLE001
        res = {"styles": [], "error": str(e)[:160]}
    with LOCK:
        rec = prints._record(con, lst["id"])
        rec.setdefault("design_tags", {})["auto_styles"] = res
        prints._save_record(con, lst["id"], rec)


# ---------- one generation job at a time ----------

def job_state():
    with _job_lock:
        return dict(_job)


def start_slot(con, settings, idea_id, slot, template_rel=None):
    """Claim the single job slot for this card. The caller runs run_slot in a worker. One click = Tony's approval
    of the cost (a library template costs nothing; a new scene costs kie.ai credits)."""
    if slot not in rs.room_slots(settings):
        raise ProductionError("room images are slot 3 and slots 9-19")
    _ctx(con, settings, idea_id)
    if template_rel and template_rel not in {t["rel"] for t in stp.library_templates(settings)}:
        raise ProductionError("no such template in the library")
    with _job_lock:
        if _job["running"]:
            raise ProductionError(f"slot {_job['slot']} is still being made; one at a time")
        _job.update(running=True, idea_id=idea_id, slot=slot, stage="starting",
                    started=datetime.now().isoformat(timespec="seconds"))
    return True


def _stage(text):
    with _job_lock:
        _job["stage"] = text


def _unique_name(folder, slot, room, decor):
    short = stp.ROOM_SHORT.get(room) or re.sub(r"[^A-Za-z0-9]+", "_", room.title()).strip("_")
    base = f"{slot:02d}_Room_{short}_{decor}"
    name, k = f"{base}.jpg", 2
    while (folder / name).exists() or (folder / ARCHIVE / name).exists():
        name = f"{base}_v{k}.jpg"
        k += 1
    return name


def run_slot(con, settings, idea_id, slot, template_rel=None, generator=None):
    """Worker for one card: pick the source, render, guard, place. Always releases the job slot."""
    try:
        idea, lst, rec, folder, arts = _ctx(con, settings, idea_id)
        if not arts:
            raise stp.TemplateError("the print JPGs are missing; run upscale + resize first")
        plan, avail = _plan(con, settings, idea, rec, folder, arts)
        card = next((c for c in plan if c["slot"] == slot), None)
        srec = dict(_prod(rec)["slots"].get(str(slot)) or {})
        if card is None:
            card = {"slot": slot, "room": srec.get("room") or "Living room", "decor": srec.get("decor") or "Modern",
                    "ratio": srec.get("ratio") or "2x3"}
        lib = stp.library_templates(settings)
        if template_rel:
            t = next(x for x in lib if x["rel"] == template_rel)
            source = "picked"
        else:                                   # the same choice the card showed (library_picks, slot order)
            plan_all = plan if any(c["slot"] == slot for c in plan) else plan + [card]
            t = library_picks(plan_all, _prod(rec)["slots"], lib, checker_fails(settings)).get(slot)
            source = "library" if t else "new"
        out = {"room": card["room"], "decor": card["decor"], "ratio": card["ratio"], "source": source,
               "credits": 0, "new_template": None}
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            render = td / "render.png"
            if t is None:
                if card["ratio"] not in (avail.get(card["room"]) or []):
                    raise stp.TemplateError(f"no {card['room']} folder in Room_Templates for "
                                            f"{rs.RATIO_LABEL[card['ratio']]}; pick a template with +")
                look = rs.pick_look(card["room"], card["decor"])      # weighted random, saved in template.json
                prompt = rs.scene_prompt(card["room"], card["decor"], card["ratio"], look=look)
                scene = td / "scene.png"
                _stage("drawing the room (kie.ai)")
                gen = stp.generate_scene(prompt, scene, settings, generator)
                out["credits"] = gen.get("credits")
                _stage("finding the frame, building the PSD")
                (td / "build").mkdir()
                try:
                    built = stp.build_psd(scene, card["ratio"], td / "build", settings,
                                          presentation=rs.presentation_for(card["room"], card["decor"], card["ratio"]))
                except stp.TemplateError as e:
                    folder.joinpath(ARCHIVE).mkdir(parents=True, exist_ok=True)
                    keep = folder / ARCHIVE / f"Scene_No_Insert_{slot:02d}_{datetime.now():%Y%m%d_%H%M%S}.png"
                    shutil.copy2(scene, keep)
                    why = str(e) if "off the print ratio" in str(e) else "the scene has no clean blank frame insert"
                    raise stp.TemplateError(f"{why} (scene kept as {ARCHIVE}/{keep.name}); Regenerate for a new scene")
                meta = {"prompt": prompt, "look": look, "engine": settings.get("room_scene_engine", "nbpro"),
                        "model": gen.get("model"), "resolution": settings.get("room_scene_resolution", "2K"),
                        "aspect": settings.get("room_scene_aspect", "4:3"), "credits": gen.get("credits"),
                        "made_for": {"idea_id": idea_id, "design": lst["title"], "slot": slot}}
                tdir, psd = stp.save_template(settings, card["room"], card["decor"], card["ratio"], scene, built, meta)
                rel = psd.relative_to(stp.library(settings)).as_posix()
                man = stp.load_manifest(psd)
                _stage("rendering the art into the room")
                art = stp.print_for(arts, rs.RATIO_VALUE[card["ratio"]], rs.PRINT_RATIO_TAG[card["ratio"]])
                r = stp.render_psd(psd, man["so_px"], art, render, settings, td, manifest=man)
                g = rt.guard_quad(render, r["fitted"], man["quad_art"], tdir / man["scene"],
                                  man.get("guard_max_cover"), settings)
                out.update(template=rel, new_template=rel, print=art.name, cropped=r["cropped"])
            elif t.get("wired"):                           # Teak Sideboard etc.: only when Tony picks it with +
                _stage("rendering the art into the room")
                room = next(x for x in rt.rooms(settings) if x["dir"] == t["room_dir"])
                light = next(x for x in room["lights"] if x["id"] == t["light"]["id"])
                art = rt.pick_art(arts, light["meta"]["art_aspect"])
                look = {"frame_layer": "Oak", "frame_id": "oak", "mat": False, "paint": None, "glass": True}
                r = rt.render_look(room, light, art, look, render, settings, td)
                g = rt.guard(room, light, render, r["fitted"], False, settings)
                out.update(template=t["rel"], print=art.name, cropped=None)
            else:
                _stage("rendering the art into the room")
                man = stp.manifest_for_render(t, settings)
                art = stp.print_for(arts, man["so_px"][0] / man["so_px"][1])
                r = stp.render_psd(t["psd"], man["so_px"], art, render, settings, td, manifest=man)
                g = rt.guard_quad(render, r["fitted"], man["quad_art"], None, None, settings)
                out.update(template=t["rel"], print=art.name, cropped=r["cropped"])
            with LOCK:
                rec = prints._record(con, lst["id"])
                prod = _prod(rec)
                old = (prod["slots"].get(str(slot)) or {})
                old_name, old_p, old_where = _current_image(folder, slot, old, rec)
                folder.mkdir(parents=True, exist_ok=True)
                if old_name and old_where == "folder":   # never overwrite: the old one goes to Archive
                    _to_archive(folder, old_name, rec, "replaced")
                name = _unique_name(folder, slot, card["room"], card["decor"])
                if g["pass"]:
                    placed = mockups._place(render, folder / name)
                else:                                    # flagged by the guard: kept in Archive, shown with why
                    (folder / ARCHIVE).mkdir(exist_ok=True)
                    placed = mockups._place(render, folder / ARCHIVE / name)
                    prod["archived"][name] = {"file": placed.name, "was": "flagged",
                                              "at": datetime.now().isoformat(timespec="seconds")}
                (rec.setdefault("mockup_approvals", {})).pop(name, None)
                tried = list(old.get("tried") or [])
                if out.get("template") and out["template"] not in tried:
                    tried.append(out["template"])
                prod["slots"][str(slot)] = {**out, "file": placed.name, "guard": g, "tried": tried, "state": "done",
                                            "message": ("" if g["pass"] else "flagged by the accuracy guard: "
                                                        + "; ".join(g["why"])),
                                            "made": datetime.now().isoformat(timespec="seconds"),
                                            "history": (old.get("history") or []) + ([old["file"]] if old.get("file") else [])}
                prints._save_record(con, lst["id"], rec)
    except Exception as e:  # noqa: BLE001  (shown on the card; the job slot is always released)
        msg = str(e) if isinstance(e, (ProductionError, stp.TemplateError)) else f"Something went wrong: {e}"
        try:
            with LOCK:
                lst = prints.listing_for(con, idea_id)
                rec = prints._record(con, lst["id"])
                s = _prod(rec)["slots"].setdefault(str(slot), {})
                s.update(state="failed", message=msg[:400])
                prints._save_record(con, lst["id"], rec)
        except Exception:  # noqa: BLE001
            pass
    finally:
        with _job_lock:
            _job.update(running=False, idea_id=None, slot=None, stage="", started=None)


def recover(con):
    """On startup: a card left running by a restart is marked failed (its thread is gone)."""
    import json
    with LOCK:
        for r in con.execute("SELECT id, record FROM listings").fetchall():
            rec = json.loads(r["record"] or "{}")
            changed = False
            for s in ((rec.get("production") or {}).get("slots") or {}).values():
                if s.get("state") in ("queued", "running"):
                    s.update(state="failed", message="stopped by a Portal restart; run it again")
                    changed = True
            if changed:
                prints._save_record(con, r["id"], rec)


# ---------- the old "Run mockups" endpoint (kept for the API; the Art tab button is gone since 2026-11-08) ----------

def start(con, settings, idea_id):
    """Queue the mockups step for a design whose print sizes are done. Returns the listing id."""
    with LOCK:
        lst = prints.listing_for(con, idea_id)
        if lst is None:
            raise prints.PrintError("run upscale + resize first")
        st = prints.step_map(con, lst["id"])
        if any(st.get(n, {}).get("status") != "done" for n in ("upscale", "resize")):
            raise prints.PrintError("run upscale + resize first, then mockups")
        if st.get("mockups", {}).get("status") in ("queued", "running"):
            raise prints.PrintError("mockups are already running for this design")
        con.execute("INSERT OR IGNORE INTO steps(listing_id, name) VALUES (?,?)", (lst["id"], "mockups"))
        con.execute("UPDATE steps SET status='queued', message='' WHERE listing_id=? AND name='mockups'", (lst["id"],))
        con.commit()
        return lst["id"]


def run(con, settings, lid, mockup_build=None):
    """Worker: the shared pipeline runner, stopped after mockups (earlier steps are already done)."""
    from .db import load_config
    from .pipeline import run_listing
    extra = {"settings": settings}
    if mockup_build:
        extra["mockup_build"] = mockup_build
    return run_listing(con, lid, load_config("pipeline"), lock=LOCK, stop_after="mockups", extra=extra)
