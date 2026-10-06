# Quality Ledger

A channel-agnostic, append-only quality log for Tony's Agent-OS pipelines, plus a
hook adapter that fills it without anyone remembering to call it.

Every line is one event with exactly one source:

- `mechanical_check` — a script or automated gate measured something
  (`pass` / `fail` / `error` plus the measured value). `error` means the tool broke
  (Kie 500, upscaler timeout); `fail` means the tool ran and the output failed the
  check (wrong hand, the van at 1.7x). That split is what Report Cards blur.
- `director_judgment` — Tony's grade and/or decision (`accept` /
  `accept_with_flaws` / `redo`), with his own words kept `verbatim`. Only Tony's own
  chat text can produce one; no script, check or agent inference fills these fields.
- `agent_self_correction` — the agent changed or redid something before Tony saw it,
  with a `reason` and a `corrects_event_id` link to the event it fixed.
- `director_edit` — Tony fixed the asset with his own hands (for example, he repainted
  the kangaroo shot's doorbell POV himself and said "Use the uploaded image as the new
  pOv panel"). `actor` is always `Tony`; `reason` (what he changed) is required; it
  carries no `check` and no `director` object. Optional: `corrects_event_id` (the
  version he fixed) and `artifact_path` (his edited file). His edited file is a new
  version of the step, so `edit` defaults to the latest attempt + 1, and a later grade
  attaches to it. A `director_edit` counts as an explained retry, like a
  self-correction. The name follows the existing `<who>_<what they did>` pattern
  (`mechanical_check`, `director_judgment`, `agent_self_correction`).

Grades attach to any level Tony comments on (`sub_step`, `step`, `final`). The
`grade` command has no default level: `--level` must always be given.

## Failure types (optional, fixed list)

Any event may carry `failure_type`, one value from this closed list. Free text is
rejected (`validate` and the writer exit 2; the CLI flag only accepts these values).
Leave it off when nothing failed. Pick the main cause when two fit.

| `failure_type` | Means | Real examples it covers |
|---|---|---|
| `spatial_layout` | Where things are or which way they face: side, depth, extent, mirror between views | driveway on the wrong side; car facing backwards; water tank/clothesline in the wrong spot; hedge cut short; feet on the wrong step |
| `scale` | Size wrong relative to people or the environment | van and characters 1.5-2x too large (Shot 07); driver "way larger"; courier too tall vs. the awning; oversized monkey |
| `continuity` | Something changes between frames or shots that should not | kangaroo there, gone, back again; food disappears in frames 4-6; driver steps back up then down |
| `subject_count` | A subject or object is missing, duplicated, or present when it should not be | two bicycles (Shot 05); kangaroo missing from frame 5; car missing from the driveway |
| `plausibility` | Breaks real-world logic | bike courier in the rural outback; driver leaves his whole bag; offset staircase; 10+ steps on a single-story house; no path from driveway to steps; floating bicycle with no kickstand |
| `camera` | Framing, drift in a locked shot, lens or perspective distortion, aspect ratio | camera drift/reframe (Shot 05); lawn rendered as a triangle; non-16:9 camera panel |
| `motion` | Movement or reaction looks staged or robotic | kangaroo frozen mid-hop for ~2 s; movers' "startled stare" |
| `render_artifact` | The output itself is broken | kangaroo merged into the mailbox post; storyboard grid reproduced as a tiled video; label/text bleed |
| `story` | Clean execution, weak storyline or hook (usually a director grade) | Shot 04 "narratively flat"; Shot 06 weak storyline |
| `other` | None of the above | anything else; if `other` keeps recurring, propose a new value |

Adding or renaming a value changes `FAILURE_TYPES` in `quality_ledger.py` and the
`failure_type` enum in `Event_Schema.json` together (a test checks they match).

## Files

| File | Purpose |
|------|---------|
| `quality_ledger.py` | Library + CLI (stdlib only) |
| `ledger_hook.py` | Fail-open hook adapter (`claude` / `codex` / `gemini`) |
| `Event_Schema.json` | JSON Schema for one event line; enums equal the code constants |
| `Grade_Scale.json` | Letter to number for averages (`B+` = 87) |
| `Readiness_Policy.json` | `threshold` 87, `window` 10, `min_runs` 3, `max_recent_redo` 0 |
| `Workflow_Registry_Example.json` | Skill name -> `workflow_id`, ledger path rule, steps |

## CLI

```
# record a mechanical check (--artifact = the generated file it measured; every
# check of that same file shares one attempt, see "Attempt numbers" below)
quality_ledger.py check --ledger <ledger> --workflow neon_parcel_longform \
  --run "<run>" --step storyboard.scale --result fail \
  --measured 1.7 --threshold 1.0 --unit x_scale --reason "van too big" \
  --artifact Storyboard_Clip2_v1.png

# map an existing check_storyboard_scale.py report into a line (the report's own
# storyboard + storyboard_sha256 become the artifact automatically)
quality_ledger.py check --ledger <ledger> --workflow neon_parcel_longform \
  --run "<run>" --step storyboard.scale --from-report Data/Scale_Check_X.json

# record Tony's grade (actor is forced to Tony; verbatim is required;
# --level is REQUIRED with no default, so a forgotten level is an error (exit 2),
# never a step redo silently counted as a final-video grade)
quality_ledger.py grade --ledger <ledger> --workflow neon_parcel_longform \
  --run "<run>" --step final --level final --grade B+ --decision accept \
  --verbatim "that's a B+"
quality_ledger.py grade --ledger <ledger> --workflow neon_parcel_longform \
  --run "<run>" --step environment --level step --decision redo \
  --verbatim "You have the driveway on the wrong side" --failure-type spatial_layout

# record an agent self-correction (actor is "agent"; failure type optional on
# check/grade/self-correct/edit)
quality_ledger.py self-correct --ledger <ledger> --workflow neon_parcel_longform \
  --run "<run>" --step storyboard.scale --level step --reason "shrunk the van" \
  --corrects <event_id> --failure-type scale

# backdate any of check / grade / self-correct / edit when rebuilding history
# (ISO 8601 with a timezone; stored as UTC; garbage or no timezone exits 2)
quality_ledger.py grade --ledger <ledger> --workflow neon_parcel_longform \
  --run "<run>" --step environment --level step --decision redo \
  --verbatim "..." --at 2026-09-19T15:37:00Z

# record that Tony edited the asset himself (actor is forced to Tony; reason required)
quality_ledger.py edit --ledger <ledger> --workflow neon_parcel_longform \
  --run "<run>" --step environment.pov --reason "Tony repainted the hedge himself" \
  --artifact Character_Sheets/POV_Panel_Final_Tony_Edit.png --failure-type spatial_layout

# validate (exit 0 valid, 2 invalid)
quality_ledger.py validate <ledger>

# per-workflow readiness + per-step activity (fixed --json shape is the future
# dashboard input; plain text and --markdown print the same two sections)
quality_ledger.py report <ledger> --threshold 87
quality_ledger.py report <ledger> --threshold 87 --json

# flat, fixed-column export for a table or dashboard (never parses nested JSON)
quality_ledger.py export <ledger> --format csv
quality_ledger.py export <ledger> --format jsonl

# dry-run Report Card backfill (never edits the Report Card)
quality_ledger.py backfill-report-cards <report_card.md> --workflow neon_parcel_longform

# list unresolved director captures for a session (with Tony's words), or clear them
quality_ledger.py pending --session <session_id>
quality_ledger.py pending --session <session_id> --clear
```

There is no delete or rewrite command. Corrections are new events.

## Readiness

The report rolls up the most recent `window` (10) graded runs per workflow against
`threshold` (87, exactly B+). A workflow is `READY` when it has at least `min_runs`
(3) counted runs and the mean numeric grade meets the threshold.

**One final per run (Tony, 2026-10-06).** Only the LATEST final-level grade of a
run counts. If Tony says "C, redo" on a run's final video, the agent fixes it, and
Tony then says "A, accept" on that same run, the run counts once, as A; the earlier
C is superseded, not averaged in and not counted as a redo. Rules:

- "Latest" is by `timestamp` (real UTC time, so a backdated `--at` line sits where
  it really happened). Two finals on one run with the very same timestamp: the later
  line in the file wins.
- The finals considered are the same as before: any final with a letter grade, plus
  a final `redo` with no letter. A later gradeless `redo` supersedes an earlier
  accepted grade (Tony rejected it after all). A decision-only `accept` with no
  letter is not a grade and supersedes nothing; ask Tony for the letter.
- The below-threshold override (next paragraph) is applied after this, to each run's
  latest final only. An earlier override on a run that was later fixed and graded A
  no longer counts in `overridden_passes`; a "C, redo" followed by "C+, ship it
  anyway" counts as one overridden pass and zero redos.
- `--window N` means the N most recent **runs** (ordered by each run's latest final),
  not the N most recent grade lines.
- Nothing is removed: the superseded line stays in the ledger file, in `export`, and
  in `steps` (first vs latest grade of that step). `step_activity` is step-level
  activity, not final grades, so it is unaffected and still counts that redo.

A run Tony lets through below the bar ("C+, ship it anyway") is logged in full:
`grade` and the hook derive `director.below_threshold_override: true` when the
decision is `accept` / `accept_with_flaws` and the grade is strictly below the
threshold. That final is left out of `n`, `mean` and the readiness verdict and is
counted in `overridden_passes` instead. Tony never types the flag.

## Attempt numbers (Tony, 2026-10-06)

An attempt number only goes up when something is actually regenerated (a new
image or video), not every time a check runs.

- `check --artifact <file>` (alias `--artifact-path`) fingerprints the file it
  measured (sha256, stored as `artifact_path` + `artifact_sha256`). A check whose
  fingerprint matches an event already on the step's latest attempt shares that
  attempt: a scale check and a hand-check on the same storyboard are both attempt 3.
  A different fingerprint is a new attempt, including a file regenerated in place
  under the same name (that is why the content is fingerprinted, not just the name).
  A fingerprint that only matches an older attempt is also a new attempt.
- `check --from-report` uses the report's own `storyboard` and `storyboard_sha256`
  (`check_storyboard_scale.py` already writes them), so a scale check from its
  report and a manual check with `--artifact` on the same storyboard collapse with
  no extra flags. `--artifact` that is not the file the report measured is exit 2.
- `edit --artifact` also fingerprints Tony's file when it is readable, so a check on
  his edited image shares his edit's attempt.
- **Safe default:** a check with no `--artifact` is its own attempt (latest + 1) and
  the CLI prints a note saying so. With no evidence that two checks looked at the
  same output they are never merged. An `--artifact` that is not a readable file is
  exit 2 (a mistyped path would otherwise look like evidence).
- `--attempt N` still overrides all of this. The number is still decided under the
  ledger lock, so concurrent checks on one file all get the same attempt.
- Lines already in a ledger keep the attempt they were written with (append-only);
  this changes how new checks are numbered, not old lines.

Effect on the report: `step_activity.max_attempt` and `unexplained_retries` now
follow real regenerations. Two different checkers on one image used to read as
attempts 1 and 2 plus one unexplained retry; now both are attempt 1, no retry.
`mech_fail` / `mech_error` still count every failing check line (two checkers that
both fail on one image are 2 fails on 1 attempt).

`export` has a `failure_type` column (last column). The `report --json` shape is:

```json
{"workflows": {"<workflow_id>": {"n": 3, "mean": 88.0, "ready": true, "why": "",
   "redo": 0, "mech_fail": 1, "mech_error": 1, "self_corrections": 1,
   "director_edits": 1, "unexplained_retries": 0, "overridden_passes": 1}},
 "steps": [{"workflow_id": "...", "run_id": "...", "step": "...",
   "first_attempt": 1, "first_grade": "C-", "latest_attempt": 2,
   "latest_grade": "B+", "delta": 17}],
 "step_activity": [{"workflow_id": "neon_parcel_longform", "step": "environment",
   "max_attempt": 8, "redos": 8, "mech_fail": 0, "mech_error": 0,
   "self_corrections": 7, "director_edits": 0}]}
```

`step_activity` (added 2026-10-05, additive) is where the iteration pain shows. One
row per `(workflow_id, step)` seen in the ledger, across every run and every level:
`max_attempt` is the highest attempt logged for that step, `redos` counts
`director_judgment` lines with `decision: redo` at that step (any level),
`mech_fail` / `mech_error` count failed / broken `mechanical_check` lines,
`self_corrections` and `director_edits` count those sources. It is visibility only
and never changes `n`, `mean` or `ready`. It reads every line as written, so the
"one final per run" rule does not change it, and since 2026-10-06 its `max_attempt`
reflects regenerations rather than check count (see Attempt numbers). The workflow-level `redo` field still
counts **final-level** redos only (the readiness math is final-only by design), so
it can read 0 while `step_activity` shows many step redos; the plain-text and
markdown reports label it `final_redo` / `final redos` for that reason. On the real
kangaroo shot (`Demo_Kangaroo_Full_Ledger.jsonl`) the final grade was an A with
`redo` 0, while `step_activity` shows 23 step redos (environment 8, storyboard 6,
environment.pov 4, environment.front_view 3, delivery driver sheet 2).

`director_edits` counts Tony's own `director_edit` lines per workflow. Like
`self_corrections` it is a visibility counter only: it never changes `n`, `mean` or
`ready`. `director_edit` lines also show up in `export` and count as explained retries.

`actor` per source says who or what did it, in plain terms: `Tony` for
`director_judgment` and `director_edit` (forced), `agent` for
`agent_self_correction`, and the checker for `mechanical_check`. A manual `check`
records `mechanical_check`; `check --from-report` records the report's own `tool`
field when it has one, else `check_storyboard_scale` (the only report shape that
path accepts). It is never `agent` (a check is a measurement, not an agent's
judgment call) and never `quality_ledger.py` (the writer, not the checker).

`timestamp` is the current UTC time unless `--at` is given. `--at` exists for
rebuilding history from an old session; the kangaroo demo uses the real times from
the shot's `Iteration_Notes.md` (minute precision; a few agent actions that sit
between two of Tony's timestamped messages carry an approximate time).

`check.measured` and `check.threshold` are pinned to number-or-null so a numeric
dashboard column never changes type between lines; a checker with several values
logs the deciding one and points `report_path` at its full report.

## The hook (auto-invocation)

`ledger_hook.py --harness claude|codex|gemini --event skill|prompt|stop` follows the
house hook pattern (fail-open, 1.0 s wall clock). It writes only a session marker in
the system temp dir and the ledger path that marker names.

- `skill` — a registered skill starts a ledger (writes the marker, injects the four
  commands into context: `check`, `self-correct`, `grade`, and `edit` for when Tony
  edits the asset himself).
- `prompt` — a `grade:` shorthand with `step=` writes a director line verbatim
  (for example `grade: B+ accept step=character_sheet.motoboy attempt=6 too stiff`,
  or just `grade: A step=final`). Its level comes from the step Tony typed:
  `step=final` is `final`, a dotted step is `sub_step`, anything else is `step`.
  With no `attempt=` the grade attaches to that step's latest attempt (like the CLI).
  How it reads the note: the grade and decision come only from the words right after
  `grade:` (up to the first ordinary word), so his comment never changes them
  (`grade: B+ accept step=final no need to redo` is accept). Grades are whole words
  in any case (`a+`, `B-`, `B plus`); `Car` / `Dog` are never grades. A bare `A`
  followed by an ordinary word (`grade: A great job`) could be the word "a", so it is
  asked about, never guessed.
  **The one rule:** a `grade:` note is either recorded exactly, or NOT recorded with
  a visible reminder saying why (no `step=`, ambiguous `A`, two grades, a bad
  `attempt=`, a letter not on the scale, no ledger known, ledger locked or its
  folder missing). It is never dropped silently and never written half-right.
  A strong signal in plain chat (a letter grade, `redo`, `accept with flaws`, or
  `approved`) only adds a pending reminder; its step is unknown, so any grade Tony
  then gives on that run (at any step) clears it. Bare `approved` is never treated as
  a passing grade ("A pass is technically a B+ / 87. What's your actual score?").
  A reminder that was not really a grade ("Plan B") is cleared with
  `quality_ledger.py pending --session <id> --clear`.
- `stop` — asks Tony for pending grades (non-blocking) and reports silent retries
  for the current run only.

Where the hook writes: a production workflow (ledger path with `{run_id}`) writes
only when the session's working folder is inside that production and its
`Data/History/` folder already exists; at the workspace root it records nothing on
its own and says so (it used to invent run "Agent-OS" and create folders for it). A
central-ledger workflow at the workspace root gets run `<date>-<workflow_id>`. A
mistyped hook command line still exits 0 (exit 2 would block Tony's prompt).

## Hardening rules (2026-10-06 bug hunt)

- The ledger never creates folders: `--ledger` must point into an existing folder.
- Bad CLI input is exit 2 with a clear message, never a silent default: `--attempt`
  must be 1 or more, `--measured` / `--threshold` finite numbers, ids non-empty,
  `--at` a real past time, `--corrects` an event_id that is in the ledger,
  `--from-report` never combined with `--result` / `--measured` / `--threshold` /
  `--unit`. `--grade b+` is read as `B+`. Every write prints the new `event_id`.
- Auto-numbered attempts are chosen while holding the file lock (no two writers get
  the same number). A file whose last line lost its newline is repaired by the next
  append instead of being glued to it.
- `validate` lists every bad line with its real line number, rejects duplicate
  event_ids and wrong field types, and warns about a `corrects_event_id` that points
  nowhere. `report` and `export` refuse a ledger with any invalid line (exit 2) and
  refuse the same ledger listed twice (it would double every grade).
- Readiness: a final `redo` with no letter grade still counts as a redo, and the
  READY test uses the exact mean (86.97 is not 87 even though it prints as 87.0).
  Since 2026-10-06 only each run's latest final counts (see Readiness).
- `backfill-report-cards` reads only the card's own first `Grade:` label (line start
  or a `| Grade |` table row, same line only), refuses unclear values (`E`, `B+/A-`,
  frontmatter that disagrees with the body), treats blank / `TBD` as not graded yet
  (never falling through to a section's grade), keeps going past a missing file, and
  never writes the same card twice.

Default mode is ask (non-blocking); `--block` is opt-in.

## Adding a workflow

One registry entry, no code:

```json
"My_Skill_Name": {
  "workflow_id": "my_workflow",
  "ledger": "001_Architecture/Logs/Quality_Ledger.jsonl",
  "steps": ["brief", "draft", "final"]
}
```

See `Workflow_Registry_Example.json`. Copy it to `Workflow_Registry.json` (wiring,
Tony-approved) and add only the workflows Tony wants covered first.

## Safety

Stdlib only, no keys, no network (`urllib`, `requests`, `http`, `socket` are never
imported). Nothing is published, uploaded or sent. The ledger never triggers paid
calls; it only records them (`cost_usd` is optional). Append-only, so earlier bytes
are never touched. The build touches no existing file; hook registration, skill edits
and the promotion move into `001_Architecture/Tools/Quality_Ledger/` are wiring steps.
