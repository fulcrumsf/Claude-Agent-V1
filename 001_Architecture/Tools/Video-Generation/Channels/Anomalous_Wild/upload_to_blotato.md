# Anomalous Wild — Blotato Upload Procedure

Mirrors Reimagined Realms Phase 12 exactly, with Anomalous Wild's own account ID.

## Account

- **Blotato accountId:** `42514` — **confirmed correct by Tony on 2026-07-08** (asked directly since Blotato's API exposes no channel URL/subscriber count to corroborate beyond process of elimination).
- Found via `mcp__blotato__blotato_list_accounts` (platform: `youtube`), which returns exactly 3 YouTube accounts: NeonParcel (`25731`), this one (`42514`), and Reimagined Realms (`30323`, distinguishable by its 18 matching playlist subaccount names). The entry for this account:
  `{"id":"42514","platform":"youtube","fullname":"Anomalos Wild (Anomalos Wild)", ...}`
  (Blotato's stored display name has a spelling variant, "Anomalos Wild" instead of "Anomalous Wild" — same channel, per Tony's confirmation; not to be confused with `30323` which is Reimagined Realms).
- Known playlist subaccount on this account: `PLjAk92z3J0EsgDRxeyJhvFLvblUe0CBmj` ("Strange Animals"). Do not auto-assign — see `playlistIds` rule below.

## Locked defaults (same as RR, do not change without Tony's explicit say-so)
- `isMadeForKids`: `false`
- `containsSyntheticMedia`: `true`
- `shouldNotifySubscribers`: `false` (while private)
- `playlistIds`: omit — added manually by Tony during scheduling

## Tags — NEVER goes to Blotato (locked 2026-09-04)

`YouTube_Package.md` may have a trailing `# Tags` section (comma-separated, ≤500
chars, from `generate_youtube_package.py --tags`). That section is for Tony to paste
into **YouTube Studio's own Tags field by hand** — Blotato's `create_post` has no
tags field, and the upload step must read ONLY the `# Description` section as the
post `text`. Never append, prepend, or otherwise fold the Tags section into the
description sent to Blotato.

## Steps
1. Present Tony: chosen video file (duration/size), 3 titles from `Package/YouTube_Package.md`, 3 thumbnail concepts, privacy status choice. ⏸ PAUSE — wait for his picks.
2. Compress thumbnail if over 2MB: `ffmpeg -y -i input.png -vf "scale=1920:-1" -q:v 5 output.jpg`
3. Get presigned upload URLs via `mcp__blotato__blotato_create_presigned_upload_url` for video + thumbnail, `curl -X PUT --data-binary` each.
4. Call `mcp__blotato__blotato_create_post` with `accountId: "42514"`, Tony's chosen title/description/thumbnail/privacy, and the locked defaults above.
5. Poll `mcp__blotato__blotato_get_post_status` (≥10s between polls) until `published` or `failed`. Report the live URL back to Tony.
