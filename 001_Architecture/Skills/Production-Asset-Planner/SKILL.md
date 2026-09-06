---
name: Production-Asset-Planner
description: "Invoke once a production's shot list/beat breakdown exists, on ANY channel — reads the script and beats in one combined pass to decide (1) which conditional image assets (prop/environment/background-character sheets) are actually needed, and (2) per beat, whether real Pexels B-roll already covers it or it needs to be generated. Triggers on: a pipeline reaching its shot-list/beat-breakdown phase, 'what assets does this production need', 'where should B-roll go', 'does this scene need a sheet', or any point deciding conditional asset generation vs. reuse of existing research footage. Channel-agnostic — used by Anomalous Wild, Reimagined Realms, Kingdom and Conquerors, Glifry, Polyoculus, and any future channel. Depends on Production-Research-Agent having already run for this production. <example>User: (Anomalous Wild pipeline, Shot_List.md just written) Assistant: invokes Production-Asset-Planner to decide which sheets are needed and which beats can use existing Pexels footage instead of generation</example>"
trigger: A pipeline has a written script + beat breakdown and needs to decide conditional asset generation AND B-roll-vs-generation placement, in one combined pass
---

# Production-Asset-Planner

One combined analysis pass over a production's script/beats that answers two questions together, not as two separate systems: **which conditional image assets does this production actually need**, and **which beats can use real, already-researched footage instead of being generated at all.** Channel-agnostic — any pipeline invokes this the same way, once its shot list/beat breakdown exists.

**Prerequisite:** `Production-Research-Agent` must have already run for this production — this skill reads `Research/Pexels_Inventory.json` and `Research/Reference_Images/` from that skill's output. If they don't exist, stop and invoke Production-Research-Agent first.

**Design principle — write scenes with full creative freedom first, never for asset reuse.** The calling pipeline's scriptwriting step should never be constrained by "let's make this reusable" — that produces repetitive, less-engaging scripts. This skill runs strictly *after* the script and beats already exist, and only builds sheets / assigns B-roll for what turns out to be genuinely recurring or genuinely covered by real footage — reuse is discovered, never engineered into the writing.

---

## Step 1 — Identify recurring subjects (semantic, not keyword matching)

Read the full shot list / beat breakdown the same way a human storyboard artist would. Identify which creatures, props, and locations recur across more than one scene.

**Be semantically smart, not string-matching.** Two scenes both mentioning "burrow" does not automatically mean the same burrow — judge from narrative context whether the script intends the same specific location/prop, or just another generic instance of that location type.

**Species/creature realism:** do not assume a documentary follows one single named individual across the whole video. Nature documentaries commonly follow "a" member of a species in a general sense — the subject may migrate, use different locations, and reasonably be depicted as several different individuals across scenes. Only assume a single continuous individual when the story is specifically about one identifiable individual (see the "specific individual" case below).

**Variation is intentional, not a bug to prevent.** Comfortably plan for **multiple character sheets per production** when it makes sense:
- A main character sheet for the primary subject.
- Additional variant sheets for other individuals of the same species used for variety (e.g. "Mantis Shrimp Character 1," "Mantis Shrimp Character 2" — real color/pattern variation).
- Background/secondary character sheets for other species that recur incidentally (e.g. a shark, a clownfish).
- Not meant to be excessive — natural variety, not maximizing sheet count.

**Documentary-realism constraint on variant sheets:** any variant must be grounded in real reference photography from `Research/Reference_Images/` (or fresh search if not already covered) showing color/pattern/lighting variation that actually occurs in that species in real life. Never invent a fictional variant that wouldn't exist in nature.

