---
name: Anomalous_Wild_Video_Pipeline
description: "Invoke when Tony says /anomalous-wild, make an Anomalous Wild video, build me a video for the nature/science channel, run the Anomalous Wild pipeline, or start an AW production. Orchestrates the full faceless YouTube science-documentary pipeline start to finish: ideation → script → voiceover with word-level timestamps → beat table → per-beat Tool-Manager routing → asset generation (live footage AND the Scientific Diagram sub-pipeline) → Remotion assembly → audio mix → YouTube package → Blotato upload. Mirrors Reimagined Realms' orchestration pattern but never hardcodes a visual tool — every beat's tool choice comes from a live Tool-Manager query. <example>User: /anomalous-wild Assistant: starts PHASE 1 INTAKE — runs new_video.py's questionnaire + Perplexity research, presents topic options</example> <example>User: make me an Anomalous Wild video about the mantis shrimp's punch Assistant: starts PHASE 1 INTAKE but pre-fills topic context from user message</example>"
trigger: User invokes /anomalous-wild or asks to produce an Anomalous Wild video
---

# Anomalous Wild — Video Pipeline Skill

You are the orchestrator for the Anomalous Wild faceless YouTube science/nature-documentary channel.
Work through all 10 phases in order, start to finish — from topic ideation through the live Blotato YouTube upload. Never skip phases and never stop at "here are your files, next steps are manual" — this skill executes the full pipeline.

**Core design principle — never hardcode a visual tool.** This channel is science/diagram-heavy. Instead of always reaching for the same composition tool, every beat's visual need is described in plain language and routed through the `Tool-Manager` skill, which reasons over a real researched capability profile (`001_Architecture/Tools/Tool-Manager/data/motion_graphics_capabilities.json`) and returns which tool(s) apply. Do this per beat, every time — do not assume "diagrams always go to Remotion" as a shortcut, even though that has been true so far in practice.

Explicit pauses are built in at: topic selection (Phase 1), live-footage cost estimate (Phase 6, only if the production has any `live_footage`-routed beats), first live-footage clip quality check (Phase 6), and title/thumbnail/privacy selection (Phase 10). Stop and wait for Tony at each.

**Output folder for this run** (create at Phase 1, Step C):
```
/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/[NNNN]_[Title_Case_Slug]/
```
Replace `[NNNN]` with the next zero-padded sequence number found under `Productions/` (e.g. `0001_Bioluminescence_Weapon` already exists → next is `0002_...`). Replace `[Title_Case_Slug]` with a Title_Case, underscore-separated slug from the chosen topic (per this workspace's file-naming convention — not RR's kebab-case).

---

## PHASE 1 — INTAKE + IDEATION

### Step A — Questionnaire + research (existing tool, reused as-is)

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/new_video.py
```

This runs the interactive questionnaire and Perplexity-backed topic research for the `001_anomalous_wild` channel entry, using existing case studies (`002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Case_Studies/`) for context. Answer the channel/format prompts as `Anomalous Wild` / `long` (16:9) unless Tony specifies otherwise.

⚠️ **Do not let `new_video.py` scaffold the production folder.** Its built-in `scaffold_project()` writes the legacy `outputs/<channel>/<id>_<slug>/001_scenes/...` layout — that is superseded by Task 9's typed folder structure (Step C below). Use `new_video.py` only for the questionnaire, research, and topic selection; if it writes a legacy `outputs/` folder as a side effect, ignore/discard it — the real production folder is created in Step C.

⏸ **PAUSE — present the researched topic options to Tony and wait for a pick before proceeding**, the same way RR pauses at its Phase 3 topic selection.

Store: `chosen_topic`, `subject` (short noun phrase for the YouTube package generator), `hook_fact`.

### Step B — Script (existing skill, reused as-is)

Write the full narration script using the `Anomalous-Wild-Scriptwriter.md` skill/voice at:
```
/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/.agents/skills/Anomalous-Wild-Scriptwriter.md
```
This defines the channel's own "Anomalous Arc™" structure, tone, and voice settings — apply it as written, do not substitute RR's DAIPBR/7-part frameworks. Cross-reference the visual/tone style guide at:
```
/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/.agents/styles/Anomalous-Wild-Hybrid.md
```

Format the script into `Scripts/Script.md` (full narration) and `Scripts/Narration.md` (TTS-ready, `## scene_01` / `## scene_02` ... headers each followed by that scene's narration text — this is the exact format `generate_narration_with_timestamps.py` parses in Phase 3).

