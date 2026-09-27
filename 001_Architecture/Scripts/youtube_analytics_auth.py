"""One-time OAuth grant for YouTube Data + Analytics read access.

Google ties the "acting as" Brand Account identity to each individual grant,
so this needs to run once per channel even though all channels share the
same Google login (fulcrumsf@gmail.com) - pick the right channel/brand at
the Google account chooser each time.

Usage: python3 youtube_analytics_auth.py <label>
  e.g. python3 youtube_analytics_auth.py reimagined_realms
Produces ~/.config/agent-os-youtube/token_<label>.json
"""
import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

CONFIG_DIR = os.path.expanduser("~/.config/agent-os-youtube")
CLIENT_SECRET_PATH = os.path.join(CONFIG_DIR, "client_secret.json")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 youtube_analytics_auth.py <label>")
        sys.exit(1)
    label = sys.argv[1]
    token_path = os.path.join(CONFIG_DIR, f"token_{label}.json")

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
    creds = flow.run_local_server(port=0, open_browser=False)
    with open(token_path, "w") as f:
        f.write(creds.to_json())
    os.chmod(token_path, 0o600)
    print(f"Saved refresh token to {token_path}")


if __name__ == "__main__":
    main()
