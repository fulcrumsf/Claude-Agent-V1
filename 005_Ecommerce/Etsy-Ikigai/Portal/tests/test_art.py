"""Stage 2 (idea to art). The prompt writer, the image engine and the worker thread are all fakes:
no Claude CLI call and no kie.ai call happens in pytest."""
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import art, assistant, engines, ideas, studio, taste
from app import chat as chat_mod
from app.db import connect

S = {"idea_cap": 100, "refresh_batch": 10, "refresh_days": 7, "pool_low_warning": 10, "art_images_per_round": 4}
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


class FakeWriter:
    """Answers like the prompt writer: one prompt per slot, cards taken from the input (or chosen for surprise)."""

    def __init__(self, surprise_cards=("flat_poster", "hatched_folk"), raw=None):
        self.calls, self.surprise_cards, self.raw = [], surprise_cards, raw

    def __call__(self, text, settings=None):
        self.calls.append(text)
        if self.raw is not None:
            return self.raw
        slots = [l for l in text.splitlines() if l.startswith("Slot ")]
        if slots:
            cards = [l.split("card ")[1].split(";")[0] for l in slots]
        else:
            cards = [c for c in self.surprise_cards for _ in range(2)]
        return "```json\n" + json.dumps({
            "cards": [{"card_id": c, "why": "fits a cat"} for c in dict.fromkeys(cards)],
            "prompts": [{"slot": k + 1, "card_id": c, "composition": ["bottom_weighted", "centered_vignette"][k % 2],
                         "note": f"try {k + 1}", "prompt": f"A gouache painting {k + 1} in the style of Someone Famous, "
                                                           "digital matte paper, two black cats."}
                        for k, c in enumerate(cards)]}) + "\n```"


class FakeAdapter:
    def __init__(self, credits=1000.0, fail_slots=()):
        self.balance, self.fail_slots, self.prompts = credits, set(fail_slots), []

    def credits(self):
        return self.balance

    def generate(self, prompt, out_path, aspect_ratio="2:3", resolution="1K", on_task=None):
        self.prompts.append((prompt, aspect_ratio, resolution))
        slot = int(out_path.name.split("_")[1])
        if on_task:
            on_task(f"task{slot}")
        if slot in self.fail_slots:
            raise engines.EngineError("kie.ai could not make it: content policy")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(PNG)
        self.balance -= 6
        return {"task_id": f"task{slot}", "path": out_path}


def banked(con, title="Two black cats sharing one red heart"):
    ideas.add_to_pool(con, [{"title": title, "description": "Two black cats nose to nose.", "lane": "rising",
                             "score": 9}], S)
    ideas.refresh(con, S)
    i = con.execute("SELECT id FROM ideas WHERE title=?", (title,)).fetchone()[0]
    ideas.approve(con, i)
    return i


@pytest.fixture
def env(tmp_path):
    con = connect(tmp_path / "t.db")
    app = FastAPI()
    chat = chat_mod.Chat(con)
    app.include_router(chat_mod.router(chat))
    w, ad = FakeWriter(), FakeAdapter()
    replies = []

    def ask(prompt, settings=None):
        return replies.pop(0)

    studio.mount(app, con, S, chat, ask=ask, writer=w, adapter=lambda eid: ad, spawn=lambda fn, *a: fn(*a))
    return {"c": TestClient(app), "con": con, "writer": w, "adapter": ad, "replies": replies, "tmp": tmp_path}


def test_options_has_six_cards_chips_and_cheapest_default(env):
    o = env["c"].get("/ikigai/api/art/options").json()
    assert [c["name"] for c in o["cards"]] == ["Linework Silhouette", "Moonlit Storybook", "Hatched Mid-Century Folk",
                                               "Palette Knife Planes", "Flat Poster Block", "Ink Line + Spot Colour"]
    assert {g["id"] for g in o["chip_groups"]} == {"palette", "accent", "mood", "composition", "texture", "treatment"}
    assert [e["label"] for e in o["engines"]] == ["GPT Image 2", "Nano Banana 2", "Nano Banana Pro"]
    cheapest = min(o["engines"], key=lambda e: e["credits_per_image"])
    assert o["default_engine"] == cheapest["id"] == "gpt-image-2"
    # swatches come from the real style profiles
    assert all(c["swatch"] and c["sources"] for c in o["cards"])


