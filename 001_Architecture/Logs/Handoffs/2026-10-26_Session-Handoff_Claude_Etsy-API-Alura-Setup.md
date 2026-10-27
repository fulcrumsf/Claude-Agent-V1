# Session Handoff, Claude, 2026-10-26 (night): Etsy API app, Alura API + MCP, Etsy login helper

Read first: this file, then `005_Ecommerce/Etsy-Ikigai/Etsy_API_V3_Application_Plan.md` (every decision and finding, newest at the bottom), then the "Etsy" and "Alura" entries in `TOOLBOX.md` (search "Alura official API" and "Etsy developer app").

## Tomorrow, Tony's part (in this order)
1. Sign in to Etsy as the **Ikigai** owner and register a second personal app at https://www.etsy.com/developers/register. Name e.g. `agent-OS-ikigai`. Purpose text: "Private tool for my own Etsy shop (Ikigai Digital Studio). Creates DRAFT listings for my original digital-download wall art. I review and publish everything manually. No other shops, no scraping, no analytics, no buyer data." Accept the terms yourself.
2. After approval: three-dot menu, **Edit callback URLs**, add `http://localhost:3003/oauth/redirect` (the same URL worked for the Bored Nomad app).
3. Put the two keys into `~/.env-secrets` as `export ETSY_IKIGAI_CLIENT_ID=...` (keystring) and `export ETSY_IKIGAI_CLIENT_SECRET=...` (shared secret). Never paste them in chat.
4. Still signed in as the Ikigai owner, run the login: `python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/etsy_auth.py --name ikigai` (opens the browser; click Allow access).
5. Optional, separate: reconnect the BoredNomad shop in Alura (Settings, Etsy Shops, Reconnect; its connection expired).

## Agent's part after that
- **Do not assume an Ikigai token exists.** The last terminal output looked like a replay of the earlier Bored Nomad run: its login link used the Bored Nomad app's keystring, no `ETSY_IKIGAI_*` lines existed, and `token_ikigai.json` does not exist. After Tony's login, verify with `GET /v3/application/users/me` then `/shops/{id}` and confirm the shop name is IkigaiDigitalStudio before trusting the label. The login label must match the account signed in.
- Then run the **TEST draft** in Ikigai (one clearly titled TEST digital-download draft, inactive and private; Tony deletes it by hand since agents never delete and the app has no `listings_d`).
- Then build `steps.etsy_draft` in `005_Ecommerce/Etsy-Ikigai/Portal/app/pipeline/steps.py` (currently raises NotConfigured), with a hard guard that never sets `state=active` (Tony publishes by hand), the Etsy trademark notice and a contact email in the Portal footer, and the mockup-upload step. Mockups for Bored Nomad listings use the Bored Nomad token.
- Pending from the previous handoff, not started: **pull the Etsy Seller Handbook** (AI policy, digital downloads, prohibited items, listing rules) as a dated snapshot, decide `who_made` and the AI-disclosure wording from it, and set a recurring re-pull. Snapshot location needs Tony's OK (candidate `005_Ecommerce/Etsy-Ikigai/`).

