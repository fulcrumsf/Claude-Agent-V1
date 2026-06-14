"""Copy OpenAI export images into OpenAI_Images and build an image map.

Run:
    python3 001_Architecture/Scripts/phase3_image_pipeline.py
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


WORKSPACE_ROOT = Path("/Users/tonymacbook2025/Documents/Agent-OS")
HISTORY_DIR = WORKSPACE_ROOT / "007_Resource_Library" / "OpenAI_History"
DEST_DIR = WORKSPACE_ROOT / "007_Resource_Library" / "Obsidian_Attachments" / "OpenAI_Images"
IMAGE_MAP_PATH = HISTORY_DIR / "image_map.json"
IGNORED_PATH_PARTS = {"Image-Review", "Boxed-Inventory", "Ingest-Review"}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def is_image(path):
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def warn(message):
    print(f"Warning: {message}")


def load_conversations():
    conversations = {}

    for json_path in sorted(HISTORY_DIR.glob("conversations-*.json")):
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            warn(f"Skipping {json_path.name}: {exc}")
            continue

        if isinstance(payload, dict):
            items = payload.values()
        elif isinstance(payload, list):
            items = payload
        else:
            warn(f"Skipping {json_path.name}: unexpected top-level type {type(payload).__name__}")
            continue

        for item in items:
            if not isinstance(item, dict):
                continue
            conversation_id = item.get("conversation_id") or item.get("id")
            if isinstance(conversation_id, str) and conversation_id not in conversations:
                conversations[conversation_id] = item

    return conversations


def part_has_image_asset_pointer(part):
    if isinstance(part, dict):
        if part.get("content_type") == "image_asset_pointer":
            return True
        return any(part_has_image_asset_pointer(value) for value in part.values())
    if isinstance(part, list):
        return any(part_has_image_asset_pointer(item) for item in part)
    return False


def node_has_generated_image(node):
    if not isinstance(node, dict):
        return False

    message = node.get("message")
    if not isinstance(message, dict):
        return False

    author = message.get("author")
    if not isinstance(author, dict):
        return False

    role = author.get("role")
    if role not in {"assistant", "tool"}:
        return False

    content = message.get("content")
    if not isinstance(content, dict):
        return False

    parts = content.get("parts")
    if not isinstance(parts, list):
        return False

    return any(part_has_image_asset_pointer(part) for part in parts)


def conversation_has_generated_image(conversation):
    if not isinstance(conversation, dict):
        return False

    mapping = conversation.get("mapping")
    if not isinstance(mapping, dict):
        return False

    return any(node_has_generated_image(node) for node in mapping.values())


def discover_images():
    discovered = []
    generated_conversations = set()
    skipped_uuid_folders = 0

    for conversation_id, conversation in load_conversations().items():
        if conversation_has_generated_image(conversation):
            generated_conversations.add(conversation_id)

    dalle_dir = HISTORY_DIR / "Dalle-Generations"
    if dalle_dir.exists():
        for path in sorted(dalle_dir.iterdir()):
            if is_image(path):
                discovered.append((path, "dalle", "dalle"))

    for path in sorted(HISTORY_DIR.rglob("*")):
        if not path.is_dir():
            continue
        if IGNORED_PATH_PARTS.intersection(path.parts):
            continue
        if not UUID_PATTERN.fullmatch(path.name):
            continue
        image_dir = path / "image"
        if not image_dir.exists():
            continue
        if path.name not in generated_conversations:
            skipped_uuid_folders += 1
            continue
        for image_path in sorted(image_dir.iterdir()):
            if is_image(image_path):
                discovered.append((image_path, "generated", path.name))

    return discovered, skipped_uuid_folders


def copy_images(discovered):
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    image_map = {}
    copied_dalle = 0
    copied_generated = 0

    print(f"Discovered {len(discovered)} images.")
    for index, (source_path, source_type, conversation_id) in enumerate(discovered, start=1):
        destination_path = DEST_DIR / source_path.name
        if destination_path.exists():
            print(f"[{index}/{len(discovered)}] Skipping existing {source_path.name}")
        else:
            shutil.copy2(source_path, destination_path)
            if source_type == "dalle":
                copied_dalle += 1
            elif source_type == "generated":
                copied_generated += 1
            print(f"[{index}/{len(discovered)}] Copied {source_path.name}")
        image_map[source_path.name] = {
            "renamed": source_path.name,
            "conversation_id": conversation_id,
            "source": source_type,
        }

    IMAGE_MAP_PATH.write_text(json.dumps(image_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return copied_dalle, copied_generated, image_map


def main():
    discovered, skipped_uuid_folders = discover_images()
    copied_dalle, copied_generated, _ = copy_images(discovered)
    print(f"Copied {copied_dalle} dalle images to {DEST_DIR}")
    print(f"Copied {copied_generated} conversation-generated images to {DEST_DIR}")
    print(f"Skipped {skipped_uuid_folders} UUID folders that only contained uploaded images")
    print(f"Image map written to {IMAGE_MAP_PATH}")


if __name__ == "__main__":
    main()
