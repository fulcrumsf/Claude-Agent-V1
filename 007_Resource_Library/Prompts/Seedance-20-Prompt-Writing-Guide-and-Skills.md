---
title: "Seedance 2.0 Prompt Writing Guide and Skills"
tags:
  - Image-Video-Model
  - Guide
created: 2026-09-13
---

## Seedance 2.0 Prompt Writing Skills

[中文](https://github.com/dexhunter/seedance2-skill/blob/main/README-zh.md)

[Agent skills](https://agentskills.io/) for writing effective video generation prompts for [Jimeng Seedance 2.0](https://jimeng.jianying.com/), ByteDance's multimodal AI video generation model. Works with Claude Code, Cursor, Cline, and other compatible agents.

Covers input constraints, @ reference syntax, camera language, prompt structure patterns, and ready-to-use templates for ads, dramas, MVs, educational content, and more.

## Install

Clone or download this repository, then copy the skill file(s) to your Claude skills directory:

```
mkdir -p ~/.claude/skills

# English
cp SKILL.md ~/.claude/skills/seedance-prompt-en.md

# Chinese
cp zh/SKILL.md ~/.claude/skills/seedance-prompt-zh.md
```

### Option B: Via skills CLI

```
npx skills add dexhunter/seedance2-skill
```

Then ask your AI agent to help you write a Seedance 2.0 video prompt.

## Skills

| File | Language | Description |
| --- | --- | --- |
| [SKILL.md](https://github.com/dexhunter/seedance2-skill/blob/main/SKILL.md) | English | Prompt writing guide for Seedance 2.0 |
| [zh/SKILL.md](https://github.com/dexhunter/seedance2-skill/blob/main/zh/SKILL.md) | 中文 | Seedance 2.0 提示词撰写指南 |

## Sources

Based on official ByteDance documentation:

- [Seedance 2.0 User Manual](https://bytedance.larkoffice.com/wiki/A5RHwWhoBiOnjukIIw6cu5ybnXQ) — Parameters, interaction methods, multimodal capabilities, and example prompts
- [Seedance 2.0 Real-world Cases](https://bytedance.larkoffice.com/wiki/LJXzwehluiFdzKkb1recZdfonZg) — Drama production, e-commerce ads, dance imitation, science education, AI MVs, and more

## License

[MIT](https://github.com/dexhunter/seedance2-skill/blob/main/LICENSE)