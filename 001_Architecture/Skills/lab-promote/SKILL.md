---
name: lab-promote
description: Claude Code only. Runs when Tony types /lab-promote [project, or his own description of what is being promoted] - the last /lab step. Takes a build Tony graded 80+ in /lab-run, commits its final on-disk state (the /lab-run fixes) to its own lab branch, checks that ONE folder out into the real workspace home named in Plan_Locked.md, adds the TOOLBOX.md entry, wikifies and cross-links it into 000_Wiki/ (ingest-skill convention), runs graphify update on the affected domains, then commits only those changes to main and pushes. Tony typing it is the approval. Cleanup commands are printed for Tony, never run.
argument-hint: [project folder name, or Tony's own words for what is being promoted]
disable-model-invocation: true
---

# /lab-promote

Fourth and last command of the `/lab` system (see `001_Architecture/Skills/lab/SKILL.md`). `/lab-plan`
wrote the recipe, `/lab-build` cooked it in a sealed kitchen, `/lab-run` was Tony's real tasting until
he graded it 80+. `/lab-promote` plates it: the one approved folder moves into the real workspace,
gets its TOOLBOX line and wiki page, the graphs are refreshed, and it is committed and pushed.

You, the Claude Code session, run this whole command in Tony's normal session (never a sandbox, never
`/lab-build`'s worker, never `delegate.py`, Jev, OpenRouter or another harness). A script does every
git step and the checks; you write the two things that need judgment: the TOOLBOX.md entry and the wiki
page with its cross-links.

Tony's argument: $ARGUMENTS (a folder name under `001_Architecture/Lab/`, a full path, Tony's own
description such as "the quality ledger we built in lab", or empty = the one project that is cleared).

Script: `python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_promote.py`
(below just `lab_promote.py`). It never calls a model or a paid API. Its only network call is the
final `git push`.

## The locked rules (to-do list, Part 4, "`/lab-promote` scope confirmed", 2026-09-30)

- **Approval:** "no separate approval gate - Tony typing `/lab-promote` with his own description of
  what's being promoted ... IS the approval; the command itself is the diff review, nothing further
  to show him first." So: show him the review from Step 1, then keep going. Never stop to ask "shall
  I go ahead?", and that includes the commit and the push to GitHub. Stop only where the script
  refuses (an exit code below) or the project is ambiguous (Step 0).
- **Only promote what passed:** the latest `/lab-run` grade in `Run_Log.jsonl` must be 80+ and the
  folder must be exactly what Tony graded. The script enforces both; never work around a refusal.
- **Scope is exactly:** the one folder, the TOOLBOX.md entry, the wiki page + cross-links + wiki log +
  wiki index, `graphify update`, one commit on main, the push. Everything else in the plan's "Wiring
  (Later, Tony-Approved)" list (hooks, `~/.claude` / `~/.codex` / `~/.gemini` settings, pasting blocks
  into other skills, `Skill-Index.md`, live registry copies, backfills) stays OUT: each one is still a
  separate change Tony approves as a diff. The script returns that list; hand it to him at the end.
- **Cleanup is never automatic:** the script prints the `git worktree remove` and `git branch -D`
  commands for Tony to run himself when he is happy. Never run them, never run any delete, never
  force-push, never `reset --hard`.
- **Do not edit the promoted folder.** A change to the tool itself is a `/lab-run` fix round, not a
  promotion edit (the script refuses to commit a folder that differs from what Tony graded).
- **No new folders** except the one promoted folder, which the script creates from the locked plan's
  path. Wiki pages go in an existing `000_Wiki/` category folder; if none fits, ask Tony.

## Files this command produces

| Where | Written by | What |
|-------|------------|------|
| `<PROJECT_DIR>/Promote_Meta.json` | script | Stage (`checked_out` / `committed` / `pushed`), lab commit, destination, what was committed, push result, the main-repo snapshot used to tell your edits from other sessions' |
| `<destination>` (e.g. `001_Architecture/Tools/Quality_Ledger/`) | script (`git checkout <lab commit> -- <folder>`) | The promoted folder, exactly as Tony graded it |
| `TOOLBOX.md` | you | One new entry |
| `000_Wiki/<Category>/<Page>.md`, `000_Wiki/index.md`, `000_Wiki/log.md`, related wiki pages | you | Wiki page, index line, log entry, cross-links |
| one commit on `main`, pushed | script | Only the folder + your edits to the files you list |

Untouched: everything else in the project folder (`Plan_Locked.md`, scores, `Run_Log.jsonl`, ...),
and the worktree except one commit on its own lab branch.

## Step 0 - Which project

If Tony named a folder or path, use it. If he described it in words or gave nothing:

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_promote.py list
```

`LAB_PROMOTE_LIST` gives every built project with its plan title, promoted path, grades and
`cleared_for_promote`. Match his words to the title or path. Exactly one match = use it and say which.
None cleared = say so and point to `/lab-run`. Several plausible = list them and ask which (this is
naming the dish, not an approval step).

## Step 1 - Gate and review (script, read-only)

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_promote.py plan "<PROJECT>"
```

