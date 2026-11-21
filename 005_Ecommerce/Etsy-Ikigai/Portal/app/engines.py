"""Image engines: the Build art pull-down and the room-scene engines. The list lives in config/engines.json (v2,
controls addendum D, 2026-11-21).

Three providers, one interface (`Adapter.generate(prompt, out_path, aspect_ratio, resolution, on_task, refs, use)`):
  - kie.ai (KieAdapter): createTask, then poll recordInfo and download resultUrls[0] (the same API as
    `001_Architecture/Tools/Image-Generation/kie_image_gen.py`). The three V1 engines (GPT Image 2, Nano Banana 2,
    Nano Banana Pro) send exactly the same JSON body as before (golden test). Cost = the balance difference.
  - fal.ai (FalAdapter): the queue API (POST queue.fal.run/<model>, poll status_url, GET response_url). fal has no
    balance API, so its cost is the price table, marked "est.".
  - WaveSpeed (WaveSpeedAdapter): POST /api/v3/<model>, poll /api/v3/predictions/<id>/result. Price table.
No blind resubmit (a retry after an unclear failure can bill twice): a job goes to the fallback provider only when the
primary clearly refused it at submit (nothing billed) and the fallback costs no more than the shown price.

Keys: read from the environment, else from ~/.env-secrets / ~/.mcp-secrets.env (values are never printed).
Tests swap the adapter (`studio.mount(..., adapter=...)`) or the httpx transport, so pytest makes no real calls.

  python -m app.engines --test gpt-image-2-6,ideogram-3,recraft-4-1,flux-3 --use art     (prints the cost; no --yes = nothing)
"""
import base64
import io
import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path

import httpx

from .db import ROOT, load_config

KIE_BASE = "https://api.kie.ai"
FAL_QUEUE = "https://queue.fal.run"
WAVESPEED_BASE = "https://api.wavespeed.ai/api/v3"
SECRET_FILES = (Path.home() / ".env-secrets", Path.home() / ".mcp-secrets.env")
STATUS_PATH = ROOT / "data" / "engine_status.json"     # tests point this at a temp file
GATES = ("untested", "passed_1", "trusted", "suspect", "failed")
GATE_OK = ("passed_1", "trusted")
_STATUS_LOCK = threading.Lock()


class EngineError(Exception):
    """A plain, short reason an engine could not make an image (safe to show Tony). refused_at_submit: the provider
    clearly refused the job before it existed (nothing billed), so a fallback provider may be tried."""

    def __init__(self, msg, refused_at_submit=False, hard=False):
        super().__init__(msg)
        self.refused_at_submit = refused_at_submit
        self.hard = hard


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


# ---------- engine status (tests, measured costs, room gates), written by code ----------

def load_status():
    try:
        return json.loads(Path(STATUS_PATH).read_text())
    except (OSError, ValueError):
        return {}


def update_status(fn):
    """Read-modify-write data/engine_status.json atomically under a lock. Returns the new status."""
    with _STATUS_LOCK:
        st = load_status()
        fn(st)
        p = Path(STATUS_PATH)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_text(json.dumps(st, indent=1, sort_keys=True) + "\n")
        os.replace(tmp, p)
        return st


def record_cost(engine_id, use, credits):
    """One measured cost (credits per image) for a token-billed engine; the label uses the mean of the last 5."""
    if credits is None:
        return

    def fn(st):
        u = st.setdefault(engine_id, {}).setdefault(use, {})
        u["costs"] = (u.get("costs") or [])[-4:] + [round(float(credits), 2)]
    update_status(fn)


def measured_cost(engine_id, use, status=None):
    st = status if status is not None else load_status()
    cs = ((st.get(engine_id) or {}).get(use) or {}).get("costs") or []
    return round(sum(cs[-5:]) / len(cs[-5:]), 2) if cs else None


# ---------- engines, prices, labels ----------

def _all():
    return config()["engines"]


