---
title: "Video Production System — Technical PDR V2"
type: spec
domain: video-production
tags: [spec, video-production, workflow-automation, remotion]
---

# Video Production System — Technical PDR V2

## 1. Objective
Build a local-first, modular video production platform that supports idea intake, approval, research, scripting, asset gathering, edit planning, Remotion rendering, archiving to MinIO, and semantic indexing in Qdrant.

The system should:
- support multiple channels and styles from one codebase
- separate operator UX from automation/runtime
- avoid using Claude Code as the unattended production runtime
- support dynamic model/provider routing per task
- preserve each project as a self-contained package
- allow human approval at key checkpoints

---

## 2. System Principles

### 2.1 Core Principles
1. **One codebase, modular workers**
2. **File-based project handoff plus database state tracking**
3. **Human approval before expensive or irreversible steps**
4. **Styles as configuration, not separate apps**
5. **Archive and indexing separated from production**
6. **Secrets and provider settings centrally managed**

### 2.2 Non-Goals for MVP
- full autonomous publishing to YouTube
- full DAM replacement
- advanced multi-user RBAC
- custom GPU orchestration beyond a single render worker/container

---

## 3. High-Level Architecture

```text
[Airtable Optional]      [Operator GUI]
        |                     |
        +----------> [Backend API / Controller] <----------+
                              |                             |
                              v                             |
                        [Postgres State]                    |
                              |                             |
                +-------------+-------------+               |
                |             |             |               |
                v             v             v               |
       [Research Worker] [Asset Worker] [Script Worker]    |
                |             |             |               |
                +-------------+-------------+               |
                              v                             |
                       [Project Folder]                     |
                              |                             |
                              v                             |
                     [Edit Plan Worker]                     |
                              |                             |
                              v                             |
                      [Remotion Render Worker]              |
                              |                             |
                              v                             |
                  [Archive Worker -> MinIO]                |
                              |                             |
                              v                             |
                 [Index Worker -> Qdrant + Postgres] ------+
```

---

## 4. Core Services

## 4.1 Operator GUI
Purpose:
- review ideas and projects
- approve/reject/send back
- inspect research/script/assets/output
- manage provider/model config
- view logs and pipeline status

Recommended stack:
- Next.js or React frontend
- local auth for MVP
- talks to backend API only

## 4.2 Backend API / Controller
Purpose:
- source of orchestration logic
- validate transitions between states
- enqueue jobs
- expose project/settings/job APIs
- aggregate logs and job status

Recommended stack:
- Node.js with TypeScript or Python FastAPI
- queue integration for workers

## 4.3 Worker Services
Recommended workers:
- `research-worker`
- `script-worker`
- `asset-worker`
- `edit-plan-worker`
- `render-worker`
- `archive-worker`
- `index-worker`

Each worker:
- accepts a `job_id` or `project_id`
- reads config from backend/database
- reads/writes project files
- writes structured status/log updates
- is independently restartable

## 4.4 Storage and Search
- **Postgres**: metadata, jobs, config, logs, status, provider routing
- **MinIO**: archived project bundles and final outputs
- **Qdrant**: embeddings and semantic retrieval
- **Local filesystem**: active/in-progress project workspace

---

## 5. Recommended Repository Layout

```text
video-system/
  app/
    api/
    controller/
    services/
    ui/
  workers/
    research/
    script/
    assets/
    edit-plan/
    render/
    archive/
    index/
  remotion/
    src/
      compositions/
      templates/
      components/
    package.json
  config/
    providers.json
    styles/
      docu-collage.json
      map-explainer.json
      commentary-facts.json
  shared/
    schemas/
    types/
    utils/
  projects/
    project-001/
      brief.md
      research.json
      script.md
      asset-manifest.json
      edit-plan.json
      render-config.json
      project-metadata.json
      logs/
      output/
      assets/
        images/
        video/
        audio/
        generated/
        temp/
  docker/
  scripts/
  .env
  docker-compose.yml
```

---

## 6. Project Package Contract

Each project folder is the local working package for a single video.

