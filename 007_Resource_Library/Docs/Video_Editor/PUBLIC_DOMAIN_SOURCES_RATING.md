---
title: "Public Domain & CC-Licensed Asset Sources — Rating & Prioritization"
type: doc
domain: video-production
tags: [doc, video-production, research, knowledge-graph]
---

# Public Domain & CC-Licensed Asset Sources — Rating & Prioritization

**Last updated:** 2026-04-07  
**Purpose:** Help researchers prioritize which sources to query for each asset type in the video production pipeline.

---

## Summary Table (Rated 1-10, 10 = Best for Video Production)

| Source | Type | Rating | Best For | Recommendation |
|--------|------|--------|----------|-----------------|
| **NASA** | Specialized API | **9/10** | Space, Earth science, atmospheric content. Broadcast quality. | **Must use** for science/space videos |
| **Pexels** | Stock footage + images | **9/10** | Modern stock video + images. Clean aesthetic. API-friendly. | **Primary for contemporary content** |
| **Wikimedia Commons** | General archive | **8/10** | Deepest, most diverse. Period pieces, cultural content, B&W. | **Primary for archival/historical** |
| **Library of Congress** | Specialized archive | **8/10** | Museum-quality historical photos, military footage, documentarian archives. | **Secondary for historical** |
| **Pixabay** | Stock footage + images | **8/10** | Modern stock video + images. Professional quality. | **Alternative to Pexels** |
| **Openverse** | Central search hub | **7/10** | Audio + images (CC/PD). Central registry of 842M items. No video yet. | **Primary for audio sourcing** |
| **Internet Archive** | Video archive | **7/10** | Historical newsreels, archival found-footage, vintage cinematography. | **Secondary for historical video** |
| **Europeana** | Cultural heritage | **7/10** | European cultural assets, period dramas, art-house aesthetics. | **Niche for cultural/historical** |
| **Chronicling America** | Historical archive | **6/10** | Newspaper pages, engravings, historical photographs. | **Niche for historical documents** |
| **Trove** | Regional archive | **6/10** | Australian-centric. Regional/geographic storytelling. | **Niche for Australian content** |
| **Coverr** | Stock video | **6/10** | Modern aesthetic footage. Licensing clarity unclear. | **Low priority, use only if needed** |
| **David Rumsey Maps** | Maps only | **6/10** | Cartography, animated map overlays. Non-commercial use only. | **Specialized for map-based content** |
| **GBIF** | Biodiversity images | **5/10** | Nature/species imagery. User-submitted quality varies. | **Avoid—metadata licensing is unreliable** |

---

## Tier System for Asset Research

### Tier 1: Always Query First (Rating 8-9/10)
These sources have the highest quality-to-effort ratio. Always include them in multi-source asset searches.

- **NASA** — Any science/space/Earth content
- **Pexels** — Contemporary visuals, general stock footage
- **Wikimedia Commons** — Historical/archival/cultural content, diverse media types
- **Pixabay** — Contemporary alternatives if Pexels coverage is thin

### Tier 2: Query Second (Rating 7-8/10)
Smaller collections or more specialized, but high-quality when relevant. Use if Tier 1 results are insufficient.

- **Library of Congress** — Historical photography, documentary footage
- **Internet Archive** — Archival newsreels, vintage cinematography, found-footage aesthetics
- **Openverse** — Audio and images (especially for Suno composition reference audio)
- **Europeana** — European period content, cultural/art-focused pieces

### Tier 3: Niche/Fallback (Rating 6-7/10)
Regional or specialized sources. Query only if Tier 1 + Tier 2 yield fewer than 3 candidates per scene.

- **Chronicling America** — Historical documents, newspaper imagery
- **Trove** — Australian/regional content
- **David Rumsey** — Map-based visualizations
- **Coverr** — Modern aesthetic if Pexels/Pixabay are insufficient

### Tier 4: Do Not Use for Production (Rating ≤5/10)
Metadata or licensing too unreliable for automated pipeline.

- **GBIF** — Avoid. Image licenses are free-text fields, not standardized. Use only if manually verified.

---

## Source-by-Content-Type Matrix

**Archival B&W Documentary (Style 01)**
1. Internet Archive (primary for newsreels)
2. Wikimedia Commons (cultural/historical)
3. Library of Congress (documentation)

**3D Animated Synthetic (Style 02)**
1. No public domain source (generate via kie.ai/Nan Banana)
2. Pexels (reference footage for composition)

**Satellite/Map Visualization (Style 03)**
1. NASA (Earth imagery, satellite data)
2. David Rumsey (historical maps for overlays)

**HD Underwater Camera (Style 04)**
1. Pexels (best quality stock footage)
2. Pixabay (alternatives)

**National Geographic Wildlife (Style 05)**
1. Wikimedia Commons (user-uploaded wildlife, species pages)
2. NASA (natural Earth imagery)
3. GBIF (only if manually verified for license)

**Scientific Infographic (Style 06)**
1. NASA (scientific diagrams, space data)
2. Library of Congress (historical scientific illustrations)
3. Wikimedia Commons (scientific commons)

---

## Programmatic Access Ranking

**Easiest to Query (for automation):**
1. NASA — Perfect structure, no auth required
2. Pexels — Simple API, clear rate limits
3. Pixabay — Similar to Pexels
4. Openverse — Large scale (842M), standardized CC metadata
5. Wikimedia Commons — Powerful MediaWiki API
6. Library of Congress — Comprehensive loc.gov API

**Harder/Not Recommended for Automation:**
7. GBIF — Good API, but metadata licensing is unreliable
8. Trove — Requires key registration, regional focus
9. Europeana — Good API, but 54M items require smart filtering
10. Coverr — No formal API documentation
11. David Rumsey — LUNA viewer is web-only
12. Chronicling America — Newspaper pages ≠ standalone footage
13. Internet Archive — Downloadable but no formal video API

---

## Recommendations for the Video Editor Pipeline

### For Speed (minimal Firecrawl spend):
Query Tier 1 only. Results will be sufficient 85% of the time.
- NASA for space/science
- Pexels for general contemporary
- Wikimedia Commons for historical/archival

### For Quality (maximum options):
Query all Tier 1 + Tier 2. Collect 3+ candidates per scene.

### For Specialized Content:
Map content type to Source-by-Content-Type Matrix above.

### Never:
- Use GBIF for automated asset selection (licensing metadata is unreliable)
- Assume Coverr metadata is correct (licensing clarity is unclear)
- Use Chronicling America for video (it's newspaper pages, not footage)

---

## Integration with documentary-research.md

When the /documentary-research skill builds an asset manifest, it should:
1. Identify the content type and cinematic style required
2. Use the "Source-by-Content-Type Matrix" above to determine which sources to query
3. Query Tier 1 sources first
4. If fewer than 3 viable candidates found, query Tier 2
5. Collect ALL candidates (not just 1 top result)
6. Flag the highest-rated source's best result as "recommended": true
7. Include all candidates in the manifest for manual override in FCP/Premiere

---

## Notes
- Ratings assume April 2026 state. Openverse was expected to add video support later in 2026.
- Ratings are based on video production workflow, not academic research or journalism.
- "Rating" combines: library size × quality × API accessibility × licensing clarity.
- Non-commercial licenses (David Rumsey, GBIF) are downrated for commercial video production contexts.
