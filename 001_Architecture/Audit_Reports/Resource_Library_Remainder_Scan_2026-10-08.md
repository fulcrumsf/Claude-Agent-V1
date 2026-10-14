---
title: "Resource Library Remainder Scan — 007_Resource_Library (all categories except Tools/)"
type: audit-report
category: architecture
tags:
  - resource-library
  - tool-scan
  - api-watchlist
created: 2026-10-08
source: 007_Resource_Library/
---

# Resource Library Remainder Scan — 007_Resource_Library (2026-10-08)

Read-only scan of the **1,526 top-level `.md` files** in the 18 Resource Library categories that were *not* covered by `Resource_Library_Tools_Scan_2026-10-08.md` (which handled `Tools/`) or by the `Archive/` exclusion. Each file's YAML frontmatter (`summary` / `ai_description` / `title` / `url`) was read first via a full-tree extraction pass covering every top-level file; the **86 files whose frontmatter description was missing or under ~25 characters** had their bodies read in full, plus ~50 additional candidate bodies were read to confirm or reject borderline tool hits. Nothing in `007_Resource_Library/` was deleted, moved, or renamed — cataloging only.

Purpose: extend the flat triage list of real, adoptable tools/apps/APIs/SaaS/skills/plugins/downloadable-resource sites so the API watch list covers the whole Resource Library, not just `Tools/`.

**Coverage statement:** all **1,526 of 1,526** top-level `.md` files (the exact set named in the task) were read and classified. Per-folder top-level counts: `Affiliate_Marketing` 13, `Clipping` 6, `Content_Ideas` 366, `Design_Inspiration` 207, `Digital_Products` 93, `Docs` 14, `Investments` 75, `Mockups` 47, `Models` 50, `OpenAI_History` 1, `POD_Prints` 112, `Personal` 30, `Prompts` 102, `Research` 35, `Travel` 25, `Tutorials` 253, `UGC` 24, `Undetermined` 19, `Workflows` 54. **No folder or range was left unread, and no coverage is guessed** — the counts above total exactly 1,526.

**Scope note / count reconciliation:** header counts include **recursive (nested)** `.md` files; this scan follows the task's file counts, which are **top-level only**. The task's numbers matched top-level counts for 15 of 18 folders. Three differ only because of nesting, which was excluded to stay consistent with the task's 1,526 total:
- `Tutorials` — task said 253, recursive is 287 (34 nested files, e.g. sub-project folders `How-To-Use-Jev-Instantly-In-Claude-Code-With-OpenRouter/`, `Jev-Will-10x-Your-Claude-Code/`). Top-level 253 scanned.
- `Docs` — task said 14, recursive is 17 (`Admin/`, `Video_Editor/` subfolders). Top-level 14 scanned.
- `Clipping` — task said 6, recursive is 7 (`graphify-out/converted/Pov-AI-Ideas_aee0c020.md` is a generated artifact). Top-level 6 scanned.
- `OpenAI_History` — task said 1, recursive is **2,012**; only 1 file is top-level (`README.md`, a folder-organization readme, not a bookmark). The other 2,011 are nested ChatGPT conversation exports under theme folders (e.g. `Content-Strategy-YouTube/`, `Image-Generation-Design/`). Nested conversation exports were **out of scope** for this scan (they are episodic history, not catalog entries) — see Notes & Skips.
- Also excluded as non-catalog artifacts, matching the prior scan's treatment of `PI-Harness-Pack/`: the `graphify-out/` directories present in `Clipping/`, `Design_Inspiration/`, `Docs/`, `Investments/`, `Models/`, `Personal/`, `Prompts/`, `Research/`, `Tutorials/`, `Workflows/`.

**Yield note (as predicted):** `Content_Ideas`, `Design_Inspiration`, `Mockups`, `Models`, `POD_Prints`, `Investments`, `Travel`, `Personal`, `Research`, and `Docs` are overwhelmingly reference/inspiration/personal notes, Etsy-search and print-design references, and AI-model spec sheets — **very low true-tool yield**, and that is reported honestly rather than padded. `Tutorials`, `Workflows`, `Prompts`, `UGC`, `Digital_Products`, and `Affiliate_Marketing` carried the real hits. Marketplace/aggregator sites that recur everywhere but are *not* new tools (`Etsy`, `Gumroad`, `Patreon`, `Skool`, `YouTube`, TikTok, Notion, Instagram, Pinterest, Google Drive) were skipped; they are platforms already known and not individual adoptable tools.

