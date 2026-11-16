"""Per template: the scene render (art, shadows/glare, foreground hidden), the visible art quad, an amber art-area
render. Writes scenes/<key>.png, scenes/<key>_amber.png, scenes/index.json. Read-only on the PSDs."""
import json
import sys
from pathlib import Path

PORTAL = Path("/Users/tonymacbook2025/Documents/Agent-OS/005_Ecommerce/Etsy-Ikigai/Portal")
sys.path.insert(0, str(PORTAL))
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

from app import template_checker as tc  # noqa: E402
from app import template_gallery as tg  # noqa: E402
from app.db import load_config  # noqa: E402

OUT = Path(sys.argv[1])
OUT.mkdir(exist_ok=True)
s = load_config("settings")
idx = {}
for t in tg.scan(s)[0]:
    if t.get("wired"):
        continue
    key = t["psd"].stem
    try:
        psd = t["psd"]
        fl = tc.flatten(tc.info(psd, s)["layers"])
        r = tc.roles(fl)
        art = r["art"]["id"]
        hide = [l["id"] for l in r["overlays"]] + [l["id"] for l in r["foreground"] if l["shown"]]
        so = tc.so_size(psd, s, OUT)
        for nm, v in (("k", 0), ("w", 255)):
            Image.new("RGB", tuple(so), (v, v, v)).save(OUT / f"_{nm}.png")
        tc.render(psd, OUT / f"{key}.png", s, hide=hide, art_hidden=True, art_id=art)
        b = tc.render(psd, OUT / "_b.png", s, hide=hide, card=OUT / "_k.png")
        w = tc.render(psd, OUT / "_wr.png", s, hide=hide, card=OUT / "_w.png")
        V = tc.quad_from_mask((w - b).mean(2) > 40)
        tg.tint_card(so[0], so[1], OUT / "_a.png")
        tc.render(psd, OUT / f"{key}_amber.png", s, card=OUT / "_a.png")
        idx[key] = {"rel": t["rel"], "ratio": t["ratio"], "V": np.round(V, 1).tolist() if V is not None else None,
                    "so": so, "foreground": [l["name"] for l in r["foreground"]], "mats": [l["name"] for l in r["mats"]]}
        print("ok", key, flush=True)
    except Exception as e:  # noqa: BLE001
        idx[key] = {"rel": t["rel"], "error": str(e)[:200]}
        print("ERR", key, e, flush=True)
    (OUT / "index.json").write_text(json.dumps(idx, indent=1))
