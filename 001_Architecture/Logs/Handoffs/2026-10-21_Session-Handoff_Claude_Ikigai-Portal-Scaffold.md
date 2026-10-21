# Session Handoff, Claude, 2026-10-21: Ikigai portal scaffold

Read first: `005_Ecommerce/Etsy-Ikigai/Ikigai_Portal_Pipeline_Brief.md`, then `005_Ecommerce/Etsy-Ikigai/Portal/README.md`.

## Where the work is
Branch `claude/ikigai-portal-pipeline` (pushed, NOT merged to main, no PR). Main does not contain the brief or the Portal yet, so check out the branch or merge it first. Rollback branches: `claude/rollback-ikigai-01-brief`, `-02-scaffold`, `-03-closeout` (tag pushes are 403 in cloud sessions).

## Done and verified
- Brief recovered from the archived Mac-side session and committed. Creative_Inspiration folder created.
- Portal scaffold runs: 10-idea list, approve/deny refill, pool warning, prompt on approve, engine dropdown, step tracker. 3 pytest tests pass; page/approve/produce smoke test OK.

## Still open
1. Merge the branch to main (Tony's call) so every harness sees it.
2. On the Mac, connect in order: PhotoCraft CLI (prove it opens the PSDs headless), Upscayl CLI, verify the 5 print sizes from a live listing (`config/print_sizes.json` is placeholder), PDF + description templates, Drive credentials, engine keys in `.env`, Etsy developer app (day-one application).
3. Build next: research job feeding `ideas.add_to_pool`, model-written prompts using the Ikigai style tokens, performance feedback into idea scoring, Frame TV variant, fidelity check for AI room mockups.
4. Graphify refresh for the new `Portal/` code and brief was not run (CLI not in the cloud container). Run `graphify update 005_Ecommerce` on the Mac.
5. Update `~/.claude/.../MEMORY.md` on the Mac (not reachable from the cloud).
6. Old interview session `session_014VW3Q29KssHuX3qJ2kHYTN` is archived; its content is now in git, so no need to restart it.

## Rules learned
Rollback label per milestone; plan/scaffold in cloud, Mac tools later; ask before creating folders.
