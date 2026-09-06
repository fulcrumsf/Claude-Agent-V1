#!/usr/bin/env python3
"""
resource_library_dedup.py — surface likely duplicate bookmarks in 007_Resource_Library.

Tony re-bookmarks the same thing sometimes (especially YouTube tutorials he re-watches
months later and forgets he saved). This scans the library, clusters notes that look
like the same source, and writes a REVIEW file — a side-by-side table with clickable
links to the "Original" and each "Duplicate", plus the match reason and confidence.

It NEVER deletes or moves anything. Tony reviews the table and decides.

Match tiers
-----------
  exact   — identical canonical URL, or identical YouTube video ID
  high    — title >= --min-title-sim similar AND same domain (or neither has a domain)
  medium  — body text >= --min-body-sim similar

Usage
-----
  python3 resource_library_dedup.py                       # default roots, writes _Dedup_Review.md + .json
  python3 resource_library_dedup.py --roots Tools Tutorials Research
  python3 resource_library_dedup.py --include-images      # also match image-stub notes by title
  python3 resource_library_dedup.py --min-title-sim 95 --min-body-sim 92
  python3 resource_library_dedup.py --format json
  python3 resource_library_dedup.py --output /tmp/dupes.md

Reusable: safe to re-run any time (e.g. after an ingest batch). Output files are
overwritten each run.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, urlunsplit, urlencode

try:
    from rapidfuzz import fuzz
except ImportError:
    sys.exit("rapidfuzz not installed. Run: python3 -m pip install rapidfuzz")

RESOURCE_LIBRARY = Path("/Users/tonymacbook2025/Documents/Agent-OS/007_Resource_Library")

# Default folders to scan. OpenAI_History (private chat exports), Obsidian_Attachments,
# graphify-out and Archive are excluded by default.
DEFAULT_ROOTS = [
    "Tools", "Tutorials", "Research", "Prompts", "Workflows", "Docs", "Models",
    "Videos", "Project_Ideas", "Design_Inspiration", "Investments", "Personal",
    "Undetermined",
]

ALWAYS_SKIP_DIRS = {"OpenAI_History", "Obsidian_Attachments", "graphify-out", ".git", ".obsidian"}

# Frontmatter keys that may carry a source URL, in priority order.
URL_KEYS = ["source", "url", "URL", "Source", "link", "source_url", "website", "repo", "repository", "github"]

# Hosts / URL shapes that are never a real "source" — boilerplate, CDN assets, placeholders.
JUNK_URL_SUBSTR = [
    "notion.so/icons/", "your-domain.com", "example.com", "example.org",
    "localhost", "127.0.0.1", "images.unsplash.com", "img.freepik.com",
    "gstatic.com", "googleusercontent.com", "w3.org", "schema.org",
    "fonts.googleapis.com", "cdn.jsdelivr.net", "unpkg.com",
    "claude.ai/code",  # "built with Claude Code" boilerplate
]
# Path prefixes that are queries/navigation, not a specific resource.
NON_RESOURCE_PATH_RE = re.compile(r"^/(search|s|results|explore|tag|tags|category|q)(/|$|\?)", re.I)

# When scavenging a URL from body text, these are usually incidental (invites,
# sponsor/support links, social follows) rather than the note's actual subject —
# only used as a last resort.
DEPRIORITIZE_HOSTS = (
    "discord.gg", "discord.com", "patreon.com", "t.me", "twitter.com", "x.com",
    "buymeacoffee.com", "ko-fi.com", "linktr.ee", "instagram.com", "facebook.com",
    "gumroad.com",
)
ASSET_EXT_RE = re.compile(r"\.(svg|png|jpe?g|gif|webp|ico|css|js|woff2?|ttf|mp4|webm|pdf)(\?|$)", re.I)
VALID_HOST_RE = re.compile(r"^[a-z0-9.-]+\.[a-z]{2,}$")

# Query params to strip when canonicalizing a URL (tracking / session / referral noise).
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id",
    "si", "feature", "ref", "ref_src", "ref_url", "fbclid", "gclid", "igshid",
    "spm", "share_id", "pp", "app", "ab_channel", "embeds_referring_euri",
    "source_ve_path", "cmpid", "mc_cid", "mc_eid",
}

YT_ID_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/|live/|v/)|youtu\.be/)"
    r"([A-Za-z0-9_-]{11})"
)
URL_RE = re.compile(r"https?://[^\s\)\]\>\"'`]+")
FM_LIST_ITEM_RE = re.compile(r"^\s*-\s+(.*\S)\s*$")
FM_KV_RE = re.compile(r"^([A-Za-z0-9_.\-]+):\s*(.*)$")


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def parse_note(path: Path):
    """Return dict with frontmatter fields + body text. Minimal YAML (no pyyaml dep)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = {}, text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            raw_fm = text[3:end].strip("\n")
            body = text[end + 4:]
            cur_key = None
            for line in raw_fm.splitlines():
                if not line.strip():
                    continue
                item = FM_LIST_ITEM_RE.match(line)
                if item and cur_key:
                    fm.setdefault(cur_key, [])
                    if isinstance(fm[cur_key], list):
                        fm[cur_key].append(_unquote(item.group(1)))
                    continue
                kv = FM_KV_RE.match(line)
                if kv:
                    key, val = kv.group(1), kv.group(2).strip()
                    cur_key = key
                    if val == "":
                        fm[key] = []          # start of a block list
                    else:
                        fm[key] = _unquote(val)
    return {"fm": fm, "body": body}


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def canonical_url(raw: str) -> str:
    """Normalize to https, lowercase host, drop www/fragment, strip tracking params, trim trailing slash."""
    raw = raw.strip().strip("<>()[]\"'`").rstrip(".,;")
    if not raw:
        return ""
    if raw.startswith("//"):
        raw = "https:" + raw
    if not re.match(r"^https?://", raw, re.I):
        raw = "https://" + raw
    try:
        parts = urlsplit(raw)
    except ValueError:
        return ""
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host in ("m.youtube.com", "youtu.be"):
        host = "youtube.com"
    path = parts.path.rstrip("/") or "/"
    q = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=False)
         if k.lower() not in TRACKING_PARAMS]
    q.sort()
    return urlunsplit(("https", host, path, urlencode(q), ""))


