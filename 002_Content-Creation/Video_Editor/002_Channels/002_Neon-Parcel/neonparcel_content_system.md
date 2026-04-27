# NEONPARCEL — FULL CONTENT SYSTEM

## CORE IDENTITY

- **Brand:** NeonParcel
- **Tagline:** Your nonstop delivery of viral animal videos.
- **Tone:** Fun, irreverent, internet-native, slightly absurdist
- **Audience:** Animal lovers, meme culture, ages 13–35
- **Concept:** Every video is a "parcel" — a delivered hit of entertainment. Neon = electric energy, always lit, always moving. Content looks like something you'd stumble across on your phone at 1am. Some of it looks completely real. Some obviously AI. All of it has an animal doing something that makes you stop scrolling.
- **Mission:** Catch attention with content that starts believable and pays off with something physical, absurd, or unhinged. No lectures. No narration most of the time. Just animals doing things they shouldn't be doing — and getting away with it.

### Channel Description (YouTube)
Welcome to Neon Parcel — your nonstop delivery of viral animal videos, AI-powered moments, and caught-on-camera chaos featuring the animal kingdom's most unhinged behavior. New drops. All the time. Subscribe so you don't miss the next one.

### Mascot & Character
**The Wombat** — neon-outlined wombat face is the profile image and brand icon. Orange-to-red outer glow, blue eyes, pink-to-blue nose gradient, pure black background. The pixel art version (orange bear/wombat on a blue bicycle carrying delivery boxes) appears in end screens and channel art.

### Comparable Channels
FailArmy (animal edition) · The Dodo (unhinged version) · viral compilation accounts on TikTok

---

## COLOR SYSTEM

- **Neon Orange:** `#FF8C00`
- **Neon Red/Coral:** `#FF2A00`
- **Neon Magenta:** `#CC00FF`
- **Neon Blue:** `#00AAFF`
- **Neon Cyan (accent):** `#00DDFF`
- **Background:** `#000000` (pure black)
- **Banner Secondary:** `#1A0A2E` (dark purple-navy, used in city scenes)

### Palette Vibe
Neon sign aesthetic. Retro arcade, synthwave, neon-lit alley at night. Never pastel. Never flat. Always glowing.

---

## LOGO & BANNER RULES

### Logo
- Circular crop · pure black background
- Neon animal face (cat/critter) — orange-to-blue gradient glow
- Gradient: orange top → red sides → magenta nose → blue eyes → cyan bottom
- No text · no flat colors — always glowing/illuminated

### Banner
- Pixel art / retro game aesthetic
- Dark night city street (deep navy + orange-red lighting)
- Mascot: pixel art delivery animal (capybara/bear) on bicycle with parcels
- Mood: cozy urban night, slightly nostalgic, synthwave

---

## CONTENT PILLARS

1. **Cats doing absurd things** — the core engine: cats in human situations, fake scenarios, bodycam style
2. **Viral animal rescue / drama** — heroic animals, emotional stories (real or dramatized)
3. **AI animal scenarios** — animals as baristas, surfers, musicians, meeting attendees
4. **Funny pets / unexpected moments** — scroll-stopping real or AI-generated moments
5. **Multi-animal compilations** — themed clips stitched together

### Top Performing Formats
- Cat + human-world situation ("Cat Detained on Airplane", "Cat Stuck in a Meeting")
- Rescue/drama framing ("Dog Saves Florida Man", "Coast Guard Rescues Puppy")
- Grandma + animal ("Grandma Bear Vlog", "Grandma Shares Food with Mama Bear")
- Cats + quantity humor ("Too Many Cats", "He Had A Few Cats... He Lied")

### Humor Types That Work
- **Physical slapstick** — unexpected impact, falls, launches, collisions
- **Indifference** — animal does something absurd and acts like it's completely normal
- **Scale incongruity** — tiny animal, enormous drama (or enormous animal, tiny container)
- **Commitment to the bit** — animal stays in an impossible position like it's fine
- **Caught-in-the-act** — animal clearly doing something wrong, gets seen
- **Anthropomorphic stubbornness** — animal behaving like a difficult human

