---
Created: 2025-10-22T17:03
---
Here’s a streamlined, non-overlapping instruction set for Rube’s Etsy head‑term research.
**Objective**
Identify niche “head terms” (the first tokens buyers type before printable/poster/download) for Etsy printable wall art. Return only the head term concepts, plus Category and a qualitative 0–100 Score.
**Ideal Scope (But not limited to)**
- Styles: Minimalist, Mid‑Century, Japandi, Nordic/Scandi, Botanical, Bathroom Humor, Food & Drinks, Vintage Travel, Frame TV.
- Categories (rooms/placement): Bathroom, Kitchen, Laundry, Bar Cart, Nursery, Living Room, Office, Bedroom, Entry, Frame TV.
**Search Criteria**
- Use intersectional phrases (2–4 words) that imply style, motif, or colorway.
- Favor head terms that recur across multiple relevant listings but are not saturated with near-identical titles.
- Exclude broad/generic words alone: abstract, vintage, nature, typography, travel.
Examples to model:
- Style × motif: Nordic folk floral; Norwegian folk bird; Japandi reeds; atomic starburst; Bauhaus portrait; wine woman; sage botanical; gouache organic shapes.
- Style × colorway: Scandi floral monochrome; Japandi wave green; mid‑century geometric sorbet; neutral abstract.
- Humor × room: funny bathroom rating; minimalist bathroom joke; toilet paper renaissance.
**How to Search on Etsy**
- Build queries as: Token + buyer‑intent suffix (add “digital download”, “wall art”, “instant download”, “art print”, or “poster” to the search phrase).
- Include Category in the search only if it’s intrinsic to the Token’s intent (e.g., “Bathroom Humor Art”). Otherwise treat Category separately (e.g., Token: “Japandi floral print”; Category: “Living Room”).
- Use best‑selling sort.
Query examples:
- “retro maze abstract wall art” → [https://www.etsy.com/search?q=retro+maze+abstract+wall+art&sort_by=best_selling ↗](https://www.etsy.com/search?q=retro+maze+abstract+wall+art&sort_by=best_selling)
- “bathroom humor wall art” → [https://www.etsy.com/search?q=bathroom+humor+wall+art&sort_by=best_selling ↗](https://www.etsy.com/search?q=bathroom+humor+wall+art&sort_by=best_selling)
**Validation Cues**
- Demand: multiple active listings with consistent style/motif; room/color qualifiers present; modern thumbnails/palettes.
- Competition: many near‑identical titles from large shops; overly broad phrasing; dated/cluttered novelty results.
**Output Format**
Write each result as: [Token] [Category] [Score]
- Token: niche head term (no “printable,” “poster,” or “download” in the Token itself).
- Category: room/placement context from the scope list.
- Score: 0–100, higher = stronger buyer intent with lower competition.
**Scoring Guidance**
- Raise score for clear room intent (bathroom/kitchen/laundry/bar cart/nursery), colorway specificity (neutral/muted/monochrome/sage/olive/sorbet/pastel), and evident demand without saturation.
- Lower score for generic breadth, heavy duplication in titles/thumbnails, or dated aesthetics.
- Ranges: 80–100 high intent/low competition; 60–79 solid; 40–59 mixed; <40 weak/broad.
**Examples (apply rules)**
- Token: Nordic folk floral; Category: Living Room; Score: 80.
- Token: Japandi kitchen reeds; Category: Kitchen; Score: 90.
- Token: Atomic starburst square; Category: Living Room; Score: 85.
- Token: Minimalist bathroom joke; Category: Bathroom; Score: 95.
- Token: Wine woman line art; Category: Bar Cart; Score: 75.
- Token: Scandi flower monochrome; Category: Nursery; Score: 70.