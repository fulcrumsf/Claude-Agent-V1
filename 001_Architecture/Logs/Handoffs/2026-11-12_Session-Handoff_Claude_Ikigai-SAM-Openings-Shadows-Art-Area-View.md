# Session Handoff, 2026-11-12 (Claude Code), Ikigai template openings, SAM, shadows, art-area view

Written for the next session. Read this first, then `Etsy-Ikigai/Mockup_Docs/Template_Layer_Rules_And_Checker_Spec.md` and `Etsy-Ikigai/Pipeline_Docs/Ikigai_Portal_Build_Plan_2026-11-10.md`.

## What is true now (verified)
- Portal runs at http://127.0.0.1:8800 (started from the last session in the background; if it is down: `cd 005_Ecommerce/Etsy-Ikigai/Portal && uv run --no-project --with-requirements requirements.txt uvicorn app.main:app --port 8800`). Restart it after every code change; tabs cache the old page, so Tony hard-refreshes (Cmd+Shift+R). 147 tests pass (`python -m pytest -q` in the same way).
- **SAM 2.1 large** (in `~/.cache/ikigai-sam`, outside the workspace) finds smart-object corners for every NEW template (`app/sam_frames.py`). Rule from Tony: pixel-perfect, SAM for every detection and mask, no flood-fill or threshold masks.
- **Opening rule (new today, in the spec doc):** the art area is the frame's HARD inner edge with the shadowed paper counted as opening (SAM's paper edge sat 4.5 px inside on the left of the living room). Art = opening + 1.5 px pad (`opening_pad_px`, range 0-2). The pad is hidden by a new `Frame Hard Shadow` layer; `Frame Edge Shadow` is a soft measured band; `Light Shadow` unchanged. All shadows are black fills, Multiply, masked, measured from the photo, never copied pixels, never invented where the photo has none. Checker and card test accept 0-2 px of art under the frame, fail a gap over 0.5 px.
- **New living-room template** `Room_Templates/Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/002_Modern/LVRM_Midcentury_Walnut_2x3/LVRM_Midcentury_Sideboard_2x3_Template.psd` (+ scene PNG, template.json, SAM_Overlay.png). Folder approved by Tony ("Reuse existing folder"). Rebuilt 2026-11-12 from the existing scene (0 credits). Old PSD, json and overlay are in that folder's `Archive/` with `_before_opening_fix_2026-11-12`. Checker PASS, card test 0.13 px. Teak Sideboard is archived (`002_Modern/Archive/Teak_Sideboard`).
- **Book Club Cat slot 3** is re-rendered: `Designs/00121-Book Club Cat/03-Etsy Images/03_Room_Living_Room_Modern_v2.jpg` (old JPG in that folder's `Archive/`). I zoomed the left edge myself: no gray strip, soft shadow beside the dark wall. Not yet clicked through in the Production tab.
- **Templates tab, "Show art area":** global checkbox plus a per-card "art area" button. It renders every template with the normal test card multiplied amber (`template_gallery.tint_card`, cache names `Gallery_<key>_at.jpg` / `_al.jpg`), so frame, mat, bevels and shadows stay visible and amber ends where the art ends. Tony's example image is the target look. The Edit-with-chat window still draws a flat translucent amber polygon from the template's saved `quad_art` (no border); Tony has not said whether he wants it to use the amber card too.
- Edit-with-chat, Build this, checker, slot map (rooms = 3 + 9-19, fixed 1, 1A video, 2, 4-8, 20) were built earlier (see the build plan and memory notes).

## Waiting on Tony (do not decide for him)
1. In Production: approve or deny the slot-3 image (v2).
2. In Templates: the living-room card shows "NEW, approve?" (Approve template / Deny to Archive).
3. Pad width: the pad shows as a thin darker line on the right and bottom. Keep 1.5 px or set `opening_pad_px` to 1.0?
4. Editor tint: switch it to the amber test card too?
5. Whether to add the kie.ai Nano Banana fill/remove runner (PhotoCraft bridge AI repo Avgilles/photocraft-bridge-AI, runner contract `xp-photocraft/runner@1`) for "remove this" in Edit with chat, using SAM masks. Unanswered; Tony's hardware (M3 Max 36 GB) can host ComfyUI but nothing is installed.

## Open work (priority order)
1. The checker still shows 2 PASS / 42 FAIL across 44 templates (stored results predate the tighter tolerance). Most failures are old shadow layers built from copied photo pixels (33 templates). Tony has not chosen the fix; the spec's "Auto-fix path" is the plan (re-measure opening with SAM, rebuild shadows from black fills, old PSD to Archive, show before saving). Tony said he'll supply a known-bad template to test SAM on.
2. SAM fails loudly on `Minimal_ISO` (no visible right edge in hard sun) and the angled `Cradenza` (vase over the bottom edge); two photos sit just over 1 px (Victorian_Floor 1.01, Wabi_ISO 1.07). Wabi bedroom is excluded from SAM (already verified by hand).
3. The full Generate path in the Portal UI (card click to `run_slot`/`build_psd` with live SAM and credits) was only covered by fake-backed tests and one scripted run. Test it once for real before relying on it.
4. Book Club Cat slots 9-19 are still pending cards; the two earlier bad rooms are archived. 721 credits left after the 18 spent on the scene (check balance before generating).
5. Later list: Video_02 template, finalization tab, 2- and 3-image and multi-pack sets, description/PDF, `etsy_draft` step (never set state=active), copy-to-clipboard buttons, main-tab layout notes from the 2026-11-10 review (ideas list responsive, Idea Bank masonry, details panel, chat colours) per the build plan.

## How-to facts worth keeping
- Never run `photocraft --help` (opens the GUI). Headless: `photocraft-cli`; live bridge: `photocraft --control <port> --control-token-file <file>`; never print the token. See the spec's PhotoCraft how-to.
- Agents never delete files or layers and never create folders without Tony approving the exact path. `rm` is blocked by the guard; do not work around.
- The router hook asks for opus-standard/opus-deep on frontier work; the opening/shadow fix was done by opus-deep (report is the basis of the spec section).
- Tony wants short direct answers, shown not told, and an explicit "unverified" when something was not checked. He catches things by eye (left-edge strip, white band); trust his visual reads and measure before disagreeing.

## Git
Everything for this work was committed at the end of the session (message names the opening/shadow fix and art-area view). Auto-generated files were left out on purpose: `001_Architecture/Graphify/REGISTRY.md`, `Skills/Skill-Index.md`, `Tools/Tool-Manager/data/model_catalog.json`, `Skills/.system/*`, `.obsidian/workspace.json`, `.tmp.driveupload/`. Large PSD/PNG/JPG outputs are not tracked.
