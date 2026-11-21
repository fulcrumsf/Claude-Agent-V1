# Session Handoff, 2026-11-21, Ikigai realism + controls builds committed, four art engines tested

Read first for Ikigai Portal work. Follows `2026-11-20_Session-Handoff_Claude_Ikigai-Slot-Set-Planner-Built-Realism-Brief.md`. The next session is about Xero, not this workflow.

## What is now true (all committed and pushed)
- **Realism build** (`5ef1f112`): blanked reference images, one reference per slot, lived-in planner rewrite, repeat limits, shorter fixed prompt, output scan for stray text, grades per slot.
- **Controls build** (`a7a3aa3a`): reference-library refresh button, share-of-slots slider (default 80%), loose-to-close slider (default 60), five art engines (kie / fal / WaveSpeed adapters), engine picker in Production with per-engine gate (untested, passed_1, trusted), Generate all with 120-credit cap. 482 tests pass, 13 skipped.
- **Portal** restarted on port 8800 with the new code (hard refresh the browser).
- **Custom Upscayl models** downloaded to `Portal/data/Upscale_Models/models/` (git-ignored): 4xHFA2k, 4xNomos8kSC, 4x_NMKD-Siax_200k. Research in `Research/Upscale_Models_Research.md`, TOOLBOX entry added.
- `Needs_Processing/` inbox folder exists (raw finished artwork, e.g. Midjourney).

## Art-engine test round (2026-11-21, a plain mug image per engine, about 34 credits, about $0.17)
| Engine | Measured cost | Time | Size | Look |
|---|---|---|---|---|
| GPT Image 2.6 | 7.34 cr (estimate said 34) | 18 s | 1024x1536 | clean, catalog-like |
| Ideogram 3 | 10 cr | 149 s | 864x1152 | muted, real, slowest |
| Recraft V4.1 | 7.0 cr (fal estimate) | 13 s | 832x1280 | best light, most character |
| Flux 3 | 9.6 cr (fal estimate) | 17 s | 832x1248 | clean |
Test images were in the macOS temp folder (`/var/folders/.../engine_test_efw0q43c/`), may be cleared. GPT Image 2.6 estimate in `config/engines.json` is still 34 cr; real is about 7.3 (not yet updated).

## Open / next (Ikigai, when Tony returns to it)
1. Each new engine needs one real room scene (with orange or blue insert) before Generate all will use it; try Ideogram 3 and Recraft V4.1 first for the lived-in look.
2. Generate and grade slots with the new planner (all 12 room slots have images; `--replan 16,17,18,19`, 72 credits on Tony's clicks). A/B closeness test is about 54 credits on Nano Banana Pro, not run.
3. Write the third addendum: Needs processing section (refresh circle button, rename + title/subtitle, collapsible rows, idea bank, Use as is / Edit with chat / Make variations, upscale) plus per-art-style upscale model choice with a side-by-side vs Remacri on real art. Plan for Tony's OK before building.
4. Tony to add 15-20 more real-home reference photos.
5. Template triage from 2026-11-16 still open; template checker edge-strip failures pre-existing; MEMORY.md is over its size limit.

## Standing notes
Do not ask Tony things he already told you or that can be looked up. Restart the Portal after code changes: `cd 005_Ecommerce/Etsy-Ikigai/Portal && uv run --no-project --with-requirements requirements.txt uvicorn app.main:app --port 8800`. Uncommitted and unrelated to this work: graphify, .obsidian, `001_Architecture/Skills/.system`, `Skills/gepeto/`, `.tmp.driveupload/`, Tool-Manager model catalog.
