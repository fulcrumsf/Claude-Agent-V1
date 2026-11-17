"""Templates tab: "Build this" on a gap tile, and proposed room folders (Tony 2026-11-10, build plan section 4 and
Decisions).

Build this (one click = Tony's approval of the cost, about 18 kie.ai credits on Nano Banana Pro):
  the gap folder (an EMPTY folder in Tony's NNN_ tree) gets a NEW AI room template, made with the Production recipe
  (room_slots.scene_prompt -> kie_edit.generate -> scene_templates.build_psd: blank-insert frame, cover-fit art,
  black-fill shadows measured from the photo). The files go straight INTO that folder (no new folder):
      AI_<Room>_<Decor>_<stamp>_Template.psd, AI_..._Scene.png, template.json (approved: false)
  The template checker runs on it at once; the tile then shows it with PASS/FAIL and Approve / Deny.
  Deny moves the three files into that folder's Archive/ (the folder becomes a gap again). Nothing is deleted.
Missing room folders (Entryway, Laundry): the tab shows the LITERAL proposed path per ratio and creates a folder only
when Tony clicks Approve on that exact path. No other folder is ever created here.
"""
import json
import re
import shutil
import tempfile
import threading
from datetime import datetime
from pathlib import Path

from . import room_slots as rs
from . import scene_templates as stp
from . import template_checker as tc
from . import template_gallery as tg

FOLDER_ROOM = {v: k for k, v in rs.ROOM_FOLDER.items() if v and k not in ("Dorm", "Kids")}   # bedroom -> Bedroom ...
FOLDER_ROOM["kids_nursery"] = "Nursery"
_job = {"running": False, "rel": None, "stage": "", "error": "", "made": None}
_lock = threading.Lock()


class BuildError(Exception):
    pass


def lib(settings=None):
    return stp.library(settings)


def gap_plan(g, settings=None):
    """What a gap tile would build: room (Etsy/scene room), decor, ratio, prompt, credits, target folder."""
    parts = g["rel"].split("/")
    room_key = rs.norm(parts[1]) if len(parts) > 1 else None
    room = FOLDER_ROOM.get(room_key) or (tg.label(parts[1]) if len(parts) > 1 else "Living room")
    decor = re.sub(r"\s+", "_", tg.label(parts[-1])) if len(parts) > 2 else "Modern"
    eng = (settings or {}).get("room_scene_engine", stp.DEFAULTS["room_scene_engine"])
    return {"rel": g["rel"], "room": room, "decor": decor, "ratio": g["ratio"],
            "prompt": rs.scene_prompt(room, decor, g["ratio"]) if g["ratio"] in rs.RATIO_VALUE else None,
            "credits": stp.SCENE_CREDITS.get(eng), "engine": eng,
            "path": f"Room_Templates/{stp.LIBRARY}/{g['rel']}/"}


def proposals(settings=None):
    """Room folders Tony may approve: {room, path (literal, under Room_Templates), rel} for each ratio folder that
    lacks it. Nothing is created here."""
    base = lib(settings)
    out = []
    for room, name in rs.PROPOSED_ROOM_FOLDERS.items():
        for rd in stp._kids(base):
            if not stp.MASTER.match(rd.name) or tg.ratio_of(rd.name) in (None, "other"):
                continue
            if any(rs.norm(c.name) == rs.norm(name) for c in stp._kids(rd)):
                continue
            rel = f"{rd.name}/{name}"
            out.append({"room": room, "ratio": tg.ratio_of(rd.name), "rel": rel,
                        "path": f"Room_Templates/{stp.LIBRARY}/{rel}/"})
    return out


def approve_folder(rel, settings=None):
    """Tony approved this exact proposed path: create it (only a listed proposal can be created)."""
    hit = next((p for p in proposals(settings) if p["rel"] == rel), None)
    if hit is None:
        raise BuildError("that folder is not a proposed path (only the listed paths can be approved)")
    d = lib(settings) / rel
    d.mkdir()                                   # parent ratio folder exists; never parents=True
    return {"created": hit["path"]}


def job():
    with _lock:
        return dict(_job)


def start(rel, settings=None):
    gaps = {g["rel"]: g for g in tg.scan(settings)[1]}
    if rel not in gaps:
        raise BuildError("that folder is not an empty template folder any more")
    plan = gap_plan(gaps[rel], settings)
    if not plan["prompt"]:
        raise BuildError("no print ratio for this folder")
    with _lock:
        if _job["running"]:
            raise BuildError(f"still building {_job['rel']}; one at a time")
        _job.update(running=True, rel=rel, stage="starting", error="", made=None)
    return plan


def _stage(t):
    with _lock:
        _job["stage"] = t