def use_spec(e, use="art", with_refs=False):
    """The provider, model and parameters an engine uses for `use` (art | room). Legacy kie engines (top-level
    "model", no uses.art) keep the old body. with_refs: a room request that sends reference photographs uses the
    engine's ref_model when it has one (Flux 3: fal edit-image)."""
    u = dict(((e.get("uses") or {}).get(use)) or {})
    legacy = use == "art" and "model" in e and "model" not in u
    if with_refs and u.get("ref_model"):
        rm = u["ref_model"]
        u = {**u, **rm}
    spec = {"provider": u.get("provider") or e["provider"], "env_key": u.get("env_key") or e.get("env_key"),
            "model": u.get("model") or e.get("model"), "params": dict(u.get("params") or {}),
            "aspect_param": u.get("aspect_param", "aspect_ratio"), "aspect_map": u.get("aspect_map") or {},
            "res_param": u.get("res_param", "resolution"), "resolution": u.get("resolution"),
            "ref_param": u.get("ref_param"), "max_refs": u.get("max_refs"), "legacy": legacy,
            "price": u.get("price"), "ref_kind": u.get("ref_kind")}
    if legacy:
        spec["output_format"] = e.get("output_format")
    return spec


def price(e, use="art", status=None, with_refs=False):
    """{credits (estimate, credits-equivalent), upper (the most it can cost), usd, unit, measured, est, provider}.
    kie fixed prices are exact; token engines use the estimate (upper bound for caps) until measured; fal / WaveSpeed
    are dollar prices converted at usd_per_credit."""
    upc = config().get("usd_per_credit", 0.005)
    p = e.get("price") or {}
    spec = use_spec(e, use, with_refs)
    sp_price = spec.get("price") or {}
    prov = spec["provider"]
    unit = p.get("unit", "image")
    if sp_price.get("usd") is not None and prov != "kie":
        usd = float(sp_price["usd"])
        cr = round(usd / upc, 1)
        return {"credits": cr, "upper": cr, "usd": round(usd, 4), "unit": "usd", "measured": False, "est": True,
                "provider": prov}
    if unit == "tokens":
        meas = measured_cost(e["id"], use, status)
        est = (p.get("estimate_credits") or {}).get(use)
        upper = (p.get("upper_credits") or {}).get(use) or est
        cr = meas if meas is not None else est
        return {"credits": cr, "upper": max(upper or 0, cr or 0), "usd": round((cr or 0) * upc, 4), "unit": "tokens",
                "measured": meas is not None, "est": meas is None, "provider": prov}
    if prov == "kie":
        cr = (p.get("credits") or {}).get(use)
        if cr is None and use == "art":
            cr = e.get("credits_per_image")
        return {"credits": cr, "upper": cr, "usd": round((cr or 0) * upc, 4) if cr is not None else None,
                "unit": "credits", "measured": False, "est": False, "provider": prov}
    key = "room_ref" if (use == "room" and with_refs) else use
    usd = (p.get("usd") or {}).get(key)
    if usd is None:
        return {"credits": None, "upper": None, "usd": None, "unit": "usd", "measured": False, "est": True,
                "provider": prov}
    cr = round(float(usd) / upc, 1)
    return {"credits": cr, "upper": cr, "usd": round(float(usd), 4), "unit": "usd", "measured": False, "est": True,
            "provider": prov}


def _num(x):
    return f"{x:g}" if isinstance(x, (int, float)) else "?"


def price_label(e, use="art", status=None, with_refs=False):
    pr = price(e, use, status, with_refs)
    if pr["credits"] is None:
        return "price unknown"
    if pr["unit"] == "tokens":
        if pr["measured"]:
            return f"{round(pr['credits'])} cr measured (${pr['usd']:.2f})"
        return f"≈{round(pr['credits'])} cr est. (${pr['usd']:.2f})"
    if pr["unit"] == "usd":
        return f"${pr['usd']:g} (≈{round(pr['credits'])} cr) · {'fal' if pr['provider'] == 'fal' else 'WaveSpeed'}"
    return f"{_num(pr['credits'])} cr (${pr['usd']:.2f})"


def _row(e, cfg, status):
    pr = price(e, "art", status)
    st = status.get(e["id"]) or {}
    room = room_info(e, status)
    return {**e, "ready": bool(secret(e["env_key"])), "default": e["id"] == cfg.get("default"),
            "credits_per_image": pr["credits"] if pr["credits"] is not None else e.get("credits_per_image"),
            "upper_per_image": pr["upper"],
            "usd_per_image": round(pr["usd"] or 0, 4), "price_label": price_label(e, "art", status),
            "price_est": pr["est"], "price_unit": pr["unit"], "provider_label": pr["provider"],
            "tested": (st.get("art") or {}).get("tested") or e.get("tested"), "room": room}


