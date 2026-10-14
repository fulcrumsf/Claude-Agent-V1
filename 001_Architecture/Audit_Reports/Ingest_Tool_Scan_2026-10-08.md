---
title: "Ingest Tool Scan — 000_Ingest Bookmark Catalog"
type: audit-report
category: architecture
tags:
  - ingest
  - tool-scan
  - api-watchlist
  - growth-tools
created: 2026-10-08
source: 000_Ingest/
---

# Ingest Tool Scan — 000_Ingest Bookmark Catalog (2026-10-08)

Read-only scan of the bookmarked links sitting in `000_Ingest/` (the 156 root-level markdown files; the `.md` files under subfolders are project artifacts and skill bundles, not topic bookmarks). Each file's title and body were read to decide whether it describes a usable **tool, app, or API/SaaS product** Tony could adopt to grow his content/business. Pure tutorial/how-to articles with no specific product, and generic news, were skipped. Nothing in `000_Ingest/` was deleted, moved, or renamed.

Purpose: a flat triage list for Tony to shortlist into the API watch list.

**Visual, searchable version:** https://claude.ai/artifact/3D9QHYnL7EZ8eunDsHRz4R ("Tool Catalog") — now merged with two follow-up scans into one 674-tool searchable page. Cross-linked from `001_Architecture/API_Directory.md`.

**Scope note (2026-10-08):** this file's own scan covers only `000_Ingest/` (156 bookmark files, 126 rows). Two follow-up passes covered all of `007_Resource_Library/`: `Resource_Library_Tools_Scan_2026-10-08.md` (936 files in `Tools/`, 472 rows) and `Resource_Library_Remainder_Scan_2026-10-08.md` (the other 18 categories, ~1,526 files, ~120 rows). All three are merged into the one artifact above. Not covered: 2,011 nested ChatGPT conversation exports in `OpenAI_History/` — excluded on purpose as episodic history, flagged for Tony as a separate decision.

**Maintenance plan:** `001_Architecture/Plans/Tool_Catalog_Maintenance_Plan.md` — how this stays current going forward, with 9 open decisions for Tony.

## YouTube / Content Tools
- **ChannelRecipe** — Faceless YouTube channel video automation / viral video generation. — `How I'm Using Claude AI to Build a GTA 6 Cash Cow Channel.md`
- **TubeLab (TubeAvatar, Niche Finder)** — YouTube niche/video-idea research, avatar videos, automation goldrush toolkit. — `Exposing The New YouTube Automation Goldrush (October 2026).md`
- **VidIQ** — YouTube SEO/analytics with an MCP connector for Claude. — `How I Automate 90% of My Social Media Content with Claude AI.md`
- **1of10** — YouTube thumbnail/title testing and packaging optimization. — `give me 9 minutes, I’ll make your thumbnails 81% better.md`; `how I forced youtube to push my videos (with 0 subs).md`
- **Morningfame** — YouTube audience/topic research and growth analytics. — `This Forces YouTube to Find the Right Audience For Your Videos.md`
- **TubeBuddy** — YouTube channel management/SEO toolkit. — `This Forces YouTube to Find the Right Audience For Your Videos.md`
- **NotebookLM** — Google research/audio-overview engine repurposed for faceless history channels. — `I Turned NotebookLM Into a History Channel Engine (Full Workflow).md`
- **Cliptai** — Marketplace to hire clippers/editors, pay-per-1K-views campaigns. — `Cliptai - Hire Clippers and Editors for Your Stream.md`
- **OpenShorts** (mutonby) — Open-source short-form clip generation from long video. — `5 Github repos that print $$$.md`
- **AI shorts generator** (yukitorido) — Open-source OpusClip/Vidyo alternative: highlight detection, subtitles, translation, voiceover. — `yukitoridoshort-video-generator-AI ...md`
- **Recordly** — Open-source screen recorder with webcam bubble + timeline editing. — `Recordly - Open-source app for incredible screen recordings..md`
- **Gyroflow** — Open-source gyro-based video stabilization. — `Gyroflow v1.6.3 is out!.md`
- **Chatcut** — Prompt-driven AI video editor (edit by describing changes). — `Chatcut Edit Videos with Prompts.md`
- **Diffusion Studio** — Agent-native professional video editor (analyze/design/edit/generate/transcribe). — `Diffusion Studio AI Video Editor for Agents.md`
- **Flick** (Creatorberry) — Turns a video/script into scene-by-scene Remotion animations. — `Creatorberryflick ...md`
- **OpenCreator** (formerly KrillinAI) — Open-source creator workspace: video, image, voice, avatars, translation. — `krillinaiOpenCreator ...md`
- **CapCut** — Consumer video editor used in micro-drama pipelines. — `How to Make Micro Dramas Better than 99% of People.md`
- **Google Flow** — Google AI filmmaking tool; Storyboard + Shot Animator workflow. — `NEW Google Flow Can Make LONG CINEMATIC AI MOVIES (FREE COURSE).md`; `Pipeline_Orchestration/Google_Flow_Storyboard/*`
- **Shot Animator** — Custom tool that turns Google Flow storyboard JSON into animated shots. — `Pipeline_Orchestration/Google_Flow_Storyboard/Google Flow From Storyboard JSON to Animated Video Pipeline  Shot Animator Tool.md`

