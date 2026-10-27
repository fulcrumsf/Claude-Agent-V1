# Etsy Open API v3: Developer App Application Plan

Snapshot: 2026-10-26. Sources: developers.etsy.com/documentation (authentication, rate-limits, listings tutorial, quickstart, reference) and etsy.com/legal/api (API Terms). Purpose: feed Ikigai Portal `steps.etsy_draft` (drafts only; nothing publishes without Tony).

## What Tony files
1. Register at https://www.etsy.com/developers/register (developer account, info@borednomad.com / Ikigai shop owner login).
2. Declare **personal use** (tools for your own shop), not commercial. The terms define personal as "building tools for your own Etsy shop."
3. Submit the **Application Purpose** (Etsy approves it before the key works; may reject for any reason). Suggested text below.
4. Register one callback URL (must be https, exact-match, case-sensitive). Portal is local FastAPI, so we need an https redirect target. Decision needed (see Open questions).
5. API key is inactive until approved; status shows under "Manage Your Apps."

### Suggested Application Purpose
"Private tool for my own Etsy shop (Ikigai Digital Studio). It creates DRAFT listings for original digital-download printable wall art I design, from my own files: title, description, tags, price, listing images and the download files. Every draft is reviewed and published manually by me in Etsy. It does not read other shops, scrape Etsy, collect analytics, or touch buyer data. Single shop, low volume (a few dozen drafts per week)."

## Scopes needed (minimum)
- `listings_w`: create and edit listings (createDraftListing, uploadListingFile, uploadListingImage, updateListing).
- `listings_r`: read non-public (draft/inactive) listings, to verify drafts after creating.
- `shops_r`: look up shop_id, shipping/section data.
- Do NOT request `listings_d`, `transactions_*`, `email_r`, `address_*`, `profile_*`. Fewer scopes = easier approval. Changing scope later needs re-authorization.

## Auth mechanics
- Every request: `x-api-key: <keystring>:<shared_secret>`. Scoped endpoints also `Authorization: Bearer <user_id>.<token>`.
- OAuth2 authorization code + mandatory PKCE (S256). Access token lasts 1 hour; refresh token 90 days (each refresh returns a new refresh token, so store the latest). Portal needs a token store (like the Drive token under `~/.config/`), never in the repo.
- Keystring and shared secret go in `~/.env-secrets`; never echo values.

## Rate limits
- Per API key: QPS and QPD (sliding 24h window); the numbers for our key are shown in the Developer Portal after approval (the doc example is 150 QPS, 100,000 QPD). Headers: `x-limit-per-day`, `x-remaining-today`. 429 returns `retry-after`; use exponential backoff.
- Creating extra API keys to dodge limits is prohibited. Our volume is far below any default.

## Draft-listing flow (digital download)
1. `createDraftListing` (POST /v3/application/shops/{shop_id}/listings, scope `listings_w`). Required: `quantity`, `title`, `description`, `price`, `who_made`, `when_made`, `taxonomy_id`. `image_ids` only needed to activate. `shipping_profile_id` and `readiness_state_id` are for physical listings only. Set `type=download`.
2. `uploadListingFile` (POST .../listings/{listing_id}/files) with `file` (binary) or an existing `file_id`.
3. `uploadListingImage` (POST .../images); at least 1 image needed to publish.
4. `updateListing` PATCH can set `type=download`; **`state=active` is the publish step, which the Portal must never call.** Drafts stay `state=draft` for Tony to publish in Etsy.
- Listing states: draft is non-public and lacks an image or active state.

## Policy and ban risks from the API Terms (relevant to us)
- Prohibited: listings incompatible with Etsy's Creativity Standards and Prohibited Items Policy (explicitly includes mass-produced items); facilitating IP infringement; using the API to collect or scan Etsy content for analytics, ML, AI training; automated scraping of Etsy; diverting buyers off Etsy.
- Implication: the Portal's research/idea scoring must NOT pull Etsy listing data through the API or by scraping (use other sources), and listing text must not push buyers to external sites.
- Etsy can review/audit the app anytime; app changes beyond the approved purpose need prior approval. So describe the draft-creation purpose honestly and re-submit if the purpose changes.
- Do not cache Etsy data longer than needed; shop's own listing data should be displayed within 6 hours freshness.
- Etsy may suspend for quality issues at its discretion.

