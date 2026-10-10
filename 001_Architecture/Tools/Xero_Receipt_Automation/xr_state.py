import fcntl
import json
import os
from datetime import datetime, timezone


TERMINAL = {"archived", "already_attached", "excluded", "rejected"}
# Classification outcomes; a later run (new Gmail candidates, a manual drop) may re-classify between them.
CLASSES = {"auto_eligible", "pending_review", "needs_manual_portal_lookup", "no_candidate"}
FAILED = {"failed_retryable", "failed_permanent"}
TRANSITIONS = {
    "discovered": {"search_planned"},
    "search_planned": {"candidates_received"},
    "candidates_received": set(CLASSES),
    "auto_eligible": CLASSES | {"upload_pending", "already_attached"} | FAILED,
    "approved": {"upload_pending", "pending_review", "already_attached"} | FAILED,
    "upload_pending": {"uploaded_unverified"} | FAILED,
    "uploaded_unverified": {"verified", "pending_review"} | FAILED,
    "verified": {"archived", "verified_not_archived", "correction_logged"} | FAILED,
    "already_attached": {"archived", "verified_not_archived"},
    "archived": {"correction_logged"},
    "pending_review": CLASSES | {"approved", "rejected", "correction_logged"},
    "needs_manual_portal_lookup": CLASSES | {"correction_logged"},
    "no_candidate": CLASSES | {"correction_logged"},
    "verified_not_archived": {"archived"} | FAILED,
    "correction_logged": {"removed_confirmed"},
    "removed_confirmed": {"pending_review", "excluded"},
    "failed_retryable": CLASSES,
    "failed_permanent": set(),
}
# States that `match` may (re-)classify on a later run.
RECLASSIFIABLE = {"candidates_received", "failed_retryable"} | CLASSES


def utc_now():
    return datetime.now(timezone.utc)


def iso_utc(value=None):
    return (value or utc_now()).isoformat()


class StateStore:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.audit_path = data_dir / "Audit_Log.jsonl"
        self.index_path = data_dir / "State_Index.json"
        self.corrections_path = data_dir / "Corrections.jsonl"
        self.notifications_path = data_dir / "Notifications.jsonl"
        self.overrides_path = data_dir / "Vendor_Overrides.json"
        self.index = self._load_index()

    def _load_index(self):
        if self.index_path.exists():
            return json.loads(self.index_path.read_text(encoding="utf-8"))
        return {"items": {}, "last_run": None}

    def save(self):
        self.index_path.write_text(json.dumps(self.index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def append(self, record):
        record = dict(record)
        record["utc_time"] = iso_utc()
        with self.audit_path.open("a", encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            stream.write(json.dumps(record, sort_keys=True) + "\n")

    def discover(self, run_id, transaction, dry_run=False):
        item_id = transaction["item_id"]
        if item_id in self.index["items"]:
            record = self.index["items"][item_id]
            if record["state"] in TERMINAL:
                return None
            record["run_id"] = run_id
            record["dry_run"] = dry_run
            return record
        record = {
            "item_id": item_id,
            "state": "discovered",
            "run_id": run_id,
            "transaction": transaction,
            "dry_run": dry_run,
        }
        self.index["items"][item_id] = record
        self.append({**record, "event": "discovered"})
        return record

    def transition(self, item_id, new_state, run_id, dry_run=False, **details):
        record = self.index["items"].get(item_id)
        if record is None:
            raise KeyError(f"unknown item {item_id}")
        old_state = record["state"]
        leaves_terminal_ok = (old_state == "archived" and new_state == "correction_logged") or (
            old_state == "already_attached" and new_state in {"archived", "verified_not_archived"}
        )
        if old_state in TERMINAL and not leaves_terminal_ok:
            raise ValueError(f"terminal item {item_id} cannot leave {old_state}")
        if new_state != old_state and new_state not in TRANSITIONS.get(old_state, set()):
            raise ValueError(f"invalid transition {old_state} -> {new_state} for {item_id}")
        record.update(details)
        record["state"] = new_state
        record["run_id"] = run_id
        event = {
            "event": "transition",
            "run_id": run_id,
            "item_id": item_id,
            "from_state": old_state,
            "to_state": new_state,
            "dry_run": dry_run,
        }
        for key in ("sha256", "score", "signals", "attachment_id", "filename", "source"):
            if key in details:
                event[key] = details[key]
        self.append(event)
        return record

    def items_in(self, states):
        return [record for record in self.index["items"].values() if record["state"] in states]

    def append_jsonl(self, path, record):
        row = dict(record)
        row["utc_time"] = iso_utc()
        with path.open("a", encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            stream.write(json.dumps(row, sort_keys=True) + "\n")

    def vendor_holds(self, now=None):
        now = now or utc_now()
        holds = {}
        if self.overrides_path.exists():
            data = json.loads(self.overrides_path.read_text(encoding="utf-8"))
        else:
            data = {}
        for vendor, entry in data.items():
            until = datetime.fromisoformat(entry["review_only_until"])
            if until.tzinfo is None:
                until = until.replace(tzinfo=timezone.utc)
            if until >= now:
                holds[vendor] = entry
        return holds

    def set_vendor_hold(self, vendor, days, note="correction", now=None):
        now = now or utc_now()
        data = {}
        if self.overrides_path.exists():
            data = json.loads(self.overrides_path.read_text(encoding="utf-8"))
        until = now.timestamp() + days * 86400
        data[vendor] = {
            "review_only_until": datetime.fromtimestamp(until, timezone.utc).isoformat(),
            "reason": note,
        }
        self.overrides_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return data[vendor]

    def clear_vendor_hold(self, vendor):
        if not self.overrides_path.exists():
            return
        data = json.loads(self.overrides_path.read_text(encoding="utf-8"))
        data.pop(vendor, None)
        self.overrides_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def archive_name(transaction, vendor_display, extension):
    date = datetime.fromisoformat(transaction["date"]).strftime(transaction.get("archive_date_format", "%m-%d-%Y"))
    amount = f"{float(transaction['total']):.2f}"
    safe_vendor = "".join(character if character.isalnum() or character in "-_." else "-" for character in vendor_display)
    return f"{date}_{safe_vendor}_{amount}.{extension}"


def safe_filename(name, fallback):
    forbidden = '<>:"/\\|?*\0'
    cleaned = "".join("_" if character in forbidden else character for character in name)
    cleaned = cleaned.strip()
    return cleaned or fallback
