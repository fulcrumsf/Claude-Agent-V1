import json
from pathlib import Path


REQUIRED_CONFIG = {
    "tenant_alias": str,
    "tenant_id": str,
    "timezone": str,
    "data_dir": str,
    "intake_dir": str,
    "archive_dir": str,
    "live_enabled": bool,
    "xero_targets": dict,
    "weekly_lookback_days": int,
    "gmail_window_days": int,
    "gmail_accounts": list,
    "gmail_byte_source": str,
    "thresholds": dict,
    "max_auto_attach_per_run": int,
    "correction_hold_days": int,
    "max_file_mb": int,
    "max_attachments_per_doc": int,
    "archive_date_format": str,
    "archive_gmail_sourced": bool,
    "notify": dict,
    "eligible_bank_accounts": list,
}


def load_config(path, data_dir=None, intake_dir=None, archive_dir=None):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = [name for name, kind in REQUIRED_CONFIG.items() if not isinstance(config.get(name), kind)]
    if missing:
        raise ValueError("config missing or invalid fields: " + ", ".join(missing))
    if config["gmail_byte_source"] not in {"none", "gmail_api"}:
        raise ValueError("gmail_byte_source must be none or gmail_api")
    # Receipts attach only to Spend Money lines on these accounts (Tony's expense credit cards). Fails closed.
    for entry in config["eligible_bank_accounts"]:
        if not isinstance(entry, dict) or not (entry.get("account_id") or entry.get("name")):
            raise ValueError("each eligible_bank_accounts entry needs a name or an account_id")
    if not isinstance(config.get("no_receipt_contacts", []), list):
        raise ValueError("no_receipt_contacts must be a list of contact names")
    # Optional, default off. Like live_enabled: flip to true only for one approved run, then back to false.
    if not isinstance(config.get("auto_archive_enabled", False), bool):
        raise ValueError("auto_archive_enabled must be true or false")
    cap = config.get("max_auto_archive_per_run", 10)
    if not isinstance(cap, int) or isinstance(cap, bool) or cap < 0:
        raise ValueError("max_auto_archive_per_run must be a whole number")
    if "auto_reconcile_enabled" in config:
        raise ValueError(
            "auto_reconcile_enabled is not supported: Xero's public API cannot read the Reconcile queue, "
            "read Bank Rules, or reconcile statement lines (see README 'Auto-reconcile'). Remove the key."
        )
    thresholds = config["thresholds"]
    for name in ("auto_min_score", "auto_min_lead", "review_min_score"):
        if not isinstance(thresholds.get(name), (int, float)):
            raise ValueError(f"threshold.{name} is required")
    for override, name in ((data_dir, "data_dir"), (intake_dir, "intake_dir"), (archive_dir, "archive_dir")):
        if override is not None:
            config[name] = str(override)
    for name in ("data_dir", "intake_dir", "archive_dir"):
        directory = Path(config[name]).expanduser()
        if not directory.is_dir():
            raise FileNotFoundError(f"{name} does not exist: {directory}")
    if not Path(path).is_file():
        raise FileNotFoundError(f"config does not exist: {path}")
    return config


def config_paths(config):
    return {
        "data": Path(config["data_dir"]).expanduser(),
        "intake": Path(config["intake_dir"]).expanduser(),
        "archive": Path(config["archive_dir"]).expanduser(),
    }