## AI-content and disclosure rules
The API docs expose no dedicated AI-disclosure field (no `is_ai` style parameter in the reference as scraped). The AI/creativity rules live in the Seller Handbook and Creativity Standards (step 2 of the handoff, not yet pulled). `who_made` must be answered truthfully (options include `i_did`, `someone_else`, `collective`); the correct value for AI-assisted designs depends on Etsy's current handbook wording. Do not hardcode until the handbook snapshot is pulled.

## Open questions for Tony
1. **Callback URL**: Etsy requires an https redirect registered exactly. Options: a small hosted page (e.g., on Cloudflare Pages/Workers under a domain you own) that just displays the code to copy, or an https tunnel to localhost. Which domain should it live on?
2. Personal vs commercial: recommend **personal** (own shop only).
3. Etsy shop name/ID to attach (needed for `shop_id`; fetch via `getShopByOwnerUserId` after first OAuth).

## Next
- Step 2: pull Seller Handbook (AI policy, digital downloads, Creativity Standards, prohibited items) and decide `who_made` and disclosure wording.
- After approval: build OAuth helper and `steps.etsy_draft` (drafts only, hard-block `state=active`).

Raw scrapes (temporary): scratchpad `etsy/` folder, can be re-pulled with `firecrawl scrape`.

## Update 2026-10-26 (later): decisions after Q&A
- Purpose now covers: Ikigai drafts, uploading Tony's own mockups to Bored Nomad listings (Printify/Printful APIs cannot take custom mockups; Printify dashboard can), and private own-shop sales/listing reporting.
- Scopes to request at OAuth: `listings_w`, `listings_r`, `transactions_r`, `shops_r`. Skip the rest.
- Analytics layers for the Agent OS dashboard: (1) Etsy API: sales, fees, ship-to geography (aggregate only, discard buyer names/addresses), listing views and favorites; (2) Etsy Download Data CSVs (orders, order items, payments, listings) fed in by hand; (3) search terms from Stats > Etsy Search and Stats > Marketplace Insights (no API or export button seen), pasted or screenshotted by Tony; (4) market data from Alura, Google Trends, Pinterest.
- To do after approval: email developer@etsy.com for written confirmation that own-shop reporting is allowed (API Terms clause 25).
- Oct 2026 Bored Nomad: only 4 of 157 visits came from Etsy Search, so own-shop search terms are thin; Marketplace Insights is the richer keyword source.

## Update 2026-10-26 (evening): Alura API changes the analytics plan
- Tony's Alura workspace (Growth plan, 20,000 API credits/month) has an official API with "Your shop": orders, customers, listing stats, ledger-based shop stats, and listing/image/file writes through Alura's own Etsy connection. See TOOLBOX.md (Alura official API entry) and https://docs.alura.io.
- **Automated analytics layer = Alura API (market keywords, competitor estimates, own-shop reads) + Printify/Printful APIs for costs.** No manual exports or pasted screenshots.
- **Still no automation exists for** Etsy's own per-shop search terms and Marketplace Insights (not in Etsy's API, not in Alura's). Use Alura keyword volume/competition instead.
- **Why keep our own Etsy app anyway:** Alura's terms limit keeping its data beyond 24 hours, so durable own-shop history (sales, fees, geography totals) belongs in our own database fed by the Etsy API (`transactions_r`), and drafts/mockup uploads stay in our app. The app purpose text stays as drafted. Alura writes could replace some of it later; decide after testing.
- Open actions: Tony creates the Alura API key and saves it in `~/.env-secrets`; Tony reconnects the BoredNomad shop in Alura (connection expired); test own-shop stats and keyword calls and record credit costs.

