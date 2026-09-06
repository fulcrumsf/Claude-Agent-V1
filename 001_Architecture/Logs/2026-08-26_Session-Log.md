# 2026-08-26 Session Log

## Neon Parcel Shot Complexity Router

- Added `route_shot_complexity.py`, an explainable pre-generation router for
  simple, complex, and borderline shots.
- Added unit coverage for model routing, physics hard gates, human overrides,
  borderline review, and document output.
- Connected the router to the Neon Parcel skill, YAML pipeline contract, and
  `TOOLBOX.md`.
- No production media, shot list, skills outside this pipeline, or provider
  calls were changed.
- Verification: seven Neon Parcel unit tests passed, Python syntax checks
  passed, and the CLI smoke test passed.
- Locked the resolution path: Seedance 2 Mini 480p -> Topaz 2x -> FFmpeg
  1920x1080; Seedance 1.5 route remains native 1080p.
