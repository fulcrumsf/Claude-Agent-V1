# Ongoing Agent-OS To-Do List

> Standing to-do list. Nothing here is crossed off automatically — Tony reviews and tells the agent which items to mark done.
> Source of Part 1: `001_Architecture/Handoffs/JEV_ROUTER_HANDOFF_PLAN.md` (2026-09-27), carried over unedited on 2026-09-28.

---

## Part 1: The Candidate Shortlist (30 items, ranked, with status dots)

*Legend:*
* ⚙️ **System Gateway / Core Daemon**
* 🟢 **GitHub Repo / Agent Skill**
* 🔴 **YouTube Tutorial**
* 🌐 **Web SaaS / Platform**
* 🔑 **API Key / Developer Setup**
* 🐳 **Containerized / Sandboxed Tool**
* ⚡ **Live Terminal / Trading Tool**

---

### 🚀 Domain 1: Multi-Agent Infrastructure, Routing & Core Skills (Save Tokens & Automate)

| Rank | Type | Tool / Resource Link | Score | What It Does in Agent-OS | Status / Notes |
| :---: | :---: | :--- | :---: | :--- | :--- |
| **1** | ⚙️ | **The Always-On Global AI Gateway**<br>*(Local Daemon + Jev via OpenRouter API)* | **99** | **Master Router.** Runs silently on `localhost:4000` (or `localhost:3456`). Auto-routes every harness (Antigravity, Claude Code, Codex) via Jev in ~70ms to the cheapest competent model. Zero manual switching, zero 5-hour lockouts. | 🔴 Architecture plan ready; pending implementation |
| **2** | 🟢 | [`Find Skills — AI Agent Skill by Vercel Labs`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Find%20Skills%20%E2%80%94%20AI%20Agent%20Skill%20by%20Vercel%20Labs.md) | **96** | **Meta-Skill Discovery.** Teaches agents to autonomously search (`npx skills find`) and install skills from `skills.sh` mid-task without stopping. | 🟢 Ready in `000_Ingest/` |
| **3** | 🟢 | [`blader/humanizer`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/bladerhumanizer%20Agent%20skill%20that%20removes%20signs%20of%20AI-generated%20writing%20from%20text.md) | **94** | **AI Writing De-Roboter.** Strips AI markers, robotic cadence, and corporate fluff from video scripts, Etsy descriptions, and articles so they read 100% human. | 🟢 Ready in `000_Ingest/` |
| **4** | 🔴 | [`How to Use Jev Instantly (OpenRouter)`](file:///Users/tonymacbook2025/Documents/Agent-OS/007_Resource_Library/Tutorials/How-To-Use-Jev-Instantly-In-Claude-Code-With-OpenRouter/How-To-Use-Jev-Instantly-In-Claude-Code-With-OpenRouter-Tutorial.md) | **92** | **YouTube Guide (Ingested).** Complete tutorial on connecting Claude Code to Jev directly through OpenRouter API with zero waitlist. | 🟢 Fully ingested & packaged |
| **5** | 🔴 | [`Jev will 10x your Claude Code`](file:///Users/tonymacbook2025/Documents/Agent-OS/007_Resource_Library/Tutorials/Jev-Will-10x-Your-Claude-Code/Jev-Will-10x-Your-Claude-Code-Tutorial.md) | **88** | **YouTube Guide (Ingested).** Pre-flight hook router setup (`tools/jev-router/router.mjs`) to offload mechanical triage and preserve tokens. | 🟢 Fully ingested & packaged |
| **6** | 🔴 | [`This NEW Jev + Claude OS`](file:///Users/tonymacbook2025/Documents/Agent-OS/007_Resource_Library/Tutorials/This-NEW-Jev-Claude-OS-Just-Changed-Every-AI-Workflow/This-NEW-Jev-Claude-OS-Just-Changed-Every-AI-Workflow-Tutorial.md) | **85** | **YouTube Guide (Ingested).** Multi-agent personal OS architecture uniting Jev, Claude Opus, Codex, and Obsidian RAG memory. | 🟢 Fully ingested & packaged |

---

### 🎬 Domain 2: Video Pipelines, 3D Blocking & Camera Control

| Rank | Type | Tool / Resource Link | Score | What It Does in Agent-OS | Status / Notes |
| :---: | :---: | :--- | :---: | :--- | :--- |
| **7** | 🟢 | [`Alisa0808/vox-director`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Alisa0808vox-director%20Turn%20one%20topic%20into%20a%20finished%20Vox-style%20paper-collage%20explainerad%20video%20%E2%80%94%20automated%20end%20to%20end%20on%20Atlas%20Cloud%20+%20ffmpeg.%20An%20agent%20skill..md) | **95** | **End-to-End Vox Explainer Engine.** Turn 1 topic into a finished Vox-style paper-collage video (script, collage frames, motion, VO, music, captions) via Atlas Cloud + FFmpeg. | 🟢 Ready in `000_Ingest/` |
| **8** | 🟢 | [`maxprokopp/film-space`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/maxprokoppfilm-space%20SwiftUI%20virtual%20film%20studio%20with%20AR%20camera%20and%20scene%20recording.md) | **94** | **iPhone 3D Virtual Camera & Blocking.** Use your iPhone's gyroscope/ARKit to walk through a 3D staging grid and record exact camera moves for Seedance 2.0 video-to-video reference. | 🟢 Ready in `000_Ingest/` |
| **9** | 🟢 | [`bilawalsidhu/gods-eye-view`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/God%27s%20Eye%20View%20GitHub%20repo.md) | **90** | **3D Globe / Satellite Engine.** Open-source spy-satellite simulator rendering photorealistic 3D globes, orbital flight paths, and terrain for cinematic video b-roll. | 🟢 Ready in `000_Ingest/` |
| **10** | 🐳 | [`Bomx/super-video-maker-skill`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Bomxsuper-video-maker-skill%20AI%20video%20production%20skill%20for%20agents%20HeyGen%20avatars,%20Seedance%20b-roll,%20OpenAI%20images,%20Remotion,%20HyperFrames,%20screen%20recording,%20FFmpeg%20captions%20and%20QC..md) | **84** | **Sandboxed Video/QC Engine.** End-to-end multi-layer pipeline (demo recording, captioning, Remotion/HyperFrames templates, visual layout QC). Sandboxed in Docker. | 🟢 Needs isolated Docker environment |
| **11** | 🔴 | [`JEV Finally Solved AI Video Editing`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/JEV%20Finally%20Solved%20AI%20Video%20Editing%20(Full%20guide).md) | **82** | **YouTube Guide.** Demonstrates automating shot classification, timeline cuts, and prompt tagging for AI video generators (Seedance/Neon Parcel). | 🔴 Pending video ingestion |
| **12** | 🔴 | [`Create FREE Map Animations (Google Flow)`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Create%20FREE%20Map%20Animations%20with%20AI%20%20Google%20Flow%20%20AI%20by%20Moiz.md) | **76** | **Map Flyovers.** Smooth cinematic route animations and 3D map flyovers for travel and documentary video channels. | 🔴 Pending video ingestion |
| **13** | 🟢 | [`socai-io/jev-social`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/socai-iojev-social%20Open-source,read-only%20social%20media%20research%20agent%20for%20Instagram,%20TikTok,%20and%20LinkedIn.%20Jev%20routes%20bounded%20steps;%20local%20socai%20CLI%20captures%20browser%20evidence..md) | **70** | **Competitor Research.** Read-only agent using Chrome to gather trending TikTok/Instagram hooks, affiliate angles, and competitor video evidence. | 🟢 Ready in `000_Ingest/` |

---

### 🎮 Domain 3: 3D Animation, Motion Diffusion & Gaming (Roblox & GTA)

| Rank | Type | Tool / Resource Link | Score | What It Does in Agent-OS | Status / Notes |
| :---: | :---: | :--- | :---: | :--- | :--- |
| **14** | 🟢 | [`squall01337/mixamo-llm-mocap`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/squall01337mixamo-llm-mocap%20Turn%20any%20video%20into%20a%20Mixamo-rig%20animation%20-%20GVHMR%20estimator,%20spec-driven%20retarget,%20FK%20apply%20in%20Blender%20via%20MCP.%20Works%20with%20any%20Mixamo%20character;%20built%20to%20be%20operated%20end-to-end%20by%20an%20AI%20agent..md) | **95** | **AI Video-to-Blender MoCap.** Turn any video into clean FK animations on Mixamo characters in Blender via MCP. Perfect for animating custom Roblox game characters. | 🟢 Ready in `000_Ingest/` |
| **15** | 🟢 | [`nv-tlabs/kimodo`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/nv-tlabskimodo%20Official%20implementation%20of%20Kimodo,%20a%20kinematic%20motion%20diffusion%20model%20for%20high-quality%20human%28oid%29%20motion%20generation..md) | **94** | **NVIDIA Text-to-3D Motion Diffusion.** Generates realistic 3D human and robot skeletal motion from text prompts or 2D paths for Roblox and game animations. | 🟢 Ready in `000_Ingest/` |
| **16** | 🟢 | [`thrixel/build-world`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/thrixelbuild-world%20Build%20interactive%203D%20worlds%20with%20high-quality%20assets%20from%20Thrixel%20and%20your%20AI%20agent%20of%20choice..md) | **82** | **3D World Builder.** Agent skill to construct interactive 3D environments and worlds with high-quality 3D assets. | 🟢 Ready in `000_Ingest/` |
| **17** | 🔴 | [`GTA 5 LSPDFR Cop Mod Setup 2026`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/How%20to%20Install%20LSPDFR%20Mod%20in%20GTA%205%20%20Play%20as%20a%20Cop%20%20Easy%20Tutorial%202026.md) | **80** | **Police Sim Setup.** Full 2026 tutorial for installing LSPDFR police simulator mod with lights, sirens, traffic stops, and arrest systems in GTA 5. | 🔴 Pending video ingestion |
| **18** | 🔴 | [`GTA Cash Cow Channels with Claude AI`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/How%20I'm%20Using%20Claude%20AI%20to%20Build%20a%20GTA%206%20Cash%20Cow%20Channel.md) & [`TikTok Shop Affiliate`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/How%20to%20Use%20GTA%206%20to%20Make%20$10,000mo%20On%20TikTok%20Shop%20Affiliate.md) | **78** | **Gaming Channel Playbook.** Strategies for generating viral GTA gameplay shorts, police pursuit narratives, and monetizing via TikTok Shop affiliate and YouTube. | 🔴 Pending video ingestion |

---

### 🎨 Domain 4: Etsy Print-On-Demand & Digital Wall Art (Ikigai Studio)

| Rank | Type | Tool / Resource Link | Score | What It Does in Agent-OS | Status / Notes |
| :---: | :---: | :--- | :---: | :--- | :--- |
| **19** | 🔑 | **Etsy Developer App & Open API v3**<br>*(Official Etsy Developer Portal)* | **82** | **Auto-Upload Pipeline.** Essential API credentials to programmatically upload print files, mockups, tags, and titles directly to your Etsy shop. | 🔑 Requires developer API registration |
| **20** | 🟢 | [`carolinaaafy/travel-memory-sticker-card`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/carolinaaafytravel-memory-sticker-card%20A%20Codex%20skill%20for%20turning%20travel%20photos%20into%20collectible%20memory%20sticker%20cards..md) | **81** | **Collectible Travel Sticker Cards.** Turns travel photos into aesthetic collectible sticker cards, printable journal ephemera, and digital sticker sheets. | 🟢 Ready in `000_Ingest/` |
| **21** | 🟢 | [`sevenevesai/riso-windowseat`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/sevenevesairiso-windowseat%20Procedural%20risograph%20films%20in%20single%20HTML%20files%20(Window%20Seat,%20Roost%20and%20more),%20with%20the%20Claude%20Code%20skills,%20docs%20and%20tools%20to%20make%20your%20own..md) | **80** | **Risograph Art Engine.** Procedural risograph print generation and multi-color drum separations in single HTML/canvas files for vintage art prints. | 🟢 Ready in `000_Ingest/` |
| **22** | 🟢 | [`alexgreensh/anidoodle`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/alexgreenshanidoodle%20Art%20and%20animation,%20written%20as%20code.%20Illustrations,%20loops,%20interactive%20web%20art,%20stickers%20and%20scored%20films%20in%20dozens%20of%20styles,%20identical%20on%20every%20render..md) | **79** | **Hand-Drawn Engine.** Generates code-driven illustrations across 31 distinct mediums (watercolor, pencil sketch, woodcut, sumi-e, marker). | 🟢 Ready in `000_Ingest/` |
| **23** | 🟢 | [`VigoZhao/AI-Visual-Prompt-Cookbook`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/VigoZhaoAI-Visual-Prompt-Cookbook%20118+%20plug-and-play%20JSON%20style%20packs%20for%20Nano%20Banana%20Pro,%20GPT%20Image%20&%20Midjourney.%20Copy%20one%20JSON,%20get%20a%20style.%20Updated%20daily..md) | **78** | **Style Packs.** 118+ structured JSON style packs for Midjourney and Nano Banana to generate cohesive product collection drops. | 🟢 Ready in `000_Ingest/` |
| **24** | 🌐 | [`Listadum - Grow your Etsy Shop`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Listadum%20-%20Grow%20your%20Etsy%20shop%20with%20the%20most%20advanced%20Shop%20&%20Listing%20Manager.md) | **75** | **Etsy SEO & Auditing.** Keyword explorer, listing health audit, and bulk tag/title editing via Etsy's official API. | 🌐 Web platform bookmark |

---

### 📈 Domain 5: Crypto, Prediction Models & Market Intelligence

| Rank | Type | Tool / Resource Link | Score | What It Does in Agent-OS | Status / Notes |
| :---: | :---: | :--- | :---: | :--- | :--- |
| **25** | 🟢 | [`shiyu-coder/Kronos`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/shiyu-coderKronos%20Kronos%20A%20Foundation%20Model%20for%20the%20Language%20of%20Financial%20Markets.md) | **85** | **Financial Foundation Model.** Trained on candlestick (K-line) tokens from 45 global exchanges for quantitative forecasting (BTC/USDT demo). | 🟢 Ready in `000_Ingest/` |
| **26** | 🟢 | [`cvxv666/fomo-robinhood-radar`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/cvxv666fomo-robinhood-radar%20Who%20the%20good%20traders%20on%20Robinhood%20Chain%20are%20buying%20resolved%20wallets,%20a%2020-second%20on-chain%20tape,%20provenance%20on%20every%20fill,%20AI%20verdicts,%20bursts%20and%20exits.%20Site%20+%20Telegram%20bot%20+%20API.%20Runs%20on%20$0month..md) | **80** | **On-Chain Whale Radar.** Resolves high-performing smart wallets on Robinhood Chain, reads live fills every 20s, and evaluates trade repeatability with AI. | 🟢 Ready in `000_Ingest/` |
| **27** | 🟢 | [`666ghj/MiroFish`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/666ghjMiroFish%20A%20Simple%20and%20Universal%20Swarm%20Intelligence%20Engine,%20Predicting%20Anything.md) | **72** | **Swarm Prediction Engine.** Constructs parallel multi-agent sandboxes from news/market signals to simulate future scenarios and collective behavior (fake personas discussing/voting). | 🟢 Ready in `000_Ingest/` |
| **28** | 🌐 | [`Potion — Crypto Markets Made Simple`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Potion%20%E2%80%94%20Crypto%20Markets%20Made%20Simple.md) | **68** | **Market Intelligence.** Research covering stocks, crypto perps, memes, DeFi, and prediction markets with tracked win-rate history. | 🌐 Web platform bookmark |
| **29** | ⚡ | [`Pump.fun / Memecoin Terminals`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Pump.fun%20%E2%80%94%20Launch%20and%20trade%20memecoins%20on%20Solana.md) | **65** | **Memecoin Trading.** Data and workflows for tracking Solana token launches and rapid trading dynamics. | ⚡ Trading terminal reference |
| **30** | 🟢 | [`aldegad/sprite-gen`](file:///Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/aldegadsprite-gen%20Generate%20clean%202D%20game%20sprites%20&%20animation%20atlases%20%E2%80%94%20component-row%20pipeline%20state%20rows,%20alpha%20cleanup,%20frame%20extraction,%20runtime%20atlases.%20CodexClaude%20skill..md) | **82** | **Game Sprite Generator.** 2D animation atlases, alpha cleanup, and frame extraction for custom games and web assets. | 🟢 Ready in `000_Ingest/` |

---

## Part 2: Jev Future Ideas (added 2026-09-28, after Option B build)

Grounded in real, already-documented pain points — not built yet, logged for later:

1. **TikTok Shop compliance false-positive gate.** The vision scan currently flags the promoted product's own logo as a violation (known bug). A cheap Jev yes/no question ("is this actually a violation, or the promoted product itself?") could gate that before it reaches human review.
2. **Two-stage Resource Library ingest.** Jev pre-triages source-type (YouTube/Screenshot/Bookmark), likely-duplicate, and already-correctly-tagged before the full ingest model runs — matches the "Level 2" pattern from the Jev tutorials.
3. **Auto-pre-score Generation_Log.json / Report_Card.md.** A Jev score (1–10) at generation time, ahead of Tony's own manual A–C grading — flags obviously weak output early without replacing his judgment.
4. **Neon Parcel scale-check trust gate.** A single, small, reviewed Jev noul question ("is this scale result trustworthy enough to skip human review?") — a much smaller version of the frontier-enforcement system attempted and rolled back on 2026-09-27/28 (see `001_Architecture/Plans/Frontier_Enforcement_Plan.md`, parked, not live).
5. **Storyline-vs-execution scoring for Neon Parcel.** Two separate Jev scores per shot (storyline strength, execution quality), matching the existing locked rule that these are different axes — flags a weak storyline before spending on generation.

### Jev fan-out / complexity-triage design (opus-deep review, 2026-09-28 8:35am)

Tony's brain-dump question — "can Jev decide whether a prompt should be split into sub-agents vs. answered inline, not just whether it's a chore" — got a full design pass. Full report is in this session's transcript; summary for planning:

- **Not a new layer.** `jev_route.py` already makes one call per prompt with `route` (answer/chore/frontier) + `multi_task`. Proposal adds a 4th signal, `fan_out` (0–1 probability: "does this split into 3+ independent parallel parts?"), to that same call — no second round-trip, no new latency/cost.
- **Jev can decide to split, but can't write the sub-tasks** — Decisions API only returns typed choices/scores, no free text. The model doing the work still writes the actual breakdown.
- **The retry-loop waste Tony actually described (a model retrying the same failed approach over and over) is a different problem** — that happens mid-turn, after the prompt's already been routed. Proposed fix is a separate `loop_guard.py`: a cheap after-tool-call hook, no Jev call, that counts repeated failures on the same command/file and injects a "stop retrying, hand this to opus-standard/sol-standard" note after 3 strikes. Flagged as the bigger win of the two.
- **Rollout:** ship `fan_out` in shadow mode first (log the score, don't act on it) for ~1 week, then set the real threshold (proposed starting point 0.75, vs. 0.6 for `route`) from `~/Library/Logs/Agent-OS-Router.jsonl` data instead of guessing.
- **Open questions for Tony before build:** (1) does Codex 0.157 / Antigravity expose an after-tool hook event (needed for `loop_guard.py` there)? (2) approve creating `~/.codex/agents/luna-standard.toml` as Codex's cheap named fan-out agent?
- **Not started** — this is a proposal only, no code written, nothing wired in. Needs Tony's go-ahead per the `openrouter-jev-calls` skill's own rule against modifying `jev_route.py` without sign-off.

**Also noted (not Jev-specific):** the "30-day log audit" idea from the tutorials — prompting an agent to mine `claude-mem` history for 5 concrete skills worth automating — is doable right now with existing tools, no new infrastructure needed.

---

## Also built/changed tonight (2026-09-27/28), for context when reviewing this list

- Option B model routing (Jev routing hook + `delegate.py` chore worker) is live and tested in Claude Code, Codex (CLI + Desktop), Gemini CLI, and Antigravity — a different architecture than item #1 above (no `localhost` daemon; per-harness hooks instead), but the same underlying goal.
- `delegate.py`'s chore worker now runs on `typesafe/jev-router` instead of `openrouter/auto` (Tony's explicit call: quality over a fixed cheap-model ceiling; the real safety net is now the monthly OpenRouter cap, not a model-family restriction).
- The official `typesafe-ai` skill and a workspace-customized `openrouter-jev-calls` skill (routes Jev calls through OpenRouter instead of TypeSafe's own direct API) are both installed and confirmed live in Claude Code, Codex, and Gemini CLI.
- A frontier-enforcement system (force real delegation to a stronger model, not just hint at it) was built, found unsafe on review, and rolled back to the safe hint-only state. The code is parked, untouched, at `001_Architecture/Scripts/route_gate.py` / `frontier.py` plus `001_Architecture/Plans/Frontier_Enforcement_Plan.md` — not wired into anything live.

---

## Part 3: Housekeeping queue (2026-09-28, not acted on — review when picked up)

Found sitting uncommitted in the working tree this session. NOT touched (per Tony: leave for later except the Neon Parcel scaffold restructure, which was committed separately as `dea0a6e4`, and the 3 Jev tutorial ingests, delegated separately).

1. **New case study: `Youtube_Studio_Ask_AI`.** Untracked folder at `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Case_Studies/Youtube_Studio_Ask_AI/` — a multi-file case study (e.g. `3-Beat-Formula.md` and others) on structuring a YouTube Shorts mini-series using the Zeigarnik effect / 3-beat escalation formula. Needs review + commit; unclear if it still needs cross-linking into a wiki article the way other case studies get treated.
2. **Uncommitted diff: `001_Architecture/Graphify/REGISTRY.md`** (6 lines changed). Leftover modification, not yet committed — check what changed before committing (may be stale from an interrupted graphify run).
3. **Uncommitted diff: `001_Architecture/Skills/Character-Sheet-Generation/SKILL.md`** (2 lines changed). Same — small uncommitted edit, needs a look before committing.
4. **Untracked: `.tmp.driveupload/`** at workspace root. Looks like a transient Google Drive sync artifact, not a real deliverable — probably safe to gitignore or delete, but confirm with Tony first (no unapproved deletions).
5. **`.obsidian/workspace.json`** — routine Obsidian UI-state diff (open panes/tabs), not a content change. Normally fine to commit whenever, low priority, no action needed unless it's noisy in status.
