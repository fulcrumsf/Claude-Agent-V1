"""One-time OAuth grant for Google Drive (Ikigai Portal package step).

Uses a Desktop OAuth client from the info@borednomad.com Google Cloud project
(Agent OS, gen-lang-client-0251496109, Internal audience), saved at ~/.config/agent-os-drive/client_secret.json.
Sign in as info@borednomad.com, owner of the "Ikigai Digital Studio" Drive folder.

Usage: python3 google_drive_auth.py
Produces ~/.config/agent-os-drive/token.json (mode 600). Never print its contents.
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow

TOKEN_DIR = os.path.expanduser("~/.config/agent-os-drive")
CLIENT_SECRET_PATH = os.path.join(TOKEN_DIR, "client_secret.json")
TOKEN_PATH = os.path.join(TOKEN_DIR, "token.json")
SCOPES = ["https://www.googleapis.com/auth/drive"]


def main():
    os.makedirs(TOKEN_DIR, mode=0o700, exist_ok=True)
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    os.chmod(TOKEN_PATH, 0o600)
    print(f"Saved refresh token to {TOKEN_PATH}")


if __name__ == "__main__":
    main()
