---
name: obsidian
description: >
  Expert guidance for Obsidian PKM (Personal Knowledge Management) workflows, vault organization,
  note-taking systems (Zettelkasten, PARA, atomic notes), plugin configuration (Dataview, Templater,
  Canvas, Bases, Tasks), MCP server setup for Claude integration, and AI-assisted knowledge workflows.
  Use this skill whenever the user mentions Obsidian, their vault, PKM, second brain, note-taking systems,
  linking notes, Zettelkasten, PARA method, Dataview queries, Templater templates, or wants Claude to
  read/write to their Obsidian vault. Also use when setting up obsidian-mcp, Local REST API plugin,
  or any Claude ↔ Obsidian integration.
---

# Obsidian Best Practices

## Core Philosophy

Obsidian is a **thinking tool**, not a filing cabinet. The goal is to surface connections between ideas over time, not to organize perfectly from the start. Favor links over folders. Write in your own words. Let structure emerge from use.

Your vault should contain your authentic thinking. If integrating with Claude/AI: keep AI-generated outputs (plans, drafts) outside the vault or in a clearly marked folder — don't pollute your knowledge graph with generated content.

---

## Vault Organization Systems

### Option A: Zettelkasten (idea-first)
Best for researchers, writers, learners who want to build a knowledge network.

```
📁 Fleeting/       ← Quick captures, inbox — process daily
📁 Literature/     ← Notes from books, articles, podcasts (source-based)
📁 Permanent/      ← Atomic ideas in your own words, heavily linked
📁 Templates/      ← Note templates
📁 Attachments/    ← Images, PDFs
```

**Key rules:**
- One idea per note (atomic)
- Always write in your own words — never copy/paste
- Every permanent note links to at least 2 others
- Fleeting notes get processed within 48h or deleted

### Option B: PARA (project-first)
Best for professionals, project managers, action-oriented people.

```
📁 Projects/       ← Active projects with a deadline
📁 Areas/          ← Ongoing responsibilities (health, finances, work)
📁 Resources/      ← Reference material by topic
📁 Archive/        ← Inactive items
```

### Option C: PARA + Zettelkasten (hybrid — recommended)
PARA as the **execution engine** (where things get done), Zettelkasten as the **insight engine** (where ideas live). Connect them via bidirectional links: project notes link to permanent notes.

### Flat Structure Option
Skip folders entirely for the knowledge graph. Use tags and links instead. Only use folders for: `Attachments/`, `Templates/`, `Daily/`. Everything else lives flat. Works surprisingly well with good search and Dataview.

---

## Note-Taking Best Practices

### Note Types

| Type | Purpose | When to Create |
|------|---------|----------------|
| **Fleeting** | Raw capture, inbox | Immediately — don't edit in the moment |
| **Literature** | One source summarized | While reading/watching |
| **Permanent** | Single atomic idea | After processing fleeting/literature notes |
| **Daily** | Journal, log, task hub | Every day (use Periodic Notes plugin) |
| **Map of Content (MOC)** | Index note for a topic | When a topic has 10+ notes |
| **Project** | Active work with deadline | When starting a project |

### Linking Rules
- Use `[[wikilinks]]` liberally — links are free
- Link on first mention of a concept
- Create notes for concepts even before writing them — the link will create a stub
- Use aliases: `[[Note Title|display text]]` for natural prose
- Avoid orphan notes — every note should have at least one link in or out
- Block references (`[[Note^block-id]]`) for citing specific passages

### Frontmatter / Properties
Use YAML frontmatter for structured metadata. Obsidian Bases (core plugin, added 2025) turns properties into database views.

```yaml
---
title: Note Title
date: 2026-03-29
tags: [topic, subtopic]
status: seedling   # seedling | growing | evergreen
type: permanent    # fleeting | literature | permanent | daily | moc
source: ""         # URL or book title
related: []
---
```

### Writing Style
- Title as a complete claim: "Attention is a finite resource" not "Attention"
- First line summarizes the entire note
- No headers in atomic notes — if you need headers, split into multiple notes
- Use `#tags` for cross-cutting themes (emotions, frameworks, people)

---

## Essential Plugins

### Core (built-in, enable these)
- **Daily Notes** or **Periodic Notes** — journal + weekly/monthly reviews
- **Templates** (basic) — simple note templates
- **Canvas** — visual mind-mapping and idea layout
- **Bases** — database views of your notes (added 2025, major feature)
- **Graph View** — visualize note connections
- **Backlinks** — see what links to current note

### Community Plugins (power stack)

| Plugin | Purpose | Learning Curve |
|--------|---------|----------------|
| **Dataview** | Query vault like a database, build dynamic dashboards | Medium |
| **Templater** | Dynamic templates with variables and JavaScript | Medium |
| **Tasks** | Track tasks across entire vault with filtering | Low |
| **QuickAdd** | Fast capture with templates | Low |
| **Calendar** | Navigate daily notes visually | Low |
| **Commander** | Custom toolbar buttons, macros, startup routines | Low |
| **Advanced Canvas** | Flowchart shapes, edge styles, collapsible groups | Low |
| **Excalidraw** | Hand-drawn diagrams embedded in notes | Low |
| **Smart Connections** | AI-powered semantic note search | Low |

