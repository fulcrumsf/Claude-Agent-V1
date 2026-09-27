---
model: gpt-image-2 (kie.ai image-to-image)
params: 16:9, 2K
refs: 1 = Data/Env_Panel_1_TopDown_v3.png (layout source of truth), 2 = Data/Env_Panel_2_Reverse_v3b.png (same quay from the opposite side), 3 = Data/Fishmonger_Sheet_Harbour_BG_Crop_A.png (approved harbour look), 4 = Data/Fishmonger_Sheet_Harbour_BG_Crop_B.png (approved harbour look)
saved: 2026-09-22 BEFORE submission
reason: v3 Camera POV per Tony: CCTV overlooking the bay, parking space directly in front, van will enter from frame-right. Chained from top-down v3 and reverse v3b. Empty scene (frame 1 before the van arrives).
---
Reference image 1 is the top-down site plan of this Scottish harbour quay and is the source of truth for every position: in it, the camera sits at the BOTTOM edge looking UP. Reference image 2 is the same quay photographed from the water side looking back at the camera building (left and right are swapped in it). Reference images 3 and 4 are the approved look of this production's harbour: match their stone, railings, water, boats, whitewashed and stone cottages with slate roofs, green-brown hills and flat overcast light.

Generate the view from a fixed CCTV security camera mounted about 3 metres up on the front wall of the stone harbourside building at the bottom of reference image 1, looking straight out across the harbour road and the quayside parking toward the bay, tilted slightly down. A real security camera's wide-angle view (about 90 degrees across) with only mild lens curvature: straight lines like the quay wall and parking lines stay nearly straight. Ordinary, flat, slightly soft CCTV image quality, overcast midday, everything damp.

Layout, near to far, matching reference image 1:
1. Bottom of the frame: the far kerb of the flagstone pavement, then the two-way harbour road of wet dark tarmac with patches of old granite setts, running left-right across the full width of the frame and continuing off BOTH edges (a vehicle can drive in from off-frame right).
2. Middle of the frame: the row of nose-in parking spaces with faint worn white lines, seen from behind. The space in the exact horizontal CENTRE of the frame, directly in front of the camera, is EMPTY. The space immediately to its left is empty and the space immediately to its right is empty. One small dark hatchback is parked nose-in two spaces to the LEFT of centre: we see its REAR (tail lights, rear window) because its front faces the water. A short stack of blue plastic fish boxes and a coil of rope sit against the quay wall well to the RIGHT of centre.
3. Beyond the parking: the low rough grey-brown dressed-stone quay wall with a black iron railing on top, running the full width of the frame.
4. FAR LEFT of the frame: a gap in the quay wall where a stone slipway slopes down from road level into the water, away from the camera.
5. Beyond the wall: calm grey harbour water, two or three small fishing boats moored in the middle distance, one small boat tied against the quay wall to the right of centre.
6. Distance: the curved stone outer harbour wall/breakwater on the left; on the right, the far side of the bay with a waterfront row of whitewashed and grey-stone cottages with slate roofs; low green-brown hills behind under a flat grey sky.

Constraints: no people, no animals, no birds; no van and no moving vehicles (the scene is empty before the van arrives); no text, signs, timestamps, labels, numbers or logos anywhere; stone throughout, no brick; parking spaces are clean rectangles, not wedges; the centre space must be empty and directly in front of the camera; no watermark.
