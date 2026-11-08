"""Production tab (stage 4): the new listing images for each design, inline, with approve / deny.

Only the images made for this design are shown (slots 1, 2, 7 and the room mockups 8-19). The fixed images that
are the same in every listing (3, 4, 5, 6, 20) are not shown. Decisions live in the listing record
(`mockup_approvals`: file -> approved | denied); a file that is made again goes back to waiting."""
from pathlib import Path

from . import mockups, prints
from .db import DB_LOCK as LOCK

FIXED_NAMES = {n for n, _ in mockups.FIXED}
TEMPLATED_SLOTS = {int(stem[:2]) for stem, _ in mockups.GENERATED}     # 1, 2, 7: art in a PSD, not reviewed here
DECISIONS = ("approved", "denied", "pending")
LABELS = {1: "Main", 2: "Poster", 7: "Detail"}


def _label(name):
    stem = Path(name).stem
    slot = int(stem[:2])
    return LABELS.get(slot) or stem[3:].replace("_", " ")


def _images_dir(settings, lst):
    return prints.design_dir(settings, lst["folder_seq"], lst["title"]) / "03-Etsy Images"


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
    files = sorted(p for p in folder.glob("*.jpg")                      # JPG only; templated slots stay out of sight
                   if p.name not in FIXED_NAMES and p.name[:2].isdigit()
                   and int(p.name[:2]) not in TEMPLATED_SLOTS) if folder.is_dir() else []
    made = {f["file"]: f for f in (rec.get("mockups") or {}).get("files", [])}
    if any(f.get("slot", 0) >= 8 and f.get("room") for f in made.values()):
        # once the room-template step has made rooms, older room files it did not make (e.g. the rejected v1
        # AI rooms) are hidden, never deleted
        files = [p for p in files if int(p.name[:2]) < 8 or int(p.name[:2]) > 19 or p.name in made]
    for p in files:
        mb = round(p.stat().st_size / 1e6, 1)
        status = approvals.get(p.name, "pending")
        info = made.get(p.name, {})
        out["images"].append({"file": p.name, "slot": int(p.name[:2]), "label": _label(p.name), "mb": mb,
                              "status": status, "print": info.get("print"),
                              "look": ({k: info.get(k) for k in ("room", "light", "frame", "mat", "paint")}
                                       if info.get("room") else None),
                              "url": f"{prefix}/api/production/{idea_id}/file/{p.name}",
                              "over_limit": mb > 19.5})
        out["counts"][status] += 1
    return out


def overview(con, settings, prefix="/ikigai"):
    with LOCK:
        ids = [r[0] for r in con.execute("SELECT id FROM ideas WHERE art_state='approved' ORDER BY decided_at DESC, id DESC")]
    return [design(con, settings, i, prefix) for i in ids]


def image_path(con, settings, idea_id, name):
    """Safe path of one listing image, or None."""
    with LOCK:
        lst = prints.listing_for(con, idea_id)
    if not lst or not lst["folder_seq"] or Path(name).name != name or Path(name).suffix.lower() not in (".jpg", ".png"):
        return None
    p = _images_dir(settings, lst) / name
    return p if p.is_file() else None


def decide(con, settings, idea_id, name, decision):
    if decision not in DECISIONS:
        raise ValueError("decision must be approved, denied or pending")
    if (image_path(con, settings, idea_id, name) is None or name in FIXED_NAMES or not name.lower().endswith(".jpg")
            or int(name[:2]) in TEMPLATED_SLOTS):
        raise KeyError(name)
    with LOCK:
        lst = prints.listing_for(con, idea_id)
        rec = prints._record(con, lst["id"])
        ap = rec.setdefault("mockup_approvals", {})
        if decision == "pending":
            ap.pop(name, None)
        else:
            ap[name] = decision
        prints._save_record(con, lst["id"], rec)


# ---------- the one "Run mockups" button (Art tab) ----------

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