def is_homepage(url: str) -> bool:
    parts = urlsplit(url)
    return parts.path in ("", "/") and not parts.query


def is_meaningful_url(url: str, allow_homepage: bool = False) -> bool:
    """Reject CDN assets, boilerplate callbacks, placeholder and malformed hosts.

    Bare homepages are rejected by default (too generic as a body-scavenged key) but
    allowed when `allow_homepage` is set — used for frontmatter `URL:`/`source:` values,
    where the homepage often IS the bookmark (e.g. Tools/Mixamo.md).
    """
    if not url:
        return False
    parts = urlsplit(url)
    host = parts.netloc.lower()
    if not VALID_HOST_RE.match(host):
        return False
    if any(j in url for j in JUNK_URL_SUBSTR):
        return False
    if ASSET_EXT_RE.search(parts.path):
        return False
    if NON_RESOURCE_PATH_RE.match(parts.path):
        return False  # /search?q=... etc — a query, not a resource
    if not allow_homepage and is_homepage(url):
        return False
    return True


def youtube_id(*texts) -> str:
    for t in texts:
        if not t:
            continue
        m = YT_ID_RE.search(t)
        if m:
            return m.group(1)
    return ""


def norm_title(s: str) -> str:
    s = re.sub(r"[^\w\s]", " ", (s or "").lower())
    return re.sub(r"\s+", " ", s).strip()


