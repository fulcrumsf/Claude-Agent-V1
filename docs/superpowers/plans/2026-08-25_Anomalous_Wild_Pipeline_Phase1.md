# Anomalous Wild Pipeline — Retrospective Fixes (Phase 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lock in the decisions from the 2026-08-24/25 Mantis Shrimp retrospective into the real Anomalous Wild pipeline code and docs — simplify the intake questionnaire, lock the default voice/video-model, remove the "one mandatory assembly tool" constraint, wire in visual-variety and NotebookLM research steps, and clean up leftover cross-channel/stale references. This is Phase 1 of a two-phase update; Phase 2 (a separate, unrelated update) is out of scope here.

**Architecture:** No new subsystems. This is a set of surgical edits to existing files: the intake script (`new_video.py`), the orchestrator doc (`Anomalous_Wild_Video_Pipeline/SKILL.md`), the video-generation dispatcher (`pipeline_supervisor.py`), and two audio scripts with stale docstrings. Each task is independently deployable — none depend on a shared new module.

**Tech Stack:** Python 3 (`questionary`, `requests`), Markdown pipeline docs, ffmpeg. No test framework exists in this codebase — verification is done by direct execution/inspection (dry-run the script, grep the edited doc, re-read the diff), not pytest.

**Spec:** `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/Pipeline_Improvements_TODO.md` (decisions) and `Mantis_Shrimp_Iteration_Log.md` (source iteration data) — both already reviewed and approved by Tony; this plan implements them as-is, no further design questions.

## Global Constraints

- Default video model for all live-footage beats: **Seedance 1.5 Pro, 1080p, via kie.ai.** No fixed backup chain — switch models manually/as-needed, never pre-set a fallback order.
- Default/locked ElevenLabs voice for every Anomalous Wild video: `KYhuk3Y57IlkV1ZjtDAt`. Change only by an explicit future hardcode edit, never a per-run question.
- No single assembly tool (Remotion, ffmpeg, HyperFrames, video-use) is mandatory — whichever tool suits a given job does that job; diagram scenes may be built independently of live-footage scenes and stitched together at the end.
- CTA is never asked as a free-text question — always one of 3 fixed lines, picked at random per production: "Subscribe for more wild animal facts." / "Follow along for more strange creatures like this one." / "Hit subscribe — nature gets weirder from here."
- Never leave two contradictory instructions standing in the same doc after an edit — when a method changes, the old method's language must be removed/marked superseded, not left alongside the new one.

---

## File Structure

| File | Responsibility | Change type |
|---|---|---|
| `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/new_video.py` | Intake questionnaire | Modify — remove 5 of 8 questions, lock voice/CTA |
| `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md` | Pipeline orchestration doc | Modify — 7 separate section edits (Phase 1, 3, 5B, 6A, 7, 8) |
| `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/pipeline_supervisor.py` | Video-clip generation dispatcher | Modify — add `generate_seedance()`, wire into dispatch |
| `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/compose_audio.py` | Audio brief composer | Modify — fix stale docstring (says "Reimagined Realms") |
| `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/analyze_stems.py` | LUFS analysis | Modify — fix stale music-bed target (-28 → -26) |

**Already correct, no change needed (confirmed during planning, do not re-touch):**
- Character-sheet variety is already implemented via `Production-Asset-Planner` ("multiple character-sheet variants for natural variety," SKILL.md line 148).
- `notebooklm` skill's capability list is already complete (slide deck, video overview, infographic, data table, flashcards, mind map, report, audio overview all documented) — the gap is integration, not documentation, hence Task 10 below only adds a pipeline invocation, not a skill-doc fix.
- Diagram animation default (Approach B / Motion-Graphics-Compositing) is already locked correctly in SKILL.md Phase 6B Step 5.
- Audio-continuity raw-PCM+numpy verification method is already fully documented in SKILL.md Phase 8.
- Standard LUFS targets (-14 narration / -26 music / -20 ambient) are already consistent in SKILL.md Phase 8 — only `analyze_stems.py`'s docstring disagrees (Task 8).

---

### Task 1: Simplify `new_video.py` intake questionnaire

