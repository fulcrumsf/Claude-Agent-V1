from conftest import load


def _client(monkeypatch, rl_fixture, tmp_path):
    serve = load("serve")
    for m in (serve.notes.config, serve.thumbs.config, serve.actions.config,
              serve.queue.config, serve.config):
        monkeypatch.setattr(m, "RESOURCE_LIB", str(rl_fixture))
        monkeypatch.setattr(m, "THUMB_CACHE", str(tmp_path / "thumbs"))
        monkeypatch.setattr(m, "DELETE_DIR", str(tmp_path / "delete"))
        monkeypatch.setattr(m, "QUEUE_DIR", str(tmp_path / "rev"))
        monkeypatch.setattr(m, "QUEUE_FILE", str(tmp_path / "rev" / "Review_Queue.md"))
    app = serve.create_app()
    app.testing = True
    return app.test_client()


def test_notes_endpoint_lists_cards(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    data = c.get("/api/notes").get_json()
    titles = [x["title"] for x in data]
    assert "OpenCode" in titles and "Vid" in titles


def test_note_detail_renders_body(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    d = c.get("/api/note", query_string={"path": "Tutorials/Vid.md"}).get_json()
    assert "<iframe" in d["body_html"]
    assert "abcdefghijk" in d["body_html"]


def test_delete_moves_and_updates_index(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    r = c.post("/api/delete", json={"paths": ["Tools/OpenCode.md"]})
    assert r.get_json()["ok"] is True
    assert not (rl_fixture / "Tools" / "OpenCode.md").exists()
    remaining = [x["path"] for x in c.get("/api/notes").get_json()]
    assert "Tools/OpenCode.md" not in remaining


def test_patch_note_writes_fields(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    r = c.patch("/api/note", json={"path": "Tools/MisLabel.md", "title": "Fixed"})
    assert r.get_json()["ok"] is True
    fm, _ = load("notes").parse_note(str(rl_fixture / "Tools" / "MisLabel.md"))
    assert fm["title"] == "Fixed"


def test_comment_and_finalize(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    c.post("/api/comment", json={"path": "Tools/MisLabel.md", "text": "retag please"})
    r = c.post("/api/queue/finalize")
    assert "FINALIZED" in r.get_json()["batch"]


def test_filters_endpoint(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    d = c.get("/api/filters").get_json()
    assert "Tools" in d["folders"]
    assert isinstance(d["top_tags"], list)


def test_index_serves_html(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    r = c.get("/")
    assert r.status_code == 200 and b"<title>" in r.data
