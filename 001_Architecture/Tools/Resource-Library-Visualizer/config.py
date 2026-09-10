import os

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")

PORT = 8756
THUMB_W = 280
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")

THUMB_CACHE = os.path.expanduser("~/.cache/rl_visualizer/thumbs")
DELETE_DIR = os.path.expanduser("~/Desktop/delete")
QUEUE_DIR = os.path.expanduser("~/Desktop/Resource_Library_Review")
QUEUE_FILE = os.path.join(QUEUE_DIR, "Review_Queue.md")

# Top-level category folders shown as folder-filter buttons / pills.
CATEGORY_FOLDERS = [
    "Project_Ideas", "Prompts", "Research", "Tools", "Tutorials",
    "Workflows", "Models", "Docs", "Design_Inspiration", "Personal",
    "Investments", "Videos", "Archive", "Undetermined", "OpenAI_History",
]

# Filenames (case-insensitive substring) that mark a structural .md
STRUCTURAL_MARKERS = ("review", "log", "registry", "directory", "agents",
                      "readme", "index", "_map", "manifest")
