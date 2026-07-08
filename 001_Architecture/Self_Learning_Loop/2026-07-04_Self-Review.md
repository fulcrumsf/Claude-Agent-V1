# Self-Review — 2026-07-04

## What went wrong and why

### 1. assemble.py was never made universal
Built it inside the Pompeii folder with hardcoded values from day one. Should have recognized immediately that any script with story-specific constants (Suno prompt, caption text) belongs in a config file, not the script. Fixed today but should have been caught at design time.

### 2. TTS duration not validated against target
Script was written to approximate word count. ElevenLabs came in 27s short of the 3-minute target. A one-line ffprobe check after TTS would have caught this before any clips were generated. This is now in SKILL.md but should have been a standard step from the beginning.

### 3. Suno endpoint was wrong
Used /jobs/createTask for Suno when the correct endpoint is /api/v1/generate. Should have verified the API endpoint against the documentation Tony provided rather than assuming it matched the video generation endpoint pattern.

### 4. C20 boat direction — over-constrained the fix
First fix: added explicit directional constraints to the video prompt. Model still rendered backwards. Better fix: remove the moving subject entirely. When a model consistently fails a spatial constraint, removing the subject is more reliable than adding more prompt rules.

### 5. Polling parser didn't handle Suno's array response
Assumed Suno would return a single URL like the video API. It returns an array. Should have either read the API docs or tested with a print statement before building the parser.

## What worked well

### Locked audio formula
LUFS measurement → gain correction → sidechain ducking solved the narration-buried-under-SFX problem definitively. The three-step approach (measure, correct, duck) is the right model for any future mixing task.

### Automated Suno candidate selection
Using ffprobe duration + LRA to pick the best Suno track is sound. Longest duration = most headroom. Highest LRA = most dynamic = best for documentary. This is a repeatable selection algorithm.

### Parallel background jobs
Running C20 image generation and Suno simultaneously saved real time. Pattern worth maintaining: whenever two API calls are independent, run them in parallel.

## Patterns to carry forward

- Every script must take production_folder as argument — no hardcoded paths, ever
- Every new API endpoint must be verified before building the polling loop
- After TTS: always ffprobe and compare to target before proceeding
- Spatial constraints in video prompts: if model fails twice, remove the subject, don't add more rules
- Suno selection: longest duration + highest LRA wins
