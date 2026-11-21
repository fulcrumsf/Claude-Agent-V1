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

from . import mockups, prints, scene_scan
from . import room_slots as rs
from . import slot_planner as splan
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
    if re.fullmatch(r"AB_\d{2}_\d{1,3}_\d{8}_\d{6}\.jpg", name):        # an A/B closeness variant (Archive only)
        a = folder / ARCHIVE / name
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


# ---------- Tony's grades (realism addendum 7, 2026-11-20) ----------
GRADES = tuple(stp.GRADE_SCORE)          # A+ ... F


def _slot_of(name, slots):
    """(slot number, slot record) of an image file name (NN_...), or (None, {})."""
    m = re.match(r"^(\d{2})_", str(name))
    if not m:
        return None, {}
    return int(m.group(1)), dict(slots.get(str(int(m.group(1)))) or {})


def grade(con, settings, idea_id, name, grade_value, note=None):
    """Tony's grade of one slot image: stored with the listing (production.grades[<file>]), in the template's
    Grades.json (scene_templates.add_grade, whitelisted keys) and on the reference used (references manifest).
    grade_value None clears it. Approve / Deny are untouched. Returns the stored entry (or None)."""
    from . import references
    if grade_value not in (None, "") and grade_value not in GRADES:
        raise ProductionError(f"grade must be one of {', '.join(GRADES)}")
    note = (str(note).strip()[:200] or None) if note else None
    with LOCK:
        lst = prints.listing_for(con, idea_id)
        if not lst:
            raise ProductionError("no listing for this design")
        rec = prints._record(con, lst["id"])
        p = _prod(rec)
        slot, srec = _slot_of(name, p["slots"])
        if slot is None:
            raise ProductionError(f"{name} is not a slot image")
        mine = srec.get("file") == name
        rel = srec.get("template") if mine else None
        ref = ((srec.get("reference") or {}).get("id") if mine and (srec.get("reference") or {}).get("sent") else None)
        gs = p.setdefault("grades", {})
        if grade_value in (None, ""):
            old = gs.pop(name, None)
            prints._save_record(con, lst["id"], rec)
            entry = None
            rel = rel or (old or {}).get("template")
            ref = ref or (old or {}).get("reference")
        else:
            entry = {"grade": grade_value, **({"note": note} if note else {}),
                     "at": datetime.now().isoformat(timespec="seconds"), "slot": slot, "template": rel,
                     "brief_rev": srec.get("brief_rev") if mine else None, "reference": ref}
            gs[name] = entry
            prints._save_record(con, lst["id"], rec)
    if rel:
        psd = stp.library(settings) / rel
        if psd.is_file():
            if entry:
                stp.add_grade(psd, {"idea_id": idea_id, "design": lst["title"], "slot": slot, "grade": grade_value,
                                    "note": note, "at": entry["at"]})
            else:
                stp.remove_grade(psd, idea_id, slot)
    eid = srec.get("engine_id") if mine else None
    if eid:
        try:
            from . import engines
            engines.record_room_grade(eid, idea_id, slot, grade_value if entry else None,
                                      stp.GRADE_SCORE.get(grade_value) if entry else None)
        except Exception:  # noqa: BLE001  (bookkeeping never breaks a grade)
            pass
    if ref:
        references.record_grade(settings, ref, {"idea_id": idea_id, "slot": slot, "grade": grade_value, "note": note,
                                                "at": datetime.now().isoformat(timespec="seconds")} if entry else
                                {"idea_id": idea_id, "slot": slot, "grade": None})
    return entry


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


def _engine(settings, con=None):
    """The panel's room-scene engine (controls addendum E.1): Tony's `ui.scene_engine` (app/prefs.py) when set, else
    the setting room_scene_engine. With the defaults this is exactly the old {"id": "nbpro", 18 credits, ...}."""
    from . import prefs
    eng = prefs.get(con, settings, "scene_engine") if con is not None else \
        settings.get("room_scene_engine", stp.DEFAULTS["room_scene_engine"])
    return _engine_info(settings, eng)


def _engine_info(settings, eng):
    info = stp.scene_engine(eng)
    return {"id": info["key"] if info["scene_id"] else info["id"], "engine_id": info["id"], "label": info["label"],
            "credits_per_scene": info["credits_per_scene"], "usd_per_scene": info["usd_per_scene"],
            "upper": info["upper"], "est": info["est"], "takes_ref": info["takes_ref"], "gate": info["gate"],
            "provider": info["provider"], "scene_id": info["scene_id"], "price_label": info.get("price_label"),
            "resolution": settings.get("room_scene_resolution", "2K")}


def slot_engine(con, settings, rec, slot):
    """The engine one slot uses: the card's own pick (listing record production.slot_engines) > the panel default
    (ui.scene_engine) > the setting. "nbpro" and "nano-banana-pro" are the same engine."""
    own = ((rec or {}).get("production") or {}).get("slot_engines", {}).get(str(slot))
    if own:
        return dict(_engine_info(settings, own), own=True)
    return dict(_engine(settings, con), own=False)


def set_slot_engine(con, settings, idea_id, slot, engine):
    """Tony's per-card engine (None = the panel default)."""
    from . import engines
    if engine not in (None, ""):
        eid = engines.scene_engine_id(engine)
        if not eid or not (engines.room_info(engines.raw_engine(eid)) or {}):
            raise ProductionError(f"unknown room engine {engine}")
        engine = eid
    with LOCK:
        lst = prints.listing_for(con, idea_id)
        if not lst:
            raise ProductionError("run upscale + resize first (Art tab)")
        rec = prints._record(con, lst["id"])
        se = _prod(rec).setdefault("slot_engines", {})
        if engine in (None, ""):
            se.pop(str(slot), None)
        else:
            se[str(slot)] = engine
        prints._save_record(con, lst["id"], rec)


def checker_fails(settings=None):
    """Templates the template checker FAILED (app/template_checker.py results; a PSD changed since its check counts
    as unchecked). They are never picked automatically; Tony can still pick one with "+"."""
    from . import template_checker as tc
    data = tc.load((settings or {}).get("template_checks_path"))
    return {rel for rel, r in (data.get("results") or {}).items() if r.get("status") == "FAIL"}


def library_picks(plan, slots, lib, fails=frozenset(), briefs=None):
    """Which library template each card's next click uses, decided in slot order so no two cards (and no template
    already used in this listing) share one; a template a slot already tried, or one the checker FAILED, is skipped.
    {slot: template or None}. briefs = {slot: usable set-plan brief} (app/slot_planner.py): a "library" brief gets its
    planned template (reserved first), a "new" brief gets None (a new scene) even when an old-style match exists;
    slots without a brief are decided exactly as before."""
    used = {s.get("template") for s in slots.values() if s.get("template")}
    out = {}
    briefs = briefs or {}
    by_rel = {t["rel"]: t for t in lib}
    reserved = {}
    for c in sorted(plan, key=lambda c: c["slot"]):
        b = briefs.get(c["slot"])
        if b and b.get("source") == "library":
            t = by_rel.get(b.get("library_rel"))
            if t is not None and t["rel"] not in fails and t["rel"] not in used:
                reserved[c["slot"]] = t
                used.add(t["rel"])
    for c in sorted(plan, key=lambda c: c["slot"]):
        b = briefs.get(c["slot"])
        if c["slot"] in reserved:
            out[c["slot"]] = reserved[c["slot"]]
            continue
        if b and b.get("source") == "new":
            out[c["slot"]] = None
            continue
        srec = slots.get(str(c["slot"])) or {}
        mine = srec.get("template")
        cands = [t for t in lib if stp.matches(t, c["room"], c["decor"], c["ratio"]) and t["rel"] not in fails
                 and t["rel"] not in used and t["rel"] != mine and t["rel"] not in (srec.get("tried") or [])
                 and stp.auto_pick_ok(t)]          # graded below B- or text-scan flagged: only with "+"
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


