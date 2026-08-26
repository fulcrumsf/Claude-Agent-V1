---
name: Reimagined_Realms_Video_Pipeline
description: "Invoke when Tony says /reimagined-realms, make a Reimagined Realms video, build me a video for the history channel, run the video pipeline, or start the RR pipeline. Orchestrates the full 12-phase faceless YouTube video production start to finish: channel analysis → story ideation (DAIPBR + 7-part) → script → beat table → cost estimate (3 combos) → ElevenLabs voiceover → beatmap (incl. fixed CTA hold beat) → shot list → YouTube package → image/video generation → assembly (with automatic CTA gap+audio append) → Blotato YouTube upload. This skill IS the orchestrator — no Higgsfield subscription needed. <example>User: /reimagined-realms Assistant: starts PHASE 1 INTAKE — asks 5 questions in one message</example> <example>User: make me a Reimagined Realms video about ancient Rome Assistant: starts PHASE 1 INTAKE but pre-fills topic context from user message</example>"
trigger: User invokes /reimagined-realms or asks to produce a Reimagined Realms video
---

# Reimagined Realms — Video Pipeline Skill

You are the orchestrator for the Reimagined Realms faceless YouTube channel.
Work through all 12 phases in order, start to finish — from topic ideation through the live Blotato YouTube upload. Never skip phases and never stop at "here are your files, next steps are manual" — this skill executes the full pipeline. Explicit pauses are built in at topic selection (Phase 3), cost combo approval (Phase 6), clip quality check (Phase 11), and title/thumbnail/privacy selection (Phase 12) — stop and wait for Tony at each.

**Output folder for this run** (create at Phase 4):
```
/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Productions/[topic-slug]/
```
Replace `[topic-slug]` with a kebab-case slug from the chosen topic (e.g., `pompeii-final-hours`).

---

## PHASE 1 — INTAKE

Ask all five questions in a single message. Do not proceed until Tony answers.

```
To get started, I need five things:

1. Which YouTube channel should I analyze for topic and style reference?
   (Press Enter for default: Brightside — https://www.youtube.com/@BRIGHTSIDEOFFICIAL/videos)

2. Aspect ratio: 16:9 (landscape) or 9:16 (shorts/vertical)?

3. How long should the final video be? (e.g., 5 minutes, 8 minutes)

4. Which model should write the script?
   A) Claude Opus 4.8 — best narrative depth and storytelling [recommended]
   B) Claude Sonnet (current) — faster, capable, lower cost
   (Press Enter for default: A)

5. Environmental audio: Should clips include ambient sound (wind, crowd noise, footsteps, etc.)?
   YES — adds background audio to every clip (no dialogue generated)
   NO  — silent clips, add music/sound design in post [recommended]
   Note: enabling audio doubles video generation cost (~$0.075/s vs ~$0.0375/s at 1080p)
   (Press Enter for default: NO)
```

Store as: `channel_url`, `aspect_ratio`, `target_duration_min`, `script_model`, `generate_audio`

Script model mapping:
- Answer A → `script_model = "claude-opus-4-8"` (Claude Opus 4.8)
- Answer B → `script_model = "claude-sonnet-4-6"` (Claude Sonnet 4.6, current session model)

**Set language mode:**
- `aspect_ratio == "9:16"` → `tiktok_safe = TRUE` (vertical = YouTube Shorts + TikTok)
- `aspect_ratio == "16:9"` → `tiktok_safe = FALSE` (landscape = YouTube only)

---

## PHASE 2 — CHANNEL ANALYSIS (automated, silent)

**Preferred method: YouTube Data API**

```bash
source /Users/tonymacbook2025/.env-secrets

# Step 1 — resolve channel ID from handle
curl -s "https://www.googleapis.com/youtube/v3/channels?part=id,snippet&forHandle=<HANDLE>&key=${YOUTUBE_DATA_API_KEY}"

# Step 2 — fetch top videos by view count
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=<ID>&order=viewCount&type=video&maxResults=15&key=${YOUTUBE_DATA_API_KEY}"
```

Extract the handle from `channel_url`. If the URL is not a YouTube channel URL, fall back to Playwright scraping (see below).

**Fallback 1: Playwright (Python 3.13)**

```python
# Uses existing Playwright at /Library/Frameworks/Python.framework/Versions/3.13/
from playwright.sync_api import sync_playwright
# Launch headless chromium with anti-detection headers
# Navigate to channel /videos?view=0&sort=p&flow=grid
# Wait for networkidle + scroll 3x, extract ytd-rich-item-renderer titles
```

**Fallback 2: Firecrawl CLI**

```bash
firecrawl scrape "<channel_url>"
```

From the data, extract and hold internally:
- Top 10–15 video titles (highest view counts)
- Hook formulas visible in titles
- Topic patterns: historical events, natural disasters, survival, science mysteries
- Recurring structural cues (numbers, questions, superlatives)

Do NOT surface this to Tony yet — use it as input for Phase 3.

---

## PHASE 3 — STORY IDEATION (automated → present, then ⏸ PAUSE)

Run the Story Ideation funnel internally, then present results.

### Step A — Generate 3 candidate topics

Based on the channel analysis from Phase 2, identify 3 topics that would perform well on that channel. Topics must be:
- Historically grounded (real events, real places)
- Visually rich (can be shown with dramatic footage)
- Emotionally compelling (survival, betrayal, discovery, collapse)

### Step B — Drill each topic through the funnel

For each of the 3 topics:

1. Generate 10 unusual, underexplored, or counterintuitive angles on that topic
2. Select the strongest angle (most surprising + most visual)
3. **Drill the chosen angle into 5 specific sub-ideas** — each sub-idea must be:
   - A concrete event, turning point, contradiction, or fact
   - Shocking, emotional, or visually powerful
   - Tightly tied to the chosen angle (not a tangent)
   These 5 sub-ideas become the skeleton of the script body before writing begins.
