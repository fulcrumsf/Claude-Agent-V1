---
title: "Shot 03 — Blocking & Capture-Device Plausibility Pass"
shot: "A parcel van's dash-cam catches a moose calf stepping out of the treeline onto a rural Northern Ontario highway at dawn"
device_type: fixed-mounted-vehicle-borne
locked: 2026-09-19
---

# Blocking Plan

**Device type: fixed-mounted, vehicle-borne (dash-cam)** — a third distinct
capture-device subtype for this pipeline, different from both prior shots:
Shot 01 was handheld/reactive (a person carrying the camera), Shot 02 was
fixed/mounted at a *stationary* location (the doorbell camera never moves
because the house never moves). This shot's camera position never changes
*relative to the van* — but the framed scene itself moves, decelerates, and
stops, because the van it's mounted to does. Nothing pans, tilts, or
reframes independently of the van's own motion.

1. The van is already en route on a two-lane rural boreal highway, early
   morning, light snow dusting the road surface, dense spruce/pine treeline
   close on both shoulders (Phase 1, `Research/Plausibility_Facts.md`).
   Pre-dawn/overcast light — headlights on and contributing meaningful
   illumination, consistent with the stated weather axis.
2. A moose calf (Phase 1: ~4-5 ft at the shoulder, notably smaller than
   an adult but not a "baby animal" default) steps out of the treeline onto
   or alongside the road ahead, at a distance — the arrival trigger.
3. The van slows and comes to a stop a safe distance away. **The driver does
   not exit the vehicle** — this is a real safety-grounded conclusion from
   Phase 1, not a production shortcut: official Ontario/Quebec guidance for
   a moose encounter is to stay in the vehicle. The driver's reaction is
   visible only through what the dash-cam itself would show: the van's
   deceleration (treeline/road optical flow slowing), and, if visible at
   all, a hand adjusting on the wheel at the extreme bottom edge of frame —
   never a separately rendered driver body exiting frame.
4. Trigger → reaction, mirrored from both prior shots but appropriately
   asymmetric here: the moose pauses in or near the road, upright, head
   lifting and ears rotating toward the van, a weight shift before it
   settles — a real physical tell (Phase 2), not a frozen pose. The van
   stays stopped and still; there is no human counter-reaction to render
   beyond the van's own braked stillness.
5. The moose resumes moving at its own pace — crossing the road or turning
   back into the treeline, continuing toward where its mother is implied to
   be waiting (Phase 1: narratively nearby, **never rendered in-frame**).
   Once the road is clear, the van resumes driving forward and the shot
   ends.

This is the plan the storyboard must match — subject count (1 moose; the
van/driver represented only through the vehicle's own motion, never as a
separately visible human body) stays fixed, and the moose's position
advances at its own pace while the van's motion (approach → stop → hold →
resume) is the only other moving element in frame.

**Real-world scale note (Phase 1/2, `Research/Plausibility_Facts.md`):** a
moose calf stands roughly 4-5 ft at the shoulder — use the road's own
lane width and the van's hood/headlights as in-frame scale references. Do
not render it at adult-moose scale (~6-6.5 ft at the shoulder) or at
generic "baby animal" proportions — it should read as gangly/leggy, not
stocky.

**Natural motion note (per locked v2 plausibility check, extended to this
shot):** the moose's pause needs a real physical tell (head lift, ear
rotation, a weight shift before it resumes moving), not a static frozen
pose — same standard already locked for the kangaroo's watch beat in Shot
02.

**Species/behavior note (Phase 1 elaboration, corrected):** this is a moose
calf (*Alces alces*), roughly 5-6 months old — not an adult, not a
newborn, and not a true yearling either (a yearling requires surviving to
the following spring, which this calf hasn't reached yet; an earlier draft
of the audit used "yearling" incorrectly and has been corrected). **No
antlers at all, regardless of sex**, at this age — a true yearling bull
might show small "button" spikes, but this calf must not. Its mother is
narratively nearby but must never be rendered in-frame — stated explicitly
so no generation prompt accidentally introduces a second animal.

**Weather note (Diversity Matrix weather axis):** light snow, pre-dawn/
overcast light, van headlights contributing meaningful illumination on the
road surface. Must stay consistent across every panel/frame of this shot.

**On-screen text note (Phase 1 elaboration — real rule tension, resolved):**
real dash-cams commonly burn in a date/time/speed telemetry bar. **Do not
render this inside any generation prompt** — this pipeline's no-on-screen-
text hard constraint exists because AI video models render burned-in text
as garbled gibberish, not because the convention itself is implausible. If
wanted for realism, add it afterward as a separate deterministic
compositing step, the same principle already locked for the Shot 02
environment sheet's labels.

# Dash-Cam Frame (locked geography, text form)

- Forward-facing, moderate wide-angle dash-cam view from within the van's
  cab, mounted low on the windshield — continuously recording, **not**
  motion-triggered like Shot 02's doorbell camera (Phase 1: this is a real,
  named difference between the two device conventions, not an oversight).
- Two-lane paved rural highway fills the mid-to-lower frame, road surface
  showing a thin fresh layer of snow.
- Dense boreal spruce/pine treeline borders both shoulders, close enough to
  read as genuinely rural/remote, consistent with the Northern Ontario
  setting (Phase 1).
- **No cab interior detail beyond what's visible at the extreme bottom
  frame edge** (dashboard edge, hands on the wheel if included at all) —
  per the Phase 2 open decision, this shot does not need a full driver
  character sheet, since the driver's body is never rendered in frame. If a
  hand/wheel detail is included, it must stay visually consistent shot to
  shot as a minor prop note, not a full character asset.
- The van's own hood/mirrors may be visible at the frame's lower edge,
  providing a fixed in-frame scale reference against the moose and the
  road's lane width.
- Pre-dawn/overcast light throughout — no clear-sky or midday brightness,
  consistent with the stated early-morning, light-snow weather axis.
- This exact fixed-to-vehicle frame is what every storyboard panel must
  show — same road, same treeline, same cab-edge framing, every time; only
  the van's own motion (approach, stop, hold, resume) and the moose's
  position change.
