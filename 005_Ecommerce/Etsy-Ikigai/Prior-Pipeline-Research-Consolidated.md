---
title: "Prior Pipeline Research — Consolidated"
type: reference
domain: ecommerce
tags: [reference, ikigai, pipeline, research, consolidated]
status: consolidated from scattered workspace sources, 2026-10-13
---

# Ikigai Pipeline — Prior Research, Consolidated

**Why this file exists:** Tony remembered talking to an LLM about building a new full pipeline for Ikigai (research → design → automate everything) and asked for it to be found and folded into one source. A full search (workspace files, ChatGPT history ingest, Claude's cross-session memory, and a direct binary-safe scan of Antigravity's local chat storage) found **no single "new full system" conversation** — but it did find several real, separately-scattered pieces of prior work that answer most of what that conversation would have covered. This file is the one place they're all pointed to from now on.

**Antigravity search result (so this never gets re-searched):** checked `~/.gemini/antigravity/conversations/*.pb` (37 files — encrypted/binary, not text-searchable) and `~/.gemini/antigravity/brain/<session>/` (readable `task.md`/`walkthrough.md`/`implementation_plan.md` files per session). Grepped all of it, binary-safe, for "ikigai," "etsy," "wall art," "POD," "digital download" — zero matches. The conversation Tony remembers is not in Antigravity's local storage on this Mac. It may have happened in the Gemini web app/chat (not the Antigravity IDE), on another device, or it may be the October 2025 session below, misremembered as more recent.

---

## 1. Niche/keyword research methodology (October 2025)

**Source:** `007_Resource_Library/Research/Ikigai-Rube-Research-Instructions.md` — "Etsy Head Term Research for Printable Wall Art," written for **Rube (Composio)**, an MCP connector tool. **Rube/Composio was discontinued May 16, 2026** (`007_Resource_Library/Tools/Rube.md`), so the tool itself is dead — but the methodology is real and reusable with any research tool/agent.

**What it specifies:**
- Objective: find niche "head terms" (the first tokens buyers type) for Etsy printable wall art — not generic words, intersectional style × motif or style × colorway phrases.
- Scope: styles (Minimalist, Mid-Century, Japandi, Nordic/Scandi, Botanical, Bathroom Humor, Food & Drinks, Vintage Travel, Frame TV) crossed with room/placement categories (Bathroom, Kitchen, Laundry, Bar Cart, Nursery, Living Room, Office, Bedroom, Entry, Frame TV).
- Search method: query Etsy as "Token + buyer-intent suffix" (e.g. "digital download," "wall art," "instant download"), sorted best-selling.
- Output format: `[Token] [Category] [Score 0-100]`, scored by demand (multiple active listings, room/color specificity) minus competition (near-identical titles, oversaturation).

**Supporting artifacts found on Tony's Desktop (same October 2025 pass, not yet moved into the workspace):**
- `~/Desktop/Ikigai Research/Competition/` — 6 competitor shop screenshots (TheCozywallsX, MysticWhale, SharpArtDigitals, EmilyBlueBean, FunkyFridayPrintsCo, SlippyCowboy).
- `~/Desktop/Ikigai Research/Image Token Workflow/` — example token outputs (bunny/spring designs) and 3 workflow screenshots.

**This is the real answer to pipeline step 1 (research, keyword-gap analysis)** from Tony's 2026-10-13 brain dump — just built a year ago, for a now-dead tool, and never folded into the workspace proper until now.

---

## 2. Design-style taxonomy / token system (October 2025)

**Source:** `007_Resource_Library/Design_Inspiration/Ikigai-Art-Styles-Tokens.md` — "Ikigai Wall Art Token Creator," built for a CustomGPT (`Instructions_For_CustomGPT_Tokenizer.txt`, referenced but not located in this workspace — may only exist inside the CustomGPT's own config on OpenAI's side).

