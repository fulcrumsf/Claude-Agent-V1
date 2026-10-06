#!/usr/bin/env python3
"""ledger_hook: fills the Quality Ledger without anyone remembering to call it.

One hook adapter shared by Claude Code, Codex and Gemini (--harness), three events
(--event skill|prompt|stop). It is fail-open and time-bounded: any error or malformed
input (including a mistyped hook command line) means exit 0, and a 1.0 s wall clock
never stalls a session.

Where it writes:
  * a session marker in the system temp dir (overridable with QUALITY_LEDGER_TMP)
  * the ledger path named by the marker (written only for Tony's explicit grades)

The one rule for Tony's explicit `grade:` notes: they are either recorded exactly,
or NOT recorded with a visible reminder that says why (ambiguous grade, no step=,
no ledger, ledger busy, ...). They are never dropped silently and never recorded
half-right (e.g. the decision kept but the grade lost).

No keys, no network, stdlib only. Paid calls are only recorded, never made.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_REGISTRY = HERE / "Workflow_Registry_Example.json"

try:
    sys.path.insert(0, str(HERE))
    import quality_ledger  # type: ignore
except Exception:  # fail open even if the sibling library cannot import
    quality_ledger = None

FALLBACK_GRADES = ("A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F")
# Plain-chat strong signal (reminder only, never written): a whole-word grade.
# Signed grades in either case ("b+", "A-"); bare B/C/D/F; a bare capital "A" only
# when it is not followed by a lowercase word ("A van drove past" is an article).
# Letters glued to words never count ("Car", "B-roll", "C++", "A-list").
GRADE_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9])([ABCabc][+\-]|A(?!\s+[a-z])|B|C|D|F)(?![A-Za-z0-9+\-])")
WORKSPACE = Path(os.environ.get("AGENT_OS_ROOT") or HERE.parents[2])
DEFAULT_LEDGER = "001_Architecture/Logs/Quality_Ledger.jsonl"
# Placeholder step on a pending item whose step Tony has not said.
UNKNOWN_STEP = "(step not given)"
# The shorthand write may wait this long for another writer's lock, so the whole
# hook still finishes well inside its 1.0 s budget.
LOCK_TIMEOUT = 0.4

# `grade:` shorthand vocabulary.
DECISION_WORDS = {"accept": "accept", "redo": "redo",
                  "accept_with_flaws": "accept_with_flaws",
                  "accept-with-flaws": "accept_with_flaws"}
_AWF_RE = re.compile(r"(?i)\baccept[\s_-]+with[\s_-]+flaws\b")
_KV_RE = re.compile(r"(?i)^(step|attempt)=(.*)$")
_EDGE = "\"'`()[]{}<>,.;:!?*"
_SIGN_WORDS = {"plus": "+", "minus": "-"}


# --------------------------------------------------------------------------- #
# markers
# --------------------------------------------------------------------------- #

def _markers_dir() -> Path:
    override = os.environ.get("QUALITY_LEDGER_TMP")
    if override:
        return Path(override)
    import tempfile as _tempfile
    return Path(_tempfile.gettempdir())


def marker_path(session_id: str) -> Path:
    if quality_ledger is not None:
        return quality_ledger.marker_path(session_id)
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", str(session_id or ""))[:128].strip(".")
    return _markers_dir() / f"agent_os_quality_ledger_{safe or 'default'}.json"


def load_marker(session_id: str) -> dict | None:
    try:
        obj = json.loads(marker_path(session_id).read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else None
    except (OSError, ValueError):
        return None


def save_marker(session_id: str, marker: dict) -> None:
    path = marker_path(session_id)
    if quality_ledger is not None:
        quality_ledger.write_marker(path, marker)  # atomic replace
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, path)


def load_registry(path: str | None = None) -> dict:
    reg_path = Path(path) if path else DEFAULT_REGISTRY
    try:
        obj = json.loads(reg_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    workflows = obj.get("workflows") if isinstance(obj, dict) else {}
    return workflows if isinstance(workflows, dict) else {}


# --------------------------------------------------------------------------- #
# where a run's ledger lives
# --------------------------------------------------------------------------- #

def _abs(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else WORKSPACE / path


def resolve_target(payload: dict, entry: dict) -> tuple[str | None, str | None, str]:
    """(run_id, ledger_path, note). ledger_path None means the hook cannot know
    where this run's ledger is, so it records nothing on its own and says so.

    Never guesses: the old version took the working folder's name as the run, so a
    session started at the workspace root became run "Agent-OS" and the hook created
    .../Productions/Agent-OS/Data/History/ to write into. Now:
      * a template with {run_id} resolves only from a working folder INSIDE the
        template's parent folder whose ledger folder already exists;
      * a central ledger (no {run_id}) uses the working folder's name as the run,
        or today's date + workflow when the session sits at the workspace root."""
    workflow_id = entry.get("workflow_id") or "run"
    template = str(entry.get("ledger") or DEFAULT_LEDGER)
    explicit = payload.get("run_id") if isinstance(payload.get("run_id"), str) else None
    cwd_text = payload.get("cwd") if isinstance(payload.get("cwd"), str) else ""
    cwd = Path(cwd_text or os.getcwd())
    dated = f"{time.strftime('%Y-%m-%d')}-{workflow_id}"

    if os.environ.get("QUALITY_LEDGER_TEST") == "1" and \
            entry.get("workflow_id") == "neon_parcel_longform":
        tmp = os.environ.get("QUALITY_LEDGER_TMP") or str(_markers_dir())
        run = explicit or cwd.name or dated
        return run, str(Path(tmp) / "Quality_Ledger.jsonl"), ""

    if "{run_id}" not in template:
        ledger = _abs(template)
        if explicit:
            run = explicit
        elif cwd.name and _resolved(cwd) not in (_resolved(WORKSPACE), _resolved(Path.home()),
                                               Path(cwd.anchor)):
            run = cwd.name
        else:
            run = dated
        if not ledger.parent.is_dir():
            return run, None, f"the ledger folder {ledger.parent} does not exist"
        return run, str(ledger), ""

    prefix_text, _, _ = template.partition("{run_id}")
    prefix = _resolved(_abs(prefix_text.rstrip("/") or "."))
    candidates: list[str] = []
    if explicit:
        candidates.append(explicit)
    else:
        try:
            parts = _resolved(cwd).relative_to(prefix).parts
        except ValueError:
            parts = ()
        candidates = ["/".join(parts[:k]) for k in range(len(parts), 0, -1)]
    for run in candidates:
        ledger = _abs(template.replace("{run_id}", run))
        if ledger.parent.is_dir():
            return run, str(ledger), ""
    if explicit:
        return explicit, None, f"the ledger folder for run {explicit} does not exist"
    return None, None, (f"the working folder ({cwd}) is not inside a {workflow_id} "
                        "production folder")


