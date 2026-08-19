# Pexels API Reference — Auth, Endpoints, Attribution, Limits

Live reference for any skill/script that searches, downloads, or attributes Pexels photos/videos. Confirmed directly from Pexels' own docs/license pages on 2026-08-18 — do not rely on memory or older summaries for attribution wording; re-check the source URLs below if this doc goes stale.

## Auth

- API key required, obtained from pexels.com.
- Pass via header: `Authorization: <PEXELS_API_KEY>` (no `Bearer` prefix).
- Key lives in `~/.env-secrets` as `PEXELS_API_KEY` (fixed 2026-08-18 — was previously malformed as `Export PEXELS API KEY=...`, invalid shell syntax).

## Rate limits

- Default: **200 requests/hour, 20,000 requests/month.**
- Response headers `X-Ratelimit-Limit`, `X-Ratelimit-Remaining`, `X-Ratelimit-Reset` track usage per call.
- Pexels grants higher limits, free, to apps that maintain consistent photographer/videographer attribution — worth requesting once this pipeline is live and attributing consistently.

## Endpoints relevant to this workspace

- **Video search** — search by subject/topic (e.g. "sloth", "mantis shrimp", "Coco the Gorilla"). Supports filtering by orientation, size, duration.
- **Photo search** — used only for reference/grounding images during research, never as a final video asset in this workspace's pipelines.
- Pagination up to 80 results per request.

## Response fields needed for attribution — capture these AT DOWNLOAD TIME, never reconstruct later

| Asset type | Fields |
|---|---|
| Photo | `photographer`, `photographer_url`, `photographer_id` |
| Video | equivalent videographer name/URL/ID fields |

## Download filtering rule (locked 2026-08-18)

Any video pulled from Pexels for use as B-roll must be filtered to **1080p resolution, 16:9 aspect ratio** — no other resolution/ratio combination is acceptable for this workspace's channels.

## Attribution — confirmed from source, two different documents give different framing

- **Pexels License page** (https://www.pexels.com/license/) — the actual legal terms: *"Attribution is not required. Giving credit to the photographer or Pexels is not necessary but always appreciated."* **Attribution is fully optional, not a legal requirement.**
- **Pexels API FAQ** (https://www.pexels.com/api/) — softer, encouragement-framed: *"Please! Always credit our photographers when possible (e.g. 'Photo by John Doe on Pexels' with a link to the photo page on Pexels)."*
- **This workspace's standing decision (2026-08-18, Tony):** attribute anyway, even though optional — **description-only, no on-screen burn-in.** Format: a Markdown "Attributions:" section in the YouTube description, one bullet per Pexels asset actually used in the final cut (not every downloaded clip), contributor name hyperlinked to their Pexels profile page:
  ```
  Attributions:
  - Mantis shrimp in the sand footage from [@username](https://www.pexels.com/@username) from Pexels
  - Mantis shrimp punching footage from [@username2](https://www.pexels.com/@username2) from Pexels
  ```

## Official client libraries

Ruby, JavaScript, .NET — no official Python library. Python integrations hit the REST API directly.

## Logo usage

Pexels logo (white/black) may be used in-app, but never as an app icon. Not currently used anywhere in this workspace.

## Where this doc is referenced from

- `Production-Research-Agent` skill (channel-agnostic Pexels search/download/attribution-logging capability)
- `Tool-Manager` SKILL.md, "Key Skills by Use Case" section
