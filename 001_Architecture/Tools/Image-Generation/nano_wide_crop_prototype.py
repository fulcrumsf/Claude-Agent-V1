"""Cloud remove/replace test with a WIDE crop and WIDE composite mask (no OpenFill code changes).
usage: nano_test.py run <obj> <engine> <step>    (engine: kie-pro | kie-21 | fal-pro; step: remove | replace)
       nano_test.py layers                       (put every result into LVRM_nano_test as named layers)
Keys are read from ~/.env-secrets and never printed."""
import base64, io, json, sys, time, uuid, urllib.request, urllib.parse
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SP = Path("/private/tmp/claude-501/-Users-tonymacbook2025--claude-spares-spare-PMD858/0a2d2af9-d0da-4700-8175-95e4ed739570/scratchpad")
SRC = SP / "test/LVRM_copy.png"
OUT = SP / "test/nano"
OUT.mkdir(parents=True, exist_ok=True)
PROFILE = Path.home() / "Library/Application Support/OpenFill for PhotoCraft"
EX = PROFILE / "exchange"
S = 2.655
# wide crops (full px) with an exact model aspect ratio, and the wide composite masks (preview px, x S)
CROPS = {"stool": ((520, 1200, 1720, 2000), "3:2"), "lamp": ((1150, 600, 2350, 1500), "4:3")}
MASKS = {
    "stool": [(200, 690), (290, 640), (330, 600), (365, 556), (560, 556), (572, 600), (560, 750), (200, 750)],
    "lamp": [(612, 330), (790, 330), (790, 548), (612, 548)],
}
PROMPTS = {
    ("stool", "remove"): "Remove the wooden stool and its cast shadow on the floor. Restore the herringbone wood floor, the sunlight on it, the door frame and the baseboard exactly as they would look without the stool. Change nothing else in the picture; keep the same framing.",
    ("stool", "replace"): "Replace the wooden stool with a small round oak side table with a ceramic bowl on top. Remove the stool's old shadow and give the new table a natural cast shadow that matches the existing window light direction and the other shadows in the room. Change nothing else in the picture; keep the same framing.",
    ("lamp", "remove"): "Remove the black table lamp with the white shade and its shadow on the wall. Restore the plain wall, the stack of books and the marble side table exactly. Do not change the picture frame on the wall. Change nothing else; keep the same framing.",
    ("lamp", "replace"): "Replace the black table lamp with a tall white ceramic vase with dried eucalyptus branches, standing on the stack of books. Remove the lamp's shadow and give the vase a natural shadow that matches the existing light in the room. Do not change the picture frame on the wall. Change nothing else; keep the same framing.",
}
MODELS = {"kie-pro": ("kie", "nano-banana-pro"), "kie-21": ("kie", "nano-banana-2-1"), "fal-pro": ("fal", "fal-ai/nano-banana-pro/edit")}


def secret(name):
    for line in (Path.home() / ".env-secrets").read_text().splitlines():
        line = line.strip()
        line = line[7:] if line.startswith("export ") else line
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip("'\"")
    return ""


def http(method, url, data=None, headers=None, timeout=180):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def kie_credits():
    h = {"Authorization": "Bearer " + secret("KIE_API_KEY")}
    return float(json.loads(http("GET", "https://api.kie.ai/api/v1/chat/credit", headers=h))["data"])


