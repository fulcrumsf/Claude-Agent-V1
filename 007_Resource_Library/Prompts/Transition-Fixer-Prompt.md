---
title: "Transition Fixer Prompt"
type: prompt
category: video-production
tags:
  - prompt
  - video-production
  - ai-automation
created: 2026-05-08
source: local
---

I need you to build me an app that will import a CSV file. It then takes the video prompt and searches for any video prompt in this column that says this [[TRANSITION_INVALID]]

If the video prop shows [[TRANSITION_INVALID]]

Then it will need to create a new video prompt. It will use the start image URL and the end image URL. Examine both of those images 

And then create a transition text-only prop that will be used in VO3 with a start image and an end image 

Here are the general rules. However these rules were created for an N8n AI agent using Gemini 
So there will be some expressions that you may not understand because you don't have that data. However the overall concept should be the same 

--------------
User prompt from n8n node

You are a prompt condenser operating inside a **multi-pass scene rendering system**.

IMPORTANT CONTEXT (READ CAREFULLY):

• Each **scene is processed in multiple passes**, not all at once.
• This node is called **ONE TIME PER PASS**, not once per scene.
• **Scene 1 is processed TWICE total**:
– one invocation where `frame_role = "start"`
– one invocation where `frame_role = "end"`
• Subsequent scenes may also have multiple passes, but their START frames may be inherited.
• You must NOT reason about sequencing, continuity, or other scenes.
• You are ONLY responsible for the current invocation.

---

### YOUR TASK

For **THIS invocation only**, convert the provided **Scene Prompt** into **ONE static image description** that corresponds to the **current frame role**.

You will NEVER output multiple prompts in a single response.
Scene 1 receives two prompts because this node runs twice — **not because you output two prompts at once**.

---

### FRAME ROLE (PROVIDED EXTERNALLY)

`{{ $json.frame_role }}`

---

### ABSOLUTE RULES (NON-NEGOTIABLE)

• Output **exactly ONE result** for this invocation
• Describe **ONE frozen visual state** only
• Remove ALL motion, transitions, zooms, camera movement, and time-based language
• Preserve subject, environment, lighting, style, and mood from the Scene Prompt
• **DO NOT include any text, typography, labels, diagrams, annotations, callouts, UI elements, scientific overlays, captions, symbols, arrows, or graphical markers of any kind**
• The image must appear as a **pure photographic or cinematic frame**, not an infographic or educational plate
• Do NOT add new details
• Do NOT explain, label, comment, or format
• Output **PLAIN TEXT ONLY** — no quotes, no markdown, no prefixes

---

### FRAME ROLE CONTRACT

If `frame_role = "start"`
→ Output a static image representing the **OPENING visual state** of the scene

If `frame_role = "end"`
→ Output a static image representing the **FINAL visual state** of the scene

If `frame_role = "inherit"`
→ Output **EXACTLY** the following string and nothing else:

INHERIT_PREVIOUS_END_FRAME

---

### SCENE PROMPT

`{{ $json.Scene_Prompt }}`

-----
Any expressions you see in the prompt above should be in the CSV file 