def list_engines(include_hidden=False):
    """The Build art pull-down rows in Tony's order (hidden engines only with include_hidden)."""
    cfg = config()
    status = load_status()
    rows = [_row(e, cfg, status) for e in sorted(cfg["engines"], key=lambda x: x.get("order", 50))
            if include_hidden or not e.get("hidden")]
    return rows


def get_engine(engine_id):
    """Any engine, hidden ones included (old rounds still resolve their label)."""
    cfg = config()
    e = next((x for x in cfg["engines"] if x["id"] == engine_id), None)
    return _row(e, cfg, load_status()) if e else None


def raw_engine(engine_id):
    return next((x for x in _all() if x["id"] == engine_id), None)


# ---------- room engines (controls addendum E) ----------

def by_scene_id(scene_id):
    return next((x for x in _all() if x.get("scene_id") == scene_id), None)


def scene_engine_id(x):
    """"nbpro" and "nano-banana-pro" are the same engine: an engines.json id, or None when unknown."""
    if not x:
        return None
    if raw_engine(x):
        return x
    e = by_scene_id(x)
    return e["id"] if e else None


def room_gate(engine_id, status=None):
    st = status if status is not None else load_status()
    g = ((st.get(engine_id) or {}).get("room") or {}).get("gate")
    if g in GATES:
        return g
    e = raw_engine(engine_id)
    return (((e or {}).get("uses") or {}).get("room") or {}).get("gate_default") or "untested"


def ref_ok(engine_id, status=None):
    st = status if status is not None else load_status()
    return bool(((st.get(engine_id) or {}).get("room") or {}).get("ref_ok"))


def room_info(e, status=None):
    """Room-scene facts of one engine: credits / usd per scene, whether it takes a reference photograph now, gate."""
    status = status if status is not None else load_status()
    spec = use_spec(e, "room")
    if not (e.get("scene_id") or (e.get("uses") or {}).get("room")):
        return None
    pr = price(e, "room", status)
    kind = spec.get("ref_kind")
    takes = kind == "guide" or (kind == "guide_unverified" and ref_ok(e["id"], status))
    grades = ((status.get(e["id"]) or {}).get("room") or {}).get("grades") or []
    gs = [g["score"] for g in grades if isinstance(g.get("score"), (int, float))]
    return {"credits": pr["credits"], "upper": pr["upper"], "usd": pr["usd"], "est": pr["est"], "unit": pr["unit"],
            "provider": spec["provider"], "label": price_label(e, "room", status), "ref_kind": kind,
            "takes_ref": takes, "gate": room_gate(e["id"], status), "scene_id": e.get("scene_id"),
            "grade_mean": round(sum(gs) / len(gs), 2) if gs else None, "graded": len(gs)}


def room_engines():
    """The room-scene pull-down rows (engines with a room use), in Tony's order."""
    status = load_status()
    out = []
    for e in sorted(_all(), key=lambda x: x.get("order", 50)):
        if e.get("hidden"):
            continue
        ri = room_info(e, status)
        if ri is None:
            continue
        out.append({**ri, "id": e["id"], "label": e["label"], "price_label": ri["label"],
                    "ready": bool(secret(use_spec(e, "room")["env_key"] or ""))})
    return out


def record_room_check(engine_id, ok, why="", scene=None):
    """One first-real-scene check (E.4): untested -> passed_1 -> trusted on passes; one fail -> suspect, two ->
    failed. Returns the new gate."""
    out = {}

    def fn(st):
        r = st.setdefault(engine_id, {}).setdefault("room", {})
        g = r.get("gate") or room_gate(engine_id, {})
        fails = int(r.get("fails") or 0)
        passes = int(r.get("passes") or 0)
        if ok:
            passes += 1
            if g != "failed":
                g = "trusted" if passes >= 2 and g in ("passed_1", "trusted") else ("passed_1" if g in ("untested", "suspect") else g)
        else:
            fails += 1
            g = "failed" if fails >= 2 else "suspect"
        r.update(gate=g, fails=fails, passes=passes)
        r["scenes"] = (r.get("scenes") or [])[-9:] + [{"ok": bool(ok), "why": str(why)[:200], "scene": scene,
                                                        "at": datetime.now().isoformat(timespec="seconds")}]
        out["gate"] = g
    update_status(fn)
    return out["gate"]


