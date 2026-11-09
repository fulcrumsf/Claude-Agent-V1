# Etsy-Ikigai Directory

Ikigai Digital Studio Etsy shop (printable digital wall art): docs, the local Portal app and the listing pipeline. Shop notes and rules for agents: `CLAUDE.md`.

## Folders

| Folder | What it holds |
|---|---|
| `Rules_And_Policies/` | Etsy rules and shop policies: `Etsy_Rules_Bible.md` (read before any listing or automation work), `Etsy_Attributes_And_Style_Crosswalk.md` (Etsy wall-art attribute values + Ikigai style crosswalk, read before drafts and the room/style pickers), `Shop_Privacy_Policy.md` |
| `Listing_Templates/` | Listing text and delivery templates: `Description_Template_AI.md`, `Description_Template_Originals.md`, `Digital_Note_To_Buyers.md`, `Download_PDF_Template_Reference.pdf` (git-ignored). Portal setting `listing_templates_dir` |
| `Mockup_Docs/` | Mockup rules and where images live: `Mockup_Style_Guide.md`, `Mockup_Originals_Locations.md`, `Image_Locations.md` |
| `Research/` | Niche and pipeline research: `Niche_Research_Methods.md`, `Prior-Pipeline-Research-Consolidated.md` |
| `Pipeline_Docs/` | Portal and Etsy API plans: `Ikigai_Portal_Pipeline_Brief.md`, `Etsy_API_V3_Application_Plan.md` |
| `Portal/` | Local FastAPI app + listing pipeline (see `Portal/README.md`, `Portal/Directory.md`). Since 2026-11-08: Run upscale + resize also makes listing images 1, 2, 7 + fixed 3-6, 20; the Production tab makes room images 8-19 one card at a time (AI scenes auto-saved as templates in `Room_Templates/`) |
| `Room_Templates/` | Room-mockup templates for listing images 8-19 (catalogue: `Room_Templates/Directory.md`) |
| `Designs/` | One folder per design: `<NNNNN>-<Name>/01-Printables`, `03-Etsy Images` (an `Archive/` subfolder there holds denied, replaced and guard-flagged images and scenes with no usable frame; the Portal shows only its own denied/flagged ones on the cards) |
| `Creative_Inspiration/` | Pinterest style dumps and Style_Profiles |
| `001-Standard Package/`, `002-Includes 1to1 Ratio/` | Git-ignored working copies of the listing mockup sets (originals: `Mockup_Docs/Mockup_Originals_Locations.md`) |

## Move map (2026-11-08)

These files moved from the folder root into subfolders. Older logs and handoffs still show the old paths.

| Old path | New path |
|---|---|
| `Etsy_Rules_Bible.md` | `Rules_And_Policies/Etsy_Rules_Bible.md` |
| `Shop_Privacy_Policy.md` | `Rules_And_Policies/Shop_Privacy_Policy.md` |
| `Description_Template_AI.md` | `Listing_Templates/Description_Template_AI.md` |
| `Description_Template_Originals.md` | `Listing_Templates/Description_Template_Originals.md` |
| `Digital_Note_To_Buyers.md` | `Listing_Templates/Digital_Note_To_Buyers.md` |
| `Download_PDF_Template_Reference.pdf` | `Listing_Templates/Download_PDF_Template_Reference.pdf` |
| `Mockup_Style_Guide.md` | `Mockup_Docs/Mockup_Style_Guide.md` |
| `Mockup_Originals_Locations.md` | `Mockup_Docs/Mockup_Originals_Locations.md` |
| `Image_Locations.md` | `Mockup_Docs/Image_Locations.md` |
| `Niche_Research_Methods.md` | `Research/Niche_Research_Methods.md` |
| `Prior-Pipeline-Research-Consolidated.md` | `Research/Prior-Pipeline-Research-Consolidated.md` |
| `Ikigai_Portal_Pipeline_Brief.md` | `Pipeline_Docs/Ikigai_Portal_Pipeline_Brief.md` |
| `Etsy_API_V3_Application_Plan.md` | `Pipeline_Docs/Etsy_API_V3_Application_Plan.md` |
