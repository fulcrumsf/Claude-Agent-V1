---
title: "Vision File Naming Rules"
type: doc
category: architecture
tags:
  - image-ingest
  - naming-conventions
  - vision-pipeline
  - visual-assets
created: 2026-05-09
source: local
---

# Semantic Screenshot Filenameing Guide

## Purpose

This document improves image and screenshot filename generation by prioritizing semantic meaning over raw OCR extraction.

The goal is to generate filenames based on:
- the actual topic,
- intent,
- subject matter,
- or purpose of the image,

rather than:
- UI labels,
- navigation bars,
- timestamps,
- menu text,
- or random visible OCR fragments.

---

# Core Instruction

When analyzing screenshots or images for filename generation:

> Generate a concise, human-meaningful filename based on the PRIMARY SUBJECT and INTENT of the image.

Ignore:
- app navigation bars,
- operating system UI,
- timestamps,
- notification icons,
- status bars,
- browser chrome,
- sidebars,
- menus,
- buttons,
- decorative text,
- repeated interface elements,
- watermarks,
- and unrelated OCR text.

Focus on:
- the core message,
- central content,
- topic,
- action,
- or informational value of the image.

---

# Filename Prioritization Rules

## Priority Order

The model should prioritize:

1. Main subject matter
2. Semantic meaning
3. User intent
4. Central visual focus
5. Important entities or concepts
6. Supporting OCR only if contextually relevant

The model should NOT prioritize:

- top navigation text
- app tabs
- generic UI labels
- repeated buttons
- timestamps
- carrier info
- status icons
- random visible words

---

# Good vs Bad Examples

## Example 1

Visible UI Text:
- LIVE
- STEM
- Explore
- Following
- Shop

Actual Content:
A TikTok discussing AI landing page prompts and vibe coding.

BAD:
LIVE-STEM-EXPLORE-FOLLOWING-SHOP.png

GOOD:
AI-LANDING-PAGE-PROMPT-TIKTOK.png

BETTER:
VIBE-CODING-BOLT-LANDING-PAGE-TIPS.png

---

## Example 2

Visible OCR:
- Home
- Search
- Notifications
- Messages

Actual Content:
A Twitter thread explaining OpenAI memory systems.

BAD:
HOME-SEARCH-NOTIFICATIONS-MESSAGES.png

GOOD:
OPENAI-MEMORY-SYSTEM-THREAD.png

---

## Example 3

Visible OCR:
- File
- Edit
- View
- Help

Actual Content:
A dashboard showing YouTube analytics growth.

BAD:
FILE-EDIT-VIEW-HELP.png

GOOD:
YOUTUBE-ANALYTICS-GROWTH-DASHBOARD.png

---

# Ideal Filename Characteristics

Good filenames are:

- semantic
- searchable
- short
- meaningful
- human-readable
- context-aware

Bad filenames are:

- OCR dumps
- UI-heavy
- generic
- timestamp-based
- ambiguous
- noisy

---

# Final Principle

The filename should answer:

> "What is this image ACTUALLY about?"

not:

> "What random text happened to be visible?"
