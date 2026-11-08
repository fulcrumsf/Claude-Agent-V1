"""Production tab: only the new listing images are listed, decisions stick, fixed images are never shown."""
from PIL import Image

from test_prints import approved_idea, env  # noqa: F401  (fixture reuse)


def _make(env, iid):
    c = env["c"]
    c.post(f"/ikigai/api/prints/{iid}/run", json={})
    folder = env["tmp"] / "Designs" / "00121-Book Club Cat" / "03-Etsy Images"
    folder.mkdir(parents=True)
    for n in ("01_Main_Mockup.png", "08_Living_Room.jpg", "03_Instant_Download.png", "notes.txt"):
        Image.new("RGB", (40, 40), (90, 90, 90)).save(folder / n) if n.endswith(("png", "jpg")) else (folder / n).write_text("x")
    return folder


def test_lists_only_new_images_and_decisions_stick(env):
    c, iid = env["c"], approved_idea(env["con"])
    _make(env, iid)
    d = c.get("/ikigai/api/production").json()["items"][0]
    assert [i["file"] for i in d["images"]] == ["01_Main_Mockup.png", "08_Living_Room.jpg"]
    assert d["counts"] == {"approved": 0, "denied": 0, "pending": 2}
    r = c.post(f"/ikigai/api/production/{iid}/images/08_Living_Room.jpg", json={"decision": "denied"}).json()
    assert r["counts"]["denied"] == 1
    c.post(f"/ikigai/api/production/{iid}/images/01_Main_Mockup.png", json={"decision": "approved"})
    d = c.get("/ikigai/api/production").json()["items"][0]
    assert d["counts"] == {"approved": 1, "denied": 1, "pending": 0}
    r = c.post(f"/ikigai/api/production/{iid}/images/08_Living_Room.jpg", json={"decision": "pending"}).json()
    assert r["counts"]["pending"] == 1


def test_rejects_fixed_unknown_and_bad_decisions_and_serves_files(env):
    c, iid = env["c"], approved_idea(env["con"])
    _make(env, iid)
    url = f"/ikigai/api/production/{iid}/images/"
    assert c.post(url + "03_Instant_Download.png", json={"decision": "approved"}).status_code == 404
    assert c.post(url + "nope.jpg", json={"decision": "approved"}).status_code == 404
    assert c.post(url + "08_Living_Room.jpg", json={"decision": "maybe"}).status_code == 422
    assert c.get(f"/ikigai/api/production/{iid}/file/08_Living_Room.jpg").status_code == 200
    assert c.get(f"/ikigai/api/production/{iid}/file/..%2Fx.jpg").status_code == 404
