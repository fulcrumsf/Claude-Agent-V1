---
model: gpt-image-2 (kie.ai image-to-image)
params: 16:9, 2K
refs: 1 = Data/Env_Panel_1_TopDown_v3.png (layout source of truth), 2 = Research/Reference_Images/Harbour_Stone_Quay_Stonehaven_01.jpg (real stone harbour-front buildings), 3 = Data/Fishmonger_Sheet_Harbour_BG_Crop_B.png (approved harbour look)
saved: 2026-09-22 BEFORE submission
reason: v3 reverse view, chained from top-down v3. Spatial reference only (not camera output): shows the camera building and the CCTV mount from the water side.
---
Reference image 1 is the top-down site plan of this Scottish harbour quay and is the source of truth for every position. Reference image 2 is a real Scottish harbour-front row of stone buildings. Reference image 3 is the approved look of this production's harbour (stone, whitewash, slate, wet tarmac, overcast).

Generate a photorealistic eye-level photograph taken from ON the quay, standing just inside the iron railing by the quay wall, looking BACK across the parking row and the harbour road toward the building at the bottom of reference image 1. Standard 50mm-equivalent lens, no wide-angle distortion. Overcast midday, everything damp.

What must be in the frame, matching reference image 1:
- Foreground: the row of nose-in parking spaces with faint worn white lines, seen end-on. The space directly in the centre of the frame is EMPTY (the van is not here yet). One small dark hatchback is parked nose-in two spaces to the RIGHT of centre in this view (because this view faces the opposite way to the top-down, left and right are swapped). No other vehicles.
- Middle: the two-way harbour road of wet dark tarmac with patches of granite setts, running left-right across the frame.
- Background, directly facing the camera across the road: a two-storey harbourside building of rough grey-brown dressed stone with a slate roof and a plain dark wooden door with a small window beside it, and a narrow flagstone pavement in front of it. Mounted on the stone wall about 3 m up, just to one side of the door, is a small white box-style CCTV security camera pointing out toward the harbour (toward this viewpoint). Neighbouring buildings on either side are whitewashed or grey stone with slate roofs.
- Far left edge of the frame: the stack of blue plastic fish boxes and a coil of rope by the quay wall (they are on the right in the top-down; left here because the view is reversed).

Constraints: no people, no animals, no birds; no text, signs, labels, numbers or logos anywhere; stone throughout, no brick; the centre parking space must be empty; parking spaces are clean rectangles, not wedges; no watermark.
