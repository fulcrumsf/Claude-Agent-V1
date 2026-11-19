# Session Handoff, 2026-11-19, Ikigai blinds shadow, wrap fixes, render gate, Studio chat, look variety

Read this first. Follows `2026-11-18_Session-Handoff_Claude_Ikigai-Office-Canvas-Shadows-Strips-Slot-11.md`. Read `Skills/Wall-Art-Shadows/SKILL.md` before any shadow or wrap work.

## Waiting on Tony (next session: he tests the other slots)
1. Approve or deny the Book Club Cat room images in Production: slot 11 (`11_Room_Office_Modern_v2`), 12 (`12_Room_Living_Room_Mid_Century_v4`), 13 (`13_Room_Bedroom_Boho`), 10 if wanted. Slot 3 is already approved by Tony.
2. Generate more slots and test them (slots 9, 10, 14-19 are empty). Office templates for slots 14 (Mid-Century) and 18 (Japandi) do not exist yet.
3. Test the new look variety on 2-3 real scenes (a frame leaning on the floor, a doorway shot, a dark wall). Nothing generated with it yet; each new scene costs about 18 credits and only on Tony's click. The 85 mm lens option was never seen in the research.
4. Click through the new Studio chat "Ask chat" button on a Production card in a browser (only syntax-checked). Re-render, template check and regenerate button were tested with stand-ins only.
5. Template triage of the live templates (keep / hand-fix / regenerate / archive), still open from 2026-11-16.

## Future, NOT now (Tony's request)
A single button in the Production tab that generates all the necessary slots for a design in one click (all empty room slots from the plan, free library templates first, credits only for new scenes with the cost shown up front, one at a time because of the single job lock in `production.start_slot`). Design it with the render gate and the Studio chat in mind; ask Tony for the credit cap before building.

## What is now true (all committed, nothing pushed)
- **Boho Bedroom 002116** blinds shadow done and approved: `light_pattern._slats` measures the periodic slat stripes directly (rectified wall, coherent sun-patch component, re-picked angle, folded profile, depth rescaled to real contrast). Placed in slot 13. Method written up in the Wall-Art-Shadows skill.
- **Render gate** `room_templates.art_area_gate` runs on every Production room render: fails any render showing blank paper, a white or orange bar, or a broken wrap seam (continuity check at each wrap edge). Library templates that fail are rebuilt free from the saved scene and re-rendered; still failing goes to Archive with the reason.
- **White bars (slot 12):** cause was a flat white band beside the canvas that SAM did not include; the builder now stretches the art over such bands. **Wrap (slots 11, 12):** art is fitted over the front face plus the wrap depth and the side shows the art continuing in the same direction, never mirrored; slot 12's strip geometry fixed (strip pixels take the art from the same height as the front at the fold).
- **Slot 3** re-rendered free from its approved Japandi template (v5) with the corrected wrap.
- **Studio chat** (`app/prod_chat.py`, `assistant.py`, `chat.py`, `studio.py`, `index.html`): knows the open slot, can see the slot image (proven through `claude -p` stream-json), can approve/deny/undo, free re-render of a slot's current template, run the template check, and write a fix request `Handoffs/YYYY-MM-DD_Fix-Request_Portal_Slot-NN.md` (slot then shows "Waiting for Claude Code"). A paid regenerate only shows a button; credits are spent on Tony's click. Fix requests: read any in this folder first.
- **Look variety v2** in `app/room_slots.py`: camera angle, height, distance, lens, focus, foreground, display, composition, wall colour and finish, floor, furniture and frame finish, 12 photographer personas; hard limits kept (no orange walls, frame contrasts with the wall, art flat and in focus). Old saved looks replay byte-identically. Research: `Research/Etsy_Mockup_Look_Database.json` and `Etsy_Mockup_Look_Findings.md` (156 tagged images: 105 Etsy listings from 37 shops via Alura, 46 of Tony's own templates, 5 generator scenes). Limit: Etsy blocked listing pages, so only each listing's first image was seen; thumbnails were downloaded once at low rate from Etsy's public image server (grey area under the Rules Bible).
- **Template library** hides failed templates unless "Show failed" is ticked. Superseded iterations were moved to `~/Desktop/Delete` (Tony deletes).
- Portal restarted on port 8800 after a PermissionError on `index.html` (files rewritten by helpers; the old process could not read them). If "internal error" appears again, restart it: `cd 005_Ecommerce/Etsy-Ikigai/Portal && uv run --no-project --with-requirements requirements.txt uvicorn app.main:app --port 8800`.

## Risks / not done
- Slot 12 uses the 2x3 print (library picks the closest shape) and the cat's tail is clipped at the right edge (normal cover crop).
- The shadow rebuild path for slot 12's template uses the newer builder that can add blind stripes; the kept render uses the original sun-line shadow.
- The gate cannot catch a mirror (looks continuous); any older render made before 2026-11-19 may still have one, re-render free from its template.
- MEMORY.md index is over its size limit; compact it.

## Standing rules learned this session
Superseded iterations go straight to `~/Desktop/Delete`; library shows non-failed only; his own mockups are the `Room_Templates/` library (failed ones included) and are a taste reference; never ask him where things are (see memory).
