# Session Handoff, 2026-11-04, Claude: Ikigai Etsy (rules, packaging, inspiration scan, idea engine design)

Written for the next session. Tony is still in design/brainstorm mode on the Ikigai portal: **nothing in the Portal or `steps.etsy_draft` gets built until Tony says he is ready to build.**

## Read first (in this order)
1. `005_Ecommerce/Etsy-Ikigai/Etsy_API_V3_Application_Plan.md`: the source of truth. Every decision below is recorded there in dated sections (newest at the bottom).
2. `005_Ecommerce/Etsy-Ikigai/Etsy_Rules_Bible.md`: Etsy's AI, listing, digital, automation and EU/UK rules, with ranked risks. Re-pull monthly and before building.
3. `005_Ecommerce/Etsy-Ikigai/Niche_Research_Methods.md`: how experienced sellers find and validate niches (guidance on thinking, not rules).
4. `005_Ecommerce/Etsy-Ikigai/CLAUDE.md` for the project overview and pointers.

## Done this session (all verified unless noted)
- **Etsy policies via API:** the shop already had a full privacy policy and a no-returns/cancellations policy. Added the UK GDPR line and a new date to the privacy policy, and withdrawal wording to both template drafts (checked via API).
- **AI Disclosure wording replaced** on both template drafts (AI Template keeps heading "AI Disclosure"; Originals heading is now "About This Artwork" with its own wording). Saved template files in the project match the live drafts. The Funny Bathroom Portrait (Ducreux) listing was rewritten and the vintage ginkgo listing's artist-name tags were swapped (kuniyoshi and Hokusai replaced by "japanese wall art" and "ginkgo botanical"); both verified live.
- **Etsy Rules Bible** written by a research agent. Key points: Etsy changed AI rules on Oct 22 2026 (per-item human oversight required, disclose AI in description), no bots/scraping on etsy.com, digital files are 5 x 20 MB, etc.
- **Public-domain art:** Tony's position (recorded): Etsy's text never names public domain, so it is a gray area, and curated/restored pieces may fall under Handpicked or Sourced. Agent's assessment: arguable but unconfirmed; Etsy Seller Support has NOT been asked. Pipeline only records what Tony changed per piece.
- **Packaging read from the real 00120 Pastel Waves upload:** PDF template saved at `Etsy-Ikigai/Download_PDF_Template_Reference.pdf` (only the Drive link on the DOWNLOAD button changes; design is fixed). Design folder scaffold, zip contents (5 JPGs + PDF), image slot map (slots 1 to 20), "file number = slot number" naming rule, 1:1 variants (only slots 4 and 5), mockup aspect-ratio rule: all recorded in the plan.
- **Mockup copies:** `001-Standard Package/` and `002-Includes 1to1 Ratio/` copied from iCloud into `Etsy-Ikigai/` (about 1.9 GB, real files not links, git-ignored). Originals' locations are in `Mockup_Originals_Locations.md`.
- **Inspiration scan built and scheduled:** `001_Architecture/Scripts/inspiration_scan.py`, launchd job `com.agent-os.inspiration-scan.plist` runs daily at 03:00. Renames new images in `Creative_Inspiration/` to `0001_<Name>` and so on, writes a style profile per image into the new `Style_Profiles/` folder, and logs to `Rename_Log.md`. 9 images were scanned (0001 to 0009). The first real 3 AM run had not happened yet.
- **Trademark check designed and tested:** USPTO has no name-search API; a real browser ran tmsearch.uspto.gov fine for one phrase. Output will be a traffic-light flag (green, orange, red) plus one line. Composio has an EU-only search tool (Strale). Not built yet.
- **Niche research** done (see file above) and **idea engine design** agreed (below).

## Idea engine and dashboard design agreed
- Stage 1 is a plain table of about 10 one-line, researched ideas with a Rising/Steady/Test tag and Approve/Deny; approved ones go to an idea bank in the same tab. Later stages narrow each approved idea.
- No room-type stage (the art decides rooms). Ideas must be specific and researched with several agreeing sources (Alura, Google Trends, Pinterest, supply data, trademark check), never random. Etsy scraping is banned.
- Tony can add seed ideas by typing in the chat window. Weekly refresh adds about 10 ideas and a refresh-now button; cap 100; scroll window.
- Every approve and deny teaches a taste profile that feeds the research agent. On Deny the dashboard invites an optional comment in the chat.
- The dashboard is chat-driven: a main chat window always open, tabs per area, Ikigai Digital Studio is its own tab (Etsy-specific for now; sales channel swappable), built as a module that plugs into a bigger business dashboard later.
- The 20 prints a week is a relaxed wish, not a requirement.
- A first sample table of 10 ideas was shown from real Alura data and Tony approved the format.

## Not built yet (all gated on Tony's go)
`steps.etsy_draft`, Portal copy buttons and manual-steps checklist, trademark step, idea engine, taste learning, dashboard, packaging code (zip without `__MACOSX`, Drive folder, PDF link swap), mockup generation step, performance tracking (Alura).

## Waiting on Tony / still to confirm
- Which Google account holds the Drive for the download folders (Tony believes Bored Nomad) and the exact Drive folder name (assumed the same as the design folder name).
- The AI Template draft heading still reads "Discloseure" (typo, extra "e"); Tony has not fixed it yet.
- Whether to ask Etsy Seller Support about restored public-domain art (optional; Tony said it is a gray area).
- Where design folders for new prints go inside the project (suggested `005_Ecommerce/Etsy-Ikigai/Designs/`; needs Tony's yes before any folder is created).
- Check that the 3 AM inspiration scan ran (log: `001_Architecture/Scripts/inspiration_scan.log`).
- Remaining main-list items: dashboard, performance tracking, Etsy draft hand-off.

## Uncommitted work (nothing was committed this session)
Modified: `.gitignore`, `Etsy-Ikigai/CLAUDE.md`, `Etsy_API_V3_Application_Plan.md`, `TOOLBOX.md`, `001_Architecture/Scripts/etsy_auth.py`. New: `inspiration_scan.py`, `Rename_Log.md`, `Style_Profiles/`, the two description templates, `Digital_Note_To_Buyers.md`, `Etsy_Rules_Bible.md`, `Mockup_Originals_Locations.md`, `Niche_Research_Methods.md`, `Shop_Privacy_Policy.md`, the PDF template. **Do not `git add` broadly:** the two mockup folders are git-ignored on purpose (1.9 GB). Commit only when Tony asks. The disk was 98% full (about 20 GB free).

## How Tony wants to work (learned today)
- Short answers; yes or no when it is a yes/no. No unrequested logistics, no long paragraphs, no re-explaining what was already done.
- Do the research or look it up (API, files) instead of saying "I'm not sure" or asking for findable info.
- Never turn his examples into rules; think broadly and make ideas your own.
- When he asks to see Etsy's text, copyright limits mean quoting only one short line; point to the section and tell him where to read it. Do not re-fetch Etsy pages with scripts.
- Do exactly the amount asked (two tags means two tags). He edits live Etsy listings himself; read-only API checks afterward confirm.
- Skills: only 1K+ installs, SkillSpector first, never the EverBee wrapper.
- Etsy API access token lasts 1 hour: `python3 001_Architecture/Scripts/etsy_auth.py --name ikigai --refresh`.