def kie(model, png, prompt, ratio):
    h = {"Authorization": "Bearer " + secret("KIE_API_KEY")}
    b = "x" + uuid.uuid4().hex
    body = (f'--{b}\r\nContent-Disposition: form-data; name="uploadPath"\r\n\r\nnanotest\r\n--{b}\r\nContent-Disposition: form-data; name="fileName"\r\n\r\n{uuid.uuid4().hex}.png\r\n'
            f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="crop.png"\r\nContent-Type: image/png\r\n\r\n').encode() + png + f"\r\n--{b}--\r\n".encode()
    up = json.loads(http("POST", "https://kieai.redpandaai.co/api/file-stream-upload", body, {**h, "Content-Type": f"multipart/form-data; boundary={b}"}))
    url = up["data"]["downloadUrl"]
    inp = {"prompt": prompt, "image_input": [url], "aspect_ratio": ratio, "resolution": "2K", "output_format": "png"}
    j = json.loads(http("POST", "https://api.kie.ai/api/v1/jobs/createTask", json.dumps({"model": model, "input": inp}).encode(), {**h, "Content-Type": "application/json"}))
    task = (j.get("data") or {}).get("taskId")
    if not task:
        raise RuntimeError(f"kie refused: {str(j.get('msg'))[:200]}")
    while True:
        time.sleep(3)
        d = json.loads(http("GET", f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task}", headers=h))["data"]
        if d.get("state") == "success":
            res = json.loads(d["resultJson"])["resultUrls"][0]
            return http("GET", res), d.get("creditsConsumed")
        if d.get("state") == "fail":
            raise RuntimeError(f"kie failed: {str(d.get('failMsg'))[:200]}")


def fal(model, png, prompt, ratio):
    h = {"Authorization": "Key " + secret("FAL_AI_API_KEY"), "Content-Type": "application/json"}
    body = {"prompt": prompt, "image_urls": ["data:image/png;base64," + base64.b64encode(png).decode()], "num_images": 1,
            "aspect_ratio": ratio, "resolution": "2K", "output_format": "png"}
    j = json.loads(http("POST", "https://fal.run/" + model, json.dumps(body).encode(), h, timeout=600))
    url = j["images"][0]["url"]
    return (base64.b64decode(url.split(",", 1)[1]) if url.startswith("data:") else http("GET", url)), None


def wide_mask(obj, size):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in MASKS[obj]], fill=255)
    return m.filter(ImageFilter.GaussianBlur(18))


def run(obj, eng, step):
    src = Image.open(SRC).convert("RGB")
    box, ratio = CROPS[obj]
    crop = src.crop(box)
    buf = io.BytesIO(); crop.save(buf, "PNG")
    prov, model = MODELS[eng]
    before = kie_credits() if prov == "kie" else None
    t0 = time.time()
    data, cr = (kie if prov == "kie" else fal)(model, buf.getvalue(), PROMPTS[(obj, step)], ratio)
    secs = time.time() - t0
    after = kie_credits() if prov == "kie" else None
    res = Image.open(io.BytesIO(data)).convert("RGB")
    rsize = res.size
    res = res.resize(crop.size, Image.LANCZOS)
    full_res = src.copy(); full_res.paste(res, box[:2])
    mask = wide_mask(obj, src.size)
    comp = Image.composite(full_res, src, mask)
    a, c = np.asarray(src, np.int16), np.asarray(comp, np.int16)
    changed = np.abs(a - c).max(2) > 3
    outside = changed & (np.asarray(mask) == 0)
    # how much the model changed OUTSIDE the wide mask inside its crop (what the composite threw away)
    raw_full = np.asarray(full_res, np.int16)
    raw_out = (np.abs(a - raw_full).max(2) > 12) & (np.asarray(mask) == 0)
    tag = f"{eng}_{step}_{obj}"
    res.save(OUT / f"{tag}_raw.png")
    rgba = full_res.convert("RGBA"); rgba.putalpha(mask)
    rgba.save(OUT / f"{tag}_layer.png")
    bx = (box[0], box[1], box[2], box[3])
    src.crop(bx).save(EX / f"Nano_Test_{obj.title()}_Before.png")
    comp.crop(bx).save(EX / f"Nano_Test_{eng}_{step}_{obj.title()}_After.png")
    rec = {"tag": tag, "seconds": round(secs, 1), "result_px": rsize, "credits": cr if cr is not None else (round(before - after, 2) if before else None),
           "changed_outside_mask_px": int(outside.sum()), "model_changed_outside_mask_in_crop_px": int((raw_out[bx[1]:bx[3], bx[0]:bx[2]]).sum())}
    print(json.dumps(rec), flush=True)
    with open(OUT / "log.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "credits":
        print(kie_credits())
