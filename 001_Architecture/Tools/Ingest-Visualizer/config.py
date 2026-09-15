import os

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
INGEST_DIR = os.path.join(WORKSPACE, "000_Ingest")
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")
SCRIPTS_DIR = os.path.join(WORKSPACE, "001_Architecture", "Scripts")

PORT = 8757
THUMB_W = 280

IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")
VIDEO_EXT = (".mp4", ".mov", ".m4v", ".avi", ".webm")

# Named drop zones with a defined ingest pipeline - these are the only
# subfolders this tool looks inside. Everything else under 000_Ingest/ is an
# ad-hoc project folder (per ingest/SKILL.md's own rule) and is never shown
# here without Tony explicitly asking for it some other way.
DROP_ZONES = ("Screenshots", "Images", "Videos", "PDF")

STATE_FILE = os.path.join(INGEST_DIR, ".ingest_visualizer_state.json")
THUMB_CACHE = os.path.expanduser("~/.cache/ingest_visualizer/video_thumbs")