**Files:**
- Modify: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/new_video.py`

**Interfaces:**
- Produces: `run()` still calls `scaffold_project(...)` with the same parameter names, but `answers` dict loses `"voiceover_tone"` and `"music_mood"` keys and gains nothing new; `cta` is now chosen internally, not typed by the user; a new module-level constant `VOICE_ID` and `CTA_LINES` are introduced for later tasks (SKILL.md Task 2/5) to reference by name.

- [ ] **Step 1: Add locked constants and remove now-unused constants**

Replace lines 80-88 (`VOICEOVER_TONES` and `DURATION_OPTIONS_*`) — keep `DURATION_OPTIONS_LONG`/`DURATION_OPTIONS_SHORT`, drop `VOICEOVER_TONES` and `MUSIC_MOODS` (lines 69-85), and add the new locked constants:

```python
VOICE_ID = "KYhuk3Y57IlkV1ZjtDAt"  # locked Anomalous Wild ElevenLabs voice — change only by editing this constant directly, never per-run

CTA_LINES = [
    "Subscribe for more wild animal facts.",
    "Follow along for more strange creatures like this one.",
    "Hit subscribe — nature gets weirder from here.",
]

DURATION_OPTIONS_LONG  = ["3–5 min", "5–8 min", "8–12 min"]
DURATION_OPTIONS_SHORT = ["< 30s", "30–60s"]
```

- [ ] **Step 2: Simplify the `run()` questionnaire body**

Replace the block from `# ── 1. Channel ──` (line 440) through `# ── 7. CTA ──` ... `sys.exit(0)` (line 514) with:

```python
    # ── 1. Channel (locked — this tool is Anomalous Wild only) ──────────────
    channel = next(c for c in CHANNELS if c["id"] == "001_anomalous_wild")
    print(f"\n  ✓ Channel: {channel['name']} ({channel['id']})")

    # ── 2. Format ──────────────────────────────────────────────────────────
    fmt_default = "Long-form (16:9 horizontal)"
    fmt_choices = ["Long-form (16:9 horizontal)", "Short (9:16 vertical)"]

    format_answer = questionary.select(
        f"Format?  [default: {fmt_default}]",
        choices=fmt_choices,
        default=fmt_default,
    ).ask()
    if not format_answer:
        sys.exit(0)

    is_short     = "short" in format_answer.lower() or "9:16" in format_answer
    format_label = format_answer

    # ── 3. Duration ────────────────────────────────────────────────────────
    dur_choices = DURATION_OPTIONS_SHORT if is_short else DURATION_OPTIONS_LONG
    duration = questionary.select(
        "Estimated duration?",
        choices=dur_choices,
    ).ask()
    if not duration:
        sys.exit(0)

    # ── 4. Narration, voice, music mood, Suno — all locked, never asked ─────
    has_vo        = True
    vo_tone       = ""
    music_moods   = []  # derived from script tone during editing, not selected here
    suno_enabled  = True

    # ── 5. CTA — picked at random from the locked rotation, never typed ─────
    import random
    cta = random.choice(CTA_LINES)
    print(f"  ✓ CTA (auto-picked): {cta}")
```

Note: `import random` at the top of `run()` is fine stylistically here since it's the only place it's used; if preferred, move it to the top-level imports (line 33 area) instead — either is acceptable, keep consistent with the rest of the file's import style (top-level is cleaner; do that instead of the inline import shown above).

- [ ] **Step 3: Move `import random` to top-level imports**

In the imports block (around line 33), add:
```python
import random
```
Then remove the inline `import random` from Step 2's block.

- [ ] **Step 4: Update `scaffold_project()`'s config dict to store the locked voice ID**

In `scaffold_project()`, in the `config` dict (around line 405-424), change:
```python
        "voiceover": answers.get("voiceover", True),
        "voiceover_tone": answers.get("voiceover_tone", ""),
        "music_mood": answers.get("music_mood", []),
```
to:
```python
        "voiceover": True,
        "voice_id": VOICE_ID,
        "music_mood": [],  # derived from script tone during editing, not asked at intake
```

- [ ] **Step 5: Update the `answers` dict built before `scaffold_project()` is called**

