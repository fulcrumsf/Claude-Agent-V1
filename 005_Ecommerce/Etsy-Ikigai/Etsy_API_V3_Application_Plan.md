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

## VERIFIED 2026-10-27: Ikigai OAuth works
- Second seller app registered under the Ikigai owner login. Keys in `~/.env-secrets` as `ETSY_IKIGAI_CLIENT_ID/SECRET` (Bored Nomad now `ETSY_BOREDNOMAD_CLIENT_ID/SECRET`); `etsy_auth.py` reads `ETSY_<NAME>_CLIENT_ID` for both. Callback had to be added on the new app (otherwise "requested redirect URL is not permitted").
- Token `~/.config/agent-os-etsy/token_ikigai.json` (listings_w listings_r shops_r). `/users/me` 200 (user_id 870795703, shop_id 48637917); shop IkigaiDigitalStudio, 18 active listings, USD.
- Etsy app types: Seller app (own shop only, near-instant approval) is the right one; Personal app is for developers building beyond their own shop.
- Next: one TEST draft (inactive), then build steps.etsy_draft with a hard never-active guard.

## Tony's two Ikigai draft templates (read via API 2026-10-27, read-only)
- Etsy drafts "AI Template |" (1766496865) and "Originals Template |" (1814257668). Most listings will use the AI template (nearly everything is AI-assisted); Originals is for art Tony builds without AI.
- Identical except the AI one adds an "AI Disclosure" block (elements incl. mockups and/or designs created with AI tools Tony owns and has full commercial rights to; concepts, prompts, final compositions directed by Tony).
- Shared settings: type download, taxonomy 2078 (Digital Prints), price 6.50 USD, quantity 999, who_made i_did, when_made 2007_2009 (looks like a leftover, check), auto-renew on, return_policy_id 1, no tags/materials/section, 6 images, 1 download file (instructions PDF with a Google Drive zip link, e.g. INSTRUCTIONS-00060-CyberTokyo.pdf).
- Description structure: digital-product banner, resize-app note, (AI disclosure), key features, what you'll receive (5 ratio files + tutorial PDF: 2:3, 3:4, 4:5, ISO, 11x14), print info, perfect for, how to download, paper/printing tips, terms of use, copyright (c) Ikigai Digital Studio 2024, no returns. Uses Unicode bold headings; the text still has CyberTokyo-specific wording ("modern cityscapes") to make generic.

## CRITICAL TO-DO + constraints for steps.etsy_draft (Tony, 2026-10-27)
- Status: NOT building yet. Logged as critical in the claude-mem work-state list `critical-todo`.
- The two template drafts are old. Etsy has since added more photo slots and video support in listings; use the current limits.
- The download file on the templates is only a placeholder Etsy needed to save a draft. Every new listing needs its own newly generated instructions PDF (Drive link + tutorial pointers) uploaded via uploadListingFile.
- Etsy's newer listing attributes are filled for physical prints even when the listing is a digital download. Do NOT send or fill physical-print attributes on Ikigai listings: framing option, depth, mat/matte included, and anything similar. Inspect the attributes Etsy exposes for taxonomy 2078 (getPropertiesByTaxonomyId) and map only the ones that make sense for a digital file; verify in the Etsy editor after the first real draft.

## Listing editor + API attribute survey (2026-10-27, nothing saved)
- API (`GET /seller-taxonomy/nodes/2078/properties`, Digital Prints) returns 16 real attributes, all optional: Material(multi), Primary/Secondary color, Width, Height, Depth, Frame mat included, Material features, Framing, Orientation, Frame color, Number of pieces, Aspect ratio(multi: 1:1 1:2 2:3 3:4 4:5 5:7 11:14 16:9), Home style, Occasion, Holiday, Room(multi), Art subject(multi), Can be personalized. Plus legacy junk (Diameter, Fabric, Flavor, TeeShirtSize...) to ignore.
- Editor "Attributes" (AI Template draft, Show all): Framing, Orientation, Materials, Width, Height, Depth, Mat included, Material features, Frame color, Number of pieces, Aspect ratio (up to 5), Home style, Occasion, Holiday, Room (up to 5), Subject (up to 3). Same set as the API (editor hides colors).
- Digital-irrelevant, never send: Framing, Depth, Mat included, Frame color, Width/Height (unless meant), Material(s)/Material features, Number of pieces. Useful for search: Aspect ratio, Orientation, Home style, Room, Subject, Occasion, Holiday, tags (13).
- Editor-only items to check against the API: "How is this digital content created?" (Created by me / With an AI generator) under How it's made, plus Who made it / What is it; "This digital item is made to order" toggle; "Note to buyers for digital items" (the long how-to-download message, can hold the Drive link); photos up to 20 + videos up to 2; up to 5 digital files; shop section (20 sections, e.g. Art Prints - Trendy); renewal automatic ($0.20); GPSR and ECGT legal info.

## ANSWERS FOR THE BUILD (verified live 2026-10-27 with a real API draft + the Etsy editor; nothing saved by hand)
Method: read Etsy's OpenAPI spec (`https://www.etsy.com/openapi/generated/oas/3.0.0.json`), created draft 4604596640 via the API, opened it in the editor. Tony deletes the draft by hand.

