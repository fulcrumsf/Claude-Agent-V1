---
name: Motion-Graphics-Compositing
description: "Use whenever a beat needs an animated diagram, infographic, data-viz, or collage-style motion graphic — never ask a video-generation model (Seedance or otherwise) to animate this kind of content. Triggers on 'build an animated diagram', 'animate this infographic', 'motion graphic scene', 'how do I animate a diagram without Seedance hallucinating', or any beat comparing/explaining/revealing abstract content over time. Channel-agnostic. Covers: isolated component-asset generation (transparent background or chroma-screen + AI matting), the style-lock rule (unified-illustration vs. collage mode), reusable Remotion animation-preset functions, audio hookup via the existing foley pipeline, and the cross-production asset library. This is the living reference — update it in place as new techniques are learned (grows via YouTube tutorial/case-study ingestion, same pattern as Seedance-Prompting-Guide), never fork a version-specific copy. <example>User: this diagram beat needs to animate from a wide comparison shot into a close-up reveal Assistant: invokes Motion-Graphics-Compositing — decomposes into isolated components, generates each with a transparent/chroma background, composites in Remotion with named animation presets</example>"
trigger: A beat needs an animated diagram/infographic/data-viz/motion-graphic, on any channel
---

# Motion-Graphics-Compositing

Builds animated diagrams, infographics, data-viz, and collage-style motion graphics from isolated static component assets composited in Remotion — instead of asking a video-generation model to animate the content, which fails hard on abstract/diagram material (see origin below).

**Full design history and reasoning:** `001_Architecture/Superpowers/Specs/2026-08-18-Motion-Graphics-Compositing-Skill-Spec.md`.

## Origin — why this exists

On Anomalous Wild's Scene 02 (photoreceptor-comparison diagram), Seedance 1.5 Pro was given a correctly-built start frame + end frame and still hallucinated within ~2 seconds — morphed into an unrelated mechanical structure, never converged on the real end frame. Worse than Seedance's known creature-drift failure mode, because abstract/diagram content gives a video model far less to anchor identity on than an organic creature does. The fix: stop asking a video model to invent the in-between motion at all. Generate each distinct visual element as its own clean asset, animate them in Remotion via keyframed opacity/scale/position. Zero drift by construction — verified pixel-exact against the source storyboard at every beat boundary. Tony graded the result "A+."

**Relationship to `Diagram-Generation`:** that skill owns the diagram-specific steps (real-reference research, base illustration, label-coordinate detection). Its Step 2 "Approach B" (component assets first) delegates the actual asset-isolation + Remotion-compositing mechanics to THIS skill. Diagram-Generation is diagram-specific; this skill is general-purpose — it also covers non-diagram motion graphics (collage-style pieces, infographic counters, title-card assemblies).

---

## Step 1 — Decide the mode: unified-illustration or collage

**Unified-illustration mode:** components are pieces of one grounded subject (e.g. a creature's anatomy, a single diagram's parts). **Style-lock required** — every component generation call must share the same base reference image and the same verbatim style-description block. Skipping this makes sibling components drift apart in lighting/color grading and look like they came from different scenes when layered.

**Collage/mixed-media mode:** components are intentionally heterogeneous (e.g. a Vox-style piece: a newsprint photo, a torn-paper texture, halftone-pattern type, a kraft-paper background). **Style-lock does NOT apply** — do not force one reference image across genuinely different materials/textures; that would fight the intended look.

Decide which mode applies before generating anything — state it up front, don't discover it after the fact.

## Step 2 — Decompose into isolated components

Same judgment call as `Diagram-Generation`'s Step 2: identify which visual elements are genuinely distinct and benefit from independent animation control. Read that skill's Approach A/B guidance for the general principle; this skill picks up once "Approach B, component assets" has been decided.

## Step 3 — Generate each component asset — try in this order

1. **Native transparent-background generation, direct OpenAI GPT-Image-2 API** (`background: "transparent"` parameter). Confirmed to exist in OpenAI's real API; **NOT exposed by kie.ai's `gpt_image_2` CLI wrapper** (no background/transparency parameter at all — checked 2026-08-18). Best case: zero keying/matting needed. **Not yet live-tested against our own account as of 2026-08-18** — test on the next real use, don't test speculatively. See `model_catalog.json`'s `capabilities.transparent_background_output` block on the `gpt-image-2` entry for the current confirmation status; update it once tested.
2. **Green/blue digital chroma-screen background + Recraft AI matting** (`kie-cli recraft_remove_background`) — robust fallback. A color far from the subject's own palette gives both classic colorkey and AI matting an easy, low-ambiguity job.
3. **Near-black background + Recraft AI matting** — last resort. Works (confirmed on Scene 02) but more failure-prone at fine-detail edges (thin lines, wisps) than a true chroma color, since a "near-black" prompt doesn't guarantee a literally pure, uniform background.

**Model routing:** check `model_catalog.json`'s `capabilities` field before defaulting to kie.ai out of habit — kie.ai is cheaper for GPT-Image-2 ($0.03 vs $0.04/image) but doesn't expose transparency, so a job that needs true alpha output must route to direct OpenAI regardless of price. Full reasoning: `GPT-Image-2-Prompting-Guide/SKILL.md`'s platform routing rule.

