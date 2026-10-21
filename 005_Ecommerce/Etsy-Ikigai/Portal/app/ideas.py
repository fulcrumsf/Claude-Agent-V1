"""Idea list logic: keep N ideas visible, refill from the pool on deny."""


def fill_visible(con, n):
    shown = con.execute("SELECT COUNT(*) FROM ideas WHERE status IN ('shown','approved')").fetchone()[0]
    need = n - shown
    if need <= 0:
        return 0
    ids = [r[0] for r in con.execute(
        "SELECT id FROM ideas WHERE status='pool' ORDER BY score DESC, id LIMIT ?", (need,))]
    con.executemany("UPDATE ideas SET status='shown' WHERE id=?", [(i,) for i in ids])
    con.commit()
    return len(ids)


def deny(con, idea_id, n):
    con.execute("UPDATE ideas SET status='denied' WHERE id=?", (idea_id,))
    con.commit()
    return fill_visible(con, n)


def approve(con, idea_id):
    con.execute("UPDATE ideas SET status='approved' WHERE id=?", (idea_id,))
    row = con.execute("SELECT title, description FROM ideas WHERE id=?", (idea_id,)).fetchone()
    # TODO: replace with a model-written prompt using the Ikigai style tokens.
    prompt = f"{row['title']}. {row['description']} Abstract, Japandi, print-ready wall art, no text."
    con.execute("INSERT INTO prompts(idea_id, text) VALUES (?,?)", (idea_id, prompt))
    con.commit()


def pool_count(con):
    return con.execute("SELECT COUNT(*) FROM ideas WHERE status='pool'").fetchone()[0]


def add_to_pool(con, items):
    """items: dicts with title, description, lane, evidence, score. Used by the research job."""
    con.executemany(
        "INSERT INTO ideas(title, description, lane, evidence, score) VALUES (?,?,?,?,?)",
        [(i["title"], i["description"], i.get("lane", "test"), i.get("evidence", ""), i.get("score", 0)) for i in items])
    con.commit()
