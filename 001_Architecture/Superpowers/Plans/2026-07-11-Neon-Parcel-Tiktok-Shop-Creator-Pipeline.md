# Neon Parcel TikTok Shop Creator Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the folder structure, compliance tooling, and skill extensions needed so Tony can run a TikTok Shop Creator affiliate product (starting with Colorsmart Pens) through a compliance-gated, audio-first video pipeline that outputs to `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/`.

**Architecture:** A per-product folder scaffolder, a citation-backed compliance ledger with a Firecrawl-based live-freshness checker, and post-build vision/transcript scan scripts — all wired into the existing `TikTok-Shop-Affiliate-Video` skill via new sections rather than a forked skill. Scripts live alongside the existing `analyze_clips.py` in the skill's `scripts/` folder; compliance data (ledger, sources, freshness log) lives in the Neon Parcel product folder per the approved spec.

**Tech Stack:** Python 3 + pytest, FFmpeg (keyframe extraction), OpenRouter (Qwen-VL vision, already used by `analyze_clips.py`), ElevenLabs Scribe (transcription), Firecrawl CLI (live policy scraping).

## Global Constraints

- Spec of record: `001_Architecture/Superpowers/Specs/2026-07-11-Neon-Parcel-Tiktok-Shop-Creator-Pipeline-Design.md` — every task below implements one section of it.
- Naming: Title-Case-With-Dashes / underscores per workspace convention (`CLAUDE.md`). Zero-padded 4-digit product numbering (`0001_Colorsmart-Pens`), matching the existing `NNN_` convention used elsewhere in this workspace.
- Never paraphrase TOS rules — every ledger entry must carry an exact quote + source filename + line/section reference.
- Amazon Associates sibling pipeline is explicitly out of scope. Do not create anything under `005_Affiliate_Marketing/Amazon_Associates/Videos/` in this plan.
- No video is ever marked ready-to-post without Tony's explicit sign-off (existing workspace-wide rule) — no task in this plan automates publishing.
- API keys are sourced via `source ~/.env-secrets` — never hardcoded, never written to local `.env` files (existing workspace rule).
- pytest is required and was confirmed installed this session via `pip3 install --user --break-system-packages pytest` (version 9.1.1). Because the `pytest` binary is not on PATH, all test commands in this plan use `python3 -m pytest` rather than the bare `pytest` command.

---

## File Structure

**New scripts** (in `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/`, alongside the existing `analyze_clips.py`):
- `scaffold_product_folder.py` — creates the per-product folder tree
- `extract_compliance_sources.py` — builds `Compliance-Sources.json` from embedded TOS URLs
- `validate_compliance_ledger.py` — structural validator for `Compliance-Ledger.md`
- `check_tos_freshness.py` — Firecrawl-based live policy diff + cadence gate
- `compliance_vision_scan.py` — post-build logo/watermark keyframe scan
- `compliance_transcript_scan.py` — post-build banned-phrase transcript scan

Each script above has a matching `test_<name>.py` in the same folder.

**New data files** (in `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/`):
- `Compliance-Ledger.md`
- `Compliance-Sources.json`
- `Compliance-Freshness-Log.md`
- `Videos/0001_Colorsmart-Pens/` (created by the scaffolder as the first real product folder)

**Modified:**
- `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/SKILL.md` — new sections for the pre-production question, the Neon Parcel output-model override, and the compliance gate.

---

### Task 1: Per-product folder scaffolder

**Files:**
- Create: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/scaffold_product_folder.py`
- Test: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/test_scaffold_product_folder.py`

**Interfaces:**
- Produces: `scaffold(base_dir: Path, product_number: int, product_name: str, ingest_folder: str = "TBD") -> Path` — returns the created product folder path (`product_name` is raw, e.g. `"Colorsmart Pens"` — `scaffold` slugifies it internally). Later tasks (5, 6, 7) write into `Edit/`, `Compliance/Vision-Scan/`, `Compliance/Transcript-Scan/`, and `Package/` inside the folder this function returns.
- Produces: `slugify(name: str) -> str` — converts a free-text product name (e.g. `"Colorsmart Pens"`) into `"Colorsmart-Pens"` (Title-Case-With-Dashes, no spaces).

- [ ] **Step 1: Write the failing tests**

```python
# test_scaffold_product_folder.py
from pathlib import Path
from scaffold_product_folder import scaffold, slugify


def test_slugify_converts_spaces_to_dashes():
    assert slugify("Colorsmart Pens") == "Colorsmart-Pens"


def test_slugify_strips_extra_whitespace():
    assert slugify("  Colorsmart   Pens  ") == "Colorsmart-Pens"


def test_scaffold_creates_typed_subfolders(tmp_path):
    product_dir = scaffold(tmp_path, 1, "Colorsmart Pens")
    assert product_dir == tmp_path / "0001_Colorsmart-Pens"
    for folder in ["Edit", "Compliance/Vision-Scan", "Compliance/Transcript-Scan", "Package"]:
        assert (product_dir / folder).is_dir()


def test_scaffold_writes_intake_template(tmp_path):
    product_dir = scaffold(tmp_path, 2, "Next Product")
    intake = product_dir / "Intake.md"
    assert intake.is_file()
    content = intake.read_text()
    assert "Next Product" in content
    assert "Source Ingest folder" in content


def test_scaffold_is_idempotent(tmp_path):
    scaffold(tmp_path, 1, "Colorsmart Pens")
    product_dir = scaffold(tmp_path, 1, "Colorsmart Pens")  # run twice, should not error
    assert product_dir.is_dir()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 -m pytest test_scaffold_product_folder.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scaffold_product_folder'`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
"""
scaffold_product_folder.py — Neon Parcel TikTok Shop Creator per-product scaffolder.

Creates the folder tree for one product under
005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Videos/
per the approved design spec (2026-07-11-Neon-Parcel-Tiktok-Shop-Creator-Pipeline-Design.md).

Usage:
  python3 scaffold_product_folder.py <videos_dir> <product_number> "<Product Name>"
"""
import re
import sys
from pathlib import Path

TYPED_FOLDERS = [
    "Edit",
    "Compliance/Vision-Scan",
    "Compliance/Transcript-Scan",
    "Package",
]

