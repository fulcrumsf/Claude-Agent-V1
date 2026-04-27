# CLAUDE.md — Video Content Engine

---

## Vault Access

**Before starting work:** Read `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/000_VAULT-INDEX.md`

This department's knowledge is organized in the vault under:
- Skills: `/Obsidian-Vault/000_Skills/` (shared workflows including NotebookLM protocol, video production workflow, case study analysis)
- Brand systems: `/Obsidian-Vault/002_Brands/` (guidelines, content systems, case studies for all active brands)
- Tools: `/Obsidian-Vault/003_Tools/` (video model pricing, kie.ai vs fal.ai analysis, Nano Banana guide)

**Warehouse root:** `/Users/tonymacbook2025/Documents/Claude-Agent/`
**TOOLBOX:** `/Users/tonymacbook2025/Documents/Claude-Agent/TOOLBOX.md`

**Vault-first rule:** Search the vault for context before asking the user. If you need clarification, ask a focused question instead of requesting extensive background.

---

## ⚡ BEFORE BUILDING ANYTHING — CHECK TOOLBOX FIRST

**Always check the TOOLBOX before writing code or suggesting new scripts.**

Tony has pre-installed tools for all common video production tasks. Never rebuild what already exists.

**TOOLBOX location:** `/Users/tonymacbook2025/Documents/Claude-Agent/TOOLBOX.md`

**Video-specific tools you should know about:**

All universal scripts live in the Obsidian Vault under `/Obsidian-Vault/003_Tools/`:
- **Video generation** → `Video-Generation/kie_video_gen.py` (Veo 3.1, Kling 3.0, Wan 2.6, Sora 2)
- **Image generation** → `Image-Generation/kie_image_gen.py` (Nano Banana 2, Nano Banana Pro)
- **Text-to-speech** → `Text-To-Speech/audio_tts.py` (ElevenLabs with word-level timestamps)
- **Video frame extraction** → FFmpeg (system CLI)
- **Video stitching** → `Video-Generation/video_stitcher.py`
- **YouTube analysis** → `AI-Analysis/gemini_video_analysis.py` + `/analyze-video` skill
- **Case studies** → `000_Skills/case_study_generator.py` + `/case-study` skill (automated full pipeline)
- **FCPXML export** → `Remotion/export_fcpxml.py` (Final Cut Pro import)
- **New video scaffolder** → `Video-Generation/new_video.py` (project folder setup)
- **Remotion** → Next.js + React video composition (remotion-app/)
- **Remotion MCP** → `npx @remotion/mcp@latest`
- **Documentary research** → `/documentary-research` skill

For complete reference, read TOOLBOX.md. For vault-first architecture details, see Obsidian Vault 000_VAULT-INDEX.md.

---

## What This Is
An AI-assisted multi-channel YouTube content production system. Claude Code handles all production manually during the trial phase. Once video quality meets monetization standards (views, retention, subscriber growth), the system migrates to n8n for automated scheduling and execution.

**Active channel:** NeonParcel (most data, most subscribers — start here)
**Phase:** Trial — quality before automation. Do not suggest n8n workflows until the user explicitly says to.

---

## Key Directories
```
001_Configuration/                ← API keys (.env), config files (pyrightconfig.json, requirements.txt)
002_Channels/                     ← All channel data (bibles, video projects, case studies, styles, docs)
  001_Anomalous-Wild/
    001_Bioluminescence-Weapon/   ← Self-contained video project (scripts, assets, output)
    002_End-Card/
  002_Neon-Parcel/
  ... (010 more channels)
  Docs/                           ← Shared API stack reference, storytelling guides
  Styles/                         ← Cinematic style templates and reference frames
003_Remotion/src/remotion/        ← Video components and compositions
003_Remotion/src/skills/          ← Remotion skill docs (sequencing, transitions, typography, etc.)
004_Tools/                        ← Orchestration only (pipeline supervisor, batch runners, preloop)
```

**Note:** All universal scripts (TTS, image gen, video gen, FCPXML export, etc.) live in Obsidian Vault under `/Obsidian-Vault/003_Tools/`

---

## Case Studies

