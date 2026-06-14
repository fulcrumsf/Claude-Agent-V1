"""Build a structured ChatGPT brain layer from the OpenAI export.

This script creates:
- theme folders in `007_Resource_Library/OpenAI_History/`
- one readable conversation note per conversation
- image assets in `007_Resource_Library/Obsidian_Attachments/OpenAI_Images/Inputs|Outputs/`
- one asset note per image in `007_Resource_Library/Research/OpenAI_Images/`

Run:
    python3 001_Architecture/Scripts/phase3_chatgpt_structured_ingest.py
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import time
import argparse
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from phase1_theme_discovery import clean_title, compile_rules, classify, load_conversations
from process_image_ingest import process_image


WORKSPACE_ROOT = Path("/Users/tonymacbook2025/Documents/Agent-OS")
HISTORY_DIR = WORKSPACE_ROOT / "007_Resource_Library" / "OpenAI_History"
THEME_INDEX_PATH = HISTORY_DIR / "Index.md"
IMAGE_MAP_PATH = HISTORY_DIR / "image_map.json"
IGNORED_PATH_PARTS = {"Image-Review", "Boxed-Inventory", "Ingest-Review"}

ATTACHMENTS_IMAGE_ROOT = WORKSPACE_ROOT / "007_Resource_Library" / "Obsidian_Attachments" / "OpenAI_Images"
RESEARCH_IMAGE_NOTES_ROOT = WORKSPACE_ROOT / "007_Resource_Library" / "Research" / "OpenAI_Images"
INPUTS_DIR = ATTACHMENTS_IMAGE_ROOT / "Inputs"
OUTPUTS_DIR = ATTACHMENTS_IMAGE_ROOT / "Outputs"
ASSET_NOTES_DIR = RESEARCH_IMAGE_NOTES_ROOT
OUTPUT_INDEX_PATH = ATTACHMENTS_IMAGE_ROOT / "output_index.json"
INPUT_INDEX_PATH = ATTACHMENTS_IMAGE_ROOT / "input_index.json"

OUTPUT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
FALLBACK_MARKER = "No vision summary returned."
BATCH_SIZE = 5
BATCH_PAUSE_SECONDS = 5
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "you",
    "your",
    "from",
    "about",
    "into",
    "can",
    "what",
    "how",
    "why",
    "please",
    "need",
    "make",
    "create",
    "help",
    "want",
    "could",
    "would",
    "show",
    "tell",
    "remove",
    "write",
    "explain",
    "build",
    "best",
    "more",
    "less",
    "like",
    "using",
    "use",
    "not",
    "any",
    "all",
    "one",
    "two",
    "three",
    "new",
    "chat",
    "image",
    "video",
    "style",
    "text",
    "prompt",
    "assistant",
    "please",
    "format",
    "guide",
    "list",
    "version",
    "draft",
    "small",
    "simple",
    "clear",
    "fast",
    "good",
    "better",
}


def slugify_title(title: str) -> str:
    text = re.sub(r"[^\w\s/-]", "", str(title)).strip()
    text = text.replace("/", "-")
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "Untitled"


def slugify_theme(theme: str) -> str:
    text = theme.replace("&", "and").replace("/", "-")
    text = re.sub(r"[^A-Za-z0-9-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "Uncategorized"


def short_id(text: str, length: int = 4) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length].upper()


def tokenize(text: str):
    return re.findall(r"[a-z][a-z0-9']+", text.lower())


def unique_ordered(items):
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def yaml_escape(text):
    return str(text).replace("\\", "\\\\").replace('"', "'")


def extract_first_text_message(conversation, role):
    mapping = conversation.get("mapping") or {}
    for node in mapping.values():
        message = (node or {}).get("message") or {}
        author = message.get("author") or {}
        if author.get("role") != role:
            continue
        content = message.get("content")
        text = ""
        if isinstance(content, dict):
            parts = content.get("parts") or []
            for part in parts:
                if isinstance(part, str) and part.strip():
                    text = part.strip()
                    break
                if isinstance(part, dict):
                    candidate = part.get("text") or part.get("content")
                    if isinstance(candidate, str) and candidate.strip():
                        text = candidate.strip()
                        break
        elif isinstance(content, str):
            text = content.strip()
        if text:
            return text
    return ""


def extract_attachments(conversation):
    attachments = []
    mapping = conversation.get("mapping") or {}
    for node in mapping.values():
        message = (node or {}).get("message") or {}
        author = message.get("author") or {}
        if author.get("role") != "user":
            continue
        metadata = message.get("metadata") or {}
        for item in metadata.get("attachments") or []:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or ""
            att_id = item.get("id") or ""
            mime = item.get("mime_type") or ""
            if not att_id or not name:
                continue
            suffix = Path(name).suffix.lower()
            if suffix not in OUTPUT_EXTENSIONS:
                continue
            attachments.append(
                {
                    "id": att_id,
                    "name": name,
                    "mime_type": mime,
                    "size": item.get("size"),
                    "height": item.get("height"),
                    "width": item.get("width"),
                }
            )
    return attachments


def extract_user_image_asset_pointers(conversation):
    pointers = []
    mapping = conversation.get("mapping") or {}
    for node in mapping.values():
        message = (node or {}).get("message") or {}
        author = message.get("author") or {}
        if author.get("role") != "user":
            continue
        content = message.get("content") or {}
        parts = content.get("parts") if isinstance(content, dict) else []
        for part in parts or []:
            if isinstance(part, dict) and part.get("content_type") == "image_asset_pointer":
                pointer = part.get("asset_pointer") or ""
                if pointer.startswith("file-service://") or pointer.startswith("sediment://"):
                    pointers.append(pointer)
    return unique_ordered(pointers)


def load_image_map():
    if not IMAGE_MAP_PATH.exists():
        return {}
    return json.loads(IMAGE_MAP_PATH.read_text(encoding="utf-8"))


def load_existing_image_index():
    if not OUTPUT_INDEX_PATH.exists():
        return {}
    return json.loads(OUTPUT_INDEX_PATH.read_text(encoding="utf-8"))


def load_input_index():
    if not INPUT_INDEX_PATH.exists():
        return {}
    return json.loads(INPUT_INDEX_PATH.read_text(encoding="utf-8"))


def note_needs_retry(note_path: str) -> bool:
    path = Path(note_path)
    if not path.exists():
        return True
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return True
    return FALLBACK_MARKER in text


def locate_source_file(filename: str):
    for path in HISTORY_DIR.rglob(filename):
        if IGNORED_PATH_PARTS.intersection(path.parts):
            continue
        if path.is_file():
            return path
    return None


def locate_attachment_file(attachment_id: str, attachment_name: str):
    prefix = f"file-{attachment_id}-"
    candidates = []
    for path in HISTORY_DIR.rglob(f"file-{attachment_id}*"):
        if IGNORED_PATH_PARTS.intersection(path.parts):
            continue
        if path.is_file():
            candidates.append(path)
    if candidates:
        candidates.sort(key=lambda p: len(p.name))
        return candidates[0]
    # fallback by name if the attachment id does not match the exported filename
    for path in HISTORY_DIR.rglob(f"*{Path(attachment_name).name}"):
        if IGNORED_PATH_PARTS.intersection(path.parts):
            continue
        if path.is_file() and path.suffix.lower() in OUTPUT_EXTENSIONS:
            return path
    return None


def locate_asset_pointer_file(asset_pointer: str):
    stem = Path(asset_pointer.split("://", 1)[-1]).name
    candidates = []
    for path in HISTORY_DIR.rglob(f"{stem}*"):
        if IGNORED_PATH_PARTS.intersection(path.parts):
            continue
        if path.is_file():
            candidates.append(path)
    if candidates:
        candidates.sort(key=lambda p: len(p.name))
        return candidates[0]
    return None


def process_image_asset(source_path: Path, source_type: str, conversation_meta: dict | None, original_key: str):
    result = process_image(str(source_path)) or {}
    title_case_name = result.get("title_case_name") or slugify_title(source_path.stem)
    ai_description = result.get("ai_description") or "No vision summary returned."
    tags = result.get("tags") or []
    tags = [t for t in tags if isinstance(t, str) and t.strip()]
    tags = unique_ordered([t.lower().replace(" ", "-") for t in tags])[:5]
    if len(tags) < 2:
        tags.extend(["chatgpt-export", "image-archive"])
        tags = unique_ordered(tags)[:5]

    suffix = short_id(original_key)
    stem = f"{title_case_name}-{suffix}"
    destination_dir = OUTPUTS_DIR if source_type == "output" else INPUTS_DIR
    destination_dir.mkdir(parents=True, exist_ok=True)
    ASSET_NOTES_DIR.mkdir(parents=True, exist_ok=True)

    destination_path = destination_dir / f"{stem}{source_path.suffix.lower()}"
    if not destination_path.exists():
        shutil.copy2(source_path, destination_path)

    note_path = ASSET_NOTES_DIR / f"{stem}.md"
    conversation_id = (conversation_meta or {}).get("conversation_id", "")
    conversation_title = (conversation_meta or {}).get("title", "")
    theme = (conversation_meta or {}).get("theme", "Image Generation / Design" if source_type == "output" else "Research / General Questions")

    embed_path = f"Obsidian_Attachments/OpenAI_Images/{destination_dir.name}/{destination_path.name}"
    note = [
        "---",
        'title: "' + stem.replace("-", " ") + '"',
        "type: asset-note",
        f"category: research",
        "tags:",
    ]
    note.extend(f"  - {tag}" for tag in tags)
    note.extend(
        [
            f"conversation_id: \"{conversation_id}\"",
            f'conversation_title: "{yaml_escape(conversation_title)}"',
            f'theme: "{yaml_escape(theme)}"',
            f"image_role: \"{source_type}\"",
            f'original_filename: "{yaml_escape(Path(original_key).name)}"',
            f"created: {datetime.now().date().isoformat()}",
            "---",
            "",
            f"![[{embed_path}]]",
            "",
            "## AI Analysis",
            ai_description,
            "",
        ]
    )
    note_path.write_text("\n".join(note), encoding="utf-8")

    return {
        "original_key": original_key,
        "source_path": str(source_path),
        "destination_path": str(destination_path),
        "note_path": str(note_path),
        "stem": stem,
        "source_type": source_type,
        "conversation_id": conversation_id,
        "conversation_title": conversation_title,
        "theme": theme,
    }


def build_theme_notes(conversations, theme_rules, input_image_links_by_conversation, output_image_notes_by_conversation):
    groups = defaultdict(list)
    for conversation in conversations:
        theme = classify(theme_rules, conversation["title"], conversation.get("first_user_message", ""))
        conversation["theme"] = theme
        groups[theme].append(conversation)

    all_notes = {}
    for theme, records in groups.items():
        theme_dir = HISTORY_DIR / slugify_theme(theme)
        theme_dir.mkdir(parents=True, exist_ok=True)
        sorted_records = []
        for record in records:
            tokens = set(tokenize(record["title"]) + tokenize(record.get("first_user_message", "")))
            sorted_records.append((record, tokens))

        for record, tokens in sorted_records:
            title = clean_title(record["title"])
            stem = f"{slugify_title(title)}-{short_id(record['conversation_id'])}"
            note_path = theme_dir / f"{stem}.md"
            first_user = record.get("first_user_message", "").strip()
            first_assistant = extract_first_text_message(record, "assistant").strip()
            theme_related = []
            for other, other_tokens in sorted_records:
                if other["conversation_id"] == record["conversation_id"]:
                    continue
                overlap = len(tokens & other_tokens)
                if overlap:
                    theme_related.append((overlap, other))
            theme_related.sort(key=lambda item: (-item[0], clean_title(item[1]["title"]).lower()))
            theme_related = [item[1] for item in theme_related[:3]]

            input_links = unique_ordered(input_image_links_by_conversation.get(record["conversation_id"], []))
            output_links = unique_ordered(output_image_notes_by_conversation.get(record["conversation_id"], []))
            note_lines = [
                "---",
                f'title: "{title}"',
                "type: conversation-note",
                f'category: "{slugify_theme(theme).lower()}"',
                "tags:",
                "  - chatgpt-conversation",
                f"  - {slugify_theme(theme).lower()}",
                "  - tony-patterns",
                f'conversation_id: "{record["conversation_id"]}"',
                f'conversation_title: "{yaml_escape(title)}"',
                f'theme: "{yaml_escape(theme)}"',
                f'model: "{record.get("default_model_slug") or ""}"',
                f'created: "{datetime.fromtimestamp(record["create_time"]).date().isoformat() if record.get("create_time") else ""}"',
                "---",
                "",
                f"# {title}",
                "",
                "## Snapshot",
                f"- Theme: [[{slugify_theme(theme)}]]",
                f"- Conversation ID: `{record['conversation_id']}`",
                f"- Model: `{record.get('default_model_slug') or 'unknown'}`",
            ]
            if first_user:
                first_user_snippet = first_user.replace("\n", " ")
                if len(first_user_snippet) > 500:
                    first_user_snippet = first_user_snippet[:497].rstrip() + "..."
                note_lines.append(f"- First user prompt: {first_user_snippet}")
            if first_assistant:
                first_assistant_snippet = first_assistant.replace("\n", " ")
                if len(first_assistant_snippet) > 400:
                    first_assistant_snippet = first_assistant_snippet[:397].rstrip() + "..."
                note_lines.append(f"- First assistant reply: {first_assistant_snippet}")
            note_lines.extend(
                [
                    "",
                    "## Readable Summary",
                ]
            )
            summary_source = first_user or title
            note_lines.append(
                f"- Tony asked for something centered on {title.lower()}. The prompt usually reads like a practical working session rather than a detached question."
            )
            if summary_source:
                summary_snippet = summary_source.replace("\n", " ")
                if len(summary_snippet) > 300:
                    summary_snippet = summary_snippet[:297].rstrip() + "..."
                note_lines.append(f"- Source prompt: {summary_snippet}")
            note_lines.extend(
                [
                    "",
                    "## Related Conversations",
                ]
            )
            if theme_related:
                for other in theme_related:
                    other_title = clean_title(other["title"])
                    other_stem = f"{slugify_title(other_title)}-{short_id(other['conversation_id'])}"
                    note_lines.append(f"- [[{other_stem}]]")
            else:
                note_lines.append("- None found yet in this theme group.")
            note_lines.extend(
                [
                    "",
                    "## Input Images",
                ]
            )
            if input_links:
                for input_image in input_links:
                    note_lines.append(f"- ![[{input_image}]]")
            else:
                note_lines.append("- No linked input images for this conversation.")
            note_lines.extend(
                [
                    "",
                    "## Related Images",
                ]
            )
            if output_links:
                for image_note in output_links:
                    note_lines.append(f"- [[{image_note}]]")
            else:
                note_lines.append("- No linked images for this conversation yet.")
            note_lines.append("")
            note_path.write_text("\n".join(note_lines), encoding="utf-8")
            all_notes[record["conversation_id"]] = str(note_path)

    return all_notes, groups


def build_theme_index(groups):
    lines = [
        "---",
        'title: "ChatGPT History Index"',
        "type: index",
        "category: archive",
        "tags:",
        "  - chatgpt-history",
        "  - index",
        "  - theme-map",
        f"created: {datetime.now().date().isoformat()}",
        "---",
        "",
        "# ChatGPT History Index",
        "",
        "Theme folders created from the approved Phase 1 taxonomy.",
        "",
        "## Themes",
    ]
    for theme, records in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0].lower())):
        lines.append(f"- [[{slugify_theme(theme)}]] — {len(records)} conversations")
    THEME_INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Build structured ChatGPT brain layers from the OpenAI export.")
    parser.add_argument(
        "--mode",
        choices=["all", "inputs", "outputs", "retry-fallback"],
        default="all",
        help="Select which image pass to run.",
    )
    args = parser.parse_args()

    conversations = load_conversations()
    theme_rules = compile_rules()
    image_map = load_image_map()
    existing_image_index = load_existing_image_index()
    existing_input_index = load_input_index()

    conversation_lookup = {conv["conversation_id"]: conv for conv in conversations}
    image_entries = []
    input_image_links_by_conversation = defaultdict(list)
    output_image_notes_by_conversation = defaultdict(list)
    processed_original_keys = set()
    retry_original_keys = set()
    retry_existing_by_key = {}

    for image_record in (existing_image_index.get("images") or []):
        original_key = image_record.get("original_key")
        note_path = image_record.get("note_path")
        if original_key:
            processed_original_keys.add(original_key)
        if original_key and note_path and note_needs_retry(note_path):
            retry_original_keys.add(original_key)
            retry_existing_by_key[original_key] = image_record
    if existing_image_index and retry_original_keys:
        print(f"Retrying {len(retry_original_keys)} image notes with fallback vision text.")

    if args.mode in {"all", "inputs"}:
        # Inputs: every user-uploaded image asset pointer across the export.
        for input_record in (existing_input_index.get("inputs") or []):
            conversation_id = input_record.get("conversation_id") or ""
            destination_path = input_record.get("destination_path") or ""
            if not conversation_id or not destination_path:
                continue
            input_image_links_by_conversation[conversation_id].append(
                f"Obsidian_Attachments/OpenAI_Images/Inputs/{Path(destination_path).name}"
            )
        for conversation in conversations:
            conversation_id = conversation["conversation_id"]
            asset_pointers = extract_user_image_asset_pointers(conversation)
            for asset_pointer in asset_pointers:
                original_key = asset_pointer
                if original_key in processed_original_keys:
                    continue
                source_path = locate_asset_pointer_file(asset_pointer)
                if not source_path:
                    continue
                destination_dir = INPUTS_DIR
                destination_dir.mkdir(parents=True, exist_ok=True)
                destination_path = destination_dir / source_path.name
                if not destination_path.exists():
                    shutil.copy2(source_path, destination_path)
                input_image_links_by_conversation[conversation_id].append(f"Obsidian_Attachments/OpenAI_Images/Inputs/{destination_path.name}")
                processed_original_keys.add(original_key)

    if args.mode in {"all", "outputs", "retry-fallback"}:
        # Outputs: the curated image_map from Phase 3.
        for original_key, payload in image_map.items():
            source_type = "output" if payload.get("source") == "dalle" else "output"
            if original_key == "":  # defensive
                continue
            if args.mode == "retry-fallback" and original_key not in retry_original_keys:
                existing = retry_existing_by_key.get(original_key)
                if existing:
                    image_entries.append(existing)
                    if existing.get("conversation_id"):
                        output_image_notes_by_conversation[existing["conversation_id"]].append(Path(existing["note_path"]).stem)
                continue
            if original_key in processed_original_keys:
                continue
            source_path = locate_source_file(original_key)
            if not source_path:
                continue
            conversation_id = payload.get("conversation_id") or ""
            conversation_meta = conversation_lookup.get(conversation_id, {})
            image_record = process_image_asset(source_path, source_type, conversation_meta, original_key)
            image_entries.append(image_record)
            processed_original_keys.add(original_key)
            if conversation_id:
                output_image_notes_by_conversation[conversation_id].append(Path(image_record["note_path"]).stem)
            if len(image_entries) % BATCH_SIZE == 0:
                print(f"Processed {len(image_entries)} image records; pausing {BATCH_PAUSE_SECONDS}s before the next batch.")
                time.sleep(BATCH_PAUSE_SECONDS)

    # Rebuild grouped conversations with readable notes.
    groups = defaultdict(list)
    for conv in conversations:
        theme = classify(theme_rules, conv["title"], conv.get("first_user_message", ""))
        conv["theme"] = theme
        groups[theme].append(conv)
    build_theme_index(groups)
    conversation_notes, groups = build_theme_notes(conversations, theme_rules, input_image_links_by_conversation, output_image_notes_by_conversation)

    OUTPUT_INDEX_PATH.write_text(
        json.dumps(
            {
                "images": image_entries,
                "conversations": conversation_notes,
                "updated_at": datetime.now().isoformat(),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Built {len(groups)} theme folders.")
    print(f"Wrote {len(conversation_notes)} conversation notes.")
    print(f"Wrote {len(image_entries)} image notes.")
    print(f"Theme index: {THEME_INDEX_PATH}")
    print(f"Output index: {OUTPUT_INDEX_PATH}")


if __name__ == "__main__":
    main()
