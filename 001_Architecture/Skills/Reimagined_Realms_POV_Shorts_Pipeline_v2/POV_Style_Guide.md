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

- **Locked, non-negotiable: strict first-person POV — never show what's physically impossible for the character's own eyes to see (their own face, the back of their own head, their own shoulder, or their own back).** Confirmed as a real failure mode 2026-08-12 (visually re-confirmed via dense per-second keyframe review — see `Case_Studies/003_Pyramid_Builder_I_Deep_Continuity_Review/Dense_Keyframes/`, not a text-only claim): the opening "waking up" shot starts as correct first-person (looking down at his own legs, matching what a person lying down would actually see), then drifts mid-shot into an external third-person view showing his own back and the side of his face as he sits up — a genuine camera-viewpoint break, not just a wrong-body-part-visible issue. The word "POV" alone is not sufficient instruction — every video prompt must explicitly state that the camera IS the character's own eyes (body-worn-camera framing) and ban the specific things a body-worn camera can never see. **This does NOT mean hands/forearms/legs must always be visible** — an earlier version of this clause over-corrected into mandating constant limb visibility in every shot regardless of context, which produced its own unnatural artifact (confirmed on Roman Gladiator, 2026-08-12: near-constant hands/legs in frame regardless of gaze direction). Whether hands/arms/legs appear should depend entirely on that scene's actual action and gaze direction, exactly like real human vision. This is now auto-enforced in code via `POV_LOCK_CLAUSE` in `shot_list_builder.build_video_prompt()` and `storyboard_generation.build_panel_prompt()` (duplicated across both — the image-generation stage is the one that actually determines visibility, since this pipeline locks composition at the first-frame image, not the video prompt) — every prompt built through those functions gets it automatically, so there is no need (and no reason) to hand-write this instruction per-shot.
- **Pose changes within one continuous shot risk this same drift.** A big pose change inside a single generation (e.g. lying down → sitting up, the exact case that produced the Pyramid Builder drift above) asks Seedance to hold a POV camera lock through more change than one continuous generation reliably manages. For any beat with a substantial pose change, split it into two separate generations instead of one: generate the first pose, extract its last frame, and hand that frame to the second generation as its `first_frame_url` (same multi-generation stitching technique documented in `Seedance-Prompting-Guide/SKILL.md` → "Chaining multiple generations into one continuous scene"). Don't trust one continuous generation to carry a major pose change through to completion.
- Default: **static POV** — most vignettes in both references use a fixed first-person frame with only the character's hands/body moving in-frame (spoon lifting, hands warming by fire, coins in a bowl).
- **Handheld POV** for any vignette involving walking (fetching water, escorted "last walk") — simulates a walking gait, adds physicality to movement beats.
- **Smooth forward tracking shot** for corridor/hallway "walking with purpose" beats (the prison "last walk") — distinct from handheld: this is deliberate, ominous, not casual walking.
- **Shaky handheld tracking** reserved for high-intensity action beats (the escape run) — the more urgent the moment, the shakier the camera.
- Camera motion should escalate with narrative tension if the video uses the escalating-plot structure (b) above; stay uniformly calm/static if using the chronological-montage structure (a).

## Scene-writing checklist (locked 2026-08-08, run this before finalizing any scene description)

Every scene description must pass all of these before it's turned into a generation prompt. Each item exists because skipping it produced a real, confirmed failure — not theoretical caution.

