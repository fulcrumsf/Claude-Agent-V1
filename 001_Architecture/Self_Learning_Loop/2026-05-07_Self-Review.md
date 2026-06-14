# 2026-05-07 Self-Review

## What Worked
- The two-part architecture finally stayed stable once it was written down in folder-level README files and the workspace map.
- Keyword-based grouping was a good compromise for the raw image pile: it made obvious files readable without burning vision calls on everything.
- The user’s “human-readable first” requirement was reinforced by the folder names themselves, which is the right design for this vault.

## What Went Wrong
- I over-relied on inference and filename heuristics too early, especially when checking whether files were already ingested.
- I gave a wrong answer about the `user-HG5...` bucket being fully ingested before verifying it.
- I created extra review layers and mirror structures that were more complex than the user wanted.

## Pattern To Keep
- For this workspace, move by explicit proof and preserve originals unless Tony approves a destination.
- Treat the canonical attachment folders as the source of truth for image status.
- Use lightweight filename grouping first, then vision only for the files that are worth the cost.

## Next Time
- Start by reading the README files and workspace map before building new ingest buckets.
- Avoid creating extra status layers unless they directly answer Tony’s current question.
- If the user wants “already ingested” versus “needs ingestion,” keep that distinction as the primary navigation model.
