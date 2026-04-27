# 🛠️ ANTI-GRAVITY AGENT — API STACK REFERENCE
**Version:** 1.0  
**Created:** March 20, 2026  
**Purpose:** Master API reference for the Anti-Gravity autonomous video production agent  
**Scope:** All channels (Anomalous Wild, Board Nomad, Neon Parcel, Reimagined Realms, etc.)

---

## ARCHITECTURE OVERVIEW

```
/Video Editor/
  /.env                                ← All API keys
  /references/docs/
    API-STACK-REFERENCE.md             ← This file
    ANOMALOUS-WILD-CHANNEL-BIBLE.md    ← Active
    BOARD-NOMAD-CHANNEL-BIBLE.md       ← Future
    NEON-PARCEL-CHANNEL-BIBLE.md       ← Future
    REIMAGINED-REALMS-CHANNEL-BIBLE.md ← Future
    [api-usage-guides].md              ← API-specific learning guides
  /src/
    ...agent code, Remotion compositions, etc.
```

### Multi-Channel System
Each channel has its own Channel Bible (profile) in `references/docs/`. When the agent receives a task, it reads the relevant Channel Bible for voice, style, content rules, and visual identity.

### Publishing Flow (Future — Blotato)
Each channel maps to a set of Blotato platform IDs:
```
Channel Bible → Agent produces video → Blotato API → routes to correct platform IDs

Anomalous Wild  → YT: BL-xxxx | IG: BL-yyyy | TT: BL-zzzz | FB: BL-wwww
Board Nomad     → YT: BL-aaaa | IG: BL-bbbb | TT: BL-cccc | FB: BL-dddd
Neon Parcel     → YT: BL-eeee | IG: BL-ffff | TT: BL-gggg | FB: BL-hhhh
...
```
> **Note:** Blotato publishing workflow is not yet implemented. IDs will be added to Airtable or a config file when ready.

### Data Layer
| Layer | Tool | Purpose |
|-------|------|---------|
| Structured data | **Airtable** | Video records, performance scores, competitor stats, pipeline state |
| Vector memory | **ChromaDB** (local) | Embeddings of high-performing scripts/hooks for semantic retrieval |

> **Future:** Supabase may be added for Postgres + pgvector + file storage if needs outgrow Airtable + ChromaDB.

---

## ACTIVE APIs — IN .ENV

These API keys are configured and ready to use.

### OpenAI
| Field | Value |
|-------|-------|
| **Purpose** | LLM for script generation, self-evaluation, embeddings |
| **Env var** | `OPENAI_API_KEY` |
| **Docs** | https://platform.openai.com/docs |
| **Models** | `gpt-4o` (reasoning), `text-embedding-3-small` (vectors for ChromaDB) |
| **Rate limits** | Tier-based; see dashboard |
| **Use cases** | Script writing, self-critique loop, embedding generation, JSON structuring |

### Blotato
| Field | Value |
|-------|-------|
| **Purpose** | Multi-platform social media publishing |
| **Env var** | `BLOTATO_API_KEY` |
| **Docs** | https://help.blotato.com/api/start |
| **Base URL** | `https://api.blotato.com/v1` |
| **Status** | Key configured; publishing workflow NOT yet implemented |
| **Use cases** | Post videos/images to YouTube, Instagram, TikTok, Facebook per channel |
| **Note** | Each channel × platform has a unique Blotato ID. IDs will be stored in Airtable or config when ready. |

### Kie.ai (kie.ai)
| Field | Value |
|-------|-------|
| **Purpose** | AI video generation + Suno music generation |
| **Env var** | `KEI_API_KEY` |
| **Docs** | https://kie.ai |
| **Key endpoints** | |

**Video Generation:**
```
POST https://api.kie.ai/v1/generate
Content-Type: application/json
Authorization: Bearer $KEI_API_KEY
```

**Music Generation (Suno V3.5–V5):**
```
POST https://api.kie.ai/v1/generate  (music endpoint)
```
| Feature | Details |
|---------|---------|
| Models | Suno V3.5, V4, V4.5, V5 |
| Max duration | Up to 8 minutes |
| Modes | Simple (text prompt) or Custom (style + title + lyrics) |
| Output | Vocal tracks, instrumentals, stems |
| Extras | Lyrics generation, audio extension, vocal separation, cover generation |

