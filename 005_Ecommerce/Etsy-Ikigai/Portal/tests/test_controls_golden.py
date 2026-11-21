"""Golden locks for the controls addendum (Pipeline_Docs/Slot_Set_Planner_Controls_Addendum.md I.1), written BEFORE any
behaviour changed: the kie.ai request bodies of the three existing art engines and of the Nano Banana Pro room scene,
the realism reference clause and the pv2 prompt at the default closeness (60 = "balanced") stay byte-identical."""
import hashlib
import json
from pathlib import Path

import httpx
import pytest

from app import engines, kie_edit, scene_templates as stp, slot_planner as sp
from test_slot_planner_realism import b2

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 20
ART_BODIES = {   # sha1 of the createTask body bytes, 2026-11-21
    "gpt-image-2": "b815bff3486cb0e33da3188183ae16c7becdca0f",
    "nano-banana-2": "b39b39373c7d73a38807e0424d76491ff041f172",
    "nano-banana-pro": "e206a92646d607a11be4fd1bd1a4a7a48942959c"}
NBPRO_BODY = {False: "8e500b7307df288702e8acf8e6784f2a5cf7284a", True: "095a10485b6909c749ea389bd54ce074832fa1ed"}
PV2 = {"with_light": ("04bdfd34f1748cbee3be54e738008edfe05402a9", "da844d803b143bb153774f9a596e39fac61cd3a0"),
       "own_light": ("6d98f88257893a66c2429bb41c69d3721e30a233", "e9850f4013035991c26378c86021edae973692ca")}
REF_CLAUSE_SHA = ("f37ceae7642d0b4d68e7fec8aee71a04668bba32", "9b8796f652f672eeaf87376838fc37a93e6e7d47")


def _sha(b):
    return hashlib.sha1(b if isinstance(b, bytes) else b.encode()).hexdigest()


def _kie_handler(seen):
    def handler(req):
        seen.append(req)
        if req.url.path.endswith("/credit"):
            return httpx.Response(200, json={"code": 200, "data": 100.0})
        if req.url.path.endswith("/createTask"):
            return httpx.Response(200, json={"code": 200, "data": {"taskId": "t1"}})
        if req.url.path.endswith("/recordInfo"):
            return httpx.Response(200, json={"code": 200, "data": {"state": "success", "resultJson": json.dumps(
                {"resultUrls": ["https://x/img.png"]})}})
        return httpx.Response(200, content=PNG)
    return handler


@pytest.mark.parametrize("eid", sorted(ART_BODIES))
def test_existing_art_engines_send_the_same_kie_body(eid, tmp_path, monkeypatch):
    monkeypatch.setenv("KIE_API_KEY", "test-key")
    seen = []
    ad = engines.KieAdapter(engines.get_engine(eid), poll_s=0,
                            client=httpx.Client(transport=httpx.MockTransport(_kie_handler(seen))))
    out = ad.generate("a painting", tmp_path / "a.png")
    body = next(r for r in seen if r.url.path.endswith("/createTask")).content
    assert _sha(body) == ART_BODIES[eid]
    assert out["path"].read_bytes() == PNG                     # a PNG answer is saved byte for byte


@pytest.mark.parametrize("with_ref", [False, True])
def test_nbpro_room_scene_sends_the_same_kie_body(with_ref, tmp_path, monkeypatch):
    monkeypatch.setenv("KIE_API_KEY", "test-key")
    seen = []
    real = httpx.Client
    monkeypatch.setattr(kie_edit.httpx, "Client",
                        lambda timeout=60: real(transport=httpx.MockTransport(_kie_handler(seen))))
    monkeypatch.setattr(kie_edit, "upload", lambda c, p: "https://up/" + Path(p).name)
    kie_edit.generate("nbpro", str(tmp_path / "s.png"), "a room", "4:3", "2K",
                      ref_imgs=("ref.png",) if with_ref else (), poll=0)
    body = next(r for r in seen if r.url.path.endswith("/createTask")).content
    assert _sha(body) == NBPRO_BODY[with_ref]


def test_nbpro_generate_scene_calls_the_generator_exactly_as_before(tmp_path):
    calls = []

    def gen(*a, **kw):
        calls.append((a, kw))
        return {"out": a[1], "model": "nano-banana-pro", "task": "t", "s": 1, "credits": 18, "left": 1}
    s = {"room_scene_engine": "nbpro"}
    stp.generate_scene("p", tmp_path / "s.png", s, gen)
    stp.generate_scene("p", tmp_path / "s.png", s, gen, ref_imgs=[tmp_path / "r.png"])
    assert calls[0] == (("nbpro", str(tmp_path / "s.png"), "p", "4:3", "2K"), {})
    assert calls[1] == (("nbpro", str(tmp_path / "s.png"), "p", "4:3", "2K"), {"ref_imgs": [str(tmp_path / "r.png")]})


@pytest.mark.parametrize("kind", sorted(PV2))
def test_pv2_prompt_at_the_default_closeness_is_the_realism_prompt(kind):
    b = b2() if kind == "with_light" else b2(light_type="north_light_even")
    assert b["lint"]["pass"]
    assert _sha(sp.assemble(b)) == PV2[kind][0]
    assert _sha(sp.assemble(b, ref=False)) == PV2[kind][1]


def test_realism_reference_clause_is_locked():
    assert (_sha(sp.REF_CLAUSE), _sha(sp.REF_CLAUSE_NO_LIGHT)) == REF_CLAUSE_SHA
    assert sp.REF_CLAUSE.startswith("Image 1 is a photograph of a different room, given only as a photography reference.")
