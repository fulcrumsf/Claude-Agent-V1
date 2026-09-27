---
title: "Neon Parcel Long-Form Pipeline — Progress Report"
type: progress-report
channel: Neon Parcel
pipeline_version: v2 (in progress, testing camera-lock removal)
prior_version: v1 (Neon_Parcel_Longform_Compilation — untouched, production-proven, used for 0001_Grandma-And-Bear-Compilation)
updated: 2026-09-17
---

# Neon Parcel Long-Form Pipeline — Progress Report

Read this before touching the pipeline. It exists so any session — this one or
a future one — has the real history instead of re-deriving it from scratch.

## Where this pipeline actually stands

Only one real production exists: `0001_Grandma-And-Bear-Compilation`, built on
v1. v1 is now frozen and untouched (`Neon_Parcel_Longform_Compilation/`). This
folder (`_v2`) is a full duplicate created to test one specific change —
un-banning the CAMERA LOCK constraint — without touching the proven v1 path.

## Pain-point history from production 0001 (v1)

Full source: `Data/History/`, `Data/Generation_Log.json`, `Data/Report_Card.md`
in `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/`.
Note: `Data/Checkpoints/` was never used (empty) and `Generation_Log.json`
doesn't actually carry the severity-tagged issues field the studio spec calls
for — the real issue detail lives in `failure_findings` on individual entries
and in the architecture logs/feedback files, not in one central place.

**1. Storyboard-as-video bug (the root cause of the CAMERA LOCK constraint).**
Two separate, layered bugs, not one:
- API-parameter layer: the storyboard image was submitted via `first_frame_url`
  instead of `reference_image_urls`, so Seedance literally animated the
  storyboard sheet as video content. Hit Shots 06/08/09/10/11/12 at once (v1).
  Fixed 2026-08-30 by rejecting invalid field combinations at the API boundary
  in `kie_market_api.py` plus regression tests. Fixed 06/09/10/12 immediately;
  08 and 11 still needed clean-start-frame fallbacks.
- Prompt-syntax layer: even with the right field, the reference tag Claude was
  using (`@image_1`) wasn't kie.ai's actual binding syntax. **The same failure
  mode recurred on 2026-09-05** on Shot 12 v3 — a literal 3×2 tiled contact
  sheet rendered inside the video, and the vision QA pass didn't catch it. The
  fix that finally stuck: kie.ai's real tag is `@Image 1` (capital I, a space,
  no underscore) — plus hardening the pre-video gate to block unverified
  composite-storyboard references and default to clean 16:9 start/end frames.
- Shot 12 alone took 8 versions. This bug had two separate onset events, not
  one — treat "it's fixed" as "fixed for now," not "solid forever."

**2. Subject/vehicle duplication — still not a solved problem.**
Shot 3: a storyboard reference alone did not reliably lock vehicle/driver/bear
count (a second identical car+driver+bear appeared). Shot 06 v4: multiple
camera views instead of one locked viewpoint, unwanted dialogue, Grandma
exiting/re-entering frame. Two *different* fixes worked on two different
shots — Shot 06 needed explicit "exactly one Grandma, never
disappear/exit/re-enter/duplicate" language plus making her silent (fixed in
v5); it also needed a structurally different mechanism (switching from
storyboard-reference to first-frame/last-frame temporal anchors, v7) to fully
lock camera and subject count. There is no single universal fix yet — expect
to keep solving this per shot.

**3. Morphing / spatial continuity.**
Shot 2: an alligator morphed instead of physically rotating when turning.
Shot 11: took 5 storyboard revision rounds (v2-v5) chasing a bear drinking
from a water source that wasn't visibly connected to the sprinkler, and
Grandma's eyeline/gesture tracking the bear's *future* position instead of
its current one — fixed only once gaze/gesture tracked actual per-frame
position.

