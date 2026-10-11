import json
from pathlib import Path


def review_json(state):
    needs = []
    auto = []
    manual = []
    other = []
    for item_id in sorted(state.index["items"]):
        item = state.index["items"][item_id]
        entry = {
            "item_id": item_id,
            "transaction": item.get("transaction", {}),
            "score": item.get("score"),
            "signals": item.get("signals", {}),
            "state": item["state"],
            "filename": item.get("filename"),
            "attachment_id": item.get("attachment_id"),
            "runner_up_score": item.get("runner_up_score"),
            "bank_account": (item.get("transaction") or {}).get("bank_account"),
            "gmail_archive": item.get("gmail_archive"),
            "flags": item_flags(item),
        }
        if item["state"] == "pending_review":
            needs.append(entry)
        elif item["state"] in {"archived", "verified", "uploaded_unverified", "correction_logged"} and item.get("auto"):
            auto.append(entry)
        elif item["state"] == "needs_manual_portal_lookup":
            manual.append(entry)
        else:
            other.append(entry)
    return {
        "needs_approval": needs,
        "auto_attached_this_week": auto,
        "manual_portal": manual,
        "other": other,
        "flagged": [entry for entry in needs + auto + manual + other if entry["flags"]],
    }


def item_flags(item):
    """Plain-language notes Tony should see under an item in /xero."""
    flags = []
    if item.get("phantom_transfer"):
        flags.append(item.get("reason", "Likely Etsy-integration phantom transfer; do not reconcile."))
    if item.get("ineligible_bank_account"):
        flags.append(item.get("reason", "Not on an eligible expense credit card; receipts are never attached here."))
    archive = item.get("gmail_archive") or {}
    if archive.get("status") == "untagged":
        flags.append(archive.get("note"))
    elif archive.get("status") == "failed":
        flags.append(f"Gmail archive failed: {archive.get('reason')}")
    return flags


def render_markdown(review):
    lines = [
        "# Xero Receipt Review",
        "",
        f"Needs your approval: {len(review['needs_approval'])}",
    ]
    for number, item in enumerate(review["needs_approval"], 1):
        transaction = item["transaction"]
        lines.append(f"- {number}. {transaction.get('date')} {transaction.get('contact_name')} ${transaction.get('total')} ({transaction.get('type')}) score {item.get('score')}")
    lines.extend(["", f"Already auto-attached this week: {len(review['auto_attached_this_week'])}"])
    for item in review["auto_attached_this_week"]:
        lines.append(f"- {item['item_id']} {item.get('filename')} score {item.get('score')}")
    lines.extend(["", f"Manual portal lookups: {len(review['manual_portal'])}"])
    lines.extend(["", f"No candidate / failures / verified-not-archived: {len(review['other'])}"])
    lines.extend(["", f"Flagged for Tony: {len(review.get('flagged', []))}"])
    for item in review.get("flagged", []):
        transaction = item["transaction"]
        for flag in item["flags"]:
            lines.append(f"- {transaction.get('date')} {transaction.get('contact_name')} ${transaction.get('total')}: {flag}")
    return "\n".join(lines) + "\n"


def write_report(data_dir, run_id, review):
    path = Path(data_dir) / f"Run_{run_id}_Report.md"
    path.write_text(render_markdown(review), encoding="utf-8")
    return path


def calibration(state):
    corrections = []
    path = state.corrections_path
    if path.exists():
        corrections = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    by_kind = {}
    for row in corrections:
        by_kind[row["kind"]] = by_kind.get(row["kind"], 0) + 1
    attached = [item for item in state.index["items"].values() if item.get("attachment_id")]
    return {
        "auto_attached_count": len(attached),
        "corrections_by_kind": by_kind,
        "precision_by_vendor": {},
    }
