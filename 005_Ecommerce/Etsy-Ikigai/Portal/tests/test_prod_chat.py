"""Studio chat x Production (2026-11-19): slot context, vision, validated slot actions, fix requests for Claude Code."""
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image

from app import assistant, chat as chat_mod, prints, prod_chat, production, studio
from test_prints import approved_idea, env, fake_upscayl, tiny_sizes  # noqa: F401  (fixture reuse)


def _design(env, slot_rec=True):
    c, con, S = env["c"], env["con"], env["S"]
    iid = approved_idea(con)
    c.post(f"/ikigai/api/prints/{iid}/run", json={})
    folder = env["tmp"] / "Designs" / "00121-Book Club Cat" / "03-Etsy Images"
    folder.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (2400, 3000), (200, 40, 40)).save(folder / "11_Room_Office_Modern.jpg")
    Image.new("RGB", (40, 40), (90, 90, 90)).save(folder / "09_Bedroom.jpg")
    if slot_rec:
        lst = prints.listing_for(con, iid)
        rec = prints._record(con, lst["id"])
        production._prod(rec)["slots"]["11"] = {
            "file": "11_Room_Office_Modern.jpg", "room": "Office", "decor": "Modern", "ratio": "4x5",
            "template": "Office/Modern/225742/Office_225742_Template.psd", "source": "library", "state": "done",
            "history": ["11_Room_Office_Modern_v1.jpg"],
            "guard": {"pass": False, "why": ["art covers the frame edge", "white bar on the left side"],
                      "art_area": {"pass": False, "why": ["white bar on the left side"]}}}
        prints._save_record(con, lst["id"], rec)
    hd = env["tmp"] / "Handoffs"
    hd.mkdir(exist_ok=True)
    S["handoffs_dir"] = str(hd)
    return iid, folder, hd


def _hooks(env, spawned=None, notes=None):
    return prod_chat.ProdHooks(env["con"], env["S"], lambda fn, *a: (spawned if spawned is not None else []).append(fn),
                               notify=(notes.append if notes is not None else None))


def test_named_slots_reads_plain_words():
    assert prod_chat.named_slots("slot 11 has a white bar") == [11]
    assert prod_chat.named_slots("slots 11 and 12, also slot #3") == [11, 12, 3]
    assert prod_chat.named_slots("the 11x14 print looks fine") == []


def test_snapshot_has_slot_file_template_guard_gate_checker_history_and_approval(env):
    iid, _, _ = _design(env)
    snap = assistant.snapshot(env["con"], env["S"], prod_idea_id=iid, open_slot=11, attached=[(11, "11_Room_Office_Modern.jpg")])
    line = next(ln for ln in snap.splitlines() if ln.startswith("- slot 11"))
    for want in ("11_Room_Office_Modern.jpg", "in the listing folder, pending", "Office/Modern/225742",
                 "accuracy guard: FAIL (art covers the frame edge)", "art-area gate: FAIL (white bar on the left side)",
                 "checker unchecked", "older images: 11_Room_Office_Modern_v1.jpg"):
        assert want in line, want
    assert "- slot 09" in snap and "Tony pointed at slot 11" in snap and "Attached image 1 = slot 11" in snap


def test_slot_images_attach_open_and_named_slots_resized_max_two(env):
    iid, _, _ = _design(env)
    imgs, att = prod_chat.slot_images(env["con"], env["S"], iid, "compare slot 9 with slot 11 and slot 3", open_slot=11)
    assert [a[0] for a in att] == [11, 9] and len(imgs) == 2
    import base64, io
    im = Image.open(io.BytesIO(base64.b64decode(imgs[0]["data"])))
    assert max(im.size) == prod_chat.MAX_SIDE and imgs[0]["media_type"] == "image/jpeg"
    assert prod_chat.slot_images(env["con"], env["S"], iid, "hello") == ([], [])


def test_stream_json_message_carries_image_blocks_then_text():
    m = json.loads(assistant.stream_message("hi", [{"media_type": "image/jpeg", "data": "QUJD"}]))
    assert [b["type"] for b in m["message"]["content"]] == ["image", "text"]
    assert "--input-format" in assistant.cli_args({}, stream=True) and "--input-format" not in assistant.cli_args({})
    out = assistant.stream_result('{"type":"system"}\nnot json\n{"type":"result","result":"ok","is_error":false}\n')
    assert out["result"] == "ok"


