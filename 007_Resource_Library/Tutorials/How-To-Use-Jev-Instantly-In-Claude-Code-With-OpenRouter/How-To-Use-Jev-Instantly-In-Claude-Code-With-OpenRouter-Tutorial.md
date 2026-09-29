---
title: "How to Use Jev Instantly in Claude Code with OpenRouter (No Waitlist)"
type: tutorial
category: ai-agents
tags:
  - claude-code
  - jev
  - typesafe-ai
  - openrouter
  - model-routing
created: 2026-09-27
source: https://www.youtube.com/watch?v=s4skNgV8nJM
---

# How to Use Jev Instantly in Claude Code with OpenRouter (No Waitlist)

A comprehensive guide to integrating TypeSafe AI's Jev model directly into Claude Code via OpenRouter without waiting for official TypeSafe platform waitlists.

## Overview & Architecture

Jev (`typesafe/jev-latest`) is TypeSafe AI's fast "System 1" decision model designed for rapid, structured evaluations (boolean decisions, categorical routing, and score assessments). Instead of relying on the proprietary TypeSafe SDK, you can route Claude Code calls directly through OpenRouter's standard chat completions endpoint.

```
+-----------------------------------------------------------+
|                        Claude Code                        |
+-----------------------------------------------------------+
                             |
                   [open-router-jev-calls]
                             v
+-----------------------------------------------------------+
|                     OpenRouter API                        |
|        Endpoint: POST /api/v1/chat/completions            |
|              Model: typesafe/jev-latest                   |
+-----------------------------------------------------------+
                             v
+-----------------------------------------------------------+
|                   TypeSafe Jev Engine                     |
|  - Fast parallel question evaluation                      |
|  - Typed structured outputs (bool, choice, score)        |
+-----------------------------------------------------------+
```

---

## Prerequisites & Environment Setup

1. **OpenRouter Account & API Key**:
   - Register at [OpenRouter](https://openrouter.ai).
   - Export your API key in your shell configuration (`~/.zshrc` or project environment):
     ```bash
     export OPENROUTER_API_KEY="sk-or-v1-..."
     ```

2. **Verify Connectivity with cURL**:
   Run the following test call to verify that your OpenRouter key can communicate with Jev:
   ```bash
   curl https://openrouter.ai/api/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     -d '{
       "model": "typesafe/jev-latest",
       "messages": [
         {
           "role": "user",
           "content": "help, my payouts have been failing for three days"
         }
       ],
       "questions": [
         {
           "id": "is_urgent",
           "question": "Is this issue time-sensitive or critical?",
           "type": "bool"
         },
         {
           "id": "department",
           "question": "Which department should handle this request?",
           "type": "choice",
           "choices": ["billing", "technical", "general"]
         },
         {
           "id": "frustration",
           "question": "Estimate user frustration from 1 to 5.",
           "type": "score",
           "range": [1, 5]
         }
       ]
     }'
   ```

---

## Step-by-Step Installation in Claude Code

### Step 1: Install the Official TypeSafe AI Plugin Base
Claude Code supports marketplace plugins. Install the base TypeSafe AI plugin:
```bash
claude plugin marketplace add typesafe-ai/skills
claude plugin install typesafe@typesafe-ai
```

### Step 2: Customize the Skill for OpenRouter
Launch Claude Code in your workspace (`claude`) and prompt the agent to adapt the official skill:

> **Customization Prompt:**
> "Please get a good overview about the installed type safe AI plugin with the skill there, and make a suggestion how we can update the skill to:
> 1. Not be too proactive when it's used (only trigger when explicitly requested or during heavy decision forks).
> 2. Work directly with OpenRouter (`typesafe/jev-latest`) instead of the official TypeSafe SDK.
> Update the skill accordingly, show me a diff of what changed, save the new skill in the user directory as `open-router-jev-calls`."

### Step 3: Remove Conflicting Official Plugin & Reload
To prevent collisions between the official SDK plugin and your OpenRouter skill:
1. Run `/plugin` inside Claude Code.
2. Select `Installed` -> choose `typesafe` -> select `Uninstall`.
3. Reload skills:
   ```bash
   /reload-skills
   ```
4. Verify with `/skills` that `open-router-jev-calls` is active.

---

## Key Benefits & Use Cases

- **No Waitlist Access**: Immediate access to TypeSafe Jev via existing OpenRouter credits.
- **Latency & Speed**: Jev functions as a lightweight classifier, eliminating large-model latency for simple boolean and triage routing decisions.
- **Structured Contracts**: Directly returns strongly-typed results without needing JSON schema retry loops.

## Related Resources
- [[Jev-Will-10x-Your-Claude-Code]]
- [[This-NEW-Jev-Claude-OS-Just-Changed-Every-AI-Workflow]]
- Official Documentation: `https://docs.typesafe.ai`
- OpenRouter Directory: `https://openrouter.ai/typesafe`
- Video Analysis: `007_Resource_Library/Tutorials/How-To-Use-Jev-Instantly-In-Claude-Code-With-OpenRouter/ANALYSIS.md`
- Wiki: [[000_Wiki/AI-Agents/Jev-OpenRouter-Router]]
