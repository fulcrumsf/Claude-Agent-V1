#!/usr/bin/env python3
"""
Tool Manager CLI — Agent-OS
Cost routing and model recommendation for all pipelines.
Usage: python tool_manager.py [command] [options]
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

import click
import requests

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PRICING_CACHE = DATA_DIR / "pricing_cache.json"
MODEL_CAPS = DATA_DIR / "model_capabilities.json"
MODEL_CATALOG = DATA_DIR / "model_catalog.json"

SECRETS_FILE = Path.home() / ".env-secrets"


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_env_key(key_name: str) -> str | None:
    if not SECRETS_FILE.exists():
        return None
    for line in SECRETS_FILE.read_text().splitlines():
        if line.startswith(f"export {key_name}="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def pricing_is_stale(cache: dict) -> bool:
    last = cache["_meta"].get("last_updated")
    if not last:
        return True
    last_dt = datetime.fromisoformat(last)
    interval = cache["_meta"].get("refresh_interval_days", 30)
    return datetime.now() > last_dt + timedelta(days=interval)


def research_model(model_key: str, model_data: dict) -> dict:
    """Use Perplexity to research a model's capabilities and populate the DB."""
    api_key = load_env_key("PERPLEXITY_API_KEY")
    if not api_key:
        click.echo("  ⚠️  PERPLEXITY_API_KEY not found — skipping live research")
        return model_data

    display_name = model_data.get("display_name", model_key)
    prompt = (
        f"Research the AI model '{display_name}' for video/image generation. "
        f"Provide: (1) 2-3 sentence pros, (2) 2-3 sentence cons, "
        f"(3) what it is best used for, (4) what to avoid using it for, "
        f"(5) any available benchmark scores for photorealism, motion quality, "
        f"prompt adherence, and character consistency. "
        f"Be factual and concise. If data is unavailable, say so."
    )

    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "sonar-pro",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 600,
            },
            timeout=30,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        model_data["research_raw"] = content
        model_data["research_needed"] = False
        model_data["last_researched"] = datetime.now().isoformat()
        click.echo(f"  ✓ Researched {display_name}")
    except Exception as e:
        click.echo(f"  ✗ Research failed for {display_name}: {e}")

    return model_data


