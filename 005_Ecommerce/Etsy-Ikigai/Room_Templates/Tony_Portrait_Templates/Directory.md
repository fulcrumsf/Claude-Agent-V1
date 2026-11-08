# Tony_Portrait_Templates: Directory

Tony's own Photoshop room-mockup templates for portrait wall art. This folder is a COPY; the originals live in iCloud (`.../002-Mockups/002-Ikigai/001-Wall Art Mockups/Room Mockups/Portrait`) and were never touched. Standardised 2026-11-08 (Opus worker): every template now has exactly one art smart object named `Place Artwork Here`, shape slots were converted, 19 flat scene PNGs were turned into layered templates, misfiled ratios moved, unusable files moved to `~/Desktop/Delete/`. PSD/PNG are git-ignored; this file and the authoring scripts are committed.

## How to use (Portal / headless)

- Art layer: always `Place Artwork Here` (smart object). `photocraft-cli run <psd> --cmd layer.select --params '{"name":"Place Artwork Here"}' --cmd layer.smartObjects.replaceContents --params '{"path":"<art.png>"}' --out out.png`.
- `replaceContents` does NOT scale: pre-fit (cover-crop) the art to the smart object's native px (column "SO px").
- **Pick templates by nearest standard ratio, not by exact slot ratio.** Folder = closest standard ratio to the eye. Slots a little off the exact value (e.g. 4x5 slots at 0.82-0.86) are fine. 11x14 (0.786) and 4x5 (0.800) are one bucket; ISO/A-series (0.707) and 5x7 (0.714) are one bucket (the ISO folder is the 5x7 bucket).
- "SO ratio" = smart object w/h (what the art is fitted to; buckets use this). "Visible ratio" = the art area actually seen after mats/frames, measured by rendering black vs white art and diffing. They differ where Tony's mat layers overlap the art (Walnut_Beige 0.698, Beige_4x5 0.785, Walnut_Modern 0.810) or the frame is in perspective (Cradenza 0.532, foreshortened).
- Verified 2026-11-08: all 44 templates rendered headless with a test card through `replaceContents` on `Place Artwork Here`; art lands in the frame with visible shadows in every one. Contact sheets were written to the session scratchpad (not the repo).

## Picker weighting (proposed starting weight, adjustable; not wired yet)

Buyers print living-room/bedroom art mostly at 2x3, then 3x4, then 4x5, then 5x7; ISO/A-series and 11x14 least. When Run mockups chooses templates/ratios for a listing, weight by bucket:

| Bucket (nearest standard) | Weight | Ready templates now |
|---|---|---|
| 2x3 (0.667) | 35% | 7 |
| 3x4 (0.750) | 25% | 11 |
| 4x5 / 11x14 (0.800 / 0.786) | 25% | 14 |
| 5x7 (0.714) | 10% | 12 (shared ISO/5x7 bucket) |
| ISO / A-series (0.707) | 5% | (same 12) |

5x7 and ISO are served by the same templates. Templates whose slot sits closer to 0.714 than 0.707 (call them 5x7): Modern_Moody_Beige 0.715, LVRM_Modern_Blue_2x3_Template 0.715, LVRM_Modern_BLue_ISO_Template 0.716, LVRM_Boho_Neautral_ISO_Template 0.718, LVRM_Modern_Leather_4x5_Template 0.721, All_Ratios_MASTER 0.717. The library is thin on 2x3 against a 35% weight (7 templates); more 2x3 rooms are the top gap.

## Final table (44 templates)

Status: **ready (renamed)** = Tony's PSD, art SO renamed only; **ready (shape converted)** = `Rectangle 1` shape turned into a smart object + new SHADOWS/GLARE groups; **made-from-PNG** = new `<Scene>_Template.psd` built from a flat 007_For_Use scene; **ready (guide)** = the All Ratios master. Every PSD that was modified has its untouched backup beside it as `Original_<name>.psd` (Tony can drop those once happy).

