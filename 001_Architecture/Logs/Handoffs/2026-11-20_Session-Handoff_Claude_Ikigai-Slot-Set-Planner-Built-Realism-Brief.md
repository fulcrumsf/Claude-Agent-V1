# Session Handoff, 2026-11-20, Ikigai slot-set planner built, slots 16-19 graded C, realism brief

Read first. Follows `2026-11-19_Session-Handoff_Claude_Ikigai-Blinds-Wrap-Gate-Studio-Chat-Look-Variety.md`.

## What is now true (all committed)
- **Slot-set planner built** (`Portal/app/slot_planner.py`, plan in `Pipeline_Docs/Slot_Set_Planner_Plan.md`): one pass writes all open-slot prompts, picks print size from the listing chart (small = tight shot, large = wide), balance check, saved prompts used by Generate, Show prompt triangle + Ask chat prompt edit on each card, plan/cost line, Replay open slots button. Panel repaints only when data changed (no flashing). 306 tests pass.
- **Blue marker for warm walls**: insert is orange by default, blue when the wall is visibly warm (sand, tan, beige, terracotta, mustard); builder, despill and art-area gate handle both. Library candidates must match decor too.
- **Portrait only**; the 4:3 Etsy photo shape is unchanged. Entry/hallway scenes go under Living Rooms.
- **Slots 16-19 generated and graded by Tony: 16 C, 17 C+, 18 C+, 19 C-.** Saved as library templates (committed). 72 credits spent in total by Tony's own clicks.
- **Reference set**: `Creative_Inspiration/Mock-Up_Inspiration/` has 26 usable screenshots (0001, 0023-0047 etc.), renamed and logged, overlays removed, low-res (<=400px) and originals in `Archive/`. Artwork references 0010-0011 in `Creative_Inspiration/`.

## Why 16-19 scored low (Tony, 2026-11-20)
Cookie-cutter and staged: same warm golden window light, same props (dried stems, stoneware, plants, fake books, rattan), looks like a big-box catalog, not a real home. Slot 17 was closest (depth, character). Wants: someone bought the print, hung it in their real home and took a nice photo. Lived in, gritty, real: windows with blinds/curtains, everyday clutter, mismatched furniture, phone-camera realism, different house types. Loud wall/furniture colours are fine in 1-2 slots; art must tie in but NOT match tones. No "why it fits" sentences on cards.

## Next (waiting on Tony's go)
Plan addendum, then build:
1. Blank the artwork inside each reference to the insert colour (SAM find frame, fill orange/blue; leftover watermarks or captions on art in 0008, 0026, 0032, 0037, 0038, 0042 go away).
2. Planner picks ONE distinct reference per slot and passes the cleaned screenshot to the image model for camera, lens, light, composition only.
3. Rewrite the planner taste section (remove my "walnut/oak, stoneware, dried stems, warm low sun" recipe) around the lived-in brief; set-wide repeat bans (dried stems once, rattan once, plant max twice); wider frame (yellow, bronze, painted) and prop lists; shorten the ~700 words of fixed prompt boilerplate.
4. Output scan for stray text, buttons or overlays (corners especially).
5. Record Tony's grade next to each prompt as learning data.
Also open: sand-wall threshold is a judgement call; the template checker fails most stand-ins for 1.5-3.5 px edge strips (pre-existing); template triage from 2026-11-16 still open; MEMORY.md is over its size limit.

## Standing notes
Do not ask Tony things he already told you or that can be looked up (listing sizes live in `Listing_Templates/Description_Template_AI.md`). Restart the Portal after code changes: `cd 005_Ecommerce/Etsy-Ikigai/Portal && uv run --no-project --with-requirements requirements.txt uvicorn app.main:app --port 8800`. Uncommitted and unrelated: graphify, .obsidian, `001_Architecture/Skills/.system`, `.tmp.driveupload/`, `Skills/gepeto/`.
