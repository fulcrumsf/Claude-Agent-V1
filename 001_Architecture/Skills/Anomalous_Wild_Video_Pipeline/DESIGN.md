---
title: "Anomalous Wild Video Pipeline — Design Spec"
type: design-spec
status: "⏳ pending review"
created: 2026-07-06
---

# 🐟 Anomalous Wild Video Pipeline — Design Spec

> ⚠️ **This is a design document, not a built skill yet.** Nothing described here has been implemented. Once Tony approves this spec, the next step is a detailed implementation plan, then building.

## 🎯 Purpose

Lock in one orchestrator skill for Anomalous Wild — `/anomalous-wild`, mirroring how `/reimagined-realms` works — **without throwing away what already works** for this channel, and **without touching or interfering with Reimagined Realms** in any way.

The goal is feature parity with Reimagined Realms: ideation → script → voiceover → shot list → assets → assembly → audio → YouTube package → Blotato upload, all through one command, with the science/diagram-heavy nature of this channel handled properly (the fix for the "AI slop" diagram problem this session diagnosed).

---

## ✅ What Already Exists and Gets Reused (not rebuilt)

Discovered this session — these are real, working pieces. The new skill wires into them; it does not replace them.

| Component | What it does | Status |
|---|---|---|
| `new_video.py` | Questionnaire + Perplexity research + folder scaffolding | ✅ Reused as-is |
| `Anomalous-Wild-Scriptwriter.md` | Script generation — "Anomalous Arc™" structure, its own voice ID/settings | ✅ Reused as-is |
| `pipeline_supervisor.py` + `pipeline_orchestrator.sh` | Batch live-footage generation, error-code-aware retries, notifications | ✅ Reused as-is |
| `check_pipeline_status.py` | Progress check | ✅ Reused as-is |
| `BioluminescenceDoc.tsx` (Remotion) | The channel's real assembly engine | ✅ Reused — new diagram/overlay work extends this, doesn't bypass it with raw ffmpeg like this session did |
| `Anomalous-Wild-Hybrid.md` | Visual/tone style guide | ✅ Reused as-is |
| `compose_audio.py`, `generate_stems.py`, `mix_stems.py`, `analyze_stems.py`, `render_video.py`, `generate_suno_music.py` | Stems/narration/Suno mixing, locked sidechain-duck formula, versioning | ✅ Built this session, already working — reused |

---

## 🆕 What's Genuinely New

| Component | Why it's needed |
|---|---|
| Word-level narration timestamps | Currently missing — RR has these from ElevenLabs, Anomalous Wild doesn't |
| Tooling Agent capability profile | Extends `Tool-Manager` skill with real, researched knowledge of Hyperframes/Remotion/video-use/Manim so it can route scene needs without being told which tool to use |
| Scientific Diagram sub-pipeline | Fixes the garbled-text diagram problem (see anglerfish example) |
| YouTube package generator | Title/description/thumbnail — mimics RR Phase 10 |
| Blotato upload | Mimics RR Phase 12 defaults |
| Clean folder structure | Both a going-forward standard AND a retrofit of the existing Bioluminescence Weapon folder |

---

## 🧩 Phase Breakdown

| # | Phase | Source |
|---|---|---|
| 1 | Intake + Ideation | ✅ Existing (`new_video.py`) |
| 2 | Script | ✅ Existing (`Anomalous-Wild-Scriptwriter.md`) |
| 3 | Voiceover | 🆕 Existing tool (ElevenLabs), upgraded to capture word-level timestamps |
| 4 | Beat table | 🆕 Narration chunked into beats (universal — same idea as RR) |
| 5 | Shot list / tool routing | 🆕 Orchestrator describes each beat's visual need in plain language to the Tooling Agent |
| 6 | Asset generation | Mix: live footage → `pipeline_supervisor.py` (✅ existing); diagrams/data-viz → 🆕 new sub-pipeline |
| 7 | Assembly | ✅ Existing Remotion engine (`BioluminescenceDoc.tsx`-style), extended for new scene types |
| 8 | Audio (stems/narration/music) | ✅ Built this session, reused unchanged |
| 9 | YouTube package | 🆕 New |
| 10 | Blotato upload | 🆕 New |

