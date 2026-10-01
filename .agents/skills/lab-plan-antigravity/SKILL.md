---
name: lab-plan-antigravity
description: Antigravity only. Use when Tony types /lab-plan <question> (or asks to lab-plan something) inside the Antigravity IDE agent chat. Runs the Gemini-side /lab-plan script and reports its result. Not for Claude Code (use the lab-plan skill there) or Codex.
---

# /lab-plan (Antigravity)

Full system design: `001_Architecture/Ongoing-Agent-OS-To-Do-List.md`, "Part 4". Build state and
file contract: `001_Architecture/Skills/lab/SKILL.md`. This skill is a thin trigger only — all the
actual logic lives in `lab_plan_gemini.py`, which is shared with every other way of running this
command (a terminal, this skill, or anything else that calls it the same way).

Tony's question: $ARGUMENTS

If the question above is empty, ask Tony what he wants planned and stop.

## Step 1 — Run the script

Run in the terminal (it can take up to ~20 minutes between the draft and the review; wait for it
to finish, do not cancel it early):

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_plan_gemini.py "<Tony's question>"
```

Quote the question safely (escape any double quotes in it). The last line of output is
`LAB_PLAN_GEMINI_RESULT {json}`.

## Step 2 — Report to Tony

Show him the full printed report as-is (it already contains: which model drafted it and what it
cost, which Gemini model reviewed it and its cost, the raw draft's score out of 100 and whether it
was locked or rewritten, how many acceptance checks were written, the folder path, `Review.md`,
and the locked plan itself). Do not summarize it away — the report is already written for him.

End by saying the plan is ready for `/lab-build`, which is not built yet.

## Exit codes that need a response, not a retry

- **5** = over the spend cap. Show Tony the script's message and ask for a yes before raising it.
  Only after a clear yes, rerun with `--cap <new USD amount>`.
- **6** / **124** = the draft failed or timed out. Tell Tony, name the log file from the error line,
  and ask whether to retry on another model (`--model <id>`, see `lab_plan_draft.py --list`). Do
  not fall back to writing the plan yourself.
- **7** = verify found problems, or the review failed in a way that needs Tony. If the problems
  name `Score.json` or `Draft_Raw.md`, do NOT try to fix it — rewriting the score now would break
  the score-before-edit rule. Tell Tony exactly what the script said and stop.
- **9** = the `google-antigravity` SDK isn't installed. Tell Tony, do not try to install it yourself
  mid-command.
- **1** / **2** = setup problem (missing key, bad arguments). Show the message to Tony and stop.

## Never do

Never write the plan, the score, the acceptance checks, or `Review.md` yourself — the script and
its own call to Gemini's reviewer are the only things allowed to write those files. Never edit
`lab_plan_draft.py` or `lab_plan_gemini.py` from inside a run of this skill. Never commit anything.
