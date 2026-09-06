---
title: "Global Director's Packet Framework Plan"
type: architecture-plan
category: architecture
tags:
  - director-packet
  - storyboard-generation
  - visual-continuity
  - ai-video
created: 2026-08-29
status: step-2-complete
scope: global-untethered
---

# Global Director's Packet Framework

## 1. Purpose

Create a global, reusable skill that coordinates detailed visual planning for difficult cinematic scenes. The skill should reproduce the useful underlying workflow demonstrated by OpenArt Smart Shot without depending on OpenArt, copying its branding, or forcing any existing video pipeline to use it.

The framework is intended for long-form, episodic, and cinematic productions where a character may move through different locations, seasons, outfits, props, and camera setups while remaining recognizably consistent.

The first pipeline-specific configuration will eventually be Reimagined Realms, but that connection is explicitly out of scope for this phase.

## 2. Decisions Already Made

- The architecture is global and reusable.
- It remains untethered from all current video pipelines after implementation.
- Each difficult scene receives its own Director's Packet.
- A project may maintain a master character bible across the entire story.
- Scene packets may contain controlled character variations such as wardrobe, season, age, injuries, and props.
- Redundant references are preferred over insufficient references.
- The full packet is the default for complex scenes; components may be omitted only when clearly unnecessary.
- Separate high-resolution assets are retained for downstream generation.
- A combined overview sheet is also generated for human review.
- Approval logic belongs to the consuming video pipeline, not this global skill.
- The skill reports `ready_for_review` or `needs_revision`; it does not decide whether a human must approve.
- Existing project and pipeline behavior must not change merely because this skill exists.

## 3. Non-Goals

- Do not connect this skill to Reimagined Realms, Neon Parcel, Anomalous Wild, or any other pipeline in this phase.
- Do not replace the existing Character Sheet, Environment Sheet, Diagram, Storyboard, GPT Image 2, or Seedance skills.
- Do not create a new video-generation provider integration.
- Do not make OpenArt, Higgsfield, Kie.ai, or any other platform a required dependency.
- Do not copy OpenArt's exact visual branding, fonts, labels, or proprietary UI layout.
- Do not embed human approval rules in the global skill.
- Do not automatically generate video from a packet.

## 4. Conceptual Model

The framework has four layers:

1. **Project Continuity Layer** — the durable master character, prop, environment, and style references for the whole story.
2. **Scene Variant Layer** — controlled changes for the current scene, such as wardrobe, weather, time period, props, injuries, and environment state.
3. **Director's Packet Layer** — a scene-specific visual blueprint combining the references, spatial plan, camera plan, storyboard, and continuity constraints.
4. **Consumer Pipeline Layer** — the pipeline decides whether to review, revise, approve, route, and eventually generate video from the packet.

The global skill owns layers 1–3. A pipeline adapter owns layer 4.

## 5. Director's Packet Contents

Every complex scene should attempt to produce the following package:

### 5.1 Scene Manifest

Machine-readable source of truth containing:

- Project and scene identifiers
- Scene purpose and narrative beat
- Characters present
- Character-bible references used
- Scene-specific wardrobe and appearance changes
- Props present and their continuity state
- Environment, season, time of day, and weather
- Camera positions and intended movements
- Lens and framing requirements
- Lighting, color, and mood
- Required storyboard duration and frame count
- Asset paths and reference ordinals
- Validation findings
- Revision/version history
- Status: `draft`, `needs_revision`, `ready_for_review`, `approved`, or `superseded`

Proposed filename: `Director-Packet-Manifest.json`.

### 5.2 Character References

Use the existing Character-Sheet-Generation skill for the master reference. Add scene-specific reference images when the current scene changes:

- Outfit or armor
- Age, injury, dirt, or weathering
- Hairstyle or makeup
- Held props
- Body position required for the opening or closing beat
- Relationship to another character

The scene variation must link back to the master character identity instead of becoming an unrelated replacement.

### 5.3 Environment Reference

Use the existing Environment-Sheet-Generation skill to establish:

- Location identity
- Architecture, terrain, and materials
- Season and weather
- Time of day
- Light direction and quality
- Important entrances, exits, obstacles, and landmarks
- Objects that must persist between shots

