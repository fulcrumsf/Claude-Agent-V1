import json
import os
import sqlite3
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("PORTAL_DB") or ROOT / "data" / "portal.db")  # PORTAL_DB: test/scratch DB
DB_LOCK = threading.RLock()     # one shared connection; request handlers and art workers write under this lock

SCHEMA = """
CREATE TABLE IF NOT EXISTS ideas (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  lane TEXT NOT NULL DEFAULT 'test',        -- rising | steady | test   (old rows: proven -> steady)
  evidence TEXT NOT NULL DEFAULT '',        -- JSON {why_buyer, why_now, competitors, warning, sources} or plain text
  score REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pool'       -- pool (pending) | shown (visible) | approved (bank) | denied | produced
);
CREATE TABLE IF NOT EXISTS prompts (
  id INTEGER PRIMARY KEY, idea_id INTEGER NOT NULL, text TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS images (
  id INTEGER PRIMARY KEY, idea_id INTEGER NOT NULL, engine TEXT NOT NULL,
  path TEXT NOT NULL, picked INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS listings (
  id INTEGER PRIMARY KEY, idea_id INTEGER NOT NULL, image_id INTEGER NOT NULL,
  folder_seq INTEGER, title TEXT, description TEXT, tags TEXT, price REAL,
  etsy_listing_id TEXT, drive_link TEXT, record TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS steps (
  id INTEGER PRIMARY KEY, listing_id INTEGER NOT NULL, name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',   -- pending | running | done | blocked | failed
  message TEXT NOT NULL DEFAULT '', UNIQUE(listing_id, name)
);
CREATE TABLE IF NOT EXISTS taste_events (
  id INTEGER PRIMARY KEY,
  idea_id INTEGER,
  action TEXT NOT NULL,                     -- approve | deny | comment | seed | note
  comment TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS chat_messages (
  id INTEGER PRIMARY KEY,
  role TEXT NOT NULL,                       -- tony | portal
  text TEXT NOT NULL,
  idea_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS art_rounds (
  id INTEGER PRIMARY KEY,
  idea_id INTEGER NOT NULL,
  round_no INTEGER NOT NULL,
  kind TEXT NOT NULL DEFAULT 'setup',        -- setup (from the style cards) | iterate (from a pick + feedback)
  parent_image_id INTEGER,                   -- iterate: the picked image the feedback is about
  engine TEXT NOT NULL,
  cards TEXT NOT NULL DEFAULT '[]',          -- JSON [card ids]
  chips TEXT NOT NULL DEFAULT '{}',          -- JSON {group: chip id} as Tony set them
  surprise INTEGER NOT NULL DEFAULT 0,
  feedback TEXT NOT NULL DEFAULT '',         -- Tony's words, verbatim
  feedback_summary TEXT NOT NULL DEFAULT '', -- the chat's short reading of them (iterate from chat)
  status TEXT NOT NULL DEFAULT 'writing',    -- writing | generating | done | partial | failed
  message TEXT NOT NULL DEFAULT '',
  writer_note TEXT NOT NULL DEFAULT '',      -- why the agent picked the cards (surprise)
  credits_before REAL, credits_after REAL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  finished_at TEXT
);
CREATE TABLE IF NOT EXISTS art_log (       -- Etsy human-oversight record, append-only
  id INTEGER PRIMARY KEY,
  idea_id INTEGER NOT NULL,
  round_id INTEGER,
  image_id INTEGER,
  action TEXT NOT NULL,                      -- round | prompt | image | pick | feedback | approve | error
  detail TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

# Columns added after the first scaffold. Added in place so an existing portal.db keeps working.
IDEA_COLUMNS = {
    "source": "TEXT NOT NULL DEFAULT 'research'",   # research | seed
    "created_at": "TEXT",
    "decided_at": "TEXT",
    "art_state": "TEXT NOT NULL DEFAULT ''",        # '' | in_progress | approved
    "art_image_id": "INTEGER",                      # the approved final image
}
PROMPT_COLUMNS = {
    "kind": "TEXT NOT NULL DEFAULT 'placeholder'",  # placeholder (from approve) | art (written for a round)
    "round_id": "INTEGER",
    "card_id": "TEXT",
    "created_at": "TEXT",
}
IMAGE_COLUMNS = {
    "round_id": "INTEGER",
    "prompt_id": "INTEGER",
    "slot": "INTEGER",
    "card_id": "TEXT",
    "chips": "TEXT NOT NULL DEFAULT '{}'",          # JSON {group: {"id":..., "by": tony|agent|default}}
    "note": "TEXT NOT NULL DEFAULT ''",             # what this variation tries
    "status": "TEXT NOT NULL DEFAULT 'done'",       # queued | running | done | failed
    "error": "TEXT NOT NULL DEFAULT ''",
    "task_id": "TEXT",
    "outcome": "TEXT NOT NULL DEFAULT ''",          # '' | picked | passed
    "approved": "INTEGER NOT NULL DEFAULT 0",
    "created_at": "TEXT",
}


def _add_columns(con, table, columns):
    have = {r[1] for r in con.execute(f"PRAGMA table_info({table})")}
    for name, ddl in columns.items():
        if name not in have:
            con.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")


def migrate(con):
    _add_columns(con, "ideas", IDEA_COLUMNS)
    _add_columns(con, "prompts", PROMPT_COLUMNS)
    _add_columns(con, "images", IMAGE_COLUMNS)
    con.execute("UPDATE ideas SET lane='steady' WHERE lane='proven'")
    con.execute("UPDATE ideas SET created_at=datetime('now') WHERE created_at IS NULL")
    con.commit()


def connect(path=None):
    p = Path(path) if path else DB_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    migrate(con)
    return con


def get_meta(con, key, default=None):
    row = con.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row[0] if row else default


def set_meta(con, key, value):
    con.execute("INSERT INTO meta(key, value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value))
    con.commit()


def load_config(name):
    return json.loads((ROOT / "config" / f"{name}.json").read_text())