---

## ⏱️ Beat Table Rules

- **Universal:** every video gets a beat table derived from real narration timing (word-level timestamps once Phase 3 is upgraded) — same principle as RR, no exceptions.
- **Conditional 8-second cap:** applies **only** to beats routed to live-footage generation (Seedance/Veo via `pipeline_supervisor.py`) — same reasoning as RR (engagement pacing + generation model limits).
- **Diagram/data-viz beats have no length cap** — a beat can run 16s+ if the narration needs it, since it's one composed Remotion scene, not stitched generated clips.
- **🔒 Hard rule for diagram/data-viz beats regardless of length: no static frame for more than 3–5 seconds.** Something must always be changing — a new callout line drawing in, a new label appearing, a camera reframe/tighten. The beat can be long; the stillness never can.

---

## 🛠️ Tooling Agent (extends `Tool-Manager`, does not create a new agent)

- **No new agent.** Extends the existing, already-mandatory `Tool-Manager` skill, which is already the workspace's authority on "what tools do we have."
- **New data file:** `Tool-Manager/data/motion_graphics_capabilities.json` — sibling to the existing `model_capabilities.json`, but for composition tools instead of generation models.
- **⚠️ Every entry must be real research, never a guess.** Sources: each tool's own skill docs already in this workspace (`hyperframes`, `hyperframes-cli`, `hyperframes-media`, `video-use`, `remotion-best-practices`), plus actual precedent from this session (what worked for the creature overlays). Anything unverifiable gets flagged as unverified, not asserted.
- **How routing works:** the orchestrator sends a plain-language scene description ("angler fish fades in, becomes a labeled diagram, callout lines animate to organs"). Tool-Manager reasons over the capability profile and returns which tool(s) apply — sometimes more than one. This is judgment against real data, not a rigid lookup table.

| Tool | Best for (per research, not assumption) |
|---|---|
| **Remotion** | Precise coordinate placement, labeled diagrams, data-viz, overlay compositing — proven this session |
| **video-use** | Cutting real/generated footage to match narration timing |
| **Hyperframes** | Caption burn-in, audio-reactive motion, animated text emphasis |
| **Manim** | Pure equation/graph/algorithm animation |

---

## 🔬 Scientific Diagram Sub-Pipeline

Fixes the exact failure shown in the anglerfish reference image (garbled labels: "Ecca wega bulk," "Culora," "Bhuum stack").

1. **🔎 Research reference** — find a real reference image of the actual subject (Wikipedia, Google Images, Openverse) so anatomy is grounded in reality
2. **🎨 Generate clean illustration** — GPT-Image-2/Nano Banana recreates it in-style, using the reference as an anatomical guide, **explicit no-text/no-label negative prompt**
3. **📐 Vision coordinate pass** — a vision model looks at *that specific generated image* and returns real coordinates for each labeled feature ("esca: 62%,38%"). If it can't confidently locate something, it flags that — it does not guess.
4. **✍️ Remotion label placement** — labels + callout lines placed at the exact detected coordinates, animated in per beat timing, respecting the 3–5s max-static rule

**🎨 Styling is per-video, not fixed.** No locked color palette or line style reused across every diagram — the orchestrator judges good styling per video (informed by the same reference-image research from step 1), the same way a real designer would adapt style to context rather than reusing one template forever.

---

## 📦 YouTube Package + 🚀 Blotato Upload

Mimics Reimagined Realms Phase 10 / Phase 12 directly — same locked defaults pattern (privacy, madeForKids, etc.), same pause-for-final-selection behavior.

## 🏁 End Card — Locked

`end_card_v3.mp4` is now a **fixed, hardcoded asset** used at the end of every Anomalous Wild video, the same way RR has a fixed CTA asset. Not generated, not chosen per video.

---

## 📁 Folder Structure — Going Forward AND Retrofit

