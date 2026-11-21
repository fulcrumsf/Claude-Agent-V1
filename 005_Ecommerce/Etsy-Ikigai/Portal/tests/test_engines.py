"""Engines v2 (controls addendum D.6): request bodies per provider and use, aspect mapping, poll states, WebP -> PNG,
no resubmit after an unclear failure, fallback only on a clear refusal, hidden engine, default, price labels, the
fal art round without a balance check. All HTTP is a stub transport: no credits, no dollars."""
import io
import json

import httpx
import pytest
from PIL import Image

from app import art, engines
from app.db import connect
from test_art import FakeWriter, S, banked

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 20


def webp_bytes():
    b = io.BytesIO()
    Image.new("RGB", (6, 9), (200, 100, 50)).save(b, format="WEBP")
    return b.getvalue()


@pytest.fixture(autouse=True)
def keys(monkeypatch):
    for k in ("KIE_API_KEY", "FAL_AI_API_KEY", "WAVESPEED_API_KEY"):
        monkeypatch.setenv(k, "test-key")


class Stub:
    """A stub transport that records requests; routes by host + path."""

    def __init__(self, fal_status=("IN_QUEUE", "COMPLETED"), ws_status=("processing", "completed"), image=PNG,
                 fal_submit=200, ws_submit=200, fal_network=False):
        self.seen, self.fal_status, self.ws_status = [], list(fal_status), list(ws_status)
        self.image, self.fal_submit, self.ws_submit, self.fal_network = image, fal_submit, ws_submit, fal_network

    def __call__(self, req):
        self.seen.append(req)
        host, path = req.url.host, req.url.path
        if host == "api.kie.ai":
            if path.endswith("/credit"):
                return httpx.Response(200, json={"code": 200, "data": 100.0})
            if path.endswith("/createTask"):
                return httpx.Response(200, json={"code": 200, "data": {"taskId": "k1"}})
            return httpx.Response(200, json={"code": 200, "data": {"state": "success", "resultJson": json.dumps(
                {"resultUrls": ["https://files/x.png"]})}})
        if host == "queue.fal.run":
            if req.method == "POST":
                if self.fal_network:
                    raise httpx.ConnectError("boom")
                if self.fal_submit != 200:
                    return httpx.Response(self.fal_submit, json={"detail": "bad input"})
                return httpx.Response(200, json={"request_id": "f1", "status_url": "https://queue.fal.run/s/f1",
                                                 "response_url": "https://queue.fal.run/r/f1"})
            if "/s/" in path:
                return httpx.Response(200, json={"status": self.fal_status.pop(0) if self.fal_status else "COMPLETED"})
            return httpx.Response(200, json={"images": [{"url": "https://files/y.webp"}]})
        if host == "api.wavespeed.ai":
            if req.method == "POST":
                if self.ws_submit != 200:
                    return httpx.Response(self.ws_submit, json={"message": "nope"})
                return httpx.Response(200, json={"data": {"id": "w1"}})
            if path.endswith("/balance"):
                return httpx.Response(200, json={"data": {"balance": 3.5}})
            st = self.ws_status.pop(0) if self.ws_status else "completed"
            return httpx.Response(200, json={"data": {"status": st, "outputs": ["https://files/z.png"],
                                                      "error": "x" if st != "completed" else ""}})
        return httpx.Response(200, content=self.image)

    def posts(self):
        return [r for r in self.seen if r.method == "POST"]


def ad(eid, stub, use="art", refs=False):
    return engines.adapter_for(eid, {"art_poll_s": 0}, use=use, with_refs=refs,
                               client=httpx.Client(transport=httpx.MockTransport(stub)))


def body(req):
    return json.loads(req.content)


# ---------- request bodies ----------

def test_gpt_image_2_6_art_and_room_bodies(tmp_path):
    st = Stub()
    ad("gpt-image-2-6", st).generate("p", tmp_path / "a.png", "2:3", "1K")
    assert body(st.posts()[0]) == {"model": "gpt-image-2-6/flare-text-to-image", "input": {
        "prompt": "p", "aspect_ratio": "2:3", "resolution": "1K", "quality": "high", "output_format": "png"}}
    st = Stub()
    res = ad("gpt-image-2-6", st, use="room").generate("p", tmp_path / "r.png", "4:3", "2K")
    assert body(st.posts()[0])["input"] == {"prompt": "p", "aspect_ratio": "4:3", "resolution": "2K",
                                            "quality": "medium", "output_format": "png"}
    assert res["measured"] and res["credits"] == 0.0 and res["provider"] == "kie"     # balance difference


