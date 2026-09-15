# Resource Library Directory

This directory serves as the filing cabinet for all reference materials, research, assets, and tools.

> **AGENT INSTRUCTION:** If an ingested file does not clearly belong in one of the existing folders below, the agent MUST ask Tony for approval before creating a new directory. Do not guess or create new top-level folders without permission.

> **GLOBAL FRONTMATTER CONTRACT:** EVERY note in this library (text-file OR image-derived) MUST conform to the single canonical contract defined in `001_Architecture/Skills/ingest/SKILL.md` → "Step 2 / Frontmatter Rules". Summary:
> - `tags:` (lowercase YAML block list) is the ONLY tag carrier — never `Tag:`, `Tags:`, or a `Category:` list. 2–5 tags, lowercase kebab-case, topical.
> - `type:` — required, single value, real content type (never `extracted-knowledge`).
> - `form:` — required, single value: what the thing IS (`github-repo`, `saas-tool`, `youtube-video`, `tiktok`, `channel-study`, …). This is what makes fuzzy library queries resolvable.
> - `summary:` — required frontmatter field, 1–3 sentences on the primary subject.
> - `url:` — required whenever a source / product / repo URL is **visible** (obfuscated-but-reconstructable counts). GitHub repos: `form: github-repo` + `github-repo` as first tag + repo URL in `url:` only if shown.
> - `search_for:` — when `url` is unknown but the thing is nameable: the web-search string to resolve it later. Pairs with a `needs-enrichment` tag. **Never invent a URL** that wasn't in the source.

## Folder Layout & Descriptions

*   **Archive:** The graveyard for outdated or irrelevant information. (Files are manually moved here; agents should *never* automatically route files to Archive).
*   **Docs:** Document files (PDFs, Excel, Pages, Word files) and their accompanying analysis notes. Markdown files belong here only in rare API/configuration cases, such as curl examples or HTTP request/reference notes. Docs is primarily for PDFs and text documents.
*   **Investments:** Saved research, screenshots of stock picks, market news, or crypto analysis. (Keeps raw research out of the active `008_Investments` workspace).
*   **Models:** Strictly for AI models (Claude, Gemini, Qwen, etc.), API specs, pricing charts, and Comfy UI model weight documentation.
*   **Image storage (2026-09-09):** Every image lives **in the same category folder as its note**, sharing the exact name stem — `Tools/OpenCode.md` + `Tools/OpenCode.png`. The `![[...]]` embed points at the sibling file. `Obsidian_Attachments/Visual_Assets/` is retired (kept only for `rename_log.md`).
*   **Visual review tool (2026-09-09):** `001_Architecture/Tools/Resource-Library-Visualizer/serve.py` — local browser gallery for browsing, culling, and fixing these notes. `python3 .../serve.py` → `localhost:8756`. See `TOOLBOX.md`.
*   **Prompts:** Screenshots or text of useful prompts. If the image clearly captures reusable prompt text, the note should preserve that prompt content in text form and route here. Categorized via YAML tags (e.g., `text-to-text`, `image-to-video`).
*   **Design_Inspiration:** Aesthetic / style reference with **no specific product or post attached** — color, layout, mood, a channel's or brand's visual style, aesthetic Instagram accounts, image-only mood references. If it's a product mockup, it goes in Mockups; if it's saved to recreate as a post/video, it goes in Content_Ideas.
*   **Mockups:** A **blank product template** meant to have Tony's own design digitally superimposed onto it later for a store listing — a blank/empty frame or poster hanging in a staged room, or a blank t-shirt on a model/mannequin (e.g. a fashion pose with a plain, graphic-free shirt). **The test is blank vs. finished, not "is there a frame/shirt in the shot":** if the frame or shirt already shows a completed, specific design/graphic, it is NOT a Mockups shot — a room with finished abstract art already framed on the wall is `Design_Inspiration` (or `Content_Ideas`/`POD_Prints` if that finished design itself is the point), and a shirt already printed with a graphic is `POD_Prints` (a print reference or an existing listing), never `Mockups`. Mockups is exclusively the blank canvas Tony overlays his own art onto.
*   **POD_Prints:** Print-on-demand references and designs for the Etsy POD stores (Board-Nomad, Unamoss-Creative) — shirt/apparel/print designs, POD product research, print provider/blank comparisons. Also digital prints/illustrations meant for sale, including the Ikigai Digital (IkigaiDigitalStudio) printable-art line — a print or illustration is a POD_Prints item even when it's a digital-only download, never `Digital_Products` (that folder is for information products — ebooks/guides/courses — not visual/print goods). Distinct from `Mockups`, which is the staged product-render photos showing a print in a room, not the print/illustration itself.
*   **Content_Ideas:** An image or clip saved specifically because Tony wants to **recreate it as a post or video** he intends to make. The "I want to do this for [channel]" bucket. Pair with a channel/project tag at ingest time. This includes AI-generated character/scene art (even styled like a "selfie") and any whimsical animal, nature/macro-photography, historical/mythic, strange-facts, or business-story image that reads like direct source material for one of the YouTube channels. Concrete visual patterns to recognize:
    - A BBC-nature-documentary-style rendering, diagram, or infographic of an animal (a pistol shrimp diagram, a "how X sees the world" science visual, any real-species deep-dive) → **Anomalous Wild**.
    - A whimsical/meme-style AI-generated animal video or image — cats, a bear, "a bear with grandma," anthropomorphized pets — → **Neon Parcel**.
    - AI-generated historical or mythic imagery (ancient civilizations, emperors, warriors, ruins, "what if history had X" concepts) → **Reimagined Realms** or **Kingdoms and Conquerors**.
    - Eerie/folklore/paranormal imagery → **Glyphary**. Strange-facts/geography/natural-phenomena visuals, ancient-mystery engineering shots, or anything using a distinctive flat "silhouette" 3D art style → **Polyoculis**. A company logo, founder photo, or "started in a garage/dorm room" imagery → **Business Origin Stories**. A scenic/food/wildlife/destination photo that reads as travel-video B-roll or a "ranking/guide" idea → **Bored Nomad** (contrast with `Personal`: a practical health/travel-logistics bookmark like a medicine or vitamin drink is `Personal`, not this). Calm/atmospheric/cozy-aesthetic imagery with no other obvious hook → **Room Portal**.
    Full channel context (tone, audience, examples): `002_Content-Creation/Video_Editor/002_Channels/*/` — read the relevant channel's `*_Content_System.md` when unsure which one an image fits.
    When in doubt between this and `Design_Inspiration`: a specific reusable image with an obvious "I'd turn this into a video/post" quality is Content_Ideas; a vaguer mood/style reference with no specific reuse plan is Design_Inspiration.
