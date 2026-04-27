# Video Editor Project

This project automates the orchestration and generation of video content using AI tools (Google Veo/Kling via Kie.ai API, TTS models, etc.) and programmatic rendering via Remotion.

## Directory Structure
```
001_Configuration/        ← API keys (.env), config files, project settings
002_Channels/             ← All channel data, bibles, video projects, case studies
  001_Anomalous-Wild/
    001_Bioluminescence-Weapon/     ← Self-contained video project
    002_End-Card/
  002_Neon-Parcel/ ... 012_Business-Origin-Stories/
  Docs/                   ← Shared API stack reference, storytelling guides
  Styles/                 ← Cinematic style templates and reference frames
003_Remotion/             ← Video composition (Next.js + React)
004_Tools/                ← Orchestration scripts, pipeline supervisor
```

**Note:** All universal scripts (TTS, image gen, video gen, FCPXML export) live in Obsidian Vault under `/Obsidian-Vault/003_Tools/`

## Running the Pipeline
Entry points are bash scripts in `004_Tools/`:
- `004_Tools/generate_all.sh` - Generates audio and video for scenes
- `004_Tools/generate_remainder.sh` - Generate remaining clips
- `004_Tools/generate_last.sh` - Generate last batch
- `004_Tools/pipeline_orchestrator.sh` - Full pipeline (stages 1-6)

All scripts reference vault-based Python tools and updated folder paths.

## Python Environment
Dependencies are listed in `requirements.txt`. Use Python 3.13+ as specified in bash scripts.

## Configuration
- API keys: `001_Configuration/.env`
- Pyright config: `001_Configuration/pyrightconfig.json`
- MCP settings: `001_Configuration/.mcp.json`
