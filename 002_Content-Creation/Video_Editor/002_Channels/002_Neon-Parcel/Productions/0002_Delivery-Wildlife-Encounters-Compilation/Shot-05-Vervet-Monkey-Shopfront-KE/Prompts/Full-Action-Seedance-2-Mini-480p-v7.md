---
saved: 2026-09-20 BEFORE submission
model: bytedance/seedance-2-mini (kie_market_api.py seedance_mini)
params: 480p, 14s, 16:9, audio on, reference_image_urls (no first/last frame)
references_in_upload_order: @Image 1 = Storyboard_v3.png; @Image 2 = Character_Sheets/Environment_Sheet_v2.png (full labeled sheet); @Image 3 = Character_Sheets/Courier_Character_Sheet_Skill_v2_BikeFixed_LabeledClean.png (title bar reads BICYCLE COURIER); @Image 4 = Character_Sheets/Vervet_Monkey_Character_Sheet_Skill_v3_LabeledClean.png (title bar reads VERVET MONKEY)
test (Tony 2026-09-20): send the LABELED character sheets to see whether the printed name links to the subject. Wording of the subject nouns deliberately left as in v6 ('courier'/'monkey') for this test; if it fails, align the prompt's names to the sheet labels (BICYCLE COURIER / VERVET MONKEY).
changes vs v6: camera POV panel is named by its printed title and pinned to the first frame; sheets are the labeled versions
output: Data/Seedance_Mini_v7_Labeled_Sheets.mp4
---

REFERENCE IMAGES:
@Image 1 = the storyboard for this shot. Follow its shot selection and panel order as one continuous uncut shot. It is a sequence of action instructions, not a collage or tiled layout to reproduce; never show its panels, borders, frame numbers or captions.
@Image 2 = the environment sheet for the shopfront where this whole clip takes place. The top-left panel, printed with the title "CAMERA POV" (panel 1), is the video camera's exact view: the video's first frame and every frame after it uses that panel's viewpoint, framing, distance and angle. The other panels (TOP-DOWN VIEW, REVERSE VIEW, LANDMARK DETAIL) show the same place from other angles for spatial reference only and are never the camera view. Never show its labels, callout boxes, text or layout.
@Image 3 = the character sheet titled "BICYCLE COURIER": his exact face, build, navy short-sleeve collared shirt, dark trousers, black sandals, black crossbody bag, and his dark-steel parcel bicycle. Never reproduce the sheet's layout, panels or its title text.
@Image 4 = the creature sheet titled "VERVET MONKEY": its exact grey-green fur, black face with white brow band, long tail, cat-sized body. Never reproduce the sheet's layout, panels or any of its text, including its title.

1. CAMERA LOCK
One fixed, static shopfront CCTV camera, placed facing the shop front exactly as in @Image 2 panel 1 and in every panel of @Image 1: a frontal view, slightly above eye level, looking slightly down. Frame layout, as in @Image 1: the shop front fills most of the frame; the wooden counter runs across the middle with goods behind it; the corrugated-iron awning is a fixed roof along the top of the frame; the awning support post stands at the left edge; the dirt apron fills the lower frame; the parked bicycle is at the right. The camera never moves, zooms, pans, tilts, re-frames or cuts, and no subject ever fills the frame. Modest consumer-CCTV dynamic range, no sharpening.

2. SCENE CONTINUITY
Exactly one @Image 3 courier, one @Image 4 monkey and exactly ONE bicycle in the whole clip; nobody else and no second bicycle. Clear hot midday sun, hard awning shadow, dry dusty apron. Scale: the counter top is about 1.0 m high; @Image 3 is about 1.7 m tall with his head well below the awning; @Image 4 is cat-sized, about 45 cm long, only slightly longer than the clipboard and about a quarter of @Image 3's height. Nothing ever lands, walks or lies on the awning roof. The parcel bicycle of @Image 3 stands upright on its kickstand on the apron at the right from the first frame to the last, never moving or floating. @Image 4 is perched on top of the awning post from the first frame. The clipboard is pale beige with a silver clip, one white sheet covering the whole board and a black pen on a short string, about 23 x 32 cm.

3. ACTION TIMELINE
[00:00-00:03] @Image 3 stands beside his parked bicycle on the apron of @Image 2 holding the clipboard, then walks to the counter still holding it. @Image 4 watches from the top of the awning post.
[00:03-00:05] @Image 3 stands at the counter of @Image 2, sets the clipboard flat on the wooden counter top at its edge, and turns his head and shoulders toward the shop interior with his back to the post. The clipboard stays on the counter top.
[00:05-00:07] @Image 4 leaps from the top of the awning post straight down beside the post onto the wooden counter top, a drop of about 1.3 m, and lands on the counter next to the clipboard. The counter top is its only landing surface.
[00:07-00:09] @Image 4 crouches on the counter top, reaches out both hands, picks the clipboard up off the counter (it takes hold of it here, not before), and drags the attached pen back and forth across the paper in a quick scribble like signing, glancing at @Image 3.
[00:09-00:11] @Image 3 turns back, startled, and lunges an open hand toward @Image 4; @Image 4 pulls the clipboard just out of his reach with a weight shift and a tail flick.
[00:11-00:14] @Image 4 scrambles back up the awning post carrying the clipboard and perches on top clutching it against its chest, while @Image 3 stands at the counter of @Image 2 with empty hands half-raised, looking up.

4. AUDIO
Natural location sound only, small-shop CCTV microphone quality: dry midday ambience, footsteps on dirt, the clipboard clacking on the wooden counter, quick monkey chatter and scrabbling on the post and awning, the courier's startled exclamation with no intelligible words.

5. HARD CONSTRAINTS
- No dialogue, voiceover, music or soundtrack; no on-screen text, captions, frame numbers or logos
- No storyboard grid, panel borders or sheet layout in the video
- Exactly one courier, one monkey, one bicycle; no other people, animals or bicycles
- The bicycle never floats, moves or is ridden
- No camera movement, zoom, push-in or re-framing
- The clipboard sits on the counter top until @Image 4 visibly picks it up; it is never on the awning roof, ground or a shelf, and never vanishes; the pen stays attached
- Nothing lands on or walks across the awning roof; no roof-to-roof jump
- @Image 4 is never person-sized and never appears from nowhere: it starts on the post, leaps down, and returns up the post
