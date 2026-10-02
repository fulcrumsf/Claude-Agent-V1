---
title: "Humanizer"
type: wiki
category: content-strategy
tags:
  - agent-skills
  - copywriting
  - ai-writing
  - editing
source: "[[007_Resource_Library/Tools/Humanizer-Blader-Agent-Skill]]"
created: 2026-10-01
---

# Humanizer

## What It Is
Humanizer (`blader/humanizer`, MIT) is an agent skill that rewrites AI-sounding text so it reads like a person wrote it, without changing what it says. It is plain Markdown instructions with no scripts, so it works in any agent that supports skills. It answers to `/humanizer` or a plain request like "humanize this". Its pattern list comes from Wikipedia's "Signs of AI writing" page, maintained by WikiProject AI Cleanup.

## Key Concepts
- **One root cause.** A model picks the most statistically likely wording, which suits the widest range of readers. A person writes for one reader and one subject. Each tell is a form of that default choice.
- **Numbered patterns, strongest first.** The ingested README (v3.0.0) lists 25 in five groups: staging instead of stating (not-X-but-Y, one-line closers, deep-sounding sayings, run-ups, arguing with no one), rhythm by rule (forced triads, repeated openings, dashes, stacked qualifiers), inflation and borrowed authority (AI vocabulary, inflated significance, sales language, "serves as" instead of "is"), formatting by rule (decorative bold and headings, curly quotes) and chat leftovers (chatbot residue, knowledge-limit disclaimers). The installed v3.1.0 adds group F, "Writing for the wrong reader", with pattern 26 (re-explaining what the reader already knows).
- **Weak-alone patterns.** Some tells (dashes, passive voice, hyphenated pairs, curly quotes) only count when several appear together, since careful writers use them on purpose.
- **No invented facts.** Names, numbers, dates and quotes must come from the source or the writer. If a sentence needs a missing detail, the skill asks.
- **Shows its work.** For pasted text it returns a first rewrite, a short critique of what still sounds artificial, and the final version. In file mode it changes only prose and leaves code, frontmatter, data and link targets alone.
- **Voice matching.** Give it two or three paragraphs of your own writing and it follows that rhythm, word choice and punctuation, including dashes if you use them.

## How Tony Uses This
Installed 2026-10-01 into `001_Architecture/Skills/humanizer/` (Claude Code, Codex and Gemini CLI) and mirrored to `.agents/skills/humanizer/` for Antigravity. Main uses: a final pass on video scripts and narration for the YouTube channels, Etsy and Amazon listing descriptions, YouTube descriptions, and digital-product copy, so they don't read as machine-written. For voice-matched output on a channel, pass a sample from that channel's existing scripts.

SkillSpector scan (static, 2026-10-01): score 42/100, CAUTION, but every finding is a false positive. The two HIGH `AR2` hits are an example sentence containing "announced without warning", and the MEDIUM `RP1` hits are README install lines. No scripts ship in the installed copy.

## Related
- [[007_Resource_Library/Tools/Humanizer-Blader-Agent-Skill]]
- [[007_Resource_Library/Tools/Humanizer-Claude-Code-Skill]]
- [[Content-Strategy-Framework]]
- [[Find-Skills]]
