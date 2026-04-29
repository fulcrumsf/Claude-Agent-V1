---
title: "Video Production System — Rough PDR"
type: spec
domain: video-production
tags: [spec, video-production, workflow-automation]
---

# Video Production System — Rough PDR

## 1. Purpose
Build a modular local-first video production system that can:
- intake and track video ideas
- support human approval before expensive work starts
- research, gather assets, script, edit, render, archive, and index projects
- support multiple channel styles without creating separate apps for each style
- run primarily outside Claude Code in app/workers/pipelines
- use Claude Code mainly to help build, refine, and maintain the system

---

## 2. Core Goals
1. Create a clean operator workflow for reviewing and approving video ideas.
2. Reuse the same production system across multiple channels/styles.
3. Keep each video project self-contained in its own folder.
4. Separate production from archive/indexing.
5. Keep orchestration simple and modular.
6. Allow model/provider settings to change without code rewrites.

---

## 3. Recommended Architecture

### 3.1 High-Level Components
- **Frontend / Control Center**
  - locally hosted GUI in Docker
  - used for approvals, review, status tracking, and configuration
- **Backend App / Controller**
  - manages jobs, state, handoffs, retries, and pipeline execution
- **Pipelines / Workers**
  - research
  - asset gathering
  - script generation
  - edit planning
  - Remotion render
  - archive
  - indexing
- **Storage**
  - local project folders during production
  - MinIO for final archived project storage
- **Databases**
  - Postgres for metadata, statuses, settings, logs, job tracking
  - Qdrant for semantic search over assets and final videos
- **Optional Backend Data Source**
  - Airtable can remain the source of truth for ideas/statuses if desired
  - or Airtable can be phased out later if the custom GUI becomes sufficient

---

## 4. Key Design Decisions

### 4.1 One App, Modular Workers
Do **not** build one giant n8n workflow.
Do **not** build five separate apps first.

Build:
- **one main app**
- **small modular workers/pipelines**
- **n8n only as trigger/router glue if needed**

### 4.2 Styles Are Configs, Not Separate Apps
Styles should be represented as:
- config files
- prompt packs
- scene/template rules

Do not create separate apps per channel unless the workflow itself becomes fundamentally different.

### 4.3 File-Based Project Handoff
Each project should live in a dedicated folder.
Agents/workers pass data through files plus database metadata, not via conversational memory.

---

## 5. Project Folder Structure

```text
video-system/
  app/
  pipelines/
  config/
  projects/
    project-001/
      brief.md
      research.json
      script.md
      asset-manifest.json
      edit-plan.json
      render-config.json
      output/
      assets/
        images/
        video/
        audio/
        generated/
        temp/
```

### 5.1 Project Folder Rules
- All project-specific assets must live inside that project folder.
- Asset paths should be stored as relative paths.
- External assets should be copied into the project folder before downstream steps use them.
- Final render outputs should be saved under `output/`.

---

## 6. Main Pipelines

### 6.1 Intake Pipeline
**Purpose:** create or sync a project from Airtable/UI input.

**Inputs:**
- title
- topic
- channel/style
- notes
- source links
- approval status

**Outputs:**
- project record in Postgres
- project folder created locally
- initial `brief.md`

### 6.2 Research Pipeline
**Purpose:** collect facts, sources, angles, and visual opportunities.

**Outputs:**
- `research.json`
- optional `sources.md`
- candidate visuals list

### 6.3 Script Pipeline
**Purpose:** produce outline/script based on approved topic and research.

**Outputs:**
- `script.md`
- optional beat map

### 6.4 Asset Pipeline
**Purpose:** collect/generate/organize source assets.

**Outputs:**
- downloaded assets in `assets/`
- updated `asset-manifest.json`

### 6.5 Edit Planning Pipeline
**Purpose:** convert script + assets + style config into a machine-readable edit plan.

**Outputs:**
- `edit-plan.json`
- optional shot/scene metadata

### 6.6 Render Pipeline
**Purpose:** build and render video using Remotion.

**Outputs:**
- final rendered video
- preview render if needed
- render logs
- output metadata

### 6.7 Archive Pipeline
**Purpose:** archive completed project into MinIO.

**Outputs:**
- full project folder uploaded to MinIO
- archive metadata stored in Postgres

### 6.8 Index Pipeline
**Purpose:** create searchable embeddings and metadata entries after archive.

**Outputs:**
- vectors in Qdrant
- asset and project metadata in Postgres

---

## 7. Human-in-the-Loop Workflow

### 7.1 Approval Stages
Suggested statuses:
- `idea_submitted`
- `needs_review`
- `approved_for_research`
- `research_complete`
- `approved_for_production`
- `rendering`
- `needs_revision`
- `complete`
- `archived`
- `indexed`

### 7.2 Operator Actions
From the GUI, operator should be able to:
- approve
- reject
- send back for more work
- trigger next pipeline
- review script/assets/edit plan
- view render status
- archive/index completed projects

---

## 8. GUI / Control Center Requirements

### 8.1 Main Dashboard
Should show:
- projects needing approval
- current pipeline state
- failed jobs
- recently completed videos
- archive/index state