- **Anatomy/pose check** — does the described pose actually support the described action? (Lying flat cannot tie a shoe; sitting/kneeling is required.)
- **Camera-logic check** — from true first-person, what would the camera actually see doing this action? State it explicitly before writing the prompt.
- **Action-mechanics check** — verify the actual physical mechanism of the action: pushed or pulled, which direction it swings/lifts/twists/slides, which hand does the work. Confirmed failure: a door opened via a ring handle was described as "pushed open" when it's actually pulled — general pose/camera checks didn't catch this because it's a distinct, more specific check.
- **POV-visibility check** — before writing any physical contact from another character onto the POV character, verify the contact point is actually within a true first-person field of view (hands, forearms, chest-down at most). Never write contact with the POV character's own shoulder, back, top of head, or face — a body-worn camera at eye height cannot physically see those, no matter how the prompt is worded. Confirmed failure: "claps a hand on the POV character's shoulder" rendered as a hand on his knee with the leg raised at a wrong angle, because the model had no visible shoulder to work with. Fix: substitute a contact point that IS visible in true POV (a handshake, an object passed hand-to-hand) or remove the touch entirely (a nod).
- **Body-position-must-be-explicit check** — any "looking up/down/to a side" instruction must also state the character's overall body position (standing, sitting, kneeling, lying) — "looking up" alone is ambiguous between e.g. "standing, head tilted back" and "lying down looking at the sky." Confirmed failure: a victory scene meant to be standing with a raised fist, written only as "looking straight up," rendered the character lying on the ground instead.
- **Difficulty triage** — is this action inherently hard for the model (multi-limb tool interactions, ladder climbs, precise mechanical motion)? If so, substitute a simpler action that tells the same story beat instead of fighting the model.
- **Reference-conflict check** — if a scene needs both an exact environment match *and* a pose different from an existing reference image, don't ask for both in one image-to-image call (the reference image's own composition tends to dominate/override a conflicting pose instruction). Pick one to anchor, let the other ride on fresh generation.
- **Hand/limb laterality check** — any scene with hand-to-hand or hand-to-object contact between two characters must explicitly name which hand on each side is involved and, for a shared gesture like a handshake, state that both use the matching side (right-to-right, not left-to-right) — never leave it for the model to pick. Also anchor the POV character's own reaching arm/hand to its actual shoulder/side in the text. Confirmed failure: scene 6's handshake prompt named no hands on either side — the model rendered the POV character's own left arm ending in a hand with a right hand's thumb orientation, paired left-to-right with Brutus's hand, which isn't how people naturally shake hands. Full research and prompting technique: [Seedance-Prompting-Guide/SKILL.md](../Seedance-Prompting-Guide/SKILL.md) → "Hand/limb laterality in POV and multi-character shots."
- **Pose-change-within-a-shot check** — does this scene ask the character to change pose significantly during one continuous generation (lying → sitting, kneeling → standing, etc.)? If so, don't write it as a single shot — split it into two generations (first pose → extract last frame → hand to second generation as `first_frame_url`) rather than trusting one continuous generation to hold the POV camera lock through the whole pose change. Confirmed failure: Pyramid Builder's opening "waking up" shot (lying down → sitting up in one generation) drifted from correct first-person into an external third-person view of the character's own back partway through — visually confirmed via dense per-second keyframe review, 2026-08-12.
- **Perspective-distortion / foreshortening check** — an extreme camera angle (e.g. looking straight up at the sky) combined with a foreshortened limb thrust toward the lens can visually misread as a completely different pose than intended, even when every individual element in the prompt was technically correct. Confirmed failure: Roman Gladiator Scene 13 ("standing, arm raised in triumph, looking straight up") rendered a raised arm at extreme fisheye close-range that reads as a raised leg due to its thigh-like proportion and foreshortening, making a standing victory pose look like the character is lying on the ground — the words were right, but the combination of camera angle + limb foreshortening produced an image that reads wrong at a glance. This is checked at the whole-composition level, not by re-verifying each described element was included — ask "what does this actually look like as a shape," not just "did the model include what I asked for." Fix: when a gesture requires extreme foreshortening to render (an arm/limb thrust nearly straight at the camera), consider substituting the reaction it's meant to produce — e.g. a cheering, roaring crowd filling the frame at normal eye-level framing — instead of forcing the foreshortened body part into frame at all.

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
