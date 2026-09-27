---
name: seedance-prompting-guide
description: This skill should be used when writing or reviewing Seedance prompts, choosing reference images versus start/end frames, directing camera movement or audio, or troubleshooting storyboard grids, titles, scale, and character continuity. Covers Seedance 1.5 Pro, 2.0, Fast, Mini, and 2.5 through provider-specific endpoints, while preserving Tony's tested labeled-sheet workflow.
---

# Seedance Prompting Guide

Use this living guide for Seedance 1.5 Pro and newer. Combine official capabilities with useful production experience. Preserve methods Tony developed through iteration; absence from an official guide does not make a technique invalid. Read [Examples.md](Examples.md) for camera-specific prompts, storyboard examples, and optional comparison tests.

## Separate capabilities, recommendations, and experience

Label the basis of advice:

- **API requirement:** obey the selected provider's actual model, input roles, limits, and supported fields. Prompt wording cannot override these.
- **Official recommendation:** use as informed guidance, with its model scope. A recommendation is not necessarily a prohibition or an exhaustive list of effective methods.
- **Local production method:** preserve Tony's approved approach, including full labeled sheets, tag use, and reference order. Describe observed results honestly without promising universal success.
- **Experiment / community technique:** retain useful ideas with provenance and uncertainty. Do not turn an agent's attempted fix into a user rule or silently replace the production method.

For a conflict, first distinguish a genuine input incompatibility from a prompting preference. Explain the former and choose a supported route; retain the approved local method when only recommendations differ. Ask before a paid comparison or a deliberate change to an approved production recipe. Do not repeat requests for authorization already given.

## Choose the exact model and input mode first

| Model | Temporal-image mode | Contextual references | Guidance scope |
|---|---|---|---|
| **Seedance 1.5 Pro** | Clean first image; optional clean last image on supported endpoints. Text-only generation also exists. | No contextual sheet/reference slot. | Build consistency into the actual scene image using sheets upstream. Do not submit grids or contextual `@Image` mappings. |
| **Seedance 2.0 / 2.0 Fast / 2.0 Mini** | First image or first/last pair, endpoint permitting. | Dedicated reference mode supports sheets and storyboards. | Select one supported mode. Do not combine temporal fields and references on Kie/Ark endpoints that forbid it. Verify each wrapper. |
| **Seedance 2.5** | Endpoint-specific first/last modes. | Richer reference and storyboard support. | Keep separate from 2.0 assumptions; verify availability and schema before use. Adding guidance does not change a channel's approved model. |

Models below 1.5 are outside this guide. Never describe all older Seedance models as sharing one capability set.

Record the provider, exact model ID, endpoint, input mode, duration, resolution, audio setting, and ordered assets before submission. Provider aliases differ: Kie's Mini is `bytedance/seedance-2-mini`; BytePlus lists `dreamina-seedance-2-0-mini-260615`. Neither alias should be substituted blindly on another service.

Treat published limits as snapshots, not universal defaults: typical documented duration ranges are 4–12 seconds for 1.5 Pro, 4–15 for 2.0, and 4–30 for 2.5. Reference counts, resolutions, aspect ratios, seeds, and camera controls vary by endpoint. Check the live schema when implementing a call. Kie's 1.5 `fixed_lens` and WaveSpeed's `camera_fixed` are different field names; neither guarantees perfectly stationary output.

**Never confuse image roles.** On Kie 1.5, `input_urls[0]` is the first frame and `[1]` is the last frame. A character sheet in slot 2 becomes an ending target, not identity context; this happened locally twice. On reference endpoints, use the designated reference array. Prompting a reference to “match the starting frame” provides direction, not the temporal constraint of a first-frame field.

## Preserve the local reference workflow

Apply this section to the approved sheet-based **reference mode**, not every possible Seedance call. Neon Parcel's current default is Mini through the existing wrapper. Other channels retain their own approved models and modes. Do not silently upgrade models, activate channels, or switch providers.

