---
name: lab-plan
description: Claude Code only. Runs when Tony types /lab-plan <question> - a cheap picked OpenRouter model drafts a build plan read-only, then an opus-standard subagent scores the raw draft 0-100, writes acceptance checks, and locks (>=80) or regenerates (<80) the plan into 001_Architecture/Lab/. Codex and Gemini - do not use this skill; it depends on Claude Code's Agent tool.
argument-hint: <question or thing to plan>
disable-model-invocation: true
---

# /lab-plan

First command of the `/lab` system (see `001_Architecture/Skills/lab/SKILL.md` for the whole system).
You, the Claude Code session, orchestrate. The draft comes from a script; the review comes from an
`opus-standard` subagent you spawn. Never skip the review, never do the review yourself, never
involve Jev or `delegate.py`, never commit.

Tony's question: $ARGUMENTS

If the question above is empty, ask Tony what he wants planned and stop.

## Files this command produces

One project folder per run: `001_Architecture/Lab/YYYY-MM-DD_Title_Slug/` (date + first words of the
question in Title_Case; `_2`, `_3` added if the name is taken). The script creates it; nothing else
creates folders. `/lab-build` will look for these exact names later:

| File | Written by | Rule |
|------|------------|------|
| `Draft_Raw.md` | picked model (via script) | Read-only. Never edited. This is what gets scored. |
| `Draft_Meta.json` | script | Model, why it was picked, tokens, cost, draft hash. |
| `Score.json` | reviewer, FIRST | Score of the RAW draft. Written before anything else, never changed. |
| `Plan_Locked.md` | reviewer | The locked plan `/lab-build` will build from. |
| `Acceptance_Checks.json` | reviewer | The builder's exam. Made read-only by verify. |
| `Review.md` | reviewer | What changed and why, in plain words. |

## Step 1 - Draft (script, picked model)

Run in the background (Bash `run_in_background: true`) and wait for the completion notice; the
script stops its worker after 20 minutes:

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_plan_draft.py "<Tony's question>"
```

Quote the question safely (escape any double quotes in it). The last line of output is
`LAB_PLAN_RESULT {json}` with `project_dir`, `model`, `why_picked`, `cost_usd`.

Exit codes that stop the command:
- `5` = over the spend cap. Show Tony the script's message and ask for a yes to raise it. Only after
  a clear yes, rerun with `--cap <new USD amount>`.
- `6` / `124` = draft failed or timed out. Tell Tony, name the log file from the error line, and ask
  whether to retry on another model (`--model <id>`, see `--list`). Do not fall back to writing the
  plan yourself.
- `1`, `2`, `3`, `4` = setup problem. Show the message to Tony and stop.

Do not read `Draft_Raw.md` into your own context; the reviewer reads it from disk.

## Step 2 - Review (spawn opus-standard)

Call the Agent tool with `subagent_type: "opus-standard"`, `run_in_background: false`,
`description: "Review /lab-plan draft"`, and this prompt with `<PROJECT_DIR>` and `<QUESTION>` filled in:

```
You are the independent reviewer for Tony's /lab-plan command. Project folder: <PROJECT_DIR>
Tony's question: <QUESTION>

Read <PROJECT_DIR>/Draft_Raw.md (a plan drafted by a cheaper model; Draft_Meta.json says which).
Never edit Draft_Raw.md. Check the draft against the real workspace: open the files, skills and
tools it names and confirm they exist and do what it says; check 001_Architecture/Skills/ and
TOOLBOX.md for anything it should reuse; if the ask is vague (e.g. "add motion graphics"), the plan
must lock it to the workspace's own skill for that job.

Hard constraints the plan must meet (a future sandboxed builder enforces them):
- it only creates new files inside ONE new folder; no edits to existing files except a separate
  "Wiring (Later, Tony-Approved)" list (TOOLBOX.md, Skill-Index.md, hooks, other pipelines);
- every paid API call sits after a cost-estimate pause, every publish after a selection pause;
- API keys load from ~/.env-secrets, never hardcoded; nothing publishes without Tony's approval.

