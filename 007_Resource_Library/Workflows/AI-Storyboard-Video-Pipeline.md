---
title: "AI Storyboard Video Pipeline"
type: workflow
category: video-production
tags:
  - video-production
  - ai-automation
  - storyboard
created: 2026-05-08
source: local
---

# AI Storyboard → Image → Video Automation Pipeline

*A modular, long-form video generation system driven by narration beats, visual logic, and continuity-aware AI.*

---

## High-Level Purpose

This workflow is designed to **automatically generate complete long-form videos** from an input concept and/or narration audio.

The system:

1. Analyzes narration (voiceover or host dialogue)
2. Breaks it into semantic beats
3. Converts beats into **high-quality text-to-image prompts**
4. Converts images into **continuous image-to-video segments**
5. Seamlessly stitches segments into a single long-form video
6. Composites a speaking avatar/host over the footage
7. Outputs a final, editor-ready or fully finished video

The design prioritizes:

* Visual continuity
* Narrative clarity
* Style consistency with controlled flexibility
* Automation without creative collapse

---

## Core Design Philosophy

### 1. Beats, Not Scripts

The system does **not** treat narration as a rigid script.
Instead, narration is analyzed into **beats**—semantic units of meaning that can breathe visually.

This allows:

* Longer clips than narration length
* Editor-led pacing
* Natural pauses and visual emphasis
* Better image-to-video motion quality

---

### 2. “House Style” with Flexible Shot Modalities

Each video belongs to a **Show** (analogous to a TV show), defined in a database.

A Show defines:

* Niche topic
* Target audience
* Contrarian angle
* Visual tone
* Art direction
* Editing philosophy

Within a Show:

* **Core invariants** remain constant
  (realism level, lighting feel, color science, motion-graphics restraint)
* **Shot modalities may vary per beat**
  (macro footage, archival look, scientific overlays, diagrams, X-ray views, minimal animation)

This allows visual variety **without stylistic chaos**.

---

### 3. Continuity Is Encouraged, Not Enforced

The system is designed for **continuity-aware generation**, not continuity-blocking rules.

Key principle:

> Never refuse to generate a shot because continuity is imperfect.

Continuity is supported downstream using:

* Reference-frame–based video extension (VO 3.1 Extend)
* Match-cut–friendly shot design
* Consistent subject identity and environments when possible

If a beat requires a visual jump, the system allows it and relies on editing and transitions to smooth the cut.

---

## Workflow Overview (End-to-End)

### Phase 1: Video & Show Selection

**Node types:**

* Database lookup
* Conditional routing
* Set nodes

Steps:

1. A database row represents **one video**
2. The row specifies:

   * Which Show it belongs to
   * Whether it is narrated or non-narrated
   * Optional constraints (e.g., aspect ratio, tone overrides)
3. The workflow routes into the appropriate pipeline
   (narrative vs. compilation)

---

### Phase 2: Audio Analysis (Narrative Pipeline Only)

**Node types:**

* Audio analysis
* Transcription
* Semantic chunking

Steps:

1. Voiceover or host audio is analyzed
2. Dialogue is segmented into narration beats
3. Each beat includes:

   * Text
   * Timing
   * Intent
   * Narrative role

---

### Phase 3: Storyboard / Prompt Generation

**Node types:**

* AI Agent (Storyboard Agent)
* Loop Over Items (batched)
* Structured Output Parser (JSON Schema)

Key characteristics:

* Beats are processed in **small batches** (e.g., 3 at a time)
* Prevents model fatigue and prompt dilution
* Produces **text-to-image prompts**, not final edits
* Enforces strict JSON for downstream reliability

Each shot includes:

* Image prompt (photoreal, cinematic, generator-ready)
* Negative prompt
* Motion intent (for image-to-video)
* Continuity notes
* Optional on-screen text

---

### Phase 4: Text-to-Image Generation

**Node types:**

* HTTP Request (Google V3.1 or equivalent)
* Asset storage

Steps:

1. Each prompt generates a high-quality still image
2. Images are stored and indexed by scene/beat
3. These images become **keyframes**, not final visuals

---

### Phase 5: Image-to-Video (Continuity-Aware)

**Node types:**

* HTTP Request (Image-to-video)
* FFmpeg (frame extraction)

Process:

1. Scene 1 generates a short video from its image
2. The **last frame** of Scene 1 is extracted
3. Scene 2 uses that frame as a reference (VO 3.1 Extend)
4. This continues sequentially, creating:

   * Natural motion continuity
   * Match cuts
   * A “single take” feel across scenes

---

### Phase 6: Video Assembly

**Node types:**

* FFmpeg
* File system operations

Steps:

1. All scene videos are concatenated
2. Timing is trimmed to narration beats
3. Visual breathing room is preserved
4. The result is one continuous background video

---

### Phase 7: Avatar / Host Compositing

**Node types:**

* FFmpeg
* Green-screen keying
* Overlay compositing

Steps:

1. A speaking avatar (human or AI host) is generated or imported
2. Green background is keyed out
3. Host is composited over the generated footage
4. Audio is synchronized with narration

---

### Phase 8: Final Output

**Outputs may include:**

* Final MP4
* Editor-ready intermediate files
* Metadata for publishing or analytics

---

## Show System (Critical Abstraction)

Each Show acts like a **production bible**.

Example: **Strange Facts**

* Focus: Evolutionary oddities & bizarre biology
* Tone: Cinematic realism grounded in real science
* Visual language:

  * Macro footage
  * Documentary realism
  * Subtle scientific overlays
* Rule: No cartoon styling, ever

Other Shows may allow:

* Stylized animation
* Surreal realism
* Comedy through tonal contrast

The workflow injects Show parameters early and enforces them consistently downstream.

---

## Why This Architecture Works

* **Scales across content types**
* **Avoids single-prompt collapse**
* **Supports multiple shows without rewrites**
* **Keeps creative intent explicit**
* **Separates thinking from rendering**
* **Plays nicely with future editor intervention**

---

## Status

This document reflects:

* The intended end-state architecture
* Design philosophy
* Node-level responsibilities

Not all components may be implemented yet.
The workflow is intentionally modular so parts can evolve independently.

---

*This file is meant to be pasted into future conversations, repos, or design docs to instantly bootstrap context.*
