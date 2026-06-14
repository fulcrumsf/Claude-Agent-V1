#!/usr/bin/env python3
import argparse
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/tonymacbook2025/Documents/Agent-OS")
INGEST_ROOT = WORKSPACE / "000_Ingest" / "Notion-Edit"
RESOURCE = WORKSPACE / "007_Resource_Library"
VISUAL_ASSETS = RESOURCE / "Obsidian_Attachments" / "Visual_Assets"
DOCS = RESOURCE / "Docs"
TOOLS = RESOURCE / "Tools"
TUTORIALS = RESOURCE / "Tutorials"
PROMPTS = RESOURCE / "Prompts"
RESEARCH = RESOURCE / "Research"
WORKFLOWS = RESOURCE / "Workflows"
PROJECTS = RESOURCE / "Project_Ideas"
DESIGN = RESOURCE / "Design_Inspiration"
PERSONAL = RESOURCE / "Personal"
INVESTMENTS = RESOURCE / "Investments"
MODELS = RESOURCE / "Models"
UNDETERMINED = RESOURCE / "Undetermined"

TEXT_EXTS = {".md", ".txt", ".json", ".csv"}
DOC_EXTS = {".pdf", ".pages", ".xlsx"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}


def slugify(name: str) -> str:
    name = Path(name).stem
    name = name.replace("&", " and ")
    name = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")
    return name


def titleize(name: str) -> str:
    parts = slugify(name).split("-")
    fixed = []
    for p in parts:
        if p.upper() in {"AI", "API", "MCP", "GPT", "YT", "PDF", "CSV", "JSON", "POD", "SEO", "UX", "UI", "LLM", "N8N"}:
            fixed.append(p.upper())
        elif p.isdigit():
            fixed.append(p)
        else:
            fixed.append(p[:1].upper() + p[1:].lower())
    return "-".join(fixed)


def ensure_unique(dest_dir: Path, filename: str) -> str:
    candidate = filename
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    i = 2
    while (dest_dir / candidate).exists():
        candidate = f"{stem}-{i}{suffix}"
        i += 1
    return candidate


def path_has(path: str, *needles: str) -> bool:
    p = path.lower()
    return any(n in p for n in needles)


def classify(rel_path: str, stem: str, ext: str):
    p = rel_path.lower()
    s = stem.lower()

    if "software subscriptions" in p:
        return TOOLS, "tool-doc"
    if "tax tracking" in p:
        return INVESTMENTS, "investment"
    if "travel hacking" in p or "travel budget tracker" in p:
        return RESEARCH, "research"
    if "automation workflows" in p:
        return WORKFLOWS, "workflow"
    if "video tutorials" in p:
        return TUTORIALS, "tutorial"
    if "prompting/prompts" in p or "prompting" in p or "prompts" in p:
        return PROMPTS, "prompt"
    if "resource dashboard/resource gallery/bookmarks" in p:
        if path_has(s, "angel", "invest", "trading", "crypto", "wallet", "stock"):
            return INVESTMENTS, "investment"
        if "tutorial" in s:
            return TUTORIALS, "tutorial"
        if "research" in s:
            return RESEARCH, "research"
        return TOOLS, "tool-doc"
    if "resource dashboard/resource gallery/video tutorials" in p:
        return TUTORIALS, "tutorial"
    if "resource dashboard/resource gallery/viral hooks" in p:
        return PROMPTS, "prompt"
    if "resource dashboard/resource gallery/python system map" in p:
        return WORKFLOWS, "workflow"
    if "resource dashboard/resource gallery/prompting" in p:
        return PROMPTS, "prompt"
    if "projects/content creation/channels" in p:
        return PROJECTS, "project-idea"
    if "projects/content creation/voice over collection" in p:
        return PROJECTS, "project-idea"
    if "projects/automation" in p:
        return WORKFLOWS, "workflow"
    if "projects/designs & pod" in p:
        if "keyword search gaps" in p:
            return RESEARCH, "research"
        if "room mockups" in p:
            return DESIGN, "design-inspiration"
        if "art styles tokens" in p or "wallart ideation to creation" in p or "ikigai" in p:
            return PROMPTS, "prompt"
        if "design ideas" in p or "categories" in p or "t-shirt ideas" in p or "sticker ideas" in p or "new project" in p:
            return PROJECTS, "project-idea"
        return PROJECTS, "project-idea"
    if "projects/whop clipping" in p:
        if "video postings tracker" in p:
            return RESEARCH, "research"
        return PROJECTS, "project-idea"
    if "travel budget tracker" in p or "travel hacking" in p:
        return RESEARCH, "research"
    if "bookmarks" in p:
        if "tutorial" in s:
            return TUTORIALS, "tutorial"
        if "research" in s:
            return RESEARCH, "research"
        if path_has(s, "angel", "invest", "trading", "crypto", "wallet", "stock"):
            return INVESTMENTS, "investment"
        if path_has(s, "prompt"):
            return PROMPTS, "prompt"
        return TOOLS, "tool-doc"
    if "resource dashboard" in p:
        return RESEARCH, "research"

    if ext in TEXT_EXTS:
        if "prompt" in s or "template" in s or "instructions" in s or "flux" in s:
            return PROMPTS, "prompt"
        if "workflow" in s or "system map" in s or "n8n" in s:
            return WORKFLOWS, "workflow"
        if "tutorial" in s or "guide" in s or "how to" in s:
            return TUTORIALS, "tutorial"
        if "research" in s or "study" in s or "benchmark" in s:
            return RESEARCH, "research"
        if "idea" in s or "project" in s or "app" in s or "channel" in s:
            return PROJECTS, "project-idea"
        if "invest" in s or "stock" in s or "crypto" in s or "trading" in s:
            return INVESTMENTS, "investment"
        return PROJECTS, "project-idea"

    if ext in DOC_EXTS:
        if "project" in s or "idea" in s:
            return PROJECTS, "project-idea"
        if "travel" in s or "research" in s:
            return RESEARCH, "research"
        if "invoice" in s or "agreement" in s or "agreement" in s:
            return DOCS, "doc"
        return DOCS, "doc"

    if ext in IMAGE_EXTS:
        if "prompt" in s or "template" in s or "storyboard" in s or "instruction" in s:
            return PROMPTS, "prompt"
        if "workflow" in s or "system map" in s or "n8n" in s or "overview" in s:
            return WORKFLOWS, "workflow"
        if "channel" in s or "tiktok" in s or "youtube" in s or "instagram" in s or "clipping" in s:
            return RESEARCH, "research"
        if "banner" in s or "logo" in s or "thumbnail" in s or "mockup" in s or "poster" in s or "style" in s or "design" in s or "art" in s or "living_room" in s or "bedroom" in s or "floral" in s or "abstract" in s:
            return DESIGN, "design-inspiration"
        if "travel" in s or "tour" in s or "personal" in s:
            return PERSONAL, "personal"
        return RESEARCH, "research"

    return UNDETERMINED, "doc"


