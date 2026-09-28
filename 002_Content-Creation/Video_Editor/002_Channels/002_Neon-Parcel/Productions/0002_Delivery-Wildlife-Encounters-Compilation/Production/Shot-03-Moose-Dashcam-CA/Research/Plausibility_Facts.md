---
title: "Shot 03 (Moose/Dashcam, CA) — Grounding Audit"
locked: 2026-09-19
format: "Two-phase Grounding Audit (Neon_Parcel_Longform_Compilation_v2/SKILL.md, redesigned 2026-09-18): Phase 1 self-questioning elaboration, Phase 2 structured 5-column check."
---

# Matrix Cell (input to this audit)

| Axis | Value |
|---|---|
| Era | Present day |
| Region/culture | Northern Ontario, Canada — rural boreal-forest highway corridor |
| Delivery/service type | Parcel van driver |
| Animal species | Moose (calf, ~6 months old; mother implied nearby, off-frame) |
| Time of day | Early morning |
| Capture-device type | Dash-cam, mounted on the delivery van |
| Weather | Light snow |

# Phase 1 — Self-Questioning Elaboration

Generated fresh from this specific matrix cell, not from a template:

1. **"Northern Canada" is too vague to generate anything real from — which
   specific region?** True far-north (Yukon/NWT/Nunavut) has minimal
   standard parcel-van infrastructure — most delivery there is by air or
   infrequent truck. A rural **Northern Ontario boreal-forest highway
   corridor** (e.g. the Chapleau/Wawa/Timmins area, Highway 101 corridor)
   is the realistic setting: real road infrastructure, real parcel service,
   and — importantly — this exact region is a well-documented
   moose-vehicle-collision corridor in Ontario, which makes the premise
   itself plausible rather than invented. Conclusion: rural Northern
   Ontario boreal highway, not true far-north Canada.
2. **"Parcel van driver" — which service is actually realistic on a rural
   Northern Ontario route?** Canada Post operates under a universal-service
   mandate covering rural and remote addresses, making it the most
   plausible year-round carrier here — more so than Amazon Logistics
   (mostly urban/suburban network in Canada) or a courier aggregator (no
   density to support one this far out). Conclusion: a generic,
   **unbranded** red/white liveried parcel van in the visual spirit of a
   rural Canadian mail vehicle — never reproduce a real carrier's actual
   logo/trademark.
3. **What does the vehicle itself look like?** A rural single-driver route
   uses a mid-size cargo van (Ford Transit/Sprinter-class), not a large box
   truck — matches the actual scale of a rural delivery route, not a
   hero-vehicle default.
4. **"Moose calf, mother off-frame" — what does this actually mean for
   scale and season?** Moose calve in May; paired with the "light snow"
   weather axis (early autumn/first snow), this calf is realistically
   **~5-6 months old** — a true yearling requires surviving to the
   following spring, which this calf hasn't reached yet, so "yearling" was
   the wrong term (corrected here from an earlier draft of this audit).
   Still notably smaller than an adult, but not tiny — moose calves grow
   extremely fast. Concrete scale: a ~6-month-old moose calf stands roughly
   4-5 ft at the shoulder versus an adult cow's ~6-6.5 ft, and critically,
   **has no antlers at all regardless of sex** at this age (unlike a true
   yearling bull, which may have small "button" spikes) — this must be
   stated explicitly in the character sheet, not left ambiguous.