## DECISION 2026-10-26 (late): Alura is the analytics layer; Etsy app narrows to drafts and mockups
- Tony's decision: use the Alura API for almost all analytics, stats, keyword research and product-gap work. Alura key verified (read-only scopes: research:read, saved:read/write, usage:read, workspace:read; no write scope, deliberately). Alura MCP connector added to Claude Code at user scope on 2026-10-26 (`claude mcp add --transport http --scope user alura https://mcp.alura.io/mcp`); Tony still has to sign in once through `/mcp` in an interactive terminal, or add it under Customize > Connectors in claude.ai.
- **Etsy app now shrinks.** Because analytics no longer depends on it, the Etsy app purpose drops the reporting wording (that is the part that touched API Terms clause 25, the analytics/ML clause) and the `transactions_r` scope.
  - Scopes at OAuth: `listings_w`, `listings_r`, `shops_r`.
  - Suggested purpose text: "Private tool for my own Etsy shops (Ikigai Digital Studio, Bored Nomad). Creates DRAFT listings for my original digital-download wall art and uploads my own mockup images to my existing listings. I review and publish everything manually. No other shops, no scraping, no analytics, no buyer data."
- **Open decision for Tony:** Alura's API can also write listings (scope `listings:write`: create, publish, delete, photos, files, inventory), so Alura could replace our own Etsy app for drafts and mockups too. Reasons to still file our own app: independence from a third party, a hard "drafts only, never publish" guard we control, and no dependency on Alura's write budget. Reasons to skip it: one fewer approval, no OAuth callback page to host. Recommendation: file the narrow app anyway, keep the Alura key read-only.
- **Durable own-shop history:** Alura's terms limit keeping its data past 24 hours (own conclusions are fine). If we want long-term sales history stored locally, we need a source that allows it; undecided, revisit when building the dashboard.
- Alura key facts and costs are in TOOLBOX.md and the Alura reference memory.

## CONFIRMED 2026-10-26: Tony chose the narrow Etsy app (purpose text above, scopes listings_w, listings_r, shops_r). Not yet filed; Tony files it. Callback URL still needs a decision (https required, can be edited later at etsy.com/developers/your-apps).

## Terms review 2026-10-26 (older API Terms text Tony pasted from the registration form, (c) 2009, 10,000 calls/day; the newer text at etsy.com/legal/api that I scraped is stricter, so follow the stricter union)
- Must put this notice prominently in the app: "The term 'Etsy' is a trademark of Etsy, Inc. This application uses the Etsy API but is not endorsed or certified by Etsy, Inc." Also show a contact email and make a reasonable effort at a terms/privacy link. Plan: Portal footer.
- Section 9: no screen scraping, no bots reading the Etsy website, no reverse-engineering internal feeds or internal APIs, even for data the public API lacks. Do not use browser automation on etsy.com pages. (A single read-only look at two Etsy dashboard pages was done in Chrome on 2026-10-26 to check export options; no data was collected. Do not repeat.)
- No caching Etsy content beyond reasonable periods; no storing or processing member personal data unless authorized; display freshness 6 hours (listings) and 24 hours (other).
- Link back to Etsy listings where the app shows product info or images.
- Etsy can change or terminate at any time; continued use is acceptance; Tony indemnifies Etsy for breaches; New York law. Standard, nothing blocks the narrow plan.

## STATUS 2026-10-26 (night): app APPROVED
- Etsy approved the "agent-OS" app almost immediately (personal use). Keystring and shared secret saved by Tony in `~/.env-secrets` as `ETSY_CLIENT_ID` and `ETSY_CLIENT_SECRET` (the lines already existed).
- **Rate limits: 10 QPS and 10,000 QPD** (set by Etsy; visible in the developer portal; headers on every response). Code must read the `x-remaining-*` headers and back off on 429 with `retry-after`.
- The registration form did not ask for a redirect URI. Next step: Tony adds one by editing the app at etsy.com/developers/your-apps. Etsy's quickstart uses `http://localhost:3003/oauth/redirect`; the OAuth docs say https is required, so if Etsy rejects http localhost, use https localhost with a locally trusted certificate.
- Next build: OAuth login helper (PKCE, token store outside the repo), then `steps.etsy_draft` with the draft-only guard, then the mockup upload step.

