---
Category: Automation
tags:
  - seo
  - metadata
  - srt
  - youtube
  - content-creation
  - workflow
Difficulty: Intermediate
Description: SRT to TXT SEO metadata generation rules - channel classification, title, description, hashtag, and keyword generation
---

# 🧠 SRT to TXT – SEO Metadata Generation Rules (V2.0)

This document defines how to generate SEO metadata for short-form videos using transcript context.

---

## ✅ PURPOSE

Read a video transcript and generate the following:

- A compelling **title**
- A rich, SEO-optimized **description**
- A set of relevant **hashtags**
- A standard channel-specific **disclaimer**
- A block of comma-separated **keywords**

Use the transcript to decide which channel the content belongs to. Then apply the formatting and style rules associated with that channel.

---

## 🔍 CHANNEL CLASSIFICATION LOGIC

Decide which channel to use based primarily on the **context of the transcript**, including:

- Topic
- Tone
- Themes

Use the keyword guidance below as **soft hints only**, not as rules. You may infer the appropriate channel even if none of the trigger words are present.

---

### 🎯 Channel 1: The Brain Blueprint

**Niche:** Psychology, neuroscience, mindset, cognitive science

**Tone:** Educational, calm, factual

**Keyword Hints:**

neuroscience, dopamine, habits, behavior, psychology, cognitive science, mindset, productivity, brain hacks, attention, memory, emotional regulation, neural, focus, decision making, mental health

**Hashtags:**

`#brainhealth #mentalhealth #brainpower #psychology #mindset #neuroscience`

**Disclaimer:**

> Disclaimer: This video is for educational and informational purposes only. The content is based on research and general knowledge but should not be taken as professional advice. Always do your own research and consult a qualified expert for personalized guidance.

**Keywords (examples):**

brain health, neuroscience, focus, mindset, cognitive science, psychology, memory improvement, neuroplasticity

---

### 🎭 Channel 2: Reimagined Realms

**Niche:** Alternate history, mythology, speculative fiction, ancient civilizations

**Tone:** Story-driven, imaginative, dramatic

**Keyword Hints:**

alternate history, mythology, Roman Empire, Greece, empires, war, ancient world, what-if scenarios, legends, historical fiction, rulers, timelines, counterfactuals

**Hashtags:**

`#AlternateHistory #HistoricalHumor #WhatIfHistory #HistorySatire #ImaginedHistory #RevisionistHistory`

**Disclaimer:**

> Disclaimer: This channel is a history satire and comedy channel. Some events may or may not have happened as depicted. This content is for entertainment purposes only and should not be taken as factual history. For accurate historical information, please consult a historian or do your own research.

**Keywords (examples):**

Vikings, ancient myths, Greek gods, lost civilizations, timeline shifts, speculative history, medieval empires

---

## 📄 OUTPUT FORMAT

The generated `.txt` should follow this exact structure:

```
mathematica
CopyEdit
[Line 1] Title (~70 characters max, no labels)

[Line 2] (Empty line)

[Line 3+] Description (900–1000 characters, single paragraph, no bullets or questions)

[Next Line] Hashtags (single line)

[Next Line] Disclaimer:
[Next Line] [Channel-specific disclaimer text]

[Final Line] Keywords (comma-separated, lowercase, no label)

```