**Use cases:** Wildlife B-roll generation, documentary background music, channel intro music

### Fal.ai
| Field | Value |
|-------|-------|
| **Purpose** | Image generation, video generation, music generation, sound effects |
| **Env var** | `FAL_KEY` |
| **Docs** | https://fal.ai/docs |
| **Python** | `pip install fal-client` |

**Key models for video production:**

| Model | Endpoint | Use Case | Cost |
|-------|----------|----------|------|
| FLUX.1 Schnell | `flux/schnell` | Fast thumbnail/image generation | ~$0.003/image |
| Kling 3.0 Pro | `kling-video/v3/pro/image-to-video` | Cinematic wildlife video from image | Per-second |
| LTX-2.3 | `ltx-video/ltx-2.3` | Text/image/audio to video | Per-second |
| Beatoven Music | `beatoven/music-generation` | Royalty-free instrumental music (up to 2.5 min, 44.1kHz stereo WAV) | Per-generation |
| CassetteAI Music | `cassetteai/music-generator` | Fast music (30s in 2 sec, 3 min in 10 sec) | Per-generation |
| MiniMax Music | `fal-ai/minimax-music` | Music from text + optional reference audio | $0.035/generation |
| Sound Effects | (check fal.ai/explore for latest) | Animal sounds, nature ambience, sci-fi FX | Per-generation |

**Music generation example (Beatoven):**
```python
import fal_client

result = fal_client.subscribe("beatoven/music-generation", arguments={
    "prompt": "Epic cinematic wildlife documentary score, orchestral, building tension",
    "duration": 90,
    "negative_prompt": "vocals, lyrics, electronic, pop"
})
audio_url = result["audio"]["url"]
```

### Perplexity
| Field | Value |
|-------|-------|
| **Purpose** | AI-powered web research and fact verification |
| **Env var** | `PERPLEXITY_API_KEY` |
| **Docs** | https://docs.perplexity.ai |
| **Use cases** | Trending topic discovery, animal fact verification, competitor research, current events |
| **Note** | Use for general research queries. For structured species data, prefer GBIF/Wikidata (see below). |

### Google AI Studio (Gemini)
| Field | Value |
|-------|-------|
| **Purpose** | LLM — script generation, analysis, long-context processing |
| **Env var** | `GOOGLE_AI_STUDIO_API_KEY` |
| **Docs** | https://ai.google.dev |
| **Models** | Gemini 2.0 Flash, Gemini 2.0 Pro |
| **Use cases** | Long-form script drafting, Channel Bible interpretation, multi-step planning |

### Airtable
| Field | Value |
|-------|-------|
| **Purpose** | Structured data storage — video records, scores, pipeline state |
| **Env var** | `AIRTABLE_API_KEY` or `AIRTABLE_PAT` |
| **Docs** | https://airtable.com/developers/web/api |
| **Base URL** | `https://api.airtable.com/v0/{baseId}/{tableName}` |

**Recommended tables:**

| Table | Key Fields | Purpose |
|-------|------------|---------|
| `videos` | video_id, channel, platform, title, publish_date, hook_text, ctr, avg_view_pct, views_24h, engagement_rate, performance_score, score_tier, embedding_id, agent_notes | Central performance database |
| `thumbnails` | thumbnail_id, video_id (link), image_url, variant (A/B/C), ctr, winner | A/B test tracking |
| `competitors` | channel_id, name, platform, subscriber_count, weekly_growth, avg_views_per_video, last_updated | Competitor benchmarks |
| `scripts` | script_id, video_id (link), full_text, hook_text, topic_tags, performance_score, embedding_id | Script archive for vector retrieval |
| `channels` | channel_name, blotato_yt_id, blotato_ig_id, blotato_tt_id, blotato_fb_id, bible_path | Channel registry with Blotato IDs |

