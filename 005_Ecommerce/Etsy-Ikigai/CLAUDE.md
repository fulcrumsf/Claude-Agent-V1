---
title: "CLAUDE.md — Ikigai Digital Studio Etsy Store"
type: config
domain: ecommerce
tags: [config, ecommerce, ikigai-digital-studios]
---

# CLAUDE.md — Ikigai Digital Studio Etsy Store

Digital downloadable wall art shop on Etsy, same owner as Bored Nomad (the two shops cross-link each other's bios). Also the subject of the "Ikigai Digital Studios" YouTube channel (`002_Content-Creation/Video_Editor/002_Channels/011_Ikigai-Digital-Studios/`), which acts as its marketing/support arm.

## Shop (verified live, 2026-10-11)

- **URL:** https://www.etsy.com/shop/IkigaiDigitalStudio (also reachable at `ikigai.digitalstudio.etsy.com`)
- **Stats at check time:** 63 sales, 18 active listings, 5.0★ (4 reviews), on Etsy since 2023 (~2.5 years), based Raleigh, NC
- **Product:** 100% digital downloads (printable wall art), $6.50–$8.50 per listing — zero production/shipping cost, pure-digital margin
- **Categories:** Art Prints — Trendy, Reimagined, Abstract, Botanical, Food & Drink, Japan Art, Mid Century, Minimalism
- **Process (per shop's own "About"):** mixed media (digital art, photography, collage, hand drawing/painting, watercolor, block print, linocut, gouache), curated/reimagined vintage and public-domain art, and some generative-AI-assisted designs (disclosed per listing)
- **Future store:** own website planned, likely LemonSqueezy, to own customer data and avoid Etsy fees (per the YouTube channel's content system doc)

## Why this matters for the monetization plan

Zero marginal production cost per sale (digital-only) makes this the structurally easiest stream to scale toward the $1,000/month-by-December goal — no POD fulfillment partner, no shipping, no inventory. See `001_Architecture/Plans/Agent-OS-Monetization-Strategy-Plan.md` for the full revenue-stream comparison.

## Portal + listing pipeline (scaffolded 2026-10-21)

Brief: `Ikigai_Portal_Pipeline_Brief.md`. Code: `Portal/` (FastAPI, SQLite, Docker; tool steps are stubs until connected on the Mac, see `Portal/README.md`). Pinterest style dumps: `Creative_Inspiration/`. Nothing publishes without Tony; Etsy listings are drafts only.

## Etsy reference links (keep current, added 2026-10-25)
- Etsy Open API v3 docs: https://developers.etsy.com/documentation/ (developer app application still to file; next task).
- Etsy Seller Handbook: https://www.etsy.com/seller-handbook. Etsy keeps changing AI and seller policies; pull the latest before any listing/automation work and on a regular schedule so Tony never risks a ban. Follow handbook best practices in the Portal listing text and AI disclosure.

## Alura API (added 2026-10-26)
Tony's Alura workspace (Growth plan) has an official API and MCP: market keywords, competitor shops, and "Your shop" reads/writes via Alura's Etsy connection. Docs `https://docs.alura.io`; details and terms limits in TOOLBOX.md ("Alura official API + MCP"). BoredNomad's Alura connection is expired and needs a reconnect. Plan and decisions: `Etsy_API_V3_Application_Plan.md`.

## Etsy developer app approved (2026-10-26)
App "agent-OS" approved (personal use). Keys in `~/.env-secrets` (`ETSY_CLIENT_ID`, `ETSY_CLIENT_SECRET`). Limits 10 QPS / 10,000 QPD. Scopes to request: listings_w, listings_r, shops_r. Redirect URI still to register. Drafts only, never `state=active`. See `Etsy_API_V3_Application_Plan.md` and TOOLBOX.md.
