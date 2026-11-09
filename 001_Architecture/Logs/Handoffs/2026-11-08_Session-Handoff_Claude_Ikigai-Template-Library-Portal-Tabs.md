# Session handoff 2026-11-08 (Claude Code): Ikigai template library, Portal Templates tab, folder cleanup, Production-tab + room-mockup build spec

Read first next session: this file (the BUILD SPEC section is the plan Tony approved in conversation), then `005_Ecommerce/Etsy-Ikigai/Room_Templates/Directory.md`, then `Mockup_Docs/Mockup_Style_Guide.md` (last sections override earlier text), then `Rules_And_Policies/Etsy_Attributes_And_Style_Crosswalk.md`, and memory `feedback_room_template_recipe_ai_frame_in_scene.md`. Tony's next session goal: confirm you understand, ask no more questions, then BUILD so he can test in the Portal (http://127.0.0.1:8800). He wants SHORT, direct answers (no recapping the UI, no asking for things you can look up or fetch yourself).

## Done (all committed, nothing pushed)
- Teak Sideboard room template cleaned (lamp + cord, book spines, one door pull, v3 PSDs). Production image `Designs/00121-Book Club Cat/03-Etsy Images/08_Room_Teak_Sideboard_Window_Light.jpg` exists; Tony will probably reject it (he is editing the Teak PSD himself; do not re-render until he says; then the old one goes to `Archive/`). NOTE: Tony now considers the computed-frame approach wrong (see recipe below); the Teak template's computed frames are the thing he disliked.
- Tony's 26 own PSD templates copied from iCloud (originals untouched), standardised (one smart object named `Place Artwork Here`), 19 PNG scenes turned into layered templates, unusable files moved to `~/Desktop/Delete`. All hand-editable (named groups SHADOWS/GLARE/MAT/FRAME; base photo on its own layer).
- Folder layout = Tony's three-digit master tree: `Room_Templates/Portrait_Templates/<NNN_Ratio_*>/<NNN_Room>/[<NNN_Style>]/<template folder>`; 44 template folders (47 tiles incl. 4 Teak lights). Empty duplicate agent-made `01_..04_Ratio_*` folders, `Teak_Sideboard/Retired/`, `Old_Directory_Merged_Delete_Me.md`, empty `007_For_Use` subfolders: for Tony to delete.
- Etsy-Ikigai root tidied (docs in `Rules_And_Policies/`, `Listing_Templates/`, `Mockup_Docs/`, `Research/`, `Pipeline_Docs/`; `Directory.md` has old->new paths).
- Portal: Production tab cache bug fixed; new Templates tab (room-type groups, Style + Ratio chips as filters, 4:3 crop assumed, gap tiles for empty folders, style assignment with Gemini auto-guess, saved in `Portal/config/template_styles.json`). 98 tests pass. `mockup_rooms` is still FALSE in `Portal/config/settings.json`.
- Etsy attributes + style crosswalk written (`Rules_And_Policies/Etsy_Attributes_And_Style_Crosswalk.md`, linked from Etsy-Ikigai CLAUDE.md/Directory.md).
- Book Club Cat's rejected listing images (12 old rooms + 2 Rejected_ files) moved to `03-Etsy Images/Archive/`.

## BUILD SPEC (Tony's decisions, ready to build; nothing below is built yet)

### 1. Art tab
- Remove the Run mockups button. Keep only "Run upscale + resize" (+ "Run again", which stays for settings problems).
- Upscale+resize now ALSO creates the always-the-same listing images: slots 1, 2, 7 (art swapped into his PSDs via the existing `app/mockups.py`) and copies slots 3, 4, 5, 6, 20 into `Designs/<design>/03-Etsy Images/`. Tony never approves/denies these (they look the same every time); do NOT surface them in Production and do not bring them up again. A later "finalization" tab may show everything; do not raise it.
- Default for re-runs: never overwrite an already-approved room image (new version goes beside it, old one to Archive). Tony has not said when a re-run is ever needed (only if upscale settings were wrong); do not add UI for it beyond what exists.

### 2. Production tab
- Only designs that have been upscaled appear (Year Fire Goat, approved but not upscaled, stays Art-tab only).
- Small thumbnail cards in a row at the top. Click one: the big middle panel opens for that listing (large enough to hold everything).
- In the panel: (a) pick up to 5 room types by check boxes, choices ONLY from Etsy's Room list (Bathroom, Bedroom, Dorm, Entryway, Game room, Kids, Kitchen & dining, Laundry, Living room, Nursery, Office); picking 1 is fine; the agent fills the rest; (b) categorise the design's style(s) from the shop style list (Trendy, Abstract, Animals, Botanical, Food-Drink, Game Room, Japan Art, Mid Century, Minimalism, Nature, Nursery, Retro, Travel, Typography, Vintage, Beach Ocean); if left blank the agent decides from the art (the Templates tab already has a vision auto-guess). Ticks become TAGS on the design.
- Then placeholder cards ONLY for slots that need building: rooms start at slot 8. Slots 8-12 take Tony's picked rooms in order; 13-19 the agent fills with rooms that make sense for the art (compatibility rule below; repeating a room type with a different style is fine, e.g. modern + mid-century living room; sensible beats unique; cyberpunk art never goes in laundry/kitchen; if too few rooms fit, show fewer rather than pad).
- Each slot card: Generate / Regenerate (one at a time; Generate-all comes later when Tony trusts it), result shown in the card, Approve / Deny (denied -> Archive). Plus a "+" on each slot to pick any template from the template library (Templates gallery picker). Mockup scenes may use rooms outside Etsy's list (Creative Space, Hallway); only the check boxes are limited to Etsy's list.
- Fix stale Portal setting `etsy_images_max` 10 -> 20 (Etsy allows 20 photos + 2 videos, verified).
- Video slot(s): Video_01 templatised; Video_02 later (probably a video template). Note only, no build now.