### ElevenLabs
| Field | Value |
|-------|-------|
| **Purpose** | Text-to-speech narration |
| **Env var** | `ELEVENLABS_API_KEY` |
| **Docs** | https://elevenlabs.io/docs |
| **Base URL** | `https://api.elevenlabs.io/v1` |

**Voice configuration is per-channel (defined in each Channel Bible).** Example for Anomalous Wild:

| Setting | Value |
|---------|-------|
| Primary voice | Higsley Bishonship |
| Voice ID | `KYhuk3Y57IlkV1ZjtDAt` |
| Model | `eleven_multilingual_v2` or `eleven_turbo_v2_5` |
| Stability | 0.55 |
| Similarity | 0.80 |
| Style | 0.30 |
| Speaker Boost | ON |

```python
import requests

url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
headers = {"xi-api-key": ELEVENLABS_API_KEY}
data = {
    "text": "This animal can recognize your face...",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.55,
        "similarity_boost": 0.80,
        "style": 0.30,
        "use_speaker_boost": True
    }
}
response = requests.post(url, json=data, headers=headers)
# response.content = MP3 audio bytes
```

### Firecrawl
| Field | Value |
|-------|-------|
| **Purpose** | Web data extraction and crawling |
| **Env var** | `FIRECRAWL_API_KEY` |
| **Docs** | https://docs.firecrawl.dev |
| **CLI** | `firecrawl` (installed) |
| **Use cases** | Extract data from websites, scrape public domain image sources, pull Reddit threads, crawl competitor pages |
| **Note** | Complements Perplexity — use Firecrawl for targeted extraction from specific URLs, Perplexity for broad research queries. |

---

## INSTALLED PLUGINS & SKILLS

These are available as Claude Code plugins or CLI tools. No API keys needed — they're authenticated through the plugin system.

| Plugin/Skill | Type | Purpose |
|-------------|------|---------|
| **Remotion** | Skill | React-based video composition — CSS animations, SVG, WebGL, frame-accurate rendering |
| **Cloudinary** | Plugin | Image/video transformation, color grading, CDN delivery |
| **Figma** | Plugin | Design asset extraction |
| **GitHub** | Plugin + CLI | Version control, repo management |
| **Notion** | Plugin | Documentation, knowledge base |
| **Vercel** | Plugin + CLI | Deployment (if dashboards/web tools needed) |
| **Context7** | Plugin | Up-to-date documentation retrieval for libraries |
| **Playwright** | CLI | Browser automation, testing |
| **Firecrawl** | CLI | Web data extraction (also in .env as API) |

---

## NEW APIs TO ADD — FREE

These require setup but have no monthly cost.

### YouTube Data API v3
| Field | Value |
|-------|-------|
| **Purpose** | Search videos, fetch public stats, read comments, find trending content, pull competitor channel data |
| **Env var** | `YOUTUBE_DATA_API_KEY` |
| **Setup** | Enable in Google Cloud Console → APIs & Services → YouTube Data API v3 |
| **Docs** | https://developers.google.com/youtube/v3 |
| **Python** | `pip install google-api-python-client` |
| **Cost** | Free — 10,000 units/day |
| **Auth** | API key (for public data) or OAuth 2.0 (for own channel) |

**Quota costs (plan accordingly):**

| Method | Units | Notes |
|--------|-------|-------|
| `search.list` | **100** | Most expensive — budget ~100 searches/day |
| `videos.list` | 1 | Get stats for known video IDs — very cheap |
| `channels.list` | 1 | Channel metadata and stats |
| `commentThreads.list` | 1 | Read comments |

**Competitor benchmarking example:**
```python
from googleapiclient.discovery import build

youtube = build('youtube', 'v3', developerKey=YOUTUBE_DATA_API_KEY)

# Get public stats for any channel (no auth needed)
response = youtube.channels().list(
    part='statistics,snippet',
    id='UCsXVk37bltHxD1rDPwtNM8Q'  # Kurzgesagt
).execute()

channel = response['items'][0]
stats = channel['statistics']
# stats['subscriberCount'], stats['viewCount'], stats['videoCount']
```