def _briefs(rec, cards):
    """{slot: usable set-plan brief} for these cards (slot_planner.brief_for: not stale, lint passed, plan usable)."""
    out = {}
    for c in cards:
        b = splan.brief_for(rec, c["slot"])
        if b:
            out[c["slot"]] = b
    return out


def panel(con, settings, idea_id, prefix="/ikigai", start_auto=None, start_plan=None):
    """Everything the big middle panel shows for one design. start_plan(idea_id): the set planner's background
    trigger (slot_planner.auto: no plan yet, or the inputs changed)."""
    if start_plan:
        start_plan(idea_id)
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
    engine = _engine(settings, con)
    approvals = rec.get("mockup_approvals") or {}
    slots = _prod(rec)["slots"]
    job = job_state()
    cards = []
    planned = {c["slot"] for c in plan}
    extra = [{"slot": int(k), "room": s.get("room") or "Room", "decor": s.get("decor") or "Modern",
              "ratio": s.get("ratio") or "2x3", "by": "earlier", "reason": "not in the current plan",
              "ratio_label": rs.RATIO_LABEL.get(s.get("ratio") or "2x3")}
             for k, s in slots.items() if int(k) not in planned and (s.get("file") or s.get("state"))]
    usable = _briefs(rec, plan + extra)
    picks = library_picks(plan + extra, slots, lib, checker_fails(settings), usable)
    set_plan = splan.get_plan(rec) or {}
    for c in sorted(plan + extra, key=lambda c: c["slot"]):
        srec = slots.get(str(c["slot"])) or {}
        b = usable.get(c["slot"])
        if b and b.get("ratio"):
            c = {**c, "ratio": b["ratio"], "ratio_label": rs.RATIO_LABEL.get(b["ratio"], b["ratio"])}
        name, p, where = _current_image(folder, c["slot"], srec, rec)
        img = None
        if name:
            img = {"file": name, "url": _url(prefix, idea_id, p, name), "status": approvals.get(name, "pending"),
                   "grade": ((_prod(rec).get("grades") or {}).get(name) or {}).get("grade"),
                   "where": where, "flagged": where == "flagged", "guard": srec.get("guard") if srec.get("file") == name
                   else None, "mb": round(p.stat().st_size / 1e6, 1), "print": srec.get("print")
                   if srec.get("file") == name else None}
        running = job["running"] and job["idea_id"] == idea_id and job["slot"] == c["slot"]
        state = "running" if running else (srec.get("state") if srec.get("state") in ("failed",) else "idle")
        made_for = None
        if srec.get("file") == name and srec.get("room") and (srec.get("room"), srec.get("decor")) != (c["room"], c["decor"]):
            made_for = f"{srec.get('room')} · {srec.get('decor')}"
        ce = slot_engine(con, settings, rec, c["slot"])
        nxt = _next_source(c, picks.get(c["slot"]), avail, ce)
        shown = b or (set_plan.get("briefs") or {}).get(str(c["slot"]))
        cb = splan.card_brief(shown)
        if cb is not None:
            cb["usable"] = bool(b)
            if cb.get("reference"):
                cb["ref_thumb_url"] = f"{prefix}/api/references/{cb['reference']}/blank"
            tight_fails = [a for a in (shown.get("attempts") or []) if a.get("result") in ("no_insert", "gate_fail")]
            cb["offer_wider"] = bool(shown.get("shot") == "tight" and len(tight_fails) >= 2)
        cards.append({**c, "image": img, "state": state, "message": srec.get("message", ""),
                      "stage": job["stage"] if running else "",
                      "source": srec.get("source"), "template": srec.get("template"),
                      "template_name": names.get(srec.get("template")) or (srec.get("template") or "").split("/")[-1],
                      "made_for": made_for, "next": nxt, "brief": cb,
                      "random_look": nxt["kind"] == "new" and not b,
                      "shot_drift": srec.get("shot_drift") if srec.get("file") == name else None,
                      "credits_spent": srec.get("credits"),
                      "engine": {k: ce.get(k) for k in ("engine_id", "label", "own", "takes_ref", "gate",
                                                        "credits_per_scene", "usd_per_scene", "upper", "est",
                                                        "provider")},
                      "engine_fail": srec.get("engine_fail") if srec.get("state") == "failed" or (
                          img and img.get("flagged")) else None,
                      "ref_note": (srec.get("reference") or {}).get("note") if srec.get("file") == name else None})
    styles, source = effective_styles(tags)
    from . import prefs
    live = prefs.all_prefs(con, settings)
    return {"idea_id": idea_id, "name": lst["title"], "title": idea["title"],
            "image_url": prints.status(con, idea_id, settings, prefix)["image_url"],
            "folder_rel": f"Designs/{folder.parent.name}/03-Etsy Images",
            "rooms_all": rs.ETSY_ROOMS, "max_rooms": rs.MAX_PICKS, "styles_all": _vocab(),
            "room_slots": rs.room_slots(settings),
            "rooms": tags.get("rooms") or [], "styles": tags.get("styles") or [],
            "styles_auto": (tags.get("auto_styles") or {}).get("styles") or [],
            "styles_auto_error": (tags.get("auto_styles") or {}).get("error"),
            "styles_used": styles, "styles_source": source, "slots": cards, "job": job, "engine": engine,
            "prints": len(arts), "set_plan": splan.panel_view(set_plan, splan.is_running(idea_id), live),
            "queue": queue_of(cards), "prefs": live, "room_engines": _room_engines(),
            "batch": batch_state(idea_id), "refresh": _refresh_view(settings),
            "batches": (_prod(rec).get("batches") or [])[-5:], "abtest": _abtest_view(set_plan, prefix)}


def queue_of(cards):
    """The Generate-all order (controls addendum F): open cards, free library first then slot order, with the credits
    each costs, its engine, reference mode and upper bound. A card with an image that is not denied is not open."""
    q = []
    for c in cards:
        if c["next"]["kind"] == "none" or c["state"] == "running" or not (c["image"] is None
                                                                        or c["image"]["status"] == "denied"):
            continue
        e = c.get("engine") or {}
        br = c.get("brief") or {}
        lib = c["next"]["kind"] == "library"
        q.append({"slot": c["slot"], "source": c["next"]["kind"], "credits": c["next"].get("credits") or 0,
                  "planned": bool(br.get("usable")), "engine": None if lib else e.get("engine_id"),
                  "engine_label": None if lib else e.get("label"),
                  "upper": 0 if lib else (e.get("upper") if e.get("upper") is not None else c["next"].get("credits") or 0),
                  "usd": 0 if lib else e.get("usd_per_scene"), "est": False if lib else bool(e.get("est")),
                  "gate": None if lib else e.get("gate"), "reference": br.get("reference"),
                  "provider": None if lib else e.get("provider"),
                  "reference_mode": (br.get("reference_mode") or "image") if br.get("reference") else None,
                  "lint_ok": (br.get("lint") or {}).get("pass", True) if br else True,
                  "label": c["next"].get("label")})
    return sorted(q, key=lambda x: (x["source"] != "library", x["slot"]))


def generate_queue(con, settings, idea_id):
    """Ordered open slots with source and credits (library first); see queue_of."""
    return panel(con, settings, idea_id)["queue"]


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


