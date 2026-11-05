"""Pipeline runner. Each step lives in steps.py as a function step(ctx) -> message.
Raise NotConfigured when a tool/credential is missing; the step is marked 'blocked' (with a plain reason)
and the listing stays resumable. Steps are swappable via config/pipeline.json.

`lock` (the shared DB lock) is held only for the step-table writes, never while a step works, so the
dashboard stays responsive during long steps. `stop_after` ends the run after that step (stage 3 stops
after resize). `extra` is merged into the step context (settings, test doubles)."""
import contextlib

from . import steps
from .base import NotConfigured


def run_listing(con, listing_id, config, lock=None, stop_after=None, extra=None):
    lock = lock or contextlib.nullcontext()
    for name in config["steps"]:
        with lock:
            row = con.execute("SELECT status FROM steps WHERE listing_id=? AND name=?", (listing_id, name)).fetchone()
            if row and row["status"] == "done":
                skip = True
            else:
                skip = False
                con.execute("INSERT OR IGNORE INTO steps(listing_id, name) VALUES (?,?)", (listing_id, name))
                con.execute("UPDATE steps SET status='running', message='' WHERE listing_id=? AND name=?",
                            (listing_id, name))
                con.commit()
        if not skip:
            try:
                msg = getattr(steps, name)({"con": con, "listing_id": listing_id, "config": config, **(extra or {})})
                status = "done"
            except NotConfigured as e:
                status, msg = "blocked", str(e)
            except Exception as e:  # noqa: BLE001
                status, msg = "failed", f"Something went wrong: {e}"
            with lock:
                con.execute("UPDATE steps SET status=?, message=? WHERE listing_id=? AND name=?",
                            (status, msg or "", listing_id, name))
                if status != "done" and stop_after:
                    # later steps of this stage would never start: show them as waiting, not queued forever
                    con.execute("UPDATE steps SET status='pending', message=? WHERE listing_id=? AND status='queued'",
                                (f"waiting for {name}", listing_id))
                con.commit()
            if status != "done":
                return status
        if name == stop_after:
            return "done"
    return "done"