**What the API can set at draft creation (`POST /shops/{shop_id}/listings`, form-encoded, 201 on success; Etsy returns 201, not 200)**
- Required: quantity, title, description, price, who_made, when_made, taxonomy_id (2078 Digital Prints).
- Use: `type=download`, `who_made=i_did`, `when_made=made_to_order` (or `2020_2026`; the old templates' 2007_2009 is wrong), `is_supply=false`, `tags` (up to 13; both comma-separated "a,b,c" and JSON array work; repeating the form key keeps only the last), `shop_section_id`, `should_auto_renew`, `return_policy_id`, `is_taxable`, `image_ids`. `styles` did not stick, skip.
- Title rule: Etsy rejects titles with more than 3 words in ALL CAPS ("all_caps" error).
- Never send shipping/weight/dimension fields, `shipping_profile_id`, `readiness_state_id`, or `production_partner_ids` for downloads.
- `state` can be set to `active` or `inactive` on update; the Portal must never call it.

**Answers to Tony's questions**
- Who made it? `who_made=i_did`: API sets it, editor shows "I did". Created drafts get it automatically.
- What is it? `is_supply=false` = "A finished product". API sets it, editor confirms.
- How is this digital content created (Created by me / With an AI generator)? NOT in the API: not in the spec, not in the create/update params, not in the listing response. A draft made via the API arrives with NEITHER option selected, and the editor does not mark it required (no asterisk). So for every AI listing, Tony picks "With an AI generator" by hand in the editor (How It's Made tab) before publishing; the Portal must show this as a manual checklist item, and the description keeps the AI Disclosure paragraph. Open: whether Etsy blocks Publish when it is blank (not clicked); re-check on the first real listing.
- Note to buyers for digital items: the API only has a SHOP-level `digital_sale_message` (already set on the Ikigai shop, ~2,300 chars of the how-to-download note). Per-listing override is not in the API, so rely on the shop message; do not try to set it per listing.
- Digital Prints attributes: set via `PUT /shops/{shop_id}/listings/{listing_id}/properties/{property_id}` with form fields `value_ids[]` and `values[]` (both required; ids from `GET /seller-taxonomy/nodes/2078/properties`). Verified working (200): Aspect ratio (property 570246213622, multi), Orientation (406291158455), Room (145330288592, multi), Home style (145330288652), Art subject (400394338806, multi). They appear in the editor (Orientation showed Vertical, Subject counted). Also available: Occasion 46803063641, Holiday 46803063659.
- Do NOT set (physical-print only): Framing, Depth, Mat included, Frame color, Number of pieces, Materials, Material features, Width, Height.
- Limits in the editor: 20 photos + 2 videos (the API has image upload; video upload is not in the spec, so videos are manual), up to 5 digital files, 13 tags, Aspect ratio up to 5, Room up to 5, Subject up to 3.
- Image + file upload: `POST .../listings/{id}/images` (multipart `image`) and `.../files` (multipart `file` + `name`) both return 201.
- Readback of properties: `GET /listings/{id}/properties` returns 404 for drafts; verify in the editor instead.
- Still manual by Tony in Etsy: AI-generator choice, videos, publish. Legal fields (GPSR, ECGT) were blank on the old drafts; EEA "trader" info, decide separately.

## DECIDED BUILD FLOW + REMINDER (Tony, 2026-10-27)
- No browser automation for regular listing creation: Etsy Terms of Use (section C Automated Tools, section E scraping) let Etsy permit or prohibit bots, scripts and agentic AI at its sole discretion; ban risk to the Ikigai account outweighs two clicks per listing.
- Flow: Tony clicks Copy on the "AI Template" (or "Originals Template") draft in Etsy, which keeps the pre-set AI choice and note to buyers. The agent then finds the new draft via the API (`GET /shops/{id}/listings?state=draft`) and fills title, description, tags, attributes, images and the download file via the API. Tony publishes.
- **REMINDER, do before building `steps.etsy_draft`:** ask Tony for (1) the note-to-buyers text (identical in both templates; the API can already read the shop-level `digital_sale_message`, so confirm that is the same text), (2) the download PDF template, (3) the description template. Tracked in claude-mem work-state list `critical-todo`.
- Check on first real copy: that the copied draft keeps the AI choice and the note.

## Portal feature request (Tony, 2026-10-27): copy-to-clipboard buttons
- One-click "Copy note to buyers" button in the Portal that puts the digital note-to-buyers text on the clipboard, for pasting into Etsy by hand when a listing needs it (the API cannot set it per listing).
- Same idea for other manual steps: "Copy description", "Copy tags", and a manual-steps checklist per listing (pick "With an AI generator", add videos, publish).
- Easy to build: the Portal is a local web app, and browsers allow clipboard copy on localhost.

## IKIGAI CHECKLIST (updated 2026-10-27, test draft deleted by Tony)
- Done: Ikigai Etsy app, login, token verified; API/editor survey; test drafts deleted.
- Tony: give note-to-buyers text, download PDF template, description template.
- Agent: build `etsy_draft` step (API only, never active); Portal copy buttons + manual-steps checklist + trademark footer; mockup step (PhotoCraft swap, upscayl); pull Seller Handbook (AI rules) + verify 5 print sizes.
- Both: one real listing end to end (Tony: Copy template, pick "With an AI generator", videos, publish; agent: fill via API).

## Note to buyers received (Tony, 2026-10-27)
- Tony pasted the digital note-to-buyers text from the Etsy editor. It matches the shop-level `digital_sale_message` the API returns (same opening, same sections, ~2,360 chars). Saved with its line breaks as `Digital_Note_To_Buyers.md` in this folder; this is the text for the Portal's "Copy note to buyers" button.
- It is Markdown (bold, ### headings, numbered lists, links) with emoji. It contains the literal text `&#39;` for apostrophes in "Etsy's"; check how a live listing shows it and fix if it appears as `&#39;`.
- Still needed from Tony: download PDF template and description template.

## Description template received (Tony, 2026-10-27)
- Tony pasted the AI template description; it is identical to the text on the "AI Template |" draft. Saved as `Description_Template_AI.md` (starts with the placeholder `{{OPENING_SEO_SALES_PARAGRAPH}}`, fixed text after it, `&#39;` entities converted to plain apostrophes).
- Structure: per-listing opening paragraph (SEO plus sales pitch for that art, e.g. "if you love abstract art") followed by the fixed template. The leading "Template |" line on the draft was a leftover and is dropped.
- Headings use Unicode look-alike bold/italic characters, not markup, so they paste as-is.
- To fix: the "Perfect For" third bullet is CyberTokyo-specific ("modern cityscapes with abstract art"); make it generic or write it per listing. The Originals template is the same minus the AI Disclosure block (build it by removing that block).
- Still needed from Tony: the download PDF template.

## CORRECTION + Originals description template (2026-10-27)
- Earlier note in this file said the Originals template differs from the AI one by lacking the AI Disclosure block. WRONG: both descriptions contain the same AI Disclosure paragraph (it covers mockups and/or designs made with AI tools).
- Real differences (diffed via API): (1) AI Disclosure sits before Key Features in the AI template, after Key Features in Originals; (2) the "AI Disclosure" heading uses italic Unicode in AI, plain bold Unicode in Originals; (3) typo "prints shops" in Originals vs "printshops" in AI. Everything else is identical.
- Saved as `Description_Template_Originals.md` (same `{{OPENING_SEO_SALES_PARAGRAPH}}` placeholder). Tony's pasted Originals text matches the Originals draft.
- Practical meaning: the real difference between the two listing types is the Etsy "How is this digital content created?" choice (Created by me vs With an AI generator), set by hand in the editor, not the description text. Open for Tony: whether the Originals description should keep the AI Disclosure (mockups may be AI) or drop it when only the mockups are AI.

## DECISION (Tony, 2026-10-27): keep the AI Disclosure in both description templates
- Reason: AI may touch any listing (fixing a hand in a painting, mockups, stock photos of unknown origin), so the paragraph stays in Originals too. The Etsy editor choice ("Created by me" vs "With an AI generator") is the per-listing indicator Tony sets by hand.
- Open (check in the Seller Handbook pull): what Etsy requires for the "Created by me" choice when AI was used for small edits; the description paragraph and the editor choice must not contradict each other.

## Template drafts edited by Tony (2026-10-27), checked via API
- Originals template: "Created by me" chosen; AI template: "With an AI generator" (not readable via API, taken from Tony). AI Disclosure kept in both descriptions. Leading "Template |" line kept on purpose as Tony's visual reminder to add the per-art opening paragraph; the build step must replace it with the opening paragraph.
- Aspect ratios set on both drafts: 2:3, 3:4, 4:5, 5:7 (ISO), 11:14 (these are the five files; all portrait, Orientation = Vertical). Two existing listings also have 1:1 as a sixth; rare, only when the image suits. Landscape designs will come later and need a different template (different aspect ratios, Orientation = Horizontal, probably different sizes/files).
- Both drafts also carry Framing = Unframed and Frame mat included = No (physical-print attributes). Tony said these should not be on digital listings; ask him to reset them in the editor (Framing has a Reset link) if Etsy allows, otherwise the build step will clear them on each copy.
- Originals draft description still shows the typo "prints shops" (cityscapes line is fixed in both).

## CORRECTION (Tony, 2026-10-27): Framing and mat are intentional
- Framing = Unframed and Frame mat included = No on both templates are deliberate: Ikigai sells digital prints with no frame and no mat, so "Unframed/No" is the true answer on every listing. The build step must LEAVE them as copied (or set them to Unframed/No), never clear them. This replaces the earlier "clear them" suggestion; the "never send physical attributes" rule only means no Depth, Frame color, Materials, Width/Height, Number of pieces, etc.
- The "Template |" first line stays on both templates as Tony's reminder to write the per-art opening paragraph; the build step replaces it with that paragraph.

## ATTRIBUTE RULE (Tony, 2026-10-27) — final
- Fixed on every portrait listing (from the template): Aspect ratio (the five sold sizes; 1:1 only on the rare listing that has it), Orientation = Vertical, Framing = Unframed, Frame mat included = No. Rule: if an attribute is a yes/no that truthfully applies and the answer is No, fill in No.
- Never add (physical product only, cannot be given with a digital file): Depth, Width, Height, Materials, Material features, Frame color, Number of pieces.
- Per listing, chosen from the actual art: Home style, Occasion, Holiday, Room (up to 5), Subject (up to 3), plus 13 tags. These help sell the print and are the attributes the idea/listing steps must fill.
- Landscape later: separate template with Orientation = Horizontal and its own aspect ratios.

## Legal and compliance section (researched 2026-10-27, not legal advice)
- Two editor items: (1) GPSR manufacturer and safety information, (2) Legal guarantee and consumer information (ECGT). Both only matter if Tony is a "trader" (business or professional seller) selling to EEA states or Northern Ireland.
- Etsy's help says GPSR applies to physical AND digital items, unless covered by other safety rules. Etsy lets you fill the manufacturer info ONCE at shop level (Settings) or per listing, and offers a GPSR setting to stop selling digital items into EEA countries.
- ECGT: for traders, Etsy automatically shows "This product comes with a legal guarantee of conformity under EU laws" on digital listings for EEA buyers; nothing to type per listing. The ecgt_* API fields are optional extra guarantee details, skip.
- The API spec has no GPSR fields, so the build step cannot set them; shop-level info set once by Tony is the way. Drafts made via the API leave both blank.
- Decision for Tony: (a) fill the shop-level GPSR info once (business name, address, email), or (b) stop selling digital items into EEA countries in GPSR settings. Check whether the shop is marked as a trader under Shop Manager Settings, Legal. Sources: Etsy Seller Handbook articles 1364599291081 and 1093438529659; Etsy Help ECGT article 43191692248343.

## EU / legal research result (research agent, 2026-10-27; not legal advice)
- GPSR (EU 2023/988) is a product-safety law, NOT privacy. Art. 3(1) defines product as "any item"; no named coverage of static art files; Commission Q&A says "physical or digital products too, including software" (aimed at software). Etsy's help says GPSR covers digital items. Conclusion: very likely not an issue for printable art, medium-high confidence; Etsy's wording is broader.
- Etsy GPSR opt-out (Shop Manager > Settings > Options > "Choose how you sell to GPSR states") blocks ALL EEA/NI purchases for the covered type; community report says listings stay searchable. No evidence found that digital listings are blocked for empty GPSR fields (the key forum thread needs a login; unverified).
- DSA economic operator ("Partners you work with"): Etsy says traders selling into the EU may need to disclose one; Art. 30 DSA is mainly marketplace-collected trader identity. No EU Responsible Person needed for digital-only (medium-high).
- ECGT: Etsy auto-shows the legal-guarantee notice for traders on digital listings; nothing manual. Withdrawal: Etsy says digital downloads may be exempt but sellers should state in the listing that they are not eligible for withdrawal; otherwise the withdrawal period may extend up to 12 months.
- Privacy (GDPR / UK GDPR): Etsy's Seller Policy (per secondary summaries, page not fetchable) makes sellers responsible for buyer data they receive and says sellers offering items to EU buyers must have a GDPR-compliant privacy policy. NI falls under UK GDPR.
- Recommended actions (pending Tony's yes): (1) leave EEA/NI on, no Responsible Person; (2) add LLC name/email/address in the GPSR "Add info" field on both template drafts so copies carry it (displayed publicly, so use a business address, not a home address); (3) add a one-sentence digital-download no-withdrawal notice to the Terms of Use in both templates; (4) publish a short shop privacy policy (what is received: name, email, order data; use; retention; contact; no marketing use of buyer emails).
- Caveats: EUR-Lex, Etsy Seller Policy and the Commission Q&A could not be fetched directly; several points rest on secondary quotes. Re-check on the Seller Handbook pull.

- Buyer data Tony actually sees on Ikigai digital orders (his report, 2026-10-27): username, what was ordered, and a "ship to" showing only the city. No name, email or street address. So the privacy policy can be very short (what Etsy passes on, no marketing use, no collection outside Etsy). My earlier "name and email" assumption was a guess, not what he sees.

## DOWNLOAD PDF TEMPLATE received (Tony, 2026-10-27)
- Reference file saved: `005_Ecommerce/Etsy-Ikigai/Download_PDF_Template_Reference.pdf` (4 pages, letter size; a copy of the Thank You letter from design 00120 Pastel Waves). Tony cannot find the original template source, so this PDF is the template, "based off a different design".
- Page 1: Ikigai Digital Studio logo, "THANK YOU for your order and supporting a small business.", a black DOWNLOAD button that is a hyperlink to the buyer's Google Drive folder, note "You do NOT need a Google Account to download the zip file", pointer to the next pages, and "reach out via Etsy Messaging". Background is a tropical-leaf design.
- Page 2: how to download the zip from Google Drive (steps 1 to 3, Mac and PC, example filename `00000-Filename-Example.zip`).
- Page 3: "Common frame sizes" chart image.
- Page 4: "Helpful tutorials": four YouTube video thumbnails (each linked) plus a Beacons link (https://beacons.ai/ikigaidigitalstudio). These are fixed for every listing.
- PER-LISTING VARIABLE: only the Google Drive folder URL on the DOWNLOAD button (page 1 link annotation). Pages 2 to 4 are identical on every PDF. CONFIRMED by Tony (2026-11-03): the design always stays the same on every PDF; the ONLY thing that changes is the hyperlink on the DOWNLOAD button.
- Drive convention: each new art print gets a new folder in Google Drive with a numbering convention (design number then name, e.g. 00120 Pastel Waves), shared as "anyone with the link"; the folder holds one zip of the purchased images. Account: Tony believes it is the Bored Nomad Google Drive (confirm which account and the exact folder naming before the build).
- Build implication: `steps.etsy_draft` (or an earlier step) must generate one PDF per listing by taking this template and replacing the page 1 button URL with that listing's Drive folder link, then upload it as the listing's digital file (replacing the placeholder). A PDF library that rewrites the link annotation (for example pypdf) is enough; no redesign needed.

## FUTURE PLAN: move off Google Drive (Tony, 2026-10-27)
- Tony wants to replace Google Drive with a better storage/delivery solution later (to be discussed; not decided).
- Consequence: every existing Etsy listing's download PDF would need regenerating with new links and re-uploading, because buyers receive that PDF. Keep the PDF generator link-source agnostic so the swap is one config change plus a bulk re-upload (Etsy API supports listing file delete and upload).
- Also update the matching text on PDF page 1 and 2 ("google drive folder", "Google Account", Drive download steps) when the storage changes.

## Mockup originals (2026-10-27)
- Mockup sets are large, so they are git-ignored; locations of the originals are in `005_Ecommerce/Etsy-Ikigai/Mockup_Originals_Locations.md`.

## CORRECTION (checked live via API getShop, 2026-11-03): privacy policy and refund policy already exist
- The shop already has a full privacy policy (policy_privacy, effective 2024-06-23, Uno Mas Creative LLC dba Ikigai Digital Studio): collection limited to what Etsy provides (username, purchase details, messages), uses, sharing, retention, GDPR rights, security, contact emails and a Raleigh NC address. Also mirrored in policy_additional. Structured policies are on.
- Refund policy (policy_refunds): "I DON'T ACCEPT RETURNS, EXCHANGES, OR CANCELLATIONS. But please contact me if you have any problems with your order." This already covers cancellations; listing template also says returns are not accepted for instant downloads.
- So recommended action (4) "publish a short privacy policy" is NOT needed. Remaining optional polish only: (a) add the word "withdrawal" to the refund policy/Terms, (b) mention UK GDPR for Northern Ireland/UK buyers, (c) the policy text shows literal &quot; entities (check how it renders on the shop page).
- The Etsy API (shops_r) exposes shop policies (policy_privacy, policy_refunds, digital_sale_message etc.) read-only, so the Portal can check them without a browser. Access tokens last 1 hour: refresh with etsy_auth.py --name ikigai --refresh.

## DECISION (Tony, 2026-11-04): AI Disclosure wording replaced (per Etsy Rules Bible conflict #3)
- AI template line: "This artwork was created with the help of AI tools, using my own original prompts and creative direction, then curated and finished by me. Product mockups may also be AI-assisted. I hold the commercial rights needed to sell this artwork."
- Originals template line: "This artwork was created and finished by me using digital design tools. AI-assisted tools may have been used for small edits or touch-ups, and product mockups may be AI-assisted."
- Commercial rights: Tony confirms his paid AI tool memberships include commercial rights, so the sentence stays.
- Buyer license is unchanged: personal use only, no resale, redistribution or commercial use.
- Saved template files updated; Tony pastes the new lines into the two Etsy drafts, then verify via API.

## TONY'S POSITION on public-domain / reimagined art (2026-11-04)
- Tony restores public-domain artwork (color reproduction, grain removal, upscaling) and sometimes cuts pieces out for mixed media; sometimes changes nothing.
- His argument: Etsy's text never names "public domain"; curated public-domain pieces can fall under "Handpicked" or "Sourced" (a print can become craft material, e.g. wrapping paper or collage).
- Agent's assessment (not a ruling): Etsy's text says digital downloads are "Designed by a seller" (original content created by the seller) and lists "someone else's work" scans as not qualifying; Handpicked examples are physical vintage items and Sourced requires primary purpose of creating by hand. Tony's reading is arguable but unconfirmed; enforcement unknown. Etsy Seller Support has not been asked.
- Listings touched: only Funny Bathroom Portrait (Ducreux, 1825753177) is clearly public-domain-based; ginkgo listing 1868376186 has artist-name tags (kuniyoshi, Hokusai) to remove.
- Pipeline: ask "what did you change?" for public-domain pieces and keep the answer in the draft log; describe the work honestly in the listing.

## PACKAGING (read from the real 00120 Pastel Waves upload, 2026-11-04)
- Design folder (iCloud: 001-Design Related/001-Designs/001-Designs Completed/00120-Pastel Waves/): `01-Printables/` (final JPGs), `02-Thumbnails/`, `03-Etsy Images/` (listing mockups, detail, video), `04-Google Drive/` (what gets uploaded), `ALT Mockups/`, `Design Elements/`, plus the Thank You PDF at the folder root. Folder name = design number + name (`00120-Pastel Waves`).
- Zip `00120-Pastel Waves.zip` (about 104 MB) holds 6 files: the Thank You PDF (the same PDF the buyer gets from Etsy) and 5 print JPGs named `<Name>_<ratio>_<size>.jpg`: `_2x3_24x36`, `_3x4_18x24`, `_4x5_24x30`, `_11x14_22x28`, `_ISO_A1_23.4x33.1`. (1:1 listings add a sixth image.)
- Etsy download file = only the Thank You PDF (about 6 MB, one file, well under Etsy's 5 files / 20 MB limits). The images live in the Drive zip behind the PDF's DOWNLOAD button.
- The existing zip contains macOS `__MACOSX` junk entries (made by Finder zipping); the pipeline should build zips without them.
- Pipeline packaging steps: 1) export the 5 sized JPGs into `01-Printables`; 2) zip them with the PDF (no junk); 3) upload the zip to a new numbered Drive folder; 4) make the folder link-shareable; 5) write that link into the Thank You PDF button; 6) upload that PDF as the Etsy digital file. Drive account and folder naming CONFIRMED 2026-11-04, see the section at the bottom.

