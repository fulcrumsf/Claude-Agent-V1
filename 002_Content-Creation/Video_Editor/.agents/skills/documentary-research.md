---
description: Asset research and sourcing skill for documentary-style videos. Searches archive.org (public domain footage/film), Openverse API (CC0/public domain images and audio), and other free sources to find real archival footage, historical photos, maps, newspaper scans, and ambient audio. Activated when a script, beat sheet, or storyboard contains historical events, real locations, real people, or any scene that calls for archival or documentary-style assets. Works in conjunction with the storytelling skill and channel bibles.
trigger: Script or story outline contains historical events, real places, real people, documentary style, archival footage, newspaper zooms, old maps, or any scene that calls for real-world visual reference material.
---

# Skill: Documentary & Archival Asset Research

Use this skill when a script or beat sheet needs real-world archival assets: footage, photographs, newspaper scans, maps, or ambient audio. Do NOT use this for AI-generated video or purely animated content — only trigger when the script explicitly calls for real historical/documentary material.

---

## When to Activate This Skill

Activate automatically when a script, scene description, or beat sheet contains:
- References to historical events (wars, space race, political events, disasters)
- Real geographic locations described in a documentary or journalistic way
- Real people (historical figures, public figures)
- Newspaper zooms, archival photo montages, old map reveals
- Vox-style documentary beats: slow push-ins on documents, photo cutouts that animate
- Nature documentary with specific real locations ("the Serengeti in 1972...")
- True crime with real locations or timeline visuals
- "Historical context" scene — any beat where the production needs to show "what it was like"

Do NOT activate for: fully AI-generated videos, animated explainers with no real-world reference, cat/pet content with no historical angle.

---

## Research Pipeline

When activated, run these steps in order:

### Step 1 — Parse the Script for Asset Needs

Read the script/beat sheet and extract every scene that needs a real-world asset. For each scene, identify:

```
Scene [N]: [brief description]
Asset type: footage | photo | newspaper | map | audio | illustration
Era/date: [approximate date range or "present day"]
Location: [country / region / city if relevant]
Subject: [person, event, topic keywords]
Style note: [e.g. "Vox-style newspaper cutout", "slow push-in", "split-screen"]
```

Group scenes by asset type — footage scenes get searched on archive.org, images on Openverse, audio on Openverse audio.

---

### Step 2 — archive.org Search (Footage & Film)

**Base URL:** `https://archive.org/search`

**Public domain filter query format:**
```
mediatype:movies licenseurl:*publicdomain* [your keywords]
```

**Direct search URL:**
```
https://archive.org/search?query=mediatype%3Amovies+licenseurl%3A*publicdomain*+[URL-encoded keywords]
```

**Example searches:**
| Goal | Search URL |
|------|-----------|
| WWII newsreel footage | `https://archive.org/search?query=mediatype%3Amovies+licenseurl%3A*publicdomain*+world+war+2+newsreel` |
| 1960s US civil rights | `https://archive.org/search?query=mediatype%3Amovies+licenseurl%3A*publicdomain*+civil+rights+1960s` |
| Space race footage | `https://archive.org/search?query=mediatype%3Amovies+licenseurl%3A*publicdomain*+NASA+space+race+1960s` |
| Old map animation material | `https://archive.org/search?query=mediatype%3Amovies+licenseurl%3A*publicdomain*+historical+map` |

**Additional archive.org collections for documentary content:**
| Collection ID | Content |
|--------------|---------|
| `prelinger` | Prelinger Archives — American industrial/educational films (CC license) |
| `moviesandfilms` | General video archive |
| `newsandpublicaffairs` | News broadcasts and public affairs programming |
| `opensource_movies` | Explicitly open-source licensed films |
| `ephemera` | Advertising films, government PSAs, training films |

**Collection-scoped search URL:**
```
https://archive.org/search?query=collection:[collection_id]+[keywords]
```

