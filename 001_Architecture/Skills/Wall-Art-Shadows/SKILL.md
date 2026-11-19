---
name: Wall-Art-Shadows
description: How to build realistic shadows and window light for wall-art room mockups in PhotoCraft (the Ikigai Portal template PSDs). Invoke when a template's shadows look wrong or missing (blind slats, window mullion bars, sun patches not continuing across the art, flat or floaty canvas, canvas edge, frame shadow), when building or fixing the Light Shadow / Frame Edge Shadow / Frame Hard Shadow layers, or when Tony says "the shadow is wrong". Method = read the wall's own shadows with the art layer hidden, judge hard vs soft, copy the shapes, set blur and opacity to match. Built from two Photoshop tutorials plus Tony's rules, 2026-11-18.
---

# Wall-Art-Shadows

Created 2026-11-18 with Tony. Version 1: the method is settled, the automation is not (see "Status"). Research is not repeated in the field; it is summarised below.

## Tony's rule (the core)
**Mimic the shadows that are already on the wall.** Do not invent a shadow and do not ask him how.
1. Turn OFF "Place Artwork Here" (and any wrap strip / glass layers) so you see the base photo around and behind the art.
2. Find the light source: which side the window is on, where sun patches and shadow bars fall on the wall and floor beside and behind the art.
3. Judge each shadow: **hard or soft**, **what shape** it makes (parallel slat bars, a window grid of mullion bars, one diagonal sun edge, a soft gradient), its angle, spacing, darkness.
4. **Duplicate that exactly across the art area**: continue the same bars along their own direction through the art so a bar on the wall to the left of the art carries on through it and out the other side. Match angle, spacing and width.
5. Match the edge: a Gaussian blur equal to the neighbouring wall shadow's edge softness (tiny or none for a hard sun shadow, large for overcast). Judge it by comparing wall and art side by side.
6. Never use black unless the wall's shadows are black; use the colour the wall's shadows actually are (sample them). Keep the shadow layer Multiply, low opacity, masked to the art face only.

## What the two tutorials add (watched and grabbed, 2026-11-18)
Source A: "How to add a drop shadow to your fine art mockup" (YouTube 9Rhv1JnXxvY, Photoshop 2021, Layer Style).
- First find the light direction from the existing shadows (plant pot, books). Strength: a bright room gives a subtle, not black, shadow.
- Drop shadow blend mode Multiply; colour sampled with the eyedropper from the photo's own shadow, dark but not black; opacity about 20-25%.
- Angle = opposite the light (light from the left means a shadow angle near 160 deg); distance small so the piece hangs ON the wall (big distance looks floating); size (blur) larger; spread 0-9.
- **Stack 3-4 drop shadows, never one**: duplicate and change each one slightly (angle a few degrees, opacity up a little, distance and size tighter). One shadow looks fake and floaty.
- Global light on so all shadows share a direction; add one tiny, faint secondary shadow on the other side if the photo shows a little shadow there.
- Canvas: Bevel and Emboss, inner bevel, depth about 100, low size and soften, opacities about 50%, highlight Screen on the light side and shadow Multiply on the far side (shadow colour sampled, not black), so the edge reads as a wrap.
- Copy the layer style to every other piece so all shadows match.

Source B: "Refining AI-generated mockups with Photoshop" (YouTube FRXYiYJiOXQ), Midjourney room mockups for Etsy.
- Window light: draw white rectangles for the window panes (4-6, short even gaps), group them ("Window Lights"), Free Transform > Distort until the pane shapes fall on the wall like the real window's light, blend mode **Overlay** at 40-50%, Gaussian Blur (smart filter) 20-30 px, then lower the background brightness until the light looks real. Buyers can toggle the group.
- Glass reflection: Layer via Copy of the bright area beside the frame, distort over the glass, lower brightness and exposure, **Screen** at 40-60%.
- Objects in front of the frame: cut them to their own layer above the art.

Third reference (read, not watched): photoshopessentials.com "Casting Light Through Window Blinds" bends blind shadows over a 3D subject with a displacement map from the Lab lightness channel. Overkill for a flat wall; the flat-wall equivalent is the parallel-band continuation above.

## How this maps to the Portal template layers
Template PSD layers (all Multiply, black fill, masked to the art quad; see `Mockup_Docs/Template_Layer_Rules_And_Checker_Spec.md`):
- **Light Shadow**: the key light across the art. This is where blind slats / mullion bars / sun edges go. Built in `Portal/app/scene_templates.py` `key_light()`.
- **Frame Edge Shadow**: soft shadow inside the opening along the frame (per side).
- **Frame Hard Shadow**: crisp inner-edge line.
- Canvas also has Wrap Strip (placeholder) and Despill layers; see `app/wrap_strips.py`, `app/despill.py`.
Photo pixels are never copied into a shadow layer (rule in the spec): shadows are black fills whose shape and strength are measured.

## Procedure in PhotoCraft
1. Open the template in PhotoCraft (Portal `template_edit.open_in_photocraft(rel)`; port 7878).
2. Hide Place Artwork Here; screenshot the wall beside the art; write down angle, spacing, hard/soft, depth.
3. Edit the Light Shadow layer: draw the continued bars as a shape (or a transformed bar group), black fill, Gaussian blur to match, layer opacity = measured darkening, mask to the art quad.
4. Show the art again, render, compare to the wall shadows: a bar must line up with its wall continuation on both sides of the art.
5. Run the checker; judge from the render PNG, not the PSD placeholder.

