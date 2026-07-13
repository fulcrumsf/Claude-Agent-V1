---
title: "Session Log — 2026-07-12"
type: log
domain: content-creation
tags: [session-log, tiktok-shop, neon-parcel, blotato, compliance]
---

# 2026-07-12 Session Log

## Neon Parcel TikTok Shop Creator pipeline built (8-task subagent-driven-development)
- Brainstormed and wrote a design spec + implementation plan for a compliance-gated TikTok Shop Creator affiliate video pipeline, extending the existing `TikTok-Shop-Affiliate-Video` skill in place (not forked).
- Executed via `superpowers:subagent-driven-development`, direct-to-main (no worktree — confirmed with Tony this repo is a live Obsidian vault, worktree would be invisible to it). 8 tasks: folder scaffolder, compliance source URL extractor, citation-backed compliance ledger (10 rules) + validator, Firecrawl-based live freshness checker, post-build vision scan, post-build transcript scan, skill extension, end-to-end wiring against the real 18-file TOS bundle + Colorsmart Pens scaffold.
- Fix rounds: Task 4 (freshness checker) — substring-match bug in always-escalate category check + no per-source error isolation, both fixed. Task 5 (vision scan) — missing HTTP status check before parsing OpenRouter response, fixed.
- Final whole-branch review (opus) caught 2 real cross-cutting fail-safe bugs invisible to per-task reviews: a fully-failed freshness run was logging the same header format as a real success, poisoning the 14-day cadence gate into dormancy; the transcript scanner defaulted to CLEAR on empty/failed transcription, inverting the vision scanner's fail-safe-to-FLAG principle. Both fixed in one follow-up commit, re-reviewed clean.
- Real-world finding: Firecrawl refuses to scrape `seller-us.tiktok.com` entirely — Phase 2 (live freshness check) is correctly wired but provides zero real drift-detection value until this vendor limitation is resolved.
- Pushed all 11 commits to `origin/main`.

## Colorsmart Pens — first real production (V1, V2, V3)
- Transcribed all 3 VO scripts (ElevenLabs Scribe, word-level timestamps), ran dense keyframe vision sampling (~every 4s) across the 8 raw clips to match footage to narration beats.
- V1 first cut used a "washing the car" clip for the "silver doesn't perfectly match" beat — Tony caught this didn't actually show the painted result. Fixed by using `IMG_9194.JPG` (a still) with a slow Ken Burns zoom onto the two visible touch-up spots — Tony confirmed this approach is expected/fine to reuse across all 3 videos for that one beat.
- Built V2 (3 beats) and V3 (5 beats) with genuinely different shot selection/pacing than V1 (4 beats), reusing the `IMG_9194` zoom for the same beat in each.
- Compliance gate run on all 3: Phase 1 manual ledger read found one real action item (RULE-008 disclosure — resolved later, see below), Phase 3 transcript scans all CLEAR, Phase 3 vision scans flagged the product's own "Colour"/"Colour Smart" label text twice (V1, V3) — resolved as false positives (own-product branding, not third-party) after Tony's sign-off.
- Discovered via direct measurement (not assumption) that raw VO audio measured -34 to -35 LUFS integrated — no clipping risk, just far too quiet vs. TikTok's ~-14 LUFS norm. Built `normalize_loudness.py` (two-pass EBU R128, -14 LUFS/-1.5 dBTP default) as a new permanent pipeline step (SKILL.md Step 5a.5), re-rendered all 3 videos — now measuring -13.8 to -14.2 LUFS / -1.4 dBTP.
- Compliance markdown reports + caption notes committed to git; video `.mp4` files intentionally left untracked per Tony's explicit instruction (only pipeline code/architecture gets committed, videos get backed up separately, method TBD).

## Blotato posting — V1 posted as a TikTok draft
- Confirmed via live `blotato_list_accounts` + `blotato_create_post` schema: NeonParcel TikTok account is `27763`. Blotato's TikTok post supports `isDraft: true` (confirmed working, Tony verified it landed in his TikTok drafts inbox) but has no field anywhere to attach/tag a TikTok Shop product — manual attachment in the TikTok app is required.
- Corrected my own assumption on `isBrandedContent`: that flag is for direct brand-paid partnerships with brand-dictated guidelines, not commission/GMV-based affiliate content — set to `false`.
- Worked through the `#ad` disclosure placement with Tony: initially over-hedged this as a "risk tolerance" decision when the TOS text is actually unambiguous ("at the beginning of a post") — corrected that framing when Tony pushed back.
- Tony then provided a real, direct platform observation that changed the actual guidance: attaching a TikTok Shop product link auto-adds a "Creator earns commission" tag, which functions as the disclosure for this content type — other TikTok Shop affiliate creators don't use `#ad` either. Added this as a dated addendum to `Compliance-Ledger.md` RULE-008 (flagged as observation-based, not a TOS-bundle citation). V1's already-posted draft caption (`#ad Chips Gone In One Coat 🚗 #touchuppaint`) left as-is; V2/V3 captions updated to drop `#ad` in favor of 3 relevant hashtags. Tony is posting V2/V3 manually, not through Blotato.

## Session close-out
- Updated TOOLBOX.md (TikTok Shop Affiliate Video section rewritten for the Neon Parcel mode + new scripts; Blotato section gained NeonParcel/ReimaginedRealms TikTok account IDs, the `isDraft`/no-product-tagging finding, and the `isBrandedContent` clarification).
- Updated 3 wiki pages (`TikTok-Shop-Affiliate-Compliance.md`, `-Do-Dont-Cheat-Sheet.md` with the RULE-008 addendum; new `Neon-Parcel-TikTok-Shop-Creator-Pipeline.md` overview page) + `000_Wiki/index.md` + `000_Wiki/log.md`.
- Updated `Global_Agent_Memory.md` with a full dated entry covering all locked facts from this build.
- Saved a new cross-session memory file (`feedback_video_git_commit_policy.md`) documenting the never-commit-video-output rule (also already covered as a Core_Memory.md hard rule — confirmed, not duplicated there).
- Graphify: ran `graphify update 001_Architecture` (SKILL.md + new scripts live there); `005_Affiliate_Marketing` still has no domain graph in the registry — added as a `pending build` row rather than doing a full semantic build this session (that's a heavier interactive pass, better suited to its own session).

## Pending / next session
- Firecrawl `seller-us.tiktok.com` block is unresolved — Phase 2 freshness checks will keep failing until Tony either contacts Firecrawl support or an alternate scrape method is found.
- Colorsmart Pens V2/V3 still need to be posted manually by Tony (captions ready in `Package/Caption-Notes.md`).
- `005_Affiliate_Marketing` domain graph is still unbuilt — flag for a future dedicated graphify session if Tony wants query access to this department.
