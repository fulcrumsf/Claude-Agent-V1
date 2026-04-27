# CLAUDE.md — AI Character Builder

## Vault Access

Before starting work: Read `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/000_VAULT-INDEX.md`

This department's knowledge is organized in the vault under:
- Skills: `/Obsidian-Vault/000_Skills/` (shared development and design workflows)
- Tools: `/Obsidian-Vault/003_Tools/` (Gemini API documentation, model capabilities)

**Vault-first rule:** Search the vault for context before asking the user. If you need clarification, ask a focused question instead of requesting extensive background.

---

## What This Is
A tool that takes a single full-body character image as input and generates 3–4 consistent views of that character from different angles. Built with Google Gemini (AI Studio) and packaged as a Docker container. The core mission is **character consistency** — same face, same clothes, same style across all generated views.

Its primary purpose is to produce animation-ready character sheets for use in AI-generated animated stories.

---

## How It Works
1. User imports a full-body character image
2. The app sends the image + a generation prompt to the Gemini API
3. Gemini returns 3–4 angle variations (front, side, back, 3/4 view)
4. Output is used downstream in animated story production

---

## Key Capabilities (Presets)

### Background
- Solid color (any hex/color name)
- Environment scenes: snowing, raining, cyberpunk, forest, desert, etc.

### Character Outfit
- Change clothing style while preserving character identity

### Pose
- Static: standing, sitting
- Action: running, jumping, kicking, punching, etc.

---

## Tech Stack
- **AI Model:** Google Gemini (via AI Studio API)
- **Frontend:** React + TypeScript (`.tsx` files)
- **Containerization:** Docker (multi-stage build — Node.js builder → nginx:alpine server)
- **Port:** `8081` (mapped from container port 80)
- **API Key Handling:** Runtime injection via `entrypoint.sh` using `__GEMINI_API_KEY__` placeholder — key sourced from `.env` file, never hardcoded

---

## File Structure
```
AI Character Builder/
├── CLAUDE.md                  ← This file
├── Dockerfile                 ← Multi-stage build (builder + nginx)
├── docker-compose.yml         ← Service definition, port 8081
├── entrypoint.sh              ← Injects GEMINI_API_KEY at container start
├── .env                       ← Secret API key (never commit to Git)
├── index.html                 ← App entry point
└── services/
    └── geminiService.ts       ← Gemini API calls, uses __GEMINI_API_KEY__ placeholder
```

---

## Running the App
```bash
# Start (builds image if needed)
docker compose up --build -d

# Access at:
http://localhost:8081

# Stop
docker compose down
```

---

## Agent Priorities
1. **Preserve character consistency** — any change to generation prompts must maintain face/body identity across angles
2. **Keep Docker setup working** — API key injection pattern must survive rebuilds
3. **Extend presets thoughtfully** — new backgrounds/poses should follow the existing preset pattern
4. **Do not break the angle pipeline** — the 3–4 view output is the core deliverable

---

## Current Status
Tool is functional. Potential future work:
- Add more pose presets
- Add style transfer options (anime, realistic, cartoon)
- Pipe output directly into the Video Editor animation pipeline
- Explore consistency improvements with newer Gemini models
