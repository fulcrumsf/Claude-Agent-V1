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
6. Two shadows per template: (a) frame-edge shadow (frame lip on the art), (b) light-source shadow (window light, measured from the photo's own wall sun line).

## Art fit rule
Cover-fit and center-crop to the opening ratio; never stretch; never leave a white edge. Mats are built into the template as a uniform-width layer with bevel shadow.

## Checker (to build; not built yet). Runs headless with `photocraft-cli`, no window needed
Run on all 43 existing templates plus every new template at build time. Result per template: PASS / FAIL with reasons, shown on the Templates tab so Tony never opens files by hand.

1. **Opening vs art area:** hide every layer but BASE, detect the opening (inner frame edges), compare to the smart-object rectangle. FAIL if any edge is off by more than 3 px or if the art overlaps frame wood.
2. **Grid / card test:** render with solid black art and with solid white art. Any pixel inside the opening that does not change = gap (white sliver); any pixel outside the opening that changes = art over the frame.
3. **Overlay size:** every shadow/glare layer's bounds equal the art rectangle, or it has a mask limiting it to the art. FAIL otherwise.
4. **Overlay purity:** every shadow layer must be neutral (chroma near zero) and non-photographic. FAIL if frame/wood colors are present.
5. **Sun angle:** measure the light/shade edge angle from the BASE wall and compare to the shadow layer's edge angle (within 3 degrees). FAIL otherwise.
6. **Ratio:** opening ratio vs target ratio within 3 percent (cover-fit crop limit); otherwise the template is mislabeled or rejected.
7. **Mat consistency (when a mat exists):** uniform width on all four sides, bevel and shadow present.
8. **Hand-editable:** named layers (`Place Artwork Here`, `SHADOWS`, `GLARE`), no stray hidden OLD layers.

Auto-fix path for failures: re-measure the opening, resize overlays, rebuild shadows from black fills per the rules above, and show the result before saving (old version goes to the folder's `Archive`).

## PhotoCraft how-to learned (live bridge)
- Launch with a control port and token file: `/Applications/ArtCraft/PhotoCraft.app/Contents/MacOS/photocraft --control 47800 --control-token-file <file> <psd>`. Talk to it with `photocraft-cli mcp --bridge 127.0.0.1:47800 --control-token-file <file>` (JSON-RPC: `doc_inspect`, `command_run`, `ui_screenshot`). Never run `photocraft --help`; it opens the GUI.
- Headless on-disk analysis: `photocraft-cli mcp --automation-read-root <dir> --automation-write-root <dir>`; `doc_open`, hide layers with `layer.setProps`, `doc_export` PNG.
- `edit.transform` with a `quad` moves layer content to a quadrilateral. **Deselect first**: with a selection active the source is only the selected part and the call does nothing useful. Pass an explicit `rect` from the layer bounds.
- A three-cornered (degenerate) quad collapses the layer. Use a rotated rectangle to make a diagonal edge.
- `layer.mergeDown` resets blend, opacity and clip on the result; re-apply them.
- `layer.setProps` takes `visible`, `opacity`, `blend`, `clipped`, `name`. Agents never delete layers; retire by hide + rename "OLD ... (retire)" and let Tony delete.

## Reference numbers for the Wabi bedroom (verified 2026-11-10)
Opening 1058, 162, 542 x 740 px (art ratio 0.7324); sun line on the wall: y = 709 - 0.406 (x - 650), about 22 degrees rising to the right.
