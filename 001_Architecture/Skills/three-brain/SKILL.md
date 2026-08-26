---
name: three-brain
description: "Three-Brain Auto-Router — intelligently routes tasks across Claude (orchestrator/builder), OpenAI Codex (reviewer/rescue), and Gemini (video/audio/PDF/long-context). Invoke this skill whenever: a task involves video files, audio files, or large PDFs; Claude has failed to solve something more than twice; the user asks for a code review, adversarial review, or second opinion; the user says \"ask all three\" or wants parallel model consensus; a handoff to another model is needed for any reason. Claude is always the conductor — it announces every handoff, logs it, and interprets the result. Large delegated output is persisted to disk and returned to Claude as a concise summary, not dumped inline. This skill should be active in every session across all departments."
---

# Three-Brain Auto-Router

Claude is the conductor. Every task starts here. Claude decides which brain handles what, announces every handoff out loud, logs it, and synthesizes the result. Delegated work happens outside Claude — but what crosses back *into* Claude's active conversation is a separate cost Claude must manage deliberately. That's the point of everything below.

---

## Token Economy — Which Brain Saves What

Delegating work to Codex or Gemini can preserve Claude's inference capacity — those models do the thinking, not Claude. But delegation is **not automatically free to Claude**. Constructing the handoff, receiving the response, interpreting it, and carrying it forward in conversation history all cost Claude context and quota. A task routed externally is only cheap to Claude if what comes back stays small.

So there are two separate costs, and only one of them is what "routing to Codex/Gemini" actually saves:

- **Delegated inference cost** — the work Codex/Gemini does. This is what routing saves Claude from doing itself.
- **Claude parent-context cost** — the tokens spent building the handoff and, especially, absorbing the result. This is **not** automatically saved just because the work was delegated. It's saved by keeping handoffs and returns concise (see Progressive Disclosure below).

| Task type | Brain | Delegated inference | Claude parent-context cost |
|-----------|-------|---------------------|------------------------------|
| Simple questions, quick lookups | Codex | Offloaded | Minimal — small in, small out |
| Code review, adversarial, rescue | Codex | Offloaded | Low if summary-only; high if full diagnostics pasted back |
| Video, audio, PDF, long-context | Gemini | Offloaded | Low if summary-only; high if full transcript/report pasted back |
| Planning, writing, creative, orchestration | Claude Sonnet | N/A — Claude does it | Full cost, done by Claude directly |
| Heavy builds, complex reasoning | Claude Sonnet | N/A | Full cost |
| Opus | Only if Tony explicitly asks | — | High — avoid by default |

**Default model:** Sonnet 4.6. Never escalate to Opus unless Tony requests it.

**The rule that actually matters:** keep delegated *returns* concise by default (see Progressive Disclosure). That's what makes delegation cheap for Claude — not the act of delegating itself.

---

## The Three Brains

### Brain 1 — Claude Sonnet (You)
**Role:** Orchestrator, IDE, primary builder
**Handles:** Planning, writing, creative work, refactoring, agent coordination, department routing, complex reasoning
**Never:** Simple Q&A (route to Codex), self-review after repeated failure (escalate to Codex)

### Brain 2 — OpenAI Codex CLI
**Role:** Second brain, quick responder, reviewer, rescue agent
**Handles:** Simple questions and quick lookups, code writing/editing, adversarial critique, rescue when Claude is stuck, brainstorming second opinions
**Invoke when:** Question is simple/conversational, user requests review, or Claude has failed the same task twice

**Invocation — always use the plugin, never raw Bash:**

| Use case | Plugin command |
|----------|---------------|
| General task, build, fix, question | `Skill("codex:rescue")` with task as args |
| Code review against git state | `Skill("codex:review")` |
| Adversarial / challenge review | `Skill("codex:adversarial-review")` |

### Brain 3 — Gemini CLI
**Role:** Eyes and long-context processor
**Handles:** Video analysis (up to 2 hours), audio transcription, PDFs (200+ pages in one pass), any task requiring 1M+ token context, whole-codebase architecture review

**Invocation — always use the plugin, never raw Bash:**

```
Skill("cc-gemini-plugin:gemini") with task as args
```

