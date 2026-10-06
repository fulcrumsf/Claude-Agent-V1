---
name: lab-run
description: Claude Code only. Runs when Tony types /lab-run [project] - Tony's own first real use of a build that /lab-build already cleared (score 80+), with real network and real paid APIs if the tool needs them, no sandbox. He tries it, gives notes and a 0-100 grade each round (logged to Run_Log.jsonl); below 80 this Claude Code session fixes the build folder in place and he tries again, until 80+ clears it for /lab-promote. Fixes never go back to /lab-build or any OpenRouter model.
argument-hint: [project folder name, or empty for the newest build waiting for /lab-run]
disable-model-invocation: true
---

# /lab-run

Third command of the `/lab` system (see `001_Architecture/Skills/lab/SKILL.md`). `/lab-build` proved
the plumbing on paper; `/lab-run` is the first real take: Tony uses the thing for real, says what he
likes and doesn't, grades it, and you fix it between takes until he grades it 80+.

You, the Claude Code session, run this whole command yourself, in Tony's normal session, with your
normal tools. It is deliberately NOT sandboxed (the opposite of `/lab-build`): real network, real
files, real API keys, exactly like Tony testing any pipeline he builds. A tiny script only does the
bookkeeping (is it cleared, append the grade, fingerprint the folder). Never commit, never delete.

Tony's argument: $ARGUMENTS (a folder name under `001_Architecture/Lab/`, a full path, or empty =
the newest project `/lab-build` cleared that `/lab-run` has not cleared yet; say which one you used).

Script: `python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_run_log.py`
(below just `lab_run_log.py`). It never calls a model, the network, or a paid API.

## The locked rule (never break it)

**Every fix during `/lab-run` is made by the harness: this Claude Code session, or an `opus-standard`
subagent it spawns. Never by `/lab-build` or the picked OpenRouter model, ever.** Concretely, during
`/lab-run` you never run `lab_build.py` in any mode (not even `--reverify`), never run
`lab_plan_draft.py` or its picker, never use `delegate.py`, Jev, OpenRouter, `codex exec`, or another
harness to make a change. Nothing here spends from the `/lab` OpenRouter budget: the $2/project cap
covers only the one plan + build pass; revision runs on Tony's Claude plan. (Tony, 2026-09-30: "for
consistency, I would just like to keep any iteration adjustments done by the harness model.")

## Files this command produces

All in the SAME project folder as `/lab-plan` and `/lab-build` (`<PROJECT_DIR>`). No new folder, no
new worktree.

| File | Written by | Rule |
|------|------------|------|
| `Run_Log.jsonl` | script (`log`) | One line per round, appended, never rewritten. Each line carries the hash of the log before it, so `status` reports if an earlier line was edited later (a warning to show Tony, not a lock). |
| the build folder (`BUILD_DIR`, inside `Build_Worktree_<n>/`) | you / `opus-standard` | Fixes are edited in place here, between rounds. Nothing outside it. |

Never touched by this command: `Plan_Locked.md`, `Acceptance_Checks.json`, `Draft_*`, `Score.json`,
`Review.md`, `Build_Meta.json`, `Build_Verdict.json`, and every `Build_Score*` / `Build_Audit*` /
`Build_Review.md` file. The `/lab-build` score stays what it was; Tony's grades live only in
`Run_Log.jsonl`.

`Run_Log.jsonl` is Tony grading the TOOL that was built. It is its own simple log and shares nothing
with any log the tool itself writes (for example Quality_Ledger's own `Quality_Ledger.jsonl` and
event schema): never write a `/lab-run` grade into a tool's own log, never read a tool's log as if
it were `Run_Log.jsonl`. One line looks like:

```
{"log": "lab_run/v1", "round": 2, "t": "2026-10-04T10:12:00", "project": "<folder>",
 "build_dir": "<path>", "built_by": "<model from /lab-build>", "build_total": 90.0,
 "changes_before_this_try": "what the harness changed since round 1, plain words ('' on round 1)",
 "folder_changes_since_last_round": {"added": [], "removed": [], "modified": ["x.py"]},
 "tried": "what Tony tried", "notes": "Tony's own words", "grade": 85, "passed": true,
 "folder_sha256": "<fingerprint of the folder as graded>", "manifest": {"x.py": "<sha256>"},
 "prev_log_sha256": "<hash of the log before this line>"}
```

Each grade also goes to the shared `/lab` log (`~/Library/Logs/Agent-OS-Lab.jsonl`, event
`lab_run_grade`, with the `/lab-build` score beside it): that is the calibration data for checking
the automated 80 against Tony's own 80 over the first 5-10 builds.

