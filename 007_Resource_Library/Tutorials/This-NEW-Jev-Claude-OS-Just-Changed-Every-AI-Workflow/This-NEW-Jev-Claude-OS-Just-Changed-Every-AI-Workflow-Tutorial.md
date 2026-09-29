---
title: "This NEW Jev + Claude OS Just Changed Every AI Workflow"
type: tutorial
category: ai-agents
tags:
  - jev
  - claude-code
  - codex
  - agentic-os
  - obsidian
  - model-routing
created: 2026-09-27
source: https://www.youtube.com/watch?v=EOdXR6lU5ZA
---

# This NEW Jev + Claude OS Just Changed Every AI Workflow

A comprehensive tutorial by Chase AI breaking down how to design, architect, and deploy a personal 3-layer **Agentic OS** (Claude OS / Codex OS). It integrates TypeSafe AI's **Jev** router, local voice models (Whisper + Kokoro), an Obsidian second-brain memory layer based on Andrej Karpathy's RAG architecture, and an automated skill backbone.

---

## 1. The 3-Layer Agentic OS Architecture

An Agentic OS is not just a visual dashboard; it is a unified operational system that sits around the user and orchestrates multiple AI runtimes (Claude Code, OpenAI Codex, GPT-4/6 Astra, Jev) outside the terminal.

```
+-------------------------------------------------------------------------+
|                         LAYER 1: VISUAL LAYER                           |
|  - Jarvis v2 Web HUD (127.0.0.1:3217) or Obsidian Native Desktop Plugin |
|  - Dual Runtime Engine: Claude Code <---> OpenAI Codex                  |
|  - System Vitals, Calendar, Directives, Skill Quick Triggers            |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  THE BRIDGE & LOCAL VOICE ROUTING                       |
|  - Ears: Whisper (Local STT)                                            |
|  - Voice: Kokoro (Local TTS with custom voice profiles)                 |
|  - Router: Jev Classifier (Typesafe AI)                                 |
+-------------------------------------------------------------------------+
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
          v                         v                         v
     [ TIER 1 ]                [ TIER 2 ]                [ TIER 3 ]
   Rules / Local Data       Small Fast Model           Real Work Agent
  - No AI, <1ms instant    - Haiku / Luna / Local    - Spawns Claude Code
  - Internal vault cmds    - "Quick news summary"       or Codex session
  - "Show my priorities"                            - Multi-step skills
                                                              |
                                                              v
+-------------------------------------------------------------------------+
|                         LAYER 2: MEMORY LAYER                           |
|  - Obsidian Vault (Karpathy RAG architecture: raw/ -> wiki/ -> output/) |
|  - Governed by CLAUDE.md / AGENTS.md rule contracts                     |
+-------------------------------------------------------------------------+
                                    ^
                                    |
+-------------------------------------------------------------------------+
|                        LAYER 3: SKILL BACKBONE                          |
|  - Domain -> Repetitive Task -> Documented Skill -> Automation          |
|  - Discovered via 30-day log audits or 15-min audio brain dumps         |
|  - Headless execution outputs reports directly back into the vault      |
+-------------------------------------------------------------------------+
```

---

## 2. Layer 1: The Visual Interface & Dual-Runtime Control

The visual frontend provides a command center for executing tasks without navigating raw terminal windows.

### Two Implementation Options
1. **Jarvis v2 Web HUD (`127.0.0.1:3217`)**:
   - Built with modern frontend tech (Vite/React/Canvas/WebGL).
   - Features central interactive 3D particle galaxy visualizer reflecting runtime state (*Idle, Listening, Working, Speaking, Error*).
   - Live dashboard cards displaying metrics (YouTube/Social analytics, weekly agent token usage, active sprint directives).
   - Top-level runtime pill toggle: Switch instantly between **Claude Code** and **OpenAI Codex** as the underlying execution engine.
2. **Obsidian Native Desktop Plugin (`AGENTIC OS V2`)**:
   - Ported directly into an Obsidian community plugin.
   - Embeds the command center inside the Markdown knowledge base.
   - Provides an integrated terminal drawer and one-click buttons to fire headless agent routines.

---

## 3. The Voice Bridge & Jev 3-Tier Classification

Instead of sending every voice or text command into an expensive LLM, the system routes through a zero-cost local speech bridge and Jev classifier.

### Zero-Cost Local Voice Pipeline
- **Ears (STT)**: Open-source **Whisper** running locally on Apple Silicon / GPU for zero-latency transcription.
- **Voice (TTS)**: Open-source **Kokoro** TTS delivering natural, sub-second synthesized speech without cloud API charges.