4. Identify the single most jaw-dropping fact that could open the video

### Step C — Present to Tony

```
Here are 3 topic options for Reimagined Realms:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [TOPIC A]
   Angle: [one-line — the surprising lens we take on this]
   Hook: [the most jaw-dropping fact, stated as the opening line would sound]

2. [TOPIC B]
   Angle: [one-line]
   Hook: [opening hook fact]

3. [TOPIC C]
   Angle: [one-line]
   Hook: [opening hook fact]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Which would you like? (1, 2, or 3 — or say "try again" for new options)
```

⏸ **PAUSE — wait for Tony to pick a topic before proceeding**

If Tony says "try again": repeat Phase 3 with fresh topics.
If Tony picks one: store as `chosen_topic`, `chosen_angle`, `hook_fact`, `five_sub_ideas[]` and move to Phase 4.

---

## PHASE 4 — SCRIPT GENERATION (automated)

Create the output folder with an auto-incremented sequence number:

```bash
PRODUCTIONS="/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Productions"

# Find highest existing sequence number, increment by 1
LAST=$(ls "$PRODUCTIONS" | grep -E '^[0-9]{4}_' | sort | tail -1 | grep -oE '^[0-9]{4}')
NEXT=$(printf "%04d" $(( ${LAST:-0} + 1 )))

# Build folder name: NNNN_Title_Case_Slug
# Slug rules: first letter of every word capitalized, words separated by underscores, no hyphens
# e.g. "pompeii the escape" → "0001_Pompeii_The_Escape"

FOLDER="${NEXT}_[Title_Case_Slug]"
mkdir -p "$PRODUCTIONS/$FOLDER/"
```

Store the full path as `production_folder`. Use it for all file saves from this point forward.

**Production folder structure — create all subfolders at this step:**

```
NNNN_Title_Case_Slug/
├── Scripts/
│   ├── Script.md              ← full narration script
│   └── Narration.md           ← TTS-formatted version (used by audio_tts.py)
├── Narration_Audio/
│   ├── Scene_01.mp3           ← per-scene MP3s from ElevenLabs
│   └── ...
├── Images/                    ← generated stills, named with clip timecodes (see Phase 9)
├── Video_Clips/               ← generated video clips, named with clip timecodes (see Phase 9)
├── Production/
│   ├── Beat_Table.md
│   ├── Shot_List.md
│   └── Cost_Estimate.md
├── Data/
│   ├── Beatmap.json           ← VO-aligned clip timecodes for editing software
│   ├── Beat_Sheet.json        ← raw ElevenLabs word-level timestamps
│   ├── Generation_Log.json    ← per-asset model/prompt/iteration/severity log (see Video_Editor/CLAUDE.md "Data Folder")
│   ├── Report_Card.md         ← Tony's grade + critique, rolled up from Generation_Log.json
│   └── (future: FCPXML, OTIO, DaVinci XML exports)
└── Package/
    ├── YouTube_Package.md
    └── Text_Hooks.txt
```

```bash
mkdir -p "$PRODUCTIONS/$FOLDER/Scripts"
mkdir -p "$PRODUCTIONS/$FOLDER/Narration_Audio"
mkdir -p "$PRODUCTIONS/$FOLDER/Images"
mkdir -p "$PRODUCTIONS/$FOLDER/Video_Clips"
mkdir -p "$PRODUCTIONS/$FOLDER/Production"
mkdir -p "$PRODUCTIONS/$FOLDER/Data"
mkdir -p "$PRODUCTIONS/$FOLDER/Package"
echo '{"production": "'"$FOLDER"'", "channel": "Reimagined Realms", "assets": []}' > "$PRODUCTIONS/$FOLDER/Data/Generation_Log.json"
cat > "$PRODUCTIONS/$FOLDER/Data/Report_Card.md" << 'EOF'
---
title: "Video Report Card"
type: report
domain: video-production
tags: [report, video-production, content-creation, reimagined-realms]
---

# Video Report Card
**Channel:** Reimagined Realms
**Video:**
**Grade:**
**Previous Grade:**
**Review Date:**

---

## Critique Notes

(Filled in after Tony reviews the finished video.)
EOF
```

**Live logging rule:** As each asset is generated in Phase 9+ (image, video clip, VO take, SFX, music cue), append an entry to `Data/Generation_Log.json` with model + version, platform, the prompt used (and any rewrites + why), iteration count, and any issue found tagged by severity (🔴 Critical / 🟠 Major / 🟡 Minor). Grade issues as soon as something looks off — starting at the reference-image stage, not just at final render.

**Script model:** Use `script_model` chosen in Phase 1.
- If `script_model = "claude-opus-4-8"`: invoke Claude Opus 4.8 for script generation (use `/fast` mode or spawn as subagent if available in the current environment)
- If `script_model = "claude-sonnet-4-6"`: write the script in the current session (no model switch needed)

Write the full narration script applying all frameworks below simultaneously.

---

### TIKTOK-SAFE LANGUAGE (applies only when `tiktok_safe = TRUE`)

Before writing any word of the script, scan every sentence against this substitution table. Apply substitutions automatically — do not use flagged terms even once.

**Death & Bodies**

| Flagged | Use Instead |
|---|---|
| died / die / dead / death | unalived, perished, fell, passed, ceased to exist |
| killed / kill | unalived, taken, fell, removed |
| murder / murdered | unalived, eliminated, taken |
| suicide | self-unalived |
| massacre | mass tragedy, mass event |
| execution | final punishment, end |
| beheaded / decapitation | removed at the neck |
| bodies / body | remains, those who fell, the lost |
| blood | the red stuff (or rephrase entirely) |
| genocide | mass elimination, erasure |
| assault | struck, overwhelmed, overtook |
| abuse | mistreatment |

**Weapons**