RR's actual pattern (Pompeii production), confirmed from disk:

```
Scripts/            Narration.md, Script.md
Production/          Beat_Table.md, Cost_Estimate.md, Shot_List.md, assemble_config.json
Images/              C01_0.0s-3.8s.png (clip-id + timecode naming)
Video_Clips/         C01_0.0s-3.8s.mp4 (same naming convention)
Narration_Audio/     Scene_01.mp3, Scene_02.mp3...
Audio_Stems/         per-scene SFX stems
Assembly/            raw_video.mp4, stems_mix.mp3, narration.mp3, music.mp3,
                     V1/, V2/, V3/... (versions live INSIDE Assembly, not as a sibling folder)
Package/             Text_Hooks.txt, Thumbnails/, YouTube_Package.md
```

**Corrections needed from this session:** the `Versions/` folder I created sits as a sibling to the production root — it should have been nested inside `Assembly/` (`Assembly/V1/`, etc.) to match RR's actual convention. Fixed as part of this work.

**✅ Going forward:** every new Anomalous Wild production uses this exact structure from day one.

**🔧 Retrofit (confirmed in scope):** Bioluminescence Weapon's current flat structure (40+ `scene_XX`/`scene_XXb` folders mixed with loose JSON manifests and render outputs at the root) gets migrated into this same typed layout. This requires:
- Mapping every existing `scene_XX` folder's `video.mp4`/`audio.mp3` into `Video_Clips/` / `Narration_Audio/` with consistent naming
- Updating every script/JSON that references the old paths (`scene_cut_sequences.json`, `ai_prompts.json`, `new_clips_prompts.json`, `pipeline_supervisor.py`'s hardcoded `BASE` path, `render_bioluminescence.sh`)
- This is real, higher-risk work (many file moves + reference updates in a folder with an already-shipped V4) — it gets its own careful implementation plan, not a quick pass

---

## 🧱 File Organization Convention

Small, single-purpose scripts — matching the pattern already established this session (`compose_audio.py`, `generate_stems.py`, `mix_stems.py`, `analyze_stems.py`, `render_video.py`, `generate_suno_music.py` as six separate files, not one monolith). New pieces (YouTube package generator, Blotato upload, diagram sub-pipeline steps, Tooling Agent profile builder) follow the same convention, living in `Tools/Video-Generation/Channels/Anomalous_Wild/`.

**Never touches:** any Reimagined Realms file. Everything Anomalous-Wild-specific gets its own duplicate if it needs to diverge from an RR original.

---

## 🚫 Non-Goals (explicit, out of scope for this spec)

- ❌ Rebuilding `pipeline_supervisor.py`, `new_video.py`, the scriptwriter skill, or `BioluminescenceDoc.tsx` — wired in as-is
- ❌ Touching any Reimagined Realms file
- ❌ Airtable-driven automation or auto-researched video ideas — **deferred until ~10 validated Anomalous Wild videos have run through this pipeline manually**, matching the same validation gate already planned for Reimagined Realms

## 🔭 Broader Context (informs scope, not part of this build)

Tony plans ~12 YouTube channels total. Each will likely get its own pipeline duplicated from this same core pattern, with per-channel tweaks (some channels may skip narration entirely, use different story arcs, different pacing). The core mechanics (beat table → tool routing → assembly → audio mix → package → upload) are meant to stay consistent across channels; only the channel-specific pieces (scriptwriter voice/structure, visual style, narration on/off) change. Anomalous Wild is the second full implementation of this pattern after Reimagined Realms — worth keeping in mind for how reusable vs. channel-specific pieces get separated in the eventual build, but not a requirement to design for yet.

---

## 📋 Open Questions for Implementation Planning (not blocking this spec's approval)

- Exact vision model to use for the coordinate-detection pass (Gemini vs. other) — needs live Tool-Manager check at build time, not decided here
- Exact retrofit migration mapping for Bioluminescence Weapon's existing scene folders — needs a full file inventory pass before the implementation plan is written
