"""Dashboard shell: main chat window (always open) + tabs. Today only the Ikigai Digital Studio tab is built;
it is a self-contained module (app/studio.py) mounted with one call, so the same shell can later host
other business modules (content, POD, affiliate...)."""
import threading
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from . import chat as chat_mod
from . import engines, studio, template_gallery
from .db import DB_LOCK, connect, load_config
from .pipeline import run_listing

app = FastAPI(title="Ikigai Portal")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
con = connect()
settings = load_config("settings")

chat = chat_mod.Chat(con)
app.include_router(chat_mod.router(chat))
ikigai = studio.mount(app, con, settings, chat)
template_gallery.mount(app, settings, ikigai.prefix)   # Templates tab (read-only room-template gallery)

# Tabs not built yet are shown as placeholders so the layout is final.
# The Art tab (stage 3: approved art -> upscale + resize) is built into index.html and reads /ikigai/api/prints.
PLACEHOLDERS = [
    {"id": "performance", "label": "Performance", "note": "Sales and search feedback into idea scoring."},
]


@app.get("/")
def index(request: Request):
    with DB_LOCK:
        prompts = con.execute("SELECT COUNT(DISTINCT idea_id) FROM ideas i JOIN prompts p ON p.idea_id=i.id "
                              "WHERE i.status='approved' AND i.art_state<>'approved'").fetchone()[0]
    return templates.TemplateResponse(request, "index.html", {
        "tab": ikigai, "s": ikigai.context(), "prefix": ikigai.prefix, "placeholders": PLACEHOLDERS,
        "prompts_waiting": prompts, "messages": chat.history()})


# ---- later stages (kept from the scaffold; UI for them arrives with the Art / Production tabs) ----

@app.post("/prompts/{prompt_id}/run")
def run(prompt_id: int, engine: str = Form(...)):
    p = con.execute("SELECT * FROM prompts WHERE id=?", (prompt_id,)).fetchone()
    try:
        engines.run_prompt(engine, p["text"])
    except Exception as e:  # noqa: BLE001
        print("run_prompt:", e)
    return RedirectResponse("/", status_code=303)


@app.post("/listings/produce")
def produce(idea_id: int = Form(...), image_id: int = Form(...)):
    cur = con.execute("INSERT INTO listings(idea_id, image_id, folder_seq, price) VALUES (?,?,?,?)",
                      (idea_id, image_id, None, settings["price_default"]))
    con.commit()
    threading.Thread(target=run_listing, args=(connect(), cur.lastrowid, load_config("pipeline")), daemon=True).start()
    return RedirectResponse("/", status_code=303)