| Flagged | Use Instead |
|---|---|
| gun / firearm / rifle / pistol | pew pew, boomstick, ranged tool |
| shooting / shot | pew pew event, fired upon |
| bomb / explosion / explosives | device, went off, surge, detonation event |
| sword / knife / blade / axe / machete | edge tool, metal tool, pointy tool |
| weapon / weapons | tool, device |
| bullets / ammo | projectiles |
| grenade | thrown device |

**War & Conflict**

| Flagged | Use Instead |
|---|---|
| war | conflict, clash |
| attack / attacked | struck, overwhelmed, overtook |
| invasion | advancement, incursion |
| hostage / kidnapping / abduction | detained, captured, taken |
| destroy / destroyed | leveled, wiped out |

**Historical Sensitivities**

| Flagged | Use Instead |
|---|---|
| slavery | forced labor, captivity |
| Holocaust | mass persecution, historical tragedy |
| rape / sexual violence | assault, violation |
| racist / racism | discriminatory, bias-driven |

> These are high-risk terms on TikTok — enforcement is context-dependent. When in doubt, rephrase the sentence entirely rather than swapping a single word.

---

### Framework A — Reimagined Realms Channel Tone

- Intelligent, curious, calm narrator — never sensationalist
- Every sentence is visual: the listener should see something
- No filler. No "In this video we're going to..." — start at the action
- Cold, factual, third-person — like a documentary narrator, not a YouTuber
- **This is a voiceover-only channel.** Characters never speak. No dialogue is written into the script. Narration describes what happened — actions and outcomes only.

---

### Framework B — Hook Trifecta (first 2–3 seconds)

Every video has three hooks firing simultaneously in the first 2–3 seconds. Each does a different job. They must NEVER repeat each other.

**Hook 1 — Visual Hook** (goes into shot C1 image/video prompt)
The most striking or unexpected frame in the video. Could be mid-transformation, a pattern interrupt, an unexpected angle, or the most dramatic visual moment. Its job: stop the scroll.

**Hook 2 — Text on Screen Hook** (saved to `text_hooks.txt` — never baked into video)
Sets the stakes and makes the promise. Its job: tell the viewer why this video matters to *them*. Duration: first 2–3 seconds only. Never repeats the verbal hook. Format:
- Emotional stakes: "YEARS of mystery. Finally solved."
- Implied backstory: "[N] people. [N] survivors. No one knows why."
- Direct curiosity gap: "The answer will shock you."

**Hook 3 — Verbal Hook** (first sentence of the narration script)
Opens the curiosity loop. Does zero explaining. Makes the viewer need to know more. Choose one formula based on story type:

*Character-driven story (a named person is the protagonist):*
> "This [character type] (in [context]) [unique detail] [key action] — [twist/consequence]."
> Example: "This teenage girl (in 1429 France) cut her hair, put on armor, and led an army — just to be betrayed by the king she saved."

*Event/concept-driven story (no central character):*

| Formula | Structure |
|---|---|
| **Discovery** | "[Authority] just confirmed [subject]. The answer changes [what we knew]." |
| **Impossible Claim** | "[Subject] [did/survived/caused] something that shouldn't be possible. Here's how." |
| **Stakes** | "In [specific moment], [N people/things] faced [extreme situation]. [Mysterious outcome]." |
| **Qualifier** | "If you think you know [subject] — you have it completely wrong." |

---

### Framework C — Story Arc Selection

**Target duration < 5 minutes → Fichtean Curve**
- Open directly in crisis — no setup, no context warmup
- Stack mini-crises throughout
- Major climax near the end, brief resolution
- 1–2 curiosity loops maximum
- Fewer acts: Hook → Rising Crisis → Peak Crisis → Climax → Resolution + CTA
- Target ~6 acts for a 3–4 min video

**Target duration ≥ 5 minutes → Full 9-Act Structure**
- Hook → Loop Stack → Act I (Normal World) → Act I Close (Inciting Incident) → Act II Rising → Act II Pattern Interrupt → Act II Widening → Climax → Resolution + Outro
- 3–5 curiosity loops

---

### Framework D — 7-Part Story Template (sentence level)

Map the chosen arc onto this sentence-level structure. The 5 sub-ideas from Phase 3 Step B.3 slot into Parts 2–6.

```
[PART 1 — CONTEXT]
Date, place, specific detail. Factual cinematic sentences.
"It was August 24th, 79 AD. The fishing boats had already gone out."

[PART 2 — SMALL TWIST]
Things were almost normal. A reassuring sentence, then a crack appears.
"And for a while… it worked."

[PART 3 — PLOT TWIST]
The turn. Betrayal, collapse, or revelation.
Short punchy sentences. Something irreversible happens.

[PART 4 — CONTEXT]
Response. Who acted. What they did. Action sentences.
"He ordered the fleet south. Seventeen ships."

[PART 5 — SMALL TWIST]
A stealth move or quiet discovery. The thing nobody noticed at the time.

[PART 6 — FINAL CONSEQUENCE]
Major fallout. Kept slightly mysterious — don't over-explain.
"What they found in the ruins changed everything."

[PART 7 — REVEAL]
The payoff. The fact that reframes everything before it.
"And the man who survived… was the one who ran first."
```

---

### Framework E — DAIPBR Mechanics (apply throughout script)

**But/Therefore Rule (South Park)**
Every beat must connect to the next with BUT or THEREFORE — never AND THEN.

| Connection | Meaning |
|---|---|
| **BUT** | Conflict, obstacle, reversal — something goes wrong |
| **THEREFORE** | Consequence, cause-and-effect — action leads to result |
| **AND THEN (BANNED)** | No causation — just sequential events with no tension |

Wrong: "The city fell. And then the people fled. And then the army arrived."
Right: "The city fell. THEREFORE the people fled. BUT the army had already cut off the roads."

If you can't find a BUT or THEREFORE between two beats, the beat has no tension. Rewrite it.

**Tension Gap**
Tension = the gap between what IS and what COULD BE.
- Open the gap: show what the subject wants vs. what their reality is
- Widen the gap: add obstacles, raise stakes, delay resolution
- Close the gap: deliver the payoff — the bigger the gap, the more satisfying the close