def run(rel, settings=None, generator=None, check=True):
    """Worker: draw the room, build the PSD, save it INTO the gap folder, run the checker. Releases the job."""
    try:
        gaps = {g["rel"]: g for g in tg.scan(settings)[1]}
        plan = gap_plan(gaps[rel], settings)
        folder = lib(settings) / rel
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            scene = td / "scene.png"
            _stage("drawing the room (kie.ai)")
            gen = stp.generate_scene(plan["prompt"], scene, settings, generator)
            _stage("finding the frame, building the PSD")
            (td / "b").mkdir()
            try:
                built = stp.build_psd(scene, plan["ratio"], td / "b", settings,
                                      presentation=rs.presentation_for(plan["room"], plan["decor"], plan["ratio"]))
            except stp.TemplateError as e:
                arch = folder / "Archive"
                arch.mkdir(exist_ok=True)               # Archive folders are pre-approved (Tony 2026-11-08)
                keep = arch / f"Rejected_Scene_{datetime.now():%Y%m%d_%H%M%S}.png"
                shutil.copy2(scene, keep)
                raise BuildError(f"{e} (scene kept in Archive as {keep.name}; {gen.get('credits')} credits spent)")
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            short = stp.ROOM_SHORT.get(plan["room"], plan["room"].title().replace(" ", "_"))
            name = f"AI_{short}_{plan['decor']}_{stamp}"
            psd = folder / f"{name}_Template.psd"
            shutil.copy2(built["psd_tmp"], psd)
            shutil.copy2(scene, folder / f"{name}_Scene.png")
            man = {"name": name, "kind": "ai_scene", "psd": psd.name, "scene": f"{name}_Scene.png",
                   "smart_object_layer": stp.ART, "room": plan["room"],
                   "etsy_room": plan["room"] if plan["room"] in rs.ETSY_ROOMS else None,
                   "decor": plan["decor"], "ratio": plan["ratio"],
                   **{k: built[k] for k in ("so_px", "so_ratio", "quad_insert", "quad_art", "mode", "canvas",
                                            "light_from", "insert", "shadows")},
                   **{k: built[k] for k in ("quad_paper", "opening_pad_px") if k in built},
                   "card_test": built.get("card_test"),
                   "layers_verified": "black-fill shadows built by scene_templates.make_layers (measured, masked)",
                   "base_layer": stp.BASE_NAME, "prompt": plan["prompt"], "engine": plan["engine"],
                   "model": gen.get("model"), "credits": gen.get("credits"), "built_for": "gap (Templates tab)",
                   "approved": False, "created": datetime.now().isoformat(timespec="seconds")}
            (folder / stp.MANIFEST).write_text(json.dumps(man, indent=1) + "\n")
        rel_psd = psd.relative_to(lib(settings)).as_posix()
        if check:
            _stage("checking the template")
            tc.run_all(settings, [rel_psd], (settings or {}).get("template_checks_path"), log=lambda *_: None)
        with _lock:
            _job["made"] = rel_psd
    except Exception as e:  # noqa: BLE001  (shown on the tile; the job is always released)
        with _lock:
            _job["error"] = str(e)[:400]
    finally:
        with _lock:
            _job.update(running=False, stage="")


def _free(dest):
    """dest, or dest with a time suffix when that name is already taken (never overwrite)."""
    if dest.exists():
        dest = dest.with_name(f"{dest.stem}_{datetime.now():%H%M%S}{dest.suffix}")
    return dest


