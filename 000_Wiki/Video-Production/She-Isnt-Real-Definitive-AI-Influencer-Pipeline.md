---
title: "She Isn't Real - Definitive AI Influencer Pipeline"
type: wiki
category: video-production
tags:
  - seedance
  - ai-influencer
  - voice-cloning
  - ugc
source: "[[She-Isnt-Real-Definitive-AI-Influencer-Pipeline]]"
created: 2026-08-10
---

# She Isn't Real - Definitive AI Influencer Pipeline

## What It Is

A complete pipeline for creating consistent AI influencers/characters using Seedance 2's multi-reference and UGC modes: 5-image character sheets, product-holding UGC ads, voice cloning + lip sync from a 6-second audio clip, infinite video extension, and placing a character into any scene via a background reference image.

## Key Concepts

- **5-image character sheet, not more** — front/side/back rotation base, close-up facial features, full body, side-profile close-up, and an extreme close-up grid of individual features (eyes, lips, nose, brows, hair). Each subsequent image uses the *previous generated image* as the new source reference, not the original — a chained refinement approach rather than five independent generations from one source.
- **UGC mode vs. multi-reference mode are different tools for different jobs** — UGC mode takes exactly one character image and is built for one-off talking-product-ad style shots. Multi-reference mode takes the full character sheet (multiple images) and is what you need for cinematic commercials, since the model needs several angles to understand the character three-dimensionally, not just a flat portrait.
- **Voice cloning + lip sync** — swap the character-sheet images for a reference of yourself plus a 6-second high-quality audio clip of your own voice. Two mandatory prompt elements: a fixed instruction line (at both the start and end of the prompt) telling the model to clone/reference the voice, and an explicit line specifying exactly what the character says (drives the lip sync).
- **Infinite video extension technique** — extract the *last frame* of the current clip, feed only that single frame (not the full character sheet) into multi-reference mode along with the same audio-cloning prompt lines plus an instruction to match "the exact same image and background as the source." Image-to-video alone can't be used here because it doesn't support the audio reference needed for voice continuity.
- **Placing a character into a new scene** — same multi-reference approach, just add a background reference image and describe the setting; reference it in the prompt by image number/tag.

## How Tony Uses This

Relevant primarily for future UGC / affiliate-style productions (Neon-Parcel-style TikTok Shop work) rather than the narrative POV Shorts pipeline — the voice-clone + lip-sync + product-hold techniques are a different use case than ReimagineRealms' third-person storytelling. Still directly useful for the "extend video while keeping consistency" technique (last-frame-only re-conditioning), which is architecturally close to what the POV Shorts v2 pipeline already does with `first_frame_url`-only video generation.

## Related

- [[Seedance-Character-Environment-Consistency-Workflows]] — companion Seedance consistency tutorials
- [[Neon-Parcel-TikTok-Shop-Creator-Pipeline]] — Tony's existing UGC/affiliate video pipeline this could extend
