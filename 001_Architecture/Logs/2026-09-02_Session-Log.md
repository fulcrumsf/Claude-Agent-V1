# 2026-09-02 Session Log

## Shot 6 Storyboard Direction Correction

- Tony approved the visual content of Shot 6 storyboard v2 but identified one
  semantic error: the frame 3 caption says Grandma opens the gate toward the
  bear, while the image correctly shows her pulling it toward the camera and
  away from the bear.
- Corrected the structured source-of-truth contract in
  `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/shot_06_storyboard_spec.json`.
  Frame 3 now encodes the safer pull-toward-camera action and exact caption,
  and adds a hard constraint forbidding a push toward the bear.
- Preserved v2 unchanged and rendered the corrected versioned prompt at
  `Prompts/Shot-06-GPT-Image-2-Storyboard-v3.md`.
- No new image generation was submitted. The 45-test relevant suite passes.
- Recommended next decision: repair only the baked caption band to preserve the
  already-good visuals, or authorize a new v3 image generation if Tony prefers
  the model to recreate the complete sheet.

## Shot 6 Caption Repair

- Tony approved a caption-only repair to preserve the visually correct v2
  storyboard without another full storyboard generation.
- Edited only frame 3's caption through the image-edit path. The corrected text
  is: `Grandma pulls the left gate toward her, away from the bear.`
- Saved the repaired result as
  `Images/Shot-06-Storyboard-v3.png`; v2 remains preserved and unchanged.
- Verified the resulting PNG exists and has SHA-256
  `bab8975e129b900da8f65db1bd4f7fa5210c592ac87fdb83c11988a1b959fcd1`.
- No video generation or Seedance submission occurred. Manual storyboard
  approval remains required before video generation.
## Shot 06 Seedance v3
- Tony approved the corrected Shot-06 storyboard v3 and authorized one Seedance generation.
- Corrected the contract's stale gate-direction phrases so all handoff language says Grandma pulls the gate toward the camera and away from the bear.
- Submitted Seedance 2 Mini with the storyboard in `reference_image_urls` only, then completed Topaz 2x and FFmpeg normalization.
- Final output: `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Video_Clips/Shot-06-1080p-v3.mp4`.
- Technical checks passed: 1920x1080, 24 fps, AAC audio, 10.08 seconds.
- Visual spot-check found a major continuity failure: a later sampled frame duplicates Grandma on both sides of the bear. Clip is preserved and marked `completed_visual_review_required`; no automatic second generation submitted.
- Tony clarified that the duplicate Grandma and non-English dialogue were errors. The replacement v4 raw generation must contain exactly one Grandma, no dialogue, and a fully locked-off camera.
- v4 raw generation returned at 480p and is intentionally held for Tony's manual approval. No Topaz upscale or FFmpeg normalization was run.
- Tony rejected v4: multiple camera views, unwanted "yeah yeah" dialogue, and Grandma exiting/re-entering. v4 remains raw only; prepared v5 prompt with one locked camera, one Grandma, silence, and no exit/re-entry.
- Tony authorized the v5 raw test. Seedance v5 returned successfully and is held at 480p for manual approval; no upscale or normalization was run.
- Tony rejected v5 because it still had double Grandma, multiple camera angles, and commercial-like audio. Regenerated the storyboard as v4 with one locked-off composition, no vehicle, exactly one Grandma, and exactly one bear. Awaiting storyboard approval before any new video generation.
- Locked Neon Parcel realism requirements into the schema, storyboard renderer, Seedance handoff builder, shared realism contract, and both prompting skills: explicit real-life tone, consumer smartphone capture, subtle handheld default unless shot-specific lock, non-commercial visual realism, and atmospheric/foley-only audio exclusions.
- Focused test suite passed: 65 tests.
- Tony approved storyboard v5 and schema-generated Seedance prompt v6. Submitted one guarded raw v6 generation; it returned successfully and is held at 480p for manual review. No upscale or normalization was run.
# 2026-09-02 Session Log — Glass Frog 0003 revision round 1, blocks A/B

## Block A finished + Tony-approved
- DiagramLabels.tsx rebuilt to reference aesthetic; DiagramShot model (same-image
  runs merged, eased camera, dwell-holds under labels); 0.5s cross-dissolve on all
  cuts (SceneVisual/SceneFade/DiagramScene/NarrationTrack); SceneOverlay callout
  50%-black plate; scene 06B camera-hold-under-labels fix.
- Skill rollout: AW SKILL Phase 7 (cross-dissolve default + camera/label rules),
  Diagram-Generation SKILL (label aesthetic section + Reference_Examples/),
  design-rules-learned Rules 5 & 6.
- TODO: Reimagined_Realms pipeline + assemble.py need the cross-dissolve default.

## Block B (in progress)
- 5 storyboards generated (Storyboard-Generation skill) → Tony approved.
- 10 start/end frames regenerated (gen_frames.py) grounded in the storyboards +
  character sheet. Old frames → Rejected_RevisionRound1/.
- 5 Seedance 1.5 Pro clips generating (regen_clips.py, task bti33df6a): 04D, 06A,
  06F, 06G, 06H. 04D done (9.05s raw → trimmed 6.07s). Others in progress.
- Scripts copied to production Scripts/ folder (durable).