Do these in order. Write only these four files, only inside <PROJECT_DIR>, no new folders.

1. SCORE THE RAW DRAFT FIRST, before editing anything. Rubric (100 total):
   grounding in real workspace files 30, answers Tony's actual question 20, buildable under the
   one-new-folder / new-files-only rule with concrete file-level steps 20, spend and safety gates 15,
   verifiable with free checks 15. Write <PROJECT_DIR>/Score.json exactly like:
   {"score": 0-100 whole number, "verdict": "lock" if score >= 80 else "regenerate",
    "reasons": ["one line per rubric area: points given and why"], "scored_by": "opus-standard"}
   Never change Score.json after this step.

2. PLAN. If verdict is "lock": fix minor issues and write <PROJECT_DIR>/Plan_Locked.md (keep the
   draft's structure). If verdict is "regenerate": this is the one allowed retry - write a new plan
   yourself from scratch into Plan_Locked.md, using the failures in Score.json as context, same
   section structure as the draft. Either way start Plan_Locked.md with this frontmatter:
   ---
   status: locked
   raw_draft_score: <score>
   drafted_by: <model from Draft_Meta.json>
   locked_by: opus-standard
   regenerated: true|false
   ---

3. ACCEPTANCE CHECKS for a future /lab-build of Plan_Locked.md, written now, before any code
   exists. Write <PROJECT_DIR>/Acceptance_Checks.json exactly like:
   {"plan": "<folder name>", "written_by": "opus-standard",
    "checks": [{"id": "C01", "tier": 0|1|2, "what": "plain words",
                "run": "shell command; use $BUILD_DIR for the new folder",
                "pass_if": "exact expected result, e.g. exit code 0 / output contains X"}],
    "tony_paid_run": ["what Tony should look at on his first real paid run"]}
   At least 3 checks, all free to run (no paid APIs, no network). Tier 0 = static/containment
   (files exist only inside $BUILD_DIR, secret scan, no hardcoded keys). Tier 1 = structural (scripts
   parse, --help runs, imports resolve, model IDs exist in the workspace pricing files, every paid
   call after its cost pause, every publish after its selection pause). Tier 2 = measured output from
   free local steps on fixture files (ffprobe, ebur128, preview frames). Paid runs are not a tier;
   list them under tony_paid_run.

4. Write <PROJECT_DIR>/Review.md for Tony in plain words: score and verdict, what you changed (or
   why you regenerated), how big the change was (none / minor / major, rough % of the plan
   rewritten), and anything Tony must decide.

Do not build or run the plan, do not call paid APIs, do not touch any other file. Reply with at most
10 lines: score, verdict, change size, number of checks, open questions for Tony.
```

## Step 3 - Verify (script, mechanical)

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_plan_draft.py --verify "<PROJECT_DIR>"
```

Last line: `LAB_PLAN_VERIFY {json}`. Exit `0` = all good (acceptance checks are now read-only).
Exit `7` = problems listed in `problems`:
- If the problems are only in `Plan_Locked.md`, `Acceptance_Checks.json` or `Review.md` (missing or
  badly formatted), send the listed problems back to the same reviewer once (SendMessage to the
  agent from Step 2), telling it to fix only those files and never touch Score.json, then re-run
  verify. If it still fails, report the remaining problems to Tony.
- If any problem names `Score.json` or `Draft_Raw.md` (bad score file, raw draft changed, or score
  written after the plan), do NOT fix it: rewriting the score now would break the
  score-before-edit rule. Tell Tony exactly what verify said and stop.

## Step 4 - Report to Tony

Read `Plan_Locked.md` and `Review.md`, then reply in short, plain words, a blank line between points:
- which model drafted it, why it was picked, and what the draft cost (`cost_usd`);
- the raw draft's score out of 100, and whether Opus locked it (80+) or rewrote it (below 80);
- what Opus changed, in one or two lines;
- how many acceptance checks were written and where the folder is;
- Opus's open questions for Tony, if any;
- then the locked plan itself (the contents of `Plan_Locked.md`, without its frontmatter).

End by saying the plan is ready for `/lab-build`, which is not built yet.
