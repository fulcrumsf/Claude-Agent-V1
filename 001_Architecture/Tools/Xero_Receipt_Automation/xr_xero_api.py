import base64
import hashlib
import json
import secrets
import subprocess
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


class ForbiddenWrite(RuntimeError):
    pass


class SelectionPaused(RuntimeError):
    pass


class FakeXeroClient:
    def __init__(self, fixtures_dir, simulate_live=False):
        self.fixtures_dir = Path(fixtures_dir)
        self.simulate_live = simulate_live
        self.call_log = []
        self.attachments = {}
        self.bytes = {}
        self.bank_transactions = json.loads((self.fixtures_dir / "Fixture_Xero_BankTransactions.json").read_text(encoding="utf-8"))
        self.invoices = json.loads((self.fixtures_dir / "Fixture_Xero_Invoices.json").read_text(encoding="utf-8"))

    def list_bank_transactions(self, where=None):
        self.call_log.append(("GET", "BankTransactions"))
        return [dict(item) for item in self.bank_transactions if not self.attachments.get(item["ID"])]

    def list_invoices(self, where=None):
        self.call_log.append(("GET", "Invoices"))
        return [dict(item) for item in self.invoices if not self.attachments.get(item["ID"])]

    def get_transaction(self, endpoint, guid):
        self.call_log.append(("GET", f"{endpoint}/{guid}"))
        source = self.bank_transactions if endpoint == "BankTransactions" else self.invoices
        for item in source:
            if item["ID"] == guid:
                result = dict(item)
                result["HasAttachments"] = bool(self.attachments.get(guid))
                return result
        raise KeyError(guid)

    def list_attachments(self, endpoint, guid):
        self.call_log.append(("GET", f"{endpoint}/{guid}/Attachments"))
        return [dict(item) for item in self.attachments.get(guid, [])]

    def get_attachment(self, endpoint, guid, filename):
        self.call_log.append(("GET", f"{endpoint}/{guid}/Attachments/{filename}"))
        key = (guid, filename)
        if key not in self.bytes:
            raise KeyError(filename)
        return self.bytes[key]

    def post_attachment(self, endpoint, guid, filename, content, mime_type):
        self.call_log.append(("POST", f"{endpoint}/{guid}/Attachments/{filename}"))
        if not self.simulate_live:
            raise SelectionPaused("live writes require live_enabled and --live, with Tony's approved dry-run")
        existing = {item["FileName"] for item in self.attachments.get(guid, [])}
        if filename in existing:
            raise FileExistsError(filename)
        attachment_id = hashlib.sha256(f"{guid}:{filename}".encode()).hexdigest()[:18]
        item = {
            "AttachmentID": attachment_id,
            "FileName": filename,
            "MimeType": mime_type,
            "ContentLength": len(content),
        }
        self.attachments.setdefault(guid, []).append(item)
        self.bytes[(guid, filename)] = content
        return item

    def forbidden_http_write(self):
        raise ForbiddenWrite("only attachment POST is implemented")


