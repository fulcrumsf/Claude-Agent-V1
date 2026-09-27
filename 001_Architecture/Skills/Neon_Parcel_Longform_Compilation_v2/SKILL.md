---
name: neon-parcel-longform-compilation-v2
description: "Use when building a Neon Parcel long-form animal compilation on the v2 architecture — a versioned duplicate of Neon_Parcel_Longform_Compilation (v1), which remains untouched and is the production-proven path used for 0001_Grandma-And-Bear-Compilation. v2 tests un-banning the CAMERA LOCK constraint (real camera-operator movement instead of a locked-off shot) now that the reference-image binding bug (wrong API parameter, then wrong @Image-tag syntax) that originally motivated the lock is understood and fixed. Triggers on 'build a Neon Parcel compilation with v2', 'test camera movement for Neon Parcel', or any request to reiterate this pipeline for the camera-lock experiment."
trigger: User invokes /neon-parcel-longform-v2 or asks to test the camera-lock change for Neon Parcel
---

# Neon Parcel Long-Form Reference-Inspired Compilation — v2 (camera-lock test)

This is a **versioned duplicate** of `Neon_Parcel_Longform_Compilation` (v1) — created 2026-09-17 per Tony's standing rule to never edit an active pipeline in place for an architecture-affecting change (see `feedback_video_pipeline_versioning` in Claude's memory). v1 is untouched and remains the production-proven path (CAMERA LOCK enforced — no pan/tilt/zoom/cut — the workaround adopted while the reference-image binding bug was still unresolved). v2 exists to test whether un-banning camera movement now produces authentic handheld realism without reopening the morphing/duplicate-subject failures, now that both the API-parameter bug (`first_frame_url` vs `reference_image_urls`) and the prompt-syntax bug (kie.ai's actual `@Image 1` tag, not a generic `@image_1`) are fixed. See `Pipeline_Progress_Report.md` in this folder for the full pain-point history and revised plan this version is testing against.

# Neon Parcel Long-Form Reference-Inspired Compilation

## Operating Rules (binding, locked 2026-09-20 by Tony — Neon Parcel pipeline only)

1. **The pipeline is the funnel; the docs are the source of truth, never recalled memory.** Before starting any new clip, and before producing ANY deliverable (matrix, audit, blocking plan, character sheet, environment sheet, storyboard, video, or anything else), re-read this SKILL.md and the skill that governs that deliverable, in that session, every time. Build the deliverable exactly as the doc specifies, completely (e.g. the environment sheet is every panel the Environment-Sheet-Generation skill requires, labeled, composited into the sheet, never a single frame), before showing it.
2. **Unsure or docs silent/conflicting/disagree with the disk: STOP and ask Tony.** Never fill the gap from memory, never pick an interpretation. Asking "should I follow the pipeline here?" is the wrong question; the answer is always yes.
3. **"Do everything up to the sheets" is a complete instruction.** Run the pipeline in order: matrix (skip if already chosen) -> Grounding Audit (Phase 1 + Phase 2) -> every other study/check listed in this doc -> Blocking Plan -> a character sheet for every subject the audit shows on camera (any visible human body part included, see below) -> the full environment sheet per its skill -> STOP and present the finished sheets. Tony reviews and gives notes or says continue. Fewer check-ins never means fewer steps.
4. **Storyboard, then video.** Do not generate video before a storyboard exists per the Storyboard-Generation skill.
5. **Never generate an environment-validation (empty-scene) video.** Tony never asks for one; it wastes money.
6. **Every video generation call sends everything built for that shot (locked 2026-09-20 by Tony).** Upload order and roles: (1) the approved storyboard, (2) the full environment sheet as approved (labels and all), (3) every character/creature sheet, (4) every prop sheet that exists. Never list only some of them because a request was worded loosely: Tony sometimes names a few items off the top of his head, but this rule, not the wording of one message, decides what is sent. Send only the FINAL version of every sheet, exactly as finished: with its title label and any markers, callouts, dots or points added. Never send a naked, unlabeled sheet, in any generation call (video OR image, e.g. storyboard generation), because the labels give the model context about what is in each sheet (locked 2026-09-20). Do not send superseded, rejected or unapproved sheets. Tag each with `@Image N` by upload order, state each role in the prompt, and check the finished video for label bleed and sheet/grid reproduction. Do not ask Tony which environment image to use; ask only if a required item is missing or has more than one candidate version.
7. **Iteration does not suspend the pipeline.** While Tony iterates on a process, every other step still follows this doc so he can judge what changed. "Lock it in / write it in" means: write it into this pipeline's docs; it is binding afterwards.
8. **Scope:** rules locked here are for the Neon Parcel pipeline only. Never write them into a shared/global file (Video_Editor/CLAUDE.md general sections, shared skills, other channels) unless Tony explicitly says "global."

10. **Always use the skill when one exists (locked 2026-09-20).** Any time a step of this pipeline asks for a deliverable that a skill or its script already covers (character/creature sheet, prop sheet, environment sheet, storyboard, prompting a model, etc.), invoke that skill and run its documented script/template, even if this doc never names the skill. Never hand-build or improvise a deliverable a skill covers. If you find a step here that has a matching skill but does not name it, add the reference to this doc in the same pass.

9a. **Environment sheets are built with the global presentation template** (`Environment-Sheet-Generation/SKILL.md`, 'Sheet presentation template'): JSON spec + `scripts/build_environment_sheet.py`, camera POV panel first and titled, labels in margins, never hand-laid-out.
9. **Always tell Tony exactly which images and settings were sent to any generation call** (every reference image by filename and role, model, resolution, duration), in the message where you report the result. Never let him assume the final sheet or a different asset was used.

### Open Test Flags

- **FLAG 1 (opened 2026-09-20, UNPROVEN): labeled environment sheet as a Seedance spatial reference.** Hypothesis (Tony): sending the full labeled environment sheet (labeled top-down / front / POV, with the POV panel titled as the camera's view) helps Seedance place landmarks in depth and out-of-frame, without the labels appearing in the video. Evidence so far: NONE on this pipeline -- Shot 02 (kangaroo) was generated from the clean POV panel only, and Shot 05 sent one clean POV panel. Test design: Tony will specify. Log: exact images sent, model/tier, whether labels bleed into the video, whether a composite sheet is reproduced as a grid/seams, and Tony's grade. If proven, Tony will lock it into the environment-sheet step (and decide whether it becomes global); until then it is not a rule.

## Optional Global Storytelling Consultation

Neon Parcel may use multiple storytelling styles across different formats. Before developing a new concept, beat structure, scene, storyline, or future Neon Parcel format, optionally consult [`Visual-Storytelling`](../Visual-Storytelling/SKILL.md) to select the smallest useful pattern. This is advisory only: this pipeline's compilation, realism, approval, generation, and artifact rules remain authoritative.

This is a dedicated pipeline for Neon Parcel YouTube animal compilations. It is
not the Neon Parcel TikTok Shop pipeline and must not route products or
affiliate content here.

## Core Output

- Master video: 16:9, target 6–8 minutes
- Content: many individually generated animal clips with natural durations
- Narrator: one consistent Neon Parcel narrator, added after the rough cut
- In-scene voices: optional and independently directed per clip
- Music: Suno by default, based on the case-study music profile
- Shorts: multiple 9:16 derivatives from the approved master
- Publishing: Blotato only after Tony approves the complete package

### Locked Default Video Route

Effective after the Shot 1–4 comparison tests, Neon Parcel's default video
generation route is:

`Neon Parcel storyboard -> Seedance 2 Mini 480p -> Topaz 2x (fal Proteus, Kie backup) -> FFmpeg 1920x1080`

This route received Tony's provisional grade of 89 (B+) based on direct review;
the previous mixed-generation route received a C-. This is a Neon Parcel
production decision, not a global replacement for other channels or models.
The Seedance 1.5 route remains available only as an explicitly chosen fallback
or comparison test. Do not silently switch routes because a shot appears
simple; record any override and its reason.

### Upscale fallback rule (locked 2026-09-20, Tony; order changed 2026-09-23, Tony)

The upscale step of the default route is: **fal.ai Topaz (model Proteus, Topaz auto settings, 2x) as the DEFAULT, up to TWO attempts; Kie.ai Topaz 2x as the BACKUP, up to TWO attempts; if all fail, Magnific's video upscaler as the last resort; then FFmpeg to exactly 1920x1080.** Why fal (Tony, 2026-09-23): it's half Kie's price ($0.02/s up to 1080p vs $0.04/s) and it exposes the Topaz model choice, while Kie takes only a scale factor. Why Proteus: it's the face-safest model fal offers (Topaz's face model Iris isn't on fal; the Starlight models are generative and more likely to morph faces). 2x keeps fal output at or under 1080p (above 1080p costs $0.08/s). First test (Shot 07 face clip, 2026-09-23): no face morphing, cleaner than raw, but softer than Magnific's Topaz Astra 2. A failed provider call spends no credits. Run it through `001_Architecture/Tools/Video-Generation/Generic_Tools/upscale_video.py`, which does all of this in order, logs every attempt to `Data/Generation_Log.json`, never overwrites an existing output, and refuses the Magnific fallback (asks Tony instead) if its estimated cost tops $5.

- **Magnific settings used and proven (monkey shot v7, Tony: "results are good"):** 1k output, `natural` flavor, creativity 0, no fps boost/sharpen/grain. Billed per output frame, about $0.007 (about $2.35 for a 14 s, 24 fps clip; confirm against the Magnific balance). Needs `MAGNIFIC_API_KEY` in `~/.env-secrets`.
- **Watch for:** Magnific can add fine detail that was not in the raw clip even at creativity 0 (it striped a monkey's tail). Review the upscaled clip against the raw one; if a subject's identity detail changed, tell Tony.
- Topaz stays the first choice: fal (about $0.28 for a 14 s clip), then Kie (about $0.56). Magnific's Topaz Astra 2 via the Magnific connector was used once for Shot 07 by Tony's one-off choice; it is NOT part of this route (Tony, 2026-09-23: save Magnific credits). This is a Neon Parcel route rule; the tool itself is generic.

## Non-Negotiable Safety Rules

- Preserve all source references, raw generated clips, edits, and renders.
- Never overwrite an approved render; create a new version.
- When a revision supersedes an unapproved file, move the old file into the
  production's `Archived/` folder. Never delete it. Keep active folders tidy by
  retaining only current working candidates and approved outputs there.
- Apply the same rule to every production artifact: images, storyboards,
  prompts, scripts, shot lists, metadata, audio, and renders. Preserve the old
  version number in the archive and give the replacement the next version
  number.
- Save every exact provider prompt payload before submission in the production
  `Prompts/` folder. Use immutable, shot/versioned files such as
  `Shot-01-Seedance-1.5-v1.json` or `.md`, including model, resolution,
  reference assets, parameters, and the resulting task ID after submission.
- A paid generation is blocked if its exact prompt has not been saved first.
- Reference videos are inspiration unless Tony has documented usage rights.
- Do not copy source dialogue, audio, choreography, framing, or sequence
  shot-for-shot from an unlicensed reference.
- Do not publish or call Blotato without explicit approval.
- Do not activate learned humor rules automatically.

## Intake

Ask:

1. What kind of animal video are we making?
2. Should Tony provide a YouTube reference, should the pipeline search, or
   should reference analysis be skipped?
3. Should generation use the default image-first path or an explicit
   text-to-video path?

If searching, return five clickable YouTube candidates. Search only videos
published between one month and one year ago. Rank using concept fit, views,
views-per-day, engagement, freshness, and competition. Add an Opportunity
badge when a concept has meaningful demand with relatively low competition;
do not make that badge the primary ranking rule.

The initial mode is human selection. Later, a configuration setting may permit
autonomous selection.

## Concept Development And Grounding

Before drafting a shot list, define the compilation's editorial promise and
scope. Treat the selected references as a curated set of submitted recordings,
not as a request to reproduce every location, climate, or joke found in them.

Generate concepts from complete believable events, not from a formula such as
"grandma plus bear plus random household object." A concept may be funny,
shocking, dramatic, or simply compelling. It does not require an explicit
punchline.

### Diversity Matrix (v2, locked 2026-09-17) — commit before writing any prompt

A single generation pass tends to drift into self-similar concepts — each new
clip idea anchors off what was just written, producing near-duplicates (e.g.
every clip defaulting to the same delivery-worker type, the same era, the
same region). Fix this structurally, not by "trying to be more creative":

1. **Build the matrix first.** Before any clip gets a written prompt, assign
   each clip a unique combination across: era (2001-present, sporadic —
   distribute across the whole range, do not cluster everything in the
   present day), region/culture (naturally varied, never stereotyped),
   delivery/service type (postal, Amazon-equivalent, food/takeout, furniture
   movers, or any other real plausible category — not just mail carriers),
   animal species, time of day, capture-device type (see the Blocking pass
   below), and **weather** (added 2026-09-18 — sunny, overcast, rain, fog,
   etc.; must be consistent with the stated region/season/time-of-day, never
   left undefined — an unstated weather condition is exactly the kind of gap
   that lets frame-to-frame lighting/ground-wetness drift happen unchecked),
   and **comedic hook** (added 2026-09-20 — a one-line, deliberately chosen
   interaction, mimicry, misunderstanding, or real-behavioral gag, not left
   to emerge from the other axes alone). **Real failure this closes:** Shot
   04 (tanuki/camcorder) passed every plausibility check and executed
   cleanly, and still graded a flat C — Tony's own words, *"it's just a guy
   on his scooter... wasn't that great."* The arrive → notice → mutual-watch
   → leave structure has no built-in comedic engine; it worked on Shot 02
   only because the kangaroo itself was visually incongruous enough to
   carry the scene alone. Era/region/service/animal/time/device/weather are
   grounding axes, not a comedy generator — a cell can be fully plausible
   and still be boring. Name the actual gag before building anything: what
   does a subject *do* that's funny, not just what does it *look like*.
   Check the table for duplicate combinations before any prose is written.
2. **Generate one clip's prompt at a time, not all at once.** Each generation
   call explicitly restates "already used: [list]" as a hard constraint —
   this interrupts drift instead of trusting one long context to
   self-regulate.
3. **Plausibility-check every matrix cell before locking it — do not assume
   a combination is real.** A combination like "2001 + Amazon package
   delivery" can be factually wrong (services, companies, and vehicle types
   didn't all exist in every era/region). Run this through the Grounding
   Audit before the matrix is locked — see below.

### Grounding Audit (v2, redesigned 2026-09-18 — two phases: self-questioning elaboration, then structured check)

**Governing principle:** every concrete, checkable real-world detail in a
shot must be explicitly stated and grounded before a prompt is written —
never left for the model to fill with its generic/statistically-dominant
default. Every plausibility failure caught in this pipeline so far (movers
and a truck ramp rendered oversized relative to a couch, a delivery courier
defaulting to a bike in a low-density regional town, robotic un-nuanced
carrying/reaction motion, a mover's body orientation flipping mid-shot,
environment geography reinvented per frame instead of held fixed) traces
back to this one root cause in a different domain each time.

**Real limitation, named directly (2026-09-18):** a fixed set of questions —
even the 5-column check below — only ever catches the categories someone
already thought to include. It cannot be exhaustive; new failure categories
will keep surfacing. The fix isn't a longer fixed list, it's a first phase
that *generates* its own questions from what this specific shot actually
contains, the way a real production researcher free-associates from "food
delivery, 2019, regional Australia" to "which specific chain — pizza,
Menulog aggregator, Chinese takeaway — what's he carrying, what's parked in
the driveway, what's in the yard" without needing to be told to ask any of
that in advance.

**Phase 1 — Self-Questioning Elaboration.** Takes the raw Diversity Matrix
cell (era, region, service/delivery type, species, time of day, capture
device, weather) as input, before any research tool runs. For every generic
or non-specific term in the cell, generate the concrete follow-up questions
a real production researcher would naturally ask to pin down the actual
real-world variant it implies — genuinely generated per shot, not pulled
from a template. This is where new concrete entities/objects/props the
matrix never explicitly named get surfaced (a specific delivery-service
variant, what it's carried in, what's actually in a rural Australian yard,
what a car vs. a ute looks like there). Write the generated questions and
their researched answers into `Research/Plausibility_Facts.md` as a plain
list, before the structured table below.

**Phase 2 — Structured Check.** Once Phase 1 has surfaced the concrete real
subjects, objects, and props for this shot, list every one of them plus the
location itself as rows in the same file, and run the fixed 5-column check
below on every row — this phase is the proven floor, not the ceiling; it
guarantees the specific failure categories already caught in this pipeline
never regress, even if Phase 1's free-form questions happen to miss one of
them for a given shot. A blank, assumed, or "sounds ordinary" answer is not
acceptable in either phase; research it (via
[`Production-Research-Agent`](../Production-Research-Agent/SKILL.md) or
direct knowledge) and write the concrete conclusion down as a stated fact.

| Column | Question it forces |
|---|---|
| Scale reference | Stated size relative to at least one other named element in frame — never assumed generic/heroic proportions |
| Arrival/mobility | How this subject moves or arrives, checked against the location's actual density/terrain/era — never a default transport mode |
| Motion/behavior nuance | The concrete physical execution of its action (weight shift, grip adjustment, flinch-then-settle arc), not just the named action or emotion |
| Era/region-appropriate form | Whether its design, clothing, tech, or behavior matches this specific real time and place |
| Plausible presence | Whether this entity/object would actually be here, in this specific setting, at all |

Every row's answers from both phases must be carried forward as explicit
stated details in the Blocking Plan and in every character-sheet/
environment/video prompt for that subject or object — the Blocking Plan may
not leave any column implicit for anything it describes, and may not skip an
entity Phase 1 surfaced just because it doesn't map cleanly onto Phase 2's
five columns.

### Grounding Coverage Check (v2, locked 2026-09-18 — mandatory before every generation call)

**Real failure this closes:** Test Shot 03's driver character sheet was
generated *before* the Grounding Audit redesign, still showing him wearing a
courier backpack — the visual archetype for a foot/bike courier. After the
Grounding Audit concluded he's a **local takeaway driver who parks a car and
hand-carries the order**, nothing ever went back and checked whether that
conclusion actually made it into the character-sheet prompt. It didn't. The
"re-read the plan before writing the prompt" rule is a discipline for the
person/agent writing the *next* prompt — it does not verify an *already
generated* asset still matches the audit once the audit itself changes. That
gap is what let a stale, ungrounded detail sit in an approved-looking sheet
indefinitely.

**The check itself:** before any generation call (character sheet,
environment plate, storyboard, or video prompt) for a shot, build a flat
checklist of every concrete fact from that shot's Grounding Audit — every
Phase 1 answer and every Phase 2 table cell — and go down it line by line
confirming each fact is either (a) explicitly present in the prompt text
about to be submitted, or (b) explicitly and intentionally excluded with a
stated reason (e.g. "car stays off-frame, not shown in this panel"). A fact
that is simply absent, with no line item accounting for it either way, means
the prompt is not ready to submit. This applies on every regeneration too,
not just the first pass — if the Grounding Audit changes after an asset
already exists (as happened here), that asset must be re-checked against the
updated audit before it's reused as a reference for anything downstream.

Record the checklist result in `Data/Grounding_Coverage_Check.md` per shot —
one checklist per generation call, not one for the whole shot — so a missed
fact is traceable to the specific prompt that dropped it.

### Remarkable-but-Believable Concept Filter

Use the global Purple Elephant principle as an optional concept check: the
idea should contain one clear, attention-stopping visual, but the footage must
still feel like a plausible real recording or submission. The unusual element
is the reason to stop; believable camera placement, environment, animal
behavior, human motivation, and cause-and-effect are what make viewers accept
the premise and continue watching.

Before approving a concept, answer briefly:

- What is the single visual anomaly that makes someone stop scrolling?
- Why would this camera realistically capture it?
- What ordinary situation makes the extraordinary event understandable?
- What visible escalation or consequence follows naturally?
- What is the cleanest ending once the visual payoff has landed?

Reject ideas that are merely weird, rely on a forced joke, or stack unrelated
surprises. Do not add a return trip, prop, line of dialogue, location change,
or reaction beat unless it strengthens the event. The pipeline may use this
filter for shocking or dramatic clips as well as humorous ones.

Treat Tony's approvals as calibration of the complete idea, not as approval of
its ingredients. A passing scene teaches the pipeline what made that scene
work overall—clear logic, plausible capture, physically readable progression,
and naturally quirky or surprising effect. It does not authorize reusing the
same environment, camera source, animal behavior, prop, dialogue pattern, or
ending. Generate the next idea from a broad variation space and run it through
an independent holistic review.

For each concept, reason through:

- Why someone would realistically capture or submit this footage
- Who is filming, where they are, and what camera perspective they have
- Whether the animal belongs naturally in the location and climate
- What the human believes is happening and why their response is sincere
- The visible progression of the event and its natural outcome
- Whether the humor comes from visual absurdity, character attitude, surprise,
  danger, reversal, or another clear editorial effect
- Whether dialogue sounds like a spontaneous human reaction
- Whether the concept is distinct without changing geography unnecessarily

Variation should serve the compilation's subject. Keep a normal themed
compilation regionally and ecologically coherent, varying homes, camera owners,
lighting, framing, and situations subtly. Use major geographic or cultural
shifts only when the stated compilation concept calls for them.

### Physical-Action Risk Filter

Before an idea becomes a shot, reject or simplify messy physical business
that is not necessary for the premise. Be especially cautious with fastening,
untangling, measuring, transferring, attaching, catching, precise handoffs,
multi-step object manipulation, and actions that require the camera operator
to hold two things at once. Prefer an observable event with a believable
camera operator, simple subject movement, and a clear natural outcome. The
complexity router may escalate a necessary action, but escalation is not a
reason to keep an avoidable action in the shot. If the premise still works
without the delicate mechanics, remove them before generating frames.

During the current review phase, present a small number of concepts one at a
time and wait for Tony's critique. Record successful and failed reasoning, but
do not impose an automatic score threshold or decide autonomously when review
is complete. Tony decides when the pipeline is ready to scale or operate
autonomously.

## Reference Case Study

For an approved reference, create one folder under:

`002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Case_Studies/`

Retain the downloaded reference video permanently with its analysis,
transcript, keyframes, and clip boundaries. Run the shared analyzer with:

```bash
python3 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py \
  "<youtube_url>" \
  --out "<case-study-folder>" \
  --profile production \
  --dense-interval 0.5
```

The production profile must analyze individual clip boundaries, editorial
beats, humor mechanics, music, sound effects, pattern interrupts, retention
techniques, dialogue placement, and originality boundaries. It should describe
why a moment appears to work without requiring Tony to annotate every clip.

Tony may add corrections or observations to the case study. Those corrections
are valuable training data but are optional for every scene.

## Learning Library

Case studies produce proposed reusable humor and editing patterns. Store them
as proposed patterns first. Tony must approve a pattern before it becomes an
active Neon Parcel rule. The director may use approved patterns autonomously,
but must not treat every case study as a rule.

Negative examples matter: when Tony identifies a clip as unfunny and explains
why, retain that critique as a guardrail against generating the same weak
pattern again.

## Character/Creature Sheets (v2, borrowed from Anomalous Wild, locked 2026-09-17)

Before storyboard generation, identify every distinct recurring subject in the
shot (each human, each animal — not the setting/props) and generate a
[`Character-Sheet-Generation`](../Character-Sheet-Generation/SKILL.md) sheet
for each one. Confirmed real failure mode this fixes: without a locked
reference, the video model reinvents each subject's identity and pose per
panel — different faces per frame, inconsistent grip/posture on a held
object. **Every distinct subject needs its own sheet — never share one sheet
across multiple subjects** (documented failure: sharing one sheet across
multiple background characters renders them all with identical faces, the
same underlying problem in reverse).

**Any visible human body part requires a character sheet — no exceptions, even a POV shot (locked 2026-09-20).** A human doesn't need to be fully on camera, or even have a visible face, to require a sheet — hands, arms, feet, or any other body part appearing anywhere in frame is enough to trigger this rule. Real gap this closes: Shot 05 (vervet monkey/shopfront) almost skipped a courier character sheet on the reasoning that no driver sheet was needed for Shots 03/04 — but those two shots had genuinely zero human body parts ever visible in frame (the driver stayed inside the vehicle), which is categorically different from Shot 05, where the courier's hands/arms are directly on camera setting down the clipboard and reaching for the monkey. **The test is "does any part of a human appear in frame," not "is the human the focus" or "is the face shown."** If the answer is yes, even for a single frame, build the sheet before generating anything downstream of it.

**Shared-wardrobe rule (v2, real failure logged 2026-09-17).** When two or
more characters need to share a matching wardrobe element (same uniform, same
company logo), do NOT rely on independent text-only character-sheet
generations to agree — they won't. Confirmed real failure: two movers'
character sheets, generated separately with identical text prompts that never
mentioned a logo at all, each independently invented their own fictional
moving-company hoodie logo, and the two logos didn't match each other. Text
silence on a detail does not prevent the model from inventing one, and two
independent generations have no shared memory to invent the *same* one.

**Fix (revised 2026-09-20):** for a shared wardrobe/logo item, generate ONE small
shared-item asset first, using [`Prop-Sheet-Generation`](../Prop-Sheet-Generation/SKILL.md)
with just that item (front view only, no extra panels), then pass it as an
`--input_urls` reference into every character sheet that must match it, with the
reference's role stated in the prompt. Full routing for every other prop is in
"Prop Routing" below.

## Prop Routing (locked 2026-09-20 — Neon Parcel rule, written to be portable)

<!-- BEGIN PORTABLE RULE: Prop Routing. To reuse in another pipeline, copy everything between the BEGIN and END markers unchanged. Requires the global Character-Sheet-Generation and Prop-Sheet-Generation skills. -->

**Goal:** a separate prop sheet is made only when it adds something the character sheets cannot. Decide it from the story beats, deterministically, before any sheet is generated.

**Step 1 — Prop ledger (once the beats/blocking plan exist, before any sheet).** List every prop in the beats. For each: who holds/wears/uses it, whether any side or orientation is hidden or matters, whether two or more subjects must match it, whether it recurs across clips or scenes.

**Step 2 — Route each prop:**

| Situation | Action | When |
|---|---|---|
| Two or more subjects must match the same worn/handheld item (uniform, logo) | Make one small shared-item asset (Prop-Sheet-Generation, single item, front only). Attach it to each character sheet call that must match it, role stated in the prompt | BEFORE the character sheets |
| Prop is used by a subject and its beats-required look/hold is visible | Put it in the subject's character sheet (in the subject description, from the beats). No separate prop sheet | During the character sheet |
| Prop is in the beats but not shown on any character sheet | Make a prop sheet | AFTER the character sheets |
| Prop has a hidden side or an orientation that matters (asymmetric front/back, a specific hold) | Make a prop sheet. Attach the holder's character sheet as a labeled reference so the held panel matches the holder; name the specific hand | AFTER the character sheets |
| Prop recurs across clips or scenes | Make a prop sheet | AFTER the character sheets |
| None of the above | No prop sheet. Write "<prop> covered by <sheet>" in the ledger | |

**Step 3 — Unsure whether a side/orientation matters, or the ledger is ambiguous: STOP and ask Tony in plain words.** Never decide alone.

**Any prop-sheet panel that shows a person's or creature's body part (hand, arm, foot) MUST be generated with that subject's character sheet attached as a labeled reference image, with the role stated in the prompt (e.g. "Reference image 1 is the courier: the hand must be this exact person's hand, same skin tone, build, and sleeve").** Describing the body part in text alone ("a dark brown hand") is never enough: it produces a generic hand that does not match the character. If that character's sheet does not exist yet, build the character sheet first.

**Always:** use the skills' own scripts/templates for every sheet; state each reference image's role in the prompt text; record the ledger and each routing decision in the shot's `Data/` folder.

<!-- END PORTABLE RULE: Prop Routing -->

Bind every sheet as an explicit `@Image N` reference in the storyboard
generation call, per this pipeline's existing reference-binding rule — a
subject with no sheet reference is exactly the condition that produces
per-frame identity drift.

## Automated Hand Check (locked 2026-09-20, Neon Parcel only — human character sheets only)

Runs automatically after **every human character sheet** is generated, before anything downstream uses it. Not run on creature/animal sheets (the tool can't read animal hands) or on environment sheets. It's our own free local tool, so there is no cost reason to skip it.

**Tool:** `001_Architecture/Tools/Video-Generation/Generic_Tools/check_sheet_hands.py` (settings in `sheet_checker_config.json` next to it: pass threshold 80%, foot filter on, scope switch `global_for_human_characters` currently false = Neon Parcel only). Finds each human hand, says LEFT or RIGHT with a confidence score, drops toes misread as hands.

**Step by step:**
1. Run `python3 check_sheet_hands.py <sheet.png> --pipeline Neon_Parcel --json --overlay-dir <shot Data folder>` and keep the annotated overlay.
2. Build the expectations only from cases where the view itself fixes the answer: front view (subject's RIGHT hand is on the picture's left, LEFT on the right); back view (LEFT on the picture's left); side profile facing left shows the LEFT side, facing right shows the RIGHT; plus any hand the story beats fix (e.g. "clipboard in his right hand"). Pass them as `--expect HAND:x0,y0,x1,y1` using the regions of the boxes the tool found.
3. **Gate:** pass at **80%** of expectations correct, AND no confident wrong answer (a hand called the wrong side at confidence 0.9 or higher fails the sheet regardless of score).
4. Save the result (overlay + pass/fail + which hands) in the shot's `Data/` folder.
5. **Fail:** regenerate the sheet, at most twice; if it still fails, stop and show Tony the overlay. Never silently accept a failed sheet.
6. **Pass:** show Tony the sheet as usual and say the hand check passed and at what score.

**Known limits (say them out loud when reporting):** since 2026-09-21 it seeds zoomed crops at every body-pose wrist, which raised recall on the courier sheet from 6 to 9 hands (it can still miss a hand); it cannot count fingers or prove a hand is not deformed (the landmark model always draws five fingers), and only flags low landmark confidence or extreme finger proportions for a human to look at; human hands only. A pass does not mean the hands look right, only that left/right matches what was expected. Until the tool covers those gaps, Tony still reviews finger count and deformity during iteration.

**Making it global later:** flip `global_for_human_characters` to true in `sheet_checker_config.json`; other pipelines then pass their own `--pipeline` name. No code change.

## Automated Body-Orientation Check (v2, locked 2026-09-18)

Runs on every generated storyboard, alongside the existing vision QA pass —
this exists specifically because Gemini's holistic visual QA missed a real
defect (a mover's body orientation silently flipped between panels) on Test
Shot 02. A vision-language model's own judgment about spatial/orientation
consistency is a documented, known weak point (see
`Character-Sheet-Generation/SKILL.md` and the pain-point history in
`Pipeline_Progress_Report.md`) — this check replaces that judgment with a
deterministic measurement instead.

**Tool:** `001_Architecture/Tools/Video-Generation/Generic_Tools/check_body_orientation.py`
— YOLO-pose (Ultralytics, PyTorch backend), not MediaPipe. MediaPipe's
pip-packaged pose models hard-crash on macOS (`DrishtiMetalHelper... Service
is unavailable`) — confirmed on both a sandboxed shell and a real M3 Max
MacBook Pro, on both full and lite model variants. Do not reintroduce
MediaPipe for this; YOLO-pose has no such dependency.

**Usage:** `python3 check_body_orientation.py <storyboard_or_frame_path>` —
reports each detected person's facing direction
(`TOWARD_CAMERA`/`AWAY_FROM_CAMERA`/`LEFT`/`RIGHT`) and bounding box.

**Known current limitation — coarse, not yet the exact check needed.** This
measures facing-toward-vs-away-from-camera, not "is Mover 1 still facing
Mover 2" (the actual continuity rule that failed). Matching which detected
person is which named character across panels, and computing their
orientation *relative to each other* rather than relative to the camera, is
real future work — pairing detections per panel by position and cross-
referencing against the character sheets. Until that refinement exists, use
this tool's output as a flag for human review (log to
`Production/Continuity_Flags.md`, same as other flags — do not auto-block or
auto-regenerate on it), not as a fully automatic pass/fail gate.

## Blocking & Capture-Device Plausibility Pass (v2, locked 2026-09-17)

Runs per shot, after a concept is picked, **before any storyboard image gets
generated.** This is directly why "Grandma wouldn't enter through the gate
even though it's right there" happened — the image model was left to infer
spatial geography with no plan, so it didn't establish the entry before
showing her past it.

**Scaled down from a real film tech scout, deliberately — not the same
thing.** A tech scout plans a trained camera operator's rig placement and
movement for planned professional coverage. Nothing here is planned or
professional — every shot is either a fixed device that nobody is operating,
or a real bystander reacting in the moment, not hitting marks. Pick which one
applies first, then only plan what that device type actually needs:

- **Fixed/mounted device (Ring, Nest, security cam, dashcam):** the camera
  position and frame are fixed by where the device is mounted — the only
  thing to plan is the subject's path through that fixed frame: where they
  enter, what they pass, where they exit. If a gate, door, or doorway is
  visible in frame, any subject who ends up on the other side of it must be
  shown passing through it — never skip straight to the far side.
- **Handheld/reactive (a real bystander filming on their phone):** there is
  no fixed geometry to plan. Instead, describe the realistic trigger →
  reaction chain: what does the subject do that a real untrained person
  filming would react to, and what would that person's camera actually do in
  response (step back, whip toward a sound, keep filming while retreating)?
  The "blocking" here is behavioral, not spatial.

Write the blocking plan as plain text per shot before generating the
storyboard image — one or two sentences is enough, it just has to exist and
be checked against the frame before the image gets made, not inferred after.

### Read the plan before writing any prompt — mandatory, not optional (real failure, logged 2026-09-18)

Confirmed real failure: an environment-sheet prompt defaulted to a generic
"wide shot + reverse angle" pairing instead of checking this shot's own
Blocking Plan first — which already specified the camera is a handheld
bystander's phone that never goes near the back of the truck. The reverse
angle was wasted generation spend on a camera position the actual shot would
never use. The Blocking Plan and Grounding Audit aren't background
context to have skimmed once — **every image or video generation prompt for
a shot (storyboard, environment plate, character sheet framing, final video
prompt) must be derived by re-reading that shot's own Blocking Plan and
Grounding Audit immediately before writing the prompt**, not from
memory of having read it earlier in the session and not from generic
photography/production convention. If the plan specifies a camera type,
position, or behavior, the prompt uses exactly that — it does not improvise
a "reasonable" alternative.

### Real-World Scale and Proportion Check (v2, locked 2026-09-18 — folded into the Grounding Audit's "Scale reference" column, see above)

Real citation for why this column exists: Test Shot 02 (approved with notes)
rendered the movers oversized relative to the couch and the truck, and the
truck's ramp/lift gate far larger and wider than that vehicle class would
actually carry. The Grounding Audit's Scale reference column is what catches
this before generation now, not after.

**Measured scale check — hard stop (Tony, 2026-09-26).** The Scale reference column is a written claim; Shot 07 passed it and still went to video with the van growing ~55% while parked and the van/fishmonger 40-100% oversized vs the harbour. So every storyboard is now measured before any video spend:

1. Write `Data/Scale_Spec.json` from the prompt and shot description: each subject's REAL height as the prompt states it (a 7-foot man = 2.13 m), a few detector words per subject (plain words often work better than names: the walrus was found as "large animal", the van as "truck"), at least one fixed anchor of known size in the environment (parked car, door, bollard), `horizon_row_frac` if all anchors sit at one distance, `static_from_panel` for anything that should stay put, and `in_panels` where a subject should be visible.
2. Exaggeration only where the prompt asks for it ("large walrus"): mark that subject `exaggerated` (and `pose_varies` if its posture changes). It still must obey physical `rules`, e.g. the walrus must fit in the van's cargo box (`max_ratio`). Everyone else stays realistic.
3. Run `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/check_storyboard_scale.py <clip_dir>` (local YOLOE, free, ~4 s). It fails only differences you'd notice by eye: same subject at the same distance changing size >15%, a parked subject moving, a subject >25% off what the anchors say that spot of ground should show, or two subjects side by side >25% off their real ratio. Undetected subjects are warnings ("not measured"), never passes. Show Tony the boxed picture (`Data/Scale_Check_<storyboard>.png`) with the storyboard for approval.
4. `seedance2_call.py` refuses the paid call unless the check PASSED on the exact storyboard file being used (sha256), printing every failure as a warning. Fix the storyboard, not the numbers.

### Natural, Unstaged Motion and Reaction (v2, locked 2026-09-18 — folded into the Grounding Audit's "Motion/behavior nuance" column, see above)

Real citation for why this column exists: Test Shot 02 (approved with notes)
had a carrying motion and startled reaction that read as robotic/staged AI
slop, because only the named end-state action/emotion was specified with no
physical micro-detail (weight shift, grip adjustment, flinch-then-settle
arc). The Grounding Audit's Motion/behavior nuance column is what catches
this before generation now, not after.

## Production Checklist (v2, locked 2026-09-17)

Every v2 production gets a `Data/Pipeline_Checklist.md`, checked off in order
as gates clear — not just prose instructions to follow, an actual trackable
list:

- [ ] Diversity Matrix built and checked for duplicate combinations
- [ ] Grounding Audit complete (every column, every subject/object/location row)
- [ ] Blocking & Capture-Device pass done for every shot
- [ ] Blocking Plan + Grounding Audit re-read immediately before writing
      each generation prompt for this shot (not assumed from memory)
- [ ] Grounding Coverage Check run against every generation prompt (character
      sheet, environment plate, storyboard, video) — including regenerations,
      and any asset that predates a later Grounding Audit update
- [ ] Automated Body-Orientation Check run on every generated storyboard
      (flags logged for human review, not auto-blocking)
- [ ] Shot-List Approval Gate (below) passed
- [ ] Continuity flags logged, not auto-regenerated (see below)

## Continuity Flag Logging (v2, borrowed from Anomalous Wild, locked 2026-09-17)

When a review pass (Video-Analyzer or manual) flags a possible continuity or
anatomy issue in a generated clip, do not automatically regenerate it —
flagging has proven unreliable in practice on other channels (a flagged issue
was reviewed and found not actually present). Log the flag with a
description and timestamp to `Production/Continuity_Flags.md` and surface it
to Tony for review instead of spending generation credits chasing a possible
false positive. This is a training-phase rule for v2 specifically — expect to
review flags by hand for the first several productions on this version, and
relax it once the camera-lock-removed approach proves reliable.

## Shot-List Approval Gate

After the compilation concept and reference study, present:

- A 2–3 sentence brief
- A numbered shot list
- One sentence per clip
- Natural clip duration estimate
- In-scene dialogue, if needed
- Tentative narrator role: none, setup, reaction, context, or transition

Tony may request targeted revisions such as "rewrite shot 3." Do not generate
the full paid batch until the approved shot list is accepted.

## Generation and Progressive Autonomy

### Video model default: Seedance 2.0 Mini (locked 2026-09-19, Neon Parcel only)

**Seedance-2-Mini, via `kie_market_api.py`'s `seedance_mini` command (never `kie-cli`), is the default video model for every Neon Parcel shot.** Confirmed via a real pilot test on Shot 03 (moose/dash-cam, `0002_Delivery-Wildlife-Encounters-Compilation`): the full multi-reference recipe (environment plate + character sheet in `reference_image_urls`, ordinal `@ImageN` tagging, timestamped action beats) ran successfully on Mini and was graded C by Tony — a real, usable result, not A-tier like the standard-model Shot 02, but roughly 80-90% cheaper per second. Given that cost difference, Mini is the default; standard Seedance-2 via `kie-cli` is a deliberate, explicitly-stated upgrade for a shot that specifically needs it, never a silent fallback.

**This default is scoped to Neon Parcel only.** It does not change any other channel's already-locked model/version choice (e.g. Anomalous Wild's Seedance 1.5 Pro) — see `Video_Editor/CLAUDE.md`'s Video preference order for the workspace-wide default and this note about per-channel overrides.

1. Generate Clip 1 using the locked default storyboard/Mini route and wait for approval.
2. Revise Clip 1 until Tony accepts it.
3. Generate Clips 2–5 individually using the locked default route and wait for approval.
4. Release the remaining approved shots for batch generation only after Tony
   explicitly says to proceed.

Clip durations are emergent. A successful 5-second clip remains 5 seconds and
a successful 12-second clip remains 12 seconds. Trim only to isolate the
payoff or remove unusable material.

Maintain a diversity ledger covering animal appearance, location, camera,
lighting, action, props, sound, dialogue source, and prompt phrasing. Compare
each new prompt against prior prompts before generation to reduce repetitive
patterns while preserving the episode concept.

### Pre-Video Quality Gates

Run these gates after the still frame or storyboard is created and reviewed,
but before any paid video-provider request. They are conservative: `pass` is
required for every gate; `review` or missing structured evidence blocks the
request. The gate must inspect the proposed scene and reference asset, not
merely search for keywords.

### Storyboard Review Policy

Storyboard vision checks are advisory evidence, not an autonomous clearance
mechanism. After each storyboard generation, the agent must inspect the
generated sheet panel by panel and report concrete findings about subjects,
object states, spatial relationships, chronology, eyelines, action, camera
geometry, physics, and captions. Gemini/OpenRouter results may support that
review, but they must never automatically clear or reject the storyboard. The
agent must present the notes to Tony and wait for his explicit decision to
approve, request a revision, or reject before revising the storyboard or
spending video credits.

### Video Inspection Provider Policy

Direct Gemini API inspection is the default for generated video. For short
Neon Parcel clips, use static processing with dense sampling (default 3 FPS)
so the reviewer can evaluate the full timeline, object origins, chronology,
eyelines, geometry, camera continuity, and audio anomalies. Use Gemini agentic
processing for long-form videos or targeted long-video questions where dynamic
timeline navigation is useful. OpenRouter remains the fallback if direct
Gemini is unavailable or a second opinion is explicitly requested. Provider
reports are evidence only: neither provider may automatically clear or reject
a video, and the agent must report findings and wait for Tony's decision
before upscaling, replacing, or advancing the asset.

- **Visual realism:** subject anatomy, fur/skin, materials, lighting, shadows,
  scale, and contact with the environment must not read as a 3D render or
  synthetic model.
- **Camera plausibility:** the claimed source (security camera, doorbell cam,
  neighbor phone, passenger phone, body-worn camera, and so on) must explain
  the camera's position, framing, lens character, movement, and who could
  physically be operating it. A security or doorbell shot must not look like a
  polished commercial camera move.
- **Meaningful visual beat:** the action must have a readable setup,
  development, and outcome. Repetition is allowed only when it escalates or
  has a clear contextual reason.
- **Humor context:** prefer believable absurdity, sincere human behavior,
  surprise, reaction, reversal, or danger over an invented punchline. Every
  line of dialogue and every important prop must have a causal reason to be
  present. The moment must remain understandable without narration.

The exact gate evidence is saved with the shot routing record. A failed or
uncertain gate keeps the shot in review and preserves the rejected asset and
reason for later calibration. The gate does not attempt to teach itself humor
or activate a learned pattern without Tony's approval.

Generation prompts describe only scene, camera, action, and native audio.
Captions, title cards, labels, rankings, emojis, watermarks, and other text
overlays are specified and rendered later in post-production. The Benny case
study may inform recording style and premise structure, but not copy its
characters, dialogue, sequence, or distinctive presentation.

### Mandatory Seedance Prompt Contract

Before writing any Neon Parcel Seedance prompt, re-read the shared
[`Seedance-Prompting-Guide`](../Seedance-Prompting-Guide/SKILL.md). Neon Parcel
prompts must follow that skill's four-layer order and the machine-readable
contract in [`Seedance-Prompt-Contract.json`](./Templates/Seedance-Prompt-Contract.json).

Because the storyboard becomes Seedance's visual planning input, also re-read
the shared [`Storyboard-Generation`](../Storyboard-Generation/SKILL.md) skill
before writing or revising any Seedance prompt. Before generating or revising
any Neon Parcel storyboard, read both skills as well: Storyboard-Generation
controls the frame-by-frame contract, while Seedance-Prompting-Guide controls
what the eventual provider can reliably receive and animate. A prompt or
storyboard handoff without both skill contexts is invalid and must not spend
provider credits.

The contract is a hard gate, not a writing suggestion. Every saved prompt must
contain these separate sections in this order:

1. **Camera Lock** — capture source, physical placement, viewpoint, lens
   character, framing, movement, and what remains fixed.
2. **Scene Continuity** — subject count, identities, setting, geometry, and
   object states that must persist.
3. **Action Timeline** — only the necessary visible beats, in chronological
   order, using concrete physical cause and effect.
4. **Audio** — native ambient sound, foley, and in-scene dialogue only when
   causally justified.
5. **Hard Constraints** — concise exclusions for duplicates, morphing,
   skipped states, disappearing geometry, camera drift, unwanted text, and
   other shot-specific failure modes.

Do not combine camera instructions and action instructions into one dense
paragraph. Do not tell Seedance to reproduce storyboard panels literally when
the storyboard is only a visual-continuity reference. Do not use vague verbs
such as “handles,” “interacts with,” or “drives it back” when the shot depends
on physical action; describe the observable movement and result instead. The
prompt preflight must fail if a required section is missing, empty, out of
order, or represented only by an unstructured freeform string.

**Tagging rule (locked 2026-09-20):** every reference image is mapped at the top (`@Image N = ...`) AND used by tag as the subject of every action beat (`@Image 3 walks to the counter...`), never plain "the courier"/"the monkey". The storyboard and environment tags are also referred to in the body. `check_seedance_prompt_refs.py` enforces this and runs automatically inside `kie_market_api.generate_seedance_mini()`; a prompt that fails makes no paid call. Full wording and examples: `Seedance-Prompting-Guide`, "Use the tag as the subject in the action text".

### Winning Video Formula (locked 2026-09-20, Tony graded the source run B+: "v7 is the winner")

This is the way every Neon Parcel Seedance video prompt is built and sent, unless Tony changes it. Full template with placeholders: [`Templates/Seedance_Winning_Prompt_Template_v7.md`](./Templates/Seedance_Winning_Prompt_Template_v7.md). Source run: monkey / African messenger shot, `Prompts/Full-Action-Seedance-2-Mini-480p-v7.md` and `Data/Seedance_Mini_v7_Labeled_Sheets.mp4`.

0. **Every Neon Parcel Seedance video call goes through `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/neon_seedance_call.py` (which runs the GLOBAL gate `Generic_Tools/seedance2_call.py`), never a hand-built call (locked 2026-09-20; global for every Seedance 2 / Mini call).** It reads the shot's `Data/Video_Reference_Set.json` (the record of the final approved labeled assets) and builds the reference list itself in fixed upload order, so what is sent never depends on memory or on how a request was worded. It blocks the paid call if the manifest or a file is missing, a sheet is not the labeled version, a printed sheet label is not quoted in the prompt, the `@Image` tag check fails, or the five sections are out of order. Update `Video_Reference_Set.json` whenever a sheet or the storyboard is approved as final. Use `--dry-run` to see exactly what would be sent.
1. **Send everything, final labeled versions only** (Operating Rule 6): storyboard, full labeled environment sheet, every character/creature sheet with its title bar, every prop sheet that exists. Upload order: storyboard, environment, characters, props.
2. **Reference block first:** one `@Image N = ...` line per image. The storyboard line says to follow its shot selection and panel order (not a collage); the environment line names the CAMERA POV panel by its printed title and pins it to the first frame and every frame; each character line quotes the sheet's printed title. Never show sheet labels, layout or title text.
3. **Five contract sections in order** (Camera Lock, Scene Continuity, Action Timeline, Audio, Hard Constraints). Camera Lock describes the frame layout in words. Scene Continuity states exact subject counts and real-world scale.
4. **Every action beat names its subject by `@Image` tag** (enforced by `check_seedance_prompt_refs.py`, runs before the paid call).
5. **Save the prompt before submission**, one paid call per version, log every reference and the grade in `Data/Generation_Log.json`.
6. Known remaining weaknesses of the formula on its first run (watch for them): a brief camera reframe, a beat arriving earlier than its timestamp, a subject cropped at the frame edge on frame 1.

### Generation Idempotency and Artifact Separation

- Create exactly one paid provider-generation task per shot version. Before
  submitting, check the production generation log for an existing provider
  task ID for that shot and version.
- Never resubmit a shot because a downstream file is missing, renamed, or being
  normalized. Retry only when the provider task failed, the output is corrupt,
  or Tony explicitly requests a new revision; record the reason and new
  version before spending credits.
- Seedance 1.5 Pro at 1080p goes directly to final normalization; it does not
  use Topaz.
- Seedance 2 Mini at 480p is the only route that uses Topaz 2x, followed by
  FFmpeg normalization to exactly 1920x1080. FFmpeg resizing is not a second
  provider generation.
- Keep provider outputs and Topaz intermediates in the production's
  `Working/` or `Intermediate/` area. Keep only the final normalized shot
  versions in `Video_Clips/`; archive experiments separately.
- Before creating a replacement shot version, archive the superseded
  unapproved version under `Video_Clips/Archived/` and preserve its metadata.
- Record every provider task ID, processing stage, source file, output file,
  and retry reason in `Data/Generation_Log.json`.
- Link the saved prompt file to the corresponding generation-log entry. Never
  replace an old prompt; a revision creates a new prompt version.

### Reference Routing Contract (rewritten 2026-09-20 to match the proven route)

The approved storyboard sheet IS sent to Kie Seedance Mini as a bound reference image in `reference_image_urls` (tagged `@Image 1`), together with the environment sheet, every character sheet, and every prop sheet, per Operating Rule 6. This is the production-proven route (Shot 12 v8; the monkey shot v3 also ran without the sheet being reproduced). Never send the storyboard as `first_frame_url`: that makes Seedance animate the grid itself (confirmed failure, Shot 12 v1). `reference_image_urls` and `first_frame_url`/`last_frame_url` are mutually exclusive on this endpoint. The prompt must say the storyboard is a sequence of action instructions, not a collage or tiled layout, and that no panels, captions, borders, labels or sheet layouts appear in the video. After every run, inspect the raw clip for sheet reproduction, grid seams, captions, label bleed, duplicate objects (e.g. a second bicycle), camera drift and geometry drift before any upscale. If the leftovers (a title bar, border or labels) sit only around the edges and the scene itself is intact, crop them off first instead of paying for a new video (Shot 07 was saved this way; Tony, 2026-09-26); save the crop as a new version and check the whole frame afterwards. If the scene itself is broken (tiled into a grid, split, or the crop would cut the action), use the **keyframe fallback** next (Tony, 2026-09-26): cut the approved storyboard's panels into clean keyframe images with `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/extract_storyboard_keyframes.py <storyboard.png>` (no generation, no cost; each panel cut at its own border, native ratio, no caption text; files land beside the storyboard as `<stem>_Keyframe_NN.png`), list them under `"keyframes"` in `Data/Video_Reference_Set.json`, and re-run the same shot with `seedance2_call.py --keyframes`. The storyboard is NOT sent in this mode (it stays saved; nothing is deleted). Reference slots fill in priority order up to Kie's 9-image limit: all keyframes, then character/creature sheets, then the environment sheet, then prop sheets; the gate lists anything left out. The prompt must say "Use @Image 1 through @Image N as keyframes in this order" (official Seedance keyframe wording) and each keyframe tag is referred to again in the beat it anchors. Only if the keyframe run also fails does the approved-first-frame/last-frame fallback apply.

### Mandatory Active-Folder Audit

After every generation, revision, archive operation, or batch completion, and
before reporting status, inspect the production's active `Video_Clips/` folder.
For each shot, exactly one current version may remain there. Move every older,
superseded, rejected, test, or duplicate version into `Video_Clips/Archived/`
without deleting it. Then verify the active folder again and report any
unresolved duplicate or ambiguous version instead of claiming the production
is tidy.

The provider wrapper must perform this check before submitting. A successful
or pending task for the same production, shot, and version blocks submission;
the only permitted exceptions are a recorded provider failure, corrupt output,
or an explicit Tony revision with a new version and reason. A missing prompt
archive or missing generation-log reservation is also a hard block.

### Shot Complexity Routing

Before generating a clip, route every approved shot through the shared
complexity checker:

```bash
python3 001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/route_shot_complexity.py \
  "<shot-list.json>" \
  --out "<production-folder>/Data/Shot_Routing.json"
```

The checker must use semantic scene understanding to assess action count,
physics, object continuity, limb precision, character interaction, spatial
continuity, timing, dialogue synchronization, failure risk, and storyboard
value. Keyword matches may support the assessment but must never be the sole
reason for routing a shot. The semantic assessment, score, reasons, QA
intensity, and any explicit route override are saved with the route decision.
The checker does not automatically move simple shots to Seedance 1.5; Neon
Parcel's normal route remains Seedance 2 Mini for low- and high-complexity
shots.

- `0-4`: default Seedance 2 Mini route with low-complexity QA notes
- `5–7`: manual route review; do not spend generation credits automatically
- `8-20`, or a hard physics trigger: default Seedance 2 Mini route with enhanced storyboard/temporal-anchor QA, followed by Topaz 2x upscaling and final FFmpeg scaling to 1920x1080

Use Seedance 1.5 only when Tony explicitly chooses it as a fallback or
comparison test and the reason is recorded in the routing log. For that
optional fallback, decide whether an end frame is needed before generating it.
Use an end frame only when it shows a materially different, unambiguous state
with stable camera geometry, consistent subject count, and a clear endpoint.
If it repeats the start composition, preserves a vehicle or subject that
should have exited, introduces disappearing geometry, or otherwise risks
confusing interpolation, omit the end frame and use start-frame-only
generation. Missing or uncertain endpoint evidence requires manual review; the
pipeline must not create a speculative second image just because the provider
supports one.

Hard triggers include mechanical interactions, catching or transferring
objects, breakage/spills, and multi-step ordered actions. A shot may include
`route_override: seedance_1_5_fallback` or
`route_override: seedance_2_mini_default`; the router records the override and
reason rather than hiding it. This router recommends QA intensity and records
route decisions only; it does not call providers, approve paid generation, or
replace Tony's review.

The default route is explicitly `Seedance 2 Mini 480p -> Topaz 2x -> FFmpeg
1920x1080`. Normalize the final long-form master to 1920x1080 before creating
Shorts derivatives. FFmpeg performs the final dimension/container normalization
and does not add an API charge.

For every complex-shot prompt, apply the shared Seedance complex-action
guidance: lock the capture source and camera geometry first, name every fixed
object involved, describe ordered visual states and object paths, and include
explicit anti-drift constraints. The storyboard is a sequence of checkpoints,
not decorative inspiration. Review the complete generated clip for skipped
states, camera drift, object continuity, duplicate subjects, and disappearing
geometry before approval.

Complex storyboards must be 16:9 and contain no more than six frames per
segment. If one shot needs more than six frames, split it into sequential
segments and name the resulting files with suffixes such as `Shot-03A`,
`Shot-03B`, and `Shot-03C`. Each segment must preserve the prior segment's
ending state as its next starting state.

### Neon Parcel Storyboard Template

This Neon Parcel template overrides the shared storyboard sheet's presentation
only; do not modify the global Storyboard Generation skill. Each storyboard
frame must be a true 16:9 landscape image area. Use a clean white caption band
under every frame. Put the frame number and a brief one-sentence description
inside that white band, never inside the image area. The sheet is a visual
continuity reference for the video model, not a comic layout or a literal
multi-panel scene to reproduce. Preserve one camera viewpoint, subject count,
setting geometry, and chronological state progression across the frames.

Use the saved example at
`001_Architecture/Skills/Neon_Parcel_Longform_Compilation/Templates/Neon-Parcel-Storyboard-Template-Example.png`
as the format reference. No captions, labels, numbers, or graphics belong in
the image areas themselves.

Seedance Mini should generate the clip's native ambient and action audio when
that model's audio mode is enabled. Do not use Suno for foley or sound
effects. Suno is reserved for instrumental background music and must not
generate vocals or voice-like lyrics.

For Mini storyboard prompts, explicitly bind the output to the storyboard's
visual language: same capture source, camera placement, angle, lens type or
focal-length feel, framing, horizon, distortion, lighting, and fixed geometry.
Use concise wording such as "match the attached 16:9 storyboard camera and
composition exactly; animate only the ordered action." QA must compare the
generated clip against the storyboard for camera angle, lens character,
framing, and geometry drift, not only for whether the action occurred.

For any storyboard-reference generation through Kie, explicitly bind
references by upload order using Kie's playground syntax: the first uploaded
image is `@Image 1`, the second is `@Image 2`, and so forth. Save that mapping
in the generation manifest. **This route is production-proven and
Tony-approved, not experimental** — confirmed 2026-09-18 against Shot 12's
actual generation history: v1 failed because the storyboard was bound as
`first_frame_url` (Seedance animated the grid itself), but the approved v8
bound it correctly as `reference_image_urls` with the `@Image 1` tag and a
prompt stating explicitly that the storyboard is "a sequence of action
instructions, not a collage or tiled layout to reproduce" — see
`Productions/0001_Grandma-And-Bear-Compilation/Prompts/Shot-12-Seedance-2-Mini-v8.md`
for the exact reference template. Use that template's structure (reference
order declaration, per-panel action breakdown, camera/realism section,
continuity/physics section, audio section) for every storyboard-bound video
generation prompt.

This rule applies to every visual reference in a Seedance prompt. If the upload
set contains a storyboard, character sheet, environment sheet, and prop sheet,
declare all four roles explicitly as `@Image 1`, `@Image 2`, `@Image 3`, and
`@Image 4` according to their actual upload order. Natural-language dictation
may describe the intent loosely, but the generated prompt and manifest must
contain the exact provider syntax.

### QA-ready storyboard contract

Before generating a Neon Parcel storyboard candidate, serialize the shot with
the structured contract in
`001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_contract.py`.
Do not rely on a freeform storyboard paragraph for continuity-critical shots.
Every frame must explicitly declare visible subjects, object states, spatial
relationships, ordered action, and the exact caption. Validate the contract
before calling GPT-Image-2. Later phases of the storyboard-QA workflow consume
the same frame requirements to inspect the generated sheet, cap retries at
three candidates, and block Seedance when no candidate passes.

### Capped storyboard regeneration

The attempt controller in
`001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_regeneration.py`
is the required chokepoint for storyboard retries. It reserves each candidate
before generation, requires the prior candidate's QA result before advancing,
archives every failed candidate, and hard-stops at three attempts. Only a
candidate with `status == "pass"` may be promoted as the active storyboard;
`fail`, `manual_review`, and provider-failure outcomes remain blocked from
Seedance handoff. Live provider adapters must be injected at the loop boundary
and still pass the existing Tool-Manager and paid-generation gates.

## Editorial Narration Pass

Assemble the approved clips into a rough cut first. Then write the narrator
script as if the narrator is the editor rewatching the completed compilation.

### Validated Neon Parcel narration defaults

- Use ElevenLabs voice `Herbie` (`Kz0DA4tCctbPjLay2QT1`) for this compilation
  pipeline unless Tony explicitly selects another voice.
- Generate narration as separate, shot-aligned lines rather than one long read.
  Save each line as a versioned audio asset with word-level timing.
- Keep narration concise: use short introductions, reactions, and transitions;
  do not narrate continuously over every moment. Preserve usable spontaneous
  dialogue already present in the clips.
- Every narration line must be shorter than its associated clip and must remain
  within that clip. Total narration should remain well below the combined clip
  runtime so the edit retains natural pauses and source audio.
- For the first review cut, do not add music, branding, captions, or publishing
  elements. The purpose is to evaluate narration, clip order, and source audio.

### Validated narration assembly and mix

- Concatenate clips with a timestamp-safe FFmpeg filter workflow. Never use
  stream-copy concat for a mixed set of generated clips: clips may have missing
  audio streams, different sample rates, or incompatible timestamps.
- Insert intentional stereo silence for a clip with no source audio. Preserve
  each clip's original audio where present, resampling the complete source bed
  to 48 kHz stereo before mixing.
- Place each VO line near the beginning of its associated clip, leaving the
  action and original sound room to breathe. Do not allow narration to cross
  into the next clip.
- Validated review-cut starting mix: original clip audio at `0.55`, narration
  at `1.6`, both mixed at 48 kHz stereo. Treat these as the pipeline defaults
  for the narration review cut, then perform a final loudness and clipping QC
  before delivery.
- Verify that video and audio durations match within a small tolerance and
  that the audio stream reaches the final video frame. A render that merely
  contains an audio stream but loses the tail is not acceptable.
- If a mix is regenerated, create a new assembly version; never overwrite a
  prior review cut.

### Music and end-screen defaults

- After Tony approves the narration review cut, add an instrumental music bed
  with a comical, quirky, whimsical, family-friendly home-video-TV-show feel.
  Avoid lyrics, profanity, ominous drama, aggressive trailer energy, and music
  that competes with original dialogue or narration.
- Keep music as a separate layer and duck it beneath narration and meaningful
  in-clip dialogue. Do not add music to the narration review cut before Tony
  approves that direction.
- Every Neon Parcel long-form video must end with the approved horizontal
  end-screen asset:
  `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Assets/Neon_Parcel_Endscreen_Horizontal_1080.mp4`.
- The end screen is a dedicated seven-second final segment. Place the CTA
  voiceover entirely inside that seven-second window; never let narration from
  the preceding clip spill into it. Generate the CTA with the locked Herbie
  voice and verify its duration before assembly.
- End-screen and CTA rendering must create a new versioned assembly and retain
  every prior review cut. Do not publish until Tony approves the complete
  music/end-screen master.

For each clip, decide:

- Self-explanatory: no narration
- Needs setup: narrator before the action
- Needs reaction: narrator during or after the payoff
- Needs context: short explanatory line
- Dialogue-driven: preserve or generate in-scene dialogue
- Transition: narrator bridges clips

Narration must add perspective, not describe the obvious, and must stay within
the clip it belongs to. Generate the approved narrator track with ElevenLabs
after the narration pass is approved.

## Shorts Derivatives

Create multiple Shorts from the final master. The target duration is 60
seconds, but it is not a hard duration.

- Use the nearest complete clip boundary to select each Short's interval from
  the approved master. Never cut through a clip, action, or narration.
- A Short may end below 60 seconds.
- A Short may exceed 60 seconds when needed to preserve the final complete clip.
- Do not allow narration to cross from one clip into the next.
- Use Part 1, Part 2, etc. only for the derived Shorts, not the long-form title.

### Locked Reframe Method: Subject-Aware Reframer, Hybrid Mode

As of 2026-09-15, the 16:9→9:16 crop for every Neon Parcel Short is produced
with the Subject-Aware Reframer at
`001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/`,
using its `hybrid` profile as the fixed default. Do not use the older manual
FFmpeg crop-expression script (`create_shorts_derivatives_v1.py`'s hand-tuned
`x_expr`) for new Shorts; that approach is superseded. Do not render Group or
Subject variants for comparison — Hybrid is locked in, not a per-video choice.
Tony confirmed this lock-in on 2026-09-15 after approving the Part One Hybrid
render; see the Feedback Loop and cross-session memory for that date.

Steps, run from the Subject-Aware-Reframer tool directory:

1. **Determine the Short's shot boundaries in the wide master.** Get each
   shot's frame count from its individual clip in `Video_Clips/` via
   `ffprobe -show_entries stream=nb_frames`, then find the cumulative pts at
   30 fps... at the master's native fps (currently 24, `time_base=1/12288`,
   512 ticks/frame). Confirm cut points against real scene changes with:
   `ffprobe -f lavfi -i "movie='<master>',select='gt(scene\,0.15)'" -show_entries frame=pts,pts_time:frame_tags=lavfi.scene_score -of csv=p=0`.
   Do not trust multiplied durations alone — the master can have small VFR
   drift from concat; always cross-check against detected scene cuts.
2. **Analyze** (`run_offline.py analyze --config <Detection-Config>.json --out <new-run-dir> --device cpu`).
   Build the detection config from the previous shot's/production's config as
   a template: same `source`/`source_sha256` (the shared wide master),
   `classes: [0,14,15,16,17,18,19,20,21,22,23]` (person + all COCO animal
   classes — needed because YOLO mislabels the AI-generated bear as dog/cat),
   `confidence: 0.1`, `inference_size: 960`, `family_tracking: true`, and a
   `shots` list with this Short's own pts boundaries. Set
   `expected_source_frames` from the tool's own probe, not your manual
   estimate — run once, let it raise a `ValueError` with the actual count if
   your guess is off, then correct the config and rerun.
3. **Frame/plan/render** (`run_offline.py reframe --job <Framing-Job>.json --out <new-run-dir>`)
   with a single `"Hybrid": {"profile": "hybrid", "settings": {}, "shot_overrides": {}}`
   variant, 1080×1920×30 output, pointing `analysis` at step 2's
   `Detections-And-Tracks-v1.json`. Verify `full_decode_passed: true` and
   `source_unchanged`/`protected_media_unchanged: true` in the run report
   before proceeding.
4. **Composite the opening title overlay** on top of the Hybrid render — this
   is a separate FFmpeg step, the reframer does not do it:
   `overlay=0:0:enable='between(n,0,29)'` (frames 1–30 at 30 FPS), reusing the
   production's existing per-part overlay PNG (1080×1920, centered, slightly
   above vertical center, TikTok/Shorts-safe padding, no payoff under it).
5. Each run's output directory, detection config, and framing job are
   permanent evidence — never overwrite a prior run; use a new run folder
   per Short.

New Shorts output/config folders live under the production's
`Shorts/Versions/<vN>/Auto-Reframe-Part-<N>/`, mirroring the Part Three Gate 3
evidence structure. Note a cosmetic bug: `diagnose.py`'s analyze step
hardcodes `Part-3` in its own output filenames (contact sheet, debug video)
regardless of which part is actually being analyzed — harmless, but don't
confuse it with the real Part Three production.

## Final Package and Publishing

### Compilation-Level Packaging Gate

The long-form title and thumbnail must promise the compilation as a whole, not
just the representative hero frame used in the thumbnail. The thumbnail may
feature one vivid moment, but its visual hook and optional text overlay must
signal the recurring collection pattern: multiple unusual animal encounters,
escalating absurdity, or a repeated Grandma-versus-wildlife situation. Do not
use a single-clip title or overlay unless the entire video is genuinely about
that clip. Keep the packaging bright, eye-catching, vivid, and poppy while
remaining truthful to the complete clip set.

### AI-Fiction Disclosure (Title + Description)

**Added 2026-09-17** after a YouTube automated-system copyright warning landed
on a realistic-looking rescue/encounter video that did not actually infringe —
the system read the footage as potentially real. Per YouTube's own guidance on
distinguishing fictional content
([support.google.com/youtube/answer/2802008](https://support.google.com/youtube/answer/2802008)),
titles and descriptions are part of how both the automated system and viewers
judge whether footage is understood as fictional. This is a hook-then-reveal
channel by design — footage should still look real on first watch — the
disclosure lives in text metadata, not a burned-in overlay, so it never
undercuts the visual hook itself.

- **Title:** for any title that reads as a real rescue/bodycam/security-cam
  moment (the channel's normal register), include a short qualifier — "AI
  Fiction" or "AI Comedy" — rather than wording that could pass as a real-event
  claim (e.g. avoid bare "Real Hero Moment" framing).
- **Description:** every long-form and Shorts description ENDS with this
  disclosure (moved from the opening to the end by Tony, 2026-09-20: the hook
  line leads, the disclosure follows it, and the hashtags stay last):
  > This is a fictional, AI-generated scene made for entertainment — not
  > footage of a real event. No real animals or people were placed in danger
  > or harmed during its creation.
- **Blotato AI-disclosure toggle:** keep this set alongside the text
  disclosure, not instead of it (per the "set synthetic-media disclosure where
  applicable" step below) — the checkbox and the text description are two
  separate signals YouTube considers, neither substitutes for the other.
- This is a mitigation, not a guarantee against a false-positive warning — it
  is the concrete step available without reworking the visual hook.

### Mandatory Thumbnail Template

Every Neon Parcel long-form compilation thumbnail must use the structured
`Thumbnail-Architecture-Template.json` from the shared
`youtube-thumbnail-design` skill. Fill the template from the actual compilation
and visually inspected reference examples before generation. Do not replace the
template with an improvised prompt. The global template is reusable across
channels, but this pipeline always requires the formatted template, including
its collection-level promise, demographic matching, subject separation, text
safe area, mobile validation, and non-destructive versioning fields.

Demographic and identity decisions are content-first. Inspect the actual
compilation before selecting the Grandma's appearance; do not carry a
demographic constraint from one production into another. For the current
Grandma-and-Bear production only, the approved direction uses varied white
Southern grandmothers because that is what this compilation's thumbnail brief
requires. This is a production decision, not a global pipeline rule.

### Thumbnail Package Scaffold

Within every production's `Package/` directory, thumbnails belong in the
existing `Thumbnails/` folder. Current approved thumbnails stay directly in
`Package/Thumbnails/`; rejected, superseded, or older thumbnail versions move
to `Package/Thumbnails/Archived/`. Never leave thumbnail image files loose in
the package root, create a parallel thumbnail folder elsewhere, delete a
superseded candidate, or overwrite an existing version.

Use the Neon Parcel skill together with:

- [`title-hook-generator`](../title-hook-generator/SKILL.md) for five title
  options, the YouTube description, and the required under-500-character tag
  string with selected common misspellings.
- [`youtube-thumbnail-design`](../youtube-thumbnail-design/SKILL.md) for the
  16:9 thumbnail concept, generation, mobile-size check, and iteration.

Every Neon Parcel long-form metadata pass must output titles, one description,
and tags together. Tags must be comma-separated, collection-level, under 500
characters, and checked for misleading claims before package approval.

Create the long-form title, description, thumbnail, Shorts titles, and report
cards after the final edit is stable. Produce both:

- `Data/Report_Card.md`
- `Data/Report_Card.json`

Wait for Tony's approval of the complete long-form and Shorts package. Only
then use the established Blotato workflow, confirm the Neon Parcel YouTube
account live, set synthetic-media disclosure where applicable, and report the
resulting status.

### Validated Blotato YouTube Upload

- Before every upload, call `blotato_list_accounts` and match the account by
  channel name and platform. Neon Parcel's YouTube account is currently `25731`;
  never infer or reuse an ID from another platform or channel.
- Upload local media through
  `blotato_create_presigned_upload_url`, then PUT the raw bytes with an explicit
  `Content-Type` header (`video/mp4` or `image/jpeg`). Use the returned public
  URLs in `blotato_create_post`.
- Check the video against Blotato's current size limit before transfer. If the
  approved PNG thumbnail exceeds 2 MB, create a separate JPEG upload copy;
  never alter or overwrite the approved source thumbnail.
- For the private first-review upload, send `privacyStatus: "private"`,
  `shouldNotifySubscribers: false`, `isMadeForKids: false`, and
  `containsSyntheticMedia: true`, plus the selected title, description,
  video URL, and thumbnail URL. Do not send tags; Blotato has no YouTube tags
  field, so surface them for manual YouTube Studio entry.
- Blotato currently exposes no YouTube category or caption-language field.
  Treat Entertainment category and English caption language as explicit
  YouTube Studio follow-up settings, not as silently completed API fields.
- Choose the YouTube category from the actual editorial promise. For a comedy-
  led animal compilation, use `Comedy`; use `Entertainment` only when the
  collection is not primarily comedic. Do not carry this choice into unrelated
  channels or formats without checking their content.
- Poll `blotato_get_post_status` after submission and record the returned
  `postSubmissionId`, status, and URL. A custom-thumbnail OAuth error means the
  YouTube account must be reconnected in Blotato; retry with the same uploaded
  media URLs rather than re-uploading.

### Validated Blotato Shorts Upload (TikTok, YouTube Shorts, Instagram Reels, Facebook Reel)

Locked in 2026-09-15 after the first cross-platform Shorts publish (Part One).
Each Short uploads once, then posts to all four Neon Parcel accounts from the
same public media URL:

- Call `blotato_list_accounts` and confirm live account IDs before every
  upload; do not hardcode from memory alone even though these are stable:
  - YouTube: `25731` (title required; this account also receives Shorts —
    a public, vertical, <60s-ish upload is auto-detected as a Short)
  - TikTok: `27763` (`@neonparcel`)
  - Instagram: `29334` (`@neonparcel`)
  - Facebook: `18651`, with `pageId: "888301901041580"` ("NeonParcel" page)
- Upload the finished Short (reframed + overlay-composited) once via
  `blotato_create_presigned_upload_url` + PUT with `Content-Type: video/mp4`,
  then reuse that one `publicUrl` in all four `blotato_create_post` calls.
- Per-platform fields used for the public Shorts release:
  - YouTube: `title`, `privacyStatus: "public"`, `shouldNotifySubscribers: true`,
    `isMadeForKids: false`, `containsSyntheticMedia: true`.
  - TikTok: `privacyLevel: "PUBLIC_TO_EVERYONE"`, `isAiGenerated: true`,
    `isBrandedContent: false`, `isYourBrand: false` (organic entertainment
    content, not a sponsored/business disclosure).
  - Instagram: `mediaType: "reel"`, `shareToFeed: true`.
  - Facebook: `mediaType: "reel"`, `pageId` as above.
- Caption/description text is shared across all four platforms; YouTube's
  `title` field is separate. Two relevant hashtags go inside the caption
  text, not a separate field.
- Poll `blotato_get_post_status` for any post that returns `in-progress`;
  Instagram and Facebook Reels routinely take 10–20+ seconds longer than
  YouTube/TikTok to finish processing.
- This is a public-release action requiring Tony's explicit go-ahead on the
  specific title/caption/hashtags before every publish — the approval gate
  is per-Short, not a standing authorization.

### Autonomy-readiness status

Track readiness in the production manifest, report card, session log, feedback
loop, and shared memory. Tony's current status for this compilation pipeline is
65%. Do not treat the pipeline as mostly autonomous or schedule it for routine
execution until Tony raises the status to 95%. Even at 95%, retain the
non-destructive versioning, paid-generation, manual exception, and publishing
approval gates.
