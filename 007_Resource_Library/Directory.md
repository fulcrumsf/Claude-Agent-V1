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

*   **Archives:** The graveyard for outdated or irrelevant information. (Files are manually moved here; agents should *never* automatically route files to Archives).
*   **Docs:** Document files (PDFs, Excel, Pages, Word files) and their accompanying analysis notes. Markdown files belong here only in rare API/configuration cases, such as curl examples or HTTP request/reference notes. Docs is primarily for PDFs and text documents.
*   **Investments:** Saved research, screenshots of stock picks, market news, or crypto analysis. (Keeps raw research out of the active `008_Investments` workspace).
*   **Models:** Strictly for AI models (Claude, Gemini, Qwen, etc.), API specs, pricing charts, and Comfy UI model weight documentation.
*   **Obsidian_Attachments/Visual_Assets:** The storage location for raw image files (`.png`, `jpg`, etc.). These are paired with note files in the matching category folder.
*   **Prompts:** Screenshots or text of useful prompts. If the image clearly captures reusable prompt text, the note should preserve that prompt content in text form and route here. Categorized via YAML tags (e.g., `text-to-text`, `image-to-video`).
*   **Design_Inspiration:** Visual inspiration references such as t-shirt designs, website designs, aesthetic Instagram accounts, and image-only mood references without a clear tool or tutorial focus.
*   **Tools:** Any plugin, SaaS, or software (including screenshots of tool websites like manis.ai). If the image primarily shows the product, a GitHub repo, a URL, or captions clearly identifying the software, route here. Kept as a flat folder to simplify routing.
*   **Tutorials:** Specifically reserved for how-to guides or screenshots of YouTube/TikTok tutorials outlining a process. If the image is mainly a walkthrough or lesson, route here and preserve title/creator/URL details when available.
*   **Workflows:** Process diagrams, flowcharts, operational pathways, and workflow references that are not primarily a software product or tutorial. Use this for screenshots or notes whose main value is the process map itself.
*   **Project_Ideas:** Raw project concepts, future build seeds, and idea capture notes that are not yet fully formed into a wiki page or a department-specific plan.
*   **Research:** Competitive analysis, channel studies, benchmark captures, market/product research, and other notes that exist to study or compare something later.
*   **Personal:** Non-business references and personal-interest captures such as concert/tour flyers, lifestyle references, and other non-work bookmarks that do not belong in a business folder.
*   **Videos:** Complete "knowledge packages" for video content. Each video gets its own subfolder (e.g., `Videos/[Descriptive-Name]/`) containing the video file, a transcript markdown file, and future tutorial/screenshot files.

*(Note: "Bookmarks" is not a category. If a file is a bookmark, it must be classified by its topic—Tool, Tutorial, Investment, etc.—and routed accordingly.)*
