"""Taste learning. Every approve / deny / deny-comment / seed / chat taste note is stored as an event (table taste_events),
and so is every art pick, art feedback and art approval (actions art_pick | art_feedback | art_approve).
`art_stats` counts, per style card, how often it was shown, picked, passed on and approved, plus which chips
the picked images used; the prompt writer and the research job read that from the profile.
and a readable profile is rewritten next to the database after each event:

  data/Taste_Profile.json   machine-readable, for the research job
  data/Taste_Profile.md     the same, for a person or a Claude session to read

The research job (outside the Portal) reads one of these before it proposes new ideas.
Print it any time with: python -m app.taste
"""
import json
from collections import Counter
from pathlib import Path

RECENT = 25


def record(con, idea_id, action, text=""):
    con.execute("INSERT INTO taste_events(idea_id, action, comment) VALUES (?,?,?)", (idea_id, action, text or ""))
    con.commit()
    write_profile(con)


def _db_dir(con):
    path = con.execute("PRAGMA database_list").fetchone()[2]
    return Path(path).parent if path else None


def art_stats(con):
    """Per style card: images shown (finished), picked, passed, approved. Chips of picked images. Feedback."""
    try:
        from .db import load_config
        names = {c["id"]: c["name"] for c in load_config("style_cards")["cards"]}
    except (OSError, ValueError, KeyError):
        names = {}
    rows = con.execute("SELECT card_id, outcome, approved, chips FROM images "
                       "WHERE round_id IS NOT NULL AND status='done'").fetchall()
    cards, chips = {}, Counter()
    for r in rows:
        c = cards.setdefault(r["card_id"], {"card_id": r["card_id"], "name": names.get(r["card_id"], r["card_id"]),
                                            "shown": 0, "picked": 0, "passed": 0, "approved": 0})
        c["shown"] += 1
        c["picked"] += r["outcome"] == "picked"
        c["passed"] += r["outcome"] == "passed"
        c["approved"] += bool(r["approved"])
        if r["outcome"] == "picked":
            try:
                for g, v in json.loads(r["chips"] or "{}").items():
                    if v.get("id"):
                        chips[f"{g}:{v['id']}"] += 1
            except (ValueError, AttributeError):
                pass
    fb = [{"text": r["comment"], "idea_id": r["idea_id"], "at": r["created_at"]} for r in con.execute(
        "SELECT * FROM taste_events WHERE action='art_feedback' ORDER BY id DESC LIMIT ?", (RECENT,))]
    order = sorted(cards.values(), key=lambda c: (-c["approved"], -c["picked"], c["passed"], c["name"] or ""))
    return {"cards": order, "picked_chips": dict(chips.most_common()), "feedback": fb}


def build_profile(con):
    rows = con.execute(
        "SELECT e.*, i.title, i.lane, i.source FROM taste_events e LEFT JOIN ideas i ON i.id=e.idea_id "
        "ORDER BY e.id").fetchall()
    comments = {}
    for r in rows:
        if r["action"] == "comment" and r["idea_id"] is not None:
            comments.setdefault(r["idea_id"], []).append(r["comment"])

    def item(r):
        d = {"idea_id": r["idea_id"], "title": r["title"], "lane": r["lane"], "source": r["source"], "at": r["created_at"]}
        if comments.get(r["idea_id"]):
            d["comments"] = comments[r["idea_id"]]
        return d

    approved = [item(r) for r in rows if r["action"] == "approve"]
    denied = [item(r) for r in rows if r["action"] == "deny"]
    seeds = [{"text": r["comment"], "at": r["created_at"]} for r in rows if r["action"] == "seed"]
    notes = [{"text": r["comment"], "at": r["created_at"]} for r in rows if r["action"] == "note"]

    def rate(key):
        a = Counter(x[key] for x in approved)
        d = Counter(x[key] for x in denied)
        return {k: {"approved": a[k], "denied": d[k]} for k in sorted(set(a) | set(d), key=str)}

    return {
        "totals": {"approved": len(approved), "denied": len(denied), "seeds": len(seeds),
                   "deny_comments": sum(len(v) for v in comments.values())},
        "by_lane": rate("lane"),
        "by_source": rate("source"),
        "recent_approved": approved[-RECENT:][::-1],
        "recent_denied": denied[-RECENT:][::-1],
        "seeds": seeds[-RECENT:][::-1],
        "notes": notes[-RECENT:][::-1],          # Tony's remarks on taste/process, saved by the chat
        "art": art_stats(con),                   # style cards and chips Tony picks / passes on, art feedback
        "guidance": "Fewer, better ideas beat volume. Lean toward what Tony approves and seeds; "
                    "treat deny comments as hard signals; never re-propose a denied title.",
    }


def to_markdown(p):
    t = p["totals"]
    out = ["# Ikigai Taste Profile", "",
           "Auto-written by the Portal after every approve, deny, deny comment, seed or chat note. Read before proposing ideas.", "",
           f"Approved {t['approved']} · Denied {t['denied']} · Seeds {t['seeds']} · Deny comments {t['deny_comments']}", "",
           f"Guidance: {p['guidance']}", "", "## By lane"]
    out += [f"- {k}: {v['approved']} approved, {v['denied']} denied" for k, v in p["by_lane"].items()] or ["- none yet"]

    def section(title, items):
        out.extend(["", f"## {title}"])
        if not items:
            out.append("- none yet")
        for x in items:
            line = f"- {x['title']} ({x['lane']}, {x['source']})"
            for c in x.get("comments", []):
                line += f"\n  - Tony: {c}"
            out.append(line)

    section("Recently approved", p["recent_approved"])
    section("Recently denied (with Tony's reasons)", p["recent_denied"])
    out.extend(["", "## Tony's seeds"] + ([f"- {s['text']}" for s in p["seeds"]] or ["- none yet"]))
    out.extend(["", "## Tony's notes on taste and process"] + ([f"- {n['text']}" for n in p.get("notes", [])] or ["- none yet"]))
    a = p.get("art") or {}
    out.extend(["", "## Art styles (picked vs passed on)"])
    out.extend([f"- {c['name']}: shown {c['shown']}, picked {c['picked']}, passed {c['passed']}, approved {c['approved']}"
                for c in a.get("cards", [])] or ["- none yet"])
    if a.get("picked_chips"):
        out.append("- chips on picked images: " + ", ".join(f"{k} x{v}" for k, v in a["picked_chips"].items()))
    out.extend(["", "## Art feedback (Tony's words)"] + ([f"- {f['text']}" for f in a.get("feedback", [])] or ["- none yet"]))
    return "\n".join(out) + "\n"


def write_profile(con):
    p = build_profile(con)
    d = _db_dir(con)
    if d:
        (d / "Taste_Profile.json").write_text(json.dumps(p, indent=2, ensure_ascii=False))
        (d / "Taste_Profile.md").write_text(to_markdown(p))
    return p


if __name__ == "__main__":
    from .db import connect
    print(to_markdown(write_profile(connect())))