**4. The one thing that reliably worked — camera/architecture legibility.**
Shot 08 (graded A) succeeded specifically because both subjects' starting
positions were visible and the path between them was unobstructed. Explicit
lesson from the Report Card: establish every moving subject's origin before
motion begins, and describe a continuous visible route — don't make the model
infer architecture.

**5. Assembly/audio defect (already resolved, unrelated to generation).**
First narration cut had a concat/audio-tail defect; fixed in v4 by switching
to timestamp-safe filtering, intentional silence for clips lacking audio,
48kHz stereo, and locked gain levels (narration 1.6 / original-audio 0.55).

**Load-bearing lesson:** nearly every major failure traces back to treating
"attach the reference image" as a solved, generic step instead of verifying
the specific provider's actual binding mechanism (API parameter AND tag
syntax). The fix that stuck combined a code-level guardrail (reject invalid
field combos before submission) with a documentation-level rule: every
uploaded reference needs its own explicit `@Image N` role in the prompt.

## What triggered this v2 fork

A real reference-video case study (`Handheld_Realism_Bear_Reference` under
`Case_Studies/`) showed that authentic camera-operator movement — whip pans,
turning away then back, camera drops — is a real driver of "looks real"
believability, alongside non-morphing bodies and genuine human reactions.
v1's CAMERA LOCK (banning all pan/tilt/zoom) was adopted specifically to stop
the morphing/duplication failures above, before the real root cause (the
two-layer reference-binding bug) was understood. Now that the actual bugs are
fixed, it's worth testing whether camera movement is safe to allow again.

## Revised plan for v2

**Video Analysis skill (shared, not Neon-Parcel-specific):**
- Add an explicit required field for camera-operator behavior — what triggered
  each pan/tilt/whip/drop, the exact motion, timestamp — instead of leaving
  it to emergent luck from the generic "camera type and motion" prompt.

**Neon Parcel v2 pipeline:**
- Un-ban CAMERA LOCK — test on one shot first, not the whole pipeline.
- **Diversity Matrix (new, locked)** — build a full cross-axis matrix (era,
  region, delivery/service type, animal, time of day, capture device) before
  writing any prompt; generate one clip at a time with an explicit
  already-used exclusion list, to stop cross-clip concept drift/repetition.
- **Plausibility Research (new, locked)** — Production-Research-Agent,
  repurposed to fact-check each matrix cell (did this service/vehicle/era/
  region combination actually exist) before the matrix locks, instead of its
  usual animal-biology research role.
- **Blocking & Capture-Device Plausibility Pass (new, locked)** — per shot,
  before any storyboard image generates: pick fixed-device vs.
  handheld-reactive first, then plan only what that device type needs (a
  subject's path through a fixed frame, or a realistic
  trigger-to-camera-reaction chain). Deliberately scaled down from a real
  film tech scout — nothing here is planned/professional, so don't import
  full crew-department formalism. This is the direct fix for the
  "Grandma didn't walk through the visible gate" failure.
- **Production Checklist (new, locked)** — `Data/Pipeline_Checklist.md` per
  production, checked off as gates clear.
- **Continuity Flag Logging (new, borrowed from Anomalous Wild)** — log
  possible issues to `Production/Continuity_Flags.md` instead of
  auto-regenerating; training-phase rule, review by hand for the first few
  v2 productions.
- Harden the existing vision QA gate with an explicit check for the tiled/
  contact-sheet failure signature specifically — it slipped past general
  judgment once already.
- Subject-count locking: treat as still-open, expect per-shot handling, not a
  universal fix.
- Carry forward the Shot-08 lesson as standing guidance: establish every
  moving subject's origin before motion begins, describe a continuous visible
  path.
- Add grain/compression-artifact language to prompts (currently only vague
  "ordinary image quality").
- Ground shots in real reference footage, not just AI-generated storyboard
  stills.
- Test Kling 3.0 Pro for shots where authentic handheld chaos matters more
  than precise control (weak prompt adherence, but camera shake reads as
  genuinely real — a plausible fit despite the tradeoff). Keep Seedance for
  shots needing tight continuity.
