---
title: "Takeaways — GPT-Image-2 + Seedance 2.0 Character/Environment Consistency Tutorial"
source: "https://www.youtube.com/watch?v=042D0gKZUGw"
prompts: "./Prompts/"
video_analysis: "./Video_Analysis/ANALYSIS.md"
date: 2026-09-19
---

# Scope note

This tutorial builds a cinematic samurai-drama animation — not relevant to
Neon Parcel or any current channel's content style, and deliberately not
being copied (see the source analysis's own "Originality Boundaries"
section). Everything below is filtered down to **prompting/workflow
technique only** — things that would genuinely change how we write a
GPT-Image-2 or Seedance prompt, regardless of subject matter.

# Findings, each checked against what our skills already document

## 1. Genuinely new: use a vision-capable LLM as a prompt-drafting intermediary (not just a template)

**What the tutorial does:** rather than writing the multi-angle character/
environment sheet prompt by hand, the base image is uploaded to Claude
along with a bracketed template (`[CHARACTER DESCRIPTION]`, `[OUTFIT
DESCRIPTION]`, etc.), and Claude — looking at the actual image — fills in
every bracket itself, then that output becomes the literal GPT-Image-2
prompt. Same pattern is repeated for the environment sheet.

**What we already document:** `GPT-Image-2-Prompting-Guide`'s character-
anchor pattern says to attach the base image as a reference and restate
invariant traits — but doesn't document *having a vision LLM inspect the
image and auto-fill a structured template* as a distinct step. We've been
writing these prompts by hand, describing what we already know about the
subject, not deriving them by having a model look at a reference photo/
image and extract the details itself.

**Verdict: real gap, worth adding.** This is a genuinely different
technique from what's documented — an extra verification/drafting layer
that could reduce human-transcription errors (e.g. the kind of thing that
caused this session's driver-backpack and architecture mistakes might have
been caught earlier if a vision model were asked to describe what it
actually sees in a reference before a prompt gets written by hand).

## 2. Genuinely new: the explicit trigger sentence

The template's closing line — **"Fill in this prompt using the attached
[character/reference] image"** — is called out in the video itself as the
specific instruction that forces feature-extraction behavior instead of
generic creative writing from the drafting LLM. Small, concrete, and not
currently in any of our skills as a named technique.

**Verdict: real gap, worth adding** as a specific line to use whenever an
intermediary LLM is asked to draft a prompt from a reference image.

## 3. Genuinely new (Seedance-specific): face-as-starting-frame is explicitly called a "massive gamble"; multi-angle character sheets are the safe substitute

Direct quote (video outro): *"Including a starting image of a face is a
massive gamble. However, using an object or environment as your starting
image is completely safe... if you do need to use a person, uploading a
multi-angle character sheet... is usually enough to bypass the face
block."*

**What we already document:** nothing this specific in
`Seedance-Prompting-Guide` about a face-detection/face-block failure mode
tied to *which type of image* is used as the starting frame.

**Verdict: real gap, worth adding** — this is a concrete, actionable rule
about Seedance's real failure mode, not a style preference.

## 4. Genuinely new (Seedance-specific): the "Inpaint Bridge" hand/anatomy recovery technique

Documented, tested recipe for recovering a video with a hallucinated-hand
(or similar localized anatomy) defect without re-rolling the whole
generation:
1. Screenshot the defective frame from the generated video.
2. In an image editor (ChatGPT/GPT-Image-2's inpaint tool), brush-select
   just the defective region and prompt narrowly ("fix the hands to look
   normal").
3. **Check for and explicitly remove any AI-generation watermark tag** that
   the inpaint step may leave behind ("remove the AI tag") — a real,
   easy-to-miss follow-up step.
4. Re-inject the corrected frame into Seedance with an explicit anchor
   instruction: `Starting frame matches [imageN]` — forcing the video
   engine to treat that corrected frame as the literal starting point
   rather than reinterpreting it loosely.

**What we already document:** nothing this specific. We've hit an
analogous problem this session (repainting a single storyboard panel
rather than regenerating a whole sheet) but never documented a matching
recipe for *video* output specifically, nor the watermark-removal
follow-up step, nor the exact `Starting frame matches [imageN]` anchor
phrasing.

**Verdict: real gap, worth adding** to Seedance-Prompting-Guide as a named
recovery technique.

## 5. Confirms (does not change) existing guidance: fresh-session-per-generation to avoid context/noise degradation

The tutorial demonstrates the exact failure our guide already flags as
weakly-sourced ("one field report") — repeated regeneration inside the
same chat thread visibly degrades output (noise/artifacts), fixed by
starting a brand-new chat per attempt. This is a second, concrete,
independent example of the same claim.

**Verdict: no new rule needed, but worth strengthening the citation** —
this was previously our single weakest-sourced claim in the guide; it now
has independent confirmation.

## 6. Confirms (does not change) existing guidance: negative-prompt-via-positive-prompt-exclusion-list

The environment base-image prompt's very long literal "NEGATIVE PROMPT:"
section, folded into the positive prompt text (since GPT-Image-2 has no
real negative-prompt parameter), is exactly the technique our guide already
documents. Worth keeping as a strong real-world example if the guide ever
wants one, but not a new rule.

## 7. Confirms (does not change) existing guidance: distinct camera angles per environment-sheet panel

The environment sheet's 2x2 grid (wide eye-level, high-angle 3/4 overview,
two close-ups) matches our Environment-Sheet-Generation skill's existing
"each panel must be a visibly different angle/zoom/height" rule. No change
needed.

# Proposed implementation plan (not yet executed — pending approval)

| # | Change | File |
|---|---|---|
| 1 | Add "Vision-LLM prompt-drafting intermediary" as a documented optional technique — upload a reference image + bracketed template to a vision-capable LLM, let it fill the template from what it actually sees, use that output as the GPT-Image-2 prompt. | `GPT-Image-2-Prompting-Guide/SKILL.md` |
| 2 | Add the explicit trigger-sentence pattern ("Fill in this prompt using the attached image") as the recommended closing line whenever technique #1 is used. | `GPT-Image-2-Prompting-Guide/SKILL.md` |
| 3 | Add a Seedance-specific rule: never use a face/person photo as a video starting frame directly — use an object/environment starting frame, or a multi-angle character sheet if a person must be referenced. | `Seedance-Prompting-Guide/SKILL.md` |
| 4 | Add the "Inpaint Bridge" recovery technique (screenshot → brush-inpaint → strip watermark → re-inject via `Starting frame matches [imageN]`) as a named, step-by-step recovery procedure for localized anatomy/hand defects in generated video. | `Seedance-Prompting-Guide/SKILL.md` |
| 5 | Strengthen the existing "fresh session per generation" citation with this tutorial as a second independent confirming source. | `GPT-Image-2-Prompting-Guide/SKILL.md` |

Items 1-4 are net-new techniques; item 5 just firms up sourcing on an
existing claim. Nothing here touches the two skills already hardened this
session (Environment-Sheet-Generation's Architectural Plausibility Check,
the storyboard reference-labeling rule) — no conflicts found.

**Waiting for your go-ahead before editing either skill file.**