def start_slot(con, settings, idea_id, slot, template_rel=None, by_batch=False):
    """Claim the single job slot for this card. The caller runs run_slot in a worker. One click = Tony's approval
    of the cost (a library template costs nothing; a new scene costs credits). While Generate all runs, card clicks
    are refused (the batch claims the job slot itself, by_batch=True)."""
    if slot not in rs.room_slots(settings):
        raise ProductionError("room images are slot 3 and slots 9-19")
    _ctx(con, settings, idea_id)
    if template_rel and template_rel not in {t["rel"] for t in stp.library_templates(settings)}:
        raise ProductionError("no such template in the library")
    if not by_batch and batch_running():
        raise ProductionError("Generate all is running")
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


def art_gate(settings, psd, man, render, work):
    """The art-area gate (room_templates.art_area_gate) on one render of template `psd` (manifest `man`)."""
    from . import template_checker as tc
    base = rt.gate_base(man, Path(psd).parent, render, psd, settings, work)
    from .despill import marker_of
    return rt.art_area_gate(render, base, man["quad_art"], tc.presentation_of(man), man.get("wrap_strips"),
                            marker_of(man))


_real_art_gate = art_gate        # tests swap art_gate for a stub and restore this one


def _with_gate(g, ag):
    return {**g, "art_area": ag, "pass": bool(g["pass"] and ag["pass"]), "why": list(g["why"]) + list(ag["why"])}


SHOT_RANK = {"tight": 0, "medium": 1, "wide": 2}
GEOMETRY_KEYS = ("so_px", "so_ratio", "quad_insert", "quad_art", "quad_paper", "mode", "canvas", "light_from",
                 "opening_pad_px", "presentation", "wrap_strips", "despill", "insert", "shadows", "card_test", "marker")


def rebuild_from_scene(settings, psd, man, work, why=""):
    """Free (no credits): template `psd` rebuilt from its saved scene PNG with the current builder (which covers blank
    bands beside the art, scene_templates.build_psd). The new PSD is saved NEXT TO the live one as a rebuild waiting
    for Tony (<stem>_Rebuild_<stamp>.psd + sidecar <stem>.json, kind rebuild, approved false; template_gallery); the
    live PSD is untouched until he approves. Returns (new psd, its manifest)."""
    from . import template_gallery as tg
    psd = Path(psd)
    scene = psd.parent / str(man.get("scene") or "")
    if not man.get("scene") or not scene.is_file():
        raise stp.TemplateError("no saved scene to rebuild from")
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    box = ((man.get("insert") or {}).get("sam") or {}).get("box")
    from .despill import marker_of
    built = stp.build_psd(scene, man["ratio"], work, settings, box=box, presentation=man.get("presentation"),
                          marker=marker_of(man))
    new = psd.with_name(f"{psd.stem.removesuffix('_Template')}_Rebuild_{datetime.now():%Y%m%d_%H%M%S}_Template.psd")
    shutil.copy2(built["psd_tmp"], new)
    side = {k: v for k, v in man.items() if k not in GEOMETRY_KEYS + ("approved", "approved_at")}
    side.update({k: built[k] for k in GEOMETRY_KEYS if k in built})
    side.update(kind=tg.REBUILD_KIND, psd=new.name, replaces=psd.name, approved=False,
                rebuilt={"when": datetime.now().isoformat(timespec="seconds"), "from": man.get("scene"), "credits": 0,
                         "why": why or "the art-area gate found blank bars beside the art"})
    new.with_suffix(".json").write_text(__import__("json").dumps(side, indent=1) + "\n")
    return new, side


def _attempt(con, idea_id, slot, rev, entry):
    """Append one attempt to the slot's set-plan brief (same rev only; never raises)."""
    try:
        with LOCK:
            lst = prints.listing_for(con, idea_id)
            rec = prints._record(con, lst["id"])
            b = ((splan.get_plan(rec) or {}).get("briefs") or {}).get(str(slot))
            if b is not None and b.get("rev") == rev:
                b.setdefault("attempts", []).append(dict(entry, at=datetime.now().isoformat(timespec="seconds")))
                prints._save_record(con, lst["id"], rec)
    except Exception:  # noqa: BLE001
        pass


def scan_scene(png, settings=None, overlay=None):
    """The free output scan of a new scene (app/scene_scan.py); tests swap this for a stub."""
    return scene_scan.scan(png, settings, overlay=overlay)


def _scan_scene(settings, scene, td):
    try:
        return scan_scene(scene, settings, overlay=str(Path(td) / "scan.png"))
    except Exception as e:  # noqa: BLE001  (a broken scanner never blocks a paid scene; noted on the template)
        return {"pass": True, "severity": "none", "findings": [], "mode": "error", "notes": [str(e)[:120]]}


def _leak(scene, built, marker):
    """Share of the scene within dE 12 of the insert colour outside the built art quad, or None."""
    try:
        from PIL import Image
        import numpy as np
        with Image.open(scene) as im:
            rgb = np.asarray(im.convert("RGB"))
        return scene_scan.marker_leak(rgb, built["quad_art"], marker or "orange")
    except Exception:  # noqa: BLE001
        return None


def _reference_for(settings, brief, marker, td, engine=None):
    """The reference photograph to send with a planned pv2 scene (realism addendum 2.5), or None when the brief has
    none. {"id", "png" (None = text-only), "sent", "flip", "note"}. Controls addendum: a brief in reference_mode
    "tags" sends no image (its tag sentence is already in the prompt); an engine that takes no photo never gets one;
    closeness below 50 sends a smaller, blurred copy (references.prep_for)."""
    if not brief or brief.get("pv") != splan.PV or not brief.get("reference"):
        return None
    from . import references
    rid = brief["reference"]
    out = {"id": rid, "png": None, "sent": False, "flip": bool(brief.get("reference_flip")), "note": ""}
    if engine is None:
        engine = _engine_info(settings, settings.get("room_scene_engine", stp.DEFAULTS["room_scene_engine"]))
    if brief.get("reference_mode") == "tags":
        out["note"] = "reference used as words"
    elif not splan.cfg(settings, "planner_references"):
        out["note"] = "reference not sent (setting)"
    elif not engine.get("takes_ref"):
        out["note"] = "reference used as words (engine takes no photo)" if brief.get("ref_tag_text") else \
            "reference not sent (engine)"
    else:
        entry = (references.load(references.ref_dir(settings)).get("refs") or {}).get(rid)
        if not entry or not entry.get("blank") or not (references.ref_dir(settings) / entry["blank"]).is_file():
            out["note"] = "reference not sent (blank missing)"
        else:
            try:
                out["png"] = references.prep_for(entry, marker or "orange", out["flip"],
                                                 brief.get("ref_closeness", references.DEFAULT_CLOSENESS), td, settings)
                out["sent"] = True
            except Exception as e:  # noqa: BLE001
                out["note"] = f"reference not sent ({str(e)[:60]})"
    return out


def _gen(prompt, scene, settings, generator, engine, ref_imgs=()):
    """generate_scene for the slot's engine; with the default engine exactly the old call."""
    kw = {"ref_imgs": ref_imgs} if ref_imgs else {}
    if engine is not None and engine.get("id") != settings.get("room_scene_engine", stp.DEFAULTS["room_scene_engine"]):
        kw["engine"] = engine["id"]
    return stp.generate_scene(prompt, scene, settings, generator, **kw)


