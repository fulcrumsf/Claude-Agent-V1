# Next Session Handoff — 2026-06-20

Pick this up at the top and work down in order.

---

## STEP 1 — Install fal.ai CLI (global)

The last CLI in the set. Research, validate safety, install globally, check for API key in `~/.env-secrets`, wire key to shell environment in `~/.zshrc` following the same pattern as kie-cli and wavespeed.

Expected key name in `~/.env-secrets`: likely `FAL_AI_API_KEY` (already present — confirmed earlier).

---

## STEP 2 — Fix WAVESPEED_API_KEY

`WAVESPEED_API_KEY` was NOT found in `~/.env-secrets` at end of session even though Tony said he added it. Verify the key name is exactly `WAVESPEED_API_KEY`. If present, test with `wavespeed status`.

---

## STEP 3 — Update TOOLBOX.md

Add entries for all three new CLIs installed this session:
- `kie-cli` (`@felores/kie-cli`) — kie.ai image/video/audio generation
- `wavespeed` (`@wavespeed/cli`) — WaveSpeed image/video/audio/3D generation, includes `wavespeed price <model>`
- `autohand` (autohand.ai installer) — OpenRouter-backed coding agent CLI, configured via `~/.autohand/config.json`

Each entry needs: tool name, install path, env key used, what it does, example commands.

---

## STEP 4 — Update Workspace-Map.md and Directory.md

Reflect any structural changes from this session (Video-Generation/Channels/ reorganization was already done in prior session — verify it's captured).

---

## STEP 5 — Graphify Refresh

Run graphify update on affected domains after TOOLBOX and doc edits:
```bash
graphify update 001_Architecture
```

Check `001_Architecture/Graphify/REGISTRY.md` to confirm which domains need rebuilding.

---

## STEP 6 — Pompeii Video — Final Assembly

All 21 video clips are generated (C01–C21 confirmed in Video_Clips/).
Remaining pipeline steps per the skill's Final Delivery section:

1. Assemble clips in Premiere / ffmpeg using `Data/Beatmap.json` timecodes
2. Apply `Package/text_hooks.txt` as caption overlay (first 2–3 seconds only)
3. Add music (Suno via kie.ai)
4. Color grade
5. Upload using `Package/YouTube_Package.md` content

Production folder:
`002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Productions/0001_Pompeii_The_Escape/`

---

## OPEN QUESTIONS / NOTES

- `enable_audio` parameter added to `batch_generate_videos.py` — exact kie.ai API parameter name unverified. Will confirm on next batch that uses `--audio` flag.
- WaveSpeed skill saved at `001_Architecture/Skills/wavespeed/SKILL.md` ✓
- kie-cli skill is the upstream package's own skill — no local SKILL.md created yet. Consider creating one.
- `~/.zshrc` now sources `~/.env-secrets` at top, maps `KIE_AI_API_KEY=$KIE_API_KEY`, and runs Python one-liner to inject OpenRouter key into Autohand config on every shell start.
