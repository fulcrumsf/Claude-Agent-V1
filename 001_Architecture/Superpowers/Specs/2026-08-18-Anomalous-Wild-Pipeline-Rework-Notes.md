# Anomalous Wild Pipeline Rework — Planning Notes (2026-08-18)

**Status: NOT IMPLEMENTED. Do not build any of this until Tony explicitly says go.** These are his own words, jotted down at end-of-session before a restart, to pick back up from later the same day (2026-08-18).

## 1. Default video model — cost-driven

- **Default #1: Seedance 1.5 Pro, 1080p.**
- **Default #2: Seedance 2.0.**
- The pipeline should ask which model to use at the point video generation starts (Phase 6A), rather than assuming — but present these two as the defaults, in this priority order, driven by cost.
- Open tension to resolve next session: this session's real test (2026-08-18) found Seedance 1.5 Pro drifted into an unrecognizable, alien-looking creature by the final frames of an 8s clip, while Seedance 2.0 held up correctly across the whole clip. Tony's cost-based default and this session's quality finding point in opposite directions — worth discussing before locking in defaults.
- **CRITICAL CORRECTION (2026-08-18, from Tony directly):** that failed test did **NOT** use the start-frame + end-frame approach this rework actually calls for. It was run with **character sheet + storyboard** as the two reference images, and 1.5 Pro tried to morph/interpolate between those two mismatched-purpose images — which is a different (and known-wrong per this session's earlier findings) reference setup, not what section 1b describes. **This means the actual open tension in section 1 is unresolved and untested under the real intended design** — a proper test needs to be run with actual GPT-Image-2-generated start frame + end frame (grounded by the character sheet + storyboard, per 1b) before any real conclusion can be drawn about whether 1.5 Pro still drifts under the correct reference setup.

## 1b. Why all image assets get built regardless of which Seedance version is used (2026-08-18)

- **How Seedance 1.5 Pro achieves continuity despite having no multi-reference field:** the character/environment/prop sheets and storyboard aren't wasted on 1.5 Pro — they're used to ground **GPT-Image-2** when it generates that scene's start frame and end frame. GPT-Image-2 grounds those frames using **both the character sheet AND the scene storyboard** (not just the character sheet alone). Consistency flows through the frames themselves (which 1.5 Pro *does* accept), rather than through a direct sheet reference at the video-generation step.
- **Why build the full asset set even when defaulting to 1.5 Pro:** Tony wants every asset (character/environment/prop sheets, storyboard, start frame, end frame) generated regardless of which Seedance version ends up being used for that scene — so that if he later decides to redo a scene with Seedance 2.0 instead (or changes his mind about a scene after the fact), the reference assets already exist and don't need to be regenerated. Deliberate redundancy, not waste: images are cheap relative to video generation, and having more reusable assets on hand beats having fewer. This is a standing preference, not specific to this pipeline.

## 2. Assets always generated, regardless of model

- **Character sheet** — always. **Can be more than one per production** (see 5a below) — a documentary is not required to follow a single named individual animal across the whole video; multiple real color-morph variants of the same species are allowed if the script's narrative implies more than one individual.
- **Storyboard** — always.
- **Start frame** and **end frame** — always, generated **per split clip** (see Open Question 1, answered — e.g. C04a/C04b/C04c each get their own start+end frame pair, not one pair per whole scene).

## 3. Assets generated conditionally, only if the script analysis says they're needed

- **Prop sheet(s)**
- **Environment sheet(s)**
- **Background/secondary character sheets**
- "If needed" = determined automatically by analyzing the video script — Tony does not want to be asked or have to specify this manually. The pipeline should decide deterministically on its own.

## 4. Which references get used, per model

| Model | References passed to video generation |
|---|---|
| **Seedance 1.5 Pro** | Start frame + end frame **only**. (Per this session's confirmed finding: 1.5 Pro has no multi-reference field — a second image is a last-frame target, not a style/consistency reference. This naturally limits 1.5 Pro to start+end frame only; anything else would need to be pre-composited into those two frames at the image-generation stage.) |
| **Seedance 2.0** | Start frame + end frame + character sheet + prop sheet + environment sheet + storyboard — **whichever of these exist for that shot** (i.e., skip any conditional asset that wasn't generated because it wasn't needed). Passed via `reference_image_urls` with `@ImageN` ordinal tagging per shot, per the Seedance-Prompting-Guide skill's documented mechanism. |

## 5. New capability needed: a deterministic asset-need analyzer

- Tony wants a **research/analysis agent or skill** that reads the video script and determines, on its own, which conditional assets (prop sheets, environment sheets, background character sheets) are actually needed for a given production — without him having to say so.
- **This should be reusable across ANY video pipeline in this workspace**, not something bespoke to Anomalous Wild. Likely candidates for where it lives: a new standalone skill (parallel to Storyboard-Generation, Character-Sheet-Generation, etc.), or a capability added to an existing cross-pipeline skill — needs a design decision, not yet made.
- Framed by Tony as needing "redundancy checks" — read as: the analyzer should be reliable/checked, not a single unverified LLM pass deciding silently. Worth designing an actual verification step into this, not just a single classification call.
- ✅ **Timing ANSWERED (2026-08-18):** Analysis runs **once for the whole production** (all scenes read together, upfront) — same pattern as character sheets today. Reasoning: recurring props/environments/burrows/reefs typically span multiple scenes in a script, so a whole-production pass can dedupe (e.g. "burrow entrance" in scenes 2, 5, 9 → one sheet, reused) rather than generating redundant or visually-inconsistent duplicates per scene.
- **Important constraint on scriptwriting (Tony, 2026-08-18): write scenes with full creative freedom first, not with an eye toward asset reuse.** Do NOT constrain scene-writing by trying to make environments/props reusable — that would make scripts repetitive and less engaging. The analyzer runs *after* the script is written and only builds sheets for things that turn out to be genuinely recurring in the finished script — reuse is discovered, never engineered into the writing.

### 5a. Semantic reuse detection — not keyword matching

- The analyzer must be **semantically smart, not string-matching**. Two scenes both mentioning "burrow" does not automatically mean it's the *same* burrow — the analyzer has to judge from narrative context whether the script intends the same specific location/prop, or just another generic instance of that location type.
- Applies to species/creature realism too: for a documentary, the pipeline should NOT assume the whole video follows one single named individual animal. Nature docs commonly follow "a" pistol shrimp / "a" mantis shrimp in a general sense — the species migrates, uses different reefs/burrows, and the video may reasonably depict several different individuals across scenes, not one continuous character.
- When the script implies multiple individuals (e.g. different behaviors/scenes don't require it to be literally the same animal), the analyzer should be able to generate **multiple character sheets for the same species** — e.g. "Mantis Shrimp 1," "Mantis Shrimp 2" — rather than forcing every scene to reuse one single character sheet.
- **Documentary-realism constraint on multi-individual variants:** any such variant sheets must be grounded in **real reference photography** (e.g. real photos sourced via Google Images or similar) showing color/pattern variation and lighting conditions that actually occur in that species in real life. Never invent a fictional color morph that wouldn't exist in nature — this breaks the documentary-style premise. Real photos across different lighting conditions are an acceptable and expected source of variation between sheets.

## 5b. New capability needed: a dedicated, channel-agnostic Research skill/agent (NOT YET BUILT — confirmed via search, no existing skill covers this)

Tony's full description (2026-08-18), captured verbatim in intent, not yet designed or built:

**Trigger point:** during the intake/ideation phase, after Tony picks a subject from the presented options (e.g. "mantis shrimp" vs. "sloth" vs. "bowerbird").

**What it should do, in order:**
1. **Deep topic research** — pull together everything needed to write an accurate, engaging script about the chosen subject (this largely already happens via Perplexity research in Phase 1 intake today — the new part is everything below).
2. **Pull in real reference images** — search and download Creative Commons / public-domain images of the subject, to use as grounding references for image-asset generation (character sheets, environment sheets, etc.) — directly relevant to the "real photo reference" requirement from the multi-individual character-sheet discussion earlier this session (section 5a).
3. **Search Pexels for matching video B-roll** — API search for real video footage of the subject/environment. For each candidate: analyze it, note its duration, and log it into a database of what's already been discovered/downloaded and is available to reuse (avoid re-searching/re-downloading the same footage across productions).
4. **Log full Pexels attribution data per asset**, not just the asset itself:
   - Photographer/videographer name (`photographer` field)
   - Link to their Pexels profile (`photographer_url` field)
   - Photographer ID (`photographer_id` field)
5. **Surface attributions into final outputs — YouTube description ONLY (revised 2026-08-18, see Gaps & Conflicts item 9 below — on-screen burn-in was dropped after confirming attribution is optional under the Pexels license).** A Markdown "Attributions:" section, one bullet per Pexels asset actually used in the final cut, contributor name hyperlinked to their Pexels profile page. Exact format specified in Gaps & Conflicts item 9.

**Pexels API attribution reference — CONFIRMED from source (2026-08-18):**
- Docs: https://www.pexels.com/api/documentation/#client_libraries
- FAQ ("Do we have to include attribution?"): https://www.pexels.com/api/ — official answer: *"Please! Always credit our photographers when possible (e.g. 'Photo by John Doe on Pexels' with a link to the photo page on Pexels). If you're unable to include a full link back, please use a text link (e.g. 'Photos provided by Pexels')."* Not strictly a hard legal requirement on the free tier, but Pexels explicitly rewards consistent attribution with **higher, no-cost rate limits** (default: 200 req/hour, 20,000 req/month).
- Every photo/video API response already includes the fields needed for attribution: `photographer`, `photographer_url`, `photographer_id` (photos) and equivalent videographer fields (videos) — no extra lookup required, just needs to be captured and stored at download time, not reconstructed later.
- Official client libraries exist for Ruby, JavaScript, and .NET (not Python) — a Python integration would need to hit the REST API directly.
- Pexels also permits use of their logo (white/black versions) in-app, but not as an app icon — noted for completeness, not currently planned to be used.

**Where this documentation should live (Tony's instruction):** Tool-Manager should have this Pexels API + attribution guidance in its documentation, and it should probably exist in more than one place (e.g. also referenced from wherever the Research skill/agent itself lives) so any agent asking "how do I use Pexels / do I need attribution" gets a consistent, correct answer rather than re-discovering it each time.

**Scope constraint — same as Production-Asset-Planner:** must be channel-agnostic from the start, usable by Anomalous Wild, Reimagined Realms, Kingdom and Conquerors, Glifry, Polyoculus, and any future channel — not something bespoke to one pipeline.

**Explicitly NOT approved to build yet** — Tony wants a clear, fully-discussed picture first (see his note: "Building before we get a clear picture makes no sense to me. Let's first get a clear picture and then we will decide to build.") This section is documentation of intent only.

**Related open finding (not yet resolved):** the existing Anomalous Wild Phase 5B storyboard-variety rule mentions "b-roll frames" but only in the sense of AI-generated establishing shots for panel variety — there is currently no logic anywhere in the pipeline that decides whether a given beat should pull real stock footage (from this new Research skill's Pexels findings) instead of being AI-generated. That decision boundary is Open Question 4 below, still unanswered.

### 5c. Tony's proposed end-to-end sequence for the Research skill + "smart editor" B-roll placement (2026-08-18, captured verbatim in intent, not yet designed)

Full ordered workflow as Tony described it:

1. **Subject chosen** (e.g. sloth) from intake options.
2. **Research skill gathers facts + reference images.** Pulls together everything about the animal — anatomy, scientific facts, useful details — plus reference images/diagrams via open-source Google Images search etc. These are grounding references only (for image-asset generation later), not final assets themselves.
3. **Pexels video search + download.** Search Pexels for the subject (e.g. "sloth"), download a capped number of results — Tony's example number: **10 videos**, deliberately varied across different contributors/camera angles, reasoning: downloads are free and 10 is a low enough call count to not strain the API.
4. **Run video analysis on each downloaded clip and save the analytical data**, so the LLM has a structured understanding of what actually happens in each clip (not just the raw file) — this is intended to reuse/extend the **Video-Analyzer** skill (per-second or near-per-second screenshotting, per Tony's note at the end of this section).
5. **(Open question raised by Tony, not yet answered):** can the LLM also just directly look at a downloaded image/clip and correctly identify what it is on its own (e.g. recognize "this is a scientific diagram of a sloth" purely from looking at it), rather than requiring a separate analysis pass for everything? Worth testing rather than assuming either way.
6. **Script/voiceover is planned and written**, same as today.
7. **Beat breakdown happens**, same as today (Phase 4/5 today) — script gets broken into beats.
8. **During beat breakdown, the "smart editor" decides where B-roll fits.** While going through beats, when it identifies a stretch where the narrator is talking generally (Tony's example: "~2 seconds where the narrator is just talking about sloths in general"), it should go back to the analyzed Pexels clip library from step 4, find a matching ~2 second segment from an already-downloaded clip, and slot that in as B-roll **instead of** generating that segment with AI. This directly avoids an unnecessary AI generation cost for a moment that real footage already covers well.

**The core design goal, in Tony's words:** *"I want this to be a smart video editor."* The system should be able to judge on its own where B-roll belongs — the way a real documentary editor would — without Tony having to manually flag beat-by-beat where to insert it. Tony's proposed path to get there: feed real documentary editing examples through an **updated Video-Analyzer skill** (capturing much denser detail — e.g. a screenshot every second or near it) so the system builds real editorial judgment from examples, rather than following a hardcoded rule like "insert B-roll every N seconds."

### 5c-2. Concrete intake sequence — as Tony walked through it (2026-08-18)

1. **Pipeline asks:** "What video topic would you like to search for?" (exact framing may vary, this is the intent).
2. **Tony replies with a loose prompt**, e.g. "Give me the five potentially most viral videos about animals or strange facts." Not a specific pre-chosen subject — a request for the pipeline to propose options.
3. **Pipeline returns ~5 concrete topic options**, e.g.: "An echidna protects its body with these spikes," "Did you know a wombat has one of the strongest butts of all mammals?", etc.
4. **Tony picks one** as the story to produce.
5. **Research skill (section 5b/5c) kicks off**, gathering whatever free assets it can:
   - **Cap reference images at 20 total downloaded.** These reference images (Google Images-sourced etc.) are grounding references only — **they are never used directly in the final video**, only the Pexels videos become actual usable footage.
   - **Cap Pexels video downloads** at the number set in section 5c (10), varied contributors/angles.
   - Produces its own inventory (text file/JSON) logging every downloaded video with its attribution fields (section 5b) and analysis data (section 5c step 4) — an inventory of what's actually available for this specific production.
6. **In parallel, immediately after the topic question, the pipeline asks the video-model question:** "What video model do you want to use?" — presented as a multiple choice:
   - Seedance 1.5 Pro, 1080p **(default if nothing is chosen)**
   - Seedance 2.0 Pro, 1080p
   - Seedance 2.0, 1080p
   - Veo 3, 1080p (Tony said "V03" — read as Veo 3)
7. **From there, the rest of the existing documented pipeline phases apply** (beat table, shot list, asset generation, assembly, etc.) — Tony does not want these re-derived from scratch here; they're already covered elsewhere in this note and the live Anomalous Wild skill.

### 5d. Creature-specific vs. generic B-roll boundary — ANSWERED (2026-08-18)

Tony's reasoning, in full — this is "common sense," not a rigid binary rule:

- **The real question to ask per production is: "Is this story about ONE specific, identifiable individual animal (out of the millions of that species), or about the species/behavior in general?"** — not "does the species name match."
- **Rare case — a specific, real, documented individual** (Tony's examples: "George" a specific named zoo sloth, or "Coco the gorilla," where the story is specifically about that one real, known animal): if real Pexels footage of *that actual individual* exists and is identifiable as them, it's fair game to use — including for beats specifically about that named individual — because it genuinely is them, not a stand-in. A documentary about Coco may still cut to generic footage of gorillas in general when the narration broadens beyond Coco specifically.
- **Common case — a general species documentary** (Tony's example: the mantis shrimp video currently in production, which is about mantis shrimp / mantis shrimp eyes, NOT about one specific individual shrimp): here there is no single "the shrimp" being followed, the same way real nature documentaries don't literally follow one continuous individual unless that individual is a known, tracked, filmable subject. In this case:
  - The **character sheet's real purpose is continuity for generated footage only** — used only when a beat describes something no existing real footage covers, so that footage which *does* have to be AI-generated still looks visually consistent scene to scene.
  - It is **NOT** a rule that every single frame must depict "the same" individual shrimp. Real Pexels B-roll of the species doing the described action is a legitimate substitute for generation whenever it exists — even though it's technically a different individual animal — because that's how real nature documentaries already work, and because this isn't a story about one tracked individual.
- **The actual determination logic:** after the Research skill has downloaded and analyzed available Pexels footage (section 5c) AND the script/beats are written, the smart editor checks each beat against the analyzed footage library: **does existing real footage already cover the specific action this beat describes** (Tony's example: "a mantis shrimp digging a burrow in the sand")? If yes → use that real clip as B-roll, skip generation entirely for that beat. If no matching footage exists → generate it, using the character sheet + storyboard to keep the generated portions visually consistent with each other.
- **New hard constraint (2026-08-18): B-roll is capped at a maximum of 5 seconds of real stock footage per clip.** Beyond that, the clip should be (or return to being) AI-generated/original footage rather than leaning on stock B-roll.

### 5e. Design goal reaffirmed

This whole capability (research + download + analyze + place) is meant to produce a genuinely **smart video editor** — one that reasons about what footage already exists vs. what still needs generating, and reaches editorial judgments about B-roll placement the way a real documentary editor would, without Tony manually flagging beat-by-beat where B-roll goes. Tony's proposed training path: run real documentary editing examples through an **updated, denser Video-Analyzer** (near-per-second screenshotting) so the system develops actual editorial judgment from examples rather than a fixed rule like "insert B-roll every N seconds."

**Still not yet answered / not yet designed:** whether the LLM can reliably self-identify what a downloaded image/clip depicts without a separate analysis pass (open question raised in 5c, step 5, not yet tested), and how this whole flow reconciles with the already-existing Phase 4/5/5B structure in the Anomalous Wild skill (extract-and-share vs. leave duplicated, per the "not folding in anything yet" instruction).

### 5f. Multiple character sheets for variety + the real reason continuity/character sheets matter (2026-08-18)

- **Variation is intentional, not a bug to prevent.** Same reasoning as section 5a (multi-individual real color-morph sheets), reinforced here: Tony explicitly does NOT want the same exact individual creature reused in every single shot — real documentaries show variety (different individuals, different background creatures). The pipeline should be comfortable generating **multiple character sheets per production** when it makes sense:
  - A **main character sheet** for the primary subject.
  - **Additional variant sheets** for other individuals of the same species that appear for variety (e.g. "Mantis Shrimp Character 1," "Mantis Shrimp Character 2" — slightly different coloring, grounded in real reference photos per section 5a).
  - **Background/secondary character sheets** for other species that appear incidentally in the scene (Tony's examples: a shark, a clownfish) — same conditional "only if it recurs / needs consistency" logic as any other sheet.
  - Not meant to be excessive ("we don't have to go crazy") — this is about natural variety, not maximizing sheet count.
- **The real underlying reason character/continuity sheets matter, restated clearly by Tony:** without a reference sheet, the video generation model is free to invent anatomically wrong details — e.g. morphing in a third claw, or a tail a mantis shrimp doesn't actually have. That's the actual failure mode the sheets prevent.
- **Correction/precision on "variety" (2026-08-18) — scope matters, this is NOT a license for inconsistency within a scene:**
  - **WITHIN one scene/beat (including all its split sub-parts, e.g. `205a`)**: identity consistency IS required. If `205a` is generated using a specific mantis shrimp character sheet, every clip/split-part of `205a` must consistently look like that same individual throughout — no drift, no swapping.
  - **ACROSS different scenes/beats (e.g. `205a` vs. `205b`)**: variety is allowed. `205b` (Tony's example: a beat about the tail) does not have to depict the same individual shown in `205a` — it's fine for it to use a different character sheet (a different mantis shrimp variant), or real B-roll, or the same one — production's choice, not a fixed rule.
  - **But if `205b` does use a different character sheet, that new individual must then stay consistent throughout ALL of `205b`'s own sub-parts** — the same continuity rule just re-applied to whichever character sheet that particular scene is drawing from. Variety is a per-scene assignment, not permission for the creature to drift mid-scene.
- **Story-driven vs. documentary-style productions:** character sheets are **more critical** in story-driven videos (e.g. Reimagined Realms, where a specific character must look consistent across a narrative), and **still important but somewhat less critical** in documentary-style videos (e.g. Anomalous Wild) — because documentary footage has more natural tolerance for "another individual of the same species," as long as the anatomy stays correct.

### 5g. B-roll trimming and file handling — non-destructive, separate folder, descriptive naming (2026-08-18)

- **Download the full clip first, always.** Never trim or modify the originally downloaded Pexels file.
- **Trimming is non-destructive:** when the smart editor selects a best-matching 2–5 second segment from a downloaded clip, it trims from a **copy**, producing a **new, separate clip file** — the original full-length download is left untouched, so it can be re-trimmed differently later if needed (matches Tony's standing [[feedback_backup_before_overwrite]] rule: never overwrite, always preserve the source).
- **Trimmed segments live in their own dedicated folder** — Tony's working name: something like `B_Roll/` — kept separate from the original full-length Pexels downloads folder, per Tony's standing preference for clearly separated, purpose-specific folder scaffolding (never everything dumped in one place).
- **File naming must be descriptive, following the workspace naming convention** — never a generic name like `image.png` or `clip.mp4`. Tony's example pattern: something scene/shot-identifiable like `Scene_02A` (i.e. tie the trimmed B-roll filename back to the specific beat/clip it was selected for, the same way generated clips are already named `C04a`/`C04b` etc.).

## 6. Pexels integration (new B-roll source)

- Tony added a **Pexels API key** (pexels.com) — Creative Commons-licensed images and video, with attribution rules to review later (not detailed yet).
- Pexels reportedly has a lot of animal footage — a good source for B-roll to reduce how much has to be AI-generated per video (cost savings).
- The asset-need analyzer (section 5) should know about and be able to pull from Pexels as an option, likely for generic/establishing/B-roll shots rather than the specific narrative beats involving the named recurring creature.
- **Found during close-out: the Pexels key in `~/.env-secrets` is malformed** — currently written as `Export PEXELS API KEY=...` (capitalized `Export`, spaces instead of underscores in the variable name). This is not valid shell syntax and will not load as `PEXELS_API_KEY`. Needs a one-line fix before any Pexels work starts — flagged, not fixed, since no code changes were made this session per Tony's instruction.

## Open questions for next session

1. ✅ **ANSWERED (2026-08-18):** Start/end frame generation granularity — **per split clip**, not per whole scene. If a scene has to be split into C04a/C04b/C04c due to the 8s cap, each sub-clip (C04a, C04b, C04c...) gets its own dedicated start frame AND end frame — not one shared pair for the whole scene. Reason (Tony): prevents the creature/subject from drifting/morphing into something unintended across a long implied span — each sub-clip needs its own tight anchor at both ends.
2. ✅ **ANSWERED (2026-08-18):** Script-analysis timing — whole production, once, after the script is fully written. See section 5 and 5a for the full reasoning and the semantic-reuse / multi-individual-character nuance Tony added.
3. ✅ **ANSWERED (2026-08-18):** Lives as a **new standalone, channel-agnostic skill named `Production-Asset-Planner`**, in `001_Architecture/Skills/` — same tier as Storyboard-Generation, Character-Sheet-Generation, Environment-Sheet-Generation, Prop-Sheet-Generation. Explicitly reusable across ALL channels (Anomalous Wild, Reimagined Realms, Kingdom and Conquerors, Glifry, Polyoculus), not folded into Tool-Manager — different concern (asset/continuity planning vs. tool/cost routing).
4. ✅ **ANSWERED (2026-08-18):** Not a rigid boundary — governed by "is this story about one specific, identifiable individual, or the species in general?" See sections 5c/5d/5e for the full reasoning, the researched-footage-vs-generation decision logic, and the new hard cap: **max 5 seconds of real B-roll per clip.**
5. ✅ **ANSWERED (2026-08-18):** Provisional default = **Seedance 1.5 Pro.** Tony's reasoning: pursuing pipeline autonomy first is the priority goal; he'll live with 1.5 Pro's results across a batch of builds and revert specific scenes to Seedance 2.0 afterward, based on real observed outcomes rather than a pre-decided rule. Not a final quality verdict — a decision to proceed and observe.

## Gaps & conflicts found in review pass (2026-08-18) — Tony's answers

1. ✅ **Default-model conflict (live skill currently defaults to Seedance 2.0, this rework flips it to 1.5 Pro):** Confirmed — flip it. The live skill's Phase 6 default line needs to change from "default to Seedance 2.0" to "default to Seedance 1.5 Pro" when this gets built. Not yet applied (whole doc still NOT IMPLEMENTED).
2. ✅ **When the model question gets asked (intake vs. Phase 6A):** Confirmed — **asked at intake**, immediately after topic selection, not deferred to Phase 6A. Tony is not worried about a model/complexity mismatch; the priority is getting the pipeline autonomous first, and he'll revert specific scenes to Seedance 2.0 manually later based on real results, not pre-empt it with per-scene complexity judgment.
3. ✅ **Model list — simplified, not 4 hardcoded options:** Don't hardcode exact sub-versions/names. The real intent is two families: **Seedance (1.5 Pro or 2.0, whichever the pipeline is set to default to), 1080p** and **Veo, 1080p** — "whatever the latest reasonably-priced 1080p Veo version is" (currently Veo 3.1 Fast/Quality per the live skill's pricing table, not "Veo 3" — resolve the exact current version via Tool-Manager at build/runtime, never hardcode a version number in this doc or the skill). Drop "Seedance 2.0 Pro" as a separate listed choice unless Tool-Manager confirms it's a real distinct kie.ai SKU (unverified) — don't put an unconfirmed model in a user-facing menu.
4. ✅ **Cost math concern — dismissed, not a real issue:** Tony's position: image generation + video analysis calls are categorically cheaper than Seedance 2.0 1080p video generation, regardless of the added volume from per-clip frames / multiple character variants / denser Video-Analyzer. This is Tool-Manager's job to verify at cost-routing time, not something to pre-litigate in planning. Do not raise this concern again without Tool-Manager data in hand.
5. ✅ **Two separate analysis passes (Production-Asset-Planner's asset-need read vs. the smart editor's B-roll-placement read) — reconcile into ONE system.** Tony's explicit instruction: this is a design job for whoever builds it (me), not a question to bounce back to him. **Not yet designed** — flagged here as a firm requirement for the eventual build: one combined analysis pass over the script/beats that determines both (a) which conditional sheets are needed and (b) where B-roll vs. generation applies, rather than two independent systems reading the same material separately.
6. ✅ **Search mechanism for a specific named individual (the "George/Coco" case) — no special branching needed, this was overcomplicated in the original gap-finding pass.** The mechanism is identical either way: **research and Pexels-search whatever the chosen story's subject literally is.** If the topic is "Why do wombats have such strong butts?" → research and search Pexels for "wombats." If the topic is "Why was Coco the Gorilla so famous?" → research and search Pexels for "Coco the Gorilla" and "gorillas." The specific-individual case isn't a separate mechanism — it just falls out naturally because the topic itself already names the individual. No extra logic branch needed.
7. ✅ **Pexels search filtering:** search/filter results to **1080p resolution, 16:9 aspect ratio only** — nothing else qualifies for download.
8. **Pexels key in `~/.env-secrets` — still broken, confirmed 2026-08-18.** Tony re-copied the key value directly from the Pexels site, but the line itself is still invalid shell syntax: `Export PEXELS API KEY=...` (capital `Export`, spaces instead of underscores in the variable name). The copied *value* is fine — the surrounding declaration syntax is what's broken and needs a one-line fix to `export PEXELS_API_KEY=...` before this key will ever load into a shell session. Not yet fixed — flagged, pending Tony's go-ahead (see conversation).
9. ✅ **ANSWERED (2026-08-18):** Pexels attribution is confirmed optional (Pexels License page: *"Attribution is not required... always appreciated"*), but Tony still wants it — **description-only, no on-screen burn-in.** Supersedes section 5b step 5's original two-place plan (YouTube description + on-screen burn-in) — the on-screen burn-in is dropped entirely.
   - **Format (Tony's exact spec):** a Markdown "Attributions:" section in the YouTube description, one bullet per Pexels asset used, each contributor name hyperlinked to their Pexels profile page. Example:
     ```
     Attributions:
     - Mantis shrimp in the sand footage from [@username](https://www.pexels.com/@username) from Pexels
     - Mantis shrimp punching footage from [@username2](https://www.pexels.com/@username2) from Pexels
     ```
   - One bullet per **asset actually used** in the final cut (not every downloaded clip — only what made it into the video), using each clip's logged `photographer`/`photographer_url` fields from the Research skill's inventory (section 5b).