**Download links:** Once a specific item is found, download URLs follow this pattern:
```
https://archive.org/download/[identifier]/[filename.ext]
```
Use `https://archive.org/metadata/[identifier]` to get JSON metadata including all available file formats.

**File format notes:**
- Prefer `.mp4` or `.mpeg` downloads
- If only `.ogv` is available: convert with FFmpeg:
  ```bash
  ffmpeg -i input.ogv -c:v libx264 -c:a aac output.mp4
  ```

---

### Step 3 — Openverse API Search (Images & Audio)

Openverse indexes 800M+ openly-licensed works. Use for: historical photos, newspaper scans, illustrations, maps, ambient/period audio.

**Base URL:** `https://api.openverse.org/v1/`

**Auth:** Pre-registered OAuth2 credentials available in `~/.mcp-secrets.env`:
```bash
OPENVERSE_API_KEY_CLIENT_ID=<registered_client_id>
OPENVERSE_API_KEY_CLIENT_SECRET=<registered_client_secret>
```

**Automatic token exchange (at runtime):**
```python
import requests
import os

def get_openverse_token() -> str:
    """Exchange client credentials for bearer token (12h expiry)"""
    client_id = os.getenv("OPENVERSE_API_KEY_CLIENT_ID")
    client_secret = os.getenv("OPENVERSE_API_KEY_CLIENT_SECRET")
    
    resp = requests.post(
        "https://api.openverse.org/v1/auth_tokens/token/",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
    )
    resp.raise_for_status()
    return resp.json()["access_token"]
```

No manual registration needed — credentials are pre-registered to the "Uno Mas Video Editor" application.

**Image Search:**
```bash
GET https://api.openverse.org/v1/images/?q=[keywords]&license_type=commercial&page_size=20
```

Key parameters:
| Parameter | Value | Notes |
|-----------|-------|-------|
| `q` | keyword string | Max 200 chars |
| `license` | `cc0,pdm` | Public domain only (cc0 = Creative Commons Zero, pdm = Public Domain Mark) |
| `license_type` | `commercial,modification` | Allows any reuse including commercial |
| `source` | `flickr,wikimedia,rawpixel` | Optionally filter to specific sources |
| `page_size` | `20` | Default; max depends on auth level |

**Python example — authenticated image search:**
```python
import requests
import os

def search_openverse_images(query: str, license_filter: str = "cc0,pdm", page_size: int = 20) -> list:
    """Search Openverse images using pre-registered credentials"""
    # Get bearer token from pre-registered credentials
    client_id = os.getenv("OPENVERSE_API_KEY_CLIENT_ID")
    client_secret = os.getenv("OPENVERSE_API_KEY_CLIENT_SECRET")
    
    token_resp = requests.post(
        "https://api.openverse.org/v1/auth_tokens/token/",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
    )
    token = token_resp.json()["access_token"]
    
    # Search with authenticated bearer token
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        "https://api.openverse.org/v1/images/",
        headers=headers,
        params={
            "q": query,
            "license": license_filter,
            "page_size": page_size,
            "filter_dead": True
        }
    )
    resp.raise_for_status()
    return resp.json().get("results", [])

# Example: search for 1940s Berlin street photos
results = search_openverse_images("1940s Berlin city street")
for item in results:
    print({
        "title": item["title"],
        "creator": item.get("creator"),
        "license": item["license"],
        "url": item["url"],           # direct image URL
        "source": item["source"],
        "foreign_landing_url": item["foreign_landing_url"],  # attribution page
        "width": item.get("width"),
        "height": item.get("height"),
    })
```

**Audio Search (ambient sound, period music, sound effects):**
```bash
GET https://api.openverse.org/v1/audio/?q=[keywords]&license=cc0,pdm&category=music
```

Audio category values: `audiobook`, `music`, `news`, `podcast`, `pronunciation`, `sound_effect`

