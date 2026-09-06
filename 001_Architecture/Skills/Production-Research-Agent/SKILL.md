---
name: Production-Research-Agent
description: "Invoke right after a video production's topic/subject is chosen, on ANY channel — gathers real-world facts, reference images, and Pexels B-roll footage for that subject before scriptwriting begins. Triggers on: a pipeline reaching its topic-selection pause and needing to kick off research, 'research this subject', 'find reference images for X', 'search Pexels for footage of X', or any point where a production needs grounding facts + real reference assets before the script is written. Channel-agnostic — used by Anomalous Wild, Reimagined Realms, Kingdom and Conquerors, Glifry, Polyoculus, and any future channel. <example>User: (Anomalous Wild pipeline, topic just picked: mantis shrimp eyes) Assistant: invokes Production-Research-Agent to gather mantis shrimp facts, reference images, and Pexels footage before Phase 1 Step B scriptwriting</example>"
trigger: A pipeline needs topic research + reference images + Pexels B-roll for a chosen subject, immediately after topic selection and before scriptwriting
---

# Production-Research-Agent

Gathers everything a production needs to know about its chosen subject, plus real reference images and real Pexels video footage — before a single word of script gets written. Channel-agnostic: any current or future YouTube pipeline in this workspace invokes this the same way.

**Trigger point:** immediately after the calling pipeline's topic-selection pause resolves (Tony has picked a subject from presented options), before scriptwriting starts.

**Do not build any of this without the calling pipeline's `production_folder` already existing** — this skill writes into that folder's `Research/` subfolder (create it if the calling pipeline's scaffolder doesn't already).

---

## Step 1 — Deep topic research

Research the chosen subject thoroughly enough to write an accurate, engaging script: anatomy, behavior, scientific facts, notable/surprising details, and — critically — **whether the story is about one specific, identifiable individual or the species/subject in general.** This single distinction (see Step 3) determines how the Pexels search in Step 3 is framed; it does not need separate logic, it just falls out of what the topic literally names.

- If the topic names a species/general subject (e.g. "Why do wombats have such strong butts?") → research the species/subject in general.
- If the topic names a specific real, known individual (e.g. "Why was Coco the Gorilla so famous?") → research that specific individual **and** their species.

Use Perplexity (or whichever research tool the calling pipeline already uses for topic research — do not duplicate an existing research call if the pipeline already ran one; this step supplements it with the reference-asset and Pexels work below, which does not exist elsewhere).

Write findings to `Research/Topic_Facts.md`.

## Step 2 — Reference images (grounding only, never used directly in the final video)

Search and download real, Creative Commons / public-domain reference images of the subject — anatomy references, scientific diagrams, real photos showing natural color/pattern variation. These exist purely to ground later image-asset generation (character sheets, environment sheets, GPT-Image-2 start/end frames) — **they are never composited or cut into the final video themselves.**

- **Cap: 20 total reference images per production.**
- Save to `Research/Reference_Images/`, named descriptively (e.g. `Mantis_Shrimp_Coloration_01.jpg`, not `image1.jpg`), per this workspace's naming convention.
- If the topic is about a specific individual (the George/Coco case), search for that individual specifically, not just the species.

## Step 2b — Map / geography asset (only when the script names a place, region, route, migration, or range)

If the topic or script references a **real location, region, route, migration path, or species range**, source a real map asset for it now — do not leave the assembly step to fake it with a synthetic shape (this was a real defect on 0003 Glass Frog, Notes 9–10).