def _generate(settings, prompt, scene, generator, ref, brief, engine=None):
    """generate_scene with the reference image when it can be sent. A refusal ("flagged as sensitive") that did not
    move the balance is retried ONCE text-only inside the same click (so one click costs at most one scene), and the
    reference is marked kie_refused so the planner never picks it again."""
    if not ref or not ref["sent"]:
        return _gen(prompt, scene, settings, generator, engine)
    before = stp.kie_balance(settings)
    try:
        return _gen(prompt, scene, settings, generator, engine, [ref["png"]])
    except stp.TemplateError as e:
        if not stp.is_refusal(str(e)):
            raise
        after = stp.kie_balance(settings)
        moved = before is None or after is None or abs(after - before) > 0.01     # unknown counts as moved
        from . import references
        references.mark_refused(settings, ref["id"])
        if moved:
            raise stp.TemplateError(f"{e} (reference {ref['id']} refused; the balance moved, so no retry)")
        ref.update(sent=False, note=f"reference {ref['id']} refused by kie.ai; retried text-only")
        return _gen(splan.assemble(brief, ref=False), scene, settings, generator, engine)


def _classify(msg):
    """hard (stop a batch: key missing, auth / balance refused) | network | slot (this slot only)."""
    m = str(msg or "").lower()
    if "is not set" in m or "missing" in m and "key" in m:
        return "hard"
    if stp.is_refusal(m) and not re.search(r"credit|balance|insufficient|unauthori|forbidden|401|402|403", m):
        return "slot"
    if re.search(r"credit|balance|insufficient|unauthori|forbidden|\b40[123]\b|auth", m):
        return "hard"
    if "network" in m or "could not be reached" in m or "took too long" in m:
        return "network"
    return "slot"


