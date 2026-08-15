---
title: "How I Got 11M Views and 30K Subscribers in 3 Days With This AI Workflow"
type: wiki
category: video-production
tags:
  - seedance
  - video-to-video
  - viral-content
  - prompt-engineering
source: "[[How-I-Got-11M-Views-30K-Subscribers-AI-Workflow]]"
created: 2026-08-10
---

# How I Got 11M Views and 30K Subscribers in 3 Days With This AI Workflow

## What It Is

A viral "portal" AI reel breakdown: a real phone-filmed clip (person opening a door) is turned video-to-video into a fantasy-world reveal using Seedance 2.0, with Claude used exclusively to generate the video-generation prompt from a plain-language description.

## Key Concepts

- **Real base footage, not text-to-video** — the whole trick relies on filming a real, physically-shot moment (opening a door and stepping through) and using Seedance 2.0's video-to-video/full-raw-footage-input capability, not generating from nothing. Sufficient lighting on the subject's face/body is called out as a hard requirement for the base footage.
- **Never hand-write the generation prompt directly** — describe the desired result in plain conversational language to Claude (or any chatbot) along with the reference image, and let it produce the structured scene-by-scene prompt, including camera-behavior description and a negative prompt. The creator explicitly says this "habit... actually matters" — going scene-by-scene rather than one vague sentence.
- **Batch discipline** — generate one result first, evaluate it, and only batch multiple generations once the first take's camera movement and subject motion feel right. Batching before validating the first result wastes credits on a flawed prompt.
- **Iterative prompt refinement through the same chat** — when a result is close but off (e.g. hair not moving naturally, an unwanted camera zoom), go back to the same Claude conversation and describe the specific correction ("no zooms, camera must be static, add a breeze so her hair sways") rather than rewriting the prompt from scratch.

## How Tony Uses This

The "describe intent in plain language, let Claude write the structured Seedance prompt" pattern is already implicit in how Tony's pipelines work, but this tutorial's specific emphasis on scene-by-scene camera-behavior description plus a negative prompt as a baked-in habit is worth checking against the current [[Seedance-Prompting-Guide]] skill for completeness.

## Related

- [[Seedance-Prompting-Guide]] — the living universal Seedance skill
- [[Seedance-Character-Environment-Consistency-Workflows]] — companion consistency tutorials