- Add Gemini Omni to the model roster as an untested option — physics-aware
  generation is directly relevant to the morphing problem; not yet in
  Tool-Manager's `model_catalog.json`.
- AI-fiction title/description disclosure — already added to both v1 and v2
  (see "AI-Fiction Disclosure (Title + Description)" section in SKILL.md).

**Parked for later, not part of this fork:**
- The multi-style plug-in structure (compilation / single-shot viral /
  AI-vlog format selection at intake) — a separate, bigger architectural
  change Tony wants to design deliberately later, not bundled into this
  camera-lock test.

## Concept selected for the v2 test production

**Theme (not a character/series):** wildlife encounters caught on camera
during a delivery — a *theme*, not a recurring protagonist. Different houses,
different delivery workers, different animals, different eras/regions each
clip — same mechanic that made Grandma-and-Bear work (varied real people in
one situation type), broadened beyond mail carriers to any delivery/moving
worker (postal, Amazon-equivalent, food/takeout, furniture movers, etc.).

## Stale pipeline docs can contradict real production history (real failure, logged 2026-09-18)

`route_shot_complexity.py`'s canned `generation_policy` text for the
`seedance_2_mini_storyboard` route said not to send a storyboard to Kie at
all — directly contradicting the fact that this exact route was the one
Tony approved in production (Shot 12 v8). This text was written before the
route was verified and never updated afterward, and it produced wrong
guidance when read at face value. **Lesson: when a tool's own docs/policy
strings conflict with what actually happened in production, or when Tony's
memory of a prior resolution disagrees with what a script currently says,
go verify against the real source records (`Generation_Log.json`, the
actual approved prompt files) before acting — don't trust a canned string
just because it's the thing that answered fastest.** Both the script and
`SKILL.md`'s "experimental route" language have been corrected to point at
the real proven technique (`Shot-12-Seedance-2-Mini-v8.md` as the reference
template: storyboard bound via `reference_image_urls` + `@Image 1` tag,
never `first_frame_url`).

## Test shot progress — Shot 2 (movers/fox, UK) — environment sheet saga

Real pipeline lessons from actually running this test, now locked into
`Character-Sheet-Generation/SKILL.md` and `Environment-Sheet-Generation/SKILL.md`:

1. **`@Image N` reference binding works as documented** — character sheets for
   both movers and the fox, bound correctly, fixed the identity-drift problem
   from the first storyboard attempt.
2. **Shared-wardrobe items need their own prop sheet first**, referenced into
   every character that wears it — two independent character-sheet
   generations invented two different logos for what was supposed to be one
   company's uniform. Fixed by generating one uniform prop sheet, then
   referencing it into both mover sheets.
3. **My own visual QA of spatial/geometric consistency is unreliable** — a
   real, known vision-language-model limitation, not something more effort
   fixes. Going forward: describe concrete specifics, don't assert
   correctness as a verdict; Tony is the actual spatial-continuity gate.
4. **The multi-panel-in-one-generation-call technique for environment sheets
   does not work**, even with real reference photos and an explicit
   strict-consistency clause — confirmed via research this is a genuine
   GPT-Image-2 capability ceiling (no ControlNet-style structural
   conditioning), not a prompting problem. Three attempts, three different
   geometry failures.
5. **What actually works:** generate one angle at a time as its own single
   image, chain each new angle's reference to the *immediately prior
   generated plate* (not the original source photos re-supplied each time),
   and only generate angles that correspond to real camera positions the
   actual shot uses (derived from the blocking plan) — not generic
   photography convention like "wide + reverse angle." Composite separately
   generated, individually-correct plates into one sheet with a deterministic
   layout tool (Pillow), never another AI call.
6. **Ground architecture-specific locations in a real reference photo**, not
   pure text-to-image invention — Google Street View Static API is now set
   up (`Antigravity-Claude` project, same key as YouTube Analytics, see
   TOOLBOX.md) specifically for this.
