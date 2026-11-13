# Template Layer Rules And Checker Spec

Written 2026-11-10 after a live fix of `BDRM_Wabi_Vertical_Template.psd` (Room_Templates/Portrait_Templates/003_Ratio_3x4/002_Bedroom/BDRM_Wabi_Vertical). Every template built by the agent before this date is suspect until the checker below has run on it.

## What was wrong in the first version (and probably in many others)
1. **Art area measured on the frame's outer edge**, so the smart object covered the frame wood on the left by about 16 px. Correct opening = the clear/white area inside the frame (inner edges), including a little shadow bleed.
2. **Shadow layers sized to the wrong box** and bigger than the art, so they spilled onto the frame.
3. **"Frame Edge Shadow" and "Scene Light & Shadow" were copies of photo pixels**, so frame-colored pixels (wood tint) showed inside the art. A shadow is NEVER a copy of the photo.
4. **Sun shadow angle was invented** (about 31 degrees) instead of measured. The real sun line on that wall rose about 22 degrees to the right.

## How a shadow layer must be built (Tony's rule)
1. Plain black fill (never copied photo pixels). Neutral only: R = G = B.
2. Cut to the shape the shadow needs (selection or rotated black rectangle whose edge lies on the measured sun line).
3. Blur to soften, blend mode Multiply, opacity low (frame edge about 30 percent; sun shade about 17 percent; window bar about 10 percent).
4. Limit it to the art opening with a layer mask cut to the opening (the "clipped" flag did not hold on merged layers; the mask always works).
5. Same position and size as `Place Artwork Here`, or masked to it.
6. Shadows per template: (a) frame-edge shadow (frame lip on the art, soft), (b) light-source shadow (window light, measured from the photo's own wall sun line), and since 2026-11-12 (c) the frame's HARD inner shadow over the art's 1-2 px pad (see "Opening rule" below).

## Opening rule: the frame's HARD inner edge, art padded under it (Tony 2026-11-12)
Found on `LVRM_Midcentury_Sideboard_2x3`: SAM's refined edge is where the PAPER looks like paper. In a 3/4 view the frame's dark inner wall shows, and the frame casts a shadow on the blank insert (a near-flat grey strip with a warm bounce from the wood, then a soft ramp). SAM stopped at the ramp, 4.5 px inside the real opening on the left, so the art left a grey strip of baked shadow between the frame's hard dark wall and the art (Book Club Cat slot 3, visible mostly bottom-left).

1. **Opening = the frame's hard inner edge, the shadowed paper counted as opening** (`sam_frames.opening_quad`, run inside `detect()`): from SAM's paper edge outward, the first HARD step in a shading-invariant material feature (chromaticity distance from the paper's own colour; a neutral white/grey/black frame uses brightness). A shadow or bounce changes that feature slowly (at most ~12% of the paper-to-frame contrast per 1.5 px); the frame starts with a jump (at least 20%). Placed sub-pixel on a linear colour projection (edge pixels are linear mixes), 200 points per side, one straight line per side. Loud failure: no hard edge within reach, not one straight line (< 60% inliers or > 0.6 px RMS), the added band looks like frame not paper, or the edge is more than 1 px inside SAM's paper edge.
2. **Art quad = opening + 1.5 px** (`opening_pad_px`, allowed 1-2 px) so the art blends under the frame edge with no sliver. The art covers ALL the baked paper, including its baked shadow.
3. **SHADOWS rebuilt from measurements** (`scene_templates.measure_edge_shadows`), all black fills, Multiply, masked to the art quad, above the art:
   - `Frame Hard Shadow`: crisp (0.35 px blur), only over the art's pad: per side the frame edge's own tone vs the paper (the dark inner wall where the photo has one, else the frame face), so no art shows on the wood.
   - `Frame Edge Shadow`: soft, per side a black band (strength, width, blur) fitted to the paper's darkening from the opening inward (fit from 1 px in; sides with flat paper get none, nothing invented).
   - `Light Shadow`: unchanged (key light / measured falloff angle).
4. **Checks accept the pad, nothing more:** `card_verify` (build) and the checker (sub-pixel SAM opening) fail a gap > 0.5 px (baked paper shows) or art > 2.5 px under the frame (pad limit 2 px + 0.5 px tolerance). The old integer edge search keeps +-3 px.

Measured 2026-11-12 on `LVRM_Midcentury_Sideboard_2x3.png` (offset of the hard edge from SAM's paper edge, outward +): left +4.53 px, top -0.41, right -0.16, bottom -0.19 (SAM ran slightly over the oak on those three). Checked against an independent per-row linear-mix estimate: median difference 0.00-0.02 px per side, 90% of rows within 0.27 px; checked by eye at 16x. Shadows measured: hard (pad tone) left 0.59 (dark inner wall), top 0.36, right 0.30, bottom 0.21; soft left 0.52 strength, 6.0 px band, 2.7 px blur (top 0.83 / -3.75 / 5.5, exponential-like lip); right and bottom none. Rebuilt PSD: card test 0.13 px, art under the frame 1.49-1.60 px per side, checker PASS (its own SAM run found the same opening within 0.03 px; art 1.42-1.59 px under it). Old PSD: `Archive/LVRM_Midcentury_Sideboard_2x3_Template_before_opening_fix_2026-11-12.psd`.

## Art fit rule
Cover-fit and center-crop to the opening ratio; never stretch; never leave a white edge. Mats are built into the template as a uniform-width layer with bevel shadow.

## Checker (BUILT 2026-11-10: `Portal/app/template_checker.py`, results `Portal/config/template_checks.json`; first run 1 PASS / 42 FAIL, see `Room_Templates/Directory.md`). Runs headless with `photocraft-cli`, no window needed
Run on all 43 existing templates plus every new template at build time. Result per template: PASS / FAIL with reasons, shown on the Templates tab so Tony never opens files by hand.

1. **Opening vs art area:** hide every layer but BASE, detect the opening (inner frame edges), compare to the smart-object rectangle. FAIL if any edge is off by more than 3 px or if the art overlaps frame wood. Since 2026-11-12 (SAM opening = the frame's hard inner edge): FAIL on a gap > 0.5 px or art > 2.5 px under the frame; the 1-2 px pad is expected. Since 2026-11-11 both sides are SUB-PIXEL: the visible art quad is fitted to the anti-aliased black/white card difference, and the opening is SAM 2's (`template_checker.sam_opening`, box = the visible art + 4%); the old inner-edge search is only the fallback (SAM failed or found another region, or the template has a mat). Never run on `BDRM_Wabi_Vertical`.
2. **Grid / card test:** render with solid black art and with solid white art. Any pixel inside the opening that does not change = gap (white sliver); any pixel outside the opening that changes = art over the frame.
3. **Overlay size:** every shadow/glare layer's bounds equal the art rectangle, or it has a mask limiting it to the art. FAIL otherwise.
4. **Overlay purity:** every shadow layer must be neutral (chroma near zero) and non-photographic. FAIL if frame/wood colors are present.
5. **Sun angle:** measure the light/shade edge angle from the BASE wall and compare to the shadow layer's edge angle (within 3 degrees). FAIL otherwise. Since 2026-11-11 the wall line is searched only on SAM's wall mask when SAM ran (props such as a dried branch no longer count as a "sun line"), and a smooth light-falloff shadow has no edge to compare (skip, not FAIL).
6. **Ratio:** opening ratio vs target ratio within 3 percent (cover-fit crop limit); otherwise the template is mislabeled or rejected.
7. **Mat consistency (when a mat exists):** uniform width on all four sides, bevel and shadow present.
8. **Hand-editable:** named layers (`Place Artwork Here`, `SHADOWS`, `GLARE`), no stray hidden OLD layers.

Auto-fix path for failures: re-measure the opening, resize overlays, rebuild shadows from black fills per the rules above, and show the result before saving (old version goes to the folder's `Archive`).

## Precision standard: SAM everywhere (Tony 2026-11-10, built 2026-11-11)
"Pixel-perfect, anti-aliased, no jagged/stair-stepped edges, no misses from shadows or soft gradients, full resolution." Flood-fill, Canny and brightness-threshold masks are NOT acceptable for new builds.

1. **Rough box:** Gemini vision (`sam_frames.gemini_box`), or the caller's box.
2. **SAM 2.1 hiera large** (`~/.cache/ikigai-sam`, Apple MPS, ~1-4 s): three prompts (box + centre click, click, box) x 3 masks; keep the clean filled four-sided ones whose edge band looks like their core (paper up to the edge, not frame moulding); try the SMALLEST first (a mat window inside a mat is the opening), then the next.
3. **Edge refinement at full resolution** (`refine_alpha`): in a thin band around SAM's edge every pixel is solved with the compositing equation between LOCAL inside and outside colours in Lab, shadow-invariant (lightness only 25% when paper and frame differ in colour, so a frame-lip shadow stays paper; when they share a colour, a line darker than both counts as opening), then a radius-1 guided filter. Result: smooth anti-aliased alpha on the real material edge.
4. **Sub-pixel corners** (`fit_quad`): ~200 alpha profiles per side along the side normal (1/8 px steps), 0.5 crossings, Huber + inlier line fit, intersections, three passes (handles perspective).
5. **Loud failure** (`verify_quad` -> QuadError): a side whose edge is not one straight line (< 60% inliers or > 0.6 px RMS), quad vs mask IoU < 0.985, or corners > 3% of the size from SAM's own. Nothing is built from a guess; the scene goes to Tony ("Open in PhotoCraft") or is regenerated.
5b. **Opening** (`opening_quad`, 2026-11-12): SAM's paper edge is extended out to the frame's hard inner edge (see "Opening rule" above).
6. **Card test in the finished PSD** (`scene_templates.card_verify`): black and white cards rendered with SHADOWS/GLARE hidden; the visible art quad (sub-pixel) must be within 1 px of the art quad (opening + pad), with zero sliver and zero art-over-frame pixels, and per side 0 to 2 px under the frame's hard inner edge (+-0.5 px).
7. **Other masks** (wall for the sun-line search) come from the same SAM + refine path (`segment_wall`). Shadow layers are black fills shaped by MEASUREMENTS (since 2026-11-12 measured from the OPENING: hard = the frame edge's tone over the art's pad, soft = per-side blurred black band fitted to the paper's darkening; before that a per-side k * exp(-d/w) lip; key light: wall sun line on the SAM wall mask, else the insert's light-falloff plane with its measured angle and depth), reaching 4 px past the art quad and cut by a real LAYER MASK (anti-aliased `select.lasso` on the quad -> `layer.layerMask.revealSelection`).

Measured 2026-11-11 (corner error vs an independent material-edge reference, checked by eye at 12-16x): Japandi_Simple 0.31 px, Modern_BLue 0.46, Victorian_Floor 1.01, Wabi_ISO 1.07; Minimal_ISO and the angled Cradenza fail loudly (no visible right edge in the sun / a vase over the bottom edge). Old method: 4-12 px. First template built this way: `LVRM_Midcentury_Sideboard_2x3` (card test 0.14 px, checker PASS).

## PhotoCraft how-to learned (live bridge)
- Launch with a control port and token file: `/Applications/ArtCraft/PhotoCraft.app/Contents/MacOS/photocraft --control 47800 --control-token-file <file> <psd>`. Talk to it with `photocraft-cli mcp --bridge 127.0.0.1:47800 --control-token-file <file>` (JSON-RPC: `doc_inspect`, `command_run`, `ui_screenshot`). Never run `photocraft --help`; it opens the GUI.
- Headless on-disk analysis: `photocraft-cli mcp --automation-read-root <dir> --automation-write-root <dir>`; `doc_open`, hide layers with `layer.setProps`, `doc_export` PNG.
- `edit.transform` with a `quad` moves layer content to a quadrilateral. **Deselect first**: with a selection active the source is only the selected part and the call does nothing useful. Pass an explicit `rect` from the layer bounds.
- A three-cornered (degenerate) quad collapses the layer. Use a rotated rectangle to make a diagonal edge.
- `layer.mergeDown` resets blend, opacity and clip on the result; re-apply them.
- `select.deselect` FAILS when nothing is selected; `layer.layerMask.revealSelection` consumes the selection (no deselect after it).
- `layer.setProps` takes `visible`, `opacity`, `blend`, `clipped`, `name`. Agents never delete layers; retire by hide + rename "OLD ... (retire)" and let Tony delete.

## Reference numbers for the Wabi bedroom (verified 2026-11-10)
Opening 1058, 162, 542 x 740 px (art ratio 0.7324); sun line on the wall: y = 709 - 0.406 (x - 650), about 22 degrees rising to the right.