### YouTube Analytics API
| Field | Value |
|-------|-------|
| **Purpose** | Pull YOUR OWN channel performance: CTR, retention, watch time, impressions, subscriber gain |
| **Env var** | Uses OAuth 2.0 tokens (same Google Cloud project as Data API) |
| **Setup** | Enable YouTube Analytics API in Google Cloud Console. Create OAuth 2.0 credentials. Authorize once. |
| **Docs** | https://developers.google.com/youtube/analytics |
| **Python** | `pip install google-api-python-client google-auth-oauthlib` |
| **Cost** | Free — 10,000 units/day |
| **Scopes** | `yt-analytics.readonly`, `yt-analytics-monetary.readonly` (for revenue) |

**Key metrics available:**

| Metric | What It Measures |
|--------|-----------------|
| `estimatedMinutesWatched` | Total watch time — YouTube's strongest ranking signal |
| `averageViewPercentage` | % of video watched per playback |
| `relativeRetentionPerformance` | 0–1 score vs all YouTube videos of similar length (1 = best-in-class) |
| `videoThumbnailImpressionsClickRate` | CTR — driven by title + thumbnail |
| `videoThumbnailImpressions` | Times thumbnail was shown |
| `subscribersGained` | Subs gained from this video |
| `likes`, `comments`, `shares` | Engagement signals |
| `estimatedRevenue` | Ad revenue (requires monetary scope) |

**Example — pull per-video metrics:**
```python
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/yt-analytics.readonly']
flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
credentials = flow.run_local_server(port=0)
yt_analytics = build('youtubeAnalytics', 'v2', credentials=credentials)

response = yt_analytics.reports().query(
    ids='channel==MINE',
    startDate='2026-01-01',
    endDate='2026-03-20',
    metrics='estimatedMinutesWatched,averageViewPercentage,videoThumbnailImpressionsClickRate,subscribersGained',
    dimensions='video',
    filters='video==VIDEO_ID'
).execute()
```

### YouTube Transcript API
| Field | Value |
|-------|-------|
| **Purpose** | Extract subtitles/transcripts from any YouTube video — competitor script analysis |
| **Env var** | None needed — no API key required |
| **Python** | `pip install youtube-transcript-api` |
| **Cost** | Free |
| **Rate limits** | No official limit, but use responsibly |

```python
from youtube_transcript_api import YouTubeTranscriptApi

# Pull transcript from a Kurzgesagt video
transcript = YouTubeTranscriptApi.get_transcript("video_id_here")
full_text = " ".join([entry['text'] for entry in transcript])
# Now embed in ChromaDB or analyze with OpenAI/Gemini
```

**Use cases:** Analyze competitor hooks, study pacing patterns, build a corpus of high-performing scripts for the learning loop.

### Meta Graph API (Instagram Insights)
| Field | Value |
|-------|-------|
| **Purpose** | Pull YOUR OWN Instagram Reels performance: views, reach, saves, shares, skip rate |
| **Env var** | `META_ACCESS_TOKEN` (long-lived token) |
| **Setup** | Create Facebook App → connect Instagram Business/Creator account → generate token |
| **Docs** | https://developers.facebook.com/docs/instagram-platform |
| **Cost** | Free |
| **Rate limits** | 200 calls/hour |
| **Auth** | OAuth 2.0 |
| **Scopes** | `instagram_basic`, `instagram_manage_insights` |

**Key Reels metrics (post-April 2025 migration):**

| Metric | Notes |
|--------|-------|
| `views` | Replaced impressions/plays (unified metric) |
| `reach` | Unique accounts that saw the Reel |
| `engagement` | Likes + comments + saves + shares |
| `saves` | Bookmarks — strong evergreen signal |
| `shares` | Distribution signal |
| `skip_rate` | **NEW 2025** — % of views where user skipped. Direct hook quality metric. |
| `average_minutes_viewed` | Replaced watch time |

```
GET /{ig-media-id}/insights?metric=views,reach,engagement,saves,shares&access_token={TOKEN}
```