def _resolved(path: Path) -> Path:
    try:
        return path.resolve()
    except (OSError, RuntimeError):
        return path


# --------------------------------------------------------------------------- #
# payload helpers
# --------------------------------------------------------------------------- #

def extract_text(payload: dict) -> str:
    if not isinstance(payload, dict):
        return ""
    for key in ("prompt", "text", "message", "user_input", "content"):
        if isinstance(payload.get(key), str):
            return payload[key]
    prop = payload.get("tool_input") or payload.get("arguments") or {}
    if isinstance(prop, dict):
        for key in ("prompt", "text", "message", "content", "request", "input"):
            if isinstance(prop.get(key), str):
                return prop[key]
    last = payload.get("lastOpenEffect")
    if isinstance(last, dict):
        for key in ("text", "content", "message"):
            if isinstance(last.get(key), str):
                return last[key]
    return ""


def extract_skill(payload: dict) -> str | None:
    if not isinstance(payload, dict):
        return None
    tool_input = payload.get("tool_input") or {}
    if isinstance(tool_input, dict):
        # Codex / Gemini have no Skill tool: a file read of */SKILL.md starts it.
        for key in ("file_path", "absolute_path", "path"):
            value = tool_input.get(key)
            if isinstance(value, str) and Path(value).name == "SKILL.md":
                return Path(value).parent.name
        for key in ("skill", "name"):
            if isinstance(tool_input.get(key), str):
                return tool_input[key]
    tool_use = payload.get("tool_use") or payload.get("toolUse") or {}
    if isinstance(tool_use, dict) and isinstance(tool_use.get("name"), str):
        return tool_use["name"]
    if isinstance(payload.get("tool_name"), str):
        return payload["tool_name"]
    return None


