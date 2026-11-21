"""Ikigai Digital Studio module: stage 1 (ideation) of the funnel.

Self-contained so it can plug into a larger business dashboard later:

    from app import studio
    tab = studio.mount(app, con, settings, chat)      # adds routes under /ikigai, returns a Tab

The host page includes `tab.panel_template` (or fetches `GET /ikigai/panel`) inside its tab, and
routes chat text through `tab.chat_responder` (or `studio.responder`).

Routes (prefix /ikigai):
  GET  /panel                     HTML fragment for the tab
  GET  /api/state                 counts, visible list, bank
  POST /api/ideas/{id}/approve    -> bank (+ placeholder art prompt)
  POST /api/ideas/{id}/deny       -> leaves the list; chat invites a comment
  POST /api/refresh               add up to `refresh_batch` pending ideas (refresh now)
  POST /api/ideas/import          research batch import (cap enforced)
  POST /api/seed                  {text} Tony's seed
  GET  /api/taste                 taste profile JSON
  Art (stage 2, app/art.py):
  GET  /api/art/options           style cards, chip groups, engines (+ default), images per round
  GET  /api/art/balance           kie.ai credit balance (live)
  GET  /api/art/{idea_id}         rounds + images + art state (the panel polls this while a round runs)
  POST /api/art/{idea_id}/rounds  {cards[], chips{}, engine} -> starts a round of 4 (no cards = Surprise me)
  POST /api/art/{idea_id}/iterate {feedback, chips?} -> 4 new variations of the picked image
  POST /api/art/images/{id}/pick  Tony's pick (others in the round become "passed")
  POST /api/art/{idea_id}/approve {image_id?} -> art approved, idea shows "Art approved"
  GET  /api/art/{idea_id}/log     human-oversight record (prompts, engine, cards/chips, sources, picks, feedback)
  GET  /art-files/{idea}/{file}   generated images (from <db folder>/art/)
  Prints (stage 3, app/prints.py; the Art tab):
  GET  /api/prints                approved-art gallery with upscale/resize status per idea
  GET  /api/prints/{idea_id}      one idea's upscale/resize status, files, design folder
  POST /api/prints/{idea_id}/run  {name?, redo?} -> queue upscale + resize (name: first run only; redo: run again);
                                  with prints_make_listing_images it also makes listing images 1, 2, 8 + fixed
  Production (stage 4, app/production.py; room images 3, 9-19):
  GET  /api/production            upscaled designs (thumbnail row) + the generation job
  GET  /api/production/{id}/panel tags, slot plan and cards for one design
  POST /api/production/{id}/tags  {rooms[], styles[]} -> Tony's ticks, saved as tags on the design
  POST /api/production/{id}/slots/{slot}/generate {template?} -> one card (one job at a time)
  POST /api/production/{id}/images/{name} {decision} -> approved | denied (-> Archive) | pending (undo)
  POST /api/production/{id}/grade {name, grade, note?} -> Tony's grade of a slot image (A+ ... F, null clears)
  POST /api/production/{id}/plan {slots?, wider?} -> (re)plan the open slots' scenes (app/slot_planner.py, free;
                                  background, claude -p); wider = plan those slots one step wider
"""
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from fastapi.responses import FileResponse, JSONResponse

from . import art, assistant, ideas, prod_chat, production, prints, slot_planner, taste
from .channels import get_channel
from .chat import Reply
from .db import DB_LOCK, get_meta, set_meta

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
LOCK = DB_LOCK                 # shared with app/art.py workers
# Listing images are rewritten in place under the same file name (Run mockups again, template fixes). Without these
# headers the browser kept showing the old picture from its cache (Production tab bug, 2026-11-08).
NO_STORE = {"Cache-Control": "no-store"}
REVALIDATE = {"Cache-Control": "no-cache"}
DENY_COMMENT_WINDOW = timedelta(minutes=20)
HELP = ("Talk to me in plain words: ask about the ideas, approve or deny one, tell me what you like. "
        "To add your own idea say so, or type seed: <idea>. After a deny, your next message is saved as the reason. "
        "Quick commands: refresh · status · skip")