**CRITICAL:** When the user says "create a case study", "do a case study", "case study of [video]", or provides a URL asking what makes it successful — **immediately invoke the case-study skill** before doing anything else.

The skill lives in: `.agents/skills/case-study.md`

The skill will:
1. Fetch YouTube metadata (views, likes, title, description)
2. Run Gemini 2.5 Flash analysis on hook structure, retention, viral score, production notes
3. Download video and extract 3 screenshots (beginning/middle/end via FFmpeg)
4. Save case study to `002_Channels/[NNN_Channel-Name]/Case-Studies/[video-title-slug]/`

Output includes: case_study.md, 3 screenshots, and a viral score breakdown.

**After the skill completes:** Present the viral score summary (Hook/Retention/Shareability/Production/Overall) and top 3 things to replicate.

---

## Starting a New Video — Workflow

**1. Research**
Search YouTube (trending in niche) + Reddit + web for ideas matching the channel's content pillars. Score each idea by hook strength, search volume, and estimated curiosity pull. Present the top 3–5 ideas to the user with a 1-line hook and a score rationale. Wait for user selection.

Once a topic is selected, create a **NotebookLM research notebook** for that video (see NotebookLM Research Protocol below). All factual claims in the script must trace back to sources in the notebook — not from model memory.

**2. Pre-Production Questions**
Before generating anything, ask the required pre-production questions below. Do not skip this step.

**3. Asset Sourcing**
All footage and images must be:
- CC0 / public domain, OR
- AI-generated (Fal.ai, Kling via Kie.ai, etc.)
- **If a copyrighted reference is needed:** use it as a detailed prompt to recreate it as AI art — we own AI-generated reinterpretations.
No paid stock licenses.

**4. Production**
Match the video style to the channel bible + styles reference. Generate assets (images → video via APIs), build the composition in Remotion. The asset manifest (generated in Step 3) contains multiple candidate assets per scene marked with `"recommended": true` for the primary choice.

**5. Asset Review & Scoring**
After Remotion renders the video, the system automatically scores it 0–100 (visual quality, pacing, narrative flow, retention hooks, CTA clarity). If the score is below 100/100, the editor can manually swap assets before final publication:

**Multi-Source Asset Swapping (Final Cut Pro / Adobe Premiere):**
1. Export FCPXML from Remotion: Use `export_fcpxml.py` from Obsidian Vault (`/Obsidian-Vault/003_Tools/Remotion/`)
2. Open the FCPXML in Final Cut Pro or Adobe Premiere
3. Locate the `asset-manifest.json` in the video project folder (e.g., `002_Channels/[Channel]/[Video-ID]/asset-manifest.json`)
4. For any clip you want to replace:
   - Open the asset manifest and find the scene's `candidates` array
   - Choose a different candidate (non-recommended is still viable)
   - Copy its URL from the manifest
   - In FCP/Premiere, right-click the clip → Replace with Media → paste the URL or download and relink
5. Re-export the timeline to MP4

This workflow lets you:
- Keep the Remotion automation (timings, transitions, text overlays)
- Swap out specific footage/images if the AI-selected version doesn't feel right
- Test multiple variants quickly without re-rendering the entire Remotion composition
- Maintain all metadata and timing from the score

**Example:** If Remotion picked a NASA Earth satellite image for "beautiful planet shot" but you want to try the Library of Congress alternative from the manifest instead, you can swap it in FCP in <2 minutes without touching Remotion code.

**6. Review Loop**
Present the edit (with or without asset swaps). Wait for user feedback. Revise. Repeat until approved. If video still scores below 100/100 after manual review, the assets have already been swapped — just iterate on pacing, music, or narration timing at this point.

**6. Finalize**
Generate title options, description, and thumbnail prompt. Log everything to Airtable. Only publish after explicit user approval.

**7. Track**
After 2 weeks: pull YouTube Analytics data, score the video, update the Airtable record.

---

## Pre-Production Question Template
Ask these before starting any video. Adapt based on what the user has already told you.

