---
name: tiktok-shop-affiliate-video
description: Use when Tony has raw product footage and voiceover clips and wants to produce TikTok Shop or YouTube Shorts affiliate videos. Triggers on "create affiliate video", "edit product footage for TikTok", "make shop video", "cut my product clips", "I have footage and voiceovers for a product", "TikTok shop affiliate", or any request combining product footage + pre-recorded audio → short-form 9:16 output. Always use this skill for TikTok Shop and YouTube Shorts affiliate video production even if the word "skill" isn't mentioned.
---

# TikTok Shop Affiliate Video

Produces six 9:16 short-form affiliate videos from raw product footage and pre-recorded voiceover clips — three for TikTok Shop, three for YouTube Shorts. Audio-first workflow: each voiceover drives the visual cut of its video, so all six outputs are visually distinct and won't be flagged as duplicate content by TikTok's algorithm.

## Input Model

Tony records audio separately and drops everything into one folder:

| Files | Description |
|---|---|
| 6 audio clips | 3 TikTok VO (CTA: "tap the orange cart") + 3 YouTube VO (CTA: "comment and I'll send") |
| 8 video clips | Raw product footage, 12s–60s each, ~37s average |

The YouTube Shorts versions share the same visual cut as their TikTok counterparts — only the audio track differs. This means you cut 3 unique visual edits, then apply 2 audio tracks each → 6 total outputs.

## Neon Parcel TikTok Shop Creator — Pre-Production Question

Before starting any product, ask: **"Is this a TikTok Shop Creator video, or something else?"**

This skill currently implements the TikTok Shop Creator path only:
- Vertical (9:16) output, posted to the NeonParcel TikTok account
- **3 distinct TikTok videos** from the shared footage pool — each with genuinely different cuts, beats, and pacing (not the same edit with swapped audio)
- No YouTube pairing. If Tony wants an Amazon-affiliate version of a product, that requires separately-shot landscape footage and a different (not-yet-built) pipeline under `005_Affiliate_Marketing/Amazon_Associates/Videos/` — flag it back to Tony rather than attempting it here.

This supersedes the "3 cuts × 2 audio = 6 outputs" model described below in Step 4/5 when the product is explicitly a Neon Parcel TikTok Shop Creator video — only produce the 3 TikTok outputs.

Output routing for Neon Parcel TikTok Shop Creator products:
```bash
python3 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/scaffold_product_folder.py \
  "005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Videos" \
  <next_product_number> "<Product Name>" "<source ingest folder path>"
```
This creates `Videos/NNNN_Product-Slug/{Edit,Compliance/{Vision-Scan,Transcript-Scan},Package}/` — write the 3 rendered `TikTok_V1.mp4` / `V2` / `V3` into `Edit/`, not into the generic `edit/` folder used by the rest of this skill for other invocation contexts.

## Setup Check

Before starting, run these in order:

```bash
# 1. FFmpeg
ffmpeg -version | head -1

# 2. OpenRouter key (required for vision analysis)
source ~/.env-secrets && echo "OpenRouter: ${OPENROUTER_API_KEY:0:8}..."

# 3. requests library (for the vision script)
python3 -c "import requests; print('requests OK')" 2>/dev/null || pip install requests

# 4. ElevenLabs key (only needed if using video-use for transcription)
source ~/.env-secrets && echo "ElevenLabs: ${ELEVENLABS_API_KEY:0:8}..."

# 5. video-use (optional — FFmpeg-only mode works fine without it)
ls ~/Developer/video-use/SKILL.md 2>/dev/null && echo "video-use installed" || echo "video-use not installed"
```

If video-use is not installed and Tony wants it: `git clone https://github.com/browser-use/video-use ~/Developer/video-use && cd ~/Developer/video-use && uv sync`. Otherwise, proceed with FFmpeg-only — it handles this workflow fully.

## Naming Convention

Tony's workspace uses Title-Case with underscores, no spaces. Outputs go to `edit/` inside the drop folder:

```
edit/
├── TikTok_V1.mp4
├── TikTok_V2.mp4
├── TikTok_V3.mp4
├── YT_Shorts_V1.mp4
├── YT_Shorts_V2.mp4
└── YT_Shorts_V3.mp4
```

## Workflow

### Step 1 — Vision Analysis (run first)

Before making any editorial decisions, analyze what's actually in each clip visually. This uses FFmpeg to extract scene-change keyframes and Qwen-VL (via OpenRouter) to describe each one.

```bash
source ~/.env-secrets
python3 skills/TikTok-Shop-Affiliate-Video/scripts/analyze_clips.py <drop_folder>
```

