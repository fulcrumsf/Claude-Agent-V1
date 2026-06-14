# 001_Architecture Directory

This directory is the **unified brain** and **single source of truth** for all agents operating within this workspace (Claude Code, Antigravity, Gemini CLI, Codex, etc.). 

> **AGENT INSTRUCTION:** NEVER write new skills, scripts, or configurations to your local hidden folders (e.g., `~/.claude/`, `~/.gemini/`, `.agents/`). Always use the standardized folders below. The local agent folders are symlinked directly to this directory.

## Folder Layout & Descriptions

*   **Automation:** Reserved for exporting and studying `n8n` workflow JSONs. These workflows are analyzed here before being deployed into isolated Docker containers for uninterrupted, background execution.
*   **Feedback_Loop:** Contains daily learning logs where agents record Tony's preferences, corrections, and successful approaches to avoid repeating mistakes.
*   **Graphify:** Configuration and output for the workspace graphing/mapping system.
*   **Install_Maps:** Holds `System-Map.md` (the registry of all installed tools/apps) and `Workspace-Map.md` (the overarching folder layout).
*   **Logs:** Compact daily session records showing what work was done, decisions made, and files modified.
*   **Memory:** The core routing system for agent context, including `Core_Memory.md` and `Global_Agent_Memory.md`.
*   **Scripts:** The global repository for all Python automation and helper scripts. Any script written to assist the user or an agent must be placed here.
*   **Self_Learning_Loop:** Periodic review documents where agents synthesize patterns from recent sessions to improve future performance.
*   **Skills:** The global repository for all AI agent capabilities. Whether you are Codex, Gemini, or Claude, any new skill (e.g., `gsd-plan-phase`, `video-ingest`) must be saved here. 
*   **Tools:** Configuration files and settings for specific tool categories. 
    *   *Subfolders include:* `Image-Generation` and `Video-Generation` (used for API configurations like fal.ai and kie.ai). Also holds UI modifications (e.g., custom CSS for Antigravity).

*(Note: If a new global capability is needed that doesn't fit these definitions, explicitly ask Tony before creating a new top-level folder in 001_Architecture.)*
