---
title: "Printing Press Print the Best Agent Designed CLI"
type: "tool-doc"
category: "ai-agents"
tags:
  - ai-agents
  - cli
  - printing-press
  - automation
  - tool
created: 2026-05-12
source: local
---

PRESS IS OPENPL. A

## Welcome to the Printing Press.Print the best agent-designed CLI of all time. From anything, or install and use the ones the community has made so far.

From an API spec, from a website with no public API, from a beloved community fan project - one command prints a token-efficient Go CLI, a Claude Code skill, an OpenClaw skill, and an MCP server. Peter Steinberger showed the way with discrawl and gogcli: a local SQLite mirror beats a remote API call, compound commands beat ten round trips, and an agent-native CLI beats raw HTTP. The press bakes that playbook into every binary it prints. Muscle memory for agents.

---

## Every API has a secret identity.

Discord isn't just a chat app - it's a searchable knowledge base. Linear isn't just an issue tracker - it's a team behavior observatory. The press finds that secret and builds the CLI around it.

---

### Non-stop flights over 8 hours from SEA, Dec 24 to Jan 1, cheapest first.

```
$ /pp-flightgoat sea long-haul nonstop dec 24 to jan 1, 4 pax, cheapest first
```

Nonstop 8+ hour SEA round-trips, Dec 24 2026 to Jan 1 2027, 4 passengers, cheapest first.

| # | Destination | Total | Per pax | Airline | Outbound |
| --- | --- | --- | --- | --- | --- |
| 1 | London LHR | $4,953 | $1,238 | Delta DL20 | 9h42m |
| 2 | Amsterdam AMS | $5,052 | $1,263 | Delta DL142 | 9h50m |
| 3 | Tokyo Haneda HND | $5,817 | $1,454 | ANA NH117 | 10h35m |
| 4 | Paris CDG | $6,515 | $1,629 | Air France AF77 | 9h35m |
| 5 | Frankfurt FRA | $6,538 | $1,635 | Lufthansa LH491 | 10h10m |
| 6 | Doha DOH | $6,912 | $1,728 | Qatar QR720 | 14h35m |
| 7 | Dubai DXB | $7,142 | $1,786 | Emirates EK230 | 14h35m |
| 8 | Seoul ICN | $7,634 | $1,909 | Delta DL197 | 11h55m |
| 9 | Taipei TPE | $8,296 | $2,074 | EVA BR25 | 13h10m |
| 10 | Istanbul IST | $8,725 | $2,181 | Turkish TK204 | 12h |

### When does OKC play next, and what's the cheapest fly-in / next-morning-out?

```
$ /pp-espn nba okc round 2 game 1 + /pp-flightgoat sea-okc, fly-in same day
```

The setup

OKC just won Game 4 vs Phoenix, 131-122. Round 2 Game 1 is TBD on date and opponent. Best estimate for the next OKC home game: Sat May 9 or Sun May 10.

| Date | Out (for ~7pm CT) | RT total |
| --- | --- | --- |
| Fri May 8 → Sat May 9 | WN 3936/735 6:30am → 4:40pm CT | $437 |
| Sat May 9 → Sun May 10 | F9 1176/1928 6:52pm → arrives too late | skip |
| Sun May 10 → Mon May 11 | WN 3936/3537 6:15am → 3:05pm CT | $437 |

Pick: Wait 24-48h for ESPN to publish Round 2 Game 1, then book Southwest 1-stop for $437 RT (Wanna Get Away+ for refundable flexibility). Skip Frontier May 9 outbound; lands after tip.

### Kelly Van Horn's filmography, sorted by Rotten Tomatoes.

```
$ /pp-movie-goat person 'Kelly Van Horn' --sort rotten-tomatoes
```

Kelly Van Horn filmography sorted by Rotten Tomatoes - one CLI call, two source APIs (TMDb + OMDb).

| RT | Title (Year) | Role |
| --- | --- | --- |
| 91% | Raising Arizona (1987) | First Assistant Director |
| 69% | Independence Day (1996) | Unit Production Manager |
| 50% | Forget Paris (1995) | Production Manager / Co-Producer |
| 49% | Eight Legged Freaks (2002) | UPM / Co-Producer |
| 45% | The Day After Tomorrow (2004) | Executive Producer |
| 38% | Almost an Angel (1990) | Line Producer |
| 29% | The Thirteenth Floor (1999) | UPM / Co-Producer |
| 24% | Resident Evil: Extinction (2007) | Executive Producer |
| 22% | Leave It to Beaver (1997) | Co-Producer |
| 20% | Godzilla (1998) | UPM / Co-Producer |
| 20% | Out on a Limb (1992) | UPM / Line Producer |