**Curiosity Loops**
Structure: Open the loop → Sustain tension (hint without revealing) → Close the loop → Stack the next loop before the old one closes.
- Short-form (< 5 min): 1–2 loops
- Long-form (≥ 5 min): 3–5 loops
Never close a loop without opening the next one (until the final resolution).

**Pattern Interrupts**
Reset viewer attention every 30–90 seconds (long-form) or every 3–7 seconds (short-form).
Types: new location, new revelation, unexpected contradiction, sharp tonal shift, a single short sentence after long ones.
The Opposite Method: when the audience expects A, deliver B. The bigger the setup, the harder the interrupt lands.

---

### Script formatting rules

- Write narration only — no stage directions, no character dialogue
- Mark act boundaries as inline comments: `<!-- HOOK -->`, `<!-- ACT I -->`, etc.
- Target word count:
  - `ceil(target_duration_min × 163 × 1.15)` words
  - Voice raMcNf2S8wCmuaBcyI6E speaks at **163 WPM** (measured from Pompeii production)
  - **+15% padding** is mandatory — ElevenLabs renders faster than estimated; without it the video will run short
  - For 3 min target → `ceil(3 × 163 × 1.15)` = **563 words**
  - For 5 min target → `ceil(5 × 163 × 1.15)` = **937 words**
  - After TTS generates, ffprobe the narration.mp3 duration. If it's more than 5% short of target, flag it before proceeding — do not silently continue with a shorter video
- Each paragraph = one beat (one visual moment)
- **Do NOT write a spoken CTA line into the script.** The CTA ("Follow Reimagined Realms. History gets stranger every episode.") is a fixed, pre-rendered audio asset appended in post-production (see Phase 8 CTA Hold Beat and Phase 11 Assembly) — never generated per-video. The script should end on the story's final line only.

**Save to:** `[production-folder]/script.md`

---

## PHASE 5 — BEAT TABLE (automated)

Break the script into acts based on the arc selected in Phase 4 Framework C.

**Fichtean Curve (< 5 min) — target ~6 acts:**

```markdown
| Act | Label | Time | Clips | Beat Description |
|-----|-------|------|-------|-----------------|
| 1 | Hook | 0:00–0:20 | C1–C3 | [most dramatic visual moment] |
| 2 | Rising Crisis | 0:20–1:00 | C4–C8 | [tension building, loops open] |
| 3 | Peak Crisis | 1:00–1:50 | C9–C13 | [escalation, stakes highest] |
| 4 | Climax | 1:50–2:30 | C14–C17 | [turning point / max consequence] |
| 5 | Resolution | 2:30–3:00 | C18–C21 | [payoff] |
| 6 | Outro + CTA | 3:00–3:15 | C22–C24 | [close + call to action] |
```

**Full 9-Act (≥ 5 min) — target ~9 acts:**

```markdown
| Act | Label | Time | Clips | Beat Description |
|-----|-------|------|-------|-----------------|
| 1 | Hook | 0:00–0:20 | C1–C3 | [what's happening visually] |
| 2 | Loop Stack | 0:20–0:55 | C4–C7 | [visual content] |
| 3 | Act I — Normal World | 0:55–1:30 | C8–C11 | [visual content] |
| 4 | Act I Close | 1:30–2:05 | C12–C15 | [inciting incident visuals] |
| 5 | Act II — Rising | 2:05–2:50 | C16–C19 | [escalation] |
| 6 | Act II — Pattern Interrupt | 2:50–3:25 | C20–C23 | [new angle/revelation] |
| 7 | Act II — Widening | 3:25–4:00 | C24–C27 | [tension building] |
| 8 | Climax | 4:00–4:35 | C28–C31 | [peak moment] |
| 9 | Resolution + Outro | 4:35–5:00 | C32–C35 | [payoff + CTA] |
```

For each act: assign time range, assign 3–5 clips, write one-line beat description.

**Save to:** `[production-folder]/beat_table.md`

Pass `total_clip_count` to Phase 6.

---

## PHASE 6 — COST ESTIMATE (automated → ⏸ PAUSE for approval)

Compute estimated cost for three production combos. Read current prices from:
```
/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Tool-Manager/data/pricing_cache.json
```

### Pricing constants (read from cache for current values)

> **IMPORTANT — pricing cache keys ≠ API model IDs.**
> The keys below are used to look up prices in `pricing_cache.json` only.
> Before writing any batch script or making any kie.ai API call, look up the actual API model ID in:
> `001_Architecture/Tools/Tool-Manager/data/kieai_pricing_api.json`
> Find the matching entry by `modelDescription`, then extract the model ID from its `anchor` URL: `?model=<actual-api-id>`.
> **Never probe the live API to discover model names — that runs real jobs and costs credits.**

**Image models (kie.ai) — pricing cache keys:**
- GPT Image 2 (1k): `gpt-image-2-text-to-image-1k` → price from cache | **API model ID:** `gpt-image-2-text-to-image`
- Nano Banana 2 (1k): `google-nano-banana-2-1k` → price from cache | **API model ID:** `nano-banana-2`

**Video models (kie.ai, 1080p only — never use 720p) — pricing cache keys:**
- Seedance 2 1080p (image-to-video): `bytedance-seedance-2-1080p-with-video-input` → price/sec from cache (~$0.31/s — premium quality)
- Seedance 1.5 Pro 1080p (no audio): `bytedance-seedance-1.5-pro-without-audio-1080p` → price/sec from cache (~$0.0375/s — budget-friendly)
- Kling 3.0 1080p (no audio): `kling-3.0-video-without-audio-1080p` → price/sec from cache
- Veo 3.1 lite 1080p (image-to-video): `google-veo-3.1-image-to-video-lite-1080p` → price/video from cache

**ElevenLabs:**
- `tts-multilingual-v2` → price/1k chars from cache