**What it is:** a 120-entry table of art styles (Bauhaus Composition, Japanese Sumi-e ×17 variants, Mid-Century Modern ×5 variants, Minimalist Abstract ×6 variants, Typography ×20+ variants, etc.), each with a Token ID (TS-293 through TS-419). This is the controlled vocabulary used to keep generated art style-consistent — this is what the existing n8n `Ikigai_Wall_Art_Token_Creator` workflow (see `001_Architecture/Plans/Revenue-Stream-Pipeline-Outlines.md` section 1) actually consumes.

**This answers pipeline steps 2-3 (ideation, style-consistent design generation)** — the taxonomy already exists; it was never the gap.

---

## 3. Production automation (existing, various dates — already catalogued)

Already fully listed in `001_Architecture/Plans/Revenue-Stream-Pipeline-Outlines.md` section 1 — not re-duplicated here. Covers: n8n art generation/tokenizing/mockup workflows, and local Python/Photoshop scripts for cropping, thumbnails, mockups, and zoom-detail shots. **Per Tony's 2026-10-13 correction, these are reference architecture only — he wants a new, purpose-built pipeline, not a reuse of these as-is.** Some of the Python scripts may be reusable pieces; which ones is still pending Tony's own walkthrough (he said the full picture is too much detail to give in one session).

---

## 4. What's still genuinely missing

