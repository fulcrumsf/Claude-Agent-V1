#!/usr/bin/env python3
"""
tools/new_video.py

Entry point for every new video. Runs a terminal questionnaire,
researches viral ideas via Perplexity (using channel case studies for context),
lets you pick one idea, then scaffolds the project folder.

Usage:
  python3 tools/new_video.py

What it creates:
  outputs/<channel_folder>/<id>_<slug>/
    _deliver/
    _review/
      report_card.md
      screenshots/
    001_scenes/            (empty — filled by pipeline_supervisor)
    002_audio/
      narration/
      score/
      sfx/
    003_docs/
      script.md            (blank template)
      beat_sheet.json      (empty stub)
      clip_manifest.json   (empty stub with schema)
"""

from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

import questionary
import requests
from dotenv import load_dotenv

HOME_SECRETS = Path.home() / ".env-secrets"
load_dotenv(HOME_SECRETS)

# ─── Paths ────────────────────────────────────────────────────────────────────

ROOT          = Path(__file__).parent.parent
OUTPUTS_DIR   = ROOT / "outputs"
CHANNELS_DIR  = ROOT / "references" / "channels"

# ─── Channel registry ─────────────────────────────────────────────────────────
# Defaults are read from the channel bible where available.
# format: "long" = 16:9 horizontal | "short" = 9:16 vertical | "both" = ask

CHANNELS = [
    {"id": "001_anomalous_wild",           "name": "Anomalous Wild",           "default_format": "long",  "niche": "nature documentary, strange animals, science"},
    {"id": "002_neonparcel",               "name": "NeonParcel",               "default_format": "short", "niche": "satisfying unboxing, fast-cut product reveals"},
    {"id": "003_reimaginedrealms",         "name": "Reimagined Realms",        "default_format": "both",  "niche": "AI fantasy world-building, alternate history"},
    {"id": "004_kingdoms_and_conquerors",  "name": "Kingdoms & Conquerors",    "default_format": "long",  "niche": "history, strategy, empire-building"},
    {"id": "005_glyphary",                 "name": "Glyphary",                 "default_format": "both",  "niche": "symbols, alphabets, secret meanings"},
    {"id": "006_polyoculis",               "name": "Polyoculis",               "default_format": "both",  "niche": "eyes, vision, perception across species"},
    {"id": "007_robotto_gato",             "name": "Robotto Gato",             "default_format": "short", "niche": "cute robot cats, AI character animation"},
    {"id": "008_borednomad",               "name": "Bored Nomad",              "default_format": "both",  "niche": "travel, offbeat destinations, van life"},
    {"id": "009_unomascreative",           "name": "Unomastre Creative",       "default_format": "both",  "niche": "creative process, AI art, digital design"},
    {"id": "010_room_portal",              "name": "Room Portal",              "default_format": "short", "niche": "satisfying room transformations, interior AI art"},
    {"id": "011_ikigaidigitalstudio",      "name": "Ikigai Digital Studio",    "default_format": "long",  "niche": "digital business, solopreneur, AI productivity"},
    {"id": "012_business_origin_stories",  "name": "Business Origin Stories",  "default_format": "long",  "niche": "startup stories, founder journeys, brand history"},
]

MUSIC_MOODS = [
    "tense / thriller",
    "epic / orchestral",
    "ambient / atmospheric",
    "lo-fi / relaxed",
    "dramatic / emotional",
    "upbeat / energetic",
    "mysterious / eerie",
    "cinematic / documentary",
]

VOICEOVER_TONES = [
    "dramatic — slow, powerful, pauses for effect",
    "calm — measured, authoritative, BBC-style",
    "curious — warm, wondering, slightly playful",
    "urgent — fast, breathless, high stakes",
]

DURATION_OPTIONS_LONG  = ["3–5 min", "5–8 min", "8–12 min"]
DURATION_OPTIONS_SHORT = ["< 30s", "30–60s"]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text[:50].strip("_")


