# RESUME NOTES — 0003 Glass Frog Transparency

**Last updated: 2026-09-04. STATUS: ✅ COMPLETE — graded A, published.**

═══════════════════════════════════════════════════════════════════════
## ✅ DONE (2026-09-04) — video approved + published
═══════════════════════════════════════════════════════════════════════

- **Grade A** (Tony: "almost an A+, just not quite"). Final cut:
  `Renders/FULL16_v2a_cta-matched.mp4` = canonical `Renders/0003_Glass_Frog_Transparency_FINAL_v2a.mp4`.
- **Published PRIVATE** via Blotato (acct 42514): https://www.youtube.com/watch?v=JMn32MmAzWw
  — same title #1, same description, `concept_1_final.jpg` thumb. **Tony deletes the
  old private `LiJcg5aUu6I` manually.**
- **Block E audio (v2a):** NEW `generate_stems_v2a.py` (fal.ai Mirelo SFX v1.6,
  motion-conditioned ambience, now the AW default; ElevenLabs = fallback) →
  `Assembly/V2A/v2a_bed.mp3`. Mix: bed -25 + gentle duck (a hair under score),
  Suno track-2 score -22 + duck, narration -14. End card CTA VO rebuilt to -14
  (`Assembly/V2A/end_card_cta_matched.mp4`).
- **This is the AW milestone reference video** — `Production/Milestone_Reference.md`.
- Docs synced to shipped cut: `Data/Report_Card.md`, `Production/Shot_List.md`,
  `Production/Timeline_Cut_Map.md`.
- Hardened: AW SKILL (v2a default, stems -25, CTA-level rule, NEW PRE-REVIEW GATE),
  `render_outputs.py` (stems -25 + duck).

**STILL OPEN:** commit the branch (see COMMIT LIST below — add `generate_stems_v2a.py`,
`Data/v2a_segment_map.json`, `render_outputs.py`, `Production/Milestone_Reference.md`,
`Images/scene_03/glass_frog_photo/`, `Images/scene_04_range_map/`); Block D pipeline
items P1/P2/P7/P8 + limb-deformation checker + push 0.5s cross-dissolve into
`Reimagined_Realms` SKILL + `assemble.py`; minor range-map "Amazon basin" timing.

═══════════════════════════════════════════════════════════════════════

**Historical handoff below (2026-09-03, superseded by the above).**

Full detail of every note = `Revision_Notes_Round1.md` (23 originals + a ROUND 2
section, R2-1..R2-6). Branch = **`glass-frog-0003-revision-round1`**, NOTHING
COMMITTED.

═══════════════════════════════════════════════════════════════════════
## 🚩 SESSION-END HANDOFF — 2026-09-03 EOD (start here)
═══════════════════════════════════════════════════════════════════════

**Every visual edit note (23 + R2-1..R2-6) is DONE and Tony-approved.**
The video is live-PRIVATE on YouTube from the original run; this branch is the
revised cut, not yet re-uploaded.

### Tony's current pick
**`Renders/FULL13_final_v3b_science-score-alt.mp4`** — video + narration + Suno
**track 2** score + the new locked mix. Tony 2026-09-03: "I like version 3b better."
This is the best full cut right now (no ambience layer, no end card yet).
- Chosen score saved: `Assembly/Score/glass_frog_score_CHOSEN_track2_body_232s.mp3`
- Body narration saved: `Assembly/Score/narration_body_232s.mp3` (= FULL13's baked
  NarrationTrack, the correct 232.917s body VO. The old `Assembly/narration.mp3`
  is 242.9s WITH the CTA appended — wrong for the no-end-card body, do not use it.)
- Video-only render (all edits, narration only): `Renders/FULL13_RevisionRound1_R2_xfades.mp4`