**Good audio search queries for documentary use:**
| Goal | Query |
|------|-------|
| 1940s radio broadcast feel | `q=radio+1940s&category=music&license=cc0` |
| Ambient crowd / street noise | `q=street+crowd+ambient&category=sound_effect&license=cc0` |
| Nature documentary score | `q=orchestral+nature+documentary&category=music&license=cc0` |
| Old film grain / projector sound | `q=film+projector+reel&category=sound_effect&license=cc0` |

---

### Step 3b — Multi-Source Search Strategy for Swappable Assets

**Philosophy:** Do not select a single asset and move on. Instead, search MULTIPLE sources for each scene's needs and return ALL viable candidates. This enables:
1. **Automated pipeline:** Recommends a primary choice for Remotion composition
2. **Manual override:** If the final video scores below 100/100, editor can swap in alternatives from the manifest without re-rendering

**Source prioritization based on quality rating:**

Reference: `references/docs/PUBLIC_DOMAIN_SOURCES_RATING.md` contains a comprehensive 1-10 rating of all public domain and CC-licensed sources. Use the Tier system below:

| Asset Type | Tier 1 (Always Query) | Tier 2 (If Needed) | Tier 3 (Fallback) | Goal |
|-----------|---|---|---|---|
| **Historical Footage** | archive.org (7/10) | Pexels video (9/10) | Pixabay video (8/10) | 3+ clips per scene |
| **Historical Photos** | Wikimedia Commons (8/10) | Library of Congress (8/10) | Openverse (7/10) | 4+ images per scene |
| **Newspaper/Documents** | Chronicling America (6/10) | Europeana (7/10) | Trove (6/10) | 3+ different angles/dates |
| **Maps/Cartography** | David Rumsey (6/10) | Library of Congress (8/10) | Old Maps Online | 2+ regional variants |
| **Ambient Audio** | Openverse audio (7/10) | Pexels audio | YouTube Audio Library | 2+ mood variants |
| **Nature/Wildlife** | NASA (9/10) | Wikimedia Commons (8/10) | GBIF (avoid — licensing metadata unreliable) | 3+ variants |
| **Contemporary Visuals** | Pexels (9/10) | Pixabay (8/10) | Coverr (6/10) | 3+ options per scene |

**Search protocol:**
1. **Start with Tier 1** sources for your asset type
2. **If fewer than 3 viable candidates found**, query Tier 2
3. **If still insufficient**, query Tier 3
4. **Never query GBIF** for automated pipeline (use only if manually verified)

**For EACH scene's asset need, search all applicable sources and collect candidates.** Update the asset manifest to list all matches, not just one. The final manifest should show sources_searched and all candidates with ratings/recommendations.

---

### Step 4 — Additional Sources by Content Type

Use these when archive.org and Openverse don't have what you need.

**For historical photographs:**
| Source | URL Pattern | Notes |
|--------|-------------|-------|
| Library of Congress | `https://www.loc.gov/search/?q=[keywords]&fo=json` | Massive US history archive, free |
| NASA Image Library | `https://images.nasa.gov/search-results?q=[keywords]` | All NASA images public domain |
| Wikimedia Commons | `https://commons.wikimedia.org/w/index.php?search=[keywords]&ns6=1` | Free media, check license per item |
| Rawpixel Public Domain | `https://www.rawpixel.com/search/[keywords]?sort=curated&mode=shop&page=1` | Curated PD art + vintage illustrations |
| New York Public Library Digital | `https://digitalcollections.nypl.org/search/index?utf8=✓&keywords=[keywords]` | Maps, photos, prints |

**For newspaper/document zooms (Vox-style):**
| Source | URL | Notes |
|--------|-----|-------|
| Chronicling America (LOC) | `https://chroniclingamerica.loc.gov/search/pages/results/?andtext=[keywords]` | US newspapers 1770–1963, free |
| Europeana | `https://www.europeana.eu/en/search?query=[keywords]` | European cultural heritage, mixed licenses |
| Trove (Australia) | `https://trove.nla.gov.au/newspaper/result?q=[keywords]` | Australian newspapers, mostly free |

