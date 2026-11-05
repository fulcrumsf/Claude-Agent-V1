"""Idea pool logic (stage 1 of the funnel).

Statuses: pool = pending (imported, not on screen yet), shown = visible list, approved = idea bank,
denied = gone from the list. The hard cap counts pool + shown together.

Weekly refresh ADDS up to `batch` pending ideas to the visible list; it never replaces what is there.
Research imports stop at the cap; approving or denying frees room and the next research run tops back up.
Seeds typed by Tony go straight onto the visible list (source='seed').
"""
import json
from datetime import datetime, timezone

from . import taste
from .db import get_meta, set_meta

LANES = ("rising", "steady", "test")
LANE_ALIASES = {"proven": "steady", "trend": "rising", "trending": "rising", "gap": "test"}
EVIDENCE_KEYS = ("why_buyer", "why_now", "competitors", "warning", "sources")
DEFAULTS = {"idea_cap": 100, "refresh_batch": 10, "refresh_days": 7, "visible_ideas": 10, "pool_low_warning": 10}


def cfg(settings, key):
    return (settings or {}).get(key, DEFAULTS[key])


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ---------- normalising ----------

def norm_lane(lane):
    lane = (lane or "test").strip().lower()
    lane = LANE_ALIASES.get(lane, lane)
    if lane not in LANES:
        raise ValueError(f"lane must be one of {LANES}, got {lane!r}")
    return lane


def norm_evidence(ev):
    """Structured evidence -> JSON string. Plain strings (old seed rows) are kept as a summary."""
    if ev is None or ev == "":
        return ""
    if isinstance(ev, str):
        return ev
    if not isinstance(ev, dict):
        raise ValueError("evidence must be an object")
    out = {k: ev.get(k, [] if k == "sources" else "") for k in EVIDENCE_KEYS}
    if isinstance(out["sources"], str):
        out["sources"] = [out["sources"]]
    return json.dumps(out, ensure_ascii=False)


def parse_evidence(text):
    if not text:
        return {}
    try:
        ev = json.loads(text)
        return ev if isinstance(ev, dict) else {"summary": str(ev)}
    except (ValueError, TypeError):
        return {"summary": text}


def row_dict(r):
    d = dict(r)
    d["evidence"] = parse_evidence(d.get("evidence"))
    return d


# ---------- counts ----------

def count(con, *statuses):
    q = ",".join("?" * len(statuses))
    return con.execute(f"SELECT COUNT(*) FROM ideas WHERE status IN ({q})", statuses).fetchone()[0]


def pool_count(con):
    return count(con, "pool")


def room(con, settings=None):
    """How many more research ideas fit under the cap (pool + shown)."""
    return max(0, cfg(settings, "idea_cap") - count(con, "pool", "shown"))


def known_titles(con):
    return {r[0].strip().lower() for r in con.execute("SELECT title FROM ideas")}


# ---------- adding ----------

def add_to_pool(con, items, settings=None, enforce_cap=True):
    """Insert research ideas as pending. Fields: title, description, lane (rising|steady|test),
    evidence {why_buyer, why_now, competitors, warning, sources[]}, score, source (research|seed).
    Highest score wins when the cap is near. Titles already seen (any status, including denied) are skipped.
    Returns {"added": [ids], "skipped_duplicate": n, "skipped_cap": n, "room_left": n}."""
    items = sorted(items, key=lambda i: -float(i.get("score", 0) or 0))
    seen = known_titles(con)
    left = room(con, settings) if enforce_cap else 10 ** 9
    added, dup, capped = [], 0, 0
    for i in items:
        title = (i.get("title") or "").strip()
        if not title:
            raise ValueError("every idea needs a title")
        if title.lower() in seen:
            dup += 1
            continue
        if left <= 0:
            capped += 1
            continue
        source = (i.get("source") or "research").strip().lower()
        if source not in ("research", "seed"):
            raise ValueError("source must be 'research' or 'seed'")
        cur = con.execute(
            "INSERT INTO ideas(title, description, lane, evidence, score, source, status, created_at) "
            "VALUES (?,?,?,?,?,?, 'pool', ?)",
            (title, (i.get("description") or "").strip(), norm_lane(i.get("lane")),
             norm_evidence(i.get("evidence")), float(i.get("score", 0) or 0), source, now()))
        added.append(cur.lastrowid)
        seen.add(title.lower())
        left -= 1
    con.commit()
    return {"added": added, "skipped_duplicate": dup, "skipped_cap": capped, "room_left": room(con, settings)}


