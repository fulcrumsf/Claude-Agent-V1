"""
Enrich Resource Library URL-only stub notes (triage bucket 2) IN PLACE.

For every stub note that has no usable screenshot but does carry a source URL,
ask Gemini (with Google Search grounding) to identify what the link is and
write a real summary into the note. Filename / path preserved.

What changes in each note:
  - form:      saas-tool | github-repo | youtube-video | article | ...
  - summary:   factual 2-3 sentence description of the linked thing
  - url:       kept as-is
  - tags:      union of existing + topic tags
  - type:      normalised content_type
  - verified:  true/false - whether Gemini could confirm the URL resolves
  - enriched:  today's date - skipped on re-runs

Reads:  007_Resource_Library/_Stub_Triage.json
Writes: each note in place + 007_Resource_Library/_URL_Enrich_Log.md

Usage:
  source ~/.env-secrets
  python3 enrich_url_stub_notes.py --dry-run --limit 5
  python3 enrich_url_stub_notes.py --limit 20
  python3 enrich_url_stub_notes.py
"""
import os
import re
import json
import time
import argparse
import urllib.request
import urllib.error
from datetime import datetime

try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")
TRIAGE = os.path.join(RESOURCE_LIB, "_Stub_Triage.json")
LOG = os.path.join(RESOURCE_LIB, "_URL_Enrich_Log.md")
TODAY = datetime.now().strftime("%Y-%m-%d")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)

CONTENT_TYPES = {"bookmark", "api-doc", "tool-doc", "tutorial", "model-doc", "prompt",
                 "reference", "case-study", "script", "workflow", "project-idea",
                 "design-inspiration", "personal", "research", "doc"}
FORMS = {"saas-tool", "desktop-app", "browser-extension", "github-repo",
         "open-source-project", "api-service", "youtube-video", "tiktok", "article",
         "social-thread", "prompt", "workflow-diagram", "channel-study",
         "market-research", "model-spec", "design-reference", "project-idea",
         "dataset", "paper", "other"}

PROMPT = """You are cataloguing a saved bookmark for a personal knowledge vault.

The saved URL is: {url}
{context}

Use Google Search to identify what this link actually is. Then return ONLY a raw
JSON object (no markdown fences):

{{
  "verified": true,
  "form": "saas-tool",
  "content_type": "tool-doc",
  "summary": "2-3 factual sentences: what the linked tool/article/video/repo IS and what it does. No marketing fluff. If it is a GitHub repo, say what the code does.",
  "tags": ["topic-one", "topic-two", "topic-three"]
}}

Rules:
- verified=false if search cannot confirm the URL points to a real, live resource. Still give your best-guess summary from the URL/context and mark it inferred.
- form: ONE of {forms}
- content_type: ONE of {ctypes}. Never "extracted-knowledge".
- If it is or references a GitHub repo, form MUST be "github-repo".
- tags: 2-5 lowercase kebab-case topic tags (not UI words, not the artifact kind).
"""


def parse_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return {}, text
    raw, body = m.group(1), m.group(2)
    fm, key = {}, None
    for line in raw.split("\n"):
        if re.match(r"^\s*-\s+", line) and key:
            fm.setdefault(key, [])
            if not isinstance(fm[key], list):
                fm[key] = []
            fm[key].append(line.strip()[1:].strip().strip("\"'"))
            continue
        mm = re.match(r"^([A-Za-z_][\w -]*?):\s*(.*)$", line)
        if mm:
            key = mm.group(1).strip()
            val = mm.group(2).strip().strip("\"'")
            fm[key] = val if val else []
    return fm, body


def as_list(v):
    return [] if v is None else (v if isinstance(v, list) else [v])


def call_gemini(url, context):
    prompt = PROMPT.format(url=url, context=context,
                           forms=" | ".join(sorted(FORMS)),
                           ctypes=" | ".join(sorted(CONTENT_TYPES)))
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {"temperature": 0.2},
    }
    api = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_KEY}"
    req = urllib.request.Request(api, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                res = json.loads(r.read().decode())
            cand = (res.get("candidates") or [{}])[0]
            parts = cand.get("content", {}).get("parts")
            if not parts:
                fr = cand.get("finishReason", "no-parts")
                if attempt < 3:
                    time.sleep(4)
                    continue
                return {"_error": f"empty response ({fr})"}
            raw = "".join(p.get("text", "") for p in parts).strip()
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw).strip()
            m = re.search(r"\{.*\}", raw, re.S)
            return json.loads(m.group(0) if m else raw)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(15 * (attempt + 1))
                continue
            return {"_error": f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:160]}"}
        except Exception as e:
            if attempt < 3:
                time.sleep(5)
                continue
            return {"_error": str(e)[:160]}