**For maps:**
| Source | Notes |
|--------|-------|
| David Rumsey Map Collection | `https://www.davidrumsey.com/luna/servlet/RUMSEY~8~1?q=[keywords]` — free for non-commercial, check license |
| Old Maps Online | `https://www.oldmapsonline.org/?q=[keywords]` — aggregator |
| LOC Geography & Maps | `https://www.loc.gov/maps/?q=[keywords]` — public domain US maps |

**For nature/geographic footage (not archive.org):**
| Source | Notes |
|--------|-------|
| Pexels (video) | `https://www.pexels.com/search/videos/[keywords]/` — free license, attribution not required |
| Pixabay (video) | `https://pixabay.com/videos/search/[keywords]/` — CC0 |
| Coverr | `https://coverr.co/search?q=[keywords]` — free for commercial |

---

### Step 5 — Output Asset Manifest (Multi-Source, Swappable Assets)

After researching, write a structured asset manifest to the project folder. This file serves two purposes:
1. **Automated pipeline:** Provides primary choice (`"recommended": true`) for Remotion composition
2. **Manual override:** Stores all candidates so editor can swap assets in Final Cut Pro if needed

**Output path:** `references/outputs/[video-id]/asset-manifest.json`

**Format with multiple candidates per source:**
```json
{
  "video_id": "0003-Space-Race",
  "researched_at": "2026-03-21T00:00:00Z",
  "philosophy": "Multi-source swappable assets — candidates organized for both automated pipeline and manual FCP/Premiere override",
  "scenes": [
    {
      "scene_id": 1,
      "description": "Sputnik launch — Soviet satellite enters orbit",
      "duration_seconds": 5,
      "asset_type": "footage",
      "sources_searched": ["archive.org", "pexels_video", "pixabay_video"],
      "candidates": [
        {
          "source": "archive.org",
          "title": "View From Space (1963)",
          "identifier": "view-from-space-1963",
          "url": "https://archive.org/download/view-from-space-1963/view_from_space.mp4",
          "landing_url": "https://archive.org/details/view-from-space-1963",
          "license": "public domain",
          "duration_seconds": 180,
          "recommended": true,
          "segment": "0:45–1:20",
          "notes": "Rocket launch exterior shot, clear footage, high contrast"
        },
        {
          "source": "archive.org",
          "title": "Soviet Space Program Documentary (1960)",
          "identifier": "soviet-space-doc-1960",
          "url": "https://archive.org/download/soviet-space-doc-1960/soviet_space.mp4",
          "landing_url": "https://archive.org/details/soviet-space-doc-1960",
          "license": "public domain",
          "duration_seconds": 420,
          "recommended": false,
          "segment": "12:30–12:50",
          "notes": "Longer context, shows facility prep, lower contrast"
        },
        {
          "source": "pexels_video",
          "title": "Rocket Launch Animation (Generic)",
          "url": "https://videos.pexels.com/...",
          "license": "cc0",
          "duration_seconds": 8,
          "recommended": false,
          "notes": "AI-generated style, less historical feel but clean visuals"
        }
      ],
      "remotion_treatment": "cut_segment"
    },
    {
      "scene_id": 2,
      "description": "Newspaper headline zoom — Sputnik announcement",
      "duration_seconds": 3,
      "asset_type": "newspaper_image",
      "sources_searched": ["chroniclingamerica.loc.gov", "europeana", "trove"],
      "candidates": [
        {
          "source": "chroniclingamerica.loc.gov",
          "title": "New York Times front page, Oct 5 1957",
          "url": "https://chroniclingamerica.loc.gov/...",
          "landing_url": "https://chroniclingamerica.loc.gov/...",
          "license": "public domain",
          "recommended": true,
          "crop_region": "header to subheader",
          "notes": "Iconic headline, clear legible text, high contrast"
        },
        {
          "source": "chroniclingamerica.loc.gov",
          "title": "Washington Post, Oct 5 1957",
          "url": "https://chroniclingamerica.loc.gov/...",
          "landing_url": "https://chroniclingamerica.loc.gov/...",
          "license": "public domain",
          "recommended": false,
          "crop_region": "full masthead + headline",
          "notes": "Alternative US perspective, slightly smaller headline"
        },
        {
          "source": "europeana",
          "title": "Pravda Soviet newspaper, Oct 5 1957",
          "url": "https://www.europeana.eu/...",
          "landing_url": "https://www.europeana.eu/...",
          "license": "public domain",
          "recommended": false,
          "crop_region": "masthead + top story",
          "notes": "Soviet perspective, Cyrillic text, historical contrast"
        }
      ],
      "remotion_treatment": "vox_newspaper_cutout"
    },
    {
      "scene_id": 3,
      "description": "Ambient music — Cold War tension underscore",
      "duration_seconds": 45,
      "asset_type": "audio",
      "sources_searched": ["openverse", "pexels_audio", "youtube_audio_library"],
      "candidates": [
        {
          "source": "openverse",
          "title": "Tension Suite No.3",
          "creator": "Kevin MacLeod",
          "url": "https://api.openverse.org/...",
          "landing_url": "https://freepd.com/...",
          "license": "cc0",
          "duration_seconds": 120,
          "recommended": true,
          "segment": "0:00–0:45",
          "notes": "Orchestral, builds slowly, perfect pacing for narration"
        },
        {
          "source": "openverse",
          "title": "Suspenseful Strings",
          "creator": "Benjamin Tissot",
          "url": "https://api.openverse.org/...",
          "license": "cc0",
          "duration_seconds": 180,
          "recommended": false,
          "segment": "0:15–1:00",
          "notes": "Faster tempo, more dramatic, good alternative if pacing feels slow"
        },
        {
          "source": "youtube_audio_library",
          "title": "Cold Dawn (Sci-Fi Ambient)",
          "url": "https://www.youtube.com/audio_library/...",
          "license": "free to use",
          "duration_seconds": 240,
          "recommended": false,
          "segment": "0:00–0:45",
          "notes": "Electronic/synth blend, more modern feel"
        }
      ],
      "remotion_treatment": "background_audio_ducked"
    }
  ],
  "ai_generated_needed": [
    {
      "scene_id": 4,
      "description": "Baikonur Cosmodrome interior",
      "reason": "No public domain footage of facility interior — generate with kie.ai",
      "suggested_prompt": "Soviet rocket facility interior 1957, brutalist concrete architecture, dramatic low angle lighting, cinematic"
    }
  ],
  "usage_in_pipeline": {
    "automated_remotion": "Remotion uses candidates marked 'recommended: true' for video composition",
    "manual_override": "If video scores below 100/100, editor can swap to alternative candidates from this manifest in Final Cut Pro using the provided URLs",
    "fcpxml_swap_workflow": "Export FCPXML from Remotion → open in FCP → replace clips using URLs from 'candidates' array → re-export"
  }
}
```

