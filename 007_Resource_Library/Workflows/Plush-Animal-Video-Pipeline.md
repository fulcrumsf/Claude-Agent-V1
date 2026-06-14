---
Status: Planning
---
# Summary
---
### 🔁 **End-to-End System Breakdown**
### 🧠 **Prompt Creation**
- Stored in Postgres with variable pools
- Templates linked to `theme_id`, auto-tagged
- Agent generates new prompts daily and submits for approval
### ✅ **Approval & Prompt Tracking**
- You approve in Baserow (`status: ready_for_generation`)
- `source_id` is generated after approval using a global counter
### 🎨 **Image Generation**
- Generated via OpenAI (pluggable for ComfyUI later)
- Stored in MinIO
- Tracked in Postgres + embedded in Qdrant with feedback block
### 📝 **Image Grading**
- Gradio interface lets you rate, lock metadata, approve/reject
- Agent learns from `original vs. edited` titles/descriptions
- Approved images go to Upscayl → Kling for video
### 🎞️ **Video Generation**
- Videos get their own `asset_id` and are tracked as remix/derivatives
- Graded separately in Gradio with reuse warning, cooldown checks, and notes
### 📬 **Publishing**
- Agent generates captions, hashtags, descriptions per platform
- Platform checkboxes in Gradio allow manual overrides
- Final approval sends content to Blotato for publishing
- Blotato response and analytics logged in Postgres
### 📈 **Performance Tracking**
- Weekly snapshot stored in Postgres with deltas
- One consolidated email report sorted by theme and format
- Performance scores per post and per theme (1–100)
- Flags reuse patterns, overuse, remix inspiration
- No automatic archiving or pruning
### 📊 **Future Dashboard Ready**
- Logs reuse, cooldowns, remix origin notes, and campaign tags
- Exploration vs. trend-driven creation controlled by a slider (coming)
- Modular agents (prompt → video → publish) operate autonomously but traceably
---
You're fully architected.
Let me know when you're ready to implement or visualize it.
# Tech Stack Flow
# 🧠 Full AI Automation Tech Stack & Process Flow
This document represents the full architecture of your end-to-end automation system, based on the original 28-step flow and all recent updates (including BLIP/CLIP integration).
---
## 🔢 Full Tech Stack & Process Flow
1. **Postgres** – Stores prompt templates, asset metadata, performance scores, and sync states
1. **Baserow** – Control panel for approvals, prompt review, and status toggles (manual input/output)
1. **Prompt Template System** – Dynamic Jinja-style text with variable pools for creative diversity
1. **Agent (n8n + OpenAI)** – Generates new prompts daily from theme-tagged templates and submits for pre-approval
1. **Global Slug Tracker (Postgres)** – Assigns unique, readable `source_id` only after prompt approval
1. **Image Generator (OpenAI for now)** – Produces images from approved prompts; ComfyUI-pluggable later
1. **MinIO** – Stores raw, upscaled, and final assets with organized folder structure
1. **Qdrant** – Embeds prompt, notes, and image data for semantic search and reuse tracking
1. **Gradio (Image Review)** – Lets you rate images, lock metadata, override reuse, and write notes
1. **Upscayl** – Locally upscales approved images automatically after Gradio approval
1. **CLIP (Prompt/Image Similarity)** – Compares prompt-to-image for semantic relevance, supports filtering and QA logic
1. **BLIP (Visual Captioning)** – Describes approved images in natural language for context, scoring, and metadata
1. **Kling** – Converts upscaled images to 5s videos per theme; stored as independent assets
1. **Gradio (Video Review)** – Used again to rate Kling videos, tag for platforms, and approve for publishing
1. **Blotato (API)** – Publishes final video/posts to TikTok, YouTube Shorts, Instagram, etc.
1. **Publishing Metadata Agent** – Suggests titles, captions, hashtags, CTAs per platform and stores originals vs. edits
1. **Postgres (Publishing Log)** – Tracks what was posted, where, when, and Blotato’s response
1. **Postgres (Performance Tracker)** – Stores weekly snapshots of views, likes, shares per post & theme
1. **Weekly Report Generator** – Emails a single styled summary sorted by performance, with deltas and post counts
1. **Asset Reuse Tracker** – Logs how many times an asset was used, where, and whether it’s in cooldown
1. **Agent Notes System** – Adds creative context like “inspired by assetXXX” in database entries
1. **Remix Detection** – Flags variant/remix relationships while promoting new ideas over reuse
1. **Exploration Slider (n8n toggle)** – Controls how often the agent relies on trends vs. experiments
1. **Scoring Engine** – Assigns 1–100 scores per post, aggregates by theme and format, flags low performers
1. **Gradio UI Logic** – Shows platform checkboxes, override warnings, and real-time reuse stats
1. **Cooldown Manager** – Silently enforces reuse gaps per asset/theme with manual toggle control
1. **Campaign Tagging** – Optional grouping of workflows under `project_tag` for trend tracking
1. **Workflow ID System** – Tracks everything from prompt to publish under a unified identifier
1. **Timeline Log (Postgres)** – Records each action taken across agents for visibility and diagnostics
1. **Dashboard-Ready Output (NocoDB/Future)** – All data structured for visual reporting, including theme-level insights
---
✅ This document should be kept as the source of truth for any updates, architecture planning, or visual flow diagrams.
---
# Step by Step Guide
# ✅ AI Content Automation Setup Checklist
This checklist is organized by phase and priority to help you build out your AI-powered creative and publishing system step by step.
---
## 🧱 PHASE 1: FOUNDATION SETUP (SYSTEM & DATA)
- [ ] **1. Set up your local development structure**
- [ ] Create project folder `/ai-content-system`
- [ ] Create subfolders: `assets/`, `scripts/`, `data/`, `templates/`
- [ ] Set up version control (e.g. GitHub or GitLab)
- [ ] **2. Install and run your core Docker services**
- [ ] Postgres container
- [ ] Qdrant container
- [ ] MinIO container (for asset storage)
- [ ] n8n container (automation engine)
- [ ] Optional: Baserow container (approval UI)
- [ ] **3. Define your database schema**
- [ ] Tables: prompts, assets, videos, workflows, performance_snapshots, logs
- [ ] Add indexes and foreign keys where needed
- [ ] Set up connection to n8n
---
## 🧠 PHASE 2: AGENT + CONTENT PIPELINE LOGIC
- [ ] **4. Create your prompt system**
- [ ] Build template structure (Postgres: `prompt_templates`)
- [ ] Create variable pools (CSV or table: `prompt_value_pools`)
- [ ] Add auto-slug generator logic (e.g. `plush_tiger_001`)
- [ ] **5. Build image generation workflow**
- [ ] Agent uses prompt + variables to generate prompt string
- [ ] Submit prompt to OpenAI image API (pluggable for ComfyUI)
- [ ] Save image to MinIO, update Postgres + Qdrant
- [ ] **6. Set up image grading system**
- [ ] Connect Gradio to Baserow or Postgres for review queue
- [ ] Display rating UI, reuse warnings, lock metadata
- [ ] Save rating, user edits, and `edited_by_user = true`
---
## 🎞️ PHASE 3: VIDEO, PUBLISHING & REPORTING
- [ ] **7. Auto-upscale and video gen**
- [ ] Integrate Upscayl via command or n8n trigger
- [ ] Send to Kling for 5s video generation
- [ ] Store video asset with new `asset_id`, keep `source_id` for lineage
- [ ] **8. Final video grading + platform selection**
- [ ] Gradio round 2: show preview, title, description, platform checkboxes
- [ ] Allow override for reuse or cooldown
- [ ] Push approved asset to Blotato node
- [ ] **9. Track publishing status**
- [ ] Create `publishing_logs` table
- [ ] Store platform, status, result, publish timestamp
- [ ] Add `performance_tracking_id`
- [ ] **10. Snapshot performance metrics**
- [ ] Create weekly snapshot process (Postgres cron or n8n)
- [ ] Pull metrics via YouTube, Meta, etc.
- [ ] Store views, likes, shares, deltas, score (1–100)
---
## 📈 PHASE 4: REPORTING, VARIANTS, REMIXING
- [ ] **11. Generate weekly report**
- [ ] Create HTML or styled email format
- [ ] Include totals, deltas, score, asset count, reuse alerts
- [ ] Highlight Top 3, Needs Attention, sort by theme
- [ ] Send from local mailer (n8n or cron)
- [ ] **12. Track remix and variant logic**
- [ ] Mark remix/variant in database (`notes`, `remix_of`, `inspired_by`)
- [ ] Log creative source or reference
- [ ] Allow remix suggestion queue with override toggle
- [ ] **13. Control cooldown + reuse logic**
- [ ] Add toggle for cooldown per asset/theme
- [ ] Track reuse counts per platform
- [ ] Disable asset use during cooldown
- [ ] Add BLIP/CLIP evaluation
---
## 🧠 PHASE 5: FUTURE SYSTEM FLEXIBILITY
- [ ] **14. Add publishing agent logic**
- [ ] Separate GPT or n8n agent for generating titles, descriptions
- [ ] Save both original + edited versions
- [ ] Track which CTAs/tags work best per platform
- [ ] **15. Add exploration vs. trend slider**
- [ ] Add config variable (0–100)
- [ ] Adjust prompt selection logic accordingly
- [ ] **16. Add optional API layer (FastAPI)**
- [ ] Build `GET`, `POST`, `PUBLISH` endpoints
- [ ] Add Swagger UI for visual interaction
- [ ] Connect to GPT in future for direct automation
---
Use this checklist to move one layer at a time — no skipping ahead. Let me know when you're ready to implement a section, and I’ll guide you through the exact setup.

> [!info] Guide: Learn how to obtain, edit, and use the new ChatGPT image generation API for your AI automations and agents  
>  
> [https://www.tiktok.com/t/ZP86yTNkf/](https://www.tiktok.com/t/ZP86yTNkf/)