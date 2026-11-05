"""Stage 3 (approved art -> upscale + resize). Upscayl is faked (a Pillow 4x resample); the print sizes are
shrunk to tiny pixel sizes so the real crop/resize/JPEG/DPI code runs on small images in well under a second."""
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image

from app import art, prints, studio
from app import chat as chat_mod
from app.db import connect
from app.pipeline import run_listing

REAL_SIZES = prints.sizes()


def tiny_sizes():
    """The real 5 sizes at 10 DPI (240x360, 180x240, 240x300, 220x280, 234x331)."""
    return [{**s, "w_px": round(s["w_in"] * 10), "h_px": round(s["h_in"] * 10), "dpi": 300} for s in REAL_SIZES]


def fake_upscayl(calls):
    def run(src, out, settings):
        calls.append((str(src), str(out)))
        with Image.open(src) as im:
            im.resize((im.width * 4, im.height * 4), Image.LANCZOS).save(out)
    return run


def painting(path, w=64, h=96):
    """Cream background, a dark 'subject' block from 30% to 100% of the height (touching the bottom)."""
    im = Image.new("RGB", (w, h), (235, 225, 200))
    for y in range(int(h * 0.3), h):
        for x in range(w // 6, w - w // 6):
            im.putpixel((x, y), (30, 28, 25))
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


def approved_idea(con, title="Cat curled on an open book under a reading lamp: book-club cat print", approve=True):
    cur = con.execute("INSERT INTO ideas(title, description, status, art_state) VALUES (?,?,?,?)",
                      (title, "d", "approved", "approved" if approve else ""))
    iid = cur.lastrowid
    rel = f"{iid}/r01_1_1.png"
    painting(art.art_root(con) / rel)
    img = con.execute("INSERT INTO images(idea_id, engine, path, status, approved) VALUES (?,?,?,?,1)",
                      (iid, "gpt-image-2", rel, "done")).lastrowid
    if approve:
        con.execute("UPDATE ideas SET art_image_id=? WHERE id=?", (img, iid))
    con.commit()
    return iid


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(prints, "sizes", tiny_sizes)
    con = connect(tmp_path / "t.db")
    (tmp_path / "Designs").mkdir()
    S = {"designs_root": str(tmp_path / "Designs"), "design_seq_floor": 120, "price_default": 6.5,
         "upscale_model": "remacri-4x"}
    app = FastAPI()
    chat = chat_mod.Chat(con)
    app.include_router(chat_mod.router(chat))
    calls = []
    studio.mount(app, con, S, chat, ask=lambda p, s=None: "", spawn=lambda fn, *a: fn(*a), upscayl=fake_upscayl(calls))
    return {"c": TestClient(app), "con": con, "S": S, "tmp": tmp_path, "calls": calls}


def test_design_name_is_short_title_case_without_punctuation():
    assert prints.design_name("Cat curled on an open book under a reading lamp: book-club cat print") == "Book Club Cat"
    assert prints.design_name("Year of the Fire Goat 2027: mid-century gouache goat among plum blossoms") == "Year Fire Goat 2027"
    assert prints.design_name("Edo ginkgo leaf") == "Edo Ginkgo Leaf"
    assert prints.clean_name("  pastel   waves! ") == "Pastel Waves"


def test_real_print_sizes_match_tonys_00120_files():
    got = {prints.file_name("Pastel Waves", s): (s["w_px"], s["h_px"]) for s in REAL_SIZES}
    assert got == {"Pastel Waves_2x3_24x36.jpg": (7200, 10800), "Pastel Waves_3x4_18x24.jpg": (5400, 7200),
                   "Pastel Waves_4x5_24x30.jpg": (7200, 9000), "Pastel Waves_11x14_22x28.jpg": (6600, 8400),
                   "Pastel Waves_ISO_A1_23.4x33.1.jpg": (7020, 9930)}


def test_next_seq_after_drive_floor_local_folders_and_listings(env):
    con, S = env["con"], env["S"]
    assert prints.next_seq(con, S) == 121
    (env["tmp"] / "Designs" / "00125-Old One").mkdir()
    assert prints.next_seq(con, S) == 126
    con.execute("INSERT INTO listings(idea_id, image_id, folder_seq) VALUES (1, 1, 130)")
    assert prints.next_seq(con, S) == 131


def test_crop_cuts_background_first_then_centres():
    flags = [False] * 10 + [True] * 90                 # top 10% is background, subject touches the bottom
    start, la, lb = prints.place_crop(flags, 0.95)     # cut 5 rows: all from the empty top
    assert start == 0.05 and la == lb == 0
    start, la, lb = prints.place_crop(flags, 0.80)     # cut 20: 10 free at the top, then 10 subject rows
    assert la + lb == pytest.approx(0.10)
    assert prints.place_crop([False] * 100, 0.8)[0] == pytest.approx(0.10)   # nothing anywhere: centred


def test_run_upscale_and_resize_end_to_end_with_tiny_real_images(env):
    c, con = env["c"], env["con"]
    iid = approved_idea(con)
    st = c.get(f"/ikigai/api/prints/{iid}").json()
    assert st["steps"]["upscale"]["status"] == "not started" and st["can_run"] and st["name"] == "Book Club Cat"
    st = c.post(f"/ikigai/api/prints/{iid}/run", json={}).json()
    assert st["steps"]["upscale"]["status"] == "done", st
    assert st["steps"]["resize"]["status"] == "done", st
    assert st["done"] and not st["can_run"] and st["folder_seq"] == 121
    assert st["folder_rel"] == "Designs/00121-Book Club Cat/01-Printables"
    assert len(env["calls"]) == 1 and "upscaled" in env["calls"][0][1]
    out = env["tmp"] / "Designs" / "00121-Book Club Cat" / "01-Printables"
    names = sorted(p.name for p in out.iterdir())
    assert names == sorted(prints.file_name("Book Club Cat", s) for s in tiny_sizes())
    # nothing else made in the design folder at this stage
    assert [p.name for p in out.parent.iterdir()] == ["01-Printables"]
    for s in tiny_sizes():
        with Image.open(out / prints.file_name("Book Club Cat", s)) as im:
            assert im.format == "JPEG" and im.size == (s["w_px"], s["h_px"])
            assert tuple(round(d) for d in im.info["dpi"]) == (300, 300)
    files = {f["ratio"]: f for f in st["files"]}
    assert files["2x3"]["cut"] == 0 and files["2x3"]["sides"] == "none"
    # 4x5 from 2:3 cuts 16.7% of the height: the empty top goes first
    assert files["4x5"]["cut"] == pytest.approx(1 / 6, abs=0.01)
    assert files["4x5"]["subject_cut"] < files["4x5"]["cut"]
    # later steps of the pipeline did not run
    steps = {r["name"]: r["status"] for r in con.execute("SELECT name, status FROM steps")}
    assert "mockups" not in steps
    # gallery lists it
    g = c.get("/ikigai/api/prints").json()
    assert [x["idea_id"] for x in g["items"]] == [iid] and g["auto_run"] is False


def test_upscayl_missing_is_blocked_in_plain_words(env, monkeypatch):
    con, S = env["con"], {**env["S"], "upscayl_bin": "no-such-upscayl"}
    iid = approved_idea(con)
    lid = prints.start(con, S, iid)
    assert prints.run(con, S, lid) == "blocked"
    st = prints.status(con, iid, S)
    assert st["steps"]["upscale"]["status"] == "blocked"
    assert "Upscayl is not installed" in st["steps"]["upscale"]["message"]
    assert st["steps"]["resize"]["status"] == "pending" and st["can_run"]
    # run again with Upscayl back: picks up where it stopped, same folder number
    assert prints.run(con, S, prints.start(con, S, iid), upscayl=fake_upscayl([])) == "done"
    assert prints.status(con, iid, S)["folder_seq"] == 121


def test_not_approved_art_is_refused(env):
    iid = approved_idea(env["con"], approve=False)
    r = env["c"].post(f"/ikigai/api/prints/{iid}/run", json={})
    assert r.status_code == 422 and "approve the art first" in r.json()["detail"]


def test_custom_name_on_first_run(env):
    iid = approved_idea(env["con"])
    st = env["c"].post(f"/ikigai/api/prints/{iid}/run", json={"name": "reading cat!"}).json()
    assert st["name"] == "Reading Cat" and st["folder_rel"].startswith("Designs/00121-Reading Cat/")


def test_auto_run_setting_starts_after_art_approval(tmp_path, monkeypatch):
    monkeypatch.setattr(prints, "sizes", tiny_sizes)
    con = connect(tmp_path / "t.db")
    (tmp_path / "Designs").mkdir()
    S = {"designs_root": str(tmp_path / "Designs"), "prints_auto_run": True, "art_images_per_round": 4}
    app = FastAPI()
    studio.mount(app, con, S, None, ask=lambda p, s=None: "", spawn=lambda fn, *a: fn(*a), upscayl=fake_upscayl([]))
    iid = approved_idea(con, approve=False)
    img = con.execute("SELECT id FROM images WHERE idea_id=?", (iid,)).fetchone()[0]
    con.execute("UPDATE images SET outcome='picked', round_id=1, card_id='flat_poster' WHERE id=?", (img,))
    con.commit()
    TestClient(app).post(f"/ikigai/api/art/{iid}/approve", json={"image_id": img})
    assert prints.status(con, iid, S)["done"]


def test_restart_marks_running_steps_failed(env):
    con = env["con"]
    iid = approved_idea(con)
    lid = prints.start(con, env["S"], iid)
    assert prints.status(con, iid, env["S"])["steps"]["upscale"]["status"] == "queued"
    prints.recover(con)
    st = prints.status(con, iid, env["S"])
    assert st["steps"]["upscale"]["status"] == "failed" and "restart" in st["steps"]["upscale"]["message"]
    assert st["can_run"]
    json.loads(con.execute("SELECT record FROM listings WHERE id=?", (lid,)).fetchone()[0])


def test_run_listing_without_stop_after_keeps_old_behaviour(tmp_path):
    con = connect(tmp_path / "t.db")
    con.execute("INSERT INTO listings(idea_id, image_id) VALUES (99, 99)")
    con.execute("INSERT INTO ideas(id, title, description) VALUES (99, 't', 'd')")
    con.commit()
    assert run_listing(con, 1, {"steps": ["generate_art", "upscale"]}) == "blocked"


def test_redo_runs_both_steps_again_in_the_same_folder(env):
    c = env["c"]
    iid = approved_idea(env["con"])
    c.post(f"/ikigai/api/prints/{iid}/run", json={})
    st = c.post(f"/ikigai/api/prints/{iid}/run", json={}).json()   # already done: nothing queued again
    assert st["done"] and len(env["calls"]) == 1
    st = c.post(f"/ikigai/api/prints/{iid}/run", json={"redo": True}).json()
    assert st["done"] and len(env["calls"]) == 2 and st["folder_seq"] == 121
