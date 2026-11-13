# Room_Templates: Directory

The ONE catalogue for every room-mockup template used for Ikigai listing images (room slots 3 and 9-19, slot map 2026-11-10), rendered headless with photocraft-cli. Everything lives under this folder; there is no other Directory file below it (merged 2026-11-08). PSDs and images are git-ignored (large); `room.json`, the template `.json` files, the authoring scripts and this file are committed. Style rules: `../Mockup_Docs/Mockup_Style_Guide.md` (later sections override earlier). Portal code: `../Portal/app/production.py` + `scene_templates.py` + `room_slots.py` (Production tab cards, AI scene templates, see the section below), `room_templates.py` (Teak looks + the shared accuracy guard), `frames.py`, `walls.py`, and `template_gallery.py` (the **Templates** tab, which reads the folder tree and the table below).

Approved by Tony 2026-11-07 (path `005_Ecommerce/Etsy-Ikigai/Room_Templates/`). Re-organised 2026-11-08 to Tony's layout (below).

## Layout (Tony's master tree, re-filed 2026-11-08)

Tony's three-digit folders are the masters. Naming convention: every ratio, room-type and style folder starts with a three-digit number `NNN_` (`001_Ratio_ISO`, `001_Living_Rooms`, `002_Modern`); template folders inside them keep their own names. The Portal strips the number and underscores for display (`001_Living_Rooms` -> "Living Rooms", `001_Japandi_Minimalist` -> "Japandi Minimalist"). Folders without the `NNN_` prefix at ratio level are not part of the library (never read as templates or gaps).

```
Room_Templates/
  Directory.md                          this file, the only directory
  Portrait_Templates/
    001_Ratio_ISO/                      ISO / A-series AND 5x7 (one bucket)
    002_Ratio_2x3/
    003_Ratio_3x4/
    004_Ratio_4x5/
    005_Ratio_11x14/                    its own folder (slots nearer 0.786 than 0.800)
      NNN_<Room_Type>/                  001_Living_Rooms, 002_Bedroom, 003_Bathroom, 004_Kitchen_Bar, 005_Office,
                                        006_GameRooms_Mancave (ISO also 007_Creative_Space, 008_Kids_Nursery)
        [NNN_<Style>/]                  optional, Tony makes these (e.g. 001_Living_Rooms/001_Japandi_Minimalist,
                                        002_Modern, 003_Boho_Colorful; ISO 002_Bedroom/001_Japandi ...)
          <Template>/                   one tidy place per template: PSD + preview (_Preview) + source scene
            Archive/                    not approved, do not use but kept (Original_ backups, old versions)
    Scripts/                            authoring scripts for the portrait templates (reference; old paths inside)
```

Current tree (depth 3, template counts; 43 portrait PSDs; the Teak Sideboard room was ARCHIVED by Tony 2026-11-10):

| Ratio | Room | Style folder (count) | Room level (no style fit) |
|---|---|---|---|
| `001_Ratio_ISO` | `001_Living_Rooms` | Japandi_Minimalist 1, Modern 6, Boho_Colorful 1 | 1 (Victorian_Floor) |
| `001_Ratio_ISO` | `002_Bedroom` | Neutral_Aesthetic 1 (Japandi, Scandinavian empty) | 1 (Girl_Peach_Trendy) |
| `002_Ratio_2x3` | `001_Living_Rooms` | Japandi_Minimalist 2, Modern 1 (`LVRM_Midcentury_Sideboard_2x3`, SAM-built 2026-11-11, checker PASS; + `Archive/Teak_Sideboard`, retired), Boho_Colorful 1 | - |
| `002_Ratio_2x3` | `002_Bedroom` / `004_Kitchen_Bar` / `006_GameRooms_Mancave` | (no style folders) | 1 / 1 / 1 |
| `003_Ratio_3x4` | `001_Living_Rooms` | Japandi_Minimalist 1, Modern 3, Boho_Colorful 1 | - |
| `003_Ratio_3x4` | `002_Bedroom` / `004_Kitchen_Bar` | (no style folders) | 4 / 2 |
| `004_Ratio_4x5` | `001_Living_Rooms` | Japandi_Minimalist 3, Modern 5, Boho_Colorful 1 | - |
| `005_Ratio_11x14` | `001_Living_Rooms` | Modern 1, Boho_Colorful 2 (Japandi_Minimalist empty) | - |
| `005_Ratio_11x14` | `002_Bedroom` / `004_Kitchen_Bar` | (no style folders) | 1 / 1 |

- Pick the ratio folder by the art slot's **nearest standard ratio** (SO ratio column), not the exact slot ratio. 5x7 (0.714) and ISO (0.707) share `001_Ratio_ISO`; 11x14 (0.786) goes to `005_Ratio_11x14`, 4x5 (0.800) to `004_Ratio_4x5`.
- Room type = what the room actually looks like = the level-2 folder. Decor style = the level-3 folder when the template sits in one (chosen by looking at the preview); templates whose look fits no existing style folder sit directly in the room folder and get their style from the `Style` column / name. Agents never create style or room folders; Tony does. File names keep old ratio tags (`Game_Room_ISO.psd` is a 2x3 slot); trust the folder and the table, not the name.
- **ARCHIVED 2026-11-10 (Tony dropped the computed-frame + wall-colour approach):** the Teak Sideboard (AI-built, mid-century modern) now lives at `Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/002_Modern/Archive/Teak_Sideboard/` and is never scanned, picked or checked (Archive is skipped everywhere; `room_templates.rooms()` ignores room.json files inside Archive). Its `Scripts/kie_edit.py` was copied to `../Portal/app/kie_edit.py`, which the Portal now uses. The text below describes it as it was (art slot 0.664-0.673 = 2x3). Its own layout: `room.json` (manifest the Portal reads, any depth; all paths inside are relative), `PSD_Templates/` (current v3 PSD + template json per light; `PSD_Templates/Archive/` = older PSDs + jsons, reasons in `room.json` `retired_lights`), `Caches/` (layer exports made on first render, safe to regenerate; `cache_dir` in room.json; `Caches/Archive/` = exports of older PSDs), `Plates_And_Masks/` (the 4 clean v3 plates + lamp-free wall mask; `Archive/` = raw, lamp and edit intermediates), `Light_Prompts/`, `Scripts/` (`build_template_v2.py` + `build_template.py`, `kie_edit.py`, `remove_object.py`, `quads.py`, `soften_light.py`, `guard.py`, `render_v2.py`).
- 2026-11-08 re-file: a duplicate tree (`01_Ratio_2x3`, `02_Ratio_3x4`, `03_Ratio_4x5`, `04_Ratio_5x7` with `Living_Room`/`Bedroom`/`Bar_Or_Kitchen`/`Game_Room`) had been created by an agent; all its template folders were moved (mv, intact with PSD, previews and `Archive/`) into the matching master folders (2x3 -> 002, 3x4 -> 003, 4x5 -> 004 or 005 when nearest 11x14, 5x7 -> 001_Ratio_ISO; Living_Room -> 001_Living_Rooms, Bedroom -> 002_Bedroom, Bar_Or_Kitchen -> 004_Kitchen_Bar, Game_Room -> 006_GameRooms_Mancave). The emptied duplicate folders are left for Tony to delete (agents cannot delete); the Templates tab and `--gaps` list them under "empty folders outside the NNN_ layout".
- `05_Ratio_Other/` (All_Ratios_MASTER guide, Untemplated_Scenes, Early_AI_Drafts) was no longer in the workspace at the 2026-11-08 re-file (not moved by the agent); its catalogue row is kept below as a note only.

