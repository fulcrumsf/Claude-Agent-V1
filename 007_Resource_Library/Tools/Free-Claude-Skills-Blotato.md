---
title: "Free Claude Skills Blotato"
type: "tool-doc"
category: "ai-agents"
tags:
  - ai-agents
  - claude-skills
  - blotato
  - automation
  - tool
created: 2026-05-12
source: local
---

Free Claude skills you install once, then use forever. They take you from blank page to scheduled social post in one conversation.

Works in Claude Code, Claude Desktop, and Claude Cowork.

## What's in the pack

5 skills compose into one workflow:

Skill

When to use it

[content-coach](https://help.blotato.com/claude-skills/claude-skills/content-coach)

"I don't know what to post". Front door for beginners. Auto-runs the others.

[brand-brief](https://help.blotato.com/claude-skills/claude-skills/brand-brief)

One-time setup. Captures your business, customer, CTA, story, and voice.

[post-writer](https://help.blotato.com/claude-skills/claude-skills/post-writer)

"Write me a post about X for Instagram". Produces a graded, polished post.

[post-grader](https://help.blotato.com/claude-skills/claude-skills/post-grader)

"Is this post any good?". Scores a draft and lists the top 3 fixes.

[post-scheduler](https://help.blotato.com/claude-skills/claude-skills/post-scheduler)

"Schedule this to LinkedIn". Ships the post via Blotato.

You only need to know one skill on day one: content-coach. It calls the others behind the scenes.

## How to install

Each skill is one file: `SKILL.md`. The install method depends on which Claude product you use.

### Claude Code or Claude Desktop (filesystem install)

1. Create a folder at `~/.claude/skills/[skill-name]/`
2. Create a file inside called `SKILL.md`
3. Copy the SKILL.md contents from the skill's page in this guide
4. Restart Claude Code, or fully quit and relaunch Claude Desktop

Use `~/.claude/skills/` for skills available in every Claude session. Use `.claude/skills/` for project-only skills.

### Claude Cowork (ZIP upload)

Cowork does not use a local skills folder. You upload skills through the app UI.

1. Create a folder on your computer named `[skill-name]/` (use the skill's slug, e.g., `post-writer`)
2. Create a file inside called `SKILL.md`
3. Copy the SKILL.md contents from the skill's page in this guide into that file
4. Compress the folder into a ZIP file
5. Open Claude Cowork
6. Click **Skills**
7. Click the **+** button, then **Upload a skill**
8. Select the ZIP file
9. Toggle the skill on

Repeat for each skill. There is no `.plugin` file — Blotato skills are distributed as copy-paste SKILL.md text, which you package into a ZIP yourself for Cowork.

For organization-wide install, an admin enables it under **Organization settings > Skills**.

### Confirm it loaded

Type one of the trigger phrases from the skill's page. If the skill responds, it loaded.

### Install in this order

1. [brand-brief](https://help.blotato.com/claude-skills/claude-skills/brand-brief)
2. [content-coach](https://help.blotato.com/claude-skills/claude-skills/content-coach)
3. [post-writer](https://help.blotato.com/claude-skills/claude-skills/post-writer)
4. [post-grader](https://help.blotato.com/claude-skills/claude-skills/post-grader)
5. [post-scheduler](https://help.blotato.com/claude-skills/claude-skills/post-scheduler)

## How they work together

A beginner only needs to know one skill: content-coach. The coach calls the others as needed.

```
content-coach
   ↓ (no brand brief yet?)
brand-brief        → saves brand-brief.md
   ↓
content-coach      → brainstorms 5 ideas
   ↓ (you pick one)
post-writer        → drafts hook, body, CTA
   ↓ (auto-runs)
post-grader        → scores, lists fixes, post-writer applies them, loops to 8+/10
   ↓ (you approve)
post-scheduler     → schedules via Blotato
```

Once `brand-brief.md` exists, you can call any skill standalone:

- post-writer directly when you have an idea
- post-grader directly when you wrote a draft and want feedback
- post-scheduler directly when you have finished copy

## Beginner walkthrough

Sarah owns a handmade candle business. She has never posted on social. She installed the skills.

### Session 1: blank page

Sarah types: "I want to start posting but I don't know what to do."

1. Claude triggers content-coach
2. content-coach checks the working folder for a brand brief. None found, so it silently invokes brand-brief
3. brand-brief asks 5 short questions: what you sell, who buys, one CTA, recent story, vibe. Saves answers to `brand-brief.md`
4. content-coach reads the brief and generates 5 specific post ideas tied to her candles and audience
5. Sarah picks one: "the customer who used my candle in a proposal"
6. content-coach asks which platform. She says Instagram
7. content-coach calls post-writer with the idea, brief, and platform
8. post-writer drafts hook, caption, and CTA
9. post-writer auto-invokes post-grader. Grader scores hook 6/10 and CTA 5/10, suggests fixes, post-writer applies them
10. content-coach shows the final post and asks "Approve and ship?"
11. Sarah says yes. content-coach calls post-scheduler. Done.

One conversation, blank page to scheduled post.

### Session 2: she has momentum

Sarah types: "give me a few more ideas."

content-coach triggers. Brand brief already exists, so it skips intake and jumps straight to ideation. Same flow, faster.

### Session 3: she wrote her own draft

Sarah types: "is this caption any good?" and pastes her draft.

Claude invokes post-grader directly. Grader scores it, shows fixes inline. Sarah accepts the rewrite, then types "schedule this for tomorrow morning". post-scheduler fires.

### Session 4: power user

Sarah types: "write me a post about \[idea\]."

post-writer fires directly. Grader runs after. Scheduler runs on approval.

## What the skills are tuned for

The pack is optimized for virality, not clean copy alone. The grader weights hook strength at 50%. The first 3 words decide whether the post gets read. The other dimensions (curiosity, emotional charge, share-worthiness, voice match, polarity, platform fit) split the remaining 50%.

The skills steer toward:

- Hook patterns with high virality ceilings: receipts ("I tested 47 X"), reverse ("most people think X, here's why they're wrong"), stolen lessons ("I copied X")
- Brand briefs capturing your strong opinion or wedge. The contrarian belief fuels polarizing posts.
- CTAs driving shares, saves, or polarizing comments. Not "what do you think?"
- Platform-algorithm fit: LinkedIn rewards comments, IG rewards saves, FB rewards shares, TikTok rewards completion. CTAs match the metric.

## Universal voice rules baked in

Every post the skills produce follows these rules:

- Contractions always ("don't" not "do not")
- Active voice, short sentences
- Address the reader as "you"
- Numbers as digits ("3 tips" not "three tips")
- No em dashes
- One concrete idea per post
- Specific details over generic statements

## Customizing

You own these files. Edit them.

- Update hook patterns in `post-writer/SKILL.md` to add ones working for your niche
- Adjust grading rubric weights in `post-grader/SKILL.md` if you care more about CTA than hook
- Re-run brand-brief any time your business changes

## Dependencies

- Required: Claude with file system access (Read, Write, Edit tools)
- Optional: Blotato MCP server for scheduling. Without it, post-scheduler falls back to writing the post to a file you paste manually. To set up, see [Claude Code MCP setup](https://help.blotato.com/api/claude-code) or [MCP Server Setup](https://help.blotato.com/api/mcp/setup)

## FAQs

### Where do I get the free Claude skills?

Click any skill name in the table above. Each skill's page has the full SKILL.md as a copy-paste block. Follow the 4-step install at the top of the page.

### Are the Claude skills free?

Yes. The full content creator pack is free to download and use.

### What Claude skills do you offer for content creation?

Five skills: content-coach, brand-brief, post-writer, post-grader, post-scheduler. They chain together. content-coach orchestrates the others.

### Do the skills work in Claude Cowork?

Yes. The same SKILL.md content works in Claude Code, Claude Desktop, and Claude Cowork. The install method differs: Claude Code and Claude Desktop read skills from `~/.claude/skills/[skill-name]/SKILL.md` on your filesystem. Cowork has no local skills folder — you save the SKILL.md inside a folder named after the skill, ZIP the folder, then upload it via **Customize > Skills > + > Upload a skill** inside the Cowork app. Full steps in the [Claude Cowork install section above](https://help.blotato.com/claude-skills/claude-skills#claude-cowork-zip-upload).

### Do I need Blotato to use the skills?

No. The first 4 skills work without Blotato. post-scheduler is the only one needing Blotato. Even there, it falls back to saving the post as a copy-paste file if Blotato isn't connected.

### Can I edit the skills?

Yes. Each skill is one SKILL.md file. Open it, change anything, save. Claude reads the updated version next session.

Same pattern. Create a folder named `[your-skill-name]/` with a `SKILL.md` file inside (frontmatter: name, description, allowed-tools, plus instructions). For Claude Code or Desktop, place the folder under `~/.claude/skills/` and restart. For Cowork, ZIP the folder and upload via **Customize > Skills > + > Upload a skill**.

Last updated