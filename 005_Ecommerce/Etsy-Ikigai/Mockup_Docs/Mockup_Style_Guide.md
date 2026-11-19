---
title: Mockup Style Guide (Ikigai room mockups, slots 8-19)
created: 2026-11-07
status: draft for Tony's review
used_by: Portal/app/rooms.py (room mockups, listing image slots 8-19)
---

# Mockup Style Guide: Ikigai room mockups

What this is for: the AI room mockups (listing slots 8-19) should look as good as the best-selling printable-art shops, and as good as Tony's own best mockups. Every rule below comes from images I looked at (Tony's live listings, his old n8n workflow and mood boards, 11 competitor listings from 10 shops). It is not from general opinion.

---

## 1. Findings by source

### 1a. Tony's live shop (IkigaiDigitalStudio, Etsy API v3 `GET /v3/application/listings/{id}/images`)

Looked at every image of 7 listings: 1753832528, 1767703085, 1768664937, 1753795168, 1825753177, 1766496265, 1847862569.

**Current image order (every listing):** 01 hero frame leaning on a herringbone floor against a white panelled wall (template) · 02 hands unrolling the print on a sunlit wooden table (template, raking sun) · **03 a subject-matched room (hand-picked, the best image in each set)** · 04 Instant Download · 05 What You Will Receive · 06 Important Notes · 07 Size Guide · 08 detail circle crop · **09-16 n8n AI rooms** · last: Loved by Customers.

**His best non-templated mockups and why they work:**

| Listing / image | What is in it | Why it works |
|---|---|---|
| 1753832528 #03 (colourful abstract) | Eclectic living room, wall painted teal and coral, mustard sofa, geometric cushions | **The room is built from the art's palette.** Teal, coral and mustard from the print are on the walls and cushions. Warm low sun from the left. The art fills about 40% of the image height. |
| 1767703085 #03 (woman drinking wine) | Black frame above a bar cart full of wine bottles and glasses, white panelled wall, pampas grass | **The room matches the subject** (wine art over a bar cart). Close crop: the art fills about 55% of the frame. A thin black frame suits the bold art. |
| 1767703085 #10 (same print) | Boho shelf corner by a window: terracotta pots, rattan, trailing plant, hard warm sun | Lived-in vignette. The terracotta and red props pick up the art's colours. Sunlight comes from a visible window. |
| 1766496265 #03 (Cyber Tokyo) | Dim attic gaming room with a lounge chair, monitors and warm low light | **The room's mood matches the art's mood.** Dark art in a dark room, so the exposure is believable. |
| 1847862569 #14 (blue ginkgo) | Wooden wall box with low raking sun and strong shadow shapes | Hard directional light, depth, and an off-axis view. |

**Tony's weak ones (09-16 on most listings):** wide, straight-on, empty rooms (white walls, generic oak sideboard, bed). The art takes up only 3-8% of the image. The rooms are interchangeable between prints. This is the same failure Tony is rejecting now.

### 1b. The old n8n mockup creator (found)

- **Workflow:** `/Users/tonymacbook2025/Documents/Docker/n8n-data/workflows/Ikigai_Mockup_Gen_Rooms _V4.json` (V1-V3 are next to it, with backups in `Docker/n8n-data-backup-20260319-150135/workflows/` and `Docker/backups/n8n_data_backups/n8n_workflows_backup/`).
- **Output folder:** `/Users/tonymacbook2025/Documents/Docker/outputs/n8n_outputs/ikigai_mockup_generator/` is **empty**. The real outputs are the live listing images 09+ (its file-naming code starts the index at 08).
- **Pipeline:** form (room type x style checkboxes plus an art upload) → every room+style combination → **random pick** of lighting, camera angle, scene focus and photo style → `chatgpt-4o-latest` writes one prompt → **Flux Schnell** (fal) draws the room, landscape 4:3, with "one portrait picture frame containing a blank white insert" → **Nano Banana edit** (fal) with the prompt *"Place the first image (artwork) naturally into the picture frame of the second image. Maintain realistic lighting, shadows, and reflections"* → resized to 2733x2050 and named `NN_<art>_<room>.jpg` from 08.
- **Variable lists in the workflow** (worth reusing):
  - camera: 3/4 corner, straight-on, wide eye-level, close-up of the wall area, low 3/4 corner, slight side angle, angled corner showing depth
  - light: natural daylight, soft diffused window light, hard directional sunlight, golden hour, overcast
  - scene focus: sofa wall, credenza corner, reading nook by a window, fireplace wall, console in an entryway, TV wall, bookshelf top
  - photo style: Dwell, Architectural Digest, lifestyle catalogue, gallery, vintage film
- **Why it looked better than rooms.py:** (1) the image model *relit the art inside the scene*, so shadows and warmth fell on the art; (2) the angles and light were varied; (3) "lived-in" was in every prompt. **Its flaw:** the art was **redrawn by AI**, so it may not be exactly what the buyer gets (Etsy risk, see 1e). Room choice was also random, not matched to the art.
- **Design notes behind it:** `007_Resource_Library/Mockups/Ikigai-Room-Mockups.md` (style, lighting and camera cheat sheets plus a JSON prompt template) and the iCloud mood boards `.../002-Ikigai/002-Mockup Generator Instruction Set/MoodBoards/*.png` (21 boards).
- **Most useful board: `MISC-Mockups.png`.** It is exactly the look Tony is asking for: hard sun through window mullions throwing **grid shadows across the wall and the frame**; frames **leaning** on floors, benches and shelves rather than hung; warm wood; close and medium crops. `LVGRM-Japandi.png` shows calm beige rooms with the art large in the frame. `PIC-FRAMES.png` shows ornate gold frames for classical art.
- **Security note:** the n8n JSON files contain a fal.ai API key written in plain text. It is not repeated here. Tony may want to rotate it.

### 1c. Competitors (Alura `search_products` digital "printable wall art", `get_keyword_top_results` for "cat wall art printable" and "book lover print"; images from the Etsy API)

Sales figures are Alura estimates (est_).

