"""Distill approved ChatGPT themes into Tony profile notes.

Run:
    python3 001_Architecture/Scripts/phase2_chatgpt_profile.py
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from phase1_theme_discovery import clean_title, compile_rules, classify, load_conversations


WORKSPACE_ROOT = Path("/Users/tonymacbook2025/Documents/Agent-OS")
HISTORY_DIR = WORKSPACE_ROOT / "007_Resource_Library" / "OpenAI_History"
PROFILE_DIR = WORKSPACE_ROOT / "001_Architecture" / "Memory" / "ChatGPT_Profile"
REPORT_PATH = HISTORY_DIR / "ChatGPT_Theme_Report.md"
IMAGE_MAP_PATH = HISTORY_DIR / "image_map.json"
PROGRESS_PATH = PROFILE_DIR / "phase2_progress.json"

STOPWORDS = {
    "give",
    "have",
    "are",
    "just",
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

THEME_GUIDANCE = {
    "Content Strategy / YouTube": {
        "think": [
            "Tony treats this as packaging and performance engineering: hook, title, thumbnail, and audience fit matter more than generic advice.",
            "He usually wants outputs that can be tested immediately, then refined against engagement or clarity.",
        ],
        "prefs": [
            "Prefers concise, high-signal creative options over theory-heavy strategy.",
            "Looks for repeatable frameworks he can reuse across channels and posts.",
        ],
    },
    "Video Production / Scripting": {
        "think": [
            "Tony approaches video as a sequence problem: pacing, beats, shots, voiceover, and on-screen text need to lock together.",
            "He tends to ask for structure first, then polish, then variations.",
        ],
        "prefs": [
            "Prefers practical shot-level output, not abstract filmmaking talk.",
            "Wants scripts and beats that are easy to hand off into editing or Remotion.",
        ],
    },
    "Travel / Lifestyle": {
        "think": [
            "Tony uses travel prompts as decision support: best neighborhoods, routes, food, logistics, and local tradeoffs.",
            "He tends to optimize for experience quality while keeping the plan concrete and usable.",
        ],
        "prefs": [
            "Prefers practical itineraries over generic travel inspiration.",
            "Often seeks a local-first view of what is actually worth doing.",
        ],
    },
    "Research / General Questions": {
        "think": [
            "Tony uses this theme to triangulate facts quickly and turn broad questions into actionable understanding.",
            "The pattern is less curiosity for its own sake and more useful context for a decision or creative project.",
        ],
        "prefs": [
            "Prefers direct explanations, comparisons, and summaries that get to the point.",
            "Often wants a second pass that narrows from broad overview to the specific answer he can use.",
        ],
    },
    "Image Generation / Design": {
        "think": [
            "Tony is highly iterative here: he cares about composition, style, text behavior, and how the image can be refined across passes.",
            "He treats visuals as a production asset, not just a pretty output.",
        ],
        "prefs": [
            "Prefers strong art direction and explicit constraints over vague aesthetic language.",
            "Often wants multiple variants, small edits, or precise text/layout control.",
        ],
    },
    "Coding / Development": {
        "think": [
            "Tony treats coding like system design plus debugging: he wants the moving parts separated, understood, and then fixed cleanly.",
            "He usually asks for implementation details, failure points, and practical next steps rather than conceptual overviews.",
        ],
        "prefs": [
            "Prefers root-cause analysis over hand-wavy guesses.",
            "Wants changes that fit into an actual workflow or repo, not just a conceptual answer.",
        ],
    },
    "POD / Print-on-Demand": {
        "think": [
            "Tony sees POD as a combinatorial product problem: theme, slogan, audience, layout, and platform constraints all matter at once.",
            "He tends to iterate on phrasing and presentation to improve sellability and clarity.",
        ],
        "prefs": [
            "Prefers output that is ready to test in a listing or design tool.",
            "Often asks for variants tuned for niche appeal rather than broad generic merch.",
        ],
    },
    "AI / Agents / Automation": {
        "think": [
            "Tony uses automation as leverage: if a workflow can be made repeatable, he wants the systemized version.",
            "He usually cares about orchestration, reliability, and how the parts fit into the broader workspace.",
        ],
        "prefs": [
            "Prefers tool-aware solutions and reusable workflows.",
            "Wants automation that saves time without hiding how the system works.",
        ],
    },
    "Business / Tax / Finance": {
        "think": [
            "Tony uses this theme to turn compliance or business rules into plain-language decisions he can act on.",
            "He tends to ask for applied interpretation instead of reading raw policy text.",
        ],
        "prefs": [
            "Prefers conservative, practical guidance with clear next steps.",
            "Wants the answer framed around his actual business setup.",
        ],
    },
    "Writing / Copy": {
        "think": [
            "Tony approaches writing as a conversion and clarity problem: the message has to land fast and read cleanly.",
            "He often wants rewrites, compression, or more punch with less clutter.",
        ],
        "prefs": [
            "Prefers concise, usable copy over polished but verbose prose.",
            "Often asks for stronger hooks, cleaner phrasing, or more human tone.",
        ],
    },
    "Ecommerce / Etsy": {
        "think": [
            "Tony uses ecommerce prompts to tighten the commercial layer: listings, policies, product logic, and store ops.",
            "He tends to connect platform mechanics directly to revenue or workflow decisions.",
        ],
        "prefs": [
            "Prefers practical store-ready output.",
            "Wants listing language and policy text that are easy to deploy.",
        ],
    },
    "Miscellaneous / One-Off Questions": {
        "think": [
            "Tony uses this bucket for fast utility answers that unblock something immediately.",
            "The interaction style is usually transactional: answer, solve, move on.",
        ],
        "prefs": [
            "Prefers a direct answer with minimal ceremony.",
            "Often wants the shortest useful path to resolution.",
        ],
    },
    "Personal Health": {
        "think": [
            "Tony tends to frame health questions as optimization problems: what to do, what to avoid, and what matters most.",
            "He usually wants a practical answer rather than a broad wellness lecture.",
        ],
        "prefs": [
            "Prefers clear, actionable guidance.",
            "Wants safety and practicality first.",
        ],
    },
    "Career / Productivity": {
        "think": [
            "Tony treats productivity and career questions as system design: goals, routines, structure, and execution.",
            "He tends to ask for formats that make action easier immediately.",
        ],
        "prefs": [
            "Prefers tools and structures that reduce friction.",
            "Wants plans that can be executed without a lot of overhead.",
        ],
    },
    "Marketing / Ads": {
        "think": [
            "Tony uses marketing prompts to improve positioning, acquisition, or message testing rather than to brainstorm in the abstract.",
            "He is usually looking for leverage points that can be tested or measured.",
        ],
        "prefs": [
            "Prefers clear metrics, target audiences, and conversion-minded language.",
            "Wants strategy that can actually move traffic or leads.",
        ],
    },
    "Legal / Compliance": {
        "think": [
            "Tony asks legal/compliance questions to understand the boundary conditions of a decision, not to debate law in the abstract.",
            "He wants the practical implication for his situation as quickly as possible.",
        ],
        "prefs": [
            "Prefers cautious, scenario-specific framing.",
            "Wants plain-language implications and action items.",
        ],
    },
    "Gambling / Vegas": {
        "think": [
            "Tony uses this theme to compare odds, risk, and strategy rather than chasing hype.",
            "He tends to prefer clear explanations of expected value and downside exposure.",
        ],
        "prefs": [
            "Prefers straightforward risk framing.",
            "Wants the practical decision, not entertainment advice.",
        ],
    },
    "Uncategorized": {
        "think": [
            "These are long-tail prompts that did not match the classifier cleanly, but they still show Tony's preference for concrete, usable answers.",
            "The residual bucket often contains edge cases, small utilities, and mixed requests that benefit from a second pass later.",
        ],
        "prefs": [
            "Prefers quick clarification when a request is ambiguous.",
            "Still tends to ask for specific outputs rather than general discussion.",
        ],
    },
}


def parse_theme_report():
    rows = []
    for line in REPORT_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        if "Theme" in line and "Count" in line:
            continue
        if "---" in line:
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) >= 3:
            rows.append((parts[0], int(parts[1]), parts[2]))
    return rows


def load_image_map():
    if not IMAGE_MAP_PATH.exists():
        return {}
    return json.loads(IMAGE_MAP_PATH.read_text(encoding="utf-8"))


def user_messages_sample(conversation, max_messages=3):
    mapping = conversation.get("mapping") or {}
    texts = []
    for node in mapping.values():
        message = (node or {}).get("message") or {}
        author = message.get("author") or {}
        if author.get("role") != "user":
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
            texts.append(text[:300])
        if len(texts) >= max_messages:
            break
    return " ".join(texts)[:600]


def tokenize(text):
    return re.findall(r"[a-z][a-z0-9']+", text.lower())


def extract_top_terms(records, limit=10):
    counter = Counter()
    for record in records:
        text = f"{record['title']} {record.get('first_user_message', '')}"
        for token in tokenize(text):
            if token in STOPWORDS or token.isdigit():
                continue
            if len(token) < 3:
                continue
            counter[token] += 1
    return [term for term, _ in counter.most_common(limit)]


def representational_samples(records, limit=3):
    samples = []
    for record in records[:limit]:
        title = clean_title(record["title"])
        message = record.get("first_user_message", "").replace("\n", " ")
        if len(message) > 180:
            message = message[:177].rstrip() + "..."
        samples.append((title, message))
    return samples


def extract_signal(text, words):
    text = text.lower()
    return sum(text.count(word) for word in words)


def style_signals(theme, records):
    count = len(records)
    avg_len = 0
    if records:
        avg_len = sum(len(r.get("first_user_message", "")) for r in records) / count
    message_blob = " ".join(r.get("first_user_message", "") for r in records[:40]).lower()
    title_blob = " ".join(r["title"] for r in records[:40]).lower()
    combined = f"{title_blob} {message_blob}"
    signals = []
    if avg_len < 160:
        signals.append("Short, outcome-first prompts are common.")
    elif avg_len < 320:
        signals.append("Requests usually arrive with enough detail to act on directly.")
    else:
        signals.append("Prompts are often dense, layered, and packed with constraints.")
    if extract_signal(combined, ["remove", "exclude", "without", "simple", "short", "clean"]):
        signals.append("Tony frequently trims, simplifies, or removes unwanted elements.")
    if extract_signal(combined, ["variations", "options", "alternate", "multiple", "different"]):
        signals.append("He often wants several variants instead of one final answer.")
    if extract_signal(combined, ["step", "outline", "structure", "framework", "system"]):
        signals.append("He likes structured breakdowns and repeatable frameworks.")
    if theme in {"Image Generation / Design", "POD / Print-on-Demand", "Video Production / Scripting"}:
        signals.append("Visual direction, layout, and production constraints matter as much as the idea itself.")
    if theme in {"Coding / Development", "AI / Agents / Automation"}:
        signals.append("Technical requests tend to include workflow context, implementation details, or failure modes.")
    if theme in {"Content Strategy / YouTube", "Marketing / Ads", "Writing / Copy"}:
        signals.append("He uses language as a performance lever: packaging, hooks, and conversion matter.")
    if theme in {"Research / General Questions", "Business / Tax / Finance", "Legal / Compliance"}:
        signals.append("He is usually looking for a decision-ready interpretation, not a broad literature review.")
    return signals


def build_image_links(theme, records, image_map):
    if not image_map:
        return []
    conv_ids = {record["conversation_id"] for record in records if record.get("conversation_id")}
    matched = []
    for original, payload in image_map.items():
        conv_id = payload.get("conversation_id")
        renamed = payload.get("renamed") or original
        source = payload.get("source")
        if conv_id == "dalle":
            continue
        if conv_id in conv_ids:
            matched.append((renamed, original, source))
    if theme == "Image Generation / Design":
        for original, payload in image_map.items():
            if payload.get("conversation_id") == "dalle":
                matched.append((payload.get("renamed") or original, original, payload.get("source")))
    seen = []
    for item in matched:
        if item[0] not in seen:
            seen.append(item[0])
    return seen[:5]


def sanitize_stem(theme):
    stem = theme.replace("&", "and").replace("/", "-").replace(":", "")
    stem = re.sub(r"[^A-Za-z0-9-]+", "-", stem)
    stem = re.sub(r"-{2,}", "-", stem).strip("-")
    return f"Tony-{stem}"


def sanitize_tag(theme):
    slug = theme.lower().replace("&", " and ").replace("/", " ")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug


def write_profile(theme, records, count, image_map):
    stem = sanitize_stem(theme)
    path = PROFILE_DIR / f"{stem}.md"
    top_terms = extract_top_terms(records, limit=12)
    samples = representational_samples(records, limit=3)
    signals = style_signals(theme, records)
    guidance = THEME_GUIDANCE.get(theme, {})
    think_bullets = guidance.get("think") or [
        "Tony treats this as a practical problem, not a theoretical one.",
        "He tends to prefer outputs that can be used, tested, or handed off immediately.",
    ]
    pref_bullets = guidance.get("prefs") or [
        "Prefers concise, direct answers with clear next steps.",
        "Often asks for refinements once the first pass is visible.",
    ]
    related_images = build_image_links(theme, records, image_map)

    lines = [
        "---",
        f"tags: [chatgpt-profile, tony-patterns, {sanitize_tag(theme)}]",
        "source: chatgpt-export-2026",
        f"conversations: {count}",
        f"date-synthesized: {datetime.now().date().isoformat()}",
        "---",
        "",
        f"# Tony's {theme}",
        "",
        "## How Tony Thinks About This Domain",
    ]
    lines.extend(f"- {bullet}" for bullet in think_bullets)
    lines.extend([
        "",
        "## Recurring Frameworks & Vocabulary",
    ])
    if top_terms:
        lines.append("- Common terms: " + ", ".join(f"`{term}`" for term in top_terms[:10]))
    else:
        lines.append("- Common terms: none extracted")
    for title, message in samples:
        if message:
            lines.append(f"- `{title}` — {message}")
        else:
            lines.append(f"- `{title}`")
    lines.extend([
        "",
        "## Prompt Style Signals",
    ])
    lines.extend(f"- {signal}" for signal in signals)
    lines.extend([
        "",
        "## Key Preferences & Opinions",
    ])
    lines.extend(f"- {bullet}" for bullet in pref_bullets)
    lines.extend([
        "",
        "## Related Images",
    ])
    if related_images:
        for image in related_images:
            lines.append(f"- ![[{image}]]")
    else:
        lines.append("- None linked from image_map.json")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def load_progress():
    if not PROGRESS_PATH.exists():
        return {"completed_themes": []}
    try:
        return json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"completed_themes": []}


def save_progress(completed_themes):
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_PATH.write_text(
        json.dumps({"completed_themes": completed_themes, "updated_at": datetime.now().isoformat()}, indent=2)
        + "\n",
        encoding="utf-8",
    )


def main():
    REPORT_PATH.read_text(encoding="utf-8")
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    theme_rules = compile_rules()
    conversations = load_conversations()
    image_map = load_image_map()
    approved_themes = [theme for theme, _, _ in parse_theme_report()]

    groups = defaultdict(list)
    for conversation in conversations:
        theme = classify(theme_rules, conversation["title"], conversation.get("first_user_message", ""))
        groups[theme].append(conversation)

    progress = load_progress()
    completed = set(progress.get("completed_themes", []))

    written = []
    for theme in approved_themes:
        if theme in completed:
            continue
        records = groups.get(theme, [])
        path = write_profile(theme, records, len(records), image_map)
        written.append(path)
        completed.add(theme)
        save_progress(sorted(completed))
        print(f"Wrote {path}")

    save_progress(sorted(completed))
    print(f"Completed {len(written)} profile notes in {PROFILE_DIR}")


if __name__ == "__main__":
    main()