def strip_markdown(body: str) -> str:
    body = re.sub(r"!?\[\[[^\]]*\]\]", " ", body)                 # wiki links / embeds
    body = re.sub(r"!?\[[^\]]*\]\([^)]*\)", " ", body)            # md links / images
    body = URL_RE.sub(" ", body)
    body = re.sub(r"[#>*_`~\-|]", " ", body)
    body = re.sub(r"\s+", " ", body)
    return body.strip().lower()


def parse_created(fm: dict, path: Path) -> str:
    val = fm.get("created") or fm.get("date") or ""
    if isinstance(val, str):
        m = re.search(r"\d{4}-\d{2}-\d{2}", val)
        if m:
            return m.group(0)
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")


def is_image_stub(rec: dict) -> bool:
    """Screenshot notes: an embed + little else. Excluded from body matching by default."""
    body = rec["body"]
    has_embed = bool(re.search(r"!\[\[[^\]]+\.(png|jpe?g|gif|webp|heic)\]\]", body, re.I)) \
        or bool(rec["fm"].get("original_filename"))
    return has_embed and len(rec["clean_body"]) < 400


# --------------------------------------------------------------------------- #
# Union-Find
# --------------------------------------------------------------------------- #
class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def build_records(roots, include_images):
    records = []
    for root in roots:
        base = RESOURCE_LIBRARY / root
        if not base.is_dir():
            print(f"  ! skip missing root: {root}", file=sys.stderr)
            continue
        for path in base.rglob("*.md"):
            if any(part in ALWAYS_SKIP_DIRS for part in path.parts):
                continue
            note = parse_note(path)
            fm, body = note["fm"], note["body"]

            url, url_from_fm = "", False
            for k in URL_KEYS:
                if fm.get(k) and isinstance(fm[k], str):
                    cand = canonical_url(fm[k])
                    if is_meaningful_url(cand, allow_homepage=True):
                        url, url_from_fm = cand, True
                        break
            if not url:
                body_urls = []
                for m in URL_RE.finditer(body):
                    cand = canonical_url(m.group(0))
                    if is_meaningful_url(cand):
                        body_urls.append(cand)
                primary = [u for u in body_urls
                           if not any(h in urlsplit(u).netloc for h in DEPRIORITIZE_HOSTS)]
                if primary:
                    url = primary[0]
                elif body_urls:
                    url = body_urls[0]

            title = fm.get("title") or path.stem.replace("-", " ").replace("_", " ")
            clean_body = strip_markdown(body)

            # count ALL real outbound links (homepages included) for index detection —
            # a link-list note is often mostly bare-homepage links
            out_links = {canonical_url(u.group(0)) for u in URL_RE.finditer(body)}
            out_links = {u for u in out_links if is_meaningful_url(u, allow_homepage=True)}

            rec = {
                "path": path,
                "rel": str(path.relative_to(RESOURCE_LIBRARY)),
                "n_links": len(out_links),
                "is_index": len(out_links) >= 5,
                "url_from_fm": url_from_fm,
                "url_homepage": bool(url) and is_homepage(url),
                "title": title if isinstance(title, str) else path.stem,
                "title_norm": norm_title(title if isinstance(title, str) else path.stem),
                "url": url,
                "domain": urlsplit(url).netloc if url else "",
                "yt": youtube_id(url, body),
                "created": parse_created(fm, path),
                "body": body,
                "fm": fm,
                "clean_body": clean_body,
                "body_hash": hashlib.sha1(clean_body.encode()).hexdigest() if clean_body else "",
            }
            rec["image_stub"] = is_image_stub(rec)
            if rec["image_stub"] and not include_images:
                # keep for exact URL/YT matching only; flag so body pass skips it
                pass
            records.append(rec)
    return records


