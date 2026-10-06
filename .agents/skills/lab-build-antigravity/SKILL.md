---
name: lab-build-antigravity
description: Antigravity only. Use when Tony types /lab-build [plan folder] (or asks to lab-build a locked plan) inside the Antigravity IDE agent chat. Runs the Gemini-side /lab-build script and reports its result. Not for Claude Code (use the lab-build skill there) or Codex (use lab-build-codex).
---

# /lab-build (Antigravity)

Full system design: `001_Architecture/Ongoing-Agent-OS-To-Do-List.md`, "Part 4". Build state and
file contract: `001_Architecture/Skills/lab/SKILL.md` and `001_Architecture/Skills/lab-build/SKILL.md`.
This skill is a thin trigger only — all the actual logic lives in `lab_build_gemini.py` (which runs
`lab_build.py` unchanged for the build and every score, and Gemini for the audit, the one fix round
and the one rebuild).

Tony's argument: $ARGUMENTS (a folder name under `001_Architecture/Lab/`, a full path, or empty =
the newest locked plan that has no build yet).

## Step 1 — Run the script

Run in the terminal (a full build can take over an hour: up to 30 minutes for the build, then the
Gemini steps; wait for it to finish, do not cancel it early):

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_build_gemini.py "<Tony's argument, or nothing>"
```

The last line of output is `LAB_BUILD_GEMINI_RESULT {json}`. To continue a project that stopped
(any exit below), run the same command with that project's folder: it carries on from where it
stopped and never repeats a finished step.

## Step 2 — Report to Tony

Show him the full printed report as-is (it already contains: which model built it, why, and the
cost; each Gemini step and its cost; the raw score split as checks /60, safety floor /15, Gemini
audit /25; any fix round or rebuild and the final score; the built folder and worktree paths;
`Build_Review.md`). Do not summarize it away.

If it says CLEARED, end by saying it is ready for Tony's first real run, `/lab-run`, which he types
when he is ready. If it ended at `stop`, say plainly it did not clear 80 and what he can decide.

## Exit codes that need a response, not a retry

- **8** = CONTAINMENT STOP. Show Tony the containment lines word for word, say no fix will be
  tried and the worktree is left for him to look at. Stop.
- **5** = over the spend cap. Show Tony the script's message and ask for a yes before raising it.
  Only after a clear yes, rerun with `--cap <new USD amount>`.
- **6** / **124** = the build failed or timed out. Name the log file, ask Tony whether to retry on
  another model (`--model <id>`, see `lab_build.py --list`). Never build it yourself.
- **7** = audit or score files have problems. If it says the score-before-edit rule broke, repair
  nothing: tell Tony exactly what it said and stop.
- **10** = a Gemini step failed. Name the log file and ask Tony whether to rerun.
- **9** = the `google-antigravity` SDK isn't installed. Tell Tony, do not install it yourself.
- **1** / **2** / **3** / **4** = setup problem (plan not verified, missing key, bad arguments).
  Show the message to Tony and stop.

## Never do

Never build, audit, fix or score anything yourself, and never write or edit any `Build_*` file,
`Acceptance_Checks.json`, `Plan_Locked.md` or anything in the build folder — only the script and
its own Gemini calls do that. Never run `frontier.py`, `delegate.py` or another harness for this.
Never edit `lab_build.py` or `lab_build_gemini.py` from inside a run of this skill. Never commit,
never delete (old worktrees stay for Tony).