def test_ideogram_maps_the_aspect_and_adds_the_room_negative_prompt(tmp_path):
    st = Stub()
    ad("ideogram-3", st).generate("p", tmp_path / "a.png", "2:3", "1K")
    assert body(st.posts()[0]) == {"model": "ideogram/v3-text-to-image", "input": {
        "prompt": "p", "image_size": "portrait_4_3", "rendering_speed": "QUALITY", "style": "AUTO",
        "expand_prompt": False}}
    st = Stub()
    ad("ideogram-3", st, use="room").generate("p", tmp_path / "r.png", "4:3", "2K")
    inp = body(st.posts()[0])["input"]
    assert inp["image_size"] == "landscape_4_3" and "watermark" in inp["negative_prompt"]


def test_recraft_on_fal_custom_size_queue_flow_and_webp_to_png(tmp_path):
    st = Stub(image=webp_bytes())
    res = ad("recraft-4-1", st).generate("p", tmp_path / "a.png", "2:3", "1K")
    post = st.posts()[0]
    assert str(post.url) == "https://queue.fal.run/fal-ai/recraft/v4.1/text-to-image"
    assert post.headers["Authorization"] == "Key test-key"
    assert body(post) == {"prompt": "p", "image_size": {"width": 1024, "height": 1536}}
    assert res["path"].suffix == ".png" and res["path"].read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert res["provider"] == "fal" and res["usd"] == 0.035 and res["credits"] == 7.0 and not res["measured"]


def test_flux_3_art_on_fal_and_rooms_on_wavespeed_or_fal_edit(tmp_path):
    st = Stub()
    ad("flux-3", st).generate("p", tmp_path / "a.png", "2:3", "1K")
    assert str(st.posts()[0].url).endswith("/blackforestlabs/flux-3/text-to-image")
    assert body(st.posts()[0]) == {"prompt": "p", "aspect_ratio": "2:3", "resolution": "1k", "output_format": "png",
                                   "enable_prompt_expansion": False}
    st = Stub()
    r = ad("flux-3", st, use="room").generate("p", tmp_path / "r.png", "4:3", "2K")
    post = st.posts()[0]
    assert str(post.url) == "https://api.wavespeed.ai/api/v3/black-forest-labs/flux-3/text-to-image"
    assert post.headers["Authorization"] == "Bearer test-key"
    assert body(post) == {"prompt": "p", "aspect_ratio": "4:3", "resolution": "2k", "output_format": "png"}
    assert r["usd"] == 0.10 and r["provider"] == "wavespeed"
    ref = tmp_path / "ref.png"
    Image.new("RGB", (300, 300), (1, 2, 3)).save(ref)
    st = Stub()
    r = ad("flux-3", st, use="room", refs=True).generate("p", tmp_path / "r2.png", "4:3", "2K", refs=[ref])
    b = body(st.posts()[0])
    assert str(st.posts()[0].url).endswith("/blackforestlabs/flux-3/edit-image")
    assert b["image_urls"][0].startswith("data:image/png;base64,") and r["usd"] == 0.15


@pytest.mark.parametrize("state", ["failed", "cancelled", "timeout", "deleted"])
def test_every_wavespeed_terminal_failure_is_a_plain_error(state, tmp_path):
    st = Stub(ws_status=("processing", state))
    with pytest.raises(engines.EngineError, match=state):
        ad("flux-3", st, use="room").generate("p", tmp_path / "r.png", "4:3", "2K")
    assert len(st.posts()) == 1


def test_no_resubmit_after_an_unclear_failure_and_no_fallback(tmp_path):
    st = Stub(fal_network=True)
    with pytest.raises(engines.EngineError, match="not resubmitted"):
        ad("flux-3", st).generate("p", tmp_path / "a.png")
    assert len([r for r in st.seen if r.method == "POST"]) == 1           # one POST, nothing on WaveSpeed


