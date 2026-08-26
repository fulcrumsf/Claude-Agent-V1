# Anomalous Wild Pipeline — Improvements To-Do

Running notes from the 2026-08-24 retrospective on the Mantis Shrimp Color Vision production (0002). Not yet actioned — capture only.

## Intake / new_video.py

- **Duration question was skipped in production.** `new_video.py`'s questionnaire always asks "Estimated duration?" — nothing in the script skips it. It didn't get asked during the Mantis Shrimp run because the orchestrating agent (Claude) didn't actually run the real intake script/flow. Need to make sure future runs go through the real questionnaire, not an ad-hoc substitute.
- **"Which channel is this video for?" question is dead/misleading.** The script only actually works for Anomalous Wild (output folders for other channels don't exist, Reimagined Realms has its own separate toolset). Either remove this question, or actually wire it up to support multiple channels.
- No fixed target duration is enforced anywhere — the intake duration pick is just a stored label. Runtime is emergent (measured after voiceover/beat table are built), not planned toward the user's pick. Worth deciding if this is fine or if it should be enforced/checked against later.

### DECIDED (2026-08-24 retrospective) — not yet implemented

- **Narration**: remove "Include voiceover narration?" question — Anomalous Wild is always narrated, assume yes.
- **Voice**: lock ElevenLabs voice ID `KYhuk3Y57IlkV1ZjtDAt` as the permanent, hardcoded Anomalous Wild voice for every video (same treatment as Reimagined Realms' hardcoded voice). Remove "Voiceover tone?" question — no longer needed once voice is fixed. To change the voice in the future, hardcode the change explicitly (not via a per-run question).
- **Music mood**: remove "Music mood?" question entirely. Never locked to a single mood — mood is derived from the script's tone during editing (video editor's call), not selected by Tony at intake.
- **Suno score**: remove "Generate a Suno score?" question — always on by default. Tony will explicitly say if he wants it skipped for a given video.
- **CTA**: remove "What should viewers do at the end? (CTA)" text question. Replace with 3 rotating lines, picked at random per production (must stay under ~10s spoken, ~25 words max at 150 wpm):
  1. "Subscribe for more wild animal facts."
  2. "Follow along for more strange creatures like this one."
  3. "Hit subscribe — nature gets weirder from here."

### Resulting questionnaire (once implemented)

Only two questions remain:
- Format? — Long-form (16:9) or Short (9:16)
- Estimated duration? — 3–5 min / 5–8 min / 8–12 min, or <30s / 30–60s for Shorts

Everything else (channel, narration, voice, voice tone, music mood, Suno, CTA) becomes fixed/automatic.

## Continuity/anatomy flagging (2026-08-25 retrospective)

- **The flagging itself is unreliable.** In this case Tony reviewed the flagged claw-continuity issue and couldn't actually see the discrepancy the AI described — the video-review pass sometimes gets its own flags wrong / points at something that isn't really there. Not fully solved yet — noted as an open reliability problem with the automated video-review step, not something to fix today.
- **DECIDED — cost-control rule for flagged issues**: when a continuity/anatomy issue is flagged (real or not), the pipeline must NOT automatically regenerate the clip via Seedance to try to fix it — that wastes money on a re-render for something that may not even need fixing. Instead: leave the clip as-is, log the flag in a report, and let Tony review it later.
- **Overall approach for this training phase**: Tony expects to run ~15 more videos through this pipeline reviewing flags like this each time; once the pipeline reaches near-error-free or the kinks are worked out, this level of per-flag human approval goes away. This is consistent with the broader autonomy goal already noted for #20 (mockup review) — Tony is dialing in the pipeline now specifically so approval isn't needed later.

## Visual variety (standing rule, 2026-08-24/25 retrospective)

- **DECIDED — not a one-off.** Scenes were looking too similar to each other (framing, character position, environment, lighting) — repetitive, reads as "AI slop," boring even though the finished video graded well overall.
- **Rule going forward**: introduce deliberate visual variety between scenes/shots — vary lighting, water clarity/environment, color grade, and where reasonable framing/composition and camera-lens "feel" — the way a real documentary mixes footage types. Do NOT achieve variety by recoloring the creature/character itself (see #10 in iteration log — no biological basis for that); vary the environment and treatment around it instead.
- **Reference example of what "good variety" looks like**: the three pre-text thumbnail concepts generated during this same production — each had its own distinct style/twist while staying on-brand. That's the target quality bar for variety.
- **Extend to character sheets too**: current character sheets show the same character from different angles but in one uniform style throughout. Consider generating variant style sheets (different lighting/treatment per style) so shots pulling from the sheet can carry that same variety, rather than every shot referencing one uniform-look sheet.
- Needs a concrete mechanism (not just a vibe instruction) — e.g. an explicit variety checklist per scene, or a step that compares planned shots against each other and flags visual repetition before generation. Not yet designed.

### Visual variety mechanism — DESIGN (2026-08-25, finalized in brainstorm)

Root cause suspected: repeated/similar prompt language being fed to generation models (e.g. GPT-Image-2) across shots in the same production, likely from templated prompting.

Two-tier mechanism:

1. **Fixed universal pool** (applies to any creature/subject, same list every production):
   - Camera angle / shot type: wide, close-up, medium shot, low angle, high angle, macro. (Dropped "over-the-shoulder" — doesn't translate to non-human subjects.)
   - Framing/composition: centered/symmetrical, rule-of-thirds off-center, negative-space-heavy, tight/filled frame, depth-layered foreground.
   - Rotate through these across shots within a production — don't reuse the same angle/framing combo back-to-back.

2. **Director's own research-driven judgment** (NOT a fixed list, decided per-production by the agent):
   - Environment specifics (region/reef/habitat — driven by where the real subject actually lives)
   - Lighting/weather/time-of-day (driven by what's realistic for that environment)
   - Subject natural variation (real color/pattern variation within the species, if factually accurate)
   - Sourced from the Production-Research-Agent step (real-world facts gathered before scriptwriting) — this is "smart" variety grounded in research, not arbitrary randomization.

**Autonomy framing**: Tony does not want to hand-pick variety himself — the agent should act as the director/cinematographer (explicit persona: BBC-style nature documentary director), making these calls independently. Tony reviews finished videos to fine-tune the director's "eye" over iterations, not to approve variety choices shot-by-shot.

**RESOLVED (2026-08-25, follow-up check)**: Confirmed the same "exists but not wired in" pattern found elsewhere in this retrospective.
- Case studies exist and are real (6 for AW, in `Case_Studies/`, built via the Video-Analyzer skill) — including a BBC Earth-style mantis shrimp case study.
- AW's `SKILL.md` (line 33) DOES point to Case_Studies — but only during Phase 1 topic research/ideation, not for shot composition.
- A separate, more detailed **Cinematic Style Guide** exists (`002_Content-Creation/Video_Editor/002_Channels/Styles/CINEMATIC_STYLE_GUIDE.md`) with a dedicated "Wildlife" style (shallow DOF, warm grading, "beauty shot" rules, explicitly citing BBC Blue Planet II and one of AW's own case studies) — but the AW pipeline **never invokes it anywhere**, zero references in SKILL.md or the scriptwriter skill.
- Instead, AW's current shot-composition rules (SKILL.md line 156: change composition every ~3s, no single feature >50% of frame, correct limb counts) are self-authored inline, not sourced from either the case studies' actual cinematography or the Wildlife style guide.
- **Action for the plan**: wire the director persona/mechanism above to explicitly invoke `CINEMATIC_STYLE_GUIDE.md`'s Wildlife style AND reference the Case_Studies folder's actual shot examples (not just for topic ideation) — this closes a second contributing cause of the sameness problem, on top of the prompt-repetition root cause.
- Video-Analyzer skill (`001_Architecture/Skills/Video-Analyzer/`) is the general-purpose tool that already extracts/analyzes visual assets from reference videos (Gemini narrative analysis + Whisper transcript + keyframes) — this is what built the case studies; no separate ingestion skill is needed, this one already does it.

### Clarification (2026-08-25): case studies are inspiration/craft lessons, NOT a copy template

- Case studies exist to teach the director HOW good documentaries tell stories through editing, shot selection, and shot generation — not to be mimicked shot-for-shot.
- Scope is broader than shot composition alone. The director should be pulling craft lessons from case studies into every stage that shapes storytelling, including:
  - Beat sheet construction
  - Pacing/timing
  - Shot selection
  - Research direction
  - Pexels B-roll selection
  - Diagram creation
  - Asset creation generally
- **Mechanism**: the director reads/studies the case studies, extracts the underlying craft lessons, and that learning should propagate into updates to the relevant skills themselves (scriptwriter skill, research skill, diagram/asset-generation skill, etc.) — not just be re-read fresh each production as passive reference material. This is a "study once, internalize into the skill set" model, not "look up whenever."
- This significantly broadens the earlier visual-variety mechanism item — it's really one instance of a general rule: case-study-derived craft lessons should be baked into the skills that do the work, across the whole pipeline, not siloed to topic ideation or to camera angles alone.

## NotebookLM integration (2026-08-25)

- **Verified: NOT implemented anywhere.** Zero references in `Anomalous_Wild_Video_Pipeline/SKILL.md` or `Production-Research-Agent/SKILL.md`. Nothing in the Mantis Shrimp Research folder was generated by it. Was discussed in a past session but never actually wired in.
- **Capability correction**: NotebookLM does NOT generate diagrams or diagram videos — that was a misremembering. It actually produces: audio overviews/podcasts, text reports (briefing docs/study guides/blog posts), and "mind maps" (JSON hierarchy data, not a rendered image). The diagram approval Tony recalled was from a different system (Motion-Graphics-Compositing), not NotebookLM.
- **Correction (2026-08-25, Tony checked live product)**: NotebookLM's actual current capability set is broader than the `notebooklm` skill's SKILL.md reflects — it can now generate slide decks, video overviews, audio overviews, mind maps, infographics, data tables, flashcards, and reports. The skill doc is likely stale (same "docs lag behind reality" pattern found repeatedly this session) — **action item: update `001_Architecture/Skills/notebooklm/SKILL.md` to reflect the full current feature set** before building on it.
- **DECIDED direction (revised)**: NotebookLM strengthens TWO phases, not just research:
  1. **Research phase** — reports, data tables, mind maps synthesized from gathered sources, added to existing research material (Topic_Facts.md, Pexels inventory, reference images).
  2. **Diagram/asset-building phase** — infographics (exportable as images) and slide decks/video overviews (which can contain diagram-like visuals) can serve as raw material/inspiration for the animated diagram and motion-graphics asset pipeline, not just static research reference.
  - Framed as "more grounding material and more raw asset material up front is better," not mandatory-forced-use on every production — still needs a concrete implementation spec (where in Phase 1/Production-Research-Agent, and where in diagram/asset generation, it plugs in).

## Technical context: how video clips actually get generated (2026-08-25, for the eventual plan)

Provided by Tony so the implementation plan respects the real order/dependencies of the current asset pipeline:

- **Reference sheets are generated first, deterministically**: character sheets, environment sheets, and (rarely) prop sheets. Prop sheets are almost never needed for this channel — it's animal subjects, and most animals don't interact with distinct enough objects to warrant one (e.g. an otter juggling a rock isn't special enough to need a prop sheet).
- **Storyboards come next**, built per scene — sometimes multiple storyboards for one scene if it's complex enough that a single clip can't cover it; it gets broken into more digestible pieces instead.
- **Each storyboard produces a start image and an end image** (via GPT-Image-2, using the storyboard as reference) for that clip.
- **Seedance 1.5 Pro** (current default) only accepts 2 image references — used as start frame + end frame. This is a deliberate cost-saving choice, not a capability ceiling being hit.
- **Seedance 2.0** accepts up to 8 image inputs (character sheets, environment sheets, etc. directly, not just start/end frames) — reserved for when cost allows, or a future default if 1.5-style savings aren't available anymore (possibly Seedance 2.5 by then).
- **Implication for the plan**: any changes to character-sheet variety, environment-sheet variety, or reference-asset generation need to respect this ordering (sheets → storyboards → start/end frame images → video gen) and the current 2-image-input constraint of the default model (1.5 Pro) versus the richer multi-image capability of 2.0/future models.

## Character sheet variety (2026-08-25)

- **DECIDED**: generate multiple character-sheet variants per production (different environments/lighting treatments), not one uniform-style sheet.
- **Real-world justification found in this production**: one shot was actually built from a liked Pexels reference image of the mantis shrimp instead of the character sheet, specifically because it looked different/better than the single-style sheet could produce. More reference variety up front (character sheet variants, B-roll, research assets) directly gives the director better raw material — same principle as the visual-variety mechanism and NotebookLM decision above. All three items are really the same underlying idea: more grounded, varied reference material in → better, less repetitive output out.

## Character sheets

- Verified: a character sheet WAS generated for Mantis Shrimp (`Character_Sheets/Mantis_Shrimp_Main_Character_Sheet.png`). No gap in practice.
- Gap found: `Anomalous_Wild_Video_Pipeline/SKILL.md` never explicitly invokes the `Character-Sheet-Generation` skill by name — it re-describes character-sheet rules inline across several phases instead. Should be changed to directly invoke the skill so the two don't drift out of sync as the skill gets refined independently.

## SKILL.md documentation gaps

- SKILL.md's PHASE 1 INTAKE section doesn't enumerate the actual questionnaire (channel, format, duration, voiceover, tone, music mood, Suno, CTA) — it just says "runs the interactive questionnaire." Should be made explicit so it's clear what's supposed to happen.
- SKILL.md references a "Seedance vs Veo" video-model-family question that doesn't exist in `new_video.py` at all — asked separately by the orchestrating agent. Mismatch between documented flow and actual code.

## Thumbnail pipeline (from earlier same-day work, for context)

- PIL-based text/arrow overlays failed — replaced with GPT-Image-2 image-to-image edits (already fixed, template v2 locked).
- Brand style JSON template existed but was never read by the generator script until manually caught — now wired in.

## Broader pipeline discrepancies (found in follow-up audit, 2026-08-24)

- **Video model default is documented as Seedance but code only ever calls Kling or Veo.** `pipeline_supervisor.py` has zero Seedance/Bytedance references — any beat defaulted to "Seedance" silently ran through Kling instead.
  - **DECIDED**: Seedance 1.5 Pro (1080p) via kie.ai is the real, locked default video engine — always used unless told otherwise. Needs to be actually wired into `pipeline_supervisor.py` (currently isn't).
  - **Clarified 2026-08-25**: there is no fixed backup chain (e.g. "Seedance 2.0 as backup, then Veo3 as fail-safe") — that was never actually locked in. Instead, switch to a different model as needed/on the fly, decided in the moment, not via a pre-set fallback order.
  - Context: item #18 in the iteration log (Seedance 2.0 vs 1.5 Pro comparison, picked 2.0) was confirmed a one-off — those were manual one-off redos of specific scene clips Tony didn't like from the original pass, not a pipeline default change. 1.5 Pro remains the default.
- **Remotion assembly (documented Phase 7) didn't run for the Mantis Shrimp production.** Explanation from Tony: the pipeline was being iterated live during that production — diagrams were generated as component assets and likely stitched together with ffmpeg instead of going through a Remotion `.tsx` composition.
  - **DECIDED**: No single tool (Remotion, video-use, HyperFrames, ffmpeg) is the mandatory default final assembler/compiler. Whichever tool is best suited for a given job does that job — e.g. diagram scenes get compiled with specialized tools (component assets, alpha channels, layer/fade control via a "manager" that decides what goes into the animated diagram), independently of how other scenes are built. Everything gets stitched together into the final video afterward regardless of which tool(s) built which pieces. SKILL.md's Phase 7 "mandatory Remotion master composition" requirement should be updated/retired to reflect this — Remotion is *a* tool, not *the* tool.
  - Separately: `compose_audio.py` in the AnomalousWild codebase still has leftover "Reimagined Realms" naming/references copied from that channel's code — should be cleaned up (unrelated to the above; confirmed as an actual code-hygiene issue, not just a naming slip).
- **Pexels attribution missing from YouTube description is NOT a bug.** Clarified: the researcher always downloads Pexels footage candidates for reference, but nothing is automatically used — Tony manually reviewed and rejected the two Pexels clips the pipeline had placed because they didn't look good / didn't fit. Attribution correctly wasn't needed because the footage wasn't actually used. No fix needed here, just confirms the "mandatory Attributions section" language in SKILL.md should be conditional on actual usage, not assumed.
- **Diagram labeling method changed mid-production, and the old documented method needs to be retired, not left standing.** What happened: label coordinates were initially estimated and came out wrong (overlapping, misplaced) using the documented coordinate-detection → Remotion-labels method. The agent identified a better approach (Motion-Graphics-Compositing / component assets) mid-iteration, Tony approved it, and it was used instead — but the SKILL.md/DESIGN.md docs were never updated to make the new method the standard and retire the old one.
  - **STANDING PROCESS RULE going forward**: when an agent finds a better way to do something mid-task and Tony approves the change, that approval means the new way REPLACES the old documented method as the standard — not just a one-off exception. The old method should be removed/marked superseded in the docs at that point, not left as the "official" process while the real process quietly diverges.
  - **Refinement**: the agent should not assume this on its own. When a mid-task method change happens, explicitly ask Tony: "We changed the way we did X — do you want this new approach locked in as the standard for the pipeline going forward?" Let Tony decide per-case rather than silently either locking it in or leaving it undocumented.
- **Static mockup-before-render step (labeling/overlay placement) is a temporary training step, NOT a permanent pipeline gate.** Purpose: let Tony safely watch and correct the coordinate-placement *method* until it's reliable, then lock in the corrected method and retire the manual review step itself. The end state is full autonomy on this step — Tony should not need to approve mockups indefinitely. Applies once the corrected method (component-asset + manager approach from the Remotion decision above) proves reliable without guessing coordinates.
- **Audio mix levels: intent was "set it like a professional video editor would," not a specific numeric target Tony dictated.** Tony's actual instruction was for narration, Suno music, and Seedance-generated ambient noise to be balanced at levels a real video editor would use (proper relative dB/LUFS relationships) — not to hit an arbitrary number pulled from nowhere. Separately, there's a stray internal inconsistency worth fixing: `analyze_stems.py`'s docstring says -28 LUFS for music while the actual render pipeline (`render_outputs.py`) locks -26 LUFS. Should reconcile to one number grounded in real audio-engineering/broadcast standards, and confirm it actually matches "how a professional video editor would set it."