### Step C — Scaffold the production folder (Task 9 scaffolder — always use this, not new_video.py's)

```bash
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/scaffold_new_production.py \
  "/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/[NNNN]_[Title_Case_Slug]"
```

Creates the 8 typed folders (`Scripts/`, `Production/`, `Images/`, `Video_Clips/`, `Narration_Audio/`, `Audio_Stems/`, `Assembly/`, `Package/`) and writes `Production/end_card_reference.txt` pointing at the locked end-card asset. This script hard-fails if `end_card_v3.mp4` is missing — that's intentional, treat a failure here as a stop-the-pipeline error, not something to route around.

Move/save `Script.md` and `Narration.md` from Step B into this folder's `Scripts/` subfolder. Store the full path as `production_folder`.

---

## PHASE 2 — SCRIPT (see Phase 1 Step B)

Script generation is folded into Phase 1 (Step B) because the channel's ideation and scriptwriting are one continuous automated pass in practice — DESIGN.md lists them as separate phases, but there is no natural pause between them, so they run back-to-back before Phase 1's topic-selection pause resolves into a written script. No further action here; proceed to Phase 3.

---

## PHASE 3 — VOICEOVER (automated)

Generate per-scene voiceover with word-level timestamps.

```bash
source /Users/tonymacbook2025/.env-secrets
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_narration_with_timestamps.py \
  "[production_folder]" \
  "<voice_id>"
```

Confirm the correct Anomalous Wild ElevenLabs voice ID with Tool-Manager or Tony before running — do not reuse Reimagined Realms' voice ID (`raMcNf2S8wCmuaBcyI6E`) by default; that voice belongs to RR's narrator persona, not this channel's.

Reads `Scripts/Narration.md` (the `## scene_id` sections written in Phase 1). Writes, per scene:
- `Narration_Audio/<scene_id>.mp3`
- `Narration_Audio/<scene_id>_beat_sheet.json` — word-level timestamps (this is the new capability Task 2 added; Anomalous Wild did not previously have these)

---

## PHASE 4 — BEAT TABLE (automated, requires a coarse routing pass first)

`build_beat_table.py` needs to know, per scene, whether that scene is headed for live-footage generation (8s clip cap applies) or a diagram/data-viz composition (no length cap, but the 3–5s max-static rule applies instead) — this decision has to exist before the table is built, because it changes the table's output shape.

### Step A — Coarse per-scene routing (invoke Tool-Manager)

For each scene in `Narration_Audio/*_beat_sheet.json`, read the scene's narration text from `Scripts/Narration.md` and describe its visual content in plain language. Invoke the `Tool-Manager` skill with that description and ask for a coarse classification: does this scene's visual need belong to `live_footage` (real/generated footage of the creature or phenomenon) or `diagram` (a labeled scientific/data-viz composition)? This is a binary routing signal only — the specific tool (Remotion vs. Hyperframes vs. Manim, etc.) is decided later, per beat, in Phase 5.

Write the result to `Production/Scene_Routing.json`:
```json
{"scene_01": "live_footage", "scene_02": "diagram", ...}
```

### Step B — Build the table

```bash
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/build_beat_table.py "[production_folder]"
```

Reads `Narration_Audio/*_beat_sheet.json` + `Production/Scene_Routing.json`, writes `Production/Beat_Table.json`. Per beat, this locks in:
- `max_clip_s: 8.0` if `routing == "live_footage"` (hard cap, same reasoning as RR: engagement pacing + generation model limits)
- `max_static_s: 5.0` if `routing != "live_footage"` (diagram/data-viz beats have no total-length cap, but nothing may hold a fully static frame longer than 3–5s — something must always be changing: a new callout line, a new label, a camera reframe)

---

## PHASE 5 — SHOT LIST / TOOL ROUTING (automated — Tool-Manager invoked per beat, never hardcoded)