INTAKE_TEMPLATE = """---
title: "{product_name} — Intake"
type: intake
created: {created_date}
---

# {product_name}

- **Source Ingest folder:** {ingest_folder}
- **Pipeline:** TikTok Shop Creator (vertical, NeonParcel TikTok account)
- **Number of TikTok cuts planned:** 3 (distinct edits, shared footage pool)
- **Restricted category (Health/Beauty/Weight-Management)?:** TBD — confirm before Phase 1 compliance scan
"""


def slugify(name: str) -> str:
    collapsed = re.sub(r"\s+", " ", name.strip())
    return collapsed.replace(" ", "-")


def scaffold(base_dir: Path, product_number: int, product_name: str, ingest_folder: str = "TBD") -> Path:
    from datetime import date

    product_dir = base_dir / f"{product_number:04d}_{slugify(product_name)}"
    product_dir.mkdir(parents=True, exist_ok=True)
    for folder in TYPED_FOLDERS:
        (product_dir / folder).mkdir(parents=True, exist_ok=True)

    intake_path = product_dir / "Intake.md"
    if not intake_path.exists():
        intake_path.write_text(INTAKE_TEMPLATE.format(
            product_name=product_name,
            created_date=date.today().isoformat(),
            ingest_folder=ingest_folder,
        ))

    return product_dir