def extract_session(payload: dict) -> str:
    if not isinstance(payload, dict):
        return "default"
    for key in ("session_id", "sessionId", "session"):
        if isinstance(payload.get(key), str) and payload[key].strip():
            return payload[key]
    return "default"


def grade_keys() -> tuple[str, ...]:
    if quality_ledger is not None:
        try:
            return tuple(quality_ledger.load_grade_scale())
        except Exception:
            pass
    return FALLBACK_GRADES


def readiness_threshold() -> int:
    if quality_ledger is not None:
        try:
            return int(quality_ledger.load_readiness_policy().get("threshold", 87))
        except Exception:
            return 87
    return 87


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _when(value) -> datetime:
    if quality_ledger is not None:
        moment = quality_ledger.parse_timestamp(value)
        if moment is not None:
            return moment
    return datetime.min.replace(tzinfo=timezone.utc)


# --------------------------------------------------------------------------- #
# parsing Tony's words
# --------------------------------------------------------------------------- #

def _clean(token: str) -> str:
    return token.strip(_EDGE)


def parse_shorthand(text: str) -> dict | None:
    """Parse `grade: <grade> <decision> step=<step> attempt=<n> <his words>`.

    Returns None when the message does not start with `grade:`. Otherwise a dict
    with grade, decision, step, attempt (None = latest) and verbatim, plus
    `problems`: everything that stops it from being recorded exactly as Tony meant.

    How it reads the message (one rule set instead of per-case patches):
      * The grade and decision are read only from the HEADER, the words right after
        `grade:` up to the first ordinary word. Words in his free-text comment never
        count ("grade: B+ accept step=final no need to redo" is accept, not redo).
      * Grades match whole words in any case ("a+", "B-", "b plus"); a letter glued
        to a word never counts ("Car", "Dog").
      * A bare A is the grade A when it ends the message, is followed by another
        header word (`step=`, `accept`, ...), or carries punctuation ("A,"). "A"
        followed by an ordinary word ("grade: A great job" / "grade: A bit soft")
        could be the article: that is reported as ambiguous, never guessed. A
        lowercase "a" before an ordinary word later in the header is the article.
      * step= and attempt= are read anywhere in the message.
      * Two different grades, two different decisions, two different step=, a bad
        attempt=, a letter not on the scale ("E", "A++"), or no grade and no
        decision at all are all problems."""
    if not isinstance(text, str):
        return None
    stripped = text.strip()
    if not re.match(r"(?i)^grade\s*:", stripped):
        return None
    body = re.sub(r"(?i)^grade\s*:\s*", "", stripped, count=1).strip()
    keys = grade_keys()
    tokens = _AWF_RE.sub("accept_with_flaws", body).split()
    grades: list[str] = []
    decisions: list[str] = []
    problems: list[str] = []
    kv: dict[str, str] = {}

    def next_word(j: int) -> tuple[int, str | None]:
        for k in range(j, len(tokens)):
            if any(ch.isalnum() for ch in tokens[k]):
                return k, _clean(tokens[k])
        return len(tokens), None

    def is_header_word(word: str | None) -> bool:
        if word is None:
            return True  # end of message
        if _KV_RE.match(word) or word.lower() in DECISION_WORDS:
            return True
        up = word.upper()
        return up in keys and (len(word) == 2 or up != "A")

    in_header = True
    first = True
    i = 0
    while i < len(tokens):
        raw = tokens[i]
        i += 1
        if not any(ch.isalnum() for ch in raw):
            continue  # "-", "—", "|" between header words
        word = _clean(raw)
        kv_match = _KV_RE.match(word)
        if kv_match:
            key, value = kv_match.group(1).lower(), _clean(kv_match.group(2))
            if key in kv and kv[key] != value:
                problems.append(f"two different {key}= values ({kv[key]!r} and {value!r})")
            kv[key] = value
            first = False
            continue
        if not in_header:
            continue
        low = word.lower()
        if low in DECISION_WORDS:
            decisions.append(DECISION_WORDS[low])
            first = False
            continue
        up = word.upper()
        if len(word) == 1 and up in "ABCDF":
            j, after = next_word(i)
            if after and after.lower() in _SIGN_WORDS and up + _SIGN_WORDS[after.lower()] in keys:
                grades.append(up + _SIGN_WORDS[after.lower()])  # "B plus" = B+
                i = j + 1
                first = False
                continue
        if up in keys:
            if up == "A" and len(word) == 1:
                _, after = next_word(i)
                if after is None or is_header_word(after) or raw[-1:] in ",.;:!?)":
                    grades.append("A")
                elif word == "A" or first:
                    problems.append(
                        f"'{word} {after}' could be the grade A or the word 'a' (write it "
                        "as `grade: A accept step=...` with the grade first, or `A,`)")
                    in_header = False
                else:
                    in_header = False  # lowercase article later in the header
                first = False
                continue
            grades.append(up)
            first = False
            continue
        if first and re.fullmatch(r"[A-G][+-]*|[a-f][+-]{2,}", word):
            problems.append(f"{word!r} is not a grade on the scale ({', '.join(keys)})")
        in_header = False
        first = False

    grade_set = list(dict.fromkeys(grades))
    decision_set = list(dict.fromkeys(decisions))
    if len(grade_set) > 1:
        problems.append(f"more than one grade ({', '.join(grade_set)})")
    if len(decision_set) > 1:
        problems.append(f"more than one decision ({', '.join(decision_set)})")
    grade = grade_set[0] if len(grade_set) == 1 else None
    decision = decision_set[0] if len(decision_set) == 1 else None
    if not problems and grade is None and decision is None:
        problems.append("no letter grade (A+ to F) or decision (accept / "
                        "accept_with_flaws / redo) right after `grade:`")
    # No default step (explicit over automatic, like the grade CLI's required
    # --level): a missing step= is None, never a guessed "final" that would land in
    # the readiness average. handle_prompt turns None into a pending reminder.
    step = kv.get("step") or None
    if step and step.lower() == "final":
        step = "final"
    attempt = None
    if "attempt" in kv:
        value = kv["attempt"]
        if re.fullmatch(r"[0-9]+", value) and int(value) >= 1:
            attempt = int(value)
        else:
            problems.append(f"attempt={value!r} is not a whole number of 1 or more")
    return {"grade": grade, "decision": decision, "step": step, "attempt": attempt,
            "verbatim": stripped, "problems": problems}