def run_slot(con, settings, idea_id, slot, template_rel=None, generator=None, engine=None, brief_override=None,
             place=True, ab=None):
    """Worker for one card: pick the source, render, guard, place. Always releases the job slot.
    With a usable set-plan brief for the slot (app/slot_planner.py) and no "+" pick: a "library" brief renders its
    planned template; a "new" brief sends its saved prompt (no random look), builds with its ratio, presentation and
    insert marker, saves the brief (not a look) in template.json and logs the attempt on the brief. Without one,
    everything runs exactly as before (random look).
    Controls addendum: engine = the slot's engine (card pick > panel default > setting); brief_override + place=False
    = an A/B variant (the render goes to 03-Etsy Images/Archive/AB_..., the slot is untouched). Returns an outcome
    {kind: done | flagged | failed, hard, network, credits, usd, why} (single-card callers ignore it)."""
    brief, attempt = None, None
    spent = {"credits": None, "usd": None}
    efail = {}
    outcome = {"kind": "failed", "hard": False, "network": False, "credits": None, "usd": None, "why": ""}
    try:
        idea, lst, rec, folder, arts = _ctx(con, settings, idea_id)
        if not arts:
            raise stp.TemplateError("the print JPGs are missing; run upscale + resize first")
        eng = _engine_info(settings, engine) if engine else slot_engine(con, settings, rec, slot)
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
        elif brief_override is not None:        # an A/B variant: always a new scene from this brief
            brief = brief_override
            card = {**card, "ratio": brief.get("ratio") or card["ratio"]}
            t, source = None, "new"
        else:                                   # the same choice the card showed (library_picks, slot order)
            plan_all = plan if any(c["slot"] == slot for c in plan) else plan + [card]
            usable = _briefs(rec, plan_all)
            brief = usable.get(slot)
            if brief and brief.get("ratio"):
                card = {**card, "ratio": brief["ratio"]}
            t = library_picks(plan_all, _prod(rec)["slots"], lib, checker_fails(settings), usable).get(slot)
            source = "library" if t else "new"
        out = {"room": card["room"], "decor": card["decor"], "ratio": card["ratio"], "source": source,
               "credits": 0, "new_template": None}
        if brief:
            out.update(brief_rev=brief.get("rev"), brief_source=brief.get("source"))
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            render = td / "render.png"
            if t is None:
                if card["ratio"] not in (avail.get(card["room"]) or []):
                    raise stp.TemplateError(f"no {card['room']} folder in Room_Templates for "
                                            f"{rs.RATIO_LABEL[card['ratio']]}; pick a template with +")
                if brief and brief.get("source") == "new":    # the planned scene: its saved prompt, no random look
                    look, prompt = None, brief["prompt"]
                    pres = "canvas" if brief.get("presentation") in ("canvas", "canvas_bare") else brief["presentation"]
                    marker = brief.get("marker") or "orange"
                else:
                    look = rs.pick_look(card["room"], card["decor"])      # weighted random, saved in template.json
                    prompt = rs.scene_prompt(card["room"], card["decor"], card["ratio"], look=look)
                    pres = rs.presentation_for(card["room"], card["decor"], card["ratio"])
                    marker = "orange"
                attempt = {"result": "not_drawn", "rev": (brief or {}).get("rev")} if brief else None
                scene = td / "scene.png"
                ref = _reference_for(settings, brief, marker, td, eng) if look is None else None
                if ref and ref["png"] is None:                        # the reference could not be sent: text-only
                    prompt = splan.assemble(brief, ref=False)
                _stage(f"drawing the room ({eng['label'] if not eng.get('scene_id') else 'kie.ai'})")
                gen = _generate(settings, prompt, scene, generator, ref, brief, eng)
                if ref:
                    out["reference"] = {k: ref[k] for k in ("id", "sent", "note", "flip")}
                    if attempt:
                        attempt["reference_sent"] = ref["sent"]
                    if not ref["sent"]:
                        prompt = splan.assemble(brief, ref=False)
                out["credits"] = gen.get("credits")
                spent.update(credits=gen.get("credits"), usd=gen.get("usd"))
                out["engine_id"] = eng["engine_id"]
                if gen.get("usd") is not None and not eng.get("scene_id"):
                    out["usd"] = gen.get("usd")
                if not eng.get("scene_id"):                # ~1 MP engines: enlarge before the build (free, local)
                    _stage("enlarging a small scene (Upscayl, free)")
                    stp.upscale_scene(scene, settings, int(settings.get("scene_min_width", 2000)))
                _stage("checking the scene for stray text (free)")
                scan = _scan_scene(settings, scene, td)
                if scan["severity"] == "hard":
                    if attempt:
                        attempt["result"] = "stray_text"
                    folder.joinpath(ARCHIVE).mkdir(parents=True, exist_ok=True)
                    stamp = f"{datetime.now():%Y%m%d_%H%M%S}"
                    keep = folder / ARCHIVE / f"Scene_Stray_Text_{slot:02d}_{stamp}.png"
                    shutil.copy2(scene, keep)
                    if scan.get("overlay") and Path(scan["overlay"]).is_file():
                        shutil.copy2(scan["overlay"], folder / ARCHIVE / f"Scene_Stray_Text_{slot:02d}_{stamp}_Scan.png")
                    raise stp.TemplateError(f"{scene_scan.summary(scan)} (scene kept as {ARCHIVE}/{keep.name}); "
                                            "Regenerate for a new scene")
                _stage("finding the frame, building the PSD")
                (td / "build").mkdir()
                try:
                    if marker == "orange":           # byte-identical call for the orange path
                        built = stp.build_psd(scene, card["ratio"], td / "build", settings, presentation=pres)
                    else:
                        built = stp.build_psd(scene, card["ratio"], td / "build", settings, presentation=pres,
                                              marker=marker)
                except stp.TemplateError as e:
                    if attempt:
                        attempt["result"] = "no_insert"
                    folder.joinpath(ARCHIVE).mkdir(parents=True, exist_ok=True)
                    keep = folder / ARCHIVE / f"Scene_No_Insert_{slot:02d}_{datetime.now():%Y%m%d_%H%M%S}.png"
                    shutil.copy2(scene, keep)
                    why = str(e) if "off the print ratio" in str(e) else "the scene has no clean blank frame insert"
                    if eng.get("gate") != "trusted" and eng.get("engine_id"):
                        _engine_check_fail(eng, f"{eng['label']} gave no clean blank insert", keep.name)
                        efail.update(engine=eng["engine_id"], label=eng["label"],
                                     why=f"{eng['label']} did not draw a clean, flat blank insert")
                    raise stp.TemplateError(f"{why} (scene kept as {ARCHIVE}/{keep.name}); Regenerate for a new scene")
                leak = _leak(scene, built, marker)
                if leak is not None and leak > scene_scan.LEAK_MAX:      # the insert colour outside the art: soft
                    extra, _ = scene_scan.classify((), (), leak)
                    scan = dict(scan, findings=list(scan.get("findings") or []) + extra, severity="soft"
                                if scan["severity"] == "none" else scan["severity"])
                    scan["pass"] = False
                bmeta = None
                if look is None:
                    bmeta = {**{k: v for k, v in brief.items() if k not in ("history", "attempts", "prompt")},
                             **({"reference_sent": ref["sent"]} if ref else {})}
                    if brief.get("pv") == splan.PV:
                        bmeta["engine"] = eng["engine_id"]
                    if ab:
                        bmeta["ab"] = ab
                meta = {"prompt": prompt, **({"look": look} if look is not None else {"brief": bmeta}),
                        **({"text_scan": {k: scan.get(k) for k in ("pass", "severity", "findings", "mode")}}
                           if scan.get("mode") != "off" else {}),
                        "engine": eng["id"],
                        "model": gen.get("model"), "resolution": settings.get("room_scene_resolution", "2K"),
                        "aspect": settings.get("room_scene_aspect", "4:3"), "credits": gen.get("credits"),
                        "made_for": {"idea_id": idea_id, "design": lst["title"], "slot": slot},
                        "engine_id": eng["engine_id"], "engine_provider": eng.get("provider"),
                        "engine_model": gen.get("model"), "usd": gen.get("usd"),
                        "cost_measured": bool(gen.get("measured", gen.get("left") is not None))}
                tdir, psd = stp.save_template(settings, card["room"], card["decor"], card["ratio"], scene, built, meta)
                rel = psd.relative_to(stp.library(settings)).as_posix()
                man = stp.load_manifest(psd)
                _stage("rendering the art into the room")
                art = stp.print_for(arts, rs.RATIO_VALUE[card["ratio"]], rs.PRINT_RATIO_TAG[card["ratio"]])
                r = stp.render_psd(psd, man["so_px"], art, render, settings, td, manifest=man)
                g = rt.guard_quad(render, r["fitted"], man["quad_art"], tdir / man["scene"],
                                  man.get("guard_max_cover"), settings)
                g = _with_gate(g, art_gate(settings, psd, man, render, td))     # a fresh build: nothing to rebuild
                if scan["severity"] == "soft":         # realism 6.4: built (credits not wasted) but flagged for Tony
                    g = {**g, "pass": False, "why": list(g["why"]) + [scene_scan.summary(scan)], "text_scan": False}
                if eng.get("gate") != "trusted" and eng.get("engine_id"):     # E.4 first-real-scene check (free)
                    chk = engine_scene_check(scene, built, marker, scan, g)
                    out["engine_check"] = chk
                    if chk["pass"]:
                        out["engine_gate"] = _engines().record_room_check(eng["engine_id"], True, "", rel)
                    else:
                        _engine_check_fail(eng, chk["why"], rel)
                        out["engine_fail"] = {"engine": eng["engine_id"], "label": eng["label"], "why": chk["why"]}
                        g = {**g, "pass": False, "why": list(g["why"]) + [chk["why"]]}
                out.update(template=rel, new_template=rel, print=art.name, cropped=r["cropped"])
                if ref and ref["sent"]:
                    from . import references
                    references.record_use(settings, ref["id"], {"idea_id": idea_id, "listing": lst["title"],
                                                                 "slot": slot, "template": rel})
                if brief:
                    m2 = stp.shot_meta(man)
                    drift = None
                    if m2.get("shot") and m2["shot"] != brief.get("shot"):
                        wider = SHOT_RANK[m2["shot"]] > SHOT_RANK.get(brief.get("shot"), 1)
                        drift = (f"drawn {'wider' if wider else 'tighter'} than planned ({m2['shot']} shot, art "
                                 f"{m2['art_h_frac']:.0%} of the picture height; planned {brief.get('shot')})")
                        out["shot_drift"] = drift
                    attempt = {"result": "built" if g["pass"] else "gate_fail", "rev": brief.get("rev"),
                               "template": rel, "drift": drift, "why": "; ".join(g["why"])[:300]}
                    if ref:
                        attempt["reference_sent"] = ref["sent"]
                    if scan["severity"] == "soft":
                        attempt["result"] = "text_flag"
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
                ag = art_gate(settings, t["psd"], man, render, td)
                out.update(template=t["rel"], print=art.name, cropped=r["cropped"])
                if not ag["pass"] and man.get("scene") and (t["psd"].parent / man["scene"]).is_file():
                    # Tony 2026-11-19: a bar beside the art is never shown as a normal card. A library template with
                    # its saved scene is rebuilt for free with the current builder and rendered again; the rebuild
                    # waits in the Templates tab for his Approve (the live PSD is untouched)
                    _stage("white bar beside the art: rebuilding the template from its saved scene (free)")
                    try:
                        npsd, nman = rebuild_from_scene(settings, t["psd"], man, td / "rebuild",
                                                        "; ".join(ag["why"]))
                        r2 = td / "render_rebuilt.png"
                        rr = stp.render_psd(npsd, nman["so_px"], art, r2, settings, td / "rebuild", manifest=nman)
                        g2 = rt.guard_quad(r2, rr["fitted"], nman["quad_art"], None, None, settings)
                        ag2 = art_gate(settings, npsd, nman, r2, td / "rebuild")
                        rel2 = npsd.relative_to(stp.library(settings)).as_posix()
                        out["rebuilt"] = {"template": rel2, "first_render": ag, "pass": ag2["pass"]}
                        if ag2["pass"]:
                            shutil.copyfile(r2, render)
                            r, g, ag = rr, g2, ag2
                            out.update(template=rel2, cropped=rr["cropped"])
                    except Exception as e:  # noqa: BLE001  (the first render stays, flagged with its reason)
                        out["rebuilt"] = {"error": str(e)[:200], "first_render": ag}
                g = _with_gate(g, ag)
            if not place:                                # an A/B variant: Archive only, the slot is untouched
                folder.joinpath(ARCHIVE).mkdir(parents=True, exist_ok=True)
                stamp = f"{datetime.now():%Y%m%d_%H%M%S}"
                placed = mockups._place(render, folder / ARCHIVE / f"AB_{slot:02d}_{(ab or {}).get('value', 'x')}_{stamp}.jpg")
                outcome.update(kind="done" if g["pass"] else "flagged", credits=spent["credits"], usd=spent["usd"],
                               why="" if g["pass"] else "; ".join(g["why"])[:300], file=placed.name,
                               template=out.get("template"))
                return outcome
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
                                                        + "; ".join(g["why"])) + (
                                                (" " if not g["pass"] else "") + out["shot_drift"].capitalize() + "."
                                                if out.get("shot_drift") else ""),
                                            "made": datetime.now().isoformat(timespec="seconds"),
                                            "history": (old.get("history") or []) + ([old["file"]] if old.get("file") else [])}
                prints._save_record(con, lst["id"], rec)
        if attempt:
            _attempt(con, idea_id, slot, attempt.get("rev"), attempt)
        outcome.update(kind="done" if g["pass"] else "flagged", credits=spent["credits"], usd=spent["usd"],
                       why="" if g["pass"] else "; ".join(g["why"])[:300])
    except Exception as e:  # noqa: BLE001  (shown on the card; the job slot is always released)
        msg = str(e) if isinstance(e, (ProductionError, stp.TemplateError)) else f"Something went wrong: {e}"
        kind = _classify(msg)
        outcome.update(kind="failed", hard=kind == "hard", network=kind == "network", why=msg[:300],
                       credits=spent["credits"], usd=spent["usd"])
        if attempt:
            _attempt(con, idea_id, slot, attempt.get("rev"),
                     dict(attempt, result=attempt["result"] if attempt["result"] != "built" else "failed",
                          why=msg[:300]))
        if place:
            try:
                with LOCK:
                    lst = prints.listing_for(con, idea_id)
                    rec = prints._record(con, lst["id"])
                    s = _prod(rec)["slots"].setdefault(str(slot), {})
                    s.update(state="failed", message=msg[:400])
                    if efail:
                        s["engine_fail"] = dict(efail)
                    else:
                        s.pop("engine_fail", None)
                    prints._save_record(con, lst["id"], rec)
            except Exception:  # noqa: BLE001
                pass
    finally:
        with _job_lock:
            _job.update(running=False, idea_id=None, slot=None, stage="", started=None)
    return outcome


