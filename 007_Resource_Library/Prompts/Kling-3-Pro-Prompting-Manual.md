---
title: "Kling 3 Pro Prompting Manual"
type: "prompt"
category: "video-production"
tags:
  - video-production
  - kling
  - prompting
  - cinematic
  - manual
created: 2026-05-12
source: local
---

# The Ultimate Kling 3.0 Pro Prompting Manual

*A working director's reference, distilled from eleven primary sources across three research passes: the official Kling 3.0 user guide (via DataCamp's full walkthrough), fal.ai's API prompting guide, ImagineArt's 5-layer template, Travis Nicholson's styles compendium, Glif's 6-element framework, VEED's motion-intensity & negative-prompt system, Alici.ai's production-workflow guide (multi-shot beat mapping, POV style transfer, native-audio physics), Leonardo.ai's 4-element foundation with motivated camera language, Atlabs.ai's $1000-of-testing guide (time-coded sequencing, SFX notation, micro-motions, performance directions), Klingaio's physics-based motion fixes (heel-first walking, hand anchoring, text stability), and the Klingmotioncontrol UI tutorial (official limits, credit math, single-variable iteration). Built so that when you give me a script or idea, I can turn it into a Kling-ready prompt in one pass.*

---

## Part 1 — How Kling 3.0 Actually "Thinks"

Kling 3.0 is not a clip generator. It is a **cinematic intent engine**. Three things follow from that, and they govern every rule below:

1. **It reads scenes as direction, not description.** Prompts written like a director's notes outperform prompts written like a Pinterest caption. Lists of adjectives lose to ordered, sequential instructions.
2. **It supports up to 6 shots in a single generation, up to 15 seconds long.** Real narrative beats — setup, turn, payoff — fit inside one prompt. You don't have to stitch.
3. **Native audio is part of the prompt, not a post-step.** Dialogue, tone, ambient sound, and language are written *inline* with the visuals, and the model lip-syncs and voice-places against them.

The model's three biggest leverage points are: **multi-shot structure, subject/element binding, and explicit motion + audio attribution.** Everything else is decoration.

---

## Part 1.5 — The Official UI: Specs, Limits, and Credit Math

Hard numbers from the Kling 3.0 web interface. Useful when planning generations and budgeting credits.

### Hard limits
- **Prompt length:** up to **2,500 characters** (the field shows `0 / 2500`)
- **Duration:** **3 to 15 seconds** (slider)
- **Multi-shot ceiling:** 6 shots max in the Custom Multi-Shot UI (inline `Shot 1:` text has no hard ceiling)
- **Reference images per Element:** 3
- **Start Frame / End Frame:** JPG or PNG, max 10 MB each
- **End Frame requires a Start Frame** to be uploaded first

### Resolution and credit cost
- **Standard (720p):** ~13 credits/second — use for drafts and prompt testing
- **Professional (1080p):** ~17 credits/second — use for final deliverables
- With native audio enabled, the official Pro plan tier rates are higher: 12 credits/s at 1080p and 9 credits/s at 720p with audio; 8 credits/s at 1080p and 6 credits/s at 720p without audio (DataCamp testing of the Pro $32.56/mo plan with 3,000 monthly credits)

**Cost math:**
| Quality | Duration | Approx cost |
|---|---|---|
| Standard 720p | 5s | ~65 credits |
| Professional 1080p | 5s | ~85 credits |
| Standard 720p | 10s | ~130 credits |
| Professional 1080p | 10s | ~170 credits |
| Professional 1080p + audio | 5s | ~60 credits (Pro plan) |

**Money-saving rule:** Draft in Standard at 5s. Once the prompt is locked and the result is good, switch to Professional and extend duration for the final.

### Aspect ratios
- **16:9** — landscape (YouTube, web, presentations, TV)
- **9:16** — vertical (TikTok, Instagram Reels, YouTube Shorts, Stories)
- **1:1** — square (Instagram feed, cross-platform)
- **4:5** — portrait (Instagram feed alternate)

**Decide platform first, then generate.** Don't generate 16:9 and try to crop to 9:16 — you'll lose composition and waste credits.

### The single-variable iteration rule
After each generation, change **only ONE thing** before regenerating. Rewrite the prompt slightly, *or* switch aspect ratio, *or* adjust duration, *or* add a Start Frame. Never two at once. Why: if you change three things and the result improves, you won't know which change helped. Isolate variables, learn faster, waste fewer credits.

### Audio toggle: when to turn it off
- **Audio ON** for finished pitches, client previews, narrative scenes with dialogue
- **Audio OFF** when you'll edit in Premiere/CapCut/Resolve later, or when you need brand-safe licensed audio control, or when iterating on visuals only

### Auto-translation fallback
If you write dialogue in a language outside the supported five (Chinese, English, Japanese, Korean, Spanish), Kling auto-translates it to English. Useful safety net but plan for it — French dialogue won't stay French.

---

## Part 2 — The Master Prompt Template

Every Kling 3.0 prompt I write for you will be built in this order. This is the merged "5-layer" template (ImagineArt) plus fal.ai's audio attribution rules plus Kling's official multi-shot syntax.

```
[SCENE]      Location, time of day, lighting, atmosphere
[CHARACTERS] Who is present, named clearly, described once
[ACTION]     What happens, as a timeline — beat by beat
[CAMERA]     Shot type, movement, framing changes
[AUDIO]      Dialogue (attributed), tone, ambient sound, language
[STYLE]      The "Style Bible" line — same on every prompt in a project
```

You write these layers as flowing prose, not as headers. Headers are for me thinking; the model wants directorial paragraphs.

---

## Part 3 — The Six Hard Rules

These are non-negotiable. Every Kling guide converges on them.

### Rule 1 — Think in shots, not clips
If the idea has more than one beat, write more than one shot. Either label them explicitly (`Shot 1: ... Shot 2: ...`) or let Kling infer them from a clearly sequenced paragraph. Up to 6 shots per generation, up to 15 seconds total. Use the **Custom Multi-Shot** button when you need to lock per-shot durations; use inline `Shot 1 / Shot 2` text when you want more than 6 beats or a freer flow.

### Rule 2 — Anchor subjects early and never rename them
Pick a name or descriptor for each character on first mention and **reuse it verbatim** for the rest of the prompt. "The woman in the grey coat" stays "the woman in the grey coat." Never drift to "she," "the girl," "the brunette." Pronouns confuse coreference. fal.ai calls this *Structured Naming* and it is the single biggest fix for "the model swapped my characters."

### Rule 3 — Bind dialogue to a visible action
Before any line of dialogue, describe a physical action that identifies the speaker. Then attribute the line.

> The black-suited agent slams his hand on the table.
> **[Black-suited Agent, angrily shouting]:** "Where is the truth?"

Without the action anchor, the model guesses who is speaking. fal.ai calls this *Visual Anchoring*.

### Rule 4 — Describe motion explicitly, for both subject and camera
Vague motion = morphing. Say what the camera does over time: *tracks alongside, pushes in, holds, pans left, freezes when she stops, resumes on her exhale*. Same for the subject — break the action into steps, not a summary. Long takes especially need the camera's relationship to the subject defined every few seconds.

### Rule 5 — Attribute every line of audio
Use this exact structure for dialogue:

```
[Character name, tone descriptor, optional language]: "line"
```

Examples:
- `[Lead Detective, controlled serious voice]: "Let's stop pretending."`
- `[Grandmother, slow regional dialect, soft laugh]: "Back in my day, we didn't rush so much."`
- `[Boy, casual tone, Korean]: "숙제 다 했어?"`