**Key changes for swappable asset strategy:**
- **`sources_searched` array:** Lists all sources queried for this scene
- **`recommended` flag:** Single true per scene; others false (but still valuable)
- **Multiple candidates per source:** All viable matches included, not just one
- **`remotion_treatment`:** Guides how asset gets animated in Remotion
- **`usage_in_pipeline` section:** Documents both automated AND manual override workflows

**Always include an `ai_generated_needed` array** — if real footage can't be found, flag it so the AI generation pipeline knows to fill the gap.

---

## Integration with Other Skills

This skill feeds into the broader video production pipeline:

```
storytelling skill         →  script with beats/scenes
                                    ↓
documentary-research skill →  asset-manifest.json
                                    ↓
kie.ai / fal.ai APIs       →  AI-generated gap-fill assets
                                    ↓
Remotion + FFmpeg           →  final video assembly
```

**Coordinate with channel bible:** Before searching, check the relevant channel bible for:
- Visual style (Vox-style newspaper cutouts? Gritty archival? Clean modern doc?)
- Content restrictions (some channels are family-safe — avoid war footage gore)
- Preferred aspect ratio (affects which footage formats to prioritize)

**Flag for Remotion/Vox-style treatment:** When an asset is a newspaper scan, old photo, or map, add a `remotion_treatment` note:
```json
"remotion_treatment": "vox_newspaper_cutout | slow_zoom | ken_burns | parallax | cutout_walk"
```
These treatments get implemented in Remotion compositions where the static image is animated — the asset manifest tells Remotion what style to apply.