def add_seed(con, text):
    """Tony's own idea from the chat window: visible immediately, marked as his seed.
    Seeds are his input, so they are never refused by the research cap."""
    title = text.strip().rstrip(".")
    if not title:
        raise ValueError("empty seed")
    short = title if len(title) <= 90 else title[:87].rstrip() + "..."
    cur = con.execute(
        "INSERT INTO ideas(title, description, lane, evidence, score, source, status, created_at) "
        "VALUES (?,?, 'test', '', 0, 'seed', 'shown', ?)",
        (short, title if short != title else "", now()))
    con.commit()
    taste.record(con, cur.lastrowid, "seed", title)
    return cur.lastrowid


# ---------- refresh ----------

def refresh(con, settings=None):
    """Move up to `refresh_batch` pending ideas onto the visible list (adds, never replaces)."""
    n = cfg(settings, "refresh_batch")
    ids = [r[0] for r in con.execute(
        "SELECT id FROM ideas WHERE status='pool' ORDER BY score DESC, id LIMIT ?", (n,))]
    con.executemany("UPDATE ideas SET status='shown' WHERE id=?", [(i,) for i in ids])
    con.commit()
    set_meta(con, "last_refresh", now())
    return len(ids)


def refresh_due(con, settings=None):
    last = get_meta(con, "last_refresh")
    if not last:
        return True
    then = datetime.strptime(last, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - then).days >= cfg(settings, "refresh_days")


def maybe_weekly_refresh(con, settings=None):
    return refresh(con, settings) if refresh_due(con, settings) else 0


def fill_visible(con, n):
    """Old scaffold helper: top the visible list up to n. Kept for compatibility; the dashboard uses refresh()."""
    need = n - count(con, "shown")
    if need <= 0:
        return 0
    ids = [r[0] for r in con.execute(
        "SELECT id FROM ideas WHERE status='pool' ORDER BY score DESC, id LIMIT ?", (need,))]
    con.executemany("UPDATE ideas SET status='shown' WHERE id=?", [(i,) for i in ids])
    con.commit()
    return len(ids)


# ---------- decisions ----------

def _get(con, idea_id):
    row = con.execute("SELECT * FROM ideas WHERE id=?", (idea_id,)).fetchone()
    if not row:
        raise KeyError(idea_id)
    return row


def approve(con, idea_id):
    row = _get(con, idea_id)
    con.execute("UPDATE ideas SET status='approved', decided_at=? WHERE id=?", (now(), idea_id))
    # Placeholder art prompt; the art stage replaces this with a model-written prompt.
    prompt = f"{row['title']}. {row['description']} Abstract, Japandi, print-ready wall art, no text."
    con.execute("INSERT INTO prompts(idea_id, text) VALUES (?,?)", (idea_id, prompt))
    con.commit()
    taste.record(con, idea_id, "approve")


def deny(con, idea_id, n=None):
    """Denied ideas leave the list. No instant refill: the next weekly/refresh-now run adds more.
    `n` is accepted for the old call signature and ignored."""
    _get(con, idea_id)
    con.execute("UPDATE ideas SET status='denied', decided_at=? WHERE id=?", (now(), idea_id))
    con.commit()
    taste.record(con, idea_id, "deny")
    return 0


def comment(con, idea_id, text):
    taste.record(con, idea_id, "comment", text.strip())


def note(con, text):
    """Tony's remark about taste or process (from the chat). Teaches the profile; never becomes an idea."""
    text = (text or "").strip()
    if not text:
        raise ValueError("empty note")
    taste.record(con, None, "note", text)


# ---------- views ----------

def visible(con):
    return [row_dict(r) for r in con.execute(
        "SELECT * FROM ideas WHERE status='shown' ORDER BY (source='seed') DESC, score DESC, id")]


def bank(con):
    return [row_dict(r) for r in con.execute(
        "SELECT * FROM ideas WHERE status='approved' ORDER BY decided_at DESC, id DESC")]


def detail_view(d):
    """What the Details panel shows for one idea (list row or bank row). Evidence is passed through as
    stored; `sources` is always a list and `summary` is set for old plain-text evidence."""
    ev = dict(d.get("evidence") or {})
    src = ev.get("sources") or []
    ev["sources"] = [src] if isinstance(src, str) else list(src)
    return {k: d.get(k) for k in ("id", "title", "description", "lane", "source", "score", "status",
                                  "decided_at", "art_state", "art_image_id")} | {"evidence": ev}


def details(s):
    """Details for every idea currently on screen (visible list + bank), keyed by id."""
    return {str(i["id"]): detail_view(i) for i in s["visible"] + s["bank"]}


def state(con, settings=None):
    cap = cfg(settings, "idea_cap")
    shown, pool = count(con, "shown"), count(con, "pool")
    return {
        "visible": visible(con), "bank": bank(con),
        "shown": shown, "pool": pool, "banked": count(con, "approved"), "denied": count(con, "denied"),
        "cap": cap, "room": room(con, settings), "batch": cfg(settings, "refresh_batch"),
        "pool_low": pool < cfg(settings, "pool_low_warning"),
        "last_refresh": get_meta(con, "last_refresh"),
    }