def next_video_id(channel_folder: Path) -> str:
    """Return zero-padded next video ID (e.g. '002') for a channel folder."""
    channel_folder.mkdir(parents=True, exist_ok=True)
    existing = [
        d.name for d in channel_folder.iterdir()
        if d.is_dir() and re.match(r"^\d+_", d.name)
    ]
    if not existing:
        return "002"
    nums = [int(re.match(r"^(\d+)", n).group(1)) for n in existing if re.match(r"^(\d+)", n)]  # type: ignore[union-attr]
    return str(max(nums) + 1).zfill(3)


def read_case_studies(channel_id: str) -> str:
    """Read all case_study.md files for a channel and return combined text (truncated)."""
    case_dir = CHANNELS_DIR / channel_id / "case_studies"
    if not case_dir.exists():
        return ""
    texts = []
    for study_dir in sorted(case_dir.iterdir()):
        md = study_dir / "case_study.md"
        if md.exists():
            content = md.read_text(encoding="utf-8")
            # Keep first 600 chars per case study to stay within API limits
            texts.append(content[:600])
    return "\n\n---\n\n".join(texts)


def read_channel_bible_excerpt(channel_id: str) -> str:
    """Return key sections of the channel bible for research context."""
    channel_dir = CHANNELS_DIR / channel_id
    bibles = list(channel_dir.glob("*content_system.md"))
    if not bibles:
        return ""
    content = bibles[0].read_text(encoding="utf-8")
    # Return first 1500 chars (identity + content pillars)
    return content[:1500]


def research_ideas_perplexity(channel: dict, niche: str, format_label: str) -> list[dict]:
    """
    Call Perplexity API to generate 5-8 viral video ideas.
    Returns list of dicts: {rank, title, hook, why_viral, score}
    """
    api_key = os.getenv("PERPLEXITY_API_KEY", "")
    if not api_key:
        print("\n  ⚠  PERPLEXITY_API_KEY not set — skipping research, using placeholder ideas.")
        return _placeholder_ideas(channel)

    bible_excerpt  = read_channel_bible_excerpt(channel["id"])
    case_study_ctx = read_case_studies(channel["id"])

    context_block = ""
    if bible_excerpt:
        context_block += f"CHANNEL IDENTITY:\n{bible_excerpt}\n\n"
    if case_study_ctx:
        context_block += f"CASE STUDIES (viral videos in this niche):\n{case_study_ctx}\n\n"

    prompt = f"""You are a viral YouTube content strategist specializing in the {niche} niche.

{context_block}
Generate exactly 7 video ideas for a {format_label} YouTube video for this channel.

Rules:
- Each idea must have a counterintuitive or surprising angle — something that defies expectation
- Hook must be answerable in the first 3 seconds
- Ideas must be specific, not generic ("The mantis shrimp punches with the force of a bullet" NOT "Cool animals")
- Score each idea 1-10 on: hook strength, search volume potential, visual richness

Return ONLY a valid JSON array. No other text. Format:
[
  {{
    "rank": 1,
    "title": "short video title",
    "hook": "one sentence opening hook",
    "why_viral": "one sentence — what makes this shareable",
    "score": 8.5
  }},
  ...
]"""

    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "sonar",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1200,
                "temperature": 0.7,
            },
            timeout=30,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip()

        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        ideas = json.loads(raw)
        return sorted(ideas, key=lambda x: float(x.get("score", 0)), reverse=True)

    except Exception as e:
        print(f"\n  ⚠  Research API error: {e} — using placeholders.")
        return _placeholder_ideas(channel)


def _placeholder_ideas(channel: dict) -> list[dict]:
    """Fallback if Perplexity is unavailable."""
    return [
        {"rank": i+1, "title": f"[Research failed — enter topic manually #{i+1}]",
         "hook": "Edit this hook", "why_viral": "Unknown", "score": 0.0}
        for i in range(5)
    ]


# ─── Folder scaffold ──────────────────────────────────────────────────────────

