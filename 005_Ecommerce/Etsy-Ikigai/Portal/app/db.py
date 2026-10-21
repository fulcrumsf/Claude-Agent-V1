import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "portal.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS ideas (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  lane TEXT NOT NULL DEFAULT 'test',        -- proven | test
  evidence TEXT NOT NULL DEFAULT '',
  score REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pool'       -- pool | shown | approved | denied | produced
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
"""


def connect(path=None):
    p = Path(path) if path else DB_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def load_config(name):
    return json.loads((ROOT / "config" / f"{name}.json").read_text())