---

## Affiliate_Marketing
- **Mavely** — affiliate marketing platform for creators (trackable links across 1,400+ brands, commission tracking); now under Later as "Later Creator". — `Affiliate_Marketing/Mavery.md`
- **Stay22** — travel-creator affiliate monetization platform (interactive maps, direct hotel links, AI pop-up for booking/retail conversion). — `Affiliate_Marketing/Stay22.md` (duplicate: `Affiliate_Marketing/Stay22-Affiliate-Platform-for-Creators-and-Publishers.md`)
- **Zeydoo** — global CPA affiliate network (SmartLink, surveys, sweepstakes, mobile apps; traffic monetization). — `Affiliate_Marketing/Zeydoo.md`
- **OpusClip / Agent Opus (Partner Program)** — AI video clipping platform; the note is the affiliate program onboarding (dashboard via Rewardful, media kit). — `Affiliate_Marketing/OpusClip-Affiliate-Program.md`
- **Submagic (Affiliate Program)** — AI editor for short-form videos; note is the affiliate program page. — `Affiliate_Marketing/Submagic-Affiliate-Program.md`
- **PayKickstart (Partner Program)** — checkout/cart and affiliate-management SaaS; note is the partner/affiliate program page. — `Affiliate_Marketing/Partner-With-PayKickstart.md`

## Clipping
- **JumpTask** — micro-task earning platform (watch videos, train AI, surveys, games; crypto/fiat payouts). — `Clipping/Whop-2.md`
- **Zerpd** — campaign platform connecting creators to clipping campaigns with rewards for short-form content. — `Clipping/Zerpd-Campaign-Platform-for-Content-Creators.md`

## Content_Ideas
*(366 files; the large majority are AI-art/thumbnail/short-video concept notes and faceless-channel scripting ideas with no adoptable product. ~10 genuine tools surfaced.)*
- **TransitionalHooks** — library of pre-made transitional video clips for short-form content. — `Content_Ideas/Transitional-Hooks.md`
- **VidClue** — categorized library of 200+ short-form video ideas for brands/creators. — `Content_Ideas/Vidclue.md`
- **VideoHooks** — library of attention-grabbing hook clips/ideas for ads and social posts. — `Content_Ideas/Videohooks.md`
- **OverseerOS** — reverse-engineers YouTube channels for content ideas (free YouTube Channel Analyzer + blueprint demo). — `Content_Ideas/OverseerOS-Reverse-Engineer-YouTube-Channels-for-Content-Ideas.md`
- **Sollo AI** — AI tool for starting a one-person business. — `Content_Ideas/Claude-AI-Just-Leaked-25-New-YouTube-Niches-Nobody-Talks-About.md`
- **Viblo (viblo.ai)** — AI video tool for producing viral shorts. — `Content_Ideas/Fastest-Way-To-Hit-10kmo-With-Yt-Shorts-Copy-Me.md`
- **Kalodata** — TikTok Shop product-research tool. — `Content_Ideas/How-I-Recreate-Viral-TikTok-Shop-Videos-With-AI-In-Minutes.md`
- **The Viral Scriptwriter** — TikTok Shop script/template tool. — `Content_Ideas/Ive-Posted-Over-1000-TikTok-Shop-Videos-This-Script-Formula-Prints.md`
- **ShortsCut (shortscut.com)** — short-form video tool. — `Content_Ideas/What-Getting-3-Billion-Views-Taught-Me-About-Human-Psychology.md`
- **MusicalSEO** — music-niche research tool. — `Content_Ideas/How-I-Made-114-000-With-Suno-AI-Distrokid-Spotify-Itunes-Best-Faceless-YouTube-Strategy.md`

## Design_Inspiration
*(207 files; almost entirely Etsy-search art styles and Pinterest-style print references. Only 2 real tools surfaced; the rest are downloadable-art references, which are not adoptable products.)*
- **VoltAgent / awesome-design-md + DESIGN.md** — Google Stitch `DESIGN.md` plain-text design-system spec read by AI agents for consistent UI, plus the VoltAgent `awesome-design-md` GitHub collection. — `Design_Inspiration/VoltAgent-Design-MD.md`
- **React Bits (reactbits.dev)** — library of ready-made animated React UI components (web-dev resource). — `Design_Inspiration/React-Bits-Web.md`