def test_fallback_only_on_a_clear_refusal_and_never_dearer(tmp_path):
    st = Stub(fal_submit=422)
    r = ad("flux-3", st).generate("p", tmp_path / "a.png")              # WaveSpeed Flux 3 1k = $0.048 <= shown
    assert r["provider"] == "wavespeed" and r["fallback_from"] == "fal"
    assert [p.url.host for p in st.posts()] == ["queue.fal.run", "api.wavespeed.ai"]
    st = Stub(fal_submit=422)
    with pytest.raises(engines.EngineError, match="refused"):            # Recraft on WaveSpeed costs more: no fallback
        ad("recraft-4-1", st).generate("p", tmp_path / "b.png")
    assert len(st.posts()) == 1


# ---------- list, default, labels ----------

def test_hidden_engine_resolves_default_and_price_labels():
    rows = engines.list_engines()
    ids = [e["id"] for e in rows]
    assert ids == ["gpt-image-2-6", "ideogram-3", "recraft-4-1", "flux-3", "nano-banana-2", "nano-banana-pro"]
    assert "gpt-image-2" not in ids and engines.get_engine("gpt-image-2")["label"] == "GPT Image 2"
    assert next(e for e in rows if e["default"])["id"] == "gpt-image-2-6"
    lab = {e["id"]: e["price_label"] for e in rows}
    assert lab["gpt-image-2-6"] == "≈34 cr est. ($0.17)"
    assert lab["ideogram-3"] == "10 cr ($0.05)"
    assert lab["recraft-4-1"] == "$0.035 (≈7 cr) · fal"
    assert lab["nano-banana-pro"] == "18 cr ($0.09)"
    for c in (31, 30, 32):
        engines.record_cost("gpt-image-2-6", "art", c)
    assert engines.get_engine("gpt-image-2-6")["price_label"] == "31 cr measured ($0.15)"


def test_engine_test_cli_plans_without_spending():
    plan = engines.test_plan(["gpt-image-2-6", "ideogram-3", "recraft-4-1", "flux-3"])
    assert 60 <= plan["upper_credits"] <= 62 and plan["upper_usd"] < 0.32


def test_run_tests_records_status_with_a_stub_adapter(tmp_path):
    class A:
        provider = "fal"

        def generate(self, prompt, out, aspect, res):
            Image.new("RGB", (683, 1024)).save(out)
            return {"path": out, "credits": 7.0}
    r = engines.run_tests(["recraft-4-1"], adapter=lambda i: A(), out_dir=tmp_path, log=lambda *_: None)
    assert r["recraft-4-1"]["ok"] and r["recraft-4-1"]["size"] == [683, 1024]
    assert engines.get_engine("recraft-4-1")["tested"]


def test_room_engines_gate_defaults_and_transitions():
    rows = {e["id"]: e for e in engines.room_engines()}
    assert rows["nano-banana-pro"]["gate"] == "trusted" and rows["nano-banana-pro"]["takes_ref"]
    assert rows["flux-3"]["gate"] == "untested" and not rows["flux-3"]["takes_ref"]      # guide_unverified
    assert not rows["gpt-image-2-6"]["takes_ref"] and rows["ideogram-3"]["credits"] == 10
    assert engines.scene_engine_id("nbpro") == engines.scene_engine_id("nano-banana-pro") == "nano-banana-pro"
    assert engines.record_room_check("flux-3", True) == "passed_1"
    assert engines.record_room_check("flux-3", True) == "trusted"
    assert engines.record_room_check("ideogram-3", False) == "suspect"
    assert engines.record_room_check("ideogram-3", False) == "failed"


# ---------- the art round on a fal engine ----------

class FalFake:
    def __init__(self):
        self.calls = 0

    def balance(self):
        return {"amount": None, "unit": "usd"}

    def credits(self):
        raise AssertionError("no credit check on fal")

    def generate(self, prompt, out_path, aspect_ratio="2:3", resolution="1K", on_task=None):
        self.calls += 1
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(PNG)
        return {"task_id": "f", "path": out_path}


def test_art_round_with_a_fal_engine_skips_the_balance_and_records_est_cost(tmp_path):
    con = connect(tmp_path / "t.db")
    i = banked(con)
    fake = FalFake()
    rid = art.start_round(con, S, i, ["flat_poster"], engine_id="recraft-4-1")
    art.run_round(con, S, rid, FakeWriter(), lambda e: fake)
    r = art.idea_art(con, i)["rounds"][0]
    assert r["status"] == "done" and fake.calls == 4
    assert r["credits_spent"] == 28.0 and r["credits_est"] and r["engine_label"] == "Recraft V4.1"