Or if invoked from the drop folder itself:
```bash
source ~/.env-secrets
python3 ~/.claude/skills/TikTok-Shop-Affiliate-Video/scripts/analyze_clips.py .
```

This produces `clip_analysis.md` in the drop folder. Read it before proceeding — it tells you:
- What's happening at each scene-change timestamp in every clip
- Shot type and visual quality per moment
- Editorial recommendation for the best 8–12 second window per clip

Cost: ~$0.02–0.05 total for 8 clips. Model: `qwen/qwen2.5-vl-72b-instruct` via OpenRouter.

### Step 2 — Inventory

List all clips with durations. Ask Tony to confirm which audio files are TikTok vs YouTube Shorts versions if the filenames don't make it obvious.

```bash
# Video clips
for f in *.mp4 *.mov; do
  dur=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null)
  echo "${dur}s  $f"
done | sort -n

# Audio clips
for f in *.mp3 *.m4a *.wav; do
  dur=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null)
  echo "${dur}s  $f"
done
```

Report the inventory table before proceeding.

### Step 3 — Aspect Ratio Check

```bash
ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 <first_clip.mp4>
```

- **1080x1920 (9:16)**: no crop needed
- **1920x1080 (16:9 landscape)**: crop center vertical strip — `crop=ih*9/16:ih`
- **Other**: crop to center 9:16

Note the crop filter needed and apply it consistently to all clips.

### Step 4 — Plan Visual Variation

Before cutting, propose a variation plan using `clip_analysis.md` as the source. Each of the 3 visual edits should draw from different clips and moments so the three TikTok videos don't look identical.

Present a table like this and wait for Tony's approval:

| Version | Clips to use | Moments |
|---|---|---|
| V1 | Clip A + Clip C | Opening action + close-up |
| V2 | Clip B + Clip D | Different angle + in-use |
| V3 | Clip E + Clip A (later section) | Context shot + result |

Target duration for each visual edit = duration of its TikTok audio clip (the YouTube version reuses the same visual, just with a different audio track).

### Step 5 — Cut Each Visual Version

For each of the 3 visual versions:

**5a. Get the target duration from the TikTok audio clip:**
```bash
ffprobe -v quiet -show_entries format=duration -of csv=p=0 tiktok_v1.mp3
```

**5a.5 — Normalize VO loudness (always run this, every video):**

Raw VO recordings vary in level and, left unchecked, tend to land far too quiet
for social platforms — measured real output from this pipeline came in around
-34 to -35 LUFS integrated, well below TikTok's ~-14 LUFS target, with no
clipping risk at all. Normalize before muxing, not after:

```bash
python3 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/normalize_loudness.py \
  tiktok_v1.mp3 tiktok_v1_normalized.wav
```

Uses two-pass EBU R128 loudnorm, targeting -14 LUFS integrated / -1.5 dBTP true
peak by default (safe headroom, no clipping). Use the `_normalized` file (not
the raw VO) in Step 5c below. Repeat for every audio variant used in this
product (V1/V2/V3 VO, and YouTube Shorts VO if that pairing is ever produced).

**5b. Build a concat list and render the visual:**
```bash
# concat_v1.txt example:
# file 'clip_a.mp4'
# inpoint 0
# outpoint 8
# file 'clip_c.mp4'
# inpoint 5
# outpoint 12

CROP_FILTER="crop=ih*9/16:ih,scale=1080:1920"  # adjust if already 9:16

ffmpeg -f concat -safe 0 -i concat_v1.txt \
  -t <target_duration> \
  -vf "$CROP_FILTER" \
  -c:v libx264 -preset fast -crf 23 \
  -an \
  edit/visual_v1_silent.mp4
```

**5c. Ask Tony whether to keep or drop the original footage audio:**
- **Drop it**: clean VO only — simpler, most affiliate videos work this way
- **Keep ambient audio**: mix at low volume under VO (product sounds, ambient)

For VO only (use the `_normalized` file from Step 5a.5, not the raw VO):
```bash
ffmpeg -i edit/visual_v1_silent.mp4 -i tiktok_v1_normalized.wav \
  -map 0:v -map 1:a \
  -c:v copy -c:a aac -shortest \
  edit/TikTok_V1.mp4
```

For mixed audio (ambient at 15% + normalized VO at full):
```bash
ffmpeg -i edit/visual_v1_silent.mp4 -i tiktok_v1_normalized.wav -i original_audio.mp3 \
  -filter_complex "[2:a]volume=0.15[amb];[1:a]volume=1.0[vo];[amb][vo]amix=inputs=2[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -shortest \
  edit/TikTok_V1.mp4
```

