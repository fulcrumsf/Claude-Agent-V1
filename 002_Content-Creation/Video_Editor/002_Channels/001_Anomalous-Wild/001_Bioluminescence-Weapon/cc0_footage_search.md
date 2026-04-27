# CC0 Footage Search List — Bioluminescence Weapon

Check these sources BEFORE generating AI footage for marked scenes.

---

## Priority CC0 Sources

| Source | URL | Notes |
|---|---|---|
| MBARI YouTube | youtube.com/@MBARI_News | All footage listed as free for education/non-commercial use. Deep-sea, dinoflagellates, anglerfish, siphonophore. |
| Wikimedia Commons | commons.wikimedia.org | Search: "bioluminescence", "anglerfish", "bobtail squid", "dinoflagellate" |
| NOAA Ocean Service | oceanservice.noaa.gov/facts | Public domain video footage |
| NASA/JPL Image Gallery | images.nasa.gov | All NASA imagery is public domain — use for Europa/Jupiter scene |
| Internet Archive | archive.org | Search "bioluminescence ocean" — historical documentary clips |
| Prelinger Archives | archive.org/details/prelinger | CC0 documentary footage |

---

## Scene-by-Scene Search Queries

### scene_03 — Ocean descent
- MBARI: "deep sea descent footage 4K"
- Wikimedia: "mesopelagic bioluminescence"
- Search: "ocean water column depth footage CC0"

### scene_04 — Dinoflagellates (Sea Sparkle)
- MBARI: "dinoflagellate bioluminescence"
- Wikimedia: "Noctiluca scintillans bioluminescence"
- Search: "sea sparkle bioluminescent waves beach night footage"
- **High probability of CC0 availability** — this footage is widely shared

### scene_07 — Anglerfish
- MBARI: "anglerfish deep sea" — MBARI has confirmed anglerfish footage
- Wikimedia: "Melanocetus johnsonii"
- Search: "anglerfish bioluminescent lure footage public domain"
- **Medium probability** — rare close-up macro may need AI

### scene_10b — Siphonophore
- MBARI: "siphonophore" — MBARI has documented siphonophore footage
- Wikimedia: "Praya dubia siphonophore"
- **High probability** — MBARI specifically filmed siphonophores

### scene_11 (partial) — Europa/Jupiter
- NASA Images: "Europa moon", "Jupiter system"
- All NASA imagery = **confirmed public domain**
- Search nasa.gov/images for "Europa ocean" and "Jupiter system"

---

## Download Instructions

For each found CC0 clip:
1. Download to `inputs/cc0_footage/bioluminescence_weapon/[scene_id]/`
2. Rename to `video_raw.mp4`
3. Update `beat_sheet.json` → set `asset_source: "cc0_found"` and `ai_prompt_needed: false`
4. Note the source URL in the scene notes field

---

## Fallback Rule

If CC0 footage exists but quality is < 720p or footage angle doesn't match the required shot type → use AI generation instead. Document the CC0 source in notes even if not used (for attribution records).