5. **Would a real driver get out of the vehicle to interact, the way the
   Shot 02 delivery driver approached the kangaroo on foot?** No — this is
   a real, documented safety difference between the two species. Official
   Ontario/Quebec wildlife guidance for a moose encounter, especially with
   a calf (implying a cow may be nearby even off-frame), is to
   **stay inside the vehicle, do not approach, do not exit.** Moose can
   bluff-charge or become defensive, unlike the kangaroo shot's calmer
   real-world precedent. Conclusion: the driver never exits the van in this
   shot — a real behavioral/safety constraint, not a production shortcut,
   though it does simplify the shot (no full driver character sheet is
   needed if the driver's body is never in frame — see Phase 2).
6. **"Dash-cam" — what does that device convention actually look like,
   and does it conflict with the pipeline's no-on-screen-text rule?** Real
   dash-cams record continuously (not motion-triggered like the Shot 02
   doorbell cam), forward-facing, moderate wide-angle, and very commonly
   burn in a date/time/speed telemetry bar at the bottom of frame. That
   telemetry text is a real, authentic feature of the format — but this
   pipeline's hard constraint against on-screen text exists because AI
   video models render burned-in text as garbled gibberish, not because
   real dashcams lack it. Conclusion: **do not ask the generation model to
   render the telemetry overlay.** If wanted for realism, it gets added
   afterward as a separate deterministic compositing step (same principle
   as labels on the environment sheet), never inside the Seedance prompt
   itself.
7. **What is the light/road condition actually doing at "early morning" +
   "light snow" in this setting?** Pre-dawn/dawn light, overcast (snow
   implies cloud cover, not clear skies), low ambient light with the van's
   own headlights likely providing meaningful illumination, a thin fresh
   layer of snow on the road surface and shoulder, boreal spruce/pine
   treeline close on both sides of the road.
8. **What kind of road specifically?** A two-lane rural paved highway
   bordered by dense boreal forest, not a gravel logging road or a
   multi-lane highway — matches the real moose-crossing-signage corridors
   this setting is grounded in.

# Phase 2 — Structured Check

| Entity | Scale reference | Arrival/mobility | Motion/behavior nuance | Era/region-appropriate form | Plausible presence |
|---|---|---|---|---|---|
| Moose (calf, ~6 months) | ~4-5 ft at the shoulder, stated explicitly against the road's lane-width and the van's hood/headlights as in-frame scale references — not adult-moose or "baby animal" proportions. | Walks out of the treeline onto or alongside the road under its own power — no vehicle/logistics question applies. | The "pause" beat needs a real physical tell — head lift/ear rotation toward the van, a weight shift before it resumes moving — not a frozen pose. Mother moose is narratively nearby (Phase 1) but never rendered in-frame. | Real wild coloration/proportions for a moose calf (*Alces alces*), gangly/leggy build rather than a stocky adult silhouette. | Moose-vehicle encounters on rural Northern Ontario highways are a genuine, well-documented, signposted real phenomenon — this is the most grounded premise in this pipeline so far. |
| Parcel delivery van (and driver, never exiting) | Ordinary mid-size cargo van scale — used as the fixed foreground scale reference the whole shot is framed against. | Already en route, slows/stops on the road as the moose appears — no separate arrival beat. | Driver's reaction is confined to what a dash-cam shows: braking, hands adjusting on the wheel, no visible body/exit motion (Phase 1 safety conclusion). | Generic unbranded red/white liveried mid-size cargo van, no reproduced real-carrier logo/trademark. | Rural parcel routes on this exact kind of highway are ordinary and era-appropriate; Canada Post's universal rural mandate is the real-world grounding (Phase 1). |
| Location (rural boreal highway, dash-cam frame) | Two-lane highway width, road-shoulder markers, and treeline are the location's own internal scale references. | N/A (fixed dash-cam mount on the van, not a separate location). | N/A. | Two-lane paved rural highway, dense boreal spruce/pine treeline close on both shoulders, thin fresh snow layer on the road surface, pre-dawn/overcast light with headlights contributing meaningful illumination (Phase 1). | Ordinary for the stated Northern Ontario boreal-highway setting; consistent with light-snow, early-morning weather axis throughout. |

**Open decision carried into the Blocking Plan:** because the driver never
exits the vehicle, this shot needs **no full driver character sheet** —
only the van's cab interior detail (hands/wheel, visible at the frame's
bottom edge if at all) needs to stay consistent, which can be handled as a
minor prop/detail note rather than a full character sheet. This is a
real production-complexity difference from Shot 01 and Shot 02, not an
oversight — confirm before skipping the character-sheet step outright.

No anachronism or implausible combination identified for this cell.
