# 0003 Glass Frog — Revision Notes, Round 1 (edit review)

Tony's notes while watching `GlassFrogDoc` in Remotion Studio. **Do NOT execute any
of these until Tony explicitly says to.** When he does, do them all in one pass with
full context from this file — do not work from memory. Cross-reference
`Timeline_Cut_Map.md` in this folder for exact frames.

Status key: ⬜ not started · 🔧 in progress · ✅ done

---

## Note 1 — Crossfade on every cut (not just scene_02)

⬜ **Replace every hard cut with a ~0.5s crossfade.** Tony prefers the look of the
scene_02 crossfade and wants it everywhere — between scenes AND between internal
shots (diagram-to-diagram image changes, b-roll clip changes in scenes 04/06,
infographic changes).

Scope / affected points (from Timeline_Cut_Map.md):
- All 6 scene boundaries (01→02→03→04→05→06→07).
- Scene 03 image cuts: frames 1013, 1303, 1544.
- Scene 04 cuts: 2231, 2413, 2595, 2777, 2989.
- Scene 05 image cuts: 3314, 3917, 4283, 4478, 4876.
- Scene 06 cuts: 5513, 5702, 5844, 6026, 6268, 6510, 6692.
- "Same image, camera continues" points (692, 754, 834, 1806, 1984, 3695, 4019,
  4705) are NOT cuts — no crossfade needed there, the camera move already carries them.

Implementation considerations (for when we build it):
- ~0.5s crossfade eats into runtime at each end; every scene is locked to its
  narration audio length, so crossfades must overlap *within* the existing
  timeline (outgoing shot's tail dissolving as incoming shot's head fades in over
  it) — never add duration. Cross-dissolves at scene boundaries mean the two
  scenes' Sequences overlap by ~15 frames; the narration audio tracks must NOT
  crossfade (keep hard audio joins or a very short 2–3 frame audio fade to avoid
  clicks — confirm against the locked audio-mix rules).
- The diagram scenes already hold the last frame between segments
  (renderDiagramChain); a crossfade there = the outgoing DiagramSeg's last ~15
  frames dissolve into the incoming one.
- Consider a single reusable `<CrossfadeCut>` / transition wrapper rather than
  hand-wiring each one. Evaluate `@remotion/transitions` `<TransitionSeries>` vs.
  extending the existing opacity-interpolate pattern.
- Verify no black/white frame is introduced at any overlap (re-run the
  blackdetect + negate-blackdetect scans after).

---

## Note 2 — "Heart" label (and all DiagramLabels) far too small / low-contrast

⬜ Around **frame 619** (scene_03, ~2.4s in, first organ-cutaway segment) the
"Heart" callout — blue dot + leader line + "Heart" text — is **barely noticeable**.

Reference screenshot: provided by Tony in-conversation 2026-08-31 (full frog
anatomy illustration; "Heart" label sits ~57% x / 34% y as thin small white text
with a faint thin line and tiny dot on the heart). If a copy is needed on disk,
Tony to drop it in this folder.

Required changes to the label treatment (`DiagramLabels.tsx`):
- **Text:** larger font, **bold**, add a subtle **black outline / stroke** (or a
  dark text-shadow halo) so it reads on any background.
- **Dot:** larger, higher contrast (brighter / more saturated, maybe a thin white
  ring around it).
- **Leader line:** thicker, higher contrast.
- **Overall:** scale the whole label element up **at least 1.5×** its current size.
- This is a global fix — applies to every label in scenes 03, 05, 06B (heart,
  liver, lungs, intestines, mirrored_pouch, guanine_crystal_surface,
  red_blood_cells*, vessel_wall, clot_formation, platelets, normal_blood_flow).
- Tony re-confirmed explicitly: same treatment for **lungs + liver** (~frame 742)
  and **intestines** (shortly after) — i.e. it is genuinely every label, not just
  the heart.
- Check the label-position coordinates still point at the right feature after
  scaling, and that larger labels don't overlap each other or cover image content
  (existing rule: composited labels must never overlap image content — but these
  are functional callouts *on* the diagram, so "near the feature, leader line to
  it" is correct; just avoid label-on-label collisions).

---

## Note 3 — Scene 03 opening frog diagram (~frames 548–1007) jumps / not fluid

⬜ The organ-cutaway frog diagram at the start of scene 03 is currently **4
separate `DiagramSeg` entries, all on the SAME image** (`ORGAN_CUTAWAY`), each
with its own camera move (fromS 0 / 4.79 / 6.88 / 9.52). Tony's observation:

- It opens with a nice slow zoom-in (good).
- Then it **hard-cuts** to the next segment. Even though it's the same image, the
  crop/position isn't identical across the cut, so **the whole frog appears to
  jump**. Then the camera goes left, right, up, down through the segments — "it's
  not fluid."
- The next same-image segment does the same: appears to re-center on cut, so the
  frog "moves."

**Fix:** collapse every run of **consecutive same-image `DiagramSeg`s into ONE
segment** with a single continuous keyframe path (one slow, fluid move through all
the framing the separate segments were doing). No internal cuts at all within a
same-image run.

Where this applies (from the current source):
- **Scene 03:** segs at fromS 0, 4.79, 6.88, 9.52 → all `ORGAN_CUTAWAY` → merge
  into one seg spanning 0→15.49 with the keyframe `t` values made cumulative.
  Also segs at 33.2, 41.94, 47.86 → all `MIRRORED_POUCH_03` → merge into one
  33.2→scene-end.
- **Scene 05:** 5.77 + 18.45 (`BLOOD_CELL`) → merge. 25.87 + 29.25
  (`MIRRORED_POUCH_CAM`) → merge. 44.56 + 52.15 (`VESSEL_CROSS`) → merge.
- Genuine image *changes* (organ cutaway → species montage, etc.) stay as
  separate segments and get the **Note 1 crossfade**.

Implementation notes for the batch:
- When merging, offset each sub-segment's keyframe `t` by that sub-segment's
  original `fromS` (relative to the merged seg's start) so the timing still
  matches the narration.
- `labelOffsetsS` / label start times are currently per-segment-relative — shift
  them onto the merged timeline too.
- **Important:** the `renderDiagramChain` "gentle continuation keyframe" I added
  on 2026-08-30 (appends a drift keyframe when a seg is held past its last
  keyframe) is **actively causing pops** here — it drifts seg N's camera to
  scale×1.035 / fx+2.5 / fy+1.2, then seg N+1's first keyframe snaps back to its
  own start value. Once same-image runs are merged this mostly goes away, but the
  continuation-keyframe logic should be reworked so it ONLY applies to a
  genuinely final held segment (e.g. the near-silence hold beat), never between
  segments that are meant to chain.
- After merging, the camera path should be ONE continuous interpolation from
  scene-in to the next real image cut — verify by scrubbing that nothing jumps.

Note 1 (crossfades) and Note 3 are complementary: Note 3 removes the *fake* cuts
(same image), Note 1 crossfades the *real* ones (image changes).

---

## Note 4 — Camera must HOLD STILL while a label is on screen (diagram scenes)

⬜ **The bug:** the `DiagramLabels` callouts (heart, lungs, liver, intestines…) are
positioned in a static coordinate space, but `DiagramCamera` is panning/zooming the
image behind them. So when a label pops up, the image keeps sliding and the leader
line stops pointing at the feature — the label and the thing it labels drift apart.

**Tony's required behaviour (not just "make labels track the image" — do this
instead):**

Per feature beat, the motion sequence is:
1. Camera **slowly eases** toward the feature's framing (ease-in AND ease-out —
   nothing abrupt).
2. Camera comes to a **full stop** and settles.
3. Label(s) fade in. **The image is completely still** for the entire time the
   label is up.
4. Label(s) fade out.
5. Camera **slowly eases** toward the next feature's framing.
6. Repeat: settle → label in → hold → label out → move.

- All camera moves are slow, ease-in/ease-out. No abrupt motion anywhere in the
  frog diagram — it doesn't need constant motion.
- Between labelled beats the camera may drift slowly; while a label is visible it
  must not move at all (or only an imperceptible <0.5% settle).