def build_note(fm, body, url, data, note_stem="Untitled"):
    q = '"'
    title = fm.get("title") or note_stem.replace("-", " ")
    category = (fm.get("category") or "").strip()
    created = fm.get("created") or TODAY

    ctype = (data.get("content_type") or fm.get("type") or "bookmark")
    if ctype in ("extracted-knowledge", "", None) or ctype not in CONTENT_TYPES:
        ctype = "bookmark"
    form = data.get("form") if data.get("form") in FORMS else "other"
    summary = (data.get("summary") or "").strip().replace(q, "'")
    verified = bool(data.get("verified"))

    tags = as_list(fm.get("tags")) + [t for t in data.get("tags", []) if t]
    if form == "github-repo" and "github-repo" not in tags:
        tags = ["github-repo"] + tags
    if not verified and "unverified-link" not in tags:
        tags.append("unverified-link")
    seen = set()
    tags = [t for t in tags if not (t in seen or seen.add(t))]

    lines = ["---", f"title: {q}{title}{q}", f"type: {ctype}"]
    if category:
        lines.append(f"category: {category.lower()}")
    lines += [f"form: {form}", f"summary: {q}{summary}{q}", f"url: {q}{url}{q}",
              f"verified: {str(verified).lower()}", "tags:"]
    lines += [f"  - {t}" for t in tags]
    lines += [f"created: {created}", f"enriched: {TODAY}", "---", "", "## Summary",
              summary or "_no summary returned_"]
    if not verified:
        lines += ["", "> [!warning] Link not verified by search — summary is inferred from the URL."]
    return "\n".join(lines) + "\n"


def log(entries):
    header = not os.path.exists(LOG)
    with open(LOG, "a") as f:
        if header:
            f.write(f"# Resource Library — URL Enrich Log\n\nStarted {datetime.now().isoformat(timespec='seconds')}\n\n")
        for e in entries:
            f.write(e + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--throttle", type=float, default=3.0)
    ap.add_argument("--shard", default="0/1", help="I/N - process items where index %% N == I")
    args = ap.parse_args()

    if not GEMINI_KEY and not args.dry_run:
        raise SystemExit("GEMINI_API_KEY not set — run: source ~/.env-secrets")

    shard_i, shard_n = (int(x) for x in args.shard.split("/"))
    items = json.load(open(TRIAGE))["bucket2_url_enrich"]
    items = [it for idx, it in enumerate(items) if idx % shard_n == shard_i]
    done = failed = skipped = 0
    entries = []

    for it in items:
        if args.limit and (done + failed) >= args.limit:
            break
        p = os.path.join(RESOURCE_LIB, it["note"])
        if not os.path.exists(p):
            continue
        fm, body = parse_frontmatter(open(p, encoding="utf-8", errors="ignore").read())
        if fm.get("enriched"):
            skipped += 1
            continue
        url = it["url"]
        ctx_bits = []
        for k in ("Description", "description", "summary", "ai_description"):
            if fm.get(k):
                ctx_bits.append(f"Existing note says: {fm[k]}")
                break
        context = ("Extra context: " + " ".join(ctx_bits)) if ctx_bits else ""

        if args.dry_run:
            print(f"[dry] {it['note']}  <- {url}")
            done += 1
            continue

        print(f"[{done + failed + 1}] {it['note']}", flush=True)
        data = call_gemini(url, context)
        if data.get("_error") or not data.get("summary"):
            failed += 1
            entries.append(f"- FAIL `{it['note']}` <- {url}  ({data.get('_error', 'no summary')})")
            time.sleep(args.throttle)
            continue

        stem = os.path.splitext(os.path.basename(it["note"]))[0]
        open(p, "w").write(build_note(fm, body, url, data, stem))
        done += 1
        v = "" if data.get("verified") else " [UNVERIFIED]"
        entries.append(f"- ok `{it['note']}`{v}\n    - {url}\n    - {data['summary'][:120]}")
        if done % 20 == 0:
            log(entries); entries = []
            print(f"  ...{done} done, {failed} failed, {skipped} skipped")
        time.sleep(args.throttle)

    if entries:
        log(entries)
    print(f"\nURL enrich complete: {done} rewritten, {failed} failed, {skipped} already-enriched")
    if not args.dry_run:
        print(f"log: {LOG}")


if __name__ == "__main__":
    main()
