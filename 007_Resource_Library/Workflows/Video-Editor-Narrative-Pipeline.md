---
title: "Video Editor Narrative Pipeline"
type: workflow
category: video-production
tags:
  - video-editing
  - pipeline
  - ai-automation
created: 2026-05-08
source: local
---


All other nodes that appear in the canvas but are:
- Deactivated
- Unconnected
- Or used as templates

…are **non-authoritative** and intentionally ignored.

---

## 4. Inputs (What the Workflow Actually Uses)

### 4.1 Voiceover (VO)
- Source: `Get_VO_URL`
- Field of record: `response` (URL to audio/video VO)
- Duration (Finder): **~1:32**

This VO length is treated as the **golden runtime reference**.

---

### 4.2 Scene Clips (Background / Visuals)
- Source: prior video-generation workflows
- Each scene returns:
  - `response` → clip URL
  - `Scene_ID`
  - `code = 200`
  - `message = success`

Total stitched duration (Finder): **~1:33**

This is considered **close enough** to VO duration and intentionally tolerated.

---

## 5. Validation Logic (Finalized)

### Success Criteria (per API contract):
A scene is valid if:
- `code === 200`

Nothing else is required.

This is enforced via the **Validate (Switch)** node.

### Failure Handling:
- Any non-200 result routes to:
  - `Log Trim Error`
  - Then safely exits the pipeline

No downstream node ever depends on failed items.

---

## 6. Merge Strategy (Important)

### Merge Node Configuration (Final Decision)

**Mode:** `Combine`  
**Strategy:** `Include any unpaired items`  
(**aka: Keep Everything / Outer Join behavior**)

### Why this is correct:
- Inputs do **not** share identical schemas
- Scene clips, VO, and optional beat map data are heterogeneous
- We want:
  - All valid clips
  - The VO URL
  - Optional metadata
- Without forcing key alignment or dropping items

⚠️ **Matching Fields is intentionally NOT used**

---

## 7. Scene Ordering (Critical Insight)

Scene ordering is controlled by:
- **Upstream generation order**
- **Array position**
- **Implicit scene sequence**

### NOT used:
- FFmpeg timestamps
- Hard beat-map enforcement
- Forced trim alignment

### Why:
- Total clip duration ≈ VO duration
- Minor drift is acceptable
- Timestamp mismatches risk:
  - Frame gaps
  - Black frames
  - Audio desync

**Sequential concatenation is preferred.**

---

## 8. Beat Map (Optional / Non-blocking)

- Beat Map may be merged
- Beat Map may be ignored
- Beat Map does **not** gate composition

It exists only as **advisory metadata** for future refinement.

---

## 9. Routing Logic (Avatar vs VO)

### Switch: `Avatar or VO`

Inputs:
- Merged data bundle

Rules:
- If avatar assets exist → route to **Avatar Host**
- Else → route to **VO Only**

This switch:
- Controls presentation style
- Does NOT affect validation or ordering

---

## 10. Video Composer (Current Focus Node)

**Status:** Actively being built

Responsibilities:
- Receive ordered clip URLs
- Receive VO URL
- Concatenate clips
- Overlay or sync VO
- Produce final narrative video

This node is the **current stopping point** of active development.

---

## 11. Explicit Non-Goals (Important)

This workflow does NOT:
- Regenerate scenes
- Enforce frame-perfect timing
- Correct upstream duration drift
- Perform creative editing

It assumes:
- Upstream generation is “good enough”
- Narrative continuity > micro-precision

---

## 12. Design Philosophy (Why This Works)

- Favor **robustness over fragility**
- Favor **sequence over timestamps**
- Favor **inclusive merges over strict joins**
- Fail fast, log clearly, move on

This keeps the pipeline:
- Debuggable
- Extensible
- Production-safe

---

## 13. Status Summary (Dec 27)

✅ Validation logic finalized  
✅ Merge strategy finalized  
✅ Routing logic finalized  
🟡 Video Composer implementation in progress  
⬜ Optional refinements deferred  

---

**This document is the authoritative context for all future work on `003A – Video Editor – Narrative`.**
