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

## Deferred to the next Mac session (standing rule for this handoff)
This session ran in the cloud, so anything it could not do belongs to the next session, when Tony is on the Mac. The next Mac session should do all of these first, before new work:
- Run the Graphify refresh (`graphify update 005_Ecommerce`) and update the REGISTRY build state.
- Update `~/.claude/projects/.../memory/MEMORY.md` from the 2026-10-21 additions in `Global_Agent_Memory.md`.
- Check whether `DEPARTMENTS.md` should get an Ikigai row (not added from the cloud; ask Tony).
- Write the wiki article for the Ikigai portal once the pipeline steps are real.
- Connect PhotoCraft, Upscayl, Drive, Etsy API and the Mac-only n8n/automation files (see Still open item 2).
- Push the real git tag `rollback/ikigai-01-brief` if wanted (created only inside the cloud container; tag pushes returned 403 there).
- Anything else found undone because of cloud limits: do it, then tick it off here.

## Ticked off 2026-10-25 (Mac session)
- Graphify refresh of 005_Ecommerce: done 2026-10-21 (REGISTRY updated, committed).
- MEMORY.md updated with the Ikigai portal and a new feedback entry.
- DEPARTMENTS.md and root CLAUDE.md: Etsy Ikigai added (plus Etsy Bored Nomad and TikTok Shop Uno Mas Creative, which were also missing).
- Branch merged to main (PR #1) and Mac main merged and pushed (7d4d2081).
- Still open: connect PhotoCraft, Upscayl, Drive, Etsy API; real rollback tag; wiki article once pipeline steps are real.