REPORT_CARD_TEMPLATE = """\
# Report Card — {title}

**Channel:** {channel_name}
**Video ID:** {video_id}
**Date Created:** {date}
**Grade:** _not yet graded_

---

## Critique Notes

### Title Card
_[ fill after review ]_

### Audio Sync (Narration → Beat Map)
_[ fill after review ]_

### Audio Layers (Narration / Score / SFX)
_[ fill after review ]_

### Scientific Accuracy (Diagrams / Labels)
_[ fill after review ]_

### Visual Quality (Clips / Images)
_[ fill after review ]_

### Pacing & Transitions
_[ fill after review ]_

---

## Summary Table

| Item | Status | Notes |
|------|--------|-------|
| Title card cinematic | ☐ | |
| Title card has audio | ☐ | |
| Narration is master clock | ☐ | |
| Three-layer audio complete | ☐ | |
| Diagrams text-free (AI) | ☐ | |
| Labels added via Figma/SVG | ☐ | |
| Reference images sourced | ☐ | |
| Clip manifest complete | ☐ | |
| FCPXML exported | ☐ | |
| Crossfades on all transitions | ☐ | |

---

## Workflow Changes for Next Video
_[ fill after review ]_
"""

SCRIPT_TEMPLATE = """\
# Script — {title}

**Channel:** {channel_name}
**Format:** {format_label}
**Hook:** {hook}
**CTA:** {cta}

---

## Scene Breakdown

### S01 — [Scene Name]
**Duration:** ~Xs
**Narration:**
> [Write narration here]

**Visuals:** [Describe]
**Overlays:** [Text overlays, if any]

---

### S02 — [Scene Name]
**Duration:** ~Xs
**Narration:**
> [Write narration here]

**Visuals:** [Describe]
**Overlays:** [Text overlays, if any]

---

_(Add scenes as needed)_

---

## CTA
> {cta}
"""

BEAT_SHEET_STUB = {
    "_note": "Generated by audio_tts.py after ElevenLabs TTS. Do not edit manually.",
    "total_duration_s": None,
    "scenes": []
}

CLIP_MANIFEST_STUB = {
    "_note": "Updated automatically by pipeline_supervisor.py after each generation run.",
    "_schema": {
        "clip_id": "string — e.g. S01A",
        "scene": "string — e.g. S01_anglerfish_hook",
        "type": "video | image | audio",
        "reference_image": "path or null",
        "reference_checked": "true | false",
        "source": "kling | veo3 | flux | elevenlabs | suno | manual",
        "model": "string",
        "prompt_used": "string",
        "output_file": "relative path from project root",
        "notes": "string"
    },
    "clips": []
}


