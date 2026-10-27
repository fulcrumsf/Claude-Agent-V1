# Session Handoff, Claude, 2026-10-27: Xero receipts cleanup done, back to the Ikigai workflow

Read first: this file, then `2026-10-26_Session-Handoff_Claude_Etsy-API-Alura-Setup.md` (it still holds the full Etsy/Alura detail and Tony's to-do list for the Ikigai app), then `005_Ecommerce/Etsy-Ikigai/Etsy_API_V3_Application_Plan.md`.

## Ikigai workflow: where it stands (unchanged today, nothing here was touched)
- **Blocking, Tony's part (from the 10-26 handoff, not confirmed done):** register the second personal Etsy app as the Ikigai owner (name e.g. `agent-OS-ikigai`), add callback `http://localhost:3003/oauth/redirect`, put `ETSY_IKIGAI_CLIENT_ID` / `ETSY_IKIGAI_CLIENT_SECRET` in `~/.env-secrets` (never paste in chat), then run `python3 001_Architecture/Scripts/etsy_auth.py --name ikigai` while signed in as the Ikigai owner. Ask Tony whether this is done before assuming; no `token_ikigai.json` existed as of 10-26.
- **Then the agent's part:** verify the token (`/users/me`, `/shops/{id}`, confirm shop name IkigaiDigitalStudio), run one clearly titled TEST digital-download draft (inactive, private; Tony deletes it by hand), build `steps.etsy_draft` in `005_Ecommerce/Etsy-Ikigai/Portal/app/pipeline/steps.py` with a hard guard that never sets `state=active`, add the Etsy trademark notice and contact email to the Portal footer, then the mockup-upload step.
- **Other open Ikigai items:** PhotoCraft smart-object art swap recipe (`photocraft-cli` 0.16.0 opens the mockup PSDs; the swap is still to be built), `upscayl-ncnn` wiring in the Portal, the Etsy download PDF template and description template from Tony, verify the 5 print sizes from a live listing, pull the Etsy Seller Handbook as a dated snapshot (location needs Tony's OK, candidate `005_Ecommerce/Etsy-Ikigai/`).
- Alura (Growth plan, read-only API key `ALURA_API_KEY`, MCP connector) is the analytics layer; its tools appear in new sessions.

## What this session did (Xero receipts, finished)
- Ran the Xero receipt tool live for the Chase Ink Unlimited charges since 9 Oct. All now have a verified receipt attached: Printful 64.85 / 44.01 / 4.69, Amazon 162.36, Adobe 75.06, OpenAI 20.00, Spectrum 30.00, Visible 19.00, Google One 19.99, Blotato 29.00, Anthropic 20.00, ElevenLabs 5.00. Nothing pending.
- Receipts with no PDF were attached as full screenshots of the real receipt email (rendered with Playwright from the Gmail API body); Tony dropped the Adobe, OpenAI and Blotato files into `000_Ingest/Xero_Receipts/`.
- **Mistake to remember:** bulk-approving 11 pending matches attached a Freshtix concert-ticket PDF (personal) to the Anthropic 20.00 charge, because the amount matched. Tony deleted it in Xero; the correct Anthropic receipt is attached. Anthropic is now on the tool's 90-day review-only hold (`vendor-trust` shows it).
- **Rule:** never bulk-approve matches. Open the matched email/file and confirm vendor and amount first; the 4.69 Printful charge also nearly got the 44.01 screenshot (the 44.01 email contains "4.69").
- Tool fixes (committed): approved items with no file go back to review instead of crashing the run; new config key `no_receipt_contacts` (CapitalOne, Credit Card Interest) hides interest charges from every report and from matching. Tony: interest charges never have receipts, do not show them.
- Gmail logins for `tony_personal` and `borednomad_business` were re-authorized 2026-10-27; they expire again in about 7 days while the Google app is in test mode (symptom: `HTTP Error 400` on a run; fix: `xero_receipts.py auth-gmail --account <label> --allow-archive`).
- Xero facts learned: Amazon review purchases and TikTok Shop review purchases are filed under account **6002** (line description "TikTok Shop purchase for review"); 5001 is Printful only; the tool's Xero login can read bank transactions, invoices and contacts but not the chart of accounts. Printful API (`PRINTFUL_API_KEY`, store BoredNomad) lists orders with costs; no invoice download found.
- Note for the weekly tool: Etsy Payment Balance charges (56) are excluded by design.

## Git state
Committed and pushed to `main`: `4b2b58e5` (Xero tool fixes) and `cdefa30f` (everything else from the 10-26 and 10-27 sessions), rollback tag `rollback-2026-10-27-xero-receipt-fixes-etsy-api-alura-setup` (undo today's work with `git reset --hard 94a8145b`). Not pushed: `.tmp.driveupload/` (temp Drive upload cache, unknown contents, Tony decides). This handoff file itself is written but not yet committed.

## Still open from earlier handoffs
- Graphify Architecture graph refresh not done (`graphify extract 001_Architecture --backend gemini`, about $1.57, run in a long Terminal tab).
- Revenue Priority Board follow-ups from the 2026-10-20 handoff (YouTube re-auth, Gear Verdict registration, compact MEMORY.md).
- Optional: reconnect the BoredNomad shop in Alura (connection expired).
- Etsy micro-charge duplicate to eyeball in Xero: CapitalOne 17.89 appears on both 3 Aug and 4 Aug.