### What Doesn't Work
- Static cute — animal just sitting there looking adorable, no action
- Setup without payoff — situation established but nothing happens
- Too long a build — payoff must arrive within 3–4 seconds of action starting
- Overexplained premise — the visual carries the joke, not a caption

---

## THE PAYOFF PRINCIPLE

**This is the most important rule on this channel.**

Every clip needs: **SETUP → ACTION → PAYOFF**

The comedy — or the "can't look away" moment — lives in the PAYOFF. A clip without a payoff is just a cute animal. A clip with a payoff is content that gets shared.

### The Frozen Paw Problem (Real Example — Project 0002)
**What was generated:** Orange cat lying on a kitchen counter, paw extended mid-air. Cat holds still. Nothing happens.
**Why it failed:** No payoff. The situation is cute but the clip goes nowhere. 80% of a joke with no punchline.
**What it should have been:** Cat slowly pushes a plate across the counter → snags a piece of toast → bolts off screen with it in its mouth. That's the payoff. The trim window is the theft, not the setup.
**The fix:** The payoff must be written explicitly into the Kling prompt. The prompt isn't describing a vibe — it's scripting an action sequence.

---

## PROMPT ENGINEERING — KLING & IMAGE GEN

### The Problem with Vague Kling Prompts
Kling 2.6 I2V needs to know what physically happens — not just how the scene feels. A prompt like "cat holds paw mid-air, looks curious, natural lighting" produces exactly that: a cat holding its paw in the air. Nothing else.

### The Kling Prompt Formula
```
[Starting state — 1 sentence, matches the reference image]
[Specific action — what the animal does, step by step]
[Physical payoff — what actually happens at the end]
[Camera behavior — handheld drift, floor level, slight shake, etc.]
[Lighting + grain — realistic, domestic, imperfect]
```

### Bad vs. Good Examples
| Bad (Vague) | Good (Scripted) |
|---|---|
| "Cat holds paw mid-air, looks curious" | "Cat slowly slides paw forward one inch at a time toward the plate, hooks a piece of toast, then suddenly bolts off the counter with it" |
| "Two kittens wrestling on the floor" | "One kitten locks the other in a full headlock. The headlocked kitten flails its back legs frantically. Both freeze for a beat, then tumble sideways in a heap" |
| "Cat crammed into a small box" | "Cat is settled in the shoebox, completely at peace. It shifts slightly — the box crinkles inward. Cat ignores this completely, looks up at camera with a slow blink, then closes its eyes again" |

### The Trim Window Rule
**Generate 8–10 seconds. Trim to the 2–3 second window where the payoff lands.**
The trim window IS the clip. Everything before it is setup that gets cut. Write prompts knowing you're going to cut most of it — the payoff moment just needs to exist somewhere in the 10 seconds.

### Image Generation Rules (Nano Banana 2)
- Aspect ratio: `9:16` for vertical content
- Resolution: `2K`
- Style: **realistic, candid, domestic** — looks like someone grabbed their phone fast
- Lighting: natural indoor (window light, kitchen overhead, bedroom lamp) or outdoor
- No studio setups, no perfect lighting, no posed shots
- Backgrounds: lived-in — cluttered counters, rugs slightly bunched, real apartments
- The starting image should look like a still frame from a viral video someone already shot

### ⚠️ URL Expiry Warning
Nano Banana 2 image URLs **expire within ~2 minutes**. Kling I2V submission must happen immediately after image generation — in the same pipeline step, not a separate phase. Do not download the image first; submit the URL to Kling immediately.

---

## VIDEO FORMATS

### Primary: 10-Scene Compilation Short
The main content vehicle for NeonParcel.

| Property | Spec |
|---|---|
| Orientation | 9:16 vertical |
| Total length | 23–35 seconds |
| Scene count | 8–12 scenes |
| Scene length | 2–3 seconds each (trimmed from 10s raw) |
| Cut style | Hard cuts only |
| Audio | Bass interrupt at every cut + background music (no vocals) |
| End | Neon Parcel end screen appended (always) |

