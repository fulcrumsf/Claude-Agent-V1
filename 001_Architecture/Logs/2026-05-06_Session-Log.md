## 2026-05-06 Session Log

- Added `001_Architecture/Scripts/phase2_chatgpt_profile.py` to distill approved ChatGPT themes into `001_Architecture/Memory/ChatGPT_Profile/`.
- Ran Phase 2 against all 2,011 conversations in `007_Resource_Library/OpenAI_History/`.
- Generated 18 profile notes, one per approved theme from `ChatGPT_Theme_Report.md`.
- Created `001_Architecture/Memory/ChatGPT_Profile/phase2_progress.json` as a checkpoint file, then regenerated the notes after tag-slug cleanup.
- Updated `001_Architecture/Install_Maps/Workspace-Map.md`, `001_Architecture/Memory/Memory_Index.md`, and `001_Architecture/Memory/Global_Agent_Memory.md` to acknowledge the new ChatGPT profile memory layer.
- Phase 2 notes now include theme-level summaries, recurring vocabulary, prompt style signals, preferences, and linked images where applicable.
- Built `001_Architecture/Scripts/phase3_chatgpt_structured_ingest.py` to turn the ChatGPT export into theme folders, readable conversation notes, and split image assets into `Obsidian_Attachments/OpenAI_Images/Inputs|Outputs`.
- Ran the structured Phase 3 ingest across all 2,011 conversations and wrote 2,011 conversation notes plus 201 image notes.
- The ingest created `007_Resource_Library/OpenAI_History/Index.md` and `007_Resource_Library/Obsidian_Attachments/OpenAI_Images/output_index.json` as the new navigation layer.
- Vision calls failed in this environment because the external API hosts were not reachable, so the image naming fallback was used for this pass.
- Switched the image vision path to OpenAI-only `gpt-4o-mini` to avoid Gemini and keep the cost path aligned with Tony's preference.
- Re-ran Phase 3 after the model switch; the structural output completed again, but `api.openai.com` still could not be resolved from this environment, so the fallback path remained in effect for image descriptions.
- Tried sourcing `~/.env-secrets` and rerunning Phase 3 from Codex; the API key loaded, but the same DNS resolution failure persisted in the Codex sandbox.
- Patched the Phase 3 image pipeline to retry only notes with fallback vision text, process in smaller batches, and back off on OpenAI `429` responses.
- Launched the retry pass from a network-enabled shell with `~/.env-secrets` loaded; it is still running while the retry queue works through the remaining images.
- Reduced the batch size from 10 to 5 for the retry pass to further lower request bursts and reduce `429` pressure.
- Restored `007_Resource_Library/Research/OpenAI_Images/Inputs` by copying 1,667 resolved user-upload image assets from `OpenAI_History` and writing `input_index.json` with conversation mappings.
- Patched `phase3_chatgpt_structured_ingest.py` so conversation notes can embed the saved input-image links directly from `input_index.json`.
- Re-ran the Phase 3 input pass so `OpenAI_History` notes now include `## Input Images` embeds for conversations that actually contain uploaded image assets.
- Moved the 303 staged ChatGPT original image files into `007_Resource_Library/Obsidian_Attachments/OpenAI_Images/ingested/` so the raw originals are grouped separately from Research copies.
- Promoted `007_Resource_Library/Obsidian_Attachments/OpenAI_Images/Inputs` and `Outputs` to the canonical asset location, moved the corresponding `input_index.json` and `output_index.json` there, and rewrote the vault links so notes point to the new attachment-root paths.
- Removed the extra `Notes/` subfolder assumption from `phase3_chatgpt_structured_ingest.py`; image notes now write directly into `007_Resource_Library/Research/OpenAI_Images/` as requested.
- Quarantined 501 duplicate output images into `007_Resource_Library/Obsidian_Attachments/OpenAI_Images/Outputs/quarantine-delete-later/`, leaving 200 canonical output files in place.
- Quarantined 108 duplicate input images into `007_Resource_Library/Obsidian_Attachments/OpenAI_Images/Inputs/quarantine-delete-later/`, leaving 1,560 canonical input files in place.
- Created `007_Resource_Library/OpenAI_History/Image-Review/` as a non-destructive hard-link mirror of the raw OpenAI History image assets so Tony can browse the files in one place without renaming or moving the originals.
- Patched the OpenAI History image walkers in `phase3_image_pipeline.py` and `phase3_chatgpt_structured_ingest.py` to ignore `Image-Review/` so the mirror folder is not re-ingested as source data.
- Tony corrected the image-organization requirement: the next image-handling pass should produce explicitly labeled staging boxes/folders with backtrackable context, not just a raw mirrored folder of files.
- Built `007_Resource_Library/OpenAI_History/Boxed-Inventory/` as a hard-link inventory with labeled buckets for confirmed ingested inputs/outputs, generated outputs, user-upload-like files, documents, exact duplicates, and a needs-review fallback, plus a manifest for backtracking.
- Replaced the multi-bucket review experiment with `007_Resource_Library/OpenAI_History/Ingest-Review/`, which uses two explicit boxes: `Already-Ingested-Delete-Later` and `Needs-Ingesting`.
## OpenAI history status folders
- Moved the root-level files from `007_Resource_Library/OpenAI_history` into two status folders only: `Already Ingested` and `Needs Ingestion`.
- Used move semantics, not copies, so the root no longer shows the raw file pile.
- Final move counts: 1,670 files into `Already Ingested` and 3,381 files into `Needs Ingestion`.

## OpenAI history conversation buckets
- Grouped the root-level UUID-style conversation folders in `007_Resource_Library/OpenAI_history` into `Already-Gone-Through-Theme-Process` so the root is human-readable.
- The folders are raw conversation export buckets, not theme folders, which is why they were not part of the theme classification output.
