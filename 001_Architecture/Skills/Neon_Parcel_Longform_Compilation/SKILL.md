---
name: neon-parcel-longform-compilation
description: "Use when Tony asks to create a Neon Parcel long-form animal compilation, analyze reference animal videos for Neon Parcel, or generate Shorts from a Neon Parcel long-form compilation."
trigger: User invokes /neon-parcel-longform or asks for a Neon Parcel long-form compilation
---

# Neon Parcel Long-Form Reference-Inspired Compilation

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

`Neon Parcel storyboard -> Seedance 2 Mini 480p -> Topaz 2x -> FFmpeg 1920x1080`

This route received Tony's provisional grade of 89 (B+) based on direct review;
the previous mixed-generation route received a C-. This is a Neon Parcel
production decision, not a global replacement for other channels or models.
The Seedance 1.5 route remains available only as an explicitly chosen fallback
or comparison test. Do not silently switch routes because a shot appears
simple; record any override and its reason.

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

### Reference Routing Contract

The storyboard is a planning and QA artifact, not a video image reference. A
composite six-to-twelve-panel storyboard sheet must not be sent to Kie Seedance
Mini as `reference_image_urls`: schema acceptance does not prove that the model
will treat the sheet as temporal conditioning, and an observed failure rendered
the entire sheet as a tiled video layout. Use the storyboard to create and
approve clean single-scene temporal anchors, then use `first_frame_url` and
`last_frame_url` with no storyboard image reference. A provider-specific adapter
may re-enable sheet references only after a documented live test proves that the
sheet is not reproduced in the output. The pre-video gate must fail closed when
an unverified composite sheet is selected.

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

Before selecting a video model, route every approved shot through the shared
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
reason for routing a shot. The semantic assessment, score, and reasons are
saved with the route decision.

- `0–4`: Seedance 1.5 at 1080p with start/end frames
- `5–7`: manual route review; do not spend generation credits automatically
- `8–20`, or a hard physics trigger: Seedance 2 Mini at 480p with a storyboard/reference image, followed by Topaz 2x upscaling and final FFmpeg scaling to 1920x1080

For the optional Seedance 1.5 fallback, decide whether an end frame is needed before generating it.
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
`route_override: force_simple` or `route_override: force_complex`; the router
records the override rather than hiding it. This router recommends a path only;
it does not call providers, approve paid generation, or replace Tony's review.

The complex route is explicitly `Seedance 2 Mini 480p -> Topaz 2x -> FFmpeg
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

For any controlled storyboard-reference test through Kie, explicitly bind
references by upload order using Kie's playground syntax: the first uploaded
image is `@Image 1`, the second is `@Image 2`, and so forth. Save that mapping
in the generation manifest. This is an
experimental route and must not become the default until manual review confirms
that the provider animates the sequence instead of reproducing the storyboard
layout.

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

- Crop the 16:9 master to 9:16 around the action.
- Use the nearest complete clip boundary.
- Never cut through a clip, action, or narration.
- A Short may end below 60 seconds.
- A Short may exceed 60 seconds when needed to preserve the final complete clip.
- Do not allow narration to cross from one clip into the next.
- Add the opening title overlay only to Shorts.
- Overlay occupies frames 1–30 at 30 FPS.
- Center horizontally, place slightly above vertical center, and respect
  TikTok/Shorts safe padding.
- Do not put the core payoff under the overlay.
- Use Part 1, Part 2, etc. only for the derived Shorts, not the long-form title.

## Final Package and Publishing

Create the long-form title, description, thumbnail, Shorts titles, and report
cards after the final edit is stable. Produce both:

- `Data/Report_Card.md`
- `Data/Report_Card.json`

Wait for Tony's approval of the complete long-form and Shorts package. Only
then use the established Blotato workflow, confirm the Neon Parcel YouTube
account live, set synthetic-media disclosure where applicable, and report the
resulting status.
