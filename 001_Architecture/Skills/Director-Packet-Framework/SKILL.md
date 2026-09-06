---
name: director-packet-framework
description: Use when a complex cinematic, episodic, or long-form scene needs coordinated character, wardrobe, prop, environment, spatial camera, and storyboard references before video generation. This global skill creates a per-scene Director's Packet from existing specialized skills, validates continuity and plausibility, and stops at a review-ready handoff. It is intentionally untethered: never invoke a video pipeline, provider, or approval process unless a consuming pipeline explicitly supplies an adapter.
compatibility: Python 3.10+, Pillow optional for overview images; existing Agent-OS character, environment, diagram, storyboard, GPT Image 2, Seedance, and visual-storytelling skills.
---

# Director's Packet Framework

This is a global orchestration skill for difficult scenes. It coordinates references the way a film continuity department would: identity, wardrobe, props, environment, spatial layout, camera, lighting, and shot progression are recorded before expensive video generation.

## Boundary

The skill owns packet creation and preflight validation. The consuming video pipeline owns human approval, revision decisions, provider routing, video generation, publishing, and project-specific archive paths. This skill must not silently change or trigger any existing pipeline.

## When to Use It

Use a full packet when a scene has several of these characteristics:

- A recurring character changes outfit, age, weathering, or props.
- A character moves through a new location, season, time of day, or weather state.
- Multiple characters or props must occupy specific spatial relationships.
- The scene requires several camera positions, lens choices, or sightlines.
- Physical action, entrances/exits, object states, or continuity handoffs are difficult to explain in text alone.
- A single storyboard would otherwise leave the model to infer too much.

Do not force a full packet for a simple, one-off shot. The caller may request a reduced packet, but the default for a complex scene is the complete packet.

## Required Inputs

Accept a scene specification as JSON. See [`references/packet-manifest-schema.md`](references/packet-manifest-schema.md). At minimum it should include:

- `project_id`, `scene_id`, `scene_purpose`
- `characters`, `wardrobe_changes`, `props`, and `environment`
- `beats` or a storyboard action list
- `visual_style`, `duration_s`, and any known camera requirements
- `output_root` supplied by the consuming project

Existing reference paths may be supplied. The framework records them; it does not regenerate an existing asset merely because it is present.

## Workflow

1. Read the scene specification and identify every subject, variant, prop, location, camera, and state transition.
2. Load the master continuity references when available.
3. Plan scene-specific references for wardrobe, props, environment, and opening/closing states.
4. Delegate asset generation to the relevant specialized skill rather than duplicating its prompting rules.
5. Register every asset with a stable path, semantic role, version, and reference ordinal.
6. Create or register the overhead spatial/camera diagram.
7. Create or register the storyboard using the active project's storyboard template.
8. Assemble a combined overview for human orientation while preserving separate high-resolution assets.
9. Run the preflight validator.
10. Return a manifest, validation report, and status: `ready_for_review` or `needs_revision`.
11. Stop. Do not generate video or decide approval.

## Packet Contents

The normal packet contains:

- `Director-Packet-Manifest.json` — machine-readable source of truth
- `Scene-Brief.md` — concise purpose, characters, environment, and intended action
- `References/Characters/` — master and scene-specific identity/wardrobe references
- `References/Props/` — important object references and state notes
- `References/Environment/` — location, season, weather, and lighting references
- `Diagrams/Overhead-Camera-Plan.*` — spatial layout, camera positions, and sightlines
- `Storyboards/` — scene storyboard(s)
- `Director-Packet-Overview.md` — human-readable overview
- `Director-Packet-Overview.png` — optional contact-sheet overview when Pillow is available
- `Validation-Report.md` — completeness, continuity, plausibility, and readiness checks

## Reference Roles

Keep the roles distinct even when one image serves more than one purpose:

- `master_character` — identity that persists across scenes
- `scene_character_variant` — controlled outfit, age, injury, weathering, or pose change
- `prop_reference` — object appearance and state
- `environment_reference` — location appearance and conditions
- `overhead_camera_plan` — spatial relationships and camera geometry
- `storyboard` — sequential visual beats
- `combined_overview` — review-only summary of the packet

Do not treat a storyboard as a character sheet, an overhead plan as footage, or a combined overview as the highest-resolution generation reference.

## Preflight Rules

The validator must check:

- Every named recurring character has a master or explicitly waived reference.
- Every material wardrobe, prop, environment, or state change is represented.
- The environment, time, weather, and lighting agree across the packet.
- Camera positions can plausibly see the described action.
- Props can be manipulated as described and do not teleport between beats.
- The storyboard has a readable beginning, progression, and ending state.
- Difficult physical transitions are split into smaller beats or explicitly shown.
- Reference paths exist and reference ordinals are unique and documented.
- The packet is versioned and no existing artifact is overwritten.

Warnings may return `ready_for_review` only when they are non-blocking and clearly listed. Missing required references, contradictory continuity, invalid paths, or physically impossible camera/action combinations return `needs_revision`.

## Versioning

Never overwrite a packet or its assets. The consuming project supplies its archive location. Superseded packets and assets move to the matching `Archived/` folder, retain their original version number, and receive a replacement version. The manifest records `parent_version`, `revision_reason`, and `status`.

## Dependencies

Read these only as needed:

- [`Character-Sheet-Generation`](../Character-Sheet-Generation/SKILL.md)
- [`Environment-Sheet-Generation`](../Environment-Sheet-Generation/SKILL.md)
- [`Prop-Sheet-Generation`](../Prop-Sheet-Generation/SKILL.md)
- [`Diagram-Generation`](../Diagram-Generation/SKILL.md)
- [`Storyboard-Generation`](../Storyboard-Generation/SKILL.md)
- [`GPT-Image-2-Prompting-Guide`](../GPT-Image-2-Prompting-Guide/SKILL.md)
- [`Seedance-Prompting-Guide`](../Seedance-Prompting-Guide/SKILL.md)
- [`Visual-Storytelling`](../Visual-Storytelling/SKILL.md)

Provider-specific reference semantics belong in the provider skill. The packet records ordinals and roles but does not assume that every provider supports every reference type.

## Commands

Scaffold and validate a packet without invoking a video pipeline:

```bash
python3 scripts/build_director_packet.py scene.json --out /path/to/packet
python3 scripts/validate_director_packet.py /path/to/packet/Director-Packet-Manifest.json
python3 scripts/assemble_packet_overview.py /path/to/packet/Director-Packet-Manifest.json
```

## Future Pipeline Adapters

A future adapter may provide project paths, style guidance, packet complexity thresholds, approval mode, provider capabilities, and archive rules. The adapter must explicitly call this skill; the global skill must not auto-discover or modify pipelines.

## Current Status

This skill is global and untethered. It is not connected to Reimagined Realms, Neon Parcel, Anomalous Wild, or any other pipeline. Evaluation and a Reimagined Realms adapter are later phases.