def record_room_grade(engine_id, idea_id, slot, grade, score):
    def fn(st):
        r = st.setdefault(engine_id, {}).setdefault("room", {})
        gs = [g for g in r.get("grades") or [] if not (g.get("idea_id") == idea_id and g.get("slot") == slot)]
        if grade:
            gs.append({"idea_id": idea_id, "slot": slot, "grade": grade, "score": score})
        r["grades"] = gs
    update_status(fn)


# ---------- adapters ----------

def _to_png(data, path):
    """Save image bytes as PNG at path: a PNG answer is written byte for byte, WebP / JPEG converted (lossless)."""
    path = Path(path).with_suffix(".png")
    path.parent.mkdir(parents=True, exist_ok=True)
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        path.write_bytes(data)
        return path
    from PIL import Image
    try:
        with Image.open(io.BytesIO(data)) as im:
            im.convert("RGB").save(path, format="PNG")
    except Exception:  # noqa: BLE001
        raise EngineError("the image the engine returned could not be read")
    return path


def _data_uri(p):
    p = Path(p)
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


class Adapter:
    """Shared plumbing: key, aspect mapping, download, the generate loop with the clear-refusal fallback."""
    provider = ""
    base_name = ""

    def __init__(self, engine, poll_s=4, timeout_s=600, client=None, use="art", spec=None):
        self.engine = engine
        self.poll_s = poll_s
        self.timeout_s = timeout_s
        self.client = client or httpx.Client(timeout=30)
        self.use = use
        self.spec = spec or use_spec(engine, use)

    def key(self):
        name = self.spec.get("env_key") or self.engine.get("env_key")
        k = secret(name)
        if not k:
            raise EngineError(f"{name} is not set", hard=True)
        return k

    def input(self, prompt, aspect_ratio, resolution, refs=()):
        s = self.spec
        inp = {"prompt": prompt}
        amap = s.get("aspect_map") or {}
        if s.get("aspect_param"):
            inp[s["aspect_param"]] = amap.get(aspect_ratio, aspect_ratio)
        if s.get("res_param"):
            inp[s["res_param"]] = s.get("resolution") or resolution
        inp.update(s.get("params") or {})
        if refs and s.get("ref_param"):
            inp[s["ref_param"]] = list(refs)[: s.get("max_refs") or len(refs)]
        return inp

    def balance(self):
        return {"amount": None, "unit": "usd"}

    def credits(self):
        raise EngineError(f"{self.base_name} has no credit balance")

    def download(self, url, path):
        try:
            if str(url).startswith("data:"):
                data = base64.b64decode(str(url).split(",", 1)[1])
            else:
                r = self.client.get(url, timeout=120, follow_redirects=True)
                r.raise_for_status()
                data = r.content
        except (httpx.HTTPError, ValueError):
            raise EngineError(f"could not download the image from {self.base_name}")
        return _to_png(data, path)

    def _cost(self, refs=()):
        pr = price(self.engine, self.use, with_refs=bool(refs))
        if self.spec.get("price") and self.spec["price"].get("usd") is not None:
            usd = float(self.spec["price"]["usd"])
            return round(usd / config().get("usd_per_credit", 0.005), 1), round(usd, 4)
        return pr["credits"], pr["usd"]

    def generate(self, prompt, out_path, aspect_ratio="2:3", resolution="1K", on_task=None, refs=(), use=None):
        t0 = time.time()
        try:
            task = self.submit(prompt, aspect_ratio, resolution, refs)
        except EngineError as ex:
            fb = self.engine.get("fallback")
            if not (ex.refused_at_submit and fb and not refs and self.use == "art"):
                raise
            shown = price(self.engine, self.use)["usd"] or 0
            if float((fb.get("price") or {}).get("usd") or 1e9) > shown + 1e-9:
                raise
            spec = {**use_spec(self.engine, self.use), **{k: fb.get(k) for k in ("provider", "env_key", "model",
                                                                               "aspect_param", "res_param")},
                    "params": dict(fb.get("params") or {}), "aspect_map": fb.get("aspect_map") or {},
                    "price": fb.get("price")}
            ad = ADAPTERS[fb["provider"]](self.engine, self.poll_s, self.timeout_s, self.client, self.use, spec)
            res = ad.generate(prompt, out_path, aspect_ratio, resolution, on_task, refs)
            res["fallback_from"] = self.provider
            return res
        if on_task:
            on_task(task)
        url = self.wait(task)
        path = self.download(url, out_path)
        cr, usd = self._cost(refs)
        return {"task_id": task, "path": path, "provider": self.provider, "model": self.spec["model"],
                "credits": cr, "usd": usd, "measured": False, "s": round(time.time() - t0)}


