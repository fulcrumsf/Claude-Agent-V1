import os
import re
import subprocess
from pathlib import Path


ENV_SECRETS = Path("~/.env-secrets").expanduser()
KEYCHAIN_SERVICE = "agent-os-xero"


def load_env_secrets():
    values = {}
    if not ENV_SECRETS.exists():
        raise FileNotFoundError("~/.env-secrets does not exist")
    for line in ENV_SECRETS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export "):].strip()
        values[key] = value.strip().strip('"').strip("'")
    return values


def required_secret(name):
    value = load_env_secrets().get(name)
    if not value:
        raise RuntimeError(f"{name} is not configured in ~/.env-secrets")
    return value


def save_refresh_token(tenant_id, token, service=KEYCHAIN_SERVICE):
    """Store the token in the Keychain. `security -i` reads the command from stdin,
    so the token never appears in the process list."""
    for value in (tenant_id, token):
        if not value or re.search(r'[\s"\\]', value):
            raise ValueError("Keychain account/token is empty or has unsafe characters")
    input_text = f'add-generic-password -U -a "{tenant_id}" -s "{service}" -w "{token}"\n'
    result = subprocess.run(["/usr/bin/security", "-i"], input=input_text, text=True, capture_output=True)
    if result.returncode != 0 or "error" in (result.stdout + result.stderr).lower():
        raise RuntimeError(f"could not save the refresh token to the Keychain (service {service})")


def read_refresh_token(tenant_id, service=KEYCHAIN_SERVICE):
    result = subprocess.run(
        ["/usr/bin/security", "find-generic-password", "-a", tenant_id, "-s", service, "-w"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return ""
    return result.stdout.strip()


def redact(value):
    return re.sub(
        r'("(?:access_token|refresh_token|id_token|client_secret)"\s*:\s*")([^"]+)(")',
        r'\1[REDACTED]\3',
        value,
    )
