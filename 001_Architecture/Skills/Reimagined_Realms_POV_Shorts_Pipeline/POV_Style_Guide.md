---
name: pov-style-guide
description: One-time distilled style guide for Reimagined Realms POV Shorts, synthesized from Video-Analyzer runs on 2 reference videos (medieval peasant, Alcatraz prisoner). Read by the pipeline on every production — never re-derive from the raw references.
---

# POV Style Guide — Reimagined Realms POV Shorts

Synthesized from `Video-Analyzer` runs on two reference videos:
- `002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Case_Studies/001_POV_Medieval_Peasant/ANALYSIS.md`
- `002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Case_Studies/002_POV_Alcatraz_Prisoner/ANALYSIS.md`

## Core concept

First-person POV of someone waking up as a specific historical/situational persona. On-screen text establishes who/when/where in the opening beat. The body of the video is a sequence of short vignettes showing what that person's day (or fate) consists of — mundane chores, meals, labor, obligations — or, in a more dramatic take, a life-or-death turn of events. No dialogue anywhere — only diegetic foley/ambient sound plus mood-appropriate music. Each vignette gets one bold on-screen text caption labeling the beat. The premise itself is the hook ("POV: you wake up as ___"); the body is proof-of-concept vignettes of that premise playing out.

## Opening beat (always present)

- First shot: static POV, eyes-just-opened framing (lying in bed/cot, hands/body visible in frame, environment established around the edges).
- Audio: a groggy sigh/yawn as the very first sound — this is the "waking up" signifier every reference video used.
- Text overlay: appears within the first second (frame 0), white text, centered, establishing the premise **with the actual subject filled in** — never a literal blank ("POV: You Wake Up As An Egyptian Pyramid Builder", not "POV: You Wake Up As A ___"). This is locked: YouTube Shorts auto-grabs an early frame as the thumbnail, so the premise text must be legible and complete from the first frame, not a fill-in-the-blank the viewer never sees resolved. A second text beat then names era/location/date ("Medieval England, 1250 AD" / "Alcatraz — 1934, Execution Day").

## Pacing

- Target ~5s per vignette/scene (matches the plan's padding-to-65s-floor logic).
- Both references ran ~40s total (well under our 65s floor) with 7-12 distinct narrative beats — confirms 65s at ~5s/scene (13 scenes) is a reasonable floor to pad toward, not an artificial stretch.
- Structure can be either: (a) chronological montage of unrelated daily activities (Video 1's model — dawn to night, no throughline beyond "a day in this life"), or (b) an escalating mini-plot with a turn and a twist ending (Video 2's model — calm → tension → climax → twist). Both are valid POV Shorts formats; pick per-topic based on whether the persona's "day" has an inherent narrative arc (e.g. "execution day" has one, "peasant's ordinary day" doesn't need one).

## Camera conventions

- Default: **static POV** — most vignettes in both references use a fixed first-person frame with only the character's hands/body moving in-frame (spoon lifting, hands warming by fire, coins in a bowl).
- **Handheld POV** for any vignette involving walking (fetching water, escorted "last walk") — simulates a walking gait, adds physicality to movement beats.
- **Smooth forward tracking shot** for corridor/hallway "walking with purpose" beats (the prison "last walk") — distinct from handheld: this is deliberate, ominous, not casual walking.
- **Shaky handheld tracking** reserved for high-intensity action beats (the escape run) — the more urgent the moment, the shakier the camera.
- Camera motion should escalate with narrative tension if the video uses the escalating-plot structure (b) above; stay uniformly calm/static if using the chronological-montage structure (a).

## Transitions

- Hard cuts between vignettes are the default (no crossfades needed for the visual cut itself — note this differs from the audio-layer crossfade rule already locked in for narration-driven long-form Reimagined Realms videos, which does not apply here since there's no narration).
- Quick effect-frame transitions (a 1-2 frame distortion/warp effect, a single black frame) are acceptable punctuation between a climax beat and its resolution — used in Video 2 between the cliff-jump and the underwater reveal. Reserve for a genuine narrative pivot, not as decoration between every cut.

## Sound design

- No dialogue, ever.
- Opening sigh/yawn is mandatory.
- Foley matches the specific action of each vignette (water sloshing, coins clinking, fork scraping a plate, footsteps echoing, splashing, panicked breathing) — generated per-clip via the locked Mirelo/Sonilo SFX approach (pending the A/B test outcome from the design spec).
- Ambient bed under every scene (crackling fire, birds, tavern murmur, wind/waves) appropriate to the setting.
- Tension beats add a low ambient drone or rising score element — this is the Suno music bed's job, not foley's.
- Escalating structure (b) videos can add a "cathartic" sound moment at the climax (a scream, an exultant shout) — optional per-topic, not a rule for every video.

## Text overlay conventions

- White text, centered on screen.
- **Vertical position: top ~18% of frame (upper safe zone), for both title and per-vignette label captions** — locked after Tony's critique of the Pyramid Builder v1 render. This is the zone the eye is drawn to first on Shorts/Reels/TikTok, and it stays clear of the platform UI (caption/description/interaction buttons) that overlays the bottom of the screen. Do not default to mid-screen or bottom placement.
- Drop shadow present (explicitly confirmed in Video 2; assume it's standard even though Video 1's analysis didn't call it out separately — Video 1's font was described as serif while Video 2's wasn't specified as different, so treat font choice as a per-video creative decision, not a locked rule, but centered-white-with-drop-shadow as the locked placement/legibility baseline).
- One caption per vignette, appears at that vignette's cut, stays for the vignette's duration.
- Opening premise text is larger/more prominent than per-vignette labels (a title moment vs. a caption moment).

## What this style guide does NOT lock in

- Total runtime beyond the 65s floor (references were shorter; that's expected, not a target to match).
- A single narrative structure — chronological-montage vs. escalating-plot is a per-topic choice, not a fixed rule.
- Exact foley/music vendor (pending the Mirelo vs. Sonilo A/B test from the pipeline design spec).