Around line 575-581, change:
```python
    answers = {
        "format":        format_label,
        "duration":      duration,
        "voiceover":     has_vo,
        "voiceover_tone": vo_tone,
        "music_mood":    music_moods,
    }
```
to:
```python
    answers = {
        "format":   format_label,
        "duration": duration,
    }
```
(`has_vo`, `vo_tone`, `music_moods` are now unused after Step 2 — remove those three local variables from Step 2's block entirely rather than assigning them, since Step 4/5 no longer read them. Revise Step 2's block to drop `has_vo = True`, `vo_tone = ""`, `music_moods = []` — they were only needed to explain what's locked; nothing downstream reads them anymore.)

- [ ] **Step 6: Update the module docstring to reflect the simplified questionnaire**

Replace the docstring (lines 1-27) description of what the script does — after "Runs a terminal questionnaire," add a note:
```python
"""
tools/new_video.py

Entry point for a new Anomalous Wild video. Runs a short terminal
questionnaire (format + duration only — narration, voice, music mood,
Suno, and CTA are all locked defaults, not asked), researches viral
ideas via Perplexity (using channel case studies for context), lets you
pick one idea, then scaffolds the project folder.
...
"""
```
(Keep the rest of the docstring — folder layout — unchanged.)

- [ ] **Step 7: Verify by dry-running the questionnaire**

Run:
```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/new_video.py
```
Expected: only two prompts appear (Format, then Estimated duration), followed immediately by "✓ CTA (auto-picked): ..." printed to the terminal and the Perplexity research phase starting. No channel/voiceover/tone/music-mood/Suno/CTA-text prompts appear. Press Ctrl-C once confirmed (no need to complete a full scaffold for this check).

- [ ] **Step 8: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/new_video.py
git commit -m "feat(anomalous-wild): lock voice/CTA/narration defaults, simplify intake to format+duration only"
```

---

### Task 2: SKILL.md Phase 1 Step A — document the real (simplified) questionnaire, and Step A2 — remove the model-family question

**Files:**
- Modify: `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md:33` and `:41-51`

**Interfaces:**
- Consumes: `VOICE_ID` constant name from Task 1 (referenced by name only, not imported — this is a Markdown doc).

- [ ] **Step 1: Replace the vague Step A description (line 33) with the real questionnaire list**

Find:
```
This runs the interactive questionnaire and Perplexity-backed topic research for the `001_anomalous_wild` channel entry, using existing case studies (`002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Case_Studies/`) for context. Answer the channel/format prompts as `Anomalous Wild` / `long` (16:9) unless Tony specifies otherwise.
```
Replace with:
```
This runs a short interactive questionnaire and Perplexity-backed topic research for Anomalous Wild, using existing case studies (`002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Case_Studies/`) for context. As of 2026-08-25 the questionnaire asks only two questions — everything else is a locked default, not a per-run question:

- **Format?** — Long-form (16:9) or Short (9:16). Default: Long-form, unless Tony specifies otherwise.
- **Estimated duration?** — 3–5 min / 5–8 min / 8–12 min (long-form), or <30s / 30–60s (short).

Locked, never asked: narration is always on; voice is always `KYhuk3Y57IlkV1ZjtDAt` (see Phase 3); music mood is derived from the script's tone during editing, never selected up front; a Suno score is always generated by default (Tony says explicitly if one should be skipped for a given video); the CTA is auto-picked at random from a fixed 3-line rotation (see Phase 7's end-card CTA section) — the channel question itself no longer appears, since this tool only ever scaffolds Anomalous Wild.
```

- [ ] **Step 2: Replace Step A2 (video model selection) — remove the per-run question, state the silent default**

Find the full Step A2 block (lines 41-51, from `### Step A2 — Video model selection` through `Store \`video_model_family\`...`). Replace with:

```
### Step A2 — Video model default (locked 2026-08-25, no question asked)

**Default: Seedance 1.5 Pro, 1080p, via kie.ai — for every live-footage beat, every production.** Do not ask Tony which model family to use; do not pre-set a fallback chain (there is no "Seedance 2.0 as backup, then Veo3" order — that was considered and explicitly rejected 2026-08-25). If a specific beat or scene needs a different model, Tony will say so explicitly in the moment; switch for that beat only, then return to the default for the next one.

Store `video_model_family = "seedance"` unconditionally at this step — every later phase reads this instead of asking again.
```

- [ ] **Step 3: Verify no other section references the removed model-family question**

Run:
```bash
grep -n "video_model_family\|Step A2\|which video model" /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md
```
Expected: only the new Step A2 block and any later `video_model_family` reads (Phase 6A) remain — no leftover text asking Tony to pick a family.