### Jev 3-Tier Execution Routing
Jev is an instant decision classifier from TypeSafe AI ($0.04/1M input tokens, free output tokens) that outputs probability distributions over predefined choices 200x faster than standard LLMs:

| Tier | Complexity | Execution Path | Example Query | Cost & Latency |
|------|------------|----------------|---------------|----------------|
| **Tier 1** | Deterministic / Retrieval | Direct filesystem / Obsidian script (No AI) | *"Bring up my morning intel brief"*, *"What are my top priorities?"* | ~0ms, $0.00 |
| **Tier 2** | Simple Comprehension | Small Fast LLM (Claude Haiku / Luna / Local SLM) | *"Summarize the top 3 AI headlines from today"* | ~400ms, <$0.001 |
| **Tier 3** | Complex Engineering / Synthesis | Terminal Agent (Claude Code / Codex / Headless Skill) | *"Analyze competitor pricing changes and generate a slide deck"* | Variable, Deep Reasoning |

---

## 4. Layer 2: Obsidian Memory Layer (Karpathy RAG Pattern)

The memory system does not rely on complex vector database infrastructures. Following Andrej Karpathy's Obsidian RAG pattern, files are divided into three clean functional directories:

1. **`raw/` (Input Zone)**:
   - Unstructured intake: Bookmarks, articles, tweets, PDF research papers, raw audio transcripts.
   - The human writes or dumps here.
2. **`wiki/` (Synthesized Knowledge Hub)**:
   - Structured, cross-linked reference notes synthesized by the AI.
   - Maintained via a `_master-index.md` and category subdirectories (`ai-agents/`, `rag-systems/`, `content-creation/`).
   - The AI writes and organizes here.
3. **`output/` (Deliverables & Reports)**:
   - Final compiled artifacts generated by Tier 3 skills: Intel briefs, slide decks, newsletters, proposals.

### Agent Governance Contract
To prevent organizational drift, the workspace root contains a `CLAUDE.md` or `AGENTS.md` file specifying exactly how the agent must classify, tag, and file documents into the vault.

---

## 5. Layer 3: The Skill Backbone

The skill backbone is the core operational engine that converts daily human habits into autonomous processes.

### The Progression Pipeline
$$\text{Domain} \longrightarrow \text{Repetitive Task} \longrightarrow \text{Documented Skill} \longrightarrow \text{Scheduled Automation}$$

### Golden Rules of Thumb
1. **Done it by hand twice** $\rightarrow$ Codify it into a documented skill.
2. **Skill works 5 times in a row** $\rightarrow$ Elevate it to an automation (cron schedule, webhook, or file watcher).
3. **Sends, spends, or publishes** $\rightarrow$ Always maintain a human-in-the-loop review checkpoint before external execution.

### Two Ways to Discover Your Skills
1. **The 30-Day Log Audit**:
   - Claude Code and Codex store 30+ days of prompt histories.
   - Prompt the agent: *"Review my conversation logs from the past 30 days. Identify repetitive workflows and propose 5 modular skills we can build."*
2. **The 15-Minute Stream-of-Consciousness Brain Dump**:
   - Open a microphone and speak freely for 10–20 minutes detailing everything done in a typical week across all business domains.
   - Have the agent parse the transcript, extract recurring responsibilities, and generate the corresponding `SKILL.md` scaffolds.

---

## 6. Packaging for Teams & Clients

One of the most powerful aspects of an Agentic OS is operational packaging:
- **Headless Execution**: Non-technical team members or clients do not need to understand terminal CLI syntax or model flags.
- **One-Click Execution**: UI cards in the dashboard trigger background CLI commands (`claude -p "..."` or `codex run "..."`).
- **Standardized Artifact Delivery**: Deliverables and reports automatically appear in the vault and dashboard feed.

---

## 7. Direct Application to Tony's Agent-OS

This tutorial provides immediate architectural validation for Tony's Agent-OS:
- **Directory Parallels**:
  - `raw/` $\leftrightarrow$ `000_Ingest/` & `007_Resource_Library/`
  - `wiki/` $\leftrightarrow$ `000_Wiki/`
  - `output/` $\leftrightarrow$ `001_Architecture/Logs/` & `002_Content-Creation/`
- **Runtime Dispatch**: Agent-OS already operates across both Claude Code and OpenAI Codex / Antigravity using unified instructions (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`).
- **Jev Integration**: Wiring Jev as the master pre-flight classifier (`tools/jev-router/router.mjs`) allows Agent-OS to filter queries into Tier 1 (local lookups), Tier 2 (Haiku), and Tier 3 (Sonnet/Codex) at near-zero routing cost.

## Related Resources
- Wiki: [[000_Wiki/AI-Agents/Jev-OpenRouter-Router]]