def level_for_step(step: str) -> str:
    if step == "final":
        return "final"
    return "sub_step" if "." in step else "step"


def detect_signal(text: str) -> dict | None:
    stripped = text.strip()
    grade = None
    match = GRADE_TOKEN_RE.search(stripped)
    if match:
        grade = match.group(1).upper()
    decision = None
    lower = stripped.lower()
    if re.search(r"\baccept\s+with\s+flaws\b", lower) or \
            re.search(r"\baccept_with_flaws\b", lower):
        decision = "accept_with_flaws"
    elif re.search(r"\bredo\b", lower):
        decision = "redo"
    elif re.search(r"\bapprov(ed|e)\b", lower):
        decision = "approve"
    if grade is None and decision is None:
        return None
    return {"grade": grade, "decision": decision, "verbatim": stripped}


# --------------------------------------------------------------------------- #
# output
# --------------------------------------------------------------------------- #

def render(hook_event: str, text: str, system_message: str | None = None) -> str:
    if not text and not system_message:
        return ""
    out: dict = {"hookSpecificOutput": {"hookEventName": hook_event}}
    if text:
        out["hookSpecificOutput"]["additionalContext"] = text
    if system_message:
        out["hookSpecificOutput"]["systemMessage"] = system_message
    return json.dumps(out)


