# Session Handoff — Claude Code — 2026-10-07
## BoredNomad project/key mapping, Plans-folder audit, sync automation

## What's done

1. **BoredNomad Cloud Console budget cap set and confirmed live.** Billing account `01AF23-B42882-ADD61A` (org `borednomad.com`), 5 projects. Only "Blotato - Antigravity" (`gen-lang-client-0251496109`) has real spend — enforced hard-cap budget created there, scoped to that project + Gemini API. Started at $10/mo, Tony raised it to **$20/mo** himself in Console same day after real spend hit $10.63 (confirmed live via the Edit Budget page: enforcement mode intact, resets Nov 1, 2026).
2. **Full BoredNomad project → credential map built**, written into `001_Architecture/API_Directory.md`: which of the 5 projects has which API key/OAuth client, whether each shows real traffic, and a keep/delete-candidate read for each. 3 of the 5 look dormant/orphaned (details below) — **nothing deleted, all flagged for Tony's decision.**
3. **Visual "Project Key Map" Artifact built and saved**, linked from `API_Directory.md`: https://claude.ai/artifact/LrtHTdWPcBzidPZyeNYkw8 — grouped project-first (Tony's explicit preference, confirmed correct on the 2nd pass) with each project's keys nested inside, status pills (active/idle/dormant).
4. **Plans-folder audit closed** (this was the prior session's flagged next-step). `Agent-OS-Xero-Receipt-Automation-Plan.md` was sitting unreferenced — fixed, now top of a new "Top priority — pending plans" section at the top of `001_Architecture/Ongoing-Agent-OS-To-Do-List.md`, ranked first per Tony's explicit call.
5. **Built and wired `001_Architecture/Scripts/sync_plans_to_todo.py`** — daily cron (6:00 AM local) that flags any new `Plans/` file missing from the to-do list into a dedicated section. Tested live (dummy file detected, re-run confirmed no duplicate). Mechanical only — does not touch the existing manual archive-on-completion rule.
6. **Committed and pushed** — `a4ffbedd` on `origin/main`. Included routine Obsidian/Graphify/Skill-Index housekeeping and the `plugin-creator` system-skill churn (already investigated/explained in the prior session's memory).

## What's still open

1. **3 of BoredNomad's 5 Cloud Console projects look like delete candidates** — none deleted, all need Tony's confirmation first:
   - **"Gemini API"** project (`gen-lang-client-0553978373`) — oldest key (2025-08-29), zero traffic, no OAuth client/service account, nothing in this workspace references it. Likely safe but confirm what it originally backed before removing.
   - **BoredNomad WooCommerce Website** (`theta-eon-450804-c2`) — zero credentials of any kind exist in this project.
   - **Make** (`fine-program-454108-r9`) — has an OAuth client for Make.com/Integromat but shows no traffic. OAuth traffic doesn't always show the same way as an API key's, so this read is less certain — **ask Tony directly whether that Make.com automation is still running** before treating it as dormant.
2. **The Xero Receipt Automation plan itself hasn't been discussed/reviewed yet** — only its priority position was set. Its own approval gate (creating `Agent-OS/Accounting/Xero/`) is still pending Tony's structural sign-off, per the plan's own section 1.
3. **`.tmp.driveupload/` still sitting untracked at workspace root** — same open item carried from prior sessions (flagged in the to-do list's Part 3 housekeeping queue), still unresolved. Needs Tony's decision: gitignore it or delete it.

## Decisions waiting on Tony

- Confirm or reject the 3 BoredNomad delete candidates above.
- Whether/when to actually start the Xero plan's Phase 1 (folder creation + review pass).
- `.tmp.driveupload/` — gitignore vs. delete.

## Context for whoever picks this up next

- Two separate Google identities are now clearly mapped: personal (fulcrumsf@gmail.com) and BoredNomad (info@borednomad.com) each have their own Cloud Console + AI Studio with independent spend caps. Don't conflate them — see `API_Directory.md`'s credential inventory section for the full breakdown.
- The new "Top priority — pending plans" section at the top of `Ongoing-Agent-OS-To-Do-List.md` is now the first thing to check for active plan work — keep it in sync via the new daily cron job, don't hand-maintain it from scratch.