---

## Practical API Reference

**Openverse image search (Python):**
```python
import requests

def search_openverse_images(query: str, license_filter: str = "cc0,pdm", page_size: int = 20) -> list:
    resp = requests.get(
        "https://api.openverse.org/v1/images/",
        params={"q": query, "license": license_filter, "page_size": page_size, "filter_dead": True}
    )
    resp.raise_for_status()
    return resp.json().get("results", [])

# Public domain images of 1960s Berlin
images = search_openverse_images("Berlin 1960s street", license_filter="cc0,pdm")
```

**archive.org metadata fetch (Python):**
```python
import requests

def get_archive_metadata(identifier: str) -> dict:
    resp = requests.get(f"https://archive.org/metadata/{identifier}")
    resp.raise_for_status()
    return resp.json()

def get_archive_download_url(identifier: str, preferred_format: str = "mp4") -> str | None:
    metadata = get_archive_metadata(identifier)
    files = metadata.get("files", [])
    for f in files:
        if f.get("format", "").lower() == preferred_format or f.get("name", "").endswith(f".{preferred_format}"):
            return f"https://archive.org/download/{identifier}/{f['name']}"
    return None
```

**archive.org search API (programmatic, not just URL):**
```python
import requests

def search_archive_public_domain(keywords: str, media_type: str = "movies", rows: int = 10) -> list:
    query = f"mediatype:{media_type} licenseurl:*publicdomain* {keywords}"
    resp = requests.get(
        "https://archive.org/advancedsearch.php",
        params={
            "q": query,
            "fl[]": ["identifier", "title", "description", "mediatype", "licenseurl"],
            "rows": rows,
            "output": "json"
        }
    )
    resp.raise_for_status()
    return resp.json().get("response", {}).get("docs", [])
```

---

### Step 4b — GBIF: Species Data, Distribution Maps & Historical Occurrence Records

Use GBIF when the script involves a specific animal species, geographic range, historical distribution, or ecology. GBIF gives you two things that are directly useful for Remotion: **species data for name cards/lower-thirds**, and **map tile images showing where a species has been found**.

**No API key required** for search and maps. Bulk occurrence downloads require a free GBIF account.

**Env vars (only needed for bulk downloads):**
```bash
GBIF_USERNAME=your_gbif_username
GBIF_PASSWORD=your_gbif_password
```

---

#### Quick Species Lookup (no auth — use for scripts and name cards)

```python
from pygbif import species, occurrences

# Step 1: Get the taxon key for a species
matches = species.name_suggest(q="mantis shrimp")
taxon_key = matches[0]["key"]  # e.g. 2440447

# Step 2: Get structured taxonomy
info = species.name_usage(key=taxon_key)
# Returns: scientificName, kingdom, phylum, class, order, family, genus, species

# Step 3: Get occurrence records (GPS, country, date, habitat)
occ = occurrences.search(taxonKey=taxon_key, limit=20, hasCoordinate=True)
records = occ["results"]
# Each record: decimalLatitude, decimalLongitude, country, year, basisOfRecord
```

