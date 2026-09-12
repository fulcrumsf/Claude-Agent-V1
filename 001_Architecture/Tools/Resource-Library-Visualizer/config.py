import os
import re

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")
DIRECTORY_MD = os.path.join(RESOURCE_LIB, "Directory.md")

PORT = 8756
THUMB_W = 280
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")

THUMB_CACHE = os.path.expanduser("~/.cache/rl_visualizer/thumbs")
DELETE_DIR = os.path.expanduser("~/Desktop/delete")
QUEUE_DIR = os.path.expanduser("~/Desktop/Resource_Library_Review")
QUEUE_FILE = os.path.join(QUEUE_DIR, "Review_Queue.md")

# Top-level category folders shown as folder-filter buttons / pills.
CATEGORY_FOLDERS = [
    "Clipping", "Prompts", "Research", "Tools", "Tutorials",
    "Workflows", "Models", "Docs", "Design_Inspiration", "Mockups",
    "POD_Prints", "Digital_Products", "Content_Ideas", "Affiliate_Marketing",
    "UGC", "Travel", "Personal", "Investments", "Videos", "Archive", "Undetermined", "OpenAI_History",
]

# Filenames (case-insensitive substring) that mark a structural .md
STRUCTURAL_MARKERS = ("review", "log", "registry", "directory", "agents",
                      "readme", "index", "_map", "manifest")


# ---------- Directory.md is the single source of truth for folder/source/tag
# ---------- definitions - parse it live rather than hardcoding a second copy.

_BULLET_RE = re.compile(r"^\*\s+\*\*([^:*]+):\*\*\s*(.*)$")


def _directory_section(text, header):
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if l.strip() == header), None)
    if start is None:
        return []
    out = []
    for l in lines[start + 1:]:
        if l.startswith("## "):
            break
        m = _BULLET_RE.match(l.strip())
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def tag_vocabulary():
    """Returns an ordered dict {TagName: definition} parsed from Directory.md's
    '## Tag Vocabulary' section - the single fixed list every note's tags must
    come from (1-2 per note)."""
    text = open(DIRECTORY_MD, encoding="utf-8").read()
    return dict(_directory_section(text, "## Tag Vocabulary"))
