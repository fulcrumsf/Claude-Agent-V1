"""Spike: kie.ai image EDIT (image-to-image) for relighting / repainting a scene plate. Keys never printed.

python kie_edit.py <engine: nbpro|nb21|gpt25|gpt25s (preferred) | nb2|gpt (old)> <in.png> <out.png> <prompt.txt> [resolution 2K]
"""
import json, sys, time
from pathlib import Path

import httpx

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "Portal" / "app").is_dir()) / "Portal"))   # Etsy-Ikigai/Portal
from app.engines import secret  # noqa: E402

KIE = "https://api.kie.ai"
UPLOAD = "https://kieai.redpandaai.co/api/file-stream-upload"
# Tony's rule (2026-11-08): room plates/edits use Nano Banana Pro, Nano Banana 2.1 or GPT Image 2.5 (nbpro best for
# precise removals / clean-up). nb2 / gpt (2.0) only if none of those is available. Ids checked on docs.kie.ai 2026-11-08.
MODELS = {"nbpro": "nano-banana-pro", "nb21": "nano-banana-2-1", "gpt25": "gpt-image-2-5-flare-image-to-image",
          "gpt25s": "gpt-image-2-5-sunburst-image-to-image", "nb2": "nano-banana-2", "gpt": "gpt-image-2-image-to-image"}


def hdr():
    k = secret("KIE_API_KEY")
    if not k:
        raise SystemExit("KIE_API_KEY missing")
    return {"Authorization": f"Bearer {k}"}


def credits(c):
    return float(c.get(f"{KIE}/api/v1/chat/credit", headers=hdr()).json()["data"])


def upload(c, path):
    with open(path, "rb") as f:
        r = c.post(UPLOAD, headers=hdr(), files={"file": (Path(path).name, f)},
                   data={"uploadPath": "ikigai-spike", "fileName": f"{int(time.time())}_{Path(path).name}"}, timeout=180)
    j = r.json()
    url = (j.get("data") or {}).get("downloadUrl")
    if not url:
        raise SystemExit(f"upload failed: {str(j.get('msg'))[:200]}")
    return url


def edit(engine, src, out, prompt, res="2K", extra_imgs=()):
    c = httpx.Client(timeout=60)
    before = credits(c)
    urls = [upload(c, src)] + [upload(c, p) for p in extra_imgs]
    inp = {"prompt": prompt, "aspect_ratio": "1:1"}
    if engine.startswith("gpt"):              # GPT Image takes input_urls; Nano Banana takes image_input
        inp["input_urls"] = urls
        inp["resolution"] = res
    else:
        inp.update(image_input=urls, resolution=res, output_format="png")
    j = c.post(f"{KIE}/api/v1/jobs/createTask", headers={**hdr(), "Content-Type": "application/json"},
               json={"model": MODELS[engine], "input": inp}).json()
    task = (j.get("data") or {}).get("taskId")
    if j.get("code") != 200 or not task:
        raise SystemExit(f"refused: {str(j.get('msg'))[:200]}")
    t0 = time.time()
    while time.time() - t0 < 900:
        d = c.get(f"{KIE}/api/v1/jobs/recordInfo", params={"taskId": task}, headers=hdr()).json().get("data") or {}
        if d.get("state") == "success":
            url = json.loads(d["resultJson"])["resultUrls"][0]
            with c.stream("GET", url, timeout=180, follow_redirects=True) as r:
                Path(out).write_bytes(r.read())
            after = credits(c)
            print(json.dumps({"engine": engine, "out": str(out), "s": round(time.time() - t0), "credits": round(before - after, 2),
                              "left": after}), flush=True)
            return out
        if d.get("state") == "fail":
            raise SystemExit(f"fail: {str(d.get('failMsg'))[:200]}")
        time.sleep(5)
    raise SystemExit("timeout")


TEXT_TO_IMAGE = {"nbpro", "nb21", "nb2"}     # Nano Banana takes a prompt alone; GPT Image 2.5 here is image-to-image


def generate(engine, out, prompt, aspect_ratio="4:3", res="2K", ref_imgs=(), timeout=900, poll=5):
    """Text-to-image (optionally with reference images) for a NEW room scene; used by the Portal's Production tab
    (app/scene_templates.py, 2026-11-08). Unlike edit() it raises RuntimeError instead of exiting, so a server
    thread survives. Returns {"out", "model", "task", "s", "credits", "left"}."""
    if engine not in MODELS:
        raise RuntimeError(f"unknown engine {engine}")
    if engine not in TEXT_TO_IMAGE and not ref_imgs:
        raise RuntimeError(f"{engine} on kie.ai needs a reference image; use nbpro or nb21 for a new scene")
    k = secret("KIE_API_KEY")
    if not k:
        raise RuntimeError("KIE_API_KEY is not set")
    c = httpx.Client(timeout=60)
    try:
        before = credits(c)
        urls = [upload(c, p) for p in ref_imgs]
    except SystemExit as e:                      # upload() keeps the CLI's SystemExit; turn it into an error here
        raise RuntimeError(str(e))
    except (httpx.HTTPError, ValueError, KeyError):
        raise RuntimeError("kie.ai could not be reached (balance or upload)")
    inp = {"prompt": prompt, "aspect_ratio": aspect_ratio}
    if engine.startswith("gpt"):
        inp.update(input_urls=urls, resolution=res)
    else:
        inp.update(resolution=res, output_format="png")
        if urls:
            inp["image_input"] = urls
    try:
        j = c.post(f"{KIE}/api/v1/jobs/createTask", headers={**hdr(), "Content-Type": "application/json"},
                   json={"model": MODELS[engine], "input": inp}).json()
    except (httpx.HTTPError, ValueError):
        raise RuntimeError("kie.ai did not accept the job (network)")
    task = (j.get("data") or {}).get("taskId") if isinstance(j.get("data"), dict) else None
    if j.get("code") != 200 or not task:
        raise RuntimeError(f"kie.ai refused the job: {str(j.get('msg'))[:200]}")
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            d = c.get(f"{KIE}/api/v1/jobs/recordInfo", params={"taskId": task}, headers=hdr()).json().get("data") or {}
        except (httpx.HTTPError, ValueError):
            time.sleep(poll)
            continue
        if d.get("state") == "success":
            url = json.loads(d["resultJson"])["resultUrls"][0]
            with c.stream("GET", url, timeout=180, follow_redirects=True) as r:
                Path(out).write_bytes(r.read())
            try:
                after = credits(c)
            except Exception:  # noqa: BLE001  (the image is made; the balance is only a nicety)
                after = None
            return {"out": str(out), "model": MODELS[engine], "task": task, "s": round(time.time() - t0),
                    "credits": round(before - after, 2) if after is not None else None, "left": after}
        if d.get("state") == "fail":
            raise RuntimeError(f"kie.ai could not make it: {str(d.get('failMsg') or d.get('failCode'))[:200]}")
        time.sleep(poll)
    raise RuntimeError("kie.ai took too long")


if __name__ == "__main__":
    eng, src, out, pf = sys.argv[1:5]
    res = sys.argv[5] if len(sys.argv) > 5 else "2K"
    edit(eng, src, out, Path(pf).read_text(), res)