## State now
- **Etsy app "agent-OS" approved** (personal use), owned by the **Bored Nomad** Etsy account. Keys in `~/.env-secrets` as `ETSY_CLIENT_ID` / `ETSY_CLIENT_SECRET`. Limits **10 QPS, 10,000 QPD**. Callback URL registered. Scopes requested at login: `listings_w`, `listings_r`, `shops_r` only.
- **Verified:** key-only ping 200; Bored Nomad login works; `/users/me` returned shop_id 19534738, shop BoredNomad, 97 active listings. Token at `~/.config/agent-os-etsy/token_borednomad.json` (mode 600). Access token lasts 1 hour; renew with `etsy_auth.py --name borednomad --refresh`.
- **Why two apps:** Etsy needs a separate login per shop, and a personal app can only be authorized by its own owner (Ikigai login got "only the app owner may authorize a seller app"). Label to key mapping in `etsy_auth.py`: `borednomad` uses `ETSY_CLIENT_ID`, any other label uses `ETSY_<LABEL>_CLIENT_ID`. Correct label spelling is `borednomad`.
- **`001_Architecture/Scripts/etsy_auth.py`** (PKCE login, local callback on port 3003, `--refresh`, `--print-url` only if the browser does not open; no longer prints the login link by default). Validated with `validate_build.py`.
- **Alura:** Tony's workspace is on **Growth** (20,000 API credits/month, 5,000/day, 120 requests/min). API key created by Tony, stored as `ALURA_API_KEY`; scopes are read-only on purpose (research:read, saved:read/write, usage:read, workspace:read). 3-keyword lookup cost exactly 3 credits (19,997 left at test time). Check each row's `as_of`; some were months old. Compute searches per competing listing yourself; Alura's `level` label looks generous.
- **Alura MCP connector** added at user scope and signed in; `claude mcp list` shows Connected. Its tools appear only in new sessions.
- **Alura API terms:** own-business use; keep Alura Data at most 24 hours unless saved in Alura; no bulk copying, no model training, no resale; only the API and MCP are permitted, not the website, app internals or Chrome extension. The Oct 20 Chrome-session endpoint method in TOOLBOX is superseded.
- **Decisions Tony made:** Alura is the analytics layer (sales estimates, keyword demand, competitor data, product gaps); the Etsy app narrows to drafts and mockup uploads; analytics must be fully automated (no manual exports or pasted screenshots). Own-shop Etsy search terms and Marketplace Insights have no API anywhere, so they are dropped. Tony did **not** ask for a gap scan; the goal is recorded (searches per competing listing, trend, competitor sales proof, store-model fit) for later.
- **Printify/Printful (verified in the dashboards):** Printify has a per-product Upload tile for custom mockups and a "Details to publish" checklist (untick Mockups to keep Etsy-side images); Printify API images are read-only. Printful has Basic vs Custom mockup maker and no finished-image upload; its API only sets one thumbnail. So mockup automation for Bored Nomad would go through the Etsy API.

## Rules and mistakes to carry forward
- **Never print key values.** Check only lengths or status codes. Tony reminded me; the credential scanner also blocks it. The keystring appeared once in a login link (shared secret never did); the helper no longer prints that link.
- **Etsy API Terms:** no scraping or bots on etsy.com pages, no internal feeds, no storing Etsy member data, show "The term 'Etsy' is a trademark of Etsy, Inc. This application uses the Etsy API but is not endorsed or certified by Etsy, Inc." in the app. One read-only look at two Etsy dashboard pages was made in Chrome on 2026-10-26 to check export options; do not repeat. Older TOOLBOX notes mention Etsy autocomplete and search pulls from earlier sessions; review those for the same risk.
- **Never use `sed -i` on macOS without an explicit empty suffix** (`sed -i ''`). I made `etsy_auth.py.orig` with `sed -i.orig` (moved to `001_Architecture/Scripts/_Archive/etsy_auth.py.orig_2026-10-26`); the same mistake likely made `~/.env-secrets-E` (Tony deleted it and the `.bak`).
- Agents never delete; the guard blocked an `rm` I tried. Move to `_Archive` instead.
- `~/.env-secrets` showed a modified time of 22:16 on 2026-10-26 that I did not cause; contents not examined.

## Still open from earlier handoffs
- Graphify: Architecture graph refresh not done (`graphify extract 001_Architecture --backend gemini`, estimate about $1.57, run in a long Terminal tab; Ecommerce graph was refreshed).
- PhotoCraft mockup step and `upscayl-ncnn` wiring in the Portal; Etsy download PDF template and description template from Tony; verify the 5 print sizes from a live listing.
- Revenue Priority Board follow-ups from the 2026-10-20 handoff (YouTube re-auth, Gear Verdict registration, compact MEMORY.md).
- Untracked clutter Tony decides on: `.mcp.json`, `Untitled.canvas`, `.tmp.driveupload/`.

## Git state
Nothing from this session is committed. Modified or new: `TOOLBOX.md`, `001_Architecture/Memory/Global_Agent_Memory.md`, `005_Ecommerce/Etsy-Ikigai/CLAUDE.md`, `005_Ecommerce/Etsy-Ikigai/Etsy_API_V3_Application_Plan.md` (new), `001_Architecture/Scripts/etsy_auth.py` (new), this handoff, plus the Claude memory files under `~/.claude/projects/-Users-tonymacbook2025-Documents-Agent-OS/memory/`. Commit only when Tony asks.
