# Gate 2 Review — Part Three Subject Detection

Date: 2026-09-09. Status: implementation and automated verification complete;
Tony's visual review and Gate 3 approval are pending.

## Review these files

- [Second-run debug video](Run-002/Part-3-Detection-Debug-v1.mp4)
- [Second-run contact sheet](Run-002/Part-3-Detection-Contact-Sheet-v1.jpg)
- [Detections and tracks](Run-002/Detections-And-Tracks-v1.json)
- [Automated verification](Gate-2-Verification-v1.json)
- [Baseline comparison video](Run-001/Part-3-Detection-Debug-v1.mp4)
- [All-class audit](Class-Audit-001/All-Class-Audit-v1.json)

These are wide diagnostic views with overlays. They do not show a proposed
vertical crop. Grey boxes are raw detections, green boxes confirmed people, and
blue boxes confirmed animals. The first three observations of a new track remain
grey while the four-observation confirmation rule takes effect.

## What Gate 2 established

The small local tool can detect and track subjects on all 771 source frames of
Part Three without uploading footage. It uses the approved YOLO11s model,
isolated pinned dependencies, OpenCV, FFmpeg, and separate ByteTrack associations
for people and animals. Full CPU analysis plus diagnostics took 71.2 seconds.

The first run's person/bear filter omitted the porch animal entirely. The
all-class audit found that YOLO located it as a dog at about 92% confidence.
Several trampoline bears also receive dog or cat labels. The second run tracks
the animal family while retaining the original class predictions in JSON. It
does not convert uncertain species predictions into claims that every animal is
a bear.

| Scene | Frames | Baseline frames with a raw bear detection | Second-run frames with any raw animal detection | Second-run frames with a confirmed animal track |
|---|---:|---:|---:|---:|
| Doorway, 97.500–107.583 s | 241 | 0 | 241 | 238 |
| Hose, 107.583–117.667 s | 241 | 212 | 227 | 207 |
| Trampoline, 117.667–129.750 s | 289 | 268 | 289 | 286 |

These are model-output presence counts, not measured accuracy or proof that
every visible animal is covered. Some frames legitimately have no visible
Grandma or bear, particularly at scene starts and exits.

## Visual findings and limits

- Doorway: the animal is now retained and Grandma is tracked once she emerges.
  The untrimmed source begins before Grandma is visible. A camera cannot open on
  her face until she appears; preserve the approved interval unless Tony requests
  an editorial trim.
- Hose: the main Grandma-and-animal interaction is detected. Temporary misses
  and an animal ID change remain as the bear changes pose or leaves.
- Trampoline: the sampled review shows Grandma and the group substantially
  covered. Confirmed animal counts are three on 243 frames, two on 33 frames,
  four on 10 frames, and zero on the first three confirmation frames. There are
  three bears in the scene; the brief four-box output includes duplicate
  detections. Late occlusion and track fragmentation remain.
- Person and animal IDs no longer share a tracker. Verification found no
  identity crossing between families or shots. This does not prove that separate
  animals never exchange IDs.
- Tracking does not understand the narration, action significance, or desired
  reveal. Directly centering each frame's boxes would still risk unstable camera
  movement. The crop planner must handle those decisions.

Agent review covered the fifteen-frame contact sheet and recorded diagnostics.
Tony should watch the debug video at normal speed, especially Grandma's exit,
the bear's hose interaction, and the final trampoline group. Playback quality and
editorial acceptance remain human review items.

## Dependency and safety evidence

- Exactly 42 approved package pins installed from compatible prebuilt wheels,
  with SHA-256 hashes from official PyPI metadata. Dependency consistency passed.
  No system Python or global package updates were performed.
- Official YOLO11s checkpoint downloaded from the Ultralytics assets release;
  its URL and calculated SHA-256 are retained in the model receipt. This recorded
  hash protects subsequent integrity; it is not a separate upstream signature.
- CPU and MPS each passed a one-frame inference smoke check. Full-sequence
  verification used CPU. MPS parity/performance is not established.
- The launcher removes inherited provider credentials, scopes caches to the tool,
  disables automatic installation/integrations, and requires restricted model
  loading. The operating-system profile denies all network access; the runtime
  confirmed denial before model imports. It is not a filesystem isolation layer.
- Master and all four protected Shorts retained their original SHA-256 hashes.
  Baseline, audit, and second-run evidence are preserved separately.
- Allocated experiment size was 1.96 GiB with 20.48 GiB disk free at verification.
  The scope reserves at most 5 GiB and requires at least 10 GiB free disk.

Private local use remains the approved scope. Distribution, a network service,
commercial-app integration, or a different model/dependency set requires a fresh
scope and license review.

## Verification

Eight unit tests passed. The Agent-OS build validator covers the functional
Python/configuration files; see the retained build-validation report.
Independent output checks confirmed:

- 771 original frames, strictly increasing source PTS, and 241/241/289 frames in
  the three approved shot intervals.
- 968 output frames at 30 fps, 1280×800 H.264/yuv420p, and AAC 48 kHz stereo audio.
- Audio and video begin at zero, agree within one frame, and decode fully with
  FFmpeg's error-exit option.
- Source-PTS conversion excludes the following endcard. The diagnostic adds
  approximately 16.7 ms of tail hold/padding to fit the 30 fps grid.
- Species predictions remain separate from stable person/animal family labels.
- Source and protected render hashes remain unchanged.

## Proposed Gate 3 scope — approval required

Build the visual camera planner and one Part Three vertical review candidate
using these existing dependencies and the approved wide master. Deliver a
versioned 1080×1920 MP4, crop/layout-plan JSON, and framing diagnostics inside this
production's Shorts folder.

The planner should use shot-local subject groups, margins, short detection-gap
holds, look-ahead, a camera dead zone, and limits on pan/zoom speed. It should
avoid layout flicker through minimum hold times. Reset camera state at each cut.
Keep Grandma and the relevant animal group visible; when they cannot fit a
vertical crop, use Tony's approved wider-scene-over-blurred-background layout.
Do not invent absent detections or treat a track ID as semantic recognition.

Review the doorway reveal, hose action, and full trampoline payoff at normal
speed. A failing scene returns for revision; it does not trigger automatic
adoption. No new dependency, cloud analysis, narration-aware switching, global
pipeline activation, or publishing is included in this proposed gate.

This is a recommendation for a controlled framing trial, not a claim that the
reframer is already production-ready. Tony's explicit approval is required before
Gate 3 starts under his interview → plan → approval → execution rule.