## SEO / Analytics
- **Distribb** — AI SEO autopilot: plans/publishes buyer-intent content for WordPress/Webflow/Shopify etc. — `AI SEO Software - Grow Organic Traffic.md`; also ships the Super Video Maker skill in `Bomxsuper-video-maker-skill ...md`
- **OpenSEO** (every-app) — Open-source, pay-as-you-go Semrush/Ahrefs alternative with agent skills. — `every-appopen-seo Open source alternative to Semrush and Ahrefs.md`; `5 Github repos that print $$$.md`
- **PostHog** — Product analytics (appears only as an optional telemetry build arg inside the Foundry repo doc, not its own bookmark). — `horizon-foundryfoundry Claude Code skills for software delivery integrity ...md`
- **Julian Goldie SEO** — AI SEO/keyword-cluster service and order desk. — `Claude Opus 5.5 AI SEO 0 to 1,300 Clicks.md`

## Social / Affiliate / Commerce
- **Blotato** — Social automation: comment-to-DM funnels and content distribution. — `Automate Your Entire Social Media Funnel wClaude ($120KYear).md`
- **OpenReply** (diwenne) — Open-source ManyChat alternative; Instagram comment-to-DM via Meta API. — `diwenneopenreply The open-source Manychat alternative.md`
- **Social SDK** (opencoredev) — Typed TypeScript SDK for Bluesky/Instagram/LinkedIn/Threads/TikTok/X/YouTube. — `opencoredevsocial-sdk ...md`
- **Jev Social / socai** — Read-only social research agent for Instagram, TikTok, LinkedIn. — `socai-iojev-social ...md`
- **Browser Use — Jev Ultrafast** — Fast/cheap cloud browser agent (waitlist). — `browser-usejev-ultrafast Fastest and cheapest web agent.md`
- **Scrapling** (D4Vinci) — Adaptive web-scraping framework with anti-bot bypass and MCP server. — `D4VinciScrapling ...md`; `5 Github repos that print $$$.md`
- **Apify** — Scraping/automation platform used in the agency stack. — `Skills/Solo_Higgsfield_Agency/Solo_Creative_Agency_Higgsfield_ Claude.md`
- **Listadum** — Etsy shop & listing manager/analytics (official API). — `Listadum - Grow your Etsy shop ...md`
- **Etsy** — Marketplace (affiliate/POD sales channel). — `How to Get Paid by Amazon for Posting AI Images on Instagram (FULL TUTORIAL).md`
- **Printify** — Print-on-demand API/store platform. — `I Gave Claude Code an API Key and It Built a Merch Store.md`
- **Krafie** — All-in-one AI tool for digital products. — `How to Get Paid by Amazon for Posting AI Images on Instagram (FULL TUTORIAL).md`
- **Trend2Design / Trend2Designs** — Daily trending-search data turned into copy-paste image prompts. — `Trend2Design — Where trends become designs.md`; `how i make $6,000week selling ai images as digital products.md`
- **Kittl** — AI image generator/design tool. — `how i make $6,000week selling ai images as digital products.md`
- **Alura** — Etsy revenue estimator. — `how i make $6,000week selling ai images as digital products.md`
- **BuyTTS** — Store selling ready TikTok Shop accounts. — `How to Use GTA 6 to Make $10,000mo On TikTok Shop Affiliate.md`
- **Assigns** — AI real-estate investing software. — `Assigns + Muse AI Makes Money While You Sleep 🤖  Assigns News EP 11.md`
- **FOMO (fomo.family)** — Social crypto trading app/web platform; Robinhood Radar variant. — `Fomo Social Crypto Trading App & Web Platform.md`; `cvxv666fomo-robinhood-radar ...md`
- **Potion** — Crypto perps signal/trading service. — `Potion — Crypto Markets Made Simple.md`
- **Pump.fun** — Solana memecoin launch/trade platform. — `Pump.fun — Launch and trade memecoins on Solana.md`
- **Padre.gg** — Memecoin trading terminal. — `Your Edge in Memecoin Trading Terminal.md`

