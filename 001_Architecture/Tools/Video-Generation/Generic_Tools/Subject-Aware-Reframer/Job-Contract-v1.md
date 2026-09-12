# Reframing Job Contract v1

The shared engine accepts an explicit local JSON job. Conversation, a future
questionnaire, a channel pipeline, or a future Airtable adapter can prepare the
same job. Gate 3 implements the job interface and framing; it does not implement
automatic clip selection, a questionnaire, a connector, or publishing.

## Execution

Run these from the tool directory with its existing offline launcher:

```text
/opt/homebrew/bin/python3.11 -B run_offline.py plan --job /absolute/path/Job.json --out /absolute/path/new-run
/opt/homebrew/bin/python3.11 -B run_offline.py reframe --job /absolute/path/Job.json --out /absolute/path/new-run
/opt/homebrew/bin/python3.11 -B run_offline.py render --plan /absolute/path/Crop-Plan-v1.json --out /absolute/path/new-render
```

`plan` creates the camera plan without rendering. `reframe` plans and renders.
`render` consumes a saved plan; it rechecks source/config fingerprints and crop
geometry before rendering. Every output directory must be new and a direct child
of the job's existing `output_root`. Failed or incomplete runs are preserved.

The macOS network-denial profile remains mandatory. All 42 installed package
versions are checked at launch. Framing reuses the detection cache; it does not
load YOLO or repeat inference. Source media remains read-only.

## Required job fields

| Field | Meaning |
|---|---|
| `schema_version` | Integer `1`; unknown top-level fields are rejected. |
| `job_id` | Local identifier using letters, digits, underscores, or dashes. |
| `approval` | Record containing `gate: 3`, `approved: true`, and human approval context. This records authorization; it is not authentication or permission to self-approve. |
| `source`, `source_sha256` | Absolute source path and expected SHA-256. |
| `analysis`, `analysis_sha256` | Absolute path and hash of the family-aware detection cache. Source PTS and shot boundaries are read from that cache and checked against the video. |
| `profile_file`, `profile_sha256` | Absolute path and hash of a saved profile file. |
| `output_root` | Existing production directory for new runs, normally inside its Shorts folder. |
| `output_stem` | Safe filename prefix; no paths or extensions. |
| `output` | Integer width, height, fps. This prototype supports even vertical dimensions up to 1080×1920 at 30 fps. Part Three uses 1080×1920. |
| `variants` | One to three named variants, each specifying a profile, setting overrides, and shot overrides. |
| `protected_media` | Mapping of absolute paths to hashes for earlier approved or protected artifacts. These are checked before and after rendering. |

The actual Part Three job is saved in its production as
`Shorts/Versions/v3/Auto-Reframe/Part-3-Framing-Job-v1.json`.
No channel path, name, shot timing, or Grandma/bear identity is embedded in the
camera engine. Other jobs must supply their own analyzed source and boundaries.

## Profiles and per-scene overrides

`Framing-Profiles-v1.json` contains common defaults and three reusable profiles.
Settings resolve in this order:

`defaults → selected profile → variant settings → shot overrides`

Example variant fragment:

```json
{
  "My-Hybrid": {
    "profile": "hybrid",
    "settings": {
      "subject_hold_seconds": 4.0,
      "group_hold_seconds": 3.0,
      "switch_policy": "alternate"
    },
    "shot_overrides": {
      "Scene-03": {"mode": "group"},
      "Scene-04": {"mode": "subject", "switch_policy": "priority"}
    }
  }
}
```

This is an illustrative fragment, not a complete runnable job. Shot names must
match the supplied analysis. A misspelled setting or unknown shot is rejected.
New profiles and jobs should receive new versioned filenames; keep previous
fingerprinted files available for reproducibility.

| Control | Default | Behavior |
|---|---:|---|
| `mode` | hybrid | `group`: full scene over blur; `subject`: follow one selected subject; `hybrid`: mix subject and group views. |
| `priority` | person, animal | Order of family preference when selecting a new subject. |
| `switch_policy` | alternate | `alternate` rotates the family preference and avoids the preceding subject when possible; it also supports two people. `priority` prefers the configured family. Neither identifies a speaker from audio. |
| `subject_hold_seconds` | 3.5 | Scheduled subject-view duration. A subject can be replaced earlier if it is lost; a safety fallback can interrupt the crop. |
| `group_hold_seconds` | 2.5 | Group-view portion of a hybrid cycle after a multi-subject scene is established. |
| `end_group_seconds` | 2.0 | Keep the ending of a multi-subject hybrid scene wide. This is a timed rule, not semantic payoff recognition. |
| `fallback_hold_seconds` | 1.5 | Minimum safety fallback hold; also suppress crop returns shorter than this beside wider views. |
| `gap_hold_seconds` | 0.3 | Retain/interpolate a recently observed subject during a brief detection gap. |
| `lookahead_seconds` | 0.25 | Allow a near-future confirmed track to guide positioning. |
| `opening_lookahead_seconds` | 0.8 | Additional look-ahead near each scene opening, such as framing a doorway before the person emerges. |
| `max_zoom` | 1.5 | Maximum vertical magnification relative to the full source height. |
| `subject_margin_fraction` | 0.08 | Desired margin around the chosen detection. Actual bounds remain protected when motion consumes the margin. |
| `smoothing_seconds` | 0.22 | Response time for pan and zoom smoothing. |
| `dead_zone_fraction` | 0.04 | Ignore small target-center changes relative to the crop dimensions. |
| `max_pan_fraction_per_second` | 0.65 | Maximum source-width movement per second, per axis, within a continuous crop. |
| `max_zoom_fraction_per_second` | 0.35 | Maximum change in crop height per second as a fraction of source height. |
| `background_brightness` | 0.55 | Brightness multiplier for the blurred background. |
| `background_blur` | 21 | Odd Gaussian kernel size on the reduced-resolution background. |

Changes between subjects or between crop/group layouts are cuts. Motion within
a crop is smoothed. If a chosen subject cannot fit or the camera cannot follow
within its movement limits, the safe fallback retains the full source over blur.
Short view changes are removed using the known future plan. Scene cuts reset all
tracking and camera context.

## Outputs and limits

Each variant receives a clean MP4. A comparison video shows the variants together;
the debug video shows the first hybrid variant (or the first variant) alongside
the original frame, selected source region, and observed/held/look-ahead subjects.
The contact sheet uses that same featured variant. The crop plan records every
output frame, original frame/PTS, selected subject, layout, crop, transition, and
decision reason. The completion report includes media verification and hashes.

The comparison/debug layouts are optimized for the tested 16:9-to-9:16 workflow.
Alternate vertical dimensions are accepted but require visual validation.
Model identities remain imperfect; a bounding box is not proof of subject
identity. Fitting the whole scene guarantees source coverage but makes subjects
smaller. This is a framing component over an explicit existing clip interval;
scene detection and selection of multiple Shorts from a whole master are later
components.

The existing source audio is trimmed to the same interval and re-encoded as AAC
48 kHz stereo. The source's original timestamps determine the output mapping.
Part Three adds about 16.7 ms of tail hold/padding to fit 30 fps. Existing burned-in
captions or logos are not separately protected by this prototype. Prefer
reframing before final captions and branding.
