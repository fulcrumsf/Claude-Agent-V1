#!/usr/bin/env python3
"""
Model Catalog Refresh — runs monthly via cron (1st of month, 3am).

What it does:
  1. Refreshes pricing for all 24 models across all platforms (only updates changed values)
  2. Runs web search for community consensus ratings on models without scores or with stale scores
  3. Detects newly deprecated models via API metadata and community signals
  4. Writes updated model_catalog.json
  5. Syncs to Airtable

Sources:
  - kie.ai: pricing_cache.json (already maintained by pricing_refresh.py)
  - WaveSpeed: wavespeed CLI (wavespeed price <model_id>)
  - fal.ai: REST API via fal-client
  - Google: public pricing page
  - OpenAI: pricing_cache.json
  - ElevenLabs: plan known ($5/mo, 30K chars)
  - Ratings: Perplexity API web search
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
CATALOG_FILE = DATA_DIR / "model_catalog.json"
PRICING_CACHE = DATA_DIR / "pricing_cache.json"

# ── API Keys ───────────────────────────────────────────────────────────────────
def get_env(key):
    val = os.environ.get(key)
    if not val:
        # Try sourcing ~/.env-secrets inline
        result = subprocess.run(
            ["bash", "-c", f"source ~/.env-secrets 2>/dev/null && echo ${key}"],
            capture_output=True, text=True
        )
        val = result.stdout.strip()
    return val or None

FAL_AI_API_KEY = get_env("FAL_AI_API_KEY")
PERPLEXITY_API_KEY = get_env("PERPLEXITY_API_KEY")
AIRTABLE_API_KEY = get_env("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = get_env("AIRTABLE_BASE_ID")
WAVESPEED_API_KEY = get_env("WAVESPEED_API_KEY")

# ── Airtable Config ────────────────────────────────────────────────────────────
AIRTABLE_TABLE_NAME = "Model Catalog"

# ── Helpers ────────────────────────────────────────────────────────────────────
def load_catalog():
    with open(CATALOG_FILE) as f:
        return json.load(f)

def save_catalog(catalog):
    catalog["_meta"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    next_month = datetime.now().replace(day=1) + timedelta(days=32)
    catalog["_meta"]["next_refresh"] = next_month.replace(day=1, hour=3, minute=0, second=0).isoformat()
    with open(CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=2)
    print(f"✅ Catalog saved: {CATALOG_FILE}")

def run(cmd, capture=True):
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True,
                            env={**os.environ, "WAVESPEED_API_KEY": WAVESPEED_API_KEY or ""})
    return result.stdout.strip() if capture else None

# ── 1. WaveSpeed Pricing ───────────────────────────────────────────────────────
def fetch_wavespeed_price(model_id):
    """Run wavespeed price <model_id> and parse the output."""
    if not model_id:
        return None
    output = run(f"source ~/.env-secrets && wavespeed price '{model_id}' 2>/dev/null")
    # Parse dollar amounts from output
    import re
    match = re.search(r'\$([0-9]+\.[0-9]+)', output)
    if match:
        return float(match.group(1))
    return None

def refresh_wavespeed_prices(catalog):
    print("\n[WaveSpeed] Refreshing prices...")
    changed = 0
    for model in catalog["models"]:
        ws = model["pricing"].get("wavespeed")
        if not ws or not isinstance(ws, dict):
            continue
        model_id = ws.get("model_id")
        if not model_id or ws.get("price") is not None:
            continue  # Already have price, skip unless forced
        price = fetch_wavespeed_price(model_id)
        if price is not None:
            ws["price"] = price
            changed += 1
            print(f"  ✓ {model['id']}: WaveSpeed ${price}")
    print(f"  {changed} WaveSpeed prices updated")
    return changed

# ── 2. kie.ai Pricing (from existing pricing_cache.json) ──────────────────────
def refresh_kieai_prices(catalog):
    print("\n[kie.ai] Refreshing prices from pricing_cache.json...")
    if not PRICING_CACHE.exists():
        print("  ⚠ pricing_cache.json not found — skipping kie.ai")
        return 0

    with open(PRICING_CACHE) as f:
        cache = json.load(f)
    kieai_services = cache.get("apis", {}).get("kie.ai", {}).get("services", {})

    changed = 0
    for model in catalog["models"]:
        ki = model["pricing"].get("kie_ai")
        if not ki or not isinstance(ki, dict):
            continue
        model_id = ki.get("model_id")
        if not model_id:
            continue
        service = kieai_services.get(model_id)
        if service and service.get("price") is not None:
            old_price = ki.get("price")
            new_price = float(service["price"])
            if old_price != new_price:
                ki["price"] = new_price
                ki["unit"] = service.get("unit", ki.get("unit"))
                changed += 1
                print(f"  ✓ {model['id']}: kie.ai ${new_price} ({model_id})")
    print(f"  {changed} kie.ai prices updated")
    return changed

# ── 3. fal.ai Pricing ─────────────────────────────────────────────────────────
def fetch_fal_price(model_id):
    """Fetch fal.ai pricing via the Platform API pricing endpoint. Retries once on 429."""
    if not FAL_AI_API_KEY or not model_id:
        return None, None
    import urllib.request, urllib.parse, urllib.error, time
    url = f"https://api.fal.ai/v1/models/pricing?endpoint_id={urllib.parse.quote(model_id)}"
    headers = {"Authorization": f"Key {FAL_AI_API_KEY}"}
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                prices = data.get("prices", [])
                if prices:
                    p = prices[0]
                    return p["unit_price"], p["unit"]
                return None, None
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            return None, None
        except Exception:
            return None, None
    return None, None

def refresh_fal_prices(catalog):
    import time
    print("\n[fal.ai] Refreshing prices...")
    changed = 0
    for model in catalog["models"]:
        fal = model["pricing"].get("fal_ai")
        if not fal or not isinstance(fal, dict):
            continue
        model_id = fal.get("model_id")
        if not model_id:
            continue
        time.sleep(1.5)
        price, unit = fetch_fal_price(model_id)
        if price is not None:
            old_price = fal.get("price")
            fal["price"] = price
            fal["unit"] = unit
            if old_price != price:
                changed += 1
                print(f"  ✓ {model['name']}: ${price}/{unit}  (was ${old_price})")
            else:
                print(f"  = {model['name']}: ${price}/{unit}  (unchanged)")
        else:
            print(f"  – {model['name']} ({model_id}): no pricing via API")
    print(f"  {changed} fal.ai prices updated")
    return changed

# ── 4. OpenAI Pricing (from pricing_cache.json) ───────────────────────────────
def refresh_openai_prices(catalog):
    print("\n[OpenAI] Refreshing prices from pricing_cache.json...")
    if not PRICING_CACHE.exists():
        return 0

    with open(PRICING_CACHE) as f:
        cache = json.load(f)
    openai_services = cache.get("apis", {}).get("openai", {}).get("services", {})

    changed = 0
    for model in catalog["models"]:
        oai = model["pricing"].get("openai_direct")
        if not oai or not isinstance(oai, dict):
            continue
        model_id = oai.get("model_id")
        if not model_id:
            continue
        service = openai_services.get(model_id)
        if service and service.get("price") is not None:
            old_price = oai.get("price")
            new_price = float(service["price"])
            if old_price != new_price:
                oai["price"] = new_price
                changed += 1
                print(f"  ✓ {model['id']}: OpenAI direct ${new_price}")
    print(f"  {changed} OpenAI prices updated")
    return changed

# ── 5. Update Cheapest Route ───────────────────────────────────────────────────
PLATFORM_PREFERENCE_ORDER = [
    "google_direct", "elevenlabs_direct", "openai_direct",
    "kie_ai", "wavespeed", "fal_ai", "openrouter"
]
DIRECT_PLATFORMS = {"google_direct", "elevenlabs_direct", "openai_direct"}

# Multipliers to normalize raw prices to the reference unit for each pricing type.
# "per second" video prices are multiplied by 5 (5-second reference clip).
# "per video" and "per image" prices are used as-is.
UNIT_NORMALIZERS = {
    # "per X" prefixed — used by kie.ai and WaveSpeed
    "per second": 5.0,
    "per 5s": 1.0,
    "per video": 1.0,
    "per image": 1.0,
    "per 1K image": 1.0,
    "per 1000 characters": 1.0,
    "per 1K chars": 1.0,
    "per second of output": 1.0,
    "per generation request": 1.0,
    "per request": 1.0,
    "per 10s video processed": 1.0,
    "per unit": 1.0,
    "per call": 1.0,
    "per generation": 1.0,
    # Bare forms — returned by fal.ai Platform API (no "per " prefix)
    "seconds": 5.0,      # matches "seconds" and "compute seconds" via substring
    "videos": 1.0,
    "images": 1.0,
    "units": 1.0,
}

def normalize_price(entry):
    """Return a comparable normalized price for routing. Free (0.00) counts as cheapest."""
    if not isinstance(entry, dict):
        return None
    price = entry.get("price")
    if price is None:
        return None
    price = float(price)
    unit = entry.get("unit", "").lower()
    # Apply multiplier based on unit type
    for unit_key, multiplier in UNIT_NORMALIZERS.items():
        if unit_key in unit:
            return price * multiplier
    # Default: use price as-is (unknown unit)
    return price

def update_cheapest_route(catalog):
    print("\n[Routing] Recalculating cheapest routes...")
    for model in catalog["models"]:
        pricing = model["pricing"]
        candidates = []
        for platform in PLATFORM_PREFERENCE_ORDER:
            entry = pricing.get(platform)
            if not isinstance(entry, dict):
                continue
            norm_price = normalize_price(entry)
            if norm_price is None:
                continue  # Skip missing prices; 0.00 (free) is valid and counts
            candidates.append((platform, norm_price))

        if not candidates:
            continue

        cheapest_platform, cheapest_price = min(candidates, key=lambda x: x[1])

        # Prefer direct API if within 5% of cheapest
        for platform, price in candidates:
            if platform in DIRECT_PLATFORMS and price <= cheapest_price * 1.05:
                cheapest_platform = platform
                cheapest_price = price
                break

        old_cheapest = pricing.get("cheapest")
        pricing["cheapest"] = cheapest_platform
        pricing["cheapest_price"] = cheapest_price
        pricing["last_compared"] = datetime.now().strftime("%Y-%m-%d")

        if old_cheapest != cheapest_platform:
            print(f"  ↻ {model['id']}: {old_cheapest} → {cheapest_platform} (${cheapest_price})")

# ── 6. Community Ratings via Perplexity ───────────────────────────────────────
def fetch_rating(model_name, model_type):
    """Query Perplexity for community consensus rating."""
    if not PERPLEXITY_API_KEY:
        return None, []

    prompt = (
        f"Based on Reddit, YouTube, and Twitter/X reviews and benchmarks, "
        f"what is the community consensus quality rating for the AI model '{model_name}' "
        f"({model_type})? Rate it on a scale of 1-10 where 10 is best-in-class. "
        f"Reply with ONLY: a number (e.g. 8.5) followed by a comma and the sources you found "
        f"(e.g. reddit,youtube). If insufficient data, reply: null,none"
    )

    try:
        import urllib.request
        payload = json.dumps({
            "model": "sonar",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 50
        }).encode()
        req = urllib.request.Request(
            "https://api.perplexity.ai/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"].strip()
            parts = text.split(",", 1)
            rating_str = parts[0].strip()
            sources = [s.strip() for s in parts[1].split(",")] if len(parts) > 1 else []
            if rating_str.lower() == "null":
                return None, []
            return float(rating_str), [s for s in sources if s and s != "none"]
    except Exception as e:
        print(f"    ⚠ Perplexity error: {e}")
        return None, []

def refresh_ratings(catalog, force=False):
    print("\n[Ratings] Refreshing community consensus scores...")
    if not PERPLEXITY_API_KEY:
        print("  ⚠ PERPLEXITY_API_KEY not set — skipping ratings")
        return 0

    changed = 0
    for model in catalog["models"]:
        # Skip if already rated and not forced
        if model.get("rating") is not None and not force:
            continue
        # Skip models explicitly marked as new with no data expectation
        if model.get("status") == "new" and model.get("rating_label") == "new – insufficient data":
            print(f"  – {model['id']}: skipping (new model, no community data yet)")
            continue

        print(f"  Searching: {model['name']} ({model['type']})...")
        rating, sources = fetch_rating(model["name"], model["type"])

        if rating is not None:
            model["rating"] = rating
            model["rating_label"] = "scored"
            model["rating_sources"] = sources
            model["rating_updated"] = datetime.now().strftime("%Y-%m-%d")
            changed += 1
            print(f"  ✓ {model['id']}: {rating}/10 ({', '.join(sources)})")
        else:
            model["rating"] = None
            model["rating_label"] = "no community data"
            model["rating_updated"] = datetime.now().strftime("%Y-%m-%d")
            print(f"  – {model['id']}: no community data found")

    print(f"  {changed} ratings updated")
    return changed

# ── 7. Discovery — New Top-Tier Models ────────────────────────────────────────
def discover_new_models():
    """One monthly search for new top-tier AI video/image/audio models."""
    if not PERPLEXITY_API_KEY:
        return []

    prompt = (
        "What are the top NEW AI video, image generation, or audio generation models "
        "released or significantly updated in the past 30 days? List only models that "
        "have strong community reception (Reddit, YouTube, Twitter). "
        "Format: one per line as: MODEL_NAME | PROVIDER | TYPE (text-to-video etc) | brief reason it's notable"
    )

    try:
        import urllib.request
        payload = json.dumps({
            "model": "sonar",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400
        }).encode()
        req = urllib.request.Request(
            "https://api.perplexity.ai/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"].strip()
            print(f"\n[Discovery] New models this month:\n{text}\n")
            return text
    except Exception as e:
        print(f"  ⚠ Discovery search failed: {e}")
        return []

# ── 8. Airtable Sync ───────────────────────────────────────────────────────────

PLATFORM_DISPLAY_NAMES = {
    "google_direct":     "Google Direct",
    "elevenlabs_direct": "ElevenLabs Direct",
    "openai_direct":     "OpenAI Direct",
    "kie_ai":            "kie.ai",
    "wavespeed":         "WaveSpeed",
    "fal_ai":            "fal.ai",
    "openrouter":        "OpenRouter",
}

def _norm_price_for_display(entry):
    """Return normalized price (per 5s clip equivalent) for a platform entry."""
    if not isinstance(entry, dict):
        return None
    p = entry.get("price")
    if p is None:
        return None
    p = float(p)
    unit = entry.get("unit", "").lower()
    for unit_key, multiplier in UNIT_NORMALIZERS.items():
        if unit_key in unit:
            return p * multiplier
    return p

def _norm_price_str(entry):
    """Format normalized price for Airtable cell. Returns 'X' if unavailable."""
    norm = _norm_price_for_display(entry)
    if norm is None:
        return "X"
    if norm == 0.0:
        return "$0.00 (free)"
    # Trim trailing zeros but keep at least 2 decimal places
    formatted = f"{norm:.4f}".rstrip("0")
    if formatted.endswith("."):
        formatted += "00"
    elif len(formatted.split(".")[-1]) < 2:
        formatted += "0"
    return f"${formatted}"

def _raw_rates_str(pricing):
    """Build human-readable raw rates string showing price + unit per platform."""
    parts = []
    for platform, label in PLATFORM_DISPLAY_NAMES.items():
        entry = pricing.get(platform)
        if not isinstance(entry, dict):
            continue
        p = entry.get("price")
        if p is None:
            continue
        unit = entry.get("unit", "")
        if float(p) == 0.0:
            parts.append(f"{label}: free")
        elif unit:
            parts.append(f"{label}: ${p}/{unit}")
        else:
            parts.append(f"{label}: ${p}")
    return " · ".join(parts) if parts else "no pricing data"

def _fmt_price(price, unit):
    """Format a per-unit price for display: '$0.31/s', '$0.02/img', etc."""
    if price is None:
        return "X"
    if price == 0.0:
        return "$0.00 (sub)"
    suffix = unit.lstrip("$").strip() if unit else ""
    formatted = f"{price:.4f}".rstrip("0")
    if formatted.endswith("."):
        formatted += "00"
    elif len(formatted.split(".")[-1]) < 2:
        formatted += "0"
    return f"${formatted}/{suffix}" if suffix else f"${formatted}"

def sync_to_airtable(catalog):
    """Sync one Airtable record per variant (resolution × audio). Price columns
    show the actual per-second or per-image cost for that variant.
    Uses batch upsert (10 records per API call) to minimise public API usage."""
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("\n[Airtable] ⚠ Missing credentials — skipping sync")
        return

    print("\n[Airtable] Syncing catalog by variant (batched)...")
    import urllib.request, urllib.error

    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    def airtable_batch_upsert(records_fields):
        """Send up to 10 records per call using Airtable batch upsert."""
        from urllib.parse import quote
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{quote(AIRTABLE_TABLE_NAME, safe='')}"
        payload = json.dumps({
            "records": [{"fields": f} for f in records_fields],
            "performUpsert": {"fieldsToMergeOn": ["Row ID"]}
        }).encode()
        req = urllib.request.Request(url, data=payload, headers=headers, method="PATCH")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            print(f"  ⚠ Airtable batch upsert: {e.code} {e.read().decode()[:200]}")
            return None

    all_records = []

    for model in catalog["models"]:
        if model.get("status") == "inactive":
            continue

        variants = model.get("variants", [])
        if not variants:
            continue

        for variant in variants:
            vid = variant.get("variant_id", "default")
            row_id = f"{model['id']}_{vid}"
            price_unit = variant.get("price_unit", "$/s")
            unit_suffix = price_unit.lstrip("$/").strip()

            res = variant.get("resolution", "N/A")
            audio = variant.get("audio", "N/A")
            if res != "N/A" and audio not in ("N/A",):
                audio_label = "Audio" if audio == "Yes" else "No Audio"
                variant_label = f"{res} · {audio_label}"
            elif res != "N/A":
                variant_label = res
            else:
                variant_label = "—"

            cp = variant.get("cheapest")
            cv = variant.get("cheapest_price")
            if cp and cv is not None:
                cp_display = PLATFORM_DISPLAY_NAMES.get(cp, cp)
                if cv == 0.0:
                    cheapest_label = f"{cp_display} (free)"
                else:
                    cv_str = f"{cv:.4f}".rstrip("0").rstrip(".")
                    cheapest_label = f"{cp_display} (${cv_str}/{unit_suffix})"
            else:
                cheapest_label = "—"

            def vprice(platform):
                v = variant.get(platform)
                return _fmt_price(v, unit_suffix)

            display_name = (
                f"{model['name']} ({variant_label})"
                if res != "N/A" else model["name"]
            )

            all_records.append({
                "Row ID":             row_id,
                "Model ID":           model["id"],
                "Name":               display_name,
                "Variant":            variant_label,
                "Resolution":         res,
                "Audio":              audio,
                "Price Unit":         price_unit,
                "Provider":           model.get("provider", ""),
                "Type":               model["type"],
                "Input/Output":       model.get("input_output", ""),
                "Description":        model.get("description", ""),
                "Status":             model.get("status", "active"),
                "Rating":             model.get("rating") or 0,
                "Rating Label":       model.get("rating_label", ""),
                "Notes":              model.get("notes", ""),
                "Google Direct":      vprice("google_direct"),
                "ElevenLabs Direct":  vprice("elevenlabs_direct"),
                "OpenAI Direct":      vprice("openai_direct"),
                "kie.ai":             vprice("kie_ai"),
                "WaveSpeed":          vprice("wavespeed"),
                "fal.ai":             vprice("fal_ai"),
                "OpenRouter":         vprice("openrouter"),
                "Cheapest Platform":  cheapest_label,
                "Last Updated":       catalog["_meta"]["last_updated"],
            })

    total_variants = len(all_records)
    synced = 0
    api_calls = 0

    for i in range(0, total_variants, 10):
        batch = all_records[i:i + 10]
        result = airtable_batch_upsert(batch)
        api_calls += 1
        if result:
            synced += len(result.get("records", []))

    print(f"  ✓ {synced}/{total_variants} variant records synced to Airtable '{AIRTABLE_TABLE_NAME}' ({api_calls} API calls)")

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Monthly model catalog refresh")
    parser.add_argument("--force-ratings", action="store_true",
                        help="Re-fetch all ratings even if already scored")
    parser.add_argument("--skip-ratings", action="store_true",
                        help="Skip rating search (faster, pricing only)")
    parser.add_argument("--skip-airtable", action="store_true",
                        help="Skip Airtable sync")
    parser.add_argument("--discover", action="store_true",
                        help="Run discovery search for new top-tier models")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Model Catalog Refresh — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    catalog = load_catalog()
    total_changes = 0

    # Pricing refreshes
    total_changes += refresh_kieai_prices(catalog)
    total_changes += refresh_wavespeed_prices(catalog)
    total_changes += refresh_fal_prices(catalog)
    total_changes += refresh_openai_prices(catalog)
    update_cheapest_route(catalog)

    # Ratings
    if not args.skip_ratings:
        total_changes += refresh_ratings(catalog, force=args.force_ratings)

    # Discovery
    if args.discover:
        discover_new_models()

    # Save
    save_catalog(catalog)

    # Airtable sync
    if not args.skip_airtable:
        sync_to_airtable(catalog)

    print(f"\n{'='*60}")
    print(f"  Done — {total_changes} values updated")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
