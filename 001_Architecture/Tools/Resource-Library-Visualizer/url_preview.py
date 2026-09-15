"""Lazy, cached og:image lookup for notes with a bookmarked URL but no
embedded image of their own. Never called during index build - only when a
card is actually requested by the browser - and every result (including a
miss) is cached on disk so a given URL is ever fetched at most once."""
import json
import os
import re
import sys
import importlib.util
import pathlib
import urllib.request
import urllib.error
from urllib.parse import urljoin

try:  # macOS framework Python frequently ships without a usable CA bundle for urllib
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass

_here = pathlib.Path(__file__).parent


def _load(name):
    key = f"rlv_{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[key] = m
    spec.loader.exec_module(m)
    return m


config = _load("config")

OG_IMAGE_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)["\']'
    r'|<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']og:image(?::secure_url)?["\']',
    re.I,
)
MAX_BYTES = 300_000  # og:image is always in <head> - no need to read the whole page
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def _load_cache():
    try:
        with open(config.URL_IMAGE_CACHE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(cache):
    os.makedirs(os.path.dirname(config.URL_IMAGE_CACHE), exist_ok=True)
    tmp = config.URL_IMAGE_CACHE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f)
    os.replace(tmp, config.URL_IMAGE_CACHE)


def fetch_og_image(url, timeout=None):
    """Fetch `url` and return its og:image content, or None on any failure
    (dead link, timeout, no tag present, blocked scraping, etc). Never raises."""
    timeout = timeout or config.URL_FETCH_TIMEOUT
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(MAX_BYTES)
        html = raw.decode("utf-8", errors="ignore")
    except Exception:
        return None
    m = OG_IMAGE_RE.search(html)
    if not m:
        return None
    image_url = (m.group(1) or m.group(2) or "").strip()
    if not image_url:
        return None
    return urljoin(url, image_url)


def get_preview_image(url):
    """Cached lookup - fetches at most once per URL, ever. Returns an image
    URL string, or None if none was found (a cached miss, not re-tried)."""
    cache = _load_cache()
    if url in cache:
        return cache[url]
    image_url = fetch_og_image(url)
    cache[url] = image_url
    _save_cache(cache)
    return image_url