For each beat in `Production/Beat_Table.json`, describe the scene's visual need in plain language — subject, action, whether it's real/generated footage or a labeled diagram, what's the source narration for that beat — and **invoke the `Tool-Manager` skill. Do not hardcode a tool choice.** Tool-Manager reasons over `001_Architecture/Tools/Tool-Manager/data/motion_graphics_capabilities.json` (Remotion, video-use, Hyperframes, Manim — researched strengths/best-for/not-for per tool, not a fixed lookup table) and returns which tool(s) apply, sometimes more than one for a single beat (e.g. video-use for the cut + Hyperframes for caption burn-in on top of it).

This is the same binary signal from Phase 4 refined into an actual execution plan:
- Beats already coarse-routed to `live_footage` will almost always resolve to `pipeline_supervisor.py`-driven generation (Phase 6), but confirm with Tool-Manager rather than assuming — a "live footage" beat could still need a Hyperframes caption pass on top.
- Beats coarse-routed to `diagram` resolve to the Scientific Diagram sub-pipeline (Phase 6) driven by Remotion, per Tool-Manager's `best_for` entry for labeled scientific diagrams — but confirm per beat; a data-viz beat that's pure chart/counter work might route to Remotion's built-in chart patterns directly without the full research→illustrate→detect→label sub-pipeline.

Write the per-beat routing decisions and Tool-Manager's reasoning to `Production/Shot_List.md`.

---

## PHASE 6 — ASSET GENERATION (automated → ⏸ pauses as noted)

Split by the Phase 5 routing decision. A production will typically have both kinds of beats.

### 6A — Live-footage beats (existing tools, reused as-is)

⏸ **PAUSE — cost estimate.** Before running any billed generation, compute an estimate the same way RR does (read current prices from `001_Architecture/Tools/Tool-Manager/data/pricing_cache.json`, look up actual kie.ai model IDs in `001_Architecture/Tools/Tool-Manager/data/kieai_pricing_api.json` by `modelDescription` — never probe the live API to discover model names). Present the estimate for the live-footage clip count × model choice and wait for Tony's approval before generating. Skip this pause entirely if the production has zero `live_footage`-routed beats.

```bash
source /Users/tonymacbook2025/.env-secrets
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/pipeline_supervisor.py
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/check_pipeline_status.py
bash    001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/pipeline_orchestrator.sh
bash    001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/preloop_videos.sh
```

These are the channel's existing, working batch-generation stack: `pipeline_supervisor.py` handles error-code-aware retries and the three-layer audio check, `pipeline_orchestrator.sh` sequences priority-tiered generation + preloop stages, `check_pipeline_status.py` reports progress. They currently expect a `Production/new_clips_prompts.json` prompt manifest (confirmed by their error output on an empty folder) — build that manifest from the Phase 5 Shot_List.md live-footage entries before invoking them.

⏸ **PAUSE — first live-footage clip quality check.** Generate one clip, show it to Tony, and wait for approval before committing to the full batch — same reasoning as RR: catch a bad model/prompt combo on 1 clip, not the whole set.

### 6B — Diagram/data-viz beats (Scientific Diagram sub-pipeline — new this session)

Fixes the garbled-text/mismatched-label failure mode seen in the Bioluminescence Weapon anglerfish diagram. Run per diagram beat:

**Step 1–2 — research a real reference, generate a clean label-free illustration:**
```bash
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/diagram_research_and_illustrate.py \
  "<subject_query>" "<style_description>" "[production_folder]/Images/<scene_id>/"
```
Searches Openverse for a real anatomical reference image (grounds the illustration in reality, doesn't invent anatomy from nothing), then generates the illustration via kie.ai GPT-Image-2 with an explicit no-text/no-label/no-callout negative prompt. **Styling is per-video, not fixed** — judge `style_description` from the same reference research, the same way a designer would adapt style to context; do not reuse one locked palette/line-style across every video.

**Step 3 — detect real label coordinates on the actual generated image:**
```bash
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/detect_label_coordinates.py \
  "[production_folder]/Images/<scene_id>/illustration.png" <feature1> <feature2> ...
```
A Gemini vision pass looks at *that specific generated image* (never a generic template) and returns `{feature, x_pct, y_pct, confidence}` per requested feature. If it can't confidently locate a feature it returns `confidence: "not_found"` — the script structurally strips any coordinates attached to a `not_found` entry, so a low-confidence guess can never leak into placement. Flag any `not_found` results to Tony rather than guessing a position. Writes `label_coordinates.json` alongside the illustration.

**Step 4 — place labels in Remotion:**
Feed `label_coordinates.json` into the `DiagramLabels` component at:
```
002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-components/DiagramLabels.tsx
```
Its Zod props schema (`diagramLabelsSchema`) takes `labels` (feature/x_pct/y_pct/confidence, where `x_pct`/`y_pct` are optional since a `not_found` entry legitimately omits them), `labelStaggerS` (seconds between each label appearing), and `displayNames` (feature key → human-readable label text). The component already filters out `not_found` entries from rendering and staggers each label's line-draw-in animation. Label entrances alone do not guarantee the beat's `max_static_s` rule is honored for its full duration — see Phase 7's mandatory static-hold check, which is where this is actually enforced.

**Label/line color — check before finalizing any diagram beat.** `DiagramLabels.tsx` currently hardcodes its line/label color to the channel's brand green (`#8AFA47`) as a blanket default. Per `003_Remotion/src/skills/design-rules-learned.md` (Rule 1), that's correct only for channel-chrome graphics — an in-scene diagram overlaid on generated illustration content should generally use a color sampled from the illustration itself (or white-on-black for contrast) rather than the brand sheet by default. This is a known, flagged gap in the shipped component, not yet fixed — read that skill file before deciding whether to override the color for a given diagram beat.

---

## PHASE 7 — ASSEMBLY (existing Remotion engine, extended for new scene types)

Assembly runs through the channel's real engine — never raw ffmpeg concatenation. The pattern is `BioluminescenceDoc.tsx`-style: a Remotion composition per production that pulls in generated clips, illustrated diagrams with `DiagramLabels` overlays, and title/end cards as React components, not a hand-stitched video file.

```
002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/[NNNN]_[Title_Case_Slug]/Remotion/
```

For each production, create a Remotion composition following the `BioluminescenceDoc.tsx` pattern (confirmed precedent at `002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/0001_Bioluminescence_Weapon/Remotion/BioluminescenceDoc.tsx`), extended to include `DiagramLabels` scenes for any Phase 6B beats. Do not bypass this engine with a manual ffmpeg concat, even for a "quick" assembly — that was a mistake corrected earlier this session.

**Mandatory check — diagram beat static-hold enforcement (no exceptions):**
`DiagramLabels.tsx` deliberately owns nothing beyond staggered label entrances — it has no pan/zoom/reframe capability, and camera motion is a per-video Remotion composition decision, not something to hardcode into the component. That means `max_static_s` (written per diagram beat in `Beat_Table.json` by Phase 3's `build_beat_table.py`) is NOT self-enforcing. Before finalizing any diagram beat's composition in this phase, the orchestrating agent must mechanically check it:
1. Compute the beat's label-entrance coverage: `labelStaggerS × (num_labels - 1) + fade_duration`.
2. Compute the remaining static hold: `beat_duration − label_entrance_coverage`.
3. If that remaining hold exceeds the beat's `max_static_s` (from `Beat_Table.json`, default 5.0), the composition MUST add a real motion element to cover the remainder — a slow Ken-Burns-style scale/pan on the illustration image, a camera reframe, or an additional visual beat (a second label, callout, or annotation appearing later in the timeline). Something must always be changing; a beat that passes this check by accident (label coverage already exceeds `max_static_s`) needs no extra motion, but every diagram beat gets the calculation, not just the ones that look long.
This is a mandatory per-beat check during assembly, not optional polish — the plan's Global Constraints state the "no static frame longer than 3–5 seconds" rule with no exceptions.

**End card — locked, always appended, never regenerated:**
```
002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Brand_Assets/End_Card/end_card_v3.mp4
```
This asset is fixed for every Anomalous Wild video. Append it via ffmpeg concat at the end of the assembled Remotion render — do not regenerate it, do not route it through Remotion, do not let a per-video prompt touch it. `Production/end_card_reference.txt` (written by `scaffold_new_production.py` in Phase 1) points at this exact path; read from there rather than hardcoding the path a second time in assembly code.

Render the Remotion composition to `Assembly/raw_video.mp4`, then append the end card to produce the pre-audio-mix cut. Audio (Phase 8) mixes onto this.

---

## PHASE 8 — AUDIO (existing scripts, built this session, reused unchanged)

Run in this order (matches the locked LUFS/sidechain-duck formula from this session's memory):

```bash
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/compose_audio.py "[production_folder]"
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_stems.py "[production_folder]"
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/analyze_stems.py "[production_folder]"
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/mix_stems.py "[production_folder]"
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_suno_music.py \
  "[production_folder]/Assembly/music.mp3" "<suno_prompt>" "<suno_style_tags>"
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/render_outputs.py "[production_folder]"
```

- `compose_audio.py` — vision-based per-scene audio brief from `Assembly/` frames + `Beatmap`/`Narration.md`, writes `Data/audio_briefs.json` and `Data/per_scene_stem_map.json`. (This script's own docstring header still says "Reimagined Realms productions" — it's this session's Anomalous-Wild duplicate of the RR original, not yet fully re-worded; functionally it operates on whatever `production_folder` you pass it.)
- `generate_stems.py` — generates the SFX stems from `Data/stem_map.json` via ElevenLabs.
- `analyze_stems.py` — measures LUFS per stem and writes corrected gain values back into the stem map (locked targets: stems -23 LUFS / vol≈0.88, narration -14 LUFS / vol≈3.09).
- `mix_stems.py` — mixes `Audio_Stems/` onto the timeline using the corrected stem map.
- `generate_suno_music.py` — generates the full-length instrumental score.
- `render_outputs.py` — final versioned render with all audio tracks kept separate (stems-only, stems+narration, and full final with sidechain-ducked music: `sidechaincompress threshold=0.015 ratio=4 attack=150 release=800`), producing `Assembly/<prod>_final.mp4`.

`render_video.py` is the lower-level versioned renderer `render_outputs.py` calls into for each of its 3 output variants — invoke it directly only if a single variant needs a targeted redo (`--phase`/`--version`/`--note` flags), not for the normal full run.

---

## PHASE 9 — YOUTUBE PACKAGE (automated)

```bash
source /Users/tonymacbook2025/.env-secrets
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_youtube_package.py \
  "[production_folder]" "<subject>" "<hook_fact>"
```

Adapts RR's Phase 10 formulas (curiosity-gap titles, search-intent description, no-text emotion-matched thumbnail) to this channel's science/nature-documentary framing. This single call does more than RR's shot-list-based thumbnail prompt step — it directly generates and downloads 3 real thumbnail concepts via kie.ai GPT-Image-2 (not just prompts for Tony to run later), across 3 mood/palette variations (intrigued/cool-blue-green, alarmed/warm-amber-red, awed/deep-purple-teal). Writes:
- `Package/YouTube_Package.md` — 3 titles + description
- `Package/Thumbnails/concept_1.png`, `concept_2.png`, `concept_3.png` — real rendered thumbnails, ready to present to Tony

---

## PHASE 10 — BLOTATO UPLOAD (⏸ PAUSE for final selections)

Follow the full procedure documented at:
```
001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/upload_to_blotato.md
```

Summary:

⏸ **PAUSE — present Tony the final video (duration/size), the 3 titles from `Package/YouTube_Package.md`, the 3 thumbnail concepts from `Package/Thumbnails/`, and a privacy status choice (private/unlisted/public). Wait for his picks before uploading**, even if a previous production's answers seem like an obvious default.

- Compress the chosen thumbnail if over 2MB: `ffmpeg -y -i input.png -vf "scale=1920:-1" -q:v 5 output.jpg`
- Get presigned upload URLs via `mcp__blotato__blotato_create_presigned_upload_url` for the final video and thumbnail, `curl -X PUT --data-binary` each.
- Call `mcp__blotato__blotato_create_post` with `accountId: "42514"` (Anomalous Wild's confirmed Blotato YouTube account — displayed there as "Anomalos Wild," a spelling variant of the same channel; do not confuse with `30323`, which is Reimagined Realms), Tony's chosen title/description/thumbnail/privacy, and the locked defaults: `isMadeForKids: false`, `containsSyntheticMedia: true`, `shouldNotifySubscribers: false`, `playlistIds` omitted (Tony adds these manually during scheduling).
- Poll `mcp__blotato__blotato_get_post_status` (≥10s between polls) until `published` or `failed`. Report the live `publicUrl` back to Tony.

---

## FINAL DELIVERY

The pipeline runs start to finish — Phases 1–10 — ending with a live (private, unless Tony says otherwise) YouTube upload, not a handoff of files for Tony to assemble manually. When all 10 phases are complete, output a summary:

```
✅ Anomalous Wild pipeline complete — uploaded to YouTube.

Production folder: [full path]
├── Scripts/               ✓ Script.md, Narration.md
├── Narration_Audio/       ✓ per-scene .mp3 + word-level *_beat_sheet.json
├── Production/            ✓ Scene_Routing.json, Beat_Table.json, Shot_List.md,
│                            end_card_reference.txt
├── Images/, Video_Clips/  ✓ live-footage clips + diagram illustrations
│                            (each diagram beat also has illustration.png,
│                            reference_image.jpg, label_coordinates.json)
├── Remotion/               ✓ BioluminescenceDoc.tsx-style composition,
│                            incl. DiagramLabels overlays for diagram beats
├── Assembly/               ✓ raw_video.mp4, stems_mix.mp3, narration.mp3,
│                            music.mp3, <prod>_final.mp4 (end card appended,
│                            never regenerated)
├── Package/                ✓ YouTube_Package.md (3 titles + description),
│                            Thumbnails/concept_1-3.png
└── YouTube                 ✓ Published as [privacyStatus] — [publicUrl]

Remaining manual step: review the private upload, then flip privacy status and add to playlists in YouTube Studio when ready.
```

---

## REFERENCE — Key File Paths

| Resource | Path |
|---|---|
| Pricing cache | `001_Architecture/Tools/Tool-Manager/data/pricing_cache.json` |
| kie.ai model ID lookup | `001_Architecture/Tools/Tool-Manager/data/kieai_pricing_api.json` — find entry by `modelDescription`, extract API model ID from `anchor` URL `?model=<id>` |
| Motion-graphics/composition tool capability profile (Tool-Manager routing input) | `001_Architecture/Tools/Tool-Manager/data/motion_graphics_capabilities.json` |
| New-video intake/research | `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/new_video.py` (questionnaire + research only — do not use its folder scaffolder) |
| Scriptwriter skill | `002_Content-Creation/Video_Editor/.agents/skills/Anomalous-Wild-Scriptwriter.md` |
| Visual/tone style guide | `002_Content-Creation/Video_Editor/.agents/styles/Anomalous-Wild-Hybrid.md` |
| Production folder scaffolder (always use this, never new_video.py's) | `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/scaffold_new_production.py` |
| Narration + word-level timestamps | `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_narration_with_timestamps.py` |
| Beat table builder | `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/build_beat_table.py` |
| Scientific Diagram sub-pipeline (steps 1–2: reference + illustration) | `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/diagram_research_and_illustrate.py` |
| Scientific Diagram sub-pipeline (step 3: coordinate detection) | `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/detect_label_coordinates.py` |
| Scientific Diagram sub-pipeline (step 4: label placement, Remotion) | `002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-components/DiagramLabels.tsx` |
| Live-footage batch generation (existing) | `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/pipeline_supervisor.py`, `pipeline_orchestrator.sh`, `preloop_videos.sh`, `check_pipeline_status.py` |
| Remotion assembly engine pattern (existing) | `002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-components/BioluminescenceDoc.tsx` (precedent: `002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/0001_Bioluminescence_Weapon/Remotion/BioluminescenceDoc.tsx`) |
| Locked end-card asset | `002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Brand_Assets/End_Card/end_card_v3.mp4` |
| Audio pipeline (this session, AW copies of RR originals) | `compose_audio.py`, `generate_stems.py`, `analyze_stems.py`, `mix_stems.py`, `render_video.py`, `render_outputs.py`, `generate_suno_music.py` — all in `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/` |
| YouTube package generator (titles/description/thumbnails) | `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_youtube_package.py` |
| Blotato upload procedure | `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/upload_to_blotato.md` |
| Blotato YouTube account ID (Anomalous Wild) | `42514` (do not confuse with `30323`, Reimagined Realms) |
| Production folder root | `002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/` |
| Channel content system | `002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Anomalos_Wild_Content_system.md` |