## 6.1 Required Files
- `brief.md`
- `project-metadata.json`
- `research.json`
- `script.md`
- `asset-manifest.json`
- `edit-plan.json`
- `render-config.json`

## 6.2 Optional Files
- `sources.md`
- `transcript.vtt`
- `transcript.txt`
- `summary.md`
- `thumbnail-plan.json`
- `qa-report.json`

## 6.3 Required Directories
- `assets/images/`
- `assets/video/`
- `assets/audio/`
- `assets/generated/`
- `assets/temp/`
- `output/`
- `logs/`

## 6.4 Rules
- all downstream file references should be relative to the project root
- no external URL should be required by the render worker once the asset pipeline is complete
- all generated assets should be versionable and stored in project-local folders
- archived copies in MinIO must preserve the folder structure

---

## 7. Database Design (Postgres)

## 7.1 Main Tables

### `projects`
Primary project record.

Suggested columns:
- `id` UUID PK
- `slug` text unique
- `title` text
- `channel_id` UUID nullable
- `style_id` text
- `status` text
- `priority` int default 0
- `source_system` text
- `source_record_id` text nullable
- `brief_markdown` text nullable
- `local_project_path` text
- `minio_archive_path` text nullable
- `created_at` timestamptz
- `updated_at` timestamptz
- `approved_at` timestamptz nullable
- `completed_at` timestamptz nullable
- `archived_at` timestamptz nullable

### `project_status_history`
Audit trail of state changes.

Columns:
- `id` UUID PK
- `project_id` UUID FK
- `from_status` text nullable
- `to_status` text
- `changed_by` text
- `reason` text nullable
- `created_at` timestamptz

### `jobs`
Queue-visible work item table.

Columns:
- `id` UUID PK
- `project_id` UUID FK
- `job_type` text
- `status` text
- `attempt_count` int default 0
- `worker_name` text nullable
- `payload_json` jsonb
- `result_json` jsonb nullable
- `error_text` text nullable
- `started_at` timestamptz nullable
- `finished_at` timestamptz nullable
- `created_at` timestamptz

### `assets`
Metadata for project assets.

Columns:
- `id` UUID PK
- `project_id` UUID FK
- `asset_key` text
- `asset_type` text
- `role` text
- `status` text
- `title` text nullable
- `description` text nullable
- `source_url` text nullable
- `local_path` text nullable
- `minio_path` text nullable
- `mime_type` text nullable
- `width` int nullable
- `height` int nullable
- `duration_ms` int nullable
- `checksum` text nullable
- `metadata_json` jsonb default '{}'
- `created_at` timestamptz
- `updated_at` timestamptz

### `project_outputs`
Final and intermediate outputs.

Columns:
- `id` UUID PK
- `project_id` UUID FK
- `output_type` text
- `local_path` text nullable
- `minio_path` text nullable
- `metadata_json` jsonb
- `created_at` timestamptz

### `provider_configs`
Maps tasks to providers/models.

Columns:
- `id` UUID PK
- `task_name` text unique
- `provider_name` text
- `model_name` text
- `base_url` text nullable
- `timeout_seconds` int default 120
- `enabled` boolean default true
- `extra_json` jsonb default '{}'
- `updated_at` timestamptz

### `secrets_registry`
Metadata only, not secret values.

Columns:
- `id` UUID PK
- `secret_name` text unique
- `provider_name` text
- `storage_backend` text
- `description` text nullable
- `last_rotated_at` timestamptz nullable
- `updated_at` timestamptz

### `channels`
Optional multi-channel configuration.

Columns:
- `id` UUID PK
- `name` text
- `slug` text unique
- `default_style_id` text nullable
- `settings_json` jsonb default '{}'

### `styles`
Optional DB-backed style records.

Columns:
- `id` text PK
- `name` text
- `description` text
- `config_json` jsonb
- `updated_at` timestamptz

### `embeddings_index_items`
Index registry for Qdrant references.

Columns:
- `id` UUID PK
- `project_id` UUID FK
- `asset_id` UUID nullable FK
- `item_type` text
- `qdrant_point_id` text
- `collection_name` text
- `text_preview` text nullable
- `minio_path` text nullable
- `metadata_json` jsonb
- `created_at` timestamptz