1. Build and visually validate the environment first, using the environment skill's plan → elevations → camera-view workflow. Then build the required subjects, props, and storyboard.
2. Send the **final full labeled** storyboard, environment sheet, and all character/creature/prop sheets built for the clip. Preserve title labels, markers, dots, and callouts. Account explicitly for any omitted sheet and its reason; do not quietly substitute unlabeled derivatives. Do not run a paid environment-only validation video after Tony has approved the environment still.
3. Upload in order: storyboard, environment, character/creature sheets, then props. Map every image using the endpoint's actual syntax; the Kie workflow uses `@Image 1`, `@Image 2`, etc. Save this order with the payload.
4. Use each subject's tag in its action beats, not merely in the mapping block. Refer to storyboard and environment again in the body. This is Tony's local consistency rule, not a claim that official grammar requires every tag to be a grammatical subject.
5. Keep the reference block followed by the gate's exact headings: **1. CAMERA LOCK**, **2. SCENE CONTINUITY**, **3. ACTION TIMELINE**, **4. AUDIO**, **5. HARD CONSTRAINTS**, in that order. Here “Camera Lock” means the agreed camera behavior: fixed, handheld, or another specified capture style. It does not force every shot to be stationary.
6. Use the existing `seedance2_call.py` gate for enabled channels and `Data/Video_Reference_Set.json` for the reference inventory. Read the channel configuration; do not change it as part of prompting. Passing a syntax gate does not establish visual quality or semantic consistency.

Tools live under `001_Architecture/Tools/Video-Generation/Generic_Tools/`: `seedance2_call.py`, `seedance2_gate_config.json`, and `check_seedance_prompt_refs.py`. Mini execution has local production history; verify support before using the same path for other variants.

Use [v7](../Neon_Parcel_Longform_Compilation_v2/Templates/Seedance_Winning_Prompt_Template_v7.md) as a **historical fixed-camera scaffold**. Preserve its useful structure and reference relationships. Its literal “every panel of @Image 1” phrase is an agent trial with uncertain benefit, not a protected clause or Tony requirement. This clarification supersedes prior claims in this guide that the phrase must remain verbatim. Do not copy fixed-camera sentences into handheld shots.

## Validate the actual images before spending

Inspect all relevant panels, not only filenames, labels, or generated reports.

- Check **scale and depth**: person relative to doorway, animal relative to vehicle, foreground versus background, distance to landmarks, ground contact, occlusion, and paths through the scene.
- Check world geometry across angles. A water tower remaining on the left of every image does not prove correct placement. A reverse view can legitimately swap screen sides; the same world positions must explain every view. Check mailbox placement and vehicle orientation as well as landmark names.
- Check identity, subject count, clothing, anatomy, and props across sheets and storyboard. For hand interactions, resolve each person's own left/right arm and contact at the image stage; the video action must match those images.
- Check entrances, exits, obstacles, and routes are physically possible and visible when needed. State origin → path → outcome rather than asking the model to invent hidden geometry.
- Check the storyboard matches the intended camera behavior. Fixed shots keep a consistent vantage point; handheld panels can change framing while preserving world layout and a feasible operator path.

Recommend repairing contradictory assets first. If Tony accepts an error, record the exception and risk in production notes. **“Ignore that error” during review is not permission to tell Seedance to ignore the reference.** Keep review commentary and hopes about model behavior out of the prompt unless explicitly requested.

Use the channel's storyboard QA and handoff requirements before prompt construction. Neon Parcel's `storyboard_handoff.py` lives in `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/`. Build the prompt from the accepted images and physical sequence, not an outdated initial idea.

## Use storyboards according to their role

Distinguish three inputs:

| Input | Intended use | Important limit |
|---|---|---|
| Composite storyboard grid in reference mode | Sequence, approximate composition, action progression | The model may copy layout/text or depart from panel details; no exact per-panel guarantee. |
| Separate ordered keyframe references | Clearer individual states and their order | Still contextual references unless the API assigns temporal roles. Count against reference limits. |
| Clean first/last scene frames | Opening/ending visual constraints in temporal mode | No contextual sheets alongside them where mode exclusion applies. |

**Official evidence:** Seedance 2.0's launch demonstrates a storyboard/shooting script with character, scene, and prop references. Storyboards are not an unsupported hack. Seedance 2.5 guidance further distinguishes approximate grid-based storytelling from ordered keyframe alignment. See the cited guides and the examples companion.

For a continuous shot, describe storyboard panels as successive moments of **one continuous view**, with camera behavior explicitly stated. For genuine multi-shot coverage, specify shot changes. A whip pan is camera movement within one recording, not automatically a cut. Do not import cinematic coverage into surveillance footage.

Keep timestamped blocks as useful local planning structure. For 2.0/Fast/Mini, treat them as sequence/pacing guidance, not exact timing guarantees. 2.5 officially improves integer-second timing control; still inspect the result rather than assuming frame accuracy.

Keep grids legible and the action achievable within the duration. Official 2.5 guidance recommends simple storyboard drawings with little text and a modest panel count (around 15 or fewer); this is not a universal API maximum or an instruction to remove Tony's sheet labels. Avoid redundant references. If the approved required assets exceed an endpoint's limits, explain the conflict and agree on a split or supported route instead of silently dropping assets.

## Direct camera, action, and audio together

