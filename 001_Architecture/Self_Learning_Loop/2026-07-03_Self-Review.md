# Self-Review — 2026-07-03

## What Went Well

**Seedance model fix was clean.** Found the wrong model slug (`bytedance/seedance-2.0/image-to-video`) and fixed it to `bytedance/seedance-2`. Also correctly diagnosed that the real root cause was padding pushing 12s clips to 13s, forcing Seedance 2.0 unnecessarily. Fixing the cap to `MAX_1_5_S=12` eliminated the 2.0 issue entirely. Cleaner than just fixing the slug.

**Parallel tooling was right.** Built `generate_stems.py`, `mix_stems.py`, and `render_outputs.py` as three separate, single-purpose scripts that each accept `production_folder` as an argument. Tony's reusability requirement was correctly interpreted and implemented. These will work on any future production without changes.

**Responded well to Tony's audio feedback.** When Tony said the panicked_crowd stem was wrong, identified the fix (out_s, fade_out_s, volume), updated stem_map.json, added per-stem volume support to mix_stems.py, and re-ran the mix without needing clarification. Fast iteration.

**Correctly preserved context of the vision-based composer discussion.** Tony's brainstorming about per-scene clips vs. stems vs. API-mixed audio was nuanced. Correctly synthesized it: clips are individually generated per scene, kept as separate files, placed on Premiere timeline via FCPXML. Did not conflate this with "stems" in the old sense.

---

## What Went Wrong

**Probed the wrong API (Wavespeed instead of kie.ai).** When the Seedance API was returning errors, I initially investigated `api.wavespeed.ai` — but `batch_generate_videos.py` uses `api.kie.ai`. Wasted diagnostic time. Should have read the script first to confirm the API host before making any assumptions.

**The first audio stem design was wrong by architecture.** I designed 13 broad thematic stems that span multiple scenes — `panicked_crowd` running 25s→57s across a complex act that includes a calm family-of-four scene at 0:37. This was wrong from the start. The beatmap doesn't tell you what's visually on screen. I should have recognized that the Gemini scene analysis was needed not just for timing reference but as the PRIMARY input to audio decisions. I used it as a reference but the stems were still too broad.

**Took too many tokens confirming the Suno 500 error.** Tried multiple payloads (full Suno format, minimal payload, JSON vs query params) before concluding it was a kie.ai service outage. Should have cut to "minimal payload, one retry, then declare outage" faster.

---

## Patterns to Improve

**When visual content drives audio, require visual analysis first.** Before designing any audio element for a video (stems, clips, music cues), the Gemini scene analysis must already exist. Do not design audio from beatmap text descriptions alone. The beatmap says what the story intends; the visual analysis says what the viewer sees. These are different.

**Read script source before probing APIs.** Any time an API returns an error, read the script making the call first — confirm the base URL, model slug, payload format. Do not assume which platform is being used.

**When Tony gives negative feedback on creative quality, go to architecture first.** Tony said "65% quality" — the right response is "what's architecturally wrong" before "how do we tune the parameters". The problem wasn't the ElevenLabs prompts; it was the stem design paradigm. Tuning the prompts would not have solved it.

---

## Ideas for Automation

**Per-stem volume tuning should happen in Premiere, not in stem_map.json.** stem_map.json volume keys are emergency overrides. The long-term system (FCPXML + per-scene clips) puts control where it belongs: in the editor, per clip, with full visibility of the timeline. The `mix_stems.py` approach will be retired once `compose_audio.py` is built.

**`compose_audio.py` should be the most important tool in this pipeline after video generation.** It's the step that separates generic YouTube AI content from something that sounds professionally scored. Worth investing 2-3 sessions to get it right. Do not rush it.

**Research pass should be written as a wiki article first.** Documentary sound design knowledge should be captured in `000_Wiki/Video-Production/Documentary-Sound-Design.md` before being baked into the composer prompt. This makes the knowledge reusable across the composer prompt, future audio designers, and any agents that read the wiki.