### 5.4 Overhead Spatial and Camera Diagram

Use the existing Diagram-Generation skill to show:

- A top-down view of the set or environment
- Subject and prop positions
- Entrances and exits
- Numbered camera positions
- Camera direction and movement arrows
- Approximate lens/framing notes
- Occlusion, sightline, and continuity risks

The diagram is a spatial planning aid. It is not a substitute for the storyboard or a promise that the video model will reproduce exact geometry.

### 5.5 Storyboard

Use the existing Storyboard-Generation skill to create the scene progression. The storyboard should show:

- A clear beginning, middle, and end state
- Camera/framing changes
- Subject movement and prop state changes
- Scene-specific wardrobe and environment continuity
- Timing or beat labels where the target video model supports them
- Concise action descriptions
- Any required transition or handoff frame

Storyboard examples belong in the global Storyboard-Generation skill's `Examples/Storyboards/` directory. The Director's Packet should link to the active storyboard rather than duplicate it unnecessarily.

### 5.6 Combined Overview Sheet

Create a human-review sheet that summarizes the packet with a clean, readable arrangement:

- Scene title and purpose
- Character/wardrobe reference
- Environment reference
- Overhead camera diagram
- Storyboard sequence
- Palette and lighting notes
- Continuity warnings

This overview is for review and orientation. High-resolution source assets remain separate for generation.

## 6. Workflow

1. Receive a scene description and identify whether the scene is complex enough to justify a full packet.
2. Load the project continuity bible, if one exists.
3. Identify all characters, variants, props, environments, and spatial relationships required by the scene.
4. Generate or reuse master references.
5. Generate scene-specific character, wardrobe, prop, and environment references.
6. Generate the overhead spatial/camera diagram.
7. Generate the storyboard using the references and scene beat list.
8. Assemble the combined overview sheet.
9. Run preflight validation before any video generation.
10. Write the manifest and validation report.
11. Return `ready_for_review` or `needs_revision` to the consuming pipeline.
12. Stop. Video generation and human approval are downstream responsibilities.

## 7. Preflight Validation

The skill should check the packet before returning it:

### Completeness

- Every named recurring character has a master reference or an explicit reason it is not needed.
- Every scene-specific wardrobe or appearance change is represented.
- Important props have a reference and a continuity state.
- The environment reference matches the scene setting.
- The overhead diagram has camera positions for shots that require spatial planning.
- The storyboard has the required number of frames and a clear progression.

### Continuity

- Character identity matches the master bible.
- Wardrobe matches the scene variant.
- Props appear in the correct hands, positions, and states.
- Lighting, weather, time of day, and environment materials agree across assets.
- Camera positions and movement do not contradict the storyboard.
- Scene start and end states are unambiguous.

### Plausibility

- Camera placement is physically possible.
- The proposed lens and framing can capture the described action.
- Subject movement does not require impossible handoffs or hidden operators.
- Props can be manipulated as described.
- The storyboard does not combine too many simultaneous actions into one unclear frame.
- Any difficult physics or state transition is explicitly represented in references or split into smaller beats.

### Generation Readiness

- Reference assets have stable paths and predictable names.
- Reference ordinals are documented before a provider prompt is written.
- The combined sheet is labeled as a visual planning reference, not as footage to imitate literally.
- Provider-specific instructions are deferred to the Seedance or other model skill.

## 8. Versioning and Preservation

The framework must follow the workspace Iteration Archive Rule:

- Never overwrite a packet, manifest, prompt, storyboard, or reference image.
- Superseded artifacts move to the matching project `Archived/` folder.
- The prior version number is preserved.
- The replacement receives the next version number.
- Every packet records its parent version and reason for revision.
- A failed downstream video generation does not erase the packet that produced it.

The global skill may define the metadata and expected archive behavior, but the consuming pipeline supplies the actual project archive location.

## 9. Skill Boundary and Dependencies

The future global skill should orchestrate existing skills through explicit contracts:

- `Character-Sheet-Generation` — recurring identity references
- `Environment-Sheet-Generation` — location and environmental continuity
- `Diagram-Generation` — overhead spatial and camera planning
- `Storyboard-Generation` — sequential scene visualization
- `GPT-Image-2-Prompting-Guide` — still-image prompting conventions
- `Seedance-Prompting-Guide` — provider/model-specific video prompting
- `Visual-Storytelling` — intentional beats and scene structure when useful

The skill should link to these dependencies and pass structured inputs to them. It should not duplicate their detailed prompting rules.

## 10. Pipeline Adapter Contract

Future pipelines may opt in through a small configuration object rather than modifying the global skill. A pipeline adapter should be able to provide:

- Project root and asset directories
- Storyboard template preference
- Character and environment style guidance
- Complexity threshold
- Required validation gates
- Approval mode
- Provider/model capabilities
- Archive location
- Whether the combined overview is shown to the user

The adapter may return commands such as:

- `generate_packet`
- `revise_packet`
- `request_human_review`
- `approve_packet`
- `route_to_generation`

The global skill should not assume any of these commands exist until a pipeline supplies them.

## 11. Proposed File Structure

```text
001_Architecture/Skills/Director-Packet-Framework/
├── SKILL.md
├── references/
│   ├── packet-manifest-schema.md
│   ├── validation-rules.md
│   ├── pipeline-adapter-contract.md
│   └── openart-smart-shot-abstraction.md
├── scripts/
│   ├── build_director_packet.py
│   ├── validate_director_packet.py
│   └── assemble_packet_overview.py
├── templates/
│   ├── Director-Packet-Manifest.json
│   └── Director-Packet-Overview.md
└── evals/
    └── evals.json
```

The exact folder and script names can be adjusted during implementation if existing architecture conventions require it.

## 12. Implementation Phases

### Phase 1 — Skill Skeleton and Contracts

- Create the global skill folder and `SKILL.md`.
- Define trigger language and compatibility requirements.
- Define the manifest schema and status values.
- Document dependencies and pipeline adapter boundaries.

### Phase 2 — Deterministic Packet Assembly

- Build the packet directory scaffold.
- Implement manifest creation.
- Implement asset naming and reference registration.
- Implement combined overview assembly from existing assets.

### Phase 3 — Validation Gates

- Implement completeness, continuity, plausibility, and generation-readiness checks.
- Produce a human-readable validation report.
- Return `ready_for_review` or `needs_revision` without triggering video generation.

### Phase 4 — Skill Evaluation

- Create 2–3 test prompts using different scene complexities.
- Compare output with and without the skill where practical.
- Human-evaluate visual organization and usefulness.
- Revise the skill based on Tony's feedback.

### Phase 5 — First Adapter, Separate Approval

- Only after the global skill is approved, design a Reimagined Realms adapter.
- Keep the adapter in the Reimagined Realms pipeline.
- Do not change other pipelines.

## 13. Acceptance Criteria

The global skill is ready for adapter work when:

- It creates a complete per-scene packet from a structured scene brief.
- Separate assets and a combined overview are both present.
- The manifest identifies every asset and reference relationship.
- Scene-specific wardrobe and environment changes are explicit.
- Camera positions and spatial relationships are represented for complex scenes.
- Validation catches missing references and contradictory continuity.
- The skill does not generate video or enforce pipeline approval.
- The skill can be used without OpenArt or Higgsfield.
- Existing pipeline tests remain unchanged and pass.
- Tony approves the packet organization and review experience.

## 14. Open Decisions for Implementation

- Whether the combined overview should be generated by GPT Image 2, assembled deterministically, or support both modes.
- Whether the spatial camera diagram should be a generated visual, a deterministic diagram, or a hybrid.
- The exact threshold for “complex scene” versus a normal storyboard.
- Whether the manifest should use JSON only or JSON plus a human-readable Markdown report.
- Whether the packet should support multiple storyboard segments when a scene exceeds the provider’s reference or frame limits.
- Which reference asset receives each provider ordinal when a packet is sent downstream.

## 15. Current Status

**Step 2 complete.** The untethered Director's Packet skill and its contracts/scripts now exist. No pipeline has been connected, no video generation has been triggered, and no existing pipeline behavior has been changed. Evaluation and a Reimagined Realms adapter remain later phases.