7. **Drop a defective generation rather than forcing it.** Plate 2 (camera-left
   angle) had the truck rendered half-on-the-sidewalk; rather than
   re-prompting repeatedly, proceeded with the one correct wide plate
   (`Environment_Plate_1.png`) and left the second angle for later.

**Current state:** `Environment_Plate_1.png` (single wide establishing shot,
grounded in a real UK terraced-street Street View photo + the approved
storyboard) is the locked environment reference for this test shot. No
second angle yet. Character sheets for both movers (uniform-matched) and the
fox are done. Storyboard itself has not yet been rebuilt against these
corrected references.

## Test shot progress — Shot 3 (kangaroo/delivery driver, doorbell cam) — environment sheet saga (2026-09-19)

By far the most extended, expensive lesson of this pipeline version so far
— documented in full because the pain here is what produced the most
durable process fixes. Chronological, not sanitized:

1. **First architecture defect:** staircase offset from the door with a
   mismatched second patio level — real construction-logic failure, not
   caught until Tony looked at it directly. Fixed: locked a single
   centered staircase, axis-aligned with the door.
2. **Second defect, same category:** the "fixed" staircase had 10+ steps —
   architecturally implausible for a normal single-story house. Root
   cause: nobody had checked step count against real building-height
   standards. Fixed by grounding in an actual construction fact (~450–
   900mm floor height ÷ ~180mm rise ≈ 4–5 steps) plus a real reference
   photo (a Queenslander with a genuinely short stair run).
3. **Third defect:** hedge drawn as one unbroken line, sealing the
   driveway off from the walkway with no gap for a person to actually
   walk through. Fixed by requiring an explicit stated gap at the
   walkway crossing, every time.
4. **Fourth, much larger defect: wrong generation order, discovered late.**
   The photoreal POV panel had been generated *first*, then treated as
   "ground truth" to measure and derive the top-down/reverse diagrams
   from — backwards. Tony's correction, stated as a hard rule after this
   had recurred: **top-down first (single source of truth), front/reverse
   view second, POV last — always, no exceptions, no "generate the photo
   first since it's more grounded" rationalization.** This is now locked
   in `Environment-Sheet-Generation/SKILL.md`.
5. **Fifth defect, exposed by the above:** every spatial check up to this
   point only compared left/right (x-axis). Real defects lived on axes
   nothing was checking: water tank and clothesline were on the *correct
   side* but at the *wrong depth* (too close to the house instead of near
   the street), a hedge reached the correct side but stopped short of the
   actual property edge (an extent error, not a position error), and the
   car's facing direction was never checked at all, independent of its
   position. Fixed: every spatial fact now needs x **and** y, line
   elements need a start/end span, and directional objects need an
   explicitly stated and separately-checked orientation.
6. **Built two new global tools mid-saga, at Tony's direction, because
   "try harder" wasn't the fix — tooling was:**
   - `check_subject_positions.py` gained `--save-panels` (full-resolution
     individual panel export) and `--onion-skin` (red/cyan frame-diff
     overlay) after repeated wrong readings from eyeballing a shrunk
     6-panel thumbnail.
   - `check_landmark_positions.py` (new): open-vocabulary object detection
     (OWL-ViT) for landmarks that aren't COCO classes (water tank,
     clothesline, mailbox, hedge). **Real, honest limitation found by
     actually testing it:** works cleanly on photoreal images, returns
     garbage on schematic/line-art diagrams (too far outside the model's
     training distribution) — the tool doesn't replace visual review for
     schematic panels, it only closes the gap for photoreal ones.
