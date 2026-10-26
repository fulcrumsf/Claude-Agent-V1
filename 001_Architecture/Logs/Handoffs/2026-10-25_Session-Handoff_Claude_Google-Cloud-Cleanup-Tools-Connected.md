# Session Handoff, Claude, 2026-10-25: Mac/GitHub synced, Google Cloud cleaned, Ikigai tools connected

Read first: this file, then `001_Architecture/Google_Cloud_Map.md`, then `005_Ecommerce/Etsy-Ikigai/Portal/README.md` (Connection status section).

## State now (all committed and pushed to origin/main; no unpushed work)
- Mac and GitHub in sync. The cloud/phone Ikigai portal session is merged (PR #1) and my merge is pushed. Rollback tag `rollback/ikigai-01-brief` is pushed.
- Tools connected (in `~/.local/bin`): `photocraft-cli` 0.16.0 (opens the 3 mockup PSDs in `~/Documents/Automations/IkigaiDigital/Mockup Automation/`), `vectorcraft-cli` (Illustrator equivalent), `pdfcraft-cli`, plus lightcraft/filmcraft/effectcraft, and `upscayl-ncnn` (the Upscayl.app bundled binary crashes; use ncnn; needs sandbox off in Claude Code). See TOOLBOX.md.
- Google Drive connected: login `001_Architecture/Scripts/google_drive_auth.py`, token `~/.config/agent-os-drive/` (info@borednomad.com), Portal helper `Portal/app/drive.py` (folders named `NNNNN-Title`, last 00120). Portal tests 4/4.
- Google Cloud: business project "Agent OS" (`gen-lang-client-0251496109`) holds Gemini + Drive; consent screen Internal. Personal project renamed "YouTube and Gmail" (`antigravity-claude-491002`); Google-managed Stitch project `nimble-question-9v9qn` can't be renamed (Stitch key last used: Never). Deleted by Tony: Upkeeply, Gemini API, Make, WooCommerce (business, 30-day restore) and My Project 29633, n8n automation (personal).
- Gemini hard cap raised $20 to $30 ("Agent-OS $30 hard cap"); `~/.env-secrets` Gemini keys return 200. claude-mem login refreshed.

## Next up (Tony's priority): Etsy Open API v3
1. Read https://developers.etsy.com/documentation/ and plan the developer-app application (Tony files it; needed for `steps.etsy_draft`, drafts only, nothing publishes without Tony). Capture scopes, rate limits, listing-draft endpoints, AI/digital-listing rules.
2. Pull the Etsy Seller Handbook https://www.etsy.com/seller-handbook into the system (firecrawl), dated snapshot, focused on AI-content policy, digital downloads, prohibited items, listing rules. Etsy keeps changing these; goal is never risking a ban. Decide with Tony where the snapshot lives (no new folder without his OK; candidate: `005_Ecommerce/Etsy-Ikigai/`), and set a recurring re-pull (scheduled task or monthly reminder).
3. Fold the handbook rules into Portal listing text, tags and AI disclosure template.

## Still open after that
- Build the PhotoCraft mockup step (place art into the "Place Artwork Here" smart object; headless convert flattens layers) in `steps.mockups`; wire `steps.upscale` to `upscayl-ncnn`.
- Tony to supply the Etsy download PDF template and description template; verify the 5 print sizes from a live listing (`config/print_sizes.json` is placeholder); then `steps.resize`, `steps.package`, `steps.listing_text`.
- Engine adapters (`engines.run_prompt`) and keys; research job feeding `ideas.add_to_pool`; Frame TV variant; fidelity check for AI room mockups.
- Old Mac-side cleanups: `.mcp.json`, `Untitled.canvas`, `.tmp.driveupload/` still untracked clutter (Tony's call).
- Wiki article for the Ikigai portal once pipeline steps are real.
- Revenue Priority Board follow-ups from 2026-10-20 handoff still open (pick rows, YouTube monetary scope re-auth, Gear Verdict registration, compact MEMORY.md).
- YouTube tokens (personal project, Testing mode) expire every 7 days; the Drive token (Internal) should not.

## Graphify refresh NOT done (needs Tony's decision)
Tried `graphify update` for 005_Ecommerce (28 changed files: 15 code, 13 docs) and 001_Architecture (1,326 changed files, over the 500-file threshold). AST pass works (Ecommerce: 59 nodes, 142 edges), but the doc files need semantic extraction, which Graphify sends to paid Gemini (`GEMINI_API_KEY` is set). The worker refused to spend and stopped before writing any graph or REGISTRY row, so graphs are unchanged (Ecommerce still 54 files @ 2026-10-21T20:29Z). Decide: allow Gemini for docs (cost; cap is $30/mo), or code-only update. Stray probe files were left in `005_Ecommerce/graphify-out/` and `001_Architecture/graphify-out/` (dot-files named `.graphify_*.json`); Tony can delete.

## CORRECTION (late 2026-10-25): Gemini still blocked
The earlier "keys return 200" test was `models.list`, which is not metered. A real `generateContent` call returns **429 "exceeded its monthly spending cap"** and points to https://ai.studio/spend (AI Studio has its own project spend cap, separate from the Cloud budget raised to $30). Tony approved Gemini for Graphify doc extraction, but the run was blocked. Next: Tony raises the cap at ai.studio/spend (business account), then re-test with a real generate call, then run Ecommerce graphify extract (`graphify extract 005_Ecommerce --backend gemini`) and get the Architecture cost estimate (keep total under $4; $30 cap, ~$20.33 already spent this month). Any tool relying on Gemini (claude-mem Gemini, Obsidian ingest) is affected until then.

## Standing rules reinforced
Never move YouTube off the personal account. Don't ask obvious questions. Never print key values (last-4 and status codes only). Stop at terms/consent boxes and ask. Agents never delete; Tony deletes projects and files.
