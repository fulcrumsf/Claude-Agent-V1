# Session handoff 2026-11-07 (Claude Code): Ikigai mockups, Production tab, PhotoCraft room templates

Read first next session: `005_Ecommerce/Etsy-Ikigai/Mockup_Style_Guide.md` (all of it; sections 6 and the later "Tony's ..." parts override earlier text), then this file.

## Done and committed (code, no images)
- Mockup step (slots 1, 2, 7 from Tony's PSDs via photocraft-cli + fixed images 3-6, 20): `Portal/app/mockups.py`, wired in `pipeline/steps.py`. JPG only now.
- Production tab (Portal, http://localhost:8800): new images inline with Approve / Deny / Undo; hides templated slots 1, 2, 7 and non-JPGs; full-width cards. `app/production.py`, tests.
- Art tab: one "Run mockups" button (`POST /ikigai/api/mockups/{idea}/run`). Rooms are OFF (`mockup_rooms: false` in `config/settings.json`) until the new room recipe is wired in.
- Room mockup v1 (`rooms.py`, 12 fixed scenes) was rejected by Tony. Do not turn it on.

## Done this session, NOT yet wired into the Portal
- `Portal/app/rooms.py`: v2 hero code (persona-driven scene prompts, magenta find_frame, composite_v2) from agent work. `Portal/app/frames.py` + `config/frame_styles.json`: tasteful frame chooser (scored, with reasons; ornate only for vintage/oil/classical/gothic/dark-moody). `Portal/app/walls.py` + `config/wall_palettes.json`: wall colour chooser (art-director logic; subtle, realistic paints only, scored on furniture tone + art accents + value key). Tests: 82 pass.
- Room_Templates folder (Tony approved the path 2026-11-07): `005_Ecommerce/Etsy-Ikigai/Room_Templates/01_Teak_Sideboard/` holds 4 PhotoCraft PSDs (soft, window-soft, leaf-dapple, golden-bars; one plate+PSD per light), the base plate, template json, and the build scripts (`build_template_v2.py`, `render_v2.py`, `guard.py`, `kie_edit.py`, `quads.py`) and light prompts. PSDs/images are git-ignored; scripts and json are committed. The scripts still reference the old scratchpad paths in places; fix paths when moving them into `Portal/app`.
- Proven recipe (see agent report summary in the style guide + `Room_Templates/.../build_template_v2.py`): plate with magenta panel -> 3 relit edits via kie.ai image-to-image (Nano Banana 2 `image_input`, GPT Image 2 `input_urls`, upload via kieai file-stream-upload; ~34 credits/room) -> one PSD per light with layers (BASE, WALL COLOUR paint layers, 2 art smart-object instances with/without mat, MAT, FRAME oak/walnut/black/white, GLASS Screen 22%) -> render by `layer.setProps` visibility + `replaceContents` on "Place Artwork Here" (~0.3 s/variant) -> guard (art hue <= 8 deg, shadow cover <= 35%).

## Tony's verdicts (all recorded in the style guide, memory `feedback_mockup_rules_2026-11-07.md`, `001_Architecture/Feedback_Loop/2026-11-07_Feedback.md`)
- v2 template shadows APPROVED; overall look/feel approved ("natural, naturally styled").
- Wall colours: must be art-directed, not random; sage okay, purple-pink wrong, charcoal hit or miss; complementary but subtle and realistic, matching the art and the furniture. `walls.py` implements this but is NOT yet used by the template renderer (renderer still has fixed paint chips).
- No faces; POV hand OK; glass sheen good; props only when lived-in (real-buyer persona, never catalogue staging); frames via chooser, some with mat; style reference ImaginatoriumLab 4583825939.
- Best-seller sweep (section 7 of the guide): top sellers often open with a plain product shot, floor-lean and flat-lay on linen are common; Tony has NOT answered: relax the straight-on limit? allow people-from-behind/feet POV? add a "frame flat on linen/bed" template?

## Open / next steps (in order)
1. Wire `walls.choose()` + `frames.frames_for_print()` into the template renderer so each print gets its own wall paint and frame set; re-render a 6-look sheet for Book Club Cat and show Tony (he will approve or fix).
2. Fix the 3 small weak spots: leaf-dapple variant barely reaches the art (one re-roll ~10 credits), white frame reads taupe in shade, greige near-white on bright plate.
3. Build 9+ more room templates (persona-driven; suggested first for Book Club Cat: reading nook, unmade-bed bedroom, floor lean), each its own `Room_Templates/<NN_Name>/`.
4. Move the render code into `Portal/app` (module), make the Run mockups button pick rooms/frames/walls/lights per slot, write rooms to `Designs/<design>/03-Etsy Images/` as JPG, show them in Production for approve/deny. Turn `mockup_rooms` on only then.
5. Videos: Video_01 = templatized (PSD `001-Standard Package/01A_Video_Mockup/Video_Mockup.psd`, hidden), Video_02 = new, shown for approval. Not built; unknown whether photocraft-cli can render the video PSD headless; Tony adds videos to Etsy by hand. Ask Tony what Video_02 should show.
6. Still open from before: "Approve with notes" auto-fix vs record only; Details-panel trimming; other production steps (package, listing_text, etsy_draft); Portal Art tab doesn't show mockups yet; stale 27 MB `Designs/00121-Book Club Cat/03-Etsy Images/07_Detail.png` is for Tony to delete (agents may not).

## Facts for the next agent
- Credits: kie.ai ~835 left after today; Alura used ~700 of 20,000 this month.
- Security: Tony's old n8n workflow JSONs (`~/Documents/Docker/n8n-data/workflows/Ikigai_Mockup_Gen_Rooms _V4.json` and backups) contain a fal.ai API key in plain text; Tony may want to rotate it. Old n8n mockup creator redrew the art with AI (Etsy accuracy risk); we composite the real pixels instead.
- Commits this session: 3d308304, d03b414c, 0d712d9b, plus the final mockup-research commit. Nothing pushed. Subagent scratch outputs are in the session scratchpad (will not persist); the PSD templates and scripts were copied into Room_Templates.
