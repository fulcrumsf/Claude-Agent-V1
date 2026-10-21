import threading
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from . import engines, ideas
from .db import connect, load_config
from .pipeline import run_listing

app = FastAPI(title="Ikigai Portal")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
con = connect()
settings = load_config("settings")


def home():
    return RedirectResponse("/", status_code=303)


@app.get("/")
def index(request: Request):
    ideas.fill_visible(con, settings["visible_ideas"])
    rows = con.execute("SELECT * FROM ideas WHERE status IN ('shown','approved') ORDER BY status, score DESC").fetchall()
    prompts = con.execute("SELECT p.*, i.title FROM prompts p JOIN ideas i ON i.id=p.idea_id ORDER BY p.id DESC").fetchall()
    listings = con.execute("SELECT * FROM listings ORDER BY id DESC").fetchall()
    steps = con.execute("SELECT * FROM steps ORDER BY listing_id, id").fetchall()
    pool = ideas.pool_count(con)
    return templates.TemplateResponse(request, "index.html", {
        "ideas": rows, "prompts": prompts, "engines": engines.list_engines(), "listings": listings,
        "steps": steps, "pool": pool, "pool_low": pool < settings["pool_low_warning"]})


@app.post("/ideas/{idea_id}/approve")
def approve(idea_id: int):
    ideas.approve(con, idea_id)
    return home()


@app.post("/ideas/{idea_id}/deny")
def deny(idea_id: int):
    ideas.deny(con, idea_id, settings["visible_ideas"])
    return home()


@app.post("/prompts/{prompt_id}/run")
def run(prompt_id: int, engine: str = Form(...)):
    p = con.execute("SELECT * FROM prompts WHERE id=?", (prompt_id,)).fetchone()
    try:
        engines.run_prompt(engine, p["text"])
    except Exception as e:  # noqa: BLE001
        print("run_prompt:", e)
    return home()


@app.post("/listings/produce")
def produce(idea_id: int = Form(...), image_id: int = Form(...)):
    cur = con.execute("INSERT INTO listings(idea_id, image_id, folder_seq, price) VALUES (?,?,?,?)",
                      (idea_id, image_id, None, settings["price_default"]))
    con.commit()
    threading.Thread(target=run_listing, args=(connect(), cur.lastrowid, load_config("pipeline")), daemon=True).start()
    return home()
