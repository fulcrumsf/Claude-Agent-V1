---
title: "Iterative AI Production Framework"
type: architecture-spec
category: agent-workflows
tags:
  - ai-production
  - iterative-development
  - human-in-the-loop
  - autonomous-agents
  - workflow-design
status: working-framework
created: 2026-08-29
source: "Validated patterns from Agent-OS video pipeline development"
---

# Iterative AI Production Framework

## Purpose

This framework defines how to build, test, improve, and eventually automate AI production pipelines across Agent-OS. It is intentionally channel-agnostic. A channel pipeline owns its content, style, tools, and output rules; this framework explains the disciplined process used to make that pipeline reliable.

The goal is not to pretend that the first design is correct. The goal is to create a system that can learn from real outputs, preserve what works, isolate what fails, and gradually earn autonomy through evidence.

## Core Principle

**Build -> test -> observe -> diagnose -> change the smallest necessary thing -> test again.**

Every production framework is a hypothesis until it has produced real output and passed review. Prompts, storyboards, model routes, scripts, folder structures, and automation logic should be treated as versioned working material rather than permanent truth.

Iteration is not a sign that the system failed. Iteration is the mechanism by which the system becomes dependable.

## Intentionality Rule

Every step, artifact, prompt instruction, model choice, gate, narration line, camera choice, transition, and sound should have a purpose. Use a tool because it solves the current problem, not because it is available or was useful in another pipeline.

Do not use a generic framework as a substitute for judgment. A hammer is not the right tool for every fastener; similarly, a storytelling pattern, image model, storyboard, voice layer, or approval gate should be selected based on the work required.

## Separation of Responsibilities

Keep these layers distinct:

1. **Global knowledge:** reusable principles, prompting practices, storytelling patterns, QA methods, and iteration rules.
2. **Pipeline orchestration:** the order of phases, pauses, routing decisions, and project-specific defaults.
3. **Tool skills:** how to use a provider, API, model, editor, or analysis tool correctly.
4. **Production artifacts:** prompts, references, renders, metadata, scripts, reports, and final media.
5. **Feedback and learning:** what was approved, rejected, misunderstood, or repeatedly successful.

An update belongs in the smallest layer that can solve the problem. Do not change a global skill to fix a channel-specific preference. Do not change a pipeline to compensate for a provider limitation that belongs in a tool skill or router.

## The Iteration Loop

### 1. Define the intended result

Write down what the output should do, not merely what it should contain. Include:

- The viewer or user experience desired
- The content or action that must be visible
- The style and capture context
- Technical output requirements
- What must not change
- The approval standard

For visual media, describe the expected result in observable terms. "Looks real" is incomplete; specify the plausible camera source, lighting, composition, motion, physical actions, audio, and outcome.

### 2. Build the smallest useful test

Start with a narrow test that can answer one important question. Examples:

- Can the model preserve a camera angle?
- Can it perform the physical action in the correct order?
- Does the storyboard communicate the transition?
- Does the chosen resolution provide acceptable detail?
- Does the editing rule preserve a complete scene boundary?

Do not spend the cost of a full production before the riskiest assumption has been tested.

### 3. Save the inputs before execution

Before any paid or irreversible provider call, save the exact:

- Prompt
- Model, version, provider, resolution, and duration
- Reference images, storyboard, and source URLs
- Tool parameters
- Intended output path
- Current artifact version

This makes the result auditable and prevents a failed output from becoming impossible to explain or reproduce.

### 4. Execute once per version

Submit a prompt only once for a given artifact version unless one of these conditions applies:

- The provider returns a genuine failure
- The output is corrupt or unusable due to a technical error
- The user explicitly requests a revision
- The approved workflow authorizes a documented retry

Do not silently resubmit because the result is disappointing. A disappointing result is evidence for diagnosis, not permission to spend again.

### 5. Review the result as a whole

Check both literal compliance and overall plausibility:

- Did the requested elements appear?
- Does the complete result make sense as a real scene or usable artifact?
- Is the camera physically plausible for the claimed capture source?
- Are object positions, body mechanics, timing, and cause-and-effect coherent?
- Does the result preserve the intended tone rather than merely following words?

For video, review the actual motion over time. For storyboards, review frame-to-frame continuity. For audio, review timing, intelligibility, tone, and whether it belongs to the visible event.

### 6. Diagnose the failure precisely

Classify the failure before changing anything:

- **Input problem:** the concept or reference was underspecified or contradictory.
- **Prompt problem:** the instruction was ambiguous, overloaded, or incorrectly structured.
- **Reference problem:** the image, storyboard, or end frame introduced confusion.
- **Model limitation:** the model cannot reliably perform the requested action.
- **Routing problem:** the task was sent to the wrong model, resolution, or tool.
- **Pipeline problem:** the phase order, artifact handoff, or guardrail was wrong.
- **Review problem:** the output passed a superficial check but failed whole-scene plausibility.