HOOK_EVENT_NAMES = {"skill": "PostToolUse", "prompt": "UserPromptSubmit", "stop": "Stop"}


# --------------------------------------------------------------------------- #
# pending items
# --------------------------------------------------------------------------- #

def _new_pending(marker: dict, **fields) -> dict:
    item = {"kind": "grade", "at": _utcnow(),
            "workflow_id": marker.get("workflow_id"), "run_id": marker.get("run_id"),
            "ledger_path": marker.get("ledger_path")}
    item.update(fields)
    marker.setdefault("pending", []).append(item)
    return item


def ledger_events(marker: dict) -> list[dict]:
    if quality_ledger is None or not marker.get("ledger_path"):
        return []
    return quality_ledger.read_events_lenient(marker["ledger_path"])[0]


def prune_pending(marker: dict) -> bool:
    """Drop pending items already answered by a director line in the ledger
    (written by the CLI or shorthand at or after the item was raised). Each item is
    checked against its own run and ledger, so items survive a skill restart."""
    pending = [p for p in marker.get("pending") or [] if isinstance(p, dict)]
    if not pending or quality_ledger is None:
        return False
    cache: dict[str, list[dict]] = {}
    keep = []
    for item in pending:
        ledger = item.get("ledger_path") or marker.get("ledger_path")
        run_id = item.get("run_id") or marker.get("run_id")
        if ledger and ledger not in cache:
            cache[ledger] = quality_ledger.read_events_lenient(ledger)[0]
        raised = _when(item.get("at"))
        # An item whose step was not known when raised is answered by any director
        # line on its run written at or after it.
        answered = any(
            e.get("source") == "director_judgment" and e.get("run_id") == run_id
            and (item.get("needs_step") or e.get("step") == item.get("step"))
            and _when(e.get("timestamp")) >= raised
            for e in cache.get(ledger, []))
        if not answered:
            keep.append(item)
    changed = len(keep) != len(marker.get("pending") or [])
    marker["pending"] = keep
    return changed


def _clear_hint(session_id: str) -> str:
    return (f" If it was not a grade, clear the reminder with `quality_ledger.py "
            f"pending --session {session_id} --clear`.")


@contextlib.contextmanager
def _alarm_blocked():
    """Hold off the 1.0 s deadline while bytes are being appended, so the deadline
    can never cut a ledger line in half (the lock wait itself is bounded by
    LOCK_TIMEOUT instead)."""
    try:
        old = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
    except (AttributeError, ValueError, OSError):
        old = None
    try:
        yield
    finally:
        if old is not None:
            signal.pthread_sigmask(signal.SIG_SETMASK, old)


def write_event(marker: dict, shorthand: dict) -> dict:
    """Write one director_judgment line via the shared writer, deriving
    below_threshold_override exactly like the grade CLI does. With no attempt=,
    the grade attaches to the latest attempt of that step (or 1), like the CLI."""
    workflow_id, run_id = marker["workflow_id"], marker["run_id"]
    step = shorthand["step"]
    director: dict = {"verbatim": shorthand["verbatim"]}
    if shorthand.get("grade"):
        director["grade"] = shorthand["grade"]
    if shorthand.get("decision"):
        director["decision"] = shorthand["decision"]
    if quality_ledger.director_is_override(director, readiness_threshold(),
                                           quality_ledger.load_grade_scale()):
        director["below_threshold_override"] = True
    event = quality_ledger.build_event(
        workflow_id=workflow_id, run_id=run_id, step=step, level=level_for_step(step),
        attempt=shorthand.get("attempt") or 1, source="director_judgment", actor="Tony",
        reason=shorthand["verbatim"], director=director,
    )
    auto = None
    if not shorthand.get("attempt"):
        def auto(events):
            return quality_ledger.max_attempt(events, workflow_id, run_id, step) or 1
    with _alarm_blocked():
        return quality_ledger.append_event(marker["ledger_path"], event,
                                           auto_attempt=auto, lock_timeout=LOCK_TIMEOUT)


