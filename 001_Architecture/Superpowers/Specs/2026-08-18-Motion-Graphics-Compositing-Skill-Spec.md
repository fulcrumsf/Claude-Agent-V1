# Motion-Graphics-Compositing Skill — Spec (2026-08-18)

**Status: APPROVED FOR BUILD.** Unlike the Anomalous Wild rework note, this one is being implemented immediately per Tony's explicit go-ahead ("update everything... leave no stones unturned").

## Origin

Built from a real test on Anomalous Wild production `0002_Mantis_Shrimp_Color_Vision`, Scene 02 (photoreceptor-comparison diagram). Seedance 1.5 Pro hallucinated badly trying to animate the diagram via start/end-frame video generation — worse than its earlier creature-drift failure, because abstract/diagram content gives a video model far less to anchor identity on. Fix: generate isolated static component assets, composite/animate them in Remotion with keyframed opacity/scale/position. Tony graded the result "A+." This spec generalizes that pattern into a reusable, channel-agnostic skill.

## 1. Skill identity

- **Name: `Motion-Graphics-Compositing`.** Lives at `001_Architecture/Skills/Motion-Graphics-Compositing/`.
- Parallel to, and distinct from, the existing `Motion-Graphics` skill (design *taste* — callout placement, reveal timing, color judgment). This new skill is the *build mechanics* — how to actually produce a layered, animated composite from isolated assets.
- **Channel-agnostic from day one** — usable by Anomalous Wild, Reimagined Realms, and any future channel, for any beat that's a diagram, infographic, data-viz, or collage-style motion graphic (not organic creature/environment footage).
- **`Diagram-Generation` points to this skill** for the actual component-asset-isolation + Remotion-compositing mechanics (its Step 2 "Approach B"). Diagram-Generation keeps ownership of the diagram-specific research/illustration/label-detection steps (Steps 1, 4-5); this skill owns the general-purpose layered-compositing mechanics any motion graphic needs, diagram or not.
- **Living reference skill, grows via case-study ingestion** — same pattern as `Seedance-Prompting-Guide`: update in place as new techniques are learned (Tony is feeding it YouTube tutorials on Vox-style motion graphics next), never fork a version-specific copy.

## 2. Core principle

Every component asset that goes into a motion-graphics composite must be a clean, isolated, alpha-matted element with no hard border — so opacity, scale, and position can all be freely keyframed without visible seams. **Never ask a generative video model to animate diagram/motion-graphic content — generate the pieces as static assets and animate them in Remotion instead.**

## 3. Asset generation method — try in this order

1. **Native transparent-background generation via direct OpenAI GPT-Image-2 API** (`background: "transparent"` parameter — confirmed to exist in OpenAI's real API, NOT exposed by kie.ai's `gpt_image_2` CLI wrapper, which has no background/transparency parameter at all). Best case: zero keying/matting needed at all.
   - **NOT YET TESTED — do not test speculatively.** Tony will use this for the next diagram beat (a different scene in the same mantis-shrimp production, expected ~2026-08-19). Confirm it actually works through the API at that point, then update this section with the real result.
2. **Green/blue digital chroma-screen background at generation time + Recraft AI matting** (`kie-cli recraft_remove_background`) as the robust fallback — a color far from the subject's own palette gives both classic colorkey and AI matting an easy, low-ambiguity job.
3. **Near-black background + Recraft AI matting** — last resort (what the Scene 02 test used, before this spec existed). Works but is more failure-prone: if the asset's own background color isn't literally pure black, even AI matting can leave faint residual artifacts at fine-detail edges.

**New model-selection rule (goes into Tool-Manager + GPT-Image-2-Prompting-Guide, see Section 6):** use kie.ai's GPT-Image-2 endpoint when it's more cost-effective AND no alpha/transparent-background output is needed. Use direct OpenAI's GPT-Image-2 API when transparent-background output is actually needed — kie.ai's wrapper doesn't expose that capability regardless of price.

## 4. Style-lock rule — conditional, not universal

