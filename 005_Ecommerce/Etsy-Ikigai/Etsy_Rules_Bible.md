# Etsy Rules Bible (IkigaiDigitalStudio)

**Purpose:** one place every agent checks before any Etsy listing or automation work for IkigaiDigitalStudio (100% digital printable wall art, mixed AI-assisted and original designs, US + EU/UK buyers, draft-only API pipeline).

**Last pulled 2026-11-04.**

**Re-pull schedule:** re-pull monthly AND before any listing or automation work. Etsy changed AI, listing-image, Seller Policy and Terms of Use pages in Jul-Oct 2026. If a source below shows a "last updated" date newer than the one recorded here, treat this file as stale for that section.

**Confidence tags:** VERIFIED = page fetched and read on 2026-11-04. SECONDARY = third-party or community report, not Etsy's own text. UNVERIFIED = could not confirm from a first-party page. Paraphrased throughout; follow the links for exact wording. This is research, not legal advice.

---

## 0. Rules that matter most for the pipeline (checklist)

1. **Drafts only, never publish.** `createDraftListing` makes a draft; publishing = `updateListing` with `state: active`. The pipeline must never send that. Every draft needs Tony's per-listing review before he publishes by hand. (API reference, VERIFIED)
2. **Human in the loop per item is now a policy requirement, not just Tony's preference.** Etsy (22 Oct 2026) bans bot-generated listings and mass-automated generation "without individualized human oversight"; every item needs direct human prompting, curation and creative input. Violations: removal, possible shop closure. Keep a record of Tony's prompts/choices per design. (AI stance, VERIFIED)
3. **Disclose AI inside the listing description for every AI-assisted item.** Mandatory under Seller Policy + Creativity Standards. Never describe AI work as handmade or "entirely my own creation." Do not put the AI line on listings where nothing was AI-made. (VERIFIED)
4. **Digital file limits:** max 5 files per listing, 20 MB each, file names 70 chars (letters, digits, . _ -), no variations on digital listings, supported types include JPG, PNG, PDF, ZIP. (Etsy Help, VERIFIED)
5. **Listing limits:** title up to 140 chars (aim under 15 words, no "sale/free shipping/perfect"), 13 tags max, 20 chars per tag, up to 20 photos + 2 videos (5-15 s). API title only allows letters, numbers, punctuation, whitespace, TM/C/R, and `% : & +` once each. (VERIFIED)
6. **Images:** must show what the buyer actually gets. Digital downloads are exempt from the "unedited photo of the real item" rule but need a visual preview/excerpt of the content; AI-made or AI-edited mockups are allowed only if accurate. (Listing Image Requirements, 22 Oct 2026, VERIFIED)
7. **No brand/artist/studio/franchise names** (e.g. "Studio Ghibli", "Disney", "Banksy") in titles, tags, descriptions, attributes. "Inspired by" or "-style" does not protect you. (Etsy IP guidance, VERIFIED)
8. **No scraping Etsy with bots/browser automation** (Firecrawl, Playwright, extensions) without Etsy's written permission; use the API for own-shop data only. Do not feed Etsy content into ML/AI training or "analytics" uses beyond what the approved app purpose covers. (Terms of Use, API Terms, VERIFIED)
9. **No QR codes or off-Etsy payment/contact/discount steering** anywhere in files, PDFs, messages. A delivery PDF containing a file link is common practice but is NOT blessed by any Etsy page I could find; see Conflicts. (Off-Platform policy, VERIFIED; PDF-link practice SECONDARY)
10. **Honest pricing/sale claims only.** No fake "was $X" or fake countdowns. (Seller Policy, VERIFIED)
11. **EU/UK:** digital downloads need explicit buyer consent + withdrawal-right waiver to be non-refundable; listings must clearly say the right of withdrawal does not apply and why. GPSR: not enforced for art/print categories in the API list; Etsy's help still says GPSR covers digital too, so confirm trader status. (VERIFIED, see section 6)
12. **API hygiene:** stay within the approved Application Purpose (changes need Etsy's prior approval), never create extra keys to dodge rate limits, handle 429 with backoff, request minimum data, no caching beyond need. (API Terms, VERIFIED)

---

## 1. AI rules (Etsy Seller Handbook + Help)

| Rule (plain English) | Source / last updated | Confidence |
|---|---|---|
| Seller-prompted AI art is allowed: AI output generated from the seller's own original prompts, curated by the seller. Falls under "Designed by a seller" (digital downloads of original designs). | AI stance, Oct 22 2026; Creativity Standards, Jun 10 2025 | VERIFIED |
| Must disclose AI use in the listing description. Policy text says "in your relevant listings" (Seller Policy) and "within their listing description" (Creativity Standards, AI stance). | etsy.com/legal/sellers (Oct 5 2026), etsy.com/legal/creativity (Jun 10 2025) | VERIFIED |
| Bot-generated content banned: every item needs direct, individual human prompting, curation and creative input into that specific item. Mass-automated generation of listings/products by scripts with no individualized human oversight is prohibited. | AI stance, Oct 22 2026 | VERIFIED |
| Bot-generated listings without human involvement are removed and may get the whole shop removed. | "Important updates to AI use on Etsy", Oct 22 2026 | VERIFIED |
| AI-generated functional instructions banned (patterns, recipes, plans, manuals, how-to guides/e-books whose purpose is a specific result). Not relevant to wall art, BUT the Drive-link tutorial PDF teaches "how to resize/unzip"; keep that human-written. | AI stance, Oct 22 2026 | VERIFIED |
| AI prompt bundles banned. | AI stance; Creativity Standards | VERIFIED |
| Cannot misrepresent AI work as handmade or entirely the seller's own creation. | AI updates FAQ, Oct 22 2026 | VERIFIED |
| Listing photos: even with AI, images must honestly show what the buyer gets. No AI edits that make the item look better, higher quality or materially different. | AI stance; Listing Image Requirements Oct 22 2026 | VERIFIED |
| At least one unedited photo against a real background is required for most products. **Digital downloads are an exception**: they should include a visual preview or excerpt of the content; representative/AI imagery is OK only if it does not mislead. | Listing Image Requirements, Oct 22 2026 | VERIFIED |
| Allowed on non-required images (incl. AI tools): fix lighting/colour, crop, resize, replace background, provided the product is represented accurately. | Listing Image Requirements | VERIFIED |
| Etsy now detects AI-generated images in the listing form and shows tips; buyers can report misleading AI imagery (initially no automatic enforcement). Etsy says it will explore buyer-facing AI labels "in the coming months." | AI updates article, Oct 22 2026 | VERIFIED |
| Best practice: if AI edited any listing photo, say so in the description. | AI updates article | VERIFIED |
| Penalties: removal; severe or repeated violations can mean permanent shop closure. Listing fees stay payable; appeals available via Shop Manager > Policy violations (expanding to most policy areas by end of 2026). | AI stance; Newly Crafted (Sep 2026) | VERIFIED |
| California SB 1050 (effective Jan 1 2027): listing images/videos that prominently feature an AI-generated "synthetic performer" (realistic AI person) may need a clear AI disclosure when reaching California buyers. Relevant if lifestyle mockups show AI people. | AI updates FAQ, Oct 22 2026 | VERIFIED |
| Listing-form field "How it's made" exists (who made it, what it is, when made, production partners). Community sources describe a choice "Created by me" vs "With an AI generator"; I could not find that exact wording on a first-party Etsy page. | help.etsy.com How to Create a Listing (undated); wording from f5design.studio field guide, Reddit | Field = VERIFIED; exact AI wording = SECONDARY |
| **API gap:** `createDraftListing` exposes `who_made` (`i_did`, `someone_else`, `collective`) and `when_made`; I found no AI/"creation method" field in the Open API reference. So the AI choice in "How it's made" likely cannot be set through the API. | developer.etsy.com reference (pulled 2026-11-04) | VERIFIED (absence of field); implication UNVERIFIED |

Etsy's stated position (quoted short phrase): items must be "made, designed, handpicked, or sourced by a seller"; listings that break AI rules "may be removed."

---

## 2. Seller Policy, Creativity Standards, Prohibited Items, IP

**Creativity Standards (last updated Jun 10 2025, VERIFIED, etsy.com/legal/creativity/)**

| Category | Meaning | Fit for Ikigai |
|---|---|---|
| Made by a seller | Physical items made by hand or with the seller's own computerized tools | Not applicable (no physical goods) |
| **Designed by a seller** | Original designs as digital download or made by a production partner; includes seller-prompted AI creations; scans of the seller's own physical artwork count as original content | **Ikigai's category** |
| Handpicked | Vintage 20+ yrs, nature items, curated baskets | N/A |
| Sourced | Craft/party supplies, buyer-personalized POD | N/A |

Not "designed by a seller": a bundle, collection, scan or PDF of someone else's work; AI prompt bundles. Etsy shows "Designed by" on listing pages (Jul 2024 handbook, VERIFIED).

**Seller Policy (last updated Oct 5 2026, VERIFIED, etsy.com/legal/sellers/)**
- Provide an accurate account of how the item was made and by whom; your own photos/video, not stock or artistic renderings (digital downloads get the exception noted above).
- Disclose AI use in listings; disclose production partners.
- Listings must offer an item for sale (digitally delivered items count). Dropshipping/reselling not allowed.
- No facilitating off-platform transactions; no duplicate shops; no manipulating clicks/carts/sales; no coordinating prices.
- Honest pricing and promotions: sales, discounts and price comparisons must be real and accurate.
- Reviews: no shilling or falsely inflating review score.
- Communication: no unsolicited advertising/spam in Messages.
- Enforcement: Etsy uses automated systems + manual review + flags; may remove listings, suspend/terminate the account and related accounts; may reduce visibility of listings/shops. Etsy normally notifies, but not always for repeat violators. Listing fees are non-refundable.
- Note: Seller Policy was reorganised July 9 2026 (older version at `/legal/policy/seller-policy-effective-through-july-8/1489086421092`). The reorganisation is described by a secondary source (bulkmockup.com, SECONDARY); the new text itself is what I read.

**Prohibited Items (last updated Oct 6 2026, VERIFIED, etsy.com/legal/prohibited/)** relevant to wall art: counterfeit/unauthorized goods, hate symbols (swastika only with clear religious/cultural context), nudity/sexual content (must follow the mature-content listing rules, applies to AI-generated depictions too), violent/profane graphics need correct mature-content labelling, content infringing privacy/publicity rights (no real people's likeness).

**IP (last updated Oct 29 2026, VERIFIED, etsy.com/legal/ip/ plus handbook "4 Policy Best Practices", May 28 2025)**
- Etsy removes reported listings, may disable listings/shops, and repeat reports can cost account privileges. Only the rights owner or an authorized agent can report. Do not relist content until resolved.
- Brand/celebrity/franchise names in titles, tags, descriptions can be reported even with "inspired by" or "-like" (handbook, May 28 2025). Applies to "Studio Ghibli", artist names, fictional characters, sports teams, etc.
- AI-specific: sellers may not use AI to create content that infringes privacy, publicity or IP rights (AI stance, Oct 22 2026, VERIFIED). Prompts like "in the style of Studio Ghibli" that produce recognisable characters are a risk even if the words are kept out of the listing text.
- Etsy points sellers to the US Trademark/Copyright databases and EUIPO before listing.

---

## 3. Digital items

| Item | Rule | Source | Confidence |
|---|---|---|---|
| Files | Up to 5 per listing, 20 MB each; types incl. .jpg .png .pdf .zip .txt .doc .mp3 .mov .stl .epub; name editing not possible after upload; max 70 chars alphanumeric/period/underscore/hyphen | help.etsy.com How to Manage Your Digital Listings (undated) | VERIFIED |
| Instant vs made-to-order | Instant needs files uploaded at listing; cannot save/publish an instant digital listing with no file; made-to-order files are uploaded at order completion | same | VERIFIED |
| Variations | Not allowed on digital listings | same | VERIFIED |
| Buyer note | One shop-wide note appears on every digital purchase's Downloads page | same | VERIFIED |
| Access | Buyers download from Purchases on Etsy.com (not in the Etsy app); generally unlimited re-downloads unless order cancelled | help.etsy.com How to Download a Digital Item | VERIFIED |
| Returns | Digital listings cannot be returned or cancelled on Etsy; problems (not as described, no delivery) can be covered by Purchase Protection | same | VERIFIED |
| Etsy "must be made/designed by you" | Digital items must be made and/or designed by the seller | Manage Digital Listings | VERIFIED |
| Star Seller | Digital-only shops still eligible | same | VERIFIED |
| API | `type: download`; add files via `uploadListingFile` (multipart; file binary + name); `createDraftListing` itself requires title, description, price, quantity, who_made, when_made, taxonomy_id; images via `uploadListingImage`; scope `listings_w` | developer.etsy.com reference | VERIFIED |
| **Drive-link PDF delivery** | No Etsy page I fetched says a PDF with an external Google Drive link is allowed or banned. Seller Policy bans facilitating off-platform *transactions* (payment, contact steering, off-Etsy discounts, QR codes to leave Etsy); file delivery is not listed there. Community/blog sources say the "PDF with a link" method is widely used and policy-compliant, but sellers also report a wave of off-platform flags/removals, some apparently mistaken. | etsy.com/legal/policy/off-platform-transactions-policy (Oct 5 2026); stablecommerce.ai, Reddit threads | Etsy text = VERIFIED; compliance claim = SECONDARY / UNVERIFIED |
| QR codes | Explicitly prohibited when used to direct members off Etsy | Off-Platform policy | VERIFIED |
| Digital to print (test) | Sep 2026 "Newly Crafted": Etsy is testing letting buyers turn eligible digital purchases into physical prints, sold/printed/shipped by a third-party POD provider; eligible sellers are included automatically, opt out any time; seller is not responsible for fulfilment. Where to opt out was not stated on the page. Third-party trade site names Printify and Shutterfly as partners and says seller payment is unclear. | help.etsy.com Newly Crafted (Sep 2026 section); valueaddedresource.net | Program = VERIFIED; partners/payment = SECONDARY |
| Buyer protection | Etsy Purchase Protection covers items not as described / not delivered; June 2026: coverage up to $250 for eligible orders, more human review. Misleading images can make the seller liable for the refund. | Newly Crafted; Listing Image Requirements | VERIFIED |

---

## 4. Listing requirements and limits

| Topic | Rule | Source (updated) | Confidence |
|---|---|---|---|
| Title | Max 140 characters. Etsy guidance (Apr 27 2026): state the item once, key traits first (colour/material/size), under 15 words, no "gift for him", no "perfect/beautiful", no "on sale/free shipping", no repeated words. Holiday/occasion words only if essential. | Create a Listing (undated); Seller Handbook "New Guidance for Listing Titles" Apr 27 2026 | VERIFIED |
| Title (API) | Letters, numbers, punctuation, math symbols, whitespace, TM, C, R only; `% : & +` allowed once each | developer.etsy.com | VERIFIED |
| Tags | Up to 13; each up to 20 characters; use multi-word phrases; do not repeat tags; do not repeat exact category/attribute phrases; do not add tags in other languages; plurals not needed | Keywords 101, Aug 26 2025; Create a Listing | VERIFIED |
| Tags (API) | Letters, numbers, whitespace, hyphen, apostrophe, TM/C/R only | developer.etsy.com | VERIFIED |
| Keyword stuffing | Handbook says long keyword lists in titles confuse buyers and Etsy's search now reads title, tags, attributes, description, first photo, reviews holistically. I found no specific "keyword stuffing = suspension" clause; stuffing is discouraged guidance, not a stated penalty. | Keywords 101; titles article | VERIFIED (guidance); penalty = not stated |
| Description | Put natural keywords in first sentences; do not copy the title verbatim or just list keywords. Must be accurate; prohibited-item words or misleading descriptors can limit visibility. | Keywords 101; Seller Policy | VERIFIED |
| Photos / video | Up to 20 photos and 2 videos (5-15 s) per listing; warning if photos under 2000 px wide; API `image_ids` accepts up to 20. | Create a Listing; How to Add Listing Videos; API | VERIFIED |
| Attributes / categories | Choose the most specific subcategory; categories and attributes act like tags; add all relevant attributes | Keywords 101 | VERIFIED |
| Styles (API) | Up to 2 styles, 45 chars each | developer.etsy.com | VERIFIED |
| Fees | $0.20 listing fee per item (non-refundable), auto-renews every 4 months at $0.20 unless turned off; 6.5% transaction fee; payment processing and Offsite Ads fees (15%, or 12% above $10k/yr sales; opt-out only under that threshold) apply. | etsy.com/legal/fees (Oct 5 2026) | VERIFIED |
| Mature content | Must follow the mature-content listing rules; AI nudity/sexual content falls under the same policy | Prohibited Items (Oct 6 2026) | VERIFIED |
| Misleading content | Photos and descriptions must accurately show the item; misleading listings removed; repeat = shop removal | Listing Image Requirements | VERIFIED |
| URL | Listing URL is fixed from the title at first publish | Create a Listing | VERIFIED |
| Quick-list form (test) | Etsy is testing a form that suggests titles/tags/attributes from photos; not relevant to the API pipeline | Newly Crafted Sep 2026 | VERIFIED |

---

## 5. Automation, bots, API

| Rule | Source (updated) | Confidence |
|---|---|---|
| Any automated access (bots, scripts, browser extensions, AI systems, "agentic technologies") counts as use of the Services; the person deploying it is the user and fully responsible. Etsy may permit, condition, block or prohibit automated agents at any time, and may require them to disclose they are automated, identify who they act for, and send verifiable identification (e.g. user-agent). | Terms of Use sec. C, Oct 26 2026 | VERIFIED |
| Do not use bots to access, scan, crawl, scrape or spider any Etsy page (including Seller Content) without express permission. Do not use Etsy content/data to develop, train, fine-tune, evaluate or prompt any ML/AI system without permission. Use the API instead. | Terms of Use sec. E, Oct 26 2026 | VERIFIED |
| Do not manipulate Etsy's systems, including prompt injection or jailbreaking Etsy's AI tools. | Terms of Use sec. F | VERIFIED |
| API use must be registered; indicate personal (own shop/testing) vs commercial use; account is for your own use only. | API Terms, Aug 18 2026 | VERIFIED |
| Application Purpose and any updates need Etsy's prior approval; the app must be consistent with the approved purpose. | API Terms | VERIFIED |
| Rate limits: per API key, QPS then QPD (sliding 24 h window); your exact numbers are in the Developer Portal (Tony's app "agent-OS" is recorded in this folder's CLAUDE.md as 10 QPS / 10,000 QPD; docs show 150 / 100,000 only as an example). Exceed = HTTP 429 with `retry-after`; use exponential backoff and caching. Creating extra keys to get around limits is prohibited; higher limits by emailing developer@etsy.com. | developer.etsy.com Rate Limits; API Terms | VERIFIED |
| Prohibited API behaviours (selection): supporting listings incompatible with Creativity Standards (including mass-produced items); facilitating copying/infringement; diverting sales off Etsy; excessive burden; collecting more data than needed; transferring/commercialising API access or data; sending order/shipping/tracking messages without written authorization; manipulating shop statistics or reviews; using automated systems/extensions to access, analyze or scrape Etsy data without written authorization; **using the API to collect Etsy content for analytics, ML, AI training, licensing or content removal without written authorization.** | API Terms items 5, 6, 10, 17, 18, 21, 24, 25 | VERIFIED |
| Display/caching: listing content shown to others must not be older than 6 h, other content 24 h; do not store longer than reasonably necessary. | API Terms | VERIFIED |
| Draft creation: `createDraftListing` ("Creates a physical draft listing product"; `type` can be download) is a General Release endpoint with scope `listings_w`; publishing a draft is done by setting state to active, which requires an image. Drafts are therefore the safe boundary; the pipeline must never set `state: active`. | developer.etsy.com reference | VERIFIED |
| Explicitly allowed for own shop: personal-use apps building tools for your own Etsy shop, once the Application Purpose is approved; AI/agent use is allowed only inside the Terms above (disclosed, accountable, no scraping). No page says "AI agents may create listings"; the AI stance page only requires individualized human oversight of each item. | API Terms; AI stance | VERIFIED (silence is not permission) |
| Etsy's own bulk tools exist (bulk edit, AI title suggestions tool) and Etsy says suggestions are optional and the seller controls what is published. | Titles article, Apr 27 2026 | VERIFIED |

---

## 6. EU / UK

| Topic | Rule | Source | Confidence |
|---|---|---|---|
| Right of withdrawal | Professional sellers (traders) shipping/selling to EU buyers must honour a 14-day withdrawal right (UK in parallel). Digital downloads are exempt only when the buyer consented to immediate delivery and explicitly waived the right before the download began, and the seller must clearly tell buyers (listing/shop policies) when the right does not apply. Failure to inform can extend the period to one year. | Seller Policy (Oct 5 2026); Etsy Seller Handbook "What Etsy Sellers Should Know About the EU's New Online Selling Regulations" (page shows a stale "1 May 2014" date; content references 2026 rules); help.etsy.com EU returns article (undated) | VERIFIED |
| Withdrawal function | Since early July 2026 buyers can submit a withdrawal request through Help With Order; seller gets a message and must review and refund within 14 days if valid. | help.etsy.com How Do I Follow EU Law Regarding Returns and Refunds | VERIFIED |
| Etsy checkout wording for the digital waiver | I did not find where or how Etsy's checkout captures the waiver for digital items, nor whether the seller must add wording. The Etsy article says the buyer must consent and waive; treat the listing/shop-policy sentence as the seller's job until confirmed. | n/a | UNVERIFIED |
| Trader status | Professional/business sellers are shown to EU buyers as traders with registration number and address; declaring as private while acting as a business is misleading and breaches Etsy policy. Etsy cannot advise which you are. | EU returns help; GPSR help | VERIFIED |
| GPSR scope | Etsy help says GPSR applies to physical and digital products "unless covered by other safety regulations," to traders selling into the EEA + Northern Ireland, regardless of seller location. Third-party legal commentators say purely digital goods are practically outside it (SECONDARY, euverify.com). | help.etsy.com GPSR article (undated) | Etsy statement VERIFIED; commentary SECONDARY |
| Economic operator | A manufacturer and EU responsible-person record that traders attach to products in required categories. API: four economic-operator endpoints + `gpsr_manufacturer_type/id`, `gpsr_responsible_person_type/id`, `gpsr_serial_number`, `gpsr_safety_warnings`. All optional now; any value you send is validated immediately. **Enforcement date: Feb 1 2027.** The required-category list I fetched covers lighting, home appliances, home improvement, cameras, computers, TV/projection and similar; **no wall-art/print/digital art category was on it.** The list "can change." Sellers can opt out of selling digital items, physical items or both into the EEA. | developers.etsy.com GPSR Economic Operators Tutorial (undated); pulled 2026-11-04 | VERIFIED |
| ECGT / commercial guarantee fields | `ecgt_*` fields are silently ignored for digital listings (guarantee fields) and for non-eligible-EU traders; `ecgt_software_update_details` applies to digital content for eligible EU traders and is ignored for physical listings. | API reference | VERIFIED |
| Other 2026 EU items | EUR 2 customs handling fee per item from Nov 1 2026 and the EU packaging/EPR update apply to imported physical goods (not digital); a US-bound DDP requirement applies to physical orders (not digital). | Create a Listing help; Etsy Handbook (headline only seen) | VERIFIED (fee); EPR page not read |
| Digital VAT | Not researched in this pass (Etsy collects/remits VAT on many digital sales; confirm in Fees/tax pages before relying on it). | n/a | UNVERIFIED |

---

## 7. Other suspension risks in this niche

| Risk | What Etsy says | Source | Confidence |
|---|---|---|---|
| Mass/bot-made listings | Removal and possible shop removal | AI updates, Oct 22 2026 | VERIFIED |
| IP/brand names, fan art, styles of living artists | Reported by rights holders; repeat reports cost account privileges; "inspired by" does not shield | IP policy; handbook May 28 2025 | VERIFIED |
| Duplicate shops | Prohibited | Seller Policy | VERIFIED |
| Duplicate/similar listings in the same shop | No explicit Etsy ban found in the policies I read. Community says multiple listings of the same item look "sketchy" and the Etsy handbook's concern is mass-produced/resold items and manipulating search; treat near-identical listings (same art, different title) as a risk. | Seller Policy (no clause); SECONDARY blogs/forums | UNVERIFIED |
| Review manipulation | No shilling, no falsely inflating review score, no buying to leave negative reviews, no pressuring | Seller Policy | VERIFIED |
| Off-Etsy communication/steering | No off-platform payment, contact sharing to complete a transaction, off-platform discounts, QR codes; no extra charges after checkout | Off-Platform policy Oct 5 2026 | VERIFIED |
| False discounts/sale claims | Must be real; do not mislead on value or timing | Seller Policy | VERIFIED |
| Misleading images (AI) | Removal, refunds from seller, shop removal if repeated | Listing Image Requirements | VERIFIED |
| Mature/violent content labelling | Must follow mature-content rules | Prohibited Items | VERIFIED |
| Spam messages | No unsolicited advertising in Messages | Seller Policy | VERIFIED |
| Sudden order spikes | Can raise or lower search ranking; unusual order activity can trigger limits on visibility/payments | Seller Policy | VERIFIED |
| About section | Etsy recommends a complete About section (shop members, production partners) as it helps Trust & Safety reviews | handbook May 28 2025 | VERIFIED |
| Appeals | Listing appeals expanding; all sellers get appeals for most policy areas by end of 2026; check appeal options before making a replacement listing | Newly Crafted Sep 2026 | VERIFIED |

---

## 8. Conflicts and risks for Tony's shop (ranked by severity)

Reviewed: `Description_Template_AI.md`, `Description_Template_Originals.md`, `Digital_Note_To_Buyers.md`, `Mockup_Originals_Locations.md` in this folder, plus the pipeline plan (drafts only).

| # | Severity | Conflict / risk | Why | Recommended action |
|---|---|---|---|---|
| 1 | **HIGH** | Pipeline vs "bot-generated listings" ban | Etsy (Oct 22 2026) bans mass-automated generation without individualized human oversight. A pipeline that fabricates designs, titles and descriptions in bulk could be read as bot-generated. | Keep every draft gated on Tony's per-listing approval of the design, title, tags and description; store a log of Tony's prompt/choice per design; never batch-publish; make it clear in the portal that the human decision is the creative step. |
| 2 | **HIGH** | Automation and scraping inside Tony's own research stack | Terms of Use sec. E and API Terms item 24 bar bots/browser automation from crawling or scraping Etsy pages without permission; item 25 bars using the API to collect Etsy content for analytics/AI without written authorization. Tony's tooling (Firecrawl, Playwright, listing/competitor scrapes, one-dashboard analytics) can cross that line. Note: this Bible's own refresh pulled etsy.com legal/help pages with Firecrawl, which technically falls under that rule; future re-pulls should be few, manual/browsed or via the Etsy-approved route. | Do not scrape Etsy listings/shops/search with bots. Use the official API for own-shop data only, keep the Application Purpose accurate (own-shop reporting and drafts), and email developer@etsy.com to confirm own-shop analytics is covered. Use Alura's official API for market data rather than scraping. |
| 3 | **HIGH** | AI disclosure line placement and accuracy | Disclosure is mandatory in the description for AI items. Both templates carry the same "AI Disclosure" block. The Originals template tells buyers the designs were AI-created, which is inaccurate for hand-made/mixed-media originals and could itself count as misrepresentation; the AI template wording ("AI tools that I own and have full commercial rights to use") is a licence claim, not a creation statement, and says "elements...and/or" without stating whether the art itself is AI. | AI template: replace with plain wording that states the art was created using AI tools from the seller's original prompts and curated by the seller (add that mockups are AI-assisted if true). Originals template: remove the AI line, or limit it to "mockup scenes may be AI-assisted" only if true. Check commercial-licence claim per tool terms. |
| 4 | **HIGH** | "Created by me" vs "With an AI generator" in How it's made | Etsy's visible item detail ("Designed by") and AI field are part of buyer trust; picking "Created by me" for AI work contradicts the disclosure rule ("cannot misrepresent AI-generated work as ... entirely their own creation"). The API has no field for this, so drafts cannot carry it. | For every AI-assisted design set the AI option by hand during Tony's draft review; add a pipeline checklist item "AI option set" before Tony publishes. Use "Created by me" only for designs with no AI generation. For mixed designs (AI base + hand finishing), disclose AI and describe the human work. |
| 5 | MEDIUM | Drive-link PDF delivery | No Etsy page endorses it; off-platform policy bans steering for transactions and QR codes; sellers report mistaken off-platform takedowns; also Drive link rot/permission changes break purchases (buyers are then covered by Purchase Protection and the seller bears the refund). The shipped description and buyer note say files come via a Drive zip. | Keep the PDF on Etsy as the real, attached deliverable; remove any QR codes; keep links purely for file retrieval (no storefront, no discount, no contact request, no other site promotion); prefer splitting files into 5 listing files under 20 MB where quality allows (the five 300dpi JPGs may fit as 5 files if each under 20 MB); keep Drive links on a business account with "anyone with link" and test monthly. If any flag arrives, ask Etsy Support in writing whether file-retrieval links are allowed and save the reply. |
| 6 | MEDIUM | Mockup images vs Listing Image Requirements | Digital downloads are exempt from the unedited-photo rule, but images must show a visual preview of what is delivered and must not mislead. The standard set includes "Poster Mockup", "Customer Reviews" (06A) and a "Download Contents" tile: AI/PSD mockups must represent real art, sizes and the real file list; anything implying a printed/framed item is shipped breaks the rule. | Ensure image 1 or an early image is a clear preview of the actual art file; "Download Contents" must match the real file list (5 files vs 6 images on the 1:1 variant); keep the "digital download, no physical item" language in images; note AI-edited mockups in the description; if people appear in mockups and are AI-made, plan for the SB 1050 disclosure (Jan 1 2027). |
| 7 | MEDIUM | "Customer Reviews" image (06A) | Review content must be real and not manipulated; fabricated or edited reviews are shilling/false advertising. | Verify every review image is a genuine Etsy review; do not fabricate; update when a review is deleted or changed. |
| 8 | MEDIUM | EU digital withdrawal wording | Digital downloads are not refundable under EU rules only if the buyer consents and waives before download, and the listing must say the right does not apply. Templates have no such sentence. | Add a short line to Digital_Note_To_Buyers and listing/shop policy: instant digital download, delivered immediately after purchase, no right of withdrawal once download starts; confirm in Etsy's checkout whether Etsy captures the waiver. Check trader status in Shop Manager. |
| 9 | MEDIUM | Title/tag rules in the pipeline | The title tool must follow 140 chars, no `*`/emoji (API rejects), no "sale/free"/gift fluff, tags 13 x max 20 chars, no brand names. Etsy's April 2026 guidance penalises keyword packing in practice (not formally). | Add validators to the portal: title regex, <=140, <15 words; tags <=13, each <=20 chars and allowed characters; blocklist of brands/artists/franchises (e.g. Ghibli, Disney, Pixar, Marvel, Pokemon, Nike, named living artists); no duplicates between tags and category/attributes. |
| 10 | MEDIUM | "Studio Ghibli" and style-of prompts | Using style names in prompts can yield derivative characters; Etsy and rights holders target franchises. | Never use franchise or living-artist names in prompts, titles, tags or descriptions; reject any design showing a recognisable character or logo. |
| 10b | **HIGH** | Public-domain / "reimagined vintage" art (shop About and CLAUDE.md say the shop sells curated, reimagined vintage and public-domain art) | Creativity Standards list "a bundle, collection, scan, or PDF of someone else's work" as NOT designed by a seller; digital items must be made/designed by the seller. Public-domain scans with light edits can be removed under Creativity Standards. | Only list public-domain-based pieces with substantial original transformation by Tony; say plainly in the description what was changed; avoid listing raw or lightly filtered scans; review existing "Reimagined" and "Japan Art" listings against this. |
| 11 | LOW | Description uses Unicode "bold" glyph headings | Not a documented policy issue. Search/accessibility effect unverified. | Optional: test plain-text headings; do not rely on glyphs for important disclosures (AI line should be plain text). |
| 12 | LOW | Digital-to-print test auto-enrols Tony | Etsy may let buyers print his designs through a third-party POD; Tony is opted in automatically unless he opts out; seller payment unclear. | Decide deliberately; opt out in Shop Manager if undesired (location not confirmed in the source). |
| 13 | LOW | "Ikigai = printable art only, no new categories" | Fine with Creativity Standards ("Designed by"). GPSR categories do not include art prints. | No action; re-check the GPSR list before Feb 1 2027. |
| 14 | LOW | Duplicate/similar listings | No explicit ban found, but near-identical listings are a flag risk. | Make each design distinct in art, title and tags; avoid cloning listings with only a new title. |

---

## 9. Source list

All fetched 2026-11-04 with `firecrawl scrape` unless noted.

| # | URL | Last updated shown | Used for |
|---|---|---|---|
| 1 | https://www.etsy.com/seller-handbook/article/1275449912004 (What's Etsy's Stance on AI Creations?) | Oct 22 2026 | AI rules |
| 2 | https://www.etsy.com/seller-handbook/article/1522733284810 (Important updates to AI use on Etsy) | Oct 22 2026 | AI updates, photos, bot ban, SB 1050 |
| 3 | https://www.etsy.com/legal/policy/listing-image-requirements/253962679005 | Oct 22 2026 | Image rules |
| 4 | https://www.etsy.com/legal/creativity/ | Jun 10 2025 | Creativity Standards |
| 5 | https://www.etsy.com/seller-handbook/article/1276491338090 | Jul 9 2024 | Creativity vision |
| 6 | https://www.etsy.com/legal/sellers/ | Oct 5 2026 | Seller Policy |
| 7 | https://www.etsy.com/legal/prohibited/ | Oct 6 2026 | Prohibited Items |
| 8 | https://www.etsy.com/legal/ip/ | Oct 29 2026 | IP policy |
| 9 | https://www.etsy.com/seller-handbook/article/1075628311049 (4 Policy Best Practices) | May 28 2025 | Brand names, IP, creativity |
| 10 | https://www.etsy.com/legal/terms-of-use/ | Oct 26 2026 | Automation, scraping |
| 11 | https://www.etsy.com/legal/api/ | Aug 18 2026 | API Terms |
| 12 | https://www.etsy.com/legal/fees/ | Oct 5 2026 | Fees, off-platform pointer |
| 13 | https://www.etsy.com/legal/policy/off-platform-transactions-policy/1254654515806 | Oct 5 2026 | Off-platform rules, QR |
| 14 | https://help.etsy.com/hc/en-us/articles/115015628347 (Manage Digital Listings) | not shown | Digital file limits |
| 15 | https://help.etsy.com/hc/en-us/articles/115013328108 (Download a Digital Item) | not shown | Downloads, refunds |
| 16 | https://help.etsy.com/hc/en-us/articles/115015628707 (Create a Listing) | not shown | Title/tags/photos |
| 17 | https://help.etsy.com/hc/en-us/articles/360053206073 (Listing Videos) | not shown | Video limits |
| 18 | https://www.etsy.com/seller-handbook/article/1399426136697 (Listing titles) | Apr 27 2026 | Title guidance |
| 19 | https://www.etsy.com/seller-handbook/article/keywords-101-everything-you-need-to-know/382774281517 | Aug 26 2025 | Tags, keywords |
| 20 | https://help.etsy.com/hc/en-us/articles/10603291042967 (Newly Crafted) | Sep 2026 section | Digital to print, appeals, quick-list |
| 21 | https://developer.etsy.com/documentation/reference/ | not shown | createDraftListing, uploadListingFile |
| 22 | https://developer.etsy.com/documentation/essentials/rate-limits | not shown | Rate limits |
| 23 | https://developers.etsy.com/documentation/tutorials/gpsr-economic-operators | not shown | GPSR, economic operators, Feb 1 2027 |
| 24 | https://help.etsy.com/hc/en-us/articles/28211364687383 (GPSR) | not shown | GPSR scope |
| 25 | https://help.etsy.com/hc/en-us/articles/5703129136407 (EU returns) | not shown | Withdrawal, trader |
| 26 | https://www.etsy.com/in-en/seller-handbook/article/22504428267 | shows "1 May 2014" (stale metadata) | Digital withdrawal waiver |
| 27 | SECONDARY: https://www.valueaddedresource.net/etsy-seller-update-september-2026/ | Sep 2026 | Digital-to-print context |
| 28 | SECONDARY: https://stablecommerce.ai/blog/deliver-large-files-etsy ; Reddit r/EtsySellers/comments/1x9lc1s ; r/Etsy/comments/1xcn638 (snippets via search; Reddit itself blocked by Firecrawl) | n/a | Drive-link practice, off-platform flags |
| 29 | SECONDARY: https://euverify.com/resource/gpsr-compliance-for-etsy-listings/ | n/a | GPSR digital view |
| 30 | SECONDARY: https://www.bulkmockup.com/etsy-policy-changes/ | 2026 | Jul 9 2026 Seller Policy reorganisation |

**Could not fetch / not found:** Reddit pages (Firecrawl unsupported), first-party text for the exact "How it's made" AI wording, the Etsy checkout wording for the EU digital waiver, any Etsy page on delivering files via external links, any Etsy page defining duplicate-listing limits, and the EU packaging/EPR handbook article (headline only). `etsy.com/help/article/3949` and the Etsy Messages policy URL (360000343608) returned "page not found" or were not tested.
