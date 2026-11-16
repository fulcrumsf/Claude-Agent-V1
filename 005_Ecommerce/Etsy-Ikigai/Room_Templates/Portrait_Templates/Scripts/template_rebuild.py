"""Rebuild ONE existing template as a NEW pending template next to it (Tony 2026-11-15; 0 credits unless --scene is a
newly generated room). The live PSD is never touched; Production never uses the rebuild until Tony clicks Approve on
its "NEW · approve?" card in the Portal Templates tab (template_gallery.is_pending / template_build.decide_rebuild).

  python template_rebuild.py <rel under Portrait_Templates> [--scene <png>] [--review <dir>] [--mat]

--mat (templates with a mat): the old mat layer is hidden, SAM finds the FRAME opening on the photo, and a new
UNIFORM mat is built (Tony 2026-11-10: one width all round, bevel + shadow): a "Mat" board layer (colour sampled from
the old mat; the frame's measured hard + soft shadow and the measured light falloff baked onto the board), a crisp
"Mat Bevel" white core along the window, the art in the window (+ opening_pad_px under the bevel), and over the art a
"Mat Bevel Shadow" (black, Multiply), the guarded Light Shadow and the Glass Sheen, all masked to the art quad. The
mat width is the one nearest 10% of the opening's height that brings the window within 3% of the print ratio.

1. the scene: the template rendered with the art, shadows/glare and foreground hidden (= the photo), or --scene (a
   regenerated room, e.g. without wainscoting; SAM's box then comes from Gemini)
2. scene_templates.build_psd: SAM opening (frame's hard inner edge) + opening_pad_px (0.5), measured black-fill
   shadows with crisp layer masks, guarded key light (sun line only on SAM's wall mask; none over a print), card test
3. writes INTO the template's own folder: <stem>_Rebuild_<date>.psd, <stem>_Rebuild_<date>_Scene.png and the sidecar
   <stem>_Rebuild_<date>.json (kind rebuild, approved false, replaces <live psd>)
4. runs the Portal checker on it (results into config/template_checks.json, shown on the card)
5. --review: an amber art-area render + 8x corner zooms into <dir> for checking by eye (not shown to Tony)
Prints one JSON line with the outcome.
"""
import json
import math
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

PORTAL = Path("/Users/tonymacbook2025/Documents/Agent-OS/005_Ecommerce/Etsy-Ikigai/Portal")
sys.path.insert(0, str(PORTAL))

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

from app import scene_templates as stp  # noqa: E402
from app import template_checker as tc  # noqa: E402
from app import template_gallery as tg  # noqa: E402
from app.db import load_config  # noqa: E402

DATE = datetime.now().strftime("%Y-%m-%d")


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def visible_quad(psd, s, work, hide):
    so = tc.so_size(psd, s, work)
    for nm, v in (("blk", 0), ("wht", 255)):
        Image.new("RGB", tuple(so), (v, v, v)).save(work / f"c_{nm}.png")
    blk = tc.render(psd, work / "blk.png", s, hide=hide, card=work / "c_blk.png")
    wht = tc.render(psd, work / "wht.png", s, hide=hide, card=work / "c_wht.png")
    return tc.quad_from_mask((wht - blk).mean(2) > 40)