Why it works: Fast enough to hold attention, long enough to binge. Each cut is its own small payoff. The bass interrupt rhythm trains the viewer to anticipate the next hit.

### Secondary Formats (Each Gets Its Own Skill When Built)
- **Single-scene viral clip** — one perfect moment, 5–15 seconds, no compilation
- **Long-form vertical** — 2–5 min vertical, multiple segments, optional narration
- **Long-form horizontal** — YouTube only, 16:9, 5–20 min, chapter structure, thumbnail required
- **Narrated compilation** — 10-scene format with brief casual narration over each clip

### Platform Specs
| Platform | Orientation | Resolution | Max Length |
|---|---|---|---|
| YouTube Shorts | 9:16 vertical | 1080×1920 | 60s |
| TikTok | 9:16 vertical | 1080×1920 | 60s |
| Instagram Reels | 9:16 vertical | 1080×1920 | 60s |
| Facebook Reels | 9:16 vertical | 1080×1920 | 60s |
| YouTube Long-form | 16:9 horizontal | 1920×1080 | No limit |

Shorts do not require a custom thumbnail — YouTube auto-selects a frame.

---

## NARRATION GUIDELINES

### Default: No Narration
~95% of NeonParcel videos have no narrator. The visuals carry the content.

### When Narration Is Used
Brief, casual, reaction-style. Not documentary. Not Attenborough. Like a person watching the video with you and reacting.

**Good narration tone:**
- "Look at this cat go."
- "He did NOT just do that."
- "This dog has no idea what's about to happen."
- "I need everyone to see this."

**Never sound like this:**
- "Remarkably, the domestic feline exhibits a behavior that..." ❌
- "Welcome back to Neon Parcel, today we're looking at..." ❌

### Narration Rules
- Short sentences only — one line per clip maximum
- Appears only at the moment of the clip, not between clips
- Never over the bass interrupt hit
- Never over the end screen
- Voice TBD — no ElevenLabs voice ID locked yet for this channel

---

## AI GENERATION PIPELINE

### The Locked Workflow (Compilation Format)

```
Step 1: Write scene plan
        └── 10 scenes × {image_prompt, kling_prompt}
        └── Each kling_prompt has explicit SETUP → ACTION → PAYOFF

Step 2: Generate starting image (Nano Banana 2)
        └── Model: nano-banana-2
        └── aspect_ratio: "9:16", resolution: "2K", output_format: "png"
        └── Save URL immediately — expires in ~2 minutes
        └── DO NOT wait or download first

Step 3: Submit to Kling immediately (same pipeline step as Step 2)
        └── Model: kling-2.6/image-to-video
        └── input: { prompt, image_urls: [fresh_url], sound: false, duration: "10" }
        └── Poll until state == "success"
        └── Download raw.mp4

Step 4: Extract frames
        └── FFmpeg: fps=2 → 1 frame per 0.5s → 20 frames for 10s clip
        └── frame_number × 0.5 - 0.5 = timestamp in seconds
        └── Files: frame_0001.jpg through frame_0020.jpg

Step 5: Analyze frames
        └── Read key frames at t=1.5, 3.0, 4.5, 6.0, 7.5, 9.0
        └── Identify the 2–3s window where the payoff lands
        └── Document in trim_timeline.md

Step 6: FFmpeg trim each raw.mp4
        └── ffmpeg -i raw.mp4 -ss [start] -t [duration] -c:v libx264 -c:a aac trimmed.mp4

Step 7: Stitch (MoviePy)
        └── Load all trimmed.mp4 clips
        └── Concatenate
        └── [If specified] Mix Bass_Interupt.mp3 at each cut point (BASS_VOLUME = 1.3)
        └── [If specified] Mix background music (Suno, no vocals, low level)
        └── Scale end screen to match output resolution (no black borders)
        └── Append end screen (always)
        └── Export final .mp4
```

