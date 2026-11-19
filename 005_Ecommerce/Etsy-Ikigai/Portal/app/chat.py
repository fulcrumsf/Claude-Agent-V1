"""Main chat window (dashboard level, always open).

A responder is any callable `(text, chat) -> Reply`; the dashboard plugs one in with `Chat.set_responder(...)`.
The Ikigai module's responder (app/studio.py) answers simple commands locally and sends everything else to
the headless Claude CLI (app/assistant.py). `chat.selected_idea_id` holds the idea open in the Details panel
for the message being handled (sent by the page), so a responder can use it as context.
"""
from dataclasses import dataclass, field
from typing import Callable

from fastapi import APIRouter
from pydantic import BaseModel

from .db import DB_LOCK


@dataclass
class Reply:
    text: str
    refresh: bool = False          # tell the page to reload the active panel
    idea_id: int | None = None
    buttons: list = field(default_factory=list)   # [{label, url, body}]: Tony's own click runs it (paid regenerate)


@dataclass
class Chat:
    con: object
    responder: Callable[[str, "Chat"], Reply] = field(default=lambda text, chat: Reply("Noted."))
    selected_idea_id: int | None = None
    prod_idea_id: int | None = None    # design open in the Production tab (last one the page sent)
    prod_slot: int | None = None       # slot Tony pointed at with "Ask chat" on its card

    def set_responder(self, fn):
        self.responder = fn

    def say(self, role, text, idea_id=None):
        with DB_LOCK:                  # shared connection; art workers write from other threads
            self.con.execute("INSERT INTO chat_messages(role, text, idea_id) VALUES (?,?,?)", (role, text, idea_id))
            self.con.commit()

    def history(self, limit=60):
        with DB_LOCK:
            rows = self.con.execute("SELECT * FROM chat_messages ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows[::-1]]

    def handle(self, text, selected_idea_id=None, prod_idea_id=None, prod_slot=None):
        text = (text or "").strip()
        if not text:
            return Reply("")
        self.say("tony", text)
        self.selected_idea_id = selected_idea_id
        if prod_idea_id is not None:
            self.prod_idea_id = prod_idea_id
        self.prod_slot = prod_slot
        try:
            reply = self.responder(text, self)
        except Exception as e:  # noqa: BLE001  never break the page; the typed text is already saved
            print("chat responder:", repr(e))
            reply = Reply("Something went wrong on my side. Your message is saved.")
        if reply.text:
            self.say("portal", reply.text, reply.idea_id)
        return reply


class ChatIn(BaseModel):
    text: str
    selected_idea_id: int | None = None
    prod_idea_id: int | None = None
    prod_slot: int | None = None


def router(chat: Chat, prefix="/api/chat"):
    r = APIRouter(prefix=prefix, tags=["chat"])

    @r.get("")
    def history():
        return {"messages": chat.history()}

    @r.post("")
    def post(body: ChatIn):
        rep = chat.handle(body.text, body.selected_idea_id, body.prod_idea_id, body.prod_slot)
        return {"reply": rep.text, "refresh": rep.refresh, "buttons": rep.buttons, "messages": chat.history()}

    return r