def scaffold_project(
    channel: dict,
    video_id: str,
    slug: str,
    title: str,
    hook: str,
    format_label: str,
    cta: str,
    suno_enabled: bool,
    answers: dict,
) -> Path:
    """Create the full folder structure and stub files."""
    channel_out = OUTPUTS_DIR / channel["id"]
    project_dir = channel_out / f"{video_id}_{slug}"
    project_dir.mkdir(parents=True, exist_ok=True)

    # ── Folders ────────────────────────────────────────────────────────────
    folders = [
        "_deliver",
        "_review/screenshots",
        "001_scenes",
        "002_audio/narration",
        "002_audio/score",
        "002_audio/sfx",
        "003_docs",
    ]
    for f in folders:
        (project_dir / f).mkdir(parents=True, exist_ok=True)

    # ── _review/report_card.md ──────────────────────────────────────────────
    report_card = project_dir / "_review" / "report_card.md"
    report_card.write_text(
        REPORT_CARD_TEMPLATE.format(
            title=title,
            channel_name=channel["name"],
            video_id=video_id,
            date=datetime.today().strftime("%Y-%m-%d"),
        ),
        encoding="utf-8",
    )

    # ── 003_docs/script.md ─────────────────────────────────────────────────
    (project_dir / "003_docs" / "script.md").write_text(
        SCRIPT_TEMPLATE.format(
            title=title,
            channel_name=channel["name"],
            format_label=format_label,
            hook=hook,
            cta=cta,
        ),
        encoding="utf-8",
    )

    # ── 003_docs/beat_sheet.json ───────────────────────────────────────────
    (project_dir / "003_docs" / "beat_sheet.json").write_text(
        json.dumps(BEAT_SHEET_STUB, indent=2),
        encoding="utf-8",
    )

    # ── 003_docs/clip_manifest.json ────────────────────────────────────────
    (project_dir / "003_docs" / "clip_manifest.json").write_text(
        json.dumps(CLIP_MANIFEST_STUB, indent=2),
        encoding="utf-8",
    )

    # ── 003_docs/project_config.json ──────────────────────────────────────
    config = {
        "video_id": video_id,
        "slug": slug,
        "title": title,
        "hook": hook,
        "channel_id": channel["id"],
        "channel_name": channel["name"],
        "format": answers.get("format", format_label),
        "aspect_ratio": "9:16" if "short" in format_label.lower() else "16:9",
        "resolution": "1080x1920" if "short" in format_label.lower() else "1920x1080",
        "duration_estimate": answers.get("duration", ""),
        "voiceover": answers.get("voiceover", True),
        "voiceover_tone": answers.get("voiceover_tone", ""),
        "music_mood": answers.get("music_mood", []),
        "suno_score_enabled": suno_enabled,
        "suno_prompt": "",
        "cta": cta,
        "created_at": datetime.today().isoformat(),
        "project_dir": str(project_dir),
    }
    (project_dir / "003_docs" / "project_config.json").write_text(
        json.dumps(config, indent=2),
        encoding="utf-8",
    )

    return project_dir


# ─── Main questionnaire ───────────────────────────────────────────────────────