**Verify the matte, don't just check the file mode.** `Image.open(path).mode == "RGBA"` confirms alpha exists, not that it's clean — AI matting can leave semi-transparent fringing/haloing on fine details. Spot-check edges visually before considering an asset locked.

## Step 4 — Composite and animate in Remotion

**No generic one-size-fits-all compositor** — every production's motion graphic is custom (different assets, different pacing, different beat count). What's reusable is the keyframe math:

- **`kf()`** — the core keyframe helper (`interpolate` wrapped for readability, monotonic breakpoints, clamped at both ends).
- **Named animation-preset functions** — `crossfade`, `pushZoom`, `pullBackReveal`, `sideBySideHold`, `explodedAssembly` (implemented); `lineTraceReveal` (stub only — needs its own research pass before real use).
- Location: `002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-lib/motion_graphics_presets.ts`. Import and compose whichever presets fit the beat in a hand-written `.tsx` composition — reference pattern: `video-components/Scene02DiagramTest.tsx`.
- **Composite with plain alpha, not blend-mode tricks.** True-alpha assets (Step 3) need no `mixBlendMode` hack — plain `opacity` on the `<Img>` composites cleanly. `mixBlendMode: "screen"` was tried as a workaround on flat-background assets and only partially worked (removed the hard seam, left a faint residual line) — not needed once assets are properly matted, and would actively cause wrong results (washed-out colors) wherever two subjects legitimately overlap on screen at once.
- Tie all timing to the beat's real narration timestamps / storyboard reveal sequence — never guessed pacing.

## Step 5 — Verify by frame extraction, not "render and assume"

Extract frames at each beat/panel boundary (`ffmpeg -vf "select='eq(n\,N)'"`) and check them directly against the source storyboard panels. This is what caught both the Seedance failure (frames didn't match at all) and the compositing seam (visible only at specific transition frames, not obvious from a cursory watch-through).

## Step 6 — Audio

Motion-graphics beats still get the channel's standard 3-layer audio treatment (narration/music/ambient-SFX) where it's actually warranted — but foley/ambient-SFX generation is not automatic for every diagram beat. See the skip rule below first.

**Foley skip rule (locked 2026-08-19):** generate dedicated foley/ambient SFX for a beat ONLY if the diagram/motion-graphic actually depicts a sound-producing action or mechanism on screen — something with a real-world sound: a ticking clock, scrolling/counting numbers, moving mechanical parts, particle/liquid motion, an impact, a pulse/glow with a "zap" quality, etc. **Skip foley entirely for pure compositional reveals** — fades, pans, zooms of otherwise-static illustrated content where nothing depicted is "doing" anything (confirmed on Anomalous Wild Scene 02: two eyes → cross-section → receptor fan, a pure comparison reveal, no depicted mechanism). There's nothing diegetic to sonify in that case, and the full-length music track already covers ambience for these beats — a generated foley track just adds a stray, disconnected sound (a "click," on Scene 02's actual test) that doesn't read as belonging to anything on screen.

**This is a per-beat judgment call, not a blanket "diagrams never get sound" rule.** A diagram that includes a genuine moving/sounding element (a counter ticking up, a mechanism visibly clicking into place) still needs foley for that specific element — decide per beat, at this step, don't default either way without looking at what the beat actually shows.

**When foley IS warranted, reuse the existing mechanism — don't build a new one.** `generate_foley.py` + `foley_config.py` (`Reimagined_Realms_POV_Shorts_Pipeline` / `_v2`, swappable Mirelo/Sonilo video-to-SFX models) already does video-to-ambient-SFX generation. Render the motion-graphic clip first, then send it through this script — same as the live-footage pipeline already does. **First real use of this engine on Anomalous Wild specifically was 2026-08-18** (previously only used on Reimagined Realms' POV Shorts, where it lost an A/B test against Seedance-native audio for live-action clips — that comparison doesn't apply to diagram beats, which never have Seedance-native audio available in the first place since they don't go through Seedance video generation).

**Practical notes from first real use (2026-08-18):**
- wavespeed's video upload aborted on a full-size 1080p clip (17.5MB) — compress first (e.g. 960px width, crf 28) if an upload fails with "operation was aborted."
- Mirelo capped its output at 5.0s against an 11.05s input clip, no error/warning, just a shorter file. Check documented max duration, or try `sonilo` (the swappable alternative), before relying on it for beats longer than ~5s.

## Step 7 — Log the asset(s) to the asset library

- **Per-production:** `Production/Motion_Graphics_Asset_Library.json` — every component asset, its source scene, style-lock reference used (if any, per Step 1's mode), matting method used (Step 3), file path.
- **Cross-production master index:** `000_Wiki/Video-Production/Motion-Graphics-Asset-Library.md` — growing index across all productions/channels, so a recurring element doesn't get regenerated from scratch. Graphified for retrieval (`graphify query "..."`).

---

## Scope

Channel-agnostic. Any pipeline in this workspace invokes this skill the same way for any diagram/infographic/data-viz/collage motion-graphics beat. Do not fork a per-channel copy.

## Growth

Living reference, same pattern as `Seedance-Prompting-Guide` — update in place as new techniques are confirmed (Tony is feeding this skill YouTube tutorials on more complex Vox-style motion-graphics techniques; ingest findings here, don't fork a separate doc).
