"""Pipeline runner. Each step lives in steps.py as a function step(ctx) -> message.
Raise NotConfigured when a tool/credential is missing; the step is marked 'blocked'
and the listing stays resumable. Steps are swappable via config/pipeline.json."""
from . import steps
from .base import NotConfigured


def run_listing(con, listing_id, config):
    for name in config["steps"]:
        row = con.execute("SELECT status FROM steps WHERE listing_id=? AND name=?", (listing_id, name)).fetchone()
        if row and row["status"] == "done":
            continue
        con.execute("INSERT OR IGNORE INTO steps(listing_id, name) VALUES (?,?)", (listing_id, name))
        try:
            con.execute("UPDATE steps SET status='running' WHERE listing_id=? AND name=?", (listing_id, name))
            msg = getattr(steps, name)({"con": con, "listing_id": listing_id, "config": config})
            status = "done"
        except NotConfigured as e:
            status, msg = "blocked", str(e)
        except Exception as e:  # noqa: BLE001
            status, msg = "failed", repr(e)
        con.execute("UPDATE steps SET status=?, message=? WHERE listing_id=? AND name=?",
                    (status, msg or "", listing_id, name))
        con.commit()
        if status != "done":
            return status
    return "done"