def cluster(records, min_title_sim, min_body_sim, include_images):
    uf = UF()
    ids = {id(r): r for r in records}
    for r in records:
        uf.find(id(r))

    reason = {}  # (rootA_id, rootB_id) not tracked; store per-pair reasons keyed by frozenset

    def link(a, b, why, conf):
        uf.union(id(a), id(b))
        key = frozenset((id(a), id(b)))
        # keep the strongest reason
        rank = {"exact": 3, "high": 2, "medium": 1, "low": 0}
        if key not in reason or rank[conf] > rank[reason[key][1]]:
            reason[key] = (why, conf)

    # ---- exact: URL ----
    skipped_keys = []
    by_url = {}
    for r in records:
        if r["url"]:
            by_url.setdefault(r["url"], []).append(r)
    for url, group in by_url.items():
        if len(group) > 6:
            # a URL shared by 7+ notes is almost certainly boilerplate that slipped
            # the filter, not a real duplicate set — report it, don't cluster on it
            skipped_keys.append((url, len(group)))
            continue
        atomic = [r for r in group if not r["is_index"]]
        anchor = atomic[0] if atomic else group[0]
        for other in group:
            if other is anchor:
                continue
            if anchor["is_index"] or other["is_index"]:
                # a per-tool note colliding with an old link-list/index note — flag,
                # don't treat as a real duplicate
                link(anchor, other, f"shares URL {url} — but one side is a link-list/index note (likely NOT a dup)", "low")
                continue
            if is_homepage(url):
                # a bare homepage is only a trustworthy key when BOTH notes name it
                # in frontmatter (not scavenged from body text)
                if not (anchor["url_from_fm"] and other["url_from_fm"]):
                    link(anchor, other, f"shares homepage {url} — weak key, one side has no explicit source (check)", "low")
                    continue
                t = fuzz.token_sort_ratio(anchor["title_norm"], other["title_norm"])
                conf = "exact" if t >= 60 else "high"
                link(anchor, other, f"same site (frontmatter source): {url}", conf)
                continue
            t = fuzz.token_sort_ratio(anchor["title_norm"], other["title_norm"])
            b = fuzz.ratio(anchor["clean_body"], other["clean_body"]) if anchor["clean_body"] and other["clean_body"] else 0
            if t < 55 and b < 40:
                link(anchor, other, f"shares URL {url} — but titles/content look unrelated (check: could be two notes citing the same link)", "low")
            else:
                link(anchor, other, f"same URL: {url}", "exact")

    # ---- exact: YouTube ID ----
    by_yt = {}
    for r in records:
        if r["yt"]:
            by_yt.setdefault(r["yt"], []).append(r)
    for yt, group in by_yt.items():
        if len(group) > 6:
            skipped_keys.append((f"youtube:{yt}", len(group)))
            continue
        atomic = [r for r in group if not r["is_index"]]
        anchor = atomic[0] if atomic else group[0]
        for other in group:
            if other is anchor:
                continue
            if anchor["is_index"] or other["is_index"]:
                link(anchor, other, f"both reference YouTube {yt} — but one side is a link-list/index note (likely NOT a dup)", "low")
                continue
            t = fuzz.token_sort_ratio(anchor["title_norm"], other["title_norm"])
            b = fuzz.ratio(anchor["clean_body"], other["clean_body"]) if anchor["clean_body"] and other["clean_body"] else 0
            if t < 45 and b < 35:
                link(anchor, other, f"both reference YouTube {yt} — but titles/content differ (check)", "low")
            else:
                link(anchor, other, f"same YouTube video: {yt}", "exact")

    # ---- high: fuzzy title AND a matching real source domain ----
    # (title similarity alone is too noisy — "Sora2 Text to Video" vs "Sora2 Image
    #  to Video" score 90%+ but aren't dupes. Require both notes to point at the
    #  same real host.)
    titled = [r for r in records
              if len(r["title_norm"]) >= 12 and VALID_HOST_RE.match(r["domain"] or "")]
    by_dom = {}
    for r in titled:
        by_dom.setdefault(r["domain"], []).append(r)
    for dom, group in by_dom.items():
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                if uf.find(id(a)) == uf.find(id(b)):
                    continue
                if fuzz.token_sort_ratio(a["title_norm"], b["title_norm"]) >= min_title_sim:
                    link(a, b, f"same domain ({dom}) + title ~{min_title_sim}%+ similar", "high")

    # ---- medium: fuzzy body ----
    bodied = [r for r in records
              if len(r["clean_body"]) >= 300 and (include_images or not r["image_stub"])]
    # rapidfuzz.ratio = 2*M/(len_a+len_b); with M <= shorter length, ratio can only
    # reach `s` when the longer body is <= shorter * (2-s)/s. Derive the early-break
    # cutoff from the actual threshold (+5% margin) so a lower --min-body-sim still works.
    s = min_body_sim / 100.0
    len_ratio_cutoff = ((2 - s) / s) * 1.05
    bodied.sort(key=lambda r: len(r["clean_body"]))
    for i, a in enumerate(bodied):
        la = len(a["clean_body"])
        for b in bodied[i + 1:]:
            lb = len(b["clean_body"])
            if lb > la * len_ratio_cutoff:
                break
            if uf.find(id(a)) == uf.find(id(b)):
                continue
            if a["body_hash"] and a["body_hash"] == b["body_hash"]:
                link(a, b, "identical body text", "exact")
                continue
            if fuzz.ratio(a["clean_body"], b["clean_body"]) >= min_body_sim:
                link(a, b, f"body ~{min_body_sim}%+ similar", "medium")

    # ---- assemble clusters ----
    groups = {}
    for r in records:
        groups.setdefault(uf.find(id(r)), []).append(r)
    clusters = [g for g in groups.values() if len(g) > 1]

    out = []
    for g in clusters:
        # keeper = earliest created; tiebreak on the more-developed note
        # (richer frontmatter, then longer body), then path for determinism
        g.sort(key=lambda r: (r["created"], -len(r["fm"]), -len(r["body"]), r["rel"]))
        original = g[0]
        dups = []
        for d in g[1:]:
            why, conf = reason.get(frozenset((id(original), id(d))), (None, None))
            if why is None:
                # linked transitively (3+ note cluster) — use the strongest reason
                # among every recorded pair that touches this duplicate
                _rank = {"exact": 3, "high": 2, "medium": 1, "low": 0}
                best = max((v for k, v in reason.items() if id(d) in k),
                           key=lambda v: _rank[v[1]], default=None)
                if best:
                    why, conf = best
            dups.append({"rec": d, "why": why or "linked in same cluster", "conf": conf or "medium"})
        out.append({"original": original, "dups": dups})
    conf_rank = {"exact": 0, "high": 1, "medium": 2, "low": 3}
    out.sort(key=lambda c: (min(conf_rank[d["conf"]] for d in c["dups"]), c["original"]["rel"]))
    return out, sorted(skipped_keys, key=lambda x: -x[1])