**The real reason these sheets matter:** without a reference sheet, the video generation model is free to invent anatomically wrong details (an extra claw, a tail that species doesn't have). That's the actual failure mode being prevented — not "the identical individual in every single frame." Character sheets are more critical in story-driven productions (a specific character must look consistent across a narrative) and still important, but somewhat less critical, in documentary-style productions.

**Identity-consistency scope — precise, not a license for drift:**
- **Within one scene/beat, including all its split sub-parts** (e.g. `205a`, `205b` if `205` itself splits) — identity consistency IS required. Whichever character sheet a scene draws from, every sub-part of that scene must look like that same individual throughout.
- **Across different scenes/beats** (e.g. scene `205` vs. scene `206`) — variety is allowed. A later scene may assign a different character sheet (a different individual) or real B-roll instead — production's choice.
- **If a scene assigns a different character sheet than a prior scene, that new individual must then stay consistent throughout all of that scene's own sub-parts** — the continuity rule reapplied to whichever sheet that scene is drawing from. Variety is a per-scene assignment, never permission for the subject to drift mid-scene.

Write `Production/Recurring_Subjects.json`:
```json
{
  "creatures": {"main": ["@mantis_shrimp_main"], "variants": ["@mantis_shrimp_02"], "background": ["@clownfish_bg"]},
  "props": [],
  "environments": ["@reef_burrow"]
}
```

**Judgment call on environments:** if a production stays in one distinct, recognizable location across several scenes, that location gets a sheet. If the subject moves through many one-off environments, none of them need one — nothing recurring to keep consistent. When genuinely unsure, skip the sheet and revisit only if a continuity check flags drift after generation.

## Step 2 — Build the sheets

Using the dedicated skill for each asset type — never the general image-prompting guide directly:
- Recurring creature/character → [`Character-Sheet-Generation`](../Character-Sheet-Generation/SKILL.md)
- Recurring prop → [`Prop-Sheet-Generation`](../Prop-Sheet-Generation/SKILL.md)
- Recurring environment → [`Environment-Sheet-Generation`](../Environment-Sheet-Generation/SKILL.md)

Ground every sheet in `Research/Reference_Images/` from Production-Research-Agent's output where available. Save to the calling pipeline's standard sheet folders.

## Step 3 — B-roll vs. generation, per beat (the "smart editor" decision)

For each beat, check it against `Research/Pexels_Inventory.json` (built by Production-Research-Agent): **does existing real footage already cover the specific action this beat describes** (e.g. "a mantis shrimp digging a burrow in the sand")?

- **Yes** → use that footage as B-roll. Skip generation for that beat entirely.
- **No** → generate it, using that scene's character/prop/environment sheet(s) + storyboard to keep the generated portion visually consistent.

**Creature-specific vs. generic boundary — governed by one question, not a rigid rule: is this story about one specific, identifiable individual, or the subject/species in general?**
- **Specific individual** (rare — a real, known, named subject the story is actually about): real footage of that actual individual is fair game to use for beats specifically about them, because it genuinely is them, not a stand-in. The story may still cut to generic footage of the species when the narration broadens beyond that individual.
- **General subject/species** (the common case): there is no single continuous individual being followed. Real B-roll of the species doing the described action is a legitimate substitute for generation whenever it exists, even though it's technically a different individual — that's how real documentaries already work. The character sheet's job here is continuity for the parts that DO have to be generated, not enforcing "same individual" across the whole video.

**Hard cap (locked 2026-08-18): B-roll is capped at a maximum of 5 seconds of real stock footage per clip.** Beyond that, the remainder of the clip should be (or return to being) generated rather than leaning further on stock footage.

**Training goal — build real editorial judgment, not a fixed rule.** This decision should work the way a real documentary editor reasons about a cut, not "insert B-roll every N seconds." If example documentary footage is available, run it through a denser Video-Analyzer pass (near-per-second screenshotting) to build that judgment from real examples over time.

Write the combined result — asset assignments AND B-roll/generation decisions — to `Production/Asset_Plan.json`:
```json
{
  "beat_id": "205a",
  "character_sheet": "@mantis_shrimp_main",
  "environment_sheet": "@reef_burrow",
  "source": "b_roll",
  "b_roll_clip": "Research/Pexels_Downloads/Mantis_Shrimp_Burrow_02.mp4",
  "b_roll_trim_s": [3.2, 6.8],
  "generation_needed": false
}
```

## Step 3b — Geography beats require a real map asset

Any beat whose narration names a **place, region, route, migration, or species range** is flagged in `Asset_Plan.json` as needing a **map asset** (`"needs_map_asset": true`, with the region described). The map is a real basemap (Production-Research-Agent Step 2b should already have sourced it — Natural Earth PD, or a stylized map generated from a reference) styled to the channel, used as a base layer with the animated path drawn over it tracing the real geography. If research did **not** produce a map for a flagged beat, that is a gap to fill before assembly — never a thing to stylize around with a synthetic squiggle (0003 Glass Frog Notes 9–10).

## Step 4 — Trim selected B-roll (non-destructive)

For any beat assigned real footage: **never trim the original download.** Trim from a copy, producing a new, separate clip file — the original in `Research/Pexels_Downloads/` stays untouched so it can be re-trimmed differently later if needed.

**Save the trimmed clip directly into that scene's own clip folder (locked 2026-08-19, supersedes the earlier separate-`B_Roll/`-folder convention):**
```
[production_folder]/Video_Clips/<Scene_ID>/Scene_<NN><Letter>_BRoll_<short-descriptor>.mp4
```
e.g. `Video_Clips/Scene_03/Scene_03B_BRoll_ReefFish.mp4`. B-roll and generated clips for a scene live side by side in the same folder, sharing one continuous lettered sequence (see Step 6) — so assembly can read one ordered file list per scene without cross-referencing a separate B-roll directory. `<short-descriptor>` is a plain-language tag for what the footage shows (e.g. `ReefFish`, `SmallShrimp`) — never a generic name like `clip.mp4`.

## Step 5 — Storyboards

Build one storyboard per scene via [`Storyboard-Generation`](../Storyboard-Generation/SKILL.md), using the calling channel's own visual style and the scene's real duration (frame count derived from actual duration, never guessed). Follow that skill's own shot-variety and anatomical-precision rules as documented there.

## Step 6 — Clip boundaries, then start/end frames (per split clip, not per scene)

**Clip-boundary decision rule (locked 2026-08-19):** a scene's storyboard panels do not split into sub-clips by fixed duration (e.g. "always halve a scene"). Instead, for each candidate span of the storyboard ask: **can one prompt, one start frame, and one end frame plausibly produce this action, in no more than ~8 seconds?** Shorter is fine — a 2-second beat doesn't need padding to hit 8s. If a span is too visually complex or discontinuous for one prompt/frame-pair to carry (e.g. it contains a hard subject change, or several unrelated actions), split it into more, shorter clips rather than forcing one generation to cover too much. A storyboard panel showing a wholly different, non-recurring subject (a background creature, a generic environment cutaway) is usually a sign that span should be **B-roll instead of a generated clip** (see Step 3), not a generation-boundary problem.

**Clip durations — record only the real target; padding + trimming is enforced downstream in code (locked 2026-08-28, revised 2026-08-30).** For every clip, write **one** duration value into `Asset_Plan.json`/`Clip_Plan.json`: `target_duration_s` — the beat's real on-screen duration from actual narration/beat-sheet timing. Do **not** hand-compute a `generation_duration_s` any more. The generation stage (`pipeline_supervisor.py` via `clip_durations.request_duration`) derives the API request length itself — `ceil(target_duration_s) + 1s`, clamped to the model's `[4, max]` range, always an integer — and after the clip generates it head-trims the file back to exactly `target_duration_s`. Rationale for the +1s pad: video models (Seedance especially) undershoot the requested integer by ~0.1–0.9s, and a clip that ends up shorter than its beat causes a loop-back flash-cut in assembly (incident 0003_Glass_Frog_Transparency). A clip that still comes back shorter than `target_duration_s` is regenerated, never stretched or looped. Sub-floor beats (a glitch-cut hook shorter than 4s) need no special handling — the clamp to 4 and the head-trim back to target cover them automatically. See [`Seedance-Prompting-Guide`](../Seedance-Prompting-Guide/SKILL.md)'s "Minimum duration is a hard floor" section.

**Sequential lettering spans the whole scene, not just generated clips (locked 2026-08-19):** every segment in a scene's timeline — generated clip or B-roll insert alike — gets one letter in chronological order: `Scene_03A`, `Scene_03B`, `Scene_03C`, `Scene_03D`, `Scene_03E`, etc. A scene that resolves to generate → B-roll → generate → B-roll → generate is lettered straight through (A/B/C/D/E) regardless of which segments are generated vs. stock — this keeps one readable ordered sequence per scene instead of two separately-numbered tracks.

For every generated sub-clip (e.g. `Scene_03A`, `Scene_03C`), generate a **dedicated start frame and end frame** via GPT-Image-2, grounded by that scene's character/prop/environment sheet(s) **and** its storyboard panel(s) — not a single shared pair for the whole scene. This is what prevents the subject from drifting/morphing across a long implied span; each sub-clip gets its own tight anchor at both ends.

**Generate the end frame using the start frame as a reference, not independently (locked 2026-08-19).** Generating a sub-clip's two frames from their storyboard panel crops alone, with no shared reference between them, lets each generation invent its own environment — different rock/terrain arrangement, different background density, different color grade — even when the storyboard panels themselves only differ because one is a close-up (little background visible) and the other is a wide shot (more background revealed). Seedance then has to interpolate between two genuinely different locations across the clip, producing a visible background shift mid-motion. Caught on a real production: Scene_03E's close-up start frame showed a near-empty dark void behind the subject, its independently-generated wide end frame invented a dense, brighter boulder field — different lighting, different rock scale, different density — and the resulting clip visibly changed environment partway through. Fix: when generating a sub-clip's end frame, pass the already-generated start frame as an additional input image (alongside the character sheet and storyboard panel) with explicit prompt language that the environment/seafloor/lighting must match the reference start frame — this is the same location revealed further, not a cut to a new one.

**Start and end frame must be visually distinct — never near-duplicate framing/composition (locked 2026-08-19).** If a sub-clip's start and end frame read as virtually the same shot to the human eye (same subject pose, same framing, only minor differences), the video model has almost no delta to interpolate motion from and produces a poor/static result. Choose start/end frame pairs from storyboard panels with a real compositional difference (wide vs. close, different subject position, different framing) — full mechanism and the confirmed failure case documented in [`Seedance-Prompting-Guide`](../Seedance-Prompting-Guide/SKILL.md).

Generate this full asset set — sheets, storyboard, start frame, end frame — **regardless of which video-generation model the production ends up using.** Images are cheap relative to video generation; having the assets on hand means a scene can be redone with a different model later without regenerating references from scratch.

---

## Reference combination at generation time

Per the `Seedance-Prompting-Guide` skill's confirmed mechanism, a beat's generation call can carry storyboard, character/prop sheet(s), and environment sheet together in one `reference_image_urls` array with `@ImageN` ordinal tags — but this exact combination is architecturally confirmed, not yet tested end-to-end. Pilot on one isolated shot before relying on it for a full batch.

## Scope

Channel-agnostic. Any pipeline in this workspace invokes this skill the same way, once its shot list exists. Do not fork a per-channel copy — channel-specific style/tone rules belong in the calling pipeline's own skill, not here.
