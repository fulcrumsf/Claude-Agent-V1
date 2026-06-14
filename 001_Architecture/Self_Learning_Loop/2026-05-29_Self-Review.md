# Self-Review — 2026-05-29

## What Went Well

- **Symlink approach for graphify was wrong from the start** — I created a symlink thinking it would work transparently in Finder, but macOS doesn't let you hide symlinks via `chflags` or `xattr`. Should have gone straight to the "move after run + hardcoded path" approach. The correct fix was obvious once tested; the detour cost several round trips.
- **Ingest flow was clean** — classified, frontmatter added, routed, logged in one pass. No steps missed.
- **Q&A before building the agent was the right call** — Tony's brief covered scope, workflow, folder logic, and long-term vision. The CLAUDE.md is detailed enough to actually guide the agent rather than being generic boilerplate.
- **Folder rename (Amazon_Associates → Affiliate_Marketing) was the correct call** — broadening the docs folder before building the agent prevented it from being too program-specific from day one.

## What to Improve

- **Test macOS hiding techniques before committing** — `chflags hidden` and `xattr` both failed silently on symlinks. Should verify approach works before presenting it as solved.
- **Don't create symlinks for organizational problems** — the root cause was graphify writing relative to CWD. The answer is instruction discipline (hardcoded path), not a filesystem workaround.
- **Superpowers plugin cache edits are fragile** — changing files in a versioned plugin cache will revert on update. Should flag this risk more prominently to Tony and ideally find an override mechanism that survives updates.

## Patterns Observed

- Tony's workspace is maturing — he cares a lot about visual cleanliness in Finder/Obsidian. Any agent-created folders that appear at root or in unexpected places will be noticed and need to be cleaned up.
- The numbered-folder pattern (`005_Affiliate_Marketing/`) is intentional — each numbered folder gets its own agent CLAUDE.md, and the root agent orchestrates through them.
- Tony thinks in systems: he described the affiliate agent not just as "manage my links" but as a full pipeline from compliance → content → link injection → performance. Building to that vision from the start is correct.

## Rules to Carry Forward

- Never create visible folders at the workspace root without explicit approval
- Always test filesystem tricks (symlinks, hidden flags) before presenting as solved
- For plugin skill edits: note the fragility risk in the same message as the change
- When an ingest has a pending wiki page, note it explicitly in log.md so it's not forgotten