---

## 8. Suggested Status Model

Recommended `projects.status` values:
- `idea_submitted`
- `needs_review`
- `approved_for_research`
- `research_running`
- `research_complete`
- `approved_for_script`
- `script_running`
- `script_complete`
- `approved_for_assets`
- `assets_running`
- `assets_complete`
- `approved_for_edit_plan`
- `edit_plan_running`
- `edit_plan_complete`
- `approved_for_render`
- `render_running`
- `render_complete`
- `needs_revision`
- `approved_for_archive`
- `archive_running`
- `archived`
- `index_running`
- `indexed`
- `failed`
- `cancelled`

MVP simplification:
- merge approvals if desired into fewer checkpoints

---

## 9. API Design

## 9.1 Project APIs
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/:id`
- `PATCH /api/projects/:id`
- `POST /api/projects/:id/approve`
- `POST /api/projects/:id/reject`
- `POST /api/projects/:id/request-changes`
- `GET /api/projects/:id/files`
- `GET /api/projects/:id/logs`

## 9.2 Job APIs
- `POST /api/projects/:id/jobs/research`
- `POST /api/projects/:id/jobs/script`
- `POST /api/projects/:id/jobs/assets`
- `POST /api/projects/:id/jobs/edit-plan`
- `POST /api/projects/:id/jobs/render`
- `POST /api/projects/:id/jobs/archive`
- `POST /api/projects/:id/jobs/index`
- `GET /api/jobs/:id`
- `POST /api/jobs/:id/retry`
- `POST /api/jobs/:id/cancel`

## 9.3 Settings APIs
- `GET /api/settings/providers`
- `PATCH /api/settings/providers/:task_name`
- `GET /api/settings/secrets`
- `POST /api/settings/secrets/test-connection`
- `GET /api/settings/styles`
- `PATCH /api/settings/styles/:id`

## 9.4 Search APIs
- `GET /api/search?q=...`
- `GET /api/search/assets?q=...`
- `GET /api/search/projects?q=...`

## 9.5 Airtable Sync APIs
If Airtable remains in the loop:
- `POST /api/integrations/airtable/sync-record/:record_id`
- `POST /api/integrations/airtable/push-status/:project_id`

---

## 10. Worker and Pipeline Design

A code pipeline is a set of worker steps implemented in code and driven by structured inputs/outputs.

## 10.1 Intake Pipeline
Trigger sources:
- operator UI
- Airtable record creation/update
- manual API call

Steps:
1. validate input
2. generate project slug
3. create local project folder
4. create base files
5. insert project record in Postgres
6. optionally sync back to Airtable

Outputs:
- `brief.md`
- `project-metadata.json`
- `projects` row

## 10.2 Research Pipeline
Inputs:
- project metadata
- brief
- provider config for research
- optional SEO analytics payload

Steps:
1. read brief and style/channel context
2. query research provider(s)
3. normalize findings
4. identify claims and sources
5. identify visual opportunities
6. write research outputs
7. update job/project status

Outputs:
- `research.json`
- optional `sources.md`

## 10.3 Script Pipeline
Inputs:
- `research.json`
- style config
- provider config for scriptwriting

Steps:
1. read research package
2. produce beat outline
3. produce narration/script draft
4. write structured script package
5. update status

Outputs:
- `script.md`
- optional `script.json`

## 10.4 Asset Pipeline
Inputs:
- `research.json`
- `script.md`
- visual opportunities
- style config

Steps:
1. derive required asset list
2. fetch/download/source assets
3. store assets under project folder
4. enrich metadata
5. update asset manifest
6. optionally generate derived assets

Outputs:
- `asset-manifest.json`
- populated `assets/` folders
- rows in `assets` table

## 10.5 Edit Plan Pipeline
Inputs:
- script
- asset manifest
- style config
- optional target duration

Steps:
1. segment script into scenes
2. assign assets to scenes
3. assign templates/transitions
4. assign timing and overlays
5. write machine-readable plan

Outputs:
- `edit-plan.json`
- `render-config.json`

## 10.6 Render Pipeline
Inputs:
- `edit-plan.json`
- `render-config.json`
- Remotion project
- local assets

Steps:
1. validate assets exist locally
2. generate any final derived media if needed
3. call Remotion render process
4. write output video(s)
5. capture logs and metadata
6. update project outputs and status

Outputs:
- `output/final.mp4`
- optional `output/preview.mp4`
- render metadata row(s)

## 10.7 Archive Pipeline
Inputs:
- completed project folder
- MinIO config

Steps:
1. verify project completeness
2. upload package recursively to MinIO
3. write archive paths
4. mark archived

Outputs:
- MinIO folder path
- archive metadata in Postgres

## 10.8 Index Pipeline
Inputs:
- archived project path
- final outputs
- transcript/script
- raw image/video assets

Steps:
1. prepare text and media indexing tasks
2. create embeddings for text/image/video assets
3. upsert into Qdrant
4. write index registry rows
5. mark indexed

Outputs:
- Qdrant points
- `embeddings_index_items` rows

---

## 11. Suggested File Schemas

## 11.1 `project-metadata.json`
```json
{
  "project_id": "uuid",
  "slug": "video-001",
  "title": "Example Title",
  "channel": "channel-a",
  "style_id": "docu-collage",
  "status": "approved_for_research",
  "created_at": "2026-03-25T00:00:00Z"
}
```

## 11.2 `research.json`
```json
{
  "topic": "Example topic",
  "angle": "What the video is trying to prove or explain",
  "key_facts": [
    {
      "claim": "Example factual claim",
      "source_url": "https://example.com",
      "confidence": "high"
    }
  ],
  "timeline": [
    {
      "date": "2025-01-01",
      "event": "Example event",
      "source_url": "https://example.com"
    }
  ],
  "visual_opportunities": [
    {
      "beat_id": "beat_01",
      "description": "Map zoom from X to Y",
      "suggested_asset_types": ["map", "headline", "archive_photo"]
    }
  ]
}
```

## 11.3 `asset-manifest.json`
```json
{
  "project_id": "uuid",
  "assets": [
    {
      "asset_key": "headline_01",
      "asset_type": "image",
      "role": "source",
      "status": "collected",
      "title": "Headline clipping",
      "source_url": "https://example.com/file.png",
      "local_path": "assets/images/headline_01.png",
      "scene_refs": ["scene_01"],
      "metadata": {
        "width": 1920,
        "height": 1080
      }
    }
  ]
}
```

## 11.4 `edit-plan.json`
```json
{
  "project_id": "uuid",
  "style_id": "docu-collage",
  "runtime_seconds": 90,
  "scenes": [
    {
      "scene_id": "scene_01",
      "duration_seconds": 4.5,
      "template": "HeadlineStackSequence",
      "narration": "Opening narration line",
      "assets": ["headline_01"],
      "transition_in": "paper_tear",
      "transition_out": "map_zoom"
    }
  ]
}
```

## 11.5 `render-config.json`
```json
{
  "composition_id": "MainComposition",
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "output_file": "output/final.mp4",
  "props_file": "edit-plan.json"
}
```

---

## 12. Style System Design

Styles should be configs plus optional prompt packs.

## 12.1 Recommended Style Config Fields
- `style_id`
- `name`
- `description`
- `tone`
- `asset_preferences`
- `transition_preferences`
- `text_treatment`
- `scene_templates`
- `pacing`
- `audio_notes`
- `research_notes`

## 12.2 Example Style File
```json
{
  "style_id": "docu-collage",
  "name": "Documentary Collage",
  "tone": ["analytical", "textured", "fast-moving"],
  "asset_preferences": ["maps", "newspapers", "archive photos", "charts"],
  "transition_preferences": ["paper_tear", "collage_slide", "zoom_cut"],
  "scene_templates": ["HeadlineStackSequence", "MapSequence", "FactCardSequence"],
  "pacing": {
    "average_shot_seconds": 2.8,
    "overlay_density": "high"
  }
}
```

---

## 13. Secrets and Dynamic Configuration

## 13.1 Secret Handling
Use:
- `.env` for local development
- Docker secrets for containerized production-like deployment

Secret examples:
- `AIRTABLE_API_KEY`
- `ANTHROPIC_API_KEY`
- `PERPLEXITY_API_KEY`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `QDRANT_API_KEY`

## 13.2 Config Layer
Keep mutable config out of worker logic.

Recommended config groups:
- provider routing by task
- model defaults by task
- base URLs and API versions
- timeout/retry settings
- feature flags

## 13.3 GUI Control Center Requirements
The settings UI should allow:
- selecting provider per task
- selecting model per task
- editing provider base URLs
- testing credentials/connectivity
- enabling/disabling providers
- viewing last successful connection status

## 13.4 Important Rule
Workers should always call config lookup functions such as:
- `getProviderForTask("research")`
- `getModelForTask("script")`
- `getSecret("perplexity")`

Workers should never hardcode provider or model names directly.

---

## 14. Queueing and Job Execution

Recommended queue options:
- BullMQ with Redis if using Node
- Celery/RQ if using Python
- Postgres-backed queue acceptable for MVP if simplicity is preferred

## 14.1 Minimum Job Fields
- job id
- project id
- job type
- payload
- status
- attempts
- worker lease/lock
- timestamps

## 14.2 Retry Rules
Suggested defaults:
- network/provider jobs: retry up to 3 times
- render jobs: retry once automatically, then manual review
- archive/index jobs: retry up to 3 times

## 14.3 Idempotency
Each worker should be idempotent where possible.
Examples:
- do not re-download identical assets if already present and checksummed
- do not create duplicate Qdrant entries without deterministic ids
- do not duplicate MinIO uploads without checking archive state

---

## 15. Remotion Integration Design

Remotion should run as a dedicated worker/container.

## 15.1 Render Worker Responsibilities
- read project package
- map `edit-plan.json` to Remotion props
- call Remotion render APIs or CLI
- save outputs locally
- capture logs and diagnostics

## 15.2 Recommended Remotion Separation
```text
remotion/
  src/
    compositions/
      MainComposition.tsx
    templates/
      HeadlineStackSequence.tsx
      MapSequence.tsx
      FactCardSequence.tsx
    components/
      TextOverlay.tsx
      ImageLayer.tsx
      TransitionLayer.tsx
