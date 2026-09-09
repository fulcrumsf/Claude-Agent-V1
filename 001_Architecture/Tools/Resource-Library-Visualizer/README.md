# Resource Library Visualizer

Local browser gallery for reviewing / culling `007_Resource_Library`.

## Run

    python3 001_Architecture/Tools/Resource-Library-Visualizer/serve.py

Opens http://localhost:8756 in your browser.

## What it does

- Grid of every note that has an image or a YouTube video, newest first.
- Filter by folder, source type, or tag.
- Click a card -> the note rendered Obsidian-style.
- Select cards -> **Delete** (moves note + image to `~/Desktop/delete/`) or
  **Re-run AI**.
- Per card: **Edit** fields, **Re-run AI**, **Add Comment**.
- Comments + edit requests append to
  `~/Desktop/Resource_Library_Review/Review_Queue.md`; **Finalize Queue**
  seals a batch to hand to the agent.

Nothing is ever hard-deleted and nothing is committed to git.

## Known limits

- **Cold start ~10-15s** — it parses every `.md` in `007_Resource_Library` on
  launch (no on-disk index cache yet). The terminal prints `scanning …` then
  `indexed N notes` when ready.
- **Source-type labels are heuristic (~90%).** `Screenshot` is the default for
  any image note; `Bookmark` only fires when a note has an `http` `source:` and
  an image; `⚠` marks `original_filename: IMG_####` iPhone captures (most
  Vision-error-prone).
- **`Re-run AI`** calls `001_Architecture/Scripts/process_image_ingest.py`
  `process_image()` (OpenRouter vision, then OpenAI fallback). Needs
  `OPENROUTER_API_KEY` in `~/.env-secrets`. Rough cost estimate shown is
  `$0.01 / note`.
- **Deletes go to `~/Desktop/delete/`** (case-insensitive match with the
  existing `~/Desktop/Delete/` review folder on macOS). Review there before
  removing anything for real.
- No in-app git. Review the working-tree diff separately after an edit session.

## Tests

    python3 -m pytest tests/resource_library_visualizer/ -v