```
1. Channel: Which channel is this for?
2. Format: Short (< 60s vertical) or long-form (3–10 min horizontal)?
3. Topic: What is the core subject or story?
4. Hook: What is the most counterintuitive or surprising angle?
5. Style: Check 002_Channels/[NNN_Channel-Name]/[Channel-Name]-Content-System.md for style options —
          confirm which visual style (AI-generated footage, CC0 real footage,
          motion graphics/Vox-style animation, mixed)?
6. Voiceover: Yes/no? If yes, tone (dramatic, calm, curious)?
7. Music mood: What feel? (tense, epic, lo-fi, ambient, etc.)
8. CTA: What should the viewer do at the end?
```

If the user gives a loose topic ("make a video about Napoleon's escape"), reframe it into a hook-driven premise before confirming: present the proposed hook and ask for approval before proceeding.

---

## Channel Bibles
Each channel's full identity, color system, content pillars, thumbnail rules, and AI prompt templates lives in:
`002_Channels/[NNN_Channel-Name]/[Channel-Name]-Content-System.md`

Always read the relevant bible before producing anything for that channel. Do not invent style rules from memory.

---

## Asset Memory (Qdrant)
Every generated image or video scene gets a Qdrant vector embedding. Tag with:
- Subject(s), setting, time period, mood, style, channel, video ID

This enables B-roll reuse: before generating new assets, search Qdrant for existing ones that match the scene description. Reusing assets saves API spend and builds a growing library.

---

## Airtable (Command Center)
*Structure to be defined — do not build tables yet without user instruction.*

When Airtable is ready, every video record should include:
- Title + description
- Thumbnail (image URL)
- All generation prompts used (sub-table or linked record)
- Status: `idea → in production → needs work → approved → scheduled → published`
- Performance score (populated after 2-week analytics pull)

Publishing slots are time-gated: minimum 3 hours between posts per channel per platform.

---

## Rules
- **Never publish** without explicit user approval on that specific piece of content
- **Never trigger n8n** or suggest automation until user gives the green light
- **Never use copyrighted material** — CC0 or AI-recreate only
- **Always read the channel bible** before producing for that channel
- **Always ask pre-production questions** before generating assets — do not assume
- **Always present ideas with scores and hooks** — not just topic names
- **Measure outcomes** — after 2 weeks, pull analytics and score the video. Use that data to improve the next one. The goal is a system that gets better, not one that just repeats.

---

## Production Quality Standards (from Video 001 Report Card — B+ grade)

These are mandatory rules derived from post-production critique. Violations repeat the same mistakes.

### Folder Naming
- All video output folders: zero-padded sequence prefix — `001_`, `002_`, `003_`
- Format: `outputs/<NNN_channelname>/<NNN_slug>/`

### Audio Is the Master Clock
1. Generate narration TTS first
2. Extract word-level timestamps from ElevenLabs (or transcribe with timestamps)
3. Build `beat_sheet.json` from those timestamps
4. **All visuals — overlays, illustrations, scene cuts, transitions — are scheduled against the beat map**
5. Never estimate timecodes manually. Every visual trigger must have a source timestamp.

### Three-Layer Audio System (BBC Earth standard)
Every video must have all three layers:
1. **Narration** — always clearest, sits on top of the mix
2. **Music/Score** — Suno generates one long instrumental from a mood description of the video; plays under the full runtime, ducked below narration
3. **Ambient/SFX** — Kling clips generated with `sound: true` for scene-specific natural sound

- All audio transitions must **crossfade** — never hard-cut between scenes
- Dead silence anywhere in a finished video is a failure condition

### NotebookLM Research Protocol

Every video that involves science, history, animals, or factual claims gets its own NotebookLM notebook. This is the grounded source of truth — the script generation agents query the notebook, not their own training data.

**Why:** NotebookLM only answers from the sources you give it. It will not hallucinate beyond what's in the notebook. For topics like deep-sea biology, historical events, or medical facts, this eliminates fabricated details.