```

## 15.3 Contract Between App and Remotion
Backend/render worker passes:
- composition id
- project path
- edit plan
- asset manifest
- output path
- render settings

Remotion returns:
- output file path
- duration/fps/size metadata
- success/failure
- logs

---

## 16. MinIO Archival Design

## 16.1 Archive Path Convention
Recommended:
```text
minio://video-archive/projects/{project_slug}/
```

Example internal layout preserved:
```text
projects/video-001/
  brief.md
  research.json
  script.md
  asset-manifest.json
  edit-plan.json
  output/final.mp4
  assets/images/...
```

## 16.2 Archive Metadata
Store in Postgres:
- bucket name
- object prefix
- archived_at
- archive checksum or manifest hash if used

---

## 17. Qdrant Indexing Design

## 17.1 Items to Index
Recommended MVP:
- final transcript or final script
- final video summary
- source images
- source video assets

Optional later:
- scene-level text chunks
- shot-level keyframes
- per-frame embeddings for selected assets

## 17.2 Suggested Collections
- `project_text`
- `project_images`
- `project_videos`

## 17.3 Metadata Payload Suggestions
- `project_id`
- `project_slug`
- `asset_id`
- `asset_type`
- `title`
- `channel`
- `style_id`
- `minio_path`
- `local_path`
- `duration_ms`
- `tags`
- `source_url`

---

## 18. Airtable Integration Strategy

Airtable should be optional and bounded.

## 18.1 Good Uses for Airtable
- idea intake
- operator review queue
- lightweight editorial planning
- external status visibility

## 18.2 What Airtable Should Not Do
- own deep pipeline logic
- replace job queueing
- replace file package storage
- replace archive/index/search layers

## 18.3 Suggested Sync Model
Airtable record fields:
- title
- brief
- channel
- style
- priority
- approval status
- linked project id
- linked output URL

Sync pattern:
- Airtable creates/updates idea
- backend syncs into project record
- backend pushes major status changes back to Airtable

---

## 19. GUI Pages and UX Requirements

## 19.1 Pages
- Login
- Dashboard
- Projects Queue
- Project Detail
- Jobs Monitor
- Search
- Settings

## 19.2 Dashboard Widgets
- needs approval
- in progress
- failed jobs
- recently rendered
- archived not indexed
- provider health

## 19.3 Project Detail Tabs
- Overview
- Research
- Script
- Assets
- Edit Plan
- Render Output
- Archive/Index
- Logs

## 19.4 Actions on Project Detail
- approve next stage
- request changes
- run pipeline
- retry failed job
- download package
- open final video
- archive now
- index now

---

## 20. Observability and Logging

## 20.1 Logging Requirements
Each worker should emit:
- start event
- milestone events
- warnings
- error details
- completion event

## 20.2 Storage
Store logs in:
- job logs in Postgres for operator access
- project-local log files for package completeness

## 20.3 Metrics to Track Later
- average stage duration
- provider failure rate
- render failure rate
- archive/index lag
- approval turnaround time

---

## 21. Security Notes

For MVP:
- local-only deployment acceptable
- password auth or local network auth acceptable

Later:
- RBAC
- audit logs
- secret rotation workflow
- encrypted backups for Postgres

Important:
- never expose raw secret values back through the frontend after creation
- only expose masked metadata and connection test results

---

## 22. Docker / Deployment Layout

Suggested services:
- `frontend`
- `backend`
- `postgres`
- `redis` optional
- `minio`
- `qdrant`
- `research-worker`
- `script-worker`
- `asset-worker`
- `edit-plan-worker`
- `render-worker`
- `archive-worker`
- `index-worker`

Optional:
- `n8n` only for trigger glue
- `airtable-mcp-adapter` if needed externally

---

## 23. Build Phases

## Phase 1: Foundation
- define project package schema
- create Postgres tables
- create backend API skeleton
- create local GUI shell
- implement intake and approval

## Phase 2: Core Production
- research worker
- script worker
- asset worker
- edit plan worker
- Remotion worker

## Phase 3: Archive and Search
- MinIO archive worker
- transcript/final summary generation
- Qdrant indexing worker
- search UI

## Phase 4: Operations and Flexibility
- provider/settings UI
- health checks
- retries and job controls
- Airtable sync polish
- style management UI

---

## 24. Recommended MVP Decisions

To reduce complexity, choose these defaults first:
- backend: Node.js + TypeScript
- frontend: Next.js
- queue: BullMQ + Redis
- render: dedicated Remotion worker container
- active workspace: local filesystem
- archive: MinIO
- metadata: Postgres
- vector search: Qdrant
- Airtable: optional intake + editorial queue only

If you prefer Python for workers, mixed architecture is acceptable, but do not split languages unless there is a clear reason.

---

## 25. Open Decisions to Resolve During Build
- exact queue framework
- whether provider configs live primarily in DB or config files
- whether styles are file-based or DB-editable from day one
- which embedding model handles image/video/text indexing
- transcript generation path for final renders
- whether asset ingestion is fully automated or semi-manual
- whether Airtable remains source of truth or only intake/UI support

---

## 26. Final Recommendation
Build a **single operator-facing app** with a **backend controller** and **modular worker pipelines**.

Keep these boundaries:
- **GUI** for humans
- **backend/controller** for orchestration and state
- **workers** for actual pipeline execution
- **project folders** for local working packages
- **MinIO** for archived packages
- **Postgres** for metadata, jobs, settings, and logs
- **Qdrant** for semantic search
- **Remotion** as a dedicated render engine behind the app
- **Airtable** only as an optional intake/editorial layer

This architecture gives you one system that can support all channels/styles without turning into one giant workflow or a pile of separate apps.