class KieAdapter(Adapter):
    """One kie.ai job per image. `generate` blocks until the file is on disk (run it in a worker thread)."""
    provider = "kie"
    base_name = "kie.ai"

    def _headers(self):
        return {"Authorization": f"Bearer {self.key()}", "Content-Type": "application/json"}

    def credits(self):
        try:
            r = self.client.get(f"{KIE_BASE}/api/v1/chat/credit", headers=self._headers())
            j = r.json()
        except (httpx.HTTPError, ValueError):
            raise EngineError("kie.ai balance check failed (network)")
        if j.get("code") != 200:
            raise EngineError(f"kie.ai balance check refused: {str(j.get('msg'))[:120]}", hard=True)
        return float(j["data"])

    def balance(self):
        """Raises EngineError when the balance cannot be read (an art round is refused then, as before)."""
        return {"amount": self.credits(), "unit": "credits"}

    def _soft_balance(self):
        try:
            return self.credits()
        except EngineError:
            return None

    def submit(self, prompt, aspect_ratio="2:3", resolution="1K", refs=()):
        if self.spec.get("legacy"):                       # the three V1 engines: byte-identical body
            inp = {"prompt": prompt, "aspect_ratio": aspect_ratio, "resolution": resolution}
            if self.engine.get("output_format"):
                inp["output_format"] = self.engine["output_format"]
        else:
            inp = self.input(prompt, aspect_ratio, resolution, refs)
        try:
            r = self.client.post(f"{KIE_BASE}/api/v1/jobs/createTask", headers=self._headers(),
                                 json={"model": self.spec["model"], "input": inp})
            j = r.json()
        except (httpx.HTTPError, ValueError):
            raise EngineError("kie.ai did not accept the job (network)")
        task = (j.get("data") or {}).get("taskId") if isinstance(j.get("data"), dict) else j.get("taskId")
        if j.get("code") != 200 or not task:
            code = j.get("code")
            raise EngineError(f"kie.ai refused the job: {str(j.get('msg'))[:160]}", refused_at_submit=True,
                              hard=code in (401, 402, 403))
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

    def generate(self, prompt, out_path, aspect_ratio="2:3", resolution="1K", on_task=None, refs=(), use=None):
        """Room use measures the balance difference around the one job (scenes run one at a time); art rounds
        measure the whole round in app/art.py (four images run in parallel)."""
        before = self._soft_balance() if self.use == "room" else None
        res = super().generate(prompt, out_path, aspect_ratio, resolution, on_task, refs)
        if before is not None:
            after = self._soft_balance()
            if after is not None:
                res.update(credits=round(before - after, 2), usd=round((before - after) * 0.005, 4), measured=True,
                           left=after)
        return res