### Find me the best chocolate cake.

```
$ /pp-recipe-goat find chocolate cake --rank trust --servings 8
```

Servings8

1. 1\. Sift 2 cups all-purpose flour, 3/4 cup cocoa, and a pinch of salt together.
2. 2\. Beat 2 cups sugar with 1/2 cup neutral oil; add 2 large eggs one at a time.
3. 3\. Bake at 350F for 30 min timer

Widget has scalable servings, ingredient links inside the steps, and timers - all from a single recipe-goat call.

### Every blocked issue whose blocker has been stuck for a week.

```
$ /pp-linear sql 'blocked issues whose blocker hasn't moved in 7 days'
```

```
linear-pp-cli sql --compact <<SQL
SELECT i.identifier, i.title, age(now(), b.updated_at) AS stuck
FROM issues i JOIN issue_relations r ON r.issue_id = i.id
JOIN issues b ON b.id = r.related_issue_id
WHERE r.type = 'blocked_by' AND b.state = 'in_progress'
AND b.updated_at < now() - interval '7 days';
SQL
```
- ENG-412 Crash on cold-start · blocked 11d
- ENG-388 Reconnect dropped sockets · blocked 9d
- ENG-301 Backfill missing rows · blocked 8d

50ms against the local SQLite mirror. Compound queries the Linear API can’t answer.

### Find a verified email for a person you've never met.

```
$ /pp-contact-goat 'Jane Doe' company:Acme --use deepline
```

1. 1 Look up on LinkedIn
2. 2 Cross-check Happenstance for warm intros
3. 3 Pay Deepline for the verified email

Magic-moment recording in flight. The CLI ships today; the type-specimen page lands when the screen recording does.

- [
	pp-cloud-run-admin
	Deploy and manage user provided container images that scale automatically based on incoming requests. The Cloud Run Admin API v1 follows the Knative Serving API specification, while v2 is aligned with Google Cloud AIP-based API standards, as described in https://google.aip.dev/.
	Printed by @cathrynlavery (Cathryn Lavery).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/cloud/cloud-run-admin)
- [
	pp-amazon-seller
	Read FBA inventory, orders, sales reports, listings, and catalog data for an Amazon seller account.
	Printed by @cathrynlavery (Cathryn Lavery).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/commerce/amazon-seller)
- [
	pp-craigslist
	Search, sync, and watch Craigslist with a local SQLite snapshot history, cross-city aggregation, scam scoring, and price-drift detection.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/commerce/craigslist)
- [
	pp-ebay
	Buyer-power-user CLI for eBay. Sold-comp intelligence, true sniper bidding, watchlist intelligence, saved-search feeds, and a local SQLite store for cross-listing analytics.
	Printed by @mvanhorn (Matt Van Horn).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/commerce/ebay)
- [
	pp-fedex
	Ship, rate, and track FedEx packages from the terminal — built for small business shippers.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/commerce/fedex)
- [
	pp-instacart
	Natural-language Instacart CLI that talks directly to the web GraphQL API. Add items to your cart, search products, and manage carts across retailers without browser automation.
	Printed by @mvanhorn (Matt Van Horn).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/commerce/instacart)
- [
	pp-shopify
	Operate a Shopify store from the terminal with curated Admin GraphQL commands, local sync, analytics, and bulk exports.
	Printed by @cathrynlavery (Cathryn Lavery).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/commerce/shopify)
- [
	pp-tiktok-shop
	Safe v1 TikTok Shop Seller API CLI/MCP for auth readiness, token exchange and refresh, read-only shops, orders, products, inventory search, fulfillment packages, and warehouses.
	Printed by @cathrynlavery (Cathryn Lavery).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/commerce/tiktok-shop)
- [
	pp-yahoo-finance
	Quotes, charts, fundamentals, options chains, and a local portfolio/watchlist tracker against Yahoo Finance — no API key, with Chrome-session fallback for rate-limited IPs
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/commerce/yahoo-finance)
- [
	pp-agent-capture
	Record, screenshot, and convert macOS windows and screens for AI agent evidence
	Printed by @mvanhorn (Matt Van Horn).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/developer-tools/agent-capture)
