---
title: "Neon Parcel Production Report Card"
type: report
tags: [report, neon-parcel, seedance-2.0-mini, wavespeed-extend, magnific, storyboard]
---

# Shot 07 — Walrus in the Fishmonger's Van (Scottish harbour quay)

**Grade: B+ (Tony, 2026-09-23). APPROVED, FINAL. No further spend on this shot.**

Tony's own words, summarised: the action and the comedic beats are a B+, and overall it's a B+. What would make it an A is **scale**: the van, the fishmonger and the walrus are about **1.5-2x too large** for the environment (the van looks huge next to the parked car), and **the van doesn't pull all the way into its parking space**. He doubts viewers care much, since it's obviously AI and meant for humour, but for realism everything has to be on the same scale as the environment.

## What ran, in order
1. Concept (dictated by Tony), Diversity Matrix, concept filters: "large walrus" changed to a subadult (2.0-2.3 m) to fit the van; Tony confirmed ("large" meant large inside the truck).
2. Grounding Audit, reference photos (walrus, kei truck, box van; later 6 Scottish harbour photos).
3. Sheets: fishmonger (hand gate 4/4), walrus, van, all approved first time.
4. Environment sheet v1 (village shopfront street) **rejected**: wrong layout. Tony wanted a harbour quay facing the bay, a parking space directly in front of the camera, and the van driving in from the right and turning right into it. The Blocking Plan and Site Plan were rewritten; Environment Sheet v2 was built top-down first (one fix: the hatchback's orientation in the reverse view) and approved.
5. Two-clip plan (Tony): Clip 1 = Kie Seedance 2 Mini with all references, up to 15 s; Clip 2 = WaveSpeed Seedance 2.0 Mini Video Extend (no sheets, accepted by Tony).
6. Storyboard v1: approved with notes, then **redone** at Tony's request (the fishmonger and walrus too large, frames 4-6 zoomed in, the driver's door left open). Storyboard v2 fixed all of these (attempt 2 of 3) and was approved.
7. Clip 1 video v1 (storyboard v1): **failed**, the whole clip was a tiled grid (storyboard-layout reproduction). My prompt had added a sentence about "later panels" and changed "every panel of @Image 1" to "panel 1 of @Image 1", departing from the v7 template.
8. Clip 1 video v2 (storyboard v2, template wording restored): action on-script and a single view, but **wrapped in a sheet presentation frame** (garbled title bar, badge, border). **Salvaged by cropping** (Tony's option 1): an FFmpeg crop to the clean 746x418 inner area, verified across all 15 s.
9. Clip 2 end frame: v1 zoomed in, with whole fish; v2 matched the framing (one provider timeout in between, no charge).
10. Clip 2 extend v1 (with the end frame, slipway route, 6 s): **failed**, the walrus dived into water that appeared on the tarmac.
11. Clip 2 extend v2 (Tony's idea: between the hatchback and the van, over the railing; **no end frame**, 8 s): **passed**, with a clean join, the railing intact, the splash beyond the wall and a dry road. Gemini evidence pass: 0.95, no error findings.
12. Upscale (Tony's one-off choice, skipping Kie Topaz): the Magnific basic API **failed** server-side ("1/2 chunks did not succeed"). Then, via the **Magnific MCP**: **Topaz Astra 2**, 1920 wide, creativity **0.3** (lowered from 0.5 to protect faces), realism 0.5, sharpness 0.5, 5,580 credits. Face check: the fishmonger's face is clean and consistent, no warping, far sharper than raw. Then the pipeline FFmpeg normalize to 1920x1080 (about 20 px side bars from the 1920x1102 source).

## Tony's grade notes (lessons for future cells)
- 🟠 **Scale drift is the main thing between B+ and A:** the van and characters render about 1.5-2x too large relative to the environment (parked cars, parking bays, quay). Prompts gave numeric scale, but Seedance still inflated it. Future cells need a stronger scale anchor (e.g. state sizes relative to fixed objects in frame: "the van is the same width as the hatchback plus half", "fills one parking bay"), and the storyboard must show correct scale first.
- 🟡 **The van doesn't fully enter its bay.** Park-into-the-space needs its own explicit end state ("its rear bumper ends level with the ends of the white bay lines").
- ✅ Action and comedic beats are solid; the railing exit was Tony's own fix and worked.

## Process lessons (mine)
- Don't add extra instructions about "panels" to the `@Image 1` line or the Camera Lock. Keep the v7 template wording word for word (both Clip 1 failures were layout reproduction).
- The sheet-frame reproduction was salvageable by cropping, since the scene sat inside a clean 16:9 area.
- For the WaveSpeed extend, an end frame showing a distant state (water behind the quay wall) got pulled onto the foreground. Without an end frame, and with a short, physically local route, it worked.
- The WaveSpeed CLI upload aborts at about 10 s for multi-MB files; host the inputs on Cloudinary instead (worked).

## Assets
- **Final: `Data/Shot07_Full_v2_1080p_FINAL_NoBars.mp4`** (1920x1080, 23.07 s; scaled to fill and cropped 11 px top and bottom per Tony, no side bars)
- Superseded: `Data/Shot07_Full_v2_1080p_FINAL.mp4` (pipeline pad version, ~20 px side bars)
- Upscale master: `Data/Shot07_Full_v2_Topaz_Astra2_1920.mp4` (1920x1102)
- Raw joined: `Data/WaveSpeed_Mini_Extend_Clip2_v2.mp4` (23.07 s)
- Clip 1 salvaged: `Data/Seedance_Mini_Clip1_v2_Cropped.mp4`
- Failed, kept: `Data/Seedance_Mini_Clip1_v1.mp4`, `Data/Seedance_Mini_Clip1_v2.mp4`, `Data/WaveSpeed_Mini_Extend_Clip2_v1.mp4`

## Upscale finding: NOT a pipeline default (Tony 2026-09-23: Magnific was a one-off; don't write it into the pipeline, to save Magnific credits; he'll decide later)
- Kie's Topaz exposes only a scale factor (1/2/4): no model, sharpness or face settings. That explains the soft, face-warping results; no setting can fix it.
- The Magnific MCP exposes full Topaz (13 models incl. Astra 2 and the face-focused Iris) with Astra creativity/realism/sharpness. Astra 2 at 0.3/0.5/0.5 gave clean faces on this shot. Our `upscale_video.py` doesn't support this route yet.
