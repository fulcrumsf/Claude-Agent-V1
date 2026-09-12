
## Neon Parcel Part Three — Saved Hybrid Export

Tony authorized saving the selected Part Three Hybrid as a 9:16 production Short. Created `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Shorts/Versions/v3/Neon-Parcel-Grandma-And-Bear-Short-Part-3-Hybrid-v1.mp4` from Gate-3-Run-002 Hybrid, retaining the existing first-second Part Three title overlay. Verified 1080×1920, 30 fps, 968 frames, 32.266 seconds, full decode, and unchanged copied audio payload. Export receipt saved alongside video. Source Hybrid hash verified unchanged; earlier Shorts preserved. No channel integration or publishing performed.

## Resource Library Visualizer — refinement pass #1

Processed the finalized Review_Queue batch (5 comments, 0 deletes): recategorized/retagged Google-Inulin-Products (personal, health/gut-health), Across-The-Globe-YOUTUBE (research/channel-study), Midjourney-Comic-Style (design-inspiration), React-Bits-Web (app-dev), Collabaway (travel). Queue file checked off + annotated.

Root-caused the "blank card" bug: ~30 notes had unescaped `"` inside double-quoted `ai_description` YAML, so the whole frontmatter was dropped by the parser. Fix script (`scratchpad/fix_yaml.py`): repaired the 25 remaining broken files by converting the offending line to a `>-` block scalar, and promoted `ai_description` to `summary` on 361 notes so every card shows a blurb. Final sweep: 0 broken frontmatter across 4001 notes.

Hardened `notes.py`: `parse_note` now falls back to `_loose_frontmatter()` (regex scrape of scalars + first block list) when YAML fails, so one bad field never blanks a card again. New test `test_parse_note_broken_yaml_recovers_title_and_tags`; 40/40 pytest green.

Title cleanup (`scratchpad/titles.py`): stripped `Unomas0795` prefix + Midjourney param/UUID junk from 45 titles; derived titles from summary for 20 `Stn-<hash>` notes; flipped `research` to `design-inspiration` (category + tag) on the 26 Midjourney generations. Some MJ titles end mid-word because source filenames were truncated at ingest — cosmetic. `ai_description` kept alongside `summary` as raw-AI-output provenance.

Server restarted at localhost:8756. Nothing committed yet.

## RL taxonomy redesign (in progress) + Move button

Long design conversation on the Resource Library folder/tag taxonomy. Mapped how the 3 intake paths actually work (image vision script = pixels-only, prompt-baked 11 folders, free-form tags, never reads Directory.md / clipper .md = agent-driven per SKILL.md + Directory.md / ChatGPT export = frozen one-off). Measured tag sprawl: 3,414 distinct tags, 2,563 used once. Saved `project_resource_library_workflow.md` + `feedback_capitalize_vocab_values.md` to Claude memory.

Emerging design (NOT locked): field stack = Source (auto) · Folder · Form (model) · Domain (model, fixed list: Video/Image/Audio/LLM/Automation/3D/Web/Design) · Intent (optional: Tool-To-Try/Post-Idea/Video-Idea/Build-Idea/Harden/Study/Reference/Visual-Style-Reference) · Project (=departments) · cascading sub-field (Channel if Content-Creation, Line if E-Commerce, Program if Affiliate). Hard rule agreed: source youtube -> Tutorials always. Plan: build an ingest triage visualizer for `000_Ingest/` with batch field-assign, AFTER Tony re-organizes the existing library by folder.

Shipped now so Tony can start re-organizing:
- Created `007_Resource_Library/Mockups/` + `Content_Ideas/` (+ .gitkeep), Directory.md entries added, Design_Inspiration description narrowed.
- RL Visualizer: added **Move** bulk action — select cards, pick destination folder, moves .md + co-located image(s); `actions.move_note()` (path-traversal guarded, dup-stem guarded), `POST /api/move`, `/api/filters` now returns `move_targets` + includes empty folders. 42/42 pytest. Live round-trip verified.
- KNOWN GAP: Move does not rewrite the `category:` frontmatter field (left for the field-schema rework, since `category:` is already inconsistent library-wide).

## Hyperframes and Remotion version audit
- Verified global Hyperframes 0.6.76; local source checkout CLI manifest 0.6.25. Main Video Editor Remotion and CLI installed at 4.0.438.
- Current web npm listings: Hyperframes 0.8.33, Remotion 4.0.523 (also confirmed in official GitHub releases). Direct npm registry queries failed with sandbox DNS ENOTFOUND; web lookup succeeded.
- Confirmed hyperframes, hyperframes-cli, and remotion-best-practices SKILL.md files accessible through Codex and Claude skill paths. No upgrades performed.
