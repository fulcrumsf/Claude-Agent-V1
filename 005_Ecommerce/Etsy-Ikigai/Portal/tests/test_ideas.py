import json
import sqlite3

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import chat as chat_mod
from app import assistant, ideas, import_ideas, studio, taste
from app.db import connect

S = {"idea_cap": 100, "refresh_batch": 10, "refresh_days": 7, "pool_low_warning": 10}


def idea(k, **kw):
    return {"title": f"idea {k}", "description": "d", "lane": "rising", "score": k,
            "evidence": {"why_buyer": "b", "why_now": "n", "competitors": "c", "warning": "w", "sources": ["Alura"]},
            **kw}


def make(tmp_path, n=15):
    con = connect(tmp_path / "t.db")
    ideas.add_to_pool(con, [idea(k) for k in range(n)], S)
    return con


def st(con, status):
    return ideas.count(con, status)


# ---- scaffold behaviour still works ----

def test_fills_ten(tmp_path):
    con = make(tmp_path)
    ideas.fill_visible(con, 10)
    assert st(con, "shown") == 10


def test_approve_makes_prompt_and_banks(tmp_path):
    con = make(tmp_path)
    ideas.refresh(con, S)
    i = con.execute("SELECT id FROM ideas WHERE status='shown'").fetchone()[0]
    ideas.approve(con, i)
    assert con.execute("SELECT COUNT(*) FROM prompts").fetchone()[0] == 1
    assert [b["id"] for b in ideas.bank(con)] == [i]


def test_old_seed_script_rows_still_load(tmp_path):
    con = connect(tmp_path / "t.db")
    ideas.add_to_pool(con, [dict(title="Sage Arcs 1", description="d", lane="test", evidence="PLACEHOLDER", score=5),
                            dict(title="Old proven", description="d", lane="proven", evidence="", score=4)])
    ideas.refresh(con, S)
    v = {x["title"]: x for x in ideas.visible(con)}
    assert v["Sage Arcs 1"]["evidence"] == {"summary": "PLACEHOLDER"}
    assert v["Old proven"]["lane"] == "steady"


def test_migrates_existing_db(tmp_path):
    p = tmp_path / "old.db"
    raw = sqlite3.connect(p)
    raw.executescript("CREATE TABLE ideas (id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL,"
                      " lane TEXT NOT NULL DEFAULT 'test', evidence TEXT NOT NULL DEFAULT '', score REAL NOT NULL DEFAULT 0,"
                      " status TEXT NOT NULL DEFAULT 'pool');"
                      "INSERT INTO ideas(title, description, lane, status) VALUES ('kept','d','proven','shown');")
    raw.commit(); raw.close()
    con = connect(p)
    r = con.execute("SELECT * FROM ideas").fetchone()
    assert r["title"] == "kept" and r["lane"] == "steady" and r["source"] == "research" and r["created_at"]


# ---- pool, cap, refresh ----

def test_refresh_adds_not_replaces(tmp_path):
    con = make(tmp_path, 25)
    assert ideas.refresh(con, S) == 10
    first = {x["id"] for x in ideas.visible(con)}
    assert ideas.refresh(con, S) == 10
    after = {x["id"] for x in ideas.visible(con)}
    assert first < after and len(after) == 20
    assert ideas.refresh(con, S) == 5 and ideas.refresh(con, S) == 0


def test_deny_leaves_list_without_instant_refill(tmp_path):
    con = make(tmp_path)
    ideas.refresh(con, S)
    a, b = [x["id"] for x in ideas.visible(con)[:2]]
    ideas.approve(con, a)
    ideas.deny(con, b)
    assert st(con, "shown") == 8 and st(con, "pool") == 5
    assert b not in {x["id"] for x in ideas.visible(con)}


def test_hard_cap_and_top_up(tmp_path):
    con = make(tmp_path, 95)
    res = ideas.add_to_pool(con, [idea(k) for k in range(100, 120)], S)
    assert len(res["added"]) == 5 and res["skipped_cap"] == 15 and res["room_left"] == 0
    # highest scores win at the cap
    assert {r[0] for r in con.execute("SELECT title FROM ideas WHERE score>=100")} == {f"idea {k}" for k in range(115, 120)}
    ideas.refresh(con, S)
    ids = [x["id"] for x in ideas.visible(con)[:2]]
    ideas.approve(con, ids[0]); ideas.deny(con, ids[1])
    assert ideas.room(con, S) == 2
    res = ideas.add_to_pool(con, [idea(k) for k in range(200, 210)], S)
    assert len(res["added"]) == 2 and ideas.room(con, S) == 0