def test_plan_two_cards_vary_composition_and_respect_tony_chips():
    plan = art.plan_setup(["flat_poster", "hatched_folk"], {"accent": "red_pop", "texture": "knife_ridges"})
    assert [p["card_id"] for p in plan] == ["flat_poster"] * 2 + ["hatched_folk"] * 2
    assert plan[0]["chips"]["composition"]["id"] != plan[1]["chips"]["composition"]["id"]
    assert plan[0]["chips"]["accent"] == {"id": "red_pop", "by": "tony"}
    assert plan[0]["chips"]["palette"]["by"] == "default"
    # knife ridges does not suit the poster card: falls back to its own texture, noted
    assert plan[0]["chips"]["texture"]["id"] == "screenprint_matte" and "note" in plan[0]["chips"]["texture"]
    one = art.plan_setup(["ink_spot"], {"composition": "tight_fill"})
    assert len(one) == 4 and {p["varies"] for p in one} == {"palette"}
    assert all(p["chips"]["composition"] == {"id": "tight_fill", "by": "tony"} for p in one)


def test_full_round_pick_iterate_approve_with_oversight_log(env):
    c, con, ad, w = env["c"], env["con"], env["adapter"], env["writer"]
    i = banked(con)
    r = c.post(f"/ikigai/api/art/{i}/rounds", json={"cards": ["flat_poster", "hatched_folk"],
                                                    "chips": {"accent": True, "mood": "cheeky"}}).json()
    rnd = r["rounds"][0]
    assert rnd["status"] == "done" and len(rnd["images"]) == 4 and not r["busy"]
    assert rnd["credits_spent"] == 24
    assert all(im["status"] == "done" and im["url"].startswith("/ikigai/art-files/") for im in rnd["images"])
    # prompt was cleaned: no artist reference, no "digital", constraints present
    p0 = rnd["images"][0]["prompt"]
    assert "style of" not in p0.lower() and "digital" not in p0.lower() and "No text" in p0
    assert ad.prompts[0][1:] == ("2:3", "1K")
    # writer saw the real profile language and Tony's chips
    assert "Brushwork (from the inspiration profiles)" in w.calls[0] and "set by Tony" in w.calls[0]
    # file is served, and nothing outside the art folder is
    assert c.get(rnd["images"][0]["url"]).content == PNG
    assert c.get(f"/ikigai/art-files/{i}/..%2F..%2Ft.db").status_code == 404

    pick = rnd["images"][2]["id"]
    st = c.post(f"/ikigai/api/art/images/{pick}/pick").json()
    outs = [im["outcome"] for im in st["rounds"][0]["images"]]
    assert outs == ["passed", "passed", "picked", "passed"]

    # chat feedback -> art_iterate -> 4 new variations of the picked card
    env["replies"].append('More muted.\n```json\n{"actions":[{"type":"art_iterate","idea_id":%d,'
                          '"feedback":"more muted, less busy","chips":{"mood":"serene"}}]}\n```' % i)
    rep = c.post("/api/chat", json={"text": "make it more muted and less busy please", "selected_idea_id": i}).json()
    assert "4 new variations" in rep["reply"] and rep["refresh"]
    st = c.get(f"/ikigai/api/art/{i}").json()
    r2 = st["rounds"][0]
    assert r2["kind"] == "iterate" and r2["feedback"] == "make it more muted and less busy please"
    assert {im["card_id"] for im in r2["images"]} == {"hatched_folk"}
    assert all(im["chips"]["mood"] == {"id": "serene", "by": "tony"} for im in r2["images"])
    assert "<picked_image>" in w.calls[-1] and "more muted, less busy" in w.calls[-1]

    # approve via button (defaults to latest pick when no id) -> idea shows art approved
    c.post(f"/ikigai/api/art/images/{r2['images'][0]['id']}/pick")
    st = c.post(f"/ikigai/api/art/{i}/approve", json={}).json()
    assert st["art_state"] == "approved" and st["art_image_id"] == r2["images"][0]["id"]
    assert st["production"] == "not built yet"
    assert c.post(f"/ikigai/api/art/{i}/rounds", json={}).status_code == 422      # no more rounds after approval
    bank = c.get("/ikigai/api/state").json()["bank"]
    assert bank[0]["art_state"] == "approved"

    actions = [e["action"] for e in c.get(f"/ikigai/api/art/{i}/log").json()["log"]]
    for a in ("round", "prompt", "image", "pick", "feedback", "approve", "round_end"):
        assert a in actions
    log = c.get(f"/ikigai/api/art/{i}/log").json()["log"]
    first = next(e for e in log if e["action"] == "round")["detail"]
    assert first["engine"] == "gpt-image-2" and first["chips_set_by_tony"] == {"accent": "red_pop", "mood": "cheeky"}
    assert any(s.startswith("0005_") for s in first["source_images"])
    fb = next(e for e in log if e["action"] == "feedback")["detail"]
    assert fb["text"] == "make it more muted and less busy please" and fb["summary"] == "more muted, less busy"

    # taste: picks and passes per card, feedback text
    prof = taste.build_profile(con)["art"]
    by = {x["card_id"]: x for x in prof["cards"]}
    assert by["hatched_folk"]["picked"] == 2 and by["hatched_folk"]["approved"] == 1
    assert by["flat_poster"]["passed"] == 2 and by["flat_poster"]["picked"] == 0
    assert prof["feedback"][0]["text"] == "make it more muted and less busy please"
    assert "Art styles (picked vs passed on)" in (env["tmp"] / "Taste_Profile.md").read_text()