# ---------- per-engine room check (controls addendum E.4) ----------
INSERT_DE_MAX = 20.0          # the insert's median colour within dE76 20 of the asked marker colour
INSERT_TEXTURE_MAX = 9.0      # std of L inside the insert (a flat, evenly lit block is ~1-4; a painted picture >> 10)
ASPECT_TOL = 0.02


def _engines():
    from . import engines
    return engines


def engine_scene_check(scene, built, marker, scan, g):
    """The first-real-scene check of an engine not yet trusted (free): the insert is flat and in the marker colour,
    the scene is 4:3, and guard + art-area gate + output scan passed. {pass, why, de, texture, aspect}."""
    from PIL import Image
    import cv2
    import numpy as np
    from .template_checker import offset_quad, poly_mask
    with Image.open(scene) as im:
        rgb = np.asarray(im.convert("RGB"))
    H, W = rgb.shape[:2]
    why = []
    q = np.float32(built.get("quad_insert") or built["quad_art"])
    side = float(np.mean([np.linalg.norm(q[(i + 1) % 4] - q[i]) for i in range(4)]))
    m = poly_mask(offset_quad(q, -0.08 * side), W, H) > 0.5
    de = tex = None
    if m.sum() > 50:
        lab = cv2.cvtColor(np.float32(rgb) / 255.0, cv2.COLOR_RGB2Lab)
        tgt = cv2.cvtColor(np.float32([[splan.MARKER_RGB.get(marker or "orange", splan.MARKER_RGB["orange"])]]) / 255.0,
                           cv2.COLOR_RGB2Lab)[0, 0]
        med = np.median(lab[m], 0)
        de = float(np.linalg.norm(med - tgt))
        tex = float(lab[m][:, 0].std())
        if de >= INSERT_DE_MAX:
            why.append(f"the insert is not the {marker or 'orange'} placeholder colour (dE {de:.0f})")
        if tex >= INSERT_TEXTURE_MAX:
            why.append("the blank insert is not flat (painted or textured)")
    asp = W / H
    if abs(asp - 4 / 3) / (4 / 3) > ASPECT_TOL:
        why.append(f"the scene is not 4:3 ({W}x{H})")
    if not g.get("pass"):
        why.append("the guard or art-area gate failed")
    if (scan or {}).get("severity") not in (None, "none"):
        why.append("the output scan found text or overlays")
    return {"pass": not why, "why": "; ".join(why), "de": round(de, 1) if de is not None else None,
            "texture": round(tex, 2) if tex is not None else None, "aspect": round(asp, 4)}


def _engine_check_fail(eng, why, where=None):
    gate = _engines().record_room_check(eng["engine_id"], False, why, where)
    return gate


def recover(con):
    """On startup: a card left running by a restart is marked failed (its thread is gone); a Generate-all run cut by
    the restart is recorded as interrupted (never resumed on its own)."""
    import json
    with LOCK:
        for r in con.execute("SELECT id, record FROM listings").fetchall():
            rec = json.loads(r["record"] or "{}")
            changed = False
            for s in ((rec.get("production") or {}).get("slots") or {}).values():
                if s.get("state") in ("queued", "running"):
                    s.update(state="failed", message="stopped by a Portal restart; run it again")
                    changed = True
            live = (rec.get("production") or {}).pop("batch_live", None)
            if live:
                live.update(status="interrupted", stop_reason="stopped by a Portal restart (not resumed)",
                            finished=datetime.now().isoformat(timespec="seconds"))
                for row in live.get("rows") or []:
                    if row.get("status") in ("waiting", "running"):
                        row.update(status="skipped", why="interrupted by a Portal restart")
                live["report"] = batch_report(live)
                bs = rec["production"].setdefault("batches", [])
                bs.append(live)
                rec["production"]["batches"] = bs[-5:]
                changed = True
            if changed:
                prints._save_record(con, r["id"], rec)


# ---------- Generate all open slots (controls addendum F) ----------
_batch = {"running": False, "idea_id": None, "rows": [], "spent": 0.0, "cap": None, "total": 0, "cancel": False,
          "started": None, "finished": None, "stop_reason": "", "kind": "all"}
_batch_lock = threading.Lock()


def batch_running():
    with _batch_lock:
        return bool(_batch["running"])


def batch_state(idea_id=None):
    with _batch_lock:
        b = {**_batch, "rows": [dict(r, brief=None) for r in _batch["rows"]]}
    if idea_id is not None and b.get("idea_id") not in (None, idea_id):
        return {"running": b["running"], "idea_id": b["idea_id"], "other_design": True, "rows": []}
    return b


def _room_engines():
    try:
        from . import engines
        return engines.room_engines()
    except Exception:  # noqa: BLE001
        return []


def _refresh_view(settings):
    try:
        from . import references
        return references.refresh_view(settings)
    except Exception:  # noqa: BLE001
        return None


def _abtest_view(set_plan, prefix):
    ab = (set_plan or {}).get("abtest") or {}
    out = {}
    for s, v in ab.items():
        out[s] = {"reference": v.get("reference"), "engine": v.get("engine"), "engine_label": v.get("engine_label"),
                  "credits_each": v.get("credits_each"), "status": v.get("status"), "message": v.get("message"),
                  "variants": {k: {"prompt": (b or {}).get("prompt"), "band": (b or {}).get("ref_band"),
                                   "lint": (b or {}).get("lint"), "result": ((v.get("results") or {}).get(k))}
                               for k, b in (v.get("variants") or {}).items()}}
    return out


def _row_key(rows):
    import hashlib
    import json
    keep = [{k: r.get(k) for k in ("slot", "source", "engine", "upper", "status", "reference", "reference_mode",
                                    "label", "why")} for r in rows]
    return hashlib.sha1(json.dumps(keep, sort_keys=True).encode()).hexdigest()


