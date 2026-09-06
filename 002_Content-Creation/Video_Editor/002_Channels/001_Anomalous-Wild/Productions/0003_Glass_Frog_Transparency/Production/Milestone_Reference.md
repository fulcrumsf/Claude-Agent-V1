---
title: "Anomalous Wild — Milestone Reference Video (0003 Glass Frog)"
type: reference
domain: video-production
tags: [anomalous-wild, reference, milestone, video-production]
---

# 0003 Glass Frog Transparency — the Anomalous Wild reference build

**Status:** gemstone / milestone. First AW video graded **A** (2026-09-04).
**Final cut:** `Renders/0003_Glass_Frog_Transparency_FINAL_v2a.mp4`
**Published (private):** https://www.youtube.com/watch?v=JMn32MmAzWw

This is the worked example. When building any future AW video, this is what
"done right" looks like. Copy the *decisions*, not the assets.

---

## Why it works

1. **One counterintuitive hook, stated as agency.** Title "The Frog That Hides
   Its Own Blood to Disappear" — active verb, mechanism withheld. Thumbnail
   reinforces a *different* angle of the same fact, never repeats the title.
2. **Audio is the master clock.** Narration TTS first → word-level timestamps →
   every visual scheduled against them. No hand-placed timecodes.
3. **Three real audio layers.**
   - Narration — ElevenLabs, −14 LUFS, always on top.
   - Score — Suno "science documentary" brief (not solo-piano/mystery), −22 LUFS,
     sidechain-ducked under narration (`threshold=0.045:ratio=2.5:attack=300:release=600`).
   - Ambience/SFX — **video-to-audio (fal.ai Mirelo SFX v1.6)** conditioned on the
     actual footage, −25 LUFS (a hair under the score), gentle duck under VO.
     Fallback = ElevenLabs text-to-SFX (`generate_stems.py`) if v2a is unavailable
     or a segment fails.
4. **The image model draws the picture, never the words.** All labels, callouts,
   cards, meters, maps = Remotion components over the illustration/footage.
5. **Diagram camera never stops, but holds under every label.**
   move → settle → label in → hold → label out → move. `buildPath()` `holdS`
   dwell keyframes.
6. **Every cut is a 0.5s cross-dissolve** (`ChainScene` freeze-under/live-over).
   No hard cuts anywhere, scene boundaries or internal. This is a global AW rule now.
7. **Geography beats use a real research-sourced basemap** (Natural Earth, public
   domain) with the range path traced over true geography — not a synthetic map.
8. **Recurring creature gets a consistency reference** before any shot is generated.
9. **Real reference photo cutaway** where a generated illustration would strain
   credibility (scene 03: actual glass-frog photo, Ken-Burns, cross-dissolved in).
10. **End card + spoken CTA**, CTA VO normalized to the *same* level as the body
    narration (measure body VO integrated LUFS, bring CTA up to it — never eyeball).

---

## The pipeline that produced it (phase → artifact)

| Phase | Artifact in this production |
|---|---|
| Intake / research | `Research/`, NotebookLM report |
| Script | `Production/` script + `Data/Beatmap.json` (word-level VO timing) |
| Beat table | `Production/Beat_Table.json` (scene-level routing + `max_static_s`) |
| Shot list / tool routing | `Production/Shot_List.md` (per-beat, reasoned against `motion_graphics_capabilities.json`) |
| Asset plan | `Production/Asset_Plan.json` (sheets needed + B-roll vs generate per beat) |
| Live footage | `pipeline_supervisor.py` → Seedance 1.5 Pro, `input_urls:[start,end]` |
| Scientific diagrams | `diagram_research_and_illustrate.py` → `detect_label_coordinates.py` → `DiagramLabels.tsx` |
| Assembly | Remotion `GlassFrogDoc.tsx` (the composition IS the timeline) |
| Audio mix | `generate_stems_v2a.py` (ambience) → `render_outputs.py` (locked formula) |
| Audio-pop gate | `audio_pop_scan.py` — run before every review |
| YouTube package | `Package/YouTube_Package.md`, `Package/Thumbnails/` |
| Upload | `upload_to_blotato.md`, accountId `42514`, private |

---

## Composition architecture (`GlassFrogDoc.tsx`) — reusable patterns

- `DiagramShot` model: same-image runs = ONE shot, ONE eased camera path (no
  remount jump). Per-segment ease-in/out via `DiagramCamera`.
- `ChainScene` (tailFreeze): freeze-under / live-over 0.5s dissolve between every
  seg — the universal cut.
- `VanishShot` / `HeldVideoShot`: for beats Seedance can't do (transparency
  dissolve, "become invisible"). Clip plays, last ~1.5–2s cross-dissolves to a
  pre-extracted end-frame still. Held tails use PNG stills — **never two live
  `OffthreadVideo`s overlapping** (causes GPU-decode horizontal-band tearing).
- `VideoSegFilled` + `KenBurns`: freeze-fill so a short clip never loops to frame 0.
- All clip durations = `floor(real ffprobe seconds)` in whole frames, never the
  planned value.
- `NarrationTrack`: one VO track, 3-frame edge fades, no per-beat concat.

---

## Do-not-repeat list (mistakes this build made and fixed)

- v2a segment cuts must be downscaled + bitrate-capped before upload — an
  all-intra / full-res segment is ~50× larger and stalls the API upload.
- Don't call a cut "done" before running: black/white scan, audio-pop scan,
  per-cut transition check, generated-clip anatomy check, CTA-vs-body-VO level check.
- CTA VO level is measured, not eyeballed.
- Seedance 1.5 Pro's 2nd image is a last-frame target, not a style reference.