def test_surprise_me_lets_writer_pick_two_cards(env):
    c, con = env["c"], env["con"]
    i = banked(con)
    st = c.post(f"/ikigai/api/art/{i}/rounds", json={"cards": [], "chips": {}}).json()
    r = st["rounds"][0]
    assert r["surprise"] and r["status"] == "done"
    assert [im["card_id"] for im in r["images"]] == ["flat_poster", "flat_poster", "hatched_folk", "hatched_folk"]
    assert "fits a cat" in r["writer_note"]
    log = c.get(f"/ikigai/api/art/{i}/log").json()["log"]
    assert any(x.startswith("0003_") for x in next(e for e in log if e["action"] == "prompt" and
                                                   e["detail"]["card"] == "hatched_folk")["detail"]["source_images"])
    assert "Surprise me" in env["writer"].calls[0] and "Card ink_spot" in env["writer"].calls[0]


def test_low_credits_and_bad_writer_spend_nothing(tmp_path):
    con = connect(tmp_path / "t.db")
    i = banked(con)
    ad = FakeAdapter(credits=10)
    rid = art.start_round(con, S, i, ["flat_poster"])
    art.run_round(con, S, rid, FakeWriter(), lambda e: ad)
    r = art.idea_art(con, i)["rounds"][0]
    assert r["status"] == "failed" and "needs about 24" in r["message"] and not ad.prompts
    rid = art.start_round(con, S, i, ["flat_poster"])
    w = FakeWriter(raw="sorry, I can't")
    art.run_round(con, S, rid, w, lambda e: FakeAdapter())
    r = art.idea_art(con, i)["rounds"][0]
    assert r["status"] == "failed" and "Nothing was spent" in r["message"] and len(w.calls) == 2   # one retry