Nothing found anywhere (this search or the prior one) covers:
- Etsy listing creation/publishing automation itself.
- Pinterest posting automation.
- Pinterest/Facebook ad creation automation.
- Alura.io integration (Tony's referral link is on file, `005_Affiliate_Marketing/Affiliate-Program-Removal-Checklist.md` line 57, but no usage/API notes exist).

These remain the real gaps in the Ikigai pipeline, same as the 2026-10-13 pipeline-outline draft already flagged.

---

## 5. Relevant skills found (via `find-skills`, 2026-10-13)

Ran the Skills CLI (`npx skills find`) against: Etsy, print-on-demand, Pinterest, image/mockup generation, SEO/keyword research, Facebook ads. **Honest caveat, per `find-skills`' own quality bar (1K+ installs = trusted, <100 = be cautious):** almost nothing Etsy/Pinterest-specific clears that bar. These are real, found-today results — not a recommendation to install any of them untested.

| Skill | Installs | What it's for |
|---|---|---|
| `resciencelab/opc-skills@seo-geo` | 52,100 | General SEO/GEO strategy — the one skill here with a real trust signal |
| `nowork-studio/notfair-plugin@meta-ads-audit` | 236 | Facebook/Meta ad account auditing |
| `crawlora-org/crawlora-skills@resale-secondhand-research` | 32 | Resale/secondhand market research (adjacent to Etsy, not Etsy-specific) |
| `crawlora-org/crawlora-skills@pinterest-research` | 28 | Pinterest research |
| `marketingskills/seo@keyword-planner` | 17 | Keyword planning |
| `scavio-ai/skills@etsy-product-data` | 7 | Etsy product data pulls |
| `scavio-ai/skills@pinterest-api` | 6 | Pinterest API wrapper |
| `scavio-ai/skills@meta-ad-library-api` | 8 | Meta Ad Library API |
| `vanities/social-skills@pinterest-post` / `@pinterest-warm` | 1 each | Pinterest posting / account warm-up |
| `easyaitech/etsy-skills@trend-radar` | 1 | Etsy trend tracking |
| `inference-sh/skills@ai-image-generation` | 14 | General AI image generation |

**Already available in this workspace (no install needed) — more relevant than most of the above:**
- **Tool-Manager** — this workspace's own rule: query it before any pipeline/API choice, every time. Should run before locking in any tool from this list.
- **firecrawl** (+ its 8 sibling skills) — web scraping/search, directly useful for the Etsy niche-research step and competitor scans.
- **ai-seo**, **programmatic-seo**, **schema-markup**, **seo-audit** — SEO tooling already in the plugin set, no new install.
- **GPT-Image-2-Prompting-Guide**, **web-asset-generator** — image-generation prompting references already in the workspace.
- **media-use** — general image/video editing by conversation; could cover mockup touch-ups.

**Verdict:** nothing found today is a drop-in replacement for the custom pipeline Tony wants to build. The workspace's own skills (Tool-Manager, firecrawl, ai-seo) are more trustworthy starting points than the marketplace results, which are mostly unproven single-digit-install packages.

## 6. Relevant APIs/agent-tool platforms found

| Tool | What it is | Relevance to Ikigai |
|---|---|---|
| **Treg** (`github.com/superdesigndev/treg`, treg.to) | **This is the tool Tony was trying to remember — "OpenRouter for agent tools."** An open-source proxy/registry: one base URL + one token gives an agent access to 3,600+ priced-per-call endpoints across 86-94 providers (SEO/backlinks, social/trends, scraping, ads, image/video gen), billed per call from a cent, no per-provider signup. Self-hostable or hosted. Full doc: `007_Resource_Library/Tools/Treg-OpenRouter-For-Agent-Tools.md`. | Could cover the research step (SEO/trend data), the Pinterest-promotion step, and ad-platform calls — all through one connection instead of separate signups. Not yet connected to this workspace. |
| **Composio Universal CLI** (`composio.dev`) | Agent-facing CLI (not MCP) to 1000+ SaaS apps, including **Canva** — create designs, list brand templates, manage folders, all via one authenticated CLI. Doc: `007_Resource_Library/Tools/Canva-CLI-for-AI-Agents.md`. Note: Rube (Composio's own MCP server) was discontinued May 2026, but the newer Universal CLI is a separate, still-live product from the same company. | Directly useful for the design/mockup step if Canva becomes part of the new Ikigai pipeline. |
| **Printing Press Library** (`printingpress.dev`, `github.com/mvanhorn/printing-press-library`) | A catalog of 58 pre-built, agent-native CLIs (Go binaries + matching Claude skills), one command to install. Doc: `007_Resource_Library/Tools/Printing-Press-Library.md`. | Several directly relevant: `tiktok-shop` (safe v1 Seller API — same shape as what Unomas-Creative needs), `shopify`, `amazon-seller`, `google-ads`, `scrape-creators` (covers Pinterest, Instagram, TikTok scraping — useful for competitor/niche research). No Etsy-specific or Pinterest-ads CLI in the catalog yet. |
| **Pipedream "string alpha"** | A vaguely-saved bookmark (TikTok video, not a doc) about an AI agent tool on Pipedream.com. Doc: `007_Resource_Library/Tools/Pipedream-Com-String.md`. | Too thin to evaluate — flagged as unverified, would need its own research pass before relying on it. |
| **Alura.io** | Etsy SEO/listing-optimization tool. Referral link on file (`005_Affiliate_Marketing/Affiliate-Program-Removal-Checklist.md` line 57), application status/waitlist not confirmed. | The listing-SEO gap in the pipeline (section 4 above). |
| **Listadum** | Third-party Etsy listing-automation tool, already locked as part of the Etsy automation route per the monetization plan. | Listing-creation step. |
| **Etsy Open API v3** | Etsy's own official API. Already the locked automation route for Etsy listing creation workspace-wide. | Listing-creation step. |

## 7. Etsy listing photo/mockup pattern (observed directly, 2026-10-13)

Tony described a fixed photo order across his listings and asked for it to be confirmed by looking at the actual shop. Checked two live listings directly (different art styles, to test whether the pattern holds across the catalog):

- **Japandi Leaf Print** (`listing/1768664937`)
- **Cyber Tokyo Art Print** (`listing/1766496265`)

**Confirmed pattern, both listings:**

| Position | Content | Fixed or varies? |
|---|---|---|
| 1 | Hero shot — a styled room photo (sometimes labeled by frame type, e.g. "in Glass Picture Frame") | Varies in framing/label, but always a hero room shot |
| **2** | **Product video mockup** | **Always fixed** — same video-mockup template, every listing |
| **3** | **"Poster" flat mockup** | **Always fixed** — same plain poster mockup template, every listing |
| 4 | Style-matched room staging (e.g. "Gaming Room" for the Cyber Tokyo piece, "on Canvas in Frame" for Japandi) | **Varies by art style** — this is Tony's "if it fits a mid-century modern living room, stage it there" step |
| 5+ | Unlabeled in the accessibility tree (likely zoom/detail shots, a "what you get" bundle graphic, and size-info graphics per the shop's 5-size-bundle workflow) | Varies, not individually checked |

**This confirms Tony's description exactly:** positions 2 and 3 are the same two fixed mockup templates on every single listing (video + flat poster), position 4 onward is where style-specific staging and zoom-detail mockups come in. The existing automation (`Ikigai_mockup_launcher.py` + `Ikigai_Batch_StaticOnly.jsx` for static mockups, a separate video-renderer step, `Ikigai_detail_zoom_launcher.py` for zoom shots — see section 3) maps directly onto this: static mockups cover positions 1/3/4, the video renderer covers position 2, the zoom launcher covers the detail shots further down the list.

**Not yet confirmed:** the exact total image count per listing (both checked listings had similar structure, full count not enumerated past position 4) and whether the 5-size-bundle info graphic is a listing-wide fixed asset or regenerated per design.

---

## 8. PhotoCraft — potential Photoshop replacement (researched 2026-10-13)

Tony wants to replace Adobe Photoshop with **PhotoCraft** for this pipeline specifically to get off Adobe Creative Cloud. Researched directly (not from memory):

**What it is:** an open-source, cross-platform image editor written in Rust, built by the ArtCraft project (led by Brandon Thomas, former CEO of storyteller.ai). Billed as a "clean-room reimplementation of Adobe Photoshop" — notably, it was built by pointing an AI agent at Photoshop, having it exercise every tool/panel, and rebuilding the observed behavior from scratch, specifically to avoid copyright/reverse-engineering issues. MIT/Apache-2.0 licensed. Available for Windows, macOS, Linux, FreeBSD, and web. Repo: `github.com/storytold/photocraft`.

**Feature parity (relevant to Ikigai mockups):** layers, masks, layer styles, smart objects, a brush engine, adjustment layers, type, vectors, and brushes. **Opens real PSD files** — meaning Tony's existing purchased Photoshop mockup templates (`.psd` files) should open directly in PhotoCraft without conversion.

**Automation — this is the critical finding for this pipeline:**
- PhotoCraft automates through **UI, a headless CLI, a JSON control channel, or a native MCP server** — roughly 500-700 commands shared across one registry. Example: `photocraft-cli run in.psd --cmd filter.blur.gaussianBlur --params '{"radius":4}' --out out.png`.
- **Batch processing is built in:** `photocraft-cli batch --actions grade.json --in ./raw --out ./graded` — applies one action list to a whole folder of images in one command.
- It embeds a **native MCP server**, so a coding agent (like this one) could directly inspect layers, manipulate selections, and run batch mockup generation without any custom scripting glue.
- **Critical gap: PhotoCraft does NOT support ExtendScript (`.jsx`) or `.atn` actions, and has no third-party plugin support** (it uses a sandboxed WebAssembly plugin runtime instead, for security). **This means Tony's existing `Ikigai_Batch_StaticOnly.jsx` and `Ikigai_Zoom_Mockup.jsx` scripts cannot be ported directly** — they'd need to be rebuilt as PhotoCraft CLI/batch commands or MCP calls, not reused as-is.

**Net assessment:** PhotoCraft is a real, viable Photoshop replacement for this pipeline, and arguably a *better* fit for agent-driven automation than Photoshop (CLI + batch + native MCP vs. Photoshop's ExtendScript-only automation). The tradeoff is that the existing JSX-based mockup scripts are a rewrite, not a port — relevant when Tony does the full pipeline walkthrough (section 1).

---

## Cross-references

- `001_Architecture/Plans/Revenue-Stream-Pipeline-Outlines.md` — the pipeline tree outline this research feeds into (section 1, currently marked superseded pending Tony's own walkthrough).
- `001_Architecture/Plans/Agent-OS-Monetization-Strategy-Plan.md` section 7c — Ikigai's revenue score and the market research behind it.
- `007_Resource_Library/Workflows/Ikigai-Digital.md` — plain-English docs for the existing production scripts.
