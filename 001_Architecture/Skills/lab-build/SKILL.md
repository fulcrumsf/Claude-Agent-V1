---
name: lab-build
description: Claude Code only. Runs when Tony types /lab-build [plan folder] - a cheap picked OpenRouter model builds a locked /lab-plan inside a network-off sandbox and a git worktree under 001_Architecture/Lab/ (new files in one new folder only), a script scores it for real on the plan's acceptance checks, then an opus-standard subagent audits it, with at most one fix round and one rebuild. Codex and Gemini - do not use this skill; it depends on Claude Code's Agent tool.
argument-hint: [plan folder name, or empty for the newest locked plan]
disable-model-invocation: true
---

# /lab-build

Second command of the `/lab` system (see `001_Architecture/Skills/lab/SKILL.md`). You, the Claude
Code session, orchestrate. The build, the containment check, the real check runs and the 75
non-model points come from a script; the 25-point audit, the fix round and the rebuild come from
`opus-standard` subagents you spawn. Never build, audit or fix anything yourself, never involve
Jev or `delegate.py`, never commit, never delete (old worktrees stay for Tony).

Tony's argument: $ARGUMENTS (a folder name under `001_Architecture/Lab/`, a full path, or empty =
the newest locked plan that has no build yet; say which one you used).

Script: `python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_build.py`
(below just `lab_build.py`). Run every call with Bash; the build itself in the background.

## Files this command produces

All in the SAME `/lab-plan` project folder (`<PROJECT_DIR>`); the built folder itself lives in the
worktree (point Tony to its path, never copy it here):

| File | Written by | Rule |
|------|------------|------|
| `Build_Worktree_<n>/` | script | git worktree, branch `lab/<project>/wt<n>`. The ONE new folder is inside it at the plan's promoted path (`BUILD_DIR`). Never deleted by agents. |
| `Build_Meta.json` | script | Model, why picked, cost, tokens, worktree, build folder, attempt, preflight. |
| `Build_Score.json` | script, FIRST | Raw build: containment result, every check's real result, 60 + 15 points. Read-only, never rewritten. |
| `Build_Audit.json` | auditor | The 25-point cited rubric for the raw build. Written before any fix. |
| `Build_Review.md` | auditor | What the audit found (and later fixed), in plain words for Tony. |
| `Build_Verdict.json` | script | Every stage's total and the next step (`lab_run`, `fix_round`, `rebuild`, `stop`). |
| `Build_Score_Fix.json` | script | Re-run after the one fix round. |
| `Build_Score_Rebuild.json`, `Build_Audit_Rebuild.json` | script / auditor | The one rebuild, scored raw then audited (`Build_Score_Rebuild_Fix.json` if its fix round runs). |
| `Build_Score_Reverify.json` | script | Step 4b only: the one voluntary recheck after a fix Tony chose once the build had already ended. Read-only, one per project; the original score and audit files stay as they were. |

Score: 60 = share of the plan's acceptance checks that really pass, 15 = containment held AND every
Tier-0 check passed, 25 = auditor rubric (only lines it can quote count). **80+ with at least 55 of
the 75 non-model points = cleared for Tony's first real paid run** (`/lab-run`).

## Step 1 - Build (script, picked model)

Run in the background (`run_in_background: true`), wait for the completion notice (it stops the
worker after 30 minutes):

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_build.py "<PROJECT>"
```

Add `--into <relative/path/New_Folder>` only if the script says it could not find the folder in
the plan. Last line: `LAB_BUILD_RESULT {json}` with `project_dir`, `build_dir`, `model`,
`why_picked`, `cost_usd`, `points`, `failed_checks`, `max_possible_total`.

Exit codes:
- `0` = raw build scored, go to Step 2.
- `8` = **CONTAINMENT STOP.** Show Tony the `containment` / `preflight` lines word for word, say no
  fix will be attempted and the worktree is left as-is for him to look at. Stop the command here.
- `5` = over the spend cap. Show the message, ask Tony for a yes; only then rerun with `--cap <USD>`.
- `6` / `124` = build failed or timed out. Name the log file, ask Tony whether to retry on another
  model (`--model <id>`, see `--list`). Never build it yourself.
- `1`, `2`, `3`, `4` = setup problem (e.g. plan not verified). Show the message and stop.

Do not read the built files into your own context; the auditor reads them from disk.

## Step 2 - Audit (spawn opus-standard)

Agent tool, `subagent_type: "opus-standard"`, `run_in_background: false`, `description: "Audit
/lab-build"`, this prompt with `<...>` filled in (attempt 1: `Build_Score.json` /
`Build_Audit.json`; after a rebuild: `Build_Score_Rebuild.json` / `Build_Audit_Rebuild.json`):