## AI Video / Image / Audio Generation
- **Higgsfield** — AI video/image model platform (Seedance, Soul, DOP) with MCP. — `Higgsfield AI vs Free AI Video Generators ...md`; `How I Make Ultra Realistic AI Videos using Seedance 2.5.md`; `I Tried The LAZIEST Way to Make Money With AI.md`
- **Maxfusion AI** — AI creative layer for agencies: UGC ads, singing ads, MCP. — `Maxfusion AI - AI Creative Layer for Brands and Agencies.md`; `Why Song Ads Are Printing Money ...md`
- **Pippit / Pippit Story Studio** — End-to-end AI video and story/scene production. — `Pippit AI Short Drama Workflow ...md`; `Pippit Story Studio Create AI Stories, Scenes & Videos Online.md`
- **Topview AI** — AI video agent for short films and marketing videos. — `Topview AI Video Agent for Short Films & Marketing Videos.md`
- **MovieFlow** — Text-to-video AI movie generator (multi-model). — `AI Movie Generator  Text to Video in Minutes.md`
- **Buzzy AI** — Pro AI video engine with Seedance workflows. — `Buzzy AI - Pro Video Engine for Everyone.md`
- **Cantina** — App to build social AI characters that make videos. — `Cantina App Infinite Creativity Unlocked.md`
- **OpenArt / OpenArt Director** — AI micro-drama director: character setup, story, editing. — `How to Make a Micro Drama with AI (Full Guide).md`; `How to Vibe Direct ...md`
- **invideo Agent One** — Invideo's agent for micro-drama season production at volume. — `How to make Microdramas with AI Agents (Filmmaking Guide).md`; `The only Workflow for an AI Microdrama Season.md`
- **Magnific** — Image variations/AI storyboard generation for consistent scenes. — `How to create a storyboard from one image with Variations  Magnific How-To.md`; `Spaces by Jerrod Lew ...md`
- **XGEN-JING** — Egocentric interactive experience model (first-person video + audio). — `XGEN-LabsXGEN-JING.md`
- **Open Generative AI** (Anil-matcha) — Self-hosted, unrestricted image/video studio, 400-600+ models. — `Anil-matchaOpen-Generative-AI ...md`
- **Wan2GP** (DeepBeepMeep) — One-stop open-source video/image/audio/TTS generator for modest GPUs. — `deepbeepmeepWan2GP ...md`
- **Open-Sora** (hpcaitech) — Open-source efficient video production model/toolkit. — `hpcaitechOpen-Sora ...md`
- **WorldSculpt** (AlayaLab) — Compositional world generation from grounded videos. — `AlayaLabWorldSculpt ...md`
- **Seedance 2.x / Dreamina** — Video model used across tutorials. — `Seedance 2.0 - How to FIX Character & Environment Consistency (+ FREE PROMPTS).md`; `Seedance 2.5 Transforms iPhone Footage into Cinematic AI Videos.md`
- **Hunyuan Video / Z-Image Turbo** — Free AI video/image models. — `Higgsfield AI vs Free AI Video Generators ...md`
- **ACE-Step 1.5** — Open-source local music generation model (Mac/AMD/Intel/CUDA). — `ace-stepACE-Step-1.5 ...md`
- **VoiceStudio** (debpalash) — Fully-local ElevenLabs alternative: voice clone/dub/dictate, 646 languages. — `debpalashVoiceStudio ...md`
- **Voicebox** — Open-source local voice cloning/TTS/dictation desktop app. — `Voicebox - Open Source Voice Cloning Desktop App.md`
- **FluidVoice** — On-device macOS voice-to-text (local model). — `FluidVoice — Voice-to-Text for macOS.md`
- **OpenLive** (katipally) — On-device voice + vision layer for AI agents (VAD/STT/TTS/barge-in). — `katipallyopenlive ...md`
- **FAL.ai** — Image/video generation API (stock-photo pipeline). — `I built a machine that creates stock photos 247.md`
- **Pixify.io** — Stock photo/keywording/upload pipeline tool. — `I built a machine that creates stock photos 247.md`
- **Thrixel / Build World** — Generates 3D assets/worlds for Three.js/Roblox/Unity/Unreal. — `thrixelbuild-world ...md`
- **Film space** (maxprokopp) — SwiftUI virtual film studio with iPhone ARKit camera capture for AI style transfer. — `maxprokoppfilm-space ...md`
- **Kimodo** (nv-tlabs) — Kinematic motion diffusion model for human/robot motion. — `nv-tlabskimodo ...md`
- **Mixamo LLM Mocap** (squall01337) — Turn any video into a Mixamo-rig animation via Blender MCP. — `squall01337mixamo-llm-mocap ...md`
- **sprite-gen** (aldegad) — 2D game sprites/animation atlases as a Codex/Claude skill. — `aldegadsprite-gen ...md`
- **anidoodle** (alexgreensh) — Code-drawn art/animation/explainers in 31 styles. — `alexgreenshanidoodle ...md`
- **riso-windowseat** (sevenevesai) — Procedural risograph films in single HTML files. — `sevenevesairiso-windowseat ...md`
- **ComfyUI Cinema Worldbuilder** — ComfyUI node pack for disciplined LTX cinematic prompt composition. — `comfyui-cinema-worldbuilderREADME.md at master.md`
- **AI Visual Prompt Cookbook** (VigoZhao) — 118+ JSON style packs for Nano Banana Pro/GPT Image/Midjourney. — `VigoZhaoAI-Visual-Prompt-Cookbook ...md`
- **Awesome Qwen-Image 2.1** (wildminder) — Checkpoints, quants, prompt engines, LoRAs, tooling. — `wildminderawesome-qwen-image ...md`
- **MuMuAINovel** (xiamuceer-j) — AI novel/story-writing assistant. — `xiamuceer-jMuMuAINovel ...md`