def _handle_shorthand(marker: dict, session_id: str, shorthand: dict) -> str:
    # Wording problems need Tony; system problems only need the agent to record it.
    problems = list(shorthand.get("problems") or [])
    if shorthand.get("step") is None:
        problems.append("it has no `step=` (a missing step is never assumed to be the "
                        "final video)")
    wording = bool(problems)
    if not marker.get("ledger_path"):
        problems.append("no ledger is known for this session"
                        + (f" ({marker['ledger_note']})" if marker.get("ledger_note") else ""))
    if quality_ledger is None:
        problems.append("quality_ledger.py could not be loaded")

    step = shorthand.get("step") or UNKNOWN_STEP
    item = _new_pending(marker, step=step, needs_step=shorthand.get("step") is None,
                        grade=shorthand.get("grade"), decision=shorthand.get("decision"),
                        verbatim=shorthand["verbatim"])
    if not problems:
        # Saved BEFORE writing: if the deadline ever ends the hook mid-way, the
        # reminder survives (and is pruned automatically once the line exists).
        save_marker(session_id, marker)
        try:
            written = write_event(marker, shorthand)
        except Exception as exc:  # ValueError, OSError, TimeoutError, ...
            problems.append(f"the ledger write failed ({exc})")
        else:
            marker["pending"] = [p for p in marker.get("pending") or []
                                 if p is not item and not (
                                     p.get("run_id") == marker.get("run_id")
                                     and (p.get("needs_step") or p.get("step") == step))]
            marker.setdefault("graded", []).append(step)
            save_marker(session_id, marker)
            what = ", ".join(x for x in (
                f"grade {written['director'].get('grade')}"
                if written["director"].get("grade") else "",
                f"decision {written['director'].get('decision')}"
                if written["director"].get("decision") else "") if x)
            return render(HOOK_EVENT_NAMES["prompt"], (
                f"Quality Ledger: recorded Tony's grade for `{step}` ({what}, attempt "
                f"{written['attempt']}, level {written['level']})."))
    item["problem"] = "; ".join(problems)
    save_marker(session_id, marker)
    record = ("`quality_ledger.py grade --ledger <ledger> --workflow <workflow> --run "
              "<run> --step <step> --level sub_step|step|final --verbatim \"<his "
              "words>\"`")
    if wording:
        advice = (". Ask Tony what he meant (which grade, decision and step), then "
                  f"record it with {record}, or have him resend it like "
                  "`grade: B+ accept step=<step>`.")
    else:
        advice = (f". His note itself is clear: record it now by hand with {record} "
                  "(his exact words are kept in the pending list).")
    return render(HOOK_EVENT_NAMES["prompt"], (
        "Quality Ledger: Tony's `grade:` note was NOT recorded: " + "; ".join(problems)
        + advice + _clear_hint(session_id)))


# --------------------------------------------------------------------------- #
# events
# --------------------------------------------------------------------------- #