Pass context flags as needed:
- `--dirs src,docs` — include directory trees in context
- `--files "path/**/*.md"` — include specific file globs
- `--model gemini-2.5-pro` — override model (default is auto-selected)

Example args: `"--dirs 000_Ingest analyze all files and classify by domain"`

---

## Routing Rules

### Route to Gemini when:
- Task involves a video file or YouTube URL
- Task involves an audio file or transcription
- Task involves a PDF of significant length (use judgment; 200+ pages is a clear trigger)
- Task requires scanning a very large codebase or document set in one pass
- User says "analyze this video/audio/file", "transcribe", "read this PDF"

### Route to Codex when:
- Question is simple, conversational, or a quick factual lookup — preserve Claude tokens
- User says "review your work", "get a second opinion", "tear this apart", "adversarial review"
- Claude has attempted the same task or fix **twice and failed** — do not attempt a third time alone
- User explicitly asks Codex to weigh in on anything

### Stay with Claude (Sonnet) when:
- Writing, creative tasks, scripting, copywriting, strategy
- Building features, refactoring, planning
- Coordinating between departments or agents
- Any task that requires judgment, synthesis, or multi-step orchestration

### Parallel consensus — "ask all three":
When the user says "ask all three" or wants multiple perspectives:
1. Announce: "Routing to all three brains in parallel."
2. Run Claude's response, then Codex, then Gemini on the same prompt
3. Present results clearly labeled: **Claude**, **Codex**, **Gemini**
4. Offer a synthesized verdict

---

## The Handoff Artifact System

Large delegated output does not belong in Claude's active conversation — it belongs on disk, where Claude can retrieve exactly the part it needs, when it needs it, without paying for the rest every time the conversation is reread.

**Location:** `/Users/tonymacbook2025/Documents/Agent-OS/.agent-handoff/`

```text
.agent-handoff/
├── INDEX.md          ← lightweight log of every artifact; check this before scanning folders
├── research/
├── code-review/
├── debugging/
├── architecture/
├── media-analysis/
├── pipeline/          ← CHECKPOINT.md for long multi-stage workflows
└── temporary/          ← disposable, one-off material
```