### Plugin Priority Order
Start with: Periodic Notes → Templater → Tasks → Dataview → QuickAdd
Add later: Commander → Smart Connections → Excalidraw

---

## Dataview Essentials

Dataview turns your vault into a queryable database. Use it for dashboards, task tracking, and MOCs.

```dataview
// List all permanent notes tagged #psychology, sorted by date
LIST
FROM #psychology
WHERE type = "permanent"
SORT file.cdate DESC
```

```dataview
// Table of active projects with status
TABLE status, due-date
FROM "Projects"
WHERE status != "complete"
SORT due-date ASC
```

```dataview
// Inline — shows note creation date
`= this.file.cdate`
```

**Best practice:** Put Dataview queries in MOC notes and dashboard notes. Don't embed them in atomic notes — it couples structure to content.

---

## Templater Essentials

Templater runs JavaScript at note creation time. More powerful than core Templates.

```
<%*
// Auto-set title from filename
tR += tp.file.title
%>
---
date: <% tp.date.now("YYYY-MM-DD") %>
tags: []
status: seedling
---

# <% tp.file.title %>

## Summary

## Links
```

**Best practice:** Create templates for every note type. Map templates to folders using Templater's folder template setting so the right template fires automatically.

---

## Claude + Obsidian MCP Integration

### Option 1: obsidian-mcp (recommended)
Installs as an MCP server. Requires the **Local REST API** community plugin.

**Setup:**
1. Install "Local REST API" plugin in Obsidian → enable → copy your API key
2. Add to Claude Code MCP config:
```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "your-api-key-here",
        "OBSIDIAN_HOST": "http://localhost:27123"
      }
    }
  }
}
```
3. Claude can now read/write notes, search vault, create notes, list tags

### Option 2: obsidian-claude-code-mcp
WebSocket-based, auto-discovers vaults. Good for multiple vaults.
- Install `obsidian-claude-code-mcp` plugin in Obsidian
- Runs on port 22360 by default
- Supports multiple vaults with unique port per vault

### Option 3: Direct file access (simplest)
If your vault is on the local filesystem, Claude can read/write `.md` files directly with Read/Write/Edit tools. No plugin needed. Best for simple workflows.

### What Claude can do with vault access
- Read notes for context before writing new content
- Create structured notes from conversations
- Run semantic searches across the vault
- Update frontmatter properties in bulk
- Generate Dataview queries based on your vault structure
- Create MOC notes linking related content

### Boundary rule
Keep Claude's working memory (`.claude/memory/`) separate from your Obsidian vault. The vault is your thinking — Claude's outputs are drafts. Only promote Claude-generated content into the vault after you've reviewed and rewritten it in your own voice.

---

## Workflows

### Daily Review Workflow
1. Open Daily Note (Periodic Notes plugin — auto-created)
2. Process Fleeting notes inbox — convert to permanent or delete
3. Check Tasks dashboard (Dataview query on active tasks)
4. Add to Daily note: what happened, ideas, links to relevant notes

### Reading/Learning Workflow
1. Create Literature note with source metadata in frontmatter
2. Take notes in your own words while reading
3. After finishing: extract 2–5 key ideas → create Permanent notes
4. Link permanent notes to each other and to existing notes
5. Archive the literature note (or tag `#processed`)

### Project Workflow (PARA)
1. Create Project note with: goal, deadline, key resources, tasks list
2. Link to relevant permanent/resource notes
3. Use Tasks plugin to track action items
4. Weekly: review project notes, update status
5. On completion: move to Archive, extract learnings as permanent notes

### MOC (Map of Content) Workflow
When you notice 10+ notes clustering around a theme:
1. Create a MOC note titled "Topic MOC" or "Topic Index"
2. List all related notes with a one-line summary each
3. Group into sub-themes
4. Link the MOC from your vault homepage
5. Add the MOC to new related notes as a backlink target

---

## Graph View Tips
- Use **groups** to color-code by folder or tag
- Filter to show only specific tags when exploring a topic
- Orphan nodes = notes that need more links — audit these periodically
- Local graph on a note = see its neighborhood of connections
- Don't obsess over the graph looking pretty — optimize for useful links

---

## Common Mistakes to Avoid
- **Over-organizing before writing** — start writing, let structure emerge
- **Perfect templates** — a simple template used is better than a complex one avoided
- **Folder hierarchies deeper than 2 levels** — use tags and links instead
- **Copying instead of paraphrasing** — you won't remember copy-pasted content
- **Never reviewing notes** — a note never re-read is wasted effort; build in review time
- **Polluting the vault with AI output** — Claude generates, you curate and rewrite
- **Too many plugins** — start with 3–5, master them before adding more