- [ ] **Step 4: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md
git commit -m "docs(anomalous-wild): document simplified intake questionnaire, remove per-run model question"
```

---

### Task 3: SKILL.md Phase 3 — lock the ElevenLabs voice ID

**Files:**
- Modify: `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md:89-100`

- [ ] **Step 1: Replace the voice-confirmation instruction**

Find:
```
```bash
source /Users/tonymacbook2025/.env-secrets
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_narration_with_timestamps.py \
  "[production_folder]" \
  "<voice_id>"
```

Confirm the correct Anomalous Wild ElevenLabs voice ID with Tool-Manager or Tony before running — do not reuse Reimagined Realms' voice ID (`raMcNf2S8wCmuaBcyI6E`) by default; that voice belongs to RR's narrator persona, not this channel's.
```
Replace with:
```
```bash
source /Users/tonymacbook2025/.env-secrets
python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_narration_with_timestamps.py \
  "[production_folder]" \
  "KYhuk3Y57IlkV1ZjtDAt"
```

**Locked voice (2026-08-25): `KYhuk3Y57IlkV1ZjtDAt`** — this is the permanent Anomalous Wild voice for every video, same treatment as Reimagined Realms' hardcoded voice. Do not confirm/ask each run. Do not reuse Reimagined Realms' voice ID (`raMcNf2S8wCmuaBcyI6E`) — that belongs to RR's narrator persona. To change the AW voice in the future, edit this constant directly (and `new_video.py`'s `VOICE_ID`, Task 1) rather than asking per-run.
```

- [ ] **Step 2: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md
git commit -m "docs(anomalous-wild): lock ElevenLabs voice ID in Phase 3, stop asking per-run"
```

---

### Task 4: SKILL.md Phase 7 — remove the mandatory-Remotion constraint

**Files:**
- Modify: `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md:239-247`

- [ ] **Step 1: Replace the Phase 7 opening paragraph**

Find:
```
Assembly runs through the channel's real engine — never raw ffmpeg concatenation. The pattern is `BioluminescenceDoc.tsx`-style: a Remotion composition per production that pulls in generated clips, illustrated diagrams with `DiagramLabels` overlays, and title/end cards as React components, not a hand-stitched video file.

```
002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/[NNNN]_[Title_Case_Slug]/Remotion/
```

For each production, create a Remotion composition following the `BioluminescenceDoc.tsx` pattern (confirmed precedent at `002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/0001_Bioluminescence_Weapon/Remotion/BioluminescenceDoc.tsx`), extended to include `DiagramLabels` scenes for any Phase 6B beats. Do not bypass this engine with a manual ffmpeg concat, even for a "quick" assembly — that was a mistake corrected earlier this session.
```
Replace with:
```
**No single tool is the mandatory final assembler (revised 2026-08-25).** Remotion, ffmpeg, video-use, and HyperFrames are all available — whichever tool actually suits a given job does that job. A live-footage-heavy production may assemble cleanly via direct ffmpeg concat; a diagram-heavy scene may be built independently as component assets (Phase 6B, Motion-Graphics-Compositing) and stitched in afterward; Remotion remains the right choice when a scene genuinely needs React-composed overlays (e.g. `DiagramLabels`). Decide per production, and per scene within a production, rather than defaulting to one engine for everything.

When a Remotion composition is the right call for a given production, follow the `BioluminescenceDoc.tsx` pattern (precedent: `002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/0001_Bioluminescence_Weapon/Remotion/BioluminescenceDoc.tsx`), saved to:
```
002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/[NNNN]_[Title_Case_Slug]/Remotion/
```
extended to include `DiagramLabels` scenes for any Phase 6B beats still using that method. When ffmpeg or another tool is the right call instead, no `Remotion/` folder is required for that production — do not treat its absence as an error.
```

- [ ] **Step 2: Update the FINAL DELIVERY checklist to make the Remotion folder conditional**

Find (around line 369-370):
```
├── Remotion/               ✓ BioluminescenceDoc.tsx-style composition,
│                            incl. DiagramLabels overlays for diagram beats
```
Replace with:
```
├── Remotion/               ✓ (if used for this production) BioluminescenceDoc.tsx-style
│                            composition, incl. DiagramLabels overlays for diagram beats
```

