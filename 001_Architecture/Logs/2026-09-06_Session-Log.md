## Neon Parcel thumbnail package scaffold

- Corrected the Grandma-and-Bear production package so thumbnails are stored
  under `Package/Thumbnails/`.
- Kept Tony-approved assets active: the “Grandma's Ridiculous Bear Encounters”
  overlay and the latest corrected Option 6 and Option 7 versions.
- Moved all older, rejected, superseded, and delivery-derivative thumbnail
  files to `Package/Thumbnails/Archived/` without deletion or overwrite.
- Added the explicit folder/archive rule to the Neon Parcel compilation skill
  and corrected references in the report card and thumbnail architecture brief.

## Compilation metadata tags

- Added comma-separated YouTube search-intent tags with intentional common
  misspellings to `Package/Title-Description-Options-v1.md`.
- Verified the tag string is 494 characters, under the 500-character limit, and
  avoids claiming the realistic-looking footage is authentic.

## Neon Parcel Blotato upload attempt

- Verified the live Neon Parcel YouTube account in Blotato as account `25731`.
- Uploaded the approved final assembly and a compressed copy of the first
  approved thumbnail to Blotato storage; both media transfers returned HTTP
  200.
- Post creation was blocked before submission because Blotato reported that the
  YouTube account must be reconnected to use custom thumbnails. No YouTube post
  was created. The uploaded media URLs remain usable after reconnection.
- Blotato's live YouTube schema exposes no caption-language field; English
  caption language remains a YouTube Studio setting.

## Codex Blotato MCP registration

- Verified `https://mcp.blotato.com/mcp` accepts bearer authentication with the
  existing `BLOTATO_API_KEY` environment variable.
- Registered the endpoint globally in Codex as enabled streamable HTTP MCP
  server `blotato`, with no credential value stored in `config.toml`.
- Codex must be restarted before the new Blotato tools appear in an active
  session.

## Neon Parcel private upload completed

- After restart, Blotato MCP loaded natively in Codex and the live account list
  reconfirmed Neon Parcel YouTube account `25731`.
- Submitted the approved final assembly privately with title option 1,
  description, compressed copy of approved thumbnail option 5,
  `isMadeForKids: false`, `containsSyntheticMedia: true`, and subscriber
  notifications disabled.
- Blotato returned `published` and confirmed the private YouTube upload:
  https://www.youtube.com/watch?v=Wxc3xBnaoNo
- Submission ID: `072ab410-d284-42db-8a7f-732313a7f2c3`.
- Tags, Entertainment category, and English caption language remain manual
  YouTube Studio steps because Blotato exposes none of those fields here.

## Neon Parcel production closeout

- Tony completed the remaining YouTube Studio metadata steps: tags were added,
  category was set to Comedy, and caption language was set to English.
- The Grandma-and-Bear production is now complete as a private upload. Only
  optional public-release scheduling or Shorts derivatives remain.
- Category guidance was hardened as content-first: use Comedy for comedy-led
  compilations, while preserving the option to choose Entertainment when the
  actual editorial promise is broader.

## Neon Parcel Seedance route inconsistency closed

- Resumed from the 2026-09-05 handoff after the Grandma-and-Bear video shipped.
- Resolved the stale Neon Parcel routing inconsistency: low-complexity shots no
  longer auto-route to Seedance 1.5. The locked default remains Seedance 2 Mini
  480p -> Topaz 2x -> FFmpeg 1920x1080 for normal shots.
- Updated `route_shot_complexity.py` so explicit `seedance_1_5_fallback` is the
  only route override to Seedance 1.5; legacy `force_simple` now stops for
  manual review instead of silently picking 1.5.
- Updated focused router tests and verified them with
  `python3 -m unittest test_route_shot_complexity.py` from the Neon Parcel tool
  folder.

## Resume correction: Shorts derivatives are next

- Tony clarified that Codex should have resumed from the newest last-chat state,
  not the older pipeline-orchestrator handoff item.
- Current Grandma-and-Bear status: private master is approved and YouTube Studio
  metadata was completed manually. The next production phase is creating and
  reviewing Shorts derivatives from the approved private master.
- Captured Tony's autonomy-score process: 65% means the pipeline remains in a
  human-iterated hardening loop with at-will checks, not fixed checkpoints. The
  target for mostly autonomous operation is roughly 95%.

## Neon Parcel Shorts Part One test candidate

- After Tony approved one test edit, created a temporary production-local
  Shorts derivative script and rendered one full Part One review candidate from
  the approved private master.
- Output:
  `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Shorts/Versions/v2/Neon-Parcel-Grandma-And-Bear-Short-Part-1-Test-v1.mp4`.
- Test specs: 55.3 seconds, 1080x1920, 30 fps, stereo 48 kHz audio, complete
  clip boundaries, opening one-second title overlay: "Ridiculous Grandma and
  Bear Encounters, Part One".
- This is not yet hardened into a global reusable tool or skill; wait for
  Tony's review before generalizing.

## Neon Parcel Shorts Part Two review candidate

- After Tony approved Part One and asked for the next video, rendered Part Two
  from the approved private master using the same temporary production-local
  Shorts method.
- Output to review:
  `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Shorts/Versions/v2/Neon-Parcel-Grandma-And-Bear-Short-Part-2-Test-v2.mp4`.
- Test specs: 42.2 seconds, 1080x1920, 30 fps, stereo 48 kHz audio, complete
  clip boundaries, opening one-second title overlay: "Ridiculous Grandma and
  Bear Encounters, Part Two".
- A first Part Two render was preserved as `Part-2-Test-v1`; `Part-2-Test-v2`
  corrected the canoe section framing so the dock/bear/person action remains
  visible.
- After Part Two, one strong main Shorts segment remains from this compilation
  before the pipeline moves into optional bonus or single-moment cuts.

## Neon Parcel Shorts Part Three review candidate

- After Tony approved Part Two and explicitly asked to create Part Three,
  rendered the final main Shorts segment from the approved private master.
- Output to review:
  `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Shorts/Versions/v2/Neon-Parcel-Grandma-And-Bear-Short-Part-3-Test-v1.mp4`.
- Test specs: 32.2 seconds, 1080x1920, 30 fps, stereo 48 kHz audio, complete
  clip boundaries, opening one-second title overlay: "Ridiculous Grandma and
  Bear Encounters, Part Three".
- This consumes the last strong full-story Shorts segment from the compilation;
  any additional Shorts would likely be optional bonus or single-moment cuts.

## Neon Parcel Shorts Part Three follow-action revision

- After Tony identified that Part Three needed to follow Grandma/action within
  each shot instead of holding one static crop, rendered a revised Part Three
  review candidate with denser visual sampling and timed crop glides.
- Output to review:
  `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Shorts/Versions/v2/Neon-Parcel-Grandma-And-Bear-Short-Part-3-Test-v2.mp4`.
- The revision opens on Grandma, glides toward Grandma leaving the doorway,
  reveals the bear in the hose beat, and frames the trampoline payoff as a
  group interaction.
- Verified specs: 32.2 seconds, 1080x1920, 30 fps, stereo 48 kHz audio.
