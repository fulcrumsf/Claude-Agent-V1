"""Image engines for the art studio. The dropdown list lives in config/engines.json.

All three V1 engines (GPT Image 2, Nano Banana 2, Nano Banana Pro) run on kie.ai through the same two calls
the workspace tool `001_Architecture/Tools/Image-Generation/kie_image_gen.py` uses (createTask, then poll
recordInfo and download resultUrls[0]). That script hard-codes 16:9 / 4K and exits the process, so this is an
in-process port of the same API with the print settings (2:3, 1K) and a credit check.

Keys: read from the environment, else from ~/.env-secrets / ~/.mcp-secrets.env (values are never printed).
Tests swap the adapter (`studio.mount(..., adapter=...)`), so pytest makes no real calls.
"""
import json
import os
import time
from pathlib import Path

import httpx

from .db import load_config

KIE_BASE = "https://api.kie.ai"
SECRET_FILES = (Path.home() / ".env-secrets", Path.home() / ".mcp-secrets.env")


class EngineError(Exception):
    """A plain, short reason an engine could not make an image (safe to show Tony)."""


def secret(name):
    """Env var first, then the secret files. Returns None when missing. Never logs the value."""
    v = os.environ.get(name)
    if v:
        return v
    for f in SECRET_FILES:
        try:
            lines = f.read_text().splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if line.startswith("export "):
                line = line[7:].strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            if k.strip() == name and v and not v.startswith("$"):
                return v
    return None


def config():
    return load_config("engines")


def list_engines():
    cfg = config()
    out = []
    for e in cfg["engines"]:
        out.append({**e, "ready": bool(secret(e["env_key"])), "default": e["id"] == cfg.get("default"),
                    "usd_per_image": round(e["credits_per_image"] * cfg.get("usd_per_credit", 0.005), 4)})
    return out


def get_engine(engine_id):
    return next((e for e in list_engines() if e["id"] == engine_id), None)


class KieAdapter:
    """One kie.ai job per image. `generate` blocks until the file is on disk (run it in a worker thread)."""

    def __init__(self, engine, poll_s=4, timeout_s=600, client=None):
        self.engine = engine
        self.poll_s = poll_s
        self.timeout_s = timeout_s
        self.client = client or httpx.Client(timeout=30)

    def _headers(self):
        key = secret(self.engine.get("env_key", "KIE_API_KEY"))
        if not key:
            raise EngineError(f"{self.engine.get('env_key', 'KIE_API_KEY')} is not set")
        return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def credits(self):
        try:
            r = self.client.get(f"{KIE_BASE}/api/v1/chat/credit", headers=self._headers())
            j = r.json()
        except (httpx.HTTPError, ValueError):
            raise EngineError("kie.ai balance check failed (network)")
        if j.get("code") != 200:
            raise EngineError(f"kie.ai balance check refused: {str(j.get('msg'))[:120]}")
        return float(j["data"])

    def submit(self, prompt, aspect_ratio="2:3", resolution="1K"):
        inp = {"prompt": prompt, "aspect_ratio": aspect_ratio, "resolution": resolution}
        if self.engine.get("output_format"):
            inp["output_format"] = self.engine["output_format"]
        try:
            r = self.client.post(f"{KIE_BASE}/api/v1/jobs/createTask", headers=self._headers(),
                                 json={"model": self.engine["model"], "input": inp})
            j = r.json()
        except (httpx.HTTPError, ValueError):
            raise EngineError("kie.ai did not accept the job (network)")
        task = (j.get("data") or {}).get("taskId") if isinstance(j.get("data"), dict) else j.get("taskId")
        if j.get("code") != 200 or not task:
            raise EngineError(f"kie.ai refused the job: {str(j.get('msg'))[:160]}")
        return task

    def wait(self, task_id):
        end = time.monotonic() + self.timeout_s
        while time.monotonic() < end:
            try:
                j = self.client.get(f"{KIE_BASE}/api/v1/jobs/recordInfo", params={"taskId": task_id},
                                    headers=self._headers()).json()
            except (httpx.HTTPError, ValueError):
                time.sleep(self.poll_s)
                continue
            d = j.get("data") or {}
            state = d.get("state")
            if state == "success":
                try:
                    urls = json.loads(d.get("resultJson") or "{}").get("resultUrls") or []
                except ValueError:
                    urls = []
                if not urls:
                    raise EngineError("kie.ai finished but returned no image")
                return urls[0]
            if state == "fail":
                raise EngineError(f"kie.ai could not make it: {str(d.get('failMsg') or d.get('failCode'))[:160]}")
            time.sleep(self.poll_s)
        raise EngineError("kie.ai took too long")

    def download(self, url, path):
        try:
            with self.client.stream("GET", url, timeout=120, follow_redirects=True) as r:
                r.raise_for_status()
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "wb") as f:
                    for chunk in r.iter_bytes():
                        f.write(chunk)
        except httpx.HTTPError:
            raise EngineError("could not download the image from kie.ai")
        return path

    def generate(self, prompt, out_path, aspect_ratio="2:3", resolution="1K", on_task=None):
        task = self.submit(prompt, aspect_ratio, resolution)
        if on_task:
            on_task(task)
        url = self.wait(task)
        ext = Path(url.split("?")[0]).suffix.lower()
        if ext in (".jpg", ".jpeg", ".webp", ".png"):
            out_path = out_path.with_suffix(ext)
        return {"task_id": task, "path": self.download(url, out_path)}


def adapter_for(engine_id, settings=None):
    e = get_engine(engine_id)
    if not e:
        raise EngineError(f"unknown engine {engine_id}")
    if e["provider"] != "kie":
        raise EngineError(f"no adapter for provider {e['provider']}")
    s = settings or {}
    return KieAdapter(e, poll_s=s.get("art_poll_s", 4), timeout_s=s.get("art_task_timeout_s", 600))


def run_prompt(engine_id, prompt):
    """Old scaffold entry point. Art is made through the Build art flow (app/art.py) now."""
    raise NotImplementedError("use the Build art flow in the Idea bank (app/art.py)")
