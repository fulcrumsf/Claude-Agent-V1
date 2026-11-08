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


if __name__ == "__main__":
    eng, src, out, pf = sys.argv[1:5]
    res = sys.argv[5] if len(sys.argv) > 5 else "2K"
    edit(eng, src, out, Path(pf).read_text(), res)