### 3. How a room mockup is made (Tony's recipe, replaces the computed-frame approach)
1. Prompt Nano Banana Pro / Nano Banana 2.1 (`nano-banana-2-1`) / GPT Image 2.5 (in `Room_Templates/.../Scripts/kie_edit.py`) for a complete photoreal room with ONE real frame holding a BLANK WHITE INSERT in the needed ratio. Prompt structure (from Tony's Midjourney example, memory file has the full text): "Photorealistic <style> <room> interior featuring one vertical picture frame with a blank white insert (<ratio>). Realistic textures, subtle decor, moody and lived-in detail that feels authentic. Lighting is soft warm daylight, naturally diffused, never harsh. Camera angle: 3/4 corner. Composition should be vertical, focused on the frame and wall area. no other frames". The art is NEVER in the prompt; the artwork already exists and is composited later, so one room template works for any print.
2. Detect the four corners of the white insert (auto; eyeball the first); in PhotoCraft make the base image a layer, add a smart object `Place Artwork Here` at those corners, replace with the print (reuse `app/mockups.py` fit logic; full art always visible, never cropped).
3. Add ONE separate shadow layer shaped like the real key light direction (e.g. window-frame shadow from the left); glass sheen optional. Keep PSD hand-editable, named groups.
4. Export JPG into `03-Etsy Images` as the slot number; hand-guard (art hue/shadow checks exist in `room_templates.guard`).
5. AUTO-SAVE every generated scene as a template (no asking) into `Portrait_Templates/<NNN_Ratio_*>/<NNN_Room>/<NNN_Style>/<Template_Name>/` (create the style folder when a template first hits that cell, only then); denied looks go to that folder's `Archive/`. Keep NNN_ three-digit numbering; use existing folders; empty folders are build targets.
- Ratio of the scene = the art ratio shown, picked by popularity weights (2x3 35%, 3x4 25%, 4x5 25%, 5x7/ISO 10%, 11x14 5%); never use a ratio that would crop the sold art. Mockup must still read as a real room with art direction (not an extreme zoom).
- Cost: one user click per card = approval; show credits left (kie.ai ~757). Tony has not discussed template-building cost beyond that.
- Existing 44 templates + Teak remain in the library and appear in the "+" picker and Templates tab; wiring them for rendering means giving each a manifest (smart-object layer name is already standard `Place Artwork Here`).

### 4. Art-to-room compatibility rule (agent-side)
Score each Etsy room type against the idea text + style tags + image (use `Etsy_Attributes_And_Style_Crosswalk.md`); exclude low scores. The room x style matrix stays internal; Tony does not want to see it. Missing combination = a template to generate (card says "generating new template" and saves it per step 5).

### 5. Etsy attributes at draft time (later step, `etsy_draft`)
Use the crosswalk: tags -> Room / Home style / Art subject / Occasion / Holiday / colours / aspect ratio. Digital downloads never get Framing, Frame mat, Frame color, size or material attributes. Never `state=active`.

## Tony's standing rules (also in memory)
- Empty template folders are build targets; never delete/rename his empty folders. Unapproved/superseded files go in an `Archive` folder inside the same folder (code and tabs ignore Archive; same for listing images). Use his existing folders, never create duplicates; NNN_ numbering.
- Models: Nano Banana Pro, Nano Banana 2.1, GPT Image 2.5. No faces, no people from behind, no feet POV; POV hand OK; props only when lived-in; no random lamps etc. Straight-on limit relaxed; add a "frame flat on linen/bed" template later.
- Answer directly and briefly; looking at the Portal is for my understanding, not to describe back; fetch findable info (Etsy API keys exist) instead of asking.

## Still open for Tony (not blockers for the build)
Tony to: finish/approve edits to the Teak PSD and say when to re-render; approve the leaf-dapple 60% shadow limit; confirm Templates tab 4:3 crop; delete the leftover files listed above. Undecided: whether/why upscale is ever re-run beyond settings problems; Video_02; what the "finalization" view looks like (later). Description-text, PDF, etsy_draft steps are still stubs; copy-to-clipboard buttons still wanted (Tony's 2026-10-27 request).

## Facts
- kie.ai credits about 757; Gemini style guesses cost about 1 cent total. Etsy API works (x-api-key = keystring:shared secret from `~/.mcp-secrets.env` ETSY_IKIGAI_CLIENT_ID/SECRET).
- The fal.ai key in Tony's old n8n workflow JSONs was verified NOT in the Agent-OS git repo; Tony said not to worry.
- Tooling note: the tool is PhotoCraft (`photocraft-cli`), not Photoshop; Python scripts drive it headless.
- Commits this session: 736e1b0d, 532f29f7, 6aed888b, 37e1c4f3, 2c0f5959, ea6b643f (nothing pushed; Etsy crosswalk/handoff/CLAUDE.md edits from the last part of the session are uncommitted).
