---
title: "Session Handoff — 2026-09-27 (Claude Code)"
type: handoff
category: session
created: 2026-09-27
updated: 2026-09-27
---

# Session Handoff — READ THIS FIRST next session

Covers 2026-09-26 evening → 2026-09-27. Log: `001_Architecture/Logs/2026-09-26_Session-Log.md` (Claude section + "Session close"). Feedback: `Feedback_Loop/2026-09-26_Feedback.md`. Self-review: `Self_Learning_Loop/2026-09-26_Self-Review.md`.

## Open to-do list (only real open items — Tony's rule)
- **cloudflare-api MCP sign-in:** do it when website work starts (Tony plans a website soon). Nothing else is open.

Do NOT list: `000_Ingest/` backlog, background/automatic jobs, the upscaler shoot-out (closed — fal Topaz Proteus locked), the keyframe fallback test (test when needed).

## What changed (all committed + pushed: `ccc0e3ec` tag `neon-parcel-v2-pipeline-2026-09-27`, `9b4837b4`, plus close-out docs)

**Neon Parcel v2**
- **Scale hard stop:** every storyboard needs `Data/Scale_Spec.json` + a passing `Channels/Neon_Parcel/check_storyboard_scale.py` (local YOLOE, free, ~4 s) before `seedance2_call.py` will spend. Tolerance = what the eye notices (15% size change, 25% vs environment/pair). Exaggerate only what the prompt names ("large walrus"), still bound by physical rules (fits in the van). Detector words: plain words beat names ("large animal", "truck").
- **Storyboard failure ladder:** 1) crop edge-only leftovers, 2) keyframe fallback (`extract_storyboard_keyframes.py` cuts panels free → `seedance2_call.py --keyframes`; slots keyframes > character sheets > environment > props, 9 max; storyboard not sent but kept), 3) clean first/last-frame route.
- **Shots > 15 s:** WaveSpeed `bytedance/seedance-2.0-mini/video-extend` on the approved Clip 1, no end frame, input hosted on Cloudinary (skill section "Shots Longer Than 15 Seconds").
- Upscale route unchanged and confirmed: fal Topaz Proteus 2x → Kie Topaz → Magnific → FFmpeg.

**Other pipelines / global**
- **Anomalous Wild:** a beat with `model: bytedance/seedance-2` (or `-2-fast`) is now a real Seedance 2 call (frames mode OR reference mode); mixed/unknown = CONFIG error, nothing spent.
- **Shared props (all channels):** uniform/logo made first as its own image, attached to every matching character sheet and any prop sheet showing it; other props follow Neon Parcel's portable Prop Routing.
- **Tool-Manager:** upscaler prices verified live; ByteDance + SeedVR2 added (untested); `tm recommend --type upscale`; fal Topaz price pinned against the monthly refresh.
- **Model weights** live only in `Generic_Tools/models/` and `Subject-Aware-Reframer/Models/`, gitignored.
- **21st.dev:** key in `~/.env-secrets` (`TWENTY_FIRST_API_KEY`, `TWENTYFIRST_TOKEN` alias); magic MCP connected; skills `21st-cli-use`, `21st-ui-build`, `21st-ui-explore`, `21st-ui-review`. Free tier: 2 code retrievals/day, no AI generation. Prefer the CLI.

## Gotchas learned
- Run secret scans and read them BEFORE committing (separate steps).
- `sync_skill_index.py` / `generate_system_map.py` read stdin: run with `</dev/null`.
- 21st skill installer refuses the symlinked `~/.claude/skills`: install to a scratch dir, copy into `001_Architecture/Skills/`.
