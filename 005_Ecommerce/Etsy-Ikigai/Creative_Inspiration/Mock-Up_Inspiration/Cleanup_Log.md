# Mock-Up Inspiration - Cleanup Log (2026-11-20)

Removed things that are not part of the photographed room (Pinterest/Etsy UI, shop labels, watermarks).
The artwork inside the frames was left alone (a later step blanks it). Untouched originals of every edited
file are in `Archive/` with the same filename. No upscaling or sharpening.

Tools: crop = Pillow; LaMa = `big-lama.pt` from the Pinokio ComfyUI models folder, run directly with torch
(no ComfyUI job), result pasted back only inside the mask; Nano = kie.ai Nano Banana 2.1 wide-crop fill
(crop with an exact ratio, result pasted back only inside the mask).

| id | overlay found | where | fix used | result |
|---|---|---|---|---|
| 0001 | Pinterest "Visit site" button + lens (visual search) button | bottom-left, bottom-right | LaMa (credenza kept, so no crop) | ok |
| 0002 | none | - | untouched | ok |
| 0003 | none | - | untouched | ok |
| 0004 | none | - | untouched | ok |
| 0005 | "Deal" bubble | top-left corner | crop top 16 px (213x302 to 213x286) | ok |
| 0006 | "0:14" video timer | top-left corner | crop left 39 px (224x221 to 185x221; wall only) | ok |
| 0007 | none | - | untouched | ok |
| 0008 | "Deal" bubble | top-left corner | LaMa (a crop would cut the frame or doorway) | ok; "ART EXPLORE" watermark sits on the artwork, left for the blanking step |
| 0009 | none | - | untouched | ok |
| 0010 | none | - | untouched | ok |
| 0011 | "Deal" bubble | top-left corner | LaMa (a crop would lose the left sconce) | ok |
| 0012 | "Artexplorespace" watermark | wall/bench, lower left of room | LaMa | ok |
| 0013 | none | - | untouched | ok |
| 0014 | "Deal" bubble | top-left corner | crop top 17 px (211x283 to 211x266) | ok |
| 0015 | none | - | untouched | ok |
| 0016 | none | - | untouched | ok |
| 0017 | none | - | untouched | ok |
| 0018 | none | - | untouched | ok |
| 0019 | none | - | untouched | ok |
| 0020 | none | - | untouched | ok |
| 0021 | "Deal" bubble | top-left corner | LaMa on the brick wall | ok |
| 0022 | "ArtisBetter" watermark | bottom-left edge | crop bottom 17 px (220x297 to 220x280) | ok |
| 0023 | none | - | untouched | ok |
| 0024 | "insert your own design" circle | top-left, over window and wall | Nano (LaMa tried first, smeared the garden view) | ok |
| 0025 | "aurethia studio" shop name | bottom centre, over floor and frame edge | LaMa | ok |
| 0026 | faint tiled "CanvaMockupStore"-style watermarks | wall left and right of frame (7 spots) | LaMa per spot | ok on wall; marks printed inside the artwork left for the blanking step |
| 0027 | faint "studio tres mood" watermark | bottom-left, tiles beside toilet | LaMa | ok |
| 0028 | "EASY EDIT" + ring of small letters | right side, over frame, rug and print | LaMa on a pixel-tight text mask (Nano refused: "flagged as sensitive", not charged) | ok; a few letters of the print's own "every day" line got softened (artwork, blanked later) |
| 0029 | carousel arrow stub | left edge, mid height | crop left 13 px (676x560 to 663x560) | ok |
| 0030 | "insert your own design" circle | top-left, over wall and plant | LaMa | ok |
| 0031 | none | - | untouched | ok |
| 0032 | faint tiled mock-up store watermarks | right wall, floor bottom-right, door glass (5 spots) | LaMa per spot | ok; marks inside the artwork left for the blanking step |

Totals: 5 crop, 12 inpaint (11 LaMa, 1 Nano), 15 untouched. kie.ai credits spent: 6 (one Nano call; the
refused 0028 call cost nothing).


## 2026-11-20 low-resolution sweep (Tony)
Images 400 px or smaller on their longest side (all ~200-340 px screenshots) moved to Archive/ so only usable references stay. Where Archive already held the untouched original, the cleaned version was moved in as `<name>_Cleaned.png`. Moved: 0002, 0003, 0004, 0005, 0006, 0007, 0008, 0009, 0010, 0011, 0012, 0013, 0014, 0015, 0016, 0017, 0018, 0019, 0020, 0021, 0022.


## 2026-11-20 batch 0033-0047 (15 new screenshots)
None are low-resolution (smallest longest side 720 px), so none went to Archive for that reason. Each image was viewed, plus a contrast-boosted high-pass check for faint tiled watermarks (none found). Same tools and rules as above.

| id | overlay found | where | fix used | result |
|---|---|---|---|---|
| 0033 | none | - | untouched | ok |
| 0034 | none | - | untouched | ok |
| 0035 | none | - | untouched | ok |
| 0036 | none | - | untouched | ok |
| 0037 | none | - | untouched | ok; small caption text is printed on the artwork itself, left for the blanking step |
| 0038 | none | - | untouched | ok; "ROOTED" caption is printed on the artwork itself, left for the blanking step |
| 0039 | none | - | untouched | ok |
| 0040 | none | - | untouched | ok |
| 0041 | none | - | untouched | ok |
| 0042 | none in the room | - | untouched | ok; "Your artwork Here" placeholder text is inside the frame, left for the blanking step |
| 0043 | none | - | untouched | ok |
| 0044 | none | - | untouched | ok |
| 0045 | none | - | untouched | ok |
| 0046 | none | - | untouched | ok |
| 0047 | faint engraved-style text watermark | mantel frieze, centre (x 288-367, y 270-282) | LaMa (branch pixels kept out of the mask) | ok |

Totals: 0 crop, 1 inpaint (1 LaMa), 14 untouched. kie.ai credits spent: 0.


## Blanked references (`_Blank.png`, realism addendum 1, 2026-11-21)

`NNNN_<Same_Name>_Blank.png` next to each source = the same cleaned screenshot with the artwork filled flat with the
insert marker colour (orange, or pale blue when the reference's own wall is warm), one pixel under the frame lip, so
captions, watermarks and poster lettering on the art are gone. Made headless and free by
`python -m app.references --prepare` (Portal; local SAM 2 + one Gemini flash-lite box call per reference, no kie.ai
credits). `Reference_Manifest.json` holds per reference: fill polygon, marker, measured facts (aspect, art height share,
camera side, light side, wall colour), the free checks and why a reference is unusable, seed tags (`tags_by`), uses and
Tony's grades. Sources are never changed. To blank one by hand: save `<name>_Blank.png` here and set its entry's
`blank_method` to `tony` (never overwritten). Usable after the first run: 16 of 26 (0023, 0024, 0025, 0026, 0029, 0030,
0031, 0032, 0034, 0035, 0036, 0037, 0039, 0042, 0044, 0047).