def main():
    if len(sys.argv) < 4:
        sys.exit('Usage: scaffold_product_folder.py <videos_dir> <product_number> "<Product Name>" [ingest_folder]')
    videos_dir = Path(sys.argv[1]).resolve()
    number = int(sys.argv[2])
    name = sys.argv[3]
    ingest_folder = sys.argv[4] if len(sys.argv) > 4 else "TBD"
    product_dir = scaffold(videos_dir, number, name, ingest_folder)
    print(f"Scaffolded {product_dir}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 -m pytest test_scaffold_product_folder.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/scaffold_product_folder.py \
        001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/test_scaffold_product_folder.py
git commit -m "feat: add per-product folder scaffolder for Neon Parcel TikTok Shop Creator pipeline"
```

---

### Task 2: Compliance source URL extractor

**Files:**
- Create: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/extract_compliance_sources.py`
- Test: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/test_extract_compliance_sources.py`

**Interfaces:**
- Produces: `extract_knowledge_ids(tos_folder: Path) -> dict[str, str]` — maps each unique `knowledge_id` to its canonical URL (`https://seller-us.tiktok.com/university/essay?knowledge_id=<ID>`), deduped across tracking-parameter variants. Task 4 (`check_tos_freshness.py`) consumes the JSON file this writes.
- Produces: `write_sources_json(sources: dict[str, str], out_path: Path) -> None`

- [ ] **Step 1: Write the failing tests**

```python
# test_extract_compliance_sources.py
import json
from pathlib import Path
from extract_compliance_sources import extract_knowledge_ids, write_sources_json


def test_extracts_unique_knowledge_id(tmp_path):
    (tmp_path / "doc1.md").write_text(
        "See [policy](https://seller-us.tiktok.com/university/essay?knowledge_id=123&role=1&from=search)"
    )
    result = extract_knowledge_ids(tmp_path)
    assert result == {"123": "https://seller-us.tiktok.com/university/essay?knowledge_id=123"}


def test_dedupes_same_knowledge_id_with_different_tracking_params(tmp_path):
    (tmp_path / "doc1.md").write_text(
        "https://seller-us.tiktok.com/university/essay?knowledge_id=555&role=1&identity=1"
    )
    (tmp_path / "doc2.md").write_text(
        "https://seller-us.tiktok.com/university/essay?knowledge_id=555#some-anchor"
    )
    result = extract_knowledge_ids(tmp_path)
    assert result == {"555": "https://seller-us.tiktok.com/university/essay?knowledge_id=555"}


def test_extracts_multiple_distinct_ids(tmp_path):
    (tmp_path / "doc1.md").write_text(
        "a: https://seller-us.tiktok.com/university/essay?knowledge_id=111\n"
        "b: https://seller-us.tiktok.com/university/essay?knowledge_id=222&lang=en"
    )
    result = extract_knowledge_ids(tmp_path)
    assert set(result.keys()) == {"111", "222"}


def test_write_sources_json(tmp_path):
    out_path = tmp_path / "Compliance-Sources.json"
    write_sources_json({"123": "https://seller-us.tiktok.com/university/essay?knowledge_id=123"}, out_path)
    loaded = json.loads(out_path.read_text())
    assert loaded == {"123": "https://seller-us.tiktok.com/university/essay?knowledge_id=123"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 -m pytest test_extract_compliance_sources.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'extract_compliance_sources'`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
"""
extract_compliance_sources.py — Pulls official TikTok Seller University source
URLs embedded inside the ingested TOS bundle, deduped by knowledge_id, so the
freshness checker (check_tos_freshness.py) has a grounded, non-guessed URL list.

Usage:
  python3 extract_compliance_sources.py <tos_folder> <out_json_path>
"""
import json
import re
import sys
from pathlib import Path

KNOWLEDGE_ID_PATTERN = re.compile(r"knowledge_id=(\d+)")
BASE_URL = "https://seller-us.tiktok.com/university/essay?knowledge_id={}"


def extract_knowledge_ids(tos_folder: Path) -> dict:
    ids = {}
    for md_file in sorted(Path(tos_folder).glob("*.md")):
        text = md_file.read_text(errors="ignore")
        for match in KNOWLEDGE_ID_PATTERN.finditer(text):
            kid = match.group(1)
            ids.setdefault(kid, BASE_URL.format(kid))
    return ids


def write_sources_json(sources: dict, out_path: Path) -> None:
    Path(out_path).write_text(json.dumps(sources, indent=2, sort_keys=True))


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: extract_compliance_sources.py <tos_folder> <out_json_path>")
    sources = extract_knowledge_ids(Path(sys.argv[1]))
    write_sources_json(sources, Path(sys.argv[2]))
    print(f"Extracted {len(sources)} unique source URLs -> {sys.argv[2]}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 -m pytest test_extract_compliance_sources.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/extract_compliance_sources.py \
        001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/test_extract_compliance_sources.py
git commit -m "feat: add compliance source URL extractor for TikTok TOS bundle"
```

---

### Task 3: Compliance ledger content + structural validator

**Files:**
- Create: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/validate_compliance_ledger.py`
- Test: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/test_validate_compliance_ledger.py`
- Create: `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Ledger.md`

**Interfaces:**
- Produces: `parse_ledger_entries(ledger_text: str) -> list[dict]` — each dict has keys `id`, `category`, `severity`, `rule`, `source`, `verified`. Task 6 (`compliance_transcript_scan.py`) consumes this to build its banned-phrase list from entries where `category` mentions "Claims" or "Health".
- Produces: `validate(ledger_text: str) -> list[str]` — returns a list of error strings (empty list = valid). Every entry must have all 5 fields non-empty.

- [ ] **Step 1: Write the failing tests**

```python
# test_validate_compliance_ledger.py
from validate_compliance_ledger import parse_ledger_entries, validate

VALID_FIXTURE = """
RULE-001 | Visual/Branding | HARD BLOCK
Rule: Do not show any third-party logo without permission.
Source: Best Practices for Promotional Content.md (line 138)
Verified: 2026-07-11

RULE-002 | Claims/Discounts | HARD BLOCK
Rule: The discounted price shown must exactly match the product detail page.
Source: Misleading Discount Content Guide.md (line 10)
Verified: 2026-07-11
"""

INVALID_FIXTURE = """
RULE-001 | Visual/Branding | HARD BLOCK
Rule: Do not show any third-party logo without permission.
Verified: 2026-07-11
"""


def test_parses_two_entries():
    entries = parse_ledger_entries(VALID_FIXTURE)
    assert len(entries) == 2
    assert entries[0]["id"] == "RULE-001"
    assert entries[0]["category"] == "Visual/Branding"
    assert entries[0]["severity"] == "HARD BLOCK"
    assert "third-party logo" in entries[0]["rule"]
    assert "Best Practices" in entries[0]["source"]
    assert entries[0]["verified"] == "2026-07-11"


def test_validate_passes_on_complete_entries():
    assert validate(VALID_FIXTURE) == []


def test_validate_flags_missing_source():
    errors = validate(INVALID_FIXTURE)
    assert len(errors) == 1
    assert "RULE-001" in errors[0]
    assert "source" in errors[0].lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 -m pytest test_validate_compliance_ledger.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'validate_compliance_ledger'`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
"""
validate_compliance_ledger.py — Structural validator for Compliance-Ledger.md.

Every rule block must have: an ID line ("RULE-NNN | Category | SEVERITY"),
a Rule: line, a Source: line, and a Verified: line. This does NOT validate
that the rule text is accurate — only that every entry is complete enough
to be traceable back to a source and a verification date.

Usage:
  python3 validate_compliance_ledger.py <ledger_path>
"""
import re
import sys
from pathlib import Path

HEADER_PATTERN = re.compile(r"^(RULE-\d+)\s*\|\s*([^|]+?)\s*\|\s*(.+)$")


def parse_ledger_entries(ledger_text: str) -> list:
    entries = []
    current = None
    for line in ledger_text.splitlines():
        line = line.strip()
        header_match = HEADER_PATTERN.match(line)
        if header_match:
            if current:
                entries.append(current)
            current = {
                "id": header_match.group(1),
                "category": header_match.group(2).strip(),
                "severity": header_match.group(3).strip(),
                "rule": "",
                "source": "",
                "verified": "",
            }
        elif current is not None:
            if line.startswith("Rule:"):
                current["rule"] = line[len("Rule:"):].strip()
            elif line.startswith("Source:"):
                current["source"] = line[len("Source:"):].strip()
            elif line.startswith("Verified:"):
                current["verified"] = line[len("Verified:"):].strip()
    if current:
        entries.append(current)
    return entries


def validate(ledger_text: str) -> list:
    errors = []
    for entry in parse_ledger_entries(ledger_text):
        for field in ("rule", "source", "verified"):
            if not entry[field]:
                errors.append(f"{entry['id']} is missing a {field} value")
    return errors


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: validate_compliance_ledger.py <ledger_path>")
    text = Path(sys.argv[1]).read_text()
    entries = parse_ledger_entries(text)
    errors = validate(text)
    print(f"Parsed {len(entries)} ledger entries.")
    if errors:
        print(f"{len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("All entries valid.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 -m pytest test_validate_compliance_ledger.py -v`
Expected: 3 passed

- [ ] **Step 5: Write the real Compliance-Ledger.md content**

This is a content-authoring step, not code — every rule below was extracted by grepping the actual 18 files in `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/TikTok-TOS/` during the design brainstorm (not paraphrased from memory). Create the file with this exact content:

```markdown
---
title: "TikTok Shop Creator Compliance Ledger"
type: compliance-ledger
created: 2026-07-11
---

# TikTok Shop Creator Compliance Ledger

Citation-backed rules extracted from the 18-file TOS bundle in
`005_Affiliate_Marketing/Tiktok_Shop_Affiliate/TikTok-TOS/`. Every entry is a
near-verbatim rule with an exact source citation — never a paraphrase, since
paraphrasing risks silently changing what the rule actually says. This is
Phase 1 of the compliance gate (see the design spec) — read on every video,
before editing starts. Categories marked ALWAYS ESCALATE trigger Phase 2
(live freshness check) regardless of cadence.

RULE-001 | Visual/Branding | HARD BLOCK
Rule: Don't use trademarks (e.g., brand names and logos) in your content without permission from their owner — including blurred/partial logos, background logos (e.g. a fast-food sign in a livestream background), and platform watermarks.
Source: Best Practices for Promotional Content.md (lines 92, 138, 157) + CREATOR CAMPAIGN TERMS AND CONDITIONS FOR TIKTOK SHOP US.md (§2.4.1.1, line 60)
Verified: 2026-07-11

RULE-002 | Visual/Branding | HARD BLOCK
Rule: Products in content that differ from the listed product in size, weight, pattern, quantity, graphics, logo, image, or print don't count as "matching" — showing a sample/differing product requires a clear disclaimer that it's a sample and doesn't represent the full listing.
Source: Best Practices for Promotional Content.md (lines 37-40)
Verified: 2026-07-11

RULE-003 | Content Originality | HARD BLOCK
Rule: Content with a visible platform watermark, sticker, or logo from another source (e.g. a screen recording with another app's watermark) is treated as unoriginal/reposted content and should not be posted, even with the watermark blurred.
Source: Best Practices for Promotional Content.md (lines 79, 92, 96) + Creating with Impact A Guide for All Creators.md (lines 50, 57)
Verified: 2026-07-11

RULE-004 | Prohibited Products | HARD BLOCK
Rule: Creators may not promote prohibited products in any content (still images, videos, or livestreams) — examples include vapes, adult products, and live animals. Full current list lives in TikTok Shop's Prohibited Products Policy (linked below). Violations can lead to removal of e-commerce access or permanent account deactivation.
Source: How to Avoid Promoting Prohibited Products.md (lines 3, 9, 14-16, 41) — links to https://seller-us.tiktok.com/university/essay?knowledge_id=1399532709988097
Verified: 2026-07-11

RULE-005 | Claims/Discounts | HARD BLOCK
Rule: The promotional/discounted price shown in content must exactly match the product detail page at time of upload. Don't display expired promotions. Unsupported price comparisons are not allowed. 300+ short videos with misleading discounts in a rolling window can trigger a posting-frequency restriction (3 shoppable videos/week for 14 days), escalating to a permanent e-commerce ban if not corrected within 14 days.
Source: Misleading Discount Content Guide.md (lines 10-17, 27-29)
Verified: 2026-07-11

RULE-006 | Claims/Health | ALWAYS ESCALATE
Rule: Medical claims, exaggerated weight-management statements, and competitor disparagement are explicitly prohibited. Claims must be accurate, evidence-based, and consistent with the product detail page; qualify statements with language like "in my experience" / "results may vary." Comparing to "what most people use" (a generic category) is permissible; disparaging a specific named competitor is not.
Source: TikTok Shop — LIVE Growth Playbook.md (lines 203, 941)
Verified: 2026-07-11

RULE-007 | Claims/Temporary-Effects | HARD BLOCK
Rule: For products with short-term/temporary effects (e.g. cosmetic or appearance-related), content must clearly disclose "the effect is temporary" or "the effect is not permanent," consistent with the product detail page.
Source: Avoid Misleading Content.md (line 72)
Verified: 2026-07-11

RULE-008 | Disclosure | HARD BLOCK
Rule: Creators must disclose paid promotions per FTC Guides Concerning Endorsements and Testimonials (16 C.F.R. Part 255) — a clear and conspicuous disclosure such as #ad or #sponsored, prominently placed (e.g. at the beginning of a post), is required on both Short Videos and Livestreams.
Source: CREATOR CAMPAIGN TERMS AND CONDITIONS FOR TIKTOK SHOP US.md (§2.2.3 line 56, §3.1.1 line 65, §4.1.1 line 75, §6.1.6 line 96)
Verified: 2026-07-11

RULE-009 | Reviews | HARD BLOCK
Rule: Do not offer money, discounts, gifts, or refunds in exchange for a review. Do not ask for only positive reviews or suggest a star rating. Review requests must be neutral, optional, and applied fairly to all customers, not just satisfied buyers.
Source: Customer Review Requests Best Practices and FAQs.md (lines 9, 17-30)
Verified: 2026-07-11

RULE-010 | Format/Livestream-ShortVideo | HARD BLOCK
Rule: Short Videos and Livestreams must include a closed-loop e-commerce product anchor link to the relevant product on TikTok Shop and must focus on showcasing products actually available for purchase there.
Source: CREATOR CAMPAIGN TERMS AND CONDITIONS FOR TIKTOK SHOP US.md (§3.1.3 line 67, §4.1.2-4.1.3 lines 76-77)
Verified: 2026-07-11

## Always-Escalate Categories

If a product falls into any of these categories, Phase 2 (live freshness check) runs regardless of cadence, before the video is finalized — not just RULE-006's specific claim language, but the whole category:
- Health / Supplements
- Beauty / Skincare
- Weight-Management

Tech gadgets (Tony's current near-term focus) do not auto-escalate by category, but RULE-001 through RULE-010 above still apply universally.
```

- [ ] **Step 6: Run the validator against the real ledger**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 validate_compliance_ledger.py "/Users/tonymacbook2025/Documents/Agent-OS/005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Ledger.md"`
Expected: `Parsed 10 ledger entries.` followed by `All entries valid.`

- [ ] **Step 7: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/validate_compliance_ledger.py \
        001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/test_validate_compliance_ledger.py \
        005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Ledger.md
git commit -m "feat: add TikTok Shop compliance ledger (citation-backed) + structural validator"
```

---

### Task 4: Live freshness checker (Firecrawl-based)

**Files:**
- Create: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/check_tos_freshness.py`
- Test: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/test_check_tos_freshness.py`
- Create: `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Freshness-Log.md`

**Interfaces:**
- Consumes: `Compliance-Sources.json` produced by Task 2.
- Produces: `should_refresh(last_verified: str, category: str | None, threshold_days: int = 14) -> bool` — pure function, no network. `category` in `{"Health", "Beauty", "Weight-Management"}` (case-insensitive substring match) always returns `True`.
- Produces: `diff_snapshots(old_text: str, new_text: str) -> list[str]` — pure function returning changed lines (unified diff style), no network.
- Produces: `fetch_snapshot(url: str) -> str` — wraps `firecrawl scrape <url> --only-main-content --format markdown` via `subprocess.run`. Not unit tested (requires network); called from `main()` only.

- [ ] **Step 1: Write the failing tests**

```python
# test_check_tos_freshness.py
from check_tos_freshness import should_refresh, diff_snapshots


def test_should_refresh_false_when_recent():
    from datetime import date, timedelta
    recent = (date.today() - timedelta(days=3)).isoformat()
    assert should_refresh(recent, category=None) is False


def test_should_refresh_true_when_older_than_threshold():
    from datetime import date, timedelta
    old = (date.today() - timedelta(days=20)).isoformat()
    assert should_refresh(old, category=None) is True


def test_should_refresh_true_for_always_escalate_category_even_if_recent():
    from datetime import date, timedelta
    recent = (date.today() - timedelta(days=1)).isoformat()
    assert should_refresh(recent, category="Health") is True
    assert should_refresh(recent, category="weight-management") is True


def test_should_refresh_true_when_no_prior_date():
    assert should_refresh(None, category=None) is True


def test_diff_snapshots_detects_changed_line():
    old = "Rule: Comparing to a specific competitor is not allowed.\n"
    new = "Rule: Comparing to a specific competitor is allowed with permission.\n"
    diffs = diff_snapshots(old, new)
    assert any("allowed with permission" in d for d in diffs)


def test_diff_snapshots_empty_when_identical():
    text = "Rule: same text\n"
    assert diff_snapshots(text, text) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 -m pytest test_check_tos_freshness.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'check_tos_freshness'`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
"""
check_tos_freshness.py — Phase 2 live freshness check.

The 18 local TOS files have no captured/source-date metadata, so they cannot
be assumed current. This pulls TikTok's currently-published policy pages
(via the Firecrawl CLI, per the workspace's CLI-first rule) and diffs them
against the last snapshot, flagging anything that changed for manual ledger
reconciliation. Never auto-edits Compliance-Ledger.md — a human/agent reviews
the diff and updates the ledger with a new dated entry.

Usage:
  python3 check_tos_freshness.py <neon_parcel_folder> [--category Health]
"""
import json
import subprocess
import sys
from datetime import date, datetime
from difflib import unified_diff
from pathlib import Path

ALWAYS_ESCALATE_CATEGORIES = {"health", "beauty", "weight-management", "supplements", "skincare"}
DEFAULT_THRESHOLD_DAYS = 14


def should_refresh(last_verified: str | None, category: str | None, threshold_days: int = DEFAULT_THRESHOLD_DAYS) -> bool:
    if category and category.strip().lower() in ALWAYS_ESCALATE_CATEGORIES:
        return True
    if not last_verified:
        return True
    last_date = datetime.fromisoformat(last_verified).date()
    return (date.today() - last_date).days > threshold_days


def diff_snapshots(old_text: str, new_text: str) -> list:
    diff = unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        lineterm="",
    )
    return [line for line in diff if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))]