def test_unknown_design_and_slot_are_refused(env):
    iid, _, _ = _design(env)
    h = _hooks(env)
    con, S = env["con"], env["S"]
    for a in ({"type": "slot_decide", "idea_id": iid, "slot": 12, "decision": "approve"},
              {"type": "slot_rerender", "idea_id": 999, "slot": 11},
              {"type": "fix_request", "slot": "eleven"},
              {"type": "check_template", "idea_id": iid, "slot": 4}):
        done, refused, _, _ = assistant.run_actions(con, S, [a], "x", prod_hooks=h, prod_idea_id=iid)
        assert not done and refused, a
    assert "no slot 12" in assistant.run_actions(con, S, [{"type": "slot_decide", "idea_id": iid, "slot": 12,
                                                          "decision": "approve"}], "x", prod_hooks=h)[1][0]
    _, refused, _, _ = assistant.run_actions(con, S, [{"type": "slot_rerender", "slot": 11}], "x")
    assert "not available" in refused[0]                        # no hooks: refused, nothing runs


def test_slot_decide_uses_production_decide_and_defaults_to_open_design(env):
    iid, folder, _ = _design(env)
    h = _hooks(env)
    done, refused, changed, _ = assistant.run_actions(env["con"], env["S"], [{"type": "slot_decide", "slot": 11,
                                                                              "decision": "deny"}], "deny it", prod_hooks=h,
                                                      prod_idea_id=iid)
    assert changed and not refused and "Denied slot 11" in done[0]
    assert not (folder / "11_Room_Office_Modern.jpg").exists() and (folder / "Archive" / "11_Room_Office_Modern.jpg").exists()
    assistant.run_actions(env["con"], env["S"], [{"type": "slot_decide", "slot": 11, "decision": "undo"}], "undo",
                          prod_hooks=h, prod_idea_id=iid)
    assert (folder / "11_Room_Office_Modern.jpg").exists()
    _, refused, _, _ = assistant.run_actions(env["con"], env["S"], [{"type": "slot_decide", "slot": 11, "decision": "maybe"}],
                                             "x", prod_hooks=h, prod_idea_id=iid)
    assert "approve, deny or undo" in refused[0]


def test_rerender_only_with_a_library_template_and_check_needs_a_template(env, monkeypatch):
    iid, _, _ = _design(env)
    spawned = []
    h = _hooks(env, spawned)
    _, refused, _, _ = assistant.run_actions(env["con"], env["S"], [{"type": "slot_rerender", "slot": 11}], "redo",
                                             prod_hooks=h, prod_idea_id=iid)
    assert "not in the library" in refused[0]
    rel = "Office/Modern/225742/Office_225742_Template.psd"
    monkeypatch.setattr(production.stp, "library_templates", lambda s=None: [{"rel": rel}])
    claimed = []
    monkeypatch.setattr(production, "start_slot", lambda con, s, i, slot, t: claimed.append((i, slot, t)))
    done, refused, _, _ = assistant.run_actions(env["con"], env["S"], [{"type": "slot_rerender", "slot": 11}], "redo",
                                                prod_hooks=h, prod_idea_id=iid)
    assert not refused and "free" in done[0] and claimed == [(iid, 11, rel)]
    h.flush()
    assert spawned == [production.run_slot]                     # current template only, started after the lock
    _, refused, _, _ = assistant.run_actions(env["con"], env["S"], [{"type": "check_template", "slot": 9}], "check",
                                             prod_hooks=h, prod_idea_id=iid)
    assert "no template" in refused[0]


def test_offer_regenerate_never_spends_it_only_returns_a_button(env, monkeypatch):
    iid, _, _ = _design(env)
    h = _hooks(env)
    monkeypatch.setattr(production, "start_slot", lambda *a, **k: (_ for _ in ()).throw(AssertionError("spent")))
    done, refused, _, _ = assistant.run_actions(env["con"], env["S"], [{"type": "offer_regenerate", "slot": 11}],
                                                "make a new one", prod_hooks=h, prod_idea_id=iid)
    assert not refused and "button below" in done[0]
    assert h.buttons and h.buttons[0]["url"] == f"/ikigai/api/production/{iid}/slots/11/generate"