Write concrete physical events, camera behavior, and audible causes. A subject → action → environment/audio → visual/camera structure is a useful drafting aid, not the only valid official format. In image-to-video, focus on what changes while matching visible identity and geometry.

For Neon Parcel, aim for spontaneous real-life footage: ordinary phone exposure, imperfect framing, reactive operator movement, or a genuinely fixed CCTV/doorbell view. Avoid advertising polish and cinematic coverage unless requested.

- **Fixed surveillance/doorbell:** state mounting position, continuous viewpoint, and no pan/zoom/reframe. Motion belongs to subjects.
- **Handheld phone:** state where the operator stands, what draws attention, pan direction, settling, and any walking/backing away. Allow natural shake and brief blur; maintain one continuous recording and coherent geography.
- **Window / car observer:** retain the viewing position and relevant window/car edges; avoid impossible passes through glass. Use parked-car or passenger framing where appropriate to the scenario.
- **POV character:** distinguish the character's eyes/body perspective from an observer holding a phone. Match limb action to the approved frame.

Keep action count manageable; “two or three camera moves” is a heuristic, not a model limit. Simplify only when action becomes rushed or contradictory. Keep a successful shot's identity and environment stable when testing action wording.

For native sound, name concrete ambience and synchronized foley. Where speech is intended, identify speaker and words clearly; quotation marks are a useful convention, not a proven unique trigger. For ambient-only footage, exclude dialogue, narration, music, and subtitles explicitly, while allowing intended animal sounds or nonverbal reactions. Do not simultaneously request screams and forbid all human vocal sound.

Retain the local dash-led exclusion line when appropriate, for example: `- No dialogue, no voiceover, no music, no subtitles, no on-screen text.` It is ordinary prompt text, not a special API negative-prompt switch. Adapt exclusions to the shot; no wording guarantees compliance. Local 1.5 narration leakage improved with concrete foley and removing genre language that suggested a documentary narrator.

For RR POV, retain native audio and no dialogue/music because music is added separately. For narration-driven films, keep characters silent and add the narration downstream. Presenter lip-sync and portal edits require their actual supported modes/tools; a tutorial's separate lip-sync service is not automatically a Seedance capability. See [Cinematic-Narrative-Multi-Character.md](Cinematic-Narrative-Multi-Character.md) for dialogue-oriented staging, applying this guide's model and evidence boundaries.

## Troubleshoot without discarding the working method

### Titles, labels, borders, split scenes, or tiled grids

1. Inspect the raw full clip before upscaling. Record when leakage appears and whether the action is otherwise usable.
2. Verify actual model, payload, and image roles. A grid used as a temporal frame is an input error; negative wording cannot fix that role.
3. Check reference consistency, camera instructions, storyboard complexity, and exclusions. Repair errors before experimenting with phrases.
4. If a stable outer border/title can be cropped without losing action or required resolution, offer a versioned crop. Inspect the whole result. Tiled scenes generally need a new generation.
5. For another attempt, state what changes and obtain any required spend approval. Keep labeled sheets as the default. Official troubleshooting suggests removing unnecessary text from references when text leakage persists; propose this as an **optional derivative comparison**, preserving originals, not an automatic label-removal rule. Landscape-then-crop is another conditional option only when the final composition permits it.
6. If reference layout continues to leak, consider the existing approved fallback: clean first/last scene frames in a separate temporal-mode call. Do not mix modes, change models silently, or imply it will necessarily preserve all reference-mode detail.

### Duplicate characters, drift, or confused sheet views

Keep the full labeled-sheet workflow. Official 2.0 guidance warns that multiple views can be interpreted as multiple people; this identifies a possible failure mechanism, not proof that Tony's sheets are harmful. If needed, propose a controlled comparison using a clear headshot plus full-body reference with explicit same-person roles, or isolated relevant views. Obtain approval for the alternative; preserve sheet originals. 2.5's improved multi-view support must not be projected backward onto 2.0/Mini. See the test plan in Examples.md.

### Motion, endpoints, and duration

Do not require a camera-angle change just to make start/end images different. Matching start/end views are allowed; a fixed camera may be essential. Choose meaningful subject-state progression when the story needs it, and describe intermediate action. Identical endpoints do not forbid motion in between.

For narration-timed pipelines, retain the local `ceil(target_duration_s) + 1` padding practice where supported, with the provider's integer minimum. If target plus padding exceeds the model cap, split/replan rather than silently truncating story action. Inspect actual returned duration, trim to the approved target while retaining required beats, and regenerate a too-short clip rather than looping it. This padding is a local workaround, not an official timing guarantee.

