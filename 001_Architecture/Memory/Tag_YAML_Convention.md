---
title: "YAML + Tag Convention for MD Files"
type: guideline
domain: architecture
tags: [guideline, architecture, obsidian, workflow-automation]
---

# YAML + Tag Convention for MD Files

## YAML Frontmatter

Every MD file in the workspace gets YAML frontmatter at the top:

```yaml
---
title: "File Title"
type: bookmark|skill|tool|doc|config|case-study|script|report
category: [broad domain - e.g., video-production, ecommerce, app-dev]
tags: [tool-name, feature, topic]
created: YYYY-MM-DD
source: url-or-local
---
```

## Tag Rules

- **Max 5 tags per file**
- **Structured/group tags only** — no ad-hoc 15,000-tag chaos
- **Hierarchical by purpose**: what it is → which tool/system → what it's about
- Examples:
  - Bookmark: `type: bookmark, tags: [hera-ai, animation, motion-graphics]`
  - Skill: `type: skill, tags: [obsidian, knowledge-management]`
  - Tool doc: `type: doc, tags: [kie-ai, video-generation, pricing]`

## Ingest Pipeline

1. File lands in `000_Ingest` (Obsidian Web Clipper)
2. Claude reads it, generates appropriate YAML + tags
3. File moves to appropriate destination folder
4. LLM Wiki synthesizes cross-references
5. Graphify maps it

## Daily Hook

End-of-day scan for new files → pass through LLM Wiki synthesis (YAML + tags + cross-refs) → Graphify update