- Implementation: this is keyframe design in the merged same-image segment (Note
  3) — insert pairs of identical keyframes (a "dwell") spanning each label's
  visible window, with eased interpolation between dwells. The label's visible
  window comes from `labelOffsetsS` + `labelStaggerS` + fade durations; the dwell
  keyframes must bracket that window.
- After building: scrub each label beat and confirm the leader line stays locked
  on the feature the whole time the label is up.

### Also — make this a standing rule for future diagram builds

Tony asked that this be captured as a forward rule, not just a one-off fix. As part
of the batch:
- Add to the diagram-building skill (`001_Architecture/Skills/Diagram-Generation/`
  and/or the AW pipeline's `Diagram_Blocking_Plans.md` spec + Phase 7 diagram
  static-hold section): **"camera holds completely still whenever a label/callout
  is on screen; all camera moves are slow ease-in/ease-out; the blocking pattern is
  move → settle → label in → hold → label out → move. Labels are never composited
  over a moving image."**
- Also captured in `001_Architecture/Feedback_Loop/2026-08-31_Feedback.md`.

---

## Note 5 — Scene 03 mirrored-pouch section (frames ~1544–2069): same non-fluid split

⬜ Same problem as Note 3, second instance. Frames 1544–2069 take ONE image
(`MIRRORED_POUCH_03`) and split it into 3 `DiagramSeg`s (fromS 33.2 / 41.94 /
47.86) with hard cuts between them and zoom-in/zoom-out that doesn't line up — the
second clip is a slightly different crop so it reads as the image jumping.
**Merge these 3 into one continuous eased camera move** (already listed under Note
3; this note confirms the visible symptom).

---

## Note 6 — "Mirrored Pouch" + "Guanine Crystal Surface" labels: barely visible + collide