*   **Tools:** Any plugin, SaaS, or software (including screenshots of tool websites like manis.ai). If the image primarily shows the product, a GitHub repo, a URL, or captions clearly identifying the software, route here. Kept as a flat folder to simplify routing.
*   **Tutorials:** Specifically reserved for how-to guides or screenshots of YouTube/TikTok tutorials outlining a process. If the image is mainly a walkthrough or lesson, route here and preserve title/creator/URL details when available.
*   **Workflows:** Process diagrams, flowcharts, operational pathways, and workflow references that are not primarily a software product or tutorial. Use this for screenshots or notes whose main value is the process map itself.
*   **Clipping:** Reference and ideas for the Whop Clipping department — clip niches, viral clip techniques, client/brand research, and content saved as clipping ideas. (Renamed 2026-09-10 from Project_Ideas; the ~30 pre-existing notes here predate this meaning and still need sorting into their real homes via the visualizer's Move button.)
*   **Digital_Products:** Reference for Tony's digital-**information**-products business — ebooks, guides, courses, templates, presets, funnels, and Gumroad/Lemon Squeezy research, his own or a bookmarked example to duplicate/sell. Roughly: anything teaching someone how to do something or get something (make money, learn a skill) via a digital download or class. **Never** a print, illustration, wall-art design, or other visual/decorative digital good — a print goes in `POD_Prints`, a design-only aesthetic reference goes in `Design_Inspiration`, and a video-worthy image goes in `Content_Ideas`.
*   **Affiliate_Marketing:** Affiliate program research and reference — Amazon Associates, Impact, travel affiliate programs, commission/payout structures, and other affiliate-partner platforms.
*   **UGC:** User-generated-content reference — UGC ad examples, UGC creator platforms/marketplaces, briefs, and rate/pricing research. (Flag if this means something more specific to you — e.g. only UGC you're commissioning vs. also UGC-style content you create yourself.)
*   **Travel:** Travel destinations, guides, and lifestyle references not tied to a specific affiliate program (see Affiliate_Marketing for the program/commission side) — the Bored Nomad travel content itself.
*   **Research:** Competitive analysis, channel studies, benchmark captures, market/product research, and other notes that exist to study or compare something later.
*   **Personal:** Non-business references and personal-interest captures — real-world life stuff: concert/tour flyers, lifestyle references, and health/food/wellness finds (a gluten-free bread, a travel anti-diarrhea medicine, a vitamin C drink spotted at a 7-Eleven in Thailand, a diagram of turmeric's health benefits). **Never** an AI-generated character, scene, or stylized "selfie" — no matter how personal it looks, that's content-creation material (see `Content_Ideas`), not a real personal-life capture.
*   **Videos:** Complete "knowledge packages" for video content. Each video gets its own subfolder (e.g., `Videos/[Descriptive-Name]/`) containing the video file, a transcript markdown file, and future tutorial/screenshot files.
*   **Undetermined:** The review queue. Notes an automated pass (ingest vision, or `retag_and_retitle.py`) couldn't confidently classify land here with a `retag_flag` explaining why, instead of being silently left wrong. Reviewed manually, or re-run through the classifier as a retry queue once the underlying issue is fixed.

*(Note: "Bookmarks" is not a category. If a file is a bookmark, it must be classified by its topic—Tool, Tutorial, Investment, etc.—and routed accordingly.)*

## Source Definitions

Every note's `source_label` is exactly one of these three (auto-detected, never hand-picked):

*   **YouTube:** A YouTube link appears in the note's `url`/`source` field or body.
*   **Bookmark:** Has an `http` `source:` field and an image — a Web Clipper capture.
*   **Screenshot:** Everything else with an image — phone screenshots with no clean source URL.
*   **MD:** A text-only note with no image and no YouTube link — plain markdown content (Notion exports, hand-written notes, idea lists).

## Tag Vocabulary

Locked 2026-09-11. `tags:` carries **1 minimum, 2 maximum** values, every one drawn from this exact list — nothing outside it. **A second tag is never required or expected by default — one good tag beats two where the second is a stretch.** Only add a second tag when it is clearly, specifically supported by the note's own content; if you're not sure it genuinely applies, leave it off rather than force it. This is the single source of truth; scripts (e.g. `retag_and_retitle.py`) must parse this list at runtime rather than hardcode a copy.

*   **Guide:** Selling or teaching how to do something — an article, screenshot, or bookmark for a guide/tutorial.
*   **Profile:** A profile page (TikTok, YouTube, any platform) saved to study later — what they're doing right.
*   **Product:** A screenshot or webpage for a specific **physical, tangible** product Tony might buy or might sell via his TikTok/Amazon affiliate shop — a vacuum, a handheld translator, a kitchen gadget, an apparel item, etc. **Never** software, an app, a game, a SaaS tool, or any digital-only good — those already have their own tags (`App`, `Gaming`, etc.) and are never `Product` regardless of how the page markets itself. If you couldn't physically ship it, it isn't `Product`.
*   **Art-Reference:** Broad creative-reference bucket — a liked visual style (e.g. 3D animation), a character sheet or storyboard, a rendered character, a company logo, an infographic, or a cute/meme screenshot to replicate. Purely visual/creative-asset reference — never apply based on a note's *subject matter* being about virality, trends, or growth; that's `Guide` or `Research-List` territory, not this tag.
*   **Gaming:** A gaming-specific tool or website.
*   **3D:** 3D/3D-animation tools — Blender, etc.
*   **Art-Style:** A specific art style that would need to be reproduced in a text-to-image model, for video-pipeline character sheets or Etsy print art.
*   **Platforms:** Only when the note's actual SUBJECT is a specific platform/service/marketplace Tony wants to bookmark and remember for later — a UGC platform that connects him with clients, an affiliate-network aggregator, a PLR marketplace, or similarly a new/niche service he doesn't already have top of mind. **Never apply this just because a well-known platform (TikTok, YouTube, Instagram, etc.) is mentioned or is the medium a screenshot came from** — a TikTok video about making money with faceless YouTube Shorts is not "about" TikTok or YouTube as platforms; it's content Tony already knows those exist and doesn't need reminding. This tag is for platforms he'd otherwise forget, not incidental context.
*   **Stocks:** A stock ticker, stock pick, or stock-advice screenshot.
*   **Crypto:** Same as Stocks but crypto.
*   **App:** A mobile/web/desktop app or SaaS (usually lands in Tools, but fine wherever its role fits — e.g. a clipping tool in Clipping).
*   **GitHub:** Specifically a GitHub repo.
*   **LLM:** A large language model, mainly for coding.
*   **Image-Video-Model:** A text-to-image, text-to-video, or image-to-video model.
*   **Audio-Model:** TTS/voice models — ElevenLabs, Whisper, Wispr Flow, etc.
*   **Research-List:** The screenshot must **visibly show an actual list layout** — numbered items (1. 2. 3.), bullet points, or a run of hashtags (e.g. `#IHeartAnimals #AnimalsAreCool #WildAnimals`), or a numbered ranking like "The 10 Best Cities in California: 1. San Francisco 2. San Diego...". A page that simply *mentions* several things (a news section, an announcement, a multi-topic article) is **not** a list unless it's actually laid out as one — don't apply this tag just because content could theoretically be counted or enumerated.
*   **Health:** Food/food-products/medicine saved to research or buy later (usually lives in Personal).
*   **Pipeline:** Any software process/automation tutorial that chains multiple tools together (Higgsfield+Adobe, Claude+Higgsfield, CapCut+Higgsfield, a POD automation, etc.) — not a single-app tutorial.
*   **Coding-Agent:** Codex, Antigravity, Claude, Claude Code, Hermes, or any coding agent/harness.
*   **Misc:** Doesn't fit anything above.