class FalAdapter(Adapter):
    """fal.ai queue API. Reference images go as data URIs (no upload)."""
    provider = "fal"
    base_name = "fal.ai"

    def _headers(self):
        return {"Authorization": f"Key {self.key()}", "Content-Type": "application/json"}

    def submit(self, prompt, aspect_ratio="2:3", resolution="1K", refs=()):
        inp = self.input(prompt, aspect_ratio, resolution, [_data_uri(p) for p in refs])
        try:
            r = self.client.post(f"{FAL_QUEUE}/{self.spec['model']}", headers=self._headers(), json=inp)
        except httpx.HTTPError:
            raise EngineError("fal.ai did not answer the job (network; not resubmitted)")
        try:
            j = r.json()
        except ValueError:
            j = {}
        rid = j.get("request_id")
        if r.status_code >= 400 or not rid:
            raise EngineError(f"fal.ai refused the job: {str(j.get('detail') or j)[:160]}", refused_at_submit=True,
                              hard=r.status_code in (401, 402, 403))
        self._urls = getattr(self, "_urls", {})
        self._urls[rid] = (j.get("status_url") or f"{FAL_QUEUE}/{self.spec['model']}/requests/{rid}/status",
                           j.get("response_url") or f"{FAL_QUEUE}/{self.spec['model']}/requests/{rid}")
        return rid

    def wait(self, task_id):
        status_url, response_url = getattr(self, "_urls", {}).get(task_id) or (
            f"{FAL_QUEUE}/{self.spec['model']}/requests/{task_id}/status",
            f"{FAL_QUEUE}/{self.spec['model']}/requests/{task_id}")
        end = time.monotonic() + self.timeout_s
        while time.monotonic() < end:
            try:
                r = self.client.get(status_url, headers=self._headers())
                j = r.json()
            except (httpx.HTTPError, ValueError):
                time.sleep(self.poll_s)
                continue
            st = j.get("status")
            if st == "COMPLETED":
                try:
                    rr = self.client.get(response_url, headers=self._headers())
                    out = rr.json()
                except (httpx.HTTPError, ValueError):
                    raise EngineError("fal.ai finished but the result could not be read")
                imgs = out.get("images") if isinstance(out, dict) else None
                if rr.status_code >= 400 or not imgs:
                    raise EngineError(f"fal.ai could not make it: {str((out or {}).get('detail') or out)[:160]}")
                return imgs[0]["url"] if isinstance(imgs[0], dict) else imgs[0]
            if st not in ("IN_QUEUE", "IN_PROGRESS"):
                raise EngineError(f"fal.ai could not make it: {str(j.get('detail') or st)[:160]}")
            time.sleep(self.poll_s)
        raise EngineError("fal.ai took too long")


class WaveSpeedAdapter(Adapter):
    provider = "wavespeed"
    base_name = "WaveSpeed"
    TERMINAL_FAIL = ("failed", "cancelled", "timeout", "deleted")

    def _headers(self):
        return {"Authorization": f"Bearer {self.key()}", "Content-Type": "application/json"}

    def balance(self):
        """GET /api/v3/balance (endpoint UNVERIFIED): dollars, or None on any error."""
        try:
            j = self.client.get(f"{WAVESPEED_BASE}/balance", headers=self._headers()).json()
            v = (j.get("data") or {}).get("balance") if isinstance(j.get("data"), dict) else None
            return {"amount": float(v) if v is not None else None, "unit": "usd"}
        except Exception:  # noqa: BLE001
            return {"amount": None, "unit": "usd"}

    def submit(self, prompt, aspect_ratio="2:3", resolution="1K", refs=()):
        inp = self.input(prompt, aspect_ratio, resolution, [_data_uri(p) for p in refs])
        try:
            r = self.client.post(f"{WAVESPEED_BASE}/{self.spec['model']}", headers=self._headers(), json=inp)
        except httpx.HTTPError:
            raise EngineError("WaveSpeed did not answer the job (network; not resubmitted)")
        try:
            j = r.json()
        except ValueError:
            j = {}
        tid = (j.get("data") or {}).get("id") if isinstance(j.get("data"), dict) else None
        if r.status_code >= 400 or not tid:
            raise EngineError(f"WaveSpeed refused the job: {str(j.get('message') or j)[:160]}", refused_at_submit=True,
                              hard=r.status_code in (401, 402, 403))
        return tid

    def wait(self, task_id):
        end = time.monotonic() + self.timeout_s
        while time.monotonic() < end:
            try:
                j = self.client.get(f"{WAVESPEED_BASE}/predictions/{task_id}/result", headers=self._headers()).json()
            except (httpx.HTTPError, ValueError):
                time.sleep(self.poll_s)
                continue
            d = j.get("data") or {}
            st = d.get("status")
            if st == "completed":
                outs = d.get("outputs") or []
                if not outs:
                    raise EngineError("WaveSpeed finished but returned no image")
                return outs[0]
            if st in self.TERMINAL_FAIL:
                raise EngineError(f"WaveSpeed could not make it ({st}): {str(d.get('error') or '')[:160]}")
            time.sleep(self.poll_s)
        raise EngineError("WaveSpeed took too long")


ADAPTERS = {"kie": KieAdapter, "fal": FalAdapter, "wavespeed": WaveSpeedAdapter}


def adapter_for(engine_id, settings=None, use="art", with_refs=False, client=None):
    e = raw_engine(engine_id)
    if not e:
        raise EngineError(f"unknown engine {engine_id}")
    spec = use_spec(e, use, with_refs)
    cls = ADAPTERS.get(spec["provider"])
    if cls is None:
        raise EngineError(f"no adapter for provider {spec['provider']}")
    s = settings or {}
    return cls(e, poll_s=s.get("art_poll_s", 4), timeout_s=s.get("art_task_timeout_s", 600), client=client, use=use,
               spec=spec)


