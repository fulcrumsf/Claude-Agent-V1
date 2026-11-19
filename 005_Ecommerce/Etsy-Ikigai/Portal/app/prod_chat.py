"""Production in the Studio chat (Tony 2026-11-19): when a Production room image has a problem he fixes it from the
chat, never by opening a separate Claude.

  - Context: the page sends the design open in the Production tab (prodSel) and the slot he pointed at ("Ask chat"
    on a card). `snapshot_lines` gives the model one line per slot: file, where it is, approval, template, accuracy
    guard + art-area gate reasons, template checker status, archive history, a waiting fix request.
  - Vision: `slot_images` returns the slot pictures (open slot + slots named in his message, max 2, long side max
    1568 px) that app/assistant.py attaches to the `claude -p` call as base64 image blocks.
  - Actions (validated here against the real listing record; unknown designs/slots are refused):
      slot_rerender {idea_id, slot}         render again with the slot's CURRENT template (free, no credits)
      slot_decide {idea_id, slot, decision} approved | denied | pending (undo), through production.decide
      check_template {idea_id, slot}        run the one-template checker on the slot's template, report in chat
      fix_request {idea_id, slot, summary?} write Handoffs/YYYY-MM-DD_Fix-Request_Portal_Slot-NN.md for Claude Code
      offer_regenerate {idea_id, slot}      a paid regenerate NEVER runs from chat: the reply gets a button, and only
                                            Tony's click on it spends credits
Fix requests are plain Markdown in the existing Handoffs folder (every Claude session reads it first). `status:
waiting` shows as a "Waiting for Claude Code" row in Production; Claude Code sets `status: done` when fixed."""
import base64
import io
import re
from datetime import datetime
from pathlib import Path

from . import prints
from . import production as prod
from . import scene_templates as stp
from .db import DB_LOCK as LOCK

MAX_IMAGES = 2
MAX_SIDE = 1568
ACTIONS = ("slot_rerender", "slot_decide", "check_template", "fix_request", "offer_regenerate")
FIX_GLOB = "*_Fix-Request_Portal_*.md"
SLOT_WORDS = re.compile(r"\bslots?\s*#?\s*(\d{1,2}(?:\s*(?:,|and|&|\+)\s*#?\d{1,2})*)", re.I)


def _line(text, n=200):
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def handoffs_dir(settings=None):
    """The existing Agent-OS Handoffs folder (never created here)."""
    p = (settings or {}).get("handoffs_dir")
    return Path(p) if p else Path(__file__).resolve().parents[4] / "001_Architecture" / "Logs" / "Handoffs"


def named_slots(text):
    """Slot numbers Tony names in plain words: "slot 11", "slots 11 and 12", "slot #3"."""
    out = []
    for m in SLOT_WORDS.finditer(text or ""):
        for n in re.findall(r"\d{1,2}", m.group(1)):
            if int(n) not in out:
                out.append(int(n))
    return out


# ---------- facts per slot (the real listing record) ----------

