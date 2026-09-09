import os
import sys
import importlib.util
import pathlib
from datetime import datetime

_here = pathlib.Path(__file__).parent


def _load(name):
    key = f"rlv_{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[key] = m
    spec.loader.exec_module(m)
    return m


config = _load("config")

OPEN_HDR = "## Batch — open (started {ts})\n"


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _read():
    try:
        return open(config.QUEUE_FILE, encoding="utf-8").read()
    except FileNotFoundError:
        return ""


def _write(txt):
    os.makedirs(config.QUEUE_DIR, exist_ok=True)
    open(config.QUEUE_FILE, "w", encoding="utf-8").write(txt)


def _ensure_open_batch():
    txt = _read()
    if "## Batch — open" not in txt:
        if txt and not txt.endswith("\n"):
            txt += "\n"
        txt += OPEN_HDR.format(ts=_now())
        _write(txt)


def add_comment(note_path, text):
    _ensure_open_batch()
    entry = f"\n- [ ] COMMENT  {note_path}\n      \"{text.strip()}\"\n"
    _write(_read() + entry)


def log_delete(note_path):
    _ensure_open_batch()
    entry = f"\n- [x] DELETE   {note_path}  (moved to {config.DELETE_DIR} {_now()})\n"
    _write(_read() + entry)


def finalize():
    _ensure_open_batch()
    txt = _read()
    start = txt.index("## Batch — open")
    batch = txt[start:]
    body = batch[batch.index("\n") + 1:]
    comments = body.count("- [ ] COMMENT")
    deletes = body.count("] DELETE")
    sealed_hdr = f"## Batch — FINALIZED {_now()}  ({comments} comments, {deletes} deletes)\n"
    new = txt[:start] + sealed_hdr + body
    new = new.rstrip() + "\n\n" + OPEN_HDR.format(ts=_now())
    _write(new)
    return sealed_hdr + body