### API Endpoints
| Service | Endpoint | Key |
|---|---|---|
| Nano Banana 2 | `POST https://api.kie.ai/api/v1/jobs/createTask` | `KIE_API_KEY` in `.env` |
| Kling 2.6 I2V | `POST https://api.kie.ai/api/v1/jobs/createTask` | Same key |
| Poll status | `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=` | Same key |

### Key Scripts
| Script | Purpose |
|---|---|
| `tools/gen_neon_parcel_cats_real.py` | Full pipeline: images → Kling I2V → frames |
| `tools/neon_parcel_cats_real_stitch.py` | Trim + stitch + bass mix + end screen |

### Tool Paths
```
FFmpeg:  /opt/homebrew/bin/ffmpeg
Python:  /Library/Frameworks/Python.framework/Versions/3.13/bin/python3
yt-dlp:  /Library/Frameworks/Python.framework/Versions/3.13/bin/yt-dlp
```

### Project Output Structure
```
references/outputs/[ID]-[Project_Name]/
├── trim_timeline.md
├── [ID]-[Project_Name].mp4         ← final output
├── scene_01/
│   ├── starting_image.png
│   ├── starting_image_url.txt
│   ├── raw.mp4                     ← 10s Kling output
│   ├── trimmed.mp4                 ← 2–3s sweet spot
│   └── frames/
│       └── frame_0001.jpg … frame_0020.jpg
└── scene_02/ … scene_10/
```

---

## AUDIO STACK

### Bass Interrupt
- **File:** `references/channels/002_neonparcel/Assets/Bass_Interupt.mp3`
- **When used:** Only when explicitly specified — primarily on compilation formats
- **Placement:** At every hard cut between scenes
- **Volume:** 1.3× relative to clip ambient audio (30% louder — noticeable but not clipping)
- **Default:** OFF — must be requested per project

### Background Music
- **When used:** Only when explicitly specified — not added by default
- **Style:** Instrumental only (no vocals); cartoony/goofy for unhinged content, lo-fi chill for calm domestic content
- **Source:** Suno AI or trending royalty-free audio
- **Mix level:** Low — music is texture, bass interrupt and visuals carry the energy
- **Default:** OFF — must be requested per project

### End Screen — Always Appended
The end screen is always added to the final export, regardless of format.

| Format | File | Duration |
|---|---|---|
| Vertical (9:16) | `references/channels/002_neonparcel/Assets/Neon_Parcel_Endscreen_Vertical.mp4` | 4.27s |
| Horizontal (16:9) | `references/channels/002_neonparcel/Assets/NeonParcel_End_Screen_1080.mp4` | native 1080p |

**Resolution matching rule:** If main video output resolution exceeds end screen native resolution, scale the end screen up to match. No black borders, no letterboxing.
```bash
# Example: upscale end screen to match 1080×1920 vertical output
ffmpeg -i Neon_Parcel_Endscreen_Vertical.mp4 -vf scale=1080:1920 endscreen_scaled.mp4
```

---

## THUMBNAIL & TITLE SYSTEM

### Short-Form (Shorts / TikTok / Reels)
- **Thumbnail:** Not required — platform auto-selects frame
- **Title formula:** [Adjective] + [Animal] + [Situation] — hook-forward, curiosity loop, SEO-aware
- **Length:** 40–60 characters ideal
- **Examples:**
  - `This Cat Stole My Toast and Felt Nothing`
  - `Cats Going Feral at 3AM #Shorts`

### Long-Form (YouTube)
- **Thumbnail:** Required — dark/black background, one expressive animal close-up or peak action frame, high contrast, bold white text 3–5 words max, neon glow (orange or blue)
- **Title:** Hook + curiosity gap, under 70 characters
- **Description:** Hook sentence, what's in the video, timestamps if chaptered, hashtags at bottom

### Title Patterns That Work
- `[Animal] [Does Relatable Human Thing]`
- `[Person] Said [Lowball Claim]… [Reveal That It Was More]`
- `[Animal] [Saves/Rescues/Protects] [Human/Other Animal]`
- `[Animal] + ASMR / Podcast / Barista / [Trend]`