**Remotion use — species name card data:**
```python
def get_species_card_data(common_name: str) -> dict:
    matches = species.name_suggest(q=common_name)
    if not matches:
        return {}
    key = matches[0]["key"]
    info = species.name_usage(key=key)
    return {
        "common_name": common_name,
        "scientific_name": info.get("scientificName", ""),
        "family": info.get("family", ""),
        "order": info.get("order", ""),
        "class": info.get("class", ""),
        "kingdom": info.get("kingdom", ""),
        "taxon_key": key
    }
# Output feeds directly into Remotion lower-third / name card components
```

---

#### GBIF Maps API — Distribution Map Images (no auth)

This is the most useful GBIF feature for video production. It generates species distribution map tile images showing every recorded location for a species — ready to embed in Remotion as an image overlay.

**Base URL:** `https://api.gbif.org/v2/map/occurrence/density/{z}/{x}/{y}@1x.png`

**Static map image (for Remotion background):**
```
https://api.gbif.org/v2/map/occurrence/density/0/0/0@2x.png?taxonKey=2440447&style=purpleYellow.point&bin=hex
```

Parameters:
| Parameter | Options | Notes |
|-----------|---------|-------|
| `taxonKey` | integer | From species lookup above |
| `style` | `purpleYellow.point`, `green.point`, `fire.point`, `classic.point` | Visual style of the dots |
| `bin` | `hex`, `square` | Clustering method |
| `resolution` | `1`, `2`, `4` | Map resolution |
| `srs` | `EPSG:4326` (default), `EPSG:3857` | Coordinate system |

**Full-world PNG map for a species (for Remotion):**
```python
import requests

def download_species_map(taxon_key: int, output_path: str, style: str = "purpleYellow.point") -> str:
    # Zoom level 0 = full world map
    url = f"https://api.gbif.org/v2/map/occurrence/density/0/0/0@2x.png"
    params = {
        "taxonKey": taxon_key,
        "style": style,
        "bin": "hex",
        "resolution": 2
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(resp.content)
    return output_path

# Example: download mantis shrimp distribution map
download_species_map(
    taxon_key=2440447,
    output_path="references/outputs/0003-Mantis-Shrimp/assets/distribution_map.png"
)
```

The saved PNG drops directly into Remotion as a static image with `staticFile()` — apply a Ken Burns slow zoom or animated dot-reveal overlay in the composition.

---

#### Historical Occurrence Search (no auth — use for date-filtered research)

For documentary scripts that need "where was this species in 1950" type data:

```python
from pygbif import occurrences

# Occurrences in Africa between 1900–1960
results = occurrences.search(
    taxonKey=2440447,
    continent="AFRICA",
    year="1900,1960",          # range: comma-separated min,max
    hasCoordinate=True,
    limit=50
)

# Filter by country
results_kenya = occurrences.search(
    taxonKey=2440447,
    country="KE",              # ISO 2-letter country code
    hasCoordinate=True,
    limit=20
)
```

Key search parameters:
| Parameter | Example | Notes |
|-----------|---------|-------|
| `taxonKey` | `2440447` | From species.name_suggest() |
| `country` | `"KE"`, `"US"`, `"DE"` | ISO 2-letter code |
| `continent` | `"AFRICA"`, `"EUROPE"`, `"ASIA"` | Continent filter |
| `year` | `"1900,1960"` | Date range (min,max) |
| `hasCoordinate` | `True` | Only records with GPS |
| `basisOfRecord` | `"PRESERVED_SPECIMEN"`, `"HUMAN_OBSERVATION"` | Record type |
| `geometry` | WKT polygon string | Filter to a specific geographic region |

---

#### Bulk Occurrence Download (requires GBIF account — use for large datasets)

For large historical datasets (thousands of records), use the async download API. Requires registration at gbif.org and credentials in `.env`.

