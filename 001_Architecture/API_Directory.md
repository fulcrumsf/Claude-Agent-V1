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

### BoredNomad business account (info@borednomad.com — separate Google identity, own Cloud Console + own AI Studio, not the same as fulcrumsf above)

**Verified live in Cloud Console, 2026-10-06.** Billing account `01AF23-B42882-ADD61A` ("My Billing Account", org `borednomad.com`). 5 projects total under it:

| Project (Console name) | Project ID | Credential | Enabled APIs | 24h traffic | This month's spend | Read: keep or candidate to delete |
|---|---|---|---|---|---|---|
| **Blotato - Antigravity** | `gen-lang-client-0251496109` | API key "Gemini API Key" (created 2026-03-18), restricted to Gemini API | Gemini API, Telemetry API | 1,210 requests — actively in use | **$7.88** (100% of this account's spend) | **Keep — this is the live one.** Matches the "AI Character and Video Generator" app from the credential inventory above. Now has the $10/mo hard cap (see Spend caps below). |
| **Upkeeply App** | `gen-lang-client-0368503082` | API key "Upkeeply Gemini API Key" (created 2026-01-16) | Gemini API, Gemini for Google Cloud API, Telemetry API | 0 requests in last 24h | $0.00 | Idle right now, not necessarily dead — Tony's said he's likely deleting the Upkeeply app itself; when that happens this project + key go with it. |
| **Gemini API** | `gen-lang-client-0553978373` | API key "Generative Language API Key" (created 2025-08-29 — the oldest of the three Gemini keys) | Gemini API | 0 requests in last 24h | $0.00 | **Candidate to delete/rotate** — oldest key, zero traffic, no OAuth client or service account attached, nothing in this workspace references it by that name. Confirm with Tony what originally used it before removing. |
| **BoredNomad WooCommerce Website** | `theta-eon-450804-c2` | None — no API keys, no OAuth clients, no service accounts | Only default boilerplate (Analytics Hub API, BigQuery API) | 0 requests | $0.00 | **Candidate to delete** — no credentials of any kind live here; looks like an auto-created shell, nothing wired to it. |
| **Make** | `fine-program-454108-r9` | OAuth 2.0 Client ID "Make" (Web application, created 2025-03-18) — no API key | Only default boilerplate | 0 requests | $0.00 | For the Make.com (Integromat) integration if that's still used — confirm with Tony whether that automation is still active before deleting; if Make.com isn't in use anymore, this is a delete candidate too. |

**Open items for Tony, not yet resolved:**
1. Confirm which `.env-secrets` variable ("Antigravity Claude API key") the fulcrumsf table above maps to.
2. Clarify the second/duplicate `client_secret.json` mentioned — same app or genuinely separate?
3. BoredNomad's credentials live entirely outside this workspace's `~/.env-secrets` right now (different Google account) — decide if/when those should also get Agent-OS access, especially since Upkeeply already has a folder in this workspace.
4. **Delete decision pending (2026-10-06):** 3 of the 5 BoredNomad projects (Gemini API, BoredNomad WooCommerce Website, Make) show zero traffic and look safe to delete, but Tony should confirm nothing dormant depends on them (especially Make.com, which uses OAuth not an API key, so traffic may not show up the same way) before anything gets deleted.

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
| **Google Gemini API, project "Blotato - Antigravity" (BoredNomad Cloud Console, `gen-lang-client-0251496109`)** | **$20/month** | Real hard pause (Google's own "spend cap enforcement," Preview feature), budget name "Blotato-Antigravity $20 Hard Cap" | Created at $10/mo 2026-10-06, raised to $20/mo same day by Tony directly in Console after spend hit $10.63 (confirmed live: ~$10.67/$20.00 at raise time, resets Nov 1, 2026). Separate from the BoredNomad AI Studio cap above. The other 4 BoredNomad projects show $0 spend, no cap needed yet. |
| Blotato | $20/month | Set by Tony directly | |
| Upkeeply app | $1/month | Set by Tony directly | Tony's likely deleting this app |

**Not capped — prepaid/credit-based, can't overspend by design:** kie.ai, fal.ai, WaveSpeed, Higgsfield, Magnific. **No spend-cap concept applies:** ElevenLabs, Cloudinary, Notion, Airtable, Obsidian, Perplexity, Firecrawl (flat subscription/tier-based).

## Watch list — categories Tony has mentioned, not yet started

Not full entries since names/final picks aren't locked in — tracked here so nothing gets lost, add a real row above once one is actually chosen and connected.

- **TikTok Shop affiliate analytics** — Tony mentioned a tool, name recalled as "Kalodata" (unconfirmed spelling/exact product — verify before acting on this).
- **SEO tools** — SEMrush and Ahrefs mentioned as known options Tony probably won't use; also mentioned an open-source alternative, name not yet confirmed (do not guess which one — ask Tony when this becomes active).
- **General:** any other analytics/API category Tony mentions in passing should get a one-line entry here first, promoted to a full row only once it's actually being connected.

## Visual project/key map (Artifact)

A visual, project-grouped view of this same data — each Cloud project as a card, with the API keys/OAuth clients inside it nested underneath and marked active/idle/dormant — is published here: **https://claude.ai/artifact/LrtHTdWPcBzidPZyeNYkw8** ("Project Key Map"). Built 2026-10-06. Re-publish to the same URL (don't create a new one) if this data changes — ask Tony before republishing since it's a visual aid he returns to directly.

## Why this file exists

Tony's own words (2026-10-06): "where do we save a list so you don't have to constantly go look this up... We've already gone through this hundreds of times... It's really annoying." This file is the fix — read it first, update it the moment something changes, never make him re-explain what's already connected.

## Maintenance rule

Any session that connects, disconnects, or discovers the real status of an API/platform integration updates this file in the same turn — same standing rule as `TOOLBOX.md`.
