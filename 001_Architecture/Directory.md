# 001_Architecture Directory

This directory is the **unified brain** and **single source of truth** for all agents operating within this workspace (Claude Code, Antigravity, Gemini CLI, Codex, etc.). 

> **AGENT INSTRUCTION:** NEVER write new skills, scripts, or configurations to your local hidden folders (e.g., `~/.claude/`, `~/.gemini/`, `.agents/`). Always use the standardized folders below. The local agent folders are symlinked directly to this directory.

## Folder Layout & Descriptions

*   **Automation:** Reserved for exporting and studying `n8n` workflow JSONs. These workflows are analyzed here before being deployed into isolated Docker containers for uninterrupted, background execution.
*   **Audit_Reports:** Architecture audits, reusable audit prompts, and system review reports. Use this for inspection-only analysis of Agent-OS structure, context efficiency, memory systems, toolchains, and cross-agent operating rules.
*   **Feedback_Loop:** Contains daily learning logs where agents record Tony's preferences, corrections, and successful approaches to avoid repeating mistakes.
*   **Graphify:** Configuration and output for the workspace graphing/mapping system.
*   **Install_Maps:** Holds `System-Map.md` (the registry of all installed tools/apps) and `Workspace-Map.md` (the overarching folder layout).
*   **Logs:** Compact daily session records showing what work was done, decisions made, and files modified.
*   **Memory:** The core routing system for agent context, including `Core_Memory.md` and `Global_Agent_Memory.md`.
*   **Scripts:** The global repository for all Python automation and helper scripts. Any script written to assist the user or an agent must be placed here.
*   **Self_Learning_Loop:** Periodic review documents where agents synthesize patterns from recent sessions to improve future performance.
*   **Skills:** The global repository for all AI agent capabilities. Whether you are Codex, Gemini, or Claude, any new skill (e.g., `gsd-plan-phase`, `video-ingest`) must be saved here. 
*   **Tools:** All Python tools, scripts, and configurations organized by capability. Think of this as the OS toolchain — every tool lives here, not scattered across content folders.
    *   *Subfolders include:* `AI-Analysis/`, `Airtable/`, `Asset-Sourcing/`, `Image-Generation/`, `Remotion/`, `Text-To-Speech/`, `Tool-Manager/`, `Video-Generation/`
    *   `Video-Generation/` further contains: `Channels/` (per-channel scripts: Anomalous_Wild, Reimagined_Realms), `Generic_Tools/` (reusable batch scripts), `Pipeline_Docs/`, `Hyperframes/`, `Video-Use/`

*(Note: If a new global capability is needed that doesn't fit these definitions, explicitly ask Tony before creating a new top-level folder in 001_Architecture.)*