def review(psd, q_art, out_dir, s, work):
    """Amber card render cropped on the art + the four corners at 8x (art quad corners)."""
    so = tc.so_size(psd, s, work)
    card = work / "amber.png"
    tg.tint_card(so[0], so[1], card)
    img = tc.render(psd, work / "amber_r.png", s, card=card).astype("uint8")
    q = np.float32(q_art)
    x0, y0 = q.min(0)
    x1, y1 = q.max(0)
    m = 0.15 * max(x1 - x0, y1 - y0)
    H, W = img.shape[:2]
    crop = Image.fromarray(img).crop((int(max(0, x0 - m)), int(max(0, y0 - m)), int(min(W, x1 + m)), int(min(H, y1 + m))))
    crop.thumbnail((1100, 1100))
    Z, S = 8, 36
    zs = []
    for cx, cy in q:
        c = Image.fromarray(img).crop((int(cx) - S // 2, int(cy) - S // 2, int(cx) + S // 2, int(cy) + S // 2))
        zs.append(c.resize((S * Z, S * Z), Image.NEAREST))
    sheet = Image.new("RGB", (max(crop.width, 4 * S * Z + 30), crop.height + S * Z + 10), (250, 250, 250))
    sheet.paste(crop, (0, 0))
    for i, z in enumerate(zs):
        sheet.paste(z, (i * (S * Z + 10), crop.height + 10))
    p = Path(out_dir) / f"{psd.stem}_review.jpg"
    sheet.save(p, quality=90)
    return p


# ---------- --mat: a uniform mat built as template layers ----------

def mat_window(q, ratio_value, size, nominal=0.10, lo=0.05, hi=0.20):
    """Uniform mat width m (fraction of the opening's real height) and the window quad (perspective-correct, in the
    opening's own unit square). Picks the m nearest `nominal` whose window is within 1.5% of the print ratio, else
    the best one within 3%; raises when no uniform mat gets there (the frame is too far from the ratio)."""
    from app.rooms import true_aspect
    a = true_aspect(q, size)
    best = None
    for m in np.arange(lo, hi + 1e-9, 0.0025):
        r = (a - 2 * m) / (1 - 2 * m)
        err = abs(r / ratio_value - 1)
        key = (0 if err <= 0.015 else 1, abs(m - nominal) if err <= 0.015 else err)
        if err <= 0.03 and (best is None or key < best[0]):
            best = (key, float(m), float(r), float(err))
    if best is None:
        raise stp.TemplateError(f"no uniform mat brings the frame opening ({a:.3f}) within 3% of {ratio_value:.3f}")
    _, m, r, err = best
    win = stp.sub_quad(q, m / a, m, 1 - m / a, 1 - m)
    return np.float32(win), {"mat_frac_of_height": round(m, 4), "window_ratio": round(r, 4),
                             "ratio_off": round(err, 4), "opening_aspect": round(float(a), 4)}


def build_mat_psd(scene_png, ratio, work, s, box, board_rgb):
    from app import room_slots as rs
    from app import sam_frames as sf
    from app.rooms import true_aspect
    from app.template_checker import offset_quad
    work = Path(work)
    with Image.open(scene_png) as im:
        rgb = np.asarray(im.convert("RGB"))
    H, W = rgb.shape[:2]
    img = rgb.astype("float32") / 255
    res, _alpha, wall = stp.sam_detect(scene_png, work, s, box=box)
    q = np.float32(res["corners"])                                   # the frame opening (hard inner edge)
    pad = float(stp._cfg(s, "opening_pad_px"))
    win, mat = mat_window(q, rs.RATIO_VALUE[ratio], (W, H))
    aq = offset_quad(win, pad)                                       # the art runs `pad` px under the bevel
    so = stp.so_pixels(aq, true_aspect(aq, (W, H)))
    black = np.zeros((H, W, 3), "float32")
    files, meta = {}, {}
    # the board: covers the opening + pad (under the frame lip), the window cut out, crisp anti-aliased edges
    board_q = offset_quad(q, pad)
    cov_board = sf.poly_coverage(board_q, W, H)
    cov_win = sf.poly_coverage(win, W, H)
    a_board = np.clip(cov_board - cov_win, 0, 1)
    sides = stp.measure_edge_shadows(img, q, pad)                    # the frame's shadow, measured at the opening
    keep_h = np.ones((H, W), "float32")
    keep_s = np.ones((H, W), "float32")
    for sd, d in zip(sides, stp.side_distance(q, W, H)):
        inside = stp.band(-d, 0.0, stp.HARD_BLUR_PX)
        if sd["hard_k"] > 0:
            keep_h *= (1 - sd["hard_k"] * (1 - inside)).astype("float32")
        if sd["soft_k"] > 0:
            keep_s *= (1 - sd["soft_k"] * stp.band(np.clip(d, 0, None), sd["width_px"], sd["blur_px"]) * inside
                       ).astype("float32")
    la, km = stp.key_light(img, q, wall)                             # guarded (no sun line off the wall mask)
    lop = float(km.get("opacity", 0.0))
    shade = keep_h * keep_s * (1 - lop * la)
    board = np.float32(board_rgb)[None, None, :] / 255 * shade[..., None]
    stp._save_rgba(board, a_board, work / "L_mat.png")
    files["Mat"] = "L_mat.png"
    # the bevel's white core: a crisp band just outside the window (the art's pad covers its inner half pixel)
    short = min(math.dist(win[0], win[3]), math.dist(win[0], win[1]))
    bw = max(1.5, 0.006 * short)
    a_bev = np.clip(sf.poly_coverage(offset_quad(win, bw), W, H) - cov_win, 0, 1)
    core = np.clip(np.float32(board_rgb) / 255 * 1.05 + 0.02, 0, 1)[None, None, :] * shade[..., None]
    stp._save_rgba(np.broadcast_to(core, (H, W, 3)).copy(), a_bev, work / "L_bevel.png")
    files["Mat Bevel"] = "L_bevel.png"
    side = stp.light_side(rgb.astype("float32") @ stp.W709, q)
    a_bs = (1 - stp.edge_shadow(win, W, H, side)) * sf.poly_coverage(offset_quad(aq, stp.LAYER_PAD), W, H)
    stp._save_rgba(black, a_bs / max(float(a_bs.max()), 1e-6), work / "L_bevel_shadow.png")
    files["Mat Bevel Shadow"] = "L_bevel_shadow.png"
    meta["Mat Bevel Shadow"] = {"kind": "mat bevel shadow (top + the side the light comes from)",
                                "opacity": round(float(np.clip(a_bs.max(), 0.05, 0.6)), 3), "light_from": side}
    region = sf.poly_coverage(offset_quad(aq, stp.LAYER_PAD), W, H)
    stp._save_rgba(black, la * region, work / "L_light.png")
    files["Light Shadow"] = "L_light.png"
    meta["Light Shadow"] = km
    stp._save_rgba(np.ones((H, W, 3), "float32"), stp.glass(aq, W, H) * region, work / "L_glass.png")
    files["Glass Sheen"] = "L_glass.png"
    stp.placeholder(so[0], so[1], work / "placeholder.png")
    base = work / "base.png"
    Image.fromarray(rgb).save(base)
    P = lambda n: str((work / n).resolve())
    C = stp._cmd

    def place(f, name, blend="Normal", op=1.0, mask=True):
        out = C("file.placeEmbedded", {"path": P(f), "smartObject": False, "scale": 100}) \
            + C("layer.setProps", {"name": name, "blend": blend, "opacity": op, "visible": True})
        if mask:
            out += C("select.lasso", {"points": stp._pts(aq), "antiAlias": True}) \
                + C("layer.layerMask.revealSelection", {})
        return out
    a = ["run", str(base), *C("layer.setProps", {"name": stp.BASE_NAME}), *C("layer.select", {"name": stp.BASE_NAME})]
    a += place(files["Mat"], "Mat", mask=False) + place(files["Mat Bevel"], "Mat Bevel", mask=False)
    a += C("layer.new.group", {"name": "MAT"})
    for n in ("Mat", "Mat Bevel"):
        a += C("layer.moveTo", {"layer": n, "target": "MAT", "position": "into"})
    a += C("layer.select", {"name": "MAT"})
    a += C("file.placeEmbedded", {"path": P("placeholder.png"), "smartObject": True, "scale": 100})
    a += C("layer.setProps", {"name": stp.ART, "blend": "Normal"}) + C("edit.transform", {"quad": stp._pts(aq)})
    shadows = ["Light Shadow", "Mat Bevel Shadow"]
    for n in shadows:
        a += place(files[n], n, "Multiply", (meta.get(n) or {}).get("opacity", 0.2))
    a += C("layer.new.group", {"name": "SHADOWS"})
    for n in shadows:
        a += C("layer.moveTo", {"layer": n, "target": "SHADOWS", "position": "into"})
    a += C("layer.select", {"name": "SHADOWS"}) + place(files["Glass Sheen"], "Glass Sheen", "Screen", 0.08)
    a += C("layer.new.group", {"name": "GLARE"})
    a += C("layer.moveTo", {"layer": "Glass Sheen", "target": "GLARE", "position": "into"})
    out_psd = work / "template.psd"
    a += ["--out", str(out_psd)]
    stp._run(s, a)
    (work / "cards").mkdir(exist_ok=True)
    card = stp.card_verify(out_psd, aq, s, work / "cards", opening=win)
    meta["Mat"] = {"kind": "uniform mat board (colour from the old mat; frame shadow + light falloff measured and "
                           "baked onto the board)", "rgb": list(board_rgb), "frame_shadow_sides": sides, **mat}
    meta["Mat Bevel"] = {"kind": "white-core bevel", "width_px": round(bw, 2)}
    return {"psd_tmp": out_psd, "quad_insert": np.round(win, 3).tolist(), "quad_art": np.round(aq, 3).tolist(),
            "quad_paper": np.round(q, 3).tolist(), "quad_frame_opening": np.round(q, 3).tolist(),
            "opening_pad_px": pad, "mode": "mat", "so_px": so, "so_ratio": round(so[0] / so[1], 4),
            "insert": {"method": "sam2 + hard inner edge (frame opening) + uniform mat",
                       "opening": res.get("opening"), "mat": mat}, "shadows": meta, "card_test": card,
            "canvas": [W, H], "light_from": side}


def old_mat_colour(psd, s, work, q, art_id):
    """Median colour of the old mat (rendered with the mat, art hidden) between the frame opening and the old art."""
    from app import sam_frames as sf
    from app.template_checker import offset_quad
    img = tc.render(psd, work / "oldmat.png", s, art_hidden=True, art_id=art_id)
    H, W = img.shape[:2]
    V = visible_quad(psd, s, work, [])
    ring = (sf.poly_coverage(offset_quad(q, -3), W, H) > 0.99) & ~(sf.poly_coverage(offset_quad(V, 6), W, H) > 0.01)
    if ring.sum() < 200:
        return (242, 240, 235)
    return tuple(int(round(v)) for v in np.median(img[ring], 0))


def main():
    rel = sys.argv[1]
    s = load_config("settings")
    t = next(x for x in tg.scan(s)[0] if x["rel"] == rel)
    psd = t["psd"]
    if t.get("pending") or t.get("wired"):
        raise SystemExit("not a live template")
    st0 = psd.stat()
    old = stp.load_manifest(psd) or {}
    work = Path(tempfile.mkdtemp(prefix="rebuild_"))
    r = tc.roles(tc.flatten(tc.info(psd, s).get("layers")))
    hide = [l["id"] for l in r["overlays"]] + [l["id"] for l in r["foreground"] if l["shown"]]
    mat_mode = "--mat" in sys.argv
    if mat_mode:
        V0 = visible_quad(psd, s, work, hide)        # the old art (SAM box), measured with the mat still shown
        hide += [l["id"] for l in r["mats"]]
        # mat groups: hide their pixel children too (a group's own visibility is enough, but be explicit)
    scene_arg = arg("--scene")
    if scene_arg:
        scene, box = Path(scene_arg), None                         # a regenerated room: Gemini finds the frame
    else:
        scene = work / "scene.png"
        tc.render(psd, scene, s, hide=hide, art_hidden=True, art_id=r["art"]["id"])
        V = V0 if mat_mode else visible_quad(psd, s, work, hide)   # SAM box = the visible art + 4% (as the checker)
        x0, y0 = V.min(0)
        x1, y1 = V.max(0)
        pad = float(arg("--box-pad", 0.20 if mat_mode else 0.04)) * max(x1 - x0, y1 - y0)   # a mat: the frame
        # opening lies outside the old art
        box = [float(x0 - pad), float(y0 - pad), float(x1 + pad), float(y1 + pad)]
    (work / "b").mkdir()
    if mat_mode:
        res0, _, _ = stp.sam_detect(scene, work / "b", s, box=box)
        board = old_mat_colour(psd, s, work, np.float32(res0["corners"]), r["art"]["id"])
        built = build_mat_psd(scene, t["ratio"], work / "b", s, box, board)
    else:
        built = stp.build_psd(scene, t["ratio"], work / "b", s, box=box)
    stem = f"{psd.stem}_Rebuild_{DATE}"
    folder = psd.parent
    new_psd = folder / f"{stem}.psd"
    if new_psd.exists():
        raise SystemExit(f"{new_psd.name} exists already")
    shutil.copy2(built["psd_tmp"], new_psd)
    shutil.copy2(scene, folder / f"{stem}_Scene.png")
    man = {"name": stem, "title": f"{psd.stem} (rebuilt {DATE})", "kind": tg.REBUILD_KIND, "psd": new_psd.name,
           "scene": f"{stem}_Scene.png", "replaces": psd.name, "smart_object_layer": stp.ART,
           "room": old.get("room") or t["room"], "decor": old.get("decor") or t["style"], "style": t["style"],
           "ratio": t["ratio"], "desc": old.get("desc") or t["desc"],
           **{k: built[k] for k in ("so_px", "so_ratio", "quad_insert", "quad_art", "quad_paper", "opening_pad_px",
                                    "mode", "canvas", "light_from", "insert", "shadows", "card_test")},
           "layers_verified": "black-fill shadows built by scene_templates.make_layers (measured, masked)",
           "base_layer": stp.BASE_NAME, "guard_max_cover": stp._cfg(s, "room_guard_max_cover"),
           "rebuilt_from": "regenerated scene (no wainscoting)" if scene_arg else "the template's own photo",
           "credits": float(arg("--credits", 0)), "approved": False,
           "created": datetime.now().isoformat(timespec="seconds")}
    if arg("--prompt-file"):
        man["prompt"] = Path(arg("--prompt-file")).read_text().strip()
    (folder / f"{stem}.json").write_text(json.dumps(man, indent=1, default=str) + "\n")
    rel_new = new_psd.relative_to(stp.library(s)).as_posix()
    data = tc.run_all(s, [rel_new], None, log=lambda *_: None)
    chk = data["results"][rel_new]
    st1 = psd.stat()
    assert (st0.st_size, st0.st_mtime_ns) == (st1.st_size, st1.st_mtime_ns), "ORIGINAL CHANGED"
    rv = review(new_psd, built["quad_art"], arg("--review"), s, work) if arg("--review") else None
    print(json.dumps({"rel": rel_new, "status": chk["status"], "reasons": chk["reasons"],
                      "card_pad": built["card_test"].get("pad_px"), "light": built["shadows"]["Light Shadow"].get("kind"),
                      "opening": (built["insert"].get("opening") or {}).get("offset_px"),
                      "placement": (chk.get("checks", {}).get("placement") or {}).get("status"),
                      "review": str(rv) if rv else None}, default=str))


if __name__ == "__main__":
    main()