def design_facts(con, settings, idea_id):
    """{name, title, folder, slots: {slot: facts}} for a design with a listing folder, else None."""
    idea_id = _int(idea_id)
    if idea_id is None:
        return None
    with LOCK:
        idea = con.execute("SELECT id, title FROM ideas WHERE id=?", (idea_id,)).fetchone()
        lst = prints.listing_for(con, idea_id)
        if not idea or not lst or not lst["folder_seq"]:
            return None
        rec = prints._record(con, lst["id"])
    folder = prod._images_dir(settings, lst)
    p = prod._prod(rec)
    approvals = rec.get("mockup_approvals") or {}
    nums = {int(k) for k in p["slots"] if str(k).isdigit()}
    if folder.is_dir():
        nums |= {int(f.name[:2]) for f in folder.glob("*.jpg") if prod._is_slot_image(f.name)}
    from . import template_checker as tc
    checks = tc.load((settings or {}).get("template_checks_path"))
    waiting = {r["slot"]: r for r in fix_requests(settings, idea_id)}
    slots = {}
    for slot in sorted(n for n in nums if n in prod.ROOM_SLOTS):
        srec = p["slots"].get(str(slot)) or {}
        name, path, where = prod._current_image(folder, slot, srec, rec)
        mine = bool(name and srec.get("file") == name)
        g = (srec.get("guard") or {}) if mine else {}
        ag = g.get("art_area") or {}
        rel = srec.get("template") if mine or not name else None
        chk = None
        if rel:
            psd = stp.library(settings) / rel
            r = tc.status_for(rel, checks, psd if psd.is_file() else None)
            chk = ({"status": "unchecked"} if r is None else
                   {"status": "stale (PSD changed since its check)" if r.get("stale") else r.get("status"),
                    "reasons": r.get("reasons") or []})
        slots[slot] = {
            "slot": slot, "file": name, "path": path, "where": where,
            "status": approvals.get(name, "pending") if name else None,
            "room": srec.get("room"), "decor": srec.get("decor"), "ratio": srec.get("ratio"),
            "template": rel, "source": srec.get("source") if mine else None, "print": srec.get("print") if mine else None,
            "guard": ({"pass": g.get("pass"), "why": [w for w in g.get("why") or [] if w not in (ag.get("why") or [])]}
                      if g else None),
            "gate": {"pass": ag.get("pass"), "why": ag.get("why") or []} if ag else None,
            "checker": chk, "state": srec.get("state"), "message": srec.get("message") or "",
            "history": list(srec.get("history") or []), "rebuilt": srec.get("rebuilt") if mine else None,
            "made": srec.get("made"), "credits": srec.get("credits"), "fix_request": waiting.get(slot),
        }
    return {"idea_id": idea_id, "name": lst["title"], "title": idea["title"], "folder": folder, "slots": slots}


def _pf(d, label):
    if not d:
        return f"{label}: not run"
    if d.get("pass"):
        return f"{label}: pass"
    return f"{label}: FAIL ({_line('; '.join(d.get('why') or []), 220) or 'no reason saved'})"


def slot_line(f):
    bits = [f"slot {f['slot']:02d}"]
    if f["room"]:
        bits.append(f"{f['room']} · {f['decor'] or '-'} · {f['ratio'] or '-'}")
    if f["file"]:
        where = {"folder": "in the listing folder", "archive": "in Archive", "flagged": "in Archive, flagged"}.get(
            f["where"], f["where"])
        bits.append(f"image {f['file']} ({where}, {f['status']})")
    else:
        bits.append("no image yet")
    if f["template"]:
        bits.append(f"template {f['template']} (source {f['source'] or '-'})")
    if f["file"]:
        bits += [_pf(f["guard"], "accuracy guard"), _pf(f["gate"], "art-area gate")]
    if f["checker"]:
        c = f["checker"]
        bits.append(f"checker {c['status']}" + (f" ({_line('; '.join(c.get('reasons') or []), 200)})"
                                               if c.get("reasons") and c["status"] != "PASS" else ""))
    if f["rebuilt"]:
        bits.append(f"rebuilt from saved scene: {_line(f['rebuilt'], 160)}")
    if f["state"] == "failed" and f["message"]:
        bits.append(f"last run failed: {_line(f['message'], 160)}")
    if f["history"]:
        bits.append("older images: " + ", ".join(f["history"][-4:]))
    if f["fix_request"]:
        bits.append(f"WAITING FOR CLAUDE CODE ({f['fix_request']['file']})")
    return "- " + " | ".join(bits)


def snapshot_lines(con, settings, idea_id, open_slot=None, attached=()):
    """Lines for the chat's <dashboard> snapshot about the design open in the Production tab."""
    d = design_facts(con, settings, idea_id) if idea_id else None
    if not d:
        return []
    out = ["", f"Production tab: design #{d['idea_id']} “{d['name']}” ({_line(d['title'], 90)}), "
               f"folder Designs/{d['folder'].parent.name}/03-Etsy Images. Room image slots:"]
    out += [slot_line(f) for f in d["slots"].values()] or ["- (no room images yet)"]
    job = prod.job_state()
    if job["running"]:
        out.append(f"A Production job is running now: slot {job['slot']} of design #{job['idea_id']} ({job['stage']}).")
    if open_slot:
        out.append(f"Tony pointed at slot {int(open_slot):02d} (\"Ask chat\" on its card): “this one”, “it” = that slot.")
    for k, (slot, name) in enumerate(attached, 1):
        out.append(f"Attached image {k} = slot {slot:02d}, {name} (resized to at most {MAX_SIDE} px).")
    return out