## Dev / Agent Tooling
- **OpenDesign** — Local open-source design engine (21 agents, 152 design systems, BYOK). — `Best Open Source Claude Design Alternative.md`
- **Skillry** (skillry.dev) — Agent-first skill marketplace/CLI for Claude Code, Codex, Cursor. — `Agent Skills for Claude Code, Codex & Cursor.md`
- **ICM Architect** (RinDig) — "Folders over agents" context methodology + skill repo. — `ICM Explained (Folders Over Agents) in Five Minutes..md`
- **here.now** — Instant web hosting/publishing for agent output. — `Instant web hosting for agents.md`
- **HarnessRouter** — Managed agent backend / harness for System One models. — `Build agent products without harness engineering.md`
- **SystemOne Harness** (HarnessRouter) — Turns a System One decision model into an agent loop. — `HarnessRouterSystemOneHarness ...md`
- **TypeSafe System One / Jev** — Decision-model ("System 1") API and blog. — `Introducing System One Models & Jev - TypeSafe AI Blog.md`
- **Laya** — Multilingual non-autoregressive decision model (HF / NandhaKishorM / Core ML ports). — `Hugging Face Laya.md`; `NandhaKishorMlaya ...md`; `mizorewwwlaya-coreml ...md`
- **NanoJev** (TianyuCodings) — Nano replica of Jev (0.6B parallel decision model). — `TianyuCodingsNanoJev ...md`
- **OpenJev** (SiliconLabAI) — Open-source System One-style decision playground. — `SiliconLabAIOpenJev OpenSource Jev.md`
- **jev-router** (gargpratyush) — Per-turn cheapest/strongest model routing for Claude Code + Codex. — `gargpratyushjev-router ...md`
- **ECC** (affaan-m) — Agent-harness performance optimization system (skills/memory/security). — `affaan-mECC ...md`
- **Ponytail** (DietrichGebert) — Agent skill that makes the agent "lazy senior dev" (minimal code). — `DietrichGebertponytail ...md`
- **CodeGraff** (justrach) — Fast agentic coding harness in Zig, multi-provider, MCP. — `justrachcodegraff ...md`
- **MiroFish** (666ghj) — Multi-agent swarm prediction engine / digital-world sandbox. — `666ghjMiroFish ...md`
- **MatrAIx Persona-8B** (MatrAIx-ai) — Simulated-user / persona evaluation infrastructure. — `MatrAIx-aiMatrAIx-Persona-8B Simulate Before Reality..md`
- **Union Alpha** — Free-preview frontier coding/research model (OpenRouter/OpenCode/CF AI Gateway). — `Union Alpha  A frontier model for coding and research.md`
- **OmniRoute** — Open-source AI router with fallback + cost-ranked marketplace. — `Omniroute - Open Source AI Router.md`
- **Caveman Router** — Cuts AI agent token costs via gateway routing. — `Caveman Router Cut AI agent token costs.md`
- **LLMRouter** — Open-source LLM routing framework. — `LLM Router Explained in 10 Minutes ( Stop Using One LLM for Everything).md`
- **Memanto** — Agent memory CLI/dashboard (pip install). — `Memanto Memory that AI Agents Love!.md`
- **Paperclip** — Open-source app to manage a team of AI agents (goals/tasks/budgets). — `you need to try Paperclip RIGHT NOW!.md`
- **skillet** (escoffier-labs) — Production-tested agent SKILL.md workflows (audits/security/releases). — `escoffier-labsskillet ...md`
- **Foundry** (Horizon Foundry) — Eleven Claude Code skills for shipping/auditing AI-built software. — `horizon-foundryfoundry ...md`
- **/watch** (bradautomates) — Gives Claude video evidence: frames + transcript from any video. — `bradautomatesclaude-video ...md`
- **Image Pipes** (mrajaeim) — Visual computer-vision pipeline builder that exports Python. — `mrajaeimimage-pipes Image Pipeline Playground.md`
- **Ruflo** (ruvnet) — Agent meta-harness: swarms, memory, federation, vector RAG. — `ruvnetruflo ...md`
- **God's Eye View** (bilawalsidhu) — Open-source 3D globe with live aircraft/ships/satellites/cameras + voice control. — `God's Eye View GitHub repo.md`; `God’s Eye View Blew Up. What You Can Do With It..md`
- **AutoHDR MCP/API** — Real-estate photo editing automation via MCP/API. — `I Connected My AI to This New MCP and Let It Run My Real Estate Photo Editing.md`
- **Rubric** (getrubric.app) — Command centre for AI agents. — `Turn Claude Into a Video Editing GENIUS (in 3 simple steps).md`
- **Reference agents (OpenClaw, Hermes)** — Agent runtimes referenced as adoptable tooling. — `every-appopen-seo ...md`; `you need to try Paperclip RIGHT NOW!.md`

## Design / Inspiration / Reference
- **Mobbin** — UI/UX design inspiration library (1,000+ apps, 200 sites). — `Mobbin — UI & UX design inspiration for mobile & web apps.md`
- **Refero Design** (Website Styles & DESIGN.md Library) — 2,000+ AI-readable design systems / DESIGN.md files. — `Website Styles & DESIGN.md Library.md`
- **SceneAI** — UI prompt library for web sections and animated landing pages. — `SceneAI The Best UI Prompt Library on the Internet.md`
- **LottieFiles motion-design-skill** — Motion-design principles skill for AI agents. — `LottieFilesmotion-design-skill ...md`
- **prompts.chat** — Community prompt library/dataset. — `AI Prompts Community.md`
- **Motion Design Awards** — Daily motion-design award/discovery platform. — `Motion Design Awards.md`
- **SceneFlow** (taruma) — Syncs screenplays with video to evaluate prompt adherence. — `taruma SceneFlow ...md`
- **Visual-storyboard / Orion system** — Contact-sheet storyboard method (delivered via Maxfusion AI agent). — `The Master Prompt Behind Viral AI Storyboard Videos.md`

## Platform / Infrastructure / Other
- **Together AI** — Serverless inference / AI-native cloud platform. — `The AI Native Cloud.md`
- **Cloudflare** — Free/cheap hosting + AI Gateway for sites and apps. — `I Fired GoDaddy. Claude Runs My 8 Sites for $1Month.md`
- **Firebase** — Google app hosting/backend. — `I Fired GoDaddy. Claude Runs My 8 Sites for $1Month.md`
- **Hostinger AI Builder** — No-code website builder (utility-site cloning). — `This Boring Ugly Website Makes $20kMonth. Here's How to Clone it (No Coding!)..md`
- **Dify** (langgenius) — Open-source LLM app/agent platform. — `5 Github repos that print $$$.md`
- **Presenton** (presenton) — Open-source presentation generator. — `5 Github repos that print $$$.md`
- **Kronos** (shiyu-coder) — Foundation model for financial-market "language". — `shiyu-coderKronos ...md`
- **Genki** — Worldwide health insurance subscription (travel/nomad). — `Worldwide Health Insurance.md`
- **Notion** — Workspace used in the agency stack. — `Skills/Solo_Higgsfield_Agency/Solo_Creative_Agency_Higgsfield_ Claude.md`

## Notes
- **VidIQ** found — `How I Automate 90% of My Social Media Content with Claude AI.md` (YouTube SEO, connected as a Claude MCP connector).
- **PostHog** found — only as a passing mention of optional site analytics inside the Foundry repo doc (`horizon-foundryfoundry ...md`); no dedicated bookmark.
- Skipped as non-tool content: pure tutorials/how-tos with no named product (e.g. `How Projection Mapping Turns Any Room Into Magic.md`, `How to Install LSPDFR Mod in GTA 5 ...md`, `Paste This Into Claude Code ...md`, `Paste This Into GPT-6 Astra ...md`, `The Most Valuable YouTube Training You'll Ever Watch.md`), monetization/news pieces (`Lets Get You Monetized on YouTube BEFORE February 2027.md`), and agent-skill bundles that are project assets rather than products. Full per-file classification notes are in the session log.
- Duplicate/product-cluster files (Maxfusion x2, Pippit x2, microdrama guides x2) are listed once under the product they describe.
