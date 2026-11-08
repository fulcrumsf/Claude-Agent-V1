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
  POST /api/prints/{idea_id}/run  {name?, redo?} -> queue upscale + resize (name: first run only; redo: run again)
"""
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from fastapi.responses import FileResponse

from . import art, assistant, ideas, production, prints, taste
from .channels import get_channel
from .chat import Reply
from .db import DB_LOCK, get_meta, set_meta

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
LOCK = DB_LOCK                 # shared with app/art.py workers
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


def make_responder(con, settings, ask=None, art_hooks=None):
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
            prompt = assistant.build_prompt(con, settings, history, text, getattr(chat, "selected_idea_id", None), note)

        try:
            raw = ask(prompt, settings)                                  # seconds; never hold the lock here
        except assistant.ChatUnavailable as e:
            if attached:
                return Reply(f"Thanks, noted against “{title}”. ({e}, so no reply this time.)", idea_id=attached)
            return Reply(f"{e}. Your message is saved; try again in a moment.")

        reply_text, actions = assistant.parse_reply(raw)
        with LOCK:
            done, refused, changed, bare = assistant.run_actions(con, settings, actions, text, art_hooks)
            if bare and not attached:
                _set_pending(con, bare[-1])
                done.append("Want to say why? Your next message is saved as the reason.")
        if art_hooks is not None:
            art_hooks.flush()
        return Reply(assistant.compose(reply_text, done, refused), refresh=changed, idea_id=attached)
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


class PrintsIn(BaseModel):
    name: str | None = None
    redo: bool = False             # re-run upscale + resize even when done


def panel_context(con, settings):
    with LOCK:
        ideas.maybe_weekly_refresh(con, settings)
        s = ideas.state(con, settings)
    s["channel"] = get_channel(settings).label
    s["details"] = ideas.details(s)
    return s


def mount(app, con, settings, chat=None, prefix="/ikigai", ask=None, writer=None, adapter=None, spawn=None,
          upscayl=None):
    """`writer` (prompt text -> raw reply), `adapter` (engine id -> engine adapter), `spawn` (run a worker)
    and `upscayl` (one Upscayl pass: src, out, settings) are injectable for tests; defaults are the Claude CLI,
    kie.ai, a daemon thread and the real upscayl-ncnn."""
    r = APIRouter(prefix=prefix, tags=["ikigai"])
    spawn = spawn or art.spawn
    art.recover(con)
    prints.recover(con)

    def runner(rid):
        spawn(art.run_round, con, settings, rid, writer, adapter)

    def run_prints(idea_id, name=None, redo=()):
        lid = prints.start(con, settings, idea_id, name, redo)
        spawn(prints.run, con, settings, lid, upscayl)
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
    responder = make_responder(con, settings, ask, hooks)
    if chat is not None:
        chat.set_responder(responder)

    def counts():
        s = ideas.state(con, settings)
        return {k: s[k] for k in ("shown", "pool", "banked", "room", "cap", "pool_low", "last_refresh")}

    @r.get("/panel")
    def panel(request: Request):
        return TEMPLATES.TemplateResponse(request, "studio_tab.html", {"s": panel_context(con, settings),
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
        return {"items": production.overview(con, settings, prefix)}

    @r.get("/api/production/{idea_id}/file/{name}")
    def api_production_file(idea_id: int, name: str):
        f = production.image_path(con, settings, idea_id, name)
        if f is None:
            raise HTTPException(404, "no such image")
        return FileResponse(f)

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
               chat_responder=responder, context=lambda: panel_context(con, settings))