Writes nothing. Last line `LAB_PROMOTE_PLAN {json}`.
- Exit `2`: not cleared. Show the `why` word for word (it names the step: no `/lab-run` round yet,
  latest grade below 80, folder changed after the passing grade, or `/lab-build` not cleared) and stop.
  If it says `Run_Log.jsonl` was edited later, show Tony; rerun with `--accept-edited-log` only if he
  says the grades are right.
- Exit `4` / `5`: show every `problems` line and stop (5 = secret scan hit; it names the file and the
  kind of secret, never the value).
- Exit `1`: already promoted, or no such project. Say so and stop.
- Exit `0`: show Tony this review, short and plain, then go straight on to Step 2 without waiting:
  - the literal destination path (`destination`): this creates that one new folder;
  - the files going in (`files`), and the `/lab-run` fixes that first get committed to the lab
    branch (`lab_run_uncommitted`; empty = nothing to commit, no empty commit is made);
  - anything left behind (`not_promoted_gitignored`, `worktree_changes_outside_folder_not_promoted`);
  - his grades (`grades`) next to the `/lab-build` score (`build_total`);
  - `main.unpushed_commits`: if not empty, say the push will also publish those earlier local commits.

## Step 2 - Commit the fixes to the lab branch, then check the folder out (script)

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_promote.py checkout "<PROJECT>"
```

Why this order (the gap found 2026-10-03): `/lab-build` committed the RAW build to
`lab/<project>/wt<n>`, but `/lab-run`'s fixes were edited in place and left uncommitted. Checking that
branch out as-is would promote stale, pre-fix code. So the script first commits the build folder
exactly as it is on disk to its OWN lab branch (never main, never pushed, only if something changed),
checks that commit file by file against Tony's passing `Run_Log.jsonl` fingerprint, then runs
`git checkout <that commit> -- <folder>` in the real workspace. A pathspec checkout cannot bring in
anything outside that one folder.

Last line `LAB_PROMOTE_CHECKOUT {json}` (also saved as `Promote_Meta.json`). Exit `0` = the folder is
in place; note `destination`, `files`, `wiring_left_for_tony`. Rerunning after a half-finished run
resumes (`resumed: true`), no second commit. Exit `6` = the commit did not match what Tony graded:
show him, stop. Other exits as in Step 1.

## Step 3 - TOOLBOX.md entry (you)

Read the README (and `Plan_Locked.md`'s Goal) in the promoted folder, then add one entry to
`/Users/tonymacbook2025/Documents/Agent-OS/TOOLBOX.md` in its existing style:
- under the `## ` section that matches the tool's job (read the section headings first; if nothing
  fits, the closest one, not a new section unless Tony asks);
- heading like `### <Tool Name> (\`<promoted path>/\`, promoted from /lab <YYYY-MM-DD>)`;
- 3-5 bullets: **Purpose**, **Usage** (the real commands from the README, with the promoted path),
  **When to use**, and **Wiring still pending** (one line naming the items from
  `wiring_left_for_tony` other than the folder move and TOOLBOX itself, or "none").

Before editing, run `git -C /Users/tonymacbook2025/Documents/Agent-OS diff TOOLBOX.md`. If another
session has uncommitted edits in the file, place your entry a few lines away from them: the final
commit takes only your lines, and an edit touching or right next to someone else's uncommitted lines
cannot be separated (the script then stops with exit `7` and commits nothing).

## Step 4 - Wiki page, cross-links, log, index (you; the `ingest` skill's convention)