def balance_of(ad):
    """{"amount", "unit"} of any adapter (old test fakes only have credits())."""
    b = getattr(ad, "balance", None)
    if callable(b):
        return b()
    return {"amount": ad.credits(), "unit": "credits"}


def run_prompt(engine_id, prompt):
    """Old scaffold entry point. Art is made through the Build art flow (app/art.py) now."""
    raise NotImplementedError("use the Build art flow in the Idea bank (app/art.py)")


# ---------- D.5: one cheap test image per engine (only with --yes, on Tony's go) ----------

TEST_PROMPT = ("A simple still life for an engine test: a white ceramic cup on a plain oak table against a soft grey "
               "wall, even daylight. No text, no people.")


def test_plan(ids, use="art"):
    rows, total_cr, total_usd = [], 0.0, 0.0
    for i in ids:
        e = raw_engine(i)
        if not e:
            raise EngineError(f"unknown engine {i}")
        pr = price(e, use)
        rows.append({"id": i, "label": e["label"], "provider": pr["provider"], "upper_credits": pr["upper"],
                     "usd": pr["usd"], "est": pr["est"]})
        total_cr += pr["upper"] or 0
        total_usd += (pr["upper"] or 0) * config().get("usd_per_credit", 0.005)
    return {"rows": rows, "upper_credits": round(total_cr, 1), "upper_usd": round(total_usd, 3)}


def run_tests(ids, use="art", out_dir=None, adapter=None, log=print):
    """The paid test round (D.5): one 2:3 1K image per engine, result in data/engine_status.json. adapter(engine_id)
    is injectable for tests; the default is the real provider."""
    import tempfile
    out_dir = Path(out_dir or tempfile.mkdtemp(prefix="engine_test_"))
    results = {}
    for i in ids:
        ad = adapter(i) if adapter else adapter_for(i, use=use)
        b0 = balance_of(ad)["amount"] if getattr(ad, "provider", "kie") == "kie" else None
        t0 = time.time()
        try:
            res = ad.generate(TEST_PROMPT, out_dir / f"Test_{i}.png", "2:3", "1K")
        except EngineError as ex:
            results[i] = {"ok": False, "why": str(ex)}
            log(f"{i}: failed: {ex}")
            continue
        b1 = balance_of(ad)["amount"] if b0 is not None else None
        cr = round(b0 - b1, 2) if b0 is not None and b1 is not None else res.get("credits")
        from PIL import Image
        with Image.open(res["path"]) as im:
            size = list(im.size)
        results[i] = {"ok": True, "credits": cr, "measured": b0 is not None and b1 is not None,
                      "seconds": round(time.time() - t0), "size": size, "file": str(res["path"])}
        today = datetime.now().date().isoformat()

        def fn(st, i=i, cr=cr, size=size):
            a = st.setdefault(i, {}).setdefault(use, {})
            a.update(tested=today, size=size, seconds=results[i]["seconds"])
        update_status(fn)
        e = raw_engine(i)
        if (e.get("price") or {}).get("unit") == "tokens" and results[i]["measured"]:
            record_cost(i, use, cr)
        log(f"{i}: ok, {cr} credits, {results[i]['seconds']} s, {size[0]}x{size[1]} -> {res['path']}")
    return results


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="One cheap test image per engine (prints the cost; --yes runs it)")
    ap.add_argument("--test", required=True, help="comma-separated engine ids")
    ap.add_argument("--use", default="art")
    ap.add_argument("--yes", action="store_true", help="really generate (spends credits / dollars)")
    a = ap.parse_args()
    ids = [x.strip() for x in a.test.split(",") if x.strip()]
    plan = test_plan(ids, a.use)
    for r in plan["rows"]:
        print(f"  {r['label']:<16} {r['provider']:<10} at most {r['upper_credits']} cr-eq"
              + (" (estimate)" if r["est"] else ""))
    print(f"Total at most about {plan['upper_credits']} credits-equivalent (${plan['upper_usd']:.2f}).")
    if not a.yes:
        print("Nothing was generated. Add --yes to run it (only on Tony's go).")
    else:
        print(json.dumps(run_tests(ids, a.use), indent=1))