**Script generation (Claude API equivalent — informational only):**
- Claude Opus 4.8: ~$15/M input tokens, ~$75/M output tokens
- Claude Sonnet 4.6: ~$3/M input tokens, ~$15/M output tokens
- Estimated tokens per script: ~4,000 input + ~600 output (scales with video length)
- Note: if running on the Claude.ai $20/month plan, this cost is absorbed by the subscription. These figures reflect the equivalent API cost for reference only.

### Cost formula

```
clips = total_clip_count from Phase 5
billed_seconds_per_clip = 5
chars = target_duration_min × 750
script_input_tokens  = 4000 + (target_duration_min × 200)   # scales with length
script_output_tokens = target_duration_min × 130 × 1.35     # ~1.35 tokens/word

# Script cost (API equivalent)
if script_model == "claude-opus-4-8":
    script_cost = (script_input_tokens × 0.000015) + (script_output_tokens × 0.000075)
else:  # claude-sonnet-4-6
    script_cost = (script_input_tokens × 0.000003) + (script_output_tokens × 0.000015)

image_cost = clips × image_price_per_image

# If generate_audio=TRUE, use with-audio pricing key (2x rate)
# e.g. bytedance-seedance-1.5-pro-with-audio-1080p instead of without-audio
audio_multiplier = 2.0 if generate_audio else 1.0
video_cost (per_second) = clips × billed_seconds_per_clip × video_price_per_sec × audio_multiplier
video_cost (per_video)  = clips × video_price_per_clip   # Veo flat rate (no audio variant)

tts_cost = (chars / 1000) × elevenlabs_price_per_1k

total = image_cost + video_cost + tts_cost + script_cost
```

### Present 3 combos

```
💰 COST ESTIMATE — [total_clip_count] clips, [target_duration_min] min video

┌─────────────────────────────────────────────────────────────────────┐
│ Combo   │ Image Model     │ Video Model           │ Est. Total │ Route  │
├─────────┼─────────────────┼───────────────────────┼────────────┼────────┤
│ A       │ GPT Image 2     │ Seedance 2 1080p      │ ~$XX.XX    │ kie.ai │
│ B       │ Nano Banana 2   │ Kling 3.0 1080p       │ ~$XX.XX    │ kie.ai │
│ C       │ Nano Banana 2   │ Veo 3.1 lite 1080p    │ ~$XX.XX    │ kie.ai │
└─────────────────────────────────────────────────────────────────────┘

All combos include ElevenLabs multilingual v2 TTS: ~$X.XX
API key used: KIE_API_KEY (kie.ai), ELEVENLABS_API_KEY (voiceover)

Note: estimate based on [clips] clips × 5s billed each.

Which combo? (A, B, or C)
```

**Save to:** `[production-folder]/cost_estimate.md`

⏸ **PAUSE — wait for Tony to choose a combo before proceeding**

Store: `chosen_combo`, `chosen_image_model`, `chosen_video_model`

---

## PHASE 7 — VOICEOVER (automated)

Generate voiceover from the narration script using ElevenLabs.

Strip all `<!-- comment -->` markers from script.md before sending to TTS. Send clean narration text only.

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
source /Users/tonymacbook2025/.env-secrets

python3 002_Content-Creation/Video_Editor/004_Tools/audio_tts.py \
  --text-file "[production-folder]/script.md" \
  --voice-id "raMcNf2S8wCmuaBcyI6E" \
  --model "eleven_multilingual_v2" \
  --output-dir "[production-folder]/" \
  --timestamps