def frontmatter(title: str, type_name: str, category_name: str, source: str, tags=None):
    tags = tags or []
    tag_block = "\n".join(f"  - {t}" for t in tags)
    return f"""---\ntitle: \"{title}\"\ntype: {type_name}\ncategory: {category_name}\ntags:\n{tag_block}\ncreated: {datetime.now().strftime('%Y-%m-%d')}\nsource: {source}\n---\n"""


def tag_list(category: str, stem: str):
    tags = [category.lower().replace("_", "-")]
    for kw in ["prompt", "tutorial", "workflow", "research", "project", "design", "tool", "investment", "personal"]:
        if kw in stem.lower() and kw not in tags:
            tags.append(kw)
    return tags[:5]


def write_md(dest: Path, title: str, type_name: str, category_name: str, source: str, body: str, tags=None):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        stem = dest.stem
        suffix = dest.suffix
        i = 2
        while dest.exists():
            dest = dest.with_name(f"{stem}-{i}{suffix}")
            i += 1
    if body.lstrip().startswith("---"):
        dest.write_text(body)
        return
    dest.write_text(frontmatter(title, type_name, category_name, source, tags) + "\n" + body)


def process():
    counts = {}
    for p in sorted(INGEST_ROOT.rglob("*")):
        if not p.is_file():
            continue
        if p.name == ".DS_Store":
            p.unlink(missing_ok=True)
            continue
        rel = p.relative_to(INGEST_ROOT).as_posix()
        ext = p.suffix.lower()
        stem = p.stem
        dest_dir, type_name = classify(rel, stem, ext)
        counts[dest_dir.name] = counts.get(dest_dir.name, 0) + 1

        if ext in IMAGE_EXTS:
            image_name = ensure_unique(VISUAL_ASSETS, f"{slugify(stem)}{ext}")
            image_dest = VISUAL_ASSETS / image_name
            image_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(image_dest))
            note_name = ensure_unique(dest_dir, f"{titleize(stem)}.md")
            note_body = f"![[{image_name}]]\n\n## AI Analysis\nImage reference from Notion export: {stem}.\n"
            write_md(
                dest_dir / note_name,
                titleize(stem).replace("-", " "),
                type_name,
                dest_dir.name.lower().replace("_", "-"),
                rel,
                note_body,
                tag_list(dest_dir.name, stem),
            )
            continue

        if ext in TEXT_EXTS:
            target_name = ensure_unique(dest_dir, f"{titleize(stem)}.md")
            body = p.read_text(errors="ignore")
            write_md(dest_dir / target_name, titleize(stem).replace("-", " "), type_name, dest_dir.name.lower(), rel, body, tag_list(dest_dir.name, stem))
            if p.exists():
                p.unlink()
            continue

        if ext in DOC_EXTS:
            target_name = ensure_unique(dest_dir, f"{titleize(stem)}{ext}")
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(dest_dir / target_name))
            continue

    return counts


def main():
    global INGEST_ROOT
    parser = argparse.ArgumentParser(description="Ingest a Notion export folder using deterministic path and filename rules.")
    parser.add_argument("path", nargs="?", default=str(INGEST_ROOT))
    args = parser.parse_args()
    INGEST_ROOT = Path(args.path).resolve()
    counts = process()
    print("Done.")
    for k, v in sorted(counts.items()):
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
