# Bored Nomad — Website Redesign Case Study
**Prepared:** March 31, 2026  
**Site:** borednomad.com  
**Current Stack:** WordPress + Elementor + Cloudways hosting  
**Proposed Stack:** Astro + Cloudflare Pages  

---

## Executive Summary

Bored Nomad has solid content — real travel experience, well-written posts, genuine affiliate integration, and good SEO bones. But the design is working against it. The site reads as a generic WordPress blog from 2019. It lacks visual identity, has no clear hierarchy on the homepage, buries calls to action, and gives visitors no emotional reason to stay.

This case study audits the current site, identifies every critical issue, and proposes a redesign strategy using Astro + Cloudflare Pages that would dramatically improve performance, aesthetics, and conversion.

---

## Section 1: Current Site Audit

### 1.1 Homepage

**What exists:**
- Plain text logo "BORED NOMAD" — no wordmark, no visual identity
- Deep dropdown navigation (Destinations > Asia > Cambodia, etc.)
- A single paragraph of text as the "hero" — no image, no visual impact
- A section titled "Most Recent Post" showing a 2-column blog card grid
- A minimal footer with only a newsletter signup

**Critical issues:**

| Issue | Impact |
|-------|--------|
| No hero image or visual anchor above the fold | Visitor has no emotional reason to stay — first impression is a wall of text |
| Cookie consent banner covers top 25% of viewport on load | Immediately degrades first impression |
| "Privacy Policy" is in the main navigation | Looks unfinished and unprofessional |
| Navigation is overly deep (11 Asia subcategories in dropdown) | Overwhelming, hard to scan, collapses badly on mobile |
| Homepage description links to `woocommerce-547246-1756076.cloudwaysapps.com/about/` | **Broken link** — points to old Cloudways staging URL, not borednomad.com/about |
| "Most Recent Post" section header is weak | Generic heading that tells visitors nothing about the brand |
| No featured destinations, no curated content, no editorial voice | Looks like a feed, not a publication |
| Blog cards are small, uniform, and lack visual hierarchy | Nothing draws the eye — everything competes equally for attention |
| No clear CTA above the fold | Visitors who don't immediately find something interesting bounce |
| GTM container not configured (console warning) | Analytics likely broken or incomplete |
| Third-party script `emrld.cc` throwing errors | Unknown tracker causing JS errors — should be audited or removed |

---

### 1.2 Blog Post Pages