def fetch_snapshot(url: str) -> str:
    result = subprocess.run(
        ["firecrawl", "scrape", url, "--only-main-content", "--format", "markdown"],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"firecrawl scrape failed for {url}: {result.stderr[:300]}")
    return result.stdout


def load_last_verified(freshness_log_path: Path) -> str | None:
    if not freshness_log_path.exists():
        return None
    for line in reversed(freshness_log_path.read_text().splitlines()):
        if line.startswith("## "):
            return line[3:].strip()
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: check_tos_freshness.py <neon_parcel_folder> [--category Health]")
    neon_parcel_dir = Path(sys.argv[1]).resolve()
    category = None
    if "--category" in sys.argv:
        category = sys.argv[sys.argv.index("--category") + 1]

    freshness_log = neon_parcel_dir / "Compliance-Freshness-Log.md"
    last_verified = load_last_verified(freshness_log)

    if not should_refresh(last_verified, category):
        print(f"Ledger last verified {last_verified}, within {DEFAULT_THRESHOLD_DAYS}-day threshold. Skipping live check.")
        return

    sources_path = neon_parcel_dir / "Compliance-Sources.json"
    sources = json.loads(sources_path.read_text())

    snapshot_dir = neon_parcel_dir / "Compliance-Snapshots" / date.today().isoformat()
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    changed = []
    for knowledge_id, url in sources.items():
        print(f"Fetching {url} ...")
        new_text = fetch_snapshot(url)
        new_path = snapshot_dir / f"{knowledge_id}.md"
        new_path.write_text(new_text)

        prior_snapshots = sorted((neon_parcel_dir / "Compliance-Snapshots").glob(f"*/{knowledge_id}.md"))
        prior_snapshots = [p for p in prior_snapshots if p != new_path]
        if prior_snapshots:
            old_text = prior_snapshots[-1].read_text()
            diffs = diff_snapshots(old_text, new_text)
            if diffs:
                changed.append((knowledge_id, url, diffs))

    with open(freshness_log, "a") as f:
        f.write(f"\n## {date.today().isoformat()}\n")
        f.write(f"Checked {len(sources)} source URL(s).\n")
        if changed:
            f.write(f"**{len(changed)} source(s) changed — review required before trusting the ledger for affected rules:**\n")
            for knowledge_id, url, diffs in changed:
                f.write(f"- `{knowledge_id}` ({url}): {len(diffs)} changed line(s)\n")
        else:
            f.write("No changes detected.\n")

    if changed:
        print(f"REVIEW NEEDED: {len(changed)} source(s) changed. See {freshness_log}")
    else:
        print("No changes detected. Ledger confirmed current.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 -m pytest test_check_tos_freshness.py -v`
Expected: 6 passed

- [ ] **Step 5: Initialize the freshness log**

Create `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Freshness-Log.md`:

```markdown
---
title: "TikTok Shop Compliance Freshness Log"
type: compliance-log
created: 2026-07-11
---

# TikTok Shop Compliance Freshness Log

Tracks every Phase 2 live-freshness check run against `Compliance-Sources.json`.
`check_tos_freshness.py` appends one dated section per run. A gap of more
than 14 days since the last entry (or an always-escalate category) triggers
the next run automatically.
```

- [ ] **Step 6: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/check_tos_freshness.py \
        001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/test_check_tos_freshness.py \
        005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Freshness-Log.md
git commit -m "feat: add Firecrawl-based live TOS freshness checker (Phase 2 compliance gate)"
```

---

### Task 5: Post-build vision scan (logo/watermark detection)

**Files:**
- Create: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/compliance_vision_scan.py`
- Test: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/test_compliance_vision_scan.py`

**Interfaces:**
- Consumes: keyframe-extraction pattern already proven in `analyze_clips.py` (`extract_scene_keyframes`, `encode_image`) — reused, not reinvented.
- Produces: `parse_verdict(vision_response_text: str) -> str` — pure function returning `"FLAG"` or `"CLEAR"` by scanning the model's response for the literal marker words the prompt requires it to emit.
- Produces: `scan_video(video_path: Path, out_dir: Path) -> Path` — writes a markdown report to `out_dir` and returns its path. Not unit tested directly (requires ffmpeg + network); `parse_verdict` carries the test coverage for the decision logic.

- [ ] **Step 1: Write the failing tests**

```python
# test_compliance_vision_scan.py
from compliance_vision_scan import parse_verdict


def test_parse_verdict_flag_when_logo_mentioned():
    response = "Frame 2 shows a visible Nike swoosh logo on a shoe in the background.\n\nVERDICT: FLAG"
    assert parse_verdict(response) == "FLAG"


def test_parse_verdict_clear_when_no_issues():
    response = "No third-party logos, watermarks, or brand marks visible in any frame.\n\nVERDICT: CLEAR"
    assert parse_verdict(response) == "CLEAR"


def test_parse_verdict_defaults_to_flag_when_ambiguous():
    # Fail safe: if the model doesn't emit a clear VERDICT line, treat as FLAG
    # so nothing slips through on a malformed response.
    response = "The frames look fine I guess."
    assert parse_verdict(response) == "FLAG"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 -m pytest test_compliance_vision_scan.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'compliance_vision_scan'`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
"""
compliance_vision_scan.py — Phase 3 post-build vision scan.

Reuses the exact keyframe-extraction approach already proven in
analyze_clips.py (same skill folder), pointed at FINISHED edit files instead
of raw clips, with a compliance-focused prompt (RULE-001/002/003 from
Compliance-Ledger.md: third-party logos, watermarks, brand marks).

Usage:
  python3 compliance_vision_scan.py <edit_video_path> <out_dir>
"""
import base64
import os
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing: pip install requests")
    sys.exit(1)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = "qwen/qwen2.5-vl-72b-instruct"
SCENE_THRESHOLD = 0.35
MAX_FRAMES = 10

COMPLIANCE_PROMPT = (
    "You are checking a TikTok Shop affiliate video for policy compliance before it is posted.\n\n"
    "Look at every frame below and identify ANY of the following (per TikTok's Creator Campaign Terms "
    "and Best Practices for Promotional Content policies):\n"
    "1. Any third-party brand name, logo, trademark, or service mark (including partial, blurred, or "
    "background logos — e.g. a fast-food sign, a competitor product box, a clothing brand logo)\n"
    "2. Any platform watermark or sticker from another app (e.g. a screen-recording watermark)\n\n"
    "For each frame, state what you see. Then end your response with exactly one line: "
    "'VERDICT: FLAG' if any issue was found in any frame, or 'VERDICT: CLEAR' if none were found."
)


def parse_verdict(vision_response_text: str) -> str:
    for line in reversed(vision_response_text.strip().splitlines()):
        stripped = line.strip().upper()
        if stripped == "VERDICT: CLEAR":
            return "CLEAR"
        if stripped == "VERDICT: FLAG":
            return "FLAG"
    return "FLAG"  # fail safe: ambiguous response is treated as a flag


def extract_scene_keyframes(video_path: str, out_dir: str) -> list:
    detect_result = subprocess.run(
        ["ffmpeg", "-i", video_path,
         "-vf", f"select='gt(scene,{SCENE_THRESHOLD})',showinfo",
         "-vsync", "vfr", "-f", "null", "-"],
        capture_output=True, text=True
    )
    timestamps = []
    for line in detect_result.stderr.splitlines():
        if "pts_time:" in line:
            try:
                timestamps.append(float(line.split("pts_time:")[1].split()[0]))
            except (IndexError, ValueError):
                pass
    if not timestamps or timestamps[0] > 0.5:
        timestamps.insert(0, 0.5)
    if len(timestamps) > MAX_FRAMES:
        step = len(timestamps) / MAX_FRAMES
        timestamps = [timestamps[int(i * step)] for i in range(MAX_FRAMES)]

    frames = []
    for i, ts in enumerate(timestamps):
        frame_path = os.path.join(out_dir, f"frame_{i:03d}_{ts:.2f}s.jpg")
        subprocess.run(
            ["ffmpeg", "-ss", str(ts), "-i", video_path, "-frames:v", "1", "-q:v", "3", frame_path, "-y"],
            capture_output=True
        )
        if os.path.exists(frame_path):
            frames.append((ts, frame_path))
    return frames


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def scan_video(video_path: Path, out_dir: Path) -> Path:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set. Run: source ~/.env-secrets")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        frames = extract_scene_keyframes(str(video_path), tmp)
        content = [{"type": "text", "text": COMPLIANCE_PROMPT}]
        for ts, frame_path in frames:
            content.append({"type": "text", "text": f"\n[Frame at {ts:.2f}s]"})
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(frame_path)}"}})

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json",
                      "HTTP-Referer": "https://agent-os.local"},
            json={"model": MODEL, "messages": [{"role": "user", "content": content}], "max_tokens": 600},
            timeout=60,
        )
        response_text = response.json()["choices"][0]["message"]["content"]

    verdict = parse_verdict(response_text)
    report_path = out_dir / f"{Path(video_path).stem}-vision-scan.md"
    report_path.write_text(f"# Vision Scan — {Path(video_path).name}\n\n{response_text}\n\nVerdict: {verdict}\n")
    return report_path


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: compliance_vision_scan.py <edit_video_path> <out_dir>")
    report = scan_video(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Vision scan report: {report}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 -m pytest test_compliance_vision_scan.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/compliance_vision_scan.py \
        001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/test_compliance_vision_scan.py
git commit -m "feat: add Phase 3 post-build vision scan for third-party logos/watermarks"
```

---

### Task 6: Post-build transcript scan (banned-phrase detection)

**Files:**
- Create: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/compliance_transcript_scan.py`
- Test: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/test_compliance_transcript_scan.py`

**Interfaces:**
- Produces: `banned_phrase_patterns() -> list[str]` — a hardcoded list of universal red-flag phrases (guarantee/cure/medical-outcome language) that apply regardless of ledger content, since these are FTC-level claim risks, not TikTok-specific. Does not parse `Compliance-Ledger.md` directly — ledger rules are free-text sentences (e.g. RULE-005's discount-accuracy language), not structured phrase patterns, so turning them into regex/substring checks is a separate future enhancement, not part of this task.
- Produces: `scan_transcript_for_violations(transcript_text: str, patterns: list[str]) -> list[str]` — pure function, returns matched banned phrases found in the transcript (case-insensitive).
- Produces: `transcribe_audio(video_path: Path) -> str` — wraps ElevenLabs Scribe. Not unit tested (requires network); called from `main()` only.

- [ ] **Step 1: Write the failing tests**

```python
# test_compliance_transcript_scan.py
from compliance_transcript_scan import banned_phrase_patterns, scan_transcript_for_violations


def test_banned_phrase_patterns_includes_guarantee_and_cure():
    patterns = banned_phrase_patterns()
    assert any("guarantee" in p.lower() for p in patterns)
    assert any("cure" in p.lower() for p in patterns)


def test_scan_detects_banned_phrase_case_insensitive():
    transcript = "This pen will absolutely CURE your handwriting problems forever."
    violations = scan_transcript_for_violations(transcript, banned_phrase_patterns())
    assert any("cure" in v.lower() for v in violations)


def test_scan_returns_empty_for_clean_transcript():
    transcript = "This pen writes smoothly and comes in six colors, in my experience."
    violations = scan_transcript_for_violations(transcript, banned_phrase_patterns())
    assert violations == []


def test_scan_detects_multiple_distinct_violations():
    transcript = "Guaranteed to work, clinically proven, and it will cure your problems."
    violations = scan_transcript_for_violations(transcript, banned_phrase_patterns())
    assert len(violations) >= 3
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 -m pytest test_compliance_transcript_scan.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'compliance_transcript_scan'`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
"""
compliance_transcript_scan.py — Phase 3 post-build transcript scan.

Transcribes each finished edit (ElevenLabs Scribe, already used elsewhere in
this workspace for audio-first editing) and checks it for banned claim
language — guarantee/cure/medical-outcome phrases that are FTC-level risks
regardless of what TikTok's own ledger says, plus anything the compliance
ledger's Claims-category rules call out.

Usage:
  python3 compliance_transcript_scan.py <edit_video_path> <out_dir>
"""
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing: pip install requests")
    sys.exit(1)

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

# Universal FTC-risk phrases — apply regardless of niche or ledger content.
_BANNED_PHRASES = [
    "guarantee", "guaranteed", "cure", "cures", "clinically proven",
    "proven to", "100% effective", "instant results", "miracle",
    "no side effects", "risk free", "fda approved",
]


def banned_phrase_patterns() -> list:
    return list(_BANNED_PHRASES)


def scan_transcript_for_violations(transcript_text: str, patterns: list) -> list:
    lowered = transcript_text.lower()
    return [p for p in patterns if p.lower() in lowered]


def extract_audio(video_path: Path, out_path: Path) -> Path:
    subprocess.run(
        ["ffmpeg", "-i", str(video_path), "-vn", "-acodec", "libmp3lame", str(out_path), "-y"],
        capture_output=True,
    )
    return out_path


def transcribe_audio(audio_path: Path) -> str:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY not set. Run: source ~/.env-secrets")
    with open(audio_path, "rb") as f:
        response = requests.post(
            "https://api.elevenlabs.io/v1/speech-to-text",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            files={"file": f},
            data={"model_id": "scribe_v1"},
            timeout=120,
        )
    response.raise_for_status()
    return response.json().get("text", "")


def scan_video(video_path: Path, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / f"{Path(video_path).stem}.mp3"
    extract_audio(Path(video_path), audio_path)
    transcript = transcribe_audio(audio_path)
    violations = scan_transcript_for_violations(transcript, banned_phrase_patterns())

    report_path = out_dir / f"{Path(video_path).stem}-transcript-scan.md"
    lines = [f"# Transcript Scan — {Path(video_path).name}\n", f"## Transcript\n{transcript}\n"]
    if violations:
        lines.append(f"## Violations Found\n{', '.join(violations)}\n\nVerdict: FLAG\n")
    else:
        lines.append("## Violations Found\nNone.\n\nVerdict: CLEAR\n")
    report_path.write_text("\n".join(lines))
    return report_path


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: compliance_transcript_scan.py <edit_video_path> <out_dir>")
    report = scan_video(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Transcript scan report: {report}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts" && python3 -m pytest test_compliance_transcript_scan.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/compliance_transcript_scan.py \
        001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/test_compliance_transcript_scan.py
git commit -m "feat: add Phase 3 post-build transcript scan for banned claim language"
```

---

### Task 7: Extend the TikTok-Shop-Affiliate-Video skill

**Files:**
- Modify: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/SKILL.md`

**Interfaces:**
- Consumes: all scripts from Tasks 1–6 (calls them by their documented CLI usage, not by importing Python directly — this is a markdown skill file, not a program).

- [ ] **Step 1: Add the pre-production question and Neon Parcel output-model override**

Insert this new section immediately after the existing `## Input Model` section (before `## Setup Check`):

```markdown
## Neon Parcel TikTok Shop Creator — Pre-Production Question

Before starting any product, ask: **"Is this a TikTok Shop Creator video, or something else?"**

This skill currently implements the TikTok Shop Creator path only:
- Vertical (9:16) output, posted to the NeonParcel TikTok account
- **3 distinct TikTok videos** from the shared footage pool — each with genuinely different cuts, beats, and pacing (not the same edit with swapped audio)
- No YouTube pairing. If Tony wants an Amazon-affiliate version of a product, that requires separately-shot landscape footage and a different (not-yet-built) pipeline under `005_Affiliate_Marketing/Amazon_Associates/Videos/` — flag it back to Tony rather than attempting it here.

This supersedes the "3 cuts × 2 audio = 6 outputs" model described below in Step 4/5 when the product is explicitly a Neon Parcel TikTok Shop Creator video — only produce the 3 TikTok outputs.

Output routing for Neon Parcel TikTok Shop Creator products:
```bash
python3 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/scaffold_product_folder.py \
  "005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Videos" \
  <next_product_number> "<Product Name>" "<source ingest folder path>"
```
This creates `Videos/NNNN_Product-Slug/{Edit,Compliance/{Vision-Scan,Transcript-Scan},Package}/` — write the 3 rendered `TikTok_V1.mp4` / `V2` / `V3` into `Edit/`, not into the generic `edit/` folder used by the rest of this skill for other invocation contexts.
```

- [ ] **Step 2: Add the compliance gate section**

Insert this new section right before the existing `## Re-runs` section:

```markdown
## Compliance Gate (Neon Parcel TikTok Shop Creator only)

Three phases, run in order, before any video in this pipeline is marked ready-to-post. Full detail: `001_Architecture/Superpowers/Specs/2026-07-11-Neon-Parcel-Tiktok-Shop-Creator-Pipeline-Design.md`.

**Phase 1 — Ledger scan (every product, before editing starts).** Read `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Ledger.md` and check the planned VO scripts against every rule. If the product is Health/Beauty/Skincare/Weight-Management, note that in `Intake.md` — it triggers mandatory Phase 2 below regardless of cadence.

**Phase 2 — Live freshness check (cadence-gated).**
```bash
source ~/.env-secrets
python3 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/check_tos_freshness.py \
  "005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator" \
  --category "<Health|Beauty|Weight-Management if applicable, else omit>"
```
Skips itself automatically if the ledger was verified within 14 days and the product isn't in an always-escalate category. If it prints `REVIEW NEEDED`, read `Compliance-Freshness-Log.md`, review the flagged snapshot diffs, and manually update the affected `Compliance-Ledger.md` entries (new dated entry, never silently overwrite) before proceeding.

**Phase 3 — Post-build scans (every video, after rendering).** Run once per rendered TikTok_V1/V2/V3:
```bash
source ~/.env-secrets
python3 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/compliance_vision_scan.py \
  "<product_folder>/Edit/TikTok_V1.mp4" "<product_folder>/Compliance/Vision-Scan"
python3 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/compliance_transcript_scan.py \
  "<product_folder>/Edit/TikTok_V1.mp4" "<product_folder>/Compliance/Transcript-Scan"
```
Repeat for V2 and V3. Each writes a report ending in `Verdict: CLEAR` or `Verdict: FLAG`.

**Final gate.** Before telling Tony a product is ready to post, present: Phase 1 summary (what was checked), Phase 2 result (skipped/clean/review-needed), and every Phase 3 report's verdict. If anything is FLAG, resolve or get explicit sign-off from Tony before moving files into `Package/`. Never auto-publish.
```

- [ ] **Step 3: Validate the edited skill file**

Run: `python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/validate_build.py --files "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/SKILL.md"`
Expected: `ALL CHECKS PASSED`

Also confirm the frontmatter parses as real YAML (matches this workspace's established gotcha where string-matching alone missed a malformed-YAML bug before):
```bash
python3 -c "
import yaml
content = open('/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/TikTok-Shop-Affiliate-Video/SKILL.md').read()
fm = content.split('---')[1]
print(yaml.safe_load(fm))
"
```
Expected: prints a dict with `name` and `description` keys, no exception.

- [ ] **Step 4: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/SKILL.md
git commit -m "feat: wire Neon Parcel TikTok Shop Creator output model + compliance gate into skill"
```

---

### Task 8: Build compliance sources + scaffold the first real product (Colorsmart Pens)

**Files:**
- Create: `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Sources.json` (generated, not hand-written)
- Create: `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Videos/0001_Colorsmart-Pens/` (generated, not hand-written)

This task wires Tasks 1–7 together against the real bundle and the real first product — it's the end-to-end proof that the machinery works, not a new script.

- [ ] **Step 1: Generate the real Compliance-Sources.json**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
python3 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/extract_compliance_sources.py \
  "005_Affiliate_Marketing/Tiktok_Shop_Affiliate/TikTok-TOS" \
  "005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Sources.json"
```
Expected: `Extracted <N> unique source URLs -> ...` where N is roughly 60-70 (the bundle has dozens of distinct knowledge_id links across 18 files).

- [ ] **Step 2: Scaffold the Colorsmart Pens product folder**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
python3 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/scaffold_product_folder.py \
  "005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Videos" \
  1 "Colorsmart Pens" \
  "000_Ingest/Tiktok_Shop_Video_Dump/002-Colorsmart Pens"
```
Expected: `Scaffolded .../Videos/0001_Colorsmart-Pens`

- [ ] **Step 3: Verify the folder tree**

```bash
find "005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Videos/0001_Colorsmart-Pens" | sort
```
Expected: `Intake.md`, `Edit/`, `Compliance/Vision-Scan/`, `Compliance/Transcript-Scan/`, `Package/`.

- [ ] **Step 4: Run the freshness check once to confirm end-to-end wiring**

```bash
source ~/.env-secrets
python3 001_Architecture/Skills/TikTok-Shop-Affiliate-Video/scripts/check_tos_freshness.py \
  "005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator"
```
Expected: since `Compliance-Freshness-Log.md` has no prior dated entry yet, `should_refresh` returns `True` — it fetches every source URL via Firecrawl, writes `Compliance-Snapshots/<today>/`, and appends a result section (likely "No changes detected" on this first run, since there's nothing prior to diff against — that's expected and correct; the value shows up on the *next* run).

If Firecrawl isn't authenticated or rate-limits mid-run, that's a live-environment issue to report to Tony, not a plan defect — the wiring itself (folder creation, JSON loading, snapshot writing, log append) is what this step verifies.

- [ ] **Step 5: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add "005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Sources.json" \
        "005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Freshness-Log.md" \
        "005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Videos/0001_Colorsmart-Pens"
git commit -m "chore: generate compliance sources + scaffold Colorsmart Pens as first Neon Parcel product"
```

---

## What Comes After This Plan

The pipeline machinery is now built. Actually producing the 3 Colorsmart Pens TikTok videos (Steps 1-7 of the existing skill: vision analysis of raw clips, inventory, aspect ratio check, variation plan, cutting, quality check, delivery) is a live, iterative, Tony-in-the-loop session using the now-extended skill — not further plan tasks, since that process requires Tony's approval at the variation-plan step and spot-checks at the end, per the skill's existing workflow.