def scrape_pricing_firecrawl(url: str) -> str | None:
    """Scrape a pricing page via Firecrawl CLI."""
    try:
        result = subprocess.run(
            ["firecrawl", "scrape", url, "--only-main-content", "--format", "markdown"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        click.echo(f"  ✗ Firecrawl failed for {url}: {e}")
    return None


@click.group()
def cli():
    """Tool Manager — live cost routing and model recommendations for Agent-OS pipelines."""
    pass


@cli.command()
@click.option("--pipeline", required=True,
              help='Pipeline spec, e.g. "images:15,video:15,tts:3min,music:1track"')
@click.option("--verbose", is_flag=True, help="Show per-model breakdown")
def cost(pipeline, verbose):
    """Estimate total cost for a pipeline and recommend cheapest options per step."""
    cache = load_json(PRICING_CACHE)

    if pricing_is_stale(cache):
        click.echo("⚠️  Pricing cache is stale. Run `tool_manager.py refresh` for current prices.")
        click.echo("   Showing last known prices (may be outdated).\n")

    steps = {}
    for item in pipeline.split(","):
        item = item.strip()
        if ":" in item:
            k, v = item.split(":", 1)
            steps[k.strip()] = v.strip()
        else:
            steps[item] = "1"

    click.echo("\n📊 PIPELINE COST ESTIMATE")
    click.echo("=" * 50)

    total_min = 0.0
    total_max = 0.0

    # Routes to compare per step — all known options with live service keys from pricing cache
    # Format: (api_key, service_key, route_label, billing_unit)
    # billing_unit: "per_second" | "per_video" | "per_image" | "per_1k_chars" | "per_request"
    step_routes = {
        "images": [
            ("openai",    "gpt-image-2",                            "OpenAI direct",       "per_image"),
            ("kie.ai",    "gpt-image-2-text-to-image-1k",           "kie.ai gateway",      "per_image"),
            ("kie.ai",    "google-nano-banana-text-to-image",        "kie.ai gateway",      "per_image"),
            ("kie.ai",    "google-nano-banana-2-1k",                 "kie.ai gateway",      "per_image"),
            ("wavespeed", "nano-banana-2",                           "WaveSpeed gateway",   "per_image"),
        ],
        "video": [
            # Seedance 2 (cheapest standard quality)
            ("kie.ai",    "bytedance-seedance-2-fast-480p-with-video-input", "kie.ai gateway",    "per_second"),
            ("kie.ai",    "bytedance-seedance-2-fast-720p-with-video-input", "kie.ai gateway",    "per_second"),
            ("wavespeed", "seedance-2.0-fast",                               "WaveSpeed gateway", "per_second"),
            # Kling 3.0
            ("kie.ai",    "kling-3.0-video-without-audio-720p",              "kie.ai gateway",    "per_second"),
            ("wavespeed", "kling-3.0-std",                                   "WaveSpeed gateway", "per_second"),
            # Veo 3.1 (flat per-video pricing)
            ("kie.ai",    "google-veo-3.1-text-to-video-lite-720p",          "kie.ai gateway",    "per_video"),
            ("kie.ai",    "google-veo-3.1-text-to-video-fast-720p",          "kie.ai gateway",    "per_video"),
            ("wavespeed", "veo-3.1-fast",                                    "WaveSpeed gateway", "per_second"),
        ],
        "tts": [
            ("elevenlabs", "tts-flash",             "ElevenLabs direct", "per_1k_chars"),
            ("elevenlabs", "tts-multilingual-v2",   "ElevenLabs direct", "per_1k_chars"),
        ],
        "music": [
            ("kie.ai", "suno-generate-music", "kie.ai/Suno", "per_request"),
        ],
        "scrape": [
            ("firecrawl", "scrape", "Firecrawl direct", "per_request"),
        ],
        "research": [
            ("perplexity", "sonar-pro", "Perplexity direct", "per_request"),
        ],
        "storage": [
            ("cloudinary", "storage", "Cloudinary direct", "per_request"),
        ],
    }

    CLIP_SECONDS = 5
    CHARS_PER_MINUTE = 750

    for step, quantity in steps.items():
        routes = step_routes.get(step)
        if not routes:
            click.echo(f"  {step}: ⚠️  unknown step")
            continue

        # Collect all routes with known prices, normalize to cost-per-clip or cost-per-unit
        priced_routes = []
        unpriced = []
        for api_key, service_key, route_label, billing_unit in routes:
            api_data = cache["apis"].get(api_key, {})
            svc = api_data.get("services", {}).get(service_key, {})
            price = svc.get("price")
            if price is not None:
                priced_routes.append((price, billing_unit, api_key, service_key, route_label, api_data))
            else:
                unpriced.append(f"{api_data.get('display_name', api_key)}/{service_key}")

        if not priced_routes:
            click.echo(f"  {step}: ⚠️  no prices available for any route — run refresh")
            if unpriced:
                click.echo(f"    Missing: {', '.join(unpriced)}")
            continue

        try:
            raw = float(quantity.replace("min", "").replace("track", "").replace("s", ""))
        except ValueError:
            click.echo(f"  {step}: could not parse quantity '{quantity}'")
            continue

        # Compute estimated cost per route and pick cheapest
        def compute_cost(price, billing_unit, raw):
            if step == "video":
                if billing_unit == "per_second":
                    return price * raw * CLIP_SECONDS, f"{int(raw)} clips × {CLIP_SECONDS}s @ ${price}/sec"
                elif billing_unit == "per_video":
                    return price * raw, f"{int(raw)} clips (flat) @ ${price}/video"
            elif step == "tts":
                chars = raw * CHARS_PER_MINUTE
                return (chars / 1000) * price, f"{raw}min ≈ {int(chars)} chars @ ${price}/1k chars"
            elif step == "images":
                return price * raw, f"{int(raw)} images @ ${price}/image"
            return price * raw, f"{quantity} @ ${price}/unit"

        route_costs = []
        for price, billing_unit, api_key, service_key, route_label, api_data in priced_routes:
            estimated, unit_note = compute_cost(price, billing_unit, raw)
            route_costs.append((estimated, price, billing_unit, api_key, service_key, route_label, api_data, unit_note))

        route_costs.sort(key=lambda r: r[0])
        estimated, cheapest_price, billing_unit, cheapest_api, cheapest_svc, cheapest_label, cheapest_api_data, unit_note = route_costs[0]

        total_min += estimated * 0.8
        total_max += estimated * 1.2
        platform = cheapest_api_data.get("display_name", cheapest_api)
        click.echo(f"  {step}: ${estimated:.4f} via {platform} [{cheapest_svc}] ✅ cheapest")
        click.echo(f"    └─ {unit_note} | compared {len(route_costs)} route(s)")

        if verbose and len(route_costs) > 1:
            for est, price, bu, ak, sk, rl, ad, un in route_costs[1:]:
                alt_platform = ad.get("display_name", ak)
                click.echo(f"    └─ alt: {alt_platform}/{sk} @ ${est:.4f} total ({un})")

        if unpriced:
            click.echo(f"    ⚠️  Could not compare: {', '.join(unpriced)} (no price data)")

    click.echo("-" * 50)
    if total_min > 0:
        click.echo(f"  Estimated total: ${total_min:.3f} – ${total_max:.3f}")
    else:
        click.echo("  Run `tool_manager.py refresh` to populate prices first.")
    click.echo()


@cli.command()
@click.option("--type", "media_type", required=True, type=click.Choice(["image", "video", "audio", "video-to-audio"]),
              help="image or video")
@click.option("--need", default="", help="What the task needs, e.g. photorealism, character-consistency")
def recommend(media_type, need):
    """Recommend the best model for a task using model_catalog.json. Returns winner + backup."""
    # Load catalog (primary) with fallback to legacy model_capabilities.json
    if MODEL_CATALOG.exists():
        catalog = load_json(MODEL_CATALOG)
        _recommend_from_catalog(catalog, media_type, need)
    elif MODEL_CAPS.exists():
        _recommend_from_caps(media_type, need)
    else:
        click.echo("  ⚠️  No model data found. Run catalog_refresh.py first.")


def _recommend_from_catalog(catalog, media_type, need):
    """Recommend from model_catalog.json — cross-platform pricing + ratings."""
    models = catalog.get("models", [])

    # Filter by type — support aliases (video = text-to-video, image = text-to-image, etc.)
    type_map = {
        "video": ["text-to-video", "video-to-video"],
        "image": ["text-to-image"],
        "audio": ["text-to-speech", "text-to-sfx", "text-to-music"],
        "video-to-audio": ["video-to-audio"],
    }
    target_types = type_map.get(media_type, [media_type])

    candidates = [
        m for m in models
        if m.get("status") != "deprecated"
        and any(t in m.get("type", "") for t in target_types)
        and m.get("rating") is not None
    ]

    # Sort by rating desc, then cheapest_price asc as tiebreaker
    candidates.sort(key=lambda m: (
        -(m.get("rating") or 0),
        m["pricing"].get("cheapest_price") or 999
    ))

    click.echo(f"\n  MODEL RECOMMENDATION — {media_type.upper()}")
    click.echo("  " + "=" * 48)

    if not candidates:
        click.echo(f"  No rated {media_type} models in catalog. Run catalog_refresh.py --force-ratings.")
        return

    winner = candidates[0]
    backup = candidates[1] if len(candidates) > 1 else None

    def _fmt_model(m, label):
        pricing = m.get("pricing", {})
        cheapest = str(pricing.get("cheapest") or "needs-pricing")
        price = pricing.get("cheapest_price")
        price_str = f"${price}" if price is not None else "price unknown"
        rating = m.get("rating", "?")
        click.echo(f"\n  {label}: {m['name']}")
        click.echo(f"     Type:      {m.get('type','')}")
        click.echo(f"     Rating:    {rating}/10")
        click.echo(f"     Platform:  {cheapest} ({price_str})")
        click.echo(f"     Use for:   {m.get('description','')[:80]}")
        if m.get("notes"):
            click.echo(f"     Notes:     {m['notes'][:80]}")

    _fmt_model(winner, "WINNER")
    if backup:
        _fmt_model(backup, "BACKUP")

    if need:
        click.echo(f"\n  Task note: '{need}'")
        # Check if any model description matches the need keyword
        matches = [m for m in candidates if need.lower() in m.get("description", "").lower()
                   or need.lower() in m.get("notes", "").lower()]
        if matches and matches[0]["id"] != winner["id"]:
            click.echo(f"  Tip: '{matches[0]['name']}' may better match this requirement.")

    # Show full ranked list
    click.echo(f"\n  All {media_type} models (by rating):")
    for m in candidates[:6]:
        pricing = m.get("pricing", {})
        price = pricing.get("cheapest_price")
        price_str = f"${price}" if price is not None else "N/A"
        platform = str(pricing.get("cheapest") or "needs-pricing")
        click.echo(f"    {m.get('rating','?'):>4}/10  {m['name']:<30} {platform:<18} {price_str}")
    click.echo()


def _recommend_from_caps(media_type, need):
    """Legacy fallback using model_capabilities.json."""
    caps = load_json(MODEL_CAPS)
    section = caps.get(media_type, {})
    top_tier = section.get("top_tier", [])
    alternatives = section.get("alternatives", [])
    models = section.get("models", {})

    click.echo(f"\n  MODEL RECOMMENDATION — {media_type.upper()} (legacy caps DB)")
    click.echo("  " + "=" * 48)

    if not top_tier:
        click.echo("  No top-tier models defined. Run catalog_refresh.py first.")
        return

    winner_key = top_tier[0]
    backup_key = top_tier[1] if len(top_tier) > 1 else (alternatives[0] if alternatives else None)
    winner = models.get(winner_key, {})
    backup = models.get(backup_key, {}) if backup_key else {}

    click.echo(f"\n  WINNER: {winner.get('display_name', winner_key)}")
    click.echo(f"     Platform: {winner.get('platform', 'unknown')}")
    if backup_key:
        click.echo(f"\n  BACKUP: {backup.get('display_name', backup_key)}")
    click.echo()


@cli.command("research-models")
@click.option("--type", "media_type", default=None, type=click.Choice(["image", "video"]),
              help="Limit to image or video models")
@click.option("--force", is_flag=True, help="Re-research even if already researched")
def research_models(media_type, force):
    """Research model capabilities via Perplexity and populate the capabilities DB."""
    caps = load_json(MODEL_CAPS)

    types_to_research = [media_type] if media_type else ["image", "video"]

    for t in types_to_research:
        section = caps.get(t, {})
        models = section.get("models", {})
        click.echo(f"\n🔍 Researching {t} models...")

        for key, data in models.items():
            if not force and not data.get("research_needed", True):
                click.echo(f"  ↩  {data.get('display_name', key)} — already researched, skipping")
                continue
            caps[t]["models"][key] = research_model(key, data)

    save_json(MODEL_CAPS, caps)
    click.echo("\n✅ Model capabilities DB updated.")


def _build_comparison_table(cache: dict) -> str:
    """Build a markdown cost comparison table from all APIs and services."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Tool Manager — Cost Comparison Matrix",
        f"_Auto-generated: {now}. Run `tm refresh` to update._",
        "",
        "## ⚠️ Refresh Failures / Access Issues",
        "",
    ]

    failures = cache["_meta"].get("refresh_failures", {})
    if failures:
        lines += ["| API | Status | Reason | Action Required |",
                  "|-----|--------|--------|-----------------|"]
        for api_key, info in failures.items():
            lines.append(f"| {api_key} | {info['status']} | {info['reason']} | {info['action']} |")
    else:
        lines.append("_No failures recorded on last refresh._")

    lines += ["", "---", "", "## Cost Comparison by Task", ""]

    # Group services by task type
    task_rows: dict[str, list] = {}
    for api_key, api_data in cache["apis"].items():
        platform = api_data.get("display_name", api_key)
        last_fetched = api_data.get("last_fetched", "unknown")[:10]
        for svc_key, svc in api_data.get("services", {}).items():
            price = svc.get("price")
            if price is None:
                continue
            unit = svc.get("unit", "")
            note = svc.get("note", "")
            # infer task type from service key
            if any(x in svc_key for x in ["image", "banana", "nano"]):
                task = "image"
            elif any(x in svc_key for x in ["video", "kling", "seedance", "veo", "wan", "sora", "hailuo"]):
                task = "video"
            elif "tts" in svc_key or "speech" in svc_key:
                task = "tts"
            elif "suno" in svc_key or "music" in svc_key:
                task = "music"
            elif "scrape" in svc_key or "crawl" in svc_key:
                task = "scrape"
            elif "credit" in svc_key:
                continue  # skip meta-pricing rows
            else:
                task = "other"

            task_rows.setdefault(task, []).append({
                "model": svc_key,
                "platform": platform,
                "price": price,
                "unit": unit,
                "note": note,
                "verified": last_fetched,
            })

    task_order = ["image", "video", "tts", "music", "scrape", "other"]
    for task in task_order:
        rows = task_rows.get(task)
        if not rows:
            continue
        rows_sorted = sorted(rows, key=lambda r: r["price"])
        cheapest_price = rows_sorted[0]["price"]

        lines.append(f"### {task.upper()}")
        lines.append("")
        lines.append("| Model | Platform | Price | Unit | Cheapest? | Last Verified | Notes |")
        lines.append("|-------|----------|-------|------|-----------|---------------|-------|")
        for r in rows_sorted:
            flag = "✅" if r["price"] == cheapest_price else ""
            lines.append(
                f"| {r['model']} | {r['platform']} | ${r['price']} | {r['unit']} "
                f"| {flag} | {r['verified']} | {r['note']} |"
            )
        lines.append("")

    # Flag APIs with no structured prices yet
    unpriced = [
        api_data.get("display_name", k)
        for k, api_data in cache["apis"].items()
        if not api_data.get("services")
        or all(v.get("price") is None for v in api_data.get("services", {}).values())
    ]
    if unpriced:
        lines += [
            "---",
            "",
            "## ⚠️ APIs With No Structured Prices Yet",
            "",
            "_Prices not yet extracted from raw snapshots. Run `tm extract-prices`._",
            "",
        ]
        for name in unpriced:
            lines.append(f"- {name}")

    return "\n".join(lines)


@cli.command()
@click.option("--api", default=None, help="Refresh a specific API only (e.g. openai, kie.ai)")
def refresh(api):
    """Fetch current pricing from all APIs, log failures, and regenerate comparison matrix."""
    cache = load_json(PRICING_CACHE)
    apis_to_refresh = [api] if api else list(cache["apis"].keys())

    click.echo(f"\n🔄 Refreshing pricing for: {', '.join(apis_to_refresh)}")

    failures = cache["_meta"].get("refresh_failures", {})

    for api_key in apis_to_refresh:
        api_data = cache["apis"].get(api_key)
        if not api_data:
            click.echo(f"  ✗ {api_key} not in pricing DB")
            failures[api_key] = {
                "status": "❌ Not in DB",
                "reason": "API key not found in pricing_cache.json",
                "action": "Add entry to pricing_cache.json",
                "logged": datetime.now().isoformat(),
            }
            continue

        url = api_data.get("pricing_url")
        method = api_data.get("fetch_method", "firecrawl")
        display = api_data["display_name"]
        click.echo(f"\n  → {display} ({method})")

        if method == "firecrawl":
            content = scrape_pricing_firecrawl(url)
            if content:
                cache["apis"][api_key]["last_fetched"] = datetime.now().isoformat()
                cache["apis"][api_key]["raw_pricing_snapshot"] = content[:2000]
                failures.pop(api_key, None)  # clear any prior failure
                click.echo(f"    ✓ Scraped {len(content)} chars")
            else:
                click.echo(f"    ✗ FAILED — no content returned from {url}")
                failures[api_key] = {
                    "status": "❌ Scrape failed",
                    "reason": f"Firecrawl returned empty for {url}",
                    "action": f"Check manually: {url}",
                    "logged": datetime.now().isoformat(),
                }
        elif method == "playwright":
            scraper = BASE_DIR / "scrape_kieai.py"
            venv_python = BASE_DIR / ".venv" / "bin" / "python"
            python_bin = str(venv_python) if venv_python.exists() else "python3"
            try:
                result = subprocess.run(
                    [python_bin, str(scraper)],
                    capture_output=True, text=True, timeout=120
                )
                raw_json = BASE_DIR / "data" / "kieai_pricing_api.json"
                if result.returncode == 0 and raw_json.exists():
                    import json as _json
                    records = _json.loads(raw_json.read_text())
                    from scrape_kieai import records_to_services
                    services = records_to_services(records)
                    cache["apis"][api_key]["services"] = services
                    cache["apis"][api_key]["last_fetched"] = datetime.now().isoformat()
                    failures.pop(api_key, None)
                    click.echo(f"    ✓ {len(services)} models fetched via Playwright API")
                else:
                    err = result.stderr[-300:] if result.stderr else "unknown error"
                    click.echo(f"    ✗ Playwright scraper failed: {err}")
                    failures[api_key] = {
                        "status": "❌ Playwright failed",
                        "reason": err,
                        "action": f"Run manually: {python_bin} {scraper}",
                        "logged": datetime.now().isoformat(),
                    }
            except Exception as e:
                click.echo(f"    ✗ Playwright scraper exception: {e}")
                failures[api_key] = {
                    "status": "❌ Exception",
                    "reason": str(e),
                    "action": f"Check {scraper}",
                    "logged": datetime.now().isoformat(),
                }

    cache["_meta"]["last_updated"] = datetime.now().isoformat()
    cache["_meta"]["next_refresh"] = (datetime.now() + timedelta(days=30)).isoformat()
    cache["_meta"]["refresh_failures"] = failures
    save_json(PRICING_CACHE, cache)

    # Auto-generate comparison matrix
    comparison_md = _build_comparison_table(cache)
    comparison_path = DATA_DIR / "Cost_Comparison.md"
    comparison_path.write_text(comparison_md)

    if failures:
        click.echo(f"\n⚠️  {len(failures)} API(s) could not be refreshed:")
        for k, f in failures.items():
            click.echo(f"   • {k}: {f['status']} — {f['reason']}")
        click.echo(f"   Full failure log: data/Cost_Comparison.md")
    else:
        click.echo("\n✅ All APIs refreshed successfully.")

    click.echo(f"✅ Cost comparison matrix written → data/Cost_Comparison.md")
    click.echo("   Run `tm extract-prices` to parse any new raw snapshots into structured prices.")


@cli.command("fal-search")
@click.argument("query")
@click.option("--limit", default=10, help="Max results to show (default 10)")
@click.option("--pricing", is_flag=True, help="Fetch pricing for each result")
def fal_search(query, limit, pricing):
    """Search fal.ai model catalog. Uses the authenticated Platform API.

    Example: tm fal-search "video to audio" --pricing
    """
    import urllib.request, urllib.parse

    key = load_env_key("FAL_AI_API_KEY")
    if not key:
        click.echo("ERROR: FAL_AI_API_KEY not found in ~/.env-secrets", err=True)
        raise SystemExit(1)

    headers = {"Authorization": f"Key {key}"}

    url = f"https://api.fal.ai/v1/models?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        raise SystemExit(1)

    models = data.get("models", [])[:limit]
    if not models:
        click.echo(f"No results for '{query}'")
        return

    click.echo(f"\nfal.ai search: '{query}' — {len(models)} result(s)\n")

    for m in models:
        eid = m["endpoint_id"]
        meta = m.get("metadata", {})
        name = meta.get("display_name") or eid
        category = meta.get("category", "")
        line = f"  {eid}"
        if name != eid:
            line += f"  [{name}]"
        if category:
            line += f"  ({category})"

        if pricing:
            price_url = f"https://api.fal.ai/v1/models/pricing?endpoint_id={urllib.parse.quote(eid)}"
            try:
                preq = urllib.request.Request(price_url, headers=headers)
                with urllib.request.urlopen(preq, timeout=10) as presp:
                    pdata = json.loads(presp.read())
                prices = pdata.get("prices", [])
                if prices:
                    p = prices[0]
                    line += f"  ${p['unit_price']}/{p['unit']}"
            except Exception:
                line += "  (price unavailable)"

        click.echo(line)

    click.echo()


@cli.command("extract-prices")
def extract_prices():
    """Parse raw pricing snapshots and populate structured price fields using Claude/GPT."""
    click.echo("\n🧮 Price extraction from raw snapshots")
    click.echo("  This step requires an LLM to parse pricing page content.")
    click.echo("  Invoke via Claude: 'parse the raw_pricing_snapshot fields in pricing_cache.json")
    click.echo("  and populate the price fields for each service.'")
    click.echo(f"\n  Cache location: {PRICING_CACHE}")


@cli.command()
def status():
    """Show current state of both databases, failures, and comparison matrix."""
    cache = load_json(PRICING_CACHE)
    caps = load_json(MODEL_CAPS)

    click.echo("\n📋 TOOL MANAGER STATUS")
    click.echo("=" * 50)

    # Pricing cache
    last_updated = cache["_meta"].get("last_updated") or "never"
    next_refresh = cache["_meta"].get("next_refresh") or "not scheduled"
    stale = pricing_is_stale(cache)
    click.echo(f"\nPricing Cache:")
    click.echo(f"  Last updated: {last_updated}")
    click.echo(f"  Next refresh: {next_refresh}")
    click.echo(f"  Status: {'⚠️  STALE — run: tm refresh' if stale else '✅ current'}")

    # Failures — always show, prominently
    failures = cache["_meta"].get("refresh_failures", {})
    click.echo(f"\nRefresh Failures:")
    if failures:
        click.echo(f"  ⚠️  {len(failures)} API(s) did NOT refresh successfully:")
        for k, f in failures.items():
            click.echo(f"    • {k}: {f['status']}")
            click.echo(f"      Reason: {f['reason']}")
            click.echo(f"      Action: {f['action']}")
    else:
        click.echo("  ✅ No failures on last refresh")

    # Model capabilities
    click.echo(f"\nModel Capabilities:")
    for media_type in ["image", "video"]:
        section = caps.get(media_type, {})
        models = section.get("models", {})
        needs_research = [k for k, v in models.items() if v.get("research_needed")]
        click.echo(f"  {media_type}: {len(models)} models, {len(needs_research)} need research")
        if needs_research:
            click.echo(f"    → Run: tm research-models --type {media_type}")

    # Comparison matrix
    comparison_path = DATA_DIR / "Cost_Comparison.md"
    click.echo(f"\nCost Comparison Matrix:")
    if comparison_path.exists():
        age = datetime.now() - datetime.fromtimestamp(comparison_path.stat().st_mtime)
        click.echo(f"  ✅ exists — last updated {int(age.total_seconds() / 3600)}h ago")
        click.echo(f"  → {comparison_path}")
    else:
        click.echo(f"  ⚠️  Not generated yet — run: tm refresh")

    click.echo(f"\nData directory: {DATA_DIR}")
    click.echo()


if __name__ == "__main__":
    cli()
