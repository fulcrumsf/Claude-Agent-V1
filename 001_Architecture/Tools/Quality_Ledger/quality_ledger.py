#!/usr/bin/env python3
"""Quality_Ledger: one channel-agnostic, append-only quality log plus its CLI.

Every line is one event with exactly one source:
  * mechanical_check    - a script/automated gate measured pass / fail / error
  * director_judgment   - Tony's grade and/or decision, his own words verbatim
  * agent_self_correction - the agent changed or redid something before Tony saw it
  * director_edit       - Tony personally edited/fixed the asset himself

Any event may carry an optional failure_type from the fixed FAILURE_TYPES list.

The ledger is append-only: there is no delete or rewrite command; corrections are
new events. Stdlib only, no keys, no network. Paid calls are only recorded (cost_usd
optional), never triggered.

Hardening rules (2026-10-06 bug hunt), so they are not re-broken later:
  * Nothing is ever written silently wrong. Bad input is a clear error (exit 2),
    never a quiet default, a crash with a traceback, or a half-written line.
  * The ledger never creates folders: the ledger's folder must already exist.
  * Auto-numbered attempts are decided while holding the file lock, so two writers
    can never get the same number.
  * report / export refuse a ledger with any invalid line (exit 2, run validate),
    exactly like they already refused a line that is not JSON.

Tony's decisions (2026-10-06):
  * Readiness counts only the LATEST final per run (latest_final_per_run); earlier
    finals on that run stay in the file and export but are superseded.
  * A check's attempt only advances when the output was regenerated: checks that
    fingerprint the same artifact (sha256) as the latest attempt share it
    (check_attempt). No artifact given means its own attempt (the safe default).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:  # POSIX only; elsewhere appends are unlocked
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

HERE = Path(__file__).resolve().parent

SOURCES = ("mechanical_check", "director_judgment", "agent_self_correction",
           "director_edit")
LEVELS = ("sub_step", "step", "final")
CHECK_RESULTS = ("pass", "fail", "error")
DECISIONS = ("accept", "accept_with_flaws", "redo")
# Fixed, closed list (never free text) of what kind of thing went wrong. Optional
# on every source; drawn from real Report Card / session failures (see README).
FAILURE_TYPES = ("spatial_layout", "scale", "continuity", "subject_count",
                 "plausibility", "camera", "motion", "render_artifact", "story",
                 "other")

GRADE_SCALE_FILE = HERE / "Grade_Scale.json"
READINESS_FILE = HERE / "Readiness_Policy.json"
SCHEMA_FILE = HERE / "Event_Schema.json"

REQUIRED_KEYS = ("event_id", "timestamp", "workflow_id", "run_id", "step",
                 "level", "attempt", "source", "actor", "reason")
# Required keys that must be non-empty strings (an empty step or run id would
# silently merge unrelated work in report).
ID_KEYS = ("event_id", "workflow_id", "run_id", "step", "actor")
# Optional top-level keys that, when present, must be non-empty strings.
OPTIONAL_STRING_KEYS = ("corrects_event_id", "artifact_path", "artifact_sha256",
                        "harness")

NESTED_KEYS = {
    "check": {"name", "result", "measured", "threshold", "unit", "report_path"},
    "director": {"grade", "decision", "verbatim", "below_threshold_override"},
}

# actor on agent_self_correction lines. director_judgment / director_edit are always
# "Tony"; the parallel, readable non-Tony value for "the agent fixed it itself" is
# "agent" (never this script's own filename, which says nothing about who acted).
SELF_CORRECTION_ACTOR = "agent"

# actor on mechanical_check lines: WHAT ran the check (a checker tool), never "agent"
# (an agent judgment call is a different thing) and never this script's filename.
# A manual `check` defaults to the generic "mechanical_check"; `check --from-report`
# uses the report's own "tool" field when it has one, else the logical name of the
# only report shape that path accepts (check_storyboard_scale.py's).
MECHANICAL_CHECK_ACTOR = "mechanical_check"
FROM_REPORT_DEFAULT_ACTOR = "check_storyboard_scale"

# --at only backdates; a little clock skew is tolerated, a future time is not (a
# future timestamp would sort last forever and poison every readiness window).
FUTURE_SKEW = timedelta(minutes=5)

MARKER_PREFIX = "agent_os_quality_ledger_"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_timestamp(value) -> datetime | None:
    """A stored timestamp as an aware UTC datetime, or None if it is not a real
    ISO 8601 time with a timezone. Used by validate, sorting and the hook, so
    mixed precision or offsets ("...00Z", "...00.123+00:00", "-07:00") compare by
    real time, never as raw strings."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text[-1:] in ("Z", "z"):
        text = text[:-1] + "+00:00"
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        return None
    if moment.tzinfo is None or moment.utcoffset() is None:
        return None
    try:
        return moment.astimezone(timezone.utc)
    except (OverflowError, ValueError):
        return None


def parse_at(value: str) -> str:
    """argparse type for --at: a real ISO 8601 timestamp with an explicit timezone
    (Z or +00:00 style), returned as a UTC ISO string. Used to backdate an event
    rebuilt from history. Garbage, a timestamp with no timezone, one that falls
    outside the calendar once converted to UTC, or one in the future is rejected
    (argparse turns this into exit 2 with the message below)."""
    text = (value or "").strip()
    if text[-1:] in ("Z", "z"):
        text = text[:-1] + "+00:00"
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{value!r} is not an ISO 8601 timestamp "
            "(expected e.g. 2026-09-19T17:47:00Z)")
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise argparse.ArgumentTypeError(
            f"{value!r} has no timezone; add Z (UTC) or an offset like +00:00 "
            "(expected e.g. 2026-09-19T17:47:00Z)")
    try:
        utc = moment.astimezone(timezone.utc)
    except (OverflowError, ValueError):
        raise argparse.ArgumentTypeError(
            f"{value!r} is out of range once converted to UTC")
    if utc > datetime.now(timezone.utc) + FUTURE_SKEW:
        raise argparse.ArgumentTypeError(
            f"{value!r} is in the future; --at only backdates an event")
    return utc.isoformat()


def _positive_int(value: str) -> int:
    """argparse type for --attempt: a whole number of 1 or more. (0 used to be
    silently treated as 'not given' and auto-numbered.)"""
    try:
        number = int(str(value).strip())
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not a whole number")
    if number < 1:
        raise argparse.ArgumentTypeError(f"{value!r} must be 1 or more")
    return number


def _non_negative_int(value: str) -> int:
    try:
        number = int(str(value).strip())
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not a whole number")
    if number < 0:
        raise argparse.ArgumentTypeError(f"{value!r} must be 0 or more")
    return number


def _threshold_int(value: str) -> int:
    number = _non_negative_int(value)
    if number > 100:
        raise argparse.ArgumentTypeError(f"{value!r} must be between 0 and 100")
    return number


def _finite_float(value: str) -> float:
    """argparse type for --measured / --threshold: nan and inf would be written as
    NaN / Infinity, which is not valid JSON for any strict reader or dashboard."""
    try:
        number = float(str(value).strip())
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not a number")
    if not math.isfinite(number):
        raise argparse.ArgumentTypeError(f"{value!r} must be a finite number")
    return number


def _nonempty_text(value: str) -> str:
    """argparse type for identifiers (--workflow, --run, --step, --ledger, ...):
    surrounding spaces are trimmed and an empty value is rejected."""
    text = (value or "").strip()
    if not text:
        raise argparse.ArgumentTypeError("must not be empty")
    return text


def load_grade_scale(path: Path | None = None) -> dict[str, int]:
    return json.loads((path or GRADE_SCALE_FILE).read_text(encoding="utf-8"))


def load_readiness_policy(path: Path | None = None) -> dict:
    return json.loads((path or READINESS_FILE).read_text(encoding="utf-8"))


def director_is_override(director: dict, threshold: int, grade_scale: dict) -> bool:
    """Re-derived from grade + decision against the active threshold, exactly as
    report does at read time (see Event Schema note on threshold changes)."""
    if director.get("decision") not in ("accept", "accept_with_flaws"):
        return False
    grade = director.get("grade")
    if not isinstance(grade, str) or grade not in grade_scale:
        return False
    return grade_scale[grade] < threshold


