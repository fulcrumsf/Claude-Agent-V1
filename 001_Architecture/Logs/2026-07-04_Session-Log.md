# Session Log — 2026-07-04

## Production: 0001_Pompeii_The_Escape (Reimagined Realms)

### Video fixes
- C20 regenerated: new image (no boat, no figures) + new video via Seedance 1.5. Retrimmed, raw_video.mp4 rebuilt.
- V7 rendered: corrected C20, locked audio formula (stems -23 LUFS vol=0.88, narration -14 LUFS vol=3.09, sidechain duck)
- V8 rendered: V7 + Suno music bed (suno_v3, 240s, LRA=10.2 selected by automated LUFS/duration analysis)

### Suno fixes
- Endpoint corrected: /api/v1/generate (was /jobs/createTask)
- callBackUrl required field added (placeholder https://example.com/callback)
- Polling parser fixed: handles array of URLs, picks longest by ffprobe duration
- 4 candidates downloaded to Assembly/suno_candidates/, suno_v3 selected automatically

### Pipeline rules locked
- 8s hard max per clip (assemble.py + SKILL.md)
- 163 WPM × 1.15 script padding formula (SKILL.md)
- TTS duration validation gate added (SKILL.md)
- Title formulas: 3 locked (curiosity gap primary, discovery secondary, pattern interrupt tertiary)
- Thumbnail formula: composition-based (lone human, back to camera, deep perspective, palette matches story)
- Description formula: search intent first, curiosity hook is title's job

### assemble.py universalized
- Universal version: 001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/assemble.py
- Reads Production/assemble_config.json per production (suno_prompt, suno_tags, caption lines)
- Pompeii config created: Production/assemble_config.json
- SKILL.md updated: Phase 8 now generates assemble_config.json

### Thumbnail generation
- 3 concepts generated via GPT Image 2 (Package/Thumbnails/)
- Tony's pick: C (Aftermath Mystery — lone figure, ash-covered Pompeii, Vesuvius silhouette)
- Rejected: B (figures too small at thumbnail size), A (strong but C more unique)

### Files created/modified this session
- 001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/assemble.py (NEW — universal)
- Productions/0001_Pompeii_The_Escape/Production/assemble_config.json (NEW)
- Productions/0001_Pompeii_The_Escape/Production/Shot_List.md (C20 prompts updated — no boat)
- Productions/0001_Pompeii_The_Escape/assemble.py (8s cap, Suno fixes, --overwrite flag)
- 001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/batch_generate_images.py (--clips, --overwrite added)
- ~/.claude/skills/Reimagined_Realms_Video_Pipeline/SKILL.md (title/thumbnail/description/duration rules)
- Assembly/V7/, Assembly/V8/ (rendered versions)
- Assembly/suno_candidates/ (4 Suno tracks)
- Assembly/music.mp3 (suno_v3 selected)
- Package/Thumbnails/ (3 concept PNGs)

### Pending (next session)
- Blotato YouTube upload skill (separate skill, tomorrow)
- Description chapter auto-generator from Beatmap.json (small script, before first upload)
- Test video 2 (validate full pipeline end-to-end on new topic)

### Future context (do not build yet)
- Airtable-driven pipeline: after 10 validated videos, intake questions become Airtable columns
- Short-form pipeline: separate 9:16 mode, after long-form is fully validated
- Idea generation cron: daily idea queue, cap ~10 ungenerated ideas, Tony approves/ignores
- All future pipeline automation discussed with Tony 2026-07-04 — see memory

---

## Session 2 (same day): Blotato MCP registration verified, first upload, pipeline locked through Phase 12

### Blotato upload
- Verified Blotato MCP tools live after restart (`mcp__blotato__*`), confirmed accounts: NeonParcel (25731), ReimaginedRealms (30323, 18 playlists)
- Uploaded Pompeii V8 to ReimaginedRealms as private: `https://www.youtube.com/watch?v=3Y8e8hOs7Ks`
- Thumbnail compressed 2.45MB PNG → 211KB JPEG (ffmpeg) to satisfy Blotato's 2MB limit
- First attempt failed — "reconnect your YouTube account" for custom thumbnails (OAuth scope). Tony reconnected in Blotato dashboard, retry succeeded without re-uploading media.

### CTA / end-screen system (new, locked)
- Static CTA audio generated once via ElevenLabs (locked voice raMcNf2S8wCmuaBcyI6E): "Follow Reimagined Realms. History gets stranger every episode." — 3.76s
- Saved as reusable channel-wide asset: `Brand_Assets/CTA/cta_follow_reimagined_realms.mp3`
- `assemble.py` (universal) now auto-appends 1.5s silence gap + this CTA audio to end of narration every run — verified with ffmpeg smoke test (2s+1.5s+3.76s=7.26s, math checked out)
- Beatmap rule added: final act's last sub-beat = "CTA Hold" beat, fixed 8.0s duration, single continuous clip, never derived from VO timing

### SKILL.md — now a true 12-phase pipeline
- Phase 4: removed spoken CTA line from script generation (CTA is post-production only now)
- Phase 8: CTA Hold beat rule added to beatmap generation
- Phase 9: CTA Hold shot template added
- New Phase 11: media generation + assembly (pause after test clip C1)
- New Phase 12: Blotato upload (pause for title/thumbnail/privacy, then automated upload with locked defaults: isMadeForKids=false, containsSyntheticMedia=true, private, playlists manual)
- Frontmatter/intro/final-delivery summary updated to reflect start-to-finish execution, not a manual handoff

### Tooling gap found and fixed
- `generate_system_map.py` only scanned `claude_desktop_config.json` for MCPs — never scanned `~/.claude.json`, where Claude Code CLI actually stores `claude mcp add` registrations (project-scoped). This is why Blotato wasn't showing up in System-Map.md despite being registered and working.
- Fixed: `scan_mcps()` now also reads `~/.claude.json` (global + per-project `mcpServers`). Regenerated System-Map.md — Blotato now correctly appears under the Agent-OS project entry.
- TOOLBOX.md updated (2 sections) with full Blotato MCP tool list, connected accounts, thumbnail size gotcha, and OAuth reconnect gotcha.

### Graphify
- Architecture domain AST/code graph refreshed (`graphify update .`) after SKILL.md/assemble.py/memory edits.
- Did NOT run full semantic `--update` — incremental detector flagged ~993 non-code files as changed, almost all pre-existing/unrelated (stale manifest from repeated fast-path `graphify update` calls that never write the manifest the full skill flow expects). Flagged as a separate hygiene issue, not addressed this session to avoid a disproportionate reindex.

### Memory written
- Global_Agent_Memory.md: new 2026-07-04 entry (Blotato live + CTA system + Phase 11/12 lock-in), stale "build next session" bullet removed
- feedback_reimagined_realms.md (claude-mem): new CTA gap-vs-hold rule entry
- project_pompeii_next.md (claude-mem): updated to published/complete status, next-session pointer to test video 2
- MEMORY.md index: both Pompeii and Reimagined Realms skill lines updated

### Pending / next session
- Test video 2 — run `/reimagined-realms` fully autonomously start to finish on a new topic, to prove Phase 11-12 work from the skill's own instructions (not just manual execution)
- Graphify manifest hygiene (separate task, not blocking)
- Chapter auto-generator from Beatmap.json (nice-to-have, currently manual)