| Template (path in this folder) | SO px | SO ratio | Visible ratio | Nearest standard | Bucket | Room / look | Status | Toggle / extra layers |
|---|---|---|---|---|---|---|---|---|
| `002_Ratio_2x3/001_Living_Rooms/001_Japandi_Minimalist/001_Walnut_LVRM_ISO.psd` | 594x867 | 0.685 | 0.684 | 2x3 | 2x3 | Bright Japandi living room, grey sofa, walnut table, slat wall | ready (renamed) | none (frame/shadow baked; hidden leftover `Group 1`) |
| `002_Ratio_2x3/001_Living_Rooms/003_Boho_Colorful/002_TealTiki_LVRM_ISO.psd` | 591x861 | 0.686 | 0.681 | 2x3 | 2x3 | Moody teal plaster wall, burnt-orange armchair, monstera | ready (renamed) | group `Shadows` (4 Multiply shadow layers) |
| `002_Ratio_2x3/004_Kitchen_Bar/003_BC_White_Bar_Cart.psd` | 734x1099 | 0.668 | 0.670 | 2x3 | 2x3 | White panelled wall, black bar cart, pampas | ready (renamed) | `Reflection`, `Soft Shadow`, `Hard Edge Shadow`, 3 adjustments |
| `007_For_Use/BDRM_Girl_Pink_Modern_2x3_Template.psd` | 620x921 | 0.673 | 0.672 | 2x3 | 2x3 | Dusty-pink bedroom, pink nightstand, sun streaks | made-from-PNG | SHADOWS, GLARE |
| `002_Ratio_2x3/006_GameRooms_Mancave/Game_Room_ISO.psd` | 423x671 | 0.630 | 0.656 | 2x3 | 2x3 | Warm attic gaming room, monitors, LED glow | ready (renamed) | `Brightness/Contrast 1` |
| `007_For_Use/Multiple_Frames/LVRM_Midcentury_Walnut_2x3.psd` | 697x1071 | 0.651 | 0.651 | 2x3 | 2x3 | Sunny mid-century, two frames (right one is the slot; left keeps baked sample art) | ready (shape converted) | SHADOWS, GLARE |
| `007_For_Use/LVRM_Minimal_ISO_Template.psd` | 306x458 | 0.668 | 0.667 | 2x3 | 2x3 | Minimal warm living room, doorway, black mushroom lamp, hard sun | made-from-PNG | SHADOWS, GLARE (blank insert shows as mat) |
| `003_Ratio_3x4/004_Kitchen_Bar/001_BC_Teal_Closeup.psd` | 921x1200 | 0.767 | 0.769 | 3x4 | 3x4 | Teal wall bar close-up, wine glasses + bottle | ready (renamed) | none (art SO is Multiply over the scene) |
| `007_For_Use/BDRM_Girl_Pink_4x5.psd` | 613x814 | 0.753 | 0.753 | 3x4 | 3x4 | Pink bedroom, sun streaks | ready (shape converted) | SHADOWS, GLARE |
| `007_For_Use/BDRM_Girl_Pink_Anime_4x5.psd` | 615x803 | 0.766 | 0.766 | 3x4 | 3x4 | Pink bedroom, sun streaks (anime set) | ready (shape converted) | SHADOWS, GLARE |
| `007_For_Use/BDRM_Japandi_Beige_4x5.psd` | 497x660 | 0.753 | 0.752 | 3x4 | 3x4 | Japandi bedroom, oak frame, soft sun | ready (shape converted) | SHADOWS, GLARE |
| `007_For_Use/BDRM_Wabi_Vertical_Template.psd` | 562x750 | 0.749 | 0.750 | 3x4 | 3x4 | Wabi-sabi neutral bedroom, linen bed, curtains, sun diagonal | made-from-PNG | SHADOWS, GLARE |
| `003_Ratio_3x4/004_Kitchen_Bar/Barcart_Green_Gold_3x4.psd` | 872x1139 | 0.766 | 0.765 | 3x4 | 3x4 | Dark-green hallway, gold bar cart, checker rug | ready (shape converted) | SHADOWS, GLARE |
| `007_For_Use/LVRM_Floor_ISO_Template.psd` | 805x1087 | 0.741 | 0.744 | 3x4 | 3x4 | Large leaning floor frame, black lounge chair, sunny window | made-from-PNG | SHADOWS, GLARE |
| `003_Ratio_3x4/001_Living_Rooms/002_Modern/LVRM_Modern_Color_3x4.psd` | 790x1074 | 0.736 | 0.736 | 3x4 | 3x4 | Bright modern living room, cream tufted sofa, olive tree | ready (renamed) | `Reflection`, `Light Reflection`, `Exposure 1`, `Levels 1` |
| `007_For_Use/LVRM_Trendy_Girl_5x7.psd` | 539x725 | 0.743 | 0.744 | 3x4 | 3x4 | Same Parisian room, tighter crop | ready (shape converted) | SHADOWS, GLARE |
| `007_For_Use/LVRM_Wabi_ISO_Template.psd` | 460x617 | 0.746 | 0.746 | 3x4 | 3x4 | Wabi-sabi loft, beams, brick, olive sofa, dried branches | made-from-PNG | SHADOWS, GLARE |
| `003_Ratio_3x4/001_Living_Rooms/002_Modern/LVRM_Walnut_Beige_3x4.psd` | 982x1330 | 0.738 | 0.698 | 3x4 | 3x4 | Japandi-modern, walnut shelf, tan leather chair | ready (renamed) | group `Picture Matte` (mat + `Matte Shadow`), group `Picture Glass` |
| `005_Ratio_11x14/001_Living_Rooms/003_Boho_Colorful/001_Colorful_LVRM_ISO.psd` | 621x790 | 0.786 | 0.775 | 11x14 | 4x5/11x14 | Colourful retro/boho living room, mustard sofa, turquoise arch | ready (renamed) | group `WITH MATTE BORDER` (mat + `Shadow Overlay`), `Picture Fame` (frame), group `Glass Reflection` (hidden) |
| `005_Ratio_11x14/004_Kitchen_Bar/002_BC_Teal_ISO.psd` | 925x1198 | 0.772 | 0.770 | 11x14 | 4x5/11x14 | Wide teal hallway, pink-brass bar cart | ready (shape converted) | SHADOWS, GLARE |
| `007_For_Use/BDRM-MidCentury_ISO_Template.psd` | 420x541 | 0.776 | 0.774 | 11x14 | 4x5/11x14 | Mid-century bedroom, cream wall, walnut nightstands, rust cushions | made-from-PNG | SHADOWS, GLARE |
| `004_Ratio_4x5/001_Living_Rooms/002_Modern/LVRM_Beige_4x5.psd` | 451x534 | 0.845 | 0.785 | 4x5 | 4x5/11x14 | Dim beige living room, blind-stripe shadows | ready (renamed) | `Shadow Overlay` (Multiply), `Matte` |
| `005_Ratio_11x14/001_Living_Rooms/003_Boho_Colorful/LVRM_Colorful_3x4.psd` | 875x1134 | 0.772 | 0.757 | 11x14 | 4x5/11x14 | Saturated retro boho, coral brick + teal wall | ready (renamed) | `Picture Matte`, `Shadow`, `Glass Reflection`, `Levels 1` |
| `004_Ratio_4x5/001_Living_Rooms/001_Japandi_Minimalist/LVRM_Gray_Japandi_4x5.psd` | 1131x1367 | 0.827 | 0.826 | 4x5 | 4x5/11x14 | Calm grey-white Japandi living room | ready (renamed) | group `Glass Reflection` |
| `007_For_Use/LVRM_Japandi_Soft_Colors_Template.psd` | 812x1015 | 0.800 | 0.801 | 4x5 | 4x5/11x14 | Bright Japandi living room, beams, terracotta cushions, plants | made-from-PNG | MAT, SHADOWS, GLARE |
| `007_For_Use/LVRM_Midcentury_Wood_Template.psd` | 441x551 | 0.800 | 0.799 | 4x5 | 4x5/11x14 | Mid-century living room, walnut side tables, lamps, sunny | made-from-PNG | MAT, SHADOWS, GLARE |
| `004_Ratio_4x5/001_Living_Rooms/001_Japandi_Minimalist/LVRM_Mint_Japandi_4x5.psd` | 1302x1584 | 0.822 | 0.824 | 4x5 | 4x5/11x14 | Sage/mint wall, grey-green sofa, orange cushions | ready (renamed) | group `Glass Reflection`, `Blank Canvas` |
| `007_For_Use/LVRM_Modern_Dark_4x5_Template.psd` | 739x938 | 0.788 | 0.788 | 11x14 | 4x5/11x14 | Dark grey wall living room, cream sofa, teal/orange cushions, lamp | made-from-PNG | SHADOWS, GLARE |
| `007_For_Use/LVRM_Modern_Nook_4x5.psd` | 1275x1486 | 0.858 | 0.858 | 4x5 | 4x5/11x14 | Reading nook, wood frame + big mat, plant | ready (shape converted) | SHADOWS, GLARE, FOREGROUND (leaf over corner) |
| `007_For_Use/LVRM_Modern_Walnut_Template.psd` | 823x1028 | 0.801 | 0.801 | 4x5 | 4x5/11x14 | Sunny mid-century living room, walnut shelves, pink chair | made-from-PNG | MAT, SHADOWS, GLARE |
| `007_For_Use/LVRM_Trendy_Girl_4x5.psd` | 598x744 | 0.804 | 0.805 | 4x5 | 4x5/11x14 | Pink/mustard Parisian panelled living room | ready (shape converted) | SHADOWS, GLARE |
| `004_Ratio_4x5/001_Living_Rooms/002_Modern/LVRM_Walnut_Modern_4x5.psd` | 1123x1347 | 0.834 | 0.810 | 4x5 | 4x5/11x14 | Sunlit modern corner, leather chair, cactus | ready (renamed) | `Picture Matte`, group `Shadows` |
| `006_Ratio_All_Ratios/All_Ratios_MASTER.psd` | 584x814 | 0.717 | 0.584 | 5x7 | ISO/5x7 | Five-frame gallery wall guide, mid-century room | ready (guide, 5 slots) | groups `Picture Mattes`, `Picture Frames` (+ shadows), `Reflections`; extra SOs `Extra Art 2x3/4x5/11x14/3x4` |
| `007_For_Use/BDRM_Girl_Peach_Trendy_2x3.psd` | 598x861 | 0.695 | 0.696 | ISO | ISO/5x7 | Dusty-pink teen bedroom, peach chair, retro radio | ready (shape converted) | SHADOWS, GLARE |
| `007_For_Use/BDRM_Trendy_Nuetral_4x5_Template.psd` | 362x516 | 0.702 | 0.703 | ISO | ISO/5x7 | Warm sunlit teen bedroom desk corner, oak frame + mat | made-from-PNG | SHADOWS, GLARE |
| `007_For_Use/LVRM_Boho_Neautral_ISO_Template.psd` | 869x1210 | 0.718 | 0.718 | 5x7 | ISO/5x7 | Soft boho-neutral living room, beige sofa, pendant, wall hoops | made-from-PNG | SHADOWS, GLARE |
| `007_For_Use/LVRM_Japandi_Simple_ISO_Template.psd` | 442x625 | 0.707 | 0.707 | ISO | ISO/5x7 | Japandi living room, linen sofa, blossom branches, wood shelves | made-from-PNG | SHADOWS, GLARE |
| `007_For_Use/LVRM_Modern_BLue_ISO_Template.psd` | 486x679 | 0.716 | 0.716 | 5x7 | ISO/5x7 | Sky-blue wall living room, teal chesterfield, palms | made-from-PNG | SHADOWS, GLARE |
| `007_For_Use/LVRM_Modern_Blue_2x3_Template.psd` | 396x554 | 0.715 | 0.716 | 5x7 | ISO/5x7 | Teal-blue wall living room, teal sofa, pendant | made-from-PNG | SHADOWS, GLARE |
| `007_For_Use/LVRM_Modern_Cradenza_Angled_ISO_Template.psd` | 501x708 | 0.708 | 0.532 | ISO | ISO/5x7 | Angled view, walnut credenza, vases, big leaning frame, window light | made-from-PNG | SHADOWS, GLARE, FOREGROUND |
| `007_For_Use/LVRM_Modern_Leather_4x5_Template.psd` | 427x592 | 0.721 | 0.719 | 5x7 | ISO/5x7 | White wall, tan leather wingback chair, fiddle-leaf plant, black frame + mat | made-from-PNG | SHADOWS, GLARE |
| `007_For_Use/LVRM_Modern_Walnut_5x7_Template.psd` | 728x1045 | 0.697 | 0.697 | ISO | ISO/5x7 | Walnut console, tan leather chair, tall windows, oak frame + mat | made-from-PNG | SHADOWS, GLARE |
| `007_For_Use/LVRM_Victorian_Floor_ISO_Template.psd` | 204x296 | 0.689 | 0.686 | ISO | ISO/5x7 | Empty Victorian panelled room, gilt frame leaning on herringbone floor | made-from-PNG | SHADOWS, GLARE |
| `001_Ratio_ISO/001_Living_Rooms/002_Modern/Modern_Moody_Beige.psd` | 462x646 | 0.715 | 0.716 | 5x7 | ISO/5x7 | Moody warm-beige living room, tan sectional, striped sun | ready (renamed) | `Reflections` (SO, Multiply 79%) |

