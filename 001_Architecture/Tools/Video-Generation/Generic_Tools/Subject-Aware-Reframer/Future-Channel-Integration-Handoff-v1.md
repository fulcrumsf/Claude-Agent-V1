# Future Channel Integration — Long-Form to Shorts

Status: deferred by Tony. This handoff closes the current framing prototype work;
it does not activate a channel, controller, scheduled job, or publishing flow.

## Resume from a request like this

> “I want to plug the short-form clipping workflow into [channel name].”

Also recognize “connect the Shorts workflow,” “use the global reframer,” or
“send this channel's long-form videos through the Shorts pipeline.”

Read this handoff and the linked job contract before rebuilding anything or
asking Tony to repeat the original project context. Identify the named channel
and its existing pipeline, inspect its configuration read-only, then discuss
only the missing decisions. Tony prefers conversational iteration. An intake
questionnaire is optional future functionality, not a required interaction style.

Tony's operating order remains: conversation → plan → explicit approval →
execution. A future request starts that integration discussion; this handoff
does not preauthorize installations, channel edits, Airtable changes, or publishing.

## What exists and what does not

| Component | Current state |
|---|---|
| Shared local detection | Built: official YOLO11s, people/animal families, ByteTrack, source timestamps, diagnostic outputs. |
| Configurable reframing | Built: group, subject, hybrid modes; smoothing, safe fallback, short-gap handling, scene resets. |
| Saved settings | Built: shared profile file, per-job settings and per-shot overrides. No channel is automatically connected. |
| Job interface | Built: local JSON jobs plus plan/render/reframe CLI commands. |
| Validation | 24 tests passed; three Part Three vertical candidates and comparison/debug outputs verified. |
| Human feedback | Tony preferred Hybrid for this particular Part Three test. This is not a global mode default. |
| Automatic scene detection / clip selection | Not built. Current jobs use an explicitly selected interval and supplied shot boundaries. |
| Multiple Shorts from a whole master | Not built as an automatic workflow. |
| Narration-aware selection or switching | Not built. Current switching uses visual tracks and configured timing. |
| Questionnaire / channel adapter / Airtable or MCP controller | Not built or activated. |
| Automatic publishing | Not included or authorized. |

The reusable framing component is complete for this prototype stage. An
end-to-end, plug-and-play clipping pipeline for arbitrary channels is not yet
complete. Other footage still needs a channel-specific pilot and review.

## Where to resume