def test_fix_request_file_shape_and_waiting_row(env):
    iid, folder, hd = _design(env)
    h = _hooks(env)
    words = 'the shadow on slot 11 goes the wrong way, "fix it"'
    done, refused, _, _ = assistant.run_actions(env["con"], env["S"], [{"type": "fix_request", "slot": 11,
                                                                        "summary": "Shadow points left."}], words,
                                                prod_hooks=h, prod_idea_id=iid)
    assert not refused and "Claude Code" in done[0]
    f = hd / f"{__import__('datetime').date.today():%Y-%m-%d}_Fix-Request_Portal_Slot-11.md"
    t = f.read_text()
    for want in ("status: waiting", f"idea_id: {iid}", "slot: 11", "template: Office/Modern/225742",
                 f"> {words}", "Shadow points left.", str(folder / "11_Room_Office_Modern.jpg"),
                 "Art-area gate: FAIL (white bar on the left side)", "Template checker: unchecked",
                 "11_Room_Office_Modern_v1.jpg"):
        assert want in t, want
    assistant.run_actions(env["con"], env["S"], [{"type": "fix_request", "slot": 11}], "again", prod_hooks=h,
                          prod_idea_id=iid)
    assert f.with_name(f.stem + "_2.md").exists()               # never overwrites
    rows = prod_chat.fix_requests(env["S"], iid)
    assert len(rows) == 2 and rows[0]["slot"] == 11
    assert "WAITING FOR CLAUDE CODE" in assistant.snapshot(env["con"], env["S"], prod_idea_id=iid)
    f.write_text(t.replace("status: waiting", "status: done"))
    assert len(prod_chat.fix_requests(env["S"], iid)) == 1


def test_fix_request_refused_when_handoffs_folder_missing(env):
    iid, _, hd = _design(env)
    env["S"]["handoffs_dir"] = str(hd / "nope")
    _, refused, _, _ = assistant.run_actions(env["con"], env["S"], [{"type": "fix_request", "slot": 11}], "x",
                                             prod_hooks=_hooks(env), prod_idea_id=iid)
    assert "Handoffs folder is missing" in refused[0] and not (hd / "nope").exists()


def test_chat_endpoint_sends_slot_context_and_images_to_the_model(tmp_path, monkeypatch):
    monkeypatch.setattr(prints, "sizes", tiny_sizes)
    from app.db import connect
    con = connect(tmp_path / "t.db")
    (tmp_path / "Designs").mkdir()
    S = {"designs_root": str(tmp_path / "Designs"), "design_seq_floor": 120, "price_default": 6.5,
         "upscale_model": "remacri-4x", "template_checks_path": str(tmp_path / "tc.json")}
    seen = {}

    def ask(prompt, settings=None, images=None):
        seen.update(prompt=prompt, images=images)
        return 'Sending it on.\n```json\n{"actions": [{"type": "fix_request", "slot": 11, "summary": "bar"}]}\n```'
    app = FastAPI()
    chat = chat_mod.Chat(con)
    app.include_router(chat_mod.router(chat))
    studio.mount(app, con, S, chat, ask=ask, spawn=lambda fn, *a: fn(*a), upscayl=fake_upscayl([]))
    c = TestClient(app)
    iid, _, hd = _design({"c": c, "con": con, "S": S, "tmp": tmp_path})
    j = c.post("/api/chat", json={"text": "this one has a white bar", "prod_idea_id": iid, "prod_slot": 11}).json()
    assert seen["images"] and len(seen["images"]) == 1 and "Tony pointed at slot 11" in seen["prompt"]
    assert "Sent to Claude Code" in j["reply"] and list(hd.glob("*_Fix-Request_Portal_Slot-11.md"))
    pan = c.get(f"/ikigai/api/production/{iid}/panel").json()
    assert pan["fix_requests"][0]["slot"] == 11