```
You are the independent auditor for Tony's /lab-build command. Project folder: <PROJECT_DIR>
Built folder: <BUILD_DIR> (built by <MODEL>). Mechanical score file: <PROJECT_DIR>/<SCORE_FILE>

Read <PROJECT_DIR>/Plan_Locked.md, <PROJECT_DIR>/Acceptance_Checks.json, the score file (every
check's real result and output tail) and every file in <BUILD_DIR>. In this step you may NOT
create, edit, move or delete anything in <BUILD_DIR> or anywhere else except the two files below
(a script fingerprints the folder; any change now voids the audit). Do not run anything inside
<BUILD_DIR> (running scripts there can leave files); to try something, copy the folder to a temp
dir first. No paid APIs, no network calls.

1. Score this 25-point rubric, 5 points each:
   R1 matches Plan_Locked.md: every planned file and behavior is there, nothing unplanned
   R2 no silent failures: errors surface with clear messages and exit codes
   R3 safety and spend gates: paid calls after a cost pause, publishes after a selection pause,
      keys from ~/.env-secrets, nothing hardcoded
   R4 workspace fit: reuses the tools the plan names, naming convention, maintainable code
   R5 honest exam: no special-casing of the acceptance checks, builder tests test behavior
   Write <PROJECT_DIR>/<AUDIT_FILE> exactly like:
   {"scored_by": "opus-standard", "attempt": <1 or 2>,
    "items": [{"id": "R1", "points": 0-5, "cite_file": "<file path relative to the built folder, or <SCORE_FILE>>",
               "cite_text": "one line copied exactly from that file, 8+ characters", "why": "plain words"},
              ... R2, R3, R4, R5],
    "failures_to_fix": ["specific named problems a small fix could solve, e.g. 'C11: validate exits 1, must be 2'"],
    "fix_would_exceed_third": true or false}
   Every item needs a real quoted line, even at full marks. A script checks each quote against the
   file and gives 0 to any item whose quote it cannot find. fix_would_exceed_third = true if fixing
   the named failures would rewrite more than about a third of the build's lines.

2. Write <PROJECT_DIR>/Build_Review.md for Tony in plain words: what was built, which checks
   failed and why, what each rubric item found, and what a fix would change. If it is a rebuild
   audit, add a "## Rebuild Audit" section instead of replacing the file.

Reply with at most 8 lines: your rubric total, the failures, whether a fix would exceed a third.
```

## Step 3 - Finalize (script, mechanical)

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_build.py --finalize "<PROJECT_DIR>"
```

Last line: `LAB_BUILD_VERDICT {json}` with `total`, `non_model_75`, `audit_25`, `named_failures`, `next`.
- Exit `7` with `score_tampered: false` (audit file missing, malformed, or an item missing): send the
  `problems` back to the same auditor once (SendMessage), telling it to fix only `<AUDIT_FILE>` /
  `Build_Review.md` and never touch the build or the score file, then rerun `--finalize`. Still
  failing = report to Tony.
- Exit `7` with `score_tampered: true` (score file changed, or the build changed before finalize):
  do NOT repair anything. Tell Tony exactly what it said and stop; the score-before-edit rule broke.
- Exit `0`: follow `next`:
  - `lab_run` -> Step 6.
  - `fix_round` -> Step 4.
  - `rebuild` -> Step 5.
  - `stop` -> Step 6 (report the failures; the one fix round and one rebuild are used up).

## Step 4 - The one fix round (only if next = fix_round)

SendMessage to the same auditor:

```
Fix round (the only one this project gets). Fix ONLY these named failures, editing files only inside
<BUILD_DIR>: <named_failures from the verdict>. Keep it small: well under a third of the build's lines
(the script measures the change; a bigger one is thrown out and triggers a rebuild). Never delete or
rename files, never touch Acceptance_Checks.json, Plan_Locked.md, any Build_Score*/Build_Audit* file,
or anything outside <BUILD_DIR>. You may now run the failing checks yourself to confirm. Then append
a "## Fix Round" section to Build_Review.md saying what you changed. Reply in at most 5 lines.
```

Then:

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_build.py --after-fix "<PROJECT_DIR>"
```

It re-checks containment (exit `8` = stop as in Step 1), re-runs every check, keeps the auditor's
25 points from the raw audit (the auditor never grades its own fix) and prints `LAB_BUILD_VERDICT`
with `fix_ratio` and `next`: `lab_run` -> Step 6, `rebuild` -> Step 5, `stop` -> Step 6.

