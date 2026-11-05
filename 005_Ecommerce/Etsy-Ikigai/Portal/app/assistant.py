"""Conversational brain for the Studio chat: headless Claude CLI (`claude -p`) on this Mac.

Uses Tony's existing Claude plan (OAuth login of the `claude` CLI), no API key. The model gets NO tools:
it can only write text. To change the dashboard it emits one fenced JSON block

    ```json
    {"actions": [{"type": "approve", "idea_id": 3}]}
    ```

which `parse_reply` pulls out and `run_actions` validates and executes through app/ideas.py. Only the types in
ACTIONS exist; anything else is refused. A seed is only accepted when Tony's own message asks for one
(`asked_to_seed`), so plain chat can never become an idea.

CLI flags (see `cli_args`): print mode, --safe-mode (no CLAUDE.md, hooks, plugins, skills, MCP, so no
claude-mem session or Agent-OS router runs), --tools "" (no tools at all), --strict-mcp-config,
--disable-slash-commands, --no-session-persistence, own --system-prompt, a cheap model, JSON output.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import art, ideas, taste

ACTIONS = ("approve", "deny", "seed", "refresh", "taste_note", "art_iterate", "art_approve", "none")
MAX_ACTIONS = 8
DEFAULTS = {"chat_model": "sonnet", "chat_fallback_model": "haiku", "chat_timeout_s": 60, "chat_history": 20}

SYSTEM_PROMPT = """You are the studio assistant inside Tony's Ikigai Portal, a local dashboard for his Etsy shop \
Ikigai Digital Studio (printable digital wall art). You talk with Tony in a chat bar under the idea table.

The dashboard (stage 1, ideation): a list of researched print ideas, each with a lane (Rising, Steady, Test), \
a score and evidence (why a buyer wants it, why now, who sells it, a warning). Tony approves an idea (it moves \
to the Idea Bank and gets queued for art) or denies it (it leaves the list; his reason teaches the taste \
profile). Tony can type his own seed ideas. A research job outside the Portal refills the pending pool \
(weekly, about 10 at a time, hard cap 100 on list plus pending). Every approve, deny, deny reason, seed and \
taste note feeds the taste profile the research job reads. Refresh only moves PENDING ideas onto the list; \
with 0 pending nothing new arrives until the research job imports a batch (it is not scheduled yet). \
Art (stage 2) happens in the Details panel of a banked idea: Tony clicks Build art, picks style cards and chips, \
4 images are made; he clicks one to pick it, then tells you in this chat what to change; you start 4 new \
variations of the picked image with art_iterate; when he is happy he approves the art (button, or art_approve). \
Production (upscale, mockups, listing) and Performance are not built yet. Each turn you get a snapshot of the \
dashboard; trust it over memory.

How to answer:
- Short, plain words, no jargon, no filler. One to four sentences unless Tony asks for more.
- Do not ask Tony for things the snapshot already shows. Make a sensible assumption instead of asking.
- Do not announce actions yourself ("I've saved", "Approved"): the Portal adds a line saying what it did.
- Never bring up copyright status, public-domain questions or legal status of art.
- No emojis.