def handle_skill(payload: dict, registry: dict) -> str:
    skill_name = extract_skill(payload)
    if not skill_name:
        return ""
    entry = registry.get(skill_name)
    if not isinstance(entry, dict):
        return ""
    session_id = extract_session(payload)
    run_id, ledger, note = resolve_target(payload, entry)
    workflow_id = entry.get("workflow_id", skill_name)
    old = load_marker(session_id) or {}
    # A re-invoked skill must not wipe reminders that are still unanswered; each
    # carries its own run and ledger, so it is checked against the right file.
    carried = []
    for item in old.get("pending") or []:
        if isinstance(item, dict):
            item.setdefault("workflow_id", old.get("workflow_id"))
            item.setdefault("run_id", old.get("run_id"))
            item.setdefault("ledger_path", old.get("ledger_path"))
            carried.append(item)
    marker = {
        "session_id": session_id,
        "workflow_id": workflow_id,
        "run_id": run_id,
        "ledger_path": ledger,
        "ledger_note": note,
        "pending": carried,
        "graded": old.get("graded") or [] if old.get("run_id") == run_id else [],
    }
    save_marker(session_id, marker)
    commands = (
        "Record events with:\n"
        "  quality_ledger.py check --ledger <ledger> ...\n"
        "  quality_ledger.py self-correct --ledger <ledger> ...\n"
        "  quality_ledger.py grade --ledger <ledger> --level sub_step|step|final ...\n"
        "  quality_ledger.py edit --ledger <ledger> ...   (Tony edited the asset himself)\n"
    )
    if ledger:
        text = (f"Quality Ledger active for workflow `{workflow_id}` run `{run_id}`.\n"
                f"Ledger: {ledger}\n" + commands)
    else:
        text = (f"Quality Ledger: workflow `{workflow_id}` started, but no ledger could "
                f"be chosen automatically: {note}. Nothing will be recorded on its own; "
                "pass --ledger and --run explicitly (the production's "
                "Data/History/Quality_Ledger.jsonl).\n" + commands)
    return render(HOOK_EVENT_NAMES["skill"], text)


def handle_prompt(payload: dict, registry: dict) -> str:
    session_id = extract_session(payload)
    text = extract_text(payload)
    if not text:
        return ""
    marker = load_marker(session_id)
    shorthand = parse_shorthand(text)
    if marker is None:
        if shorthand is not None:
            # An explicit grade typed when no workflow ledger is active must not
            # vanish without a word.
            return render(HOOK_EVENT_NAMES["prompt"], (
                "Quality Ledger: Tony's `grade:` note was NOT recorded: no workflow "
                "ledger is active in this session (no registered skill has started "
                "one). Record it by hand with `quality_ledger.py grade --ledger "
                "<ledger> ... --verbatim \"<his words>\"`."))
        return ""
    if prune_pending(marker):
        save_marker(session_id, marker)

    if shorthand is not None:
        return _handle_shorthand(marker, session_id, shorthand)

    signal_ = detect_signal(text)
    if signal_:
        # The step is unknown: never assume "final". Any director line Tony then
        # gives on this run (at any step) answers it.
        needs_grade = (signal_.get("decision") == "approve" and not signal_.get("grade"))
        _new_pending(marker, step=UNKNOWN_STEP, needs_step=True,
                     grade=signal_.get("grade"), needs_grade=needs_grade,
                     verbatim=signal_["verbatim"])
        save_marker(session_id, marker)
        if needs_grade:
            reminder = ("Quality Ledger: Tony said 'approved' with no grade. "
                        "A pass is technically a B+ / 87. What's your actual score?")
        else:
            reminder = ("Quality Ledger: Tony gave a judgment. Record it with "
                        "`quality_ledger.py grade ... --level sub_step|step|final "
                        "--verbatim \"<his words>\"`, asking which step (and level) "
                        "if unclear.")
        return render(HOOK_EVENT_NAMES["prompt"], reminder + _clear_hint(session_id))

    pending = marker.get("pending") or []
    if pending:
        lines = ["Quality Ledger: still pending a grade for these items:"]
        for item in pending:
            lines.append(_pending_line(item, marker))
        return render(HOOK_EVENT_NAMES["prompt"],
                      "\n".join(lines) + "\n" + _clear_hint(session_id).strip())
    return ""