## Digital_Products
- **Lemon Squeezy** — all-in-one e-commerce platform for digital products/subscriptions/software licenses (Merchant of Record: payments, tax, fraud). — `Digital_Products/Lemon-Squeezy.md`
- **Creepypasta.com** — long-running platform/archive of user-generated horror short stories (content-sourcing resource). — `Digital_Products/Creepy-Stories.md`
- **AI Animation Course (Societiesr / Tudor Morari)** — Gumroad course teaching practical AI animation workflows (video lessons, cheat sheets, prompts). — `Digital_Products/AI-Animation-Course.md`
- **StayViral** — platform/course teaching organic TikTok affiliate marketing. — `Digital_Products/TIKTOK-Stayviral-Olgalia-Mont-Step-By-Step-Stay.md`
- **Maxime Labonne (mlabonne.github.io) blog** — ML/LLM articles and notebooks; a downloadable-resource site. — `Digital_Products/Education-And-Online-Courses.md`
- **Creatorwood (Michael Evans book landing page)** — downloadable book/landing page. — `Digital_Products/TIKTOK-Who-Michael-Evans-Chapters-Book.md`
- **Wirestock (wirestock.io)** — stock photo/video marketplace for creators (sell and source datasets). — `Digital_Products/Stock-Video-Dataset-for-AI-Training.md`
- **Entrepedia + Circle (entrepedia.co / circle.so)** — done-for-you digital products + community platform (rebrand/resell). — `Digital_Products/Digital-Products-And-PLR.md`
- **Stan Store (stan.store)** — link-in-bio storefront for selling digital products. — `Digital_Products/Sheet-Chita-Cheat-Selling-Digital-Products.md`

## Docs
*(14 files; handbooks, medicine notes, and setup docs — no adoptable products, except the item below.)*
- **Claude Code + Meta Ads plugin** — a Claude Code plugin automating Meta Ads campaign work (one-plugin "agency"). — `Docs/Claude-Code-Meta-Ads-A-10K-Agency-in-One-Plugin.md`

## Investments
- **Equitybee** — fintech marketplace connecting startup employees with accredited investors (option exercise funding, private-equity liquidity). — `Investments/Angel-Investing.md`
- **Arkham Intelligence** — AI blockchain-intelligence platform (de-anonymizes on-chain wallets, tracks entities across chains). — `Investments/Crypto-Wallet-Analyzers.md`
- **Stoic AI** — automated crypto trading / AI portfolio management (connects exchange accounts via API). — `Investments/Robo-Trading.md`
- *(reference only, skipped: Autopilot and Alinea investing apps, Copilot finance app, Kalshi prediction market, StockAnalysis/DEXTools, DraftKings — app-marketing screenshots or non-adoptable references.)*

## Mockups
*(47 files; all product mockups and print-design references — no adoptable products. Skipped cleanly.)*