def estimate(con, settings, idea_id, cap=None):
    """What Generate all would do, in run order (library first, then slot order): rows with engine, reference mode,
    estimate and upper bound, skipped rows with reasons; totals per engine; the kie balance; the cap; key = sha1 of
    the rows (the POST must send it back unchanged). Free."""
    from . import engines, prefs
    pan = panel(con, settings, idea_id)
    sp = pan.get("set_plan") or {}
    if pan["job"]["running"] or batch_running():
        raise ProductionError("a slot is being made; wait for it to finish")
    if not pan["queue"]:
        raise ProductionError("no open slot to generate (every slot has an image waiting or approved)")
    if sp.get("status") in ("planning",) or sp.get("running"):
        raise ProductionError("the scenes are still being planned")
    if sp.get("status") == "failed":
        raise ProductionError("the scene plan failed; Re-plan open slots first")
    rows = []
    for q in pan["queue"]:
        r = {"slot": q["slot"], "source": q["source"], "engine": q["engine"], "engine_label": q["engine_label"],
             "est": q["credits"] if q["source"] == "new" else 0, "upper": q["upper"] if q["source"] == "new" else 0,
             "usd": q["usd"] or 0, "estimated": q["est"], "reference": q["reference"],
             "reference_mode": q["reference_mode"], "label": q["label"], "status": "waiting", "why": "",
             "provider": q.get("provider")}
        if q["source"] == "new" and not q["planned"]:
            r.update(status="skipped", why="no usable plan for this slot (Re-plan open slots)")
        elif not q["lint_ok"]:
            r.update(status="skipped", why="its prompt failed the rules check")
        elif q["source"] == "new" and q["gate"] not in engines.GATE_OK:
            r.update(status="skipped", why=f"{q['engine_label']} has not passed its room check yet "
                                           "(generate one by hand first)")
        rows.append(r)
    run = [r for r in rows if r["status"] == "waiting"]
    per = {}
    for r in run:
        if r["source"] == "new":
            p = per.setdefault(r["engine_label"], {"slots": 0, "credits": 0.0, "upper": 0.0, "usd": 0.0})
            p["slots"] += 1
            p["credits"] += r["est"] or 0
            p["upper"] += r["upper"] or 0
            p["usd"] += r["usd"] or 0
    cap = prefs.get(con, settings, "generate_all_cap") if cap is None else int(cap)
    total_up = round(sum(r["upper"] or 0 for r in run), 1)
    return {"idea_id": idea_id, "rows": rows, "per_engine": per, "total_credits": round(sum(r["est"] or 0 for r in run), 1),
            "total_upper": total_up, "total_usd": round(sum(r["usd"] or 0 for r in run), 3),
            "balance": stp.kie_balance(settings), "cap": cap, "runnable": len(run),
            "over_cap": total_up > cap, "key": _row_key(rows)}


def start_batch(con, settings, idea_id, key, cap, spawn, generator=None):
    """Tony's Confirm: refused when the estimate changed since he looked (key), when nothing can run, or when a job or
    another batch is running. Claims the batch and runs it in a worker."""
    est = estimate(con, settings, idea_id, cap)
    if est["key"] != key:
        raise ProductionError("the plan changed; check the new total")
    run = [r for r in est["rows"] if r["status"] == "waiting"]
    if not run:
        raise ProductionError("no open slot can be generated")
    with _batch_lock:
        if _batch["running"]:
            raise ProductionError("Generate all is already running")
        if job_state()["running"]:
            raise ProductionError("a slot is being made; wait for it to finish")
        _batch.update(running=True, idea_id=idea_id, rows=[dict(r) for r in est["rows"]], spent=0.0, cap=est["cap"],
                      total=est["total_upper"], cancel=False, started=datetime.now().isoformat(timespec="seconds"),
                      finished=None, stop_reason="", kind="all")
    _save_live(con, idea_id)
    spawn(run_batch, con, settings, idea_id, est["cap"], generator, est["total_upper"])
    return batch_state(idea_id)


def cancel_batch():
    with _batch_lock:
        if not _batch["running"]:
            return False
        _batch["cancel"] = True
        return True


def _save_live(con, idea_id, final=False):
    """Mirror the batch into the listing record (production.batch_live) so a restart can mark it interrupted; at the
    end it moves to production.batches (last 5) with its plain report."""
    try:
        with _batch_lock:
            snap = {k: v for k, v in _batch.items() if k not in ("running", "cancel")}
            snap["rows"] = [{k: v for k, v in r.items() if k not in ("brief",)} for r in _batch["rows"]]
        with LOCK:
            lst = prints.listing_for(con, idea_id)
            rec = prints._record(con, lst["id"])
            p = _prod(rec)
            if final:
                p.pop("batch_live", None)
                if snap.get("kind") == "all":
                    snap["report"] = batch_report(snap)
                    p["batches"] = (p.get("batches") or [])[-4:] + [snap]
            else:
                p["batch_live"] = snap
            prints._save_record(con, lst["id"], rec)
    except Exception:  # noqa: BLE001  (bookkeeping never stops a batch)
        pass


def batch_report(b):
    rows = b.get("rows") or []
    made = [r for r in rows if r.get("status") in ("done", "flagged")]
    flagged = [r for r in rows if r.get("status") == "flagged"]
    failed = [r for r in rows if r.get("status") == "failed"]
    t = f"Generate all {'finished' if b.get('status') != 'interrupted' else 'was interrupted'}: {len(made)} made"
    t += f" ({len(flagged)} flagged)" if flagged else ""
    if failed:
        t += f", {len(failed)} failed (" + "; ".join(f"slot {r['slot']}: {r.get('why') or 'failed'}"[:120]
                                                      for r in failed[:3]) + ")"
    if b.get("stop_reason"):
        t += f". {b['stop_reason']}"
    t += f". Spent {round(b.get('spent') or 0, 1):g} credits."
    return t


def _row_cost(res, row):
    if res.get("credits") is not None:
        return float(res["credits"])
    if res.get("usd") is not None:
        return round(float(res["usd"]) / 0.005, 1)
    if res.get("kind") in ("done", "flagged") and row["source"] == "new":
        return float(row.get("est") or 0)
    return 0.0


def run_batch(con, settings, idea_id, cap, generator=None, shown=None, place=True):
    """Worker: one slot at a time through the single job lock. Stops before a paid slot that would pass min(cap,
    shown total) or when the kie balance is below the slot's estimate; a hard failure (key, auth, balance, two network
    timeouts in a row) stops the run; a slot failure does not. Cancel stops after the running slot. Never approves."""
    limit = min(float(cap if cap is not None else 1e9), float(shown if shown is not None else 1e9))
    net = 0
    stop = ""
    try:
        while True:
            with _batch_lock:
                row = next((r for r in _batch["rows"] if r["status"] == "waiting"), None)
                cancel = _batch["cancel"]
                spent = _batch["spent"]
            if row is None:
                break
            if cancel:
                stop = f"Cancelled by you; stopped after {_last_done()}"
                break
            if row["source"] == "new":
                if spent + float(row.get("upper") or 0) > limit + 1e-9:
                    stop = (f"Stopped before slot {row['slot']}: it could cost up to {row.get('upper'):g} credits and "
                            f"the run is capped at {limit:g} ({spent:g} used)")
                    break
                if row.get("provider") in ("kie", None):
                    bal = stp.kie_balance(settings)
                    if bal is not None and bal < float(row.get("est") or 0):
                        stop = f"Stopped before slot {row['slot']} (kie.ai balance too low: {bal:g} credits)"
                        break
            with _batch_lock:
                row["status"] = "running"
            _save_live(con, idea_id)
            try:
                start_slot(con, settings, idea_id, row["slot"], by_batch=True)
            except ProductionError as e:
                with _batch_lock:
                    row.update(status="failed", why=str(e))
                continue
            res = run_slot(con, settings, idea_id, row["slot"], None, generator, engine=row.get("engine"),
                           brief_override=row.get("brief"), place=place, ab=row.get("ab"))
            cost = _row_cost(res, row)
            with _batch_lock:
                _batch["spent"] = round(_batch["spent"] + cost, 2)
                row.update(status=res["kind"], why=res.get("why") or "", spent=cost,
                           **({"file": res["file"]} if res.get("file") else {}),
                           **({"template": res["template"]} if res.get("template") else {}))
            _save_live(con, idea_id)
            if res.get("hard"):
                stop = f"Stopped after slot {row['slot']} ({res.get('why') or 'the provider refused'})"[:200]
                break
            net = net + 1 if res.get("network") else 0
            if net >= 2:
                stop = f"Stopped after slot {row['slot']} (two network timeouts in a row)"
                break
    except Exception as e:  # noqa: BLE001
        stop = f"Generate all stopped: {str(e)[:160]}"
    finally:
        with _batch_lock:
            for r in _batch["rows"]:
                if r["status"] == "waiting":
                    r.update(status="skipped", why=stop or "not run")
            _batch.update(running=False, cancel=False, stop_reason=stop,
                          finished=datetime.now().isoformat(timespec="seconds"))
        _save_live(con, idea_id, final=True)