Moved to `~/Desktop/Delete/` (for Tony to delete): `BDRM_Purple_Desk_2x3.psd` (flat 1024 px, no slot, baked anime art), its preview `007_For_Use/Templated/BDRM_Purple_Desk_2x3.png` (as `BDRM_Purple_Desk_2x3_Preview.png`), and `Duplicate_Copy_All_Ratios_MASTER.psd` (a byte-identical extra copy made while backing up the master).

## Layer structure (what to edit by hand)

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

## Renames, moves (old -> new)

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

File names keep their old ratio tags (e.g. `Game_Room_ISO.psd` now lives in 2x3); trust the folder and this table, not the name. `007_For_Use` is Tony's working set, not a ratio folder, so its templates stay there; use the "Bucket" column.

## Other folders and notes

- `007_For_Use/Templated/`: flattened previews of the PSDs (not templates). `Multiple_Frames/`: 3 multi-frame scene PNGs (not templated) + the Midcentury_Walnut PSD. `Unusable/`: 5 scenes Tony rejected (left as is). `untitled folder/`: 9 early AI drafts (unreviewed, left as is).
- Flat scenes kept as sources next to their new templates; `LVRM_Modern_Nook_4x5.png` is a 4096 px copy of the Leather scene (templated once, as `LVRM_Modern_Leather_4x5_Template.psd`); `LVRM_Modern_ISO_Moody_Beige.png` is the preview of `Modern_Moody_Beige.psd`.
- Sample art with illustrated faces (Girl PSDs, Trendy_Girl, BC_Teal_Closeup, BC_White_Bar_Cart) is now hidden under the placeholder or replaced art; only Tony's original `Original_` backups still show it. `LVRM_Midcentury_Walnut_2x3` still shows a baked sample print in its LEFT frame (only the right frame is a slot).
- Image generation: none used (0 kie.ai credits).
- Authoring scripts (reference, ran from a scratch dir): `lib.py` (quad maths, edge snapping, light/shadow layer builders), `build_layers.py`, `specs.py` (frame quads per PNG scene), `build_png.py`, `process_existing.py`, `rtest.py` + `testcard.py` (render/measure).
