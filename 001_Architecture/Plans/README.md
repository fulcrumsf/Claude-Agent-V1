# Plans Folder — Standing Rule (2026-10-02)

**This folder is for plans that have NOT been implemented yet.**

- A plan lives here (top level) while it is still pending, in progress, or waiting on Tony's decision.
- The moment a plan is **implemented, finished, and finalized**, move its file into `Archive/` (same filename, no rename needed).
- `Archive/` is a holding pen, not permanent storage — files there are flagged for Tony to delete later. Agents never delete; only move.
- If a plan is **superseded/abandoned** rather than completed (e.g. replaced by a newer plan), note that in the file itself and ask Tony whether it goes to `Archive/` or gets deleted by him — don't assume "superseded" equals "done."

## Mechanics

```bash
mv "001_Architecture/Plans/<Plan_Name>.md" "001_Architecture/Plans/Archive/<Plan_Name>.md"
```

Any agent (Claude Code, Codex, Gemini CLI, Antigravity) that finishes implementing a plan from this folder should perform this move as part of closing out that work — same close-out moment as updating logs/memory, not a separate pass.

## Current contents (as of 2026-10-02 — treat as the live to-do list)

| Plan | Status |
|---|---|
| `Agent_OS_Command_Center_Dashboard_Roadmap.md` | Draft/brain-dump roadmap, not started |
| `Multi_Agent_Bridge_MCP_Slack_Plan.md` | Draft/planned, not started |
| `robotto-gato-channel-strategy.md` | Untracked, appeared 2026-10-02, not yet reviewed by this session's lineage |
| `Tool_Catalog_Maintenance_Plan.md` | Draft for discussion, 9 open decisions pending Tony's sign-off (2026-10-08) |
| `Tool_Catalog_Tagging_Plan.md` | Deferred by Tony's explicit call — not a current priority, parked until after the online/vector-DB migration (2026-10-08) |