def _last_done():
    rows = [r for r in _batch["rows"] if r["status"] not in ("waiting", "skipped")]
    return f"slot {rows[-1]['slot']}" if rows else "no slot"

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


# ---------- A/B closeness (controls addendum C.5): three variants of one slot, on the batch runner ----------

def ab_estimate(con, settings, idea_id, slot):
    """The confirm box of "Generate 3 variants": one row per planned variant (place False), cost from the slot's
    engine. Free."""
    with LOCK:
        lst = prints.listing_for(con, idea_id)
        rec = prints._record(con, lst["id"]) if lst else {}
    ab = ((splan.get_plan(rec) or {}).get("abtest") or {}).get(str(slot))
    if not ab:
        raise ProductionError("plan the A/B variants first (free)")
    eng = _engine_info(settings, ab.get("engine") or "nbpro")
    rows = []
    for v, b in sorted((ab.get("variants") or {}).items(), key=lambda x: int(x[0])):
        r = {"slot": int(slot), "source": "new", "engine": eng["engine_id"], "engine_label": eng["label"],
             "est": eng["credits_per_scene"] or 0, "upper": eng["upper"] or eng["credits_per_scene"] or 0,
             "usd": eng["usd_per_scene"] or 0, "reference": ab.get("reference"), "reference_mode": "image",
             "label": f"closeness {v}", "status": "waiting", "why": "", "provider": eng["provider"],
             "ab": {"slot": int(slot), "value": int(v)}}
        if not (b or {}).get("prompt"):
            r.update(status="skipped", why="its prompt failed the rules check")
        rows.append(r)
    run = [r for r in rows if r["status"] == "waiting"]
    return {"rows": rows, "total_upper": round(sum(r["upper"] for r in run), 1),
            "total_usd": round(sum(r["usd"] for r in run), 3), "balance": stp.kie_balance(settings),
            "key": _row_key(rows), "briefs": ab.get("variants") or {}}


def start_abtest(con, settings, idea_id, slot, key, spawn, generator=None):
    est = ab_estimate(con, settings, idea_id, slot)
    if est["key"] != key:
        raise ProductionError("the variants changed; check the new total")
    rows = [dict(r, brief=est["briefs"].get(str(r["ab"]["value"]))) for r in est["rows"]]
    with _batch_lock:
        if _batch["running"]:
            raise ProductionError("Generate all is already running")
        if job_state()["running"]:
            raise ProductionError("a slot is being made; wait for it to finish")
        _batch.update(running=True, idea_id=idea_id, rows=rows, spent=0.0, cap=est["total_upper"],
                      total=est["total_upper"], cancel=False, started=datetime.now().isoformat(timespec="seconds"),
                      finished=None, stop_reason="", kind="ab")
    spawn(run_abtest, con, settings, idea_id, slot, est["total_upper"], generator)
    return batch_state(idea_id)


def run_abtest(con, settings, idea_id, slot, total, generator=None):
    """The batch runner with place=False; results saved on set_plan.abtest[slot].results (nothing approved, nothing
    placed in a slot)."""
    run_batch(con, settings, idea_id, total, generator, total, place=False)
    with _batch_lock:
        rows = [dict(r, brief=None) for r in _batch["rows"]]
    res = {str(r["ab"]["value"]): {k: r.get(k) for k in ("status", "why", "file", "template", "spent")} for r in rows
           if r.get("ab")}

    def fn(sp):
        ab = (sp.get("abtest") or {}).get(str(slot))
        if ab is not None:
            ab.setdefault("results", {}).update(res)
            ab["status"] = "generated"
    splan._save(con, idea_id, fn)


def ab_place(con, settings, idea_id, slot, value):
    """"Put in slot N" (free): the variant's render is copied into the slot as a pending image (the slot's current
    image goes to Archive as usual). Never approves."""
    idea, lst, rec, folder, arts = _ctx(con, settings, idea_id)
    ab = ((splan.get_plan(rec) or {}).get("abtest") or {}).get(str(slot)) or {}
    r = (ab.get("results") or {}).get(str(value)) or {}
    src = folder / ARCHIVE / str(r.get("file") or "")
    if not r.get("file") or not src.is_file():
        raise ProductionError("that variant has no image yet")
    b = (ab.get("variants") or {}).get(str(value)) or {}
    room, decor = b.get("room") or "Living room", b.get("decor") or "Modern"
    with LOCK:
        rec = prints._record(con, lst["id"])
        prod = _prod(rec)
        old = prod["slots"].get(str(slot)) or {}
        old_name, _, old_where = _current_image(folder, int(slot), old, rec)
        if old_name and old_where == "folder":
            _to_archive(folder, old_name, rec, "replaced")
        name = _unique_name(folder, int(slot), room, decor)
        shutil.copy2(src, folder / name)
        (rec.setdefault("mockup_approvals", {})).pop(name, None)
        prod["slots"][str(slot)] = {"room": room, "decor": decor, "ratio": b.get("ratio"), "source": "new",
                                    "template": r.get("template"), "new_template": r.get("template"), "file": name,
                                    "state": "done", "message": f"A/B variant at closeness {value}",
                                    "made": datetime.now().isoformat(timespec="seconds"), "engine_id": ab.get("engine"),
                                    "ab": {"value": int(value)},
                                    "history": (old.get("history") or []) + ([old["file"]] if old.get("file") else [])}
        prints._save_record(con, lst["id"], rec)
    return name


def ab_grade(con, settings, idea_id, slot, value, grade_value):
    """Tony's grade of one A/B variant: on the variant (set_plan.abtest) and in its template's Grades.json."""
    if grade_value not in (None, "") and grade_value not in GRADES:
        raise ProductionError(f"grade must be one of {', '.join(GRADES)}")
    with LOCK:
        lst = prints.listing_for(con, idea_id)
        rec = prints._record(con, lst["id"])
    ab = ((splan.get_plan(rec) or {}).get("abtest") or {}).get(str(slot)) or {}
    tpl = ((ab.get("results") or {}).get(str(value)) or {}).get("template")

    def fn(sp):
        r = ((sp.get("abtest") or {}).get(str(slot)) or {}).setdefault("results", {}).setdefault(str(value), {})
        r["grade"] = grade_value or None
    splan._save(con, idea_id, fn)
    if tpl:
        psd = stp.library(settings) / tpl
        if psd.is_file():
            if grade_value:
                stp.add_grade(psd, {"idea_id": idea_id, "design": lst["title"], "slot": int(slot), "grade": grade_value,
                                    "note": f"A/B closeness {value}", "at": datetime.now().isoformat(timespec="seconds")})
            else:
                stp.remove_grade(psd, idea_id, int(slot))