def test_duplicates_and_denied_titles_never_return(tmp_path):
    con = make(tmp_path, 3)
    ideas.refresh(con, S)
    ideas.deny(con, ideas.visible(con)[0]["id"])
    res = ideas.add_to_pool(con, [idea(0), idea(1), idea(50)], S)
    assert res["skipped_duplicate"] == 2 and len(res["added"]) == 1


def test_bad_lane_rejected(tmp_path):
    con = connect(tmp_path / "t.db")
    with pytest.raises(ValueError):
        ideas.add_to_pool(con, [idea(1, lane="viral")], S)


def test_weekly_refresh_due(tmp_path):
    con = make(tmp_path)
    assert ideas.maybe_weekly_refresh(con, S) == 10
    assert ideas.maybe_weekly_refresh(con, S) == 0      # not due again until 7 days pass
    con.execute("UPDATE meta SET value='2000-01-01 00:00:00' WHERE key='last_refresh'")
    assert ideas.maybe_weekly_refresh(con, S) == 5


# ---- seeds, taste ----

def test_seed_is_visible_marked_and_ignores_cap(tmp_path):
    con = make(tmp_path, 100)
    i = ideas.add_seed(con, "Retro bowling alley art for league bowlers")
    r = con.execute("SELECT * FROM ideas WHERE id=?", (i,)).fetchone()
    assert r["status"] == "shown" and r["source"] == "seed"
    assert ideas.visible(con)[0]["id"] == i                 # seeds sort first


def test_taste_events_and_profile_file(tmp_path):
    con = make(tmp_path)
    ideas.refresh(con, S)
    a, b = [x["id"] for x in ideas.visible(con)[:2]]
    ideas.approve(con, a)
    ideas.deny(con, b)
    ideas.comment(con, b, "too generic")
    acts = [r[0] for r in con.execute("SELECT action FROM taste_events ORDER BY id")]
    assert acts == ["approve", "deny", "comment"]
    p = json.loads((tmp_path / "Taste_Profile.json").read_text())
    assert p["totals"] == {"approved": 1, "denied": 1, "seeds": 0, "deny_comments": 1}
    assert p["recent_denied"][0]["comments"] == ["too generic"]
    assert "too generic" in (tmp_path / "Taste_Profile.md").read_text()


# ---- import CLI ----