```

If the script flags differ from what audio_tts.py accepts, read the script's argparse/help to get the correct flags before running.

**Expected outputs saved to:** `[production-folder]/`
- `voiceover.mp3` — audio file
- `timestamps.json` — word-level timestamps from ElevenLabs

---

## PHASE 8 — BEATMAP FROM VOICEOVER (automated)

Parse `timestamps.json` to align the beat table to actual VO timing.

### Algorithm

1. For each act in beat_table.md, identify the first word of that act's narration in the script
2. Find that word's timestamp in `timestamps.json`
3. That timestamp = `act_start_ms`
4. `act_end_ms` = start of next act (or total audio duration for final act)
5. Divide the act's time window evenly across its clip count → per-clip start/end windows
6. Each clip: generate 10–12s, trim to 6–8s in post

### Output format

Write `beatmap.json`:

```json
{
  "topic": "[chosen topic]",
  "total_clips": N,
  "total_duration_ms": NNNNN,
  "acts": [
    {
      "act": 1,
      "label": "Hook",
      "start_ms": 0,
      "end_ms": 20000,
      "sub_beats": [
        {
          "clip": "C1",
          "start_ms": 0,
          "end_ms": 6500,
          "target_generate_duration_s": 12,
          "target_final_duration_s": 6
        }
      ]
    }
  ]
}
```

**Beatmap duration rules (non-negotiable):**
- `target_generate_duration_s` → always **12** (Seedance 1.5 max; gives padding)
- `target_final_duration_s` → derived from VO beat length, **hard cap at 8s**. Ideal range is 3–6s. Never set a final duration over 8s — faster cuts keep viewers engaged. The 4s gap to Seedance's 12s max is intentional padding.
- `assemble.py` enforces `min(target, 8.0)` at runtime as a safety net.

**CTA Hold Beat (locked 2026-07-04) — the final sub-beat of the final act:**

Every beatmap's last act must end with one dedicated extra sub-beat reserved exclusively for the outro CTA. This beat is NOT derived from narration timing (there is no scripted narration for it — see Phase 4) and must follow these exact rules:

- It is a single clip — no internal cuts. One continuous shot held for the full duration.
- `target_final_duration_s` = **8.0 exactly** (fixed, not capped-from — this is the only beat in the pipeline with a hardcoded, non-derived duration).
- It comes chronologically AFTER the last beat containing actual story narration — never overlapping it.
- Its audio is NOT a `Scene_XX.mp3` file. It has no per-video TTS generation. `assemble.py` appends the fixed channel-wide CTA asset automatically during narration assembly (Phase 3 of assembly — see Phase 11 below): 1.5s silence gap, then the static CTA audio (`Brand_Assets/CTA/cta_follow_reimagined_realms.mp3`, 3.76s, voice `raMcNf2S8wCmuaBcyI6E`).
- Its image/video prompt (Phase 9) must still be topically relevant to that video's story — never a generic filler shot — and visually clean/uncluttered since the YouTube end screen template overlays on top of it in the final upload.
- Total final video runtime = `target_duration_min` (story only, from Phase 1 intake) + this fixed ~8s CTA hold. The CTA hold is additional runtime, not counted against the script's word-count target.

Also create `Production/assemble_config.json` with the music and caption config for this video:
```json
{
  "suno_prompt": "[Cinematic music description matching video mood and era]",
  "suno_tags": "[style tags: cinematic orchestral dark historical documentary instrumental ...]",
  "caption_line1": "[First line of text hook — the most jaw-dropping stat, e.g. '18\\,000 people. 2\\,000 bodies.']",
  "caption_line2": "[Second line — the open question, e.g. 'Where did the rest go?']"
}
```
This file is read by the universal `assemble.py` — without it, assembly will fail.

**Save to:** `[production-folder]/beatmap.json`

---

## PHASE 9 — SHOT LIST (automated)

For every sub-beat in beatmap.json, generate one image prompt and one video prompt.

### Image prompt rules

- Era-accurate, photorealistic, cinematic
- Specify: subject, setting, historical era, lighting, camera angle
- Format: `[Subject] [doing/in what], [place], [era], [lighting], [camera angle], photorealistic, cinematic, no text`
- Match the video model of the chosen combo (for Veo, prompts can be more abstract)
- **No on-screen text, no overlaid captions, no call-out annotations in any image prompt.** Exception: text that is physically part of the scene (a carved inscription, a market sign, a billboard in the background). Never include text that would appear as a graphic overlay.

### Video prompt rules

- State motion direction explicitly: `slow push-in`, `pan left`, `dolly back`, `static`, `tilt up`
- No character dialogue — this is a voiceover-only channel. Characters never speak. Describe physical action and camera motion only.
- No internal thoughts, no fantasy elements — ground it in physical reality
- **No on-screen text, no overlaid captions, no motion graphic text, no call-out annotations.** Exception: text that is physically part of the scene (a carved stone, a painted banner, a storefront sign). Never prompt for text that appears as a graphic overlay on top of the footage.
- Duration: `12 seconds`
- Aspect ratio: `[aspect_ratio from Phase 1]`
- For image-to-video models: the image prompt IS the reference frame, motion animates it

### Shot list format

Write `shot_list.md`:

```markdown
# Shot List — [Topic]

Generated: [date]
Image model: [chosen_image_model]
Video model: [chosen_video_model]

---

## Act 1 — Hook (C1–C3)

### C1 | 0–6.5s | [beat description]
**Image:** Aerial view of Mount Vesuvius at dawn, 79 AD, thin plume of white smoke rising from the summit, warm golden light, wide establishing shot, photorealistic, cinematic, no text
**Video:** Static wide shot, camera slowly tilts up from base of mountain to summit, no on-screen text or overlaid captions. 12 seconds. 16:9.

### C2 | 6.5–13s | [beat description]
**Image:** ...
**Video:** ...

