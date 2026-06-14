---
title: "Printing Press Library"
type: "tool-doc"
category: "ai-agents"
tags:
  - ai-agents
  - cli
  - tool-library
  - automation
  - printing-press
created: 2026-05-12
source: local
---

## Printing Press Library

Nothing is more valuable than time and money. In a world of AI agents, that's speed and token spend. A well-designed CLI is muscle memory for an agent: no hunting through docs, no wrong turns, no wasted tokens. The [CLI Printing Press](https://github.com/mvanhorn/cli-printing-press) prints those CLIs. This repo is the catalog of CLIs already printed and ready to install.

58 CLIs across 13 categories.

Browse them all at [printingpress.dev](https://printingpress.dev/).

Three to try first:

- ESPN (sniffed, no official API). *"Tonight's NBA playoff games with live score, series state, each team's leading scorer's stat line, and any injury or lineup news from the last 24 hours."* One call.
- flight-goat (Kayak nonstop search plus sniffed Google Flights). *"Non-stop flights over 8 hours from Seattle for 4 people, Dec 24 to Jan 1, cheapest first."* Two sources, one query.
- sentry-pp-cli (local SQLite mirror, SQL across orgs and projects). *"Every issue first seen in the last release whose error rate is climbing across two projects."* Compound queries the Sentry API can't answer.

## Install

The fastest way to start — install four hand-picked CLIs and skills in one command:

```
npx -y @mvanhorn/printing-press install starter-pack
```

The starter pack: [`espn`](https://github.com/mvanhorn/printing-press-library/blob/main/library/media-and-entertainment/espn) (live sports), [`flight-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/library/travel/flightgoat) (flight search), [`movie-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/library/media-and-entertainment/movie-goat) (movie discovery), [`recipe-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/library/food-and-dining/recipe-goat) (recipe ranking).

Every install pulls the Go binary **and** the focused skill in one shot. Pass `--cli-only` or `--skill-only` if you want just one half.

One tool:

```
npx -y @mvanhorn/printing-press install espn
```

Several at once (bundles and CLI names mix freely):

```
npx -y @mvanhorn/printing-press install espn sentry dub
npx -y @mvanhorn/printing-press install starter-pack cal-com
```

Under the hood: the npm package is a thin orchestrator that reads the live catalog in `registry.json`, resolves each CLI's Go module path, runs `go install`, and installs the matching skill from `cli-skills/pp-<name>`.

Useful commands:

```
npx -y @mvanhorn/printing-press search sports
npx -y @mvanhorn/printing-press list
npx -y @mvanhorn/printing-press update espn
npx -y @mvanhorn/printing-press uninstall espn --yes
```

While the catalog repository is private, live installer use requires `GITHUB_TOKEN` or `GH_TOKEN` for catalog and skill fetches, plus working private Go module access for `go install`.

## Focused skills

When you already know the tool you want, install just that skill:

```
npx skills add mvanhorn/printing-press-library/cli-skills/pp-espn -g
```

Then use the focused slash skill directly:

```
/pp-espn lakers score
/pp-flightgoat sea to lax dec 24 to jan 1 nonstop
/pp-weather-goat phoenix forecast
```

Each `/pp-<name>` skill is a focused interface for one CLI.

## Catalog

Tools grouped by category, sourced from [`registry.json`](https://github.com/mvanhorn/printing-press-library/blob/main/registry.json). Each row links to the tool source, its focused direct-install skill, and the latest release.

| Name | Skill | Release | What it does |
| --- | --- | --- | --- |
| [`agent-capture`](https://github.com/mvanhorn/printing-press-library/blob/main/library/developer-tools/agent-capture) | [`/pp-agent-capture`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-agent-capture/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/agent-capture-current) | Record, screenshot, and convert macOS windows and screens for AI agent evidence.   <sub>Printed by <a href="https://github.com/mvanhorn">@mvanhorn</a></sub> |
| [`ahrefs`](https://github.com/mvanhorn/printing-press-library/blob/main/library/marketing/ahrefs) | [`/pp-ahrefs`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-ahrefs/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/ahrefs-current) | Query Ahrefs backlinks, keyword, rank tracking, site audit, and SERP data from the terminal.   <sub>Printed by <a href="https://github.com/cathrynlavery">@cathrynlavery</a></sub> |
| [`airbnb`](https://github.com/mvanhorn/printing-press-library/blob/main/library/travel/airbnb) | [`/pp-airbnb`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-airbnb/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/airbnb-current) | Search Airbnb and VRBO, find the host's direct booking site, and report the cheapest of three sources side-by-side.   <sub>Printed by <a href="https://github.com/mvanhorn">@mvanhorn</a></sub> |
| [`allrecipes`](https://github.com/mvanhorn/printing-press-library/blob/main/library/food-and-dining/allrecipes) | [`/pp-allrecipes`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-allrecipes/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/allrecipes-current) | Search and fetch Allrecipes recipes as structured data, scale ingredients, build grocery lists, rank by Bayesian-smoothed popularity, and clear Cloudflare with a Chrome session cookie.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`amazon-seller`](https://github.com/mvanhorn/printing-press-library/blob/main/library/commerce/amazon-seller) | [`/pp-amazon-seller`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-amazon-seller/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/amazon-seller-current) | Read FBA inventory, orders, sales reports, listings, and catalog data for an Amazon seller account.   <sub>Printed by <a href="https://github.com/cathrynlavery">@cathrynlavery</a></sub> |
| [`apartments`](https://github.com/mvanhorn/printing-press-library/blob/main/library/other/apartments) | [`/pp-apartments`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-apartments/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/apartments-current) | Search Apartments.com listings, sync results to a local SQLite store, and run workflows the website never built — diff saved searches, rank by $/sqft, compare shortlists, and surface price drops or phantom listings.   <sub>Printed by <a href="https://github.com/rderwin">@rderwin</a></sub> |
| [`archive-is`](https://github.com/mvanhorn/printing-press-library/blob/main/library/media-and-entertainment/archive-is) | [`/pp-archive-is`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-archive-is/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/archive-is-current) | Bypass paywalls and look up web archives via archive.today. Hero command: find or create an archive for any URL with lookup-before-submit, Wayback Machine fallback, and agent-hints on stderr when called non-interactively.   <sub>Printed by <a href="https://github.com/mvanhorn">@mvanhorn</a></sub> |
| [`cal-com`](https://github.com/mvanhorn/printing-press-library/blob/main/library/productivity/cal-com) | [`/pp-cal-com`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-cal-com/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/cal-com-current) | Every Cal.com feature, plus offline agendas, composed booking flows, and analytics no other Cal.com tool ships.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`clarity`](https://github.com/mvanhorn/printing-press-library/blob/main/library/marketing/clarity) | [`/pp-clarity`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-clarity/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/clarity-current) | Client-side instrumentation helpers for Microsoft Clarity.   <sub>Printed by <a href="https://github.com/cathrynlavery">@cathrynlavery</a></sub> |
| [`cloud-run-admin`](https://github.com/mvanhorn/printing-press-library/blob/main/library/cloud/cloud-run-admin) | [`/pp-cloud-run-admin`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-cloud-run-admin/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/cloud-run-admin-current) | Deploy and manage user provided container images that scale automatically based on incoming requests. The Cloud Run Admin API v1 follows the Knative Serving API specification, while v2 is aligned with Google Cloud AIP-based API standards, as described in [https://google.aip.dev/](https://google.aip.dev/).   <sub>Printed by <a href="https://github.com/cathrynlavery">@cathrynlavery</a></sub> |
| [`coingecko`](https://github.com/mvanhorn/printing-press-library/blob/main/library/payments/coingecko) | [`/pp-coingecko`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-coingecko/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/coingecko-current) | CoinGecko public API for cryptocurrency data. Free tier, no API key required for basic endpoints.   <sub>Printed by <a href="https://github.com/hnshah">@hnshah</a></sub> |
| [`company-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/library/developer-tools/company-goat) | [`/pp-company-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-company-goat/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/company-goat-current) | One call across seven authoritative sources to research a startup's funding history (SEC Form D), engineering velocity (GitHub), HN mentions, legal entity (US/UK), and domain age. Compares competitors side-by-side and flags inconsistencies between public claims and filings.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`contact-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/library/sales-and-crm/contact-goat) | [`/pp-contact-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-contact-goat/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/contact-goat-current) | Super LinkedIn for the terminal - search, enrich, and map warm-intro paths across LinkedIn (stickerdaniel/linkedin-mcp-server subprocess), Happenstance (Chrome cookie auth with Clerk JWT refresh), and Deepline (paid enrichment, hybrid subprocess+HTTP). Unified SQLite store powers warm-intro, coverage, and cross-source prospect commands no single tool has.   <sub>Printed by <a href="https://github.com/mvanhorn">@mvanhorn</a></sub> |
| [`craigslist`](https://github.com/mvanhorn/printing-press-library/blob/main/library/commerce/craigslist) | [`/pp-craigslist`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-craigslist/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/craigslist-current) | Search, sync, and watch Craigslist with a local SQLite snapshot history, cross-city aggregation, scam scoring, and price-drift detection.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`customer-io`](https://github.com/mvanhorn/printing-press-library/blob/main/library/marketing/customer-io) | [`/pp-customer-io`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-customer-io/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/customer-io-current) | Manage Customer.io campaigns, broadcasts, segments, deliveries, exports, and Reverse-ETL via the Service Account token.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`docker-hub`](https://github.com/mvanhorn/printing-press-library/blob/main/library/developer-tools/docker-hub) | [`/pp-docker-hub`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-docker-hub/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/docker-hub-current) | Docker Hub public API. Search container images, browse tags, check sizes, inspect Dockerfiles, and explore the world's largest container registry. No authentication required for public repositories (rate limited to ~18 req/min).   <sub>Printed by <a href="https://github.com/hnshah">@hnshah</a></sub> |
| [`dominos`](https://github.com/mvanhorn/printing-press-library/blob/main/library/food-and-dining/dominos) | [`/pp-dominos`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-dominos/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/dominos-current) | Order pizza, browse menus, optimize deals, and track delivery from your terminal — with a local SQLite store that powers reorder, price comparison, and deal stacking no other Domino's tool offers.   <sub>Printed by <a href="https://github.com/mvanhorn">@mvanhorn</a></sub> |
| [`dub`](https://github.com/mvanhorn/printing-press-library/blob/main/library/marketing/dub) | [`/pp-dub`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-dub/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/dub-current) | Modern link attribution platform — short links, conversion tracking, affiliate/partner programs.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`ebay`](https://github.com/mvanhorn/printing-press-library/blob/main/library/commerce/ebay) | [`/pp-ebay`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-ebay/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/ebay-current) | Buyer-power-user CLI for eBay. Sold-comp intelligence, true sniper bidding, watchlist intelligence, saved-search feeds, and a local SQLite store for cross-listing analytics.   <sub>Printed by <a href="https://github.com/mvanhorn">@mvanhorn</a></sub> |
| [`espn`](https://github.com/mvanhorn/printing-press-library/blob/main/library/media-and-entertainment/espn) | [`/pp-espn`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-espn/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/espn-current) | Live scores, standings, news, and game history across 17 sports from ESPN.   <sub>Printed by <a href="https://github.com/mvanhorn">@mvanhorn</a></sub> |
| [`fedex`](https://github.com/mvanhorn/printing-press-library/blob/main/library/commerce/fedex) | [`/pp-fedex`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-fedex/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/fedex-current) | Ship, rate, and track FedEx packages from the terminal — built for small business shippers.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`firecrawl`](https://github.com/mvanhorn/printing-press-library/blob/main/library/developer-tools/firecrawl) | [`/pp-firecrawl`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-firecrawl/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/firecrawl-current) | API for interacting with Firecrawl services to perform web scraping and crawling tasks.   <sub>Printed by <a href="https://github.com/hnshah">@hnshah</a></sub> |
| [`fireflies`](https://github.com/mvanhorn/printing-press-library/blob/main/library/productivity/fireflies) | [`/pp-fireflies`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-fireflies/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/fireflies-current) | Every Fireflies meeting feature, plus offline search, cross-meeting intelligence, and a local database no other tool... |
| [`flight-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/library/travel/flight-goat) | [`/pp-flight-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-flight-goat/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/flight-goat-current) | Search Google Flights, scan Kayak long-haul routes, and join FlightAware AeroAPI reliability, alerts, and tracking from one CLI.   <sub>Printed by <a href="https://github.com/mvanhorn">@mvanhorn</a></sub> |
| [`food52`](https://github.com/mvanhorn/printing-press-library/blob/main/library/food-and-dining/food52) | [`/pp-food52`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-food52/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/food52-current) | Search, browse, and read Food52 from your terminal — with offline FTS, pantry matching, recipe scaling, and the editorial signals other tools throw away.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`google-ads`](https://github.com/mvanhorn/printing-press-library/blob/main/library/marketing/google-ads) | [`/pp-google-ads`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-google-ads/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/google-ads-current) | Google Ads API for account discovery, GAQL reporting, campaigns, budgets, assets, conversions, audiences, planning, and billing operations.   <sub>Printed by <a href="https://github.com/cathrynlavery">@cathrynlavery</a></sub> |
| [`google-photos`](https://github.com/mvanhorn/printing-press-library/blob/main/library/media-and-entertainment/google-photos) | [`/pp-google-photos`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-google-photos/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/google-photos-current) | Google Photos Library and Picker APIs for app-created media, albums, uploads, and user-selected media.   <sub>Printed by <a href="https://github.com/cathrynlavery">@cathrynlavery</a></sub> |
| [`hackernews`](https://github.com/mvanhorn/printing-press-library/blob/main/library/media-and-entertainment/hackernews) | [`/pp-hackernews`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-hackernews/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/hackernews-current) | Hacker News from your terminal — with a local SQLite store, snapshot history, and agent-native output no other HN tool has.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`instacart`](https://github.com/mvanhorn/printing-press-library/blob/main/library/commerce/instacart) | [`/pp-instacart`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-instacart/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/instacart-current) | Natural-language Instacart CLI that talks directly to the web GraphQL API. Add items to your cart, search products, and manage carts across retailers without browser automation.   <sub>Printed by <a href="https://github.com/mvanhorn">@mvanhorn</a></sub> |
| [`kalshi`](https://github.com/mvanhorn/printing-press-library/blob/main/library/payments/kalshi) | [`/pp-kalshi`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-kalshi/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/kalshi-current) | Trade prediction markets, persist tick data, and answer category-level P&L questions Kalshi.com cannot.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`klaviyo`](https://github.com/mvanhorn/printing-press-library/blob/main/library/marketing/klaviyo) | [`/pp-klaviyo`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-klaviyo/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/klaviyo-current) | Marketing automation, profiles, events, campaigns, flows, segments, and templates.   <sub>Printed by <a href="https://github.com/cathrynlavery">@cathrynlavery</a></sub> |
| [`linear`](https://github.com/mvanhorn/printing-press-library/blob/main/library/project-management/linear) | [`/pp-linear`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-linear/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/linear-current) | Offline-capable, agent-native CLI for the Linear API with SQLite-backed sync, FTS5 search, cross-cycle comparison, project burndown, and pp\_created fixture lifecycle for safe live testing.   <sub>Printed by <a href="https://github.com/mvanhorn">@mvanhorn</a></sub> |
| [`mercury`](https://github.com/mvanhorn/printing-press-library/blob/main/library/payments/mercury) | [`/pp-mercury`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-mercury/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/mercury-current) | Business banking API for accounts, transactions, payments, recipients, cards, invoices, treasury, and webhooks.   <sub>Printed by <a href="https://github.com/cathrynlavery">@cathrynlavery</a></sub> |
| [`movie-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/library/media-and-entertainment/movie-goat) | [`/pp-movie-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-movie-goat/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/movie-goat-current) | The movie CLI that combines TMDb's discovery engine with OMDb's multi-source ratings — and ships a SQLite watchlist that flags what's streaming on your services right now.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`notion`](https://github.com/mvanhorn/printing-press-library/blob/main/library/productivity/notion) | [`/pp-notion`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-notion/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/notion-current) | Every Notion database queryable offline — cross-workspace SQL joins, stale detection, and relation graph traversal... |
| [`nvd`](https://github.com/mvanhorn/printing-press-library/blob/main/library/developer-tools/nvd) | [`/pp-nvd`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-nvd/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/nvd-current) | The NVD is the U.S. government repository of standards-based vulnerability management data. Search CVEs by keyword, product (CPE name), CVE ID, or date range. Get CVSS scores, affected versions, references, and severity ratings. No API key required (optional for higher rate limits).   <sub>Printed by <a href="https://github.com/hnshah">@hnshah</a></sub> |
| [`open-meteo`](https://github.com/mvanhorn/printing-press-library/blob/main/library/other/open-meteo) | [`/pp-open-meteo`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-open-meteo/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/open-meteo-current) | Forecasts, historicals, marine, air quality, flood, climate, ensemble, and seasonal data from Open-Meteo's free tier.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`pagliacci`](https://github.com/mvanhorn/printing-press-library/blob/main/library/food-and-dining/pagliacci) | [`/pp-pagliacci`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-pagliacci/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/pagliacci-current) | Order Seattle's Pagliacci Pizza from the terminal — half-and-half pies, small-party planner, slice rotation, and rewards stacking.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`pokeapi`](https://github.com/mvanhorn/printing-press-library/blob/main/library/media-and-entertainment/pokeapi) | [`/pp-pokeapi`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-pokeapi/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/pokeapi-current) | Fully offline Pokédex with SQL, full-text search, type math, and a damage calculator no other Pokémon tool ships as a CLI.   <sub>Printed by <a href="https://github.com/hnshah">@hnshah</a></sub> |
| [`postman-explore`](https://github.com/mvanhorn/printing-press-library/blob/main/library/developer-tools/postman-explore) | [`/pp-postman-explore`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-postman-explore/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/postman-explore-current) | Public API network directory for discovering community collections, workspaces, and APIs.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`producthunt`](https://github.com/mvanhorn/printing-press-library/blob/main/library/marketing/producthunt) | [`/pp-producthunt`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-producthunt/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/producthunt-current) | Read Product Hunt from your terminal — works token-free for the daily skim, unlocks a launch-day cockpit and a marketer research desk in one onboarding step.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`pypi`](https://github.com/mvanhorn/printing-press-library/blob/main/library/developer-tools/pypi) | [`/pp-pypi`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-pypi/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/pypi-current) | PyPI JSON API. Look up Python package metadata, versions, release files, and vulnerability data. Browse recent updates and newest packages via RSS feeds. No authentication required — all endpoints are public.   <sub>Printed by <a href="https://github.com/hnshah">@hnshah</a></sub> |
| [`recipe-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/library/food-and-dining/recipe-goat) | [`/pp-recipe-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-recipe-goat/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/recipe-goat-current) | Find the best version of any recipe across 37 trusted sites — trust-aware ranking weights real reader signal at 80% and editorial trust at 15% (curated chef/baker sites win tie-break over crowdsourced aggregators). Builds a local SQLite cookbook with pantry match, meal plans, cook log, substitutions, and USDA-backed nutrition backfill. Powered by Surf-Chrome HTTP transport — bypasses TLS-fingerprint bot detection that previously blocked Dotdash properties.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`redfin`](https://github.com/mvanhorn/printing-press-library/blob/main/library/other/redfin) | [`/pp-redfin`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-redfin/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/redfin-current) | Search Redfin homes for sale via internal Stingray endpoints, sync to local SQLite, and run workflows the website doesn't expose — saved-search diff, $/sqft net-HOA ranking, sold comps, multi-region trends.   <sub>Printed by <a href="https://github.com/rderwin">@rderwin</a></sub> |
| [`roam`](https://github.com/mvanhorn/printing-press-library/blob/main/library/productivity/roam) | [`/pp-roam`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-roam/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/roam-current) | Every Roam HQ surface — chat, transcripts, On-Air events, SCIM, webhooks — in one local-first CLI with offline...   <sub>Printed by <a href="https://github.com/gregvanhorn">@gregvanhorn</a></sub> |
| [`scrape-creators`](https://github.com/mvanhorn/printing-press-library/blob/main/library/developer-tools/scrape-creators) | [`/pp-scrape-creators`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-scrape-creators/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/scrape-creators-current) | Scrape public social media data from the terminal — profiles, posts, videos, comments, ads, and transcripts across TikTok, Instagram, YouTube, Twitter/X, LinkedIn, Facebook, Reddit, Threads, Bluesky, Pinterest, Snapchat, Twitch, Kick, Truth Social, and 15+ link-in-bio / creator link services.   <sub>Printed by <a href="https://github.com/adrianhorning08">@adrianhorning08</a></sub> |
| [`seats-aero`](https://github.com/mvanhorn/printing-press-library/blob/main/library/travel/seats-aero) | [`/pp-seats-aero`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-seats-aero/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/seats-aero-current) | Seats.aero Partner API for award travel availability, cached search, route lists, and trip revalidation details.   <sub>Printed by <a href="https://github.com/cathrynlavery">@cathrynlavery</a></sub> |
| [`sentry`](https://github.com/mvanhorn/printing-press-library/blob/main/library/monitoring/sentry) | [`/pp-sentry`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-sentry/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/sentry-current) | Error tracking and performance monitoring - projects, issues, events, releases.   <sub>Printed by <a href="https://github.com/cathrynlavery">@cathrynlavery</a></sub> |
| [`shopify`](https://github.com/mvanhorn/printing-press-library/blob/main/library/commerce/shopify) | [`/pp-shopify`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-shopify/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/shopify-current) | Operate a Shopify store from the terminal with curated Admin GraphQL commands, local sync, analytics, and bulk exports.   <sub>Printed by <a href="https://github.com/cathrynlavery">@cathrynlavery</a></sub> |
| [`slack`](https://github.com/mvanhorn/printing-press-library/blob/main/library/productivity/slack) | [`/pp-slack`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-slack/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/slack-current) | Send messages, search conversations, monitor channels, and manage your Slack workspace from the terminal.   <sub>Printed by <a href="https://github.com/mvanhorn">@mvanhorn</a></sub> |
| [`steam-web`](https://github.com/mvanhorn/printing-press-library/blob/main/library/media-and-entertainment/steam-web) | [`/pp-steam-web`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-steam-web/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/steam-web-current) | Look up Steam players, games, achievements, friends, and stats from the command line.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`tiktok-shop`](https://github.com/mvanhorn/printing-press-library/blob/main/library/commerce/tiktok-shop) | [`/pp-tiktok-shop`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-tiktok-shop/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/tiktok-shop-current) | Safe v1 TikTok Shop Seller API CLI/MCP for auth readiness, token exchange and refresh, read-only shops, orders, products, inventory search, fulfillment packages, and warehouses.   <sub>Printed by <a href="https://github.com/cathrynlavery">@cathrynlavery</a></sub> |
| [`trigger-dev`](https://github.com/mvanhorn/printing-press-library/blob/main/library/developer-tools/trigger-dev) | [`/pp-trigger-dev`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-trigger-dev/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/trigger-dev-current) | Durable background jobs and AI agent orchestration — runs, schedules, deployments, batches, queues, waitpoints, env vars, and TRQL analytics.   <sub>Printed by <a href="https://github.com/mvanhorn">@mvanhorn</a></sub> |
| [`ufo-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/library/other/ufo-goat) | [`/pp-ufo-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-ufo-goat/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/ufo-goat-current) | Browse, search, and download declassified UAP files from the War.gov PURSUE archive.   <sub>Printed by <a href="https://github.com/davemorin">@davemorin</a></sub> |
| [`wanderlust-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/library/travel/wanderlust-goat) | [`/pp-wanderlust-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-wanderlust-goat/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/wanderlust-goat-current) | Wanderlust GOAT — what a knowledgeable local with great taste would tell you to walk to from here, fused across editorial, local-language, and crowd layers no single tool ranks together.   <sub>Printed by <a href="https://github.com/jheitzeb">@jheitzeb</a></sub> |
| [`weather-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/library/other/weather-goat) | [`/pp-weather-goat`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-weather-goat/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/weather-goat-current) | Weather forecasts, severe weather alerts, air quality, and GO/CAUTION/STOP activity verdicts for walk, bike, hike, commute, and drive.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |
| [`wikipedia`](https://github.com/mvanhorn/printing-press-library/blob/main/library/media-and-entertainment/wikipedia) | [`/pp-wikipedia`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-wikipedia/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/wikipedia-current) | Wikipedia REST API. Get article summaries, search, browse related topics, and access on-this-day events. No authentication required. Uses a polite User-Agent header.   <sub>Printed by <a href="https://github.com/hnshah">@hnshah</a></sub> |
| [`yahoo-finance`](https://github.com/mvanhorn/printing-press-library/blob/main/library/commerce/yahoo-finance) | [`/pp-yahoo-finance`](https://github.com/mvanhorn/printing-press-library/blob/main/cli-skills/pp-yahoo-finance/SKILL.md) | [latest](https://github.com/mvanhorn/printing-press-library/releases/tag/yahoo-finance-current) | Quotes, charts, fundamentals, options chains, and a local portfolio/watchlist tracker against Yahoo Finance — no API key, with Chrome-session fallback for rate-limited IPs.   <sub>Printed by <a href="https://github.com/tmchow">@tmchow</a></sub> |

## Binary-only install

If you only want the binary and not the companion skill, install directly with [Go 1.26.3 or newer](https://go.dev/dl/):

```
go install github.com/mvanhorn/printing-press-library/<path>/cmd/<binary>@latest
```

A few worked examples:

```
go install github.com/mvanhorn/printing-press-library/library/media-and-entertainment/espn/cmd/espn-pp-cli@latest
go install github.com/mvanhorn/printing-press-library/library/monitoring/sentry/cmd/sentry-pp-cli@latest
go install github.com/mvanhorn/printing-press-library/library/travel/flightgoat/cmd/flightgoat-pp-cli@latest
```

For the MCP server companion:

```
go install github.com/mvanhorn/printing-press-library/library/media-and-entertainment/espn/cmd/espn-pp-mcp@latest
claude mcp add espn-pp-mcp -- espn-pp-mcp
```

If a CLI needs credentials, the focused skill and the per-CLI README document the required environment variables.

## Repo structure

```
library/
  <category>/
    <tool>/
      cmd/
        <cli-binary>/
        <mcp-binary>/        # when available
      internal/
      README.md
      go.mod
      .printing-press.json
      .manuscripts/

cli-skills/
  pp-*/
    SKILL.md                 # generated direct-install mirror of library/<.>/SKILL.md

npm/
  package.json
  src/
  bin/

registry.json
```

Each published tool is self-contained: source code, a local README, a `.printing-press.json` provenance manifest, and the manuscripts from the printing run. `cli-skills/pp-*` is a generated mirror of each library `SKILL.md`, produced by `tools/generate-skills/main.go`.

## What endorsed means

Published tools in this repo are validated at publication time and during deliberate baseline sweeps against:

1. Generation from an API spec or captured interface through the [CLI Printing Press](https://github.com/mvanhorn/cli-printing-press)
2. Validation checks: build, vet, reachable Go vulnerability scan, help, version, plus the structural dogfood and runtime verify gates
3. Provenance capture through `.printing-press.json` and `.manuscripts/`

Some tools are refined after generation. The generated artifacts remain in the tool directory so the provenance stays inspectable.

## Contributing

See [CONTRIBUTING.md](https://github.com/mvanhorn/printing-press-library/blob/main/CONTRIBUTING.md). For deeper architecture, see [AGENTS.md](https://github.com/mvanhorn/printing-press-library/blob/main/AGENTS.md).

## License

MIT