Record what actually failed. Do not describe a prompt failure as a model failure without evidence, and do not describe a model failure as a prompt failure merely because another prompt might work.

### 7. Change one meaningful variable

Preserve all parts that were working and change only the smallest necessary part. A revision might change:

- One action or action order
- One ambiguous sentence
- One reference image or end frame
- One camera instruction
- One model or resolution
- One duration or trim point

When several variables must change, make the reason explicit. Otherwise the next result cannot teach us what caused the improvement.

### 8. Re-test and compare

Compare the new version against both the intended result and the previous version. Record:

- What improved
- What regressed
- What remained unchanged
- Whether the original failure was solved
- Whether the result is good enough to advance

Do not keep iterating indefinitely on a low-value problem. Use a cheaper test, simplify the action, change the route, or accept the best available result when the user approves that tradeoff.

## Human Review and Approval

Human review is a calibration phase, not a permanent requirement for every future run. During calibration, the user may approve, reject, score, or critique outputs at any stage:

- Concept
- Storyline or beat structure
- Shot list
- Reference image or storyboard
- First generated clip
- Batch of generated clips
- Rough cut
- Final video package

The agent should ask for the smallest review that resolves the current uncertainty. If the user approves a batch, do not create unnecessary per-item approval gates. If the user requests one-by-one review for a risky step, honor that checkpoint.

Approval must be recorded with the artifact version and, when useful, the reason. A score is useful calibration data, but a score without a reason should not be treated as a complete rule.

## Non-Destructive Versioning

Never delete or overwrite a superseded artifact. When an iteration is rejected or replaced:

1. Move the old artifact into the matching `Archived/` folder.
2. Preserve its original version number.
3. Assign the replacement the next version number.
4. Keep the exact prompt, references, parameters, and review note with the version.
5. Keep active folders limited to current working or approved artifacts.

This applies to prompts, scripts, shot lists, storyboards, images, audio, video, metadata, reports, and configuration files.

## Learning Loop

Feedback should become useful knowledge at the right level:

- **Session log:** what happened and what remains.
- **Feedback log:** a correction, preference, or validated approach.
- **Self-learning review:** recurring patterns and possible automation.
- **Global skill:** a confirmed rule that applies across projects.
- **Pipeline skill:** a channel or format-specific rule.
- **Case study library:** observed patterns from reference work, separated from invented recommendations.

Do not promote a single failed experiment into a universal rule. A finding becomes a candidate rule when it is clear, repeatable, and useful. The user approves changes to active skills or pipeline behavior when the change could affect future work.

## From Manual to Autonomous

Autonomy should be earned in stages:

1. **Manual:** the agent proposes each major decision and waits for approval.
2. **Guided:** the agent executes low-risk steps but pauses at defined gates.
3. **Batch-approved:** the user approves a group after reviewing representative outputs.
4. **Supervised autonomous:** the agent runs within locked rules and reports exceptions.
5. **Autonomous:** the agent runs routine work and escalates only when a gate fails, confidence is low, or a rule is missing.

A user saying a pipeline is "95% ready" is a calibration signal, not an automatic command to enter autonomous mode. The user decides when the operating mode changes.

## Quality Gates Before Expensive Work

Place cheap checks before paid or difficult-to-reverse steps:

- Validate the concept and intended beat.
- Check realism, physical plausibility, and camera plausibility.
- Inspect reference images and storyboards for ambiguity.
- Confirm the model and resolution match the task.
- Confirm the prompt is saved and the version is new.
- Confirm the provider task has not already been submitted for that version.
- Confirm the output route and archival behavior.

Quality gates should catch preventable errors, not attempt to guarantee subjective creative success.

## Reporting Template

Each meaningful iteration should be explainable in this compact form:

```text
Artifact: [name and version]
Intent: [what this test was meant to prove]
Inputs: [prompt, references, model, provider, parameters]
Result: [what happened]
Assessment: [pass, fail, or conditional pass]
Failure or success reason: [specific observation]
Change for next version: [smallest justified change]
Approval: [person, date, score if provided]
Archive action: [old version moved where, if applicable]
```

## Future Productization

Keep this framework implementation-independent so it can later become:

- A global Agent-OS skill
- A pipeline design template
- A production checklist
- A training playbook for other agents
- A sellable AI production systems guide

Before turning it into a product, remove private paths, channel-specific names, credentials, and internal assumptions. Keep the underlying principles, decision tables, examples, and reusable templates.

## Current Scope and Non-Goals

This document currently defines the method for building and improving production frameworks. It does not:

- Replace any channel pipeline
- Select a specific video or image provider
- Guarantee that an AI model understands humor or physics
- Automatically activate learned rules
- Replace human approval during calibration
- Define a single storytelling formula for every project

Those decisions belong to the relevant pipeline, tool skill, router, or approved future version of this framework.