## Status and known limits (be honest)
- Tony's bedroom (Boho floater) and office (bare canvas) test templates exist (2026-11-18). The AI draws the print area evenly lit on purpose, so the wall's bars stop at the art unless this skill's step 4 is applied.
- WORKING (Office, 2026-11-18): `Portal/app/light_pattern.py` (wired into `key_light`) now (1) RECTIFIES the wall with the canvas's own four corners, because a distant sun's bars are parallel on the wall but converge in the photo (fitting in photo space gave only soft blobs); (2) fits ambient + sun x column-profile x crossbar-profile in the flat view (vertical-bar angle from edge histogram, crossbar angle by search); (3) continues the bars over the canvas and warps back. Office window grid: fit rms 0.096, mullion bar and slanted crossbars line up with the wall's own bars. Limit MAX_FIT_RMS 0.14 (else it falls back to the old sun line).
- RULE (Tony 2026-11-18, physics): every shadow cast by one window onto the wall (post between panes, mullions, the big diagonal shadow that cuts the windows off) is the SAME darkness; shadows never stack where bars cross. `light_pattern.py` maps each fitted profile to shaded/lit and gives all shaded points one common level (COMMON shade, LIT_AT/SHADED_AT). Verify by sampling render luminance at the post vs the diagonal: they must match within a few percent (Office: 163 vs 166).
- WORKING (Boho bedroom blinds, 2026-11-18): the band model cannot hold thin slats (its crossbar angle is a few degrees off, so stripes wash out). `light_pattern._slats` measures them directly: high-pass the rectified wall, keep the one coherent sun-patch component (coherence along the stripe angle, not edges/leaves/macrame), re-pick the stripe angle on that patch alone (0.1 deg steps), fold the profile at the fitted period, rescale depth to the pixels' real 10-90 percentile contrast (the fold averages it away), and continue the periodic pattern from the patch's upper edge (`s_edge`) over the canvas. Bedroom 002116: 129.4 deg, period 19 px, depth ~0.2 log; stripes land only in the art's lower-left triangle, lines continue the wall's. Gotchas: median over a whole stripe line reads as "no stripes" (most of the line is un-striped wall); the full-wall angle search latched onto plaster texture until scored on fine band-passed variance.
- Open: the edge check still fails about 2 px on the Office template (separate from shadows).
- Open (2026-11-19): on Living Room Mid Century 233500 (soft window patches, NO blinds) the current builder's window-pattern fit returned "slats" (130 deg, period 27 px, opacity 0.6): fine stripes and a darker art that the wall does not have. When that template was rebuilt (white-bar fix) its Light Shadow was kept as the original sun line. A slat fit needs a check that the wall really shows stripes before it is trusted. The automatic free rebuild in Production (`production.rebuild_from_scene`) uses the current builder, so it can bring these slats in; its result waits for Tony's Approve.
- Update this section when a method is proven.

## Hard-won lessons (2026-11-18, Office canvas; read before touching any template shadow)
Tony had to correct this five times in one session. Do these without being told:
1. **Do the matching the way Tony does it, by eye on the wall, not by a fitted model alone.** Hide the art, look at the wall next to and BELOW the canvas, copy each shadow's shape, strength and softness. Numbers (luminance samples) are a check, never the judge; the render crops are.
2. **Physics rules he enforces:** shadows cast by one window are the same strength, they never stack where bars cross, and no shadow may look darker than its neighbour (post vs mullions vs the big diagonal shadow that cuts the windows off). A hard-edged band reads darker than a soft one at the same level, so the post is kept slightly LIGHTER (`POST_K = 0.8` in `light_pattern.py`), never darker. The winning render was Office `AI_Office_Scandinavian_20261118_225742` (post 173, diagonal 166, lit 210 in blurred luminance).
3. **Before saying "done", compare against the previous good render side by side** (three-up of old/previous/new at 1x and a 3-6x crop of every canvas edge, bottom especially). A fix to one area (the post) silently broke another (the bottom). Check the whole canvas, all four edges, every time.
4. **Do not build a pile of template folders.** Each rebuild saves a new folder. Rebuild once per real change, reuse the saved scene (no credits), and say which folder is final. Superseded ones go to the style folder's Archive (Tony deletes).
5. **Do not hand Tony a question he already answered or a quick diagnosis he can see.** When he says "still off", measure the specific region he named, compare against the wall, and fix it; if the first attempt was blind, show a 3-up of options instead of asking him to describe it.
6. **Placing a template in a slot** is not a question: when Tony names a slot, set `approved: true` + `approved_at` in the template's `template.json` (his chat approval counts) and run `production.start_slot` + `run_slot(con, settings, idea_id, slot, template_rel)` (free for a library template). Office 225742 is in Book Club Cat slot 11 (`11_Room_Office_Modern.jpg`, guard pass, 7.7% crop).
7. **Wall truth, for when you change the fit again:** on this wall the crossbar bars are lighter (thin, penumbra) than the post/top shade, there is a soft glow above the lit patches, and the vertical post is full shade. Flattening everything to one level needs the post pulled back (POST_K) to read right.
8. **Never ask which slot: read the plan.** The Production tab already assigns each room slot a room (`production._plan(...)` -> card room/decor/ratio). Put a template in the slot whose planned room matches it (Office = slots 11, 14, 18; Living room 3 is NOT for an office). Pick the first matching free slot yourself.
