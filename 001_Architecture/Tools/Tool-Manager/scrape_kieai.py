#!/usr/bin/env python3
"""
Fetch all kie.ai model pricing via the undocumented JSON API.
Uses an existing Chrome session (copies profile to temp dir) for auth.

Endpoint: POST https://api.kie.ai/client/v1/model-pricing/page
Payload:  {"pageNum": N, "pageSize": 50, "modelDescription": "", "interfaceType": ""}
Returns:  {"code": 200, "data": {"records": [...], "total": N}}
"""

import sys
import json
import shutil
import tempfile
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME_PROFILE = Path("/Users/tonymacbook2025/Library/Application Support/Google/Chrome")
API_URL = "https://api.kie.ai/client/v1/model-pricing/page"
PAGE_SIZE = 50
OUTPUT_FILE = Path(__file__).parent / "data" / "kieai_pricing_api.json"


def fetch_all_models() -> list[dict] | None:
    tmp_dir = tempfile.mkdtemp(prefix="kie_api_")
    tmp_profile = Path(tmp_dir) / "chrome_copy"
    try:
        shutil.copytree(str(CHROME_PROFILE), str(tmp_profile), dirs_exist_ok=True)
    except Exception as e:
        print(f"  ⚠ Profile copy warning: {e}", file=sys.stderr)

    all_records = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(tmp_profile),
                channel="chrome",
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            page = browser.new_page()
            page.goto("https://kie.ai", wait_until="domcontentloaded", timeout=20000)
            time.sleep(2)

            page_num = 1
            while True:
                payload = {
                    "pageNum": page_num,
                    "pageSize": PAGE_SIZE,
                    "modelDescription": "",
                    "interfaceType": "",
                }
                resp = page.evaluate(
                    """async ([url, body]) => {
                        const r = await fetch(url, {
                            method: "POST",
                            headers: {"Content-Type": "application/json"},
                            body: JSON.stringify(body),
                        });
                        return await r.json();
                    }""",
                    [API_URL, payload],
                )

                records = resp.get("data", {}).get("records", [])
                if not records:
                    break

                all_records.extend(records)
                total = resp.get("data", {}).get("total", 0)
                print(f"  Page {page_num}: {len(records)} models (total so far: {len(all_records)}/{total})", file=sys.stderr)

                if len(all_records) >= total:
                    break
                page_num += 1

            browser.close()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return None

    shutil.rmtree(tmp_dir, ignore_errors=True)
    return all_records


def records_to_services(records: list[dict]) -> dict:
    """Convert raw API records to the pricing_cache services format."""
    services = {}
    for item in records:
        name = item.get("modelDescription", "")
        price_str = str(item.get("usdPrice", "0")).replace(",", ".")
        try:
            price = float(price_str)
        except (ValueError, TypeError):
            continue

        slug = name.lower()
        for ch in " /,()'":
            slug = slug.replace(ch, "-")
        slug = "-".join(p for p in slug.split("-") if p)[:60]

        services[slug] = {
            "price": price,
            "unit": item.get("creditUnit", ""),
            "provider": item.get("provider", ""),
            "interface_type": item.get("interfaceType", ""),
            "official_fal_price": item.get("falPrice"),
            "note": name,
        }
    return services


if __name__ == "__main__":
    print("Fetching kie.ai pricing via JSON API...", file=sys.stderr)
    records = fetch_all_models()
    if records:
        OUTPUT_FILE.write_text(json.dumps(records, indent=2))
        print(f"✅ {len(records)} models saved to {OUTPUT_FILE}")

        services = records_to_services(records)
        print(f"\nKey models:")
        for kw in ["seedance-2", "kling-3.0", "veo-3.1-text-to-video-fast-720", "nano-banana-text", "nano-banana-2-1k", "suno-generate-music-"]:
            for slug, data in services.items():
                if kw in slug and data.get("price", 0) > 0:
                    print(f"  {slug}: ${data['price']} {data.get('unit','')}")
                    break
    else:
        print("FAILED — no records returned")
        sys.exit(1)
