# Gemini Agent Instructions — Agent-OS Workspace

> **For:** Gemini CLI agents operating in this workspace.
> **Claude Code users:** See `CLAUDE.md`. **Codex users:** See `AGENTS.md`.

This workspace is Tony's operating system for all business operations. The same rules apply across all agents — same brain, same procedures.

> [!NOTE]
> **Legacy Workspace Rename:** The workspace was formerly called `Claude-Agent` (or jokingly `clogged-agent`). Any IDE configs, startup URIs, or CLI integrations that still advertise `/Users/tonymacbook2025/Documents/Claude-Agent` must always be translated to `/Users/tonymacbook2025/Documents/Agent-OS/` on startup.



## Start Here

1. Read `001_Architecture/Install_Maps/Workspace-Map.md` — full folder map with explanations
2. Read `001_Architecture/Install_Maps/System-Map.md` — installed apps, CLIs, Homebrew packages, npm globals, MCPs, scripts, skills, and local tool paths
3. Read `001_Architecture/Memory/Core_Memory.md` — tiny always-read memory
4. Read `001_Architecture/Memory/Memory_Index.md` — routing layer for relevant memory
5. Read `TOOLBOX.md` before writing scripts or installing tools

Do not load every memory or log file by default. Use `claude-mem` for relevant memory injection/search, then targeted file reads based on `Memory_Index.md`.

## Skills Registry

- The canonical skill library lives in `001_Architecture/Skills/`.
- Read `001_Architecture/Skills/Skill-Index.md` first when choosing a skill.
- Then open the matching `SKILL.md` file before using that skill.
- `001_Architecture/Scripts/sync_skill_index.py` regenerates the index when skills change.

## Dynamic Memory — Claude-Mem

`claude-mem` is installed for Gemini CLI and injects relevant context through `~/.gemini/GEMINI.md`.

- Worker status: `npx claude-mem status`
- Start worker: `npx claude-mem start`
- Viewer: `http://localhost:37701`
- Hooks live in `~/.gemini/settings.json`
- Use `<private>...</private>` tags for sensitive material that should not be stored.

Markdown memory should stay small and curated:
- `Core_Memory.md` — always-read bootstrap facts
- `Memory_Index.md` — memory routing
- `Global_Agent_Memory.md` — stable cross-agent decisions only
- `Logs/` and `Feedback_Loop/` — historical records, read only when relevant

## Session Memory — Write Automatically

Capture knowledge without being asked when Tony gives feedback, reveals preferences, validates an approach, or asks to wrap/save a session.

- Corrections and preferences → `001_Architecture/Feedback_Loop/YYYY-MM-DD_Feedback.md`
- Significant actions and files touched → `001_Architecture/Logs/YYYY-MM-DD_Session-Log.md`
- Durable cross-agent decisions → `001_Architecture/Memory/Global_Agent_Memory.md`
- Patterns after meaningful work → `001_Architecture/Self_Learning_Loop/YYYY-MM-DD_Self-Review.md`
- ALWAYS update all Workspace Maps, System Maps, TOOLBOX.md, and directory definitions to include any new folders, scripts, skills, or configurations before closing out a session.

Let `claude-mem` handle episodic memory. Do not turn markdown memory into a transcript.

## Ingest Procedure

When Tony says "ingest" or files are in `000_Ingest/`, follow the procedure in `AGENTS.md` exactly. The steps are identical for all agents.

**Recurse into all subfolders by default** unless told otherwise.

**Media rule:** When ingesting images (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.svg`) or word docs (`.docx`, `.doc`):

1. **Lookup-first gate** — run before any vision call:
   ```bash
   python /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/check_vision_needed.py "/path/to/images"
   ```
   Files with real Asset Note descriptions → skip vision, proceed to routing.
   Files with filler descriptions or no note → continue to vision.

2. **Vision** — for flagged files only: use your multimodal capabilities (Gemini has native vision) to analyze the image, generate a descriptive kebab-case filename, and create a proper Asset Note in `007_Resource_Library/Asset_Notes/`. A good Asset Note includes the specific subject, platform (TikTok, Instagram, GitHub, etc.), key text/data visible, and business relevance to Tony's workflow.

PDFs go to `007_Resource_Library/Docs/` with no companion file (Obsidian can display them natively).

**Notion exports:** Skip top-level database container `.md` files; ingest individual record files normally.

Full flow: Classify → (If media: Analyze & Rename) → Add YAML or Create Asset Note → Route to `007_Resource_Library/` → Create wiki page in `000_Wiki/` (text only) → Cross-link → Update log + index → Run `graphify update .` for code-bearing domains, and use the interactive `/graphify <domain> --update` flow for docs-only wiki-heavy domains.
Do not graphify `000_Ingest/`; it is a temporary staging area and only becomes graph targets after ingest routes files into durable folders.

## File Naming

No spaces. Title-Case-With-Dashes.md. Acronyms uppercase. Python scripts exempt.

## Full Instructions

See `AGENTS.md` for the complete procedure. This file is a Gemini-focused bootstrap, with memory behavior mirrored from Claude and Codex.
