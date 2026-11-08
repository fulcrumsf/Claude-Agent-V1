from pathlib import Path
import sys, numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Portal"))   # Etsy-Ikigai/Portal
from app import rooms
ref=None
for f in sys.argv[1:]:
    rgb=np.array(Image.open(f).convert("RGB"))
    q,info=rooms.find_frame(rgb,min_fill=0.6)
    if q is None: print(f,"NOT FOUND",info); continue
    if ref is None: ref=q
    print(f, np.round(q).astype(int).tolist(), "max corner shift px", round(float(np.abs(q-ref).max()),1), "fill", info.get("fill"))