## Models
*(50 files; mostly model/API spec sheets and Civitai/LoRA reference notes. Genuinely usable downloadable models/run-times below; the rest are model references already tracked elsewhere.)*
- **Nari Dia** — open-source 1.6B text-to-speech model (ultra-realistic multi-speaker dialogue with non-verbals). — `Models/Nari-Dia.md`
- **Kokoro TTS** — 82M-parameter text-to-speech model (StyleTTS 2 architecture; efficient, natural voice synthesis). — `Models/Kokoro-Tts.md`
- **ComfyUI (models/setup)** — node-based generative-AI UI; the note lists essential ComfyUI models/tools plus companion repos (`ComfyUI-LTXVideo`, `ComfyUI-Manager`, `ComfyUI-VideoHelperSuite`, `ComfyUI-ModelDownloader`). — `Models/ComfyUI_Models_Recommendations.md`; `Models/Comfyui.md`; duplicate `Workflows/Comfyui-Models-Reccomendations.md`
- **ElevenLabs Voice Library** — community marketplace of AI voices usable in TTS projects. — `Models/Hope-The-Story-Teller.md`; `Models/Kat-Dollar-British-Story-Teller.md`
- **Veo 2 (Google DeepMind)** — generative video model platform. — `Models/Veo-2.md`
- **Kie.ai** — unified API access across video/image/music models (Kling, Sora 2, Veo 3.1, Nano Banana, Seedream, Suno, Wan). — `Models/API-STACK-REFERENCE.md` and the per-model spec files in `Models/` (Kling, Sora2, Veo3.1, Wan 2.6, Suno, Seedream, Nano Banana 2)
- **World Labs (Marble)** — 3D world-generation API/platform. — `Models/World-Labs-API-Quickstart.md` (also referenced in `Content_Ideas/World-Labs-AI-Intranet.md`)
- **Magnific API** — image upscaling/enhancement API. — `Models/Welcome-to-Magnific-API.md`; `Models/Magnific-API.md`
- **Perplexity Sonar API** — web-grounded, citation-backed chat-completion API. — `Models/Sonar-API.md`
- **Unsloth** — tooling to run/quantize large open LLMs locally (GLM-5.2 GGUFs). — `Models/GLM-52-LLM---Running-Locally-with-Unsloth.md`
- **Civitai (model host)** — model/LoRA hosting platform (DreamShaper XL, Juggernaut XL, Surreal Collage, etc.). — `Models/Model-Stlyes.md`, `Models/Juggerna-Xl.md`, `Models/Surreal-Sdxl-Model.md`, and other `Models/*.md`

## OpenAI_History
*(top-level: 1 file, `README.md` — folder-organization readme, not a tool. Nested conversation exports out of scope; see Notes & Skips.)*

## POD_Prints
*(112 files; essentially all are print designs, t-shirt graphics, and POD listing research. No adoptable products surfaced.)*
- *(single borderline item skipped: `POD_Prints/Bal-Tins-Listing-Details-Shap-Naleani.md` — a product listing detail, not a tool.)*

## Personal
*(30 files; personal notes/screenshots and one hydration-soda reference — no adoptable products. Skipped cleanly.)*

## Prompts
*(102 files; mostly prompt snippets and prompt-engineering notes. Genuine adoptable products below.)*
- **viralsoraprompts.com** — AI tool that generates viral-ready Sora 2 video prompts. — `Prompts/Viral-Sora-Prompts.md`
- **godofprompt.ai** — prompt library/site (Veo 3 prompt templates). — `Prompts/God-Of-Prompt-Veo.md`
- **prompts.chat** — prompt directory with integrations for ChatGPT, Claude, Gemini, Llama. — `Prompts/Prompts-Chat.md`
- **Seedance 2.0 Prompt Writing Skill (dexhunter/seedance2-skill)** — agent skill for writing Seedance video prompts; works with Claude Code/Cursor/Cline. — `Prompts/Seedance-20-Prompt-Writing-Guide-and-Skills.md`
- **Seedance 2.0 Prompting Guide & Library (Higgsfield)** — full prompt library + guide hosted on Higgsfield. — `Prompts/Seedance-2-0-Complete-Prompting-Guide-Full-Prompt-Library.md`
- *(reference only, skipped: ChatGPT prompt cheat-sheets, JSON prompt templates, "Nano Banana" prompting guide, Etsy prompt snippets, Kingdoms & Conquerors script prompts.)*

## Research
- **Crypto data-visualization tools** — curated list: **Bubblemaps** (blockchain visualizer), **Crypto Bubbles** (interactive market bubble chart), **DappRadar** (dApp analytics). — `Research/Research.md`
- *(reference only, skipped: DraftKings screenshots, "3d-videos"/conspiracy research lists, TikTok Ad Swipe File, Etsy keyword-research notes.)*

## Travel
*(25 files; travel guides, restaurant lists, itineraries, and booking-infrastructure notes — no adoptable products surfaced.)*
- *(borderline skipped: `Travel/Travel-Public-Relations.md` — list of luxury-travel PR agencies, a contact resource rather than a tool.)*

