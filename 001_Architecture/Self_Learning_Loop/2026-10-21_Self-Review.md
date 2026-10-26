# Self-Review 2026-10-21 (Claude)
**Went wrong:** first answer stopped at "brief not found" before checking `list_sessions`; the lost-work cause (unpushed file in a Mac-side session) was findable immediately. Tag push 403 cost two attempts before switching to branch labels.
**Worked:** extracted the brief from the old transcript with a script; asked one decision question (folder path) before creating a folder; smoke-tested the app end to end, not just unit tests.
**Recurring:** work produced in Mac-side Remote Control sessions is not in git. Cloud sessions cannot see it.
**Automate next:** a close-out habit or hook that commits and pushes handoff-referenced files before a session ends; a one-line check at session start that every file named in the latest handoff exists in the repo.
