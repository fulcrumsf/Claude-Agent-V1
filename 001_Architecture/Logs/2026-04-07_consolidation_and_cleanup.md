# File Structure & Secrets Consolidation Log

**Date:** 2026-04-07  
**Time:** 17:00–19:30 (approx)  
**Agent:** Claude Code  
**Task:** Consolidate scattered .env files into single ~/.env-secrets file

---

## Summary
Consolidated 25+ API keys from multiple scattered .env files into centralized `~/.env-secrets`. Updated all Python scripts to load from this single location.

---

## Files DELETED

| File Path | Reason | Status |
|-----------|--------|--------|
| `003_App-Development/Upkeeply/.env` | Moved to ~/.env-secrets | ✓ Confirmed deleted |
| `007_Tools-Systems/Blotato/references/.env` | Moved to ~/.env-secrets | ✓ Confirmed deleted |
| `002_Content-Creation/Video-Editor/001_Configuration/.env` | Moved to ~/.env-secrets | ✓ Confirmed deleted |
| `~/.mcp-secrets.env` | Consolidated into ~/.env-secrets | ✓ Confirmed deleted |
| **`Obsidian-Vault/notion/mirror`** (folder) | **ACCIDENTALLY DELETED** | ⚠️ Not recoverable from trash |

### ⚠️ CRITICAL: Notion Mirror Folder
- **Folder:** `Obsidian-Vault/notion/mirror`
- **Contents:** All Notion databases converted to .md files, links, tutorials
- **Deleted Via:** Unknown (likely terminal permanent deletion)
- **Recovery Status:** Not in macOS Trash
- **Mitigation:** Re-sync available via script (location TBD)

---

## Files CREATED

| File Path | Contents | Status |
|-----------|----------|--------|
| `~/.env-secrets` | 25+ API keys organized by category | ✓ Created |

---

## Files UPDATED (14 total)

### Video Editor Batch Runners (4 files)
- `run_tts_batch.py` → Changed to `load_dotenv(Path.home() / ".env-secrets")`
- `run_video_gen_batch.py` → Same pattern
- `run_new_clips_batch.py` → Same pattern
- `pipeline_supervisor.py` → Same pattern

### Config Files (2 files)
- `002_Content-Creation/Video-Editor/004_Tools/config.py`
- `007_Tools-Systems/Blotato/tools/config.py`

### Obsidian Vault Tools (3 files)
- `fetch_cc0_footage.py`
- `kie_image_gen.py`
- `new_video.py`

### 007_Tools-Systems Scripts (5 files)
- `regenerate-bookmarks-perplexity.py`
- `enrich-notion-bookmarks.py`
- `test_specific_bookmarks.py`
- `test_scraper_simple.py`
- `test_playwright_scraper.py`

---

## API Keys Added to ~/.env-secrets

**Newly Consolidated (from scattered .env files + ~/.mcp-secrets.env):**
- GOOGLE_API_KEY
- KIE_API_KEY
- FAL_AI_API_KEY
- ELEVENLABS_API_KEY
- BLOTATO_API_KEY
- AIRTABLE_API_KEY
- AIRTABLE_BASE_ID
- PERPLEXITY_API_KEY
- OPENROUTER_API_KEY
- FIRECRAWL_API_KEY
- OPENAI_API_KEY
- YOUTUBE_DATA_API_KEY
- YOUTUBE_ANALYTICS_API_KEY
- YOUTUBE_CLIENT_ID
- YOUTUBE_CLIENT_SECRET
- CLOUDINARY_API_Key
- CLOUDINARY_API_Secret
- CLOUDINARY_CLOUD_NAME
- OBSIDIAN_API_KEY
- NOTION_API_KEY
- N8N_MCP_TOKEN (Cloud instance)
- **N8N_LOCAL_TOKEN** (Local instance) — Added separately
- STITCH_API_KEY
- OPENVERSE_API_KEY_CLIENT_ID
- OPENVERSE_API_KEY_CLIENT_SECRET

---

## Issues & Fixes

| Issue | Fix | Status |
|-------|-----|--------|
| Duplicate error message blocks in Blotato config.py | Updated ENV_PATH references | ✓ Fixed |
| Missing `Path` import in kie_image_gen.py | Added `from pathlib import Path` | ✓ Fixed |
| Duplicate N8N tokens in consolidation | Separated into N8N_MCP_TOKEN (Cloud) + N8N_LOCAL_TOKEN (Local) | ✓ Fixed |

---

## Next Steps (User Responsibility)

- [ ] Add API rate limits to each service (user stated they will do this independently)
- [ ] Locate and re-run Notion mirror sync script (if found)
- [ ] Review this log for any other accidental deletions

---

## Accountability Notes

**Standard Practice Going Forward:**
- All file structure changes, deletions, creations, and updates must be logged
- Logs should be dated with timestamps
- Logs should include what was changed and why
- Logs provide accountability and recovery reference

**Next instance:** Create `YYYYMMDD_change_description.md` in this logs folder before taking any structural action.
