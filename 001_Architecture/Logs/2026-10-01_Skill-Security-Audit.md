# Skill Security Audit — 2026-10-01

Full sweep with NVIDIA SkillSpector (static scan, `--no-llm`, v2.12.0) across every skill reachable by Claude Code, Codex, Gemini CLI, and Antigravity, plus every other skill-like thing found on the machine (other editors, app bundles, caches). Requested after installing `find-skills`, `humanizer`, and `skillspector` itself this session.

**Full per-skill tables (1,583 lines, ~230KB):** [`2026-10-01_Skill-Security-Audit-Appendix.md`](2026-10-01_Skill-Security-Audit-Appendix.md)

## Bottom line

- **Nothing malicious found.** No hidden-text attacks, no hardcoded secrets, no skill quietly exfiltrating keys or files. Checked by hand: every HIGH/CRITICAL finding in the 798 skills an agent can actually load, 12,615 files for invisible Unicode, 6,790 files for secret patterns.
- **The "DO_NOT_INSTALL" label fired on 246 skills — nearly all false positives.** SkillSpector's scorer reacts to normal documentation language (`.env`, "access token", example `rm -rf` commands, HTML comments, compiled `.pyc` files). Each one was checked by hand, not taken at face value.
- **Three real, minor issues need your call** — below.
- **Scope:** 2,011 skill locations found, 1,543 distinct after removing byte-identical copies. 798 are actually loadable by some agent; the other 745 are caches/old versions/catalog clones that nothing loads.

## Three things needing your decision

1. **`nano-banana-pro-prompts-recommend-skill`** (canonical — all four harnesses can load it). Its SKILL.md tells the agent to auto-update by downloading ~35MB of prompt text from `github.com/YouMind-OpenLab/...`'s `main` branch if local data is >24h old — unpinned, unverified, then read by the agent. Today's copy is clean (last pulled 2026-03-25), but this is a standing prompt-injection channel if that repo ever changes hands or gets compromised. **Fix: pin to a specific commit, or drop the auto-update step.**
2. **`media-use`** (canonical + both mirrors). Sends anonymous usage telemetry to PostHog by default (no filenames/paths/prompt text, per its own code). Would link to your HeyGen account email if you're signed in there — you're not, so it's anonymous today. Opt-out: set `HYPERFRAMES_NO_TELEMETRY=1` or `DO_NOT_TRACK=1`. **Your call whether that's worth doing.**
3. **`video-use`** (`001_Architecture/Tools/Video-Generation/Video-Use`). Four pinned dependencies with known CVEs in `pyproject.toml`/`uv.lock`: `pillow==12.2.0`, `msgpack==1.1.2`, `soupsieve==2.8.3`, `urllib3==2.7.0`. CVE numbers weren't independently verified. **Likely fix: `uv lock --upgrade` in that folder, then re-test.**

## Worth knowing, not threats

- **Adobe Premiere Pro's 8 AgenticSkills are encrypted** — unauditable by any scanner, including this one. Only Premiere itself uses them.
- **claude-mem's Telegram integration** flagged CRITICAL ("credential exfiltration") — false positive: it only sends your own bot token to Telegram's own API, interactively, and it's currently unconfigured (empty token/chat ID) so it does nothing.
- **`remotion-best-practices`** has a stray invisible Unicode character (U+2060) in a Mapbox URL — a copy-paste bug, not an attack.
- A handful of vendor installers use `curl | bash` (Android CLI plugin, Gemini's `antigravity-support`, Cloudflare docs, Warp's `oz-platform`) — all from their official domains.

## Housekeeping found along the way

- **11 skills exist only in Antigravity's `.agents/skills/`**, never mirrored to the canonical folder: `embedded-captions`, `faceless-explainer`, `figma`, `general-video`, `lab-plan-antigravity`, `music-to-video`, `pr-to-video`, `product-launch-video`, `remotion-to-hyperframes`, `slideshow`, `talking-head-recut`.
- **`typesafe-ai`** exists only in `~/.agents/skills` (home), not mirrored anywhere else.
- **`find-skills` has drifted**: the copy in `~/.agents/skills` differs from the canonical + workspace copies (which match each other).
- **Clutter inside skill folders inflating scan noise:** `excalidraw-diagram-skill` ships a 130MB `references/.venv` (507 binary-file flags from that alone); `Video-Use` has a `.venv` too; `graphify` has a stale `SKILL.md.bak`; several skills ship `.pyc` files.
- **`gsap` and `hyperframes` canonical links point outside the workspace** to `/opt/homebrew/lib/node_modules/...` — an `npm update -g` would silently change those skills' content without touching this repo.
- **The 16 broken symlinks** (firecrawl ×8, cloudflare, 5 UI/design skills) were left untouched per instructions — fix script already handed to Tony separately (`/tmp/fix_broken_skill_symlinks.sh`).

## Not covered

- Static analysis only — no LLM semantic pass.
- Plugin `hooks.json` files and MCP server code aren't skills, so they weren't scanned. Flagged as a natural next audit if wanted.
- `~/Library` was only spot-checked for agent-app folders, not swept in full (too slow, stopped early).

## Method

`skillspector scan <path> --no-llm --format json`, one scan per distinct copy (byte-identical duplicates scanned once, mapped to every location they're reachable from). Scripts and raw JSON output are in this session's scratchpad (temporary, not copied into the repo): `inventory.py`, `run_scans.py`, `aggregate.py`, `make_tables.py`, plus `aggregate.json` / `inventory.json` / `scans/`.