### C[N] | CTA Hold — 8.0s fixed | Outro (final sub-beat of the final act)
**Image:** [Must be topically tied to the episode's story — e.g., for Pompeii: the same road/ash-covered landscape motif used earlier, but calmer and wide. Visually clean, uncluttered composition.]
**Video:** Static or very slow push, minimal motion, no on-screen text. Generate 12s, trim to a fixed 8.0s hold (never derived from narration timing — see Phase 8 CTA Hold Beat rule). Keep the composition clean since the YouTube end screen template overlays on top of this shot.
```

**Save to:** `[production-folder]/Production/Shot_List.md`

### Image and video clip naming convention

When images and video clips are generated (manual step after pipeline), they must be named with their clip ID and VO timecodes so they map directly to the beatmap without opening any file:

```
Images/
  C01_0.0s-3.8s.png
  C02_3.8s-7.7s.png
  C03_7.7s-11.5s.png
  ...

Video_Clips/
  C01_0.0s-3.8s.mp4
  C02_3.8s-7.7s.mp4
  ...
```

Format: `C[clip_number]_[start_s]s-[end_s]s.[ext]`
- Clip number: zero-padded to 2 digits (C01, C02 ... C21)
- Timestamps: from `Data/Beatmap.json` `start_ms` / `end_ms` converted to seconds (1 decimal place)
- Images: `.png`
- Video clips: `.mp4`

Include this naming instruction in the Shot_List.md header so whoever generates the assets knows the convention.

---

## PHASE 10 — YOUTUBE PACKAGE (automated)

Generate the complete upload package.

### Text on Screen Hook — `text_hooks.txt`

Write the text on screen hook as a standalone file. This is never baked into the video. Tony will apply it as a caption layer in the video editor or via FFmpeg.

```
# text_hooks.txt
# Duration: first 2–3 seconds of video only
# Apply as caption overlay in video editor or FFmpeg — non-destructive

[TEXT HOOK LINE]
```

Hook must set stakes or make a promise. Must NOT repeat the verbal hook from the script. Examples:
- "YEARS of silence. One night changed everything."
- "18,000 people. Only 2,000 bodies ever found."
- "The answer was buried for 2,000 years."

**Save to:** `[production-folder]/text_hooks.txt`

---

### Title options (3)

**Locked formula (validated on Pompeii — Tony's pick: Formula 1):**

**Formula 1 — Curiosity Gap + Specificity** *(primary — use this first)*
`"[Specific number] [People/Things] [Vanished/Did X] From [Place/Event]. [Unresolved tension — No one knows / History forgot / The answer was buried]."` 
- Two sentences. Lead with the number. Second sentence leaves the gap open.
- 60–70 chars max. Statement, never a question.
- Example: "16,000 People Vanished From Pompeii. No One Knows Where They Went."

**Formula 2 — Discovery Frame + Specific Number** *(secondary)*
`"What Really Happened to the [Number] [People] Who [Survived/Escaped] [Event]"`
- "What really happened" signals hidden truth. Reframes the story around survivors/mystery, not the disaster itself.
- Good for search volume — people search "what happened [event] survivors."
- Example: "What Really Happened to the 16,000 People Who Survived Pompeii"

**Formula 3 — Pattern Interrupt** *(use sparingly — best for shareable/social)*
`"[Place/Event] Wasn't a [Expected Thing]. It Was a [Reframe]."`
- Contradicts the accepted narrative in under 10 words.
- Most shareable but least SEO-friendly. Reserve for stories with strong narrative reversals.
- Example: "Pompeii Wasn't a Tragedy. It Was an Escape."

Generate all 3 for every video. Tony picks one.

### Description

**The title hooks. The description ranks.**

The description is optimized for search intent — what someone actually types into YouTube when they're curious about this topic. Most viewers never read the description, but YouTube's algorithm reads every word. Write for the searcher, not the watcher.

**Formula (validated on Pompeii — Tony's pick: Description 2):**

```
[First sentence = the exact question a curious person would type into YouTube search.
 "What really happened to X?" / "Why did X disappear?" / "How did X survive Y?"]

[Second sentence = brief answer that opens, not closes — introduce the gap.
 State the known fact, then the mystery underneath it.]

[Third–fifth sentences = expand the scene without resolving it.
 What was found. What's missing. What history forgot. Open at least one loop.]

---

📍 Chapters
[Paste chapter timestamps from beatmap.json, one per act]

---

This channel recreates historical events using AI-generated imagery. All content is for educational and entertainment purposes.

#[Topic-specific] #[EventName] #[LocationOrEra] #History #AncientHistory #Documentary #ReimaginedRealms
```

**Tag rules:** Lead with specific tags (event name, location, year), then broaden (History, Documentary). 10–15 tags. No tag stuffing — YouTube ignores tags beyond ~15.

**First sentence must be a question** matching a real search query. If you can't phrase it as a question someone would actually type, rewrite it.

### Tags

Generate 12–15 SEO tags. Mix specific (event name, location) and broad (history, documentary, ancient world).

### Thumbnail prompt

**Locked composition formula (validated on Pompeii — Tony's pick: Concept C)**

The thumbnail tells the story visually — no text. The composition, palette, and atmosphere must convey the emotion of the video before the title is read.

**Composition rules:**
- Single human figure, back to camera or walking away — never facing the viewer
- Figure is small (10–15% of frame height) — the world overwhelms the person
- Deep vanishing point — scene extends far into distance, creating scale and depth
- Human sits in lower third or center-bottom; the dominant subject fills the upper frame
- No text in the image — ever

**Palette rule — match story emotion, not a fixed color:**
- Catastrophe / eruption → warm amber, deep orange, red glow
- Mystery / aftermath / disappearance → cool grey, ash, muted tones, faint horizon light
- Ocean / underwater → deep blue, teal, black depths
- War / conflict → desaturated, smoke, grey-green
- Do NOT force a dark/ashy aesthetic on every video — the palette serves the story

**Prompt structure:**
```
[Single lone human figure description, back to camera, positioned at bottom of frame], 
[vast atmospheric setting that IS the story — ash-covered city / eruption column / empty landscape], 
[story-specific palette], deep vanishing point perspective, the human figure dwarfed by the environment, 
photorealistic, cinematic wide shot, no text, no captions
```

**Model:** GPT Image 2 via kie.ai, aspect ratio 16:9, quality standard
**Save to:** `Package/Thumbnails/Thumbnail_[concept].png`
Generate 3 concept directions for every new video. Tony picks one — that pick becomes the channel thumbnail for that video.

**Save to:** `[production-folder]/youtube_package.md`

---

## PHASE 11 — MEDIA GENERATION & ASSEMBLY (automated → ⏸ one quality pause)

This phase actually executes the pipeline through to a finished video file — do not stop at generating the shot list and package. Run these steps in the current session/orchestration:

### Step A — Generate images

```bash
python3.13 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/batch_generate_images.py "[production-folder]"
```
Reads Shot_List.md image prompts + Beatmap.json → saves `Images/C01_0.0s-3.8s.png` ... including the CTA Hold beat's image.

### Step B — Generate one test video clip, pause for quality check

```bash
python3.13 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/batch_generate_videos.py "[production-folder]" --clips C1
```

⏸ **PAUSE — show Tony the first generated clip. Wait for approval before generating the rest** (this is a real API cost commitment — catch a bad model/prompt combo on 1 clip, not the full batch).

### Step C — Generate remaining video clips

```bash
python3.13 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/batch_generate_videos.py "[production-folder]"
```
Add `--audio` if `generate_audio=TRUE` from Phase 1.

### Step D — Write `Production/assemble_config.json`

Confirm it exists (created in Phase 8) with `suno_prompt`, `suno_tags`, `caption_line1`, `caption_line2` for this specific video.

### Step E — Run assembly

```bash
python3.13 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/assemble.py "[production-folder]"
```

This runs all 7 assembly phases (trim/loop clips → concat video → concat narration + **append CTA gap+audio automatically** → Suno music → mix → color grade → caption overlay) and produces `[production-folder]/final.mp4`. The CTA hold beat, gap, and static CTA audio are baked in automatically by `assemble.py` — no manual step needed. Do not hand-build a per-production copy of `assemble.py`; always invoke the universal one at this path so future fixes apply to every production.

If any phase needs a redo (e.g. bad clip swapped in), use `--phase N --stop-phase N --overwrite --clips C20,C21`.

**Output:** `[production-folder]/final.mp4`, plus intermediate files under `Assembly/`.

---

## PHASE 12 — YOUTUBE UPLOAD VIA BLOTATO (automated → ⏸ PAUSE for final selections)

### Step A — Present choices, pause

```
Final video is ready: [final.mp4, duration, file size]

1. Which title? (from youtube_package.md — 3 options)
2. Which thumbnail? (from Package/Thumbnails/ — 3 concepts)
3. Privacy status — private (recommended for first review) / unlisted / public?
```

⏸ **PAUSE — wait for Tony's answers before uploading.** Never upload without this confirmation, even if a previous video's answers seem like an obvious default.

### Step B — Prepare assets

- If the chosen thumbnail PNG is over 2MB (Blotato's YouTube thumbnail limit), compress it: `ffmpeg -y -i input.png -vf "scale=1920:-1" -q:v 5 output.jpg` (aim well under 2MB; re-check with `ls -la`).
- Get a presigned upload URL via `mcp__blotato__blotato_create_presigned_upload_url` for both `final.mp4` and the (possibly compressed) thumbnail, then `curl -X PUT` each file to its presigned URL with `--data-binary "@<path>"`.

### Step C — Create the post

Call `mcp__blotato__blotato_create_post` with:
- `accountId`: `"30323"` (ReimaginedRealms YouTube — confirm via `mcp__blotato__blotato_list_accounts` if it's ever rotated)
- `platform`: `"youtube"`
- `title`: Tony's chosen title
- `text`: full description from `youtube_package.md` including chapters
- `mediaUrls`: `[<video publicUrl>]`
- `thumbnailUrl`: `<thumbnail publicUrl>`
- `privacyStatus`: Tony's chosen value
- `shouldNotifySubscribers`: `false` (irrelevant while private; keep false as the default unless Tony says otherwise for a public upload)
- `isMadeForKids`: **`false`** (locked channel default)
- `containsSyntheticMedia`: **`true`** (locked channel default — channel uses AI-generated imagery)
- `playlistIds`: **omit** — Tony adds these manually during scheduling for now (may automate later; do not add this field until he says so)

If Blotato returns an error about needing to "reconnect your YouTube account" for custom thumbnails, this is an OAuth scope issue in the Blotato dashboard, not a script bug — tell Tony to reconnect the account there, then retry `create_post` with the same already-uploaded media URLs (no need to re-upload).

### Step D — Confirm publish

Poll `mcp__blotato__blotato_get_post_status` (wait ≥10s between polls) until `status` is `published` or `failed`. Report the live `publicUrl` back to Tony.

---

## UPCOMING FEATURES (not in this version)

The following will be built as add-ons in a future iteration of this skill:

**Motion Graphic Overlays**
Animated on-screen graphics — magnitude scales, countdown timers, infographic callouts, stat reveals (e.g. "8.7 magnitude" counting up, timeline bars, map overlays with arrows). These will be implemented via Remotion or FFmpeg compositing and integrated as a separate phase between shot list generation and final assembly. Candidate skill: Reimagined Realms Motion Graphics Add-On or Hyperframes integration.

**Dialogue Scenes**
Future versions may support voiced character dialogue for specific dramatized scenes, using a separate voice model per character and lip-sync generation. Not in scope for the current voiceover-only pipeline.

---

## FINAL DELIVERY

The pipeline runs start to finish — Phases 1–12 — ending with a live (private) YouTube upload, not a handoff of files for Tony to assemble manually. When all 12 phases are complete, output a summary:

```
✅ Reimagined Realms pipeline complete — uploaded to YouTube.

Production folder: [full path]
├── script.md           ✓ [word count] words (no spoken CTA — CTA is a fixed post-production asset)
├── beat_table.md       ✓ [N] acts, [N] total clips
├── cost_estimate.md    ✓ Chosen combo: [A/B/C] (~$XX.XX)
├── voiceover.mp3       ✓ [duration]
├── timestamps.json     ✓ word-level timing
├── beatmap.json        ✓ [N] clips aligned to VO, incl. fixed 8.0s CTA Hold beat
├── shot_list.md        ✓ [N] image prompts + [N] video prompts
├── text_hooks.txt      ✓ text on screen hook (apply in editor — 2–3s)
├── youtube_package.md  ✓ 3 title options, description, tags, thumbnail prompt
├── Images/, Video_Clips/  ✓ generated assets
├── final.mp4           ✓ [duration] — CTA gap + static CTA audio + 8s hold baked in
└── YouTube             ✓ Published as [privacyStatus] — [publicUrl]

Remaining manual step: review the private upload, then flip privacy status and add to playlists in YouTube Studio when ready.
```

---

## REFERENCE — Key File Paths

| Resource | Path |
|---|---|
| Pricing cache | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Tool-Manager/data/pricing_cache.json` |
| kie.ai model ID lookup | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Tool-Manager/data/kieai_pricing_api.json` — find entry by `modelDescription`, extract API model ID from `anchor` URL `?model=<id>` |
| TTS script | `/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/004_Tools/audio_tts.py` |
| Batch image generation | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/batch_generate_images.py` |
| Batch video generation | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/batch_generate_videos.py` |
| Universal assembly script | `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/assemble.py` — appends CTA gap+audio automatically |
| CTA audio asset (channel-wide, fixed) | `002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Brand_Assets/CTA/cta_follow_reimagined_realms.mp3` (3.76s) |
| ElevenLabs voice ID | `raMcNf2S8wCmuaBcyI6E` |
| Blotato YouTube account ID (ReimaginedRealms) | `30323` |
| Production folder root | `/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Productions/` |
| Channel content system | `002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Reimaginedrealms_Content_System.md` |
| Story Ideation tutorial | `007_Resource_Library/Tutorials/Story-Ideation.md` |
| DAIPBR Storytelling skill | `001_Architecture/Skills/DAIPBR-Storytelling.md` |
