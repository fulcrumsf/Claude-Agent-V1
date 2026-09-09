# Subject-Aware Reframer — Experimental Gate 2

Tony approved the Gate 2 dependency installation and Part Three detection/tracking
diagnostics on 2026-09-08. Camera planning, vertical reframing, integration into the
production pipeline, and publishing are not authorized at this gate.

The isolated Python 3.11 environment and pinned packages belong here. Model weights
and caches are ignored by Git. Production configuration and diagnostic results
belong in the production's `Shorts/` folder. Existing source media and candidates
must never be overwritten. Every analysis run requires a new output directory.

The runtime must disable automatic installs, use restricted model loading, verify
the model receipt and source fingerprint, and run offline. `Offline.sb` denies
network access; it is not a filesystem security boundary. No cloud credentials or
provider integrations are needed. The package and model licensing route is private
local AGPL use; reevaluate before distributing software or exposing a service.

## Dependencies

`requirements-approved.txt` is the exact 42-package set reviewed in Gate 1.
`requirements.lock` contains wheel-specific hashes from official PyPI metadata.
The install uses prebuilt wheels only, the existing Python interpreter, and this
tool's `.venv` and `.cache` paths. Do not install the standard `ultralytics` or
another OpenCV distribution alongside the approved headless distribution.

## Resource limits

Reserve no more than 5 GiB for this experiment's environment, caches, and outputs.
Stop work below 10 GiB of available disk. Process one frame at a time. Full source
frames should not be materialized as a persistent frame sequence.

## Implemented commands

Run the launcher with the existing Homebrew Python 3.11 interpreter. It invokes
the tool's isolated environment under the macOS network-denial profile. The
diagnostic itself checks that the operating system rejects network access before
importing third-party model code. A restricted host may require execution
permission for `sandbox-exec`; do not bypass the profile to resolve that.

```text
/opt/homebrew/bin/python3.11 -B run_offline.py runtime --config /absolute/path/to/config.json --device cpu
/opt/homebrew/bin/python3.11 -B run_offline.py analyze --config /absolute/path/to/config.json --out /absolute/path/to/new-run --device cpu
/opt/homebrew/bin/python3.11 -B run_offline.py audit-classes --config /absolute/path/to/config.json --out /absolute/path/to/new-audit --device cpu
```

- `runtime`: validate pins, model receipt, offline enforcement, source timestamps,
  and one-frame inference. CPU and MPS smoke checks passed; only CPU has completed
  the full Part Three diagnostic and is the current default.
- `analyze`: retain every raw detection and active track, then create a debug MP4,
  contact sheet, PTS mapping, and run report in a new directory.
- `audit-classes`: inspect all COCO classes on fifteen selected frames to explain
  filter misses. It produces diagnostic JSON and does not relabel the subjects.

Every run needs a fresh directory. A missing `Run-Report-v1.json` means an analysis
is incomplete; preserve that directory and use the next run number for a retry.
`Run-Started.json` documents the configuration before work begins. No command
uploads footage, trains a model, downloads dependencies, creates a crop plan, or
renders a vertical Short.

## Detection and tracking behavior

The baseline configuration tracks person and bear classes. The second diagnostic
configuration groups person detections separately from all COCO animal classes
(14–23). This is necessary for the AI-generated footage: YOLO repeatedly labels
the porch animal as dog and some trampoline bears as dog or cat.

Raw species labels remain in JSON. The tool suppresses strongly overlapping
animal detections before tracking and associates people and animals separately.
It namespaces IDs by shot and family, resets trackers at cuts, and displays a
colored box after four consecutive observations. Thin grey boxes are raw
detections; green boxes are confirmed people; blue boxes are confirmed animals.
Four observations add roughly 125 ms from the first observation to confirmation
at 24 fps. Reappearing tracks must earn confirmation again.

These IDs are tracking hints, not recognition of Grandma or individual bears.
The model may still miss, duplicate, swap, or split subjects. A stable family does
not guarantee a stable identity. There is no narration-based editorial intent,
gap-filling camera behavior, or automatic shot detection in this gate. Shot
boundaries are explicit production configuration.

## Part Three evidence

Review files are under the production's
`Shorts/Versions/v3/Auto-Reframe/`. `Run-001/` is the baseline; `Class-Audit-001/`
explains species confusion; `Run-002/` uses animal-family tracking. Both runs
remain as deliberate comparison evidence.

The input interval is 97.500–129.750 seconds from the approved wide master:
771 source frames across three shots. Original presentation timestamps drive
sample-and-hold conversion to 968 diagnostic frames at 30 fps. Debug output is
1280×800, including the footer, with H.264 video and AAC 48 kHz stereo audio.
The nominal duration is 32.266667 seconds, adding about 16.7 ms of final-frame hold
and audio padding; the next shot/endcard is excluded.

The second CPU run took 71.2 seconds including rendering and peaked at about
631 MiB process RSS. Allocated environment, caches, model, and production evidence
were about 1.96 GiB at verification. The 10 GiB free-space floor is enforced by
the CLI; the 5 GiB total experiment budget is checked in the gate verification.

See `Gate-2-Review-v1.md` and `Gate-2-Verification-v1.json` beside the run folders.
Automated timing, media decode, source-preservation, and family-separation checks
passed. Eight unit tests cover timestamp conversion, cut boundaries, preservation,
offline launch rejection, and animal deduplication:

```text
.venv/bin/python -B -m unittest -v test_diagnose.py
```

Tony's normal-speed review remains pending. Detection presence is not measured
accuracy, and these diagnostics do not establish vertical framing quality.

## Next approval boundary

Gate 3 may build the camera planner and a Part Three vertical review candidate
only after Tony approves that scope. It must tolerate tracking gaps, include the
interaction group, reset at cuts, and fit the wider scene over a blurred
background when the group cannot fit in 9:16. Global adoption, automatic pipeline
activation, distribution, and publishing remain separate decisions.
