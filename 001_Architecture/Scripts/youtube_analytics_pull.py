"""Pull real YouTube channel + analytics numbers for every logged-in channel.

Uses the OAuth tokens created by youtube_analytics_auth.py
(~/.config/agent-os-youtube/token_<label>.json). A channel whose token has
gone stale (Testing-mode refresh tokens expire 7 days after login, fixed,
not reset by use) is reported by name, not silently skipped or crashed on --
rerun youtube_analytics_auth.py <label> to fix it.

Usage:
  python3 youtube_analytics_pull.py                  # all channels, last 28 days
  python3 youtube_analytics_pull.py --days 7          # last 7 days instead
  python3 youtube_analytics_pull.py neon_parcel glyphary   # just these channels

Writes 001_Architecture/Logs/YouTube_Analytics_<YYYY-MM-DD>.json (full detail)
and prints a plain summary table to stdout.
"""
import argparse
import datetime
import glob
import json
import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CONFIG_DIR = os.path.expanduser("~/.config/agent-os-youtube")
WORKSPACE = os.path.expanduser("~/Documents/Agent-OS")
LOG_DIR = os.path.join(WORKSPACE, "001_Architecture", "Logs")


def all_labels():
    paths = sorted(glob.glob(os.path.join(CONFIG_DIR, "token_*.json")))
    return [os.path.basename(p)[len("token_"):-len(".json")] for p in paths]


def load_credentials(label):
    path = os.path.join(CONFIG_DIR, f"token_{label}.json")
    with open(path) as f:
        data = json.load(f)
    creds = Credentials.from_authorized_user_info(data)
    creds.refresh(Request())  # raises google.auth.exceptions.RefreshError if dead
    return creds


def pull_channel(label, days):
    result = {"label": label, "ok": False}
    try:
        creds = load_credentials(label)
    except Exception as exc:
        result["error"] = "login expired or revoked"
        result["fix"] = f"python3 001_Architecture/Scripts/youtube_analytics_auth.py {label}"
        result["detail"] = str(exc)[:200]
        return result

    try:
        yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
        ch = yt.channels().list(part="snippet,statistics", mine=True).execute()
        if not ch.get("items"):
            result["error"] = "no channel found for this login (wrong account picked?)"
            return result
        item = ch["items"][0]
        stats = item["statistics"]

        end = datetime.date.today()
        start = end - datetime.timedelta(days=days)
        yta = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
        report = yta.reports().query(
            ids="channel==MINE",
            startDate=start.isoformat(),
            endDate=end.isoformat(),
            metrics="views,estimatedMinutesWatched,subscribersGained,subscribersLost,likes,comments",
        ).execute()
        row = (report.get("rows") or [[0, 0, 0, 0, 0, 0]])[0]

        result.update({
            "ok": True,
            "title": item["snippet"]["title"],
            "channel_id": item["id"],
            "lifetime_subscribers": int(stats.get("subscriberCount", 0)),
            "lifetime_views": int(stats.get("viewCount", 0)),
            "lifetime_video_count": int(stats.get("videoCount", 0)),
            "window_days": days,
            "window_views": row[0],
            "window_watch_minutes": row[1],
            "window_subscribers_gained": row[2],
            "window_subscribers_lost": row[3],
            "window_net_subscribers": row[2] - row[3],
            "window_likes": row[4],
            "window_comments": row[5],
        })
    except HttpError as exc:
        result["error"] = f"YouTube API error: {exc.resp.status if exc.resp else '?'}"
        result["detail"] = str(exc)[:300]
    except Exception as exc:
        result["error"] = type(exc).__name__
        result["detail"] = str(exc)[:300]
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("channels", nargs="*", help="channel labels; default = every logged-in channel")
    ap.add_argument("--days", type=int, default=28, help="analytics window, default 28 days")
    args = ap.parse_args()

    labels = args.channels or all_labels()
    if not labels:
        print("No YouTube channels logged in. Run youtube_analytics_auth.py <label> first.", file=sys.stderr)
        sys.exit(1)

    results = [pull_channel(label, args.days) for label in labels]

    ok = [r for r in results if r["ok"]]
    failed = [r for r in results if not r["ok"]]

    print(f"\n{'Channel':<26} {'Subs':>9} {'Lifetime Views':>15} {f'Views ({args.days}d)':>14} {'Watch Hrs':>10} {'Net Subs':>9}")
    print("-" * 90)
    for r in sorted(ok, key=lambda x: -x["window_views"]):
        print(f"{r['title']:<26} {r['lifetime_subscribers']:>9,} {r['lifetime_views']:>15,} "
              f"{r['window_views']:>14,} {r['window_watch_minutes']/60:>10,.1f} {r['window_net_subscribers']:>+9}")

    if failed:
        print(f"\n{len(failed)} channel(s) need attention:")
        for r in failed:
            print(f"  - {r['label']}: {r['error']}" + (f"  -> {r['fix']}" if "fix" in r else ""))

    os.makedirs(LOG_DIR, exist_ok=True)
    out_path = os.path.join(LOG_DIR, f"YouTube_Analytics_{datetime.date.today().isoformat()}.json")
    with open(out_path, "w") as f:
        json.dump({"pulled_at": datetime.datetime.now().isoformat(), "window_days": args.days,
                   "results": results}, f, indent=2)
    print(f"\nFull detail written to {out_path}")


if __name__ == "__main__":
    main()
