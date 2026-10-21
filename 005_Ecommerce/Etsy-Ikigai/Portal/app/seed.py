"""Seed placeholder ideas so the portal is usable before the research job exists."""
from . import ideas
from .db import connect

SAMPLES = [("Sage Japandi Abstract Arcs", "Soft arcs in sage and oat, Japandi living room.", "test", "PLACEHOLDER evidence", 50 - i)
           for i in range(30)]

if __name__ == "__main__":
    con = connect()
    ideas.add_to_pool(con, [dict(title=f"{t} {n}", description=d, lane=l, evidence=e, score=s)
                            for n, (t, d, l, e, s) in enumerate(SAMPLES, 1)])
    print("seeded", len(SAMPLES))