## Step 1 - Is it cleared? (script)

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_run_log.py status "<PROJECT or empty>"
```

Last line: `LAB_RUN_STATUS {json}`.
- Exit `2`: `/lab-build` has not cleared it. Show Tony the `why` line (it names the exact `/lab-build`
  step still needed, or that the build ended without clearing 80) and stop.
- Exit `1`: no such project, or nothing is waiting for `/lab-run`. Say so and stop.
- Exit `0`: note `build_dir`, `worktree`, `build_total`, `built_by`, `tony_paid_run`, `rounds`.
  - `rounds` not empty = a loop is already under way: tell Tony which round is next and his latest
    grade, then carry on.
  - `cleared_for_promote: true` = Tony already passed it and the folder has not changed since: say it
    is ready for `/lab-promote` and stop, unless Tony says he wants another round.
  - `log_problems` not empty = tell Tony plainly that an earlier line of `Run_Log.jsonl` was edited
    after it was written. Repair nothing; carry on only if he says so.

## Step 2 - Show Tony how to try it for real

What "try it" means is different for every build, so never guess and never hardcode it. Read the
whole `<PROJECT_DIR>/Plan_Locked.md` (look for its goal, how-to-verify, steps, spend and safety
gates, and wiring sections) and the build folder's own README or instructions if it has one, plus
`tony_paid_run` from the status. Then tell Tony, short and plain, a blank line between points:
- where the built thing is: the full `build_dir` path (inside the worktree). It runs from there; do
  not copy it into the real workspace, that is `/lab-promote`'s job;
- exactly how to use it for real: the command(s) to run, bash-fenced so he can run them as-is, or
  the steps to follow if it is not a command;
- what it will cost, if anything, and where the tool's own cost or selection pauses are;
- what to look at, from `tony_paid_run`;
- on round 2+, what changed since his last try (the fix you just made).

Ask whether he wants to run it himself or wants you to run it. If you run it: use Bash in this
session, stop at every one of the tool's own cost-estimate and selection pauses and wait for his
yes, and never publish, send or upload anything without his explicit yes. Paid API spend here is
the tool's own normal spend behind its own gates; `/lab-run` adds no spend cap of its own.

This is a real, uncontained run. Many workspace scripts use the absolute Agent-OS path, so the tool
may read and write the real workspace while it runs, like any pipeline test. Say so if the plan
shows it writes outside its folder.

**When real use needs wiring** (a hook, a skill edit, a TOOLBOX line, another pipeline calling it):
that wiring edits existing files, which the plan's "Wiring (Later, Tony-Approved)" list reserves
for a Tony-approved diff. Prefer a standalone real try first (run the tool directly on real input).
If Tony wants it wired to try it properly, show him the exact diff of each existing file first and
make that one change only after his explicit yes; record it in the next `--changes`. Never wire
anything on your own.

## Step 3 - Notes and grade (script)

When Tony reports back, ask in one message for (a) his notes, what he liked and what he didn't, and
(b) a grade 0-100 (same scale as `/lab-build`: 80 or more passes, below 80 does not). Use his own
words; never suggest a grade or soften his notes. Then append the round:

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_run_log.py log "<PROJECT_DIR>" --tried '<what he tried>' --notes '<his notes>' --grade <N> --changes '<what you changed before this try, empty on round 1>'
```

Single-quote each value (a `'` inside becomes `'\''`). Last line: `LAB_RUN_LOGGED {json}` with
`round`, `grade`, `passed`, `next`. Exit `1` = bad grade or missing notes: ask Tony again, nothing
was written. Exit `2` = the `/lab-build` clearance is gone (show `why`, stop). Log each round once;
if a value was wrong, tell Tony and log a corrected round rather than editing the file.

## Step 4 - Pass, or fix and go again

**`passed: true` (80+):** go to Step 5.

**`passed: false` (below 80):** fix it yourself, in place, from Tony's notes:
- Where: only inside `build_dir`. Never edit any file listed under "Never touched" above, never
  touch the real workspace's copy of anything, never commit (not even to the lab branch).
- Who: you, with Edit / Write / Bash, for small clear fixes. For a tricky or multi-file fix, spawn
  `opus-standard` (Agent tool, `description: "Fix /lab-run round <n>"`) with Tony's notes, the
  `build_dir`, `Plan_Locked.md`, and the same rules as this list. Both are the harness. Nothing else
  is allowed (see the locked rule).
- No deletes, renames or new folders (Tony does those; `fs_guard.py` blocks them anyway). If a file
  should go, tell Tony the exact command to run himself.
- If his notes ask for something the locked plan ruled out, or a redesign bigger than a fix, say so
  plainly and let him choose: keep fixing here, or start a fresh `/lab-plan`.
- Check the fix before handing it back: run the build's own tests if it has any, then the free
  regression smoke test (same network-off sandbox `/lab-build` used, writes nothing, never a new
  score):

  ```
  python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_run_log.py checks "<PROJECT_DIR>"
  ```

  `LAB_RUN_CHECKS` gives `passed` / `total` / `failed`. A check can now fail only because Tony's real
  run left output in the folder; say which, don't hide it.
- Tell Tony in plain words what you changed (file, one line each) and the smoke-test result, then
  go back to Step 2 for his next real try. The next `log` call's `--changes` is that same summary.

There is no round limit (Tony's rule: repeat until 80+). If two or three rounds go by without the
grade moving, say so honestly and ask whether to keep going, rethink the plan, or drop it.

## Step 5 - Report to Tony

Short, plain words, a blank line between points:
- the grade this round and how many rounds it took (grades in order), next to the `/lab-build` score;
- what changed across the rounds, one or two lines;
- the built folder's full path and `Run_Log.jsonl`'s path;
- if it passed: **cleared for `/lab-promote`** (Tony types it when he wants it promoted). Stop there.
  Any later edit to the folder un-clears it (`status` shows `cleared_for_promote: false` until a new
  round passes).

## Known limits (honest)

- Fixes sit uncommitted in the worktree. The lab branch still holds `/lab-build`'s version, so
  `/lab-promote` first commits the folder as it is on disk to the lab branch (checked against the
  passing round's fingerprint), and only runs when `status` says `cleared_for_promote: true`
  (latest round 80+ and the folder unchanged since that grade).
- `folder_changes_since_last_round` lists every file that differs, including output the tool wrote
  into its own folder during a real run, not only your edits.
- `Run_Log.jsonl` is append-only by convention, not locked; an edit is detected, not prevented.
- Claude Code only for now: no Codex or Antigravity trigger. Another harness running this would
  break the locked rule's "same harness every round" consistency.