| Shop / listing | est sales | Images | Mockup vs info | What they do |
|---|---|---|---|---|
| SoftNSoft 1173486968 Flower Market | 12,676 lifetime | 10 | 6 / 4 | Set grid, flat frames with soft drop shadows, hands with the print on a sunlit table, a woman beside the hung print (scale), small prints on stands |
| DarkMoodyWallArt 1548503629 ghost | 547 | 10 | 7 / 3 | **All close vignettes.** Rustic wood frames leaning on shelves among old books, jars, apples and knitwear; dark green panelled walls; frame fills 60-80%; one full-bleed art crop |
| PrintsByRamla 4573247356 witch/cat bookstore | 10 (new) | 14 | 10 / 4 | Frame style changes per shot (gilded, carved walnut, ornate gold on velvet); mantel with pumpkins; **hands holding the frame on a knit blanket with tea**; mullion shadow over hands holding the print |
| PrintsByRamla 4548165569 pumpkins | 71 (23/mo) | 13 | 9 / 4 | Same system: angled flat-lay on linen with pinecones and tea; **frame leaning on a sage sofa with leaf-shadow sun**; woman holding the frame |
| ImaginatoriumLab 4583825939 cowgirl | 28 (23/mo) | 16 | **16 / 0** | All lifestyle. Extreme angled close-up of the texture (#02), leaning frames, people hanging or holding the art, golden window sun, warm wood rooms that echo the art's oxblood colour |
| VividArtPrint 4323785580 forest | 129 | 11 | 6 / 5 | Gilded frame in a hallway and a white wainscot kitchen; **sun with window shadow beside the frame** above a mid-century credenza; a bicycle as a lifestyle prop |
| Moonoinarakshop 4307050258 flowers | 240 | 10 | 10 / 0 | Desk, sofa and concrete walls; **2 shots with mullion shadows across the frame** (#06, #08) |
| LYRArtPrints 4600146204 Christmas set | 32 (32/mo) | 12 | 10 / 2 | Dark wood frames on mantels and dressers; **angled close-up of canvas texture with raking light** (#02); warm candle light |
| CultHausStudio 4436684957 13-print set | 159 | 6 | 2 / 4 | Angled gallery wall; extreme angled close-up with a sun band (#02) |
| VividArtSpace 1331071178 Matisse cat | 188 | 6 | 6 / 0 | Plain studio frames and 2 detail crops. Weak but cheap; sells on the art |
| ChicGlowPosters 4496104193 hand+book | 31 | 5 | 5 / 0 | Gold, black and oak frames; reading-corner bedroom; zoom crop |

**Patterns seen across them:**
- 60-100% of images are mockups; the leaders use 0-4 info slides.
- **Close and medium vignettes beat wide rooms.** In most mockups the art fills **35-80% of the image**. Only 1-2 shots per listing are wide "scale" rooms.
- At least one **angled, raking-light close-up** of the surface or texture (Imaginatorium, LYR, CultHaus).
- **Frames leaning** (floor, mantel, shelf, sofa, bench) are as common as hung frames.
- **Frame style follows the art era:** vintage or oil art gets gilded, carved or rustic wood; modern graphic art gets thin black or oak.
- **The room follows the subject or season** (pumpkins next to pumpkin art, books next to bookish art, bar cart next to wine art).
- People appear (holding, hanging, reading) in Ramla, Imaginatorium and SoftNSoft. See 1e for the California disclosure.

### 1d. The current rooms.py, read only to diagnose (not changed)

`Portal/app/rooms.py` asks for "camera faces the wall straight on", "a quarter of the image width" (art too small), "no shadow inside the picture area" (so it can never receive sun or mullion shadows), and uses 12 fixed scenes for every print. The compositing (lines 155-161) clamps the lighting to 0.75-1.2, blurs it with sigma 6 and applies it at 70%. Any shadow pattern is erased and the art stays brighter than the room. `find_frame` rejects frames that touch the edge or are partly covered (fill below 0.88), which rules out close-ups and overlapping props.

### 1e. Etsy rules (`../Rules_And_Policies/Etsy_Rules_Bible.md`)

- Images must show what the buyer gets. AI or AI-edited mockups are allowed **only if accurate**. No AI edits that make the item look better or different (lines 20, 41-43, 124, 175).
- Lighting, colour fixes, crops and background replacement are allowed if the product is shown accurately (line 43).
- Realistic **AI people** in images may need an AI disclosure for California buyers from **1 Jan 2027** (SB 1050, line 47).
- The current "compositing keeps the real pixels" approach is the right one. **Never let the image model redraw the art** (the n8n Nano Banana step did).

---

## 2. Why good mockups work (ranked)

1. **The room is chosen for the print.** Subject match (wine and bar cart, books and a reading chair, pumpkins and a mantel), mood or value match (dark art in a dark room, light art in a light room), and 1-2 of the art's accent colours repeated in props. This is the biggest difference between Tony's #03 images and his n8n rooms.
2. **The art is big.** It fills 35-80% of the frame in most shots. A wide room shot is used once, for scale.
3. **There is one visible light source, and it touches the art.** Window sun with mullion or leaf shadows that **continue from the wall onto the frame and the art**, a warm lamp, or candles. Shadow direction is the same everywhere in the image.
4. **The exposure matches.** The print's whites are never brighter than the lit wall next to it. In a warm room the paper white is warm. In shadow the art is dim.
5. **Angles and distances vary.** Mix 3/4 corner views (20-40°), low leans, angled raking close-ups, overhead or 45° flat-lays, and at most 1-2 straight-on shots.
6. **Contact and depth.** The frame casts a soft drop shadow on the wall or floor. A prop slightly overlaps the frame's bottom corner. The foreground or background is a little out of focus.
7. **The frame suits the art era.** Gilded or carved for vintage, oil and classical; thin black for bold graphic; natural oak or white for Scandi, Japandi and botanical; walnut for mid-century.
8. **It feels lived-in, not cluttered.** 3-6 props with a story (open book, mug, throw, ceramics, dried stems, fruit), slightly imperfect placement, no empty showroom.

---

## 3. Shot list for slots 8-19 (reusable recipe)

Rule of thumb: at most 2 straight-on shots, at least 4 close or medium shots, at least 4 shots with visible window-sun shadows, 1 evening or lamp shot. Two rooms per listing are picked from the mapping table in 3b. The others are vignettes in that same palette.

| Slot | Shot | Camera | Light | Art in frame | Frame |
|---|---|---|---|---|---|
| 8 | **Hero room A** (best-matched room from 3b) | 3/4 corner, 25-35° off-axis, eye height | Morning window sun from the side, mullion grid shadow across the wall **and the frame** | 30-40% of height | Era frame (3c) |
| 9 | **Lean vignette** on a sideboard or mantel with 3-5 props, one prop overlapping a frame corner | 15-25° off-axis, slightly low | Same sun, softer | 50-65% | Same frame |
| 10 | **Raking close-up**: corner of the frame and art | 35-50° off-axis, near the wall, shallow focus | Low sun, hard mullion bands across the art | Frame fills the image, edges may be cropped | Same |
| 11 | **Floor lean** against the wall on wood or herringbone, 1-2 props | Low, 10-20° off-axis | Side window light, one diagonal shadow band | 45-60% | Contrasting second frame (e.g. oak if 8 was black) |
| 12 | **Hero room B** (second-best room from 3b) | 3/4 from the other side (mirror of 8) | Soft overcast or diffused daylight, no hard shadows (gives the buyer one clean view) | 25-35% | Era frame |
| 13 | **Flat-lay**: unframed or framed print on linen or a wooden table with mug, book, stems | Overhead or 45° | Window light with leaf or mullion shadow at one edge | 55-70% | None or thin |
| 14 | **Evening vignette** | 20° off-axis | Warm table lamp or candles, wall falls to shadow, art dimmer than the lamp | 40-55% | Era frame |
| 15 | **Scale wall**: sofa, bed or console under the art | Straight-on allowed (one of the 2) | Even daylight | 15-25% (scale is the point) | Era frame |
| 16 | **Picture ledge or shelf** with books and ceramics, art leaning, possibly one plain small companion object (never other artwork) | 15-30° off-axis | Daylight from a visible window | 40-50% | Thin black or oak |
| 17 | **Subject prop vignette** (3b "story prop": e.g. a stack of books and a teacup for a reading cat) | 25° off-axis, close | Golden hour, warm | 50-60% | Era frame |
| 18 | **Detail crop**, made in post from slot 10 or 8 at full resolution (not a new generation) | n/a | As the source | Fills the image | n/a |
| 19 | **Season or alternate room** (bedroom, entry or kids room per 3b) | 3/4 corner | Cool morning (if 8 was warm) | 30-40% | White or oak |

### 3a. Light and exposure rules
- **One light story per image.** The window is visible or implied on the shadow side. The mullion grid is skewed to match the camera (it is a projected shape, so it lands as parallelograms and is never upright squares on a 3/4 wall).
- **Time of day:** morning = cooler and crisp-edged; golden hour = warm (about 3200-3800K) with long diagonal bands; overcast = no hard shadows (only slot 12); evening lamp = warm pool with dark falloff.
- **Shadow on the art:** cover no more than **about 35% of the art area**. Never cross the main subject's face or eyes, or the title text. The shadow must be continuous from the wall onto the art (same angle, spacing and softness).
- **Exposure:** the art's brightest paper white = the brightness of the lit wall next to the frame × 0.9-0.95 (paper is slightly darker than a painted wall in the same light). In shadow bands the art drops to the wall's shadow level. Never above.
- **White balance:** tint the art's whites toward the wall's colour at that spot (warm room = cream whites).

### 3b. Picking the room from the print (mapping table)

Compute from the print: the **subject** (from the idea or listing text), the **value key** (mean brightness: light / mid / dark), and **2 accent colours** (k-means on the art, drop near-white and near-black).

| Print subject or mood | Room A / Room B | Wall + palette | Story props | Light | Frame |
|---|---|---|---|---|---|
| Cute animal, light (e.g. **cat reading a book**) | **Sunny reading nook with a window seat** / cozy bedroom | Cream or warm white walls, art accent in a cushion or throw | Stacked books, open book face-down, teacup, knit throw, small plant | Morning sun with mullion shadow | Natural oak or white |
| Dark, moody, vintage oil, gothic | Dark green or charcoal panelled study / mantel | Deep green, brown, brass | Old books, apothecary jars, candles, dried flowers | Low lamp or candle, or a single shaft of sun | Gilded, carved or rustic wood |
| Bold graphic, pop, maximalist | Eclectic living room with a painted wall in the art's accent / bar cart | Accent wall from the art's colour 1, cushions in colour 2 | Bar cart, records, colourful ceramics | Warm late sun | Thin black |
| Food, drink, wine | Kitchen open shelves / bar cart | Warm white, wood, brass | Bottles, glasses, cutting board, fruit | Golden hour | Black or oak |
| Botanical, Japandi, Scandi, minimal | Japandi living room / bedroom | Oat, linen, pale oak, sage | Ceramic vase with one branch, linen, low table | Soft morning sun, leaf or mullion shadow | Oak or white, wide mat |
| Mid-century abstract | Mid-century living room / walnut credenza | Walnut, mustard, teal echoing the art | Sculptural lamp, books, a ceramic | Warm side sun | Walnut or black |
| Japan, anime, neon, cyber | Dim gaming or media room / bedroom | Dark walls, colour of the art's glow | Monitor, headphones, figure, LED strip (reads as practical light) | Night, practical lights | Black |
| Boho, desert, earth tones | Boho living room / shelf corner | Terracotta, sand, rattan | Pots, baskets, trailing plant, pampas | Hard warm window sun | Oak or rattan-tone |
| Funny bathroom | Bathroom vanity / beside a clawfoot tub | Tile in the art's accent, white | Towels, soap, plant | Bright window light | White or black |
| Kids, nursery | Nursery / playroom | Soft pastel in the art's accent | Plush toy, basket, books | Soft morning | White or oak |
| Seasonal (fall, Halloween, Christmas) | Mantel / entry console | Warm neutrals plus the season colour | Pumpkins, leaves, candles, greenery | Golden hour or candle | Era frame |

**Rule of thumb:** match the **value key first** (light art goes in a light room, dark art in a dark room), then the **subject**, then the **accent colours**. The cat-reading print in a dark library failed the first test.

### 3c. Frame options
`thin matte black` · `natural oak, 2 cm` · `white wood` · `slim walnut` · `ornate antique gold` · `carved dark wood` · `brass metal`, each optionally with a `white mat (5-8 cm)`. Use one frame per room. Use 2-3 different frames across slots 8-19 (as Ramla does) so buyers see options. The mat is part of the frame, not the print, so it is never drawn inside the magenta area.

### 3d. What to avoid
- Wide, empty, straight-on showrooms where the art is under 15% of the image (Tony's current 09-16).
- Light that does not touch the art: sun on the wall but a flat, shadow-free print; the art brighter than the room.
- The same room for every print; rooms that contradict the art's mood or value.
- More than 2 straight-on shots; a vertical window grid on a wall seen at an angle.
- Other artwork, posters, TVs showing pictures, text or logos in the scene (buyer confusion, Etsy accuracy).
- Realistic AI faces (see the open questions). Hands are lower risk but still optional.
- Glass glare or shadows so strong that colours look different from the file.
- Letting any AI model touch the art pixels.

---

## 4. Prompt templates

Placeholders: `{room}`, `{wall}`, `{accent_1}`, `{accent_2}`, `{props}`, `{frame}`, `{orientation}` (portrait or landscape), `{ratio}` (2:3, 3:4, 4:5, 11:14 or 5:7), `{angle}`, `{distance}`, `{light}`, `{time}`, `{lean_or_hang}`.

### 4a. Scene plate (GPT Image 2 or Nano Banana), magenta picture area that still receives the light
```
Photorealistic interior photograph for a home-decor magazine, {room}. {wall} walls; the room's palette
quietly repeats {accent_1} and {accent_2} in {props}. Lived-in, styled, not cluttered.
Camera: {angle}, {distance}, 35-50mm lens look, slight depth of field, no wide-angle distortion.
Light: {light} at {time}. A window just out of frame on the {side} throws a crisp shadow of its
window bars (mullions) as a skewed grid of light and shadow across the wall, and part of that same
pattern falls across the frame and the picture inside it. Everything in the image follows that one
light direction.
One picture frame, {frame}, {orientation}, outer shape {ratio}, {lean_or_hang}. The frame casts a
soft natural shadow on the wall/surface behind it.
The picture area inside the frame is a single flat sheet of matte magenta paper (#FF00FF): no
pattern, no image, no text, no mat, no glass glare. The magenta paper receives the room's light
exactly like the wall: it is brighter where the sun hits it and darker where the window-bar shadow
and the frame's edge shadow fall on it.
All four corners of the picture area are visible. No other artwork, no posters, no screens showing
images, no text, no logos, no people. {extra_avoid}
```
- `{distance}` examples: "medium shot, the frame fills about half the image height"; "close-up, the frame fills most of the image"; "wide room view for scale".
- `{angle}` examples: "three-quarter view from the left, about 30 degrees off the wall"; "low angle, 15 degrees off-axis"; "overhead flat-lay"; "straight on at eye level" (slot 15 only).
- `{lean_or_hang}`: "hung on the wall above the {furniture}" / "leaning against the wall on the {surface}, slightly tilted back".
- For slot 14 (lamp), replace the window sentence with: "A warm table lamp beside the frame is the main light; the far wall falls into soft shadow; the magenta paper is lit warmly on the lamp side and darker on the far side."
- For slot 12 (clean view), replace it with: "Soft overcast daylight, no hard shadows."
- Generate at **1:1, 2K**, or larger then crop. For close-ups (slots 10 and 18), generate the medium shot and **crop in post** so the corner detector still sees the whole frame.

### 4b. Avoid line (append)
```
Avoid: straight-on catalogue look, empty showroom, tiny frame, multiple frames, mirror reflections of
the picture area, glossy glass, harsh flash, overexposed white walls, cartoon or 3D-render look.
```

### 4c. Compositing in post (for the person who changes rooms.py; nothing changed yet)
1. **Read the light from the magenta itself.** Find the area by hue (R/G and B/G ratios rather than fixed differences, so dark shadowed magenta is still found). Light map = V (max of R,G,B) of that area divided by its 95th percentile. Blur only lightly (sigma about 1-1.5 px at 2K) so the mullion edges stay sharp. Allow a range of about 0.2-1.05 (not 0.75-1.2) and apply it at 100%.
2. **Exposure match:** scale the art so its 99th-percentile luma = 0.92 × the 95th-percentile luma of a wall sample just outside the frame on the lit side. Then multiply by the light map. The art can then never be brighter than the room.
3. **White balance:** multiply the art by (the wall sample's mean RGB / its luma), normalised, at about 60% strength.
4. **Fallback shadow (if the model left the magenta flat but the wall shows a grid):** build a gobo mask from the wall's shadow pattern next to the frame (threshold the wall luma), extend it across the art along the same skew, soften it by about 2-4 px, and **multiply** it at the wall's measured shadow depth (wall shadow luma / wall lit luma). If no wall pattern exists, draw a procedural window grid (2x3 panes, bar width about 4% of the pane, skewed with the frame's own perspective homography, blur growing with distance) and multiply it over both the wall and the art so it is continuous.
5. **Frame lip shadow:** inside the edge of the picture area on the light-source side, multiply a 1-3% wide gradient (about 0.85 → 1.0) for frame depth.
6. **Glass sheen (optional, black and gold frames only):** screen a faint diagonal gradient (3-6% opacity). Never over 8%, so colours stay accurate.
7. **Grain match:** add noise at the scene's noise level so the art does not look pasted on.
8. **Accuracy guard:** after compositing, compare the art region's colours with the source file (ignoring the light map). If hue moves by more than about 8° or shadow covers more than 35% of the art, flag the image for Tony instead of using it.

---

## 5. Open questions for Tony

1. **People:** competitors use hands and people (holding or hanging the art). OK to use **hands only**, none, or full people (which needs an AI disclosure for California buyers from Jan 2027)?
2. **How many shadow shots:** is about 4 of the 12 with strong mullion shadow over the art right, or do you want it on most of them?
3. **Frames:** one frame style per listing (cleaner), or 2-3 styles across the set like Ramla (shows options)?
4. **Room generation per print vs cached:** cached rooms are cheap but generic. Matching rooms to each print means about 12 image generations per listing. Is the cost OK, or should we build a cached library per row of the 3b table (about 11 moods × 12 shots) and pick from it?
5. **Slot 3:** the hand-picked subject-matched #03 is your strongest image. Should the best new AI room take that slot?

---

## 6. Tony's decisions (2026-11-07) - these override anything above

1. **No people** in any mockup (no hands either unless Tony says so later).
2. **Every mockup has some shadow**, not just 4. Reason: a plain, shadow-free image can be screenshotted, run through an AI upscaler and printed by a buyer; shadows baked into the image block that and also show how the print looks in real light. Vary the kind and strength: window panes (mullions), tree-leaf dapple, soft cast shadow, lamp falloff. Goal is many different looks while keeping the anti-screenshot effect.
3. **Frames:** several styles, as long as they fit the art. Not the generic thin IKEA-style metal frame on almost every image (still allowed as one option). Some images show the print with a **white mat/matte border** so buyers can see that look.
4. **Template library is fine** (cached, reused across designs), as long as listings do not all look the same across slots 1-20. Aim for at least **10 reusable room templates**, each with switchable layers: shadow overlays (window panes / leaf dapple / soft), wall colour, frame and mat variants. Tony is fine with PSD smart-object templates or an equivalent; the templates must be saved in a sensible, documented place.
5. Room is still picked per print (section 3b); the template library gives the room, the layers give the variation.

### Tony's additions (2026-11-07, later)
6. **Glass is good.** A subtle glass reflection/sheen over the print adds realism (competitors do it). Keep it faint so colours stay accurate; it is its own switchable layer.
7. **Hands are allowed**: POV only, never a face, e.g. a hand holding up a small frame. Still no people otherwise.
8. **Frames must be chosen tastefully, by a mechanism, not at random.** Ornate/gilded/carved frames only when the art's style suits them (vintage, oil, classical, gothic, dark-moody). Modern/graphic/minimal/botanical art gets oak, walnut, white or black. The chooser scores each frame style against the print (style tags, value key, accent colours, subject) and the set uses 2-3 distinct styles that all fit; some shots use a white mat.
9. **Props:** sparse and believable (1-2 per scene, placed where a person would leave them); the print fills 50%+ of the frame height in most shots; shadow strength softer than the first hero (shadow on every image, varied: window panes, leaf dapple, soft cast).
10. **Templates are PhotoCraft PSDs** (smart object for the art, shadow overlay layers, wall-colour layers, frame/mat/glass variants), rendered headless with photocraft-cli.

### Tony's style pick (2026-11-07)
Of the competitor sets shown, Tony prefers the **first one: ImaginatoriumLab (listing 4583825939, 16 lifestyle images)**. Its traits: warm natural-wood rooms, golden window sun with soft shadows, frames leaning on floors/benches/shelves as often as hung, art large (50-80% of the frame), sparse believable styling, thin natural wood frames with visible glass reflection, an extreme angled raking-light close-up of the paint texture, colours in props echoing the print, light herringbone/parquet floors. Use it as the reference when judging new mockups.

### Tony's authenticity rule (2026-11-07) - most important of all
Room mockups must look like **a real buyer's own photo**, not a catalogue: a trendy girl (or a stay-at-home mom with her own modern taste) printed the art, hung it, and took a candid photo in her real room. She has style (vintage tulip chair, thrifted rug, mid-century sideboard, plants she keeps) and the room fits the art she bought. Avoid department-store/Belk-catalogue staging: no posed prop groups, no furniture that does not belong (e.g. books on a random wooden stool). Mechanism: pick a buyer persona + room character per print; name specific furniture and its era; coherent personal palette; incidental clutter (mug left out, cable, shoes, half-read paperback); candid phone/35mm look with slightly imperfect framing and mixed light. Ask: would a real person plausibly own this room?
Clarification (Tony): props are not banned. Use them when they give true lifestyle (lived-in, belonging to the persona and room, left where a real person would leave them), never staged lifestyle (posed, arranged, catalogue-style). The earlier "1-2 props" guidance is superseded by this test.

---

## 7. Best-seller sweep (2026-11-07)

**What I did:** Alura `search_products` (digital only, sorted by estimated lifetime sales) for "printable wall art", "vintage art print", "abstract wall art", "trendy wall art", "boho wall art", "retro poster", "cat print", "cat art print", "book print", plus "wall art" listed after 2025-09-01 (new fast sellers), then `get_products` for the 30 picked. I dropped SVG/cut files, crochet/macrame patterns, mega bundles of thousands of files, custom portraits, matchbook Canva templates and planners, because their images are not room mockups. Every image of the 29 listings below came from the Etsy API (Ikigai key) and I looked at each contact sheet. Sales are **Alura estimates** (lifetime, est/mo = lifetime monthly average). **Alura had no last-month or 3-month numbers for any of these listings** (null, which means unknown), so "recent" is judged only by est/mo on listings created after Sep 2025. Alura credits used: 140 (564 used of 20,000 this month).

Contact sheets: `/private/tmp/claude-501/-Users-tonymacbook2025-Documents-Agent-OS/bc29af18-c208-42a9-b046-a10458a15093/scratchpad/bestsellers/Sheet_<Shop>_<listing>.jpg` (the single images sit in the folder of the same name). Scratchpad only, so they will not last; copy any you want to keep.

### 7a. Listings studied

| Shop | Listing | Est sales (lifetime / est/mo) | Images | Mockup / info | Slot 1 | Look |
|---|---|---|---|---|---|---|
| SoftNSoft | 1173486968 | 12,676 / 224 | 10 | 6 / 4 | flat studio grid of the set | catalogue, warm beige; one woman-from-behind room, one hands-unroll |
| NorthPrints | 1034647646 | 10,901 / 169 | 11 | 8 / 3 | gallery wall on plain wall | **no rooms at all**: frames on grey wall, one full-bleed crop |
| KIKIANDNIM | 1042867485 | 7,815 / 120 | 13 | 7 / 6 | hung over a vintage glass cabinet | **real-photo feel**: leaning on a radiator with an apple basket on red/black tile, on a kitchen counter with a Le Creuset pot and a snack bag |
| FloralsPrints | 1482944655 | 7,012 / 166 | 6 | 4 / 2 | floor lean on herringbone | 4 airy, believable rooms (dining nook, window, cabinet); straight-on |
| MitArtPrints | 1311295978 | 7,287 / 148 | 9 | 7 / 2 | frame filling a plain wall | 1 catalogue living room, 2 full-bleed crops, green wall |
| VibrantVintagePrints | 1352672873 | 6,128 / 129 | 10 | 10 / 0 | wide catalogue living room | 6 wide straight-on rooms (brick loft, rattan sideboard), 1 sun-shadow wall, 1 face crop |
| LILAxLOLA | 616984209 | 5,765 / 56 | 8 | 6 / 2 | real nursery, toddler from behind | real-photo nursery rooms, wallpaper close-up |
| NorthPrints | 1141061208 | 5,729 / 98 | 10 | 8 / 2 | gold frame on plain wall | plain wall + 4 frame styles, 2 crops, 1 sparse bedroom |
| DionysosArtPrints | 1480774361 | 5,297 / 125 | 10 | 5 / 5 | wide Scandi living room, set of 3 | 3 near-identical **lean on linen with cherry blossom and leaf-dapple shadow** |
| NorthPrints | 1038776665 | 4,889 / 75 | 10 | 8 / 2 | ornate frame on plain wall | plain walls only, 5 frame styles, 2 crops |
| TheFineArtPrintCo | 1467802411 | 4,360 / 101 | 10 | 9 / 1 | rustic frame, white wall | stock template set: crop, floor lean, plinth, mat on rattan, leaf shadow, chair corner |
| LegacyFineArtPrints | 1196973798 | 3,923 / 71 | 15 | 10 / 5 | gold frame, plain wall | **one persona across rooms** (grandmillennial): piano with candles, floral-wallpaper bedroom, vanity with perfume, kitchen shelf, mantel |
| diamoderndesign | 1404662500 | 3,932 / 92 | 5 | 4 / 1 | rustic frame, plain wall | 1 window room, 1 ornate frame, 1 crop |
| SeptandFlyArt | 1301105477 | 3,683 / 73 | 9 | 7 / 2 | trio leaning on floor in sun | catalogue rooms, a shelf vignette with a yellow craspedia |
| TheFineArtPrintCo | 1481938600 | 3,549 / 88 | 10 | 9 / 1 | rustic frame, white wall | same template as 1467802411 |
| PrintablePrints | 1539792461 | 3,086 / 80 | 9 | 4 / 5 | frameless on wall | weak, plain; sells on the art |
| AmptonDesigns | 1303817524 | 3,045 / 63 | 9 | 6 / 3 | trio above a sofa, **window reflected in the glass** | pink room with lamp, floor leans |
| BohoPrintablesCo | 1172632283 | 2,611 / 46 | 10 | 8 / 2 | flat grid of the set | plain walls, 2 rooms |
| GateOfDesign | 1282116135 | 2,976 / 58 | 20 | 15 / 5 | gallery wall in a room | **every single-print shot has hard window/leaf shadow across wall and frame** (04-12) |
| CircaArtCollection | 934882431 | 2,931 / 43 | 8 | 7 / 1 | rustic frame, plain wall | **real photos** (white fireplace, bookshelf, sideboard with a toy truck and pinecones) |
| selfhealjourney | 1221989006 | 2,468 / 46 | 11 | 9 / 2 | **POV top-down, her sneakers and jeans, frame on a green checkered rug** | the most "real buyer" set: unmade bed with pink throw, slippers, space heater, plastic side table, mug and book on the floor next to a lean |
| FirumWalls | 1037439822 | 2,336 / 36 | 20 | 6 / 14 | floor lean, **motion-blurred person walking past** | hands everywhere; info slides are lifestyle photos with text |
| ArdorPrints | 1573002391 | 2,211 / 59 | 6 | 5 / 1 | black frame with mat | 1 sun-shadow room |
| ElsartPrint | 1584695460 | 2,092 / 58 | 10 | 8 / 2 | catalogue boho room | 3D-render catalogue rooms (rattan, pampas) |
| NoirPixelStudio | 1762201282 | 2,029 / 76 | 10 | 8 / 2 | floor lean, panelled wall | **people in 4 of 8** (woman holding it in a bath, man hanging it, hand, woman reading in bed), raking-angle close-up |
| WellAndWest (new 2025) | 4374935162 | 1,987 / **151** | 10 | 8 / 2 | **oval gold frame laid on rumpled linen** | flat-lays on fabric, raking close-up, ribbon-hung frame on beadboard |
| MetisArtPrints | 786809244 | 1,811 / 23 | 9 | 7 / 2 | pair leaning on floor, warm sun | catalogue rooms |
| ClubTwentyThree (new 2025) | 4393449122 | 1,541 / **129** | 9 | 6 / 3 | **frame lying on a rumpled white sheet** | leans on herringbone with mullion sun, **lean against kitchen cabinets on red/black checker tile in hard sun**, picture-wire hang |
| ImaginatoriumLab (Tony's pick, from 1c) | 4583825939 | 28 / 23 (12 last month) | 16 | 16 / 0 | (see 1c) | reference set |

### 7b. Findings, ranked (what the top sellers actually do)

1. **The art sells, not the room.** The biggest sellers (SoftNSoft 12.7k, NorthPrints 10.9k/5.7k/4.9k, MitArt 7.3k) use plain studio walls or catalogue rooms. NorthPrints sells three top-10 listings with **no room at all**. So the mockups' job is to show the art large and honestly. A clever room does not rescue weak art. Realism is what lifts us above the many average sets, not a must-have to sell.
2. **Slot 1 is a product shot more often than a room shot.** In about 13 of 29, slot 1 is a single frame filling 50-80% of the image on a plain or near-plain wall, straight-on, with a soft drop shadow. The rest open with a floor lean (6), a wide room (5) or a top-down frame on fabric or a rug (3). **Contradicts our rules:** almost none of them uses a 3/4 room view as slot 1, and straight-on is the norm for slot 1.
3. **Straight-on is everywhere.** Most hung-frame shots in every set are straight-on. Our "at most 2 straight-on" rule is stricter than the market. The angled views that do appear are floor leans (camera low, 10-30° off) and raking close-ups. Recommendation: allow straight-on for slot 1 and wall shots; get variety from **distance and surface** (wall / floor lean / fabric flat-lay / shelf) rather than from camera angle.
4. **The floor lean is the most common lifestyle shot** (14 of 29 sets): on herringbone or plank floors, against a radiator, kitchen cabinets or panelling, often with hard window light. It is also the easiest shot to make look like a real buyer's photo ("I just got it framed, not hung yet").
5. **The newest fast sellers lead with a top-down frame on fabric.** WellAndWest (151/mo, 2025) and ClubTwentyThree (129/mo, 2025) put the frame flat on rumpled linen or a bed sheet in slot 1. selfhealjourney does the same on a checkered rug with the buyer's own sneakers in shot. This shot type is **missing from our shot list** and fits the "I just unboxed it" candid story.
6. **A detail crop is standard** (11 of 29), usually in slot 2 or 3: either a full-bleed crop of the art (often with the shop name over it) or a raking-angle close-up of the frame corner (NoirPixel, WellAndWest). Our slot 10/18 plan is right, but it should move up to slot 2.
7. **The candid "real buyer" sets are the newer, trendier shops**: selfhealjourney, KIKIANDNIM, ClubTwentyThree, CircaArt, FloralsPrints. The cues they share: bold floors (checkerboard tile or rug), an unmade bed or rumpled sheet, everyday objects that are not decor (slippers, space heater, radiator, apple basket, snack bag, cast-iron pot, a mug and paperback on the floor), lamps left on, imperfect crops that cut the frame or furniture, mixed warm light. This backs Tony's authenticity rule with real sellers. Catalogue rooms (Elsart, Vibrant, Metis, Dionysos) still sell, but they look like each other.
8. **Hard window or leaf shadow is common but not universal.** About a third of the sets use it (GateOfDesign on every single-print shot, Dionysos, ClubTwentyThree, Septand, FineArtPrintCo #08, Vibrant #07, selfheal). Almost every set has at least a soft drop shadow on every frame. Tony's "shadow on every image" rule is stricter than the market but already followed by the strongest-looking sets (GateOfDesign). Keep it, with soft drop shadow as the mildest level.
9. **People and faces are used, and they contradict our rule.** NoirPixel shows faces of people holding and hanging the art (4 of 8 shots, 76/mo). LILAxLOLA has a toddler, SoftNSoft and Retruly have women from behind, FirumWalls has hands on most slides and a motion-blurred passer-by. We still keep **no faces** (Tony's decision 1/7 and the California AI-disclosure risk), but **back-of-head / blurred / feet-POV** people are a proven middle ground. The selfheal sneakers-and-jeans POV is the safest version and fits "POV hand OK".
10. **Several frame styles per listing is a vintage-seller habit.** NorthPrints, Legacy, FineArtPrintCo and WellAndWest show 3-5 styles (gold, ornate, silver, rustic wood, black, white with mat, oval). Modern and graphic sellers keep one thin oak or black frame across the set. This matches decision 8 (frame chosen by art style).
11. **Room follows one persona across the set.** Legacy keeps a grandmillennial home (piano, floral wallpaper, vanity) and selfheal keeps one young renter's flat, so the set reads as one person's home. Elsart and Dionysos change room style per shot and feel generic. Use one persona per listing and vary only the spot in her home.
12. **Info slides: 1-3 at the end.** The median is 2 (size guide plus "digital download"). The leaders with 5 or more info slides (Dionysos, Firum, Printable) mix in promos and reviews. Glass reflection is visible in about 5 sets (Ampton's window in the glass is the clearest). It helps, as decision 6 says.

### 7c. Refined image order, slots 1-20

Template (PhotoCraft) or AI room as the Portal splits them now: slots 1-7 and 20 template, 8-19 room. One persona per listing for every room shot.

| Slot | Shot | Why (from 7b) |
|---|---|---|
| 1 | **Hero: single frame large (55-75% of height), straight-on or slight lean, near-plain wall in the persona's wall colour, soft window shadow plus drop shadow, faint glass sheen** | #2; what the leaders do; reads at thumbnail size |
| 2 | **Detail: raking-angle close-up of the frame corner and art surface** (or a full-bleed crop) | #6 |
| 3 | **Best candid room** (persona room A, floor lean or hung), a real-buyer photo | #4, #7 |
| 4 | **Top-down frame on fabric**: rumpled linen or bed sheet, or the persona's rug with her feet in shot (POV) | #5 |
| 5 | Instant Download / what you get (one slide) | #12 |
| 6 | Size guide (one slide) | #12 |
| 7 | Frame + mat options in one image (2-3 frames that fit the art) | #10 |
| 8 | Floor lean against kitchen cabinets, radiator or panelling, hard sun on the floor (checker or herringbone) | #4, #8 |
| 9 | Persona room B, hung above the furniture she owns (bed, sideboard, desk), lamp on | #7, #11 |
| 10 | Shelf or dresser lean with 2-3 everyday objects she left there | #7 |
| 11 | Leaf-dapple shadow vignette (lean on a bench or sideboard) | #8 |
| 12 | Clean even-light view, straight-on (colours true) | #3 |
| 13 | Evening: lamp on, warm pool, art dimmer than the lamp | #7 |
| 14 | Scale shot: wider room view, art 15-25% | 2nd scale view |
| 15 | POV hand holding the small frame in a doorway or by a window (no face) | #9 |
| 16 | Unmade bed or sofa corner with the print leaning behind | #7 |
| 17 | Season or alternate room for the same persona (entry, bathroom, kids room if it fits) | #11 |
| 18 | Detail crop of the art at full resolution (made in post) | #6 |
| 19 | Second frame style in a new spot (e.g. white with mat on beadboard, ribbon or picture-wire hang) | #10, WellAndWest/Club |
| 20 | Important notes / colours may vary (one slide) | #12 |

Info slides: 3 (5, 6, 20) plus the frame-options image. Everything else is a mockup.

### 7d. Prompt wording for "real buyer photo" realism

Add these to the 4a template (they keep the magenta picture area and the compositing rules):

- **Who and when**: "Photo taken on an iPhone by the woman who lives here, the afternoon she brought the framed print home. {persona}: {age range}, {style: e.g. thrifted mid-century + bold colour}, renting a {flat type} in {city type}."
- **Camera**: "Phone camera, 26mm equivalent, handheld, slightly tilted (1-3°), framing a little off-centre, the frame or furniture cut by the image edge; natural phone HDR, mild noise in the shadows; no studio lighting."
- **Floors and surfaces she actually has**: "worn red-and-black checker tile", "green-and-cream checkered rug", "old pine floorboards", "herringbone parquet with scuffs", "rumpled white bedsheet", "stonewashed linen".
- **Everyday objects, not decor**: pick 2-4 from the persona: "her slippers on the rug", "a space heater", "radiator under the window", "a mug of coffee and a paperback on the floor", "an apple basket", "a cast-iron pot on the stove", "a tote bag on the chair", "phone charger cable", "half-burnt candle", "laundry on a chair". Say "left there, not arranged".
- **Light she lives with**: "late-afternoon sun through the window making hard window-pane shadows on the floor and the lower half of the frame; a lamp left on in the background (mixed warm and daylight)".
- **For the top-down shots (slot 4)**: "shot straight down from standing height; the framed print lying on {rumpled linen / her checkered rug}; the toes of her {sneakers / bare feet} and a bit of her jeans at the bottom edge; soft creases and shadows in the fabric across the frame edge".
- **Ban list (append to 4b)**: "no matching decor sets, no symmetrical styling, no pampas-and-rattan showroom, no 3D render, no empty catalogue room, no perfectly made bed, no faces".
- Keep one persona per listing: pass the same persona sentence to every slot 8-19 prompt, change only the spot in her home.

### 7e. Sets for Tony to look at first

1. `/private/tmp/claude-501/-Users-tonymacbook2025-Documents-Agent-OS/bc29af18-c208-42a9-b046-a10458a15093/scratchpad/bestsellers/Sheet_selfhealjourney_1221989006.jpg`: the closest to the real-buyer rule (POV sneakers on a rug, unmade bed, slippers, heater).
2. `/private/tmp/claude-501/-Users-tonymacbook2025-Documents-Agent-OS/bc29af18-c208-42a9-b046-a10458a15093/scratchpad/bestsellers/Sheet_ClubTwentyThree_4393449122.jpg`: a 2025 fast seller (129/mo); frame on bedsheet, checker-tile kitchen lean in hard sun, mullion leans.
3. `/private/tmp/claude-501/-Users-tonymacbook2025-Documents-Agent-OS/bc29af18-c208-42a9-b046-a10458a15093/scratchpad/bestsellers/Sheet_KIKIANDNIM_1042867485.jpg`: a 7.8k seller with real-feeling everyday props (radiator, apples, kitchen counter).
4. `/private/tmp/claude-501/-Users-tonymacbook2025-Documents-Agent-OS/bc29af18-c208-42a9-b046-a10458a15093/scratchpad/bestsellers/Sheet_GateOfDesign_1282116135.jpg`: the shadow-on-every-shot look done well.
- Counter-examples worth a glance: `.../Sheet_NorthPrints_1034647646.jpg` (10.9k sales with no rooms) and `.../Sheet_NoirPixelStudio_1762201282.jpg` (people with faces).

### Tony's feedback on the v2 template sheet (2026-11-07)
- **Approved:** the shadows (all six looks), and the overall look and feel: natural, naturally styled. Shadows may be turned on freely ("at least acceptable").
- **Wall colour is art direction, not randomness.** Variants 2 (sage, "okay"), 5 (purple-pink clay, does not fit the room) and 6 (charcoal, hit or miss) were wrong: colours must be complementary but subtle, realistic (would a real person paint their wall this?), tailored to the art being shown AND to the room's furniture (teak sideboard etc.), thinking like an art director/interior designer. Never randomly generated. Implemented as `Portal/app/walls.py` + `config/wall_palettes.json` (scored like frames.py: furniture tone, art accent family, value key; realistic paints only; no pink/purple/neon).
- The Book Club Cat print is also not very stylised for a strongly coloured wall; prefer quiet warm neutrals (oat, warm white, warm sand, putty, greige).

### Tony's decisions on the best-seller sweep (2026-11-07, late) - override section 3 and 7 where they differ
- **Camera:** the straight-on limit is relaxed. Angled and three-quarter views are fine, and so is straight-on (any mix).
- **People:** still NO faces. **No people from behind and no feet/sneaker POV** (rejected; 7b item 9 and the 7c slot 4 "feet in shot" idea are out). A POV hand holding a small frame is still OK.
- **Future template:** add a "frame lying flat on rumpled linen / a bed sheet, shot from above" room template to the list of rooms to build (7b item 5). Not built yet.
- **Video_02:** decision deferred. The fal.ai key in the old n8n JSONs: ignore (no action).

### Room templates wired into the Portal (2026-11-07, late)
- Code: `Portal/app/room_templates.py`. Each wired room folder under `Room_Templates/` (any depth; the only one, `Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/002_Modern/Teak_Sideboard/`, was ARCHIVED 2026-11-10 to `Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/002_Modern/Archive/Teak_Sideboard/` and is ignored) has a `room.json` manifest (furniture tone, frame layers, lights with rank and the 3b mood rows they suit). Per print: frames from `frames.py` (only frames the PSD has), wall paint from `walls.py`, light ranked by mood row; every look is rendered with photocraft-cli and checked by the accuracy guard before it goes into `03-Etsy Images/` as `NN_Room_<Room>_<Light>.jpg`.
- Any paint is possible: the PSD's Greige layer is exported once (cached as `Cache_<light>_*.png` next to the PSD) and recoloured in linear light.
- Weak spots fixed: (1) leaf-dapple re-rolled once (Nano Banana 2 edit, 12 credits) so the dapple now crosses the whole art (`Room_Template_leaf_dapple_across.psd`; the old `gpt_b2_dapple_lit` is retired in room.json). Dapple naturally puts ~40 % of the art in soft shade, so its guard limit is 60 % instead of 35 % (set in room.json; Tony to confirm). (2) white frame is neutralised (no more taupe in shade). (3) paints get a highlight shoulder so a sunlit wall keeps its colour, plus a cool-cast limit so warm paints do not turn mauve in golden-hour shade.
- `mockup_rooms` stays `false` in `Portal/config/settings.json` until Tony approves the first image; flip it to `true` and the Run mockups button adds up to 4 room looks (slots 8-11). The Production tab hides older room files once the new step has made rooms (never deletes them).

### Tony's review of the Teak Sideboard room (2026-11-08) - override earlier text
- **No lamps or random props** unless they are clearly lived-in and fit the room and the persona. The desk lamp on the sideboard looked out of place and random, so it was removed from every light of the template.
- **Zoom-level clean-up is part of every template:** no garbled or fake lettering (book spines plain), furniture must make sense (one door pull per door, not two side by side), no odd paint patches where an object was removed.
- **Frames need real depth:** stepped moulding profile, a lip shadow on the mat/art, a visible side edge where the angle shows it, and a soft contact shadow on the wall (built into the PSD frame layers, never by redrawing the art). Done in `build_template_v2.py` (v3 PSDs).
- **Model rule for all room image generation and edits:** use Nano Banana Pro (`nano-banana-pro`), Nano Banana 2.1 (`nano-banana-2-1`) or GPT Image 2.5 (`gpt-image-2-5-flare-image-to-image` / `-sunburst-`). The older nano-banana-2 / gpt-image-2 only if none of these is available. Nano Banana Pro is best for precise removals and clean-up. Ids checked on docs.kie.ai 2026-11-08 (GPT Image 2.6 also exists).
- Template plate origin: the Teak Sideboard base plate was made by **GPT Image 2 text-to-image on kie.ai** (2K, 1:1, persona prompt "bookish_renter", saved as `Light_Prompts/plate_b_original_gpt_image_2_prompt.txt`), then cropped; the lights were Nano Banana 2 relight edits.
- Approval: Tony approved the Book Club Cat room image with the lamp removed; `mockup_rooms` stays `false` until he has seen the corrected v3 image.

### Template picker weighting by print ratio (Tony, 2026-11-08) - proposed starting weight, adjustable, not wired yet
- When Run mockups picks templates/ratios for a listing, weight toward what buyers actually print for living rooms and bedrooms: **2x3 35%, 3x4 25%, 4x5 25%, 5x7 10%, ISO/A-series and 11x14 5%**.
- Pick templates by **nearest standard ratio**, not exact slot ratio. 5x7 (0.714) and ISO (0.707) share one bucket (the ISO folder serves 5x7); 11x14 (0.786) has its own folder `005_Ratio_11x14` (slots nearer 0.786 than 0.800).
- Library: `Room_Templates/Portrait_Templates/` (43 ready templates; the 4 Teak Sideboard lights were archived 2026-11-10; all with art layer `Place Artwork Here`; per-template table and counts in `Room_Templates/Directory.md`, the only directory). Thin spot: 2x3 has 11 templates against a 35% weight.

### Template library rules (Tony, 2026-11-08) - override earlier text
- **One layout (Tony's master tree, re-filed 2026-11-08):** `Room_Templates/Portrait_Templates/<NNN_Ratio_X>/<NNN_Room_Type>/[<NNN_Style>/]<Template>/`, every ratio/room/style folder numbered with three digits (`001_Ratio_ISO` = ISO + 5x7, `002_Ratio_2x3`, `003_Ratio_3x4`, `004_Ratio_4x5`, `005_Ratio_11x14`; rooms `001_Living_Rooms`, `002_Bedroom`, `003_Bathroom`, `004_Kitchen_Bar`, `005_Office`, `006_GameRooms_Mancave` ...; styles such as `001_Japandi_Minimalist`). Templates go in the style folder their look fits, else directly in the room folder; agents never create room or style folders. One catalogue: `Room_Templates/Directory.md`.
- **The folder tree is the build plan:** an empty template folder Tony created (e.g. `001_Ratio_ISO/002_Bedroom/001_Japandi/`) is a missing template that must be built. Never remove or rename Tony's empty folders. Before building templates, list the gaps (`cd Portal && python3 -m app.template_gallery --gaps`) and fill them, popular ratios first (picker weighting above). Code handles any depth.
- **Archive:** in any template folder, anything not approved (old, superseded or rejected PSDs, JSONs, plates, `Original_` backups) goes into an `Archive/` sub-folder of that folder: do not use, but kept. Production code and the Templates tab ignore Archive.
- **Templates tab** (Portal): every template as a 4:3 Etsy-thumbnail crop centred on the frame (assumed shape; the rules docs do not state one), grouped by room type, with Style and Ratio chips as filters and gap cards for empty folders. Template styles use the Ikigai shop's own section names (vocabulary + Tony's manual choices + auto guesses in `Portal/config/template_styles.json`); manual always wins over the auto guess.

### Wainscoting and wall molding rule (Tony, 2026-11-15) - overrides earlier text
- **Wainscoting only when the style calls for it** (elegant or traditional rooms: formal living, dining, entry, Parisian/Victorian). Casual, modern and minimal rooms usually get none. A template with no wainscoting is never marked down for it.
- **When used, it must never touch the art.** Either (a) a LOW wainscot: panels and chair rail only from about waist height down, never behind the frame; or (b) panels where the art hangs: the panel is clearly bigger than the frame and the frame sits INSIDE one panel, centred, with clear wall margin on every side, never touching or overlapping any molding, rail or corner ornament.
- Why: a real frame cannot hang flat over raised molding. Found on `LVRM_Trendy_Girl_5x7` (frame covers the moldings between two panels), `LVRM_Trendy_Girl_4x5` (frame pushed to the left/bottom of its panel, against the corner ornament) and `003_BC_White_Bar_Cart` (frame over the upper panels' bottom molding and sitting on the chair rail).
- **Prompt line in every scene prompt (`Portal/app/room_slots.py` `WAINSCOT_RULE`, in `scene_prompt` since 2026-11-15):**
  "Wall paneling or wainscoting only if the room style calls for it; if used, either keep it below waist height and fully below the frame, or make the panels larger than the frame with the frame hanging centred inside one panel, with clear wall space on every side; the frame never touches or overlaps any molding, rail or panel edge."
- Checked by the template checker's placement check since 2026-11-15 (`template_checker.placement`; see `Template_Layer_Rules_And_Checker_Spec.md`, "Placement rule").

### Scene presentation, insert colour and ratio rule (Tony, 2026-11-16) - overrides earlier "blank white insert" text
- **Insert colour:** the printed area in every scene prompt is ONE flat onion-skin orange (about RGB 250, 215, 170), never white or grey (both failed SAM: white paper vs a white mat, grey vs wall and frame). Orange lets SAM tell the print area from shadows, mats and walls. Tested 2026-11-16: orange scenes found cleanly in all three presentations.
- **Presentations** (`room_slots.presentation_for(room, decor, ratio)`, deterministic, weighted by decor): `frame` (thin frame, no mat, negative prompt), `mat` (wide even off-white mat, bevelled window; elegant/traditional lean this way), `canvas` (1.5-2 in stretched canvas in a NATURAL LIGHT WOOD floater frame, never black or dark, thin gap, only a soft light shadow; since 2026-11-17 only the FRONT FACE is orange and the side edges are plain WHITE, because same-orange side edges made SAM take face + side edge as one shape). Canvas build path: `sam_detect(canvas=True)` / `build_psd(presentation="canvas")` treats the canvas face as the opening (no frame-lip rule, pad 0), then `sam_frames.canvas_face_quad` moves any side that SAM ran onto a side edge back to the face edge (+0.5 px in). See Template_Layer_Rules_And_Checker_Spec.md, "Independent edge check".
- **Ratio:** a drawn frame a bit off the print ratio is fine (buyers resize; mockups never state a ratio). Cover-fit and crop, never letterbox. `art_quad` tolerance, `MAX_CROP` and the checker's opening-ratio limit are now 35% (were 3%): only absurd mismatches are rejected. Tony has said this repeatedly; never add a ratio blocker back.
- Test scenes and prompts for this decision are not kept in the library; the three template scenes with wainscoting were built by hand-selected smart objects (see the 2026-11-16 handoff).
- **Canvas wrap strips (2026-11-17):** on canvas templates the camera-facing side edge shows the art wrapping round the corner (the art continuing round the edge in its own order, never mirrored: the print is cover-fit over the face plus the wrap depth; shaded with the photo's own side-edge light, luminance only; 2026-11-19), so the orange/white side of the scene never shows in a mockup. Spec: Template_Layer_Rules_And_Checker_Spec.md, "Canvas wrap strips". Never a white or orange bar beside the art: the art-area gate fails any render that shows one (same spec, "Blank bands beside the art").

### Light and photographer variety (Tony, 2026-11-17)
Every NEW scene gets a weighted random "look" so the library does not all look the same or all look staged. Code: `Portal/app/room_slots.py` (`LOOK_AXES`, `pick_look`, `look_weights`, `look_text`, `LOOK_GUARD`), used by `scene_prompt`.
- **Axes and base weights** (picked in this order; a later axis keeps only options that make physical sense with the earlier picks):

| Axis | Options (base weight) |
|---|---|
| Light style | direct sun with soft-edged visible shadows 35 (Tony's favourite, the Bedroom Wabi vertical look) · soft even overcast daylight 20 · crisper direct sun, sharper shadows 15 · dappled blinds / leaves 15 · low warm golden sun 15 |
| Photographer | relatable home-decor creator (natural staging, a little visible life, slightly casual framing, good-not-perfect light) 60 · architecture / interiors magazine 40 |
| Time of day | mid-morning 30 · late afternoon ~5 pm 30 · golden hour 25 · midday 15 |
| Season | autumn 30 (low warm sun) · spring 25 · summer 25 (high bright sun) · winter 20 (low pale sun) |
| Sun direction | window off to one side (raking light) 45 · window facing the sun 35 · window facing away (soft reflected light) 20 |

- **Physical-sense rules:** golden light only at late afternoon or golden hour (and at 5 pm only in autumn or winter); golden hour only with golden light; 5 pm winter only with golden light; a window facing away from the sun only with soft even light, a window facing the sun only with sunny styles. Resulting overall mix (neutral room): time late afternoon 46%, morning 32%, midday 16%, golden hour 7%; sun from the side 59%, facing 35%, away 6%.
- **Room and decor nudge, never remove:** `LOOK_NUDGE_ROOM` / `LOOK_NUDGE_DECOR` multiply weights (e.g. Boho and Botanical favour dappled leaf light, Coastal favours crisp summer sun, Victorian favours the magazine look, Dorm and Kids favour the creator look, Office and Kitchen favour mornings); each multiplier is clamped to 0.5-2.0, so every option stays possible in every room.
- **Positive wording only** in every phrase (tested). The guard sentence is in every variant: sun patches, shadows and any blind or leaf pattern land on the floor and the wall around the frame while the printed area stays one flat, evenly lit tone, and the frame, mat or canvas edge and wall keep crisp outlines (for SAM and the independent edge check). The orange matte surface text, canvas white side edges, black-frame "only occasionally" rule, no-people rule, wainscoting rule, presentation pick and ratio logic are unchanged. Shadow layers are still measured from each image.
- **Recorded:** `template.json` gets `"look"` ({version, seed, light_style, photographer, time_of_day, season, sun_direction}) next to the exact `"prompt"` sent, on both build paths (Templates tab "Build this" in `template_build.run`, and Production's auto-save via `scene_templates.save_template`). Replay: `pick_look(room, decor, seed=look["seed"])` or `pick_look(room, decor, override=look)`; `template_build.run(..., look=<seed or dict>)` rebuilds with a chosen look.
- **Gap tile tooltip** (Templates tab): shows the prompt with the line "Light and photographer look: picked at random when Build this is clicked ... and saved in template.json", because the real pick happens at build time (a sample shown earlier would differ from the one built).

### Scene look v2: camera, display, walls, personas (2026-11-19)
Tony: every scene looked shot by the same photographer (hardcoded "Camera angle: 3/4 corner", beige limewash, old planks, book + mug + throw). `LOOK_VERSION = 2` adds the axes proposed in `Research/Etsy_Mockup_Look_Findings.md` (evidence: 105 top Etsy listings, 46 of Tony's templates, our generator). Reference for variety, never copies. Same code and functions as above (`LOOK_AXES`, `LOOK_ORDER`, `pick_look`, `look_weights`, `_look_fits`, `_look_gate`, `PERSONA_NUDGE`).

| Axis (pick order) | Options (weight) |
|---|---|
| Photographer (key name kept) | 12 personas: warm lifestyle creator 40 · airy Scandi catalogue 36 · mid-century magazine 35 · editorial minimal 32 · Parisian apartment 30 · trendy renter 28 · bold colour eclectic 26 · Japandi calm 26 · moody dark academia 22 · coastal cottage 22 · country farmhouse 22 · playful nursery 17 (kids rooms only). Each brings its own props; no light, lamp, wall or floor words |
| Display | hung over furniture 62 · floor lean 52 · leaning on furniture 47 · hung on a bare wall 36 (anchor / surface per room) |
| Camera height | eye 71 · low (knee-hip) 57 · counter 32 · seated 28 |
| Camera angle | straight-on 69 · slight left / right 36 each · through a doorway 35 · 3/4 corner left / right 26 each |
| Distance | medium 63 · close vignette 59 (art at most ~60% of the height) · wide 50 |
| Lens | 35-50 mm 87 · 24-28 mm 41 · 85 mm 10 (never seen in the data: UNTESTED) |
| Foreground | clear 59 · sofa/chair/bed edge 50 · plant leaves 37 · side table 37 · rug/throw edge 35, always well clear of the frame |
| Focus | deep 88 · soft far background 35 · soft nearest object 32 (art always sharp) |
| Composition | centred 67 · left / right third 39 each · beside a window 39 · offset over furniture 32 |
| Walls | warm white 56 · ivory 36 · greige 36 · pale grey 32 · sage 30 · teal/dusty blue 28 · deep moody 26 · blush 22 · cool colour block 20. Never orange, peach, apricot, terracotta, coral or rust |
| Wall finish | plain 72 · panelling 40 (hung art only) · limewash 35 · shiplap 28 · wallpaper 26 (kids, vintage, boho, coastal, botanical, bathrooms) · painted brick 22 |
| Floor | light herringbone 50 · light plank 50 · rug 39 · honey 37 · dark 30 · checker tile 24 · pale stone 24 |
| Furniture | walnut/teak 55 · light oak 49 · colour upholstery 40 · painted 35 · rattan 32 · white/linen 28 |
| Frame finish (frame and mat only) | light oak 69 · walnut 37 · black 33 · white 30 · antique gold 26 (vintage decors only) |

- **Weight rule:** weight = round(10 x sqrt(research %)). The square root keeps the order of the data but flattens a 7:1 lead to about 2.6:1, so rare looks really appear. Black frame uses the market's 11% (Tony: black only occasionally); telephoto is fixed low.
- **Fit rules (contradictions blocked):** floor lean never at counter height; counter height only with art on or over furniture; low camera never close under hung art (steep tilt keystones the opening); doorway shots are medium or wide, centred, nothing else in front; panelling only behind hung art centred in one panel (wainscot rule); a rug/throw never under a floor lean; soft background never when the art wall is the background; offset composition needs furniture; a window in the art wall never faces the sun; wide lens never close, 85 mm never wide; frame must contrast with the wall (blush: black or walnut only; no oak on ivory, greige, blush or limewashed white; no white frame on white or pale grey; no black or walnut on deep walls); a canvas floater on a pale warm wall is asked for in a darker honey oak. Gamer, arcade and mancave decors use only 5 fitting personas.
- **Prompt wording:** the fixed "Camera angle: 3/4 corner" and the canvas "slight 3/4 view" are gone; the picked angle drives it. When the art leans, no sentence says it hangs. `LOOK_GUARD` plus a new `LOOK_GUARD_FRAME` (whole frame in the picture, clear wall on four sides, nothing overlapping the frame, art face flat, upright and sharp, frame stands out from the wall) are in every prompt.
- **Old looks:** a template.json look with `"version": 1` replays with the v1 tables and gives the byte-identical old prompt (`pick_look(room, decor, override=look)`, or `seed=..., version=1`). Tested.
- **Not yet proven:** nothing has been generated with v2. SAM and the edge check on leaning frames, doorway shots, low angles and dark walls need 2-3 real test scenes.