## Step 4b - Voluntary reverify (only when a fix was applied after the build already ended)

Use this only when the latest verdict already said `lab_run` or `stop` (the normal path is done)
and Tony still chose to have the audit's named failures fixed inside `<BUILD_DIR>`. If the verdict
says `fix_round`, use Step 4 (`--after-fix`); if it says `rebuild`, use Step 5. The script refuses
`--reverify` in those cases, and refuses a second one on the same project.

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_build.py --reverify "<PROJECT_DIR>"
```

Free, no model: it re-checks containment (exit `8` = stop as in Step 1), re-runs every check for
fresh 60 + 15 points, keeps the original audit's 25 points unchanged (no new audit), and writes
`Build_Score_Reverify.json` once. A fix that rewrote more than a third of the build cannot keep the
audit's points (same rule as Step 4). Exit `7` = a score or audit file changed since `--finalize`:
tell Tony, repair nothing. `LAB_BUILD_VERDICT` has `stage: "reverify"`, `total`, `previous_total`,
`fix_ratio` and `next`: `lab_run` -> Step 6; `stop` -> Step 6 (say plainly the fix made it worse).
There is no fix round or rebuild after a reverify.

## Step 5 - The one rebuild (only if next = rebuild)

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_build.py --rebuild-prep "<PROJECT_DIR>"
```

It makes a FRESH worktree with an empty `build_dir` (the old worktree stays for Tony). Spawn a NEW
`opus-standard` (Agent tool, `description: "Rebuild /lab-build"`), not the auditor:

```
Rebuild Tony's /lab project from scratch; the first build scored too low. Build folder (new, empty):
<BUILD_DIR>. Plan: <PROJECT_DIR>/Plan_Locked.md (build exactly this; its Wiring section is not for you).
Exam: <PROJECT_DIR>/Acceptance_Checks.json ($BUILD_DIR = the build folder). You may read
<PROJECT_DIR>/Build_Review.md to learn what went wrong, but write everything fresh.
Rules: create new files ONLY inside <BUILD_DIR> (subfolders only if the plan names them); never edit any
other file anywhere, never delete or rename, no git commands, no paid APIs or network calls, keys load
from ~/.env-secrets at run time and are never hardcoded. Run the checks yourself before finishing.
Reply in at most 8 lines: files created, which checks pass.
```

Then score it raw (before any audit):

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_build.py --score-rebuild "<PROJECT_DIR>"
```

Exit `8` = containment stop (Step 1 rules). Exit `0` = repeat Step 2 with a NEW `opus-standard`
auditor (independence: never the rebuilder) using `Build_Score_Rebuild.json` /
`Build_Audit_Rebuild.json`, then Step 3. If that says `fix_round` (only possible when no fix round
was used yet), do Step 4 once; anything else ends at Step 6. The script refuses a second fix round
or a second rebuild.

## Step 6 - Report to Tony

Read `Build_Verdict.json` and `Build_Review.md`, then reply in short, plain words, a blank line
between points:
- which model built it, why it was picked, what it cost (`Build_Meta.json`);
- the RAW score out of 100 split as checks /60, safety floor /15, Opus audit /25, and the final
  score if a fix or rebuild happened (with how much the fix rewrote, `fix_ratio`);
- what failed and what Opus fixed, one or two lines;
- the built folder's full path (inside the worktree) and the worktree path;
- if `next` was `lab_run`: say it is **cleared for Tony's first real paid run**, list the
  `tony_paid_run` items from the verdict, and say that run is `/lab-run` (Tony types it when ready).
  Stop there;
- if it ended at `stop`: say plainly it did not clear 80 after one fix and one rebuild, and what
  Tony could decide (adjust the plan with `/lab-plan`, try `--model`, or drop it);
- old worktrees from a rebuild are left in the project folder for Tony to delete himself.

## Known limits (honest)

- The OS sandbox guards the picked model's build. The fix round and the rebuild are done by
  `opus-standard` through Claude Code's own tools, not inside that sandbox: the git containment
  check still runs after them, but it only sees the worktree (Claude Code's permission prompts and
  `fs_guard.py` are the net for the real workspace there).
- `fs_guard.py` is wired as a Codex PreToolUse hook, so the builder cannot make subfolders inside
  the build folder. Flat plans are fine; a plan that names subfolders will need Tony to decide.
- Reads are not sandboxed: the builder (a remote model) sees any file it opens, like `/lab-plan`'s
  drafter does. The network is off for its commands, so nothing it reads can be sent anywhere else.
