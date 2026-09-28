# Continuity Flags — Storyboard Clip 1 v1 (logged, not auto-regenerated)
Refs sent (GPT-Image-2, kie.ai, 16:9, 2K, task d11699f51370dd72a3ab56a26a84974c): 1 Fishmonger_Character_Sheet_v1_Titled, 2 Walrus_Creature_Sheet_v1_Titled, 3 Van_Prop_Sheet_v1_Titled, 4 Environment_Sheet_v2. Prompt: Prompts/Storyboard-Clip-1-GPT-Image-2-v1.md (rendered from Data/Storyboard_Spec_Clip1_v1.json).

- 🔴 Frame 6: the parked hatchback has disappeared; the walrus is lying where it was parked. Present in frames 1-5.
- 🟠 The slipway isn't visible in any frame (the left edge shows parking and quay wall only). In frame 6 the walrus is heading left along the parking row but doesn't clearly reach the top of a slipway, and Clip 2 needs that ramp to go down into the water.
- 🟡 The hatchback is parked in the space right next to the van, not two spaces left. Consistent across frames 1-5, so harmless.
- 🟡 Frame 4: the fishmonger leaps several metres toward the camera; in frame 5 he's back beside the van. Exaggerated but readable.
- 🟡 Frame 4: fish heads aren't readable inside the box (only ice). Frames 5-6 show them clearly in the spill.
- ✅ The van path reads correctly: in from the right (1), turning (2), parked nose-in with the rear to the camera (3-6). The reefer unit is on the front of the box, the door rolls up, and the tail lift stays folded. The walrus reads huge in the box with small tusks and no ears. No blood. One fishmonger, one walrus, one van. The camera is fixed in all 6 frames.
- Body-orientation checker (YOLO-pose, per-frame crops): fishmonger TOWARD_CAMERA in frames 3-6 (walking back toward the rear, then facing the camera/walrus side). No flip; consistent.

## Tony's review, 2026-09-22: storyboard Clip 1 v1 APPROVED as is, with notes for any redo
- Frame 3: the driver's door is still open; in frame 4 it's closed. Intent: he gets out and CLOSES the door behind him.
- Frames 4-6: the fishmonger looks too large; frame 5: the walrus looks overbearingly large and out of proportion. Intent: real-world scale (a normal adult man, a ~2.0-2.3 m subadult walrus).
- Frames 4-6 look zoomed in compared with frames 1-3 (confirmed: the boats and cottages are larger). Intent: the same fixed CCTV framing and zoom as frame 1 for the whole clip.
- These go into the Clip 1 video prompt as explicit constraints, and into any storyboard redo.

## Video Clip 1 v1, 2026-09-23: FAILED QA (sheet reproduction)
- 🔴 The whole clip plays as a tiled grid of small panels (about 3 across), each a separate mini-scene, with some larger elements overlapping, instead of one continuous CCTV shot. It's the storyboard-layout contamination the pipeline's Reference Routing Contract warns about. Not upscaled, not sent to extend.
- The content inside the panels was otherwise on-script (the van arrives, the door opens, the walrus slumps out on ice, the fishmonger stands aside, the hatchback stays), so the prompt and sheets read correctly; the failure is the layout.

## Storyboard Clip 1 v2, 2026-09-23 (attempt 2 of 3; task c3b22573be2d8ef35605b37c1161180f; same 4 labeled refs)
- ✅ Zoom is the same in all 6 panels (the boats, cottages and breakwater match in size and position). The hatchback is present in all 6. Frame 3: the driver's door is shut and he's walking to the rear. The fishmonger is realistic-sized (about one-fifth of the frame height). Frame 4: one step back, not a leap, with fish heads visible around the walrus. The walrus fits inside the box. Frames 5-6: clear ice cascade with fish heads. The slipway ramp shows faintly at the far left in every panel.
- 🟡 The van is drawn about 1.5x wider in frames 4-6 (and 2) than in frame 3, even though it hasn't moved. The background stays the same size, so it's the van, not a zoom.
- 🟡 Frame 6: the walrus is heading left past the hatchback's rear but hasn't reached the top of the slipway yet (the video prompt carries the end state).
- Body-orientation (YOLO-pose): fishmonger TOWARD_CAMERA in frames 3-6; no flip.

## Video Clip 1 v2, 2026-09-23: FAILED QA (sheet-template reproduction / label bleed)
- 🔴 Every frame sits inside the dark sheet presentation frame: a garbled title bar at the top ("CREATURE SHEET ... VAN"), a numbered panel badge and a border. The grid is gone (a single view) and the action is on-script: the van arrives and parks, he gets out, rolls the door up, the walrus is revealed in ice, it slumps out in an ice-and-fish-head cascade, and heads left; the hatchback stays and the zoom stays steady.
- 🟡 The walrus is still on the large side on the road. At 15 s it hasn't reached the slipway (it's heading left).
- The inner scene area is about 749x420 (16:9) at x57-806, y52-472, so it's salvageable by cropping if Tony chooses.

## Clip 2 end frame (last_image for the WaveSpeed extend), 2026-09-23
- v1 (task 07db7b68..., after one provider timeout on 255813b4...): 🔴 zoomed in (the van about 2x larger than in Clip 1's last frame) and whole fish instead of fish heads. Not used.
- v2 (task 8a4d8f81...): ✅ framing matches Clip 1's last frame (same wide view, van the same size and place); the walrus is swimming in the harbour just off the quay wall at the left, head above water with ripples, by the slipway/steps; the hatchback is fully visible; the ice pile matches Clip 1 (Clip 1's own fish read as fairly whole, and the end frame matches that). 🟡 The fishmonger is facing the van rather than turned toward the water.

## Clip 2 (WaveSpeed Mini extend) v1, 2026-09-23: FAILED QA
- ✅ The join at 15 s is seamless; the fishmonger, van, ice pile and hatchback stay consistent; the camera stays fixed.
- 🔴 About 17.5-21 s: instead of reaching the slipway, the walrus dives into a pool of water that appears on the tarmac beside the hatchback, then swims in that puddle. The model met the end frame (walrus in water, lower left) by putting water on the road. Cause: the walrus is in the foreground and the slipway/water is far behind it, too far to cover plausibly in 6 s, and the end frame pulled the water toward it.

## Clip 2 (WaveSpeed Mini extend) v2, 2026-09-23: railing exit, no end frame (Tony's idea)
- ✅ The join at 15 s is clean; the walrus heaves up the empty space between the hatchback and the van, rears at the railing, flops over it (the railing stays intact), and splashes into the harbour beyond the wall (~20.7 s); the road stays dry; the fishmonger watches, then looks down at the ice; the camera is fixed; audio has the grunt and splash. Gemini evidence pass: confidence 0.95, no error findings.
- 🟡 At the railing the walrus rears almost fully upright on its hind flippers, which a real walrus can't do. It reads as comedic.
- 🟡 The spilled fish read as whole fish, not just heads (Gemini noticed too). This comes from Clip 1, so the extend didn't cause it.