## Tutorials
*(253 files; mainly video tutorials and workflow walkthroughs. Real tools/repos referenced by those tutorials, harvested below.)*
- **GitHub repos:** **Ponytail** (`DietrichGebert/ponytail`) — Claude Code agentic-OS/observability layer; **Draw.io Skill** (`Agents365-ai/drawio-skill`) — diagram generation skill; **Improve** (`shadcn/improve`) — code-improvement repo; **NVIDIA skillspector** (`nvidia/skillspector`) — skill-scanning tool; **Handy** (`cjpais/Handy`) — open-source dictation app; **Infinite Bookshelf** (`Bklieger/infinite-bookshelf`) — generates full books from a prompt via Groq + Llama; **Impeccable** (`pbakaus/impeccable`) — gives Claude Code a design vocabulary for frontend work; **matts-peeker** (`ston6919/matts-peeker`) — Claude skill that "watches" videos (frame extraction + Whisper); **claude-watch / `/watch`** (`taoufik123-collab/claude-watch`) — Claude skill/plugin to watch any video URL or file; **open-generative-ai** (`anil-matcha/open-generative-ai`) — open-source Higgsfield alternative; **dataforseo-claude** (`zubair-trabzada/dataforseo-claude`) — AI SEO toolkit on Claude Code + DataForSEO API. — `Tutorials/5-NEW-Vibe-Coding-Repos-You-Havent-Heard-of-Yet.md`, `Tutorials/Arcads-Claude-Code-GitHub-repo.md`, `Tutorials/Infinite-Bookshelf-GitHub-repo.md`, `Tutorials/Claude-Watchatch-GitHub-repo.md`, `Tutorials/This-Open-Source-Repo-Solves-Claude-Codes-Biggest-Problem.md`, `Tutorials/Claude-Codes-Biggest-Problem.md`, `Tutorials/I-Built-a-Claude-Skill-That-Instantly-WATCHES-Any-Video.md`, `Tutorials/How-To-Get-The-Open-Source-Higgsfield-AI-Free.md`, `Tutorials/Claude-Just-Changed-the-SEO-Industry-Forever.md`
- **Arcads AI (Agent Skill Pack)** — Claude Code/Cursor skill pack for AI ad creative using an Arcads account (Seedance 2.0, Sora 2, Veo 3.1, Kling 3.0, Nano Banana, etc.). — `Tutorials/Arcads-Claude-Code-GitHub-repo.md`
- **Open Montage** — open-source agentic video studio that plugs into an AI coding assistant (research → script → shots → edit). — `Tutorials/This-FREE-Open-Source-Video-Agent-Is-WILD.md`
- **Remotion** — open-source "video in React" framework that Claude Code drives for motion graphics/animation. — `Tutorials/I-Forced-Claude-to-Clone-Any-Video-Editing-Style-in-Remotion.md`; `Tutorials/Claude-CapCut-Animations.md`
- **Buzz (buzz.xyz)** — Block's app letting AI agents join a team (self-hostable Slack/GitHub alternative). — `Tutorials/This-New-App-Gave-Me-an-AI-Team-of-Employees.md`
- **RUBRIC (getrubric.app)** — "command centre" for AI agents. — `Tutorials/Higgsfield-Just-Launched-Their-AI-Agent-Supercomputer.md`; `Tutorials/The-NEW-Agentic-OS-standard-for-Claude-5-Models-is-here-Full-Breakdown.md`; `Tutorials/This-NEW-Claude-Prompting-Technique-is-blowing-peoples-minds-gauntlet-loop.md`
- **Blotato** — AI content-repurposing/publishing tool. — same three `robonuggets`-sourced files above
- **Kit MCP** — connects a Kit (email) account to Claude for list/broadcast management. — `Tutorials/How-to-Connect-Kit-to-Claude-with-the-Kit-MCP-Step-by-Step-Tutorial.md`
- **Kie.ai / dainami.ai FREE MCP connector** — connects Claude to many creative models (Seedance, Veo, GPT-Image, Suno, Kling) pay-per-use. — `Tutorials/Claude-Replaced-Higgsfield-with-This-FREE-MCP.md`
- **ViroScope AI** — niche/video idea generator with virality scores. — `Tutorials/My-Channel-Isn-T-Monetized-But-It-Already-Paid-Me-Using-Claude.md`
- **Kalodata** — TikTok Shop product-research tool. — `Tutorials/Meet-The-College-Dropout-Who-Makes-80kmonth-On-TikTok-Shop.md`
- **The Daily Virals** — viral-video discovery tool. — `Tutorials/Meet-The-College-Dropout-Who-Makes-80kmonth-On-TikTok-Shop.md`
- **invideo Agent One** — AI storyboard-to-video agent. — `Tutorials/The-Only-Workflow-To-Turn-A-Storyboard-Into-An-AI-Video.md`
- **AI Video Studio for Resolve** — DaVinci Resolve plugin replacing cloud AI video platforms (local/GPU). — `Tutorials/This-DaVinci-Resolve-Plugin-Just-Replaced-EVERY-AI-Platform-Cloud-Free-GPU.md`
- **ChatLLM (Abacus.ai)** — all-in-one AI agent/chat tool. — `Tutorials/TikTok-Live-Studio-MAC.md`
- **OpenArt (openart.ai)** — platform to access/compare GPT-Image 2 and other image models. — `Tutorials/How-to-Use-GPT-Image-2-Better-Than-99-of-People.md`
- **Zappy Flow** — Chrome extension for batch image generation (Vox-style workflow). — `Tutorials/FREE-Claude-Prompt-That-Creates-VOX-Style-Videos-AUTOMATICALLY-Heres-How.md`
- **Whisperflow** — macOS dictation app (talk instead of type). — `Tutorials/How-I-Make-42035mo-Posting-On-Facebook-Using-Claude-AI.md`
- **Open-source Higgsfield / LTX 2.3 (local video gen)** — free local AI-video pipelines (ComfyUI-free LTX workflows; BBox Animator LoRA). — `Tutorials/Uncensored-Ltx2.3-Is-Here-Generate-AI-Videos-Locally-Without-ComfyUI.md`; `Tutorials/LTX-25-BBox-Animator-is-AMAZING-Control-any-Object-in-ComfyUI.md`
- **Ollama + Qwen3.5** — run open LLMs locally. — `Tutorials/Run-Qwen-AI-Models-Locally.md`
- **Obsidian (+ Dataview, Web Clipper)** — note system extended with community plugins/agentic loops. — `Tutorials/Obsidian-Vault-Deep-Dive-Custom-Plugins-Agentic-Loops-My-Full-System.md`; `Tutorials/Build-Obsidian-System.md`; `Tutorials/The-4-Levels-Of-Obsidian.md`
- **n8n / Make / Zapier (Agents)** — automation/orchestration platforms (tutorials, not new tools; noted for completeness). — `Tutorials/Agents-Agent-Search-Hersyagent-Ote-Forms.md`, `Tutorials/AI-Automation.md`, `Tutorials/Nn-MCP-Setup-Guide.md`
- **Yapper (yapper.so)** — AI film/video tool. — `Tutorials/Remaking-a-39000-Higgsfield-Film-with-100-In-depth-Full-Workflow.md`
- **Enhancor AI (app.enhancor.ai)** — AI-influencer video generator + Seedance 2 API dashboard. — `Tutorials/She-Isnt-Real-Definitive-AI-Influencer-Pipeline.md`; `Tutorials/The-Cheapest-Way-To-Run-Al-UGC-Ads-Claude-Plus-Seedance.md`
- **Seedance 2.0 AI UGC repo** — free UGC-ads pipeline (`github.com/sirioberati/Seedance-2.0-AI-UGC`). — `Tutorials/The-Cheapest-Way-To-Run-Al-UGC-Ads-Claude-Plus-Seedance.md`
- **Recraft (recraft.ai)** — AI image/design generator. — `Tutorials/The-Secret-To-AI-Character-Sheets.md`
- **Topview (topview.ai)** — AI video generation tool (Seedance storyboards). — `Tutorials/These-4-Seedance-20-Techniques-Make-AI-Video-Actually-Look-Good.md`; `Tutorials/Ultimate-Seedance-Control-Storyboards-With-GPT-Image-2.md`
- **Reel Stack (reel-stack.com)** — AI motion-graphics tool. — `Tutorials/Step-by-Step-AI-Motion-Graphics-Fable-vs-Sol.md`
- **Dreamina (CapCut)** — CapCut image/video generator (character/environment consistency). — `Tutorials/Seedance-2.5-Character-Environment-Consistency-Tutorial.md`; `Tutorials/Seedance-2.0-GPT-Image-2-Character-Environment-Consistency-Tutorial.md`
- *(reference only, skipped: ~200 "how to make $X with Claude/AI" tutorials, faceless-channel strategy videos, Seedance/GPT-Image prompt walkthroughs, course/membership links [Skool], and community-invite links.)*

