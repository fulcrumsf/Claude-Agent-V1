from conftest import load


def _q(monkeypatch, tmp_path):
    queue = load("queue")
    monkeypatch.setattr(queue.config, "QUEUE_DIR", str(tmp_path))
    monkeypatch.setattr(queue.config, "QUEUE_FILE", str(tmp_path / "Review_Queue.md"))
    return queue


def test_add_comment_creates_batch_and_entry(monkeypatch, tmp_path):
    q = _q(monkeypatch, tmp_path)
    q.add_comment("Tools/MisLabel.md", "should be a github repo not a plugin")
    txt = open(q.config.QUEUE_FILE).read()
    assert "## Batch — open" in txt
    assert "- [ ] COMMENT  Tools/MisLabel.md" in txt
    assert "should be a github repo" in txt


def test_log_delete_entry(monkeypatch, tmp_path):
    q = _q(monkeypatch, tmp_path)
    q.log_delete("Research/Old.md")
    txt = open(q.config.QUEUE_FILE).read()
    assert "DELETE   Research/Old.md" in txt


def test_finalize_seals_and_reopens(monkeypatch, tmp_path):
    q = _q(monkeypatch, tmp_path)
    q.add_comment("A.md", "x")
    q.log_delete("B.md")
    sealed = q.finalize()
    txt = open(q.config.QUEUE_FILE).read()
    assert "FINALIZED" in txt and "(1 comments, 1 deletes)" in txt
    assert txt.count("## Batch — open") == 1          # a fresh one was opened
    assert "COMMENT  A.md" in sealed
