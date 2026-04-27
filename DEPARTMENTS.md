# Agent Registry — Department CLAUDE.md Files

This is the single source of truth for locating department documentation, agent responsibilities, and production guidelines across the warehouse.

---

## Department Directory

| Department | Status | CLAUDE.md Location | Purpose |
|-----------|--------|-------------------|---------|
| **Video Editor** | Active | `002_Content-Creation/Video_Editor/CLAUDE.md` | YouTube content production (12 channels), AI pipeline, case studies, cinematic styles (6 methodologies), Remotion compositions |
| **Whop Clipping** | Planned | `002_Content-Creation/Whop_Clipping/CLAUDE.md` | Long-form → shorts pipeline for client brands, per-view income |
| **Social Media Marketing** | Planned | `002_Content-Creation/Social_Media_Marketing/CLAUDE.md` | Static image + carousel strategy for Pinterest/Instagram, fashion/clothing niche |
| **POD Store** | Active | `005_Ecommerce/POD/CLAUDE.md` | Print-on-demand store (t-shirts, wall art), design + fulfillment |
| **Digital Products** | Planned | `005_Ecommerce/Digital_Products/CLAUDE.md` | Digital downloadable products: wall art, guides, templates via Gumroad/own website |
| **Amazon KDP** | Active | `005_Ecommerce/KDP/CLAUDE.md` | Book publishing on Kindle Direct Publishing |
| **Amazon Merch** | Planned | `005_Ecommerce/Amazon_Merch/CLAUDE.md` | T-shirt designs on Amazon Merch on Demand |
| **Upkeeply** | In Development | `003_Apps/Upkeeply/CLAUDE.md` | App project (home maintenance tracking with AI chatbot) |
| **AI Character Builder** | In Development | `003_Apps/AI_Character_Builder/CLAUDE.md` | AI character/avatar builder tool |
| **Roblox Game** | In Development | `004_Games/Roblox_Game/CLAUDE.md` | Roblox game development, Luau scripting, Studio architecture |

---

## Key Systems & References

### Root Warehouse
- **Warehouse manifest:** `App Building/CLAUDE.md` — overview of all departments, shared principles, API stack
- **Obsidian vault:** `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/` — business strategy, notes, research (1,382+ markdown files)

### Video Editor Special Systems
Located in `App Building/Video Editor/references/`:

| System | Location | Purpose |
|--------|----------|---------|
| Cinematic Style Guide | `styles/CINEMATIC_STYLE_GUIDE.md` | 6 production methodologies, visual identity, generation workflows |
| Model Selector | `docs/MODEL_SELECTOR.md` | Model selection guide with cost scenarios, decision tree |
| Model Catalog | `docs/MODEL_CATALOG.json` | Full pricing table across kie.ai and fal.ai |
| Style Templates | `styles/style-templates/style_0[1-6]_*/` | 6 style folders with JSON configs + representative frames |
| Case Study Skill | `.agents/skills/case-study.md` | Analyzes YouTube videos (hook, retention, viral mechanics, production notes) |
| API Stack Reference | `docs/API-STACK-REFERENCE.md` | Complete API integration guide for video production |

---

## How Agents Use This File

**When you need to:**

1. **Find a department's guidelines** → look up the department in the table above → read its CLAUDE.md
2. **Understand cross-department coordination** → read `App Building/_HQ/CLAUDE.md` (coordinates all departments)
3. **Access production systems** → go to Video Editor special systems above
4. **Update a department's status** → update the Status column and `updated_at` timestamp below
5. **Search semantically** → use `search_vault()` (Obsidian RAG, available once indexing is live)

---

## How to Update This File

- Add new departments to the directory table
- Update Status when a department moves from Planned → In Development → Active
- Add new system references as they're created
- Keep relative paths consistent with the warehouse structure
- Last updated: 2026-04-04

---

## Integration with Obsidian RAG

Once the Obsidian RAG system is live, all agents will have access to `search_vault()` for semantic queries:

```
search_vault("where is the Video Editor system?")
→ returns relevant CLAUDE.md sections + paths

search_vault("what departments handle content production?")
→ returns Video Editor, Travel Vlog, Whop Clipping CLAUDEs

search_vault("Tony's revenue streams")
→ returns notes from Obsidian vault + warehouse CLAUDE.md
```

This DEPARTMENTS.md file remains the authoritative directory for exact paths.
