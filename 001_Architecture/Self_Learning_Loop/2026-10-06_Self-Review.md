# Self-Review — 2026-10-06

## What went wrong, honestly

**I let "take it further" and similar open-ended continuations drift without re-grounding in what Tony actually meant, more than once.** A few times I picked the next mechanically-obvious `/lab` step without pausing to confirm that's what "take it further" meant, and a couple of times that guess was close enough but not quite — most visibly when I framed a pass/fail bug as something Tony needed to "grade." He had to correct the scope of what grading even meant for this tool, more than once, before I had it right. The lesson: an open-ended instruction after a long complex session is not permission to autopilot the next step — it still needs a one-line confirmation of what "further" means before diving in, especially after a context-heavy stretch where my own momentum can substitute for his actual intent.

**I used jargon ("backfill," technical event-schema field names) in direct chat with Tony multiple times despite already knowing, from standing memory, that he wants plain language by default.** This is a known, previously-recorded pattern (`feedback_plain_language_default.md`) and it still happened again tonight, repeatedly, in a way that visibly frustrated him. Knowing a rule exists in memory isn't the same as applying it under pressure when a task is technically dense — I need to actively re-check my own phrasing against "would this need a glossary" before sending it, not just rely on having read the rule once at session start.

## What worked well

**Treating "fix everything, rock solid" as a literal mandate for one real adversarial pass, not a vague aspiration.** Delegating a genuine fuzz-style hunt (deliberately malformed inputs, concurrency races, boundary values) rather than a surface code read caught 34 real bugs in one pass, several of which were the same silent-failure *pattern* repeating in different commands — fixing the pattern once rather than patching each instance was the right level of fix, and it held up when verified against the reverted old code.

**Going to the real, raw session transcript instead of a cleaned-up summary when the data needed to be trustworthy.** This was explicitly Tony's instinct, not mine first — but once pointed there, treating the real transcript as ground truth (copying his words verbatim, never paraphrasing) rather than smoothing it into a tidier narrative is the right default for anything meant to preserve "what actually happened," and it should generalize beyond tonight's one example.

## Patterns worth automating or watching for

- **A standing pre-send check for jargon before any message to Tony that names a tool's internal command, field, or concept he didn't invent himself** — this has now recurred enough times across sessions that a passive memory entry isn't enough; it may need an active habit of re-reading my own draft reply for unexplained internal names before sending, every time, not just when a correction already happened in-session.
- **When an instruction is open-ended after a long complex session ("take it further," "take this further"), state in one sentence what I'm about to do and let that sentence itself be the check, before spending real tool calls on it** — cheaper than a full subagent dispatch landing on the wrong interpretation.
- **Grading/scoring scope confusion (am I grading the tool or the output; is this a bug or a judgment call) is worth a one-time durable memory entry**, since it's a distinction that will recur every time a new `/lab`-built tool goes through its own `/lab-run`.
