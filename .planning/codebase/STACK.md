# Stack

## Runtime
- Python 3.x scripts with standard-library-first implementations.
- Shell commands and FFmpeg/ImageMagick-style media utilities are used for inspection and normalization.
- No repository-wide package manifest; tooling is organized by workspace department.

## Relevant Components
- Neon Parcel helpers live in `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/`.
- Production artifacts live under `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/`.
- Skills are Markdown contracts in `001_Architecture/Skills/`.
- Generation/provider behavior is documented in `TOOLBOX.md` and shared tool folders.

## Current Workflow Technology
- GPT-Image-2 creates storyboard/reference images.
- Seedance generates video clips through the configured provider wrappers.
- JSON and JSONL files provide auditable state and generation history.
- `unittest` is used for focused Python tests; relevant tests sit beside the Neon Parcel modules.

## Constraints
- Paid generation must be guarded and explicitly logged.
- Prompt files are archived before submission and hashed by `generation_guard.py`.
- Superseded media and prompts are moved to `Archived/`, never deleted.
- Storyboard images are reference inputs, not temporal first-frame inputs.
