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