def md_link(rec) -> str:
    # relative to the review file, which sits at RESOURCE_LIBRARY root
    label = rec["title"].replace("[", "(").replace("]", ")")
    return f"[{label}](<{rec['rel']}>)"


def write_markdown(clusters, skipped_keys, out_path, roots, args):
    n_dupes = sum(len(c["dups"]) for c in clusters)
    lines = [
        "---",
        "title: \"Resource Library — Duplicate Bookmark Review\"",
        "type: report",
        "generated_by: 001_Architecture/Scripts/resource_library_dedup.py",
        f"generated: {datetime.now().isoformat(timespec='seconds')}",
        "---",
        "",
        "# Resource Library — Duplicate Bookmark Review",
        "",
        f"**{len(clusters)} clusters**, **{n_dupes} suspected duplicates** across roots: "
        f"`{', '.join(roots)}`.",
        "",
        f"Thresholds: title ≥ {args.min_title_sim}%, body ≥ {args.min_body_sim}%. "
        f"Image-stub notes {'included' if args.include_images else 'excluded'} from body matching.",
        "",
        "Nothing has been deleted or moved. Open both notes via the links and decide "
        "which to keep. **Suggested keeper** = earliest `created:` date (tiebreak: the "
        "more-developed note). `low` rows are probably NOT real duplicates — two notes "
        "that happen to cite the same link — skim and move on.",
        "",
        "| # | Confidence | Match reason | Suggested keeper | Other note | Keeper date | Other date |",
        "|---|---|---|---|---|---|---|",
    ]
    row = 0
    for c in clusters:
        for d in c["dups"]:
            row += 1
            lines.append(
                f"| {row} | {d['conf']} | {d['why']} | {md_link(c['original'])} "
                f"| {md_link(d['rec'])} | {c['original']['created']} | {d['rec']['created']} |"
            )
    lines.append("")
    lines.append("## Clusters with 3+ notes")
    lines.append("")
    multi = [c for c in clusters if len(c["dups"]) >= 2]
    if not multi:
        lines.append("_None._")
    for c in multi:
        lines.append(f"- **{c['original']['title']}** — keep `{c['original']['rel']}`, "
                     f"review: " + ", ".join(f"`{d['rec']['rel']}`" for d in c["dups"]))
    lines.append("")
    if skipped_keys:
        lines.append("## Skipped keys (boilerplate — not clustered)")
        lines.append("")
        lines.append("A URL shared by 7+ notes is treated as boilerplate, not a real "
                     "duplicate set. If any of these IS a real source worth de-duping, "
                     "re-run with a tighter `--roots`.")
        lines.append("")
        lines.append("| Shared URL | Notes |")
        lines.append("|---|---|")
        for url, n in skipped_keys:
            lines.append(f"| `{url}` | {n} |")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_json(clusters, out_path):
    payload = []
    for c in clusters:
        payload.append({
            "original": {"path": c["original"]["rel"], "title": c["original"]["title"],
                         "url": c["original"]["url"], "created": c["original"]["created"]},
            "duplicates": [
                {"path": d["rec"]["rel"], "title": d["rec"]["title"], "url": d["rec"]["url"],
                 "created": d["rec"]["created"], "match": d["why"], "confidence": d["conf"]}
                for d in c["dups"]
            ],
        })
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roots", nargs="+", default=DEFAULT_ROOTS,
                    help=f"folders under 007_Resource_Library to scan (default: {' '.join(DEFAULT_ROOTS)})")
    ap.add_argument("--output", type=Path, default=RESOURCE_LIBRARY / "_Dedup_Review.md",
                    help="markdown review file path (default: 007_Resource_Library/_Dedup_Review.md)")
    ap.add_argument("--format", choices=["md", "json", "both"], default="both")
    ap.add_argument("--min-title-sim", type=int, default=92)
    ap.add_argument("--min-body-sim", type=int, default=90)
    ap.add_argument("--include-images", action="store_true",
                    help="also match image-stub screenshot notes by body text")
    args = ap.parse_args()

    print(f"Scanning {len(args.roots)} roots under {RESOURCE_LIBRARY} ...", file=sys.stderr)
    records = build_records(args.roots, args.include_images)
    print(f"  {len(records)} notes parsed "
          f"({sum(1 for r in records if r['url'])} with URLs, "
          f"{sum(1 for r in records if r['yt'])} YouTube, "
          f"{sum(1 for r in records if r['image_stub'])} image stubs)", file=sys.stderr)

    clusters, skipped_keys = cluster(records, args.min_title_sim, args.min_body_sim, args.include_images)
    n_dupes = sum(len(c["dups"]) for c in clusters)
    print(f"  {len(clusters)} duplicate clusters, {n_dupes} suspected duplicate notes, "
          f"{len(skipped_keys)} boilerplate keys skipped", file=sys.stderr)

    if args.format in ("md", "both"):
        write_markdown(clusters, skipped_keys, args.output, args.roots, args)
        print(f"  wrote {args.output}", file=sys.stderr)
    if args.format in ("json", "both"):
        jpath = args.output.with_suffix(".json")
        write_json(clusters, jpath)
        print(f"  wrote {jpath}", file=sys.stderr)


if __name__ == "__main__":
    main()