**5d. Apply the YouTube Shorts audio to the same visual (normalize this VO too):**
```bash
ffmpeg -i edit/visual_v1_silent.mp4 -i youtube_v1_normalized.wav \
  -map 0:v -map 1:a \
  -c:v copy -c:a aac -shortest \
  edit/YT_Shorts_V1.mp4
```

Repeat for V2 and V3.

### Step 6 — Quality Check

After each render:
```bash
ffprobe -v quiet \
  -show_entries stream=width,height,codec_name,duration \
  -of default \
  edit/TikTok_V1.mp4
```

Confirm: 1080x1920, h264 video, aac audio, duration matches audio clip. Report any mismatch before moving on.

### Step 7 — Deliver

List all 6 outputs with file sizes:
```bash
ls -lh edit/*.mp4
```

Ask Tony to spot-check 1–2 videos in QuickTime before treating the batch as done.

## Compliance Gate (Neon Parcel TikTok Shop Creator only)

Three phases, run in order, before any video in this pipeline is marked ready-to-post. Full detail: `001_Architecture/Superpowers/Specs/2026-07-11-Neon-Parcel-Tiktok-Shop-Creator-Pipeline-Design.md`.

**Phase 1 — Ledger scan (every product, before editing starts).** Read `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Ledger.md` and check the planned VO scripts against every rule. If the product is Health/Beauty/Skincare/Weight-Management, note that in `Intake.md` — it triggers mandatory Phase 2 below regardless of cadence.

**Phase 2 — Live freshness check (cadence-gated).**
```bash
source ~/.env-secrets
python3 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/check_tos_freshness.py \
  "005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator" \
  --category "<Health|Beauty|Weight-Management if applicable, else omit>"
```
Skips itself automatically if the ledger was verified within 14 days and the product isn't in an always-escalate category. If it prints `REVIEW NEEDED`, read `Compliance-Freshness-Log.md`, review the flagged snapshot diffs, and manually update the affected `Compliance-Ledger.md` entries (new dated entry, never silently overwrite) before proceeding.

**Phase 3 — Post-build scans (every video, after rendering).** Run once per rendered TikTok_V1/V2/V3:
```bash
source ~/.env-secrets
python3 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/compliance_vision_scan.py \
  "<product_folder>/Edit/TikTok_V1.mp4" "<product_folder>/Compliance/Vision-Scan"
python3 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/compliance_transcript_scan.py \
  "<product_folder>/Edit/TikTok_V1.mp4" "<product_folder>/Compliance/Transcript-Scan"
```
Repeat for V2 and V3. Each writes a report ending in `Verdict: CLEAR` or `Verdict: FLAG`.

**What's machine-checked vs. human-only:**

| Ledger Rule | Category | Automated? |
|---|---|---|
| RULE-001, RULE-002, RULE-003 | Visual/Branding, Content Originality | Yes — Phase 3 vision scan |
| RULE-006 (partial) | Claims/Health (guarantee/cure language) | Yes — Phase 3 transcript scan (universal FTC phrase list only) |
| RULE-004, RULE-005, RULE-007, RULE-008, RULE-009, RULE-010 | Prohibited Products, Discounts, Temporary-Effects, Disclosure, Reviews, Format | **No — Phase 1 manual read only** |

RULE-008 (the #ad/#sponsored disclosure requirement) has no automated check — it's a required element that must be *present*, and the automated scans only detect banned content that's *present*, not required content that's *missing*. Do not treat a clean Phase 3 result as covering disclosure compliance.

**Final gate.** Before telling Tony a product is ready to post, present: Phase 1 summary (what was checked), Phase 2 result (skipped/clean/review-needed), and every Phase 3 report's verdict. If anything is FLAG, resolve or get explicit sign-off from Tony before moving files into `Package/`. Never auto-publish.

## Re-runs

This workflow repeats identically for each new product. Drop new footage + audio clips into a folder, invoke the skill. The only thing that changes is the input path.

## Adding Captions Later

If metrics show captions improve performance, the next layer is Hyperframes (`heygen-com/hyperframes`). It adds subtitle animations on top of the rendered MP4s. Install it then — not now.

## Troubleshooting

| Problem | Fix |
|---|---|
| Black bars in output | Check source dimensions with ffprobe; adjust crop filter |
| Audio sync drift | Add `-vsync 2` to the concat step |
| No audio in output | Verify `-map` flags include the audio stream from the VO file |
| Video too short | Source clips may not have enough coverage — pick longer segments in concat list |
| `uv sync` fails for video-use | Try `pip install -e .` inside the video-use directory instead |
