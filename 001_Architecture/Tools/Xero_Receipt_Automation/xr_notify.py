import json
import subprocess
from datetime import datetime
from pathlib import Path


def notification_count(record):
    return (
        len(record.get("review_items", []))
        + len(record.get("manual_items", []))
        + len(record.get("failure_items", []))
    )


def message_for(count):
    return f"Xero bot needs your attention on {count} items. Type /xero in Claude Code to review."


class NotifyStore:
    def __init__(self, data_dir):
        self.path = Path(data_dir) / "Notifications.jsonl"

    def decision(self, state, now):
        now_dt = datetime.fromisoformat(now.replace("Z", "+00:00"))
        count = 0
        for item in state.index["items"].values():
            if item.get("last_run_scheduled") and item.get("last_run_id") == state.index.get("last_run"):
                if item["state"] in {"pending_review", "needs_manual_portal_lookup", "failed_retryable", "failed_permanent"}:
                    count += 1
        if count == 0:
            return {"decision": "SKIP", "reason": "nothing needs Tony"}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                sent = datetime.fromisoformat(row["utc_time"].replace("Z", "+00:00"))
                if sent.isocalendar()[:2] == now_dt.isocalendar()[:2]:
                    return {"decision": "SKIP", "reason": "notification already sent this ISO week"}
        return {"decision": "SEND", "message": message_for(count)}

    def record_sent(self, channel, result, now):
        row = {
            "channel": channel,
            "result": result,
            "utc_time": now if "T" in now else datetime.fromtimestamp(float(now)).isoformat(),
        }
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, sort_keys=True) + "\n")


def send_macos(message):
    script = 'display notification "{}" with title "Xero Receipt Automation"'.format(message.replace('"', '\\"'))
    return subprocess.run(["/usr/bin/osascript", "-e", script], check=True, capture_output=True, text=True).stdout