- **Unified-illustration mode** (e.g. an anatomical diagram's separate components — human eye, cross-section, receptor fan): all components MUST share the same base reference image and the same verbatim style-description block in their generation prompts. Without this, sibling components drift apart in lighting/color grading and look like they came from different scenes when layered together.
- **Collage/mixed-media mode** (e.g. a Vox-style piece with a newsprint photo, torn-paper texture, halftone-pattern type, kraft-paper background): style-lock does NOT apply — intentional material/texture variety across elements is the point. Do not force a single reference image across genuinely heterogeneous elements.
- Decide which mode applies per motion-graphic beat before generating any components — this is a judgment call stated up front, not discovered after the fact.

## 5. Reusable building blocks — NOT a rigid one-size-fits-all compositor

Every production's motion graphic is custom (different assets, different pacing, different beat count) — there is no single generic "data-driven compositor" component that fits all of them. What IS reusable:

- **The `kf()` keyframe helper** — `interpolate(frame, [frames], [values], {extrapolateLeft: "clamp", extrapolateRight: "clamp"})`, wrapped for readability. Extracted from `Scene02DiagramTest.tsx` into a shared lib.
- **Named animation-preset functions**, each a small reusable function returning transform/opacity values for a given frame range, composed together per-production rather than duplicated:
  - `crossfade(frame, fromFrame, toFrame)` — opacity handoff between two layers
  - `pushZoom(frame, startFrame, endFrame, fromScale, toScale)` — continuous scale-up "camera push-in"
  - `pullBackReveal(frame, startFrame, endFrame)` — scale-down + reposition to reveal surrounding context
  - `sideBySideHold(...)` — two elements held in fixed offset positions for a comparison beat
  - `explodedAssembly(frame, startFrame, endFrame, fromOffset, toOffset)` — parts animate from separated to assembled position
  - `lineTraceReveal(...)` — placeholder for a whiteboard-style vector-trace reveal (needs its own research pass — not built today, stub only)
  - Each production's composition (a hand-written `.tsx` file, same as `Scene02DiagramTest.tsx`) imports and composes whichever presets fit that beat — not forced through one template.

## 6. Tool-Manager capability-parity gap — being fixed

**Finding:** Tool-Manager's `model_catalog.json` only tracks price parity across platforms (`cheapest`/`cheapest_price` fields) — it has no field for feature/capability parity (e.g. "does this platform's wrapper expose transparent-background output for this model"). This gap caused a real mistake today: defaulted to kie.ai for GPT-Image-2 without checking whether its wrapper supports the transparency parameter the job actually needed (it doesn't; direct OpenAI does).

**Fix (this spec authorizes it):**
- Add a `capabilities` object per platform entry in `model_catalog.json` (start with the GPT-Image-2 entry: `kie_ai.capabilities.transparent_background: false`, `openai_direct.capabilities.transparent_background: true` — pending live confirmation per Section 3, Step 1).
- Update `Tool-Manager/SKILL.md`'s routing guidance to check capability requirements BEFORE applying the cheapest-price rule — price only decides between platforms that both support the required capability.
- **Standing process correction (logged to Feedback_Loop and Global_Agent_Memory):** consult Tool-Manager before defaulting to any specific platform/endpoint for a generation call, without waiting to be asked. When Tool-Manager's own data doesn't cover the actual question, instruct Tool-Manager to research and update its own data via its documented Update Protocol (`⚠️ TOOLBOX UPDATE NEEDED`, hand back exact text, calling agent writes it) — never surface an unresearched question back to Tony as if it were his job to know the answer.

## 7. Audio — reuse the existing foley mechanism, don't build a new one

Every motion-graphics beat still gets the channel's standard 3-layer audio treatment (narration/music/ambient-SFX) — a rendered motion graphic doesn't get to skip audio just because there's no Seedance-native audio to lean on.

**Mechanism: reuse `generate_foley.py` + `foley_config.py`** (already built, `Reimagined_Realms_POV_Shorts_Pipeline` and `_v2`, swappable Mirelo/Sonilo video-to-SFX models). Render the motion-graphic clip first, then send it through this existing script for ambient/foley audio — same as the live-footage pipeline already does. No new audio tool needed.

## 8. Asset library — per-production + cross-production master index

- **Per-production:** `Production/Motion_Graphics_Asset_Library.json` — every component asset generated for that production, its source scene, which style-lock reference it used (if any), which matting method (Section 3), and its file path.
- **Cross-production master index:** a wiki page (location: `000_Wiki/Video-Production/Motion-Graphics-Asset-Library.md`), a running, growing index across ALL productions/channels — "need a dog asset → check here → found, with a link to where it lives," same pattern as the rest of the vault's knowledge system.
- **Graphified** so it's queryable the normal way (`graphify query "dog asset"`) instead of requiring a manual file browse.

## 9. What's explicitly deferred, not being built in this pass

- Live-testing the direct-OpenAI transparent-background generation (Section 3, Step 1) — Tony will test this himself on the next real diagram beat, expected ~2026-08-19. Do not spend API cost testing it speculatively.
- `lineTraceReveal` preset — stubbed only, needs its own research/reference pass before real implementation.
- Retrofitting Scene 02's existing test assets to the new skill's conventions — explicitly left as-is per Tony ("leave as is because it looks fine the way it is"). Only remaining work on Scene 02 is its audio pass (Section 7).
