---
name: seedance-prompting-guide
description: Use whenever writing or reviewing a prompt for ByteDance Seedance (any version — 1.5 Pro, 2.0, 2.0 Fast, and future releases) — image-to-video or text-to-video generation via kie.ai, WaveSpeed, or fal.ai. Triggers on "write a Seedance prompt", "generate a video with Seedance", "how do I prompt Seedance for dialogue/audio/camera movement", "Seedance negative prompt", or any video-generation task using a Seedance model. Covers native audio control (dialogue vs. ambient/foley-only), camera movement/cinematic shot language, and negative-prompt conventions. This is the living reference — update it in place as new Seedance versions ship, never fork a separate per-version file.
---

# Seedance Prompting Guide (All Versions)

ByteDance Seedance generates video and — since 1.5 Pro — synchronized native audio in the same pass. This guide is the single reference for prompting any Seedance version correctly. Update this file in place when a new version ships; do not create version-specific duplicate skills.

## Used by

Pipelines that generate video through Seedance should link back to this file rather than re-deriving capability knowledge locally:

- [Reimagined_Realms_POV_Shorts_Pipeline_v2](../Reimagined_Realms_POV_Shorts_Pipeline_v2/SKILL.md) — Seedance 2.0 via kie.ai, character-sheet + environment-sheet reference conditioning (active POC)
- [Reimagined_Realms_POV_Shorts_Pipeline](../Reimagined_Realms_POV_Shorts_Pipeline/SKILL.md) — v1, Seedance 1.5 Pro via WaveSpeed, single per-shot image (production-proven baseline)

## Core philosophy

Seedance wants **cinematic direction, not image-generation keywords**. Write the prompt like a shot list handed to a director of photography, not a mood-board caption. The model responds to narrative structure across four layers, in this order:

1. **Subject definition** — who/what, framing, setting
2. **Action / key sound events** — what happens, what makes sound (dialogue if any, footsteps, specific foley events)
3. **Environmental audio cues** — the ambient bed (wind, birds, crowd murmur, distant traffic)
4. **Visual style / camera / lighting** — grade, lens feel, camera movement

