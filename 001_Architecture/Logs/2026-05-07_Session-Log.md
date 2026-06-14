## OpenAI history architecture clarified
- Tony clarified that `OpenAI_history` should be a library of readable `.md` conversation files.
- Images should live only in `007_Resource_Library/Obsidian_Attachments/`, with the `.md` files linking to them.
- The history tree should not be treated as the canonical image storage location.

## Two-part asset architecture
- Tony clarified a two-part system: conversations live in `OpenAI_history` and searchable visual assets live in `Obsidian_Attachments`.
- Image notes are the visual-library layer and should support category searches independent of the conversation they came from.

## Workspace map update
- Added `OpenAI_history/`, `Obsidian_Attachments/`, and `Obsidian_Attachments/OpenAI_Images/` to the workspace map with brief explanations.
- Renamed the new folder docs to `README.md` to match the workspace naming style.

## Review-layer collapse
- Moved files from `Image-Review` and `Ingest-Review` into the root `Needs Ingestion` bucket when they were not already represented in the canonical ingested set.
- Duplicate files already present in the target were skipped rather than churned again.

## Conversation shard move
- Moved all `conversations-*.json` shards from `OpenAI_history/Needs Ingestion` into `OpenAI_history/Already Ingested`.
- Created `OpenAI_history/Needs Ingestion/Multiple Conversations In One` as the fallback bucket for any future raw bundle that cannot be split cleanly.

## Image correlation move
- Compared raw images in `OpenAI_history/Needs Ingestion` against the canonical hashes in `Obsidian_Attachments/OpenAI_Images`.
- Moved 221 matching image files into `Already Ingested`.
- Deleted 1,670 exact duplicates that were already present in the destination.
- Left 3,795 unmatched files in `Needs Ingestion` for later review.

## Uncategorized note-link check
- Scanned `OpenAI_history/Uncategorized` for direct embeds to `Obsidian_Attachments/OpenAI_Images/Inputs` and `Outputs`.
- The uncategorized notes referenced canonical attachment files, but there were no raw `Needs Ingestion` files with exact matching names to move on this pass.
- This confirmed that filename-only matching is not enough for these notes; the canonical attachment folders remain the source of truth for the linked assets.

## N8n screenshot bucket
- Moved 879 raw files from `OpenAI_history/Needs Ingestion` into `OpenAI_history/Needs Ingestion/N8n-Screenshots/` based on `n8n` in the filename.
- Left the rest of `Needs Ingestion` untouched so Tony can review or delete the obvious N8n workflow screenshots later without touching higher-value assets.

## Keyword buckets for raw images
- Moved 642 additional files from the root of `OpenAI_history/Needs Ingestion` into keyword-based folders based on repeated filename words.
- New buckets added: `Screenshots`, `Generated-Images`, `Typography`, `Framing`, `Consular-Service-Assistant`, `Pastel-Waves`, `DNS-Checker`, and `Summer-Flowers-Arrangement`.
- The remaining root-level files in `Needs Ingestion` are now mostly the harder-to-classify items rather than the obvious repeated-name sets.

## Closeout state
- The current working model is locked in: `OpenAI_history` is the conversation layer and `Obsidian_Attachments` is the visual asset layer.
- Obvious N8n screenshots and repeated-name raw images were grouped into readable buckets so Tony can review or delete them later without per-file inspection.
- The remaining `Needs Ingestion` files are still present for a later pass and should be treated as the unresolved remainder, not as already processed assets.