For ambient audio, write it inline as a sentence: *"Rain tapping softly on the roof. Low lo-fi music from the speakers."* Kling handles foley and score from plain English.

### Rule 6 — Control sequence with linking words
Between dialogue lines, use words that force temporal order: *immediately, then, after a beat, pause, suddenly*. Without these, the model can merge two characters' lines into one mouth. fal.ai's optional trick: literally write *"this is when the speaker switches"* if the rhythm is tricky.

---

## Part 4 — Multi-Shot Syntax (the two modes)

**Mode A — Inline narrative (best for dialogue scenes, up to many beats):**
Write the scene as one paragraph with `Shot 1:`, `Shot 2:`, etc. embedded. Kling parses them. This is what the official guide uses for the European villa scene and the truck-driver scene. No 6-shot ceiling because it's text-driven.

**Mode B — Custom Multi-Shot UI (best for precise per-shot timing):**
Click the *Custom Multi-Shot* button under the prompt box. Write each shot in its own field and set its duration. Hard-capped at 6 shots. Use this when you care about a specific 3s + 5s + 2s split, or when inline parsing is misreading your beats.

When in doubt: **inline for storytelling, Custom Multi-Shot for precise timing or commercials.**

---

## Part 5 — Subject Binding & Omni Mode (Character Consistency)

This is what makes Kling 3.0 a production tool instead of a toy.

### Subject Binding (single video)
After uploading a first-frame image, toggle **"Bind elements to enhance Consistency."** You can attach up to 3 reference images per element (e.g., front, side, angry expression). Give the element a name and optionally a voice. The model locks features and stops "inventing" what it can't see in frame one.

**Use it whenever:** the first frame doesn't show the full character (sunglasses, profile, half-body) and the camera is going to move.

### Omni Mode (multi-element scenes)
Omni lets you create reusable Elements — characters, props, locations — and reference them in any prompt with `@`. Type `@` and a picker opens.

```
Shot 1: Mid-shot, background @CoffeeShop. @Jamie and @Sam sit on the couch as @Alex rushes in.
Shot 2: @Alex says, "I just liked my ex's photo from 2016."
Shot 3: @Jamie turns and says, "How bad?"
```

`@Image` references a scene/background element. Character elements get named (`@Grace`, `@Alan`). Even animals work (`@Samoyed`).

**Use Omni when:** you need the same character across multiple separate generations (the only reliable path to longer-form content), or when a single scene has 3+ named characters interacting.

**Building good Element references:** generate 3 angles of each character (front, ¾, expression variant). For locations, one establishing shot is enough. For props, one clean shot.

---

## Part 6 — Audio, Dialogue & Languages

### Supported speech languages
Chinese, English, Japanese, Korean, Spanish. Specify the language inline if it's not English:

```
[Vendor, friendly tone, Japanese]: "今日は寒いですね。"
[Tourist, slightly accented Japanese]: "はい、でも雰囲気が素敵です。"
```

### The four audio principles (fal.ai canonical table)

| Principle | What to do |
|---|---|
| **Structured Naming** | Unique, consistent character labels. Never swap to pronouns. |
| **Visual Anchoring** | Describe an identifying action *before* each line. |
| **Audio Details** | Give each character a distinctive tone/voice descriptor and reuse it. |
| **Temporal Control** | Use *immediately / then / pause / suddenly* between lines. |

### Tone descriptors that actually work
*trembling, shouting, whispering, calm but threatening, sleepy amused, urgent, hesitant, cold, raspy, voice cracking, fast urgent, controlled serious, sharp defensive, warm nostalgic, exhausted.*

Mix tone with delivery: `[Mom, fast urgent voice]`, `[Detective, calm but threatening tone]`.

### Ambient & score
Write it as a setting sentence at the top of the scene or above a beat:
- *"Rain tapping softly on the roof. Low lo-fi music playing from the speakers."*
- *"A sad piano chord enters quietly."*
- *"Music tightens with a rising pulse."*

Kling renders these natively.

---

## Part 7 — Image-to-Video: Lock First, Then Move

When you start from an image, treat it as an anchor. The model is excellent at preserving identity, layout, and **on-image text** (logos, signage, product labels) — which is why it's the best current model for branded content.

**Write the prompt as how the scene evolves *from* the image, not what the image already shows.** Don't re-describe what's visible. Describe the motion, camera move, environmental change, and what happens next.

For products with text on them (your Teranga Eats baobab logo case): mention the text explicitly in the prompt — *"the baobab logo on the bag remains crisp and readable as the camera pushes in"* — and Kling will preserve it through the motion.

---

## Part 8 — The Style Bible (consistency across a project)

Pick one style sentence and append it to **every** prompt in the same project. This is how you get visual cohesion across separately generated shots.

**Example Style Bibles:**

- *Cinematic realism, 35mm film grain, anamorphic lens flares, moody teal-orange color grade, shallow depth of field, high production value.*
- *Documentary handheld, natural daylight, slight motion blur, muted color grade, authentic feel, no music.*
- *Wes Anderson symmetry, pastel palette, deadpan composition, centered framing, soft even lighting.*
- *Blade Runner cyberpunk, neon reflections, rain-slicked streets, volumetric haze, deep teal and magenta.*
- *Ridley Scott prestige, low-key chiaroscuro, golden hour rim light, anamorphic widescreen, atmospheric haze, IMAX-grade detail.* ← good base for your prophecy/Jerusalem work
- *West African daylight commercial, warm naturalistic color, golden hour sun, shallow depth, soft lift to skin tones, premium food-photography sheen.* ← good base for Teranga Eats

### Style menu (pick one per project, then stop changing it)

**Cinematic / film:** cinematic realism · Hollywood blockbuster · film noir · Wes Anderson symmetry · Christopher Nolan grounded · Tim Burton gothic · Blade Runner cyberpunk · Ridley Scott prestige

**Visual / aesthetic:** photorealistic 8K · Studio Ghibli hand-drawn · vintage 1990s VHS · high-fashion editorial · epic fantasy with volumetric god rays · documentary handheld

**Lighting / mood:** golden hour magic hour · moody night with practical street lamps · dramatic chiaroscuro · soft diffused window light

---

## Part 9 — Camera Language Kling Understands

Lead with these. They are not optional in 3.0 — without camera direction, the model defaults to static framing.

**Shot sizes:** wide establishing · medium · medium close-up · close-up · macro close-up · extreme wide · over-the-shoulder · profile · POV · two-shot

**Movements:** dolly in / dolly out · push in · pull back · tracking shot (alongside / behind) · orbit · slow pan left/right · tilt up/down · crane · handheld · static lock-off · whip pan · rack focus

**Lens / framing:** anamorphic · shallow depth of field · deep focus · low angle · high angle · Dutch tilt · symmetrical composition

**Coverage language:** shot-reverse-shot · cutaway · insert · establishing-to-close progression

---

## Part 10 — The Constraint Sandwich (compact prompt method)

When a single-shot prompt is enough, use this 3-line structure:

1. **Subject Anchor** — who and where
2. **Shot + Action** — framing and what happens
3. **Constraints** — what must stay stable + Style Bible line

> *A cyberpunk detective in a long trench coat, standing in a rain-slick neon alley. Slow dolly-in as he lights a cigarette and exhales; smoke catches the magenta sign behind him. Preserve character identity across the move, realistic rain physics, reflections sharp on wet pavement. Cinematic realism, 35mm film grain, moody teal-magenta color grade.*

---

## Part 11 — Common Failure Modes & Fixes

