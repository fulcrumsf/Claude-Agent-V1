---
title: "API Directory"
type: reference
domain: architecture
tags: [reference, api, integrations, analytics]
---

# API Directory

**The single source of truth for "is X actually connected."** Check this file before saying anything is connected, missing, or needs setup — never guess or re-derive from memory. Update it the moment a connection's real status changes (same discipline as `TOOLBOX.md` for tools and `001_Architecture/Graphify/REGISTRY.md` for graphs).

**Last verified live:** 2026-10-06 (checked `~/.env-secrets` key names, `~/.config/agent-os-youtube/`, Blotato's own `list_accounts`, and the MCP connector list — not assumed from docs).

| Platform | Status | Detail |
|---|---|---|
| **YouTube Data + Analytics API** | 🟢 Fully live — logins + real data pull both working | OAuth done for all 12 launched channels (2026-10-06): Neon Parcel, Reimagined Realms, Anomalous Wild, Board Nomad, Business Origin Stories, Glyphary, Kingdoms & Conquerors, Polyoculis, Unomas Creative, Room Portal, Ikigai Digital Studios, The Brain Blueprint (token label `business_blueprint`). Only Robotto Gato has no channel yet (not launched — skip). Tokens at `~/.config/agent-os-youtube/token_<label>.json`, created via `001_Architecture/Scripts/youtube_analytics_auth.py <label>`.<br><br>**Pull script built and tested live (2026-10-06): `001_Architecture/Scripts/youtube_analytics_pull.py`** — `python3 001_Architecture/Scripts/youtube_analytics_pull.py [--days N] [channel_label ...]`, no args = every logged-in channel, default 28-day window. Pulls lifetime subs/views + windowed views/watch-time/subscriber-gain/likes/comments per channel, prints a summary table, writes full detail to `001_Architecture/Logs/YouTube_Analytics_<date>.json`. A dead/expired login is reported by channel name with the exact fix command, never crashes the whole run.<br><br>**Known limitation, accepted by Tony (2026-10-06):** the Google Cloud project (`antigravity-claude-491002`) is in OAuth **Testing** publishing status, not Production. Refresh tokens expire **7 days after login on a fixed clock — regular use does NOT extend it.** Publishing to Production would fix this permanently but needs a hosted privacy policy + Google's sensitive-scope review (days, maybe longer) — not worth it for single-user use. Decision: stay in Testing, redo the login command whenever a channel's token goes stale.<br><br>**All 12 channels confirmed live and pulling real data, 2026-10-06.** Current snapshot (lifetime subs / lifetime views / last-30-day views): Neon Parcel 2,100 / 2.7M / 3,962 — Board Nomad 289 / 254,538 / 2,585 — Reimagined Realms 204 / 134,545 / 564 — Business Origin Stories 46 / 7,614 / 18 — The Brain Blueprint 35 / 35,590 / 141 — Anomalous Wild 1 / 123 / 72 — Glyphary, Kingdoms & Conquerors, Polyoculis, Room Portal, Unomas Creative, Ikigai Digital Studios: 0-485 lifetime views, effectively not yet producing. Neon Parcel is the clear lead by a wide margin. Rerun `youtube_analytics_pull.py` any time for a fresh snapshot — any login that goes stale again will be named by channel with the exact fix command, never silent. |
| **Blotato** (publishing + some post analytics) | 🟢 Connected | Confirmed live via `blotato_list_accounts`: YouTube, Facebook, Instagram, TikTok across Neon Parcel, Reimagined Realms, Anomalous Wild. Post-level analytics tools exist (`blotato_get_post_analytics` etc.) but haven't been tested for real numbers yet. |
| **Cloudflare** | 🟡 Configured, not authenticated | An MCP connector exists (`cloudflare-api`) but needs Tony to sign in via claude.ai connector settings before any tool call works. |
| **Etsy Open API v3** | 🔴 Not connected | No key saved anywhere. On the tool shortlist already (`001_Architecture/Ongoing-Agent-OS-To-Do-List.md` Part 1, score 82) — needs developer app registration first. |
| **Alura** | 🔴 Not connected | Tony applied for API access, no response yet (as of this writing — check with Tony if that's changed). |
| **Pinterest** | 🔴 Not connected | No key, no integration started. |
| **Google Analytics** | 🔴 Not connected | `GOOGLE_API_KEY` in `~/.env-secrets` exists but is generic (used for Gemini/other Google AI calls) — not a GA4 property connection. Needs its own OAuth/service-account setup. |
| **Agent Reach** (social scraping) | 🔴 Not evaluated | Flagged in conversation as a possible tool for pulling competitor/own social profile data; not looked into yet. |

## Google Cloud project — verified setup (2026-10-06)

Project `antigravity-claude-491002` ("Antigravity-Claude"). Checked live in Google Cloud Console, not assumed:

- **OAuth client:** exactly one, `Antigravity-ClaudeCode` (Desktop type, created Mar 21, 2026). No duplicate or stray clients.
- **Scopes granted:** `youtube.readonly` (Google's "sensitive" tier) + `yt-analytics.readonly` (Google's "non-sensitive" tier). Neither is in the "restricted" tier (the one needing a full security assessment) — if this project is ever published to Production, review would be the lighter sensitive-scope process, not the heavy one.
- **Publishing status:** Testing (see the YouTube row above for what that means and the accepted tradeoff).
- **APIs enabled on this project:** only YouTube Data API v3 and YouTube Analytics API show real traffic (24 calls each, from tonight's testing). Everything else enabled (BigQuery family, Cloud Storage, Cloud Logging, Cloud Monitoring, Cloud SQL, Geocoding, Street View Static, etc.) is default Google Cloud boilerplate with zero requests — not something Tony set up, harmless, ignore it.

**Future to-do, flagged not scheduled (2026-10-06):** if 2-3 more Google APIs get connected (Google Analytics being the next obvious one), revisit publishing this project to Production — one privacy policy covers every Google API under this one project, not per-API. Planned host: **unomascreative.com** (Tony's main LLC page) once that's live. **Hard constraint: the public privacy-policy page must never reveal anything that could help someone else access this Google Cloud project** — no project ID, no client ID, no internal URLs, no account-linkage specifics. Generic, standard privacy-policy language only (what data is accessed, why, how it's stored) — the same kind any small app publishes, nothing identifying the underlying infrastructure.

## Credential inventory — what Tony actually has in 1Password (2026-10-06)

**Purpose: stop relying on Tony's memory for this.** Built from Tony dictating his 1Password list live — names only, **never values**, not even partial. Where he gave a last-4 reference tag, it's recorded the same way a credit card statement shows one (last 4 chars reveal nothing about the real key). Several rows below are honestly uncertain — marked, not guessed at. Confirm with Tony before treating an uncertain row as fact.

### Personal Google account (fulcrumsf@gmail.com — the account used all night, project `antigravity-claude-491002`)

| Label (Tony's own words) | Best-guess identity | Status |
|---|---|---|
| Client secret (`client_secret.json`) | The OAuth app's client secret for `youtube_analytics_auth.py`, at `~/.config/agent-os-youtube/client_secret.json` | Confirmed — this is the one Agent-OS actually uses |
| "Antigravity/Claude Code credentials" + "another client secret.json for that" | Possibly a second, separate OAuth client (unclear if duplicate of the one above or genuinely different) | **Unconfirmed — ask Tony which app this backs before touching it** |
| "Antigravity Claude API key" | Likely the current value of `GOOGLE_API_KEY` or `GEMINI_API_KEY` in `~/.env-secrets` | **Unconfirmed which variable** |
| "YouTube Analytics and Data V3" | `YOUTUBE_ANALYTICS_API_KEY` + `YOUTUBE_DATA_API_KEY` in `~/.env-secrets` | Confirmed, both exist as env var names |
| "Antigravity Claude secret, new September [17]" | Likely `YOUTUBE_CLIENT_SECRET` — date matches the Sept 17, 2026 original OAuth token creation found earlier tonight | Likely match, not fully confirmed |
| "Antigravity Claude YouTube data API key" | `YOUTUBE_DATA_API_KEY` | Confirmed, exists |
| Gemini API key, created 2026-10-06 (tonight), ref tag ends **...5oI4** | The new key created under `antigravity-claude-491002` after the Firebase-shadow-project discovery. **Decision: goes into `GOOGLE_API_KEY`** (see below) | Created, not yet placed in `~/.env-secrets` as of this writing |

### BoredNomad business account (a separate Google identity — its own Google Cloud + its own Google AI Studio, not the same as above)

| App / Project | Uses | Status |
|---|---|---|
| **AI Character and Video Generator** (Tony's own app, built in Antigravity) | Gemini 2.5 Flash for image generation; "3.1 Flash Generate Preview" for video (likely a Veo model — confirm exact name) | Has its own Gemini API key under the BoredNomad GCP account, separate from everything above |
| **Upkeeply** (`003_Apps/Upkeeply/` in this workspace, built in Antigravity ~2025) | Gemini API | Has its own key, separate account |
| An n8n-connected app under BoredNomad | Gemini API key + a client ID (OAuth) | Separate from Agent-OS's own `n8n-automation-460016` project (the one flagged for deletion earlier) — **do not confuse the two** |

**Open items for Tony, not yet resolved:**
1. Confirm which `.env-secrets` variable ("Antigravity Claude API key") the row above maps to.
2. Clarify the second/duplicate `client_secret.json` mentioned — same app or genuinely separate?
3. BoredNomad's credentials live entirely outside this workspace's `~/.env-secrets` right now (different Google account) — decide if/when those should also get Agent-OS access, especially since Upkeeply already has a folder in this workspace.

## Spend caps — confirmed live, 2026-10-06

Checked and set directly in each platform's own console, not assumed:

| Key / Account | Cap | Enforcement | Notes |
|---|---|---|---|
| Google Gemini API (`antigravity-claude-491002`) | **$10/month** | Real hard pause (Google's own "spend cap enforcement," Preview feature) — pauses the Gemini API specifically until the next month or manually lifted | New as of tonight; was uncapped before |
| OpenRouter — `Antigravity-ClaudeCode` key (Jev routing + chores) | **$20/month** (Tony's explicit call, reverted from a brief $10 test) | Real hard stop ("key stops working") | Current pace ~$1.81 in 6 days of October — $20 gives headroom; this is the key the whole Option B routing system depends on |
| OpenRouter — `n8n` key | $5/month | Real hard stop | Already tighter than $10, left alone, barely used (last active 8 months ago) |
| OpenAI (`Uno Mas Creative` org) | **$10/month**, hard enforcement toggled ON | Real hard stop (429 errors once hit) | Was $120/month with hard-limit OFF (soft/informational only) before tonight |
| Google AI Studio — personal (fulcrumsf) | $10/month | Set by Tony directly | |
| Google AI Studio — BoredNomad (info@borednomad.com) | $10/month | Set by Tony directly | |
| Blotato | $20/month | Set by Tony directly | |
| Upkeeply app | $1/month | Set by Tony directly | Tony's likely deleting this app |

**Not capped — prepaid/credit-based, can't overspend by design:** kie.ai, fal.ai, WaveSpeed, Higgsfield, Magnific. **No spend-cap concept applies:** ElevenLabs, Cloudinary, Notion, Airtable, Obsidian, Perplexity, Firecrawl (flat subscription/tier-based).

## Watch list — categories Tony has mentioned, not yet started

Not full entries since names/final picks aren't locked in — tracked here so nothing gets lost, add a real row above once one is actually chosen and connected.

- **TikTok Shop affiliate analytics** — Tony mentioned a tool, name recalled as "Kalodata" (unconfirmed spelling/exact product — verify before acting on this).
- **SEO tools** — SEMrush and Ahrefs mentioned as known options Tony probably won't use; also mentioned an open-source alternative, name not yet confirmed (do not guess which one — ask Tony when this becomes active).
- **General:** any other analytics/API category Tony mentions in passing should get a one-line entry here first, promoted to a full row only once it's actually being connected.

## Why this file exists

Tony's own words (2026-10-06): "where do we save a list so you don't have to constantly go look this up... We've already gone through this hundreds of times... It's really annoying." This file is the fix — read it first, update it the moment something changes, never make him re-explain what's already connected.

## Maintenance rule

Any session that connects, disconnects, or discovers the real status of an API/platform integration updates this file in the same turn — same standing rule as `TOOLBOX.md`.