# ---------- vision ----------

def encode_image(path, max_side=MAX_SIDE):
    from PIL import Image
    with Image.open(path) as im:
        im = im.convert("RGB")
        im.thumbnail((max_side, max_side))
        b = io.BytesIO()
        im.save(b, "JPEG", quality=85)
    return {"media_type": "image/jpeg", "data": base64.b64encode(b.getvalue()).decode()}


def slot_images(con, settings, idea_id, text, open_slot=None):
    """(images, attached) for the slots Tony points at or names, max 2: images = [{media_type, data}],
    attached = [(slot, file)]."""
    want = ([int(open_slot)] if _int(open_slot) else []) + named_slots(text)
    if not want or not idea_id:
        return [], []
    d = design_facts(con, settings, idea_id)
    if not d:
        return [], []
    imgs, att = [], []
    for s in want:
        f = d["slots"].get(s)
        if not f or not f["path"] or (s, f["file"]) in att:
            continue
        try:
            imgs.append(encode_image(f["path"]))
        except Exception:  # noqa: BLE001  (an unreadable image is just not attached)
            continue
        att.append((s, f["file"]))
        if len(imgs) >= MAX_IMAGES:
            break
    return imgs, att


# ---------- fix requests (Handoffs) ----------

def _front(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    out = {}
    for ln in (m.group(1).splitlines() if m else []):
        if ":" in ln:
            k, v = ln.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def fix_requests(settings=None, idea_id=None, status="waiting"):
    """Fix requests in the Handoffs folder with that status (newest first), optionally for one design."""
    d = handoffs_dir(settings)
    out = []
    for f in sorted(d.glob(FIX_GLOB), reverse=True) if d.is_dir() else []:
        try:
            fm = _front(f.read_text()[:2000])
        except OSError:
            continue
        if status and fm.get("status") != status:
            continue
        if idea_id is not None and _int(fm.get("idea_id")) != int(idea_id):
            continue
        out.append({"file": f.name, "slot": _int(fm.get("slot")), "idea_id": _int(fm.get("idea_id")),
                    "design": fm.get("design"), "created": fm.get("created"), "status": fm.get("status"),
                    "words": fm.get("tony_words", "")})
    return out


def write_fix_request(settings, facts, slot, tony_words, summary="", now=None):
    """Writes the hand-off for Claude Code; returns its path. Never overwrites (a taken name gets _2, _3...)."""
    d = handoffs_dir(settings)
    if not d.is_dir():
        raise prod.ProductionError(f"the Handoffs folder is missing ({d}); nothing written")
    now = now or datetime.now()
    f = facts["slots"][slot]
    base = f"{now:%Y-%m-%d}_Fix-Request_Portal_Slot-{slot:02d}"
    p, k = d / f"{base}.md", 2
    while p.exists():
        p, k = d / f"{base}_{k}.md", k + 1
    lib = stp.library(settings)
    q = '"' + " ".join(str(tony_words).split()).replace('"', "'") + '"'
    lines = [
        "---", f"title: Fix request from the Portal, slot {slot:02d} of {facts['name']}", "type: fix-request",
        "status: waiting", f"created: {now:%Y-%m-%d %H:%M}", f"idea_id: {facts['idea_id']}", f"design: {facts['name']}",
        f"slot: {slot}", f"template: {f['template'] or ''}", f"tony_words: {q}", "---", "",
        f"# Fix request: slot {slot:02d} of {facts['name']} (Portal Production tab)", "",
        "Tony asked for this from the Studio chat in the Ikigai Portal. Do not ask him to explain again: everything he "
        "said and everything the Portal knows is below. When it is fixed, change `status: waiting` to `status: done` "
        "in the front matter (the Portal then drops its \"Waiting for Claude Code\" row) and tell Tony in one plain "
        "sentence what changed.", "",
        "## Tony's exact words", "", f"> {tony_words}", "",
    ]
    if summary:
        lines += ["## What the chat understood", "", summary, ""]
    lines += [
        "## The slot", "",
        f"- Design: #{facts['idea_id']} {facts['name']} ({facts['title']})",
        f"- Slot: {slot:02d} · {f['room'] or '-'} · {f['decor'] or '-'} · {f['ratio'] or '-'}",
        f"- Image: `{f['path']}`" if f["path"] else "- Image: none yet",
        f"- Where / approval: {f['where'] or '-'} / {f['status'] or '-'}",
        f"- Template (rel under Portrait_Templates): `{f['template'] or '-'}`"
        + (f" (PSD `{lib / f['template']}`)" if f["template"] else ""),
        f"- Source: {f['source'] or '-'} · print: {f['print'] or '-'} · made: {f['made'] or '-'}"
        + (f" · credits: {f['credits']}" if f["credits"] else ""), "",
        "## What the Portal measured", "",
        f"- {_pf(f['guard'], 'Accuracy guard')}", f"- {_pf(f['gate'], 'Art-area gate')}",
    ]
    c = f["checker"]
    lines.append(f"- Template checker: {c['status']}" + ("".join(f"\n  - {r}" for r in c.get("reasons") or []))
                 if c else "- Template checker: no template")
    if f["rebuilt"]:
        lines.append(f"- Rebuilt from its saved scene: `{f['rebuilt']}`")
    if f["state"] == "failed" and f["message"]:
        lines.append(f"- Last run failed: {f['message']}")
    lines.append("- Older images of this slot (in 03-Etsy Images/Archive): " + (", ".join(f["history"]) or "none"))
    lines += ["", "## Where to look", "",
              "- Code: `005_Ecommerce/Etsy-Ikigai/Portal/app/production.py` (run_slot), `scene_templates.py`, "
              "`room_templates.py` (guard, art-area gate), `template_checker.py`.",
              "- Read the Wall-Art-Shadows skill lessons first for shadow problems; never delete files (Archive / "
              "~/Desktop/Delete), never spend credits without Tony's click.", ""]
    p.write_text("\n".join(lines))
    return p


# ---------- actions ----------

class ProdHooks:
    """What the chat may do in Production. Jobs (render, checker) are queued and started by flush() after the chat
    released the DB lock. `notify(text)` posts a later chat line (checker result)."""

    def __init__(self, con, settings, spawn, generator=None, notify=None, prefix="/ikigai"):
        self.con, self.settings, self.spawn, self.generator = con, settings, spawn, generator
        self.notify, self.prefix, self.queued, self.buttons = notify, prefix, [], []

    def _slot(self, a, default_idea):
        iid = _int(a.get("idea_id")) or _int(default_idea)
        slot = _int(a.get("slot"))
        if iid is None:
            raise prod.ProductionError("no design is open in the Production tab")
        facts = design_facts(self.con, self.settings, iid)
        if facts is None:
            raise prod.ProductionError(f"design #{iid} has no Production images")
        if slot is None or slot not in facts["slots"]:
            have = ", ".join(f"{s:02d}" for s in facts["slots"]) or "none"
            raise prod.ProductionError(f"{facts['name']} has no slot {a.get('slot')} (slots with images: {have})")
        return iid, slot, facts

    def run(self, kind, a, user_text, default_idea):
        iid, slot, facts = self._slot(a, default_idea)
        f = facts["slots"][slot]
        if kind == "slot_decide":
            dec = str(a.get("decision") or "").strip().lower()
            dec = {"approve": "approved", "deny": "denied", "undo": "pending"}.get(dec, dec)
            if dec not in prod.DECISIONS:
                raise prod.ProductionError("decision must be approve, deny or undo")
            if not f["file"]:
                raise prod.ProductionError(f"slot {slot:02d} has no image to decide on")
            try:
                prod.decide(self.con, self.settings, iid, f["file"], dec)
            except KeyError:
                raise prod.ProductionError(f"slot {slot:02d}'s image {f['file']} was not found")
            return {"approved": f"Approved slot {slot:02d} ({f['file']}).",
                    "denied": f"Denied slot {slot:02d}; {f['file']} moved to Archive (Undo brings it back).",
                    "pending": f"Undid the decision on slot {slot:02d} ({f['file']})."}[dec]
        if kind == "slot_rerender":
            rel = f["template"]
            if not rel:
                raise prod.ProductionError(f"slot {slot:02d} has no template to render again; use its card")
            if rel not in {t["rel"] for t in stp.library_templates(self.settings)}:
                raise prod.ProductionError(f"slot {slot:02d}'s template {rel} is not in the library any more "
                                           "(archived or waiting for approval)")
            prod.start_slot(self.con, self.settings, iid, slot, rel)       # one job at a time; raises if busy
            self.queued.append(("render", iid, slot, rel))
            return (f"Rendering slot {slot:02d} again with its current template (free, no credits); the new image "
                    "shows on its card in about a minute and the old one goes to Archive.")
        if kind == "check_template":
            rel = f["template"]
            if not rel:
                raise prod.ProductionError(f"slot {slot:02d} has no template to check")
            from . import template_checker as tc
            if tc.job()["running"]:
                raise prod.ProductionError("the template checker is already running; ask again when it is done")
            self.queued.append(("check", iid, slot, rel))
            return (f"Checking template {rel.split('/')[-1]} now (free); I post the result here when it is done, "
                    "usually within a few minutes.")
        if kind == "fix_request":
            p = write_fix_request(self.settings, facts, slot, user_text, _line(a.get("summary"), 600))
            return (f"Sent to Claude Code: slot {slot:02d}'s problem, your words, the image, template and check "
                    f"results are in Handoffs/{p.name}; the next Claude Code session reads it first, and the slot "
                    "shows “Waiting for Claude Code” in Production until it is fixed.")
        if kind == "offer_regenerate":
            label, note = self._regen_label(iid, slot)
            self.buttons.append({"label": label, "url": f"{self.prefix}/api/production/{iid}/slots/{slot}/generate",
                                 "body": {}, "idea_id": iid, "slot": slot})
            return f"{note} I can't start that from chat; the button below does it when you click it."
        raise prod.ProductionError(f"unknown action {kind}")

    def _regen_label(self, iid, slot):
        try:
            pan = prod.panel(self.con, self.settings, iid, self.prefix)
            c = next((c for c in pan["slots"] if c["slot"] == slot), None)
            nx = (c or {}).get("next") or {}
        except Exception:  # noqa: BLE001
            nx = {}
        if nx.get("kind") == "library":
            return (f"Regenerate slot {slot:02d} ({nx['label']}, free)",
                    f"Regenerate for slot {slot:02d} uses {nx['label']} (free).")
        cr = nx.get("credits") or prod._engine(self.settings).get("credits_per_scene")
        cost = f"about {cr} kie.ai credits" if cr else "kie.ai credits"
        return (f"Regenerate slot {slot:02d} (new AI scene, {cost})",
                f"A new AI scene for slot {slot:02d} costs {cost}.")

    def flush(self):
        while self.queued:
            job = self.queued.pop(0)
            if job[0] == "render":
                _, iid, slot, rel = job
                self.spawn(prod.run_slot, self.con, self.settings, iid, slot, rel, self.generator)
            else:
                self.spawn(self._check, *job[1:])

    def _check(self, iid, slot, rel):
        from . import template_checker as tc
        try:
            data = tc.run_all(self.settings, [rel], (self.settings or {}).get("template_checks_path"),
                              log=lambda *_: None)
            r = (data.get("results") or {}).get(rel)
            if not r:
                msg = f"Template check for slot {slot:02d}: {rel} was not found by the checker."
            elif r.get("status") == "PASS":
                msg = f"Template check for slot {slot:02d} ({rel.split('/')[-1]}): PASS."
            else:
                msg = (f"Template check for slot {slot:02d} ({rel.split('/')[-1]}): {r.get('status')}: "
                       + _line("; ".join(r.get("reasons") or []), 600))
        except Exception as e:  # noqa: BLE001
            msg = f"Template check for slot {slot:02d} did not finish: {_line(e, 200)}"
        if self.notify:
            self.notify(msg)
