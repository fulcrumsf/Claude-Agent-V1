# Self-Review — 2026-07-08

## What went wrong and why

### 1. The plan's own example code shipped with real bugs, more than once
Task 2's brief had a working-but-broken import path (missing `config.py` on `sys.path`). Task 4's brief's example code was an incomplete stub (submitted a kie.ai task but never polled/downloaded the result, despite the task's own Interfaces section requiring the output file to exist). Both were caught and fixed correctly, but the pattern recurred: a plan document's "complete code to write verbatim" section is not a substitute for verifying it against the actual task contract. Should treat plan example code as a strong draft to verify, not a transcription target to trust blindly — this was mostly done right this session, but worth calling out as a recurring plan-writing gap for future PLAN.md authoring.

### 2. Two approved, individually-correct tasks contradicted each other when composed
Task 5's `not_found` coordinate-stripping and Task 6's required-field Zod schema were each reviewed and approved in isolation — neither reviewer had visibility into the other task's file. The contradiction (a valid `not_found` entry would fail Task 6's schema) only surfaced in the final whole-branch review. This isn't a process failure — the subagent-driven-development skill's design explicitly expects the final review to catch exactly this class of bug — but it's worth internalizing as a recurring risk in any multi-task plan with real data-interface handoffs between tasks: assume cross-task contradictions exist until the final full-file-set review proves otherwise, and don't skip that step even when every individual task looked clean.

### 3. A hard constraint ("no static frame >3-5s") was written into three places that didn't actually enforce it
Task 3 recorded it as data, Task 6's component had no mechanism to act on it, and the orchestrator SKILL.md only mentioned it in passing. All three pieces existed and each looked reasonable on its own, but the actual enforcement was nowhere. This is a design-time gap, not an implementation bug — when a plan states "X is a hard rule, no exceptions," the plan (or its review) should ask "which specific file/step actually checks this and what does it do when the check fails" before calling any task that touches that rule done.

## What worked well

### Escalating an inference-based finding to the human instead of digging for more (nonexistent) evidence
Task 8's Blotato account-ID identification rested on process-of-elimination + a spelling-similarity argument. Rather than either accepting it as "probably fine" or spending more tool calls trying to manufacture stronger API-level corroboration that didn't exist, the direct move was asking Tony by name to confirm the specific ID. He confirmed in one turn. For any finding where the real-world consequence is high-stakes/irreversible (publish target, financial, destructive) and available evidence is inference rather than ground truth, asking the human directly is both faster and more reliable than continuing to reason toward artificial confidence.

### Real before/after evidence beats a parser's verdict in isolation
The Task 11 YAML frontmatter bug wasn't just "yaml.safe_load() throws an error" — it was proven to matter by comparing this session's own live skill-list display before and after the fix (bare H1 fallback vs. the full rich description). This turned a plausible-but-arguable "is this really broken" question into an directly observable fact, which is what let it be classified Critical with real confidence rather than a judgment call.

### Fresh subagent + task-scoped review + fix-loop pattern held up across 10 built tasks
No task needed more than one fix-and-re-review cycle. Every implementer subagent that hit a real ambiguity (Task 2's import bug, Task 4's incomplete stub, Task 8's account lookup) surfaced it rather than silently guessing past it. This is the second large multi-task build in this workspace to use subagent-driven-development successfully (after Reimagined Realms' original build) — continue defaulting to it for future multi-task plans rather than inline execution.