### Title Rules (All Formats)
- Use trending terms only if the video actually contains that content
- No keyword stuffing — title reads naturally
- Curiosity gap: viewer wants to click to resolve a question
- Emojis: optional, 1–2 max, only if it adds meaning
- Hashtags on Shorts: `#NeonParcel #Shorts` + 1–2 animal/topic tags

---

## REFERENCE SOURCING METHOD

### Where to Find References
1. **YouTube** — primary source
2. **TikTok** — secondary source

### How to Sort
- Filter by **views** (highest first)
- Filter by **upload date**: this year or this month only — ensures virality is current, not a 5-year-old accumulation

### What to Look For
- Animals doing something physically unexpected
- Situations where an animal goes somewhere or does something it shouldn't
- The "I can't believe that just happened" moment
- Bodycam, phone-grab, security cam angles — caught-on-camera energy

### How References Are Used
References inspire the **scene concept and humor type only** — they are not copied. The image prompt, Kling action prompt, and trim window are all original. The reference tells you what kind of payoff the audience finds funny; the AI content delivers its own version.

---

## FIXED CHANNEL ASSETS

| Asset | Path |
|---|---|
| Bass interrupt SFX | `references/channels/002_neonparcel/Assets/Bass_Interupt.mp3` |
| End screen (9:16 vertical) | `references/channels/002_neonparcel/Assets/Neon_Parcel_Endscreen_Vertical.mp4` |
| End screen (16:9 horizontal) | `references/channels/002_neonparcel/Assets/NeonParcel_End_Screen_1080.mp4` |

---

## LESSONS LEARNED (LIVING SECTION)

This section grows with every project. These are the learnings that change how future projects are approached.

### From Project 0002 — Neon_Parcel_Cats_Real (March 2026)

**URL expiry kills Phase 2.** Nano Banana 2 image URLs expire within ~2 minutes. Running image gen and Kling submission as separate phases causes 404 errors. Fix: pipeline mode — submit to Kling within seconds of receiving the image URL.

**Vague Kling prompts produce static clips.** Describing a situation without scripting the action produces a clip that looks correct but has no payoff. Every Kling prompt must specify what the animal does and what the physical outcome is. The action is not implied — it must be written explicitly.

**The image model matters for first-frame quality.** Nano Banana 2 at 9:16/2K produces a realistic, candid-looking starting frame that Kling animates naturally. The realism of the starting image directly affects how believable the final clip feels.

**Generate 10 seconds. Trim to 2–3.** Kling at `duration: "10"` gives enough footage to find the payoff window. The trim IS the clip — everything else is discarded. Frame extraction at `fps=2` (20 frames) gives sufficient granularity to locate the peak action window.

**The missing 20%** in the first Neon Parcel AI compilation was prompt depth. The situations were correct, the aesthetics were right, but several clips had no physical payoff — setup with no punchline. The fix is upstream in the Kling prompt, not in the edit.

---

## CHANNEL STATS (as of session date)
- Subscribers: 2,100
- Videos: 222
- Total Views: 2,687,976
- Avg views/video: ~12,108
- Best performing content: Cats + human situations, rescue drama

---

## AI PROMPT TEMPLATES

**For thumbnails:**
Create a YouTube thumbnail: black background, one expressive [animal] in center-right, neon [orange/blue] glow around subject, bold white text top-left reading "[title]", high contrast, mobile-readable, synthwave neon aesthetic, no clutter.

**For scene concepts (Kling):**
Use the formula:
[Starting state matching reference image] → [Specific step-by-step action] → [Physical payoff at the end] → [Camera: handheld drift / floor level / slight shake] → [Lighting: natural indoor, imperfect, lived-in]

**For video concepts:**
Generate a NeonParcel scene plan: [animal] placed in [human context / absurd situation], SETUP → ACTION → PAYOFF structure, each scene scripted with explicit physical action, punchy 3-second hook on first scene, visual storytelling only, internet humor tone, compilation format (10 scenes × 2–3s each).