## UGC
- **BeeRoll** — AI video-marketing platform connecting brands with 10,000+ UGC creators. — `UGC/Beeroll.md`
- **Brands Meet Creators** — marketplace connecting brands with creators for TikTok Shop partnerships. — `UGC/Brands-Meet-Creators.md`
- **Cohley** — creator platform driving brand growth (UGC/influencer campaigns). — `UGC/Cohley-Creator-Platform.md`
- **Fastlane (usefastlane.ai)** — UGC platform. — `UGC/FastLane-AI-UGC-Platform.md`
- **SideShift (sideshift.app)** — platform to recruit/source UGC creators. — `UGC/Google-Side-Shift-Short-Sideshift-Https.md`
- **Insense** — UGC + influencer-marketing platform connecting brands and creators. — `UGC/Insence.md`
- **JoinBrands** — UGC/creator marketplace for authentic video and photo content. — `UGC/Join-Brands.md`
- **Kale (kalecard.com)** — creator-rewards / UGC platform for brand-creator collabs (crypto/cash earning). — `UGC/Kale.md`
- **Payday Social** — creator-economy platform connecting people with brands for short-form content. — `UGC/Payday.md`
- **Payper (getpayper.app)** — connects creators with brands for UGC marketing campaigns. — `UGC/Payper.md`
- **Promote.fun** — performance-based content-distribution marketplace (brands ↔ creators, short-form campaigns). — `UGC/Promote-Fun.md`
- *(reference only, skipped: Glew.ee rate-card ad, Noise app, Vidsy/Fiverr mention, create-with-AI-UGC method notes.)*