## ART PRINT FOLDER SCAFFOLD (Tony's standard, read from 00120-Pastel Waves, 2026-11-04)
Rule from Tony: new designs are built and saved in the PROJECT folder (Agent-OS), never in iCloud; the iCloud folder is read-only reference for the structure. The exact project location for design folders is still to be approved by Tony before the pipeline creates any folder.

Per design folder `<number>-<Name>` (e.g. `00120-Pastel Waves`):
- `<number>-<Name>-Ikigai Thank You Letter-.pdf`: the finished Thank You PDF (also copied into 04).
- `01-Printables/`: 5 final JPGs named `<Name>_<ratio>_<size>.jpg` (2x3_24x36, 3x4_18x24, 4x5_24x30, 11x14_22x28, ISO_A1_23.4x33.1; 1:1 listings add a sixth).
- `02-Thumbnails/`: one small preview per printable, same name plus `_TN` (about 150-330 KB).
- `03-Etsy Images/`: per-design listing images: `01_Main_Mockup_72dpi.png`, `02_Poster_Mockup_72dpi.png`, `07_Detail.png`, room mockups `08_`, `09_`, `10_...jpg`, and `1A_Video_Mockup.mp4`. Numbers 03-06 are missing here because they are the shared images (Instant Download, Download Contents, Important Notes, Size Guide, Customer Reviews) that live in the Standard Package / 1to1 mockup sets copied into Etsy-Ikigai (agent inference; confirm with Tony).
- `04-Google Drive/`: exactly what is uploaded to Drive: the Thank You PDF and `<number>-<Name>.zip` (5 JPGs + PDF; no `__MACOSX` junk when the pipeline zips).
- `ALT Mockups/`: spare mockups not used in the listing (e.g. `12_..._Living_Room.jpg`).
- `Design Elements/`: the master artwork (`<Name>.png`, about 97 MB) plus `Reference/` (the generation or inspiration image).
- Sibling folders in the iCloud library for reference: `00000-Patterns`, `00000-Size Charts & Mockups`, `00000-Templates`, numbered designs from `00001-...`. Older/other designs differ (e.g. Practice Love uses Ads/Assets/Mockups) so 00120 is the current pattern.