class XeroClient:
    BASE_URL = "https://api.xero.com/api.xro/2.0"
    AUTH_URL = "https://login.xero.com/identity/connect/authorize"
    TOKEN_URL = "https://identity.xero.com/connect/token"
    CONNECTIONS_URL = "https://api.xero.com/connections"

    def __init__(self, client_id, tenant_id, refresh_token, secrets_reader=None):
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.refresh_token = refresh_token
        self.access_token = None
        self.secrets_reader = secrets_reader
        self.call_log = []

    def authorize(self, scopes, redirect_port=5035):
        verifier = secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        state = secrets.token_urlsafe(24)
        query = urllib.parse.urlencode({
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": f"http://localhost:{redirect_port}/callback",
            "scope": scopes,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        })
        subprocess.run(["/usr/bin/open", f"{self.AUTH_URL}?{query}"], check=True)
        captured = {}

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                values = urllib.parse.parse_qs(parsed.query)
                captured.update({key: value[0] for key, value in values.items()})
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Authorization complete. You may close this window.\n")

            def log_message(self, format, *args):
                return

        server = HTTPServer(("127.0.0.1", redirect_port), Handler)
        server.handle_request()
        if captured.get("state") != state:
            raise RuntimeError("authorization state mismatch")
        return captured["code"], verifier

    def request(self, method, url, data=None, headers=None, expected=(200,)):
        request = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
        attempts = 0
        while True:
            attempts += 1
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    body = response.read()
                    if response.status not in expected:
                        raise RuntimeError(f"unexpected Xero status {response.status}: {body[:300]!r}")
                    return response.status, body
            except urllib.error.HTTPError as error:
                if error.code == 429 and attempts < 3:
                    retry_after = float(error.headers.get("Retry-After", "1"))
                    time.sleep(min(retry_after, 30))
                    continue
                detail = error.read()[:300]
                raise RuntimeError(f"Xero {method} {url} failed: HTTP {error.code}: {detail!r}") from error

    @staticmethod
    def _parse_json(body, what):
        try:
            return json.loads(body)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"Xero response for {what} was not JSON ({len(body)} bytes): {body[:300]!r}") from error

    def refresh(self):
        data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.refresh_token,
        }).encode()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        _, body = self.request("POST", self.TOKEN_URL, data, headers)
        token = self._parse_json(body, "token refresh")
        self.access_token = token["access_token"]
        self.refresh_token = token.get("refresh_token", self.refresh_token)
        if self.secrets_reader:
            self.secrets_reader.save_refresh_token(self.tenant_id, self.refresh_token)
        return self.access_token

    def exchange_code(self, code, verifier, redirect_port=5035):
        data = urllib.parse.urlencode({
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "redirect_uri": f"http://localhost:{redirect_port}/callback",
            "code_verifier": verifier,
        }).encode()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        _, body = self.request("POST", self.TOKEN_URL, data, headers)
        token = self._parse_json(body, "code exchange")
        self.access_token = token["access_token"]
        self.refresh_token = token["refresh_token"]
        return token

    def list_connections(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        _, body = self.request("GET", self.CONNECTIONS_URL, headers=headers)
        return self._parse_json(body, "connections list")

    def get(self, endpoint, where=None, page=None):
        url = f"{self.BASE_URL}/{endpoint}"
        params = {key: value for key, value in (("where", where), ("page", page)) if value}
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Xero-tenant-id": self.tenant_id,
            "Accept": "application/json",
        }
        self.call_log.append(("GET", endpoint))
        _, body = self.request("GET", url, headers=headers)
        return json.loads(body)

    @staticmethod
    def normalize(raw):
        """Map Xero's JSON shape to the flat fields the pipeline uses."""
        return {
            "ID": raw.get("BankTransactionID") or raw.get("InvoiceID"),
            "Type": raw.get("Type", ""),
            "Status": raw.get("Status", ""),
            "Date": (raw.get("DateString") or "")[:10],
            "Total": raw.get("Total"),
            "CurrencyCode": raw.get("CurrencyCode", ""),
            "ContactName": (raw.get("Contact") or {}).get("Name", ""),
            "Reference": raw.get("Reference", ""),
            "IsReconciled": raw.get("IsReconciled", False),
            "HasAttachments": raw.get("HasAttachments", False),
        }

    def _list_paged(self, endpoint, where):
        items, page = [], 1
        while True:
            batch = self.get(endpoint, where=where, page=page).get(endpoint, [])
            items.extend(self.normalize(raw) for raw in batch)
            if len(batch) < 100:  # Xero pages hold 100 records
                return items
            page += 1

    def list_bank_transactions(self, where=None):
        return self._list_paged("BankTransactions", where)

    def list_invoices(self, where=None):
        return self._list_paged("Invoices", where)

    def get_transaction(self, endpoint, guid):
        found = self.get(f"{endpoint}/{guid}").get(endpoint, [])
        if not found:
            raise RuntimeError(f"Xero {endpoint} {guid} not found")
        return self.normalize(found[0])

    def list_attachments(self, endpoint, guid):
        return self.get(f"{endpoint}/{guid}/Attachments").get("Attachments", [])

    def get_attachment(self, endpoint, guid, filename):
        url = f"{self.BASE_URL}/{endpoint}/{guid}/Attachments/{urllib.parse.quote(filename)}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Xero-tenant-id": self.tenant_id,
            "Accept": "application/pdf",
        }
        _, body = self.request("GET", url, headers=headers)
        return body

    def post_attachment(self, endpoint, guid, filename, content, mime_type):
        self.call_log.append(("POST", f"{endpoint}/{guid}/Attachments/{filename}"))
        if not self.access_token:
            raise SelectionPaused("Tony must approve the dry-run range and auto-attach count before live mode")
        url = f"{self.BASE_URL}/{endpoint}/{guid}/Attachments/{urllib.parse.quote(filename)}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Xero-tenant-id": self.tenant_id,
            "Content-Type": mime_type,
        }
        _, body = self.request("POST", url, content, headers)
        return json.loads(body)["Attachments"][0]