## Undetermined
- **Fal.ai** — developer platform for running generative AI models (fast inference APIs for image/video). — `Undetermined/Fal.md`
- **Klap** — AI SaaS that converts long-form YouTube videos into short clips (auto-reframe, multilingual captions). — `Undetermined/Klap.md`
- **SerpApi** — real-time search-engine-results API (structured JSON; proxies/CAPTCHA handled). — `Undetermined/Serpapi.md`
- **Lowest Hanging Fruit** — product-discovery tool + Chrome extension for Amazon Influencers (high-commission, low-competition products). — `Undetermined/Low-Hanging-Fruit.md`
- **TrustedHousesitters** — housesitting/pet-sitting exchange platform (remote-work travel stay). — `Undetermined/Remote-Work.md`
- *(reference only, skipped: Amazon Associates/contract agreements, stock analysis, prompt snippets, "make money" tutorials.)*

## Workflows
*(54 files; mostly personal automation specs and Node-RED/n8n/Zapier flow exports. Tools referenced by the flows below.)*
- **Lands.ai** — workflow/pipeline builder SaaS (visual "Add first step" editor). — `Workflows/Lands-Landscaping-Workflow-Builder.md`
- **PiAPI** — unified API gateway for Midjourney/Suno/Kling/Flux image+video models (used by the n8n faceless-POV template). — `Workflows/Faceless-Pov-AI-Agent-N8N-Template.md`
- **Creatomate** — programmatic video-rendering API (referenced in the same n8n template). — `Workflows/Faceless-Pov-AI-Agent-N8N-Template.md`
- **Topview MCP** — marketing-intelligence MCP connector driven from Claude. — `Workflows/Claude-To-Topview-Mcp-Automation.md`
- **Composio** — integration layer connecting apps/agents to Notion (AI content-repurposing system). — `Workflows/Composio-To-Notion-AI-Content-Repurposing-System.md`
- **Miro (Claude Code AI setup)** — collaborative whiteboard wired to Claude Code for visual brainstorming → dev. — `Workflows/Miro-Claude-Code-AI-Setup.md`
- **Flowise** — open-source LLM/agent flow builder (used in the TTS API workflow). — `Workflows/Text-to-Speech-API-Workflow-Flowise.md`
- **FFmpeg + Whisper (Auto Shorts Editor V2)** — open-source local video-editing automation. — `Workflows/Auto-Editor-V2.md`; `Workflows/Auto_Editor_V2.0_(Python_Local).md`
- **Easy Machine Protocol / EasyMachineAI** — AI-OS workflow resource/community (Skool-backed templates and tools). — `Workflows/Easy-Machine-Protocol-V2.md`
- *(reference only, skipped: raw Node-RED/Zapier/n8n TTS flow screenshots, Apple Shortcut shell scripts, personal master workflows.)*

