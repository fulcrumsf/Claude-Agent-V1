---
name: reimagined-realms-pov-shorts-pipeline
description: Use when building Reimagined Realms POV Shorts (vertical historical "day in the life" videos with no dialogue). This skill folder currently contains the Foley/SFX generator sub-component only — beat planning, image/video generation, assembly, and publishing are separate, later plans. Foley invocation — python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/generate_foley.py <video_path> --out <audio_output_path> [--prompt "text hint"] [--model mirelo|sonilo]
---

# Reimagined Realms POV Shorts Pipeline

Vertical (9:16), historical "day in the life" POV videos with no dialogue for the Reimagined Realms channel. See the full design at `001_Architecture/Superpowers/Specs/2026-08-01-RR-POV-Shorts-Pipeline-Design.md` and the distilled reference conventions at `POV_Style_Guide.md` in this folder.

## Foley/SFX Generator (built)

`generate_foley.py` takes any local video clip and produces a synced Foley/ambient audio track via either Mirelo SFX or Sonilo SFX (both on WaveSpeed) — used per-clip in the pipeline's sound design phase, and standalone for Tony's A/B model comparison.

**Usage:**

```bash
python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/generate_foley.py \
  "<video_path>" --out "<audio_output_path>" --prompt "footsteps on straw" --model mirelo
```

**Swapping the default model:** edit `FOLEY_MODEL` in `foley_config.py` — that's the only line that needs to change after the A/B test picks a winner. `--model` on the CLI overrides the default for a single call without touching the config file (useful for the A/B test itself, running both models against the same clip).

## Not yet built

Beat planning, shot list generation, cost estimation, image/video generation, assembly, text overlay, YouTube package, and Blotato upload — each is a separate implementation plan per the design spec's phase list.