Source: [Seedance 2.0 Prompting Guide (fal.ai)](https://fal.ai/learn/tools/seedance-2-0-prompting-guide), [How to Use Seedance 2.0 Like a Pro (fal.ai)](https://fal.ai/learn/tools/how-to-use-seedance-2-0)

## Which production style is this?

Confirm this before picking a reference-image strategy or writing the prompt — it changes which sections below actually apply.

| Style | What it is | Where the guidance lives |
|---|---|---|
| **1. POV / First-person** | One character, camera IS the character, no dialogue | "Style 1: POV" section below (this file) — our current locked convention |
| **2. Cinematic Narrative / Multi-character** | Third-person, multiple named characters interacting, may speak (two-shots, OTS, wide coverage) | [`Cinematic-Narrative-Multi-Character.md`](./Cinematic-Narrative-Multi-Character.md) in this folder — not used by any pipeline yet |
| **3. Documentary / Narration-driven** | Third-person, characters never speak, a narrator describes the action; includes pure B-roll/timelapse with no characters at all | "Style 3: Documentary" section below — everything else needed is in Core sections |
| **4. UGC / Talking presenter** | One character facing camera, talking via pre-generated voiceover + lip-sync, often holding a product | "Style 4: UGC / Talking Presenter" section below |
| **5. Portal / Transition / Effect-driven** | Real filmed footage stays unchanged; AI replaces one specific element (e.g. what's behind a door) | "Style 5: Portal / Transition Effects" section below |

Everything in the sections between here and "Style 1" (Audio control, Camera movement, Hand/limb laterality, Character consistency, Chaining multiple generations, Version-specific parameters) is Core — it applies no matter which style you picked above.

## Audio control

Seedance's audio generation is driven entirely by prompt content plus one boolean parameter — there is no separate "audio prompt" field.

### The `generate_audio` parameter

- Boolean, defaults to `true` on 1.5 Pro (confirmed live via `wavespeed schema bytedance/seedance-v1.5-pro/image-to-video`).
- Set explicitly per call — never assume the platform default matches what you want.
- When `false`, no audio track is generated at all (silent output) — useful if the pipeline plans to add all audio in post (e.g. a dedicated Foley/music pipeline stage) instead of relying on native generation.

### Dialogue — triggered by quotation marks

**Putting a spoken line in double quotes inside the prompt is the trigger for lip-synced dialogue.** Example:

> A barista leans over the counter and says, "Your usual, right?" with a warm smile.

The model lip-syncs the quoted line to the character's mouth. This works for both 1.5 and 2.0.

**To avoid dialogue entirely: never include quoted spoken lines in the prompt.** There is no separate toggle to "turn off" the lip-sync mechanism other than simply not writing quoted speech — the presence of quotes IS the mechanism.

Source: [Seedance 1.5 Prompt Guide (fal.ai)](https://fal.ai/learn/devs/seedance-1-5-prompt-guide)

### Ambient / foley-only sound (no dialogue)

Treat the prompt like **a sound brief**, not a vague mood description — name the specific sounds you want in the mix as concrete nouns/events (footsteps on packed dirt, water sloshing, distant birds, crowd murmur), not abstract adjectives (avoid "atmospheric sound"). An open-ended prompt tends to default toward whatever was most common in training data (often music-forward, "ad-like" scoring) rather than a clean ambient/foley mix.

### Negative prompts — explicitly excluding unwanted audio/visual elements

Seedance defaults toward elements common in its training distribution unless told otherwise — background music, on-screen captions, logos/watermarks, and even incidental extra people/objects can "sneak in" even when not requested, because the model has seen so many clips containing them.

**Convention:** a single closing line, beginning with a dash, listing every forbidden element by name. Their own universal example (documented as "the universal nine word closer"):

> `- No music, No logo, no text on screen.`

Adapt per-project. For a no-dialogue, foley-only, no-baked-music POV Short (our own convention — see "Our locked convention" below):

> `- No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text.`

Source: [Seedance 2.0 Negative Prompts Guide (videoai.me)](https://videoai.me/blog/seedance-2-0-negative-prompts)

**Constraints can also be woven inline, not just in the closing line.** Real production prompts often state continuity/anti-hallucination rules directly where the relevant character or action is introduced — e.g. "Hands anatomically correct, no extra fingers, no warping," "Positions never swap" stated right inside that character's description — in addition to a closing negative-prompt line, not instead of it. Use both together for anything that needs to hold firm across a whole generation. (Source: kie.ai Seedance 2.0 production prompt, `Universal_Case_Studies/002_Seedance_2.0_GPT_Image_2_Character_Environment_Consistency/Keyframes/019.jpg`; Claude-written video-to-video prompt, `Universal_Case_Studies/008_How_I_Got_11M_Views_30K_Subscribers/Keyframes/013.jpg`)

## Camera movement / cinematic shot language

- Describe **how** the camera moves, not just what's in frame — this is the single biggest gap between amateur-looking and cinematic-looking output.
- Universal template: **Subject + Camera movement + Modifier + Lighting + Style**
- Modifiers like "smooth," "aggressive," or "handheld" set the emotional register of the movement (calm/controlled vs. urgent/chaotic).
- **Never stack more than 2-3 camera instructions in one prompt** — more than that and the model's motion output degrades/conflicts.
- `camera_fixed` boolean parameter (1.5 Pro, confirmed via WaveSpeed schema) locks the camera to a static position — set `true` for POV static shots (e.g. sitting, eating, watching), `false` (default) when you want camera motion (walking POV, tracking shots).

Example (from fal.ai's own guide):

> A flamenco dancer in a deep red dress drops into a low spin on a worn wooden stage, the skirt flaring wide before she snaps upright and stamps twice, dust lifting in the single hard spotlight above her. Shot from a low front angle on a long lens, the background falling into black, a warm amber grade with hard-edged shadows.

Source: [Seedance 2.0 Prompting Guide (fal.ai)](https://fal.ai/learn/tools/seedance-2-0-prompting-guide)

## Hand/limb laterality in POV and multi-character shots (applies beyond Seedance — any first-person image or video model, including GPT-Image-2)

**The problem:** in any shot with two people's hands interacting (handshake, object hand-off, a hand placed on the POV character), image/video models frequently get left/right hand wrong relative to which arm it's attached to, and get the pairing wrong (e.g. a left hand shaking a right hand, which isn't how people actually shake hands). Confirmed failure on Reimagined Realms 0005 (Roman Gladiator), Scene 6: prompt said only "Brutus grips the POV character's forearm in a handshake," with no hand specified on either side — the model rendered the POV character's own left arm ending in a hand with a right hand's thumb orientation (the wrist twist didn't match the arm it was on), and paired it with Brutus's hand in a left-to-right grip, which people don't naturally do (handshakes are same-side: right-to-right, or left-to-left if both are left-handed).

**Root cause, per actual research (not guessed):** community-documented and cross-platform — this is a known training-data-level limitation of image/video models, not a one-off bug specific to any single tool ([OpenAI Developer Community thread](https://community.openai.com/t/image-gneration-is-great-but-struggles-with-left-right-direction/1245598)). Two findings from that thread matter directly for how we prompt:
1. **Screen/camera-relative directional language is unreliable** ("screen right," "camera left," "our right") — models don't reliably hold a character's own left/right constant against a shifting viewer perspective.
2. **What works better: anchor the description to the character's own anatomy**, not the screen — state which shoulder/side an arm originates from and which of the character's own hands is doing the action, e.g. *"his right hand, attached to his right arm and shoulder, extends forward"* rather than *"a hand reaches from the left of frame."*
3. **Reference images can make this worse, not better** — multiple users in that thread reported that attaching pose/style reference images (even when the instruction says "use this only for styling") increased left/right reversal errors. This is directly relevant to our sheet-driven pipeline, since every shot attaches multiple reference sheets — do not assume more reference material automatically fixes hand laterality; it can do the opposite.

**How to prompt any scene with hand-to-hand or hand-to-object contact between two characters:**
1. **Always name which hand** on each side of the contact — never leave it to the model to pick (e.g. "POV character's right hand" / "Brutus's right hand," not just "grips the POV character's forearm").
2. **State the pairing explicitly when it's a shared gesture** — for a handshake specifically, say "both use their right hands" (or left, if that's the deliberate staging) rather than assuming the model will default to the natural same-side pairing.
3. **Anchor each hand to its own arm/shoulder in the text**, especially for the POV character's own limb reaching into frame, since that's the hand most likely to get its laterality flipped relative to the arm it's attached to.
4. **Do not rely on reference sheets to self-correct this** — laterality needs to be solved in the prompt text itself, independent of whatever reference images are attached.
5. This is a genuine, distinct scene-writing checklist item — see `Reimagined_Realms_POV_Shorts_Pipeline_v2/POV_Style_Guide.md`'s "Hand/limb laterality check."

**This guidance applies to prompting the STARTING IMAGE — not to the video-generation prompt once that image exists.** When a scene already has a corrected `first_frame_url` (a storyboard panel/scene image where laterality was already solved at the image-generation stage), the video prompt should NOT re-describe which hand is doing what — image-to-video prompting research is consistent on this: the model already has the pose/identity/hand-position from the reference frame, and prompt tokens should go toward what changes over time (motion, camera movement, sound), not toward re-stating static visual details already visible in the frame. Re-describing them risks diluting the motion instruction or, worse, describing something that doesn't exactly match what the frame already shows, which reads as a conflicting instruction rather than reinforcement. **Rule of thumb: solve laterality once, at the image stage; describe motion, camera, and sound at the video stage.**

Sources: [OpenAI Developer Community — image generation struggles with left/right direction](https://community.openai.com/t/image-gneration-is-great-but-struggles-with-left-right-direction/1245598), [Seedance 2.0 Reference Guide — image/video/audio tagging patterns (magichour.ai)](https://magichour.ai/blog/seedance-20-reference-guide), [How to Use Seedance 2.0 — reference images without drift (magichour.ai)](https://magichour.ai/blog/how-to-use-seedance-20)

## Character consistency across shots (storyboards, character sheets, reference images)

**The problem this section solves:** when a production is built from many separate Seedance generations (e.g. a 13-shot POV sequence), each call has no memory of any other call. Without an explicit anchor, the model re-imagines the character's identity (skin tone, hand/build proportions, clothing) independently each time — this is "identity drift," a known model-level limitation, not a one-off bug. Confirmed on our own production: Gemini's Video-Analyzer flagged hand/skin-tone/proportion drift in nearly every scene of Reimagined Realms 0003 (Pyramid Builder I. Deep), plus a background pyramid changing shape (Great Pyramid → step pyramid) between the opening and closing shots.

**Capability differs sharply by version — verified live, 2026-08-04:**

| Version | Reference mechanism | Verified via |
|---|---|---|
| **1.5 Pro** | Only `image` (first-frame) + `last_image` (last-frame). No dedicated multi-reference field. The only way to anchor identity across separate clips is to reuse the *same* character-sheet image as the `image` input on every call (or composite the character sheet into each shot's own first-frame image before generating). This is a workaround, not a native feature. | `wavespeed schema bytedance/seedance-v1.5-pro/image-to-video` |
| **2.0 / 2.0 Fast / 2.0 Turbo** | Has a genuine, separate multi-reference input: `reference_image_urls` (up to 9 images, for style/subject guidance) plus `reference_video_urls` (up to 3) and `reference_audio_urls` (up to 3) — distinct from `first_frame_url`/`last_frame_url`. **Correction, confirmed live 2026-08-08 against the real API (not just `--help` output): `reference_image_urls` and `first_frame_url`/`last_frame_url` are mutually exclusive on kie.ai's `bytedance_seedance_video` endpoint — the API rejects a call using both with "The reference image and the first and last frames are mutually exclusive, and only one scene can be selected."** The `--help` schema listing both flags as available options does NOT mean they're combinable in one call; this was wrongly assumed on 2026-08-06 and never tested end-to-end until a real production run hit it. Pick one: `first_frame_url` when a specific starting composition already exists (the normal case once an image-generation stage has produced it — see Reimagined_Realms_POV_Shorts_Pipeline_v2/SKILL.md); `reference_image_urls` only for shots with no first-frame image, where style/subject guidance is all you have. **Note:** WaveSpeed's `seedance-2.0/image-to-video-turbo` schema only exposes `image`/`last_image` (no reference array) — the multi-reference field is confirmed live on **kie.ai's** `bytedance_seedance_video` endpoint, so route character-consistency work through kie.ai, not WaveSpeed, for 2.0. | `kie-cli bytedance_seedance_video --help`, and a real submitted task on 2026-08-08 for the mutual-exclusivity finding |
| **2.5** | **Confirmed live and in active hands-on use, per two independent tutorials (2026-08) — the earlier "not yet available, marketing-only" caveat below is now outdated.** Supports up to 30-second generations (vs. 2.0's shorter cap) and up to 50 references in a single pass — sometimes marketed as "Omni reference" mode on third-party platforms (e.g. Dreamina). Reference images should be named descriptively and tagged by that exact name in the prompt (see "Multi-character scenes" below). **Still verify exact parameter names/ranges via a live kie.ai/WaveSpeed schema check before integrating** — these are tutorial-observed capabilities, not a confirmed API schema yet. Original marketing sources for context: [ByteDance Seed blog](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5), [MindStudio](https://www.mindstudio.ai/blog/seedance-2-5-50-reference-multimodal-input-consistency). | "Seedance 2.5 - How to Fix Character & Environment Consistency," `Universal_Case_Studies/003_Seedance_2.5_Character_Environment_Consistency/ANALYSIS.md`; "She Isn't Real," `Universal_Case_Studies/004_She_Isnt_Real_AI_Influencer_Pipeline/ANALYSIS.md` |

### Reference-mode choice also decides how far the camera can move

A first-frame-only setup (our default — see table above) means Seedance never sees the character from any angle but the one in that frame, so it can't invent a believable view of what it hasn't seen — no full rotations or reveals of the character's back. A multi-reference setup (several angles passed in `reference_image_urls`) gives the model enough to work with for bigger camera moves, at a small cost: identity holds slightly less tightly shot-to-shot than the locked first-frame method.

This is a non-issue for POV shots — a first-person camera never orbits itself. It matters for Cinematic Narrative-style shots, where a move might call for circling around a character. Decide reference mode by what the shot actually needs: first-frame-only by default, multi-reference specifically when the camera move requires an angle the first frame doesn't show (e.g. a spin/turn move) — not as a default "more references = better" habit. (Source: "The Secret to AI Character Sheets" case study, `Universal_Case_Studies/006_The_Secret_To_AI_Character_Sheets/ANALYSIS.md`)

### Multi-character scenes — ordinal image referencing (`@Image1`, `@Image2`)

**Confirmed live, 2026-08-06, via ByteDance's own BytePlus ModelArk docs** (`docs.byteplus.com/en/docs/ModelArk/2222480`, the Seedance 2.0/2.5 series' own prompt guide — the primary source, not a third-party guess): when multiple reference images are passed in `reference_image_urls`, the model understands ordinal tags in the prompt text itself to assign each image to a specific character or element. Syntax: `@Image1`, `@Image2` (or `@Image 1` with a space — both forms appear in ByteDance's own examples). Direct example from their docs: *"Reference @Image 2 for the pianist. Reference @Image 3 for the cello. Reference @Image 4 for the violin."* This is corroborated by multiple independent practitioner guides (magichour.ai, glbgpt.com, piapi.ai) describing the same pattern for identity ("@Image for identity, @Video for motion/camera, @Audio for rhythm/voice"). **kie.ai's own docs page for the endpoint doesn't document this syntax explicitly** — it only describes `reference_image_urls` as a plain URL list — but the prompt field is free text, so the tags work regardless of which platform relays the call; the model itself (not the aggregator) is what understands them.

**Why this matters:** if a single character sheet is the only human-identity reference passed to a multi-person shot, Seedance has nothing else to draw a second identity from and will duplicate the same face for every person in frame — confirmed as a real failure mode on Reimagined Realms 0004 (Titanic Stoker), where three background stokers in one shot all rendered with identical faces because only one character sheet existed. **Fix:** build a separate reference sheet per distinct character (e.g. `Main_Character_Sheet.png`, `Background_Worker_Sheet.png`), pass all of them in `reference_image_urls`, and explicitly assign each one in the prompt via `@Image1`/`@Image2` ordinal tags. **Not yet live-tested end-to-end in our own pipeline** — this is a documented, sourced capability, not something we've confirmed produces distinct faces in an actual Seedance 2.0 output yet. Test on an isolated shot before relying on it for a full production.

**Named-tag alternative to pure ordinal numbers, confirmed in two independent tutorials:** name reference files descriptively (e.g. `brutus.png`, `forest_man.png`, `seller.png`) and reference that same name directly in the prompt text, instead of "image one." This is the naming convention Tony already uses for character sheets — extend it to every reference passed in a multi-reference call, not just the file on disk. **Caution when passing several references in one call:** more than a couple of references the model can't clearly tell apart from each other causes real confusion — every additional reference needs to be clearly named/tagged, not just added in bulk. Fewer, well-labeled references beat more, ambiguous ones. (Source: "Seedance 2.5 - How to Fix Character & Environment Consistency," `Universal_Case_Studies/003_Seedance_2.5_Character_Environment_Consistency/ANALYSIS.md`; "Create Seamless AI Films of Any Length," `Universal_Case_Studies/007_Create_Seamless_AI_Films_Of_Any_Length/ANALYSIS.md`)

### Preventing face-bleed between two characters in one shot — a second technique alongside `@Image` tagging

Even with correct ordinal/named tagging, two characters sharing a shot can still have their identities "bleed" into each other (features swapping, faces blending). A second, complementary technique observed: mask/black out all but one face across a multi-image reference sheet before passing it in, so the model only has one clear face to lock onto per reference. Tested finding from the source: no measurable difference for single-character shots, but a real reduction in identity-swap errors specifically for multi-character shots. Worth trying alongside `@Image` tagging (not instead of it) if Titanic-Stoker-style face duplication/bleed shows up again. (Source: "The Secret to AI Character Sheets," `Universal_Case_Studies/006_The_Secret_To_AI_Character_Sheets/ANALYSIS.md`)

### One composite "cast sheet" with multiple named people — confirmed for GPT-Image-2; Seedance 2.0 side unverified, corrected 2026-08-07

**The question:** can a single reference image containing several distinct people (a "cast sheet" — e.g. Jim, Bob, and Ed on one sheet with visible name labels) be handed to the model with a prompt like "add Jim and Bob as background extras," instead of one reference image per person?

**GPT-Image-2 (image generation stage): yes, this is a real, documented technique.** If the name is baked into the image itself as visible text (e.g. "Jim" printed under his portrait), the model can read the label and associate it with that person — confirmed practitioner pattern: label the reference, then reference the person by that name in the prompt ("Kristina is sitting at her desk" — the model knows who Kristina is because it can see her name). Use this at the image-generation stage, when building a shot's specific starting frame with named background extras placed correctly.

**Seedance 2.0 (video generation stage): correction — an earlier version of this entry claimed a specific "twins bug" caused by multi-view reference sheets. That claim could not be verified and has been retracted** (checked directly against sagnikbhattacharya.com, abdullahyahya.com, seedance2pro.io, and vicsee.com — none of them state it; it came from a search-tool synthesis that wasn't checked against the source pages before being written down here, which shouldn't have happened). **What IS actually confirmed from those sources, about related-but-different scenarios:**
- `10b.ai`: multiple separate reference uploads of the *same* person from different angles get averaged by the model into a morphing effect, rather than reinforcing one clean identity.
- `vicsee.com`: two *different* characters placed in separate reference slots with similar framing/angle can get misread as "the same character being reinforced" rather than two distinct people — fix suggested is using visibly different angles/framing per character slot.
- `sagnikbhattacharya.com`: recommends uploading a single clean view as the actual reference rather than a full multi-angle sheet, without stating a specific failure mode for why.

None of this confirms or denies what happens with one *composite multi-person* sheet fed to Seedance specifically — that scenario remains genuinely untested. **Until tested, the documented-safe path for Seedance video generation is separate single-person reference images tagged by `@Image1`/`@Image2` ordinal position** (see above) — not because the composite-sheet approach is confirmed bad, but because it's unconfirmed either way and the ordinal-tagging approach IS confirmed via ByteDance's own docs.

### Character sheets — yes, build one, even for POV

Even though POV shots rarely show a face, identity drift shows up in **hands, forearms, skin tone, build, and visible props/clothing** — exactly what a POV camera does show constantly. Research-backed practice (GitHub `CHARACTER_CONSISTENCY.md` writeups, WaveSpeed/Medium guides) converges on:

1. Generate a small reference set, not one image — one hero/close-up (hands + forearms for POV), one mid-shot (torso/build), one showing any recurring props (sandals, tools, jewelry) — 2-3 stills max, same lighting/session.
2. Reuse that exact set across every shot in the sequence:
   - 1.5 Pro: pass the closest-angle reference still as `image` for each shot (limits you to one anchor per call).
   - 2.0 (via kie.ai): pass the full reference set into `reference_image_urls` on every call, while `first_frame_url` still sets that shot's specific composition/pose — this is the correct fix for our drift problem today.
3. Known failure modes even with a reference set: hair/skin-tone shift mid-sequence, costume/prop details changing between cuts, facial or hand proportions drifting subtly by the 4th-5th shot — reference images reduce drift, they don't eliminate it. Continue running Video-Analyzer's continuity-anomaly check as a QA pass after generation regardless.
4. **Keep sheets minimal — more panels isn't more consistent.** One practitioner's own multi-week retrospective across 5 real productions found that elaborate, heavily-annotated multi-panel sheets were "wasted space... just for looking pretty," not more effective for identity consistency than a minimal front/side/back + face-closeup + clothing-closeup set. This is one detailed, evidence-based account, not a cross-validated industry consensus — but it's specific and worth defaulting to: build the minimal set first, and only add a detail call-out for a garment/prop with small details prone to error. (Source: "Storyboards to Consistent Videos Using Seedance 2.0," `Universal_Case_Studies/005_Storyboards_To_Consistent_Videos_Seedance_2.0/ANALYSIS.md`)
5. **A face-only close-up as the sole starting image can trigger Seedance's content-safety filter** (likely tuned against single-face-photo-to-video, to reduce deepfake-style misuse) — a full multi-angle character sheet or a non-face starting image avoids this. Not an action item for our pipeline specifically, since GPT Image 2 already composes each shot's starting frame with full-body/environment context rather than a bare face close-up — noted here only so a blocked-generation error is recognizable if it ever happens. (Source: "How to Fix Character & Environment Consistency," `Universal_Case_Studies/002_Seedance_2.0_GPT_Image_2_Character_Environment_Consistency/ANALYSIS.md`)

### Environment/location reference sheets

Environment identity drifts across separate generations the same way character identity does — and more visually complex locations drift more (a plain room holds together across cuts better than an ornate palace or a crowded market). Our pipeline already avoids most of this by never handing Seedance an open-ended prompt: the environment sheet and character sheet get composited into one fully-realized starting frame via GPT Image 2 *before* Seedance ever runs, so Seedance is animating a locked composition, not improvising the scene itself. **This pre-composition step is the correct mitigation — keep it as standard practice.** The only new consideration: budget extra reference detail specifically for locations that are inherently complex, since even a well-built environment sheet won't fully cancel out that extra drift risk. (Source: "How to Turn Storyboards into Consistent Videos Using Seedance 2.0," `Universal_Case_Studies/005_Storyboards_To_Consistent_Videos_Seedance_2.0/ANALYSIS.md`)

### Storyboard-to-video (one multi-panel image + a character sheet, in a single generation call)

**Seedance never generates the storyboard image itself — that's an image-generation model's job (GPT Image 2, Nano Banana, or Midjourney), not Seedance's.** Seedance's role only starts once a storyboard (or any other static image) already exists; it turns static images into moving video, it doesn't draw them. Keep storyboard-construction conventions (panel count, annotation style, layout) in whichever skill governs image-generation prompting — not duplicated here. This section is specifically about feeding an already-built storyboard image into Seedance as an option worth testing, alongside the per-shot method our pipeline uses today.

**Confirmed workflow, transcribed word-for-word off a real demo** (Video-Analyzer run with full transcription against [this tutorial](https://www.youtube.com/watch?v=7qBYe_VX_lE), full ANALYSIS.md saved at `Case_Studies/004_Seedance_Storyboard_Character_Consistency_Tutorial/` under Reimagined Realms — Tony pre-screened the video before this was run). This is the actual mechanism, not a guess:

1. **Build the storyboard image**: write a story/panel-count prompt in an LLM (he used Claude — "make me a prompt for GPT Image 2, a storyboard of 5x5 panels"), then generate ONE image containing all N panels via an image model (compared Nano Banana 2 vs. GPT Image 2 side by side; preferred GPT Image 2's more realistic/contrasty look for this use).
2. **Build a character sheet** (see above) — a 3x3 grid of yourself from multiple angles/expressions, restyled into the story's costume via the same image model.
3. **Merge them**: feed the character sheet back into the image model along with the original storyboard prompt — "give me the same storyboard but with the character I've attached" — producing a single storyboard image where your likeness is baked into every panel already, before any video generation happens.
4. **Generate video from BOTH images in one call**: upload the merged storyboard image AND the character sheet image as two separate image inputs to the video model, with a prompt structured as: *"Generate a photorealistic cinematic video following the attached storyboard panel by panel, using the attached character sheet to maintain character consistency. No music, just sound effects."* Duration was set long enough to cover multiple story beats in one generation (14s for a multi-panel astronaut sequence, 12s for a simpler one) — **this produces one continuous multi-beat clip from a single call, not 13 separate ~5s clips.** For a storyboard with no personal character (e.g. a product ad), the character-sheet image and its prompt clause are simply omitted — same mechanism, one fewer input.
5. He names the video tool in the demo as "Seed-TTS 2.0" on Hugging Face — this is almost certainly a transcription/mishearing of **Seedance 2.0** (there is no ByteDance video model called Seed-TTS; TTS = text-to-speech, unrelated to what's shown on screen). Treat the tool identity as Seedance 2.0, not confirmed as literally "Seed-TTS."

**Quality still isn't perfect, and the creator says so himself:** even with the character sheet baked in, the resulting video still had minor artifacts — fingers warping/blending at one hand-object interaction, eyes rendering an unnaturally solid glow, a flashlight beam not perfectly tracking hand movement. Overall character *identity* held consistent (same face throughout, unlike our 1.5 Pro POV drift), but small-scale limb/physics artifacts persisted. **His own stated conclusion, verbatim:** storyboard-to-video is good for speed/credits and for sending a client a fast concept proof, but *"if you want to have more control and make it a little bit better... the matter of generating frame by frame or just using two or three images for one portion of the video is still, in my opinion, a bit better because you have more control over it... more time-consuming and more credits, but you will have a better output."* For a real channel production (not a proof-of-concept), this is a real trade-off to weigh, not just a shortcut win.

**Recommendation for the POV Shorts pipeline specifically:** two options worth testing against each other before committing:
- **(a)** kie.ai's `bytedance_seedance_video` (Seedance 2.0) per-shot, with a locked 2-3-image character-sheet reference set passed via `reference_image_urls` on every shot call (finer control, matches our existing 13-shot structure).
- **(b)** the storyboard+character-sheet merged-image method above, generating multi-beat clips in fewer, longer calls (faster/cheaper, but per the creator's own admission, less controllable and likely to carry its own small artifacts).
Both require kie.ai (not WaveSpeed) for the reference-image capability, and neither has been tested on our own production yet — **do not implement either into the live pipeline without Tony's go-ahead; the next step there is a versioned pipeline duplicate (v2), not an in-place edit.**

## Chaining multiple generations into one continuous scene

Seedance has a hard per-call duration cap (well under a minute even on 2.5). For anything longer, or for a multi-panel storyboard too large to cover in one call, don't force it into a single generation — chain several generations together instead.

**Technique 1 — last-frame-passing for a seamless cut:** generate clip 1, extract its literal last frame, and use that frame as the starting image for clip 2 (alongside whatever character/prop references are still needed). Because clip 2 starts on the exact pixels clip 1 ended on, the stitched result reads as one continuous shot instead of two generations awkwardly cut together. (Source: "Create Seamless AI Films of Any Length," `Universal_Case_Studies/007_Create_Seamless_AI_Films_Of_Any_Length/ANALYSIS.md`)

**Technique 2 — row/panel-cropping a storyboard:** crop one row (or a few panels) of a multi-panel storyboard at a time, animate just that crop in its own generation call with the relevant character sheet attached, and repeat per row/section. Combine with Technique 1 between each row for a seamless join. (Source: same case study above)

**Failure mode to avoid:** sending an entire multi-panel storyboard into one generation call without splitting it can cause the model to replicate the whole storyboard's content across every segment of the output instead of progressing through it panel-by-panel — confirmed independently on a second platform testing "direct" vs. "agent-split" generation modes against the same storyboard. Splitting first (Technique 2) avoids this. (Source: "Ultimate Seedance Control - Storyboards With GPT Image 2," `Universal_Case_Studies/010_Ultimate_Seedance_Control_Storyboards_GPT_Image_2/ANALYSIS.md`)

## Version-specific API parameters

**Confirm which version this build targets before writing the prompt or picking parameters — capabilities differ meaningfully between 1.5 Pro, 2.0/2.0 Fast, and 2.5. Never apply a newer version's capabilities (e.g. 2.5's 50-reference/30-second capacity) to a 1.5 or 2.0 build, or vice versa.**

**Seedance 1.5 Pro** (confirmed live via `wavespeed schema bytedance/seedance-v1.5-pro/image-to-video`, 2026-08-01):

| Field | Type | Notes |
|---|---|---|
| `prompt` | string | required |
| `image` | string | required — first-frame reference (image-to-video mode) |
| `last_image` | string | optional — last-frame reference for interpolation |
| `aspect_ratio` | enum | `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16` |
| `duration` | integer | default 5, range 4-12 (seconds) |
| `resolution` | enum | `480p`, `720p` (default), `1080p` |
| `generate_audio` | boolean | default `true` |
| `camera_fixed` | boolean | default `false` |
| `seed` | integer | `-1` = random |

**Seedance 2.0 / 2.0 Fast:** same core prompting philosophy (4-layer structure, quote-triggered dialogue, dash-led negative-prompt closer) — check the live schema (`wavespeed schema <model-id>`, or `kie-cli --help` / the platform's own docs) for exact parameter names/ranges before each new integration, since ByteDance has been shipping frequent version updates and defaults can shift. **Never hardcode assumed parameter values from this table into new code without a live schema check first** — this table is a snapshot, not a guarantee.

## Related but distinct tool: Seed Audio 1.0

ByteDance also ships **Seed Audio 1.0** (`bytedance/seed-audio-1.0` on fal.ai) — a standalone audio-only generation model, not part of Seedance video generation. It produces multi-character dialogue, sound effects, ambience, and music from a single text prompt, independent of any video. Two modes: text-to-speech (dialogue only) and text-to-audio (full cinematic mix with dialogue + sound design). Useful as a future option for post-hoc full audio-scene generation decoupled from video generation, but **not currently used in any Agent-OS pipeline** — Seedance's own `generate_audio` (synced to the video it's generating) is what we use today. Source: [How to Use Seed Audio 1.0 (fal.ai)](https://fal.ai/learn/tools/how-to-use-seed-audio), [What Is Seed Audio 1.0? (MindStudio)](https://www.mindstudio.ai/blog/what-is-seed-audio-1-0-bytedance)

## Style 1: POV / First-Person (our locked convention — Reimagined Realms POV Shorts)

For the POV Shorts pipeline (`001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/`), every Seedance prompt must:

1. Never include quoted spoken dialogue — these videos have no dialogue by design.
2. Name specific foley/ambient events concretely (footsteps, sloshing, birds, wind, crowd murmur) rather than vague mood words.
3. End with a negative-prompt closing line: `- No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text.` (the "no music" clause matters specifically for us — Suno generates the separate music layer, so Seedance's native audio should stay foley/ambient-only, not compete with its own score). This also matches a more general rule worth keeping in mind for any per-shot (not single-long-take) pipeline: audio baked into a generation can't be cleanly stripped back out later, so if shots get stitched together afterward, leave music out of the Seedance call entirely and add it once, separately, across the whole edit.
4. Use `generate_audio=true` (this pipeline uses Seedance's native audio instead of a separate Foley-model step — see `001_Architecture/Superpowers/Specs/2026-08-01-RR-POV-Shorts-Pipeline-Design.md` for the decision history).
5. Set `camera_fixed` per the shot: `true` for static POV vignettes (eating, sitting, watching), `false` for walking/handheld/tracking shots — per `POV_Style_Guide.md`'s camera conventions.

## Style 2: Cinematic Narrative / Multi-Character

Third-person storytelling with multiple named characters interacting and speaking (e.g. a commander giving orders to a lieutenant, two characters facing off before a fight). Full guidance lives in a separate file to keep this main reference lean: see [`Cinematic-Narrative-Multi-Character.md`](./Cinematic-Narrative-Multi-Character.md) in this same folder. **Not currently used by any pipeline** — `Reimagined_Realms_Video_Pipeline` has a documented placeholder for future character dialogue ("not in scope for the current voiceover-only pipeline") that this style would serve whenever that gets built.

## Style 3: Documentary / Narration-Driven

Third-person footage where characters never speak — a narrator describes what's happening over the visuals. Can include characters performing silent action, or pure environment/B-roll shots with no characters at all (including timelapses). No dedicated techniques beyond the Core sections above: character/environment sheets (if characters are present), camera language, negative-prompt conventions. The one hard rule specific to this style: never write quoted spoken dialogue into the prompt. **Current pipeline using this style:** `Reimagined_Realms_Video_Pipeline` ("voiceover-only, characters never speak").

## Style 4: UGC / Talking Presenter

One character, camera-facing, actively talking — usually while holding/promoting a product. Voice comes from a pre-generated voiceover (e.g. ElevenLabs), not Seedance voice-cloning — Seedance's job here is lip-syncing the character's mouth to that already-made audio track, not generating the voice itself. **Not currently used by any pipeline** (Neon-Parcel's TikTok Shop pipeline currently edits real footage rather than generating AI presenters), documented here for if that changes.

Practical notes from a real UGC-mode platform (Enhancor):
- A separate "Lipsyncing" input mode exists, distinct from that platform's Text-to-Video/Image-to-Video modes — feed it a video/image plus your pre-generated audio file directly, rather than trying to trigger lip-sync through quoted dialogue text the way Style 1/2 do.
- "UGC mode" (one character image, single-shot talking-product ad) and "Multi-reference mode" (full character sheet, needed for anything more cinematic — multiple angles, camera moves) are different tools on the same platform. Pick UGC mode for a quick single-shot talking ad, multi-reference mode for anything requiring more than one angle.

(Source: "She Isn't Real - Definitive AI Influencer Pipeline," `Universal_Case_Studies/004_She_Isnt_Real_AI_Influencer_Pipeline/ANALYSIS.md`)

## Style 5: Portal / Transition / Effect-Driven

Real filmed footage stays completely unchanged — same face, clothes, movement, camera framing — except one specific element gets replaced by AI (most commonly: what's revealed when a door/window/threshold opens). This is video-to-video on real source footage, not character-sheet-driven generation from scratch, so none of the character-consistency guidance above applies.

**Prompt pattern — state what stays constant before describing what changes.** Lock everything about the real footage first (face, hair, outfit, body movement identical to the source, camera completely static — no panning/zooming/shake), THEN describe the one thing that changes with its own inline negative constraints. Verbatim real example, written by Claude (Sonnet 5):

> A woman opens a door in a static, completely unchanged real-world interior scene. Her face, hair, outfit, and body movements remain exactly identical to the original footage up until the moment the door opens. The camera is completely static and locked throughout the entire shot — no panning, no zooming, no camera shake, no movement of any kind. As the door swings open, instead of revealing the original background, the doorway opens directly onto a photorealistic outdoor location: a wide green valley with a fairytale stone castle with tall Gothic spires perched on a distant hill... There are no fantasy visual effects of any kind — no glowing edges, no light flashes, no sparkles, no particle effects, no warping or distortion around the doorway. The transition must look like a completely ordinary door opening onto a real physical place, strictly photorealistic...

(Source: "How I Got 11M Views and 30K Subscribers," `Universal_Case_Studies/008_How_I_Got_11M_Views_30K_Subscribers/Keyframes/013.jpg`)

**Not currently used by any pipeline** — documented here for when a channel wants this format.