---

## Notes & Skips
- **Coverage:** all 1,526 top-level `.md` files were read (full-tree frontmatter extraction for every file; full-body reads for the 86 files with missing/short frontmatter plus ~50 borderline bodies). No unread range remains. The 18 folder counts above sum to 1,526.
- **Why the yield is low, as expected:** `Content_Ideas` (366), `Design_Inspiration` (207), `POD_Prints` (112), `Mockups` (47), `Models` (50), `Investments` (75), `Travel` (25), `Personal` (30), `Research` (35), and `Docs` (14) are reference/inspiration/personal collections. Matches were **not** forced; folders with no genuine adoptable product (`Mockups`, `POD_Prints`, `Personal`, `Travel`, `OpenAI_History`) are reported as empty rather than padded.
- **Marketplace/aggregator platforms skipped as already-known, not individual tools:** Etsy (95 occurrences), Gumroad (20 `public-files` links), Patreon, Skool (50+ community/membership invites), YouTube, TikTok, Notion, Instagram, Pinterest, Google Drive, Calendly, Typeform. These are ubiquitous in the notes but are not new adoptable products.
- **Duplicates collapsed to one entry with extra filenames noted:** Stay22 (`Stay22.md` + `…Affiliate-Platform…`), ComfyUI models (`Models/ComfyUI_Models_Recommendations.md` + `Workflows/Comfyui-Models-Reccomendations.md` + `Workflows/Comfyui-Node-Map.md`), Kie.ai (1 stack reference + ~13 per-model spec files), Higgsfield (referenced in 18 files; already cataloged in the `Tools/` scan), ElevenLabs Voice Library (2 voice-profile notes).
- **Deliberately NOT duplicated from the prior `Tools/` scan:** tool-doc bookmarks that live in these folders but whose product is already listed in `Resource_Library_Tools_Scan_2026-10-08.md` were kept out to avoid double-counting the watch list (e.g. Higgsfield, Nano Banana, Seedance, Arcads, n8n/Kie entries already there). Where a note here adds a genuinely new product, it is listed above.
- **`OpenAI_History/` nested exports out of scope — flag for Tony:** the folder holds **2,011 nested `.md` ChatGPT conversation exports** under theme folders (`Content-Strategy-YouTube` 242, `Image-Generation-Design` 145, `Coding-Development` 129, `AI-Agents-Automation` 102, `POD-Print-on-Demand` 105, etc.). These are episodic history, not bookmark/catalog entries, and were excluded from this scan (this pass covered only the 1 top-level file). If Tony wants tool mentions harvested from old conversations, that is a separate, much larger pass — not done here.
- **Skipped — pure reference/inspiration with no adoptable product:** Etsy search-result pages and print-design references (the bulk of `Design_Inspiration`, `Mockups`, `POD_Prints`, `Digital_Products`), AI-art/thumbnail concept notes (`Content_Ideas`), stock-photo/Unsplash art references, and personal screenshots (`Personal`, frozen-pizza/payment/App-Store screenshots).
- **Skipped — model/API spec sheets already tracked as models rather than tools:** Sora 2, Wan 2.6, Seedream 5.0 Lite, Kling 2.6/3.0, Veo 3.1, Suno, Nano Banana 2, OpenAI GPT model-version lists, Genie/Tencent D/Skyfall-GS/Hermes model promo notes (`Models/`). Only genuinely adoptable hosts/runtimes (Nari Dia, Kokoro TTS, ComfyUI, Unsloth, Civitai, ElevenLabs, Veo 2, World Labs, Magnific, Sonar, Kie.ai) are cataloged.
- **Skipped — tutorials/strategy with no discrete product:** the ~200 pricing/algorithm/faceless-channel tutorials and prompt walkthroughs in `Tutorials/`, course/membership funnels (Skool, Patreon, Gumroad course links), and prompt snippet notes in `Prompts/` that are prompts rather than products.
- **No files in `007_Resource_Library/` were modified, moved, renamed, or deleted.** Cataloging only; original filenames preserved.

*Generated 2026-10-08 by Codex chore worker. Read-only; no files in `007_Resource_Library/` were modified.*