def decide_rebuild(psd, side, decision, settings=None):
    """A REBUILT template (sidecar <stem>.json, kind rebuild; template_gallery.REBUILD_KIND) next to the live PSD.
    approved: the live PSD (+ its template.json and _Preview.png) moves into the folder's Archive/ as
    <old>_before_rebuild_<date>, the sidecar becomes the folder's template.json (approved true), and Tony's style
    choice moves to the new PSD. denied: the new PSD, its scene and sidecar move into Archive/; the live PSD stays.
    Nothing is deleted."""
    from . import template_styles as ts
    man = json.loads(side.read_text())
    if man.get("kind") != tg.REBUILD_KIND or man.get("psd") != psd.name:
        raise BuildError("only a rebuilt template can be approved or denied here")
    folder = psd.parent
    arch = folder / "Archive"
    arch.mkdir(exist_ok=True)                   # Archive folders are pre-approved (Tony 2026-11-08)
    day = f"{datetime.now():%Y-%m-%d}"
    rel_new = psd.relative_to(lib(settings)).as_posix()
    if decision == "denied":
        moved = []
        for f in (psd, folder / (man.get("scene") or ""), side):
            if f.is_file() and f != folder:
                dest = _free(arch / f.name)
                shutil.move(str(f), str(dest))
                moved.append(dest.name)
        return {"denied": rel_new, "archived": moved, "kept_in_use": man.get("replaces")}
    if decision != "approved":
        raise BuildError("decision must be approved or denied")
    old = folder / (man.get("replaces") or "")
    moved = []
    if old.is_file() and old != psd:
        for f, dest in ((old, arch / f"{old.stem}_before_rebuild_{day}.psd"),
                        (folder / f"{old.stem}_Preview.png", arch / f"{old.stem}_Preview_before_rebuild_{day}.png")):
            if f.is_file():
                dest = _free(dest)
                shutil.move(str(f), str(dest))
                moved.append(dest.name)
    tj = folder / stp.MANIFEST
    if tj.is_file():
        dest = _free(arch / f"{old.stem}_template_before_rebuild_{day}.json")
        shutil.move(str(tj), str(dest))
        moved.append(dest.name)
    man.update(approved=True, approved_at=datetime.now().isoformat(timespec="seconds"))
    tj.write_text(json.dumps(man, indent=1) + "\n")
    shutil.move(str(side), str(_free(arch / f"{psd.stem}_rebuild_manifest_{day}.json")))   # kept as the record
    if old.name:                                # Tony's manual styles follow the template to its new file
        rel_old = (folder / old.name).relative_to(lib(settings)).as_posix()
        sp = (settings or {}).get("template_styles_path") or ts.FILE
        if Path(sp).is_file():
            data = ts.load(sp)
            if rel_old in (data.get("manual") or {}) and rel_new not in data["manual"]:
                ts.set_manual(rel_new, data["manual"][rel_old], sp)
    return {"approved": rel_new, "archived": moved}


def archive_template(rel_psd, settings=None):
    """Retire one template (the card's "..." menu, Tony 2026-11-16): its PSD, _Preview.png, rebuild sidecar and scene
    PNG move into the folder's Archive/ (pre-approved, never used by Production or the checker). The folder's
    template.json goes too when it names this PSD or this is the only PSD there. Nothing is deleted."""
    psd = lib(settings) / rel_psd
    if not psd.is_file() or psd.suffix.lower() != ".psd" or psd.parent.name == "Archive":
        raise BuildError("no such template")
    folder = psd.parent
    arch = folder / "Archive"
    arch.mkdir(exist_ok=True)
    others = [f for f in folder.glob("*.psd") if f != psd]
    moved = []
    cand = [psd, folder / f"{psd.stem}_Preview.png", folder / f"{psd.stem}_Scene.png", psd.with_suffix(".json")]
    tj = folder / stp.MANIFEST
    if tj.is_file():
        try:
            names = json.loads(tj.read_text()).get("psd")
        except ValueError:
            names = None
        if names == psd.name or (not others and names in (None, psd.name)):
            cand.append(tj)
    for f in cand:
        if f.is_file():
            nm = f.name if f != tj else f"{psd.stem}_template.json"
            dest = _free(arch / nm)
            shutil.move(str(f), str(dest))
            moved.append(dest.name)
    return {"archived": rel_psd, "files": moved}


def decide(rel_psd, decision, settings=None):
    """approved: template.json approved true. denied: the PSD, scene and template.json move into that folder's
    Archive/ (the folder becomes a gap again). A rebuilt template (sidecar manifest) goes to decide_rebuild."""
    psd = lib(settings) / rel_psd
    side = psd.with_suffix(".json")
    if psd.is_file() and side.is_file() and (tg.psd_manifest(psd) or {}).get("kind") == tg.REBUILD_KIND:
        return decide_rebuild(psd, side, decision, settings)
    man_f = psd.parent / stp.MANIFEST
    if not psd.is_file() or not man_f.is_file():
        raise BuildError("no such new template")
    man = json.loads(man_f.read_text())
    if man.get("kind") != "ai_scene" or man.get("psd") != psd.name:
        raise BuildError("only a newly built template can be approved or denied here")
    if decision == "approved":
        man["approved"] = True
        man["approved_at"] = datetime.now().isoformat(timespec="seconds")
        man_f.write_text(json.dumps(man, indent=1) + "\n")
        return {"approved": rel_psd}
    if decision != "denied":
        raise BuildError("decision must be approved or denied")
    arch = psd.parent / "Archive"
    arch.mkdir(exist_ok=True)
    moved = []
    for f in (psd, psd.parent / man.get("scene", ""), man_f):
        if f.is_file():
            dest = arch / (f.name if f.name != stp.MANIFEST else f"{man['name']}_template.json")
            if dest.exists():
                dest = arch / f"{dest.stem}_{datetime.now():%H%M%S}{dest.suffix}"
            shutil.move(str(f), str(dest))
            moved.append(dest.name)
    return {"denied": rel_psd, "archived": moved}
