"""One-time OAuth login for the Etsy Open API v3 (Ikigai Portal etsy_draft step).

Uses the approved "agent-OS" Etsy app. Keystring and shared secret come from
~/.env-secrets (ETSY_CLIENT_ID = keystring). Never print them or the tokens.

Usage:
  python3 etsy_auth.py --name ikigai        # log in as the Ikigai shop owner
  python3 etsy_auth.py --name boredomad     # a different Etsy login, separate token file
  python3 etsy_auth.py --name ikigai --refresh   # swap the refresh token for a new access token

Scopes are fixed to the approved minimum: listings_w listings_r shops_r.
The callback URL http://localhost:3003/oauth/redirect must be registered on the app.
Tokens are saved to ~/.config/agent-os-etsy/token_<name>.json (mode 600).
"""
import argparse
import base64
import hashlib
import json
import os
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN_DIR = os.path.expanduser("~/.config/agent-os-etsy")
SECRETS_FILE = os.path.expanduser("~/.env-secrets")
SCOPES = "listings_w listings_r shops_r"
PORT = 3003
PRINT_URL = "--print-url" in sys.argv
REDIRECT_URI = f"http://localhost:{PORT}/oauth/redirect"
CONNECT_URL = "https://www.etsy.com/oauth/connect"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"


def key_var(name):
    """Each Etsy login owns its own app. borednomad uses the original app's keys."""
    return "ETSY_CLIENT_ID" if name == "borednomad" else f"ETSY_{name.upper()}_CLIENT_ID"


def keystring(name):
    """Read the app's keystring from the environment or ~/.env-secrets without echoing it."""
    var = key_var(name)
    value = os.environ.get(var, "")
    if not value and os.path.exists(SECRETS_FILE):
        with open(SECRETS_FILE) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"export {var}="):
                    value = line.split("=", 1)[1].strip().strip("'\"")
    if not value:
        sys.exit(f"{var} is empty in ~/.env-secrets")
    return value


def token_path(name):
    return os.path.join(TOKEN_DIR, f"token_{name}.json")


def save_token(name, data):
    os.makedirs(TOKEN_DIR, mode=0o700, exist_ok=True)
    path = token_path(name)
    with open(path, "w") as f:
        json.dump(data, f)
    os.chmod(path, 0o600)
    print(f"Saved token to {path} (scopes: {data.get('scope')}, expires_in: {data.get('expires_in')}s)")


def post_token(fields):
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        TOKEN_URL, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def login(name):
    client_id = keystring(name)
    verifier = secrets.token_urlsafe(64)[:100]
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(24)
    result = {}
    done = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/oauth/redirect":
                self.send_response(404)
                self.end_headers()
                return
            params = dict(urllib.parse.parse_qsl(parsed.query))
            result.update(params)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Etsy login received. You can close this tab and return to the terminal.")
            done.set()

        def log_message(self, *args):
            pass

    server = HTTPServer(("localhost", PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    query = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        },
        quote_via=urllib.parse.quote,
    )
    url = f"{CONNECT_URL}?{query}"
    print("Opening your browser to approve the app on Etsy...")
    if not webbrowser.open(url):
        print("The browser did not open. Re-run with --print-url to show the link (it contains the app keystring).")
        if PRINT_URL:
            print(url)

    if not done.wait(timeout=300):
        server.shutdown()
        sys.exit("Timed out after 5 minutes waiting for the Etsy approval.")
    server.shutdown()

    if "error" in result:
        sys.exit(f"Etsy returned an error: {result.get('error')}: {result.get('error_description')}")
    if result.get("state") != state:
        sys.exit("State mismatch, stopping (possible tampering).")

    data = post_token(
        {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "code": result["code"],
            "code_verifier": verifier,
        }
    )
    save_token(name, data)


def refresh(name):
    client_id = keystring(name)
    with open(token_path(name)) as f:
        old = json.load(f)
    data = post_token(
        {"grant_type": "refresh_token", "client_id": client_id, "refresh_token": old["refresh_token"]}
    )
    save_token(name, data)


def main():
    parser = argparse.ArgumentParser(description="Etsy OAuth login for the agent-OS app")
    parser.add_argument("--name", required=True, help="label for this Etsy login, e.g. ikigai")
    parser.add_argument("--refresh", action="store_true", help="refresh instead of a new login")
    parser.add_argument("--print-url", action="store_true", help="print the login link if the browser does not open")
    args = parser.parse_args()
    refresh(args.name) if args.refresh else login(args.name)


if __name__ == "__main__":
    main()
