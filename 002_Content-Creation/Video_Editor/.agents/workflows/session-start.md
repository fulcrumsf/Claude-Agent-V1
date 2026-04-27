---
description: Session startup questionnaire. Run this BEFORE any video creation workflow begins. Collects all context needed to load the right channel bible, set format constraints, and determine if character sheets are required.
---

# Session Start — Video Agent Context Setup

You are a video editing AI agent. Before doing any creative work, you must gather context by asking the user ALL of the following questions in a single message. Do not ask them one at a time — present the full list together so the user can answer efficiently.

## Step 1: Ask All Questions at Once

Present this to the user exactly as a numbered list:

---

Before we start, I need a few quick answers to set up your session:

1. **Channel** — Which channel is this video for? (e.g., Anomalous Wild, or a new channel?)
2. **Topic / Idea** — What is the video about? (One sentence is fine — we'll develop it further.)
3. **Format** — Short-form, medium-form, or long-form?
   - Short-form: 30–90 seconds (YouTube Shorts / TikTok / Reels)
   - Medium-form: 5–12 minutes
   - Long-form: 15–40 minutes
4. **Target Duration** — Approximate duration in minutes (or seconds for short-form)?
5. **Aspect Ratio** — Horizontal (16:9) or Vertical (9:16)?
6. **Recurring Characters** — Does this video feature any characters, animals, or subjects that must look EXACTLY consistent across scenes? (e.g., a specific animal with a particular look, a human character with a specific outfit)
   - Yes → We'll build a character sheet before scripting
   - No → We'll use descriptive text for consistency
7. **Project Status** — Are you starting fresh, or continuing an existing project? If continuing, provide the Project ID (e.g., `0003-Mantis_Shrimp`).

---

## Step 2: Process Answers

Once the user responds, do the following:

### 2a. Load Channel Bible
- If the user names an existing channel, locate and read the corresponding channel bible file from `references/docs/`.
- File naming convention: `[Channel_Name] — CHANNEL BIBLE.md` (e.g., `ANOMALOUS WILD — CHANNEL BIBLE.md`)
- If no channel bible exists for the named channel, inform the user: *"I don't have a channel bible for [Channel Name] yet. Would you like to create one before we proceed, or continue with general best practices?"*
- If continuing without a channel bible, proceed with the universal prompt guidelines from `references/docs/Prompt-best-practices.md`.

### 2b. Set Format Context
Store the following as your working session context:

```
CHANNEL: [channel name]
CHANNEL_BIBLE: [loaded / not found]
TOPIC: [user's topic]
FORMAT: [short / medium / long]
DURATION: [target duration — e.g., "60 seconds" or "8 minutes"]
ASPECT_RATIO: [16:9 or 9:16]
RECURRING_CHARACTERS: [yes / no]
PROJECT_STATUS: [new / continuing: PROJECT_ID]
```

### 2c. Determine Aspect Ratio Rules
- **16:9 (Horizontal):** Primary format. Use for YouTube medium-form and long-form. Models: Veo 3.1, Kling 3.0 pro, Sora 2 landscape.
- **9:16 (Vertical):** Short-form / Reels / TikTok / YouTube Shorts. Models: Veo 3.1 native 9:16, Kling 3.0 pro 9:16, Sora 2 portrait.
- Record this in session context — ALL scene prompts must respect this aspect ratio. Never generate a prompt without the correct ratio prefix or parameter.

### 2d. Determine Scene Duration Budget
Based on format and target duration, calculate the approximate number of scenes and their average length:

| Format | Typical Scene Length | Max Scenes |
|---|---|---|
| Short-form (30–90s) | 3–8 seconds | 5–15 scenes |
| Medium-form (5–12 min) | 5–12 seconds | 30–80 scenes |
| Long-form (15–40 min) | 5–15 seconds | 80–250 scenes |

Inform the user of the estimated scene count based on their duration.

### 2e. Character Sheet Decision
- If **RECURRING_CHARACTERS = yes**, immediately trigger the character sheet workflow **before** any scripting or storyboarding.
- Say: *"You have recurring characters. Let's build their character sheets first so every scene references them correctly. I'll start the character sheet workflow now."*
- Load and execute: `.agents/workflows/character-sheet.md`
- Do NOT proceed to video creation until all character sheets are complete and confirmed.

- If **RECURRING_CHARACTERS = no**, proceed directly to the video creation workflow.
- Load and execute: `.agents/workflows/create-viral-video.md`

### 2f. Continuing a Project
- If PROJECT_STATUS = continuing, locate the existing project directory: `references/outputs/[PROJECT_ID]/`
- Read any existing storyboard, script, or character reference files in that directory before proceeding.
- Summarize what already exists and ask the user where they want to pick up.

## Step 3: Session Summary

Before moving to the next workflow, confirm the session context back to the user in one concise block:

---

**Session loaded:**
- Channel: [channel name]
- Topic: [topic]
- Format: [format] | Duration: [duration] | Ratio: [16:9 or 9:16]
- Estimated scenes: ~[N]
- Character sheets: [required / not required]
- Status: [new project / continuing [ID]]

Ready to proceed. [Next step description.]

---
