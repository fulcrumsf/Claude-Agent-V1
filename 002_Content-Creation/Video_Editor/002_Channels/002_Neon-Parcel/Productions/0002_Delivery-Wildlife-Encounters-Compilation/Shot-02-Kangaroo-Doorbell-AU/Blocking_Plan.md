---
title: "Test Shot 03 — Blocking & Capture-Device Plausibility Pass"
shot: "A delivery driver drops off a food order and is leaving the porch when a kangaroo wanders into the yard"
device_type: fixed-mounted
locked: 2026-09-18
---

# Blocking Plan

**Device type: fixed/mounted (doorbell camera)** — first v2 test of this
branch (Test Shot 02 was handheld/reactive). The camera position and
wide-angle fisheye frame are fixed by the door-height mount; nothing pans,
tilts, or reframes. Only the subjects' path through that fixed frame is
planned.

1. A **local takeaway shop's own delivery driver** (not a gig-app/aggregator
   courier — Phase 1 elaboration in `Research/Plausibility_Facts.md`
   concluded a small regional town in 2019 is more realistically served by a
   local shop's own driver than app-courier density), carrying a **plain
   insulated delivery bag** (not a branded aggregator-style backpack, no
   real-world restaurant logo), approaches from screen-right on foot, having
   just parked an **ordinary older-model sedan or hatchback** in the
   driveway — now visible at the screen-right edge of frame (corrected
   2026-09-19 — driveway is the property's west side, which appears on the
   doorbell POV's right; see the Orientation reference in
   `Data/Architectural_Site_Plan.md`), not a bike or
   motorbike, and not a rideshare-branded vehicle (a low-density
   bushland-fringe setting doesn't support bike-courier distances). Crosses
   the porch.
2. **Corrected 2026-09-18 (Tony's catch):** the driver does **not** leave the
   whole bag behind — he opens it, removes the food item/container(s) from
   inside, and places only that item on the doormat directly below the
   camera. He keeps the now-lighter bag in hand the entire time; no real
   driver would leave his carrying bag at a customer's door.
3. The driver turns and starts back down the porch steps toward
   screen-right/driveway, order delivered, bag still in hand.
4. As the driver reaches the bottom of the steps, a kangaroo hops into frame
   from screen-left (the side yard/garden bed), landing mid-lawn — **clear
   of the letterbox**, not overlapping or colliding with it (corrected
   2026-09-18 — v2's storyboard showed the kangaroo's body merged into the
   letterbox post, a real deformity/collision defect).
5. Trigger -> reaction: the driver notices the kangaroo mid-stride, freezes
   and half-turns to look. The kangaroo pauses too, upright, watching the
   driver — a real held moment, not a scripted standoff.
6. The kangaroo continues on its own path across the lawn toward the rear/side
   of the yard and exits frame; the driver resumes walking toward the
   driveway/street and exits frame opposite, bag still in hand.

This is the plan the storyboard must match — subject count (1 driver + 1
kangaroo) stays fixed, the fixed doorbell frame never changes, and each
subject's screen-position advances monotonically toward their own exit side.

**Real-world scale note (per locked v2 plausibility check):** an adult
kangaroo stands upright to roughly chest/shoulder height on an adult human —
much larger than a dog, noticeably shorter than the driver. Do not render it
house-cat/dog-sized or larger than the driver. The doormat, porch steps, and
letterbox are ordinary residential scale — use them as the size reference in
the prompt.

**Natural motion note (per locked v2 plausibility check):** the driver's
"notice" beat needs a concrete physical micro-detail (a half-step
stutter-stop, a shoulder/head turn that slightly overshoots before settling),
not just "looks surprised." The kangaroo's pause needs its own real physical
tell (weight settling back on its haunches/tail, ears rotating toward the
driver) rather than a static frozen pose.

**Species note (Phase 1 elaboration, `Research/Plausibility_Facts.md`):**
this is specifically an **eastern/western grey kangaroo**
(*Macropus giganteus*/*fuliginosus*) — the species associated with
bushland-*fringe* and coastal-regional towns — not a red kangaroo
(*Osphranter rufus*), which is a true arid-interior/outback species and
would not be plausible for this setting.

**Weather note (Phase 1 elaboration / Diversity Matrix weather axis, added
2026-09-18):** clear, dry, mild midday conditions — hard shadows, no wet
pavement, no overcast flatness. Must stay consistent across every panel.

# Fixed Doorbell Frame (locked geography, text form)

- Wide-angle fisheye frame from door height, looking down/out over the porch
  — matching mainstream 2018/2019-era consumer doorbell-camera hardware
  (Ring Doorbell 2/Pro-generation): motion-triggered clip start, fixed
  non-pan/tilt mount, modest dynamic range/color rendering by later
  standards (Phase 1 elaboration).
- Doormat centered in the lower-frame foreground, directly below the camera.
- Porch steps lead down from the mat toward screen-right, ending at a
  driveway edge **visible at the screen-right edge of frame** (corrected
  2026-09-18 — Tony caught that the car was never actually shown; a
  wide-angle fisheye doorbell mount plausibly captures at least a sliver of
  the driveway). **The driver's parked car (ordinary older-model
  sedan/hatchback, per the Grounding Audit) is visible there, stationary,
  for the entire shot** — small in frame at that edge, not a hero object,
  but no longer implied-but-unshown.
- **Architectural plausibility correction (2026-09-18, Tony's catch):** the
  generated environment plate showed a real, basic construction-logic
  failure — the staircase offset to one side of the patio, away from the
  door, with a mismatched, separate half-level patio strip beside it. No
  real residential entry is built this way, and it also breaks the actor's
  blocking (an unnaturally awkward diagonal path from the top of the stairs
  to the doormat). **Corrected requirement: a single, direct, centered
  staircase runs straight from ground level up to the porch landing
  immediately in front of the door — same axis as the door and doormat, the
  way an ordinary real entry is actually built.** No offset, no second
  mismatched patio level, no diagonal detour required to reach the doormat.
  The handrail must be structurally attached to and running directly
  alongside that single staircase, not floating or attached to an unrelated
  structure. This must be checked explicitly against the environment plate
  before it is used as a reference for any further generation — a plausible-
  looking photo can still depict an unbuildable structure, and that defect
  propagates into every downstream storyboard/video prompt that references
  it, which is exactly what happened here.
- **Three distinct ground surfaces, named explicitly (added 2026-09-18 after
  a real, repeated misjudgment of which one the driver was standing on):**
  1. **Porch surface:** smooth gray concrete, directly below the camera and
     around the doormat/steps top — the driver starts and ends near here.
  2. **Step tile:** tan/pink-toned tile treads forming the staircase between
     the porch and the driveway — a distinct color and texture from both the
     porch and the driveway, visible as a diagonal strip in frame.
  3. **Driveway surface:** light gray speckled gravel/pebble texture, where
     the parked car sits, at the screen-right edge — visually distinct from
     both the smooth porch concrete and the tan step tile.
  Every frame description for the driver from frame 3 onward must state
  which of these three specific surfaces his feet are on, by name and
  texture, not by proximity to a landmark like "near the car" or "at the
  bottom of the steps" — proximity language is exactly what produced the
  earlier misreads (a subject can be near the car while still standing on
  the step tile, not the driveway itself).
- The house itself is a **single-story brick-veneer or weatherboard project
  home with a corrugated-iron roof** — the ordinary regional-Australian
  house type (Phase 1 elaboration), visually distinct from Test Shot 02's UK
  terraced-house brick front.
- A low garden bed/hedge line borders the lawn on screen-left; this is where
  the kangaroo enters and exits. Native/bushland-style plantings, not a
  manicured lawn.
- Open lawn occupies the mid-frame background between the steps and the
  garden bed — this is the kangaroo's path.
- A letterbox sits near the screen-left edge of the lawn as a fixed scale
  reference. A **Hills Hoist rotary clothesline** and a **rainwater tank**
  are visible in the yard as regional-Australian set dressing (Phase 1
  elaboration) — static background only, not part of any subject's path.
  **No dog and no other animals** in this shot — explicitly excluded to keep
  subject count fixed at exactly driver + kangaroo.
- This exact fixed frame and layout is what every storyboard panel must show
  — same mat, same steps, same house, same hedge line, same letterbox
  position, every time; only the subjects move within it.
