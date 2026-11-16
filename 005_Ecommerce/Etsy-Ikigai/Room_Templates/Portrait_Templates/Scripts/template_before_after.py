"""One labelled before/after image (amber art-area card, like the Templates tab "Show art area").

  python compare.py <before.psd> <after.psd> <out.jpg> --title "..." --bnote "line|line" --anote "line|line"

Top: both templates rendered with the amber test card, cropped around the art. Below: 8x zooms of the four corners
(before row, after row), so a sliver, a dark line or art on the frame is visible.
"""
import argparse
import sys
import tempfile
from pathlib import Path

PORTAL = Path("/Users/tonymacbook2025/Documents/Agent-OS/005_Ecommerce/Etsy-Ikigai/Portal")
sys.path.insert(0, str(PORTAL))

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from app import template_checker as tc  # noqa: E402
from app import template_gallery as tg  # noqa: E402
from app.db import load_config  # noqa: E402


def font(sz):
    for f in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def amber(psd, s, work):
    so = tc.so_size(psd, s, work)
    card = Path(work) / f"amber_{abs(hash(str(psd)))}.png"
    tg.tint_card(so[0], so[1], card)
    fl = tc.flatten(tc.info(psd, s)["layers"])
    r = tc.roles(fl)
    out = Path(work) / f"r_{abs(hash(str(psd)))}.png"
    img = tc.render(psd, out, s, card=card)
    blk = Path(work) / "k.png"
    wht = Path(work) / "w.png"
    Image.new("RGB", tuple(so), (0, 0, 0)).save(blk)
    Image.new("RGB", tuple(so), (255, 255, 255)).save(wht)
    hide = [l["id"] for l in r["foreground"] if l["shown"]]
    D = (tc.render(psd, Path(work) / "wk.png", s, hide=hide, card=wht)
         - tc.render(psd, Path(work) / "bk.png", s, hide=hide, card=blk)).mean(2) > 40
    return img.astype("uint8"), tc.quad_from_mask(D)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("out")
    ap.add_argument("--title", default="")
    ap.add_argument("--before-label", default="BEFORE (current template)")
    ap.add_argument("--after-label", default="AFTER (proposed fix)")
    ap.add_argument("--bnote", default="")
    ap.add_argument("--anote", default="")
    a = ap.parse_args()
    s = load_config("settings")
    work = tempfile.mkdtemp(prefix="cmp_")
    A, qa = amber(Path(a.before), s, work)
    B, qb = amber(Path(a.after), s, work)
    q = np.float32(qb if qb is not None else qa)
    x0, y0 = q.min(0)
    x1, y1 = q.max(0)
    m = 0.18 * max(x1 - x0, y1 - y0)
    H, W = A.shape[:2]
    box = (int(max(0, x0 - m)), int(max(0, y0 - m)), int(min(W, x1 + m)), int(min(H, y1 + m)))
    TH = 760
    tiles = []
    for img in (A, B):
        c = Image.fromarray(img).crop(box)
        tiles.append(c.resize((round(c.width * TH / c.height), TH), Image.LANCZOS))
    Z, S = 8, 34                      # zoom factor, window size px
    zrows = []
    for img, qq in ((A, qa), (B, qb)):
        row = []
        for cx, cy in np.float32(qq if qq is not None else q):
            cx, cy = int(round(cx)), int(round(cy))
            c = Image.fromarray(img).crop((cx - S // 2, cy - S // 2, cx + S // 2, cy + S // 2))
            row.append(c.resize((S * Z, S * Z), Image.NEAREST))
        zrows.append(row)
    pad = 24
    colw = max(t.width for t in tiles)
    zw = 4 * S * Z + 3 * 10
    Wt = max(2 * colw + 3 * pad, zw + 2 * pad + 200)
    f1, f2, f3 = font(34), font(26), font(22)
    bl = [x for x in a.bnote.split("|") if x]
    al = [x for x in a.anote.split("|") if x]
    nl = max(len(bl), len(al))
    Ht = 70 + 46 + TH + 16 + nl * 30 + 30 + 2 * (S * Z + 46) + pad
    out = Image.new("RGB", (Wt, Ht), (250, 249, 246))
    d = ImageDraw.Draw(out)
    d.text((pad, 18), a.title, fill=(20, 20, 20), font=f1)
    y = 70
    for i, (t, lab, lines, col) in enumerate(((tiles[0], a.before_label, bl, (170, 40, 30)),
                                              (tiles[1], a.after_label, al, (20, 110, 40)))):
        x = pad + i * (colw + pad)
        d.text((x, y), lab, fill=col, font=f2)
        out.paste(t, (x, y + 40))
        for j, ln in enumerate(lines):
            d.text((x, y + 46 + TH + 10 + j * 30), ln, fill=(40, 40, 40), font=f3)
    y = 70 + 46 + TH + 16 + nl * 30 + 20
    names = ["top-left", "top-right", "bottom-right", "bottom-left"]
    for r_i, (row, lab) in enumerate(zip(zrows, ("before", "after"))):
        d.text((pad, y + 6), f"{lab}: corners 8x", fill=(60, 60, 60), font=f3)
        for k, z in enumerate(row):
            x = pad + 200 + k * (S * Z + 10)
            out.paste(z, (x, y + 36))
            if r_i == 0:
                d.text((x, y + 8), names[k], fill=(90, 90, 90), font=f3)
        y += S * Z + 46
    out.save(a.out, quality=90)
    print(a.out, out.size)


if __name__ == "__main__":
    main()