⬜ In the mirrored-pouch segment the two `DiagramLabels` callouts are:
- barely visible (covered by Note 2's global size/contrast fix), AND
- **too close together** — "Guanine Crystal Surface" and "Mirrored Pouch" text
  stack almost on top of each other.

Fix (in addition to Note 2's sizing):
- Enforce a minimum vertical gap between stacked labels; if two labels' anchor
  points are close, offset the label boxes (not the leader-line targets) so the
  text blocks don't overlap.
- Reference screenshot from Tony: 2026-08-31, the crystal-pouch frame — the two
  white labels near the dark pouch on the right are illegibly small and cramped.

---

## Note 7 — Green animated callout ("MIRRORED ORGAN POUCHES") low-contrast on blue

⬜ The big animated green callout (the `SceneOverlay` `type: "callout"` —
`OV.scene_03` "Mirrored organ pouches", green brand text, position bottom) is
**hard to read** against the blue crystal image — green-on-blue blends.

Fix: give the animated callout a **backing plate** while it's on screen. Exact spec
(Tony, refined in Note 16) — build this as a **reusable template / block**, applied
to EVERY instance of this green-callout animation, not hand-placed per scene:
- **Colour:** 50% black — `rgba(0, 0, 0, 0.5)` (not pure black).
- **Sizing:** just slightly larger than the text — a little padding around it
  (roughly text bounds + a small even margin). It tracks the text size, whatever
  that ends up being after the Note 2 sizing pass.
- **Animation:** eases IN in sync with the green letters easing in; eases OUT with
  them. Same timing curve as the text.
- Shape: rectangle or lightly-rounded; keep it simple.
- Keep the green text (brand colour) — the plate is what makes it read on any
  background.
- Lives wherever the callout component lives (`SceneOverlay.tsx` `callout` type);
  the *guideline* goes in the diagram/design skill (see P5 / Note 16).
- Reference screenshots from Tony: 2026-08-31 — "MIRRORED ORGAN POUCHES" (green on
  blue, unreadable) and "90% ... red blood cells hidden" (green callout that reads
  OK but still needs the plate for consistency).

---

## Note 8 — Label / callout AESTHETIC target (reference image from Tony)

⬜ Tony generated a reference in **GPT Image 2** showing the label look he wants —
the "RED BLOOD CELLS (awake)" vessel diagram. **This is the vibe / inspiration for
all future diagram labels and callouts** (not a pixel-exact spec). Provided
2026-08-31, in-conversation.

What the reference establishes (describe here so it survives without the file):
- Main term: large, clean sans-serif, **white**, near-title weight ("RED BLOOD
  CELLS").
- Qualifier in parentheses directly under it in an **accent colour** ("(awake)"
  in red) — accent picked from the subject, not the brand.
- **Thin white leader line** with a single right-angle bend, terminating in a
  small **dot** at the label end.
- A **glowing halo dot / target ring** at the feature end of the line (soft bloom,
  not a hard dot).
- Optional short **description sentence** below the term, smaller white text, 2–3
  lines max ("Oxygen-carrying cells essential for energy and vital functions.").
- Very high contrast, reads cleanly over a dark background with no plate needed —
  achieved through size + weight + the subtle glow, not a box.
- Overall: restrained, editorial, "science documentary" — not gamer-HUD, not
  neon.

**Actions (batch):**
1. Save Tony's two reference screenshots (the crystal-pouch legibility example and
   the RED BLOOD CELLS aesthetic example) into a diagram-reference location —
   **needs Tony to confirm the folder and drop the files** (agent can't persist
   an inbound image). Proposed: `001_Architecture/Skills/Diagram-Generation/
   reference_examples/` (needs create-folder approval).
2. Rewrite `DiagramLabels.tsx` toward this aesthetic (ties into Note 2 + Note 6).
3. Lock the guidelines into:
   - `001_Architecture/Skills/Diagram-Generation/SKILL.md`
   - `002_Content-Creation/Video_Editor/003_Remotion/src/skills/design-rules-learned.md`
   - `001_Architecture/Feedback_Loop/2026-08-31_Feedback.md` (done)
   with a pointer to the reference image(s).

---

## Note 9 — Scene 04 range map needs a real MAP underneath the line (~frame 2107)

⬜ Narrator: "from southern Mexico ... to the Amazon basin." On screen: just a
green zigzag line + the bottom caption "SOUTHERN MEXICO → CENTRAL AMERICA → ANDES
→ AMAZON BASIN" on near-black. **There should be an actual regional map behind the
line** so it reads as a range, not an abstract squiggle.

Fix for THIS video:
- Get / generate a map asset of the region (S. Mexico → Central America → Andes →
  Amazon basin), styled to the channel (dark, desaturated, subtle). Place it as
  the background layer in `RangeMapAnimation`; keep the animated glowing path and
  the pulsing end dot drawing on over it; keep or restyle the caption.
- Source options: research-tool download (preferred), or GPT Image 2 / a map
  service styled to match.

### Process rule to lock in (Tony: "common sense ... learn from this")

A geography / real-place / route / range beat MUST have a real map asset, and that
asset should be **sourced during research** (`Production-Research-Agent`) and
passed to the motion-graphics / diagram build — not left for the assembly step to
fake with a synthetic shape. Add to:
- `001_Architecture/Skills/Production-Research-Agent/SKILL.md` — when the script
  references a location, region, route, migration, or range, download/generate a
  suitable map asset as part of research output.
- `001_Architecture/Skills/Production-Asset-Planner/SKILL.md` — a geography beat is
  flagged as needing a map asset; if research didn't produce one, that's a gap to
  fill before assembly, not something to stylize around.
- `001_Architecture/Skills/Diagram-Generation/SKILL.md` — a "map / geography"
  diagram type: real map base layer + animated path overlay, never path-only.
- `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md` Phase 5/6 —
  reference the above.

---

## Folder for reference images — APPROVED

Tony approved creating `001_Architecture/Skills/Diagram-Generation/Reference_Examples/`
(naming: `Reference_Examples`, capital R + E). Created with a `README.md` listing
the expected files. Tony will drag-and-drop:
- `Label_Aesthetic_Red_Blood_Cells.png` (the GPT-Image-2 target look — Note 8)
- `Label_Legibility_Problem_Crystal_Pouch.png` (anti-example — Note 6)
- `Callout_Contrast_Problem_Green_On_Blue.png` (anti-example — Note 7)
- `Range_Map_Missing_Background.png` (anti-example — Note 9)

---

## Note 10 — Range-map animated line must trace the real map geography

⬜ Extension of Note 9. The current green path was drawn before any map existed,
so it's an arbitrary zigzag. When the real regional map goes in behind it, the
**animated glowing path must follow the actual geography** on that map — trace
S. Mexico → down through Central America → along the Andes → into the Amazon basin,
landing the pulsing end dot on the Amazon. Not a random line over a map.

---

## Note 11 — Scene 04 clip 04D anatomy anomaly (~frame 2713) — re-run

⬜ Around frame 2713 (this is **clip `Scene_04D_looped.mp4`**, scene 04, ~2595–2777)
there's an anatomy glitch: as the heart is revealed, the frog's **leg detaches from
its foot** / dislocates. Needs a re-run.

Diagnosis path:
- **CONFIRMED by Tony scrubbing Studio: the clip is `Scene_04D_looped.mp4`**
  (rendered via `VideoClip` / `GlassFrogDoc.tsx:73`). Note: `Clip_Plan.json`'s 04D
  description ("Frog motionless on leaf underside...") does not match what's on
  screen — the generated clips drifted from the plan on the autonomous run.
- **Gap being fixed (see "Pipeline improvements" section):** `Clip_Plan.json` does
  not record model / storyboard / start-end frame paths per clip.
- If the offending clip was made on **Seedance 1.5 Pro** (start + end frame only,
  no multi-reference), a single 1.5 Pro call over a beat with this much
  limb + organ-reveal motion is exactly the case the skill warns physics will break.

Fix (the technique IS in `Seedance-Prompting-Guide` → "Chaining multiple
generations into one continuous scene" — Tony confirmed it should already be known):
1. Split the beat into **clip A + clip B**.
2. Generate clip A with its own start/end frames (start/end must be *visually
   distinct* per the locked rule — wide vs close, different pose).
3. Extract clip A's **literal last frame**; feed it as clip B's **start image**
   (last-frame-passing, Technique 1). Give clip B its own end frame.
4. Weave anatomy constraints **inline** in both prompts, anchored to the frog's own
   body — e.g. "each hind leg stays fully attached to its foot; anatomically
   correct amphibian limbs; no warping, no detaching, no extra digits" — in
   addition to the closing negative line.
5. If the storyboard for this shot is thin, regenerate a better one first
   (Storyboard-Generation) so the start/end frames are well-composed.

Also add/confirm a **standing rule**: any beat with significant limb motion +
an internal-anatomy reveal on Seedance 1.5 Pro is split-and-chained by default,
not attempted as one call. Check whether `Seedance-Prompting-Guide` /
`Production-Asset-Planner` Step 6 already say this explicitly; if not, add it.

---

## Note 12 — Audio pop in the scene 04 VO between "by day" and "they sleep" (~frame 2776)

⬜ Noticeable **pop in the narration** right between the VO lines
"...by day **[POP]** they sleep." Around frame 2776–2777 absolute ≈ 23.4s into
`Narration_Audio/scene_04.mp3` (scene_04 starts at frame 2075 / 1:09.17).

This is in the VO audio itself, not a video-cut artifact (though it lands almost
exactly on the 04D→04E boundary at frame 2777 — coincidental).

Likely cause: a **hard-cut silence/pause trim** in the VO. Known rule
(`feedback_vo_pause_trimming`, `trim_vo_pauses.py`): never hard-cut a pause gap —
pad 120ms + 15ms fade. Either the trim step hard-cut this gap, or the raw
ElevenLabs generation has the artifact.

Fix:
1. Inspect `scene_04.mp3` around 23.4s (raw PCM + numpy, per
   `feedback_audio_verification_method` — not astats/grep).
2. If it's a hard-cut pause: re-run `trim_vo_pauses.py` on it (pad + fade), or
   splice a 120ms padded crossfade at that join.
3. If the pop is in the raw TTS: regenerate that sentence via ElevenLabs and
   re-stitch.
4. After fix: re-verify with the numpy RMS method + listen; then the Phase 8
   audio mix needs re-running for scene_04 (or the whole video, TBD at execution).

---

## PIPELINE IMPROVEMENTS (not video edits — do in the same batch, or right after)

These are process/tooling fixes so the classes of problem above don't recur.

### P1 — `Clip_Plan.json` records full per-clip provenance  *(Tony asked, confirmed)*
Add as **required** fields on every `"generated": true` clip, written by the
generation step (`pipeline_supervisor.py` / manifest builder):
- `model` (exact model slug used)
- `storyboard` (path to the storyboard image used, if any)
- `first_frame` / `last_frame` (paths to the start/end frame images used)
- `real_generated_s` (ffprobe of the raw clip) — partly already added via
  `clip_manifest.json`; mirror it here
- `chained_from` (if this clip's start frame came from another clip's last frame)
SKILL rule: a clip is not "done" until its provenance row is complete. Lock into
`Anomalous_Wild_Video_Pipeline` Phase 6 + `Production-Asset-Planner` Step 6.

### P2 — Seedance 1.5 anatomy-reveal beats are split-and-chained by default
Any beat with significant limb/body motion + an internal-anatomy reveal, routed to
Seedance 1.5 Pro, is split into ≥2 chained clips (last-frame-passing) by default —
not attempted as one call. Confirm/extend `Seedance-Prompting-Guide` +
`Production-Asset-Planner` Step 6.

### P3 — geography beats require a real map asset from research
(see Note 9) — Production-Research-Agent, Production-Asset-Planner,
Diagram-Generation, AW pipeline.

### P4 — diagram camera holds still under labels; move→settle→label→hold→label→move
(see Note 4) — Diagram-Generation SKILL, `Diagram_Blocking_Plans.md` spec,
`design-rules-learned.md`.

### P5 — label/callout aesthetic locked to the reference image
(see Note 8) — Diagram-Generation SKILL, `design-rules-learned.md`,
`Reference_Examples/`.

### P6 — VO pause-trim hard-cuts (see Note 12) — verify `trim_vo_pauses.py` is
actually invoked in the AW pipeline audio phase and its pad+fade is applied to
every VO segment, not just some.

---

## Note 13 — Scene 04D visual doesn't match the narration (regenerate to match)

⬜ The VO over 04D's slot is about the frog being **motionless, then snapping up an
insect with a flick of the tongue**. The generated clip instead shows the **heart
inside the frog** — wrong beat entirely (the internal-anatomy/transparency material
belongs to scenes 03/05, not here).

Since 04D is already being regenerated for the anatomy glitch (Note 11), regenerate
it to **match the storyline**:
- Beat content: frog still/motionless on the leaf → alert posture → **tongue-flick
  strike → insect caught**.
- Pull the exact VO wording for this beat from `Data/Beatmap.json` /
  `Narration_Audio` transcript so the on-screen action lines up with the words.
- This is really two actions (hold, then strike) → good candidate for the
  split-and-chain from Note 11: clip A = motionless/alert hold, clip B (start frame
  = A's last frame) = tongue-flick + catch.
- Cross-check `Clip_Plan.json`: 04C was *also* speced as "tongue-flick strike ->
  insect caught (B-roll rejected)". Make sure 04C and 04D aren't now both trying to
  show the strike — decide which clip owns which half of the action and align both
  to their VO.

### Pipeline note (add to P-list)

**P7 — every generated clip is validated against its beat's VO before acceptance.**
The rule already exists (CLAUDE.md: "Every creature visual must match narrator's
description exactly"; Video-Analyzer continuity check) but was not enforced on the
autonomous run — 04D shipped showing the wrong beat. Make this a hard gate in
`Anomalous_Wild_Video_Pipeline` Phase 6: after a clip generates, confirm its
content matches the beat's narration text; mismatch = regenerate, don't accept.

---

## Note 14 — Second audio pop, scene 04, between 04E and 04F (~frame 2988→2989)

⬜ Another VO pop, at the 04E→04F boundary. Frame 2988 abs ≈ 30.4s into
`scene_04.mp3`.

**Both scene-04 pops (Note 12 and this one) land exactly on video clip
boundaries** (2776/2777 and 2988/2989). That's either coincidence (VO splice
points happen to align with cuts) OR a sign the pop is introduced at
**assembly/mix time** — e.g. a per-beat SFX stem boundary, or how the scene audio
is concatenated. During execution:
1. Check whether the pops are in `Narration_Audio/scene_04.mp3` itself (raw PCM +
   numpy) or only appear in the mixed output.
2. If only in the mix: look at `Audio_Stems/` for scene 04 and how `mix_stems.py` /
   `compose_audio.py` joins beat stems — a stem starting/ending without a fade at a
   beat boundary will pop.
3. If in the raw VO: same fix as Note 12 (pad + fade the pause trim, or regenerate).

---

## Note 15 — Scene 05 blood-cell labels too small (again) — same fix

⬜ "Red Blood Cells" (and later "Red Blood Cells (asleep)") labels in scene 05 are
too small / low-contrast — **same problem, same fix as Note 2**. Tony: make ALL
labels consistent with the reference-image aesthetic
(`Reference_Examples/Label_Aesthetic_Red_Blood_Cells.png`). The label rework in
Note 2 is global and covers every label in scenes 03, 05, 06B — this note just
confirms the scene-05 instances (`red_blood_cells_awake`, `red_blood_cells_asleep`,
`liver`, `mirrored_surface`, `red_blood_cells`, `vessel_wall`).

---

## Note 16 — Green callout backing plate = reusable template  (spec folded into Note 7)

⬜ The green callout at ~frame 3744 ("90% of its red blood cells hidden") reads OK
on this red image, but for consistency it gets the same backing plate as Note 7.
Full spec is now in **Note 7** (50% black `rgba(0,0,0,0.5)`, small even padding,
eases in/out synced with the text).

Key instruction: **make it a reusable block/template**, applied automatically to
every instance of this green-callout animation — never hand-placed per scene.
- Component: `SceneOverlay.tsx` `callout` type gets the plate built in.
- Guideline home: the diagram/design skill (P5) — if it's channel-specific styling,
  the AW channel bible; if it's general, `design-rules-learned.md`. Put it wherever
  a future build will actually look. (Decide at execution; default to
  `design-rules-learned.md` + `Diagram-Generation/SKILL.md` since callouts recur
  across channels.)

---

## Note 17 — EXHAUSTIVE label + green-callout pass (Tony will not call out each one)

⬜ Tony's blanket instruction: he is **not** going to flag every small/illegible
text overlay individually (e.g. the "Liver" label at scene 5 frame 4009 — same
problem). **Go through the ENTIRE video** and apply the label/callout treatment
from Notes 2, 6, 7, 8:

- **Every `DiagramLabels` label** in every scene (03, 05, 06B): rebuild to the
  reference aesthetic (`Reference_Examples/Label_Aesthetic_Red_Blood_Cells.png`) —
  larger, bold white sans-serif, subject-accent qualifier, black outline/glow,
  thicker higher-contrast leader line, larger glowing target dot, ≥1.5× current
  size, minimum-gap spacing so stacked labels never collide.
- **Every green animated bottom callout** (`SceneOverlay` `callout` type) in every
  scene: reusable 50%-black backing plate that eases in/out with the text (Note 7
  spec).

Full list of label instances to check (from source):
- scene 03: heart, liver, lungs, intestines, mirrored_pouch, guanine_crystal_surface
- scene 05: red_blood_cells_awake, red_blood_cells_asleep, liver, mirrored_surface,
  red_blood_cells, vessel_wall
- scene 06B: clot_formation, platelets, normal_blood_flow

Callout instances: scene 03 ("Mirrored organ pouches"), scene 05 ("90% of red blood
cells hidden", "2–3x more transparent"), scene 06 ("Studied for human blood-clot
research").

Do a full playback + frame scan after the rework to confirm every one is legible.

---

## Note 18 — Scene 5 liver/mirrored-pouch section: same-image jump (merge to one fluid move)

⬜ Same root cause and fix as Notes 3 & 5, now confirmed for scene 5.

The liver material reuses ONE image (`MIRRORED_POUCH_CAM`) across multiple
`DiagramSeg`s (fromS 25.87 with the "Liver" label, then 29.25). Each seg mounts its
own image copy and its own camera move starting from its own first keyframe — so on
the hard cut between them the picture snaps from "where move 1 ended" to "where move
2 begins" (usually back toward the default centered framing). Because it's the same
picture, it reads as the **liver jumping/teleporting**, not as a new shot. Not
fluid.

Fix: **merge the whole same-image run into one segment** — one image element
mounted once, one continuous eased camera path (keyframes: ease to the liver, hold
still while "Liver" is up, ease to the next area, hold while its labels are up, ease
out) with zero discontinuity. Cut only when the image actually changes
(→ side-by-side, → vessel cross-section), and crossfade those (Note 1).

(Already in Note 3's merge list: scene 05 `MIRRORED_POUCH_CAM` segs 25.87 + 29.25 →
merge. This note is the visible symptom + Tony's confirmation.)

---

## Note 19 — "REMOUNT JUMP" tag + fix ALL of them from source (no more watching)

⬜ **Tag defined:** **"remount jump"** — a hard cut between shots that are the same
still image, where each shot is a separate Remotion `<Sequence>` that remounts its
own image copy and resets the camera to its own first keyframe, so the picture
appears to jump/teleport instead of reading as a new shot. Fix: merge the whole
same-image run into ONE `<Sequence>` with one continuous eased camera path; cut
(with crossfade) only when the image genuinely changes.

Use "remount jump" in all future notes + skill docs.

**Tony's instruction (2026-08-31, late — stopping the watch here):** don't make him
re-watch and re-explain. Fix ALL remount jumps by reading the source. They're
fully source-detectable: runs of consecutive `DiagramSeg` sharing the same `src`.

**Complete inventory (this is all of them in GlassFrogDoc.tsx):**
| Scene | Same-image run | Merge target |
|---|---|---|
| 03 | `ORGAN_CUTAWAY` ×4 — S03_SEGS fromS 0, 4.79, 6.88, 9.52 | one seg 0→15.49 |
| 03 | `MIRRORED_POUCH_03` ×3 — fromS 33.2, 41.94, 47.86 | one seg 33.2→scene end |
| 05 | `BLOOD_CELL` ×2 — S05_SEGS fromS 5.77, 18.45 | one seg |
| 05 | `MIRRORED_POUCH_CAM` ×2 — fromS 25.87, 29.25 | one seg |
| 05 | `VESSEL_CROSS` ×2 — fromS 44.56, 52.15  (Tony's frame 4872) | one seg |
| 06 | none — 06B (`CIRCULATORY_INFOGRAPHIC`) and 06C (`LAB_INSERT_06C`) differ | — |

When merging: make each sub-seg's keyframe `t` values cumulative from the merged
seg start; carry label offsets onto the merged timeline; insert dwell keyframe
pairs so the camera holds still whenever a label is up (Note 4).

---

## What still needs Tony's eyes LATER (after the batch build, in a review pass)

Source-detectable → agent fixes now, no re-watch needed:
- All remount jumps (Note 19 / 3 / 5 / 18)
- All label sizing/contrast/spacing (Notes 2, 6, 15, 17)
- All green-callout backing plates (Notes 7, 16, 17)
- Crossfades replacing hard cuts (Note 1)
- Camera-holds-still-under-labels blocking (Note 4)
- Black/white frame scans (already clean; re-verify after)

Needs Tony's judgement AFTER the build (new review pass):
- Ken Burns / camera-move *amount* and pacing — does it feel right
- Any regenerated clips (04D anatomy + storyline, Note 11/13) — do they look good
- The new scene-04 map (Note 9/10) — styling + the traced path
- Whether the crossfades feel right at each point
- Audio pops fixed (Notes 12, 14) — listen
- Overall pacing once cuts are dissolves

---

## Note 20 — Scene 06A has an internal Seedance jump-cut (~3s in) — regenerate as ONE continuous shot

⬜ `Video_Clips/scene_06/Scene_06A.mp4` (6.05s, single file, single generation per
`Clip_Plan.json` — "Wide cinematic, frog on leaf, camera pulling back") contains a
**visible discontinuity ~3.0s in**: frog snaps from small/far/wide (2.9s) to
larger/repositioned-lower-left/slightly-different-pose (3.1s). Confirmed by frame
extraction 2026-09-01. In the Remotion timeline this hits around abs frame
5423–5424 (~3s into scene 06).

Cause: **Seedance internally cut the shot mid-generation** — it treated the
6.3s "camera pulling back" as two separate moves instead of one continuous
pull-back. Not a Remotion remount jump (it's inside the raw video file), not a
deliberate A/B split.

Tony: the beat is just a simple ~6s zoom-out from a frog on a leaf to the Amazon
river — no reason for it to be broken up. **Regenerate 06A as one clean continuous
shot.**

Fix:
- Regenerate with start frame = frog on leaf (cloud-forest), end frame = wide
  Amazon river, ONE continuous pull-back / crane-out.
- Prompt must force a single unbroken take: explicit "one continuous camera
  movement, single unbroken shot, no cut, no scene change, no jump" inline AND in
  the closing negative line.
- Keep it to the real target duration (padded per the clip_durations rule).
- After generation: scan the new clip for internal shot boundaries before
  accepting (see P8).

### P8 — reject clips with internal Seedance cuts

Add to `Anomalous_Wild_Video_Pipeline` Phase 6 QA: after a clip generates, run a
shot-boundary / scene-change detector (ffmpeg `select='gt(scene,0.4)'` or
Video-Analyzer) over it. A clip that was supposed to be one continuous shot but
contains an internal cut = **regenerate** with stronger "single unbroken take"
prompt constraints. Seedance does this on its own, especially on longer
generations and "camera moves from X to Y" prompts — catch it automatically
instead of shipping it.

---

## Note 21 — Scene 06B labels (clot formation / platelets) — same overlay problems

⬜ ~3:07 (abs frame ~5540). Confirmed instance, covered by the exhaustive Note 17
label pass. No separate action — just listed for completeness.

---

## Note 22 — Scene 06 F/G/H ending: three near-identical pull-back shots, deformed frog in 06H

⬜ From ~frame 6348 (06F) through 06G and 06H, the closing sequence is broken:

- **06F** (`Scene_06F_looped.mp4`, local 937–1179): close on a frog on a leaf,
  zooms out, the leaf disappears, then comes BACK to almost the same shot, zooms
  out again. Internal repetition (likely another Seedance internal cut, cf. Note
  20).
- **06G** (local 1179–1361): almost a copy of 06F — same "zoom out from frog on
  leaf." Reads as the same shot a third time.
- **06H** (local 1361–1513): does it AGAIN, and **the frog looks deformed**.

Root problem: `Clip_Plan.json` speced 06F / 06G / 06H all as variations of
"overhead pull-back from the leaf" (and 06G+06H were a split of one over-length
clip). Three consecutive nearly-identical camera moves + composition. The
"frog on a leaf in the foreground, Amazon forest" framing has also been used
heavily earlier in the video — it works there, not here.

Rework 06F, 06G, 06H so they are **visually distinct from each other** — different
angles, compositions, and beats — while still being the Amazon-forest,
frog-disappearing ending. Suggestions (align to the actual VO for these beats):
- One shot: the transparency/vanish effect itself (frog going see-through against
  the leaf, held).
- One shot: a genuinely wide environmental context (canopy, river, scale) — NOT
  another leaf close-up.
- One shot: the final beat the narration lands on.
- Not three overhead pull-backs. Not the same leaf-close-up composition repeated.
- Fix the deformed frog in 06H (anatomy constraints inline; split-and-chain if the
  move is complex — Note 11 technique).
- Check each regenerated clip for internal Seedance cuts before accepting (P8).

Verify at execution: extract frames from `Scene_06F/G/H.mp4` to confirm the
repetition + the 06H deformity before rewriting the prompts.

---

## Note 23 — Third audio pop: scene 06, 06G→06H boundary (frames 6692→6693)

⬜ Another VO pop, at the 06G→06H cut. Frame 6692 abs = ~45.4s into
`scene_06.mp3`.

**This is now THREE pops, ALL exactly on video-clip cut boundaries:**
- 2776/2777 — scene 04, 04D→04E (Note 12)
- 2988/2989 — scene 04, 04E→04F (Note 14)
- 6692/6693 — scene 06, 06G→06H (this note)

That correlation is conclusive: **the pops are introduced at audio-assembly time,
not in the raw VO.** Almost certainly per-beat audio segments (native Seedance
clip audio extracted into stems, and/or beat-sliced narration) being **butt-joined
without a fade** at each clip boundary. 06G/06H especially — they're two halves of
one split clip, each likely carrying its own native audio stem.

Fix (supersedes the "check raw VO" step in Notes 12/14):
1. Look at `compose_audio.py` / `mix_stems.py` / the native-audio-extraction step —
   how beat-boundary audio segments are concatenated.
2. Every beat-boundary audio join gets a short (~15–30ms) equal-power crossfade or
   fade-out/fade-in pair — never a hard concat.
3. Re-mix scene 04 and scene 06 audio (or the whole video) after the fix.
4. Verify with raw-PCM + numpy RMS at each former pop point (per
   `feedback_audio_verification_method`).

Fold into **P6** (was "verify trim_vo_pauses.py") — expand P6 to: **no hard audio
concat anywhere in the pipeline; every audio segment join (VO pause trims, beat
stems, native clip audio, scene boundaries) has a fade.**

---

# ==== REVIEW COMPLETE (Tony, 2026-09-01) — EXECUTION STARTED ====

Tony's watch-through is done. Notes 1–23 + pipeline items P1–P8 above are the full
Round 1 revision set. **Tony said "yes please complete" 2026-09-01 → executing
block A now.**

Reference folder ready: `001_Architecture/Skills/Diagram-Generation/Reference_Examples/`
- `Label_Aesthetic_Red_Blood_Cells.png` — the TARGET label look (Tony's GPT-Image-2
  ref; agent renamed it from "Codex Image Aug 30...png" to the convention).
  Tony confirmed: `DiagramLabels.tsx` should be rebuilt to produce labels that look
  like this, as an animated overlay (leader line draws on, dot glows, text eases in).
- `Anti_Example_Labels_And_Callout_Crystal_Pouch.png` — agent-extracted, frame 1700
- `Anti_Example_Range_Map_No_Background.png` — agent-extracted, frame 2150

## Execution order (proposed, for when Tony says go)

**A. Remotion-only, source-detectable (no re-watch needed, no cost):**  — ✅ DONE 2026-09-01, on branch `glass-frog-0003-revision-round1`
1. ✅ Remount jumps merged — new `DiagramShot` model; same-image runs are ONE shot
   with one eased camera path. `S03_SHOTS` (4 shots) / `S05_SHOTS` (6 shots).
2. ✅ `DiagramCamera` now does per-segment ease-in/out; `buildPath()` expands
   waypoint `holdS` into dwell keyframes so the camera sits still under each label
   (move→settle→label→hold→label→move). Old continuation-keyframe hack removed.
3. ✅ `DiagramLabels.tsx` fully rebuilt to the reference aesthetic — large bold
   white term, accent parenthetical (auto-split from "(...)"), thin white leader
   line that draws on + end dot, glowing target ring, black outline/glow,
   collision avoidance (min vertical gap, text block offset not the target),
   optional description support, `labelHoldS` fade-out. Verified on the "Red Blood
   Cells (Asleep)" frame — matches the reference well.
4. ✅ `SceneOverlay.tsx` `callout` type: 50%-black backing plate
   (`rgba(0,0,0,0.5)`), even padding, fades+scales in/out with the text. Verified
   on "MIRRORED ORGAN POUCHES".
5. ✅ Crossfades: `DiagramScene` cross-dissolves image changes within a scene;
   `SceneVisual` + `SceneFade` cross-dissolve every scene boundary (outgoing
   scene FREEZES its last frame for the 0.5s tail — video clips would loop
   otherwise — while the next fades in on top; true dissolve, no bg bleed, no
   loop). `NarrationTrack` = one hard-cut VO track with 3-frame edge fades at the
   joins (visual crossfades, audio doesn't).
6. ✅ Black scan (strict `pix_th=0.03`): NONE. White scan: NONE. Full render OK.

**Still needs Tony's eyes on block A (subjective, after review):** the Ken Burns /
camera-move *amount* and label dwell timing across scenes 03 & 05; whether the
0.5s crossfade duration feels right; the callout plate size/opacity.

### Tony sign-off 2026-09-01 (block A review)

> "the fade looks great. The fade in, also the [moves] in the diagrams, those are
> excellent. The text overlays and labels are great."

**APPROVED:** label rebuild, callout plate, crossfades, diagram camera moves.

**New standing rule (Tony): 0.5s cross-dissolve is the DEFAULT transition, not
hard cuts — GLOBALLY, across channels.** Lock into:
- `001_Architecture/Skills/Diagram-Generation/SKILL.md`
- `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md` (Phase 7)
- `001_Architecture/Skills/Reimagined_Realms_Video_Pipeline/SKILL.md` + its
  `assemble.py` (the RR editing skill — Tony: "if there's a video editing skill
  for Reimagined Realms then this should be a global thing")
- `002_Content-Creation/Video_Editor/003_Remotion/src/skills/design-rules-learned.md`
Captured in `001_Architecture/Feedback_Loop/2026-09-01_Feedback.md`.

### Note 21 REFINED (scene 06B — platelets / clot formation)

⬜ Frame ~5518: platelets + clot_formation labels appear — **correct**. But at
frame ~5614 the image behind them starts to move and the narration moves on to
another point — the platelets/clot labels **should fade away** as the camera
starts moving, then the next label comes up. i.e. scene 06B needs the SAME
camera-holds-under-labels + `labelHoldS` fade-out treatment applied to scenes
03/05. **06B must migrate from the old `DiagramSeg` to the new `DiagramShot`
model (or at minimum get `labelHoldS` + dwell keyframes).** — doing now.

### Block B — Tony's instruction

> "for the next block if you can create the storyboards for those shots, I would
> love to view them before it goes through the video generation part"

So: **generate storyboards for 04D, 06A, 06F, 06G, 06H (and the scene-04 map
concept) → present to Tony → only then video generation.** Use the
Storyboard-Generation skill. No paid video gen until Tony approves the boards.

**B. Asset regeneration (costs money — confirm each):**
7. Scene 04D — regenerate to match VO (motionless → tongue-flick → insect),
   split-and-chain, anatomy constraints (Notes 11/13).
8. Scene 06A — regenerate as one continuous pull-back, no internal cut (Note 20).
9. Scene 06F/G/H — rework as three visually distinct ending shots, fix 06H
   deformity (Note 22).
10. Scene 04 range map — source/generate a real regional map, retrace the path
    (Notes 9/10).

**C. Audio:**
11. Fix the 3 boundary pops at assembly (Note 23 / P6); re-mix affected scenes.

**D. Pipeline / skills (P1–P8):** fold in alongside or right after.

**E. New review pass** with Tony on everything in "needs Tony's eyes later".

---

## EXECUTION PROGRESS (live)

### 2026-09-01 — block A DONE + approved (see "Tony sign-off" above)
### 2026-09-01 — 06B label fade fixed (Note 21 refined) — verified: clot/platelets fade as camera eases to normal_blood_flow.
### 2026-09-01 — skill rollout of the new defaults:
- `Anomalous_Wild_Video_Pipeline/SKILL.md` Phase 7 — added the 0.5s cross-dissolve
  default rule + the camera-holds-under-labels / label-aesthetic / callout-plate rules.
- `002_Content-Creation/Video_Editor/003_Remotion/src/skills/design-rules-learned.md`
  — Rules 5 (label aesthetic + camera under labels), 5b/5c, 6 (cross-dissolve default).
- `001_Architecture/Skills/Diagram-Generation/SKILL.md` — label/callout aesthetic +
  camera section, points at Reference_Examples/ and design-rules-learned.
- STILL TODO: `Reimagined_Realms_Video_Pipeline/SKILL.md` + `assemble.py` — the
  cross-dissolve default needs applying there too (Tony: "global thing").

### 2026-09-02 — Block B storyboards (present to Tony BEFORE any paid video gen)
Generated via Storyboard-Generation skill (GPT-Image-2, 16:9 4K, 6 frames each,
character sheet as reference). Output:
`Images/Storyboards/RevisionRound1/`. Specs: `Data/storyboard_spec_Scene_*.json`.
- ✅ `Scene_04D_Tongue_Strike_Storyboard.png` — night ambush → tongue-flick → moth
  caught → settle. 6 clean panels, anatomy correct (4 legs, 2 eyes every panel),
  matches the VO. **Looks right.** ($0.08 / 16 credits)
- ⏳ `Scene_06A_PullBack_To_Amazon` — one continuous pull-back, frog on leaf → Amazon.
- ⏳ `Scene_06F_Backlit_Transparency` — side, frog going transparent on a backlit leaf.
- ⏳ `Scene_06G_Grand_Wide` — dawn wide establishing, finds the tiny frog.
- ⏳ `Scene_06H_Final_Upside_Down` — intimate close, upside-down under a leaf, vanishing.
(06F/G/H deliberately three visually distinct concepts per Note 22.)

### 2026-09-02 — Boards APPROVED ("all storyboards look good"). Executing block B video regen.

Model: **Seedance 1.5 Pro** (`bytedance/seedance-1.5-pro`, kie.ai direct createTask,
`input_urls: [start_frame, end_frame]`, `generate_audio: true`) — the AW default.
Path = start-frame + end-frame per shot (1.5 Pro has no multi-ref field; the
storyboard sheet + character sheet feed the FRAME generation, not the Seedance
call).

Old start/end frames backed up to
`Images/Start_End_Frames/Rejected_RevisionRound1/`.

**5 clips being regenerated** (04C stays — only 04D was flagged; 04D = the strike):
| clip | target | start → end frame concept |
|---|---|---|
| `scene_04/Scene_04D_looped.mp4` | 6.07s | still ambush crouch + moth → tongue at full stretch hitting moth |
| `scene_06/Scene_06A_looped.mp4` | 6.30s | close on frog on leaf → aerial wide of the Amazon basin (one unbroken pull-back) |
| `scene_06/Scene_06F_looped.mp4` | 8.07s | frog visible on backlit leaf → frog dissolved into the leaf |
| `scene_06/Scene_06G_looped.mp4` | 6.07s | extreme wide dawn ravine → medium on tiny frog under a leaf (one push-in) |
| `scene_06/Scene_06H_looped.mp4` | 5.07s | frog visible hanging upside-down → frog merged with the leaf, invisible |

Scripts: `scratchpad/gen_frames.py` (frame pairs), `scratchpad/regen_clips.py`
(Seedance via `pipeline_supervisor.generate_seedance` + `clip_durations` pad/trim).
Each Seedance prompt forces a single unbroken take (heavy "no cut" negative) since
06A/06F/06G were internally cut before, and weaves inline frog-anatomy constraints
(04D leg glitch). After download: ffprobe + trim to target; then manual
shot-boundary check before accepting.

**NEXT:** frames → clips → drop the 5 `_looped.mp4` into place (filenames unchanged,
Remotion picks them up) → re-render → Tony watches.

### 2026-09-02 — Block B RESULT + Tony sign-off
All 5 clips regenerated, trimmed, in place. `FULL7_RevisionRound1_blockB.mp4` in
`Renders/`. Black/white scans clean, 0 internal cuts in any clip. Tony (2026-09-02):
**"okay with the edit and the re-run videos."** 06F/06H "vanish" still to be done in
assembly (Seedance can't do transparency) — end-frame crossfade, deferred with the
range map. 06A/06G accepted.

### 2026-09-02 — Block C (Notes 12 / 14 / 23 — VO pops) — RESOLVED
Investigation (raw-PCM + numpy, per `feedback_audio_verification_method`):
- **Raw `Narration_Audio/scene_04.mp3` / `scene_06.mp3` are clean** at all three
  flagged points (23.4s / 30.4s in s04, 45.4s in s06) — single continuous
  ElevenLabs generations, no internal splice, max sample Δ 0.04–0.18 (mid-speech).
  The pops were never in the raw VO.
- **FULL7 (current Remotion render) is clean** end-to-end — no hard click anywhere,
  every `NarrationTrack` scene-boundary hard cut lands in silence (Δ < 0.07). Block
  A's whole-scene-mp3 + 3-frame-edge-fade `NarrationTrack` already eliminated the
  per-beat concat path that caused the pops.
- **The Aug-29 assembly (`Assembly/..._final.mp4`) really did pop** — Δ 0.77 @ 1:58,
  Δ 0.62 @ 3:27 — but in its **SFX/stems** layer, not the VO, and not at the frames
  the notes guessed. That mix is superseded; the stem-free current cut doesn't have it.
- **Root cause of the class of bug:** `Reimagined_Realms/assemble.py`
  `phase_concat_narration` joined the per-scene VO mp3s with `ffmpeg -f concat -c
  copy` — raw bitstream splice, no fade. The AW pipeline calls this for
  `Assembly/narration.mp3`, which `render_outputs.py` consumes for the final
  three-layer mix — so it would have reintroduced pops the moment music+SFX were
  remixed in.

**Fix shipped** (branch `glass-frog-0003-revision-round1`):
- `assemble.py` — new `build_narration_concat_filter()` + `_audio_duration_s()`;
  `phase_concat_narration` now re-encodes with a **20ms fade-out/fade-in pair at
  every scene join** (duration-preserving — not a crossfade). CTA-append step also
  gets a 20ms fade-in on the CTA. Constant `NARRATION_JOIN_FADE_S = 0.02`.
- `test_assemble_narration.py` — 6 unit tests on the filter builder (pass).
- Integration-verified on the real 0003 scene mp3s: output 232.8497s vs expected
  232.85s (< 1ms drift over 7 joins); every join point now max Δ 0.0002–0.069
  (was up to 0.77 on the old hard concat).
- `mix_stems.py` / `compose_audio.py` already fade every stem join — left as-is.
- `Anomalous_Wild_Video_Pipeline/SKILL.md` Phase 8 — added "no hard audio concat
  anywhere" rule (fade-pair not crossfade, the reasoning, where the hole was).

### 2026-09-02 — Notes 9 + 10 (scene-04 range map) — DONE
Replaced the abstract green squiggle-on-black with a real regional map:
- **Asset:** Natural Earth II shaded relief (`NE2_50M_SR_W`, **public domain**, no
  attribution required per Natural Earth terms). Cropped to lon [-112,-38] / lat
  [-13,28.6] (16:9), restyled to the AW palette — navy ocean (blue-channel mask),
  desaturated dark-green relief land, thin coastline, vignette. →
  `Images/scene_04_range_map/basemap.png` + `SOURCE.md` (provenance/license).
- **`RangeMapAnimation` (GlassFrogDoc.tsx) rewritten:** `<Img>` basemap fades in +
  slow push toward the Amazon; the glowing range path (`pathLength={1}` +
  `strokeDashoffset`) is drawn over the real geography — S. Mexico → Pacific-side
  Central America → Panama → Colombian Andes → down the Andes → western Amazon
  basin, ending on a pulsing dot. Restyled lower-left caption ("GLASS FROG RANGE /
  Southern Mexico → the Amazon basin").
- Verified: tsc clean, strict black-frame scan clean, stills eyeballed.
- **Process rules locked** (Note 9's "learn from this"): a location/region/route/
  range beat = real basemap base layer + path tracing real geography, never
  path-only. Added to `Production-Research-Agent` (Step 2b), `Production-Asset-Planner`
  (Step 3b), `Diagram-Generation` (new "map / geography type"), AW SKILL Phase 5B.
- Open (minor, Tony's call): the map leaves screen at 5.2s but the VO says "Amazon
  basin" at ~8s — could extend RangeMap to hold under that line (shifts 04B–04F,
  touches the frame-floor layout). And RangeMap→04B is still a hard cut (Block D's
  cross-dissolve sweep).

**Nothing to re-render for 0003** — current cut's VO is already pop-free; the fix
makes the eventual final music+SFX mix clean and stops the bug channel-wide.
Satisfies **P6** (expanded form). Also completes the `assemble.py` half of the
2026-09-01 "STILL TODO" (cross-dissolve default still pending there separately).


---

# ==== ROUND 2 — Tony feedback on FULL8 (2026-09-03) ====

## R2-1 — Range map polish (follow-up to Notes 9/10) — DONE 2026-09-03
Tony on FULL8: "The map is great." Three tweaks requested + done:
1. **Place labels in Remotion** — added `MEXICO`, `AMAZON BASIN`, and `ANDES`
   (rotated -70° to run along the cordillera) as staggered-in SVG `<text>` inside
   `RangeMapAnimation`'s map svg (they pan with the Ken Burns). White, bold,
   0.16em tracking, black stroke via `paintOrder`.
2. **Andes more visible** — basemap restyled: high-pass hillshade of the relief
   luminance pushed back into the land ramp (`relief*0.55`) + a ridge-crest
   highlight, so the mountain chain reads.
3. **Less desaturation** — land ramp brighter, more chroma (R rises toward tan on
   highlights, `Color` enhance 1.12), less global darkening (Brightness 0.98).
   Ocean stays deep navy. Re-saved `Images/scene_04_range_map/basemap.png`
   (regen script logic in scratchpad; NE2 source still in scratchpad/ne2/).
Verified: tsc clean, stills eyeballed. Still open from Notes 9/10: map exits ~2.5s
before VO says "Amazon basin"; RangeMap→04B still a hard cut (Block D sweep).

## R2-2 — Scene 03 ~1:00 "camouflaging its insides" — cut to a real frog photo (Ken Burns)  ✅ DONE 2026-09-03
**Beat:** scene_03 word timings — "transparent." @ 43.55s, "actively" @ 45.06,
"camouflaging" @ 45.67, "insides." @ 46.81, scene ends 50.90s. Scene_03 starts at
frame 548 → this span is ~frames 1855–2075 (abs). Currently covered by the tail of
the `MIRRORED_POUCH_03` diagram shot (pull-back + near-silence hold).

**Tony wants:** for variety, cut away from the animated diagram here to **a single
beautiful real-looking glass-frog photo** with a **very subtle Ken Burns** push in
Remotion. Generate the photo with **GPT-Image-2**, styled after the reference he
likes: `Research/Reference_Images/Glass_Frog_Euknemos_Species_19.jpg` (a
yellow-flecked *Sachatamia*-type glass frog, in profile, on a wet grey rock,
macro, shallow DOF, warm neutral bg, side/rim light).

Tony's constraints:
- Frog **on something** — rock is fine, does NOT have to be a leaf.
- Scenery does NOT have to be the Amazon — **another country is good for variety**
  (as long as that species really occurs there). Sachatamia albomaculata range =
  Costa Rica / Panama / Colombia / Ecuador cloud forest → a Costa Rican or
  Ecuadorian cloud-forest stream setting is honest and visually distinct from the
  dark-leaf shots elsewhere in the video.
- Compose with **negative space** so the Ken Burns move has somewhere to travel.
- **SHOW TONY THE IMAGE PROMPT BEFORE GENERATING** (his explicit instruction).

**Proposed GPT-Image-2 prompt (16:9) — awaiting Tony's OK:**
> A single small glass frog (Sachatamia albomaculata, the yellow-flecked glass
> frog) perched in profile on a smooth, wet, moss-edged granite river stone.
> Translucent pale mint-green skin scattered with tiny golden-yellow flecks;
> delicate semi-transparent limbs where pale bone and a faint blush of internal
> organs show through near the belly; one large domed eye with a fine silver-grey
> reticulated iris and a horizontal pupil. Body ~2 cm, realistic proportions —
> four legs, two eyes, long padded toes gripping the wet stone. Setting: night at
> the margin of a Costa Rican cloud-forest stream (not the Amazon); behind the
> frog a softly blurred backdrop of dark wet rock, out-of-focus rushing water
> catching faint highlights, a few blurred leaves at the frame edge; a thin film
> of water on the stone and one or two droplets. Macro photograph, ~100mm
> equivalent, very shallow depth of field — only the head and shoulder tack sharp,
> the rest melting to bokeh. Soft diffused key from upper left with a cool moonlit
> rim on the frog's back, deep rich shadows, background falling to near-black at
> the edges. High-end natural-history photography look, subtle cinematic
> teal-and-amber grade. Frog positioned slightly right of centre facing left, with
> open negative space to the left and above. No text, letters, watermark, logo,
> caption, borders, human hands, or multiple frogs. Photorealistic, not
> illustrated or 3D-rendered.

**DONE:** Tony approved the prompt 2026-09-03. Generated 2 variants via GPT-Image-2
(4K 16:9), chose **v1** (internal organs visible through the translucent belly —
lands the beat — + strong left-side negative space). Saved to
`Images/scene_03/glass_frog_photo/` (`illustration.png` = v1, `_v1`/`_v2` kept,
+ SOURCE.md). Wired into `GlassFrogDoc.tsx`: `MIRRORED_POUCH_03` shot shortened
17.698s→9.8s; new `FROG_PHOTO_03` DiagramShot (7.898s, slow 1.03→1.10 push toward
the frog, no labels) — `DiagramScene` cross-dissolves them at ~43.0s scene-rel,
right as "actively camouflaging its own insides" lands (45.7s). tsc clean, stills
verified. In **FULL10** render.


## R2-3 — 06F + 06H "vanish" (finishes Block B) — DONE 2026-09-03
Seedance 1.5 can't animate a transparency dissolve, so done in the composition:
new `VideoSegVanish` helper (GlassFrogDoc.tsx) — the generated clip plays, then
over the last ~2s cross-dissolves to a static `<Img>` of that shot's
`Images/Start_End_Frames/Scene_06{F,H}_End.png` (frog already dissolved into the
leaf), with a slight continued 1.0→1.03 push so it isn't a dead freeze.
- 06F (3:28.9–3:37.0): dissolveS 2.2
- 06H (3:43.1–3:48.1): dissolveS 2.0
Stills confirm the frog fades to a faint impression in the leaf. tsc clean.
No regen, no cost. In FULL11.


## R2-4 — 06F→06G→06H tail rework (Tony feedback on FULL11, 2026-09-03)
Tony: horizontal-band tearing artifact at the 06F→06G boundary (~3:34-3:36); 06G
"too fast, you only see about a second" (the tear was eating 06G's opening);
"otherwise the fades look great."

Root cause of the tear: two live `OffthreadVideo`s overlapping at the hard cut,
one being pulled for frames right at its clip boundary. Fix — new `VanishShot` /
`HeldVideoShot` helpers + `Scene06Tail` layout:
- **No two live OffthreadVideos ever overlap.** Each clip's video fully fades out
  AND unmounts (`frame < cutoff` guard) ≥ ~50 frames before its real footage ends.
- Held tails use **pre-extracted still PNGs** (`Images/scene_06/hold_frames/`), not
  `<Freeze><OffthreadVideo/></Freeze>`.
- Every tail boundary is a real ~1.3s cross-dissolve (incoming fades in on top,
  outgoing holds its last still underneath).
- **06G extended**: video (6.07s real) plays ~5.5s then cross-dissolves to a hold
  still that Ken-Burns'es — **~8.8s on screen** now (was 6.07, and the front ~2s
  was garbled). 06F now 937→1095, 06G 1095→1360, 06H 1360→1513 (scene still 1513f).
Verified on stills: clean crossfades 06F→06G→06H, zero banding, 06G held shot
reads. In FULL12.


## R2-5 — 0.5s cross-dissolve on EVERY cut (Tony, FULL12 review 2026-09-03)
Tony: the ~1:25 cut (04C→04D) and "a couple clips after it" still feel like hard
cuts — the Note-1 0.5s cross-dissolve was only wired for scene boundaries +
diagram image changes + the 06F/G/H tail, NOT the scene_04 b-roll segments or the
scene_06 06A→06E run.

Fix: new `ChainScene` / `ChainSegBody` — lays a scene's video/diagram/node
segments with a ~0.5s (15f) cross-dissolve at every cut. Each non-final segment
extends 15f past its nominal end and FREEZES its last real frame there (video must
not play past floor(real) — loop-flash bug); next segment fades in on top on the
nominal boundary. Freeze-under + live-over = the scene_02 shape Tony approved;
never two live videos at once. Nominal boundaries stay frame-exact, scene totals
locked.
- scene_04: `<ChainScene>` over [RangeMap, 04B, 04C, 04D, 04E, 04F] (sum 1066).
- scene_06: `<ChainScene tailFreeze>` over [06A, 06B, 06C, 06D, 06E] (sum 937),
  06E freezes into the 06F tail; 06F `fadeInF` 0→15. `DiagramSeg` refactored to
  expose `DiagramSegInner` (no Sequence wrapper) so 06B/06C work as chain nodes.
Verified: tsc clean, mid-dissolve stills at all 10 boundaries show the crossfade,
no banding. In FULL13.
scene_03 / scene_05 already crossfade (DiagramScene). Still a hard cut: scene
06E→06F is now 0.5s; RangeMap→04B now 0.5s. Nothing left hard-cut except inside
single-clip scenes (01/07) which have nothing to cut to.

## R2-6 — Scene 06F limb deformation (~3:32) — Tony LET IT PASS, logged in Report_Card
Frog's front foot goes 3-4 toes → 1 toe mid-crawl (Seedance artifact). Tony's
choice to keep it. Recorded in `Data/Report_Card.md` under "let pass", plus the
gap it exposed: no per-frame limb/deformation checker on generated video clips
(only storyboard count-check + P8 internal-cut detector exist). Future pipeline
candidate.


## R2-7 — Audio mix retune + new score (Tony, judging FULL13 mixes by ear, 2026-09-03)
- **First mix (`FULL13_final_narr+music.mp4`):** score too quiet, sidechain duck
  "ducks in too abruptly." Tony asked whether the values were a standard or
  hardcoded. Answer: narration -14 LUFS = real YouTube standard; music level + all
  duck params = hardcoded workspace values ("Audio Mix Formula" memory).
- **Retuned + LOCKED** in `render_outputs.py`: music `loudnorm I=-26` → `I=-22`;
  duck `threshold=0.015:ratio=4:attack=150:release=800` → `0.045:2.5:300:600`.
  Tony A/B'd (`FULL13_final_v2_louder-gentler-duck.mp4`): "that worked great, lock
  it in." Memory (`feedback-audio-mix-formula`, `Global_Agent_Memory`), AW SKILL
  Phase 8, `2026-09-03_Feedback.md` all updated.
- **Score mood:** the original piano/ambient score = "sounded like a mystery
  trailer for a movie." Wants scientific, warmer, curious. New Suno prompt
  approved → generated. `generate_suno_music.py` rewritten to **save both API
  tracks** (`_v1`/`_v2.mp3`) + a `_suno.json` prompt sidecar (the 0003 original
  prompt had been lost). Score dir + both tracks: `Assembly/Score/`.
- **Tony picked Suno track 2** (`glass_frog_score_v2_v2.mp3`) → mix
  `Renders/FULL13_final_v3b_science-score-alt.mp4`. Chosen body-length score +
  body narration preserved in `Assembly/Score/` (`*_CHOSEN_track2_body_232s.mp3`,
  `narration_body_232s.mp3`).
- Still open: ambience/SFX stems layer (needs full regen — stale + no-audio
  clips), end card + CTA VO.