# --------------------------------------------------------------------------- #
# reading
# --------------------------------------------------------------------------- #

def _parse_lines(text: str):
    """Yield (line_no, obj or None, problem or None) for every non-blank line.
    Windows line endings and a UTF-8 byte-order mark are tolerated."""
    if text.startswith("\ufeff"):
        text = text[1:]
    for line_no, line in enumerate(text.split("\n"), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except ValueError as exc:
            yield line_no, None, f"not valid JSON ({exc})"
            continue
        if not isinstance(obj, dict):
            yield line_no, None, "line is not a JSON object"
            continue
        yield line_no, obj, None


def _read_text(path: str | os.PathLike) -> str:
    with open(path, "rb") as handle:
        data = handle.read()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: not UTF-8 text ({exc})")


def read_events(path: str | os.PathLike) -> list[dict]:
    """Strict read: every non-blank line must be a JSON object (ValueError names
    the first bad line)."""
    events: list[dict] = []
    for line_no, obj, problem in _parse_lines(_read_text(path)):
        if problem:
            raise ValueError(f"{path}:{line_no}: {problem}")
        events.append(obj)
    return events


def read_events_lenient(path: str | os.PathLike) -> tuple[list[dict], list[str]]:
    """Read what can be read: (events, problems). A missing file is ([], []).
    Used where one damaged line must not block an append (attempt numbering, the
    hook); the problems are reported, never silently swallowed."""
    try:
        text = _read_text(path)
    except FileNotFoundError:
        return [], []
    except (OSError, ValueError) as exc:
        return [], [str(exc)]
    events: list[dict] = []
    problems: list[str] = []
    for line_no, obj, problem in _parse_lines(text):
        if problem:
            problems.append(f"{path}:{line_no}: {problem}")
        else:
            events.append(obj)
    return events, problems


def max_attempt(events: list[dict], workflow_id: str, run_id: str, step: str) -> int:
    best = 0
    for ev in events:
        if (ev.get("workflow_id") == workflow_id and ev.get("run_id") == run_id
                and ev.get("step") == step):
            attempt = ev.get("attempt")
            if isinstance(attempt, int) and not isinstance(attempt, bool):
                best = max(best, attempt)
    return best


_SHA256_RE = re.compile(r"[0-9a-f]{64}")


def file_sha256(path: str | os.PathLike) -> str | None:
    """sha256 of a file's bytes, or None when it is not a readable file. This is
    the artifact fingerprint: two checks with the same fingerprint measured the
    exact same output; a regenerated file (even one saved under the same name)
    has a different fingerprint."""
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
    except OSError:
        return None
    return digest.hexdigest()


def _real_sha256(value) -> str | None:
    """A sha256 taken from a report: 64 hex digits, never the all-zero placeholder."""
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    if not _SHA256_RE.fullmatch(text) or set(text) == {"0"}:
        return None
    return text


def check_attempt(events: list[dict], workflow_id: str, run_id: str, step: str,
                  artifact_sha256: str | None) -> int:
    """Attempt number for a new mechanical_check (Tony, 2026-10-06: the attempt only
    advances when something is actually regenerated, not every time a check runs).

    * The check names the same artifact fingerprint as an event already on the
      step's LATEST attempt (another checker on the same image, or Tony's edited
      file): it shares that attempt.
    * Anything else is a new attempt (latest + 1): a different fingerprint (a
      regenerated output), a fingerprint that only matches an OLDER attempt, or no
      fingerprint at all. No fingerprint is the safe default: without evidence that
      two checks looked at the same output, they are never merged."""
    latest = max_attempt(events, workflow_id, run_id, step)
    if artifact_sha256 and latest:
        for ev in events:
            attempt = ev.get("attempt")
            if (ev.get("workflow_id") == workflow_id and ev.get("run_id") == run_id
                    and ev.get("step") == step and isinstance(attempt, int)
                    and not isinstance(attempt, bool) and attempt == latest
                    and ev.get("artifact_sha256") == artifact_sha256):
                return latest
    return latest + 1


def latest_attempt(path: str | os.PathLike, workflow_id: str, run_id: str, step: str) -> int:
    events, problems = read_events_lenient(path)
    for problem in problems:
        print(f"warning: skipped unreadable ledger line while numbering attempts: "
              f"{problem}", file=sys.stderr)
    return max_attempt(events, workflow_id, run_id, step)


# --------------------------------------------------------------------------- #
# writing
# --------------------------------------------------------------------------- #

def _serialize(event: dict) -> bytes:
    """One JSON line. NaN/Infinity are refused (not JSON). U+2028/U+2029/U+0085 are
    escaped so a reader that splits on every Unicode line break (str.splitlines,
    many JSONL tools) still sees exactly one line per event."""
    text = json.dumps(event, ensure_ascii=False, allow_nan=False)
    text = (text.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
            .replace("\x85", "\\u0085"))
    try:
        return (text + "\n").encode("utf-8")
    except UnicodeEncodeError:
        raise ValueError("event text contains characters that are not valid UTF-8")


def _lock(fd: int, timeout: float | None) -> None:
    if fcntl is None:
        return
    if timeout is None:
        fcntl.flock(fd, fcntl.LOCK_EX)
        return
    deadline = time.monotonic() + timeout
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return
        except BlockingIOError:
            if time.monotonic() >= deadline:
                raise TimeoutError("the ledger is locked by another writer")
            time.sleep(0.02)


def append_event(path: str | os.PathLike, event: dict, *, auto_attempt=None,
                 lock_timeout: float | None = None) -> dict:
    """Append one JSON object on its own line while holding an exclusive lock, so
    two writers never interleave. Earlier bytes are never touched.

    * An event that breaks a schema rule raises ValueError and nothing is written.
    * The ledger's folder must already exist (the ledger never creates folders).
    * If the file does not end in a newline (a hand edit or an older crash), a
      newline is added first so the new line is never glued onto the last one.
    * auto_attempt, if given, is called with the ledger's current events while the
      lock is held and returns the attempt number, so two concurrent writers can
      never both claim the same auto-numbered attempt.
    * lock_timeout (seconds) bounds the wait for the lock (TimeoutError after it).
    Returns the event as written."""
    event = dict(event)
    probe = dict(event, attempt=1) if auto_attempt else event
    errors, _ = validate_event(probe)
    if errors:
        raise ValueError("refusing to write invalid event: " + "; ".join(errors))
    _serialize(probe)  # refuse NaN / bad text before the file is even opened
    p = Path(path)
    if not p.parent.is_dir():
        raise ValueError(f"ledger folder does not exist: {p.parent} (the ledger "
                         "never creates folders; point --ledger at an existing folder)")
    fd = os.open(p, os.O_RDWR | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        _lock(fd, lock_timeout)
        size = os.fstat(fd).st_size
        needs_newline = size > 0 and os.pread(fd, 1, size - 1) != b"\n"
        if auto_attempt:
            data = os.pread(fd, size, 0) if size else b""
            current = [obj for _, obj, problem in
                       _parse_lines(data.decode("utf-8", errors="replace"))
                       if not problem]
            event["attempt"] = int(auto_attempt(current))
            errors, _ = validate_event(event)
            if errors:
                raise ValueError("refusing to write invalid event: " + "; ".join(errors))
        payload = (b"\n" if needs_newline else b"") + _serialize(event)
        written = 0
        while written < len(payload):
            written += os.write(fd, payload[written:])
    finally:
        os.close(fd)  # closing the descriptor releases the lock
    return event


def _type_errors(event: dict) -> list[str]:
    """Type/emptiness checks on top-level fields (only once the shape is known)."""
    errors: list[str] = []
    for key in ID_KEYS:
        value = event.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{key} must be a non-empty string")
    if parse_timestamp(event.get("timestamp")) is None:
        errors.append("timestamp must be an ISO 8601 time with a timezone "
                      "(e.g. 2026-09-19T17:47:00+00:00)")
    for key in OPTIONAL_STRING_KEYS:
        if key in event:
            value = event[key]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{key} must be a non-empty string when present")
    if "cost_usd" in event:
        value = event["cost_usd"]
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value < 0):
            errors.append("cost_usd must be a finite number of 0 or more")
    return errors


def validate_event(event: dict) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a single event dict."""
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(event, dict):
        return ["event is not a JSON object"], []

    for key in REQUIRED_KEYS:
        if key not in event:
            errors.append(f"missing required key {key!r}")

    allowed = set(REQUIRED_KEYS) | {
        "check", "director", "corrects_event_id", "artifact_path",
        "artifact_sha256", "cost_usd", "harness", "failure_type",
    }
    for key in event:
        if key not in allowed:
            errors.append(f"unknown top-level key {key!r}")

    if not errors:  # only run value checks once shape is known
        if event["source"] not in SOURCES:
            errors.append(f"source {event['source']!r} not one of {SOURCES}")
        if event["level"] not in LEVELS:
            errors.append(f"level {event['level']!r} not one of {LEVELS}")
        attempt = event["attempt"]
        if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
            errors.append("attempt must be an integer >= 1")
        if not isinstance(event.get("reason"), str):
            errors.append("reason must be a string")
        errors.extend(_type_errors(event))

    for nested in ("check", "director"):
        if nested in event:
            if not isinstance(event[nested], dict):
                errors.append(f"{nested} must be an object")
                continue
            for child in event[nested]:
                if child not in NESTED_KEYS[nested]:
                    errors.append(f"unknown {nested} key {child!r}")

    # Rule 1: mechanical_check.
    if event.get("source") == "mechanical_check":
        if "director" in event:
            errors.append("mechanical_check must not have director")
        check = event.get("check")
        if not isinstance(check, dict):
            errors.append("mechanical_check must have check")
        else:
            name = check.get("name")
            if not isinstance(name, str) or not name.strip():
                errors.append("check.name must be a non-empty string")
            if check.get("result") not in CHECK_RESULTS:
                errors.append(f"check.result must be one of {CHECK_RESULTS}")
            for field in ("measured", "threshold"):
                if field in check:
                    value = check[field]
                    if value is not None and not (
                        isinstance(value, (int, float)) and not isinstance(value, bool)
                        and math.isfinite(value)
                    ):
                        errors.append(f"check.{field} must be a number or null")
            for field in ("unit", "report_path"):
                if field in check and not isinstance(check[field], str):
                    errors.append(f"check.{field} must be a string")
            reason = event.get("reason")
            if (check.get("result") in ("fail", "error") and isinstance(reason, str)
                    and not reason.strip()):
                warnings.append(f"mechanical {check.get('result')} has an empty reason "
                                "(say what failed)")

    # Rule 2: director_judgment.
    if event.get("source") == "director_judgment":
        if "check" in event:
            errors.append("director_judgment must not have check")
        if event.get("actor") != "Tony":
            errors.append("director_judgment actor must be 'Tony'")
        director = event.get("director")
        if not isinstance(director, dict):
            errors.append("director_judgment must have director")
        else:
            verbatim = director.get("verbatim")
            if not isinstance(verbatim, str) or not verbatim.strip():
                errors.append("director.verbatim must be a non-empty string")
            if director.get("grade") is None and director.get("decision") is None:
                errors.append("director must have at least one of grade/decision")
            grade = director.get("grade")
            if grade is not None and (not isinstance(grade, str)
                                      or grade not in load_grade_scale()):
                errors.append(f"director.grade {grade!r} is not a Grade_Scale key")
            decision = director.get("decision")
            if decision is not None and decision not in DECISIONS:
                errors.append(f"director.decision {decision!r} not one of {DECISIONS}")
            if "below_threshold_override" in director:
                value = director["below_threshold_override"]
                if not isinstance(value, bool):
                    errors.append("director.below_threshold_override must be a boolean")

    # Rule 3: agent_self_correction.
    if event.get("source") == "agent_self_correction":
        if "director" in event:
            errors.append("agent_self_correction must not have director")
        if "check" in event:
            errors.append("agent_self_correction must not have check")
        reason = event.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append("agent_self_correction must have a non-empty reason")
        if not event.get("corrects_event_id"):
            warnings.append("agent_self_correction has no corrects_event_id (recommended)")

    # Rule 5: director_edit (Tony changed the asset himself).
    if event.get("source") == "director_edit":
        if "director" in event:
            errors.append("director_edit must not have director")
        if "check" in event:
            errors.append("director_edit must not have check")
        if event.get("actor") != "Tony":
            errors.append("director_edit actor must be 'Tony'")
        reason = event.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append("director_edit must have a non-empty reason "
                          "(what Tony changed)")

    # Optional failure_type: only values from the fixed FAILURE_TYPES list.
    if "failure_type" in event:
        value = event["failure_type"]
        if not isinstance(value, str) or value not in FAILURE_TYPES:
            errors.append(f"failure_type {value!r} not one of {FAILURE_TYPES}")
        elif (event.get("source") == "mechanical_check"
              and isinstance(event.get("check"), dict)
              and event["check"].get("result") == "pass"):
            warnings.append("failure_type on a mechanical pass (nothing failed)")

    # below_threshold_override is only ever legal inside director (rule 4 handles it).
    if "below_threshold_override" in event:
        errors.append("below_threshold_override may only appear inside director")

    return errors, warnings


def check_files(paths) -> tuple[list[dict], list[str], list[str]]:
    """Read and validate ledger files as one set.

    Returns (valid_events, errors, warnings). errors name file:line for every line
    that is not JSON, not an object, breaks a schema rule, or repeats an event_id
    already seen (which also catches the same ledger passed twice, which would
    double-count every grade). A corrects_event_id that points at no event is a
    warning (the event it fixes may live in another ledger)."""
    valid: list[dict] = []
    errors: list[str] = []
    warnings: list[str] = []
    seen: dict[str, str] = {}
    located: list[tuple[str, dict]] = []
    for path in paths:
        try:
            text = _read_text(path)
        except (OSError, ValueError) as exc:
            errors.append(f"{path}: cannot read ({exc})")
            continue
        for line_no, obj, problem in _parse_lines(text):
            where = f"{path}:{line_no}"
            if problem:
                errors.append(f"{where}: {problem}")
                continue
            errs, warns = validate_event(obj)
            event_id = obj.get("event_id")
            if isinstance(event_id, str) and event_id:
                if event_id in seen:
                    hint = (" - is the same ledger listed twice?"
                            if seen[event_id] == where else "")
                    errs.append(f"duplicate event_id {event_id!r} "
                                f"(first seen at {seen[event_id]}{hint})")
                else:
                    seen[event_id] = where
            errors.extend(f"{where}: {err}" for err in errs)
            warnings.extend(f"{where}: warning: {w}" for w in warns)
            located.append((where, obj))
            if not errs:
                valid.append(obj)
    for where, obj in located:
        ref = obj.get("corrects_event_id")
        if isinstance(ref, str) and ref and ref not in seen:
            warnings.append(f"{where}: warning: corrects_event_id {ref!r} matches no "
                            "event in the files checked")
    return valid, errors, warnings


def load_checked_events(paths) -> list[dict] | None:
    """For report / export: every line must be valid. On any problem, print each
    one to stderr and return None (the caller exits 2)."""
    events, errors, _ = check_files(paths)
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        print(f"error: {len(errors)} problem(s) in the ledger; nothing was reported. "
              "Run `quality_ledger.py validate` for details.", file=sys.stderr)
        return None
    return events


def build_event(*, workflow_id: str, run_id: str, step: str, level: str,
                attempt: int, source: str, actor: str, reason: str,
                check: dict | None = None, director: dict | None = None,
                corrects_event_id: str | None = None, extra: dict | None = None,
                failure_type: str | None = None,
                timestamp: str | None = None) -> dict:
    event: dict = {
        "event_id": str(uuid.uuid4()),
        "timestamp": timestamp or utcnow(),
        "workflow_id": workflow_id,
        "run_id": run_id,
        "step": step,
        "level": level,
        "attempt": attempt,
        "source": source,
        "actor": actor,
        "reason": reason,
    }
    if check is not None:
        event["check"] = check
    if director is not None:
        event["director"] = director
    if corrects_event_id is not None:
        event["corrects_event_id"] = corrects_event_id
    if failure_type is not None:
        event["failure_type"] = failure_type
    if extra:
        for key, value in extra.items():
            event[key] = value
    return event


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #

def _attempt_rule(args, bump: bool, check_sha256: str | None = None,
                  is_check: bool = False):
    """(fixed attempt, auto_attempt callable). Tony's edits are a new version
    (latest + 1). Mechanical checks are a new version unless they fingerprint the
    same artifact as the latest attempt (see check_attempt). Grades and
    self-corrections attach to the latest attempt (or 1). The auto number is
    decided under the ledger lock."""
    if args.attempt is not None:
        return args.attempt, None
    wf, run, step = args.workflow, args.run, args.step
    if is_check:
        return 1, lambda events: check_attempt(events, wf, run, step, check_sha256)
    if bump:
        return 1, lambda events: max_attempt(events, wf, run, step) + 1
    return 1, lambda events: max_attempt(events, wf, run, step) or 1


def _write(args, event: dict, bump: bool, is_check: bool = False) -> dict | None:
    """Append via the shared writer; print warnings; None means exit 2."""
    fixed, auto = _attempt_rule(args, bump, event.get("artifact_sha256"), is_check)
    event["attempt"] = fixed
    if auto is not None:
        # Numbering skips a damaged line; say so instead of numbering silently.
        for problem in read_events_lenient(args.ledger)[1]:
            print(f"warning: skipped unreadable ledger line while numbering attempts: "
                  f"{problem}", file=sys.stderr)
    try:
        written = append_event(args.ledger, event, auto_attempt=auto)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return None
    for warning in validate_event(written)[1]:
        print(f"warning: {warning}", file=sys.stderr)
    return written


def _corrects_exists(args) -> bool:
    """--corrects must name an event that is really in this ledger; a typo would
    otherwise link the correction to nothing, silently."""
    if not args.corrects:
        return True
    events, _ = read_events_lenient(args.ledger)
    if any(e.get("event_id") == args.corrects for e in events):
        return True
    print(f"error: --corrects {args.corrects!r}: no event with that event_id in "
          f"{args.ledger}", file=sys.stderr)
    return False


def cmd_check(args) -> int:
    if args.from_report:
        given = [flag for flag, value in (("--result", args.result),
                                          ("--measured", args.measured),
                                          ("--threshold", args.threshold),
                                          ("--unit", args.unit)) if value is not None]
        if given:
            print(f"error: --from-report takes the result and numbers from the report; "
                  f"do not also pass {', '.join(given)}", file=sys.stderr)
            return 2
        try:
            report = json.loads(Path(args.from_report).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            print(f"error: cannot read report {args.from_report}: {exc}", file=sys.stderr)
            return 2
        if not isinstance(report, dict) or not isinstance(report.get("passed"), bool):
            print(f"error: {args.from_report} has no boolean 'passed' field; "
                  "not a check_storyboard_scale.py report", file=sys.stderr)
            return 2
        failures = report.get("failures") or []
        result = "pass" if report["passed"] else "fail"
        measured, unit = _deciding_value(report, failures)
        report_name = report.get("name")
        if not (isinstance(report_name, str) and report_name.strip()):
            report_name = None
        name = args.name or report_name or _slug_stem(args.from_report)
        threshold = report.get("threshold")
        if (isinstance(threshold, bool) or not isinstance(threshold, (int, float))
                or not math.isfinite(threshold)):
            threshold = None
        check = {"name": name, "result": result}
        if measured is not None:
            check["measured"] = measured
        if threshold is not None:
            check["threshold"] = threshold
        if unit:
            check["unit"] = unit
        check["report_path"] = args.from_report
        reason = args.reason if args.reason else "mechanical check from report"
        tool = report.get("tool")
        actor = tool.strip() if isinstance(tool, str) and tool.strip() \
            else FROM_REPORT_DEFAULT_ACTOR
        # check_storyboard_scale.py already fingerprints the image it measured: that
        # is the artifact signal for free (see check_attempt).
        report_sha = _real_sha256(report.get("storyboard_sha256"))
        report_artifact = report.get("storyboard")
        if not (isinstance(report_artifact, str) and report_artifact.strip()):
            report_artifact = None
    else:
        report_sha = report_artifact = None
        actor = MECHANICAL_CHECK_ACTOR
        if args.result is None:
            print("error: check requires --result pass|fail|error (or --from-report)",
                  file=sys.stderr)
            return 2
        check = {"name": args.name or f"check_{args.step}", "result": args.result}
        if args.measured is not None:
            check["measured"] = args.measured
        if args.threshold is not None:
            check["threshold"] = args.threshold
        if args.unit:
            check["unit"] = args.unit
        reason = args.reason

    # The artifact this check measured. Its fingerprint (sha256) is what lets two
    # different checks on the same generated output share one attempt number.
    extra: dict = {}
    artifact = getattr(args, "artifact", None)
    if artifact:
        sha = file_sha256(artifact)
        if sha is None:
            print(f"error: --artifact {artifact!r}: cannot read that file to fingerprint "
                  "it. Pass the path of the generated image/video this check measured, "
                  "or leave --artifact off (the check then counts as its own attempt).",
                  file=sys.stderr)
            return 2
        if report_sha and report_sha != sha:
            print(f"error: --artifact {artifact!r} is not the file the report measured "
                  f"(report storyboard_sha256 {report_sha}, file sha256 {sha})",
                  file=sys.stderr)
            return 2
        extra = {"artifact_path": artifact, "artifact_sha256": sha}
    elif report_sha:
        extra = {"artifact_sha256": report_sha}
        if report_artifact:
            extra = {"artifact_path": report_artifact.strip(), **extra}

    event = build_event(
        workflow_id=args.workflow, run_id=args.run, step=args.step,
        level=args.level, attempt=1, source="mechanical_check",
        actor=actor, reason=reason or "", check=check, extra=extra or None,
        failure_type=getattr(args, "failure_type", None),
        timestamp=getattr(args, "at", None),
    )
    written = _write(args, event, bump=True, is_check=True)
    if written is None:
        return 2
    print(f"recorded {written['source']} {check.get('result')} "
          f"{args.workflow}/{args.run}/{args.step} attempt {written['attempt']} "
          f"(event_id {written['event_id']})")
    if args.attempt is None and "artifact_sha256" not in written:
        print("note: no --artifact given, so this check counts as its own attempt; "
              "pass the same --artifact on every check of one generated output so "
              "they share one attempt", file=sys.stderr)
    return 0


def _deciding_value(report: dict, failures: list) -> tuple[float | None, str | None]:
    """The deciding number from a real check_storyboard_scale.py report: its failure
    lines state how far off a subject is as a signed percent ("(+70% too big)",
    "(-20%)") or "by 70%". Log the largest deviation in percent; else null."""
    worst = None
    for line in failures if isinstance(failures, list) else []:
        for match in re.finditer(r"(?:\(|by )([+-]?\d+(?:\.\d+)?)%", str(line)):
            value = abs(float(match.group(1)))
            worst = value if worst is None else max(worst, value)
    return (worst, "pct_off") if worst is not None else (None, None)


def _slug_stem(path: str) -> str:
    stem = Path(path).stem
    stem = re.sub(r"(?<!^)(?=[A-Z])", "_", stem).lower()
    return stem or "report"


def cmd_grade(args) -> int:
    verbatim = (args.verbatim or "").strip()
    if not verbatim:
        print("error: grade requires --verbatim (Tony's own words)", file=sys.stderr)
        return 2
    grade_scale = load_grade_scale()
    grade = None
    if args.grade is not None:
        grade = args.grade.strip().upper()  # "b+" and " B+ " mean B+
        if grade not in grade_scale:
            print(f"error: unknown grade {args.grade!r}; expected one of "
                  f"{', '.join(grade_scale)}", file=sys.stderr)
            return 2
    if args.decision is not None and args.decision not in DECISIONS:
        print(f"error: unknown decision {args.decision!r}; expected one of {DECISIONS}",
              file=sys.stderr)
        return 2
    if grade is None and args.decision is None:
        print("error: grade needs --grade and/or --decision", file=sys.stderr)
        return 2
    director: dict = {"verbatim": verbatim}
    if grade is not None:
        director["grade"] = grade
    if args.decision is not None:
        director["decision"] = args.decision

    threshold = int(load_readiness_policy()["threshold"])
    override = director_is_override(director, threshold, grade_scale)
    if override:
        director["below_threshold_override"] = True
    event = build_event(
        workflow_id=args.workflow, run_id=args.run, step=args.step,
        level=args.level, attempt=1, source="director_judgment",
        actor="Tony", reason="", director=director,
        failure_type=getattr(args, "failure_type", None),
        timestamp=getattr(args, "at", None),
    )
    written = _write(args, event, bump=False)
    if written is None:
        return 2
    what = " ".join(x for x in (grade, args.decision) if x)
    print(f"recorded director_judgment {args.workflow}/{args.run}/{args.step} {what} "
          f"attempt {written['attempt']} (event_id {written['event_id']})")
    if override:
        print(f"notice: grade {grade} is below the threshold {threshold}; "
              "this run is logged but will not count toward readiness.")
    return 0


def cmd_self_correct(args) -> int:
    reason = (args.reason or "").strip()
    if not reason:
        print("error: self-correct requires --reason", file=sys.stderr)
        return 2
    if not _corrects_exists(args):
        return 2
    extra = {"harness": args.harness} if getattr(args, "harness", None) else None
    event = build_event(
        workflow_id=args.workflow, run_id=args.run, step=args.step,
        level=args.level, attempt=1, source="agent_self_correction",
        actor=SELF_CORRECTION_ACTOR, reason=reason,
        corrects_event_id=args.corrects, extra=extra,
        failure_type=getattr(args, "failure_type", None),
        timestamp=getattr(args, "at", None),
    )
    written = _write(args, event, bump=False)
    if written is None:
        return 2
    print(f"recorded agent_self_correction {args.workflow}/{args.run}/{args.step} "
          f"attempt {written['attempt']} (event_id {written['event_id']})")
    return 0


def cmd_edit(args) -> int:
    """Tony fixed the asset with his own hands. actor is forced to Tony; reason
    (what he changed) is required. His edited file is a new version of the step,
    so the attempt defaults to the latest attempt + 1."""
    reason = (args.reason or "").strip()
    if not reason:
        print("error: edit requires --reason (what Tony changed)", file=sys.stderr)
        return 2
    if not _corrects_exists(args):
        return 2
    extra = None
    if getattr(args, "artifact", None):
        extra = {"artifact_path": args.artifact}
        # Fingerprint his file when it is readable, so a later check on that same
        # file shares his edit's attempt instead of inventing another one. A path
        # that cannot be read is still recorded as given (unchanged behavior).
        sha = file_sha256(args.artifact)
        if sha:
            extra["artifact_sha256"] = sha
    event = build_event(
        workflow_id=args.workflow, run_id=args.run, step=args.step,
        level=args.level, attempt=1, source="director_edit",
        actor="Tony", reason=reason, corrects_event_id=args.corrects, extra=extra,
        failure_type=getattr(args, "failure_type", None),
        timestamp=getattr(args, "at", None),
    )
    written = _write(args, event, bump=True)
    if written is None:
        return 2
    print(f"recorded director_edit {args.workflow}/{args.run}/{args.step} "
          f"attempt {written['attempt']} (event_id {written['event_id']})")
    return 0


def cmd_validate(args) -> int:
    events, errors, warnings = check_files(args.files)
    for err in errors:
        print(err)
    for warn in warnings:
        print(warn, file=sys.stderr)
    if errors:
        print(f"{len(errors)} problem(s); {len(events)} valid event(s)")
        return 2
    print(f"VALID {len(events)} events")
    return 0


_EPOCH = datetime.min.replace(tzinfo=timezone.utc)


def _ts_key(event: dict) -> datetime:
    return parse_timestamp(event.get("timestamp")) or _EPOCH


def _by_time(events: list[dict]) -> list[dict]:
    """Sort by real time (not by raw string), then event_id for a stable order."""
    return sorted(events, key=lambda e: (_ts_key(e), str(e.get("event_id", ""))))


def is_readiness_final(event: dict) -> bool:
    """A final-level judgment that matters for readiness: every graded final, plus a
    final "redo" with no letter grade (Tony often just says "redo"; without it a
    gradeless final redo never reached the redo gate and the workflow could read
    READY right after Tony rejected a final). A decision-only accept is not a grade
    and is not one of these (a bare approval is never a grade)."""
    director = event.get("director") or {}
    return (event.get("source") == "director_judgment"
            and event.get("level") == "final"
            and (director.get("grade") is not None
                 or director.get("decision") == "redo"))


def latest_final_per_run(events: list[dict]) -> list[dict]:
    """The latest readiness final of each (workflow_id, run_id), oldest run first.

    "Latest" is the real timestamp (backdated --at times included); two finals on
    one run with the very same timestamp are settled by file order, the later line
    wins. Earlier finals on the run are superseded for readiness only: nothing is
    removed from the ledger, export or the per-step deltas."""
    latest: dict[tuple, tuple] = {}
    for index, ev in enumerate(events):
        if not is_readiness_final(ev):
            continue
        key = (str(ev.get("workflow_id")), str(ev.get("run_id")))
        rank = (_ts_key(ev), index)
        if key not in latest or rank >= latest[key][0]:
            latest[key] = (rank, ev)
    return [ev for _, ev in sorted(latest.values(), key=lambda item: item[0])]


def compute_report(events: list[dict], threshold: int, window: int,
                   min_runs: int, grade_scale: dict,
                   max_recent_redo: int | None = None) -> dict:
    grade_scale = grade_scale or load_grade_scale()
    if max_recent_redo is None:
        max_recent_redo = int(load_readiness_policy().get("max_recent_redo", 0))
    by_workflow: dict[str, list[dict]] = {}
    for ev in events:
        by_workflow.setdefault(str(ev.get("workflow_id", "?")), []).append(ev)

    workflows: dict[str, dict] = {}
    steps: list[dict] = []

    # Per-step deltas (include every director grade, including overridden ones).
    step_keys: dict[tuple, list[dict]] = {}
    for ev in events:
        if ev.get("source") != "director_judgment":
            continue
        director = ev.get("director") or {}
        if director.get("grade") is None:
            continue
        key = (str(ev.get("workflow_id")), str(ev.get("run_id")), str(ev.get("step")))
        step_keys.setdefault(key, []).append(ev)
    for (workflow_id, run_id, step), group in sorted(step_keys.items()):
        group = sorted(group, key=lambda e: (e.get("attempt", 0), _ts_key(e)))
        first = group[0]
        latest = group[-1]
        fg = (first.get("director") or {}).get("grade")
        lg = (latest.get("director") or {}).get("grade")
        delta = (grade_scale.get(lg, 0) - grade_scale.get(fg, 0)) if (
            fg in grade_scale and lg in grade_scale) else 0
        steps.append({
            "workflow_id": workflow_id,
            "run_id": run_id,
            "step": step,
            "first_attempt": first.get("attempt"),
            "first_grade": fg,
            "latest_attempt": latest.get("attempt"),
            "latest_grade": lg,
            "delta": delta,
        })

    for workflow_id, evs in sorted(by_workflow.items()):
        mech_fail = sum(1 for e in evs if e.get("source") == "mechanical_check"
                        and (e.get("check") or {}).get("result") == "fail")
        mech_error = sum(1 for e in evs if e.get("source") == "mechanical_check"
                         and (e.get("check") or {}).get("result") == "error")
        self_corrections = sum(1 for e in evs
                               if e.get("source") == "agent_self_correction")
        # Visibility only: Tony's own edits never change n / mean / ready.
        director_edits = sum(1 for e in evs if e.get("source") == "director_edit")
        retry_attempts = collect_attempts(evs)
        unexplained_retries = unexplained(retry_attempts, evs)

        # One final per run: only the run's LATEST readiness final counts (Tony,
        # 2026-10-06); an earlier "C, redo" on a run he later accepted is superseded,
        # not averaged in. The superseded lines stay in the file, export and steps.
        # The override exclusion below is applied to that latest final only.
        finals = latest_final_per_run(evs)
        counted: list[dict] = []
        considered: list[dict] = []  # counted finals + redos, in time order
        overridden_passes = 0
        redo = 0
        for e in finals:
            decision = (e.get("director") or {}).get("decision")
            if director_is_override(e.get("director") or {}, threshold, grade_scale):
                overridden_passes += 1
                continue
            considered.append(e)
            if decision == "redo":
                redo += 1
                continue
            counted.append(e)
        # Rolling window over the counted (non-overridden, non-redo) finals: one per
        # run, so --window N means the N most recent RUNS, not N grade lines.
        recent = counted[-window:] if window and window > 0 else counted
        recent_all = considered[-window:] if window and window > 0 else considered
        recent_redo = sum(1 for e in recent_all
                          if (e.get("director") or {}).get("decision") == "redo")
        n = len(recent)
        mean = None
        raw_mean = None
        if n:
            total = sum(grade_scale.get((e.get("director") or {}).get("grade"), 0)
                        for e in recent)
            raw_mean = total / n
            mean = round(raw_mean, 1)
        # Readiness compares the exact mean: 86.96 must not round up into READY.
        ready = (n >= min_runs and raw_mean is not None and raw_mean >= threshold
                 and recent_redo <= max_recent_redo)
        why = ""
        if not ready:
            parts = []
            if recent_redo > max_recent_redo:
                parts.append(f"recent redo={recent_redo} > max_recent_redo={max_recent_redo}")
            if n < min_runs:
                parts.append(f"n={n} < min_runs={min_runs}")
            if raw_mean is not None and raw_mean < threshold:
                shown = mean if mean < threshold else round(raw_mean, 2)
                parts.append(f"mean={shown} < threshold={threshold}")
            if raw_mean is None:
                parts.append("no graded finals")
            why = "; ".join(parts) or "not ready"
        workflows[workflow_id] = {
            "n": n,
            "mean": mean,
            "ready": ready,
            "why": why,
            "redo": redo,
            "mech_fail": mech_fail,
            "mech_error": mech_error,
            "self_corrections": self_corrections,
            "director_edits": director_edits,
            "unexplained_retries": unexplained_retries,
            "overridden_passes": overridden_passes,
        }
    return {"workflows": workflows, "steps": steps,
            "step_activity": compute_step_activity(events)}


def compute_step_activity(events: list[dict]) -> list[dict]:
    """Per (workflow_id, step) iteration pain, across every run and every level.

    Visibility only: this never feeds n / mean / ready (those stay final-level
    only). It exists so step-level redos, failed checks, self-corrections and Tony's
    own edits show up in report instead of hiding behind a clean final grade."""
    rows: dict[tuple, dict] = {}
    for ev in events:
        key = (str(ev.get("workflow_id", "?")), str(ev.get("step", "?")))
        row = rows.setdefault(key, {
            "workflow_id": key[0], "step": key[1], "max_attempt": 0, "redos": 0,
            "mech_fail": 0, "mech_error": 0, "self_corrections": 0,
            "director_edits": 0,
        })
        attempt = ev.get("attempt")
        if isinstance(attempt, int) and not isinstance(attempt, bool):
            row["max_attempt"] = max(row["max_attempt"], attempt)
        source = ev.get("source")
        if source == "director_judgment":
            if (ev.get("director") or {}).get("decision") == "redo":
                row["redos"] += 1
        elif source == "mechanical_check":
            result = (ev.get("check") or {}).get("result")
            if result == "fail":
                row["mech_fail"] += 1
            elif result == "error":
                row["mech_error"] += 1
        elif source == "agent_self_correction":
            row["self_corrections"] += 1
        elif source == "director_edit":
            row["director_edits"] += 1
    return [rows[key] for key in sorted(rows)]


def collect_attempts(evs: list[dict]) -> dict[tuple, list[int]]:
    """Map (workflow, run, step) -> sorted list of distinct attempts seen."""
    out: dict[tuple, list[int]] = {}
    for e in evs:
        key = (e.get("workflow_id"), e.get("run_id"), e.get("step"))
        attempt = e.get("attempt")
        if isinstance(attempt, int) and not isinstance(attempt, bool):
            out.setdefault(key, []).append(attempt)
    for key in out:
        out[key] = sorted(set(out[key]))
    return out


def unexplained(retry_attempts: dict[tuple, list[int]], evs: list[dict]) -> int:
    """Steps whose attempt number went up with no director grade, no
    self-correction and no director edit that explains the retry."""
    self_corrected = set()
    for e in evs:
        if e.get("source") in ("agent_self_correction", "director_edit"):
            self_corrected.add((e.get("workflow_id"), e.get("run_id"), e.get("step")))
    director_graded = set()
    for e in evs:
        if e.get("source") == "director_judgment":
            director_graded.add((e.get("workflow_id"), e.get("run_id"), e.get("step")))
    count = 0
    for key, attempts in retry_attempts.items():
        if len(set(attempts)) < 2:
            continue
        if key in self_corrected or key in director_graded:
            continue
        count += 1
    return count


def cmd_report(args) -> int:
    try:
        policy = load_readiness_policy()
    except (OSError, ValueError):
        policy = {}
    try:
        threshold = int(args.threshold if args.threshold is not None
                        else policy.get("threshold", 87))
        window = int(args.window if args.window is not None else policy.get("window", 10))
        min_runs = int(args.min_runs if args.min_runs is not None
                       else policy.get("min_runs", 3))
        max_recent_redo = int(policy.get("max_recent_redo", 0))
    except (TypeError, ValueError):
        print("error: Readiness_Policy.json has a value that is not a whole number",
              file=sys.stderr)
        return 2

    events = load_checked_events(args.ledgers)
    if events is None:
        return 2
    report = compute_report(events, threshold, window, min_runs, load_grade_scale(),
                            max_recent_redo)
    if args.json:
        print(json.dumps(report))
        return 0
    return print_report_text(report, markdown=args.markdown)


def print_report_text(report: dict, markdown: bool = False) -> int:
    if markdown:
        print("## Quality Ledger Readiness")
        print()
    if not report["workflows"]:
        # An empty ledger used to print nothing at all, which reads like a crash.
        print("_No events in the ledger yet._" if markdown
              else "no events in the ledger yet")
        return 0
    for workflow_id, w in report["workflows"].items():
        status = "READY" if w["ready"] else f"NOT READY ({w['why']})"
        mean = "null" if w["mean"] is None else f"{w['mean']:.1f}"
        if markdown:
            # Text label says "final" because the JSON "redo" counts final-level
            # redos only; step-level redos are in the Step Activity section below.
            print(f"- **{workflow_id}**: {status} — n {w['n']}, mean {mean}, "
                  f"final redos {w['redo']}, mech fail {w['mech_fail']}, mech error "
                  f"{w['mech_error']}, self-corrections {w['self_corrections']}, "
                  f"director edits {w['director_edits']}, "
                  f"unexplained retries {w['unexplained_retries']}, "
                  f"overridden passes {w['overridden_passes']}")
        else:
            print(f"{workflow_id}: {status} (n={w['n']}, mean={mean}, "
                  f"final_redo={w['redo']}, mech_fail={w['mech_fail']}, "
                  f"mech_error={w['mech_error']}, "
                  f"self_corrections={w['self_corrections']}, "
                  f"director_edits={w['director_edits']}, "
                  f"unexplained_retries={w['unexplained_retries']}, "
                  f"overridden_passes={w['overridden_passes']})")
    print_step_activity(report.get("step_activity") or [], markdown=markdown)
    return 0


def print_step_activity(rows: list[dict], markdown: bool = False) -> None:
    """Where the iteration pain is, per step. Readiness above is untouched."""
    if not rows:
        return
    print()
    if markdown:
        print("### Step Activity (where the redos are; does not change readiness)")
        print()
        print("| workflow | step | max attempt | redos | mech fail | mech error "
              "| self-corrections | director edits |")
        print("|---|---|---|---|---|---|---|---|")
        for r in rows:
            print(f"| {_md_cell(r['workflow_id'])} | {_md_cell(r['step'])} | "
                  f"{r['max_attempt']} | {r['redos']} | {r['mech_fail']} | "
                  f"{r['mech_error']} | {r['self_corrections']} | "
                  f"{r['director_edits']} |")
        return
    print("step activity (where the redos are; does not change readiness):")
    for r in rows:
        print(f"  {r['workflow_id']} / {r['step']}: max_attempt={r['max_attempt']}, "
              f"redos={r['redos']}, mech_fail={r['mech_fail']}, "
              f"mech_error={r['mech_error']}, "
              f"self_corrections={r['self_corrections']}, "
              f"director_edits={r['director_edits']}")


def _md_cell(value) -> str:
    """A '|' inside a step name would split the markdown table cell."""
    return str(value).replace("|", "\\|")


EXPORT_COLUMNS = [
    "event_id", "timestamp", "workflow_id", "run_id", "step", "level",
    "attempt", "source", "actor", "reason", "corrects_event_id",
    "check_name", "check_result", "check_measured", "check_threshold",
    "check_unit", "check_report_path", "director_grade", "director_grade_numeric",
    "director_decision", "director_verbatim", "director_below_threshold_override",
    "artifact_path", "artifact_sha256", "cost_usd", "harness", "failure_type",
]


def flatten(event: dict, grade_scale: dict) -> dict:
    check = event.get("check") or {}
    director = event.get("director") or {}
    grade = director.get("grade")
    return {
        "event_id": event.get("event_id"),
        "timestamp": event.get("timestamp"),
        "workflow_id": event.get("workflow_id"),
        "run_id": event.get("run_id"),
        "step": event.get("step"),
        "level": event.get("level"),
        "attempt": event.get("attempt"),
        "source": event.get("source"),
        "actor": event.get("actor"),
        "reason": event.get("reason"),
        "corrects_event_id": event.get("corrects_event_id"),
        "check_name": check.get("name"),
        "check_result": check.get("result"),
        "check_measured": check.get("measured"),
        "check_threshold": check.get("threshold"),
        "check_unit": check.get("unit"),
        "check_report_path": check.get("report_path"),
        "director_grade": grade,
        "director_grade_numeric": grade_scale.get(grade) if grade in grade_scale else None,
        "director_decision": director.get("decision"),
        "director_verbatim": director.get("verbatim"),
        "director_below_threshold_override": director.get("below_threshold_override"),
        "artifact_path": event.get("artifact_path"),
        "artifact_sha256": event.get("artifact_sha256"),
        "cost_usd": event.get("cost_usd"),
        "harness": event.get("harness"),
        "failure_type": event.get("failure_type"),
    }


def cmd_export(args) -> int:
    events = load_checked_events(args.ledgers)
    if events is None:
        return 2
    grade_scale = load_grade_scale()
    rows = [flatten(e, grade_scale) for e in _by_time(events)]
    if args.format == "jsonl":
        for row in rows:
            print(json.dumps({k: row[k] for k in EXPORT_COLUMNS}))
    else:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=EXPORT_COLUMNS,
                                extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        sys.stdout.write(buffer.getvalue())
    return 0


# --------------------------------------------------------------------------- #
# Report Card backfill
# --------------------------------------------------------------------------- #

# The card's own grade label: at the START of a line (so "Re-Grade:" or
# "Upgrade:" never match), optional bullet/quote/heading and bold, value on the SAME
# line only (a blank "**Grade:**" must never borrow the next line's first letter).
_GRADE_LABEL_RE = re.compile(
    r"^[ \t]*(?:[-*+>#]+[ \t]+)?\**[ \t]*Grade[ \t]*\**[ \t]*:[ \t]*\**[ \t]*"
    r"(?P<value>[^\n]*)$", re.M | re.I)
# The same label as a markdown table row: "| Grade | B+ |".
_GRADE_ROW_RE = re.compile(
    r"^[ \t]*\|[ \t]*\**[ \t]*Grade[ \t]*\**[ \t]*\|[ \t]*(?P<value>[^|\n]*)\|",
    re.M | re.I)
# A grade slot that is filled in but says "not graded yet".
_NOT_GRADED = {"tbd", "pending", "n/a", "na", "none", "-", "—", "?", "todo"}


def _grade_from_value(value: str, grade_scale: dict) -> tuple[str | None, str | None]:
    """(grade, problem) from the text after a Grade label. (None, None) means the
    card is not graded yet (blank, TBD, pending, ...)."""
    text = value.strip().strip("*_`\"' \t").strip()
    if not text or text.lower().rstrip(".") in _NOT_GRADED:
        return None, None
    match = re.match(r"([A-Fa-f])([+-]?)(?![A-Za-z0-9+\-/])", text)
    if match:
        rest = text[match.end():].strip(" \t.,;:!*_)")
        letter, sign = match.group(1), match.group(2)
        # A lowercase bare letter followed by more words ("a work in progress") is
        # English, not a grade.
        if letter.islower() and not sign and rest:
            return None, f"Grade {text!r} does not start with a clear letter grade"
        grade = (letter + sign).upper()
        if grade in grade_scale:
            return grade, None
    return None, f"Grade {text!r} is not a Grade_Scale.json grade"


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """(frontmatter key/values, body). No frontmatter -> ({}, text)."""
    if not text.startswith("---"):
        return {}, text
    rest = text[3:]
    end = rest.find("\n---")
    if end == -1:
        return {}, text
    out: dict = {}
    for line in rest[:end].splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            out[key.strip()] = value.strip()
    body_start = rest.find("\n", end + 4)
    return out, (rest[body_start + 1:] if body_start != -1 else "")


def _parse_report_frontmatter(text: str) -> dict:
    """Extract key: value pairs from a leading YAML frontmatter block."""
    return _split_frontmatter(text)[0]


def read_report_card_grade(text: str, grade_scale: dict) -> tuple[str | None, str | None]:
    """(grade, problem) for one Report Card. (None, None) = no grade given yet.

    Frontmatter Grade wins; the body's FIRST Grade label (line or table row) is the
    card's overall grade. A later section grade (e.g. a thumbnail's) is never used
    as a fallback, and a frontmatter grade that disagrees with the body is refused."""
    if text.startswith("\ufeff"):
        text = text[1:]
    text = text.replace("\r\n", "\n")
    front, body = _split_frontmatter(text)
    front_value = None
    for key in ("Grade", "grade"):
        if key in front and front[key].strip():
            front_value = front[key]
            break
    matches = [m for m in (_GRADE_LABEL_RE.search(body), _GRADE_ROW_RE.search(body)) if m]
    body_match = min(matches, key=lambda m: m.start()) if matches else None

    body_grade = body_problem = None
    if body_match is not None:
        body_grade, body_problem = _grade_from_value(body_match.group("value"), grade_scale)
    if front_value is not None:
        grade, problem = _grade_from_value(front_value, grade_scale)
        if problem:
            return None, f"frontmatter {problem}"
        if grade and body_grade and grade != body_grade:
            return None, (f"frontmatter Grade {grade} disagrees with the body's "
                          f"Grade {body_grade}")
        return grade, None
    if body_match is None:
        return None, None
    return body_grade, body_problem


def _already_backfilled(ledger: str, workflow: str, run_id: str, verbatims: set) -> bool:
    events, _ = read_events_lenient(ledger)
    return any(e.get("source") == "director_judgment"
               and e.get("workflow_id") == workflow and e.get("run_id") == run_id
               and e.get("step") == "final"
               and (e.get("director") or {}).get("verbatim") in verbatims
               for e in events)


def cmd_backfill(args) -> int:
    grade_scale = load_grade_scale()
    threshold = int(load_readiness_policy()["threshold"])
    failed = False
    for path in args.files:
        try:
            raw = Path(path).read_bytes()
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"error: {path}: cannot read ({exc}); skipped", file=sys.stderr)
            failed = True
            continue
        grade, problem = read_report_card_grade(text, grade_scale)
        if problem:
            print(f"error: {path}: {problem}; skipped", file=sys.stderr)
            failed = True
            continue
        if grade is None:
            print(f"no grade yet in {path} (no Grade: value); skipped")
            continue
        # Report Cards live in <Production>/Data/Report_Card.md: the run is the
        # production folder, not the file stem (every card is named Report_Card).
        resolved = Path(path).resolve()
        parent = resolved.parent
        run_id = (parent.parent if parent.name == "Data" else parent).name
        verbatim = f"backfilled from {resolved}"
        director = {"grade": grade, "decision": args.decision, "verbatim": verbatim}
        if director_is_override(director, threshold, grade_scale):
            director["below_threshold_override"] = True
        event = build_event(
            workflow_id=args.workflow, run_id=run_id, step="final", level="final",
            attempt=1, source="director_judgment", actor="Tony", reason="",
            director=director,
        )
        if args.ledger:
            # Idempotent: running the backfill twice must not double-count a run.
            if _already_backfilled(args.ledger, args.workflow, run_id,
                                   {verbatim, f"backfilled from {path}"}):
                print(f"already backfilled run {run_id} from {path}; skipped")
                continue
            try:
                append_event(args.ledger, event)
            except (OSError, ValueError) as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 2
            print(f"wrote director_judgment {grade} {args.decision} run {run_id} "
                  f"from {path}")
        else:
            preview = json.dumps({
                "source": event["source"], "actor": event["actor"], "run_id": run_id,
                "grade": grade, "decision": f"{args.decision} (assumed, --decision)",
                "verbatim": director["verbatim"],
            })
            print(f"{preview}  (dry run; pass --ledger to write)")
    return 2 if failed else 0


# --------------------------------------------------------------------------- #
# session markers (shared with ledger_hook.py)
# --------------------------------------------------------------------------- #

def _markers_dir() -> Path:
    override = os.environ.get("QUALITY_LEDGER_TMP")
    if override:
        return Path(override)
    import tempfile as _tempfile
    return Path(_tempfile.gettempdir())


def safe_session(session_id) -> str:
    """A session id as a safe file-name fragment: no '/' or '..' can steer the
    marker file into another folder."""
    text = re.sub(r"[^A-Za-z0-9._-]", "_", str(session_id or ""))[:128]
    return text.strip(".") or "default"


def marker_path(session_id) -> Path:
    return _markers_dir() / f"{MARKER_PREFIX}{safe_session(session_id)}.json"


def write_marker(path: Path, marker: dict) -> None:
    """Atomic replace: a crash or the hook's deadline mid-write can never leave a
    truncated marker (which would silently switch the ledger off for the session)."""
    path.parent.mkdir(parents=True, exist_ok=True)  # the temp dir, never the workspace
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, path)


def cmd_pending(args) -> int:
    path = marker_path(args.session)
    try:
        marker = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(marker, dict):
            raise ValueError("marker is not an object")
    except (OSError, ValueError):
        print("no pending items (no marker for this session)")
        return 0
    pending = marker.get("pending") or []
    if args.clear:
        marker["pending"] = []
        write_marker(path, marker)
        print(f"cleared {len(pending)} pending item(s)")
        return 0
    if not pending:
        print("no pending items")
        return 0
    for item in pending:
        if not isinstance(item, dict):
            continue
        line = (f"pending {item.get('kind', 'grade')} for {item.get('step')} on "
                f"{item.get('run_id') or marker.get('run_id')}")
        if item.get("problem"):
            line += f" (not recorded: {item['problem']})"
        if item.get("verbatim"):
            line += f"\n  Tony's words: {item['verbatim']}"
        print(line)
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _add_failure_type(p: argparse.ArgumentParser) -> None:
    # choices= makes argparse reject anything off the fixed list with exit code 2.
    p.add_argument("--failure-type", dest="failure_type", choices=FAILURE_TYPES,
                   help="optional, fixed list: " + ", ".join(FAILURE_TYPES))


def _add_at(p: argparse.ArgumentParser) -> None:
    # type= makes argparse reject garbage / timezone-less values with exit code 2.
    p.add_argument("--at", type=parse_at, metavar="ISO8601",
                   help="optional: backdate the event to this UTC time, e.g. "
                        "2026-09-19T17:47:00Z (default: now; never in the future)")


def _add_identity(p: argparse.ArgumentParser) -> None:
    p.add_argument("--ledger", required=True, type=_nonempty_text)
    p.add_argument("--workflow", required=True, type=_nonempty_text)
    p.add_argument("--run", required=True, type=_nonempty_text)
    p.add_argument("--step", required=True, type=_nonempty_text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quality_ledger.py",
        description="Append-only quality ledger for Tony's pipelines.")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("check", help="record a mechanical check (pass/fail/error)")
    _add_identity(p)
    p.add_argument("--level", choices=LEVELS, default="step")
    p.add_argument("--attempt", type=_positive_int,
                   help="default: the latest attempt when --artifact is the same file "
                        "already checked there, else latest attempt + 1")
    p.add_argument("--result", choices=CHECK_RESULTS,
                   help="required unless --from-report is set (then not allowed)")
    p.add_argument("--name", help="check name")
    p.add_argument("--measured", type=_finite_float)
    p.add_argument("--threshold", type=_finite_float)
    p.add_argument("--unit")
    p.add_argument("--reason")
    p.add_argument("--from-report", type=_nonempty_text,
                   help="read a check_storyboard_scale-shaped JSON report")
    p.add_argument("--artifact", "--artifact-path", dest="artifact", type=_nonempty_text,
                   help="the generated file this check measured (must be readable; "
                        "it is fingerprinted with sha256). Checks on the same file "
                        "share one attempt; a regenerated file is a new attempt. "
                        "Without it, every check is its own attempt.")
    _add_failure_type(p)
    _add_at(p)
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("grade", help="record Tony's grade/decision (actor forces to Tony)")
    _add_identity(p)
    # Required, no default (explicit over automatic): a forgotten level must be a hard
    # error, never silently recorded as a final-video grade in the readiness math.
    p.add_argument("--level", choices=LEVELS, required=True,
                   help="required, no default: sub_step, step or final "
                        "(only final grades count toward readiness)")
    p.add_argument("--attempt", type=_positive_int, help="default: latest attempt")
    p.add_argument("--verbatim", help="Tony's own words (required)")
    p.add_argument("--grade", help="Grade_Scale.json key, e.g. B+ (case-insensitive)")
    p.add_argument("--decision", choices=DECISIONS)
    _add_failure_type(p)
    _add_at(p)
    p.set_defaults(func=cmd_grade)

    p = sub.add_parser("self-correct", help="record an agent self-correction")
    _add_identity(p)
    p.add_argument("--level", choices=LEVELS, default="step")
    p.add_argument("--attempt", type=_positive_int, help="default: latest attempt")
    p.add_argument("--reason", required=True)
    p.add_argument("--corrects", dest="corrects", type=_nonempty_text,
                   help="event_id this fixes (must exist in the ledger)")
    _add_failure_type(p)
    _add_at(p)
    p.set_defaults(func=cmd_self_correct)

    p = sub.add_parser("edit", help="record that Tony edited the asset himself "
                                    "(actor forced to Tony)")
    _add_identity(p)
    p.add_argument("--level", choices=LEVELS, default="step")
    p.add_argument("--attempt", type=_positive_int, help="default: latest attempt + 1")
    p.add_argument("--reason", required=True, help="what Tony changed")
    p.add_argument("--corrects", dest="corrects", type=_nonempty_text,
                   help="event_id of the version he fixed (must exist in the ledger)")
    p.add_argument("--artifact", "--artifact-path", dest="artifact", type=_nonempty_text,
                   help="path of Tony's edited file (fingerprinted when readable)")
    _add_failure_type(p)
    _add_at(p)
    p.set_defaults(func=cmd_edit)

    p = sub.add_parser("validate", help="validate one or more ledger files")
    p.add_argument("files", nargs="+")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("report", help="per-workflow readiness report")
    p.add_argument("ledgers", nargs="+")
    p.add_argument("--threshold", type=_threshold_int)
    p.add_argument("--window", type=_positive_int)
    p.add_argument("--min-runs", type=_non_negative_int)
    p.add_argument("--json", action="store_true")
    p.add_argument("--markdown", action="store_true")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("export", help="flat csv/jsonl for a dashboard")
    p.add_argument("ledgers", nargs="+")
    p.add_argument("--format", choices=("csv", "jsonl"), default="csv")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("backfill-report-cards", help="turn Report Card Grade: into director lines")
    p.add_argument("files", nargs="+")
    p.add_argument("--workflow", required=True, type=_nonempty_text)
    p.add_argument("--ledger", type=_nonempty_text)
    p.add_argument("--decision", choices=DECISIONS, default="accept",
                   help="decision to record; a finished Report Card is assumed accepted "
                        "unless you say otherwise (shown in the dry run)")
    p.set_defaults(func=cmd_backfill)

    p = sub.add_parser("pending", help="list (or clear) unresolved items for a session marker")
    p.add_argument("--session", required=True)
    p.add_argument("--clear", action="store_true",
                   help="drop every pending reminder for this session (use when Tony "
                        "says it was not a grade); never writes the ledger")
    p.set_defaults(func=cmd_pending)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
