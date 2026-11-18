# Session Handoff, 2026-11-17, Ikigai canvas wrap strips, despill, independent edge check, light variety

Read this first. Follows `2026-11-16_Session-Handoff_Claude_Ikigai-Orange-Insert-Prompts-Template-Triage-Decisions.md`.

## What is now true (all committed, 221 tests passed at last run)
- **Templates tab:** failed templates are hidden by default. The old "FAIL only" box is now "Show failed (N)" (on = only the failed ones, to fix or archive at leisure). New/rebuilt templates awaiting approval always show.
- **Independent edge check** (`template_checker.py`): measures colour steps across each art edge from the scene pixels (not SAM, not the builder outline), says what the card edge sits on, attaches 8x zoom crops. Opening limit is about one screen pixel (not 0.5 px). No ratio blocker, ever.
- **Canvas fixes:** card placeholder has a 1 px dark-orange edge line; canvas path searches inward for the face-to-side step (`sam_frames.canvas_face_quad`); checker runs SAM with canvas=True for canvas templates.
- **Wrap strips** (`app/wrap_strips.py`): mirrored art band warped onto each camera-facing canvas side, shaded from the photo's luminance, drawn by the renderer (Production + `render_psd`). The PSD only holds a grey "Wrap Strip (placeholder)" layer, so judge from the render PNG, not PhotoCraft. Only the camera-facing side(s) show (right side in the Japandi scene).
- **Despill** (`app/despill.py`): pixel layer "Despill (orange bounce fix)" above BASE neutralises orange bounce in the gap/edge band; checker flags leftover orange. Older orange-blank templates: `python -m app.despill <folder>`. Tony approved this look as the SOURCE OF TRUTH for canvas-in-floater templates.
- **Prompt:** positive wording (matte flat orange face only, white canvas sides, direct soft-edged window light allowed). **Light variety** (`room_slots.pick_look`): weighted random light style (soft direct 35, overcast 20, crisp 15, dappled 15, golden 15), photographer (relatable creator 60, magazine 40), time, season, sun direction; saved in template.json with a seed; guard sentence keeps the art face flat and evenly lit. Gap tile tooltip says the look is picked at Build time.
- **Japandi Minimalist 11x14 template** (`Room_Templates/Portrait_Templates/005_Ratio_11x14/001_Living_Rooms/001_Japandi_Minimalist/`): built, wrap strips + despill, checker PASS, approved by Tony, rendered into Book Club Cat slot 3 (`03_Room_Living_Room_Modern_v4.jpg`, pending Tony's approve in Production).

## Waiting on Tony
1. Approve or deny the slot 3 image in Production (Book Club Cat). Slot 15 (Living room Japandi 4x5) is the closer decor match if he prefers; say so and re-run it there.
2. Triage of the 40 live templates (keep / hand-fix / regenerate / archive) from the 2026-11-16 handoff is still open; use "Show failed".
3. Delete (Tony does deletes): three superseded despill PSDs in the Japandi `Archive/` (`*_despill_v1..v3_superseded_20261117.psd`, about 26 MB each). A scan of live PSDs found no layers named OLD/retire; hidden or special layers are Mid-century Wood "Paper (covers old sample art)", Japandi "Wrap Strip (placeholder)", Colorful_LVRM_ISO hidden "Glass Reflection". All legitimate, none marked for deletion.

## Not yet done / risks
- New white-side-edge prompt and light-variety looks untested on a real generation (about 18 credits each; kie.ai about 1,250 earlier).
- Wrap depth is a fixed 5% guess; side detection only tested on Japandi and a synthetic scene (white sides, dark frames untested).
- Other canvas templates have no strips yet (`python -m app.wrap_strips`).
- Idea: put each side strip into the PSD as a smart object so PhotoCraft shows the true result (needs a check that a perspective-transformed smart object is possible).
- Re-running `app.wrap_strips` refreshes template.json but not the PSD placeholder layer.
- Dappled/crisp light may throw patterns onto the art area; creator-style framing may tilt verticals.

## Housekeeping notes
- Two PhotoCraft instances exist: the Portal-controlled one (control port 7878, now on its home screen, nothing open, leave running) and the plain app. The plain app was closed this session; its scratch example PSD (`Portal/data/rooms/Japandi_11x14_Book_Club_Cat_Example_For_PhotoCraft_2026-11-17.psd`) was saved.
- A stray click at screen point 1447,788 landed on the YouTube player in Chrome (accessibility access was newly granted); harmless but worth knowing.
- Test command: `cd Portal && uv run --no-project --with-requirements requirements.txt python -m pytest -q`. Portal restarts: `uv run --no-project --with-requirements requirements.txt uvicorn app.main:app --port 8800` (log /tmp/portal8800.log).

## Read first
`005_Ecommerce/Etsy-Ikigai/Mockup_Docs/Template_Layer_Rules_And_Checker_Spec.md` (new sections: independent edge check, wrap strips, orange despill), `Mockup_Style_Guide.md` ("Light and photographer variety"), memory `feedback_canvas_wrap_strips_despill_source_of_truth_2026-11-17.md`.