Dashboard actions. You have no tools. To change the dashboard, end your reply with ONE fenced block:
```json
{"actions": [{"type": "approve", "idea_id": 3}]}
```
Allowed types (nothing else exists):
- approve {idea_id}: only ideas with status "shown", and only when Tony clearly asks.
- deny {idea_id, reason?}: ideas "shown" or in the bank, only when Tony clearly asks. Put his words in reason.
- seed {text}: ONLY when Tony explicitly asks to add or seed an idea. text = a short descriptive idea line.
- refresh: move up to 10 pending ideas onto the list, when Tony asks.
- taste_note {text}: when Tony states a preference, a like or dislike, or how he wants to work or the process \
to go. Save a short faithful summary in his words. This is how the profile learns.
- art_iterate {idea_id, feedback, chips?}: when Tony asks for changes to the art of the idea open in Details \
and the snapshot shows a picked image. feedback = his change request in his own words. chips is optional, only \
when he names one: {"palette"|"mood"|"composition"|"texture"|"treatment": chip id, "accent": true}. Chip ids: \
palette terracotta_charcoal, sage_forest, moonlit_teal, marigold_primaries, pastel_burnt_orange, cream_spot; \
mood serene, dreamy, cheeky, joyful, bold, contemplative; composition centered_vignette, bottom_weighted, \
sweeping_edges, split_horizon, tight_fill; texture chalky_paper, woven_linen, scraped_spatter, knife_ridges, \
screenprint_matte, halftone_stipple; treatment dressed_character, pure_silhouette, pattern_filled, \
faceted_planes, tiny_figure, contour_line. Each art_iterate makes 4 paid images, so use it only on a clear request.
- art_approve {idea_id, image_id?}: only when Tony clearly says the art is final/approved. image_id defaults to \
the picked image.
- none: nothing to do (or just leave the block out).
A plain remark, plan or instruction about process is a taste_note, NEVER a seed. Use the ids exactly as shown \
in the snapshot. Never invent ids. Do not put the JSON anywhere except that final block."""


def cfg(settings, key):
    return (settings or {}).get(key, DEFAULTS[key])


# ---------- prompt ----------

def _line(text, n=140):
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def _evidence_line(ev):
    ev = ev or {}
    if ev.get("summary"):
        return _line(ev["summary"])
    bits = [ev.get("why_buyer"), ev.get("why_now") and "now: " + ev["why_now"], ev.get("warning") and "watch: " + ev["warning"]]
    return _line(" | ".join(b for b in bits if b), 200)


def _profile_md(con):
    d = taste._db_dir(con)
    f = d / "Taste_Profile.md" if d else None
    if f and f.exists():
        return f.read_text()[:4000]
    return taste.to_markdown(taste.build_profile(con))[:4000]


def snapshot(con, settings, selected_id=None):
    s = ideas.state(con, settings)
    out = [f"Counts: on list {s['shown']}, pending {s['pool']}, in bank {s['banked']}, denied {s['denied']}, "
           f"room {s['room']} of cap {s['cap']}. Last refresh {s['last_refresh'] or 'never'}.", "",
           "Idea list (status shown):"]
    out += [f"- #{i['id']} [{i['lane']}{', Tony seed' if i['source'] == 'seed' else ''}, score {round(i['score'])}] "
            f"{_line(i['title'], 120)} :: {_evidence_line(i['evidence']) or 'no evidence yet'}" for i in s["visible"]] or ["- (empty)"]
    out += ["", "Idea bank (approved):"]
    out += [f"- #{b['id']} [{b['lane']}] {_line(b['title'], 120)}" for b in s["bank"]] or ["- (empty)"]
    rows = con.execute("SELECT e.comment, i.title FROM taste_events e LEFT JOIN ideas i ON i.id=e.idea_id "
                       "WHERE e.action='comment' ORDER BY e.id DESC LIMIT 8").fetchall()
    out += ["", "Recent deny reasons:"]
    out += [f"- {_line(r['title'], 80)}: {_line(r['comment'], 160)}" for r in rows] or ["- none yet"]
    if selected_id:
        r = con.execute("SELECT * FROM ideas WHERE id=?", (selected_id,)).fetchone()
        if r:
            d = ideas.detail_view(ideas.row_dict(r))
            out += ["", f"Tony has this idea open in the Details panel: #{d['id']} ({d['status']}, {d['lane']}, "
                        f"{d['source']}) {d['title']}", f"Description: {_line(d['description'], 300) or '-'}",
                    f"Evidence: {json.dumps(d['evidence'], ensure_ascii=False)[:1200]}"]
            out += art.snapshot_lines(con, selected_id)
    out += ["", "Taste profile:", _profile_md(con)]
    return "\n".join(out)


def build_prompt(con, settings, history, text, selected_id=None, note=None):
    convo = [f"{'Tony' if m['role'] == 'tony' else 'You'}: {_line(m['text'], 600)}" for m in history]
    parts = ["<dashboard>", snapshot(con, settings, selected_id), "</dashboard>", "",
             "<conversation>", "\n".join(convo) or "(start)", "</conversation>", ""]
    if note:
        parts += [f"<portal_note>{note}</portal_note>", ""]
    parts += ["Tony's new message:", text]
    return "\n".join(parts)


# ---------- CLI ----------

class ChatUnavailable(Exception):
    """The CLI could not answer (missing, timed out, error). The message is short and plain."""


def claude_bin():
    return os.environ.get("PORTAL_CLAUDE_BIN") or shutil.which("claude") or "/opt/homebrew/bin/claude"


def cli_args(settings, system_prompt=None, model=None, fallback=None):
    args = [claude_bin(), "-p", "--safe-mode", "--tools", "", "--strict-mcp-config", "--disable-slash-commands",
            "--no-session-persistence", "--output-format", "json", "--model", model or cfg(settings, "chat_model"),
            "--system-prompt", system_prompt or SYSTEM_PROMPT]
    fb = fallback if fallback is not None else cfg(settings, "chat_fallback_model")
    if fb:
        args += ["--fallback-model", fb]
    return args


def run_cli(prompt, system_prompt, model, fallback, timeout, settings=None, who="The chat"):
    """Headless `claude -p`, prompt on stdin, no tools. Returns the reply text or raises ChatUnavailable.
    Shared by the chat and the art prompt writer (app/art.py)."""
    env = dict(os.environ)
    env.pop("CLAUDECODE", None)            # the Portal may have been started from a Claude Code shell
    try:
        p = subprocess.run(cli_args(settings, system_prompt, model, fallback), input=prompt, capture_output=True,
                           text=True, timeout=timeout, cwd=tempfile.gettempdir(), env=env)
    except subprocess.TimeoutExpired:
        raise ChatUnavailable(f"{who} took too long to answer")
    except OSError:
        raise ChatUnavailable("The Claude app on this Mac could not be started")
    try:
        out = json.loads(p.stdout or "{}")
    except ValueError:
        out = {}
    if p.returncode != 0 or out.get("is_error") or not isinstance(out.get("result"), str):
        raise ChatUnavailable(f"{who} could not answer just now")
    return out["result"]


def call_claude(prompt, settings=None):
    """The chat brain. Returns the reply text or raises ChatUnavailable."""
    return run_cli(prompt, SYSTEM_PROMPT, cfg(settings, "chat_model"), cfg(settings, "chat_fallback_model"),
                   cfg(settings, "chat_timeout_s"), settings)


# ---------- actions ----------

FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.S)
SEED_ASK = re.compile(r"\b(seed|seeds|seeding)\b|\badd\b.{0,40}\b(idea|ideas|list)\b|\b(new idea|idea for the list)\b", re.I)


def parse_reply(raw):
    """Split model output into (visible text, actions list). Only a fenced block with an "actions" list counts.
    Malformed JSON gives no actions; the block is still hidden from Tony."""
    raw = raw or ""
    actions, keep = [], raw
    for m in FENCE.finditer(raw):
        try:
            obj = json.loads(m.group(1))
        except ValueError:
            obj = None
        if isinstance(obj, dict) and "actions" in obj:
            if isinstance(obj["actions"], list):
                actions = [a for a in obj["actions"] if isinstance(a, dict)]
            keep = keep.replace(m.group(0), "")
    return keep.strip(), actions


def asked_to_seed(text):
    return bool(SEED_ASK.search(text or ""))


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _title(con, idea_id):
    r = con.execute("SELECT title FROM ideas WHERE id=?", (idea_id,)).fetchone()
    return r[0] if r else None


def run_actions(con, settings, actions, user_text, art_hooks=None):
    """Validate and execute. Returns (done lines, refused lines, changed?, denied ids without a reason).
    `art_hooks` (from app/studio.py) has iterate(idea_id, feedback, chips, user_text) and approve(idea_id, image_id);
    each returns a done line or raises art.ArtError."""
    done, refused, changed, bare_denies = [], [], False, []
    if len(actions) > MAX_ACTIONS:
        refused.append(f"only the first {MAX_ACTIONS} actions were considered")
        actions = actions[:MAX_ACTIONS]
    for a in actions:
        kind = str(a.get("type", "")).strip().lower()
        if kind not in ACTIONS:
            refused.append(f"unknown action “{_line(kind, 30)}”")
            continue
        if kind == "none":
            continue
        if kind in ("approve", "deny"):
            i = _int(a.get("idea_id"))
            row = i is not None and con.execute("SELECT title, status FROM ideas WHERE id=?", (i,)).fetchone()
            if not row:
                refused.append(f"no idea #{a.get('idea_id')}")
                continue
            ok = ("shown",) if kind == "approve" else ("shown", "approved")
            if row["status"] not in ok:
                refused.append(f"#{i} is {row['status']}, can't {kind} it")
                continue
            if kind == "approve":
                ideas.approve(con, i)
                done.append(f"Approved #{i} “{_line(row['title'], 70)}” (now in the bank).")
            else:
                ideas.deny(con, i)
                reason = _line(a.get("reason"), 500)
                if reason:
                    ideas.comment(con, i, reason)
                else:
                    bare_denies.append(i)
                done.append(f"Denied #{i} “{_line(row['title'], 70)}”" + (" with your reason." if reason else "."))
            changed = True
        elif kind == "seed":
            text = _line(a.get("text"), 300)
            if not text:
                refused.append("seed with no text")
            elif not asked_to_seed(user_text):
                refused.append("didn't add a seed: you didn't ask for one")
            else:
                i = ideas.add_seed(con, text)
                done.append(f"Added your seed #{i} “{_line(text, 70)}” to the list.")
                changed = True
        elif kind == "refresh":
            n = ideas.refresh(con, settings)
            done.append(f"Refreshed: {n} ideas added to the list." if n else "Refresh: nothing pending.")
            changed = changed or bool(n)
        elif kind in ("art_iterate", "art_approve"):
            i = _int(a.get("idea_id"))
            if i is None or art_hooks is None:
                refused.append(f"{kind}: no idea or art is not available here")
                continue
            try:
                if kind == "art_iterate":
                    fb = _line(a.get("feedback"), 500)
                    if not fb:
                        refused.append("art change with no feedback")
                        continue
                    chips = a.get("chips") if isinstance(a.get("chips"), dict) else None
                    done.append(art_hooks.iterate(i, fb, chips, user_text))
                else:
                    done.append(art_hooks.approve(i, _int(a.get("image_id"))))
                changed = True
            except art.ArtError as e:
                refused.append(f"{kind.replace('_', ' ')}: {e}")
        elif kind == "taste_note":
            text = _line(a.get("text"), 500)
            if not text:
                refused.append("empty taste note")
            else:
                ideas.note(con, text)
                done.append("Saved to your taste profile.")
    return done, refused, changed, bare_denies


def compose(text, done, refused):
    lines = [text] if text else []
    lines += done
    if refused:
        lines.append("Not done: " + "; ".join(refused) + ".")
    return "\n".join(lines).strip() or "OK."