## Progress 2026-10-26 (night)
- Callback URL `http://localhost:3003/oauth/redirect` registered by Tony on the app ("successfully updated").
- Key-only ping verified: HTTP 200, limits 10 per second and 10,000 per day confirmed in headers.
- Login helper written and validated: `001_Architecture/Scripts/etsy_auth.py` (login not run yet; needs Tony to approve in the browser).
- Test plan: (1) login as the Ikigai shop owner; (2) read test with `getMe` / shop lookup (scope shops_r); (3) one clearly labeled TEST draft listing (inactive, private); Tony deletes it by hand since agents never delete and we do not request `listings_d`.
- Open: confirm which Etsy login owns Ikigai and which owns Bored Nomad (one token file each).

## FINDING 2026-10-26 (night): the agent-OS app is owned by the Bored Nomad Etsy account
- Tony registered the app while signed in as the Bored Nomad owner (his first Etsy account). Etsy's personal-use apps can only be authorized by the app owner: logging in as the Ikigai owner returns "only the app owner may authorize a seller app".
- So the current app (ETSY_CLIENT_ID/SECRET) works for the **Bored Nomad** login only (e.g., mockup uploads on Printify/Printful listings). Ikigai drafts need a different route:
  - A) register a second personal app while signed in as the Ikigai owner (own keys, e.g. ETSY_IKIGAI_CLIENT_ID/SECRET), Ikigai-only purpose; or
  - B) let Alura's Etsy connection (Ikigai shop already synced there; `listings:write` scope would need a new write key) create the drafts.
- Terms caution for A: extra API keys made to get around rate limits are prohibited; a second app for a different account's own shop is a different purpose, but state that plainly in its purpose text.

## DECISION 2026-10-26 (night): two Etsy accounts, two apps
- Tony confirmed Etsy requires a separate login (and email) per shop, so Bored Nomad and Ikigai are two separate accounts. Each personal-use app can only be authorized by its own owner.
- Bored Nomad: existing app, keys `ETSY_CLIENT_ID` / `ETSY_CLIENT_SECRET`, login label `borednomad` (`etsy_auth.py --name borednomad`).
- Ikigai: second app to register while signed in as the Ikigai owner, keys `ETSY_IKIGAI_CLIENT_ID` / `ETSY_IKIGAI_CLIENT_SECRET`, login label `ikigai`. Ikigai-only purpose: "Private tool for my own Etsy shop (Ikigai Digital Studio). Creates DRAFT listings for my original digital-download wall art. I review and publish everything manually. No other shops, no scraping, no analytics, no buyer data." Callback `http://localhost:3003/oauth/redirect`.
- `etsy_auth.py` now picks the keys by login label (validated 2026-10-26). Typo to avoid: the label is `borednomad`.

## VERIFIED 2026-10-26 (night): Bored Nomad OAuth works
- Tony logged in as the Bored Nomad owner. The token (scopes listings_w listings_r shops_r) was first saved as `token_ikigai.json` because the label given was `ikigai`; it was moved to `~/.config/agent-os-etsy/token_borednomad.json`.
- Read check passed: `GET /v3/application/users/me` -> 200 (user_id 61788715, shop_id 19534738); `GET /shops/19534738` -> 200, shop BoredNomad, 97 active listings, USD. Rate-limit headers 10/s, 10,000/day.
- Lesson: the login label must match the Etsy account signed in at the time; check the shop name with `/users/me` after every login.
- Ikigai still needs its own app (second app) and login.
