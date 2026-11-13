# Ikigai Portal Build Plan (locked 2026-11-10, from the tab-by-tab review)

Status: PLAN ONLY. Nothing below is built until Tony says go. Read with `Mockup_Docs/Template_Layer_Rules_And_Checker_Spec.md`, the 2026-11-08 handoff and memory `ikigai-listing-slot-map`, `mockup-fit-and-mat-rules`, `template-checker-needed`.

## 1. Main tab (Ikigai Digital Studio)
- Ideas list: fully responsive width (grows/shrinks with the Chrome window, fills evenly, no dead space); bigger score, two-line description.
- Idea Bank: Pinterest-style masonry grid of larger cards with the approved art as the thumbnail (default 4 columns, responsive).
- Details panel: art capped to about 45% of panel height (contain, click for full size); "Run upscale + resize" and Approve/Deny in a sticky action bar at the top.
- Studio chat: no white-on-black bubbles; dark text on light backgrounds (warm tint for Tony, paper/white for the studio).

## 2. Art tab
- Fine as is.

## 3. Production tab
- Listing slot map: 1 main, 1A video (never "slot 2"), 2 poster, **3 room**, 4 Instant Download, 5 what-you-get + sizes, 6 wall diagram, 7 important notes, 8 close-up detail, **9-19 rooms**, 20 reviews. Fixed slots: 1, 1A, 2, 4, 5, 6, 7, 8, 20 (same every listing). Rooms: 3 and 9-19 (12 total); Tony's checked rooms fill 3, 9, 10, 11, 12 in order; the agent fills the rest.
- Fix the fixed-slot copy: current files are numbered one lower for 4-8 (`03_Instant_Download` -> slot 4, `04_Download_Contents` -> 5, `05_Wall_Size_Guide` -> 6, `06_Important_Notes` -> 7, `07_Detail` -> 8); remap in code.
- Panel "Not Found" was only the stale server; new routes exist (restart the Portal after every build).
- Fit rule: cover-fit, centered, clip the excess, never stretch, no white borders; mats only as built-in template layers (uniform width, bevel + shadow). Reject scenes whose frame ratio is more than about 3% off the art ratio.

## 4. Templates tab
- "Build this" button on every gap tile (shows cost about 18 credits, one click approves, saves the new template into that folder, shown for approval).
- Remove the two-image template from the picker/tab for this version (move into that folder's `Archive`; bring back for 2/3-image and multi-pack sets later).
- Three-dots menu on each card: "Edit with chat" opens a large overlay (room left, chat right, before/after). Chat edits layers via PhotoCraft's CLI/bridge (smart-object corners, shadow/glare opacity/blur/position, mat, frame); healing/Content-Aware tools for small removals; image-edit model (about 18 credits, cost shown first) only for real pixel changes, pasted onto the BASE layer. X asks Save/Discard when there are unsaved edits; old versions go to `Archive`. "Open in PhotoCraft" button launches the app with the control port + token file and selects the layer Tony names (bridge verified 2026-11-10).

## 5. Template checker (headless, `photocraft-cli`)
- Spec in `Mockup_Docs/Template_Layer_Rules_And_Checker_Spec.md` (opening vs art area, black/white card render test, overlay size/mask, overlay purity, sun angle, ratio, mat, hand-editable layers).
- Run on all 43 existing templates and on every new template; PASS/FAIL with reasons on the Templates tab; failures list shown before anything is changed; fixes follow the rules (rebuild shadows from black fills, masked to the opening, measured sun angle).

## 6. Frame detection upgrade: BUILT 2026-11-11 as the standard (SAM everywhere)
- **Standard (Tony 2026-11-10):** pixel-perfect, anti-aliased, no jagged/stair-stepped edges, no misses from shadows or soft gradients, full resolution. Flood-fill / Canny / brightness-threshold masks are not used for new builds (the old `find_insert` stays only as legacy code for tests). Full method in `Mockup_Docs/Template_Layer_Rules_And_Checker_Spec.md` ("Precision standard").
- Built: `Portal/app/sam_frames.py` (SAM 2.1 hiera **large** on Apple MPS, ~1-4 s per photo; Gemini rough box -> SAM candidates -> material-edge alpha refinement -> sub-pixel four-corner fit -> loud failure), wired into `scene_templates.build_psd` (corners, measured lip + key-light shadows, layer masks, black/white card test <= 1 px) and into the checker's opening check (SAM opening on the BASE render; old edge search only as fallback / for mat templates). SAM lives in `~/.cache/ikigai-sam` (venv + checkpoints), run as a subprocess.
- Measured 2026-11-11 on the blank-frame photos (Wabi bedroom excluded): Japandi_Simple 0.31 px max, Modern_BLue 0.46, Victorian_Floor 1.01, Wabi_ISO 1.07 (corner error vs an independent material-edge reference, visually checked at 12-16x); Minimal_ISO fails LOUDLY (its inner mat panel has no visible right edge in the sun), as does the angled Cradenza (a vase covers the bottom edge). Before: 4-12 px.
- Original plan text (kept for reference):
- Segment the insert with SAM 2 (Segment Anything, free, Apache 2.0, runs on the Mac), with Gemini vision supplying a rough box; fit four corners to the mask; verify with the checker's black/white card test; failures go to Tony with "Open in PhotoCraft".
- Ask AI scene prompts for a plain matte white insert, no glare, no heavy shadow on it.
- Prototype target: corner error 2 px or less (current method 4-12 px). **Do not prototype on the Wabi bedroom (already verified).** Tony will supply a template that was done wrong; test on that, then on the 5 known blank-frame photos.
- Install SAM outside the workspace (user cache/venv); no new Agent-OS folders.

## 7. Later / not in this build
- Video_02 template, the "finalization" view, 2- and 3-image sets, multi-packs, description text/PDF/etsy_draft steps, copy-to-clipboard buttons.

## Rules that apply to the whole build
- Never delete files or layers (retire by `Archive` or hide + rename "OLD ..."; Tony deletes). Never create folders except style folders under the template tree; ask for anything else.
- Shadows: black fill, cut, blur, Multiply, masked to the opening, angle measured from the photo; never copy photo pixels.
- Precision: every new template's corners and every mask come from SAM 2 + edge refinement at full resolution (section 6); a build fails loudly rather than guessing.
- Restart the Portal at the end of every build and report how it was verified.

## Decisions from Tony (2026-11-10, after the plan was locked)
- **New folders:** missing room/style folders (for example Entryway, Laundry) ARE created inside the template tree, in the correct NNN_ place, but ONLY after Tony approves the exact name and path. The agent shows the literal proposed path first ("Build this" card or chat), waits for approval, then creates it. No other folders, ever. (Reason: past agents invented odd folder names.)
- **Book Club Cat re-slot (rename only, nothing deleted):** fixed images renamed to the new slot numbers, done highest slot first so nothing collides: `07_Detail` -> `08_Detail`, `06_Important_Notes` -> `07_...`, `05_Wall_Size_Guide` -> `06_...`, `04_Download_Contents` -> `05_...`, `03_Instant_Download` -> `04_...`. `08_Room_Teak_Sideboard_Window_Light` is renamed to room slot 3 (Tony may reject it; he is editing the Teak PSD). The two rooms the agent built (`09_Room_Living_Room_Boho`, `10_Room_Bedroom_Modern`) had border problems: move both to `03-Etsy Images/Archive/` and redo them after the checker and fit rule exist.