For longer sequences, last-frame carryover can help continuity in a supported temporal mode. Inspect pose, motion, camera, lighting, and audio across the join; it does not guarantee a seamless cut. Smaller storyboard groups can reduce overload but do not guarantee removal of tiling. Do not attach character sheets to a 1.5 continuation or combine incompatible modes.

A localized anatomy repair using an edited extracted frame followed by regenerating a segment (“inpaint bridge”) remains tutorial-reported, not locally validated. It changes the regenerated segment and may require transition repair; neither exact preservation nor lower cost is guaranteed. Follow actual provider face/person restrictions; sheets are not a promised way to avoid provider checks.

## Review and retain evidence

Before submission, compare prompt and payload with the approved shot: model/mode, reference versions/order, camera behavior, geometry, tags in beats, section order, sound, and exclusions. Keep anti-layout intent without mandating one magic sentence. Existing automated gates cover only part of this review; do not bypass a gate that rejects a new camera/mode combination—resolve its compatibility first.

After generation, review playback and frames at beat boundaries before approval/upscaling. Score motion/physics, scale/geometry, identity/count, camera continuity, detail, and audio separately. Save exact prompt, model, settings, assets, result, and changes for every attempt. Version outputs and preserve superseded artifacts in the approved project archive. Prefer changing one variable in comparison tests; acknowledge confounding changes when several are necessary.

Keep these local findings accurately scoped:

- Kangaroo doorbell: standard 2.0 result graded A. Model tier changed without approval, so recipe versus model effects cannot be separated.
- Moose Mini: usable local run graded C; later Monkey/v7 and Shot 07 history also exist. Do not keep the obsolete assertion that Mini was never tested. Mini remains Neon Parcel's approved default, not a universal quality winner.
- Shot 07: initial attempt tiled; retry changed both storyboard and wording, yielded one scene with title/border, then cropping salvaged it. No causal proof for the “every panel” phrase. Tony's acceptance of image defects was misread as model-facing instructions.
- Full labeled sheets: Tony reports improvement over many iterations. Preserve this practical evidence while leaving room for targeted comparisons.

## Sources and further reading

Audit sources reviewed September 2026; recheck live schemas when implementing. Official recommendations and provider limits remain separately scoped.

- [ByteDance Seedance 2.0 launch](https://seed.bytedance.com/en/blog/seedance-2-0-official-launch): storyboard plus character/scene/prop references.
- [Official 1.5 Pro guidance](https://docs.volcengine.com/docs/ark/seedance-1-5-pro?lang=zh): motion, camera, and sound direction.
- [Official 2.0 series guide](https://docs.byteplus.com/zh-CN/docs/modelark/2222480): reference use, multi-view ambiguity, and text troubleshooting.
- [Official 2.5 guide](https://docs.volcengine.com/docs/ark/seedance-2-5-prompt-guide?lang=zh): timing, grids, and multi-view improvements.
- [BytePlus-authored 2.5 guide on fal](https://fal.ai/learn/devs/how-to-use-seedance-2-5): grid versus ordered-keyframe examples.
- [BytePlus model table](https://docs.byteplus.com/zh-CN/docs/modelark/1330310) and [API](https://docs.byteplus.com/zh-CN/docs/modelark/1520757): exact IDs, availability, and input roles. A provider retirement does not establish retirement on all services.
- Kie schemas: [1.5 Pro](https://docs.kie.ai/market/bytedance/seedance-1-5-pro), [2.0](https://docs.kie.ai/market/bytedance/seedance-2), [Mini](https://docs.kie.ai/market/bytedance/seedance-2-mini).
- [fal 2.0 reference API](https://fal.ai/models/bytedance/seedance-2.0/reference-to-video/api): provider-specific fields and tags. WaveSpeed also exposes reference-capable endpoints; inspect the selected endpoint rather than assuming all routes behave alike.

Related skills: [environment sheets](../Environment-Sheet-Generation/SKILL.md), [character sheets](../Character-Sheet-Generation/SKILL.md), [storyboards](../Storyboard-Generation/SKILL.md), [Neon Parcel v2](../Neon_Parcel_Longform_Compilation_v2/SKILL.md), [RR POV v1](../Reimagined_Realms_POV_Shorts_Pipeline/SKILL.md), [RR POV v2](../Reimagined_Realms_POV_Shorts_Pipeline_v2/SKILL.md).

Historical tutorial links and prior wording are preserved in the [pre-audit snapshot](../../Audit_Reports/Seedance-Guide-Pre-Audit-2026-09-26.md). It is evidence/history, not active instructions. Consult it for older mask, presenter, portal, Seed Audio, and unreviewed tutorial leads; do not promote those leads to requirements without checking their source and model scope.
