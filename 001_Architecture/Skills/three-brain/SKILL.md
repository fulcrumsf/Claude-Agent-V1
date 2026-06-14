---
name: three-brain
description: "Three-Brain Auto-Router — intelligently routes tasks across Claude (orchestrator/builder), OpenAI Codex (reviewer/rescue), and Gemini (video/audio/PDF/long-context). Invoke this skill whenever: a task involves video files, audio files, or large PDFs; Claude has failed to solve something more than twice; the user asks for a code review, adversarial review, or second opinion; the user says \"ask all three\" or wants parallel model consensus; a handoff to another model is needed for any reason. Claude is always the conductor — it announces every handoff, logs it, and interprets the result. This skill should be active in every session across all departments."
---

# Three-Brain Auto-Router

Claude is the conductor. Every task starts here. Claude decides which brain handles what, announces every handoff out loud, logs it, and synthesizes the result.

---

## Token Economy — Which Brain Saves What

Codex and Gemini burn **zero Claude tokens**. Use them aggressively to preserve Claude capacity for work that actually needs it.

| Task type | Brain | Claude tokens used |
|-----------|-------|--------------------|
| Simple questions, quick lookups | Codex | None |
| Code review, adversarial, rescue | Codex | None |
| Video, audio, PDF, long-context | Gemini | None |
| Planning, writing, creative, orchestration | Claude Sonnet | Low |
| Heavy builds, complex reasoning | Claude Sonnet | Medium |
| Opus | Only if Tony explicitly asks | High — avoid by default |

**Default model:** Sonnet 4.6. Never escalate to Opus unless Tony requests it.

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

## Claude Conservation Mode

When Claude's usage quota is running low, switch to **Conservation Mode**: Codex becomes the primary brain and Claude steps back to synthesis and final delivery only.

### Reactive Trigger — Tony says any of:
- "usage limit", "rate limit", "you're full", "you're almost out", "save tokens", "conservation mode", "switch to Codex", "running low"

### Proactive Trigger — Claude self-detects heavy usage:
Activate Conservation Mode automatically when **any two** of the following are true in the current session:
- More than 15 tool calls have been made
- Claude has written or edited more than 5 files
- The conversation has passed 3 major tasks (plan → build → review cycles)
- Claude has already done one large multi-file refactor or build this session

When proactive trigger fires, announce it:
```
⚡ CONSERVATION MODE ACTIVATED
Reason: Heavy Claude usage detected this session — switching Codex to primary brain to preserve quota.
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
3. **Pass to Codex** with full context: what was tried, what failed, what the goal is.
4. **Interpret** Codex's response and implement the fix or present it to Tony.

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
→ Skill("cc-gemini-plugin:gemini") args: "analyze /Downloads/alexhormozi.mp4 for transcript and visual overlay"

🧠 HANDOFF → Codex
Reason: Claude has failed this fix twice — escalating for rescue
Task: JWT middleware bug in /src/auth/middleware.ts — two attempts failed
→ Skill("codex:rescue") args: "Fix JWT middleware bug in /src/auth/middleware.ts. Claude tried X and Y, both failed."

🧠 HANDOFF → Codex
Reason: User requested adversarial code review
Task: Reviewing the HTML document generated in the last step
→ Skill("codex:adversarial-review")
```

---

## Logging

Every handoff must be logged. Append to the daily session log at:

```
/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Logs/YYYY-MM-DD_Session-Log.md
```

Log entry format:
```
[HH:MM] HANDOFF → [Brain] | Reason: [why] | Task: [what] | Result: [summary of outcome]
```

Log at the moment of handoff (before result) and update with outcome once complete. If no session log exists for the day, create it.

---

## After a Handoff

1. Interpret the response from Codex or Gemini — don't just dump raw output on Tony
2. Summarize what the other brain found or produced
3. Tell Tony what you're doing with the result (implementing it, presenting options, flagging an issue)
4. If the result raises new questions, ask Tony before proceeding

---

## What This Is Not

- Codex does **not** run silently in the background on every task
- Gemini is **not** invoked for short text tasks Claude can handle
- Claude does **not** self-review after failure — escalate
- Handoffs are **not** silent — Tony always sees what's happening and why
