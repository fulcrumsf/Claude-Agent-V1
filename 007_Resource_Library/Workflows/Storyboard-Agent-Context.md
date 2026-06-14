---
title: "Storyboard Agent Context"
type: workflow
category: video-production
tags:
  - storyboard
  - ai-agents
  - video-production
created: 2026-05-08
source: local
---

# Storyboard Agent — MD Overview (Context + Current State)

## What this workflow is trying to do

This workflow takes a **narrated script/audio** (or narration beats) and turns it into a **timestamped storyboard**: a JSON “shot list” where each scene gets:

* a generator-ready **image_prompt**
* **negative_prompt**
* optional **motion_prompt**
* **continuity_notes**
* optional **on_screen_text**
  …and the output stays visually consistent across all scenes via a reusable `style_lock` + `hero_asset`.

## How the system currently works (high-level)

1. **Theme / Show selection**

   * A theme is selected (e.g., Strange Facts, Heartwarming, Animal History, Science, True Crime).
   * That theme provides the **style brief fields** used later:

     * `Niche_Topic`
     * `Target_Audience`
     * `Contrarian_Angle`
     * `Visual_Tone`
     * `Art_Direction`
     * `Editing_Pacing`

2. **Scene breakdown**

   * Scenes are generated/assembled into an array `scenes[]`, where each scene includes:

     * `scene_id`
     * `start`, `end`, `duration_ms`
     * `narration_beat`
     * `visual_intent`

3. **Loop over items**

   * The workflow loops through items, where each item contains the style brief + the `scenes[]` payload to be storyboarded.

4. **Storyboard Agent (LLM)**

   * The AI Agent node is responsible for converting `scenes[]` + style brief into **strict JSON** matching the schema.

## What’s wrong (current blocking issue)

The **Storyboard Agent prompt** is currently written as **instructions only**, but it is **not injecting the style brief and/or scenes values into the message** via n8n expressions.

Because of that, the model does not receive the actual values for:

* `Niche_Topic`
* `Target_Audience`
* `Contrarian_Angle`
  (and optionally the other style brief fields + `scenes[]`)

So the agent cannot reliably generate storyboard prompts that match the selected show style and constraints.

## What we need to continue working on

### 1) Inject the style brief into the AI Agent prompt (via expressions)

In the AI Agent node “Prompt (User Message)”, include the actual fields using expressions so the model receives real context, e.g.:

* `Niche_Topic: {{ $json.Niche_Topic }}`
* `Target_Audience: {{ $json.Target_Audience }}`
* `Contrarian_Angle: {{ $json.Contrarian_Angle }}`
* `Visual_Tone: {{ $json.Visual_Tone }}`
* `Art_Direction: {{ $json.Art_Direction }}`
* `Editing_Pacing: {{ $json.Editing_Pacing }}`

### 2) Inject scenes[] into the AI Agent prompt (via expressions)

Also include the full scenes payload so the agent can storyboard what actually exists in the timeline, e.g.:

* `Scenes JSON: {{ JSON.stringify($json.scenes) }}`

### 3) Keep output contract strict

The Storyboard Agent must output **only valid JSON** with the required schema, so downstream nodes (Parse JSON / Split Out / media generation) can consume it without repair steps.

---

## Prompt scaffold to paste into the AI Agent (with context injection)

Use this as the base message and replace/adjust field names if your JSON keys differ:

You are the Storyboard Agent (Visual Director + Prompt Engineer).

GOAL:
Convert timestamped scenes into a storyboard shot list with highly consistent, generator-ready prompts.

STYLE BRIEF (CONTEXT):

* Niche_Topic: {{ $json.Niche_Topic }}
* Target_Audience: {{ $json.Target_Audience }}
* Contrarian_Angle: {{ $json.Contrarian_Angle }}
* Visual_Tone: {{ $json.Visual_Tone }}
* Art_Direction: {{ $json.Art_Direction }}
* Editing_Pacing: {{ $json.Editing_Pacing }}

SCENES INPUT (JSON):
{{ JSON.stringify($json.scenes) }}

OUTPUT RULES (CRITICAL):

* Output ONLY valid JSON (no markdown, no commentary).
* Do NOT add keys outside the schema.
* Keep prompts consistent with Visual_Tone + Art_Direction.
* Do NOT introduce cartoon styling unless explicitly allowed by the style brief.
* Assume vertical video (9:16).
* Maintain continuity across scenes (define and reuse hero_asset + style_lock).
* Avoid unsafe/graphic content; keep depiction documentary-safe.

OUTPUT JSON SCHEMA:
{
"style_lock": "string",
"hero_asset": "string",
"shots": [
{
"scene_id": number,
"start": "HH:MM:SS.mmm",
"end": "HH:MM:SS.mmm",
"duration_ms": number,
"narration_beat": "string",
"visual_intent": "string",
"shot_design": {
"shot_type": "string",
"image_prompt": "string",
"negative_prompt": "string",
"motion_prompt": "string|null",
"continuity_notes": "string",
"on_screen_text": "string|null"
}
}
]
}