## Template checker + Templates tab tools (built 2026-11-10)

- **Checker** (`../Portal/app/template_checker.py`, spec `../Mockup_Docs/Template_Layer_Rules_And_Checker_Spec.md`): headless and READ-ONLY (renders with `photocraft-cli run ... --out <temp png>`, PSD size + mtime compared before/after). Checks: opening vs art (3 px), black/white card, overlay spill outside the opening, overlay purity (neutral black fill; layers named `Scene Light & Shadow` / `Frame Edge Shadow` made by the 2026-11-08 script count as photo-built until a template.json has `layers_verified`), sun angle (3 deg), ratio (3%) + smart-object stretch, mat uniformity + bevel, layer names (`Place Artwork Here`, SHADOWS, GLARE, no hidden OLD layers). Run: `cd ../Portal && python3 -m app.template_checker --all` (or `--fails`). Results: `../Portal/config/template_checks.json`, shown as PASS/FAIL badges with reasons on the Templates tab ("Run the checker on all", per-card "Check again"). Production never auto-picks a FAIL template ("+" still can).
- First run 2026-11-10 on the 43 templates: **1 PASS** (BDRM_Wabi_Vertical, Tony's hand-verified known PASS: opening 1058,162,542x740, sun line 21-22 deg), **42 FAIL**.
- Re-run 2026-11-11 with the SAM precision checker (sub-pixel visible art, SAM 2 opening on 18 templates, old edge search on 25: mats, SAM loud failures, Wabi excluded; sun line only on SAM's wall mask): still **1 PASS / 42 FAIL**. Changes: opening fail->pass 3 (Japandi_Simple, Victorian_Floor, BDRM_Japandi_Beige), pass->fail 3 (Boho_Neautral, Gray_Japandi_4x5, BDRM-MidCentury); card pass->fail 5 (SAM's true opening shows slivers/over-frame the old edge search hid); ratio fail->pass 3, pass->fail 2; sun fail->skip 4 (prop edges no longer taken for sun lines), pass->fail 1 (Trendy_Girl_4x5). Most FAILs remain the 2026-11-08 photo-pixel shadow layers (purity 33). Counts per check: purity 33, card 22, opening 20, layer names 14, ratio 10, overlay spill 10, mat 10, sun 9. Nothing was changed; fixes follow the spec rules after Tony reviews the list.
- Findings: photocraft-cli renders ignore clipping masks (a clipped shadow spills outside the art; use a layer mask/alpha). Wabi's template.json `so_px` 542x740 is not the smart object's native 562x750; the Portal now always reads the native size from the PSD.
- **Fit rule** (Tony 2026-11-10): the art is cover-fit to the smart object's native pixels, centred, excess clipped; never stretched, never a white border; more than 3% crop is refused (`scene_templates.fit_cover`). New AI scenes whose insert is >3% off the print ratio are rejected (regenerate), never padded with a mat.
- **New AI template shadows**: `SHADOWS > Light Shadow` (black fill on the shade side of the wall's measured sun line, or a black gradient along the measured light falloff of the blank insert; ~17%) + `Frame Edge Shadow` (black lip falloff, ~30%), both limited to the opening; `GLARE > Glass Sheen`. No photo pixels are copied.
- **Build this** (gap tiles): one click (~18 credits, Nano Banana Pro) builds a new AI template straight INTO that empty folder (`AI_<Room>_<Decor>_<stamp>_Template.psd`, `_Scene.png`, `template.json` with `approved: false`), runs the checker, and shows Approve / Deny; Deny moves the files to that folder's `Archive/` and the folder is a gap again. Code: `../Portal/app/template_build.py`.
- **Missing room folders**: Entryway and Laundry have no folders. The tab lists the literal proposed paths (`<NNN_Ratio>/009_Entryway/`, `<NNN_Ratio>/010_Laundry/`; 009/010 because ISO already uses 007/008) and creates one only when Tony clicks Approve on that exact path. None created yet.
- **Edit with chat** (three-dots menu): works on a copy (`../Portal/data/rooms/Edit_<key>_vN.psd`); chat lines become allow-listed layer edits (show/hide, opacity, blend, rename, move, blur, art corners, retire = hide + "OLD ... (retire)", spot-heal at a clicked point); a real pixel change is an image-edit call (~18 credits, shown first, run only on Confirm). Save moves the old PSD to the template folder's `Archive/<name>_before_edit_<stamp>.psd` and re-checks. **Open in PhotoCraft** launches the app on control port 47811 with a token file in `../Portal/data/rooms/` and selects the named layer. Code: `../Portal/app/template_edit.py`.
- **Two-image template retired** (2026-11-10, Tony): `002_Ratio_2x3/001_Living_Rooms/002_Modern/LVRM_Midcentury_Walnut_2x3/` PSD, preview and template.json moved into that folder's own `Archive/` (kept for later 2/3-image sets).

## Production tab room images + AI scene templates (built 2026-11-08, Tony's recipe; slots and fit updated 2026-11-10 above)

Room slots (now 3 and 9-19) are made one card at a time in the Portal **Production** tab (`../Portal/app/production.py`), not by Run mockups (that button is gone; `mockup_rooms` stays false). Per card the source is a matching library template not used yet in that listing (free), else a NEW AI scene; the "+" on a card picks any template here.
- **AI scene recipe** (`../Portal/app/scene_templates.py`, replaces computed frames): Nano Banana Pro (`room_scene_engine` nbpro, 2K, 4:3; nb21 also works; GPT Image 2.5 on kie.ai needs a reference image) draws a whole room with ONE frame holding a BLANK WHITE insert (prompt: `room_slots.scene_prompt`, Tony's Midjourney structure, art never in it) through `kie_edit.generate()` (`../Portal/app/kie_edit.py` since 2026-11-10; was in `Teak_Sideboard/Scripts/kie_edit.py`. The insert's corners are found automatically (bright, neutral, smooth four-sided paper inside a darker frame; true width:height from the perspective). If the drawn insert is not the print's ratio the art sits inside it at the exact ratio (the rest reads as a white mat); never cropped, never stretched.
- **PSD layers** (PhotoCraft, hand-editable): `GLARE > Glass Sheen` (Screen 8%), `SHADOWS > Key Light Shadow` (Multiply: the light that fell on the blank paper, so the real key light crosses the print; `Mat Bevel Shadow` too in mat mode), `Place Artwork Here` (smart object on the corners), `BASE (room photo)`.
- **Auto-save**: every generated scene becomes a template at `Portrait_Templates/<NNN_Ratio>/<NNN_Room>/<NNN_Style>/AI_<Room>_<Decor>_<date_time>/` with `<name>_Template.psd`, `<name>_Scene.png` (source) and `template.json` (prompt, model, credits, quads, mode, made-for slot). A style folder is created (next free NNN_) only when a template first lands in that cell; ratio and room folders are never created (a card for a room with no folder says so, e.g. Entryway, Laundry). Denying a card's image moves its new template into that style folder's `Archive/` (Undo / Approve moves it back).
- **template.json for Tony's 43 PSDs** (written 2026-11-08 by `cd ../Portal && python3 -m app.scene_templates --manifests`): smart-object px, visible art quad (black vs white card render diff), room, decor, ratio. Lets the cards and the "+" picker render any template with the same full-art fit (contain; up to 1% absorbed, more padded with paper white) and the accuracy guard (`room_templates.guard_quad`: hue for all; shadow cover only for AI scenes, measured on the blank insert). The Teak Sideboard (room.json) is never picked automatically; it renders only when picked with "+".
- **Ratio per slot**: weights in `../Portal/config/settings.json` `room_ratio_weights` (2x3 35, 3x4 25, 4x5 25, ISO/5x7 10, 11x14 5), only ratios with a folder for that room.
- First live AI template (smoke test, 18 credits): `003_Ratio_3x4/002_Bedroom/001_Modern/AI_Bedroom_Modern_20261108_230611/` (Book Club Cat slot 10; the model drew a 2:3 insert, so the 3x4 art sits in a white mat; a second frame edge shows at the far right, for Tony to judge). Its style folder `001_Modern` was created by the rule above.

## Standing rule: Archive folders (Tony, 2026-11-08)

- In any template folder (and its sub-folders), anything NOT approved (old, superseded or rejected PSDs, JSONs, plates, versions, `Original_` backups) goes into a sub-folder named `Archive` inside that same folder. Scrolling a folder then shows only usable, approved files; `Archive` = do not use, but kept. Tony approves creating `Archive` folders wherever needed.
- Nothing in an `Archive` folder is used for production: `room.json` points only at `PSD_Templates/`, the Portal ignores `Archive` (Templates tab shows only a count), and an `Archive` folder is never read as a gap.
- Left for Tony to delete: the emptied `Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/002_Modern/Archive/Teak_Sideboard/Retired/` (moved with the Teak archive 2026-11-10) (its contents went to `PSD_Templates/Archive/`).

## Standing rule: the folder tree IS the build plan (Tony, 2026-11-08)

- Tony creates folders (ratio / room type / and any deeper style level, e.g. `001_Ratio_ISO/002_Bedroom/001_Japandi/`) knowing a mockup is needed there. **An EMPTY template folder (no PSD) is a missing template that must be built.** Building those to fill the library is the priority for future template work.
- Never treat an empty folder as clutter; never remove or rename Tony's empty folders.
- Before building any template, scan for empty leaf folders and build to fill them, preferring the popular ratios (picker weighting below):
  `cd 005_Ecommerce/Etsy-Ikigai/Portal && python3 -m app.template_gallery --gaps`
  It lists the gaps (every empty leaf folder in the `NNN_` tree, at its real depth: ratio / room / style) and, separately, empty folders outside the `NNN_` layout (Tony may delete those).
- Code must handle any depth: `NNN_Ratio/NNN_Room/[NNN_Style/...]/Template/`. `room_templates.py` finds every `room.json` at any depth; `template_gallery.py` reads the style from any level between room type and template folder.

## Templates tab (Portal, read-only)

`http://127.0.0.1:8800/` -> **Templates**. Grouped by ROOM TYPE (one section each). Each card shows the template rendered with a neutral test card, cropped **4:3 landscape centred on the art** (the shape Etsy shows listing thumbnails in search and shop grids; assumed, because `../Rules_And_Policies/Etsy_Rules_Bible.md` and `../Mockup_Docs/Mockup_Style_Guide.md` do not state a thumbnail crop), plus two clickable chips: **Style** (e.g. Japandi) and **Ratio** (e.g. 5x7 / ISO), so a card reads "Japandi · 5x7 / ISO" inside Living Room. Chips filter by style or ratio; click the image to enlarge.
- **Shop styles (style assignment).** The style options are the style/theme sections of Tony's Ikigai Etsy shop (IkigaiDigitalStudio, shop 48637917, fetched 2026-11-08 with Etsy API v3 getShopSections), labels without the "Art Prints - " prefix: Trendy, Abstract, Animals, Botanical, Food-Drink, Game Room, Japan Art, Mid Century, Minimalism, Nature, Nursery, Retro, Travel, Typography, Vintage, Beach Ocean (from "Photos - Beach Ocean"). Left out (not a look): Art Prints - Originals and Art Prints - Reimagined (provenance), Photos - Travel (medium; Travel already covered), Frame TV Art (product format). Click **Styles** on a card to pick one or more; manual choices always win. Without a manual choice the Portal guesses 1-3 styles from the thumbnail (Gemini `gemini-3.5-flash-lite`, about 1,200 tokens per image, classified once per thumbnail) and shows them as dashed amber chips with one-click **confirm**; **back to auto** drops a manual choice.
- File: `../Portal/config/template_styles.json` (one file: `vocabulary`, the full `shop.all_sections` list, `excluded`, `manual` {template path: [styles]}, `auto` {template path: {styles, key, model, tokens}}). Code: `../Portal/app/template_styles.py`. Re-fetch the sections when Tony changes them in the shop.
- The room's decor style (Japandi, Boho, Modern ...) is a separate grey chip; it comes from the folder level, the `Style` column below, or the name. Empty template folders show as dashed **gap** cards with the same chips, and the header shows the Library gaps count.
- Style = the folder level if one exists, else the `Style` column below, else a keyword in the template name / description (Japandi, Wabi, Boho, Mid-century, Victorian, Trendy, Moody, Modern ...), else "Unstyled". No folders are created for it.
- Thumbnails are cached in `../Portal/data/rooms/Gallery_*.jpg` (git-ignored), keyed by path + PSD size + date, so an edited PSD re-renders on the next visit. `python3 -m app.template_gallery --build` renders them all now.

## Picker weighting (proposed starting weight, adjustable; not wired yet)

Buyers print living-room/bedroom art mostly at 2x3, then 3x4, then 4x5, then 5x7; ISO/A-series and 11x14 least. When Run mockups chooses templates/ratios for a listing, weight by bucket:

| Bucket (nearest standard) | Folder | Weight | Templates now |
|---|---|---|---|
| 2x3 (0.667) | `002_Ratio_2x3` | 35% | 8 portrait (the 4 Teak Sideboard lights archived 2026-11-10; `LVRM_Midcentury_Sideboard_2x3` added 2026-11-11 in `002_Modern/LVRM_Midcentury_Walnut_2x3/` with Tony's approval) |
| 3x4 (0.750) | `003_Ratio_3x4` | 25% | 11 |
| 4x5 (0.800) | `004_Ratio_4x5` | 25% | 9 |
| 11x14 (0.786) | `005_Ratio_11x14` | 5% | 5 |
| 5x7 (0.714) | `001_Ratio_ISO` | 10% | 11 (shared ISO/5x7 bucket) |
| ISO / A-series (0.707) | `001_Ratio_ISO` | 5% | (same 11) |

Templates whose slot sits closer to 0.714 than 0.707 (true 5x7): Modern_Moody_Beige 0.715, LVRM_Modern_Blue_2x3_Template 0.715, LVRM_Modern_BLue_ISO_Template 0.716, LVRM_Boho_Neautral_ISO_Template 0.718, LVRM_Modern_Leather_4x5_Template 0.721. The library is still thin on 2x3 against a 35% weight; more 2x3 rooms are the top gap.

## How to use a template (headless)

- Art layer: always `Place Artwork Here` (smart object). `photocraft-cli run <psd> --cmd layer.select --params '{"name":"Place Artwork Here"}' --cmd layer.smartObjects.replaceContents --params '{"path":"<art.png>"}' --out out.png`.
- `replaceContents` does NOT scale: pre-fit (cover-crop) the art to the smart object's native px (column "SO px").
- "SO ratio" = smart object w/h (what the art is fitted to; buckets use this). "Visible ratio" = the art area actually seen after mats/frames, measured by rendering black vs white art and diffing. They differ where Tony's mat layers overlap the art (Walnut_Beige 0.698, Beige_4x5 0.785, Walnut_Modern 0.810) or the frame is in perspective (Cradenza 0.532, foreshortened).
- Teak Sideboard PSDs also have `Place Artwork Here (Mat)`, frame layers `Frame Oak/Walnut/Black/White`, `MAT`, `WALL COLOUR` and `GLASS`; the Portal switches them (`room_templates.py`).
- Verified 2026-11-08: all 48 templates rendered headless with a test card through `replaceContents` on `Place Artwork Here`.

## Catalogue

The tables below are machine-read by the Templates tab (matched by PSD file name): keep the column layout when adding rows. `Room type` = the room folder without its number; `Style` is optional (the style folder level wins).

### Teak Sideboard (ARCHIVED 2026-11-10; paths below are the old ones, now under `002_Modern/Archive/Teak_Sideboard/`)

Active looks (v3, 2026-11-08: lamp-free, plain book spines, one door pull, stepped 3D frame moulding with contact shadow). Plate made with GPT Image 2 (persona "bookish_renter"), lights relit with image edits; see `../Mockup_Docs/Mockup_Style_Guide.md`.

| Template (path in Room_Templates) | Room type | Style | SO px | SO ratio | Visible ratio | Nearest standard | Bucket | Room / look | Status | Toggle / extra layers |
|---|---|---|---|---|---|---|---|---|---|---|
| `Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/002_Modern/Teak_Sideboard/PSD_Templates/Room_Template_window_soft_v3.psd` | Living_Rooms | Mid_Century | 1601x2400 | 0.667 | 0.667 | 2x3 | 2x3 | Bookish renter: teak sideboard, books, greige wall, soft window-pane light (rank 1) | ready (wired) | frames Oak/Walnut/Black/White, MAT, WALL COLOUR (any paint), GLASS, contact shadow |
| `Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/002_Modern/Teak_Sideboard/PSD_Templates/Room_Template_leaf_dapple_across_v3.psd` | Living_Rooms | Mid_Century | 1594x2400 | 0.664 | 0.664 | 2x3 | 2x3 | Teak sideboard room, tree-leaf dapple across wall and art (rank 2) | ready (wired) | same as above; guard shadow limit 60% |
| `Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/002_Modern/Teak_Sideboard/PSD_Templates/Room_Template_golden_bars_v3.psd` | Living_Rooms | Mid_Century | 1615x2400 | 0.673 | 0.673 | 2x3 | 2x3 | Teak sideboard room, golden-hour window bars (rank 3) | ready (wired) | same as above |
| `Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/002_Modern/Teak_Sideboard/PSD_Templates/Room_Template_soft_v3.psd` | Living_Rooms | Mid_Century | 1600x2400 | 0.667 | 0.667 | 2x3 | 2x3 | Teak sideboard room, soft cast shadow (rank 4) | ready (wired) | same as above + `Soft cast shadow` |

### Portrait templates (Tony's own PSDs, 44)

A COPY of Tony's Photoshop portrait room mockups; the originals live in iCloud (`.../002-Mockups/002-Ikigai/001-Wall Art Mockups/Room Mockups/Portrait`) and were never touched. Standardised 2026-11-08: every template has exactly one art smart object named `Place Artwork Here` (All_Ratios_MASTER has extra slots), shape slots were converted, 19 flat scene PNGs were turned into layered templates. Status: **ready (renamed)** = Tony's PSD, art SO renamed only; **ready (shape converted)** = `Rectangle 1` shape turned into a smart object + new SHADOWS/GLARE groups; **made-from-PNG** = new `<Scene>_Template.psd` built from a flat scene (the scene PNG sits beside it); **ready (guide)** = the All Ratios master. Every PSD that was modified has its untouched backup in the `Archive/` sub-folder of its template folder as `Original_<name>.psd`. Styles of Tony's own PSDs come from his original style folders (Japandi_Minimalist, Modern, Boho_Colorful, Food_and_Drink, Gamer).

| Template (path in Room_Templates) | Room type | Style | SO px | SO ratio | Visible ratio | Nearest standard | Bucket | Room / look | Status | Toggle / extra layers |
|---|---|---|---|---|---|---|---|---|---|---|
| `Portrait_Templates/002_Ratio_2x3/004_Kitchen_Bar/003_BC_White_Bar_Cart/003_BC_White_Bar_Cart.psd` | Kitchen_Bar | Food_and_Drink | 734x1099 | 0.668 | 0.670 | 2x3 | 2x3 | White panelled wall, black bar cart, pampas | ready (renamed) | `Reflection`, `Soft Shadow`, `Hard Edge Shadow`, 3 adjustments |
| `Portrait_Templates/002_Ratio_2x3/002_Bedroom/BDRM_Girl_Pink_Modern_2x3/BDRM_Girl_Pink_Modern_2x3_Template.psd` | Bedroom | Trendy | 620x921 | 0.673 | 0.672 | 2x3 | 2x3 | Dusty-pink bedroom, pink nightstand, sun streaks | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/002_Ratio_2x3/006_GameRooms_Mancave/Game_Room_ISO/Game_Room_ISO.psd` | GameRooms_Mancave | Gamer | 423x671 | 0.630 | 0.656 | 2x3 | 2x3 | Warm attic gaming room, monitors, LED glow | ready (renamed) | `Brightness/Contrast 1` |
| `Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/003_Boho_Colorful/002_TealTiki_LVRM_ISO/002_TealTiki_LVRM_ISO.psd` | Living_Rooms | Boho | 591x861 | 0.686 | 0.681 | 2x3 | 2x3 | Moody teal plaster wall, burnt-orange armchair, monstera | ready (renamed) | group `Shadows` (4 Multiply shadow layers) |
| `Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/001_Japandi_Minimalist/001_Walnut_LVRM_ISO/001_Walnut_LVRM_ISO.psd` | Living_Rooms | Japandi | 594x867 | 0.685 | 0.684 | 2x3 | 2x3 | Bright Japandi living room, grey sofa, walnut table, slat wall | ready (renamed) | none (frame/shadow baked; hidden leftover `Group 1`) |
| `Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/002_Modern/LVRM_Midcentury_Walnut_2x3/LVRM_Midcentury_Walnut_2x3.psd` | Living_Rooms | Mid_Century | 697x1071 | 0.651 | 0.651 | 2x3 | 2x3 | Sunny mid-century, two frames (right one is the slot; left keeps baked sample art) | ready (shape converted) | SHADOWS, GLARE |
| `Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/001_Japandi_Minimalist/LVRM_Minimal_ISO/LVRM_Minimal_ISO_Template.psd` | Living_Rooms | Minimal | 306x458 | 0.668 | 0.667 | 2x3 | 2x3 | Minimal warm living room, doorway, black mushroom lamp, hard sun | made-from-PNG | SHADOWS, GLARE (blank insert shows as mat) |
| `Portrait_Templates/003_Ratio_3x4/004_Kitchen_Bar/001_BC_Teal_Closeup/001_BC_Teal_Closeup.psd` | Kitchen_Bar | Food_and_Drink | 921x1200 | 0.767 | 0.769 | 3x4 | 3x4 | Teal wall bar close-up, wine glasses + bottle | ready (renamed) | none (art SO is Multiply over the scene) |
| `Portrait_Templates/003_Ratio_3x4/004_Kitchen_Bar/Barcart_Green_Gold_3x4/Barcart_Green_Gold_3x4.psd` | Kitchen_Bar | Food_and_Drink | 872x1139 | 0.766 | 0.765 | 3x4 | 3x4 | Dark-green hallway, gold bar cart, checker rug | ready (shape converted) | SHADOWS, GLARE |
| `Portrait_Templates/003_Ratio_3x4/002_Bedroom/BDRM_Japandi_Beige_4x5/BDRM_Japandi_Beige_4x5.psd` | Bedroom | Japandi | 497x660 | 0.753 | 0.752 | 3x4 | 3x4 | Japandi bedroom, oak frame, soft sun | ready (shape converted) | SHADOWS, GLARE |
| `Portrait_Templates/003_Ratio_3x4/002_Bedroom/BDRM_Girl_Pink_4x5/BDRM_Girl_Pink_4x5.psd` | Bedroom | Trendy | 613x814 | 0.753 | 0.753 | 3x4 | 3x4 | Pink bedroom, sun streaks | ready (shape converted) | SHADOWS, GLARE |
| `Portrait_Templates/003_Ratio_3x4/002_Bedroom/BDRM_Girl_Pink_Anime_4x5/BDRM_Girl_Pink_Anime_4x5.psd` | Bedroom | Trendy | 615x803 | 0.766 | 0.766 | 3x4 | 3x4 | Pink bedroom, sun streaks (anime set) | ready (shape converted) | SHADOWS, GLARE |
| `Portrait_Templates/003_Ratio_3x4/002_Bedroom/BDRM_Wabi_Vertical/BDRM_Wabi_Vertical_Template.psd` | Bedroom | Wabi_Sabi | 562x750 | 0.749 | 0.750 | 3x4 | 3x4 | Wabi-sabi neutral bedroom, linen bed, curtains, sun diagonal | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/003_Ratio_3x4/001_Living_Rooms/002_Modern/LVRM_Modern_Color_3x4/LVRM_Modern_Color_3x4.psd` | Living_Rooms | Modern | 790x1074 | 0.736 | 0.736 | 3x4 | 3x4 | Bright modern living room, cream tufted sofa, olive tree | ready (renamed) | `Reflection`, `Light Reflection`, `Exposure 1`, `Levels 1` |
| `Portrait_Templates/003_Ratio_3x4/001_Living_Rooms/002_Modern/LVRM_Walnut_Beige_3x4/LVRM_Walnut_Beige_3x4.psd` | Living_Rooms | Modern | 982x1330 | 0.738 | 0.698 | 3x4 | 3x4 | Japandi-modern, walnut shelf, tan leather chair | ready (renamed) | group `Picture Matte` (mat + `Matte Shadow`), group `Picture Glass` |
| `Portrait_Templates/003_Ratio_3x4/001_Living_Rooms/003_Boho_Colorful/LVRM_Trendy_Girl_5x7/LVRM_Trendy_Girl_5x7.psd` | Living_Rooms | Trendy | 539x725 | 0.743 | 0.744 | 3x4 | 3x4 | Same Parisian room, tighter crop | ready (shape converted) | SHADOWS, GLARE |
| `Portrait_Templates/003_Ratio_3x4/001_Living_Rooms/002_Modern/LVRM_Floor_ISO/LVRM_Floor_ISO_Template.psd` | Living_Rooms | Unstyled | 805x1087 | 0.741 | 0.744 | 3x4 | 3x4 | Large leaning floor frame, black lounge chair, sunny window | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/003_Ratio_3x4/001_Living_Rooms/001_Japandi_Minimalist/LVRM_Wabi_ISO/LVRM_Wabi_ISO_Template.psd` | Living_Rooms | Wabi_Sabi | 460x617 | 0.746 | 0.746 | 3x4 | 3x4 | Wabi-sabi loft, beams, brick, olive sofa, dried branches | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/005_Ratio_11x14/004_Kitchen_Bar/002_BC_Teal_ISO/002_BC_Teal_ISO.psd` | Kitchen_Bar | Food_and_Drink | 925x1198 | 0.772 | 0.770 | 11x14 | 4x5/11x14 | Wide teal hallway, pink-brass bar cart | ready (shape converted) | SHADOWS, GLARE |
| `Portrait_Templates/005_Ratio_11x14/002_Bedroom/BDRM-MidCentury_ISO/BDRM-MidCentury_ISO_Template.psd` | Bedroom | Mid_Century | 420x541 | 0.776 | 0.774 | 11x14 | 4x5/11x14 | Mid-century bedroom, cream wall, walnut nightstands, rust cushions | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/005_Ratio_11x14/001_Living_Rooms/003_Boho_Colorful/001_Colorful_LVRM_ISO/001_Colorful_LVRM_ISO.psd` | Living_Rooms | Boho | 621x790 | 0.786 | 0.775 | 11x14 | 4x5/11x14 | Colourful retro/boho living room, mustard sofa, turquoise arch | ready (renamed) | group `WITH MATTE BORDER` (mat + `Shadow Overlay`), `Picture Fame` (frame), group `Glass Reflection` (hidden) |
| `Portrait_Templates/005_Ratio_11x14/001_Living_Rooms/003_Boho_Colorful/LVRM_Colorful_3x4/LVRM_Colorful_3x4.psd` | Living_Rooms | Boho | 875x1134 | 0.772 | 0.757 | 11x14 | 4x5/11x14 | Saturated retro boho, coral brick + teal wall | ready (renamed) | `Picture Matte`, `Shadow`, `Glass Reflection`, `Levels 1` |
| `Portrait_Templates/004_Ratio_4x5/001_Living_Rooms/001_Japandi_Minimalist/LVRM_Gray_Japandi_4x5/LVRM_Gray_Japandi_4x5.psd` | Living_Rooms | Japandi | 1131x1367 | 0.827 | 0.826 | 4x5 | 4x5/11x14 | Calm grey-white Japandi living room | ready (renamed) | group `Glass Reflection` |
| `Portrait_Templates/004_Ratio_4x5/001_Living_Rooms/001_Japandi_Minimalist/LVRM_Japandi_Soft_Colors/LVRM_Japandi_Soft_Colors_Template.psd` | Living_Rooms | Japandi | 812x1015 | 0.800 | 0.801 | 4x5 | 4x5/11x14 | Bright Japandi living room, beams, terracotta cushions, plants | made-from-PNG | MAT, SHADOWS, GLARE |
| `Portrait_Templates/004_Ratio_4x5/001_Living_Rooms/001_Japandi_Minimalist/LVRM_Mint_Japandi_4x5/LVRM_Mint_Japandi_4x5.psd` | Living_Rooms | Japandi | 1302x1584 | 0.822 | 0.824 | 4x5 | 4x5/11x14 | Sage/mint wall, grey-green sofa, orange cushions | ready (renamed) | group `Glass Reflection`, `Blank Canvas` |
| `Portrait_Templates/004_Ratio_4x5/001_Living_Rooms/002_Modern/LVRM_Midcentury_Wood/LVRM_Midcentury_Wood_Template.psd` | Living_Rooms | Mid_Century | 441x551 | 0.800 | 0.799 | 4x5 | 4x5/11x14 | Mid-century living room, walnut side tables, lamps, sunny | made-from-PNG | MAT, SHADOWS, GLARE |
| `Portrait_Templates/004_Ratio_4x5/001_Living_Rooms/002_Modern/LVRM_Beige_4x5/LVRM_Beige_4x5.psd` | Living_Rooms | Modern | 451x534 | 0.845 | 0.785 | 4x5 | 4x5/11x14 | Dim beige living room, blind-stripe shadows | ready (renamed) | `Shadow Overlay` (Multiply), `Matte` |
| `Portrait_Templates/004_Ratio_4x5/001_Living_Rooms/002_Modern/LVRM_Modern_Nook_4x5/LVRM_Modern_Nook_4x5.psd` | Living_Rooms | Modern | 1275x1486 | 0.858 | 0.858 | 4x5 | 4x5/11x14 | Reading nook, wood frame + big mat, plant | ready (shape converted) | SHADOWS, GLARE, FOREGROUND (leaf over corner) |
| `Portrait_Templates/004_Ratio_4x5/001_Living_Rooms/002_Modern/LVRM_Modern_Walnut/LVRM_Modern_Walnut_Template.psd` | Living_Rooms | Modern | 823x1028 | 0.801 | 0.801 | 4x5 | 4x5/11x14 | Sunny mid-century living room, walnut shelves, pink chair | made-from-PNG | MAT, SHADOWS, GLARE |
| `Portrait_Templates/004_Ratio_4x5/001_Living_Rooms/002_Modern/LVRM_Walnut_Modern_4x5/LVRM_Walnut_Modern_4x5.psd` | Living_Rooms | Modern | 1123x1347 | 0.834 | 0.810 | 4x5 | 4x5/11x14 | Sunlit modern corner, leather chair, cactus | ready (renamed) | `Picture Matte`, group `Shadows` |
| `Portrait_Templates/005_Ratio_11x14/001_Living_Rooms/002_Modern/LVRM_Modern_Dark_4x5/LVRM_Modern_Dark_4x5_Template.psd` | Living_Rooms | Moody | 739x938 | 0.788 | 0.788 | 11x14 | 4x5/11x14 | Dark grey wall living room, cream sofa, teal/orange cushions, lamp | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/004_Ratio_4x5/001_Living_Rooms/003_Boho_Colorful/LVRM_Trendy_Girl_4x5/LVRM_Trendy_Girl_4x5.psd` | Living_Rooms | Trendy | 598x744 | 0.804 | 0.805 | 4x5 | 4x5/11x14 | Pink/mustard Parisian panelled living room | ready (shape converted) | SHADOWS, GLARE |
| `Portrait_Templates/001_Ratio_ISO/002_Bedroom/BDRM_Girl_Peach_Trendy_2x3/BDRM_Girl_Peach_Trendy_2x3.psd` | Bedroom | Trendy | 598x861 | 0.695 | 0.696 | ISO | ISO/5x7 | Dusty-pink teen bedroom, peach chair, retro radio | ready (shape converted) | SHADOWS, GLARE |
| `Portrait_Templates/001_Ratio_ISO/002_Bedroom/003_Neutral_Aesthetic/BDRM_Trendy_Nuetral_4x5/BDRM_Trendy_Nuetral_4x5_Template.psd` | Bedroom | Trendy | 362x516 | 0.702 | 0.703 | ISO | ISO/5x7 | Warm sunlit teen bedroom desk corner, oak frame + mat | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/001_Ratio_ISO/001_Living_Rooms/003_Boho_Colorful/LVRM_Boho_Neautral_ISO/LVRM_Boho_Neautral_ISO_Template.psd` | Living_Rooms | Boho | 869x1210 | 0.718 | 0.718 | 5x7 | ISO/5x7 | Soft boho-neutral living room, beige sofa, pendant, wall hoops | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/001_Ratio_ISO/001_Living_Rooms/001_Japandi_Minimalist/LVRM_Japandi_Simple_ISO/LVRM_Japandi_Simple_ISO_Template.psd` | Living_Rooms | Japandi | 442x625 | 0.707 | 0.707 | ISO | ISO/5x7 | Japandi living room, linen sofa, blossom branches, wood shelves | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/001_Ratio_ISO/001_Living_Rooms/002_Modern/LVRM_Modern_BLue_ISO/LVRM_Modern_BLue_ISO_Template.psd` | Living_Rooms | Modern | 486x679 | 0.716 | 0.716 | 5x7 | ISO/5x7 | Sky-blue wall living room, teal chesterfield, palms | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/001_Ratio_ISO/001_Living_Rooms/002_Modern/LVRM_Modern_Blue_2x3/LVRM_Modern_Blue_2x3_Template.psd` | Living_Rooms | Modern | 396x554 | 0.715 | 0.716 | 5x7 | ISO/5x7 | Teal-blue wall living room, teal sofa, pendant | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/001_Ratio_ISO/001_Living_Rooms/002_Modern/LVRM_Modern_Cradenza_Angled_ISO/LVRM_Modern_Cradenza_Angled_ISO_Template.psd` | Living_Rooms | Modern | 501x708 | 0.708 | 0.532 | ISO | ISO/5x7 | Angled view, walnut credenza, vases, big leaning frame, window light | made-from-PNG | SHADOWS, GLARE, FOREGROUND |
| `Portrait_Templates/001_Ratio_ISO/001_Living_Rooms/002_Modern/LVRM_Modern_Leather_4x5/LVRM_Modern_Leather_4x5_Template.psd` | Living_Rooms | Modern | 427x592 | 0.721 | 0.719 | 5x7 | ISO/5x7 | White wall, tan leather wingback chair, fiddle-leaf plant, black frame + mat | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/001_Ratio_ISO/001_Living_Rooms/002_Modern/LVRM_Modern_Walnut_5x7/LVRM_Modern_Walnut_5x7_Template.psd` | Living_Rooms | Modern | 728x1045 | 0.697 | 0.697 | ISO | ISO/5x7 | Walnut console, tan leather chair, tall windows, oak frame + mat | made-from-PNG | SHADOWS, GLARE |
| `Portrait_Templates/001_Ratio_ISO/001_Living_Rooms/002_Modern/Modern_Moody_Beige/Modern_Moody_Beige.psd` | Living_Rooms | Modern | 462x646 | 0.715 | 0.716 | 5x7 | ISO/5x7 | Moody warm-beige living room, tan sectional, striped sun | ready (renamed) | `Reflections` (SO, Multiply 79%) |
| `Portrait_Templates/001_Ratio_ISO/001_Living_Rooms/LVRM_Victorian_Floor_ISO/LVRM_Victorian_Floor_ISO_Template.psd` | Living_Rooms | Victorian | 204x296 | 0.689 | 0.686 | ISO | ISO/5x7 | Empty Victorian panelled room, gilt frame leaning on herringbone floor | made-from-PNG | SHADOWS, GLARE |

Not in the workspace since the 2026-11-08 re-file (was `Portrait_Templates/05_Ratio_Other/`): `All_Ratios_MASTER.psd` (five-frame gallery guide, 584x814 slot, 0.717, ready (guide, 5 slots)), `Untemplated_Scenes/` (3 multi-frame scene PNGs + `Early_AI_Drafts/`). Moved to `~/Desktop/Delete/` for Tony earlier: the 5 rejected `Unusable` scenes (now `Unusable_<name>`), `BDRM_Purple_Desk_2x3.psd` + preview and `Duplicate_Copy_All_Ratios_MASTER.psd`.

## Library gaps (empty template folders = templates to build)

Run `python3 -m app.template_gallery --gaps` (from `Portal/`) for the live list; the Templates tab shows them as gap cards at their real depth. On 2026-11-08 after the re-file: 30 gaps, all Tony's empty master folders: ISO Bedroom Japandi / Scandinavian; ISO Bathroom Minimal / Monochrome / Botanical; ISO Kitchen_Bar Food_and_Drink / Retro_Kitchen / Rustic_Farmhouse; ISO Office Modern / Neutral_Workspace / Motivational; ISO GameRooms Gamer / Retro_Arcade / Mancave; ISO Creative_Space and Kids_Nursery; 11x14 Living Rooms Japandi_Minimalist; Bathroom and Office in 2x3, 3x4, 4x5, 11x14; GameRooms in 3x4, 4x5, 11x14; 4x5 Bedroom and Kitchen_Bar.

## Layer structure of the portrait templates (what to edit by hand)

**Made-from-PNG (`*_Template.psd`, 19)**, top to bottom:
- `FOREGROUND` > `Foreground Plant (in front of frame)` (only Cradenza): cut-out of the plant/vase pixels that overlap the frame, so the art sits behind them.
- `GLARE` > `Glass Sheen` (Screen, 12%): soft diagonal glass reflection. Raise/lower opacity or hide.
- `SHADOWS` > `Mat Bevel Shadow` (Multiply, mat-mode only), `Frame Edge Shadow` (Multiply), `Scene Light & Shadow` (Multiply): the room's own light on the art. For blank-frame scenes it is the blank insert from the photo (text/marks inpainted); for scenes that had sample art it is rebuilt from the mat/paper/wall around the art, so window stripes and falloff carry across the print.
- `Place Artwork Here` (smart object, Normal, set to the frame's corner quad; double-click to replace).
- `MAT` > `Paper (covers old sample art)` (mat-mode art scenes only: Japandi_Soft_Colors, Midcentury_Wood, Modern_Walnut): flat paper fill hiding the old sample print so a 4x5 slot can sit inside a squarer frame with a mat border.
- `BASE (room photo)`: the untouched scene. Retouch it freely; nothing is baked into it.
- Mat-mode scenes (art smaller than the frame opening, centred with a paper border): Japandi_Soft_Colors, Midcentury_Wood, Modern_Walnut (4x5 inside a squarer frame) and Minimal_ISO (2x3 inside a very tall frame; the blank insert itself is the border).

**Shape converted (10)**: `Background` (or the full-canvas scene smart object in the three BDRM_Girl PSDs) unchanged; `Place Artwork Here` (smart object, Normal, same bounds as the old `Rectangle 1`, holds a grey grid placeholder that hides the old sample art); `SHADOWS` (`Scene Light & Shadow`, `Frame Edge Shadow`, Multiply); `GLARE` (`Glass Sheen`, Screen 12%); `FOREGROUND` (Nook only: leaf over the bottom-right corner).

**Renamed (14)**: Tony's own layer stack unchanged except the art layer name. Removed from the copies (backups keep them): `001_Walnut_LVRM_ISO` hidden leftover smart object `Screenshot 2024-12-22 ...`; `001_Colorful_LVRM_ISO` hidden alternate slot `PLACE IMAGE HERE` (no-mat variant); `LVRM_Walnut_Beige_3x4` top-level duplicate `PLACE IMAGE HERE`. The Walnut_Beige pair were two instances of ONE smart object at identical bounds (replacing either changed both, hiding either changed nothing), so the one kept is the copy inside group `Picture Matte`, which carries the mat and matte shadow.

**All_Ratios_MASTER**: the five shape slots in `PLACE IMAGES INSIDE HERE` are now smart objects: `Place Artwork Here` (the ISO frame) plus `Extra Art 2x3`, `Extra Art 4x5`, `Extra Art 11x14`, `Extra Art 3x4`. This is a five-frame guide, so it is the one template with more than one art smart object; only `Place Artwork Here` is touched by the standard recipe. Tony's mats, frames, frame shadows and reflections sit above them and apply as before (the ISO mat window shows 0.584 of the slot).

Nothing was flattened or merged. New shadow/glare layers are pixel layers (generated images with blend modes), not adjustment layers, because they carry per-pixel light from the photo. The paper fill is a pixel layer rather than a solid-colour fill layer (headless PhotoCraft cannot mask a fill layer to a quad).

## History: 2026-11-08 standardisation renames and moves (paths at that time; superseded by the re-file above)

Leading-space file names (rule E):
- `003_Ratio_3x4/001_Living_Rooms/002_Modern/ LVRM_Modern_Color_3x4.psd` -> `LVRM_Modern_Color_3x4.psd`
- `004_Ratio_4x5/001_Living_Rooms/001_Japandi_Minimalist/LVRM_ Gray_Japandi_4x5.psd` -> `LVRM_Gray_Japandi_4x5.psd`
- `004_Ratio_4x5/001_Living_Rooms/001_Japandi_Minimalist/LVRM_ Mint_Japandi_4x5.psd` -> `LVRM_Mint_Japandi_4x5.psd`
- `004_Ratio_4x5/001_Living_Rooms/002_Modern/LVRM_ Walnut_Modern_4x5.psd` -> `LVRM_Walnut_Modern_4x5.psd`
- Their previews in `007_For_Use/Templated/` likewise: ` LVRM_Modern_Color_3x4.png`, `LVRM_ Gray_Japandi_4x5.png`, `LVRM_ Mint_Japandi_4x5.png`, `LVRM_ Walnut_Modern_4x5.png` -> same names without the space.
- `006_Ratio_All_Ratios/All Ratios MASTER.psd` -> `All_Ratios_MASTER.psd` (backup `Original_All_Ratios_MASTER.psd`).

Misfiled by measured SO ratio, moved to the nearest-ratio folder (with their `Original_` backups):
- `001_Ratio_ISO/001_Living_Rooms/001_Japandi_Minimalist/001_Walnut_LVRM_ISO.psd` (0.685) -> `002_Ratio_2x3/001_Living_Rooms/001_Japandi_Minimalist/`
- `001_Ratio_ISO/001_Living_Rooms/003_Boho_Colorful/002_TealTiki_LVRM_ISO.psd` (0.686, borderline: 2x3 by 0.002) -> `002_Ratio_2x3/001_Living_Rooms/003_Boho_Colorful/`
- `001_Ratio_ISO/001_Living_Rooms/003_Boho_Colorful/001_Colorful_LVRM_ISO.psd` (0.786) -> `005_Ratio_11x14/001_Living_Rooms/003_Boho_Colorful/`
- `001_Ratio_ISO/004_Kitchen_Bar/001_Food_and_Drink/001_BC_Teal_Closeup.psd` (0.767) -> `003_Ratio_3x4/004_Kitchen_Bar/`
- `001_Ratio_ISO/004_Kitchen_Bar/001_Food_and_Drink/002_BC_Teal_ISO.psd` (0.772) -> `005_Ratio_11x14/004_Kitchen_Bar/`
- `001_Ratio_ISO/004_Kitchen_Bar/001_Food_and_Drink/003_BC_White_Bar_Cart.psd` (0.668) -> `002_Ratio_2x3/004_Kitchen_Bar/`
- `001_Ratio_ISO/006_GameRooms_Mancave/001_Gamer/Game_Room_ISO.psd` (0.630) -> `002_Ratio_2x3/006_GameRooms_Mancave/`
- `003_Ratio_3x4/001_Living_Rooms/003_Boho_Colorful/LVRM_Colorful_3x4.psd` (0.772) -> `005_Ratio_11x14/001_Living_Rooms/003_Boho_Colorful/`

File names keep their old ratio tags (e.g. `Game_Room_ISO.psd` now lives in 2x3); trust the folder and this table, not the name. Later the same day an agent re-filed everything into a duplicate `<NN_Ratio>/<Room_Type>/<Template>/` tree; that was reversed into Tony's `NNN_` master tree (the Catalogue paths above are current).

## Notes from the standardisation (old layout names)

- `007_For_Use/Templated/`: flattened previews of the PSDs (not templates). `Multiple_Frames/`: 3 multi-frame scene PNGs (not templated) + the Midcentury_Walnut PSD. `Unusable/`: 5 scenes Tony rejected (left as is). `untitled folder/`: 9 early AI drafts (unreviewed, left as is).
- Flat scenes kept as sources next to their new templates; `LVRM_Modern_Nook_4x5.png` is a 4096 px copy of the Leather scene (templated once, as `LVRM_Modern_Leather_4x5_Template.psd`); `LVRM_Modern_ISO_Moody_Beige.png` is the preview of `Modern_Moody_Beige.psd`.
- Sample art with illustrated faces (Girl PSDs, Trendy_Girl, BC_Teal_Closeup, BC_White_Bar_Cart) is now hidden under the placeholder or replaced art; only Tony's original `Original_` backups still show it. `LVRM_Midcentury_Walnut_2x3` still shows a baked sample print in its LEFT frame (only the right frame is a slot).
- Image generation: none used (0 kie.ai credits).
- Authoring scripts (reference, ran from a scratch dir; now in `Portrait_Templates/Scripts/`): `lib.py` (quad maths, edge snapping, light/shadow layer builders), `build_layers.py`, `specs.py` (frame quads per PNG scene), `build_png.py`, `process_existing.py`, `rtest.py` + `testcard.py` (render/measure).