## Handoff
RESUME_NOTES.md rewritten as the full where-are-we / what-next handoff.
Revision_Notes_Round1.md is the master plan (23 notes + P1-P8).
Branch glass-frog-0003-revision-round1, NOT committed (working tree also has
unrelated pre-existing dirty files — commit list is in RESUME_NOTES.md).

## Block B RESULTS
5 Seedance 1.5 Pro clips generated + trimmed + in place (Video_Clips/). Re-rendered
GlassFrogDoc (FULL7, scratch). Scans clean. 0 internal cuts in any clip.
- 04D ✅ (lunge/snap at moth; wrong-beat + leg glitch fixed)
- 06A ✅ (continuous pull-back, no cut; doesn't reach full Amazon aerial)
- 06F ❌ (Seedance can't do transparency-dissolve; frog crawled + got more opaque)
- 06G ✅-ish (great push-in; weak frog reveal at end)
- 06H ⚠️ (frog stays visible; vanish didn't happen)
KEY FINDING: Seedance 1.5 Pro cannot animate "become transparent/invisible."
06F + 06H "vanish" beat must be done in ASSEMBLY — crossfade the clip to a static
Img of its _End.png over the last ~1.5s. Documented in RESUME_NOTES next-steps.
Also: all 5 clips came back ~3s LONGER than requested (Seedance overshoot);
clip_durations head-trim handled it cleanly.

Session ending for context. RESUME_NOTES.md is the handoff.
- Shot 06 v7-first-last generated with approved first/end anchors and no audio. Tony approved the raw clip despite a minor gate defect; next step is paid Topaz upscale and final 1920x1080 normalization.
- Pipeline preservation enforcement added: versioned paid attempts are required, provider downloads reject unversioned or existing paths, archive moves are collision-safe, and storyboard-to-first/last fallback plus manual inspection gates are documented in the Seedance and Storyboard skills. Neon Parcel tests: 71 passing; focused Kie/preservation tests passing.
- Neon Parcel dual-skill requirement locked into `pipeline.yaml` and `Seedance-Prompt-Contract.json`: every storyboard and Seedance prompt must use both `Storyboard-Generation` and `Seedance-Prompting-Guide` context. The contract also records raw inspection before upscale, first/last fallback after storyboard-route failure, and append-only version/archive rules.

## 2026-09-02 (evening) — Glass Frog 0003 Block C (VO pops / P6)
- Tony signed off on Block B (edit + 5 re-run clips). FULL7 copied to production `Renders/`.
- Block C investigation (systematic-debugging): raw scene_04/06 VO mp3s clean; FULL7 render clean end-to-end; the pops only ever existed in the superseded Aug-29 assembly's SFX layer. Block A's `NarrationTrack` already removed the per-beat concat path.
- Root cause of the bug class: `Reimagined_Realms/assemble.py::phase_concat_narration` used `ffmpeg -f concat -c copy` (raw mp3 splice) for `narration.mp3`, which `render_outputs.py` feeds the final mix.
- Fix: `build_narration_concat_filter()` — 20ms fade-out/fade-in pair at every scene join (duration-preserving). CTA-append gets a 20ms fade-in. `NARRATION_JOIN_FADE_S=0.02`. `test_assemble_narration.py` (6 tests, pass). Integration-verified on real 0003 mp3s: <1ms drift, join Δ ≤0.069 (was ≤0.77).
- Docs: AW SKILL Phase 8 "no hard audio concat" rule; Revision_Notes_Round1.md Block C section.
- No 0003 re-render needed. P6 satisfied. Next per Tony's "go in order": range map (Note 9/10), then 06F/06H vanish, then Block D.
- Prevention (Tony: "make sure it doesn't happen again"): NEW `Anomalous_Wild/audio_pop_scan.py` + `test_audio_pop_scan.py` (7 tests) — raw-PCM splice-pop detector, exit 1 on any silence-bounded/very-hard step or narration-join discontinuity. Verified: FULL7 → clean/exit0, old Aug-29 mix → exit1 (catches the 3:27 pop). Wired into AW SKILL Phase 8 as a mandatory pre-review gate + tools table.
- Notes 9/10 (scene-04 range map): replaced the abstract green squiggle with a real map. Sourced Natural Earth II shaded relief (NE2_50M_SR_W, public domain, no attribution), cropped to lon[-112,-38]/lat[-13,28.6], styled to AW palette (navy ocean via blue-channel mask, dark-green relief land, coastline, vignette) → `Images/scene_04_range_map/basemap.png` + SOURCE.md. Rewrote `RangeMapAnimation` in GlassFrogDoc.tsx: <Img> basemap fade-in + slow push, glowing range path (pathLength/dashoffset) tracing real geography S.Mexico→Pacific C.America→Panama→Colombian Andes→down Andes→W.Amazon, pulsing end dot, restyled lower-left caption. tsc clean, black scan clean, stills verified.
- Process rules locked (Note 9's "learn from this"): map/geography-beat = real basemap + path-over-real-geography, never path-only. Added to Production-Research-Agent (Step 2b), Production-Asset-Planner (Step 3b), Diagram-Generation (map/geography type), AW SKILL Phase 5B.
- FULL8 render running in background (scratchpad/FULL8.mp4).