**What exists:**
- Social share buttons at the very top (before the title)
- Hero/banner image above the fold (inconsistent — some posts have it, some don't)
- Good content structure with H2/H3 headings
- Affiliate links embedded in text
- Pinterest pin images at the bottom
- "Related posts" carousel at the bottom

**Critical issues:**

| Issue | Impact |
|-------|--------|
| No table of contents | Long posts (Istanbul guide is very long) are hard to navigate — users scan, not read |
| No estimated read time | Visitors can't commit to reading without knowing the time investment |
| No author bio section | No personal connection — Tony's story (sold house, full-time nomad) is compelling and unused |
| Social share buttons appear before the title | Wrong placement — share intent comes after value is delivered, not before |
| No sticky header or progress indicator on long posts | Reader gets lost, no breadcrumb back to the top |
| Post dates are visible and old (most 2020-2022) | Signals neglect to visitors even if content is still valid |
| Footer is just a newsletter form | No navigation, no about, no recent posts — dead end for engaged readers |
| "Read More »" CTA is weak | Generic — should be destination/topic specific |
| No internal linking strategy visible | SEO and reader flow opportunity being left on the table |

---

### 1.3 Navigation

Current navigation structure:
```
Destinations
  └── Asia
        ├── Cambodia
        ├── Indonesia
        ├── Japan
        ├── Malaysia
        ├── Myanmar
        ├── Philippines
        ├── Singapore
        ├── Thailand
        └── Vietnam
  └── Europe
        └── Italy
  └── West Asia
Tips & Tutorials
  ├── Travel Tips
  └── Website Tutorials
Gear
Resources
Privacy Policy   ← should NOT be here
```

**Problems:**
- Privacy Policy in the primary nav is a significant design error
- 9 Asia sub-countries in a single dropdown is overwhelming
- "Tips & Tutorials" and "Website Tutorials" are confusing — what's the difference?
- No search visible in desktop nav (it's hidden/collapsed)
- No "About" link in primary navigation — Tony's personal story is a core differentiator

---

### 1.4 Performance & Technical

- Running jQuery + jQuery Migrate (legacy WordPress dependency)
- Elementor CSS/JS load adding significant overhead
- WordPress PHP rendering on every request (Cloudways server)
- No visible image lazy loading strategy
- GTM container not configured despite being installed
- Unknown third-party script `emrld.cc` causing errors
- SSL is Full (strict) ✓
- Cloudflare proxy active ✓ (provides some CDN benefit despite WordPress)

---

## Section 2: Design Diagnosis

### What the site feels like right now

Generic. Safe. Dated. It feels like a beginner blog template that hasn't been touched since setup. There's no editorial voice in the design — nothing that says "this is Tony's perspective on travel" versus any other travel blog. The layout, typography, and color scheme communicate zero personality.

### What it should feel like

Bored Nomad has a genuinely interesting premise: a digital nomad who sold everything and travels while building a business. That's a story. The design should feel like:

- **Adventurous but not chaotic** — editorial travel magazine energy, not generic blog
- **Personal** — Tony is the brand, not just an anonymous publisher
- **Trustworthy** — affiliate recommendations need credibility signals
- **Fast** — travel content readers are mobile-first, often on slow connections abroad

---

## Section 3: Redesign Recommendations

### 3.1 Homepage — Full Rethink

**Current:** Text + blog card feed  
**Proposed:** Editorial homepage with three zones

**Zone 1 — Hero (above the fold)**
- Full-width cinematic photo from one of Tony's destinations
- Large, bold headline: something like *"Real travel. Real stories."* or lean into the nomad angle
- Two CTAs: "Explore Destinations" (primary) + "About Tony" (secondary)
- No cookie banner blocking this — move cookie to a slim bottom bar

**Zone 2 — Featured Content (below hero)**
- 3 "Editorial Picks" cards — manually curated, large format, with destination photo + headline + one-line tease
- Replace "Most Recent Post" with something like "Where We've Been" or just let the images do the talking
- Each card gets a region color accent (warm for Southeast Asia, cool for Europe, etc.) — subtle but creates visual language

**Zone 3 — Content Feed**
- Blog grid below featured section
- Cards should be larger with a clear image:text ratio
- Add category tag, read time, and title — drop the full excerpt (too much text per card)
- "Load more" instead of pagination (or infinite scroll for Astro)

**Footer — Complete rebuild**
- 4-column layout: About Bored Nomad | Popular Destinations | Quick Links | Newsletter
- Include Tony's face/bio blurb (1–2 sentences) — this builds trust for affiliate clicks
- Social links (Pinterest especially matters for travel)

---

### 3.2 Navigation — Simplify Radically

**Proposed structure:**
```
[Logo/Wordmark]    Destinations ▾    Blog    About    Resources    [Search icon]
```

Destinations dropdown — flattened to regions only:
```
Southeast Asia    |  East Asia   |  Europe  |  West Asia
[top 3 posts]     |  [top 3]    |  [top 3] |  [top 3]
```

- Remove Privacy Policy from nav entirely (footer only)
- Remove "Website Tutorials" from primary nav (move to Resources)
- Make "About" a primary nav item — Tony's story is a conversion driver
- Search should be visible (icon in nav bar), not hidden
- Mobile nav: hamburger → full-screen overlay with region cards

---

### 3.3 Blog Post Pages — Reader Experience

**Add:**
1. **Table of Contents** — sticky sidebar on desktop, collapsible block on mobile. Especially important for long guides like Istanbul.
2. **Estimated read time** — next to the date, e.g. "12 min read"
3. **Author bio block** — at the bottom of every post. Photo of Tony, 3–4 sentences, links to About page and social. This is critical for affiliate trust.
4. **Progress bar** — thin line at top of viewport showing scroll progress
5. **Post hero** — full-width image above the title on every post, consistent

**Move:**
- Social share buttons → bottom of post (after conclusion), plus a floating side button on desktop
- Pinterest pin images → integrate into content naturally, not a "Pin It" dump at the end

**Remove/Fix:**
- Visible old dates → either hide the year or add "Updated: [date]" to signal freshness
- "Read More »" → replace with contextual CTAs like "Explore Istanbul →" or "Read the Full Guide →"

---

### 3.4 Visual Identity

**Typography**
- Headlines: A strong serif or display font — something with character (Playfair Display, Lora, or a custom variable font)
- Body: Clean sans-serif for readability on mobile (Inter, Plus Jakarta Sans)
- Currently using generic system/WordPress fonts — no identity

**Color**
- Pick one accent color and commit to it. Travel sites often use a warm amber/gold or deep teal.
- Currently: undefined — whatever Elementor default applied
- Add destination-specific color accents (subtle tags per region)

**Photography**
- Tony has real travel photos — they should be the hero of the site
- Current implementation uses small thumbnails in cards — they're too small to evoke emotion
- Cards should be image-first, taller aspect ratio

**Logo**
- "BORED NOMAD" in plain text is not a logo
- Needs a wordmark at minimum — simple typography treatment with personality
- Optional: a small mark/icon that works as a favicon and social avatar

---

## Section 4: Astro Migration Plan

### Why Astro Makes Sense Here

| Factor | WordPress | Astro + Cloudflare Pages |
|--------|-----------|--------------------------|
| Page speed | ~60-75 PageSpeed (typical) | 95-100 (static HTML) |
| Hosting cost | Cloudways ~$14-30/mo | Free (Cloudflare Pages) |
| Maintenance | Plugin updates, security patches, PHP | Zero — just Markdown files |
| Affiliate links | Manual in post editor | Markdown + components |
| Build complexity | None (live edit) | Build step on each publish |
| Content editing | WordPress editor | Markdown files or CMS |

### Content Migration

borednomad.com has approximately 30-40 posts based on the sitemap. Migration path:

1. Export all posts from WordPress (Tools → Export → All content)
2. Use `wordpress-export-to-markdown` CLI to convert to `.md` files
3. Download all media from WordPress Media Library
4. Upload media to Cloudflare R2 (or keep on Cloudflare Pages `/public`)
5. Rebuild pages in Astro with new design

### Recommended Astro Setup

```
borednomad.com (Astro)
├── src/
│   ├── content/
│   │   └── posts/          ← All blog posts as .md files
│   ├── components/
│   │   ├── PostCard.astro
│   │   ├── Hero.astro
│   │   ├── TableOfContents.astro
│   │   ├── AuthorBio.astro
│   │   └── Newsletter.astro
│   └── pages/
│       ├── index.astro     ← Homepage
│       ├── about.astro
│       ├── [slug].astro    ← Blog post template
│       └── destinations/
├── public/                 ← Static assets
└── astro.config.mjs
```

### Content Management Options

Since Tony publishes occasionally (not daily), options ranked by simplicity:

1. **Markdown files in GitHub** — Edit in VS Code or GitHub web editor, push to deploy. Zero cost. Best for someone comfortable with Claude Code.
2. **Keystatic** — Git-based CMS with a nice UI. Runs locally or in the browser. Free.
3. **Decap CMS (formerly Netlify CMS)** — Git-based, browser UI, free. Works with Cloudflare Pages.
4. **Sanity** — More powerful, has a hosted studio. Free tier is generous. Good if content gets complex.

**Recommendation:** Start with Markdown + GitHub. If editing feels painful, add Keystatic later — it's a 30-minute addition to an Astro project.

---

## Section 5: Bugs to Fix Regardless of Stack

These should be fixed on the current WordPress site immediately:

1. **Broken link on homepage** — The "about us page" link points to `woocommerce-547246-1756076.cloudwaysapps.com/about/` — a Cloudways staging URL. Change it to `borednomad.com/about`.
2. **Privacy Policy in main nav** — Move to footer only.
3. **GTM container** — Either configure it properly or remove it. It's installed but not set up, consuming load time for nothing.
4. **emrld.cc script** — Audit this. It's throwing JS errors on every page load. Likely a plugin-injected tracker. Identify and remove if unused.
5. **Cookie banner** — Replace the full-page-blocking banner with a slim bottom bar.

---

## Section 6: Prioritized Action Plan

### Phase 1 — Fix now (current WordPress site, 1-2 hours)
- [ ] Fix broken about page link on homepage
- [ ] Remove Privacy Policy from main navigation
- [ ] Audit and remove emrld.cc script
- [ ] Configure or remove GTM container

### Phase 2 — Content prep (2-4 hours)
- [ ] Export WordPress content to Markdown
- [ ] Inventory all images, identify which need replacement
- [ ] Write updated author bio (3-4 sentences, current)
- [ ] Choose accent color and typography pair

### Phase 3 — Astro build (1-2 focused sessions with Claude Code)
- [ ] Scaffold Astro project with Cloudflare Pages adapter
- [ ] Build PostCard, Hero, TableOfContents, AuthorBio components
- [ ] Import Markdown content
- [ ] Deploy to Cloudflare Pages
- [ ] Point borednomad.com DNS to Cloudflare Pages (change A record)

### Phase 4 — Design polish (ongoing)
- [ ] New wordmark/logo
- [ ] Redesigned navigation
- [ ] Homepage editorial sections
- [ ] Mobile nav
- [ ] Footer rebuild

---

## Section 7: Expected Outcomes

| Metric | Current (estimate) | Post-Astro (estimate) |
|--------|-------------------|-----------------------|
| PageSpeed (mobile) | 55-70 | 92-98 |
| Time to First Byte | ~800ms+ (PHP + Cloudways) | <50ms (Cloudflare edge) |
| Hosting cost | ~$14-30/mo | $0 |
| Plugin maintenance | Monthly | None |
| Bounce rate | High (slow load + no hook) | Lower (fast + visual impact) |
| Affiliate click trust | Low (generic design) | Higher (author bio + credibility) |

---

*Case study prepared by Claude Code. Next step: review this document with Tony, align on design direction, then proceed to Phase 1 fixes.*

---

## Section 8: Recommended Tools — Fix WordPress Now, Then Migrate to Astro

### 8.1 WordPress MCP Servers (Let Claude Code control WordPress directly)

These tools give Claude Code direct access to your WordPress site so you don't have to manually make changes in the dashboard. You install a plugin or configure credentials once, then Claude does the rest.

---

#### Option A — Novamira (Recommended for cleanup work)
**URL:** https://novamira.ai  
**Cost:** Free, open source  
**What it is:** A WordPress plugin that acts as an MCP server. Once installed, Claude Code can run PHP directly inside WordPress, query the database, read/write/delete files, and call plugin APIs.

**What Claude can do with it:**
- Query and clean the WordPress database (remove post revisions, orphaned metadata, transients)
- Audit and identify unused/problematic plugins
- Read and edit theme CSS files directly
- Remove injected scripts (like the `emrld.cc` tracker found in the audit)
- Fix broken links (like the Cloudways staging URL on the homepage)
- Export content programmatically

**Important:** Novamira is designed for development/staging environments. Before using it, take a full site backup from Cloudways dashboard. It requires WordPress 6.9+.

**Setup:**
1. Install the Novamira plugin on borednomad.com via WordPress dashboard → Plugins → Add New
2. Activate and get the MCP connection credentials
3. Add to Claude Code's MCP config (`~/.claude/settings.json`)
4. Claude Code can then directly manipulate the site

---

#### Option B — claudeus-wp-mcp (Best for content + site management)
**GitHub:** https://github.com/deus-h/claudeus-wp-mcp  
**Cost:** Free, open source  
**Stars:** 115  
**What it is:** A TypeScript MCP server with 145 tools covering the full WordPress REST API. Uses WordPress Application Passwords for auth (no plugin install needed — works with any WordPress site).

**What Claude can do with it:**
- Manage all posts, pages, media, menus, taxonomies
- Run site health diagnostics
- Manage users and access
- Control Full Site Editing templates and global styles
- WooCommerce management (if needed later)

**Setup:**
1. In WordPress admin → Users → Profile → scroll to "Application Passwords" → create one
2. Create `wp-sites.json` with your site URL, username, and app password
3. Add to Claude Code MCP config
4. Requires Node.js ≥ 22

**Best for:** Ongoing content management, fixing nav structure, cleaning up pages, managing categories.

---

#### Option C — mcp-wordpress (easiest install, good for general use)
**GitHub:** https://github.com/docdyhr/mcp-wordpress  
**npm:** `npm install -g mcp-wordpress`  
**Cost:** Free  
**Stars:** 76  
**What it is:** 59-tool MCP server with a one-click Claude Desktop Extension install (DXT format). Supports multi-site. Good for general WordPress management without needing a plugin installed on the site.

**Setup:**
```bash
npm install -g mcp-wordpress
```
Then configure with your WordPress URL and Application Password.

---

#### Option D — elementor-mcp (Elementor-specific)
**GitHub:** https://github.com/msrbuilds/elementor-mcp  
**Cost:** Free  
**Stars:** 146 (very active — updated 3 hours ago as of research)  
**What it is:** A WordPress plugin that turns Elementor into an MCP server with 97 AI-ready tools. Since borednomad uses Elementor, this could let Claude directly edit page layouts, sections, and widgets.

**Best for:** If you want to redesign the current WordPress site before migrating, rather than after. Let Claude rebuild your homepage layout in Elementor without touching the editor manually.

---

### 8.2 Recommended Cleanup Workflow (Using MCP Tools)

Once Novamira + claudeus-wp-mcp are connected, here's the sequence Claude Code would run:

**Step 1 — Database cleanup**
```
- Remove all post revisions (keeps only latest)
- Delete orphaned postmeta
- Clear expired transients
- Optimize database tables
```

**Step 2 — Plugin audit**
```
- List all active plugins
- Identify plugins not updated in 12+ months
- Flag plugins known to inject scripts (check emrld.cc source)
- Deactivate and delete unused/broken plugins
```

**Step 3 — Script audit**
```
- Read wp_head and wp_footer hooks
- Identify emrld.cc injection source (which plugin added it)
- Remove or deactivate the source
```

**Step 4 — CSS cleanup**
```
- Read child theme CSS
- Remove unused/overriding styles
- Fix any Elementor inline style conflicts
```

**Step 5 — Content fixes**
```
- Fix broken homepage "about" link (staging URL → borednomad.com/about)
- Move Privacy Policy out of primary nav
- Configure or remove GTM container
```

**Step 6 — Export for migration**
```
WordPress admin → Tools → Export → All content → download XML
```

---

### 8.3 WordPress → Markdown Migration Tool

#### wordpress-export-to-markdown
**GitHub:** https://github.com/lonekorean/wordpress-export-to-markdown  
**npm:** `npx wordpress-export-to-markdown`  
**Cost:** Free, open source  

This is the cleanest tool for converting a WordPress XML export into Astro-ready Markdown files.

**What it does:**
- Converts each post to its own `.md` file with YAML frontmatter
- Downloads all images (attached media + scraped from post content) and updates references
- Handles drafts, pages, and custom post types
- Supports resuming interrupted runs (won't re-download existing files)

**How to run it:**
```bash
# 1. Export from WordPress
# WordPress Admin → Tools → Export → All Content → Download XML

# 2. Run the converter
npx wordpress-export-to-markdown

# Follow the wizard — it will ask:
# - Path to your XML export file
# - Whether to create a folder per post
# - Date prefix format
# - Whether to download images (say YES)
```

**Output structure:**
```
output/
├── 2024/
│   └── a-culinary-journey-through-istanbul/
│       ├── index.md          ← post content with frontmatter
│       └── images/           ← all downloaded images
├── 2022/
│   └── 12-delicious-must-try-foods-in-rome/
│       ├── index.md
│       └── images/
└── ...
```

**Frontmatter example:**
```yaml
---
title: "A Culinary Journey Through Istanbul: The Ultimate Food Guide"
date: "2024-07-12"
categories: ["Destinations", "West Asia", "Turkey"]
tags: ["food", "istanbul", "turkey"]
---
```

This output drops directly into Astro's `src/content/posts/` directory with minimal cleanup.

---

### 8.4 Full Automated Pipeline (End-to-End)

Here's the complete sequence from broken WordPress to live Astro site:

```
Phase A — Connect MCP tools (30 min setup)
├── Install Novamira plugin on borednomad.com
├── Create WordPress Application Password
├── Configure claudeus-wp-mcp in Claude Code settings
└── Claude Code now has full access to the site

Phase B — Cleanup via Claude Code (1 session)
├── Database: remove revisions, transients, orphaned data
├── Plugins: audit, remove unused/broken ones
├── Scripts: identify and remove emrld.cc injection source
├── Nav: remove Privacy Policy, fix broken about link
├── GTM: configure or remove
└── Export: download full WordPress XML export

Phase C — Convert to Markdown (20 min)
├── Run: npx wordpress-export-to-markdown
├── Choose: create folders per post + download images
└── Output: ~35 .md files with YAML frontmatter + all images

Phase D — Build Astro site (1-2 sessions with Claude Code)
├── npx create astro@latest (with Cloudflare Pages adapter)
├── Drop Markdown files into src/content/posts/
├── Build components: PostCard, Hero, TOC, AuthorBio, Newsletter
├── Set up routing: [slug].astro for post template
└── Test locally

Phase E — Deploy to Cloudflare Pages (30 min)
├── Push to GitHub repo
├── Connect repo in Cloudflare Pages dashboard
├── Set build command: npm run build
├── Set output directory: dist/
└── Cloudflare Pages auto-deploys on every push

Phase F — DNS cutover (5 min, after verification)
├── In Cloudflare DNS for borednomad.com:
│   Change A record from 206.189.211.50 (DigitalOcean)
│   to Cloudflare Pages CNAME
└── Old Cloudways server can be deleted after 30-day monitoring period
```

---

### 8.5 Cloudways Cleanup (After Migration)

Once borednomad.com is live on Cloudflare Pages and verified stable:

**borednomad.com:**
- Remove the Cloudways application
- If robottogato.com is also on the same Cloudways server, evaluate whether the server is still needed
- If N8n/MinIO are the only remaining services on the server, that's a separate decision (those are Docker services, not Cloudways-managed)

**robottogato.com:**
- Currently only used for the Cloudflare tunnel (N8n + MinIO) — not hosted on Cloudways
- The domain DNS is already managed through Cloudflare
- No Cloudways dependency there

**Net result:** Once borednomad migrates, Cloudways can potentially be cancelled entirely, saving $14-30/mo. N8n and MinIO run locally via Docker tunnel — no server needed for those.

---

### 8.6 Tool Summary Table

| Tool | Purpose | Cost | Install method |
|------|---------|------|----------------|
| **Novamira** | MCP server — run PHP, edit files, query DB in WordPress | Free | WordPress plugin |
| **claudeus-wp-mcp** | MCP server — 145 tools via REST API | Free | npm + wp-sites.json |
| **mcp-wordpress** | MCP server — 59 tools, easiest setup | Free | npm global or DXT |
| **elementor-mcp** | MCP server — edit Elementor layouts via AI | Free | WordPress plugin |
| **wordpress-export-to-markdown** | Convert WP XML export → .md files + download images | Free | npx (no install) |
| **Astro** | Static site framework for the rebuilt site | Free | npm |
| **Cloudflare Pages** | Hosting for the Astro site | Free | Cloudflare dashboard |
