# Grounding Coverage Check — Shot 07 (summary; every sheet call carried the Phase 1/2 facts from Research/Plausibility_Facts.md)
- Fishmonger sheet: apron/boots/no-branding, van setting -- all present. Walrus/van excluded (separate sheets).
- Walrus sheet: subadult size correction, just-emerging tusks, no external ears, front-flipper drag, damp skin -- all present as anatomy_notes + description.
- Van sheet: kei-truck-proportioned cab + UK box body, roller shutter (not barn doors), stowed/folded lift gate (never deployed), no logos -- all present; front/back/open-door/broadside panels cover every orientation the storyboard will need.
- Environment sheet: van's diagonal parking path (rear toward camera) corrected once (v1 was broadside) and carried into panels 1-2; shop window with fish/shellfish, doorway, lamp post all present.

## 2026-09-22, Environment sheet v2 (harbour quay, Tony's layout): one check per call
- **Top-down v3:** quay facing the bay, road across frame, nose-in parking row with the van dead centre (front to water, rear to road, by literal parts), adjacent spaces empty, hatchback two left, fish boxes right, quay wall + railing, slipway far left, moored boats, breakwater, far-shore cottages, stone not brick: all present. People, animals and fishmonger excluded (empty-location rule). Walrus/ice/fish heads excluded (action, not set). Result PASS on the first generation.
- **Reverse v3 → v3b:** camera building with the CCTV above the door, empty centre space, hatchback, fish boxes, road: all present. v3 showed the hatchback's rear toward the water side (wrong for nose-in); v3b is a one-change fix, front now faces the viewer. Minor: a small car badge on the hatchback grille (reference panel only).
- **Camera POV v3:** the fixed wide CCTV view, road off both edges (van entry at right), empty centre space directly ahead, hatchback two left (rear to camera), fish boxes right, quay wall + railing, slipway far left, boats, breakwater, cottages, hills, overcast damp: all present. Van excluded on purpose (frame 1 is before it arrives). PASS on the first generation (the API call timed out, but the same task was polled to completion, not re-paid).
- **Landmark detail v3:** van's space + quay wall, slipway, van rear (door closed, lift stowed, from the approved van sheet), fish boxes + rope: all present. PASS.
- **Deterministic overlay:** the van's path arrow on the top-down was drawn with PIL, not by the image model. The first draw curved the wrong way and was discarded; the second follows Site_Plan v2 exactly.

## 2026-09-22, Storyboard Clip 1 v1 (Data/Storyboard_Spec_Clip1_v1.json, rendered by storyboard_contract.py)
- Walrus: subadult 2.0-2.3 m, fills most of the box, grey-brown wrinkled skin, white whisker pad, small just-emerging tusks, no external ears, heaves on its front flippers: present. Stowaway origin: present (inside the closed box from the start; the harbour stow-away itself is off-screen by design).
- Van: kei-truck-proportioned white cab, white refrigerated box, reefer unit on the front of the box, roller-shutter door rolling UP, tail lift folded throughout (never deployed), UK right-hand drive with the driver exiting on camera-right: present. Nose-in, rear to camera, by literal parts: present.
- Fishmonger: face/build/grey hair, navy knit jumper, navy oilskin bib apron, black wellingtons, no branding: present (via sheet + reference line).
- Spill: crushed ice cascading onto the road behind the van, fish heads only, no blood: present.
- Location: every Site_Plan v2 landmark (road off both edges, centre space, hatchback two left, fish boxes right, quay wall + railing, slipway far left, boats, breakwater, cottages): present via the camera_lock + env sheet reference.
- Audio: burp, grunts, ice clatter, shutter rattle, gulls, water; no music or speech: present.
- Intentionally excluded: the walrus entering the water (that's Clip 2, the WaveSpeed extend).

## 2026-09-23, Video Clip 1 v1 (Prompts/Clip-1-Seedance-2-Mini-480p-v1.md, Kie Seedance 2 Mini, 480p, 15 s)
- Every storyboard-coverage fact above: present. Plus Tony's storyboard notes: the driver's door is shut before the rear door opens; real-world scale with numbers (fishmonger ~1.8 m, walrus 2.0-2.3 m, fits the box); the wide framing holds, no zoom (the storyboard's later panels are called out as drawn too close); the hatchback stays parked (the storyboard's frame 6 omission is overridden in the constraints).
- Refs (gate dry-run PASS): @1 Storyboard_Clip1_v1, @2 Environment_Sheet_v2, @3 Fishmonger (FISHMONGER), @4 Walrus (WALRUS), @5 Van (DELIVERY VAN). Routing: seedance_2_mini_storyboard, score 16/20, enhanced QA, hard trigger.
- Intentionally excluded: the walrus entering the water (Clip 2, WaveSpeed extend).
