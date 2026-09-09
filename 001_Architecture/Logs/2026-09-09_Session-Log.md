# 2026-09-09 Session Log

## Neon Parcel subject-aware reframer — resumed Gate 2

- Session began September 8 and resumed September 9. Tony requested interview →
  plan → explicit approval → execution. Planning and Gate 1 changed no workspace
  files or installed dependencies. Tony explicitly approved Gate 2 and 42 package pins.
- Confirmed M3 Max, 36 GB RAM, Python 3.11.12, FFmpeg 8.1.1. Part Three source is
  97.500–129.750 s: 771 actual frames with irregular timestamps; cuts at 107.583333
  and 117.666667 s. The prior v2 Short starts video about 33 ms after its audio.
- Created `001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/`
  with isolated `.venv`, `.cache`, hash-locked requirements, dependency provenance,
  official YOLO11s weights/receipt, offline launcher, diagnostic CLI, and tests.
  No global package changes. Installed environment and caches total about 1.9 GiB.
- Dependency consistency and six unit tests passed. CPU and MPS each loaded the
  model with restricted loading under OS network denial and ran one-frame inference.
- Full CPU baseline produced `Shorts/Versions/v3/Auto-Reframe/Run-001/` with raw
  detections/tracks, debug video, contact sheet, timing map, and run report. It took
  60.8 seconds for detection and 71.7 seconds including diagnostics; peak process
  RSS was 678 MB. Debug video is 1280x800, 968 frames at 30 fps, about 32.266 seconds,
  with 48 kHz stereo audio. Both streams start at zero; full decode passed.
- Hash checks confirm the master, approved Parts One/Two, and both prior Part Three
  candidates are unchanged. No camera planner or vertical render was built.
- Initial visual review: Grandma tracking generally works; doorway bear missed
  throughout Shot 10. Hose interaction is substantially detected. Trampoline
  tracks exhibit four person/bear class transitions and late missed bears.
- All-class audit on 15 source frames identified species confusion: the porch
  animal is consistently classified as dog; some trampoline bears as dog/cat.
  Ran a second diagnostic using all COCO animal classes and separate person/animal
  trackers, retaining original species labels and the baseline for comparison.
- `Run-002/` completed in 71.2 seconds, peak RSS 661 MB. The porch animal appears
  in all 241 raw frames and 238 confirmed tracks; trampoline animals in all 289
  raw frames and 286 confirmed tracks. These are presence counts, not accuracy.
  Three-animal tracking covers 243 trampoline frames; brief duplicates, missed
  detections, ID fragmentation, and occlusion remain.
- Eight unit tests and independent Run-002 timing, full decode, family separation,
  source preservation, and resource checks passed. Created
  `Gate-2-Verification-v1.json`, review handoff, and updated tool README.
  Resource check: 1.96 GiB allocated, 20.48 GiB free. Tony's playback review is
  pending; no Gate 3 approval or vertical reframe is implied by these diagnostics.
- Experimental inventory entries added to TOOLBOX, Workspace Map, and Architecture
  Directory. Full auto-generated System Map refresh/pipeline adoption remains
  deferred to the global-adoption gate; it was not manually rewritten.
- Agent-OS build validation passed for all 16 selected functional/configuration
  artifacts; report retained as `Auto-Reframe/Build-Validation-v1.txt`. Gate 2
  handoff is ready, with camera planning and the vertical candidate awaiting
  Tony's explicit Gate 3 approval.