- [Tool README](/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/README.md)
- [Job contract and settings guide](/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/Job-Contract-v1.md)
- [Shared profiles](/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/Framing-Profiles-v1.json)
- [Offline launcher](/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/run_offline.py)
- [Detection CLI](/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/diagnose.py)
- [Framing CLI](/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/reframe.py)
- [Camera planner](/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/camera_plan.py)
- [Renderer](/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/render_reframe.py)
- [Part Three job example](/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Shorts/Versions/v3/Auto-Reframe/Part-3-Framing-Job-v1.json)
- [Gate 3 review and output links](/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Shorts/Versions/v3/Auto-Reframe/Gate-3-Review-v1.md)
- [Tony's scoped Hybrid preference](/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Shorts/Versions/v3/Auto-Reframe/Gate-3-Review-Decision-v1.json)
- [Verified comparison](/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Shorts/Versions/v3/Auto-Reframe/Gate-3-Run-002/Framing-Comparison-v1.mp4)
- [Verification evidence](/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Shorts/Versions/v3/Auto-Reframe/Gate-3-Verification-v1.json)

Code, dependencies, and common profiles belong in this shared tool directory.
Channel/job settings and generated media belong in the selected production's
Shorts folder. Do not copy the whole environment into each channel.

## Tony's intended future workflow

An approved 16:9 long-form master should optionally enter a shared workflow:

1. Obtain source timing, existing scene/shot metadata, and relevant editorial context.
2. Select complete sections and create several Shorts.
3. Detect subjects and apply the chosen framing profile to each Short.
4. Apply channel-specific captions/branding at the appropriate later stage.
5. Return versioned drafts, crop plans, and review evidence to the production.

Two clipping behaviors may be useful, and should be chosen for the channel:

- **Chronological series:** partition the master into complete scenes or scene
  groups, as with the Grandma-and-Bear Parts One, Two, and Three.
- **Standalone highlights:** select self-contained moments for individual Shorts.
  This requires additional editorial selection logic and must not be assumed to
  exist merely because detection/reframing works.

Preserve complete action, dialogue, and payoffs. Do not simply divide the master
at arbitrary fixed timestamps. Use existing production manifests or edit
timelines when available. Duration targets, number of Shorts, chronological
coverage, and narration/caption handling are channel-level choices.

## Recommended integration sequence

### 1. Inspect the chosen channel and propose its first connection

Locate its approved-master handoff, existing shot/timing data, source-media
conventions, output folders, and review process. Establish whether it already
selects Short intervals.

If intervals already exist, the first integration can simply call the reframer
for those intervals. If only a complete master exists, explicitly plan the
missing clip-selection component before promising automatic Shorts.

Agree on a saved channel profile: group, subject, or hybrid; switching/hold
preferences; output requirements; and when per-video overrides are needed.
Do not copy the Hybrid preference from Part Three into every channel.

### 2. Pilot one approved video

After Tony approves the concrete implementation plan, create the smallest
adapter that produces the documented JSON job and calls the existing local
engine. Prefer reframing after interval selection and before final captions
and branding. Preserve the source and generate new versioned outputs.

Test footage representative of that channel. Check subject coverage, switching
and reveal timing, complete action/dialogue, audio/video alignment, captions,
and endings. Require Tony's review before enabling routine use.

### 3. Add automatic clip selection where required

Build this as a separate component that outputs selected intervals and shot
boundaries to the reframer. Introduce narration/transcript awareness only with
an approved dependency/provider plan. Keep selection decisions reviewable.

### 4. Add an optional controller

An Airtable checkbox could request Shorts for an approved long-form video,
using a saved channel profile. Airtable would control the job; a local worker
would process the video. It is not the rendering engine.

A later controller plan should specify the master reference, channel/profile,
requested action, job status, returned draft locations, and error reporting.
Prevent duplicate submissions and concurrent writes. Decide how a worker
receives jobs without exposing local footage or credentials unnecessarily.
Missing settings can trigger a short conversation; established profiles can
run without repeating intake after Tony authorizes that workflow.

No Airtable fields, credentials, worker, automation, MCP server, or publishing
integration were created during the prototype. Do not install a connector merely
because this handoff mentions it.

## Technical boundaries to inspect before a new channel

- Use the existing isolated environment and locked package set. Gate 3 added no
  dependencies. Recheck availability after a long pause; do not reinstall or
  upgrade automatically.
- Full-sequence validation used CPU on Tony's Mac. MPS had a smoke check only.
  The launcher and FFmpeg paths currently target this Mac; portability is not
  established.
- Current detection families are people and animals. Products, gameplay,
  diagrams, text-heavy footage, or different visual styles need their own
  strategy and validation. Tracking IDs are not semantic character identities.
- Output validation covers 30 fps vertical video, up to 1080×1920. The tested
  comparison is 16:9 source to 9:16 output.
- Source fingerprints and presentation timestamps are important. Do not carry
  Part Three's paths, hashes, time base, boundaries, frame counts, or protected
  file list into another production.
- The older detection diagnostic still uses Part-3-specific output filenames.
  Generalize those names in an approved integration pass; the camera/render
  job interface already takes a job-specific output stem.
- Existing burned-in captions/logos are not independently protected by the
  current detector. Establish a suitable source or handling plan for that channel.
- The prototype's resource bounds are 5 GiB for the experiment and at least
  10 GiB free disk. Review storage/concurrency requirements before scaling.
- Keep offline enforcement and safe model loading. Current scope is private
  local use; reassess licensing before distribution or network-service use.
- The JSON approval field records human approval. It is not authentication and
  does not authorize an agent or controller to approve its own work.

## Completion criteria for a future channel connection

The named channel has a reviewed profile, a tested adapter, clearly defined
interval selection, versioned production-local outputs, source-preservation
checks, and an explicit enable/disable choice. Missing or failed jobs report
their status instead of silently continuing. Publishing remains a separate
authorization.

Do not mark every channel connected after one pilot. Adopt each channel
deliberately, using this shared engine and retaining its own settings.