```python
import requests
import time
import os

GBIF_USER = os.getenv("GBIF_USERNAME")
GBIF_PASS = os.getenv("GBIF_PASSWORD")

def request_gbif_download(taxon_key: int, country: str = None, year_min: int = None, year_max: int = None) -> str:
    predicates = [{"type": "equals", "key": "TAXON_KEY", "value": str(taxon_key)}]
    if country:
        predicates.append({"type": "equals", "key": "COUNTRY", "value": country})
    if year_min:
        predicates.append({"type": "greaterThanOrEquals", "key": "YEAR", "value": str(year_min)})
    if year_max:
        predicates.append({"type": "lessThanOrEquals", "key": "YEAR", "value": str(year_max)})

    payload = {
        "creator": GBIF_USER,
        "notificationAddresses": [],
        "sendNotification": False,
        "format": "SIMPLE_CSV",
        "predicate": {"type": "and", "predicates": predicates}
    }
    resp = requests.post(
        "https://api.gbif.org/v1/occurrence/download/request",
        json=payload,
        auth=(GBIF_USER, GBIF_PASS)
    )
    resp.raise_for_status()
    return resp.text.strip('"')  # returns download key

def poll_gbif_download(download_key: str, max_wait: int = 300) -> str:
    """Poll until SUCCEEDED, return download URL."""
    for _ in range(max_wait // 10):
        resp = requests.get(f"https://api.gbif.org/v1/occurrence/download/{download_key}")
        data = resp.json()
        status = data.get("status")
        if status == "SUCCEEDED":
            return data["downloadLink"]
        elif status == "FAILED":
            raise RuntimeError(f"GBIF download failed: {data}")
        time.sleep(10)
    raise TimeoutError("GBIF download timed out")
```

**Supported predicate filters for bulk downloads:**
- `equals`, `in`, `and`, `or`, `not` — standard logic
- `lessThan` / `greaterThan` / `lessThanOrEquals` / `greaterThanOrEquals` — for YEAR, ELEVATION
- `within` — WKT polygon for exact geographic boundary
- `geoDistance` — radius from a lat/lon point (e.g., `"5km"`)
- `isNull` / `isNotNull` — check for empty fields

---

#### GBIF Asset Output for the Manifest

When GBIF provides data for a scene, add it to the asset manifest like this:

```json
{
  "scene_id": 5,
  "description": "Species distribution map — mantis shrimp global range",
  "asset_type": "distribution_map",
  "source": "gbif_maps_api",
  "taxon_key": 2440447,
  "species": "Odontodactylus scyllarus",
  "map_url": "https://api.gbif.org/v2/map/occurrence/density/0/0/0@2x.png?taxonKey=2440447&style=purpleYellow.point",
  "local_path": "references/outputs/0003-Mantis-Shrimp/assets/distribution_map.png",
  "selected": true,
  "remotion_treatment": "slow_zoom",
  "notes": "Full-world distribution. Animate with 8s Ken Burns push-in. Overlay species name card."
},
{
  "scene_id": 6,
  "description": "Species taxonomy — lower-third name card data",
  "asset_type": "species_data",
  "source": "gbif_species_api",
  "data": {
    "common_name": "Mantis Shrimp",
    "scientific_name": "Odontodactylus scyllarus",
    "family": "Odontodactylidae",
    "order": "Stomatopoda",
    "class": "Malacostraca"
  },
  "remotion_treatment": "lower_third_name_card"
}
```

---

## Common Mistakes to Avoid

- **Don't search archive.org without the `licenseurl:*publicdomain*` filter** — you'll get copyrighted content that looks free but isn't
- **Don't assume all Openverse results are fully free** — always check `license` field. `cc0` and `pdm` = fully public domain. `by` = requires attribution. `by-nc` = no commercial use.
- **Always verify file format before downloading** — many archive.org items only have `.ogv`; convert to `.mp4` with FFmpeg
- **Log every source used** — even public domain assets need attribution notes in the manifest for legal clarity
- **Flag gaps for AI generation** — it's better to note "no asset found" and generate with kie.ai/fal.ai than to use a copyrighted asset
- **Consider the channel style** — a Vox-style newspaper cutout is a different deliverable than raw footage; the Remotion treatment is as important as the asset itself
