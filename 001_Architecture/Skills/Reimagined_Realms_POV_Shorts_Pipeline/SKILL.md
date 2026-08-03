---
name: reimagined-realms-pov-shorts-pipeline
description: Use when building Reimagined Realms POV Shorts (vertical historical "day in the life" videos with no dialogue), planning beats/scenes, generating a shot list, generating/trimming scene images and video clips, assembling the final cut, or compositing text-overlay captions onto the assembled video. This skill folder currently has the Foley/SFX generator, beat planning (scenes_needed_for_floor, write_beat_table), shot list generation (build_video_prompt, write_shot_list), image generation (generate_image via GPT-Image-2), video generation (generate_video via Seedance 1.5 Pro with native audio), clip trimming (trim_to_best_window), assembly (concatenate_videos, audio extraction/stitching, music generation via Suno, LUFS mix/normalize, and versioned final mux via get_next_version/mux_final), and text overlay (build_caption_props, write_props_file, ensure_public_symlink, render_text_overlay via the Remotion POVShort composition) built — YouTube trend-research ideation, YouTube package, and Blotato upload are separate, later plans. Foley invocation — python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/generate_foley.py <video_path> --out <audio_output_path> [--prompt "text hint"] [--model mirelo|sonilo]
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

## Intake, Beat Planning & Shot List (built)

**Intake:** at the start of every production, ask Tony to either (a) name a topic directly (era + role, e.g. "medieval peasant," "pyramid builder"), or (b) request idea suggestions. Path (b) — YouTube trend-research ideation — is not yet built; if Tony asks for suggestions, say so and ask for a named topic instead until that plan exists.

**Beat planning:** once a topic is set, generate a day-in-life scene list (~5s/scene, opening with a waking-up beat per `POV_Style_Guide.md`). Use `scenes_needed_for_floor()` (in `beat_planning.py`) to check whether the scene count reaches the 65s floor — if not, add that many more day-in-life beats before finalizing. Save the beat list via `write_beat_table()` to `<production_folder>/Data/Beat_Table.json`.

**Shot list:** for each beat, write an image prompt (GPT-Image-2 style) and gather the scene's sound events and camera_fixed flag (per `POV_Style_Guide.md`'s camera conventions), then call `write_shot_list()` (in `shot_list_builder.py`) to produce `<production_folder>/Production/Shot_List.md`. When converting a beat dict from `Beat_Table.json` to a shot dict for `write_shot_list()`, map the beat's `"description"` field to the shot's `"scene_description"` field; supply `"image_prompt"` and `"sound_events"` fresh per shot (they are not derived from the beat table), and carry `"camera_fixed"` over unchanged. `write_shot_list()` internally calls `build_video_prompt()`, which auto-appends the mandatory Seedance negative-prompt closer and raises `ValueError` if any quoted dialogue-like text is detected in the scene description or sound events. Never hand-assemble a Seedance video prompt outside this function — the safety check only applies if you call it.

## Image & Video Generation (built)

**Image generation:** `generate_image(prompt, output_path, aspect_ratio="9:16", resolution="1K")` in `image_generation.py` — submits to GPT-Image-2 via `kie-cli gpt_image_2`, polls `kie-cli get_task_status` until completion, downloads the result. CLI: `python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/image_generation.py "<prompt>" --out "<path>"`.

**Video generation:** `generate_video(image_url, video_prompt, output_path, duration=5, resolution="1080p", aspect_ratio="9:16")` in `video_generation.py` — runs Seedance 1.5 Pro via `wavespeed run bytedance/seedance-v1.5-pro/image-to-video` with `generate_audio=true` (the model/platform/params validated by the live A/B test that chose Seedance native audio over dedicated Foley models). Note: the reference image (from `generate_image()`) is a local file path and must first be uploaded to a public URL via `wavespeed upload <path> --json`, then parse the returned `url` field before passing it to `generate_video()`. `video_prompt` must be pre-built via `shot_list_builder.build_video_prompt()` — never hand-assemble it. CLI: `python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/video_generation.py "<image_url>" "<prompt>" --out "<path>"`.

**Clip trimming:** `trim_to_best_window(video_path, output_path, target_seconds=5.0)` in the same module — if a generated clip exceeds the target length, trims to the middle window (a heuristic, not motion-aware; a future improvement could pick a genuinely-best window via scene/motion detection). Call this after every `generate_video()` call before using the clip downstream.

## Assembly (built)

**Video concatenation:** `concatenate_videos(video_paths, output_path)` in `assembly.py` — concatenates per-scene clips (video-only, audio stripped) into `Video_Stitched.mp4`.

**Audio extraction:** `extract_audio(video_path, output_path)` and `stitch_audio_files(audio_paths, output_path)` in `audio_extraction.py` — pulls each clip's native Seedance audio into `Clip_Audio/`, then stitches into `Ambient_Foley_Full.mp3`.

**Music:** `generate_music(prompt, output_path)` in `music_generation.py` — Suno via kie-cli (note: real status strings are case-varying, e.g. `"SUCCESS"` vs image generation's `"success"` — comparisons are case-insensitive). `fit_music_to_duration(music_path, output_path, target_seconds)` trims (if longer) or loops (if shorter) the track to the video's exact runtime.

**Mix + normalize:** `measure_lufs`, `calculate_gain`, `mix_and_normalize` in `assembly.py` — measures foley and music LUFS via `ffmpeg loudnorm`, calculates each track's gain to hit -14 LUFS (foley) / -23 LUFS (music, ~9dB under foley per the style guide's bed convention), mixes via `amix`.

**Final mux:** `get_next_version` and `mux_final` in `assembly.py` — muxes the silent stitched video with the mixed audio into a versioned `Final_vN.mp4` (never overwrites a prior version).

## Text Overlay (built)

Composites per-scene captions onto an assembled `Final_vN.mp4` using the Remotion project at `002_Content-Creation/Video_Editor/003_Remotion/` (component: `POVCaption.tsx`, composition: `POVShort.tsx`, registered in `Root.tsx`).

**Python wrapper** (`text_overlay.py`): `build_caption_props(background_video_file, captions, fps=24)` converts snake_case caption dicts (`text`/`start_s`/`duration_s`/`variant`) into the camelCase props shape the Remotion composition expects, `write_props_file(props, output_path)` writes them to disk, `ensure_public_symlink(production_dir, symlink_name)` creates the `003_Remotion/public/<name>` symlink the composition reads its background video from (matching the existing `render_bioluminescence.sh` convention), `render_text_overlay(props_path, output_path)` invokes `npx remotion render POVShort ...` via subprocess.

Caption text/timing is decided by the orchestrating Claude session at runtime per scene (same pattern as beat planning and shot list generation) — this module only handles the mechanical props/symlink/render plumbing, never the creative wording.

## Not yet built (updated)

YouTube trend-research ideation, YouTube package, and Blotato upload — each is a separate implementation plan.