## LISTING IMAGE MAP (read live via API + viewed, 2026-11-04; Tony's rule: keep this order)
All 18 live listings have 1 video and 11-19 images. Newest listing (Abstract Desert Landscape, 4390688055, 11 images) is the model. Slot order:

| Slot | Image | Source | Changes per design? |
|---|---|---|---|
| 1 | Main mockup (framed print leaning on a wall) | `01_Main_Mockup` (3 Etsy Images) | YES, generated |
| 2 | Poster mockup (hands holding the print) | `02_Poster_Mockup` | YES, generated |
| 3 | Instant Download ("digital product only") | `03_Instant_Download.png` | NO, same always |
| 4 | What You Will Receive (PDF link, zip, ratio tiles) | `04_Download_Contents.png` (1:1 listings: `04A_Download_Contents-6Images.png`) | NO (two variants) |
| 5 | Wall Size Guide | `06_Wall_Art_Size_Guide.png` (1:1: `06A_Wall_Art_Size_Guide_With_1x1_Ratio.png`) | NO (two variants) |
| 6 | Important Notes (no refunds, colors vary, AI transparency, personal use) | `05_Important_Notes.png` | NO, same always |
| 7 | Detail close-up | `07_Detail` | YES, generated |
| 8 to 19 | Room mockups | generated | YES (12 slots; today's listings use 3 to about 9) |
| 20 (last) | Loved by Customers (testimonials) | `06A_Customer_Reviews.png` (1:1: `06B_Customer_Reviews.png`) | NO, same always |

- Slot numbers are NOT the same as the file-name numbers (e.g. Size Guide is file 06 but slot 5; Important Notes is file 05 but slot 6). `List_Order.png` in the mockup folder is Tony's order reference. File prefixes 06A/06B are reused between the two package folders for different images, so the pipeline must map by name, not by prefix.
- Etsy limits now: 20 images + 2 videos. Tony wants to use the extra slots: 9 additional room-style images (11 + 9 = 20, reviews last) and 1 additional video (slot 2 videos total). Today every listing has 1 video (`1A_Video_Mockup.mp4`).
- Older listings vary (e.g. the blue ginkgo listing has a room mockup in slot 3, and a special paper-texture comparison detail in slot 8). The newest layout above is the standard for new listings.
- Generated per design: slots 1, 2, 7, the room mockups (8 to 19), and the video(s). Fixed: slots 3, 4, 5, 6 and the last slot.
- API: images are uploaded with `uploadListingImage` (multipart, `rank` sets position); videos cannot be uploaded through the API, so Tony adds the video(s) by hand.
- Note for the Rules Bible: the "Loved by Customers" image must show genuine reviews only.

## FILE NUMBER = SLOT NUMBER (Tony's rule, 2026-11-04; supersedes the old prefixes)
Every listing image file is named with the number of the slot it occupies. Always a number. Images 01 to 20, videos numbered separately.

| File | Slot | Fixed or per design |
|---|---|---|
| `01_Main_Mockup` | 1 | per design |
| `02_Poster_Mockup` | 2 | per design |
| `03_Instant_Download` | 3 | fixed |
| `04_Download_Contents` (1:1: `04_Download_Contents_1x1`) | 4 | fixed (two variants) |
| `05_Wall_Size_Guide` (1:1: `05_Wall_Size_Guide_1x1`) | 5 | fixed (two variants) |
| `06_Important_Notes` | 6 | fixed |
| `07_Detail` | 7 | per design |
| `08_` to `19_Room_Mockup` | 8 to 19 | per design (12 mockups) |
| `20_Customer_Reviews` | 20 | fixed (no 1:1 variant; the two copies are byte-identical) |
| Videos: `Video_01`, `Video_02` | video 1, 2 | per design (Tony adds by hand) |

- Every new listing uses all 20 image slots (8 to 19 = 12 room mockups: today's 3 plus the 9 additional), so Customer Reviews is always 20.
- This renames the old files (old 04 Download Contents stays 04; old 05 Important Notes becomes 06; old 06 Wall Art Size Guide becomes 05; old 06A/06B Customer Reviews becomes 20; old 04A and 06A 1:1 files get the `_1x1` suffix; old `1A_Video_Mockup` becomes `Video_01`). Applied to the working copies in Etsy-Ikigai when we build; the iCloud originals and older designs keep their old names.

## 1:1 LISTINGS (Tony, 2026-11-04)
- 1:1 listings will be very rare. Only slots 4 and 5 differ: 04 shows the additional file in the download (6 images), 05 adds the 1:1 ratio to the wall size guide. Slots 3, 6 and 20 are identical to the standard set (verified by file hash).
- Files already provided and copied: `002-Includes 1to1 Ratio/04A_Download_Contents-6Images.png` (becomes `04_Download_Contents_1x1`) and `06A_Wall_Art_Size_Guide_With_1x1_Ratio.png` (becomes `05_Wall_Size_Guide_1x1`). Nothing more needed from Tony for 1:1.
- Landscape listings, if started later, will need their own versions of the shared images (separate template).

## MOCKUP ASPECT-RATIO RULE (Tony, 2026-11-04)
- AI-generated mockups (Nano Banana, GPT Image 2, etc.) must show the artwork in an aspect ratio the listing actually sells. Normally that means only 2:3, 3:4 or 4:5 on the wall; 11x14 and ISO can appear in the extra room mockups but nobody measures them, so they are not required.
- Exact ratio is not required. Close enough by eye is the standard. A mockup whose framed art is clearly a different shape from the sizes sold (for example square or wide when the listing is portrait 2:3 to 4:5) is rejected and regenerated.
- Pipeline check (to build): after each mockup is generated, measure or visually check the framed art's width to height and flag it if it is clearly outside the sold ratios (suggested tolerance: within about 10 percent of the nearest sold ratio, to be tuned by eye). Tony reviews flagged ones; nothing is auto-approved.
- Also matches Etsy's image rule that mockups must not mislead about what the buyer gets (see Etsy_Rules_Bible.md).

## ART WORKFLOW (Tony's answers, 2026-11-04)
- Inspiration folder: `Creative_Inspiration/`. Tony saves images only: screenshots, photos of art, and sometimes mockups (a painting hung in a living room). The agent must interpret what each image is; when a mockup is dropped, the ART is the reference, never the room.
- On drop, each image is analyzed, renamed by what it is, and given a style profile saved as a `.md` file (JSON-style fields) so a library of styles builds up. A style is pulled from the library and passed to the image model with a new subject.
- STYLE means painting style: brushstrokes, composition, how the paint behaves (fine brush marks, subtle paint changes like a real brush on canvas). Style reference and subject stay independent and flexible (same style with a cat holding a wine glass, or a dog, or a different palette).
- Dashboard uploads: separate manual upload slots for (a) style references and (b) subjects/characters. Tony decides per image which role it plays (a public-domain painting can be the subject or the style). Tony can also give an edit instruction on an uploaded image, e.g. "cut out the person on the bike and use only that in the new composition" (public-domain cutout as mixed media).
- Art first, then everything else: generate the ARTWORK (never a mockup). Tony curates, requests changes, finalizes the art. Only after his approval (a button or keyword in the dashboard) does production run: mockups, listing images, title, SEO description, tags, researched with Alura data (real search data, not guesses).
- Prompts: the agent writes them. They must be nuanced and detailed, not generic or vector-looking: real brushstrokes, paint texture, canvas feel. Learn from the inspiration styles; also look for a prompt-writing skill (existing: GPT-Image-2-Prompting-Guide skill; use find-skills for more).
- 4 variations per art prompt; Tony picks which he likes.
- Engines in a dashboard dropdown (not hard-coded): Nano Banana Pro, Nano Banana 2, GPT Image 2. Default undecided until Tony compares quality.
- Upscaling: Upscayl is the default for now; test its quality first.
- Etsy rule support: log the prompt, engine, source images and Tony's pick for every design (human oversight record; for public-domain pieces also log what was changed).

## INSPIRATION SCAN built 2026-11-04
- Script: `001_Architecture/Scripts/inspiration_scan.py` (vision via OpenRouter `google/gemini-3.7-flash`, fallbacks qwen3.5-flash then OpenAI gpt-4o-mini; keys read from `~/.env-secrets`, never printed).
- Schedule: launchd `~/Library/LaunchAgents/com.agent-os.inspiration-scan.plist`, every day at 03:00 (runs on wake if the Mac was asleep). Run log: `001_Architecture/Scripts/inspiration_scan.log`.
- Outputs: images renamed in place inside `Creative_Inspiration/`; style profiles in `Creative_Inspiration/Style_Profiles/<same stem>.md` (YAML frontmatter: id, title, new_filename, original_filename, image_path, scanned, source_type, status, medium, era_feel, subject, style_prompt, avoid, palette_hex, tags, vision_model, quality_flags, style_json); append-only log `Creative_Inspiration/Rename_Log.md`.
- Numbering: 4-digit prefix, first ever 0001, next = highest number in the log or filenames + 1. Name = `NNNN_` + 3 to 6 Title_Case words describing the artwork (medium, style, subject), extension kept. Files logged `ok` are never renamed again; `error` rows are retried next run.
- Style vs subject: the style prompt fragment never contains subject words (the script flags it in `quality_flags` if it does); the subject has its own field. Mockups, screenshots and photos: only the artwork inside is analyzed.
- Run by hand (also what the dashboard "scan now" should call): `/opt/homebrew/opt/python@3.14/Frameworks/Python.framework/Versions/3.14/bin/python3 001_Architecture/Scripts/inspiration_scan.py` (add `--dry-run` to preview, `--limit N` to cap).
- Undo: `... inspiration_scan.py --undo 0004` renames that image back to its original name (nothing is deleted; profile kept with `status: "undone"`; the file is then left alone by future scans).
- First run 2026-11-04: 9 images scanned as 0001 to 0009, 0 errors.

## TRADEMARK CHECK FOR TYPOGRAPHY (tested 2026-11-04)
- Need: any artwork containing text (slogans, quotes) gets screened against trademarks before production. Volume: about 5 checks a week at most.
- Findings: USPTO has no official name-search API (the Open Data Portal APIs are patents, bulk data and TSDR status-by-serial only). Composio has an EU trademark search tool (Strale, `STRALE_EU_TRADEMARK_SEARCH`, EUIPO records, connected, appears to be paid per call) but no US search. OpenRouter has no trademark data.
- Tested: a real browser pane loaded tmsearch.uspto.gov with no bot block and ran the phrase "new phone who dis" (one search, no workaround needed). Results: 55,494 fuzzy hits. Exact phrase "NEW PHONE, WHO DIS?": one LIVE registered mark in class 028 (card games, What Do You Meme, LLC); dead ones in classes 009, 025 and 032. No live mark in the art-print or digital-download classes seen on page 1.
- Plan: check step = exact-phrase search on tmsearch (live status filter, classes 9, 16, 41 plus 25/21 for context), show hits to Tony; nothing auto-approved. Fallback if the site blocks automation: give Tony a pre-filled link. EU via Composio Strale tool if EU coverage is wanted. This is screening, not legal clearance; song lyrics and titles are a copyright question, not covered by this search.

## TRADEMARK CHECK OUTPUT FORMAT (Tony, 2026-11-04)
- Output is a traffic-light flag, nothing more: GREEN, ORANGE or RED, plus at most one line of reason and the short disclaimer "Estimate from the information found, not legal advice."
- GREEN: likely in the clear (e.g. only dead marks, or live marks in unrelated goods). ORANGE: could go either way (live mark in a related class, close sound-alike, or unclear). RED: not in Tony's best interest to pursue that wording (live mark in the same or closely related goods, strong or famous brand).
- No long explanations, class lessons or logistics in the output. Tony decides every item; nothing auto-approved. Check sound-alike spellings too (e.g. Who/Hoo/Woo) and the class that matches the product (25 apparel, 16 prints, 9 downloads).

## IDEA ENGINE: THE FUNNEL (Tony, 2026-11-04)
- Stage 1 = a plain table of 10 ideas, one descriptive line each, with Approve / Deny buttons (and a proven/test tag). Approved ideas go into the idea bank; denied ones are replaced from the researched pool. Later stages narrow each approved idea step by step.
- NO room-type stage, ever. The art decides where it fits (cyberpunk game art suits a game room or bedroom, not a living room; vintage birds could suit a kitchen). Room mockups are chosen from the finished art.
- Ideas must be RESEARCHED before they appear. No random or generic ideas (e.g. just "pastel waves"). Each row must be specific and descriptive and backed by evidence.
- NOT RULES (Tony's correction, 2026-11-04): crossing two interests into a niche (cats x cat moms x nurses) is ONE example of how an idea can be found, not the method and not the only path. The agent must think broadly and come up with its own ways to find ideas, and make them its own; copying Tony's example or turning it into a fixed methodology is wrong.
- What IS required: ideas are specific, descriptive and researched. Evidence comes from several real sources (Google Trends, social hashtags/Pinterest, Etsy market data through Alura, since Etsy scraping is banned), and the agent forms a consensus on whether the idea is worth pursuing before it reaches the table.
- Tony's examples (cats, cat moms, nurses) are illustrations of how to think, not things to build and not a template.

## NICHE RESEARCH FINDINGS (research agent, 2026-11-04): see `Niche_Research_Methods.md`
- Good niches are a person, a moment and a reason (who hangs this, why now, what they search), not a style. Several ways of noticing, not one pipeline. Validation = several sources agreeing (demand: Alura and Google Trends; mood: Pinterest and Etsy trend report; supply: top-result age, sales, reviews; legal: trademark check); disagreements are flagged, not averaged. Each idea row should carry why this buyer, why now, who else sells it, and one warning sign.
- Seasonality: list about 3 months ahead (6 weeks minimum). As of 2026-11-04 the Christmas window is mostly closed; January-February and spring events should go live in the next 4 to 12 weeks.
- No installable skill teaches niche thinking; skills reviewed were shallow or unproven. Tony's rule: only 1K+ installs, SkillSpector first, never the EverBee wrapper. Reddit could not be read by the agent (blocked), so Reddit insight is snippet-only.

## DASHBOARD DESIGN DIRECTION (Tony, 2026-11-04)
- Mostly chat-driven: a main chat window that always stays open; tabs for the different areas. Ikigai Digital Studio is its own tab (Etsy-specific for now; Etsy is the only sales channel today, but later Shopify, Lemon Squeezy or Tony's own website may sell the prints, so keep sales-channel logic swappable).
- Seeds: Tony adds his own seed ideas by typing them in the chat window. The engine also keeps filling the researched pool on its own (both).
- Flow: the engine shows 10 researched ideas; approved ones move into an idea bank (another bank in the same tab of the same dashboard). Layout to be tinkered with after the first build.
- Bigger picture: this Ikigai dashboard will plug into a larger business dashboard that controls everything (content creation, POD, affiliate marketing, etc.). Build it as a self-contained module with clean interfaces so it can be plugged in later.

## IDEA POOL SCHEDULE AND CAP (Tony, 2026-11-04)
- Pace: Tony WANTS to make about 20 prints a week, which is a relaxed wish, NOT a requirement and not set in stone; not rushing the first week. Curated carefully. Tony takes his time approving ideas.
- Refresh runs once a week (plus a refresh-now button). New ideas ADD to the list if Tony hasn't approved or denied the old ones, so the list can grow to 50 to 100, shown in a scroll window.
- Hard cap of 100 ideas. At the cap, generation stops. When Tony approves or denies some, the next scheduled run generates enough new ideas to get back to 100 (e.g. approve 2, get 2 more).
- Approved ideas move into the idea bank (same tab); denied ideas leave the list.
- DECIDED (Tony, 2026-11-04): keep it modest. The weekly run adds about 10 ideas (up to the 100 cap); no push to fill 100 quickly. The 20 prints a week is a loose goal, not a first-week requirement.
- TASTE LEARNING (Tony): every approve and deny teaches the engine Tony's taste and what he wants in the shop. That taste profile feeds back into the research agent so future ideas are curated to him. Fewer, better ideas matter more than volume.

## DENY COMMENTS (Tony, 2026-11-04)
- When Tony clicks Deny on an idea, the dashboard asks if he'd like to comment on why, pointing him to the chat window (no fixed reason buttons). Comments teach the taste profile and go to the research agent. A bare deny still counts as a signal.

## Drive account and folder CONFIRMED, Designs folder created (2026-11-04)
- Drive account: info@borednomad.com (Bored Nomad workspace). Verified 2026-10-26 via the Portal Drive helper (`Portal/app/drive.py`, token `~/.config/agent-os-drive/token.json`). This closes the "which account" question above.
- Drive parent folder: "Ikigai Digital Studio", ID `16zSQOE4UeRYvMyZrE5llaNgR-ZWZ4YsQ`, write access confirmed. It holds 18 numbered design folders (00060 to 00120, non-sequential). Next folder name is auto-sequenced as `NNNNN-Title` after the highest existing number (gaps are not reused).
- Folder naming for new prints: same as the design folder name (design number + name).
- Created `005_Ecommerce/Etsy-Ikigai/Designs/` (Tony approved 2026-11-04) for new print design folders.
- AI Template draft heading typo ("Discloseure") FIXED by Tony (reported 2026-11-04). No longer open.

## DASHBOARD V1 DESIGN APPROVED (Tony, 2026-11-04)
- Tony approved the look and layout of the Portal dashboard as "version 1": chat as a compact bar along the bottom (about a quarter of the height), idea table and idea bank full width above it (about 75%).
- Built: idea table with tags and evidence, idea bank, seeds and deny comments via chat, taste events and profile, 100-idea cap, refresh-now, tab layout, import path (`python -m app.import_ideas batch.json`, `POST /ikigai/api/ideas/import`). 17 tests pass.
- Not built yet: automatic research job, chat answering with a model, Art/Production/Performance tabs.
- Run locally: `http://localhost:8800` (uv command in `Portal/README.md`). Do NOT run `app/seed.py`: it inserts placeholder ideas.
- Next: import the first real researched batch (research agent running), then stage 2: art generation.

## MOCKUP STEP PARTLY BUILT (2026-11-05)
- `Portal/app/mockups.py`: slots 1, 2, 7 built from the PSDs with photocraft-cli `layer.smartObjects.replaceContents`. That command does not scale, so the art is cover-cropped (centre) and resized to the smart object's native size first (main 1931x2732, poster 1664x2348, detail 3039x3031; read at run time). Fixed slots 3, 4, 5, 6, 20 are copied with the slot-number names. Output: `Designs/<NNNNN>-<Name>/03-Etsy Images/` (git-ignored images).
- Detail PNG came out 27 MB (Etsy limit 20 MB), so over 19 MB it is saved as `07_Detail.jpg` (q95, 2.7 MB).
- Source art is the ISO A1 print JPG. Detail crops a centre square (about 30% of the art cut); Tony to confirm that is how he wants the detail zoom framed.
- Not built: room mockups 8-19 (AI, with the aspect-ratio and fidelity checks) and the video(s). 1:1 variants of slots 4/5 not wired (rare).
- Proven on 00121 Book Club Cat; 55 Portal tests pass.