@dataclass
class Tab:
    id: str
    label: str
    prefix: str
    panel_template: str
    chat_responder: object
    context: object                      # callable -> dict for the panel template


# ---------- pending deny comment ----------

def _set_pending(con, idea_id):
    set_meta(con, "pending_deny", json.dumps({"id": idea_id, "at": ideas.now()}))


def _take_pending(con):
    raw = get_meta(con, "pending_deny")
    if not raw:
        return None
    set_meta(con, "pending_deny", "")
    p = json.loads(raw)
    at = datetime.strptime(p["at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return p["id"] if datetime.now(timezone.utc) - at <= DENY_COMMENT_WINDOW else None


# ---------- chat responder ----------
# Simple commands are answered locally. Everything else is a normal conversation through the Claude CLI
# (app/assistant.py). Plain text NEVER becomes a seed on its own: seeds come from `seed: ...` or from a
# model `seed` action that the Portal only accepts when Tony's message asks for one.

class ArtHooks:
    """What the chat may do with art (actions art_iterate / art_approve), wired to the same worker as the panel."""

    def __init__(self, con, settings, runner, on_approve=None):
        self.con, self.settings, self.runner, self.queued = con, settings, runner, []
        self.on_approve = on_approve

    def iterate(self, idea_id, feedback, chips, user_text):
        rid = art.start_round(self.con, self.settings, idea_id, feedback=user_text or feedback,
                              chip_changes=chips, summary=feedback)
        self.queued.append(rid)          # started by flush() once the chat has released LOCK
        return f"Making 4 new variations of your pick for #{idea_id}; they appear in the Details panel."

    def approve(self, idea_id, image_id=None):
        iid = art.approve(self.con, idea_id, image_id)
        extra = self.on_approve(idea_id) if self.on_approve else ""
        return f"Art approved for #{idea_id} (image #{iid}).{extra}"

    def flush(self):
        while self.queued:
            self.runner(self.queued.pop(0))


def make_responder(con, settings, ask=None, art_hooks=None, prod_hooks=None):
    ask = ask or assistant.call_claude

    def respond(text, chat):
        low = text.lower().strip()
        with LOCK:
            if low in ("refresh", "refresh now", "/refresh"):
                n = ideas.refresh(con, settings)
                return Reply(f"Added {n} ideas to the list." if n else
                             "No pending ideas. Run the research job to fill the pool.", refresh=True)
            if low in ("status", "/status"):
                s = ideas.state(con, settings)
                return Reply(f"On list {s['shown']} · pending {s['pool']} · bank {s['banked']} · "
                             f"room {s['room']} of {s['cap']}.")
            if low in ("help", "/help", "?"):
                return Reply(HELP)
            if low in ("skip", "/skip", "no", "no comment"):
                _take_pending(con)
                return Reply("OK, deny saved without a note.")
            for p in ("seed:", "/seed"):
                if low.startswith(p):
                    _take_pending(con)
                    i = ideas.add_seed(con, text[len(p):].strip(" :"))
                    return Reply("Seed added to the list, marked as yours.", refresh=True, idea_id=i)
            note, attached, title = None, None, None
            pending = _take_pending(con)
            if pending:
                ideas.comment(con, pending, text)
                attached = pending
                title = con.execute("SELECT title FROM ideas WHERE id=?", (pending,)).fetchone()[0]
                note = (f"Tony just denied idea #{pending} “{title}”. The Portal already saved his new message as "
                        "the deny reason. Acknowledge it briefly; do not deny it again or save it as a taste_note.")
            history = chat.history(cfg_history(settings) + 1)[:-1]      # last one is this message
            prod_id, open_slot = getattr(chat, "prod_idea_id", None), getattr(chat, "prod_slot", None)
            try:                         # vision: the slot pictures Tony points at or names (max 2, <=1568 px)
                images, seen = prod_chat.slot_images(con, settings, prod_id, text, open_slot)
            except Exception as e:  # noqa: BLE001
                print("chat slot images:", repr(e))
                images, seen = [], []
            prompt = assistant.build_prompt(con, settings, history, text, getattr(chat, "selected_idea_id", None), note,
                                            prod_id, open_slot, seen)
        if prod_hooks is not None:
            prod_hooks.buttons = []
        try:                                                             # seconds; never hold the lock here
            raw = ask(prompt, settings, images=images) if images else ask(prompt, settings)
        except assistant.ChatUnavailable as e:
            if attached:
                return Reply(f"Thanks, noted against “{title}”. ({e}, so no reply this time.)", idea_id=attached)
            return Reply(f"{e}. Your message is saved; try again in a moment.")

        reply_text, actions = assistant.parse_reply(raw)
        with LOCK:
            done, refused, changed, bare = assistant.run_actions(con, settings, actions, text, art_hooks, prod_hooks,
                                                                 prod_id)
            if bare and not attached:
                _set_pending(con, bare[-1])
                done.append("Want to say why? Your next message is saved as the reason.")
        if art_hooks is not None:
            art_hooks.flush()
        buttons = []
        if prod_hooks is not None:
            prod_hooks.flush()
            buttons = list(prod_hooks.buttons)
        return Reply(assistant.compose(reply_text, done, refused), refresh=changed, idea_id=attached, buttons=buttons)
    return respond


def cfg_history(settings):
    return int(assistant.cfg(settings, "chat_history"))


# ---------- module ----------

class SeedIn(BaseModel):
    text: str


class RoundIn(BaseModel):
    cards: list[str] = []
    chips: dict = {}
    engine: str | None = None


class IterateIn(BaseModel):
    feedback: str
    chips: dict = {}


class ApproveIn(BaseModel):
    image_id: int | None = None


class DecisionIn(BaseModel):
    decision: str


class TagsIn(BaseModel):
    rooms: list[str] = []
    styles: list[str] = []


class GenerateIn(BaseModel):
    template: str | None = None    # "+" picker: a library template (rel path under Portrait_Templates)
    engine: str | None = None      # one click on another engine ("Try on Nano Banana Pro"); also saved for the card


class PrefIn(BaseModel):
    key: str                       # reference_share | reference_closeness | scene_engine | generate_all_cap
    value: object = None


class SlotEngineIn(BaseModel):
    engine: str | None = None      # None = the panel default


class GenerateAllIn(BaseModel):
    key: str                       # sha1 of the estimate rows Tony saw
    cap: int | None = None


class AbIn(BaseModel):
    key: str | None = None
    value: int | None = None
    grade: str | None = None


class NanoIn(BaseModel):
    ids: list[str] = []


class GradeIn(BaseModel):
    name: str                      # the slot image file
    grade: str | None = None       # A+ ... F; None clears
    note: str | None = None


class PlanIn(BaseModel):
    slots: list[int] | None = None   # only these open slots (default: every open slot)
    wider: bool = False              # plan them one step wider (after two failed tight scenes)


class PrintsIn(BaseModel):
    name: str | None = None
    redo: bool = False             # re-run upscale + resize even when done


def bank_art(con, bank, prefix="/ikigai"):
    """Thumbnail for each Idea Bank card (Tony 2026-11-10): the approved art, else the picked image, else the latest
    finished image of the idea; None when no art was made yet."""
    for b in bank:
        row = None
        if b.get("art_image_id"):
            row = con.execute("SELECT path FROM images WHERE id=? AND status='done'", (b["art_image_id"],)).fetchone()
        if row is None:
            row = con.execute("SELECT path FROM images WHERE idea_id=? AND status='done' AND path IS NOT NULL "
                              "ORDER BY (outcome='picked') DESC, id DESC LIMIT 1", (b["id"],)).fetchone()
        b["art_url"] = art.file_url(prefix, row["path"]) if row and row["path"] else None
    return bank


def panel_context(con, settings, prefix="/ikigai"):
    with LOCK:
        ideas.maybe_weekly_refresh(con, settings)
        s = ideas.state(con, settings)
        bank_art(con, s["bank"], prefix)
    s["channel"] = get_channel(settings).label
    s["details"] = ideas.details(s)
    return s


def mount(app, con, settings, chat=None, prefix="/ikigai", ask=None, writer=None, adapter=None, spawn=None,
          upscayl=None, mockup_build=None, scene_generator=None, art_classify=None, planner_ask=None):
    """`writer` (prompt text -> raw reply), `adapter` (engine id -> engine adapter), `spawn` (run a worker),
    `upscayl` (one Upscayl pass: src, out, settings), `scene_generator` (kie.ai room scene) and `art_classify`
    (Gemini style guess) are injectable for tests; defaults are the Claude CLI, kie.ai, a daemon thread, the real
    upscayl-ncnn, kie_edit.generate and template_styles.classify_art. `planner_ask` (prompt, images -> raw reply) is
    the slot-set planner's model call (default: claude -p, app/slot_planner.default_ask)."""
    r = APIRouter(prefix=prefix, tags=["ikigai"])
    spawn = spawn or art.spawn
    art.recover(con)
    prints.recover(con)
    production.recover(con)
    slot_planner.recover(con)
    from . import references as refs_mod
    refs_mod.recover()

    def runner(rid):
        spawn(art.run_round, con, settings, rid, writer, adapter)

    def run_prints(idea_id, name=None, redo=()):
        lid = prints.start(con, settings, idea_id, name, redo)
        spawn(prints.run, con, settings, lid, upscayl, mockup_build)
        return lid

    def auto_prints(idea_id):
        """After an art approval: start upscale + resize when `prints_auto_run` is on."""
        if not prints.cfg(settings, "prints_auto_run"):
            return " Next: Art tab, Run upscale + resize."
        try:
            run_prints(idea_id)
            return " Upscale + resize started (Art tab)."
        except prints.PrintError as e:
            return f" Upscale + resize did not start: {e}."

    hooks = ArtHooks(con, settings, runner, auto_prints)
    phooks = prod_chat.ProdHooks(con, settings, spawn, scene_generator,
                                 (lambda t: chat.say("portal", t)) if chat is not None else None, prefix)
    responder = make_responder(con, settings, ask, hooks, phooks)
    if chat is not None:
        chat.set_responder(responder)

    def counts():
        s = ideas.state(con, settings)
        return {k: s[k] for k in ("shown", "pool", "banked", "room", "cap", "pool_low", "last_refresh")}

    @r.get("/panel")
    def panel(request: Request):
        return TEMPLATES.TemplateResponse(request, "studio_tab.html", {"s": panel_context(con, settings, prefix),
                                                                       "prefix": prefix})

    @r.get("/api/state")
    def api_state():
        with LOCK:
            return ideas.state(con, settings)

    @r.post("/api/ideas/{idea_id}/approve")
    def api_approve(idea_id: int):
        with LOCK:
            try:
                ideas.approve(con, idea_id)
            except KeyError:
                raise HTTPException(404, "idea not found")
            set_meta(con, "pending_deny", "")      # a later chat message is a seed again, not a deny note
            return {"ok": True, **counts()}

    @r.post("/api/ideas/{idea_id}/deny")
    def api_deny(idea_id: int):
        with LOCK:
            try:
                ideas.deny(con, idea_id)
            except KeyError:
                raise HTTPException(404, "idea not found")
            _set_pending(con, idea_id)
            title = con.execute("SELECT title FROM ideas WHERE id=?", (idea_id,)).fetchone()[0]
            if chat is not None:
                chat.say("portal", f"Denied “{title}”. Want to say why? Type it here, or just keep going.",
                         idea_id)
            return {"ok": True, "invite_comment": True, **counts()}

    @r.post("/api/refresh")
    def api_refresh():
        with LOCK:
            n = ideas.refresh(con, settings)
            return {"added": n, **counts()}

    @r.post("/api/ideas/import")
    def api_import(payload=Body(...)):
        items = payload.get("items") if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            raise HTTPException(422, "send a list of ideas or {\"items\": [...]}")
        with LOCK:
            try:
                return ideas.add_to_pool(con, items, settings)
            except ValueError as e:
                raise HTTPException(422, str(e))

    @r.post("/api/seed")
    def api_seed(body: SeedIn):
        with LOCK:
            try:
                return {"id": ideas.add_seed(con, body.text), **counts()}
            except ValueError as e:
                raise HTTPException(422, str(e))

    @r.get("/api/taste")
    def api_taste():
        with LOCK:
            return taste.build_profile(con)

    # ---------- art ----------

    def art_call(fn, *a, **kw):
        try:
            return fn(*a, **kw)
        except art.ArtError as e:
            raise HTTPException(422, str(e))

    @r.get("/api/art/options")
    def api_art_options():
        return art.options(settings)

    @r.get("/api/art/balance")
    def api_art_balance(engine: str | None = None):
        from . import engines as eng
        eid = engine or eng.config().get("default")
        try:
            ad = adapter(eid) if adapter else eng.adapter_for(eid, settings)
            return {"engine": eid, "credits": ad.credits(), "usd_per_credit": eng.config().get("usd_per_credit")}
        except eng.EngineError as e:
            return {"engine": eid, "credits": None, "error": str(e)}

    @r.get("/api/art/{idea_id}")
    def api_art_state(idea_id: int):
        return art_call(art.idea_art, con, idea_id, prefix)

    @r.get("/api/art/{idea_id}/log")
    def api_art_log(idea_id: int):
        return {"idea_id": idea_id, "log": art.oversight_log(con, idea_id)}

    @r.post("/api/art/{idea_id}/rounds")
    def api_art_round(idea_id: int, body: RoundIn):
        rid = art_call(art.start_round, con, settings, idea_id, body.cards, body.chips, body.engine)
        runner(rid)
        return art.idea_art(con, idea_id, prefix)

    @r.post("/api/art/{idea_id}/iterate")
    def api_art_iterate(idea_id: int, body: IterateIn):
        if not body.feedback.strip():
            raise HTTPException(422, "say what to change")
        rid = art_call(art.start_round, con, settings, idea_id, feedback=body.feedback.strip(), chip_changes=body.chips)
        runner(rid)
        return art.idea_art(con, idea_id, prefix)

    @r.post("/api/art/images/{image_id}/pick")
    def api_art_pick(image_id: int):
        idea_id = art_call(art.pick, con, image_id)
        return art.idea_art(con, idea_id, prefix)

    @r.post("/api/art/{idea_id}/approve")
    def api_art_approve(idea_id: int, body: ApproveIn | None = None):
        iid = art_call(art.approve, con, idea_id, body.image_id if body else None)
        extra = auto_prints(idea_id)
        if chat is not None:
            chat.say("portal", f"Art approved for #{idea_id} (image #{iid}).{extra}", idea_id)
        return art.idea_art(con, idea_id, prefix)

    # ---------- prints: upscale + resize (stage 3) ----------

    @r.get("/api/prints")
    def api_prints():
        return {"items": prints.gallery(con, settings, prefix), "auto_run": bool(prints.cfg(settings, "prints_auto_run")),
                "model": prints.cfg(settings, "upscale_model")}

    @r.get("/api/prints/{idea_id}")
    def api_prints_one(idea_id: int):
        try:
            return prints.status(con, idea_id, settings, prefix)
        except prints.PrintError as e:
            raise HTTPException(404, str(e))

    @r.post("/api/prints/{idea_id}/run")
    def api_prints_run(idea_id: int, body: PrintsIn | None = None):
        try:
            run_prints(idea_id, body.name if body else None, ("upscale", "resize") if body and body.redo else ())
        except prints.PrintError as e:
            raise HTTPException(422, str(e))
        return prints.status(con, idea_id, settings, prefix)

    # ---------- production: listing images, inline, approve / deny ----------

    @r.get("/api/production")
    def api_production():
        return JSONResponse({"items": production.overview(con, settings, prefix), "job": production.job_state()},
                            headers=NO_STORE)

    def prod_call(fn, *a, **kw):
        try:
            return fn(*a, **kw)
        except production.ProductionError as e:
            raise HTTPException(422, str(e))

    def start_auto(idea_id):
        spawn(production.auto_styles, con, settings, idea_id, art_classify)

    def start_plan(idea_id):
        """The set planner in the background (setting planner_auto): no plan yet, or the inputs changed."""
        slot_planner.auto(con, settings, idea_id, spawn, planner_ask)

    def with_fixes(pan):
        """+ the "Waiting for Claude Code" fix requests of this design (Handoffs folder, status waiting)."""
        try:
            pan["fix_requests"] = prod_chat.fix_requests(settings, pan["idea_id"])
        except Exception:  # noqa: BLE001
            pan["fix_requests"] = []
        return pan

    @r.get("/api/production/{idea_id}/panel")
    def api_production_panel(idea_id: int):
        return JSONResponse(with_fixes(prod_call(production.panel, con, settings, idea_id, prefix, start_auto,
                                                 start_plan)), headers=NO_STORE)

    @r.post("/api/production/{idea_id}/plan")
    def api_production_plan(idea_id: int, body: PlanIn | None = None):
        body = body or PlanIn()
        prod_call(production._ctx, con, settings, idea_id)
        slots = [int(x) for x in body.slots] if body.slots else None
        if not slot_planner.start(con, settings, idea_id, spawn, slots, planner_ask,
                                  tuple(slots or ()) if body.wider else ()):
            raise HTTPException(422, "the scenes are already being planned for this design")
        return JSONResponse(with_fixes(prod_call(production.panel, con, settings, idea_id, prefix)), headers=NO_STORE)

    @r.get("/api/fix-requests")
    def api_fix_requests():
        return {"items": prod_chat.fix_requests(settings)}

    @r.post("/api/production/{idea_id}/tags")
    def api_production_tags(idea_id: int, body: TagsIn):
        prod_call(production.save_tags, con, settings, idea_id, body.rooms, body.styles)
        return JSONResponse(with_fixes(prod_call(production.panel, con, settings, idea_id, prefix, start_auto,
                                                 start_plan)), headers=NO_STORE)

    @r.post("/api/production/{idea_id}/slots/{slot}/generate")
    def api_production_generate(idea_id: int, slot: int, body: GenerateIn | None = None):
        tpl = body.template if body else None
        eng = body.engine if body else None
        if eng:                                   # "Try on Nano Banana Pro": the card's engine becomes that one
            prod_call(production.set_slot_engine, con, settings, idea_id, slot, eng)
        prod_call(production.start_slot, con, settings, idea_id, slot, tpl)
        spawn(production.run_slot, con, settings, idea_id, slot, tpl, scene_generator)
        return JSONResponse(with_fixes(prod_call(production.panel, con, settings, idea_id, prefix)), headers=NO_STORE)

    # ---------- controls addendum: sliders, engines, Generate all, A/B, reference Refresh ----------

    @r.post("/api/prefs")
    def api_prefs(body: PrefIn):
        from . import prefs
        try:
            prefs.put(con, body.key, body.value, settings)
        except prefs.PrefError as e:
            raise HTTPException(422, str(e))
        return prefs.all_prefs(con, settings)

    @r.post("/api/production/{idea_id}/slots/{slot}/engine")
    def api_production_slot_engine(idea_id: int, slot: int, body: SlotEngineIn):
        prod_call(production.set_slot_engine, con, settings, idea_id, slot, body.engine or None)
        return JSONResponse(with_fixes(prod_call(production.panel, con, settings, idea_id, prefix)), headers=NO_STORE)

    @r.get("/api/production/{idea_id}/generate-all")
    def api_generate_all_estimate(idea_id: int, cap: int | None = None):
        return JSONResponse(prod_call(production.estimate, con, settings, idea_id, cap), headers=NO_STORE)

    @r.post("/api/production/{idea_id}/generate-all")
    def api_generate_all(idea_id: int, body: GenerateAllIn):
        from . import prefs
        if body.cap is not None:
            try:
                prefs.put(con, "generate_all_cap", body.cap, settings)
            except prefs.PrefError as e:
                raise HTTPException(422, str(e))
        prod_call(production.start_batch, con, settings, idea_id, body.key, body.cap, spawn, scene_generator)
        return JSONResponse(with_fixes(prod_call(production.panel, con, settings, idea_id, prefix)), headers=NO_STORE)

    @r.post("/api/production/generate-all/cancel")
    def api_generate_all_cancel():
        return {"cancelled": production.cancel_batch(), "batch": production.batch_state()}

    @r.post("/api/production/{idea_id}/slots/{slot}/abtest")
    def api_abtest_plan(idea_id: int, slot: int):
        """Free: three plans of this slot at closeness 20 / 60 / 100 (claude -p), in the background."""
        prod_call(production._ctx, con, settings, idea_id)

        def job():
            try:
                slot_planner.plan_variants(con, settings, idea_id, slot, planner_ask)
            except Exception as e:  # noqa: BLE001
                slot_planner._save(con, idea_id, lambda sp: sp.setdefault("abtest", {}).__setitem__(
                    str(slot), {"status": "failed", "message": str(e)[:200]}))
        slot_planner._save(con, idea_id, lambda sp: sp.setdefault("abtest", {}).__setitem__(
            str(slot), {"status": "planning"}))
        spawn(job)
        return JSONResponse(with_fixes(prod_call(production.panel, con, settings, idea_id, prefix)), headers=NO_STORE)

    @r.get("/api/production/{idea_id}/slots/{slot}/abtest/estimate")
    def api_abtest_estimate(idea_id: int, slot: int):
        est = prod_call(production.ab_estimate, con, settings, idea_id, slot)
        est.pop("briefs", None)
        return est

    @r.post("/api/production/{idea_id}/slots/{slot}/abtest/generate")
    def api_abtest_generate(idea_id: int, slot: int, body: AbIn):
        prod_call(production.start_abtest, con, settings, idea_id, slot, body.key or "", spawn, scene_generator)
        return JSONResponse(with_fixes(prod_call(production.panel, con, settings, idea_id, prefix)), headers=NO_STORE)

    @r.post("/api/production/{idea_id}/slots/{slot}/abtest/place")
    def api_abtest_place(idea_id: int, slot: int, body: AbIn):
        prod_call(production.ab_place, con, settings, idea_id, slot, body.value)
        return JSONResponse(with_fixes(prod_call(production.panel, con, settings, idea_id, prefix)), headers=NO_STORE)

    @r.post("/api/production/{idea_id}/slots/{slot}/abtest/grade")
    def api_abtest_grade(idea_id: int, slot: int, body: AbIn):
        prod_call(production.ab_grade, con, settings, idea_id, slot, body.value, body.grade)
        return JSONResponse(with_fixes(prod_call(production.panel, con, settings, idea_id, prefix)), headers=NO_STORE)

    @r.post("/api/references/refresh")
    def api_references_refresh():
        from . import references
        if not references.start_refresh(settings, spawn):
            raise HTTPException(422, "the reference library is already refreshing")
        return references.refresh_view(settings)

    @r.get("/api/references/refresh")
    def api_references_refresh_state():
        from . import references
        return JSONResponse(references.refresh_view(settings), headers=NO_STORE)

    @r.post("/api/references/{rid}/ok")
    def api_reference_ok(rid: str):
        from . import references
        try:
            references.mark_ok(settings, rid)
        except KeyError:
            raise HTTPException(404, "no such reference")
        return references.refresh_view(settings)

    @r.post("/api/references/{rid}/archive")
    def api_reference_archive(rid: str):
        from . import references
        try:
            references.archive_ref(settings, rid)
        except KeyError:
            raise HTTPException(404, "no such reference")
        return references.refresh_view(settings)

    @r.post("/api/references/nano")
    def api_reference_nano(body: NanoIn):
        """PAID (about 6 kie.ai credits each, only on Tony's click); the cap is enforced here."""
        from . import references
        plan = references.nano_plan(settings, body.ids)
        if not plan["ok"]:
            raise HTTPException(422, f"{plan['credits']} credits is over the cap of {plan['cap']}; pick fewer images")
        return {"results": references.nano_fill(body.ids, settings), "view": references.refresh_view(settings)}

    @r.get("/api/references/check/{name}")
    def api_reference_check(name: str):
        from . import references
        if not re.fullmatch(r"\d{4}_[A-Za-z0-9_\-]+_Cleanup_Check(_Original(_\d+)?)?\.png", name):
            raise HTTPException(404, "no such image")
        f = references.ref_dir(settings) / "Archive" / name
        if not f.is_file():
            raise HTTPException(404, "no such image")
        return FileResponse(f, headers=REVALIDATE)

    @r.post("/api/mockups/{idea_id}/run")
    def api_mockups_run(idea_id: int):
        try:
            lid = production.start(con, settings, idea_id)
        except prints.PrintError as e:
            raise HTTPException(422, str(e))
        spawn(production.run, con, settings, lid, mockup_build)
        return prints.status(con, idea_id, settings, prefix)

    @r.post("/api/production/{idea_id}/grade")
    def api_production_grade(idea_id: int, body: GradeIn):
        """Tony's grade of one slot image (realism addendum 7): stored with the listing, the template and the
        reference; Approve / Deny are untouched."""
        prod_call(production.grade, con, settings, idea_id, body.name, body.grade or None, body.note)
        return JSONResponse(with_fixes(prod_call(production.panel, con, settings, idea_id, prefix)), headers=NO_STORE)

    @r.get("/api/references/{rid}/blank")
    def api_reference_blank(rid: str):
        """The blanked reference photograph of a planned slot (Show prompt thumbnail)."""
        from . import references
        if not re.fullmatch(r"\d{4}", rid):
            raise HTTPException(404, "no such reference")
        folder = references.ref_dir(settings)
        e = (references.load(folder).get("refs") or {}).get(rid) or {}
        f = folder / str(e.get("blank") or "")
        if not e.get("blank") or not f.is_file():
            raise HTTPException(404, "no such reference")
        return FileResponse(f, headers=REVALIDATE)

    @r.get("/api/production/{idea_id}/file/{name}")
    def api_production_file(idea_id: int, name: str):
        f = production.image_path(con, settings, idea_id, name)
        if f is None:
            raise HTTPException(404, "no such image")
        return FileResponse(f, headers=REVALIDATE)

    @r.post("/api/production/{idea_id}/images/{name}")
    def api_production_decide(idea_id: int, name: str, body: DecisionIn):
        try:
            production.decide(con, settings, idea_id, name, body.decision)
        except ValueError as e:
            raise HTTPException(422, str(e))
        except KeyError:
            raise HTTPException(404, "no such image")
        return production.design(con, settings, idea_id, prefix)

    @r.get("/art-files/{idea_id}/{name}")
    def art_file(idea_id: int, name: str):
        with LOCK:
            root = art.art_root(con).resolve()
        f = (root / str(idea_id) / name).resolve()
        if (f.parent != root / str(idea_id) or f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp")
                or not f.is_file()):
            raise HTTPException(404, "no such image")
        return FileResponse(f)

    app.include_router(r)
    return Tab(id="ikigai", label="Ikigai Digital Studio", prefix=prefix, panel_template="studio_tab.html",
               chat_responder=responder, context=lambda: panel_context(con, settings, prefix))
