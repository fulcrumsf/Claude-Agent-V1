# 🚀 Creative Content Engine + Blotato — Free Template

A ready-to-use AI agent template for creating visual ad content at scale. Generate images, build campaigns, and schedule social media posts — all from a single AI conversation.

**Powered by:** [Google AI Studio](https://aistudio.google.com) + [Blotato](https://blotato.com)

---

## What's Inside

| Folder | What It Does |
|--------|-------------|
| `.agent/` | Agent brain — the instructions, skills, and workflows that make your AI assistant smart |
| `references/` | Your config, docs, and media files (product images go in `inputs/`) |
| `tools/` | Python scripts that handle image generation, Airtable, and file hosting |

### Skills (`.agent/skills/`)
- **Blotato Best Practices** — How to upload media, generate captions, schedule posts, and handle platform-specific requirements
- **Modal Deployment** — Deploy automated pipelines to the cloud with [Modal.com](https://modal.com) (serverless, pay-per-use)

### Workflows (`.agent/workflows/`)
- **30-Day Campaign** — Create a full 30-day marketing campaign: brand discovery → content calendar → AI image generation → auto-scheduling

### Tools (`tools/`)
- **Image Generation** — Generate images with Nano Banana Pro via Google AI Studio
- **Airtable Integration** — Use Airtable as your content review hub
- **Provider System** — Extensible architecture for adding new AI providers

---

## Quick Start

### 1. Open this folder in Claude Code

Open this folder as a workspace in [Claude Code](https://claude.ai/code).

### 2. Install the Blotato MCP Server

Blotato is how your agent posts to social media (Instagram, TikTok, YouTube, LinkedIn, etc.). You need to connect it as an MCP server in Claude Code.

1. Open your MCP config file. In Claude Code, use `/config` to open settings, or edit the appropriate MCP config file.
2. Add the following entry inside the `"servers"` object:

```json
"blotato": {
  "serverUrl": "https://mcp.blotato.com/mcp",
  "headers": {
    "blotato-api-key": "YOUR_BLOTATO_API_KEY_HERE"
  }
}
```

3. Replace `YOUR_BLOTATO_API_KEY_HERE` with your Blotato API key (get one at [my.blotato.com](https://my.blotato.com) → API settings)
4. Save the file — the MCP server will connect automatically

### 3. Set Up API Keys

1. Copy `references/.env.example` to `references/.env`
2. Fill in your API keys:
   - **`GOOGLE_API_KEY`** — Free from [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (for Nano Banana Pro image generation)
   - **`KIE_API_KEY`** — From [kie.ai/api-key](https://kie.ai/api-key) (for file hosting)
   - **`AIRTABLE_API_KEY`** — From [airtable.com/create/tokens](https://airtable.com/create/tokens) (for content management)
   - **`AIRTABLE_BASE_ID`** — From your Airtable base URL
   - **`BLOTATO_API_KEY`** — Same key you used in the MCP config above

### 4. Install Python Dependencies

```
pip install -r tools/requirements.txt
```

### 5. Create Your Airtable Table

Create a table called **Content** in your Airtable base. The full schema is listed in `.agent/AGENT_BASIC.md`.

### 6. Connect Your Social Accounts in Blotato

Head to [my.blotato.com](https://my.blotato.com) and connect the social media accounts you want to post to (Instagram, TikTok, YouTube, LinkedIn, etc.).

### 7. Start Creating!

Open the Claude Code chat and try:

- **Quick post:** *"Hey, post this image to Instagram and TikTok"* (drop an image in `references/inputs/`)
- **Schedule posts:** *"Schedule these 3 images across the week — one today, one tomorrow, one in two days"*
- **Full campaign:** *"Let's create a 30-day marketing campaign for my product"* (this runs the `/30-day-campaign` workflow)

---

## What You Can Do

| Level | Demo | What It Does |
|-------|------|-------------|
| **1** | Multi-platform post | Post a single piece of media to multiple platforms in one command |
| **1** | Scheduled posting | Stagger posts across days/weeks with automatic scheduling |
| **2** | 30-day campaign | Full brand discovery → image generation → auto-scheduling pipeline |

---

## Want More?

This is the **free version** of the Creative Content Engine. The full version includes:

- 📝 **Detailed prompt engineering guides** — model-specific best practices refined from real campaigns
- 🎬 **Video generation** — Veo 3.1 (native audio), Kling 3.0 (cinematic), Sora 2 Pro
- 🔄 **Multi-provider orchestration** — Google, Kie AI, and WaveSpeed with automatic routing
- 🤖 **YouTube → LinkedIn automation** — Daily pipeline that monitors a channel, generates infographics, and posts on autopilot
- 🧠 **Full agent intelligence** — The complete AGENT.md with advanced orchestration logic

**Get the full version →** [RoboNuggets.com](https://robonuggets.com)

---

*Built with ❤️ for the RoboNuggets community*