- Preferred source: **Natural Earth** raster (naturalearthdata.com — explicitly public domain, no attribution required). `NE2_50M_SR_W` (shaded relief) crops well to any region. Wikimedia Commons PD relief/terrain maps also work — **verify the license and record any required attribution.**
- If no suitable real map exists: do a plain web/image search for the correct map and keep it as a *reference only*, then note that the geography beat needs a stylized map generated from it (GPT-Image-2, or GeoJSON→SVG) at the diagram/asset step — never ship a hand-drawn approximation.
- Save to `Research/Reference_Images/` (or a `Research/Maps/` subfolder) with a `SOURCE.md` recording the origin, license, and whether on-screen attribution is required. If attribution is required, it goes bottom-right on the map in the final composition.
- The map is styled to the channel and used as a **base layer** with the animated route/path drawn over it (see Diagram-Generation's map/geography type) — the path must trace the real geography on that base, never float over nothing.

## Step 3 — Pexels video search + download

Search Pexels for video footage matching the subject exactly as named by the topic — no special branching logic for the "specific individual" case, the search term is just whatever the topic names:
- Generic subject topic → search the species/subject name (e.g. "wombat").
- Specific-individual topic → search both the individual's name and the species (e.g. "Coco the Gorilla" and "gorilla").

**Filtering (locked 2026-08-18): 1080p resolution, 16:9 aspect ratio only.** Discard any result that doesn't match both.

**Cap: 10 videos downloaded per production**, deliberately varied across different contributors and camera angles — do not download 10 near-identical clips from the same contributor.

Full API reference (auth, endpoints, rate limits): `001_Architecture/Tools/Tool-Manager/data/Pexels_API_Reference.md` — read this before writing any Pexels integration code.

**At download time, capture and store the attribution fields immediately** — do not plan to reconstruct them later:
- `photographer` / videographer name
- `photographer_url` / videographer profile URL
- `photographer_id` / videographer ID

Save full-length downloads to `Research/Pexels_Downloads/`, named descriptively (e.g. `Wombat_Burrow_Digging_01.mp4`). **Never trim or modify these files in place** — see the Production-Asset-Planner skill's B-roll trimming step, which works from copies of these originals.

## Step 4 — Analyze each downloaded clip

Run each downloaded Pexels clip through the `Video-Analyzer` skill (or the densest available frame-sampling pass — near-per-second screenshotting is the target density per Tony's 2026-08-18 guidance on training real editorial judgment, not a fixed rule like "insert B-roll every N seconds") to build a structured understanding of what actually happens in the clip, not just its raw filename/duration.

Write `Research/Pexels_Inventory.json` — one entry per downloaded video:
```json
{
  "filename": "Wombat_Burrow_Digging_01.mp4",
  "duration_s": 14.2,
  "resolution": "1920x1080",
  "aspect_ratio": "16:9",
  "photographer": "Jane Doe",
  "photographer_url": "https://www.pexels.com/@janedoe",
  "photographer_id": "123456",
  "analysis": {
    "actions_depicted": ["wombat digging burrow entrance", "wombat backing into burrow"],
    "notes": "single continuous wide shot, no cuts, natural lighting"
  }
}
```

This inventory is the shared library the calling pipeline's B-roll placement logic (Production-Asset-Planner, section on smart-editor B-roll matching) reads from — it should never need to re-download or re-analyze the same footage across productions if the subject repeats.

**Open question, not yet resolved (2026-08-18):** whether an LLM can reliably self-identify what a clip/image depicts purely by looking at it, without this separate analysis pass. Not yet tested — run the full analysis pass until this is validated.

## Step 5 — Hand off

Once Steps 1–4 are complete, the calling pipeline proceeds to scriptwriting as normal. `Research/Topic_Facts.md`, `Research/Reference_Images/`, `Research/Pexels_Downloads/`, and `Research/Pexels_Inventory.json` are now available for every later phase — reference-sheet generation, Production-Asset-Planner's B-roll matching, and the final YouTube description's attribution section.

---

## Design goal — this is meant to enable a genuinely smart editor, not just a downloader

The point of this skill isn't just to fetch files — it's to give the downstream B-roll-placement logic (Production-Asset-Planner) enough structured understanding of what's actually available that it can make real editorial judgments: does existing real footage already cover a given beat's described action, or does that beat need to be generated? See `Production-Asset-Planner/SKILL.md` for how the inventory built here gets used.

## Scope

Channel-agnostic. Any pipeline in this workspace invokes this skill the same way, immediately after topic selection. Do not fork a per-channel copy.