- [ ] **Step 3: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md
git commit -m "docs(anomalous-wild): remove mandatory-Remotion constraint from Phase 7, tool choice is per-job"
```

---

### Task 5: SKILL.md Phase 7 — lock the end-card CTA to the 3-line rotation

**Files:**
- Modify: `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md` (end-card CTA paragraph, currently ~line 262 pre-Task-4-edit; re-locate by content match after Task 4's edit shifts line numbers)

- [ ] **Step 1: Replace the CTA wording instruction**

Find:
```
**End card CTA voiceover — standard step (locked 2026-08-24), not optional polish.** The end card visually says "Like, Comment" but has no spoken call to action and, left unaddressed, plays under complete audio silence (confirmed on 0002_Mantis_Shrimp_Color_Vision — the narration/music mix stops right at the end-card boundary with nothing filling the remaining ~10s). Generate a short line ("Follow for more content like this," "Subscribe for more content like this," or similar) via ElevenLabs using the same `voice_id` as the production's narration (check `Data/Generation_Log.json` for the voice_id already used), and mix it into the end-card audio starting ~1-1.5s in (after the card's own text has begun animating), with its own short tail fade so it doesn't clip. Verify duration fits inside the end card's own runtime before finalizing.
```
Replace with:
```
**End card CTA voiceover — standard step (locked 2026-08-24, wording locked 2026-08-25).** The end card visually says "Like, Comment" but has no spoken call to action and, left unaddressed, plays under complete audio silence (confirmed on 0002_Mantis_Shrimp_Color_Vision — the narration/music mix stops right at the end-card boundary with nothing filling the remaining ~10s). The spoken line is picked at random by `new_video.py` at intake (Task 1's `CTA_LINES`, stored in `project_config.json`/`Production/` as `cta`) from this fixed 3-line rotation — never write a new line, never ask Tony to type one:
- "Subscribe for more wild animal facts."
- "Follow along for more strange creatures like this one."
- "Hit subscribe — nature gets weirder from here."

Generate that stored `cta` line via ElevenLabs using the locked voice `KYhuk3Y57IlkV1ZjtDAt` (Phase 3), and mix it into the end-card audio starting ~1-1.5s in (after the card's own text has begun animating), with its own short tail fade so it doesn't clip. All 3 lines are well under 10s spoken (~2.5-3.5s each at 150 wpm) — verify duration still fits inside the end card's own runtime before finalizing.
```

- [ ] **Step 2: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md
git commit -m "docs(anomalous-wild): lock end-card CTA to fixed 3-line rotation"
```

---

### Task 6: Wire Seedance into `pipeline_supervisor.py`'s dispatch logic

**Files:**
- Modify: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/pipeline_supervisor.py`

**Interfaces:**
- Consumes: `kie_headers()`, `kie_poll()`, `extract_video_url()`, `_classify_kie_response()`, `log()` — all already defined earlier in this file (used identically by `generate_veo3`/`generate_kling`, lines 201-287).
- Produces: `generate_seedance(entry: dict) -> dict` — same return contract as `generate_veo3`/`generate_kling`: `{"ok": True, "url": ...}` or `{"ok": False, "error_category": ..., "reason": ...}`.

- [ ] **Step 1: Add `generate_seedance()` after `generate_kling()` (after line 287)**

```python
def generate_seedance(entry: dict) -> dict:
    """Submit Seedance 1.5 Pro job via kie.ai createTask. Returns {ok, url, error_category} or {ok:False, reason, error_category}."""
    try:
        resp = requests.post(
            "https://api.kie.ai/api/v1/jobs/createTask",
            headers=kie_headers(),
            json={
                "model": "bytedance/seedance-1.5-pro",
                "input": {
                    "prompt": entry["video_prompt"],
                    "image_urls": [
                        url for url in [
                            entry.get("start_frame_url"),
                            entry.get("end_frame_url"),
                        ] if url
                    ],
                    "resolution": "1080p",
                    "duration": str(entry.get("duration_s", 8)),
                    "aspect_ratio": entry.get("aspect_ratio", "16:9"),
                    "generate_audio": entry.get("generate_audio", True),
                },
            },
            timeout=30,
        )
    except requests.exceptions.ConnectionError as e:
        return {"ok": False, "error_category": "RETRY", "reason": f"Network error: {e}"}
    except requests.exceptions.Timeout:
        return {"ok": False, "error_category": "RETRY", "reason": "Request timed out"}

    try:
        body = resp.json()
    except Exception:
        body = {}

    category, reason = _classify_kie_response(resp.status_code, body)
    if category != "OK":
        return {"ok": False, "error_category": category, "reason": reason}

    nested  = body.get("data") or {}
    task_id = body.get("taskId") or nested.get("taskId")
    if not task_id:
        return {"ok": False, "error_category": "UNKNOWN", "reason": f"No taskId in response: {str(body)[:200]}"}

    log(f"  Seedance task: {task_id}")
    result = kie_poll(task_id, "/api/v1/jobs/recordInfo")
    if not result["ok"]:
        return result

    url = extract_video_url(result["data"])
    return {"ok": True, "url": url} if url else {"ok": False, "error_category": "RETRY", "reason": "No URL in completed response"}
```

Note: `start_frame_url`/`end_frame_url` field names must match whatever `entry` dict keys the clip-manifest/prompt-manifest actually uses for the two GPT-Image-2 reference frames (per SKILL.md Phase 6A's reference table: Seedance 1.5 Pro takes start frame + end frame only). If the existing manifest schema uses different key names, adjust the two `entry.get(...)` calls to match — check `Production/new_clips_prompts.json`'s actual keys for one existing entry before finalizing this step.

- [ ] **Step 2: Change the model default and dispatch branch (lines 536-537 and 558)**

Find:
```python
        model    = entry.get("model", "kling_v2")
        is_veo   = "veo" in model.lower()
```
Replace with:
```python
        model       = entry.get("model", "bytedance/seedance-1.5-pro")
        model_lower = model.lower()
        is_veo      = "veo" in model_lower
        is_seedance = "seedance" in model_lower or "bytedance" in model_lower
```

Find (line 558):
```python
                result = generate_veo3(entry) if is_veo else generate_kling(entry)
```
Replace with:
```python
                if is_veo:
                    result = generate_veo3(entry)
                elif is_seedance:
                    result = generate_seedance(entry)
                else:
                    result = generate_kling(entry)
```

- [ ] **Step 3: Verify the dispatch logic manually**

Run:
```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
python3 -c "
import sys
sys.path.insert(0, '001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild')
import pipeline_supervisor as ps
assert hasattr(ps, 'generate_seedance'), 'generate_seedance not defined'
print('generate_seedance defined OK')
"
```
Expected: `generate_seedance defined OK`, no import errors.

- [ ] **Step 4: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/pipeline_supervisor.py
git commit -m "feat(anomalous-wild): add Seedance 1.5 Pro dispatch, make it the default model in pipeline_supervisor"
```

---

### Task 7: Fix `compose_audio.py`'s stale "Reimagined Realms" docstring

**Files:**
- Modify: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/compose_audio.py:1-20`

- [ ] **Step 1: Replace the docstring header**

Find:
```python
"""
compose_audio.py — Vision-based per-scene audio composer for Reimagined Realms productions.
```
Replace with:
```python
"""
compose_audio.py — Vision-based per-scene audio composer for Anomalous Wild productions.
```

- [ ] **Step 2: Verify no other "Reimagined Realms" references remain in this file**

Run:
```bash
grep -n -i "reimagined realms\|reimagined_realms" /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/compose_audio.py
```
Expected: no output.

- [ ] **Step 3: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/compose_audio.py
git commit -m "fix(anomalous-wild): correct compose_audio.py docstring, was still labeled Reimagined Realms"
```

---

### Task 8: Fix `analyze_stems.py`'s stale music-bed LUFS target

**Files:**
- Modify: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/analyze_stems.py:25-28`

- [ ] **Step 1: Correct the docstring's target LUFS reference**

Find:
```python
Target LUFS reference:
  SFX bed base:   -20 LUFS  (leaves headroom for narration)
  Narration:      -14 LUFS  (YouTube standard — sits clearly on top)
  Music bed:      -28 LUFS  (ambient, never competes)
```
Replace with:
```python
Target LUFS reference (matches the locked standard in Anomalous_Wild_Video_Pipeline/SKILL.md Phase 8):
  SFX bed base:   -20 LUFS  (leaves headroom for narration)
  Narration:      -14 LUFS  (YouTube standard — sits clearly on top)
  Music bed:      -26 LUFS  (~12dB below narration, never competes)
```

- [ ] **Step 2: Verify no other -28 references remain in this file**

Run:
```bash
grep -n -- "-28" /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/analyze_stems.py
```
Expected: no output.

- [ ] **Step 3: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/analyze_stems.py
git commit -m "fix(anomalous-wild): correct analyze_stems.py music-bed LUFS docstring, -28 was stale"
```

---

### Task 9: Wire the visual-variety mechanism into SKILL.md Phase 5B

**Files:**
- Modify: `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md` (Phase 5B section, the `**Anomalous-Wild-specific storyboard style**` paragraph)

- [ ] **Step 1: Insert a new subsection immediately after the existing `**Anomalous-Wild-specific storyboard style (locked 2026-08-17, still applies):**` paragraph**

Find the end of that paragraph (ends with `...Run the mandatory character-sheet count-check on every generated storyboard before presenting it to Tony, per Storyboard-Generation's own requirement.`) and insert directly after it:

```

**Visual variety mechanism (locked 2026-08-25) — the director role.** The agent planning shot composition for this channel acts as the director/cinematographer — BBC-style nature documentary, in the tradition of the channel's own case studies (`Case_Studies/`) and the Cinematic Style Guide's "Wildlife" methodology (`002_Content-Creation/Video_Editor/002_Channels/Styles/CINEMATIC_STYLE_GUIDE.md`) — making shot-variety calls independently, not deferring them to Tony. Tony reviews finished videos to refine this judgment over iterations; he does not hand-pick variety per shot.

Two-tier mechanism, applied when building each scene's storyboard:

1. **Fixed universal pool — rotate every shot, don't repeat the same combo back-to-back:**
   - Camera angle / shot type: wide, close-up, medium shot, low angle, high angle, macro.
   - Framing/composition: centered/symmetrical, rule-of-thirds off-center, negative-space-heavy, tight/filled frame, depth-layered foreground.
2. **Director's own research-driven judgment — NOT a fixed list, decided per-production from real research, not arbitrary randomization:**
   - Environment specifics (region/reef/habitat — driven by where the real subject actually lives, sourced from Production-Research-Agent's Phase 1 Step A3 output).
   - Lighting/weather/time-of-day (driven by what's realistic for that environment).
   - Subject natural variation (real color/pattern variation within the species, if factually accurate).

**Explicitly pull from case studies and the Cinematic Style Guide for this, not just at topic-ideation time (Phase 1).** Case studies teach craft — how good documentaries tell a story through shot selection and pacing — they are inspiration, never a template to copy. Read `CINEMATIC_STYLE_GUIDE.md`'s Wildlife style (shallow DOF, warm grading, "beauty shot" rule) as a direct input to shot planning at this step, not a separately-maintained doc the AW pipeline never opens.

Do NOT achieve variety by recoloring the creature/character itself — no biological basis for that. Vary the environment, lighting, and camera treatment around it instead.
```

- [ ] **Step 2: Verify the insertion landed in the right place**

Run:
```bash
grep -n "Visual variety mechanism\|character-sheet count-check on every generated storyboard" /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md
```
Expected: the "character-sheet count-check" line appears immediately before the "Visual variety mechanism" line.

- [ ] **Step 3: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md
git commit -m "docs(anomalous-wild): add visual-variety director mechanism to Phase 5B, wire in case studies + style guide"
```

---

### Task 10: Add NotebookLM as a research-phase step

**Files:**
- Modify: `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md` (Phase 1, Step A3)

- [ ] **Step 1: Extend Step A3 with a NotebookLM sub-step**

Find:
```
### Step A3 — Kick off Production-Research-Agent (new, 2026-08-18)

Immediately after the topic is picked (in parallel with Step A2), invoke the [`Production-Research-Agent`](../Production-Research-Agent/SKILL.md) skill with `chosen_topic` and `production_folder`. It gathers topic facts, reference images (capped 20), and Pexels B-roll footage (capped 10 clips, 1080p 16:9 only, analyzed and inventoried) — all before scriptwriting starts, so Phase 5B/Production-Asset-Planner has real material to check against once beats exist. Do not proceed to Step B until this completes.
```
Replace with:
```
### Step A3 — Kick off Production-Research-Agent + NotebookLM (Production-Research-Agent added 2026-08-18, NotebookLM added 2026-08-25)

Immediately after the topic is picked (in parallel with Step A2), invoke the [`Production-Research-Agent`](../Production-Research-Agent/SKILL.md) skill with `chosen_topic` and `production_folder`. It gathers topic facts, reference images (capped 20), and Pexels B-roll footage (capped 10 clips, 1080p 16:9 only, analyzed and inventoried) — all before scriptwriting starts, so Phase 5B/Production-Asset-Planner has real material to check against once beats exist.

Also invoke the `notebooklm` skill on the same topic, once the Production-Research-Agent's gathered sources are available to feed it: generate a report (`notebooklm generate report --format briefing-doc`) synthesizing the topic facts into a structured briefing doc, and save its output to `Research/NotebookLM_Briefing.md`. This adds grounding material on top of Topic_Facts.md, not a replacement for it — more real, varied reference material up front produces better downstream shot/script/diagram quality (the same principle behind Task 9's visual-variety mechanism and the character-sheet-variety decision). This step is not mandatory-forced on every production if NotebookLM is unavailable/rate-limited that session — skip and proceed with Production-Research-Agent's output alone if it fails, log the skip, don't block the pipeline on it.

Do not proceed to Step B until Production-Research-Agent completes (NotebookLM's report may still be finishing in the background if it's a longer-running artifact type — do not block on it specifically, only on Production-Research-Agent).
```

- [ ] **Step 2: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md
git commit -m "docs(anomalous-wild): add NotebookLM research-phase step to Phase 1 Step A3"
```

---

### Task 11: Add the continuity/anatomy-flagging cost-control rule

**Files:**
- Modify: `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md` (Phase 6A, end of section, before Phase 6B begins)

- [ ] **Step 1: Insert a new subsection at the end of Phase 6A (immediately before `### 6B — Diagram/data-viz beats`)**

Insert:
```

**Continuity/anatomy flagging — cost-control rule (locked 2026-08-25).** When a review pass (Video-Analyzer or manual) flags a possible continuity/anatomy issue in a generated clip (e.g. a limb/feature that looks inconsistent between shots), do NOT automatically regenerate that clip via Seedance/Veo to try to fix it — that spends money re-rendering something that may not even be a real issue (flagging has proven unreliable in practice; a flagged issue was reviewed and found not actually present on 0002_Mantis_Shrimp_Color_Vision). Instead: leave the clip as-is, log the flag with a description and timestamp to `Production/Continuity_Flags.md`, and surface it to Tony for review rather than acting on it automatically. This is a training-phase rule — Tony expects to review flags like this across roughly the next 15 productions; once the pipeline is reliably near-error-free, this level of per-flag human review is expected to be relaxed (see also Phase 5B's visual-variety mechanism, which is under the same "review now to earn autonomy later" framing).
```

- [ ] **Step 2: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md
git commit -m "docs(anomalous-wild): add continuity-flagging cost-control rule to Phase 6A"
```

---

## Self-Review Notes (completed during plan authoring)

- **Spec coverage:** every "DECIDED" item in `Pipeline_Improvements_TODO.md` maps to a task above (Task 1: narration/voice/music/Suno/CTA; Task 2/6: Seedance default + no fallback chain; Task 4: tool-agnostic assembly; Task 5: CTA rotation; Task 9: visual variety + case-study/style-guide wiring; Task 10: NotebookLM; Task 11: continuity cost-control; Task 3: voice lock; Task 7/8: stale-doc cleanup). Items already confirmed correct in the codebase (character-sheet variety, notebooklm capability docs, diagram animation default, audio-continuity method, LUFS consistency in SKILL.md) are explicitly called out as "no change needed" in the File Structure section so no task duplicates them.
- **Placeholder scan:** no TBD/TODO markers; every step shows exact before/after text or real code.
- **Type consistency:** `generate_seedance()` (Task 6) matches the exact return contract (`{"ok": ..., "url": ...}` / `{"ok": False, "error_category": ..., "reason": ...}`) used by `generate_veo3`/`generate_kling` in the same file. `VOICE_ID`/`CTA_LINES` (Task 1) are referenced by value (not import) in SKILL.md's Markdown (Tasks 3/5) since SKILL.md is documentation, not code — consistent given the file types involved.
- **Scope check:** Phase 2 (the separate, unrelated update Tony mentioned) is explicitly out of scope and not anticipated anywhere in this plan.
