# Quality Ledger — agent instructions (paste into workflow skills)

A quality ledger records what happened as structured, append-only lines beside the
human-readable Report Card. Run the right command at the right moment; the ledger is
the machine-readable record the readiness dashboard and autonomous queue will read.

## When to record

- **After every mechanical gate** — a script/a check that measured something:
  record `pass`, `fail`, or `error`, plus the measured value.

  ```
  quality_ledger.py check --ledger <ledger> --workflow <workflow_id> \
    --run "<run_id>" --step <step> [--level step] [--attempt N] \
    --result pass|fail|error [--measured V --threshold T --unit U] [--reason ...] \
    --artifact <the generated file you checked>
  ```

  `error` means the tool broke (provider 500, timeout). `fail` means the tool ran and
  the output failed the check.

  **Always pass `--artifact` (alias `--artifact-path`) with the path of the image or
  video the check measured.** Every check of that same file (scale check, hand-check,
  any other checker) then shares ONE attempt number; only a regenerated file gets a
  new one. The file is fingerprinted, so a file regenerated under the same name still
  counts as new. Leave `--artifact` off and each check is treated as its own attempt
  (the safe default: no evidence they looked at the same output), which looks like a
  retry. The path must be a readable file (exit 2 otherwise). `--from-report` picks
  the storyboard up from the scale report by itself. A checker that measures several values logs the
  deciding one (for example the worst ratio) and points `--report-path` or
  `--from-report Data/Scale_Check_<stem>.json` at the full report.

- **When you change or redo something before Tony sees it** — record the correction
  and link the event it fixes:

  ```
  quality_ledger.py self-correct --ledger <ledger> --workflow <workflow_id> \
    --run "<run_id>" --step <step> --reason "why you redid it" --corrects <event_id>
  ```

- **When Tony gives a grade or decision** — only Tony's own words can fill this, and
  they are kept verbatim. Ask which step if it is unclear, then:

  ```
  quality_ledger.py grade --ledger <ledger> --workflow <workflow_id> \
    --run "<run_id>" --step <step> --level sub_step|step|final \
    --grade <A+..F> [--decision accept|accept_with_flaws|redo] \
    --verbatim "<Tony's exact words>"
  ```

  `--level` is required (no default). Use `final` only for a grade on the finished
  video; a redo on a sheet, storyboard or other step is `step` or `sub_step`. Only
  final grades count toward readiness, so the wrong level corrupts the average.
  If Tony grades a run's final more than once (for example "C, redo", then "A,
  accept" after the fix), record every grade; only the latest one counts toward
  readiness and the earlier ones stay in the ledger as history.

  Tony can also type `grade: B+ accept step=<step> attempt=N <his words>` (or just
  `grade: A step=final`) in chat; the hook records it for you. If the hook says the
  note was NOT recorded, it says why: a wording problem (no `step=`, an ambiguous
  `A`, two grades) means ask Tony; a system problem (no ledger known, ledger locked)
  means record his exact words yourself as above. If a reminder was not really a
  grade, clear it with `quality_ledger.py pending --session <id> --clear`.

  If Tony approves a run whose grade is below 87, the writer sets
  `below_threshold_override: true` automatically and tells you the run will not count
  toward readiness. A bare "approved" is never a grade: ask Tony
  "A pass is technically a B+ / 87. What's your actual score?" and record nothing
  until he gives a letter.

- **When Tony edits or fixes an asset himself** (for example he uploads his own
  edited image and says "use this instead") — record what he changed:

  ```
  quality_ledger.py edit --ledger <ledger> --workflow <workflow_id> \
    --run "<run_id>" --step <step> --reason "what Tony changed" \
    [--artifact <path of his file>] [--corrects <event_id>]
  ```

- **Failure type (optional)** — on `check`, `self-correct`, `grade` or `edit`, add
  `--failure-type` with one value from the fixed list: `spatial_layout`, `scale`,
  `continuity`, `subject_count`, `plausibility`, `camera`, `motion`,
  `render_artifact`, `story`, `other`. Never free text. Leave it off when nothing
  failed. See README for what each one means.

- **Backdating (only when rebuilding history)** — `check`, `grade`, `self-correct`
  and `edit` accept `--at <ISO 8601 time with timezone>`, e.g.
  `--at 2026-09-19T15:37:00Z`. Leave it off for anything happening now.

## Rules

- Every write prints the new `event_id`; use it for `--corrects` (which must name an
  event already in that ledger).
- The ledger's folder must already exist (the tool never creates folders).
- Append-only. Never edit or rewrite the ledger; a correction is a new event.
- `mechanical_check` must not carry a grade; `director_judgment` must not carry a
  check; `agent_self_correction` needs a non-empty reason; `director_edit` is always
  actor Tony with a non-empty reason and no check or grade.
- You never infer a grade. If the hook reminds you that Tony gave a judgment, ask for
  the step and record his exact words.
