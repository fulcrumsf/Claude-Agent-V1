---
title: "NotebookLM Research Protocol"
type: skill
domain: research
tags: [skill, research, content-creation, ai-agents]
---

# NotebookLM Research Protocol

## Purpose
Create grounded research notebooks using NotebookLM that prevent hallucination in video scripts and content creation. Each notebook is video-specific and tied to a case study.

## Protocol Steps

### 1. Gather Source Material
- Collect 5–10 authoritative sources (academic papers, articles, primary sources)
- Save PDFs or URLs for import into NotebookLM
- Ensure sources directly support the video narrative

### 2. Create Notebook via CLI
```bash
notebooklm --create --name "Video-Title-Notebook" --sources [source-list]
```

### 3. Generate Audio Overview (Optional)
```bash
notebooklm --audio --notebook [notebook-id]
```

### 4. Create Study Guide
Use NotebookLM's web interface to generate:
- Key points summary
- Timeline of events
- Important quotes with citations
- Q&A for fact-checking

### 5. Export and Store
- Export notebook as PDF or Markdown
- Store in `/004_Research/reference-material/[video-title]/`
- Link from case study file

### 6. Reference in Script
- Use notebook as source of truth during scriptwriting
- Include citations directly in script
- Cross-reference with audio if created

## When to Use
- Creating video content requiring factual accuracy (documentaries, case studies, educational)
- Building a case study (see Case-Study-Analysis.md)
- Researching for multi-part series
- Creating affiliate or promotional content based on product research

## When NOT to Use
- Purely narrative or entertainment content with no factual claims
- Quick shorts or clips under 1 minute
- When no sources are available or needed

## Integration with Video Production
- NotebookLM notebook reference goes into Video Production Workflow at "Script" stage
- Notebook output informs Remotion composition fact-checking
- Case study references the notebook

## Maintenance
- Notebooks are versioned with the video they support
- Archive completed notebooks in reference-material
- Link from case studies to notebooks for future reference

## Resources
- NotebookLM CLI: `notebooklm` command
- Documentation: `/Users/tonymacbook2025/.claude/projects/[-path-]/memory/project_notebooklm_role.md`