**Workflow:**
```bash
# 1. Create a notebook for the video
notebooklm create "Bioluminescence - Deep Sea Animals - [date]"

# 2. Add sources (URLs, PDFs, YouTube videos, uploaded images)
notebooklm source add "https://en.wikipedia.org/wiki/Bioluminescence"
notebooklm source add "https://www.nature.com/articles/..."
notebooklm source add-research "anglerfish bioluminescence biology"  # auto-research

# 3. Query for specific facts before scripting
notebooklm ask "What percentage of deep sea animals are bioluminescent?"
notebooklm ask "How does the anglerfish lure work biologically?"
notebooklm ask "List all bioluminescent animals featured in this notebook"

# 4. Generate a structured research report
notebooklm generate report

# 5. Download the report and save to the video's 003_docs folder
notebooklm download report --output 002_Channels/[NNN_Channel]/[Video-ID]/003_Docs/research_report.md
```

**What to add as sources:**
- Wikipedia articles for each key subject (animal, phenomenon, location)
- Scientific journal abstracts (Nature, PLOS, NCBI)
- YouTube video URLs (NotebookLM can process video transcripts)
- Uploaded reference images of the actual animals/organisms
- Any PDF research papers

**Rule:** The script writer agent reads the NotebookLM report before generating any narration. Facts go in, hallucinations stay out.

---

### Scientific Accuracy — Reference-First Pipeline
For any scientifically specific animal, organism, or anatomy:
1. Researcher finds real reference images (Google Images, scientific journals) — save to project folder
2. Nano Banana recreates the illustration **without text, lines, or callouts**
   - Negative prompt: `"no text, no labels, no callout lines, no arrows, no annotation marks"`
3. All text labels and callout lines added in Figma (MCP available) or SVG — **never by the image model**
4. Export as PNG/SVG → drop into Remotion as static asset

**Rule:** The image model draws the picture. It never writes the words.

### Title Card Standard
- Must be cinematic and world-specific — never generic 3D text on a star field
- Must have ambient audio during the title card — never silent
- Reference quality: George Lucas / Pixar opening — pull the viewer into the world before the story starts

### Infographics
- Illustrations triggered by narration beat map timestamps — not manually placed
- Never use image model for labeled diagrams — gibberish text destroys credibility

### Clip Manifest
- Generated automatically after every video
- Columns: Clip ID | Reference image ✓/✗ | Source | Model used | Notes
- Saved to `<video_folder>/003_docs/clip_manifest.json`

### Report Card
- After every video: user gives a grade and critique
- Saved to `<video_folder>/_review/report_card.md`
- Used to improve the next video — not filed and forgotten

### FCPXML Export
- Generated for every video using **relative paths** (not absolute)
- Saved in video root folder so moving the folder doesn't break paths

---

## Cinematic Styles & AI Model Selection

The video production pipeline uses **6 production methodologies** (cinematic styles) — not content categories, but **treatment approaches** to how footage is composed, generated, and edited.

**Core styles:**
1. **Style 01: Archival B&W Documentary** — Grayscale, 1960s–90s aesthetic, historical credibility
2. **Style 02: 3D Animated Synthetic** — Clean geometric visualization, educational, bright synthetic colors
3. **Style 03: Satellite/Map Visualization** — Google Earth style, topographic overhead, information overlays
4. **Style 04: HD Underwater Camera** — Cinematic submersible footage, color depth gradient, bioluminescence
5. **Style 05: National Geographic Wildlife** — Professional wildlife cinematography, shallow DOF, warm colors
6. **Style 06: Scientific Infographic** — Information visualization, high-contrast diagrams, data-driven

**Key principle: Image-first workflow**
- Generate static images via Nano Banana 2 (kie.ai) — cheapest, fastest
- Extend to video only when narrative requires motion
- Text labels **always** in Remotion, **never** in image model

**Public domain asset sourcing:**
- **Reference:** `002_Channels/Docs/PUBLIC-DOMAIN-SOURCES-RATING.md` — 1-10 rating of all public domain/CC sources
- **Tier system:** Always query Tier 1 sources first (NASA, Pexels, Wikimedia Commons), then Tier 2 if needed
- **Philosophy:** Multiple candidates per scene, not just one selected asset
- **Manual override:** Asset manifest includes all candidates for FCP/Premiere swap if video scores <100/100

**Model selection rules:**
- **Default platform:** kie.ai (30–70% cheaper than fal.ai)
- **Default image model:** Nano Banana 2 on kie.ai ($0.04–0.09 per image)
- **Default video model:** Kling 2.1 Pro on kie.ai ($0.025–0.05/second)
- **Hero sequences:** Veo 3 Quality on kie.ai ($0.25/second)
- **NEVER use Seedance 2.0** (suspended March 15, 2026) — fallback to Veo 3 Quality or Kling 2.1 Pro