| Failure | Cause | Fix |
|---|---|---|
| Two characters swap mid-scene | Pronouns or inconsistent naming | Lock one descriptor per character; never use "she/he" |
| Wrong character speaks the line | No visual anchor before dialogue | Add an identifying action immediately before the line |
| Lines merge into one mouth | No temporal linking words | Insert *immediately / then / pause* between lines |
| Static framing despite movement prompt | Camera direction was vague | Specify shot size + movement verb + duration relationship |
| Character morphs across cuts | First frame underdetermined | Use Subject Binding with 3 reference images |
| Shot 1 starts empty / wrong | Inline shot parsing misread | Switch to Custom Multi-Shot UI, or provide a first-frame image that already contains the characters |
| Logo / text degrades during motion | Not mentioned in prompt | Explicitly state the text remains crisp and readable |
| Tone feels flat | No tone descriptors on dialogue | Add `[Name, <tone> voice]` to every line |
| Background invents extras | Scene under-described | Add a specific ambient detail and an exclusion (*"empty café except for the two of them"*) |

---

## Part 11.5 — Kling 3.0's Known Weaknesses (design around them)

Every Kling guide that actually tested the model converges on the same blind spots. Don't fight them — design around them.

- **Ultra-close beauty/skin detail.** Kling 3.0 is less reliable for luxury close-up beauty shots and pore-level skin detail. If a shot requires perfect skin, frame slightly wider or shoot it elsewhere.
- **Extreme facial close-ups during rapid motion.** Distortion appears around eyes and mouth. Either slow the motion or pull the camera back.
- **Multiple subjects performing independent complex actions simultaneously.** Causes tracking issues and identity confusion. Stagger the actions in time, or split into shots.
- **Precise product label rendering at small scale.** Fine for mid-frame logos and crisp typography (this is one of Kling's actual strengths from a clean image input), but small text on a moving product can degrade. Mention the text in the prompt and hold it large enough to read.
- **Physics-defying actions.** Levitation, impossible balance, floating objects — the model fights you. Stay inside realistic physics.
- **Numerical specifics.** Don't say "5 trees" or "6 puppies" — Kling won't count reliably. Say "a small cluster" or "a handful." For split-screens, *do* specify the number of panels ("4 camera angles").
- **Complex physical trajectories.** Bouncing balls, projectile arcs, juggling — these are still unreliable. Avoid building shots around them.

**Design rule:** play to Kling's strengths — fast kinetic action, complex camera reveals, photorealistic textures, fabric/water/smoke physics, multi-shot pacing, native audio rhythm. Frame around the weaknesses.

---

## Part 11.6 — Motion Intensity Scale (numerical control)

VEED documents that Kling responds to explicit motion intensity values. Adding this number to your action description gives you predictable, dial-able control instead of letting the model guess.

| Range | Energy | Use for | Example phrasing |
|---|---|---|---|
| **0.1 – 0.3** | Subtle / minimal | breathing, slight sway, slow blink, gentle gesture, contemplative stillness | *"motion intensity 0.2, barely-perceptible sway"* |
| **0.4 – 0.6** | Natural / moderate | walking, conversational gestures, normal handling of objects, relaxed pace | *"motion intensity 0.5, relaxed natural pace"* |
| **0.7 – 1.0** | Dynamic / energetic | running, dancing, jumping, fighting, fast camera moves, intense action | *"motion intensity 0.9, explosive sprint"* |

**How to write it:** drop the value directly into the action sentence. *"She walks slowly through the garden, motion intensity 0.5, relaxed natural pace."*

**Word-only equivalents (when you don't want to use numbers):**
- **Subtle:** gentle, slow, slight, barely-perceptible, minimal, contemplative
- **Moderate:** natural, steady, conversational, measured, relaxed
- **Dynamic:** rapid, energetic, dramatic, explosive, frenetic, urgent

Match motion language to the mood: smooth/steady for calm scenes, jerky/handheld for tension, explosive for action.

---

## Part 11.7 — Negative Prompts (prevent artifacts)

Kling 3.0 supports negative prompting to suppress recurring artifacts. Add a negative line at the end of any prompt that's been giving you trouble.

**General-purpose negative prompt (drop-in default):**
```
Negative: motion blur, face distortion, warping, morphing, inconsistent physics, 
floating objects, unnatural movements, extra limbs, background shifting, 
duplicated characters, low detail, watermark, text artifacts
```

**Targeted negatives by problem:**
- **Face morphs:** `Negative: face distortion, warping eyes, melting features, mouth artifacts`
- **Hand/limb errors:** `Negative: extra fingers, fused hands, missing limbs, malformed hands`
- **Physics breaks:** `Negative: floating objects, levitation, gravity errors, clipping through surfaces`
- **Background drift:** `Negative: background morphing, environment shifting, scene inconsistency`
- **Lip-sync errors:** `Negative: misaligned mouth, robotic lips, voice mismatch, asynchronous speech`

Use sparingly — over-stacked negatives can flatten output. Target the specific failure you're seeing.

---

## Part 11.8 — Glif's 6-Element Sentence Format (alternative compact method)

Glif's framework is the second canonical compact prompt structure (alongside the Constraint Sandwich in Part 10). It packs six elements into one flowing sentence, written like a continuous take rather than a list.

**The six elements, in this order:**
1. **Camera** — what type of shot and how it moves
2. **Subject** — who/what is on screen and what they're doing
3. **Environment** — where the scene takes place
4. **Lighting** — the actual light source and how it feels
5. **Texture** — physical details that sell the realism
6. **Emotion** — the mood/tone of the moment

You don't have to hit all six every time, but the more you include, the more control you have.

**Worked example (anatomy of a strong single-sentence prompt):**

> *Static tripod camera in narrow neon-lit ramen shop, condensation fogs the window, couple sits side by side under flickering magenta sign, steam rising from bowls as they eat noodles in slow synchronized rhythm, broth splattering gently, their faces softly illuminated by red neon glow, shot on 35mm film with shallow focus and glowing bokeh behind them.*

- **Camera:** static tripod, shot on 35mm
- **Subject:** couple eating noodles in synchronized rhythm
- **Environment:** narrow neon-lit ramen shop
- **Lighting:** flickering magenta sign, red neon glow
- **Texture:** condensation, steam rising, broth splattering
- **Emotion:** shallow focus and glowing bokeh — intimate, cinematic warmth

It reads like one continuous take, not a list of keywords. That flow is what gives Kling the information it needs to generate coherent motion.

### The four Glif rules

1. **Motion verbs matter.** Use cinematic phrasing — *dolly push, whip-pan, shoulder-cam drift, crash zoom, snap focus*. Generic words like *moves* or *goes* give Kling nothing to work with.
2. **Texture = credibility.** Include grain, lens flares, reflections, fabric sheen, condensation, smoke, sweat, breath in cold air. Tactile details are what make the output feel physically real.
3. **Describe the temporal flow.** Tell Kling how the shot evolves: beginning → middle → end. Continuity in the prompt produces coherent motion instead of a frozen moment.
4. **Name real light sources.** Don't say "dramatic lighting." Say *neon signs, candlelight, golden hour, LED panels, flickering fluorescent tubes, practical street lamps, magic-hour rim light*. Real sources produce real results.

### Weak prompts vs strong prompts

| Element | Weak | Strong |
|---|---|---|
| Camera | *"camera follows person"* | *"handheld shoulder-cam drifts behind subject with subtle sway"* |
| Subject | *"a woman walking"* | *"woman in red dress, heels clicking on wet cobblestone"* |
| Environment | *"in a city"* | *"narrow Tokyo alley, steam rising from grates, vending machines glowing"* |
| Lighting | *"dramatic lighting"* | *"flickering neon signs casting magenta and cyan across wet pavement"* |
| Texture | *"it looks realistic"* | *"rain beading on leather jacket, condensation on glass, visible breath"* |
| Motion | *"she walks away"* | *"she turns slowly, hair catching the light, then disappears around the corner"* |

---

## Part 11.9 — Leonardo's 4-Element Foundation (the absolute minimum)

When a prompt is failing because it's too sparse, Leonardo's framework is the diagnostic. Every Kling prompt needs at least these four elements — if any one is missing, the model is forced to guess.

1. **Subject** — the primary focus (character, creature, object)
2. **Action** — what the subject does
3. **Context** — where and when it happens (setting, time of day, environment)
4. **Style** — the visual aesthetic (genre, tone, format)

These four are the foundation. Camera, lighting, framing, and lens are *optional modifiers* on top — but if any of the four foundation elements is missing, fix that first.

### Motivated camera moves

Leonardo's most useful contribution is the principle of the **motivated camera move**: every camera movement should have a narrative reason. The audience should feel *why* the camera is moving, not just see that it is.

- **Pan-to-reveal:** the camera leaves a character's reaction to show what caused it. *"The camera pans slowly to the right, moving away from the detective's shocked face, who remains petrified. The pan gradually and deliberately reveals a massive clue board on the wall, covered in photos, maps, and red string."*
- **God's-eye crane:** a high crane shot pulls up and away from a character to make them seem small, isolated, or overwhelmed by their environment. Use for grandeur, vastness, defeat, or epiphany.
- **Hero tilt-up:** start low-angle on a subject's feet, slow tilt up to the face — makes them appear powerful and heroic.
- **Dolly push-in vs zoom (important distinction):** a dolly *moves the entire camera through space* — the audience feels like they're stepping toward the subject. A zoom changes the focal length and remains static — it feels unnatural and stylized. **Default to dolly. Use zoom only when you want that hyper-stylized, artificial feel.**

### Speed and direction matter

When you specify a camera move, also specify *how fast* and *in what direction*:
- *"slow dolly-in"* vs *"crash zoom"* — speed sets the emotional register
- *"pan from left to right across the city"* — defining start and end points gives the model a clear arc
- *"tracking shot with slight handheld shake"* — layering movements creates texture
- *"smooth for calm, jerky for tension"* — match movement quality to mood

---

## Part 11.10 — Ad Production: The Beat Map Workflow

For commercial work (Teranga Eats, etc.) — this is the workflow Alici.ai documents from real ad-production testing. **Structure beats prompting.** Design the edit before you generate anything.

### The 4–6 scene beat map

| Scene | Job | Length |
|---|---|---|
| **Hook** (Scene 1) | The visual spike that stops the scroll | 3–5s |
| **Stakes** (Scenes 2–3) | The tension, context, or problem | 5–10s combined |
| **Turn / Payoff** (Scenes 4–5) | The product moment or resolution | 5–10s combined |
| **Exit** (Scene 6) | A clean end frame for CTA / brand lockup | 2–3s |

For a Netflix-style "escape reality" or "transformation" narrative:
1. Real-world setup (candid, believable)
2. Trigger moment (product activates / portal opens)
3. High-concept world (Kling's strength zone — kinetic, photoreal, atmospheric)
4. Return + brand lockup (clean end frame)

### Multi-shot prompt structure for ads

```
Master Intent: [One sentence: what this video is, tone, genre, what the viewer should feel.]

Scene 1 (5s): [Camera angle + subject + setting]. [Immediate hook moment].
Scene 2 (5s): [New camera angle]. [Escalation or context reveal]. [Specific motion].
Scene 3 (10s): [Peak action or narrative turn]. [Subject position + motion direction].
Scene 4 (5s): [Resolution beat or product clarity]. [Clean end frame].
```

### The 5-step ad production workflow (LTX-Studio-inspired, applied to Kling)

1. **Lock your character before writing any story.** Define them like a casting note — one wardrobe anchor, one facial signature, one emotional baseline. Reuse across every shot. If the character drifts between scenes, your ad looks like a collage.
2. **Lock a visual style reference.** Commit to a realism level, color palette, and lens language *before* storyboarding. This is what makes an ad feel like one world.
3. **Generate composition variants first.** Before animating, scout your best camera angle. Generate a 3×3 grid of framing options (using a separate image tool — Nano Banana, Midjourney, etc.), pick the strongest still for product readability and text negative space, *then* hand it to Kling as a first-frame.
4. **Build the beat map (4–6 scenes).** Each scene gets one job, one camera move, one action.
5. **Iterate rhythm before frame quality.** Watch the first pass with sound off — is the story readable? Then with sound on — does pacing feel right? Only then regenerate the failing scene.

### The most important workflow rule: regenerate only the weakest scene

When a sequence isn't working, **judge the weakest scene, not the whole sequence.** Regenerate that one scene only. Don't restart the full generation unless your visual style anchor is fundamentally wrong. This single habit cuts iteration time and credit cost more than any prompt-engineering trick.

### Pro tip from Alici testing
> *"When a hook isn't working, regenerate Scene 1 only — not the entire sequence. That single workflow change cuts iteration time significantly."*

---

## Part 11.11 — POV Style Transfer: The 4-Layer Architecture

This is the technique for keeping a single recognizable character across radically different visual aesthetics — anime → photoreal → oil painting → cyberpunk in one continuous video. It comes from real Alici.ai field testing and is the most reliable way to push Kling 3.0 across style boundaries without losing the subject.

### The architecture

1. **Establish (Shots 1–2, third-person):** Lock the character's face, wardrobe, and emotional baseline in two clear shots. The model needs to *see* them clearly before it can carry them.
2. **Enter POV (Shot 3):** Switch to first-person perspective. The viewer becomes the character. *This is the key mechanic.*
3. **World-hop in POV (Shots 4–6):** Three consecutive style shifts. Because you're in POV, the model doesn't need to render the protagonist anymore — only the world around them. That's what frees up the consistency budget for aggressive aesthetic changes.
4. **Final break (Shot 7):** Switch the medium entirely (anime illustration, oil painting, watercolor, claymation). The character returns to frame, now rendered in the new style.

**Why it works:** rendering a specific face and body consistently *through* a foreign aesthetic is the hardest thing the model has to do. POV removes that requirement entirely — the camera only has to move through a new world. With that constraint lifted, the model can push much further on style.

### The 7-shot rollercoaster template (proven, copy-paste blank)

```
Shot 1: A [medium/wide] shot of [character] in [scene]. [Color palette]. [Emotional action].
Shot 2: A [close-up] shot of [character]. [Emotion detail]. Background shows [speed/motion].
Shot 3: A first-person POV shot from [position]. [Main visual]. [Environment] visible [relation].
Shot 4: A POV shot as [element] transforms into [World A — style + materials + atmosphere].
Shot 5: A POV shot through [World B — signature visuals]. Motion is [tempo].
Shot 6: A POV shot as [movement] emerges into [World C — hyper-real place, lighting, detail].
Shot 7: A transition into [medium/style]. [Character in new style]. [Peak emotion + background].
```

### Worked example (the validated rollercoaster prompt)

> **Shot 1:** A medium shot from behind the head of a blonde woman as she sits in a rollercoaster car. The sky is a vibrant, deep pink and orange sunset. She suddenly turns her head to the side with an expression of intense shock and terror.
> **Shot 2:** A close-up, front-facing shot of the woman in the rollercoaster car. Her hair is blowing wildly in the wind, and her eyes are wide with fear as she screams.
> **Shot 3:** A first-person POV shot from the front of the rollercoaster as it rapidly ascends a steep, metal track. Below, an amusement park is visible.
> **Shot 4:** A POV shot as the rollercoaster track transforms into a soft, pink fuzzy material. The coaster climbs a bright green, rounded hill populated by white fluffy sheep.
> **Shot 5:** A POV shot through a futuristic, dark tunnel illuminated by concentric rings of glowing white and pink neon lights. Motion is extremely fast and dizzying.
> **Shot 6:** A POV shot as the rollercoaster emerges into a hyper-realistic New York City street during golden hour, track running down the center of the avenue, sun setting at the end of the street.
> **Shot 7:** A transition into an anime-style illustration. The woman, drawn in a classic 90s anime aesthetic, stands in the moving coaster car with arms raised, screaming as sun rays burst behind her.

This template is reusable. Swap the character, swap the three "worlds," swap the final medium. The architecture stays.

---

## Part 11.12 — Native Audio Through Physics (the right way to prompt sound)

The most counter-intuitive Kling 3.0 finding from Alici's testing: **don't write sound instructions. Write physical actions, surfaces, and materials. The audio generates from the physics description.**

### Wrong vs right

| Wrong (sound instruction) | Right (physics description) |
|---|---|
| *"add ambient footsteps"* | *"footsteps on concrete steps"* |
| *"include crowd noise"* | *"a dense crowd of partygoers shuffling and talking"* |
| *"add fabric rustling sound"* | *"coat flapping dramatically as he turns"* |
| *"play tense music"* | *"music tightens with a rising pulse"* (still works because it's a *progression*, not just a label) |
| *"car engine sound"* | *"engine revving as the tachometer climbs"* |

### Why it works

The model infers audio from the physics it sees. *Concrete steps* → footstep resonance. *Coat flapping* → fabric whip. *Cigarette smoke trailing* → quiet ambient texture. *Glass clinking* → ceramic tones. *Rain on leather* → soft tapping.

None of these required a sound instruction. The physics description generated the audio.

### The full audio toolkit (combine these)

1. **Surface + material + motion + timing** — for foley (footsteps, fabric, impacts, water).
2. **Ambient atmosphere line** — one sentence at scene-top describing the environmental audio bed (*"Rain tapping softly on the roof. Low lo-fi music from the speakers."*).
3. **Score progression cues** — describe how music *evolves*, not just what it is (*"a sad piano chord enters quietly," "music tightens with a rising pulse," "ambient hum drops out"*).
4. **Dialogue with attribution** — `[Name, tone, optional language]: "line."` (see Part 6).
5. **Linking words for rhythm** — *immediately, then, pause, suddenly* between dialogue lines.

### Earn your duration

If you're using Kling's 10s or 15s tier, write an *arc*: initiation → escalation → resolution. A 15-second static description wastes the duration budget and you'll get a frozen moment that just runs longer. **If your prompt doesn't have a beginning, middle, and end, neither will your clip.** Long clips reward structure; short clips tolerate sparseness.

---

## Part 11.13 — Realistic vs Experimental: Same Concept, Two Energies

Glif's most useful creative principle: run the same concept through two stylistic lenses. The realistic version leans on texture and physicality. The experimental version leans on surrealism and abstract motion. Both work because they give Kling specific visual instructions.

**Realistic version of "woman eating pizza at a party":**
> *Handheld camcorder footage zooming in erratically on woman's face as she devours a messy slice of pizza, melting mozzarella stretching and dripping, bright red tomato sauce smearing across her lips, VHS aesthetic with heavy grain, dim party lighting with colored gels.*

**Experimental version of the same concept:**
> *Handheld shoulder-cam drifting through endless mirror maze reflecting multiple versions of two women eating food infinitely, strobing pink and cyan light washing over reflections, dripping sauces morph into shimmering liquid chrome, camera performs continuous circular orbit as reflections distort in rhythm with pulsing ambient bass.*

When you're stuck on a concept, write both versions. You'll learn which direction the idea actually wants to go.

---

## Part 11.14 — Physics-Based Motion Fixes (the technique that prevents AI moonwalk)

The single most useful trick from Klingaio's testing: **describe the physics, not just the action.** Kling 3.0 calculates motion mechanically — give it the mechanics and the artifacts disappear.

### Walking — fix sliding feet
Instead of *"a man walking,"* write the biomechanics:

> *"He walks at a steady pace, each foot landing **heel-first**, then **rolling forward** with visible **weight transfer**. Arms swing naturally at his sides."*

Why it works: "heel-first" and "weight transfer" force the model to calculate ground contact, which prevents the floating-feet AI moonwalk.

### Hands — fix floating/morphing fingers
**Never let hands move freely in empty space. Anchor them to an object.**

| Wrong | Right |
|---|---|
| *"She moves her hands"* | *"Her fingers firmly grip the edge of the ceramic coffee cup."* |
| *"He gestures while speaking"* | *"His hand rests on the table, thumb tapping the rim of his glass as he speaks."* |
| *"She reaches out"* | *"She wraps her fingers around the door handle and pulls."* |

Hand-against-object beats hand-in-air every time.

### Texture — fix the "plastic" / over-smoothed look
Kling 3.0 defaults toward perfect, smiling, slightly plastic faces. To break that default, add tactile details to the prompt:

> *"film grain, skin pores, sweat, fabric creases, condensation, visible breath in cold air, subtle blemishes, hair flyaways"*

### Text on objects — fix morphing labels
For any on-screen text, logo, or product label, add this exact phrase:

> *"...ensuring the text **remains stable and readable throughout the motion**."*

Worked example for a product shot:
> *"Slow macro dolly-in shot of a luxury crystal perfume bottle on a velvet pedestal. Clearly embossed on the glass label is the word 'ETTREAL' in an elegant gold serif font. The bottle slowly rotates 45 degrees, ensuring the text 'ETTREAL' remains perfectly stable and readable throughout the motion."*

This is critical for Teranga Eats branding — the baobab logo and any wordmark needs this phrase.

### The "perfect smile" default — fix with negatives
Kling tends toward upbeat, smiling, polished faces unless told otherwise. For gritty, real, serious looks, use this negative line:

> *"Negative: smiling, cartoonish, 3D render, smooth plastic skin, perfect teeth"*

---

## Part 11.15 — Time-Coded Duration Sequencing (granular pacing control)

Beyond the standard `Shot 1 / Shot 2` format, Atlabs documents that Kling 3.0 also accepts **time-stamped sequences within a single prompt**. This gives you frame-accurate pacing control without using the Custom Multi-Shot UI.

### The format

```
First sequence (0-1 seconds): [opening beat, often slow motion or static]
Second sequence (1-4 seconds): [middle action, usually the main motion]
Third sequence (4-7 seconds): [resolution beat, close-up or pull back]
```

### Worked example (sports hero shot)

> *Stadium tunnel, dim lighting, distant crowd roaring. American football players in full gear.*
> *First sequence (0-1 seconds): Football players walking out of tunnel, dramatic slow motion.*
> *Second sequence (1-4 seconds): Shaky handheld camera movement with quick pans and slight zooms, following the action.*
> *Third sequence (4-7 seconds): Close-up on player's face, determination in their eyes, crowd roaring in background.*

### Why use time codes instead of `Shot 1:`
- **Pacing inside one continuous shot.** When you want speed/intensity changes inside a single take rather than hard cuts between shots.
- **Speed ramps.** Time codes let you describe acceleration: *"Speed ramp from 40% to 100% as the action intensifies."*
- **Mixed pacing.** Slow-mo intro → real-time middle → close-up payoff, all in one generation.

### Speed ramp template
```
Speed ramp from [40%] to [100%] as [trigger action], finishing on [final framing].
```

---

## Part 11.16 — Micro-Motions: How to Make Static Scenes Feel Alive

Atlabs's most valuable creative principle: **even in a "static" scene, the prompt should describe micro-motions.** Without them, Kling generates a frozen tableau that just runs longer. With them, the scene breathes.

### The micro-motion library
Add 2–4 of these to any scene that risks feeling static:

- **Breathing** — *"chest rising and falling slowly"*
- **Blinking** — *"slow deliberate blink"*
- **Subtle hand movements** — *"thumb idly tracing the rim of the cup"*
- **Drifting dust** — *"dust particles catching the shaft of sunlight"*
- **Fabric sway** — *"curtain billowing gently in the breeze"*
- **Hair movement** — *"loose strand of hair lifting in the air conditioning"*
- **Steam rising** — *"steam curling upward from the bowl"*
- **Light flickering** — *"flickering neon sign casting unstable magenta across the wall"*
- **Liquid motion** — *"surface of the coffee rippling slightly"*
- **Smoke trailing** — *"cigarette smoke trailing upward in slow lazy curls"*
- **Visible breath in cold air** — *"each exhale visible as a soft white cloud"*
- **Condensation** — *"droplets forming on the glass and slowly sliding down"*

### Worked example (the ramen shop again, now with micro-motions called out)

> *Static tripod camera in narrow neon-lit ramen shop, **condensation fogs the window**, couple sits side by side under **flickering magenta sign**, **steam rising from bowls** as they eat noodles in slow synchronized rhythm, **broth splattering gently**, their faces softly illuminated by red neon glow.*

The bolded items are all micro-motions. Without them, the camera is static AND the scene is static — dead. With them, the camera is static but the scene breathes.

**Rule:** if the camera is static, the world must move. If the world is calm, the camera must move. Never both still at the same time.

---

## Part 11.17 — SFX Notation (explicit sound effects)

Beyond ambient audio and dialogue, Kling 3.0 supports an explicit `SFX:` notation for specific sound effects. Use this when you need a particular sound to land at a specific moment.

### The format
```
SFX: [precise sound description, optionally with timing and intensity]
```

### Examples
- `SFX: A massive power-up sound effect like a turbine spinning at max speed that cuts the silence of the final frame`
- `SFX: Paper scraping sound`
- `SFX: Glass shattering`
- `SFX: Heavy footsteps echoing in the empty hall`
- `SFX: Thunder rumbling in distance`
- `SFX: Engine revving as the tachometer climbs`
- `SFX: Sudden loud crash followed by silence`
- `SFX: Soft spray sound, elegant background music`

### When to use SFX vs physics-description
- **Physics-description** (Part 11.12) for *implied* foley that comes naturally from the scene — footsteps on concrete, fabric flapping, etc. Just describe the surface and motion.
- **SFX:** for *specific* sounds that the scene wouldn't generate on its own — a power-up, a thunderclap, a designed sound design moment, a stinger.

You can layer them: physics description for the bed, `SFX:` for the punctuation.

---

## Part 11.18 — Combined & Complex Camera Moves

Kling 3.0 handles sophisticated camera choreography when you describe it precisely. Atlabs's most advanced finding: you can chain multiple camera moves in a single shot using sequence words.

### Example: robotic arm camera control

> *Camera performs a fast lateral pass left to right (0.5–0.8 seconds), then a brief crash push into the face. Quick pull back and a fast pass back right to left. No circular motion around the object. Robotic arm camera control. Very snappy accelerations, but no shake. Stable face. Braids intact. Outfit artifact free.*

Notice the layered specifications:
- Multiple sequenced moves in one shot
- Exact timings (0.5–0.8 seconds)
- Speed character ("snappy accelerations")
- Constraint exclusions ("no shake," "no circular motion")
- Continuity locks ("stable face," "braids intact," "outfit artifact free")

### Advanced camera vocabulary (to combine)
- **Combined dolly + zoom:** "vertigo effect" / "Hitchcock zoom" — dolly out while zooming in (or vice versa), holds subject size while warping background
- **Tracking + slight orbit:** dynamic movement around a moving subject
- **Rise + pan:** vertical movement while panning horizontally — reveals expansive landscapes
- **Forward + tilt up:** moves into subject while looking up — hero reveal
- **Speed ramp** within a move: *"slow dolly-in that accelerates into a crash push"*
- **Rack focus + camera move:** *"rack focus from foreground to background as the camera pulls back"*

### Speed-of-camera vocabulary
- **Slow:** *gentle, measured, deliberate, gradual*
- **Medium:** *steady, smooth, even*
- **Fast:** *snap, whip, crash, rapid, snappy*

### FPV drone shot template (for high-octane action)
> *Dynamic FPV drone shot chasing [subject] through [environment]. The camera **whips and rolls 360 degrees** as it follows. [Subject] [intense action]. High contrast, motion blur on the background, [subject] remains in sharp focus.*

---

## Part 11.19 — Performance Direction & Character Gestures

Kling 3.0 understands acting direction and body language vocabulary. Use specific gesture verbs instead of generic descriptors for the model to execute the performance you want.

### Gesture vocabulary that works
- *"Shakes head in disbelief"*
- *"Arms open as if pleading a case in court"*
- *"Walks close to the camera and delivers a loaded question"*
- *"Leans forward slowly"*
- *"Shifts in chair, tense"*
- *"Lowers his head"*
- *"Eyes wide with [emotion]"*
- *"Grips the steering wheel nervously"*
- *"Crosses arms defensively"*
- *"Runs a hand through her hair"*
- *"Exhales shakily"*
- *"Nods slowly, eyes glistening"*

### Emotional escalation pattern
For dramatic scenes, escalate the body language across beats:

> *The man appears to get more and more agitated as if what he has just been told is nonsense. He shakes his head and then protests with arms open as if pleading a case in court. He walks close to the camera and then delivers a loaded question in a gravelly voice.*

Three escalating gestures (shake → plead → walk-in) plus a vocal turn at the end. Much more reliable than *"he gets angrier."*

### Acting and emotion modifiers for dialogue
Stack these in the dialogue tag for more specific delivery:

`[Character A: Old Friend, warm nostalgic voice, voice trembling slightly]: "It's been... what, ten years?"`

Examples:
- *softly speaking* / *whispering* / *barely audible*
- *voice cracking* / *voice trembling* / *catching in the throat*
- *fast urgent* / *measured deliberate* / *slow contemplative*
- *raspy deep* / *clear high* / *hoarse* / *gravelly*
- *defensive* / *pleading* / *commanding* / *resigned*
- *exhausted* / *breathless* / *recovering composure*

---

## Part 11.20 — Genre-Specific Tips (cheat codes per video type)

Different video formats reward different prompt structures. Atlabs distilled these from real testing.

### Social media (TikTok / Reels / Shorts)
- **Punchy first 2 seconds.** The hook beat must land in the opening moments. Front-load the visual spike.
- **Vertical 9:16.** Generate native, never crop from 16:9.
- **Trending audio styles in the prompt.** Reference VHS, lo-fi, slo-mo aesthetics that match current platform vibes.
- **Text overlays.** Mention them in the prompt — Kling preserves on-frame text well.
- **5–10 seconds.** Don't waste the 15s budget on social — shorter clips iterate faster.

### Advertising / commercial
- **Product clearly framed in the first frame.** Either provide it as Start Frame, or describe it explicitly in Shot 1.
- **Beauty lighting + slow elegant camera moves.** Soft golden hour, slow dolly, rack focus.
- **CTA in the dialogue.** *"Link in my bio"*, *"Order now"*, *"Visit our store"* — write it as a character line.
- **Consistent brand aesthetic.** Lock the Style Bible to your brand and never deviate.
- **Hold the logo at readable size** with the *"stable and readable throughout the motion"* phrase.

### Narrative / storytelling
- **Build emotional arcs** across the 15 seconds — initiation, escalation, resolution.
- **Vary shot sizes** for visual interest: wide → medium → close-up → reaction.
- **Music and sound bed** to enhance mood — describe it as a progression, not a static label.
- **Character moments, not just action.** Reaction shots are often more powerful than the action itself.

### Music videos
- **Sync camera moves to beat and rhythm** — describe the camera moving on a tempo.
- **Dramatic lighting changes** — strobing, color shifts, blackouts.
- **Mix performance shots with artistic b-roll** — multi-shot is built for this.
- **Lyric-synchronized visuals** — write specific imagery for specific lyric moments.

### Horror / thriller
- **POV shots through darkness with searching flashlight beams**
- **Quick cuts to shadows or off-screen impacts**
- **Extreme close-ups on dilating pupils, cold breath, trembling hands**
- **Sound design via SFX:** *"ominous low frequency drone, sudden loud crash, heavy breathing"*
- **Voice trembling, whispering** for dialogue tone

---

## Part 11.21 — The "Earn Your Duration" Discipline

A unifying principle from multiple sources: **Kling's 15-second tier rewards arcs, not extended single moments.** A 15-second static description wastes the budget — you get a frozen moment that just runs longer.

### The arc requirement
Every 10s+ generation should have a beginning, middle, and end embedded in the prompt:
- **Initiation** (0–25%) — establishing beat
- **Development / escalation** (25–75%) — main action evolves
- **Resolution / payoff** (75–100%) — closing beat or emotional turn

### How to enforce the arc
Use one of these structural markers:

1. **Time codes:** `0–4s: ... / 5–9s: ... / 10–13s: ... / 14–15s: ...` (granular)
2. **Multi-shot labels:** `Shot 1: ... Shot 2: ... Shot 3:` (cleaner cuts)
3. **Sequence words inside a continuous take:** *first... then... finally...* (single-shot evolution)
4. **Camera-state changes:** *camera holds, then begins to push in, then freezes on her face* (the camera tells the arc)

### The diagnostic
Before generating, ask: **"If I cut this prompt at the halfway point, are the two halves different?"** If no — the prompt is static, you're wasting duration. Add a turn.

---

## Part 12 — Reference Templates (fill-in-the-blanks)

### Template A — Single-shot cinematic moment
```
[SCENE: location, time of day, weather, atmosphere]. [CHARACTER: full descriptor — clothing, posture, position in frame]. [ACTION as timeline: first beat, then beat, then beat]. [CAMERA: shot size + movement verb, what it does at the turn]. [AUDIO: ambient line. Then [Character, tone]: "line."]. [STYLE BIBLE].
```

### Template B — Inline multi-shot dialogue (no 6-shot limit)
```
[SCENE setup paragraph establishing location and ambient audio.]

Shot 1: [Camera + character + action]. [Character A, tone]: "line."
Shot 2: [Camera move or new angle]. [Character B, tone]: "line."
Shot 3: [Reaction shot]. [Character A, tone]: "line."
Shot 4: [Resolution beat].

[STYLE BIBLE.]
```

### Template C — Custom Multi-Shot (precise timing)
```
Shot 1 (Xs): [single beat, single camera move, optional one line of dialogue]
Shot 2 (Ys): [next beat]
Shot 3 (Zs): [payoff]
```

### Template D — Omni multi-character scene
```
Shot 1: [Camera], background @Location. @CharA does [action]. [@CharA, tone]: "line."
Shot 2: @CharB [reaction action]. [@CharB, tone]: "line."
Shot 3: Close-up @CharA. [@CharA, tone]: "line."
[STYLE BIBLE.]
```

### Template E — Image-to-video product/brand
```
[Reference the first frame as anchor — do not re-describe what's visible.] The camera [movement verb] toward/around [subject]. [On-screen text or logo] remains crisp and readable throughout the motion. [Ambient audio]. [Voiceover, tone]: "line." [STYLE BIBLE.]
```

### Template F — 15-second long take with internal beats
```
[SCENE setup.]

0–4s: [opening beat, establishing camera + subject motion]
5–9s: [middle development, camera reacts to subject]
10–13s: [emotional turn, framing change]
14–15s: [closing beat]

[Ambient audio across the whole. STYLE BIBLE.]
```

### Template G — Ad Beat Map (4–6 scenes for commercial work)
```
Master Intent: [One sentence — what this video is, tone, genre, what the viewer should feel.]

Scene 1 — HOOK (3–5s): [Camera angle + subject + setting]. [Visual spike that stops the scroll].
Scene 2 — STAKES (5s): [New angle]. [Tension or context reveal]. [Specific motion + intensity].
Scene 3 — TURN (5–10s): [Peak action or product reveal]. [Subject position + motion direction]. [Physics description that generates audio].
Scene 4 — PAYOFF (5s): [Resolution beat]. [Product clarity, on-frame text crisp].
Scene 5 — EXIT (2–3s): [Clean end frame for CTA / brand lockup].

[Negative line if needed. STYLE BIBLE.]
```

### Template H — POV Style Transfer (7-shot architecture)
```
Shot 1 (third-person establish): [Medium/wide] shot of [character] in [scene]. [Color palette]. [Emotional action].
Shot 2 (third-person close): Close-up of [character]. [Emotion detail]. Background shows [motion/speed].
Shot 3 (enter POV): First-person POV from [position]. [Main visual]. [Environment detail].
Shot 4 (POV — World A): POV shot as [element] transforms into [World A — style + materials + atmosphere].
Shot 5 (POV — World B): POV shot through [World B — signature visuals]. Motion is [tempo].
Shot 6 (POV — World C): POV shot as [movement] emerges into [World C — hyper-real place + lighting].
Shot 7 (medium break): Transition into [new medium/style]. [Character now rendered in new style]. [Peak emotion + background].
```

### Template I — Glif 6-Element single-sentence prompt (compact, no shots)
```
[Camera type and movement] in [environment with one specific atmospheric detail], [subject doing action with motion intensity], [light source naming the actual fixture], [tactile texture detail × 2–3], [emotional/lens descriptor — depth, bokeh, mood].
```
Example fill:
> *Slow handheld dolly through a dim Senegalese kitchen at dusk, an older woman stirring a pot of thieboudienne with steam rising in soft swirls, warm tungsten bulb overhead casting amber light on her hands, oil glistening on the rice, fabric of her boubou catching the light, shallow depth with golden bokeh — intimate, nostalgic, alive.*

### Template J — Time-Coded Single Shot (granular pacing inside one take)
```
[SCENE setup with ambient audio.]

First sequence (0–[X]s): [opening beat, often slow or static, wide framing].
Second sequence ([X]–[Y]s): [main action, motion verbs, camera reaction].
Third sequence ([Y]–[Z]s): [resolution, close-up or pull back, emotional payoff].

[Speed ramp from X% to Y% as trigger action, if needed.]
[STYLE BIBLE.]
```

### Template K — Physics-Anchored Single Shot (the artifact-resistant default)
For any shot featuring walking, hand movements, or on-screen text — use this template to bake in the anti-artifact tricks from Part 11.14.

```
[SCENE: location, time, lighting, ambient audio]. 
[CHARACTER: full descriptor]. 
[Walking biomechanics: "each step lands heel-first, rolling forward with visible weight transfer"] OR [Hands anchored: "fingers gripping/resting on/wrapped around <object>"]. 
[Camera: shot size + motion verb + speed]. 
[Micro-motions × 2–3: condensation, steam, fabric sway, blinking, breath].
[Texture details: film grain, skin pores, fabric creases].
[If on-screen text: "ensuring the text '<TEXT>' remains stable and readable throughout the motion"].

[STYLE BIBLE.]
Negative: smiling, plastic skin, sliding feet, floating limbs, text morphing, face distortion.
```

---

## Part 13 — Working Together: How I'll Build Prompts For You

When you give me a script or an idea, my process is:

1. **Identify the form** — single shot, inline multi-shot, Custom Multi-Shot, Omni, Ad Beat Map, POV Style Transfer, Time-Coded Sequence, or Physics-Anchored. (Default: inline multi-shot for dialogue, Ad Beat Map for any commercial brief, POV architecture if you want to push through styles.)
2. **Run the Leonardo 4-element diagnostic** — does the idea give me a Subject, Action, Context, and Style? If any one is missing, I'll fill it in or ask.
3. **Run the duration diagnostic** — if I cut the prompt at the halfway point, are the two halves different? If not, I add a turn before sending.
4. **Lock character names** — one descriptor per character, used verbatim everywhere. No pronouns.
5. **Sequence the beats** — translate the idea into a timeline of 1–6 shots (or time-coded blocks), each with one job, one camera move, one action.
6. **Lead with the camera, motivate the move** — every camera instruction has a narrative reason (pan-to-reveal, hero tilt-up, god's-eye crane).
7. **Specify motion intensity** — drop a 0.1–1.0 value (or its word equivalent) into the action sentence.
8. **Add micro-motions** — if the camera is static, the world must move. Always include 2–3 micro-motions for scenes that risk feeling frozen.
9. **Anchor the physics** — for walking shots, "heel-first, weight transfer." For hands, anchor to an object. For on-screen text, "stable and readable throughout the motion."
10. **Anchor every line of dialogue** — physical action immediately before each piece of dialogue, then `[Name, tone, optional language]: "line."`
11. **Generate audio through physics** — describe surfaces, materials, fabric, footing — never write "add sound." Use `SFX:` for designed sound moments.
12. **Add the Style Bible** — your project's locked style sentence. (Ridley Scott prestige for the Jerusalem/Bitcoin prophecy piece; West African daylight commercial for Teranga Eats — both already drafted in Part 8.)
13. **Add a negative line** — at minimum the "anti-default": *"Negative: smiling, plastic skin, sliding feet, text morphing, face distortion"* — plus any specific artifact you've been seeing.
14. **Specify what to bind** — flag which characters need Subject Binding (3 reference images) or Omni Elements with `@`.
15. **Tell you the UI settings** — recommend resolution, duration, aspect ratio, and audio toggle for the use case so there's no second-guessing in the interface.
16. **Deliver in two versions** — a full structured prompt and a tightened fallback, so you can A/B if the first generation drifts.

Tell me the script or the idea and I'll run it through this pipeline.

---

## Quick-Reference Cheat Card

**Structure**
- **Order:** Scene → Characters → Action → Camera → Audio → Style
- **Foundation (Leonardo 4):** Subject + Action + Context + Style — never ship a prompt missing any of these
- **Compact alt (Glif 6):** Camera + Subject + Environment + Lighting + Texture + Emotion in one flowing sentence
- **Klingaio formula:** [Camera Movement] + [Subject & Action Physics] + [Environment/Lighting] + [Texture & Details] + [Audio/Emotion]

**Motion**
- **Lead with the camera, motivate the move** (pan-to-reveal, hero tilt-up, god's-eye crane)
- **Dolly ≠ zoom** — default to dolly; zoom is stylized
- **Motion intensity scale:** 0.1–0.3 subtle · 0.4–0.6 natural · 0.7–1.0 dynamic
- **Walking:** *"heel-first, rolling forward with visible weight transfer"* — fixes sliding feet
- **Hands:** anchor to an object, never let them move freely in empty space
- **Texture sells credibility:** grain, condensation, fabric, breath in cold air, skin pores

**Camera**
- **Combine moves:** *"lateral pass left to right (0.5–0.8s), then crash push, then pull back"*
- **Speed ramps:** *"Speed ramp from 40% to 100% as the action intensifies"*
- **FPV drone with rolls:** *"The camera whips and rolls 360 degrees as it follows"*
- **Constraint exclusions:** *"no shake, no circular motion, stable face, outfit artifact free"*

**Dialogue**
- **Format:** `[Character A: Name + descriptor, tone + emotion, optional language]: "line."`
- **Always anchor a line with a physical action right before it**
- **Linking words between lines:** immediately, then, pause, suddenly, after a beat
- **Stack tone modifiers:** *"warm nostalgic voice, voice trembling slightly"*

**Audio**
- **Generate through physics** — surfaces + materials + motion, never "add sound"
- **`SFX:` notation** for explicit sound design moments (power-ups, crashes, stingers)
- **Score by progression** — *"music tightens with a rising pulse"*, not *"tense music"*

**Multi-shot & duration**
- **Inline `Shot 1:`** for storytelling (no 6-cap), **Custom Multi-Shot UI** for precise timing (max 6)
- **Time-coded sequences** (`First sequence (0–1s):...`) for granular pacing inside one take
- **Earn your duration** — 15s clips need an arc (init → escalate → resolve)
- **Halfway-point diagnostic:** if the two halves of your prompt aren't different, add a turn
- **Regenerate the weakest scene only**, never the whole sequence
- **If camera is static, world must move** — add 2–3 micro-motions (breathing, steam, fabric sway, drifting dust)

**Consistency**
- **Subject Binding** (1 video, 3 ref images) or **Omni Elements with `@Name`** (across videos)
- **Lock character in shots 1–2** before any style change
- **POV is the consistency hack** for aggressive style jumps — viewer becomes the character, model only renders the world
- **Text on objects:** *"remains stable and readable throughout the motion"*

**Negative defaults**
- **Anti-AI-default:** *"Negative: smiling, cartoonish, 3D render, smooth plastic skin, perfect teeth"*
- **Anti-artifact:** *"Negative: motion blur, face distortion, warping, morphing, floating objects, sliding feet, text morphing, extra limbs, background shifting"*

**Official UI specs**
- **Prompt limit:** 2,500 characters
- **Duration:** 3–15 seconds (slider)
- **Resolutions:** Standard 720p (~13 cr/s) · Professional 1080p (~17 cr/s)
- **Aspect ratios:** 16:9 · 9:16 · 1:1 · 4:5
- **Start/End Frame:** JPG/PNG, 10MB max, Start required before End unlocks
- **Languages:** EN · ZH · JA · KO · ES (others auto-translate to English)

**Iteration discipline**
- **Change ONE variable at a time** — never two — so you know which change worked
- **Draft in Standard 720p at 5s**, finalize in Professional 1080p at full duration
- **Decide platform first**, then aspect ratio, then generate

**Always**
- **Lock the Style Bible per project and never change it**
- **Image-to-video:** describe evolution, not the image itself; explicitly preserve any on-image text
- **Default to physics description over sound instructions**
- **Default to dolly over zoom**
- **Default to specific descriptors over pronouns**