### GBIF (Global Biodiversity Information Facility)
| Field | Value |
|-------|-------|
| **Purpose** | Species occurrence records, taxonomic data, distribution maps, conservation status |
| **Env var** | None needed — no API key required |
| **Docs** | https://www.gbif.org/developer/summary |
| **Python** | `pip install pygbif` |
| **Cost** | Free |
| **Records** | 2.5 billion+ species occurrence records |

```python
from pygbif import species, occurrences

# Get structured species data
result = species.name_suggest(q="mantis shrimp")
# Returns: key, scientificName, rank, kingdom, phylum, class, order, family, genus

# Get occurrence records with coordinates
occ = occurrences.search(scientificName="Odontodactylus scyllarus", limit=10)
# Returns: GPS coordinates, country, habitat, recorded date, institution
```

**Use cases:** Populate species name cards, verify taxonomic classifications, generate location overlays for videos, fact-check habitat claims.

### Wikidata
| Field | Value |
|-------|-------|
| **Purpose** | Structured knowledge graph — returns clean JSON with species attributes |
| **Env var** | None needed — no API key required |
| **Docs** | https://www.wikidata.org/wiki/Wikidata:Data_access |
| **Python** | `pip install qwikidata` or use REST API directly |
| **Cost** | Free (CC0 license) |

**One SPARQL query returns structured data:**
```python
import requests

SPARQL_URL = "https://query.wikidata.org/sparql"
query = """
SELECT ?item ?itemLabel ?iucnStatus ?iucnStatusLabel ?diet ?dietLabel ?lifespan ?habitat ?habitatLabel WHERE {
  ?item wdt:P31 wd:Q16521 .       # instance of taxon
  ?item rdfs:label "axolotl"@en .
  OPTIONAL { ?item wdt:P141 ?iucnStatus . }
  OPTIONAL { ?item wdt:P1034 ?diet . }
  OPTIONAL { ?item wdt:P2250 ?lifespan . }
  OPTIONAL { ?item wdt:P2974 ?habitat . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
"""
response = requests.get(SPARQL_URL, params={"query": query, "format": "json"})
data = response.json()["results"]["bindings"]
```

**Returns:** IUCN status, diet, lifespan, habitat, taxonomic hierarchy, linked identifiers — all as structured fields the agent can slot directly into scripts and fact overlays.

