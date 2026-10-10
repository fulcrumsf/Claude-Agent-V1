import re
from datetime import datetime
from pathlib import Path

from xr_extract import extract_text, parse_extraction


RECEIPT_SUBJECT = re.compile(r"(receipt|invoice|payment|order|billing)", re.I)


def load_aliases(path):
    return Path(path).read_text(encoding="utf-8")


def vendor_for(contact_name, aliases):
    normalized = (contact_name or "").lower()
    for vendor, entry in aliases.items():
        names = [vendor.lower()] + [name.lower() for name in entry.get("name_aliases", [])]
        if any(name and name in normalized for name in names):
            return vendor
    return None


def domain_for(sender, aliases):
    address = (sender or "").lower()
    local, _, domain = address.partition("@")
    domain = domain or local
    for vendor, entry in aliases.items():
        if domain in {item.lower() for item in entry.get("sender_domains", [])}:
            return vendor
    return None


def date_score(candidate_date, transaction_date):
    if not candidate_date:
        return 0.0
    try:
        delta = abs((datetime.fromisoformat(candidate_date) - datetime.fromisoformat(transaction_date)).days)
    except ValueError:
        return 0.0
    if delta <= 2:
        return 0.20
    if delta <= 5:
        return 0.12
    if delta <= 7:
        return 0.05
    return 0.0


def score_candidate(transaction, candidate, aliases):
    signals = {}
    text = " ".join([candidate.get("body_text", ""), candidate.get("subject", ""), candidate.get("sender", "")])
    parsed = parse_extraction(text)
    exact_amount = money_key(transaction) in parsed["money"]
    signals["amount"] = 0.40 if exact_amount else 0.0
    vendor = domain_for(candidate.get("sender"), aliases) or vendor_for(transaction.get("contact_name"), aliases)
    text_vendor = vendor_for(candidate.get("subject") or "", aliases) or vendor_for(candidate.get("body_text", ""), aliases)
    if vendor and text_vendor == vendor:
        signals["vendor"] = 0.30
    elif vendor or text_vendor:
        signals["vendor"] = 0.15
    else:
        signals["vendor"] = 0.0
    signals["date"] = date_score(candidate.get("date"), transaction["date"])
    attachments = candidate.get("attachments", [])
    receipt_evidence = bool(attachments) or bool(RECEIPT_SUBJECT.search(candidate.get("subject", "")))
    signals["receipt_evidence"] = 0.10 if receipt_evidence else 0.0
    score = round(sum(signals.values()), 2)
    return score, signals, exact_amount, vendor


def money_key(transaction):
    """(currency, amount): an amount only matches in the transaction's own currency."""
    return (transaction.get("currency") or "USD", float(transaction["total"]))


def byte_evidence(transaction, candidate, max_file_mb):
    path = candidate.get("staged_fixture") or candidate.get("staged_path") or candidate.get("path")
    if not path or not Path(path).is_file():
        return None
    size = Path(path).stat().st_size
    if size > max_file_mb * 1024 * 1024:
        return None
    extraction = extract_text(path)
    if extraction["confidence"] not in ("text", "ocr"):
        return None
    parsed = parse_extraction(extraction["text"])
    if money_key(transaction) not in parsed["money"]:
        return None
    return {"path": str(Path(path)), "confidence": extraction["confidence"], "text": extraction["text"], "size": size}


def classify(transaction, candidates, aliases, config, vendor_holds=None, max_attachments=10):
    vendor_holds = vendor_holds or {}
    scored = []
    for candidate in candidates:
        score, signals, exact_amount, vendor = score_candidate(transaction, candidate, aliases)
        evidence = byte_evidence(transaction, candidate, config["max_file_mb"])
        if evidence:
            import hashlib
            evidence["sha256"] = hashlib.sha256(Path(evidence["path"]).read_bytes()).hexdigest()
        scored.append({**candidate, "score": score, "signals": signals, "exact_amount": exact_amount, "vendor": vendor, "byte_evidence": evidence})
    scored.sort(key=lambda item: item["score"], reverse=True)
    best = scored[0] if scored else None
    runner_up = scored[1]["score"] if len(scored) > 1 else 0.0
    lead = round((best["score"] if best else 0.0) - runner_up, 2)
    transaction_vendor = vendor_for(transaction["contact_name"], aliases)
    thresholds = config["thresholds"]
    if best:
        auto = (
            best["score"] >= thresholds["auto_min_score"]
            and lead >= thresholds["auto_min_lead"]
            and best["exact_amount"]
            and best["signals"].get("vendor", 0.0) >= 0.30
            and best["byte_evidence"] is not None
            and best["byte_evidence"]["confidence"] == "text"
            and transaction_vendor not in vendor_holds
            and transaction.get("attachment_count", 0) < max_attachments
        )
        if auto:
            return "auto_eligible", scored, best, lead
        if best["score"] >= thresholds["review_min_score"]:
            return "pending_review", scored, best, lead
    if not candidates and transaction_vendor and aliases.get(transaction_vendor, {}).get("gmail_less"):
        return "needs_manual_portal_lookup", scored, None, 0.0
    return "no_candidate", scored, None, 0.0