**Full documentation:**
- **CINEMATIC_STYLE_GUIDE.md** — Complete guide to all 6 styles, visual identity, generation workflows, post-processing rules
- **MODEL_SELECTOR.md** — Human-readable model selection guide with cost scenarios and decision trees
- **MODEL_CATALOG.json** — Full pricing table and model catalog (agent-readable, JSON format)
- **MODEL_SELECTOR.json** — Decision rules for agents (agent-readable, JSON format)

**How to choose:**
1. Check the script's narrative beats
2. Map each beat to the appropriate style (use case section in CINEMATIC_STYLE_GUIDE.md)
3. Consult MODEL_SELECTOR.md for quality tier and platform
4. Generate image → review → extend to video if needed → compose in Remotion

**Creature accuracy requirement (critical):**
- Every creature visual must match narrator's description exactly (size, behavior, environment, appearance)
- Always reference real-world images before generation
- Validate against beat_sheet.json timestamps (narrator timing is master clock)

### Accessing the Cinematic Style System

The system is fully documented and ready for production:

1. **For understanding styles:** Read `002_Channels/Styles/CINEMATIC-STYLE-GUIDE.md` (human-readable definitions of all 6 styles)
2. **For model selection:** Use `002_Channels/Docs/MODEL-SELECTOR.md` (decision tree) or `002_Channels/Docs/MODEL-SELECTOR.json` (for agent logic)
3. **For reference frames:** Each style folder contains representative frames: `002_Channels/Styles/style-templates/style_0N_*/frames/`
4. **For pricing details:** `002_Channels/Docs/MODEL-CATALOG.json` has complete model catalog across both platforms
5. **For production examples:** `002_Channels/001_Anomalous-Wild/Case-Studies/What-They-Found-In-The-Deepest-Place-On-Earth/` shows real-world style usage

**Agent workflow:**
1. Receive script → identify narrative beats
2. Map beats to styles (use CINEMATIC_STYLE_GUIDE.md)
3. Query MODEL_SELECTOR.json for model recommendation (provide style, budget, quality tier)
4. Generate image first (Nano Banana 2 on kie.ai, default)
5. Extend to video if needed (Kling 2.1 Pro or Veo 3)
6. Review reference frames for this style to validate quality
7. Post-process using style-specific rules from CINEMATIC_STYLE_GUIDE.md
8. Schedule all cuts against beat_sheet.json timestamps

---

## API Stack (keys in 001_Configuration/.env)
| Tool | Purpose |
|------|---------|
| Fal.ai | Image and video generation (secondary platform) |
| Kie.ai | Primary platform: Image + video generation (Nano Banana, Kling, Veo, Runway, Seedance) |
| ElevenLabs | Text-to-speech voiceover + timestamp extraction |
| Suno | Music/score composition and ambient SFX generation |
| YouTube Data API v3 | Trend research, video lookup |
| YouTube Analytics API | Performance tracking (OAuth — 2-week scoring) |
| Airtable | Command center / production database |
| Cloudinary | Image/video CDN storage |
| OpenRouter | LLM routing (scripts, scoring, research) |
| Blotato | Social media scheduling |
| Perplexity | Web research |
| Openverse | Open-licensed image/video search (Creative Commons, public domain) |
| Qdrant | Vector DB for asset memory |

Full API reference: `002_Channels/Docs/API-STACK-REFERENCE.md`

**Note on kie.ai vs fal.ai:** Kie.ai is the primary gateway for image and video generation. It offers unified pricing that is 30–70% cheaper than fal.ai for Nano Banana, Kling, and Veo models. Use fal.ai only for models unavailable on kie.ai.

---

## Remotion Stack
Built in Next.js + Remotion. Two videos completed (1 vertical Short, 1 3-min Anomalos Wild long-form).
Components: `003_Remotion/src/remotion/video-components/`
Skill docs (sequencing, transitions, spring physics, typography): `003_Remotion/src/skills/`