def test_import_cli(tmp_path, capsys):
    db = tmp_path / "t.db"
    batch = tmp_path / "batch.json"
    batch.write_text(json.dumps({"items": [idea(k) for k in range(3)]}))
    assert import_ideas.main([str(batch), "--db", str(db)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["added"] == 3
    import_ideas.main(["--room", "--db", str(db)])
    assert json.loads(capsys.readouterr().out)["room"] == 97


# ---- HTTP module (mount + chat) ----

class FakeClaude:
    """Stands in for `claude -p`. Tests set .reply (str) or .error; prompts are recorded."""
    def __init__(self):
        self.reply, self.error, self.prompts = "OK.", None, []

    def __call__(self, prompt, settings=None):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return self.reply


@pytest.fixture(autouse=True)
def no_real_cli(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("tests must not call the real Claude CLI")
    monkeypatch.setattr(assistant.subprocess, "run", boom)


@pytest.fixture
def fake():
    return FakeClaude()


@pytest.fixture
def client(tmp_path, fake):
    con = connect(tmp_path / "t.db")
    app = FastAPI()
    chat = chat_mod.Chat(con)
    app.include_router(chat_mod.router(chat))
    studio.mount(app, con, S, chat, ask=fake)
    return TestClient(app), con


def test_http_import_refresh_approve_deny_comment(client):
    c, con = client
    r = c.post("/ikigai/api/ideas/import", json=[idea(k) for k in range(12)])
    assert len(r.json()["added"]) == 12
    assert c.post("/ikigai/api/refresh").json()["added"] == 10
    vis = c.get("/ikigai/api/state").json()["visible"]
    assert vis[0]["evidence"]["why_buyer"] == "b"
    assert c.post(f"/ikigai/api/ideas/{vis[0]['id']}/approve").json()["banked"] == 1
    d = c.post(f"/ikigai/api/ideas/{vis[1]['id']}/deny").json()
    assert d["invite_comment"] and d["shown"] == 8
    # next chat message attaches to the denied idea
    c.post("/api/chat", json={"text": "Feels like every other abstract print"})
    ev = con.execute("SELECT idea_id, comment FROM taste_events WHERE action='comment'").fetchone()
    assert ev["idea_id"] == vis[1]["id"] and "abstract" in ev["comment"]
    # an explicit seed command still adds a seed
    j = c.post("/api/chat", json={"text": "seed: Lighthouse keeper cats"}).json()
    assert j["refresh"] and "seed" in j["reply"].lower()
    assert any(x["source"] == "seed" for x in c.get("/ikigai/api/state").json()["visible"])
    assert c.get("/ikigai/api/taste").json()["totals"]["deny_comments"] == 1
    assert "Lighthouse keeper cats" in c.get("/ikigai/panel").text


def test_bare_deny_and_chat_commands(client):
    c, con = client
    c.post("/ikigai/api/ideas/import", json=[idea(k) for k in range(3)])
    c.post("/api/chat", json={"text": "refresh"})
    i = c.get("/ikigai/api/state").json()["visible"][0]["id"]
    c.post(f"/ikigai/api/ideas/{i}/deny")
    assert "without a note" in c.post("/api/chat", json={"text": "skip"}).json()["reply"]
    assert con.execute("SELECT COUNT(*) FROM taste_events WHERE action='deny'").fetchone()[0] == 1
    assert con.execute("SELECT COUNT(*) FROM taste_events WHERE action='comment'").fetchone()[0] == 0
    assert "room" in c.post("/api/chat", json={"text": "status"}).json()["reply"]
    assert c.post("/ikigai/api/ideas/999/approve").status_code == 404
    assert c.post("/ikigai/api/ideas/import", json=[{"title": "x", "lane": "nope"}]).status_code == 422


def test_drive_sequence_and_name():
    from app.drive import next_sequence, folder_name
    assert next_sequence(["00083-A", "00120-Pastel Waves", "notes"]) == 121
    assert next_sequence([]) == 1
    assert folder_name(121, " Sage Leaf ") == "00121-Sage Leaf"


def test_channel_is_swappable():
    from app.channels import get_channel, NotConfigured
    ch = get_channel({"sales_channel": "etsy"})
    assert ch.label == "Etsy"
    with pytest.raises(NotConfigured):
        ch.create_draft({})


# ---- details panel data (list + bank evidence in the panel) ----

def _panel_details(c):
    import re
    html = c.get("/ikigai/panel").text
    m = re.search(r'<script type="application/json" id="studio-data">(.*?)</script>', html, re.S)
    assert m, "panel must carry the details data"
    return html, json.loads(m.group(1))


def test_details_cover_list_and_bank(client):
    c, con = client
    c.post("/ikigai/api/ideas/import", json=[idea(k) for k in range(3)])
    c.post("/ikigai/api/refresh")
    vis = c.get("/ikigai/api/state").json()["visible"]
    c.post(f"/ikigai/api/ideas/{vis[0]['id']}/approve")
    c.post(f"/ikigai/api/ideas/{vis[1]['id']}/deny")
    seed = ideas.add_seed(con, "Lighthouse keeper cats")
    html, d = _panel_details(c)
    banked, denied, shown = str(vis[0]["id"]), str(vis[1]["id"]), str(vis[2]["id"])
    assert d[banked]["status"] == "approved" and d[banked]["evidence"]["why_buyer"] == "b"
    assert d[banked]["evidence"]["sources"] == ["Alura"] and d[banked]["decided_at"]
    assert d[shown]["status"] == "shown" and d[shown]["lane"] == "rising"
    assert denied not in d                                    # removed ideas drop out of the panel
    assert d[str(seed)]["source"] == "seed" and d[str(seed)]["evidence"]["sources"] == []
    assert f'class="banked lane-rising" data-id="{banked}"' in html   # bank rows are clickable


def test_detail_view_handles_old_evidence():
    v = ideas.detail_view({"id": 1, "title": "t", "evidence": {"summary": "PLACEHOLDER"}})
    assert v["evidence"] == {"summary": "PLACEHOLDER", "sources": []}
    v = ideas.detail_view({"id": 2, "title": "t", "evidence": {"sources": "one"}})
    assert v["evidence"]["sources"] == ["one"]


def test_details_json_is_script_safe(client):
    c, con = client
    ideas.add_seed(con, "</script><b>x</b>")
    html, d = _panel_details(c)
    assert any(x["title"].startswith("</script>") for x in d.values())


# ---- conversational chat (Claude CLI mocked) ----

def _shown(c, n=3):
    c.post("/ikigai/api/ideas/import", json=[idea(k) for k in range(n)])
    c.post("/ikigai/api/refresh")
    return c.get("/ikigai/api/state").json()["visible"]


def _seeds(con):
    return con.execute("SELECT COUNT(*) FROM ideas WHERE source='seed'").fetchone()[0]


TONY = ("So for now, basically, I just want you to start with the idea that is currently in the idea bank. "
        "As we build that one, we will go through an iterative process that you can learn from.")


def test_plain_text_is_not_a_seed(client, fake):
    c, con = client
    _shown(c)
    fake.reply = "Got it, we'll start with the banked idea."
    j = c.post("/api/chat", json={"text": TONY}).json()
    assert _seeds(con) == 0 and j["reply"].startswith("Got it")
    assert j["messages"][-1]["text"].startswith("Got it")
    # even if the model wrongly asks for a seed, the Portal refuses: Tony didn't ask for one
    fake.reply = 'Sure.\n```json\n{"actions":[{"type":"seed","text":"start with the banked idea"}]}\n```'
    j = c.post("/api/chat", json={"text": TONY}).json()
    assert _seeds(con) == 0 and "Not done" in j["reply"] and "```" not in j["reply"]


def test_explicit_seed_request_creates_one(client, fake):
    c, con = client
    fake.reply = 'Added.\n```json\n{"actions":[{"type":"seed","text":"Lighthouse keeper cats at dusk"}]}\n```'
    j = c.post("/api/chat", json={"text": "Add an idea to the list: lighthouse keeper cats at dusk"}).json()
    assert j["refresh"] and _seeds(con) == 1
    r = con.execute("SELECT * FROM ideas WHERE source='seed'").fetchone()
    assert r["title"] == "Lighthouse keeper cats at dusk" and r["status"] == "shown"


def test_taste_note_saved_not_idea(client, fake, tmp_path):
    c, con = client
    fake.reply = 'Noted.\n```json\n{"actions":[{"type":"taste_note","text":"Start with the banked idea and iterate"}]}\n```'
    j = c.post("/api/chat", json={"text": TONY}).json()
    assert _seeds(con) == 0 and "taste profile" in j["reply"]
    ev = con.execute("SELECT idea_id, action, comment FROM taste_events").fetchall()
    assert [(e["idea_id"], e["action"]) for e in ev] == [(None, "note")]
    p = json.loads((tmp_path / "Taste_Profile.json").read_text())
    assert p["notes"][0]["text"] == "Start with the banked idea and iterate"
    assert "Start with the banked idea" in (tmp_path / "Taste_Profile.md").read_text()


def test_approve_and_deny_actions(client, fake):
    c, con = client
    vis = _shown(c)
    a, b = vis[0]["id"], vis[1]["id"]
    fake.reply = (f'Done.\n```json\n{{"actions":[{{"type":"approve","idea_id":{a}}},'
                  f'{{"type":"deny","idea_id":{b},"reason":"too generic"}}]}}\n```')
    j = c.post("/api/chat", json={"text": f"approve {a}, deny {b}, too generic"}).json()
    assert j["refresh"] and "Approved" in j["reply"] and "Denied" in j["reply"]
    st_ = {r["id"]: r["status"] for r in con.execute("SELECT id, status FROM ideas")}
    assert st_[a] == "approved" and st_[b] == "denied"
    assert con.execute("SELECT comment FROM taste_events WHERE action='comment'").fetchone()[0] == "too generic"


def test_action_validation(client, fake):
    c, con = client
    vis = _shown(c)
    banked = vis[0]["id"]
    c.post(f"/ikigai/api/ideas/{banked}/approve")
    fake.reply = ('Trying.\n```json\n{"actions":[{"type":"approve","idea_id":999},'
                  '{"type":"delete_all"},{"type":"shell","cmd":"rm -rf /"},'
                  f'{{"type":"approve","idea_id":{banked}}},{{"type":"approve","idea_id":"x"}}]}}\n```')
    before = con.execute("SELECT id, status FROM ideas ORDER BY id").fetchall()
    j = c.post("/api/chat", json={"text": "approve them all"}).json()
    assert [tuple(r) for r in con.execute("SELECT id, status FROM ideas ORDER BY id")] == [tuple(r) for r in before]
    assert not j["refresh"]
    rep = j["reply"]
    assert "no idea #999" in rep and "unknown action" in rep and "is approved" in rep and "no idea #x" in rep
    done, refused, changed, _ = assistant.run_actions(con, S, [{"type": "none"}], "hi")
    assert (done, refused, changed) == ([], [], False)


def test_parse_reply():
    t, a = assistant.parse_reply('Sure thing.\n```json\n{"actions":[{"type":"refresh"}]}\n```')
    assert t == "Sure thing." and a == [{"type": "refresh"}]
    t, a = assistant.parse_reply("Just talking, no block.")
    assert t == "Just talking, no block." and a == []
    t, a = assistant.parse_reply('Oops\n```json\n{"actions": [ broken\n```')
    assert a == []
    t, a = assistant.parse_reply('x\n```\n{"actions": "nope"}\n```')
    assert a == [] and t == "x"
    t, a = assistant.parse_reply('Look:\n```json\n{"example": 1}\n```')      # other code blocks stay visible
    assert a == [] and "example" in t
    assert assistant.asked_to_seed("seed: cats") and assistant.asked_to_seed("please add this idea to the list")
    assert not assistant.asked_to_seed(TONY)


def test_cli_timeout_and_failure_fallback(client, fake, monkeypatch):
    c, con = client
    import subprocess
    def slow(*a, **k):
        raise subprocess.TimeoutExpired(cmd="claude", timeout=60)
    monkeypatch.setattr(assistant.subprocess, "run", slow)
    with pytest.raises(assistant.ChatUnavailable):
        assistant.call_claude("hi", S)
    # through the HTTP route: a short plain error, the typed text kept, no crash
    fake.error = assistant.ChatUnavailable("The chat took too long to answer")
    r = c.post("/api/chat", json={"text": "what's on the list?"})
    assert r.status_code == 200
    j = r.json()
    assert "too long" in j["reply"] and j["messages"][-2]["text"] == "what's on the list?"
    # an unexpected crash inside the responder also stays a chat message
    fake.error = RuntimeError("bad")
    assert "saved" in c.post("/api/chat", json={"text": "hello"}).json()["reply"]


def test_call_claude_reads_json_result(monkeypatch):
    seen = {}
    class P:
        returncode, stdout = 0, json.dumps({"is_error": False, "result": "hello Tony"})
    def run(args, **k):
        seen["args"], seen["input"] = args, k["input"]
        return P()
    monkeypatch.setattr(assistant.subprocess, "run", run)
    assert assistant.call_claude("the prompt", S) == "hello Tony"
    args = seen["args"]
    assert "-p" in args and "--safe-mode" in args and args[args.index("--tools") + 1] == ""
    assert "--no-session-persistence" in args and "--strict-mcp-config" in args and seen["input"] == "the prompt"
    P.stdout = json.dumps({"is_error": True, "result": "Not logged in"})
    with pytest.raises(assistant.ChatUnavailable):
        assistant.call_claude("x", S)


def test_prompt_has_snapshot_history_and_selected(client, fake):
    c, con = client
    vis = _shown(c)
    c.post("/api/chat", json={"text": "status"})                       # local, no CLI call
    assert fake.prompts == []
    c.post("/api/chat", json={"text": "what do you think of this one?", "selected_idea_id": vis[1]["id"]})
    p = fake.prompts[-1]
    assert f"#{vis[0]['id']}" in p and "Idea bank" in p and "Taste profile" in p
    assert f"Details panel: #{vis[1]['id']}" in p and "Tony: status" in p
    assert p.rstrip().endswith("what do you think of this one?")


def test_deny_invite_reason_goes_through_cli(client, fake):
    c, con = client
    vis = _shown(c)
    c.post(f"/ikigai/api/ideas/{vis[0]['id']}/deny")
    fake.reply = "Fair, I'll steer away from that."
    j = c.post("/api/chat", json={"text": "Too much like every other print"}).json()
    ev = con.execute("SELECT idea_id, comment FROM taste_events WHERE action='comment'").fetchone()
    assert ev["idea_id"] == vis[0]["id"] and j["reply"].startswith("Fair")
    assert "already saved his new message as the deny reason" in fake.prompts[-1]
    # CLI down: the reason is still saved and acknowledged
    c.post(f"/ikigai/api/ideas/{vis[1]['id']}/deny")
    fake.error = assistant.ChatUnavailable("The chat could not answer just now")
    j = c.post("/api/chat", json={"text": "boring"}).json()
    assert "noted against" in j["reply"]
    assert con.execute("SELECT COUNT(*) FROM taste_events WHERE action='comment'").fetchone()[0] == 2