def run() -> None:
    print("\n" + "═" * 60)
    print("  NEW VIDEO — Production Setup")
    print("═" * 60 + "\n")

    # ── 1. Channel ─────────────────────────────────────────────────────────
    channel_choices = [f"{c['id']} — {c['name']}" for c in CHANNELS]
    channel_answer  = questionary.select(
        "Which channel is this video for?",
        choices=channel_choices,
    ).ask()
    if not channel_answer:
        sys.exit(0)

    channel = next(c for c in CHANNELS if channel_answer.startswith(c["id"]))
    print(f"\n  ✓ Channel: {channel['name']} ({channel['id']})")

    # ── 2. Format ──────────────────────────────────────────────────────────
    if channel["default_format"] == "long":
        fmt_default = "Long-form (16:9 horizontal)"
        fmt_choices = ["Long-form (16:9 horizontal)", "Short (9:16 vertical)"]
    elif channel["default_format"] == "short":
        fmt_default = "Short (9:16 vertical)"
        fmt_choices = ["Short (9:16 vertical)", "Long-form (16:9 horizontal)"]
    else:
        fmt_default = "Long-form (16:9 horizontal)"
        fmt_choices = ["Long-form (16:9 horizontal)", "Short (9:16 vertical)"]

    format_answer = questionary.select(
        f"Format?  [default: {fmt_default}]",
        choices=fmt_choices,
        default=fmt_default,
    ).ask()
    if not format_answer:
        sys.exit(0)

    is_short     = "short" in format_answer.lower() or "9:16" in format_answer
    format_label = format_answer

    # ── 3. Duration ────────────────────────────────────────────────────────
    dur_choices = DURATION_OPTIONS_SHORT if is_short else DURATION_OPTIONS_LONG
    duration = questionary.select(
        "Estimated duration?",
        choices=dur_choices,
    ).ask()
    if not duration:
        sys.exit(0)

    # ── 4. Voiceover ───────────────────────────────────────────────────────
    has_vo = questionary.confirm("Include voiceover narration?", default=True).ask()

    vo_tone = ""
    if has_vo:
        vo_tone = questionary.select(
            "Voiceover tone?",
            choices=VOICEOVER_TONES,
        ).ask()
        if not vo_tone:
            sys.exit(0)

    # ── 5. Music mood ──────────────────────────────────────────────────────
    music_moods = questionary.checkbox(
        "Music mood? (select all that apply)",
        choices=MUSIC_MOODS,
    ).ask()
    if music_moods is None:
        sys.exit(0)

    # ── 6. Suno score ──────────────────────────────────────────────────────
    suno_enabled = questionary.confirm(
        "Generate a Suno score for this video?", default=True
    ).ask()

    # ── 7. CTA ────────────────────────────────────────────────────────────
    cta = questionary.text(
        "What should viewers do at the end? (CTA)",
        default="Subscribe for more wild animal facts",
    ).ask()
    if cta is None:
        sys.exit(0)

    # ── Research phase ─────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    print(f"  Researching viral ideas for {channel['name']}...")
    print("─" * 60)

    ideas = research_ideas_perplexity(channel, channel["niche"], format_label)

    # ── Display ideas ──────────────────────────────────────────────────────
    print("\n  Top ideas (sorted by score):\n")
    idea_choices = []
    for idea in ideas:
        score_str = f"{idea.get('score', '?'):.1f}" if isinstance(idea.get("score"), (int, float)) else "?"
        label = f"[{score_str}]  {idea['title']}"
        print(f"  {label}")
        print(f"         Hook: {idea.get('hook', '')}")
        print(f"         Why:  {idea.get('why_viral', '')}\n")
        idea_choices.append(label)

    idea_choices.append("✏  Enter my own idea instead")

    # ── Pick idea ──────────────────────────────────────────────────────────
    print("─" * 60)
    picked = questionary.select(
        "Which idea do you want to make?",
        choices=idea_choices,
    ).ask()
    if not picked:
        sys.exit(0)

    if picked.startswith("✏"):
        title = questionary.text("Enter the video title:").ask() or "untitled"
        hook  = questionary.text("Enter the opening hook:").ask() or ""
    else:
        idx   = idea_choices.index(picked)
        idea  = ideas[idx]
        title = idea["title"]
        hook  = idea.get("hook", "")

    # ── Confirm slug / folder name ─────────────────────────────────────────
    slug_raw  = slugify(title)
    video_id  = next_video_id(OUTPUTS_DIR / channel["id"])
    folder_preview = f"{video_id}_{slug_raw}"

    confirmed_slug = questionary.text(
        "Folder name (edit if needed):",
        default=folder_preview,
    ).ask()
    if not confirmed_slug:
        sys.exit(0)

    # Re-parse id and slug from final confirmed name
    match = re.match(r"^(\d+)_(.+)$", confirmed_slug)
    if match:
        video_id = match.group(1)
        slug_raw = match.group(2)
    else:
        slug_raw = slugify(confirmed_slug)

    # ── Build ──────────────────────────────────────────────────────────────
    answers = {
        "format":        format_label,
        "duration":      duration,
        "voiceover":     has_vo,
        "voiceover_tone": vo_tone,
        "music_mood":    music_moods,
    }

    project_dir = scaffold_project(
        channel      = channel,
        video_id     = video_id,
        slug         = slug_raw,
        title        = title,
        hook         = hook,
        format_label = format_label,
        cta          = cta,
        suno_enabled = suno_enabled,
        answers      = answers,
    )

    # ── Done ───────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("  ✓  Project scaffolded successfully")
    print("═" * 60)
    print(f"\n  Folder : {project_dir}")
    print(f"  Title  : {title}")
    print(f"  Hook   : {hook}")
    print(f"  Format : {format_label} | {duration}")
    print(f"  Suno   : {'enabled' if suno_enabled else 'disabled'}")
    print()
    print("  Next steps:")
    print("  1. Write the script  →  003_docs/script.md")
    print("  2. Generate narration  →  python3 tools/audio_tts.py <project_dir>")
    print("     (outputs beat_sheet.json automatically)")
    print("  3. Build clip prompts  →  003_docs/ai_prompts.json")
    print("  4. Run generation  →  python3 tools/pipeline_supervisor.py <project_dir>")
    print()


if __name__ == "__main__":
    run()
