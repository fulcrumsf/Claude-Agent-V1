import base64
import hashlib
import json
import secrets
import subprocess
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


class FakeGmailSource:
    def __init__(self, fixtures_dir):
        self.data = json.loads((Path(fixtures_dir) / "Fixture_Gmail_Candidates.json").read_text(encoding="utf-8"))

    def candidates(self):
        return self.data["items"]


class GmailClient:
    BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me"

    def __init__(self, access_token, account_label):
        self.access_token = access_token
        self.account_label = account_label

    def search(self, query, page_size=10):
        params = urllib.parse.urlencode({"q": query, "maxResults": min(page_size, 10)})
        request = urllib.request.Request(
            f"{self.BASE_URL}/threads?{params}",
            headers={"Authorization": f"Bearer {self.access_token}", "Accept": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read())

    def message(self, message_id, format_name="FULL"):
        params = urllib.parse.urlencode({"format": format_name})
        request = urllib.request.Request(
            f"{self.BASE_URL}/messages/{message_id}?{params}",
            headers={"Authorization": f"Bearer {self.access_token}", "Accept": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read())

    def attachment(self, message_id, attachment_id):
        request = urllib.request.Request(
            f"{self.BASE_URL}/messages/{message_id}/attachments/{attachment_id}",
            headers={"Authorization": f"Bearer {self.access_token}", "Accept": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return base64.urlsafe_b64decode(json.loads(response.read())["data"])


GMAIL_KEYCHAIN_SERVICE = "agent-os-xero-gmail"
TOKEN_URL = "https://oauth2.googleapis.com/token"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"


def authorize(client_id, client_secret, redirect_port=5036):
    """Browser + local-callback PKCE flow for a Gmail read-only refresh token.
    Opens the system browser; Tony signs in and approves. Returns the refresh_token."""
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(24)
    query = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": f"http://localhost:{redirect_port}/callback",
        "scope": READONLY_SCOPE,
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    })
    subprocess.run(["/usr/bin/open", f"{AUTH_URL}?{query}"], check=True)
    captured = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            values = urllib.parse.parse_qs(parsed.query)
            captured.update({key: value[0] for key, value in values.items()})
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Gmail authorization complete. You may close this window.\n")

        def log_message(self, format, *args):
            return

    server = HTTPServer(("127.0.0.1", redirect_port), Handler)
    server.handle_request()
    if captured.get("state") != state:
        raise RuntimeError("Gmail authorization state mismatch")
    if "error" in captured:
        raise RuntimeError(f"Gmail authorization denied: {captured['error']}")
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": captured["code"],
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": f"http://localhost:{redirect_port}/callback",
        "code_verifier": verifier,
    }).encode()
    request = urllib.request.Request(TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(request, timeout=30) as response:
        token = json.loads(response.read())
    if "refresh_token" not in token:
        raise RuntimeError(
            "Google did not return a refresh_token (it only issues one on first consent); "
            "revoke prior access at https://myaccount.google.com/permissions and retry"
        )
    return token["refresh_token"]


def access_token(client_id, client_secret, refresh_token):
    """Read-only (gmail.readonly) access token from a refresh token kept in the Keychain."""
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }).encode()
    request = urllib.request.Request(TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())["access_token"]


def attachment_parts(payload):
    """Yield (filename, mime, attachment_id) for every file part of a Gmail message payload."""
    stack = [payload or {}]
    while stack:
        part = stack.pop()
        stack.extend(part.get("parts", []))
        body = part.get("body", {})
        if part.get("filename") and body.get("attachmentId"):
            yield part["filename"], part.get("mimeType", ""), body["attachmentId"]


def fetch_candidate_bytes(client, candidate):
    """Exact bytes of the first PDF/image attachment named in the candidate, or None."""
    wanted = {item.get("filename") for item in candidate.get("attachments", [])}
    message = client.message(candidate["message_id"], "full")
    for filename, mime, attachment_id in attachment_parts(message.get("payload")):
        if filename in wanted and (mime == "application/pdf" or mime.startswith("image/")):
            return filename, client.attachment(candidate["message_id"], attachment_id)
    return None
