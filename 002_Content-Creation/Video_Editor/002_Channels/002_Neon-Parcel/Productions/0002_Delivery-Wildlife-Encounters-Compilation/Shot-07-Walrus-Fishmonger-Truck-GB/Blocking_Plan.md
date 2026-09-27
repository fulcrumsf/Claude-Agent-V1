---
title: "Shot 07 — Blocking & Capture-Device Plausibility Pass (v2)"
shot: "A fishmonger's small refrigerated van pulls into a quayside parking space facing the bay; opening the rear roll-up door reveals a stowaway subadult walrus that ate the fish delivery, which slumps out in a cascade of ice and fish heads and heads for the water"
device_type: fixed-mounted-static
locked: 2026-09-22
revision: "v2, 2026-09-22 — rewritten to Tony's layout (camera overlooks the bay, parking space directly in front, van drives in from frame-right and turns right into it). v1 (shopfront street) kept at Data/Blocking_Plan_v1_Superseded.md."
---

# Blocking Plan

**Device type: fixed/mounted static harbourside CCTV.** Nobody operates it; nothing pans, tilts or zooms. The subject includes a moving vehicle entering frame, so its full path is planned in `Data/Site_Plan.md` (v2).

## Fixed frame
Camera mounted about 3 m up on the front wall of a harbourside stone building (the premises receiving the fish delivery), wide-angle security lens, looking straight out across the harbour road and the quayside parking row to the bay. Overcast midday, damp stone and tarmac, no current rain.
- **Foreground:** the harbour road running left-right across the whole frame.
- **Centre:** the empty quayside parking space directly in front of the camera, where the van ends up.
- **Beyond:** the low stone quay wall with an iron railing, calm harbour water with moored fishing boats, the stone breakwater, and the far shore with whitewashed and stone cottages and hills.
- **Far left:** a stone slipway down into the water (the walrus's exit).
- **Right edge:** where the van enters from off-frame.

## Vehicle entry path (per the Site Plan)
The van enters from frame-right in the near lane, drives straight toward screen-left, then turns right, away from the camera, and pulls nose-first into the space directly in front of the camera. It stops short of the quay wall, its front toward the water and its REAR ROLLER DOOR facing the camera square-on. Engine off; it never moves again. A real drive-in-and-park, not a jump-cut to "already parked."

## Subject origins (nothing appears from nowhere)
- **Van:** enters from off-frame right at frame 1.
- **Fishmonger:** driving the van (UK right-hand drive); gets out of the driver's door on the camera-right side only after it's parked.
- **Walrus:** already inside the closed cargo box from frame 1. It snuck in earlier at the harbour (off-screen) and ate the fish delivery during the drive. It only becomes visible when the fishmonger rolls the rear door up.

## Beats (one continuous uncut shot)
1. Van drives in from frame-right along the harbour road, turns right, and parks nose-in in the space directly in front of the camera, rear door facing the camera.
2. Fishmonger gets out of the driver's door (camera-right side) and walks back along the side of the van to the rear.
3. He rolls the rear roller-shutter door up.
4. Inside: the walrus, lying in a bed of crushed ice, surrounded by fish heads (everything else eaten). The fishmonger startles and jumps back toward the camera, hand raised.
5. The walrus burps once, then heaves itself forward and slumps out of the doorway, over the lip of the folded tail lift and down onto the road. It's so big that it pushes a cascade of crushed ice out with it, which tumbles onto the road with fish heads scattered through it.
6. The walrus turns to its left and heaves along the road toward the slipway at the far left, exiting frame-left toward the water. The fishmonger is left standing by the empty van, with a pile of ice and fish heads on the road. No blood anywhere.

## Grounding carried into every prompt (from Research/Plausibility_Facts.md)
Walrus: subadult, ~2.0-2.3 m, several hundred kg, grey-brown wrinkled skin, dense white whisker pad, small just-emerging tusks, no external ears, rolling/heaving gait on land. It should look huge inside the van's cargo box: filling most of it. Van: kei-truck-proportioned cab, UK-scale refrigerated box body, roll-up rear shutter door, hydraulic tail lift folded/stowed (never deployed), right-hand drive. Ice + fish heads only, no blood. Fishmonger: per his approved sheet (navy knit jumper, navy oilskin bib apron, black wellingtons).

## Tone / capture / audio
Unplanned real-life harbourside CCTV footage, ordinary and observational. Audio: natural location only: the van's engine and door, the roller shutter's rattle, the walrus's burp and grunts, ice sliding and clattering onto tarmac, the fishmonger's startled exclamation (no intelligible words), gulls, lapping water. No dialogue, music or voiceover.

## Hard constraints
Exactly one fishmonger, one walrus, one van (plus the one empty parked hatchback as set dressing); no other people or animals. The van's path is continuous (enters, drives straight, turns right, parks) with no teleporting. The tail lift stays folded throughout. No blood, only ice and fish heads. Stone, not brick. No camera movement, no on-screen text or logos.

## Two-clip generation plan (Tony, 2026-09-22)
- **Clip 1 (Kie Seedance 2.0 Mini, up to 15 s, the normal winning-formula call):** storyboard + full labeled environment sheet + fishmonger, walrus and van sheets, every beat tagged. Covers beats 1-5 and the start of 6: drive-in and park → door up → startle → burp → slump-out with the ice and fish-head cascade → walrus heaving toward the slipway. Ends with the walrus at the top of the slipway.
- **Clip 2 (WaveSpeed Seedance 2.0 Mini Video Extend, approved by Tony for this step):** input = Clip 1 + a continuation prompt + an end frame (`last_image`): the walrus in the harbour water off the bottom of the slipway, the fishmonger by the open van, the ice pile on the road. The end frame is generated AFTER Clip 1 exists, from Clip 1's real last frame, so the van, fishmonger and ice pile match. The extend model takes no reference sheets; that's accepted for this step. Confirm the cost with Tony before the call.