If a department already has a better-established output location for a specific kind of work (e.g. a channel's own `Data/` or `Research/` folder), use that instead of duplicating it into `.agent-handoff/` — this directory is for cross-cutting inter-model handoff material, not a competing storage system.

**Proportionality:** not every handoff needs a file. A two-paragraph Codex answer or a quick Gemini lookup should just come back inline — see Test D below. File creation should scale with the size and future usefulness of the result.

---

## Progressive Disclosure — Three Levels

For any substantial delegated task (not trivial lookups), the delegated model should produce three tiers of output. Claude operates from Level 1 by default and only reaches deeper when the decision at hand actually requires it.

### Level 1 — Handoff Summary (what Claude receives by default)
Target ~300–1,000 tokens, up to ~1,500 when genuinely necessary. Contains only:
- task completed
- main conclusion
- key findings
- important caveats or uncertainty
- decision/recommendation
- files created or changed
- exact path to the Level 2/3 artifact
- whether Claude needs to inspect deeper material before proceeding

```text
HANDOFF RESULT — Gemini
Status: Complete
Conclusion: Topic X is the strongest candidate.
Why: A, B, C.
Important caveat: Claim Y needs independent verification.
Detailed report: .agent-handoff/research/topic-x-report.md
Raw/source notes: .agent-handoff/research/topic-x-raw.md
Recommended next action: Proceed to narrative outline; no deep read required unless validating Claim Y.
```

### Level 2 — Structured Detailed Report (`<category>/<task-id>-report.md`)
A few thousand tokens: key evidence, reasoning, source references, alternatives considered and rejected, important technical detail, unresolved questions. Claude reads this only when Level 1 isn't enough to make the current decision.

### Level 3 — Full / Raw Artifact
The complete delegated material — full research notes, exhaustive code analysis, full transcript, raw diagnostic output. Claude does **not** auto-ingest this. Read it only when:
- the user asks for the underlying detail
- a factual claim must be verified
- a subtle implementation decision depends on it
- Level 1/2 turns out insufficient
- debugging needs the original evidence

When possible, retrieve just the relevant section of a Level 3 file rather than the whole thing.

**The artifact is the source of truth, not the summary.** If precision, provenance, code behavior, source evidence, or disputed reasoning matters, go get the detailed artifact — never treat a lossy Level 1 summary as authoritative for something that needs exactness. Conceptually: "I know the conclusion. I know where the evidence lives. I load the evidence only if this decision requires it."

### Selective retrieval, not full reload
When Claude needs something from a stored artifact (own memory or answering "why did it choose X?"): identify the exact question → identify the most likely artifact (check `INDEX.md` first) → read/search the relevant section → expand only if that's insufficient → read the whole file only if the task genuinely requires all of it. Don't reflexively reload every referenced artifact.

---

## Return-Size Instructions in Every Substantial Delegation

When a delegated task is expected to produce a substantial result, the handoff prompt itself should instruct the brain doing the work:

```text
Perform the full analysis. Persist detailed output to:
.agent-handoff/research/<task>.md

Return to the Claude parent only a concise handoff summary containing:
- conclusion
- key findings
- critical caveats
- artifact path
- recommended next action

Do not return the complete analysis inline.
```

Adapt this to whatever the Codex/Gemini plugin actually supports. If a plugin cannot directly write the file itself, use the most token-efficient supported alternative (e.g. Claude writes the file after receiving the result once, then discards the inline copy from active reasoning) — but never claim a file was persisted if it wasn't.

For small tasks, skip all of this and just let the result come back inline (see Test D below).

---

## Claude Conservation Mode

When Claude's usage quota is running low, switch to **Conservation Mode**: Codex becomes the primary brain and Claude steps back to synthesis and final delivery only.

### Reactive Trigger — Tony says any of:
- "usage limit", "rate limit", "you're full", "you're almost out", "save tokens", "conservation mode", "switch to Codex", "running low"

### Proactive Trigger — active context size (primary signal)
If Claude can determine active context size (e.g. via `/context` or the harness surfacing it), use it as the primary conservation signal:

| Zone | Active context | Behavior |
|------|----------------|----------|
| **Normal** | Below ~100K | Normal routing, normal handoff summaries, persist large outputs as usual |
| **Caution** | ~100K–125K | Keep handoffs aggressively concise, prefer artifact pointers over inline output, avoid broad rereads, retrieve targeted sections only |
| **Compact Recommended** | ~125K–150K | Write/update a pipeline checkpoint, recommend or perform `/compact`, then continue from checkpoint + artifacts |
| **New Major Phase** | Phase boundary reached, next phase doesn't need full live conversation | Write a checkpoint, use `/clear`, restart from project memory + checkpoint + artifact index |

Don't wait for the full context window to fill up — a large window is not the same thing as an efficient usage budget. If Claude cannot programmatically see context/token size in the current environment, don't pretend to — fall back to the behavioral proxies below and prompt for `/context` or user-provided usage info when it's genuinely needed.

### Behavioral Proxy Trigger (fallback, when context size isn't visible)
Activate Conservation Mode automatically when **any two** of the following are true in the current session:
- More than 15 tool calls have been made
- Claude has written or edited more than 5 files
- The conversation has passed 3 major tasks (plan → build → review cycles)
- Claude has already done one large multi-file refactor or build this session

When either trigger fires, announce it:
```
⚡ CONSERVATION MODE ACTIVATED
Reason: [Active context in Caution/Compact zone | Heavy Claude usage detected this session] — switching Codex to primary brain to preserve quota.
Claude will handle synthesis and final output only.
```

### What changes in Conservation Mode:

| Task type | Normal routing | Conservation routing |
|-----------|---------------|---------------------|
| Simple questions | Codex | Codex (no change) |
| Quick file reads / lookups | Claude | Codex |
| Code writing / editing | Claude | Codex |
| Building features | Claude | Codex (Claude reviews output) |
| Planning / strategy | Claude | Codex drafts, Claude refines |
| Complex reasoning / synthesis | Claude | Claude (irreplaceable) |
| Video / audio / PDF | Gemini | Gemini (no change) |

**Rule:** In Conservation Mode, default every task to Codex first. Only pull Claude in when Codex output needs synthesis, judgment, or multi-step orchestration that Codex cannot do.

### Exiting Conservation Mode:
Tony says "full mode", "back to normal", "use Claude", or the session ends. Log the mode change.

---

## Failure Detection (Hard Stop Rule)

Claude must not loop. If you have attempted to solve the same problem **twice without success**:

1. **Stop.** Do not attempt a third time.
2. **Announce** the handoff (see Handoff Protocol below).
3. **Pass to Codex the minimum sufficient context** — not the whole conversation:
   - the goal
   - the exact failure (error message, wrong output, etc.)
   - relevant file paths
   - approaches already tried and why they failed
   - constraints
   - relevant code sections, if necessary
   Do not forward unrelated conversation history. Only escalate to a broader context package if the first focused one proves insufficient.
4. **Interpret** Codex's response and implement the fix or present it to Tony. If Codex's diagnostic output is large, persist it under `.agent-handoff/debugging/` and work from the Level 1 summary; pull the full diagnostics only if implementation requires them.

---

## Department Risk Path Detection

Risk level for any task is not hardcoded — it is determined by reading the CLAUDE.md of the relevant department. Before starting any task in a department folder:

1. Read that department's `CLAUDE.md` for sensitivity notes, protected files, or review requirements
2. If the CLAUDE.md flags certain files or operations as high-risk, treat those as requiring Codex review before finalizing
3. When in doubt, announce the risk and ask Tony whether to proceed or invoke Codex

---

## Handoff Protocol (Always Announce)

Every time a task is routed to Codex or Gemini, announce it clearly before executing. Use this format:

```
🧠 HANDOFF → [Brain Name]
Reason: [one sentence — why this brain is being invoked]
Task: [what is being sent]
```

Examples:
```
🧠 HANDOFF → Gemini
Reason: Video file analysis — native video input required
Task: Analyzing /Downloads/alexhormozi.mp4 for transcript and visual overlay
→ Skill("cc-gemini-plugin:gemini") args: "analyze /Downloads/alexhormozi.mp4 for transcript and visual overlay; persist full transcript to .agent-handoff/media-analysis/alexhormozi-transcript.md; return only a Level 1 handoff summary"

🧠 HANDOFF → Codex
Reason: Claude has failed this fix twice — escalating for rescue
Task: JWT middleware bug in /src/auth/middleware.ts — two attempts failed
→ Skill("codex:rescue") args: "Fix JWT middleware bug in /src/auth/middleware.ts. Claude tried X and Y, both failed. [minimum sufficient context only]"

🧠 HANDOFF → Codex
Reason: User requested adversarial code review
Task: Reviewing the HTML document generated in the last step
→ Skill("codex:adversarial-review")
```

For trivial handoffs (short question, small review), skip the artifact instructions entirely — just send the task and take the inline result.

---

## Logging

Every handoff must be logged. Append to the daily session log at:

```
/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Logs/YYYY-MM-DD_Session-Log.md
```

Log entry format:
```
[HH:MM] HANDOFF → [Brain] | Reason: [why] | Task: [what] | Result: [concise summary] | Artifact: [path, or "none — inline"]
```

Log a concise result summary and the artifact path only — never duplicate the full delegated output into the session log. It's an audit trail, not a second copy of the context store.

Log at the moment of handoff (before result) and update with outcome once complete. If no session log exists for the day, create it.

---

## After a Handoff

1. Receive the Level 1 handoff summary — don't ask for or expect the full output by default.
2. Confirm the detailed-artifact path if one was created.
3. Interpret the summary — don't just dump raw output on Tony.
4. Decide whether the current decision actually requires Level 2/3 detail. Most of the time it doesn't.
5. If it does, retrieve the specific artifact (selectively — see Progressive Disclosure above), not the whole pipeline history.
6. Tell Tony what you're doing with the result (implementing it, presenting options, flagging an issue) — this announcement itself should stay concise.
7. If the result raises new questions, ask Tony before proceeding.

**User access is never restricted.** If Tony asks for the complete analysis, all the research, the full Codex review, or detailed reasoning behind a conclusion, retrieve and present the actual material — Level 1 summaries are a default retrieval strategy for Claude's own working context, not a way of hiding information from Tony.

---

## Pipeline Checkpoints

For long, multi-stage workflows (e.g. a video production moving through research → B-roll → scenes → generation), maintain a running checkpoint instead of carrying every prior stage's raw output forward in conversation.

**Location:** `.agent-handoff/pipeline/CHECKPOINT.md` — or a project-specific pipeline state file if one already exists for that department (don't create a duplicate).

A checkpoint should contain: current objective, completed stages, key decisions, selected assets/topics, relevant artifact paths, current implementation state, unresolved problems, next action, and what the next phase depends on. Link to research/logs by path — don't duplicate their content into the checkpoint.

```text
# Pipeline Checkpoint

## Current project
Video: <title/id>

## Completed
- Topic research complete
- Topic X selected
- Source set approved
- B-roll discovery complete

## Key decisions
- Narrative angle: ...
- Runtime target: ...
- Visual style: ...

## Relevant artifacts
- Research: .agent-handoff/research/topic-x-report.md
- B-roll: .agent-handoff/media-analysis/broll-manifest.json
- Scene plan: .agent-handoff/pipeline/scene-plan.md

## Open issue
Scene 7 needs a replacement establishing shot.

## Next
Generate Seedance prompts for scenes 1–10.
```

### Video-pipeline delegation
Video productions are unusually context-heavy — topic research, source research, B-roll discovery/download, transcript analysis, narrative construction, scene generation, and Seedance prompting all produce bulk. Default these stages to artifact-backed handoffs: each stage saves its full output, hands Claude a small Level 1 summary, and the checkpoint tracks where things stand. Don't carry all earlier raw research into every later stage — pull a specific prior artifact only when a later decision actually depends on it.

---

## Artifact Index

**Location:** `.agent-handoff/INDEX.md`

Keep it small — one line per entry:
```text
- 2026-08-22 | Gemini | Topic research | research/topic-x-report.md | Selected Topic X; Claim Y flagged
- 2026-08-22 | Codex | Downloader bug | debugging/broll-timeout.md | Root cause identified; retry logic proposed
```

Consult the index before scanning directories or opening multiple artifacts. Rotate or archive it if it starts growing into a giant historical log — it's a lookup table, not an archive.

---

## Persistent Knowledge vs. Temporary Work

Not everything a handoff produces deserves the same lifespan.

**Goes to project memory / CLAUDE.md** (durable, applies to future work): pipeline architecture, directory conventions, durable design decisions, recurring rules, lessons that generalize, stable model-routing rules.

**Stays in `.agent-handoff/` artifacts** (scoped to this task/production): today's research, source dumps, candidate topics, B-roll results, generated prompts, transcripts, debugging traces, rejected scene ideas, one-off diagnostics.

Don't promote temporary bulk into memory just because it was useful once.

---

## Artifact Hygiene

Token efficiency should not turn into file-management chaos:

- Don't create an artifact for a trivial response — a two-paragraph answer just comes back inline.
- Reuse or update an existing task artifact rather than spawning a near-duplicate.
- Use stable, descriptive task IDs/filenames so artifacts are findable later.
- Disposable, one-off material goes in `temporary/`.
- Completed temporary handoffs can be archived or deleted per normal project cleanup — never delete or modify important project artifacts merely to save context.
- Never persist hidden chain-of-thought or private model reasoning — store conclusions, evidence, diagnostics, decisions, and outputs.

---

## What This Is Not

- Codex does **not** run silently in the background on every task
- Gemini is **not** invoked for short text tasks Claude can handle
- Claude does **not** self-review after failure — escalate
- Handoffs are **not** silent — Tony always sees what's happening and why
- Delegation to Codex/Gemini is **not** "zero Claude tokens" — it can be *low-cost* to Claude's active context if returns stay concise, but the handoff and its interpretation are never literally free
- Progressive disclosure is **not** an information restriction on Tony — he can always get the full detail on request
- A large context window is **not** permission to carry everything forward indefinitely