def _pending_line(item: dict, marker: dict) -> str:
    line = (f"  pending grade for `{item.get('step')}` on "
            f"`{item.get('run_id') or marker.get('run_id')}`.")
    if item.get("problem"):
        line += f" (not recorded: {item['problem']})"
    return line


def handle_stop(payload: dict, registry: dict) -> str:
    session_id = extract_session(payload)
    marker = load_marker(session_id)
    if marker is None:
        return ""
    if prune_pending(marker):
        save_marker(session_id, marker)
    parts: list[str] = []
    questions: list[str] = []
    for item in marker.get("pending") or []:
        line = _pending_line(item, marker).strip()
        parts.append(line)
        questions.append(
            f"Quality Ledger: pending grade for `{item.get('step')}` on "
            f"`{item.get('run_id') or marker.get('run_id')}`. What grade do you give it "
            "(A+ to F)?")
    # Silent retries: only for THIS run (a shared central ledger holds every run;
    # old runs must not nag every session forever).
    events = [e for e in ledger_events(marker)
              if e.get("run_id") == marker.get("run_id")
              and e.get("workflow_id") == marker.get("workflow_id")]
    if quality_ledger is not None and events:
        attempts = quality_ledger.collect_attempts(events)
        unexplained = quality_ledger.unexplained(attempts, events)
        if unexplained:
            line = (f"pending review of {unexplained} unexplained retry(ies) "
                    f"(attempt went up with no director grade or self-correction).")
            parts.append(line)
            questions.append("Quality Ledger: " + line)
    if not parts:
        return ""
    # Claude Stop and Gemini AfterAgent both show a top-level systemMessage to the
    # user; Stop has no hookSpecificOutput. reason carries the same text (it is what
    # Claude feeds back to the agent when --block turns this into decision=block).
    return json.dumps({"systemMessage": "\n".join(questions),
                       "reason": "Quality Ledger:\n" + "\n".join(parts)})


def run(payload: dict, harness: str, event: str, registry_path: str | None = None) -> str:
    registry = load_registry(registry_path)
    if not isinstance(payload, dict):
        return ""
    if event == "skill":
        return handle_skill(payload, registry)
    if event == "prompt":
        return handle_prompt(payload, registry)
    if event == "stop":
        return handle_stop(payload, registry)
    return ""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ledger_hook.py",
        description="Fail-open hook adapter that fills the Quality Ledger.")
    parser.add_argument("--harness", choices=("claude", "codex", "gemini"),
                        default="claude")
    parser.add_argument("--event", choices=("skill", "prompt", "stop"), required=True)
    parser.add_argument("--registry", help="workflow registry JSON path")
    parser.add_argument("--block", action="store_true",
                        help="opt-in hard stop on Stop (default: ask, non-blocking)")
    return parser


class _Deadline(Exception):
    pass


def _on_deadline(signum, frame):
    raise _Deadline()


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except SystemExit:
        # Fail open even on a mistyped hook command line: argparse's exit 2 would
        # block Tony's prompt on UserPromptSubmit. (--help still prints first.)
        return 0
    old = None
    try:
        old = signal.signal(signal.SIGALRM, _on_deadline)
        signal.setitimer(signal.ITIMER_REAL, 1.0)
    except (ValueError, AttributeError, OSError):
        old = None
    try:
        try:
            raw = sys.stdin.read()
            payload = json.loads(raw) if raw.strip() else {}
            if not isinstance(payload, dict):
                return 0
            out = run(payload, args.harness, args.event, args.registry)
            # --block (opt-in): exit 2 on Stop while items are pending, unless the
            # agent is already continuing from a block (avoids a loop).
            if out and args.event == "stop" and args.block \
                    and not payload.get("stop_hook_active"):
                print(json.loads(out)["reason"], file=sys.stderr)
                return 2
            if out:
                print(out)
            return 0
        except Exception:
            return 0
    except _Deadline:
        return 0
    finally:
        if old is not None:
            try:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, old)
            except _Deadline:
                pass


if __name__ == "__main__":
    sys.exit(main())