### PubMed / NCBI
| Field | Value |
|-------|-------|
| **Purpose** | Search 35M+ peer-reviewed scientific papers on animal behavior and biology |
| **Env var** | `NCBI_API_KEY` (free — get at https://www.ncbi.nlm.nih.gov/account/settings/) |
| **Docs** | https://www.ncbi.nlm.nih.gov/books/NBK25497/ |
| **Python** | `pip install biopython` |
| **Cost** | Free — 10 requests/second with API key (3/sec without) |

```python
from Bio import Entrez

Entrez.email = "your@email.com"
Entrez.api_key = NCBI_API_KEY

# Search for papers on octopus intelligence
handle = Entrez.esearch(db="pubmed", term="octopus intelligence tool use", retmax=5)
results = Entrez.read(handle)
ids = results["IdList"]

# Fetch abstracts
handle = Entrez.efetch(db="pubmed", id=ids, rettype="abstract", retmode="text")
abstracts = handle.read()
```

**Use cases:** Source novel animal facts not yet on Wikipedia, verify claims with primary research, discover obscure behaviors for video topics.

---

## LOCAL TOOLS — NO API KEY

### ChromaDB
| Field | Value |
|-------|-------|
| **Purpose** | Vector database for high-performer memory — semantic retrieval of top scripts/hooks |
| **Install** | `pip install chromadb` |
| **Docs** | https://docs.trychroma.com |
| **Cost** | Free (runs locally) |
| **Storage** | Local disk |

**How it fits the learning loop:**
1. Agent publishes video → collects analytics after 7 days
2. Computes performance score (0–100)
3. If score ≥ 75: embeds script + hook text into ChromaDB with metadata
4. When writing new scripts: queries ChromaDB for similar high-performers
5. Feeds retrieved scripts as context to OpenAI/Gemini for new generation

```python
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_data")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-3-small"
)

collection = client.get_or_create_collection(
    name="high_performer_scripts",
    embedding_function=openai_ef
)

# Store a top-performing script
collection.add(
    documents=["Script text: This animal can recognize your face..."],
    metadatas=[{
        "video_id": "abc123",
        "channel": "anomalous_wild",
        "platform": "youtube",
        "performance_score": 87.5,
        "ctr": 0.072,
        "avg_view_pct": 61.2,
        "topic": "animal_intelligence"
    }],
    ids=["video_abc123"]
)

# Retrieve similar high-performers when writing a new script
results = collection.query(
    query_texts=["deep sea creatures with bioluminescence"],
    n_results=5,
    where={"performance_score": {"$gte": 75}}
)
```

### FFmpeg
| Field | Value |
|-------|-------|
| **Purpose** | Core video/audio processing — encoding, concatenation, filters, format conversion |
| **Install** | Pre-installed or `apt install ffmpeg` / `brew install ffmpeg` |
| **Cost** | Free (LGPL) |
| **Use cases** | Final video assembly, audio mixing, subtitle burn-in, format conversion, glitch effects via filter graphs |

### Remotion (Skill)
| Field | Value |
|-------|-------|
| **Purpose** | React-based programmatic video composition |
| **Type** | Claude Code skill (installed) |
| **Docs** | https://www.remotion.dev/docs |
| **Use cases** | Text animations, motion graphics, kinetic typography, data visualization overlays, lower-thirds, animated fact callouts |
| **Note** | Requires Node.js. Compositions defined in React/TypeScript, rendered to MP4. |

---

## PERFORMANCE SCORING SYSTEM

The agent evaluates each video using a composite weighted score (0–100):

| Metric | Weight | Source API | Benchmark |
|--------|--------|------------|-----------|
| CTR (Click-Through Rate) | 25% | YouTube Analytics API | 4–6% = healthy |
| Average View Percentage | 25% | YouTube Analytics API | 50%+ = strong |
| Views/Hour (24h velocity) | 20% | YouTube Analytics API (calculated) | Channel-specific |
| Engagement Rate | 15% | YouTube Analytics API | 2–5% = strong |
| Relative Retention | 15% | YouTube Analytics API | 0.7+ = top-tier |

```python
def compute_performance_score(metrics: dict) -> float:
    ctr_score = min(metrics['ctr'] / 0.10, 1.0)
    retention_score = metrics['avg_view_pct'] / 100
    velocity_score = min(metrics['views_per_hour_24h'] / 1000, 1.0)
    engagement_score = min(metrics['engagement_rate'] / 0.05, 1.0)
    retention_relative = metrics.get('relative_retention', 0.5)

    score = (
        0.25 * ctr_score +
        0.25 * retention_score +
        0.20 * velocity_score +
        0.15 * engagement_score +
        0.15 * retention_relative
    ) * 100

    return round(score, 1)
```

**Score tiers:**
- **75–100:** Top performer → embed in ChromaDB, use as template reference
- **50–74:** Average → analyze for improvement opportunities
- **0–49:** Underperformer → run LLM self-evaluation, identify failure points

---

## LEARNING LOOP — 7-DAY CYCLE

After every video reaches 7-day maturity (when metrics stabilize):

1. **Collect** — Pull metrics from YouTube Analytics API (and Meta Graph API for Reels)
2. **Score** — Compute performance score using weighted formula above
3. **Store** — Update Airtable `videos` table with scores; update `scripts` table
4. **Embed** — If score ≥ 75, embed script + hook into ChromaDB with metadata
5. **Evaluate** — Run LLM self-evaluation: compare this video vs top performers from ChromaDB
6. **Learn** — Store `agent_notes` in Airtable; feed into next script generation as context
7. **Benchmark** — Pull competitor stats via YouTube Data API; update `competitors` table

---

## FUTURE INTEGRATIONS

These are planned but not yet configured:

| Integration | Purpose | Status |
|-------------|---------|--------|
| **Blotato publishing workflow** | Automated multi-channel posting with platform-specific IDs | Key in .env; routing workflow not built |
| **Supabase** | Postgres + pgvector + file storage — potential Airtable supplement or replacement | Under consideration |
| **TikTok Business API** | Own channel TikTok analytics (views, engagement, demographics) | Will add when TikTok becomes a priority |
| **Reddit API (PRAW)** | Trending topics from wildlife subreddits (r/NatureIsFuckingLit, r/interestingasfuck) | Free but requires pre-approval — apply when ready |
| **Google Trends (pytrends)** | Trending search interest for topic timing | Free but unreliable (429 errors); SerpApi fallback available |

---

## ENV TEMPLATE

```bash
# === LLMs ===
OPENAI_API_KEY=sk-...
GOOGLE_AI_STUDIO_API_KEY=AI...
PERPLEXITY_API_KEY=pplx-...

# === Video & Media Generation ===
FAL_KEY=...
KEI_API_KEY=...

# === Voice ===
ELEVENLABS_API_KEY=...

# === Publishing ===
BLOTATO_API_KEY=...

# === Data & Storage ===
AIRTABLE_PAT=pat...

# === Web Research ===
FIRECRAWL_API_KEY=fc-...

# === YouTube (Google Cloud — same project) ===
YOUTUBE_DATA_API_KEY=AI...
# YouTube Analytics uses OAuth tokens, not API key — see setup instructions above

# === Instagram ===
META_ACCESS_TOKEN=EAA...

# === Scientific Data ===
NCBI_API_KEY=...
# GBIF — no key needed
# Wikidata — no key needed
# youtube-transcript-api — no key needed

# === Local (no keys) ===
# ChromaDB — runs locally, no key
# FFmpeg — system tool, no key
# Remotion — installed skill, no key
```

---

## QUICK REFERENCE — ALL TOOLS BY CATEGORY

| Category | Tool | Type | Cost |
|----------|------|------|------|
| **LLM** | OpenAI (GPT-4o) | API (.env) | Pay-per-token |
| **LLM** | Google AI Studio (Gemini) | API (.env) | Free tier + paid |
| **LLM** | Perplexity | API (.env) | Subscription |
| **Video Gen** | Kei.ai | API (.env) | Pay-per-use |
| **Video Gen** | Fal.ai | API (.env) | Pay-per-use |
| **Video Composition** | Remotion | Skill (local) | Free |
| **Video Processing** | FFmpeg | CLI (local) | Free |
| **Narration** | ElevenLabs | API (.env) | Pay-per-character |
| **Music Gen** | Kei.ai (Suno V3.5–V5) | API (.env) | Pay-per-use |
| **Music Gen** | Fal.ai (Beatoven/CassetteAI/MiniMax) | API (.env) | Pay-per-use |
| **Image/Video Processing** | Cloudinary | Plugin | Free tier + paid |
| **Thumbnail Gen** | Fal.ai (FLUX) + Cloudinary | API + Plugin | Pay-per-use |
| **Publishing** | Blotato | API (.env) | Subscription |
| **Structured Data** | Airtable | API (.env) | Free tier + paid |
| **Vector Memory** | ChromaDB | Local | Free |
| **Web Research** | Perplexity | API (.env) | Subscription |
| **Web Extraction** | Firecrawl | API + CLI (.env) | Pay-per-use |
| **YouTube Research** | YouTube Data API v3 | API (.env) | Free |
| **YouTube Analytics** | YouTube Analytics API | OAuth | Free |
| **Competitor Scripts** | youtube-transcript-api | Python lib | Free |
| **Instagram Analytics** | Meta Graph API | OAuth | Free |
| **Species Data** | GBIF | REST (no key) | Free |
| **Species Data** | Wikidata | REST (no key) | Free |
| **Scientific Papers** | PubMed/NCBI | API (.env) | Free |
| **Design** | Figma | Plugin | — |
| **Docs** | Notion | Plugin | — |
| **Deployment** | Vercel | Plugin + CLI | — |
| **Version Control** | GitHub | Plugin + CLI | — |
| **Browser Automation** | Playwright | CLI | Free |
| **Docs Lookup** | Context7 | Plugin | — |