- [
	pp-company-goat
	One call across seven authoritative sources to research a startup's funding history (SEC Form D), engineering velocity (GitHub), HN mentions, legal entity (US/UK), and domain age. Compares competitors side-by-side and flags inconsistencies between public claims and filings.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/developer-tools/company-goat)
- [
	pp-docker-hub
	Docker Hub public API. Search container images, browse tags, check sizes, inspect Dockerfiles, and explore the world's largest container registry. No authentication required for public repositories (rate limited to ~18 req/min).
	Printed by @hnshah (Hiten Shah).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/developer-tools/docker-hub)
- [
	pp-firecrawl
	API for interacting with Firecrawl services to perform web scraping and crawling tasks.
	Printed by @hnshah (Hiten Shah).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/developer-tools/firecrawl)
- [
	pp-nvd
	The NVD is the U.S. government repository of standards-based vulnerability management data. Search CVEs by keyword, product (CPE name), CVE ID, or date range. Get CVSS scores, affected versions, references, and severity ratings. No API key required (optional for higher rate limits).
	Printed by @hnshah (Hiten Shah).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/developer-tools/nvd)
- [
	pp-postman-explore
	Public API network directory for discovering community collections, workspaces, and APIs
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/developer-tools/postman-explore)
- [
	pp-pypi
	PyPI JSON API. Look up Python package metadata, versions, release files, and vulnerability data. Browse recent updates and newest packages via RSS feeds. No authentication required — all endpoints are public.
	Printed by @hnshah (Hiten Shah).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/developer-tools/pypi)
- [
	pp-scrape-creators
	Scrape public social media data from the terminal — profiles, posts, videos, comments, ads, and transcripts across TikTok, Instagram, YouTube, Twitter/X, LinkedIn, Facebook, Reddit, Threads, Bluesky, Pinterest, Snapchat, Twitch, Kick, Truth Social, and 15+ link-in-bio / creator link services.
	Printed by @adrianhorning08 (Adrian Horning).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/developer-tools/scrape-creators)
- [
	pp-trigger-dev
	Durable background jobs and AI agent orchestration — runs, schedules, deployments, batches, queues, waitpoints, env vars, and TRQL analytics
	Printed by @mvanhorn (Matt Van Horn).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/developer-tools/trigger-dev)
- [
	pp-allrecipes
	Search and fetch Allrecipes recipes as structured data, scale ingredients, build grocery lists, rank by Bayesian-smoothed popularity, and clear Cloudflare with a Chrome session cookie.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/food-and-dining/allrecipes)
- [
	pp-dominos
	Order pizza, browse menus, optimize deals, and track delivery from your terminal — with a local SQLite store that powers reorder, price comparison, and deal stacking no other Domino's tool offers.
	Printed by @mvanhorn (Matt Van Horn).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/food-and-dining/dominos)
- [
	pp-food52
	Search, browse, and read Food52 from your terminal — with offline FTS, pantry matching, recipe scaling, and the editorial signals other tools throw away.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/food-and-dining/food52)
- [
	pp-pagliacci
	Order Seattle's Pagliacci Pizza from the terminal — half-and-half pies, small-party planner, slice rotation, and rewards stacking.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/food-and-dining/pagliacci)
- [
	pp-ahrefs
	Query Ahrefs backlinks, keyword, rank tracking, site audit, and SERP data from the terminal.
	Printed by @cathrynlavery (Cathryn Lavery).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/marketing/ahrefs)
- [
	pp-clarity
	Client-side instrumentation helpers for Microsoft Clarity.
	Printed by @cathrynlavery (Cathryn Lavery).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/marketing/clarity)
- [
	pp-customer-io
	Manage Customer.io campaigns, broadcasts, segments, deliveries, exports, and Reverse-ETL via the Service Account token.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/marketing/customer-io)
- [
	pp-dub
	Modern link attribution platform — short links, conversion tracking, affiliate/partner programs.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/marketing/dub)
- [
	pp-google-ads
	Google Ads API for account discovery, GAQL reporting, campaigns, budgets, assets, conversions, audiences, planning, and billing operations.
	Printed by @cathrynlavery (Cathryn Lavery).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/marketing/google-ads)
- [
	pp-klaviyo
	Marketing automation, profiles, events, campaigns, flows, segments, and templates.
	Printed by @cathrynlavery (Cathryn Lavery).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/marketing/klaviyo)
- [
	pp-producthunt
	Read Product Hunt from your terminal — works token-free for the daily skim, unlocks a launch-day cockpit and a marketer research desk in one onboarding step.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/marketing/producthunt)
- [
	pp-archive-is
	Bypass paywalls and look up web archives via archive.today. Hero command: find or create an archive for any URL with lookup-before-submit, Wayback Machine fallback, and agent-hints on stderr when called non-interactively.
	Printed by @mvanhorn (Matt Van Horn).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/media-and-entertainment/archive-is)
- [
	pp-google-photos
	Google Photos Library and Picker APIs for app-created media, albums, uploads, and user-selected media.
	Printed by @cathrynlavery (Cathryn Lavery).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/media-and-entertainment/google-photos)
- [
	pp-hackernews
	Hacker News from your terminal — with a local SQLite store, snapshot history, and agent-native output no other HN tool has.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/media-and-entertainment/hackernews)
- [
	pp-pokeapi
	Fully offline Pokédex with SQL, full-text search, type math, and a damage calculator no other Pokémon tool ships as a CLI.
	Printed by @hnshah (Hiten Shah).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/media-and-entertainment/pokeapi)
- [
	pp-steam-web
	Look up Steam players, games, achievements, friends, and stats from the command line
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/media-and-entertainment/steam-web)
- [
	pp-wikipedia
	Wikipedia REST API. Get article summaries, search, browse related topics, and access on-this-day events. No authentication required. Uses a polite User-Agent header.
	Printed by @hnshah (Hiten Shah).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/media-and-entertainment/wikipedia)
- [
	pp-sentry
	Error tracking and performance monitoring - projects, issues, events, releases
	Printed by @cathrynlavery (Cathryn Lavery).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/monitoring/sentry)
- [
	pp-apartments
	Search Apartments.com listings, sync results to a local SQLite store, and run workflows the website never built — diff saved searches, rank by $/sqft, compare shortlists, and surface price drops or phantom listings.
	Printed by @rderwin.
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/other/apartments)
- [
	pp-open-meteo
	Forecasts, historicals, marine, air quality, flood, climate, ensemble, and seasonal data from Open-Meteo's free tier.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/other/open-meteo)
- [
	pp-redfin
	Search Redfin homes for sale via internal Stingray endpoints, sync to local SQLite, and run workflows the website doesn't expose — saved-search diff, $/sqft net-HOA ranking, sold comps, multi-region trends.
	Printed by @rderwin.
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/other/redfin)
- [
	pp-ufo-goat
	Browse, search, and download declassified UAP files from the War.gov PURSUE archive
	Printed by @davemorin (Dave Morin).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/other/ufo-goat)
- [
	pp-weather-goat
	Weather forecasts, severe weather alerts, air quality, and GO/CAUTION/STOP activity verdicts for walk, bike, hike, commute, and drive
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/other/weather-goat)
- [
	pp-coingecko
	CoinGecko public API for cryptocurrency data. Free tier, no API key required for basic endpoints.
	Printed by @hnshah (Hiten Shah).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/payments/coingecko)
- [
	pp-kalshi
	Trade prediction markets, persist tick data, and answer category-level P&L questions Kalshi.com cannot.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/payments/kalshi)
- [
	pp-mercury
	Business banking API for accounts, transactions, payments, recipients, cards, invoices, treasury, and webhooks
	Printed by @cathrynlavery (Cathryn Lavery).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/payments/mercury)
- [
	pp-cal-com
	Every Cal.com feature, plus offline agendas, composed booking flows, and analytics no other Cal.com tool ships.
	Printed by @tmchow (Trevin Chow).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/productivity/cal-com)
- [
	pp-fireflies
	Every Fireflies meeting feature, plus offline search, cross-meeting intelligence, and a local database no other tool...
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/productivity/fireflies)
- [
	pp-notion
	Every Notion database queryable offline — cross-workspace SQL joins, stale detection, and relation graph traversal...
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/productivity/notion)
- [
	pp-roam
	Every Roam HQ surface — chat, transcripts, On-Air events, SCIM, webhooks — in one local-first CLI with offline...
	Printed by @gregvanhorn (Greg Van Horn).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/productivity/roam)
- [
	pp-slack
	Send messages, search conversations, monitor channels, and manage your Slack workspace from the terminal
	Printed by @mvanhorn (Matt Van Horn).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/productivity/slack)
- [
	pp-airbnb
	Search Airbnb and VRBO, find the host's direct booking site, and report the cheapest of three sources side-by-side.
	Printed by @mvanhorn (Matt Van Horn).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/travel/airbnb)
- [
	pp-flight-goat
	Search Google Flights, scan Kayak long-haul routes, and join FlightAware AeroAPI reliability, alerts, and tracking from one CLI.
	Printed by @mvanhorn (Matt Van Horn).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/travel/flight-goat)
- [
	pp-seats-aero
	Seats.aero Partner API for award travel availability, cached search, route lists, and trip revalidation details.
	Printed by @cathrynlavery (Cathryn Lavery).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/travel/seats-aero)
- [
	pp-wanderlust-goat
	Wanderlust GOAT — what a knowledgeable local with great taste would tell you to walk to from here, fused across editorial, local-language, and crowd layers no single tool ranks together.
	Printed by @jheitzeb (Joe Heitzeberg).
	Library →
	](https://github.com/mvanhorn/printing-press-library/tree/main/library/travel/wanderlust-goat)