### WHAT'S LEFT (recommended order)
1. **Ambience/SFX stems — Tony's call whether to do it at all.** NOT in the mix.
   Blockers: `Assembly/stems_mix.mp3` is on the OLD 242.9s timeline + old scene-6
   timings; `Audio_Stems/Scene_06{F,G,H}.mp3` are STALE (pre-Block-B clips); the
   regenerated 06F/G/H clips have **no audio stream**. → full stems regen against
   the new 232.917s timeline (compose_audio → generate_stems → mix_stems), then
   re-mix. If skip: narration+score cut is deliverable.
2. **End card + CTA VO.** Body has no end card. Append `Anomalos_Wild_End-Card_Hero.mp4`
   (path in `Production/end_card_reference.txt`) + spoken CTA VO (AW SKILL "End
   card CTA" — auto-pick from 3-line rotation, this production's ElevenLabs voice).
3. **Block D — pipeline hardening (does NOT touch this video):** P1 Clip_Plan.json
   provenance (Tony wants), P2 Seedance split-and-chain default, P7 clip-vs-VO
   validation, P8 shot-boundary detector, NEW per-frame limb-deformation checker
   on generated clips (from R2-6), apply 0.5s cross-dissolve default to
   `Reimagined_Realms` SKILL + `assemble.py`. (P3/P4/P5/P6 done this arc.)
4. **Block E — full review with Tony**, fill in `Data/Report_Card.md`, grade,
   then **re-upload final to YouTube** replacing the live-private cut.
5. Minor: range map exits ~2.5s before VO says "Amazon basin" (Tony's call to fix).

### HARDENED THIS ARC — do not revert
| File | Change |
|---|---|
| `Anomalous_Wild/audio_pop_scan.py` (+test) | NEW splice-pop gate, in AW SKILL Phase 8 — run before every review |
| `Reimagined_Realms/assemble.py` (+`test_assemble_narration.py`) | `phase_concat_narration` now fade-joins VO mp3s (was hard `concat -c copy`) |
| `Anomalous_Wild/render_outputs.py` | music `loudnorm -22` (was -26), duck `0.045:2.5:300:600` (was `0.015:4:150:800`) — Tony A/B'd. See `feedback-audio-mix-formula` memory. |
| `Anomalous_Wild/generate_suno_music.py` | saves BOTH Suno tracks + `_suno.json` prompt sidecar. AW score = "science doc," not solo-piano/mystery. |
| Skills | Production-Research-Agent (2b), Production-Asset-Planner (3b), Diagram-Generation (map type + label aesthetic), AW Pipeline (Phase 5B/7/8) |
| `design-rules-learned.md` | Rules 5 (label aesthetic), 6 (0.5s cross-dissolve default) |

### COMMIT LIST (when Tony asks) — code/`.md`/`.py` only, NEVER `.mp4`
`GlassFrogDoc.tsx` `DiagramLabels.tsx` `SceneOverlay.tsx` `design-rules-learned.md` ·
AW: `audio_pop_scan.py`(+test) `render_outputs.py` `generate_suno_music.py`
`clip_durations.py`(+2 tests) `pipeline_supervisor.py` · RR: `assemble.py`(+test) ·
SKILLs: `Anomalous_Wild_Video_Pipeline` `Diagram-Generation` `Production-Asset-Planner`
`Production-Research-Agent` `Seedance-Prompting-Guide` + `Reference_Examples/` ·
`Feedback_Loop/2026-08-3*` `2026-09-0{1,3}_Feedback.md` · `Logs/2026-08-3*`
`2026-09-0{1,3}_Session-Log.md` · `Global_Agent_Memory.md` · production `.md`/`.py`
+ `Images/scene_03/glass_frog_photo/` + `Images/scene_04_range_map/` (PD-derived
PNGs + SOURCE.md). Do NOT sweep the unrelated pre-existing dirty files (see "Git").

═══════════════════════════════════════════════════════════════════════

## LATEST (2026-09-03) — detailed changelog
- Block A ✅ approved. Block B ✅ approved ("okay with the edit and the re-run videos").
- Block C (VO pops) ✅ — render was already clean; fixed the pipeline hard-concat in
  `Reimagined_Realms/assemble.py` + NEW `Anomalous_Wild/audio_pop_scan.py` gate
  (wired into AW SKILL Phase 8). See Block C section below.
- Notes 9/10 (range map) ✅ — real Natural Earth basemap + geography-traced path.
- **Round 2 R2-1 (map labels + less desat + Andes relief) ✅ done 2026-09-03.**
- **Round 2 R2-2 (scene 03 ~1:00 → Ken-Burns glass-frog photo) ✅ done 2026-09-03.**
  Prompt approved; GPT-Image-2 v1 chosen; `MIRRORED_POUCH_03` shot shortened to
  9.8s + new `FROG_PHOTO_03` DiagramShot cross-dissolves in at ~43s. Photo +
  SOURCE.md in `Images/scene_03/glass_frog_photo/`.
- **R2-3 (06F/06H "vanish") ✅ done 2026-09-03** — Block B fully complete. New
  `VideoSegVanish` helper: clip plays, last ~2s cross-dissolves to the shot's
  `Scene_06{F,H}_End.png` still (frog dissolved into leaf). No regen.
- **R2-4 (2026-09-03): 06F→06G→06H tail reworked** — Tony caught a horizontal-band
  tear at 06F→06G on FULL11 + "06G too fast". New `VanishShot`/`HeldVideoShot`:
  no two live OffthreadVideos overlap, video unmounts before its clip boundary,
  held tails use pre-extracted PNG stills, every boundary a ~1.3s crossfade, 06G
  held+KenBurns'd to ~8.8s. Verified tear-free on encoded frames.
- **R2-5 (2026-09-03): 0.5s cross-dissolve on EVERY cut.** Note-1 crossfade was
  only on scene boundaries + diagram image changes + the 06F/G/H tail; scene_04
  b-roll cuts and scene_06 06A→06E were still hard. New `ChainScene` helper
  (freeze-under/live-over 0.5s dissolve) — scene_04 + scene_06 front converted.
  `DiagramSeg`→`DiagramSegInner` for chain nodes. All 10 boundary stills + encoded
  frames verified, no tearing.
- **R2-6: 06F ~3:32 toe deformation (3-4→1 toe mid-crawl)** — Tony LET IT PASS.
  Logged in `Data/Report_Card.md` + the gap (no generated-clip limb checker).
- **R2-7 (2026-09-03): audio mix retuned + new science-doc score.** Locked new
  values in `render_outputs.py` (music `-22`, duck `0.045:2.5:300:600`).
  `generate_suno_music.py` rewritten (saves both tracks + prompt). **Tony picked
  Suno track 2** → `Renders/FULL13_final_v3b_science-score-alt.mp4`.
- **Latest video-only render: `Renders/FULL13_RevisionRound1_R2_xfades.mp4`**;
  latest full cut w/ score: `Renders/FULL13_final_v3b_science-score-alt.mp4` (both
  black + audio pop scan clean).
- Nothing committed yet on branch `glass-frog-0003-revision-round1`. Add to commit
  list: `Images/scene_03/glass_frog_photo/` (v1/v2/illustration.png + SOURCE.md).

## What's actually left after R2-3
1. **Block D pipeline items** — P1 (Clip_Plan.json provenance), P2 (Seedance
   anatomy-reveal split-and-chain default), P7 (clip-vs-VO validation), P8
   (shot-boundary detector). P3/P4/P5/P6 already done. + apply 0.5s cross-dissolve
   default to `Reimagined_Realms` SKILL + `assemble.py`.
2. **Final Phase 8 audio** — narration + NEW score DONE 2026-09-03. Mix formula
   RETUNED + locked (`render_outputs.py`): music `loudnorm -22` (was -26), duck
   `threshold=0.045:ratio=2.5:attack=300:release=600` (was 0.015/4/150/800) —
   Tony A/B'd, "worked great." New "science documentary" Suno score generated
   (`Assembly/Score/glass_frog_score_v2_{v1,v2}.mp3` + `_suno.json` — both tracks
   saved now; `generate_suno_music.py` rewritten for that). Two mixes for Tony:
   `Renders/FULL13_final_v3_science-score.mp4` (Suno track 1, looped) +
   `_v3b_science-score-alt.mp4` (track 2). **Still NOT included:** SFX/ambience
   stems (`stems_mix.mp3` on old 242.9s timeline; Audio_Stems/Scene_06{F,G,H} stale;
   regen 06F/G/H clips have no audio) — full stems regen needed IF Tony wants
   ambience. Then append end card + CTA VO.
3. **Block E** — full review with Tony, then re-upload final to YouTube (replaces
   the live-private cut).
4. Minor: range map exits ~2.5s before VO says "Amazon basin"; RangeMap→04B hard
   cut (folds into #1's cross-dissolve sweep).

---

## Status in one paragraph

The Glass Frog video (0003) shipped LIVE-PRIVATE on YouTube
(https://www.youtube.com/watch?v=LiJcg5aUu6I) from a full autonomous pipeline run.
Tony then did a full frame-by-frame edit review and gave 23 notes. We are working
through them on git branch **`glass-frog-0003-revision-round1`** (branched from
`main`, **NOT committed** — see "Git" below). **Block A (Remotion-only) is DONE and
Tony approved it. Block B (5 clip regenerations) is executing right now.**

---

## What's DONE (block A — Tony approved 2026-09-01)

All in `002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-components/`:

1. **`DiagramLabels.tsx` — fully rebuilt** to the reference aesthetic
   (`001_Architecture/Skills/Diagram-Generation/Reference_Examples/Label_Aesthetic_Red_Blood_Cells.png`):
   big bold white term, accent parenthetical auto-split from "(...)", thin white
   leader line that draws on + end dot, glowing target ring, black outline,
   collision avoidance, `labelHoldS` fade-out, optional description.
2. **`GlassFrogDoc.tsx` — new `DiagramShot` model.** Same-image runs are now ONE
   shot with ONE eased camera path (kills the "remount jump"). `S03_SHOTS` (4),
   `S05_SHOTS` (6). `DiagramCamera` does per-segment ease-in/out; `buildPath()`
   `holdS` = dwell keyframes so the **camera holds still under every label**
   (Tony's Note 4: move→settle→label in→hold→label out→move).
3. **Crossfades everywhere** (~0.5s): `DiagramScene` cross-dissolves within-scene
   image changes; `SceneVisual`/`SceneFade` cross-dissolve scene boundaries
   (outgoing scene FREEZES its last frame for the tail so video clips don't loop);
   `NarrationTrack` = one hard-cut VO track with 3-frame edge fades.
4. **`SceneOverlay.tsx`** — `callout` type gets a 50%-black backing plate
   (`rgba(0,0,0,0.5)`) that eases in/out with the text.
5. **Scene 06B** (`Scene06Content` DiagramSeg) — camera now holds on clot/platelets
   while those labels are up, then eases to normal_blood_flow as they fade
   (Note 21). `DiagramSeg` gained `labelHoldS`/`labelScale` passthrough.
6. Earlier same-branch fixes still in place: black-frame fixes (`<Img>` not `<img>`,
   frame-exact `SCENE_FRAMES`, scene_02 tail), `VideoSegFilled` + `KenBurns`
   freeze-fill, the `clip_durations.py` padding/trim + `pipeline_supervisor.py`
   wiring + tests.

**Verified:** strict + generous black scan NONE, white scan NONE, `tsc` clean
(only 2 pre-existing unrelated TS6133 in other files). Reference render:
`FULL6.mp4` in the scratchpad (now stale — re-render after block B).

Remotion Studio: `cd 002_Content-Creation/Video_Editor/003_Remotion && npm run
remotion` (was running on :3101).

---

## What's RUNNING NOW (block B — 5 clip regenerations)

**Check the background task output first:**
`/private/tmp/claude-501/.../342bbeaf-.../tasks/bti33df6a.output`
(scripts: `scratchpad/gen_frames.py`, `scratchpad/regen_clips.py` — copy them out
of scratchpad if you need them again; scratchpad is session-local).

5 clips being regenerated via **Seedance 1.5 Pro** (`bytedance/seedance-1.5-pro`,
kie.ai direct createTask, `input_urls: [start, end]`, `generate_audio: true`):

| clip file (overwrites in place) | target | why |
|---|---|---|
| `Video_Clips/scene_04/Scene_04D_looped.mp4` | 6.07s | Note 11+13: leg glitch + wrong beat (showed a heart; VO is the tongue-flick) |
| `Video_Clips/scene_06/Scene_06A_looped.mp4` | 6.30s | Note 20: internal Seedance cut ~3s in |
| `Video_Clips/scene_06/Scene_06F_looped.mp4` | 8.07s | Note 22: 3 near-identical pull-backs — this is now "backlit transparency" |
| `Video_Clips/scene_06/Scene_06G_looped.mp4` | 6.07s | Note 22: now "grand wide → find the frog" |
| `Video_Clips/scene_06/Scene_06H_looped.mp4` | 5.07s | Note 22: now "intimate upside-down vanish" + fix deformed frog |

- Storyboards (Tony APPROVED): `Images/Storyboards/RevisionRound1/`
- New start/end frames (Tony saw the pairs, look good):
  `Images/Start_End_Frames/Scene_0{4D,6A,6F,6G,6H}_{Start,End}.png`
  (old ones backed up in `Images/Start_End_Frames/Rejected_RevisionRound1/`)
- 04C stays as-is (only 04D was flagged).

### Block B RESULTS (2026-09-02) — all 5 clips generated, trimmed, IN PLACE, re-rendered (`FULL7.mp4` in scratchpad). Black/white scans clean. Internal-cut check: **0 cuts in any clip** (the "no cut" negatives worked, incl. 06A).

Per-clip assessment (extract frames + judge yourself, montages were in scratchpad):
- **04D ✅** — frog holds in ambush crouch, then lunges / snaps at the moth. Wrong-beat
  (heart) + leg glitch both GONE. Anatomy clean. Good. (Tongue reads more as a
  mouth-lunge than a long pink flick, but the beat lands.)
- **06A ✅ (Tony to judge)** — one continuous pull-back, NO internal cut. Goes from
  macro-frog-on-leaf out to a wide misty forest-valley — does NOT reach the full
  aerial-Amazon of the end frame. Clean continuous move though. Tony may want it
  wider / or it's fine.
- **06F ❌ NEEDS WORK** — Seedance can't animate "become transparent/invisible". It
  made the frog CRAWL across the leaf and become MORE opaque (wrong direction),
  organ blob showing. The clip itself is a fine "frog on a backlit leaf" shot but
  it does not deliver the vanish beat.
- **06G ✅-ish** — gorgeous continuous push-in over the golden misty canopy +
  waterfall. Frog "reveal" at the very end is weak / barely visible. Mostly good,
  maybe wants the end to settle on the frog more.
- **06H ⚠️ NEEDS WORK** — frog stays clearly visible the whole time; the
  "disappears into the leaf" doesn't happen (same Seedance limitation as 06F).
  Anatomy clean. Just doesn't deliver the vanish.

### NEXT SESSION — finish block B:
1. **06F + 06H — do the "vanish" in ASSEMBLY, not Seedance** (Seedance 1.5 can't do
   a transparency dissolve). Play the Seedance clip, then in the last ~1.5–2s
   **crossfade to a static `<Img>` of that shot's `_End.png` frame** (frog
   dissolved into the leaf). New Remotion helper, or extend `VideoSegFilled` with
   an `endFrameOverlay` fade. This achieves "the frog slowly becomes invisible"
   using the end frame we already generated. Cheap, no regen.
2. **06G** — optionally regen with the end frame pushed tighter on the frog, OR
   accept (a camouflaged frog being hard to spot is on-theme). Tony's call.
3. **06A** — accept, or regen aiming for the fuller aerial. Tony's call.
4. **04D** — accept (it's good).
5. Once 06F/06H are handled: re-render, re-scan, present to Tony for block-B notes.

Old approach note: all 5 Seedance clips came back ~3s LONGER than requested
(8s req → 9–11s raw) — Seedance overshoots here; `clip_durations.trim_to_target`
head-trimmed each to exact target cleanly (no shortfalls).

---

## What's PENDING (blocks C, D, E)

**Block C — audio pops (Note 23 / P6): DONE 2026-09-02.** Investigation (raw-PCM +
numpy): raw `scene_04/06.mp3` clean; FULL7 render clean end-to-end; the pops only
existed in the superseded Aug-29 assembly's SFX layer (Δ up to 0.77 @ 1:58 & 3:27,
never the VO). Block A's `NarrationTrack` already killed the per-beat concat path.
Root cause of the bug class: `Reimagined_Realms/assemble.py::phase_concat_narration`
used `ffmpeg -f concat -c copy` on the scene VO mp3s. Fixed: `build_narration_concat_filter()`
now re-encodes with a 20ms fade-out/fade-in pair at every join (duration-preserving),
+ `test_assemble_narration.py` (6 tests), + AW SKILL Phase 8 "no hard audio concat"
rule. `mix_stems.py`/`compose_audio.py` already faded stems correctly. **No 0003
re-render needed** — current cut's VO is pop-free; fix protects the eventual final
music+SFX mix and every future video. Add `assemble.py`, `test_assemble_narration.py`
to the commit list.

**Note 9/10 — scene 04 range map: DONE 2026-09-02.** Real Natural Earth basemap
(PD, no attribution), AW-styled, in `Images/scene_04_range_map/basemap.png` +
SOURCE.md; `RangeMapAnimation` rewritten to draw the glowing range path over the
real geography (S.Mexico→C.America→Andes→W.Amazon, pulsing end dot). Process rules
locked into Production-Research-Agent / Production-Asset-Planner / Diagram-Generation
/ AW SKILL. Minor open: map exits 2.5s before VO says "Amazon basin" (Tony's call).

**Block D — pipeline/skill items P1–P8** (full text in `Revision_Notes_Round1.md`):
- P1: `Clip_Plan.json` per-clip provenance (`model`, `storyboard`, `first_frame`,
  `last_frame`, `real_generated_s`, `chained_from`) — Tony explicitly wants this.
- P2: Seedance-1.5 anatomy-reveal beats split-and-chained by default.
- P3: geography beats require a research-sourced map asset.
- P4/P5: diagram camera-holds + label aesthetic (DONE in skills — see below).
- P6: no hard audio concat anywhere; every join faded (ties to block C).
- P7: every generated clip validated against its beat's VO before acceptance.
- P8: shot-boundary detector on every generated clip; reject internal cuts.
- Also TODO: apply the 0.5s cross-dissolve default to
  `Reimagined_Realms_Video_Pipeline/SKILL.md` + `assemble.py` (Tony: "global thing").

**Block E — final review pass** with Tony on everything.

---

## Skill / doc updates made THIS arc (so the next session doesn't redo them)

- **`Anomalous_Wild_Video_Pipeline/SKILL.md`** — Phase 6A: `new_clips_prompts.json`
  video entries carry `target_duration_s` only; supervisor computes padded API
  duration + trims + hard-fails/needs_fill short footage; refuses to start without
  `target_duration_s`. Phase 7: ffprobe-durations rule, no-black-frames rule
  (+ raw-`<img>` / frame-rounding / short-nested-sequence causes), **0.5s
  cross-dissolve default rule**, **camera-holds-under-labels + label-aesthetic +
  callout-plate rule**.
- **`Diagram-Generation/SKILL.md`** — new "Label / callout aesthetic + camera
  behaviour" section, points at `Reference_Examples/` and design-rules-learned.
- **`Reference_Examples/`** (NEW folder in Diagram-Generation skill) —
  `Label_Aesthetic_Red_Blood_Cells.png` (target, from Tony's GPT-Image-2 ref, was
  renamed from "Codex Image Aug 30…png"), 2 agent-extracted anti-examples, README.
- **`Production-Asset-Planner/SKILL.md`** Step 6 — planners record
  `target_duration_s` only, no hand-set `generation_duration_s`.
- **`Seedance-Prompting-Guide/SKILL.md`** — floor section rewritten:
  `ceil(target)+1` clamped to model range, then trim; enforced in
  `clip_durations.py`.
- **`design-rules-learned.md`** — Rule 5 (label aesthetic + camera under labels),
  5b/5c, Rule 6 (0.5s cross-dissolve default, global).
- **NEW code:** `.../Channels/Anomalous_Wild/clip_durations.py` +
  `test_clip_durations.py` + `test_pipeline_supervisor_durations.py` (17 tests
  pass). `pipeline_supervisor.py` wired to it.
- **Feedback_Loop:** `2026-08-30_Feedback.md`, `2026-08-31_Feedback.md`,
  `2026-09-01_Feedback.md` (new). **Logs:** `2026-08-30`, `2026-08-31`,
  `2026-09-01_Session-Log.md`. **`Global_Agent_Memory.md`** — 2026-08-30 entry.
- **Claude memory:** `memory/project_glass_frog_video_0003.md` (+ MEMORY.md line).

---

## Git

Branch **`glass-frog-0003-revision-round1`**, **nothing committed.** The working
tree also contains a lot of UNRELATED pre-existing dirty files from prior sessions
(DAIPBR-Storytelling, GPT-Image-2-Prompting-Guide, Neon_Parcel*, Reimagined_Realms,
Skill-Index, Tool-Manager, Video-Analyzer, Root.tsx, .obsidian, 000_Wiki, …) — do
NOT sweep those into a commit.

**This session's files to commit (when Tony asks):**
- `002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-components/GlassFrogDoc.tsx` (new)
- `.../video-components/DiagramLabels.tsx`, `.../SceneOverlay.tsx`
- `.../003_Remotion/src/skills/design-rules-learned.md`
- `001_Architecture/Skills/{Anomalous_Wild_Video_Pipeline,Diagram-Generation,Production-Asset-Planner,Seedance-Prompting-Guide}/SKILL.md`
- `001_Architecture/Skills/Diagram-Generation/Reference_Examples/` (new)
- `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/{clip_durations.py,test_clip_durations.py,test_pipeline_supervisor_durations.py,pipeline_supervisor.py}`
- `001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/{assemble.py,test_assemble_narration.py}` (Block C — edge-faded narration concat)
- `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/{audio_pop_scan.py,test_audio_pop_scan.py}` (Block C — pre-review splice-pop gate)
- `001_Architecture/Skills/{Production-Research-Agent,Production-Asset-Planner,Diagram-Generation}/SKILL.md` (Notes 9/10 — map/geography process rules)
- `Productions/0003_Glass_Frog_Transparency/Images/scene_04_range_map/` (basemap.png + SOURCE.md — new asset, safe to commit, it's a PNG derived from PD data + a .md)
- `001_Architecture/Feedback_Loop/2026-08-3*.md`, `2026-09-01_Feedback.md`; `001_Architecture/Logs/2026-08-3*.md`, `2026-09-01_Session-Log.md`
- `001_Architecture/Memory/Global_Agent_Memory.md`
- The `0003_Glass_Frog_Transparency/` production folder is untracked and contains
  `.mp4` output — **only commit code/scripts/`.md`, never the `.mp4`s** (they're
  gitignored / must stay local per standing rule).

---

## Historical (earlier this arc — all resolved)

Original edit-review started as a single flash-cut at scene_02's 02A→02B
transition (Remotion `OffthreadVideo` loops to frame 0 past real footage). That
plus the 12-clip systemic duration mismatch, the black frames, and the white
flash are ALL fixed. See `Revision_Notes_Round1.md` "Historical" + the
2026-08-30/31 session logs for the detail.