Follow `001_Architecture/Skills/ingest/SKILL.md` Steps 4-6 for a text source. The promoted folder is
the "original", so ingest's Steps 0-3 (markitdown, classify, route into `007_Resource_Library/`) do not
apply and no Resource Library note is made.
1. **Page:** a NEW synthesized page (not a copy of the README) in the existing `000_Wiki/` category
   folder from ingest's Topic Domain table (AI-Agents, RAG-Systems, App-Dev, Content-Strategy,
   Architecture, Video-Production; Affiliate-Marketing also exists). Pick the primary one. Name it
   after the tool in Title-Case-With-Dashes (e.g. `Quality-Ledger.md`). Use ingest's template:
   frontmatter `title`, `type: wiki`, `category`, `tags` (2-5, lowercase kebab-case), `source` (the
   promoted folder's README path), `created`; sections `## What It Is`, `## Key Concepts`,
   `## How Tony Uses This`, `## Related` (link the TOOLBOX entry's tool, related wiki pages).
2. **Cross-link:** search `000_Wiki/` for pages about the same tool or concept and add `[[link]]` to
   the new page under their `## Related` section. None = skip, don't force links.
3. **Log:** append to `000_Wiki/log.md` in its format: `## [YYYY-MM-DD] lab-promote | <Title>`, then
   `Source:` (`001_Architecture/Lab/<project>` -> the promoted path), `Wiki/Asset Note:` (the new page),
   `Cross-links:` (pages you linked, or none).
4. **Index:** add `- [[<Category>/<Page>]] - one-line description` under the right `## ` section of
   `000_Wiki/index.md`.

Do not run ingest's own graphify step (`graphify update .` from the root); Step 5 refreshes exactly
the affected domains from `001_Architecture/Graphify/REGISTRY.md`.

## Step 5 - Graphify, commit, push (script)

List every file you edited in Steps 3-4 with `--file` (paths relative to Agent-OS). `TOOLBOX.md` and at
least one `000_Wiki/` file are required. `--description` is Tony's own words for what is being promoted
(from his `/lab-promote` message). Add each commit trailer line your session instructions require for
commits (e.g. the `Co-Authored-By:` line) with `--trailer`. Single-quote values (`'` becomes `'\''`).

```
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_promote.py finish "<PROJECT_DIR>" --description '<Tony words>' --file TOOLBOX.md --file 000_Wiki/<Category>/<Page>.md --file 000_Wiki/index.md --file 000_Wiki/log.md [--file <each cross-linked page>] --trailer '<trailer line>'
```

Run it with Bash, timeout 600000 or in the background (graphify on a large domain can take minutes).
What it does, in the locked order:
1. Checks the promoted folder is still exactly the lab commit, and secret-scans your added lines.
2. `graphify update <domain>` for each registry domain the changes land in (the promoted path's
   domain and the Wiki's; AST-only, no LLM, no spend). A graphify failure is reported, never fatal
   (`graphify-out/` is gitignored, so nothing from it is committed).
3. ONE commit on `main`, built in a private index: the promoted folder plus only YOUR edits to the
   listed files. Other sessions' uncommitted edits, even in the same file, stay uncommitted on disk.
   If main moved meanwhile, the commit goes on top of the new tip; never a merge, never a force.
4. `git push` to main's upstream (no force).

Last line `LAB_PROMOTE_DONE {json}` with `main_commit`, `pushed`, `files_committed`, `graphify`,
`warnings`, `wiring_left_for_tony`, `cleanup_commands_for_tony`.

Exit codes:
- `0`: done. Go to Step 6. Read `warnings`: a file you changed but did not list is NOT committed;
  if you forgot a cross-linked page, tell Tony which (it stays uncommitted for his next commit).
- `9`: push failed (auth, network, or main is behind GitHub). The commit is safe on local main. Show
  `push.output_tail`. Never force, never pull/rebase on your own. Once the cause is fixed, rerun the
  same `finish` (it only retries the push), or give Tony the `push.retry` command.
- `8`: main moved during the commit; nothing changed. Rerun `finish` once.
- `7`: a listed-file problem (overlap with another session's uncommitted lines, a file you listed but
  did not change, a file that existed before this run, a path inside the promoted folder or the Lab).
  Fix your own edit or the `--file` list and rerun; if it is an overlap, move your entry away from the
  other session's lines, or ask Tony.
- `6`: the promoted folder changed after checkout. Edits to it belong in `/lab-run`; tell Tony, stop.
- `5`: secret in your edits (names only). Remove it from your edit and rerun.
- `1`: already pushed, or `checkout` was not run.

## Step 6 - Report to Tony

Short, plain words, a blank line between points:
- what was promoted and where: the full destination path; the `/lab-run` grades and `/lab-build` score;
- whether the `/lab-run` fixes had to be committed to the lab branch first (`lab_commit_made_now`);
- the TOOLBOX section and wiki page you added (paths), and which pages you cross-linked;
- the main commit hash and that it is pushed (or why not, with the retry command bash-fenced);
- graphify: which domains refreshed, any that failed;
- **still to wire, each a separate approved change:** the `wiring_left_for_tony` items minus the
  folder move and TOOLBOX (for Quality_Ledger: the three harness hooks, the live registry, pasting
  `Agent_Instructions.md` into skills, the checker calls, the central ledger, the Report Card backfill);
- **cleanup, when he is happy with the promoted copy**, bash-fenced, for him to run himself (never run
  them): every line of `cleanup_commands_for_tony`. The project folder in `001_Architecture/Lab/` can
  stay as the record (it is gitignored). If `git worktree remove` says the worktree is not clean, he
  checks it and decides about `--force` himself.

## Known limits (honest)

- The commit is built with git plumbing (`commit-tree` + a compare-and-swap `update-ref`) so it can
  never sweep in another session's staged or uncommitted work. That means git commit hooks do not run;
  Agent-OS has none today. If one is ever added, this needs revisiting.
- "Your edits" are measured against a snapshot of the workspace taken at `checkout` (`git stash create`,
  objects only, no stash entry, no file change). Something another session writes into the same file
  after that moment, before `finish`, is counted as yours.
- A new file you list must have been created after `checkout`; anything older is refused as not yours.
- The push publishes any earlier local commits on main that were not pushed yet (shown in Step 1).
- Claude Code may still show its own permission prompt for the script or the push; that is the
  harness, not an extra `/lab` gate.
- Claude Code only for now: no Codex or Antigravity trigger.
