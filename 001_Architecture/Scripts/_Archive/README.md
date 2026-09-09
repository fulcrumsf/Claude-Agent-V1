# Scripts Archive

Deprecated scripts, kept for reference / possible future rework. **Do not run these.**
Nothing in the workspace should invoke a script from this folder.

| Script | Retired | Why |
|--------|---------|-----|
| `reroute_visual_assets.py` | 2026-09-09 | Routed images from the retired `Visual_Assets/` into category folders — the one-time `migrate_images_to_notes.py` did this permanently. |
| `fix_image_case.py` | 2026-09-09 | Renamed lowercase image filenames inside `Visual_Assets/` (folder deleted; migration normalized all names). |
| `update_asset_notes_vision.py` | 2026-09-09 | Re-visioned filler descriptions on images in `Visual_Assets/` (folder deleted; notes enriched). |
| `fix_embeds.py` | 2026-09-09 | Fixed wrong-case `![[]]` embeds via a `Visual_Assets/` lookup (all embeds now verified + images co-located). |
| `rename_screenshots.py` | 2026-09-09 | Superseded by `process_image_ingest.py`; produced lowercase kebab-case names. |

Current image ingest: `001_Architecture/Scripts/process_image_ingest.py` — writes note + image
side by side in the category folder, dedups on ingest.