7. **Car orientation flip-flopped THREE times** before landing correctly.
   "Backed in" as shorthand got misread in both directions across
   attempts. What actually fixed it: (a) describing orientation by literal
   visible parts ("front bumper/headlights face X, rear bumper/tail
   lights face Y") instead of jargon, and (b) annotating the front/rear
   arrows directly onto the top-down source-of-truth image via a
   deterministic PIL overlay, so orientation became a fixed visual fact
   instead of something re-derived in prose on every new panel.
8. **Lawn rendered as a triangle/wedge instead of a rectangle** on a
   photoreal panel — fixed by naming the actual defect shape explicitly
   in the prompt ("must NOT narrow into a triangle") plus specifying a
   standard (not wide-angle) lens, since generic "match the reference"
   language wasn't specific enough to prevent the distortion.
9. **Switched the front/reverse-angle panel from schematic line-art to
   photorealistic mid-saga**, on Tony's suggestion — sending the top-down
   as a real image reference with "interpret positions from the attached
   diagram" framing, generating with no baked-in labels, adding labels
   afterward as a separate deterministic PIL step. This produced
   noticeably more reliable geometry than asking one call to solve
   real-world photographic accuracy and correct label placement at once.

**Current state (resolved, 2026-09-19):** the full environment sheet was
completed (top-down, front/reverse, POV, landmark detail — 4-panel
composite, Tony-edited POV as final ground truth), labeled, composited,
and approved. The shot then went all the way through Seedance video
generation and was graded **A** on the first full attempt. See "Shot 3
outcome" below for what actually happened once generation started.

**The single biggest meta-lesson, stated directly by Tony and now the
standing discipline for this whole pipeline:** a coordinate check that
only measures one axis, or a verification method that's just "look at a
screenshot and describe it," will keep missing real defects that live on
whatever dimension isn't being checked. The fix each time wasn't trying
harder at the same method — it was building or writing down something
that made the missed dimension checkable at all (a tool, an annotated
image, an explicit stated fact).

## Shot 3 outcome — first A-grade result, and the confirmed recipe it produced (2026-09-19)

All the environment-sheet discipline above paid off directly: once the
sheet was locked, Seedance video generation succeeded on the first
attempt at the hardest shot type this pipeline has attempted yet (fixed
doorbell POV, two independent subjects — human + kangaroo — six
sequential action beats, multiple hard continuity constraints). Tony's
own words: *"That did extremely well... grade that an A."*

**Two-step generation process used, now the default:**

1. **Cheap validation pass (205 credits, 5s, single reference):** the
   clean environment plate alone, camera-locked, empty-scene prompt — to
   confirm the sheet holds up in motion (object orientation, line-element
   extent, no label bleed, genuine static lock) before spending real
   credits on the full shot. This is the same "verify before spending"
   discipline as the depth/extent/orientation checks above, applied one
   stage later in the pipeline.
2. **Full multi-reference call (574 credits, 14s, three references):**
   environment plate + both character sheets in one `reference_image_urls`
   array, `@Image1`/`@Image2`/`@Image3` ordinal-tagged, driven by a
   timestamped 6-beat action-block prompt with continuity constraints
   repeated inline at the beat where each applies, closed with the
   standard negative-prompt line.

Both steps used the **clean, unlabeled** POV panel — never the labeled
reference-sheet copy — confirmed to produce zero label bleed across both
generations. Full recipe now locked in
[`Seedance-Prompting-Guide/SKILL.md`](../Seedance-Prompting-Guide/SKILL.md)'s
"Confirmed recipe" section and
[`Environment-Sheet-Generation/SKILL.md`](../Environment-Sheet-Generation/SKILL.md)'s
"clean vs. labeled" rule — this is the first time either pipeline's
Seedance multi-reference/multi-character-sheet theory has been confirmed
end-to-end on a real production shot, not just documented as a sourced
hypothesis.

**One open minor note carried forward, not blocking:** the kangaroo held
its mid-hop pose fairly statically for ~2s during the watch beat — a
softer version of the "staged/robotic motion" issue first flagged on Shot
2. Worth naming explicitly in a future shot's prompt (an animal's
weight-settling detail, the way the driver's stutter-step was already
named) if it recurs.

## Open question blocking the next step

Whether to proceed to a full production render of Shot 3, or treat it as
complete and move to the next Diversity Matrix test shot — Tony's call,
not yet made as of 2026-09-19.