def test_writer_offline_and_partial_failure(tmp_path):
    con = connect(tmp_path / "t.db")
    i = banked(con)

    def offline(text, settings=None):
        raise assistant.ChatUnavailable("The prompt writer took too long to answer")
    rid = art.start_round(con, S, i, ["ink_spot"])
    art.run_round(con, S, rid, offline, lambda e: FakeAdapter())
    assert "took too long" in art.idea_art(con, i)["rounds"][0]["message"]
    rid = art.start_round(con, S, i, ["ink_spot"])
    art.run_round(con, S, rid, FakeWriter(), lambda e: FakeAdapter(fail_slots={2}))
    r = art.idea_art(con, i)["rounds"][0]
    assert r["status"] == "partial" and [im["status"] for im in r["images"]].count("failed") == 1
    assert "content policy" in next(im["error"] for im in r["images"] if im["status"] == "failed")


def test_guards(env):
    c, con = env["c"], env["con"]
    ideas.add_to_pool(con, [{"title": "not banked", "lane": "test", "score": 1}], S)
    ideas.refresh(con, S)
    nb = con.execute("SELECT id FROM ideas WHERE title='not banked'").fetchone()[0]
    assert "Idea bank" in c.post(f"/ikigai/api/art/{nb}/rounds", json={}).json()["detail"]
    i = banked(con)
    assert c.post(f"/ikigai/api/art/{i}/rounds", json={"cards": ["a", "b", "c"]}).status_code == 422
    assert "unknown" in c.post(f"/ikigai/api/art/{i}/rounds", json={"chips": {"palette": "neon"}}).json()["detail"]
    assert "pick an image first" in c.post(f"/ikigai/api/art/{i}/iterate", json={"feedback": "x"}).json()["detail"]
    # chat iterate with nothing picked is refused, nothing generated
    env["replies"].append('```json\n{"actions":[{"type":"art_iterate","idea_id":%d,"feedback":"brighter"}]}\n```' % i)
    rep = c.post("/api/chat", json={"text": "brighter", "selected_idea_id": i}).json()
    assert "Not done" in rep["reply"] and not env["adapter"].prompts


def test_restart_marks_running_rounds_failed(tmp_path):
    con = connect(tmp_path / "t.db")
    i = banked(con)
    art.start_round(con, S, i, ["flat_poster"])
    art.recover(con)
    r = art.idea_art(con, i)["rounds"][0]
    assert r["status"] == "failed" and "restart" in r["message"]


def test_chat_snapshot_shows_art_state(tmp_path):
    con = connect(tmp_path / "t.db")
    i = banked(con)
    rid = art.start_round(con, S, i, ["flat_poster"])
    art.run_round(con, S, rid, FakeWriter(), lambda e: FakeAdapter())
    img = art.idea_art(con, i)["rounds"][0]["images"][1]["id"]
    art.pick(con, img)
    snap = assistant.snapshot(con, S, i)
    assert f"Picked image: #{img}" in snap and "Flat Poster Block" in snap


def test_kie_adapter_payload_without_network(tmp_path, monkeypatch):
    """The real adapter builds the documented kie.ai calls; httpx is replaced by a stub transport."""
    import httpx
    seen = []

    def handler(req):
        seen.append(req)
        if req.url.path.endswith("/createTask"):
            return httpx.Response(200, json={"code": 200, "data": {"taskId": "t1"}})
        if req.url.path.endswith("/recordInfo"):
            return httpx.Response(200, json={"code": 200, "data": {"state": "success",
                                                                    "resultJson": json.dumps({"resultUrls": ["https://x/img.png"]})}})
        if req.url.path.endswith("/credit"):
            return httpx.Response(200, json={"code": 200, "data": 120.5})
        return httpx.Response(200, content=PNG)

    monkeypatch.setenv("KIE_API_KEY", "test-key")
    e = engines.get_engine("gpt-image-2")
    ad = engines.KieAdapter(e, poll_s=0, client=httpx.Client(transport=httpx.MockTransport(handler)))
    assert ad.credits() == 120.5
    out = ad.generate("a painting", tmp_path / "a.png")
    body = json.loads(seen[1].content)
    assert body == {"model": "gpt-image-2-text-to-image", "input": {"prompt": "a painting", "aspect_ratio": "2:3",
                                                                    "resolution": "1K"}}
    assert out["path"].read_bytes() == PNG and out["task_id"] == "t1"