### 8.2 Project Detail View
Should open as a full-page detail view with tabs or sections for:
- overview
- research
- script
- assets
- edit plan
- render output
- archive/index status
- logs

### 8.3 Settings View
Should allow secure management of:
- provider assignments per task
- default model selections
- feature toggles
- API endpoints/base URLs
- non-secret workflow settings

---

## 9. Airtable Role

### Option A — Keep Airtable
Use Airtable as:
- idea database
- lightweight backend for status tracking
- optional interface layer for early operations

Use the custom GUI as the better operator frontend.

### Option B — Phase Airtable Out Later
Once the local app is mature, move all state to Postgres and let Airtable become optional.

### Recommendation
Keep Airtable initially if it is already part of the workflow, but build the custom GUI as the primary operator experience.

---

## 10. Remotion Role
Remotion should be treated as the rendering engine, not the main app.

### Recommended Setup
- a dedicated Remotion render worker/container
- backend app submits render jobs
- worker reads project files and renders output
- result is saved locally, then archived to MinIO

Claude Code should not be the unattended production runtime for rendering.

---

## 11. n8n Role
n8n should be optional and limited.

Use n8n only for:
- event triggers
- simple routing
- notifications
- kicking off workers

Do not put core business logic or long-term workflow complexity inside n8n.

---

## 12. Data Storage Responsibilities

### 12.1 MinIO
Use for:
- full archived project folders
- final renders
- source assets
- generated assets
- packaged manifests

### 12.2 Postgres
Use for:
- project records
- statuses
- job tracking
- logs
- configuration
- provider/model mappings
- archive references
- searchable metadata

### 12.3 Qdrant
Use for semantic search over:
- final video transcript/summary
- source video assets
- source image assets
- optionally final rendered video description/metadata

---

## 13. Indexing Strategy
Index after project completion and archive.

### Recommended Items to Vectorize
- final transcript/script
- raw source image assets
- raw source video assets
- final video summary/transcript

### Optional Metadata per Indexed Item
- project_id
- asset_id
- asset_type
- title
- channel/style
- tags
- source path in MinIO
- local path
- duration
- frame/time references where relevant

---

## 14. Configuration & Secrets

### 14.1 Secrets
Secrets should not be hardcoded.

Use:
- `.env` for local development
- Docker secrets for more secure containerized deployment

### 14.2 Dynamic Provider Configuration
Model/provider settings should be editable without changing pipeline code.

Store configurable selections in Postgres or config files, such as:
- research provider
- script provider
- render helper provider
- default model per task
- provider base URLs / versions

### 14.3 Rule
Pipelines should always call a config lookup function such as:
- `getProviderForTask("research")`
- `getModelForTask("script")`

Never hardcode provider/model names directly into pipeline logic.

---

## 15. Suggested Provider Routing
Example only; can change later:
- **Research / web intelligence / SEO analysis:** Perplexity
- **Scriptwriting / planning / structured creative reasoning:** Claude or other selected provider
- **Editing logic / code generation / pipeline help:** Claude-assisted during development, local app in production
- **Embeddings:** dedicated embedding model/service of choice

This should remain configurable via the GUI control center.

---

## 16. Initial MVP Scope

### 16.1 Must-Have
- local GUI dashboard
- project list + approval flow
- project detail page
- Postgres project/job storage
- local project folder creation
- research pipeline
- script pipeline
- asset manifest pipeline
- Remotion render worker
- archive to MinIO
- index to Qdrant
- config/settings page

### 16.2 Nice-to-Have Later
- role-based auth
- automated retries
- per-style analytics
- thumbnail generation
- shot-level indexing
- automated SEO scoring
- notifications
- batch jobs

---

## 17. Recommended Build Order
1. Define project folder schema.
2. Build Postgres schema for projects/jobs/settings.
3. Build GUI dashboard and project detail view.
4. Implement intake + approval workflow.
5. Implement research pipeline.
6. Implement script pipeline.
7. Implement asset pipeline.
8. Implement Remotion render worker.
9. Implement archive to MinIO.
10. Implement indexing to Qdrant.
11. Add settings GUI for providers/models/secrets handling.
12. Optionally connect Airtable and/or n8n.

---

## 18. Open Questions to Resolve During Build
- Will Airtable remain the main source of truth, or only an intake layer?
- Will styles be stored in JSON, database tables, or markdown prompt packs?
- How much of asset sourcing will be automated vs manually approved?
- What transcript extraction method will be used for final videos?
- What embedding model will be used for image/video/text indexing?
- How will failed renders and retries be handled?
- What exact metadata schema is needed for search and reuse?

---

## 19. Final Recommendation
Build a **single modular production system** with:
- one custom GUI/control center
- one backend/controller
- modular code pipelines/workers
- Remotion as a render worker
- MinIO for archive
- Postgres for metadata/config/state
- Qdrant for semantic indexing
- Airtable optional as backend intake/source of truth in early versions
- n8n optional as trigger glue only

Keep style logic configurable and reusable.
Keep each project self-contained.
Keep production and indexing separate.

