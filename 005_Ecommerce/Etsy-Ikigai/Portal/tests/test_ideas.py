from app import ideas
from app.db import connect


def make(tmp_path, n=15):
    con = connect(tmp_path / "t.db")
    ideas.add_to_pool(con, [dict(title=f"i{k}", description="d", score=k) for k in range(n)])
    return con


def test_fills_ten(tmp_path):
    con = make(tmp_path)
    ideas.fill_visible(con, 10)
    assert con.execute("SELECT COUNT(*) FROM ideas WHERE status='shown'").fetchone()[0] == 10


def test_deny_refills_and_keeps_approved(tmp_path):
    con = make(tmp_path)
    ideas.fill_visible(con, 10)
    a, b = [r[0] for r in con.execute("SELECT id FROM ideas WHERE status='shown' LIMIT 2")]
    ideas.approve(con, a)
    ideas.deny(con, b, 10)
    assert con.execute("SELECT status FROM ideas WHERE id=?", (a,)).fetchone()[0] == "approved"
    assert con.execute("SELECT COUNT(*) FROM ideas WHERE status IN ('shown','approved')").fetchone()[0] == 10
    assert ideas.pool_count(con) == 4


def test_approve_makes_prompt(tmp_path):
    con = make(tmp_path)
    ideas.fill_visible(con, 10)
    i = con.execute("SELECT id FROM ideas WHERE status='shown'").fetchone()[0]
    ideas.approve(con, i)
    assert con.execute("SELECT COUNT(*) FROM prompts").fetchone()[0] == 1


def test_drive_sequence_and_name():
    from app.drive import next_sequence, folder_name
    assert next_sequence(["00083-A", "00120-Pastel Waves", "notes"]) == 121
    assert next_sequence([]) == 1
    assert folder_name(121, " Sage Leaf ") == "00121-Sage Leaf"
