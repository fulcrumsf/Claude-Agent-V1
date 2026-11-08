"""Production step 1b: room mockups (listing image slots 8-19).

How it works (so the real art is never redrawn by an AI):
  1. kie.ai draws an EMPTY room scene with one frame whose picture area is flat magenta. These scenes do not
     depend on the design, so each is made once and cached in data/rooms/ and reused for every listing.
  2. The magenta area is found (OpenCV), its four corners measured.
  3. The print JPG whose shape matches that frame is chosen automatically (2x3, 3x4, 4x5, 11x14 or ISO A1),
     cover-cropped (never stretched) to the frame's measured shape, perspective-warped into the corners and
     lit with the scene's own shading. The art in the image is the real file, pixel for pixel.
Output: square JPGs (1:1), the shape Etsy's mobile app and web grid both show without cropping the picture.
Nothing is deleted; a scene that cannot be read is reported, not faked.
"""
import hashlib
import json
import math
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .db import ROOT
from .pipeline.base import NotConfigured

DEFAULTS = {"room_engine": "gpt-image-2", "room_resolution": "2K", "room_attempts": 2, "room_jpg_quality": 92,
            "room_workers": 4, "rooms_cache": "data/rooms", "room_shape_tolerance": 0.12}

RATIO = {"2x3": 2 / 3, "3x4": 3 / 4, "4x5": 4 / 5, "11x14": 11 / 14, "ISO_A1": 23.4 / 33.1}
FRAME = {"black": "a thin matte black frame", "oak": "a thin natural oak frame",
         "white": "a thin white frame", "walnut": "a slim dark walnut frame"}

# (slot, file key, print shape, frame, scene)
SCENES = [
    (8, "Living_Room", "2x3", "black", "a bright modern living room, cream linen sofa with a few cushions under the frame, soft daylight from the left"),
    (9, "Bedroom", "2x3", "oak", "a calm bedroom, bed with white linen bedding and a wooden headboard, frame centred above the headboard, warm morning light"),
    (10, "Entryway", "2x3", "white", "a tidy entryway, narrow wooden console table with a small lamp and a plant below the frame, light plaster wall"),
    (11, "Home_Office", "2x3", "black", "a home office, wooden desk with a laptop and a chair, a shelf at the side, frame on the wall above the desk"),
    (12, "Dining_Room", "3x4", "oak", "a dining room, round wooden table with two chairs, frame on the wall behind them, soft natural light"),
    (13, "Hallway", "3x4", "black", "a bright hallway, wooden bench with a basket beneath the frame, pale wall"),
    (14, "Breakfast_Nook", "3x4", "white", "a kitchen breakfast nook, built-in bench with cushions, small table, frame on the wall above the bench"),
    (15, "Reading_Nook", "4x5", "oak", "a reading nook, armchair with a throw blanket and a floor lamp, frame on the wall beside the chair"),
    (16, "Gallery_Wall", "4x5", "black", "a minimal white room with one large frame on the wall, light wood floor, a potted plant at the side"),
    (17, "Bathroom", "4x5", "white", "a bright bathroom, wooden vanity with a mirror shelf, a plant, frame on the wall next to the vanity"),
    (18, "Fireplace", "11x14", "walnut", "a living room fireplace mantel with a few candles and a vase, frame hung centred above the mantel"),
    (19, "Moody_Study", "ISO_A1", "black", "a moody study with dark green walls, bookshelves, a leather armchair, frame on the wall, warm lamp light"),
]


def _cfg(settings, key):
    return (settings or {}).get(key, DEFAULTS[key])


def scene_prompt(shape, frame, scene):
    w, h = shape.replace("ISO_A1", "5x7").replace("11x14", "11x14").split("x")
    return (f"Photorealistic interior photograph, {scene}. The camera faces the wall straight on, at eye level, "
            f"no wide-angle distortion. On the wall hangs exactly one upright portrait picture frame ({FRAME[frame]}), "
            f"shaped {w}:{h} (taller than wide), fully visible with space around it, taking up about a quarter of "
            f"the image width. The whole picture area inside the frame is flat solid pure magenta (#FF00FF): no mat, "
            f"no glass glare, no reflections, no shadow inside the picture area, no pattern. No other artwork, no "
            f"text, no people. Square composition, sharp, natural colours.")


# ---------- finding the frame ----------
def magenta_mask(rgb):
    """Magenta picture-area pixels, found by colour RATIOS (R/G and B/G) rather than fixed differences, so the
    paper is still found where a window-bar shadow darkens it (guide 4c.1)."""
    a = rgb.astype("float32")
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    rg, bg = (r + 4) / (g + 4), (b + 4) / (g + 4)
    rb = (r + 4) / (b + 4)
    return (rg > 1.55) & (bg > 1.45) & (rb > 0.5) & (rb < 3.5) & (a.max(axis=2) > 22)


def _line(p, q):
    import numpy as np
    return np.cross(np.array([p[0], p[1], 1.0]), np.array([q[0], q[1], 1.0]))


def _quad_from_hull(hull):
    """Four corners of a (possibly perspective, possibly corner-clipped) quadrilateral: simplify the hull,
    keep its 4 longest sides and intersect neighbouring sides. A prop that cuts one corner off leaves a
    5th short side, which is dropped, and the true corner is rebuilt from the two long sides."""
    import cv2
    import numpy as np
    for eps in (0.008, 0.012, 0.018, 0.025, 0.035, 0.05):
        ap = cv2.approxPolyDP(hull, eps * cv2.arcLength(hull, True), True).reshape(-1, 2).astype("float64")
        if 4 <= len(ap) <= 7:
            break
    else:
        return cv2.boxPoints(cv2.minAreaRect(hull)).astype("float32")
    if len(ap) == 4:
        return ap.astype("float32")
    n = len(ap)
    lens = [math.dist(ap[i], ap[(i + 1) % n]) for i in range(n)]
    keep = sorted(sorted(range(n), key=lambda i: -lens[i])[:4])
    pts = []
    for j in range(4):
        i1, i2 = keep[j], keep[(j + 1) % 4]
        x = np.cross(_line(ap[i1], ap[(i1 + 1) % n]), _line(ap[i2], ap[(i2 + 1) % n]))
        if abs(x[2]) < 1e-9:
            return cv2.boxPoints(cv2.minAreaRect(hull)).astype("float32")
        pts.append(x[:2] / x[2])
    return np.array(pts, "float32")


def true_aspect(quad, image_size):
    """Width:height of the real rectangle behind a perspective quad (tl,tr,br,bl), using Zhang & He's
    whiteboard method (focal length from the quad, principal point = image centre). An off-axis frame is
    foreshortened on screen, so the on-screen edge ratio would pick the wrong print and crop the art.
    Falls back to the on-screen ratio when the view is too frontal to solve."""
    import numpy as np
    W, H = image_size
    c = np.array([W / 2, H / 2])
    tl, tr, br, bl = [np.array([*(p - c), 1.0]) for p in np.asarray(quad, "float64")]
    m1, m2, m3, m4 = tl, tr, bl, br
    try:
        k2 = np.dot(np.cross(m1, m4), m3) / np.dot(np.cross(m2, m4), m3)
        k3 = np.dot(np.cross(m1, m4), m2) / np.dot(np.cross(m3, m4), m2)
    except FloatingPointError:
        k2 = k3 = float("nan")
    n2, n3 = k2 * m2 - m1, k3 * m3 - m1
    f2 = None
    if np.all(np.isfinite([k2, k3])) and abs(n2[2] * n3[2]) > 1e-12:
        v = -(n2[0] * n3[0] + n2[1] * n3[1]) / (n2[2] * n3[2])
        if (0.4 * max(W, H)) ** 2 < v < (5 * max(W, H)) ** 2:
            f2 = v
    if f2 is None:
        f2 = (1.2 * max(W, H)) ** 2                       # ~40 mm lens; only used when the view is near frontal
    if not np.all(np.isfinite([k2, k3])):
        q = np.asarray(quad, "float64")
        return ((math.dist(q[0], q[1]) + math.dist(q[3], q[2])) /
                (math.dist(q[0], q[3]) + math.dist(q[1], q[2])))
    num = (n2[0] ** 2 + n2[1] ** 2) / f2 + n2[2] ** 2
    den = (n3[0] ** 2 + n3[1] ** 2) / f2 + n3[2] ** 2
    return float(math.sqrt(num / den))


def loose_magenta(rgb):
    """Looser magenta test for the thin, dark, wood-blended strip of paper under the frame lip."""
    a = rgb.astype("float32")
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return ((r + 4) / (g + 4) > 1.3) & ((b + 4) / (g + 4) > 1.15) & (r > g + 12)


def refine_quad(rgb, quad, max_px=14):
    """Push each edge of the quad outward while the line just outside it is still (loosely) magenta, then
    rebuild the corners from the shifted edges. The ratio mask misses the darkest strip of paper in the frame
    lip's shadow; without this the art stops a few px short and a magenta line shows."""
    import numpy as np
    H, W = rgb.shape[:2]
    loose = loose_magenta(rgb)
    q = np.asarray(quad, "float64")
    c = q.mean(axis=0)
    lines = []
    for i in range(4):
        p0, p1 = q[i], q[(i + 1) % 4]
        t = (p1 - p0) / max(np.linalg.norm(p1 - p0), 1e-6)
        nrm = np.array([t[1], -t[0]])
        if np.dot(nrm, (p0 + p1) / 2 - c) < 0:
            nrm = -nrm
        ts = np.linspace(0.12, 0.88, 40)
        base = p0[None, :] + (p1 - p0)[None, :] * ts[:, None]
        d = 0
        for step in range(1, max_px + 1):
            pts = np.round(base + nrm * step).astype(int)
            ok = (pts[:, 0] >= 0) & (pts[:, 0] < W) & (pts[:, 1] >= 0) & (pts[:, 1] < H)
            if not ok.all() or loose[pts[:, 1], pts[:, 0]].mean() < 0.5:
                break
            d = step
        lines.append((p0 + nrm * d, p1 + nrm * d))
    out = []
    for i in range(4):
        a0, a1 = lines[(i - 1) % 4]
        b0, b1 = lines[i]
        x = np.cross(_line(a0, a1), _line(b0, b1))
        if abs(x[2]) < 1e-9:
            return np.asarray(quad, "float32")
        out.append(x[:2] / x[2])
    return np.array(out, "float32")


def find_frame(rgb, min_fill=0.8):
    """Corners of the magenta picture area as a float32 (4,2) array ordered tl,tr,br,bl, plus checks.
    Copes with an off-axis (perspective) frame, window-bar shadows across the paper and a prop clipping one
    corner. Returns (quad, info) or (None, reason)."""
    import cv2
    import numpy as np
    mask = magenta_mask(rgb).astype("uint8") * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), "uint8"))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), "uint8"))
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cs:
        return None, "no magenta picture area found"
    c = max(cs, key=cv2.contourArea)
    H, W = mask.shape
    solid = np.zeros_like(mask)
    cv2.drawContours(solid, [c], -1, 255, -1)              # holes (deep shadow bars) count as paper
    area = float((solid > 0).sum())
    if area < 0.02 * W * H:
        return None, "the frame is too small in the picture"
    hull = cv2.convexHull(c)
    quad = order_quad(refine_quad(rgb, order_quad(_quad_from_hull(hull))))
    if not cv2.isContourConvex(quad.reshape(-1, 1, 2)):
        return None, "the picture area is not a clean four-sided shape"
    qarea = cv2.contourArea(quad)
    fill = area / qarea if qarea else 0
    if fill < min_fill or fill > 1.08:
        return None, f"the frame is partly hidden (only {min(fill, 1):.0%} of it is clear)"
    if quad[:, 0].min() < 2 or quad[:, 1].min() < 2 or quad[:, 0].max() > W - 3 or quad[:, 1].max() > H - 3:
        return None, "the frame touches the edge of the picture"
    top = math.dist(quad[0], quad[1])
    bottom = math.dist(quad[3], quad[2])
    left = math.dist(quad[0], quad[3])
    right = math.dist(quad[1], quad[2])
    asp = true_aspect(quad, (W, H))
    if not 0.35 < asp < 2.8:
        return None, f"the picture area has an impossible shape ({asp:.2f} wide:tall)"
    return quad, {"aspect": asp, "screen_aspect": ((top + bottom) / 2) / ((left + right) / 2),
                  "px": [round((top + bottom) / 2), round((left + right) / 2)], "fill": round(fill, 3),
                  "skew": round(max(left, right) / max(min(left, right), 1), 3)}


def order_quad(pts):
    import numpy as np
    pts = np.asarray(pts, "float32")
    s = pts.sum(axis=1)
    d = pts[:, 0] - pts[:, 1]
    return np.array([pts[s.argmin()], pts[d.argmax()], pts[s.argmax()], pts[d.argmin()]], "float32")


def pick_print(arts, planned_shape, measured_aspect, tolerance):
    """Print JPG for this frame: the planned shape when the measured frame agrees (within tolerance),
    otherwise the print whose shape is nearest the measured frame. Returns (path, shape_tag, note)."""
    def tag_of(p):
        for t in RATIO:
            if f"_{t}_" in p.name:
                return t
        return None
    by = {tag_of(p): p for p in arts if tag_of(p)}
    if not by:
        raise NotConfigured("No print JPGs found in 01-Printables for the room mockups.")
    if planned_shape in by and abs(math.log(measured_aspect / RATIO[planned_shape])) <= tolerance:
        return by[planned_shape], planned_shape, ""
    best = min(by, key=lambda t: abs(math.log(measured_aspect / RATIO[t])))
    return by[best], best, f"frame drawn {measured_aspect:.2f} wide:tall, used the {best} print instead of {planned_shape}"


# ---------- compositing ----------
def composite(scene_path, quad, art_path, out_path, quality=92):
    """Warp the art into quad (cover-cropped to the frame's own shape, never stretched), lit by the scene."""
    import cv2
    import numpy as np
    from PIL import Image
    from .mockups import fit_art
    scene = np.array(Image.open(scene_path).convert("RGB"))
    H, W = scene.shape[:2]
    top = math.dist(quad[0], quad[1]); bottom = math.dist(quad[3], quad[2])
    left = math.dist(quad[0], quad[3]); right = math.dist(quad[1], quad[2])
    qw, qh = (top + bottom) / 2, (left + right) / 2
    k = 1.5                                                    # work above the on-screen size, then warp down
    size = (max(64, round(qw * k)), max(64, round(qh * k)))
    with tempfile.TemporaryDirectory() as td:
        fitted = Path(td) / "fit.png"
        cropped = fit_art(art_path, size, fitted)
        art = np.array(Image.open(fitted).convert("RGB"))
    aw, ah = size
    src = np.array([[0, 0], [aw - 1, 0], [aw - 1, ah - 1], [0, ah - 1]], "float32")
    c = quad.mean(axis=0)
    grown = quad + (quad - c) / np.linalg.norm(quad - c, axis=1, keepdims=True) * 1.5   # cover the magenta fringe
    M = cv2.getPerspectiveTransform(src, grown.astype("float32"))
    warped = cv2.warpPerspective(art, M, (W, H), flags=cv2.INTER_CUBIC).astype("float32")
    mask = np.zeros((H, W), "uint8")
    cv2.fillConvexPoly(mask, grown.round().astype("int32"), 255, lineType=cv2.LINE_AA)
    mask = cv2.GaussianBlur(mask, (0, 0), 0.7).astype("float32")[..., None] / 255
    # the scene's own light across the picture area (the flat magenta shows it), kept gentle
    luma = scene.astype("float32") @ np.array([0.299, 0.587, 0.114], "float32")
    inside = mask[..., 0] > 0.99
    med = np.median(luma[inside]) if inside.any() else 1.0
    shade = cv2.GaussianBlur(np.clip(luma / max(med, 1.0), 0.75, 1.2), (0, 0), 6)
    shade = (1 + 0.7 * (shade - 1))[..., None]
    out = scene.astype("float32") * (1 - mask) + np.clip(warped * shade, 0, 255) * mask
    Image.fromarray(out.round().astype("uint8")).save(out_path, "JPEG", quality=quality, dpi=(72, 72), optimize=True)
    return round(cropped, 3)


# ---------- scenes (made once, cached) ----------
def cache_dir(settings):
    p = Path(_cfg(settings, "rooms_cache"))
    p = p if p.is_absolute() else ROOT / p
    p.mkdir(parents=True, exist_ok=True)
    return p


def scene_file(settings, scene):
    slot, key, shape, frame, text = scene
    h = hashlib.sha1(scene_prompt(shape, frame, text).encode()).hexdigest()[:8]
    base = cache_dir(settings) / f"{slot:02d}_{key}_{h}"
    for ext in (".png", ".jpg", ".jpeg", ".webp"):          # the engine may hand back any of these
        if base.with_suffix(ext).is_file():
            return base.with_suffix(ext)
    return base.with_suffix(".png")


def _read_frame(path):
    import numpy as np
    from PIL import Image
    with Image.open(path) as im:
        return find_frame(np.array(im.convert("RGB")))


def ensure_scene(settings, scene, adapter):
    """Cached scene and its frame. A cached scene that reads fine costs nothing; otherwise kie.ai draws it
    (up to `room_attempts` tries, each overwriting the last file, nothing deleted).
    Returns (path, quad, info, new_scene_calls) or (None, None, reason, calls)."""
    slot, key, shape, frame, text = scene
    path = scene_file(settings, scene)
    calls, reason = 0, "scene could not be made"
    if path.is_file():
        quad, info = _read_frame(path)
        if quad is not None:
            return path, quad, info, 0
        reason = info
    for _ in range(int(_cfg(settings, "room_attempts"))):
        if adapter is None:
            return None, None, reason if path.is_file() else "scene is not cached and no image engine is available", calls
        calls += 1
        res = adapter.generate(scene_prompt(shape, frame, text), path, "1:1", _cfg(settings, "room_resolution"))
        path = Path(res["path"])
        if not path.is_file():
            continue
        quad, info = _read_frame(path)
        if quad is not None:
            return path, quad, info, calls
        reason = info
    return None, None, reason, calls


def build_rooms(out_dir, arts, settings, adapter=None, scenes=None):
    """Make the room mockups into out_dir. Returns (made, notes, failed) where failed lists slots not built."""
    scenes = scenes or SCENES
    made, notes, failed = [], [], []
    tol = float(_cfg(settings, "room_shape_tolerance"))

    def one(scene):
        slot, key, shape, frame, text = scene
        try:
            path, quad, info, spent = ensure_scene(settings, scene, adapter)
        except Exception as e:  # noqa: BLE001  (engine errors, network)
            return scene, None, f"{e}", 0
        if path is None:
            return scene, None, info, spent
        return scene, (path, quad, info), "", spent

    with ThreadPoolExecutor(max_workers=int(_cfg(settings, "room_workers"))) as pool:
        results = list(pool.map(one, scenes))
    for scene, got, err, spent in results:
        slot, key, shape, frame, text = scene
        if got is None:
            failed.append(slot)
            notes.append(f"room {slot:02d} {key}: not built ({err})")
            continue
        path, quad, info = got
        art, tag, note = pick_print(arts, shape, info["aspect"], tol)
        out = out_dir / f"{slot:02d}_{key}.jpg"
        cropped = composite(path, quad, art, out, int(_cfg(settings, "room_jpg_quality")))
        made.append({"file": out.name, "slot": slot, "room": True, "print": tag, "frame_px": info["px"],
                     "art_cropped": cropped, "mb": round(out.stat().st_size / 1e6, 1), "new_scene_calls": spent})
        if note:
            notes.append(f"{out.name}: {note}")
        if cropped > 0.1:
            notes.append(f"{out.name}: {cropped:.0%} of the art was cropped to fit the frame; check it by eye")
    return sorted(made, key=lambda m: m["slot"]), notes, failed


# =====================================================================================================
# v2 recipe (Mockup_Docs/Mockup_Style_Guide.md sections 2, 3, 3a, 3b, 4a-4c). v1 SCENES above stay as they are; v2 builds
# a brief per print (room matched to the art), asks for a 3/4 off-axis scene whose magenta paper RECEIVES the
# window-bar shadow, and composites with the light read from that magenta at full strength.
# =====================================================================================================
FRAME_V2 = {"oak": "a natural oak frame about 2 cm wide", "white": "a white wood frame", "black": "a thin matte black frame",
            "walnut": "a slim walnut frame", "gold": "an ornate antique gold frame", "carved": "a carved dark wood frame",
            "brass": "a slim brass metal frame"}
DARK_FRAMES = {"black", "walnut", "gold", "carved", "brass"}

# guide 3b, one row per mood. value = value keys the row suits (value key is matched first).
PROFILES_V2 = [
    {"key": "cute_light", "words": ["cat", "kitten", "dog", "puppy", "bunny", "rabbit", "fox", "bear", "bird", "owl",
                                    "animal", "book", "reading", "read", "library", "cozy", "cute"],
     "value": ["light", "mid"],
     "room_a": "a sunny reading nook: a built-in window seat with plump cushions and a chunky knit throw, a low side "
               "table, warm wooden floorboards",
     "room_b": "a cozy bedroom with soft linen bedding and a reading lamp",
     "wall": "warm cream painted plaster",
     "props": "a stack of hardback books, an open book lying face-down, a white teacup on a saucer, a chunky knit "
              "throw and a small potted plant",
     "prop_accent": "the knit throw and one cushion",
     "light": "bright morning sun", "time": "about 9 am", "frame": "oak"},
    {"key": "dark_moody", "words": ["gothic", "moody", "dark", "vintage", "oil", "skull", "raven", "witch", "ghost",
                                    "victorian", "academia"],
     "value": ["dark", "mid"],
     "room_a": "a dark green panelled study with a mantel", "room_b": "a mantel corner with old books",
     "wall": "deep green panelled", "props": "old leather books, apothecary jars, candles and dried flowers",
     "prop_accent": "the candle glass and dried flowers", "light": "a single shaft of low sun",
     "time": "late afternoon", "frame": "gold"},
    {"key": "bold_graphic", "words": ["pop", "graphic", "bold", "maximalist", "retro", "groovy", "abstract"],
     "value": ["light", "mid", "dark"],
     "room_a": "an eclectic living room with a painted accent wall and a velvet sofa", "room_b": "a bar cart corner",
     "wall": "accent painted", "props": "a bar cart, a stack of records, colourful ceramics",
     "prop_accent": "the cushions and ceramics", "light": "warm late sun", "time": "about 5 pm", "frame": "black"},
    {"key": "food_drink", "words": ["wine", "coffee", "cocktail", "food", "kitchen", "fruit", "lemon", "drink", "bar"],
     "value": ["light", "mid", "dark"],
     "room_a": "a kitchen with open wooden shelves", "room_b": "a bar cart corner", "wall": "warm white",
     "props": "bottles, glasses, a wooden cutting board and a bowl of fruit", "prop_accent": "the fruit and a tea towel",
     "light": "golden hour sun", "time": "about 6 pm", "frame": "black"},
    {"key": "botanical_calm", "words": ["botanical", "leaf", "flower", "floral", "japandi", "scandi", "minimal", "line",
                                        "plant", "tree"],
     "value": ["light", "mid"],
     "room_a": "a calm Japandi living room with a low oak bench", "room_b": "a linen bedroom", "wall": "oat linen-toned",
     "props": "a ceramic vase with one branch, folded linen, a low oak table", "prop_accent": "the linen and the vase",
     "light": "soft morning sun", "time": "about 8 am", "frame": "oak"},
    {"key": "neon_night", "words": ["anime", "neon", "cyber", "tokyo", "japan", "night", "city", "gaming"],
     "value": ["dark", "mid"],
     "room_a": "a dim gaming room", "room_b": "a dark bedroom", "wall": "charcoal",
     "props": "a monitor, headphones and a small figure", "prop_accent": "an LED strip glow",
     "light": "night with practical lights", "time": "night", "frame": "black"},
]

# Buyer personas (Tony 2026-11-07): a room mockup should look like a REAL BUYER'S OWN PHOTO - someone with taste
# printed the art, put it up in her own room and took a candid picture - never a department-store catalogue.
# Each persona is a coherent room: named furniture pieces with era/provenance that belong together, one personal
# palette, and incidental un-arranged clutter (left where she left it, not a posed prop group).
# Keys: who, room, furniture, palette, accent_hook (where the art's accent colours turn up), clutter,
# floor, wall, place (where the frame is: hung over / leaning on a named piece).
PERSONAS = {
    "cute_light": [
        {"key": "bookish_renter",
         "who": "a bookish illustrator in her late twenties who rents a 1920s apartment and furnishes it from flea "
                "markets",
         "room": "the reading corner of her living room",
         "furniture": "a thrifted 1960s teak sideboard with slightly worn veneer, a white vintage tulip side table, "
                      "a low-slung linen armchair with a wool throw she actually uses, a faded kilim rug, and a "
                      "big pothos she keeps alive in a terracotta pot",
         "palette": "warm cream walls, honey teak, faded tomato red, off-black",
         "accent_hook": "the kilim rug and one thrifted ceramic",
         "clutter": "a half-drunk mug of tea left on the tulip table, a paperback lying open face-down on the "
                    "armrest, reading glasses, and a phone charger cable trailing off the sideboard",
         "floor": "light oak parquet", "wall": "warm cream painted plaster",
         "place": "hung on the wall above the teak sideboard"},
        {"key": "young_mom_modern",
         "who": "a stay-at-home mum with her own modern taste, in a sunny 1930s house she is slowly doing up",
         "room": "the bay-window corner of her sitting room",
         "furniture": "a mid-century oak bench under the window, a Danish-style rattan lounge chair bought second "
                      "hand, a jute rug, a fiddle-leaf fig that leans toward the light, and a woven basket",
         "palette": "warm white walls, pale oak, natural cane, soft rust and black accents",
         "accent_hook": "a rust linen cushion and the basket's stripe",
         "clutter": "a child's picture book left on the rug, a coffee mug on the bench, a cardigan thrown over "
                    "the chair's arm, and slippers kicked off by the chair",
         "floor": "light oak herringbone parquet", "wall": "warm white painted plaster",
         "place": "leaning against the wall on the oak bench"},
    ],
    "dark_moody": [
        {"key": "academia_collector",
         "who": "a PhD student who collects old books and antique-shop finds",
         "room": "her small study",
         "furniture": "a Victorian mahogany writing desk, a worn leather club chair, an inherited brass lamp, "
                      "overflowing bookshelves, and a threadbare Persian rug",
         "palette": "deep green walls, oxblood, aged brass, dark wood",
         "accent_hook": "the rug and the chair's leather",
         "clutter": "a stack of library books with paper slips, a cold cup of coffee, a pen left on an open "
                    "notebook, and a wool scarf over the chair back",
         "floor": "dark worn floorboards", "wall": "deep green painted panelling",
         "place": "hung on the wall above the writing desk"},
        {"key": "gothic_romantic",
         "who": "a tattoo artist with a soft spot for gothic antiques",
         "room": "the corner of her bedroom",
         "furniture": "a carved dark-oak chest of drawers from an estate sale, a velvet armchair, iron candle "
                      "holders, and a trailing ivy plant",
         "palette": "charcoal walls, plum velvet, black iron, candle gold",
         "accent_hook": "the velvet chair",
         "clutter": "a burnt-down candle, a ring dish with rings in it, a sketchbook left open, and boots by the "
                    "chair",
         "floor": "dark stained floorboards", "wall": "charcoal painted plaster",
         "place": "leaning against the wall on the chest of drawers"},
    ],
    "bold_graphic": [
        {"key": "maximalist_creative",
         "who": "a graphic designer in her thirties with a maximalist, colourful flat",
         "room": "her living room",
         "furniture": "a 1970s mustard velvet sofa found on Marketplace, a chrome-and-glass coffee table, a "
                      "record player on a teak sideboard, and a big monstera",
         "palette": "one painted accent wall, mustard, chrome, teak, a bright pop colour",
         "accent_hook": "the painted accent wall and the sofa cushions",
         "clutter": "a stack of vinyl records leaning on the sideboard, headphones on the sofa, a coffee cup on "
                    "the table and a tote bag dropped on the floor",
         "floor": "honey parquet", "wall": "painted accent",
         "place": "hung on the accent wall above the sideboard"},
        {"key": "city_studio",
         "who": "a young city professional with good taste and a small studio flat",
         "room": "the corner by her desk",
         "furniture": "a vintage chrome cantilever chair, a white tulip table used as a desk, a Bauhaus-style "
                      "globe lamp, and a snake plant",
         "palette": "white walls, chrome, black, one bold accent",
         "accent_hook": "a notebook and a ceramic cup",
         "clutter": "a laptop half closed, a phone face down, a water glass and a cable trailing to the wall",
         "floor": "pale wood floorboards", "wall": "white painted plaster",
         "place": "leaning against the wall on the floor beside the desk"},
    ],
    "food_drink": [
        {"key": "home_cook",
         "who": "a keen home cook who hosts friends every weekend",
         "room": "her kitchen-dining corner",
         "furniture": "open reclaimed-wood shelves, a scrubbed pine farmhouse table, mismatched bentwood chairs "
                      "from a café clearance, and a herb pot on the sill",
         "palette": "warm white walls, pine, terracotta, brass",
         "accent_hook": "a tea towel and a bowl of fruit",
         "clutter": "a used wine glass, a cork, a cookbook left open, and a cutting board with crumbs",
         "floor": "terracotta tiles", "wall": "warm white painted plaster",
         "place": "hung on the wall above the table"},
    ],
    "botanical_calm": [
        {"key": "japandi_minimalist",
         "who": "a yoga teacher who lives simply in a calm, light flat",
         "room": "her bedroom corner",
         "furniture": "a low oak bench, a paper floor lamp, a linen-covered bed, and an olive tree in a clay pot",
         "palette": "oat walls, pale oak, linen, sage",
         "accent_hook": "the linen bedding and a ceramic vase",
         "clutter": "a folded jumper on the bench, a cup of tea, a book with a pencil in it, and a phone "
                    "charging on the floor",
         "floor": "pale oak boards", "wall": "oat limewash",
         "place": "leaning against the wall on the low oak bench"},
    ],
    "neon_night": [
        {"key": "gamer_artist",
         "who": "a digital artist and gamer in a small apartment",
         "room": "her desk corner at night",
         "furniture": "a desk with a monitor, a mesh office chair, a small shelf of figures, and a warm desk lamp",
         "palette": "charcoal walls, warm lamp glow, one neon accent",
         "accent_hook": "an LED strip glow",
         "clutter": "an energy drink can, headphones on the desk, a hoodie over the chair, and a tangle of cables",
         "floor": "dark laminate", "wall": "charcoal painted",
         "place": "hung on the wall above the desk"},
    ],
}


def pick_persona(profile_key, subject, accents=None):
    """Deterministic buyer persona for a print: the persona whose palette/accent hook names one of the art's
    accent colours wins; ties are broken by a hash of the subject so different prints get different rooms."""
    options = PERSONAS.get(profile_key) or PERSONAS["cute_light"]
    colour_words = {w for a in (accents or []) for w in a.get("name", "").split() if w not in ("pale", "deep", "warm")}
    h = int(hashlib.sha1(subject.encode()).hexdigest()[:8], 16)

    def score(i_p):
        i, p = i_p
        text = f"{p['palette']} {p['accent_hook']}".lower()
        return (sum(w in text for w in colour_words), -((i - h) % len(options)))
    return max(enumerate(options), key=score)[1]


def _colour_name(rgb):
    """Plain colour word for a prompt (not exact; the art's real pixels are never touched)."""
    import colorsys
    r, g, b = [x / 255 for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    deg = h * 360
    if s < 0.12:
        return "warm grey" if r > b else "cool grey"
    names = [(15, "brick red"), (40, "burnt orange"), (55, "warm tan"), (70, "mustard"), (160, "sage green"),
             (200, "teal"), (250, "dusty blue"), (290, "violet"), (335, "plum"), (361, "brick red")]
    base = next(n for lim, n in names if deg < lim)
    if base in ("brick red", "burnt orange", "warm tan") and l < 0.4 and s < 0.6:
        return "deep walnut brown" if l < 0.25 else "warm walnut brown"
    if base == "warm tan" and s > 0.55 and l < 0.55:
        base = "ochre"
    if base == "brick red" and l > 0.4 and s > 0.6:
        base = "tomato red"
    return ("pale " if l > 0.75 else "deep " if l < 0.25 else "") + base


def analyze_print(path, k=6):
    """Value key (mean brightness) and 2 accent colours (k-means, near-white and near-black dropped), guide 3b."""
    import cv2
    import numpy as np
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    with Image.open(path) as im:
        im.draft("RGB", (400, 600))
        a = np.array(im.convert("RGB").resize((200, 300))).astype("float32")
    mean = float((a @ np.array([0.299, 0.587, 0.114], "float32")).mean() / 255)
    key = "light" if mean >= 0.55 else "dark" if mean < 0.35 else "mid"
    _, lab, cen = cv2.kmeans(a.reshape(-1, 3), k, None, (3, 30, 1.0), 3, cv2.KMEANS_PP_CENTERS)
    counts = np.bincount(lab.ravel(), minlength=k)
    acc = []
    for i in np.argsort(-counts):
        c = cen[i]
        lum = float(c @ np.array([0.299, 0.587, 0.114]))
        sat = (c.max() - c.min()) / max(c.max(), 1)
        if lum > 200 or lum < 50:                            # near-white paper / near-black ink
            continue
        acc.append({"rgb": [int(x) for x in c], "share": round(float(counts[i] / counts.sum()), 3),
                    "sat": round(float(sat), 2), "name": _colour_name(c)})
    acc.sort(key=lambda x: -(x["share"] * (0.3 + x["sat"])))   # common AND colourful first
    return {"mean": round(mean, 3), "value_key": key, "accents": acc[:2]}


def pick_profile(subject, value_key):
    """Value key first, then subject words (guide 3b rule of thumb)."""
    words = set("".join(ch.lower() if ch.isalnum() else " " for ch in subject).split())
    words |= {w[:-1] for w in words if w.endswith("s")}

    def score(p):
        return (3 if value_key in p["value"] else -5) + 2 * len(words & set(p["words"]))
    return max(PROFILES_V2, key=score)


FRAME_WIDEN = 1.12   # GPT Image 2 draws portrait frames ~12-16% narrower than asked (3 of 3 tries, 2026-11-07),
                     # so the prompt asks for a slightly wider frame and the full print still fits uncropped


def _ask_ratio(w, h, widen=FRAME_WIDEN):
    """Ratio to ask the model for, compensated for its narrow-frame habit, as 'a:b' with small whole numbers."""
    target = (float(w) / float(h)) * (widen if float(w) < float(h) else 1 / widen)
    best = min(((a, b) for a in range(1, 12) for b in range(1, 12)), key=lambda ab: abs(ab[0] / ab[1] - target))
    return f"{best[0]}:{best[1]}"


def brief_v2(subject, analysis, shape="2x3", slot=8):
    """Everything the slot-8 'hero room A' prompt needs, picked from the print (guide 3 shot list + 3b) plus a
    buyer persona (whose real room it is; Tony 2026-11-07: a buyer's own candid photo, never a catalogue)."""
    p = pick_profile(subject, analysis["value_key"])
    persona = pick_persona(p["key"], subject, analysis.get("accents"))
    acc = [a["name"] for a in analysis["accents"]] or ["warm cream"]
    if len(acc) == 1:
        acc.append("natural linen")
    w, h = {"ISO_A1": ("5", "7")}.get(shape, shape.split("x"))
    return {"slot": slot, "shot": "hero_room_a", "profile": p["key"], "persona": persona["key"], "shape": shape,
            "who": persona["who"], "room": persona["room"], "furniture": persona["furniture"],
            "palette": persona["palette"], "clutter": persona["clutter"], "floor": persona["floor"],
            "wall": persona["wall"], "accent_1": acc[0], "accent_2": acc[1], "prop_accent": persona["accent_hook"],
            "frame": p["frame"],
            "ratio": f"{w}:{h}", "ask_ratio": _ask_ratio(w, h), "orientation": "portrait" if int(w) < int(h) else "landscape",
            "angle": "three-quarter view from the right, the camera turned about 30 degrees off the wall, so the "
                     "frame is clearly seen in perspective: its near right edge is noticeably taller than its far left "
                     "edge and its top and bottom edges converge toward the left",
            "distance": "medium-close shot from standing height, the frame fills about 55 to 60 percent of the "
                        "image height",
            "light": p["light"], "time": p["time"], "side": "left",
            "lean_or_hang": persona["place"]}


def _shape_words(ratio):
    w, h = (float(x) for x in ratio.split(":"))
    if h > w:
        return f"its height is {h / w:.2f} times its width, not a tall narrow panel"
    return f"its width is {w / h:.2f} times its height"


def _persona_text(b):
    return (
        f"A candid photo that a real buyer took on her own phone of the print she just put up in her own home: "
        f"{b['who']}. This is {b['room']}, a real lived-in room she has put together over years: {b['furniture']}. "
        f"The pieces belong together and to her; her palette is {b['palette']}, and {b['accent_1']} and "
        f"{b['accent_2']} turn up naturally in {b['prop_accent']}. {b['wall'].capitalize()} walls, {b['floor']} floor.\n"
        f"Lived-in props that belong to her and sit where she actually left them, not arranged for a photo: "
        f"{b['clutter']}. True lifestyle, never staged lifestyle.\n"
        f"Camera: {b['angle']}; {b['distance']}; phone or 35mm film photo feel: natural, slightly imperfect "
        f"framing, mixed real-world light, a bit of depth of field, fine grain. Not a home-decor magazine shoot, "
        f"not a catalogue.\n")


AVOID_V2 = ("Avoid: straight-on catalogue look, department-store or showroom styling, home-decor magazine polish, "
            "posed prop groups, matching furniture sets, furniture that does not belong in the room, empty showroom, "
            "tiny frame, multiple frames, mirror reflections of the picture area, glossy glass, harsh flash, "
            "overexposed white walls, cartoon or 3D-render look.")


def scene_prompt_v2(b, plate=False):
    """Guide 4a scene plate + 4b avoid line, filled from a brief, written as the buyer's own candid photo.
    plate=True is the TEMPLATE plate: soft light with no baked shadows and a plain magenta panel instead of a
    frame, because the template's own layers add the frame, mat, glass and shadows (switchable)."""
    if plate:
        return (
            _persona_text(b) +
            f"Light: soft, warm, diffused daylight from a window just out of frame on the {b['side']}, gentle falloff "
            f"across the wall. No hard shadows, no window-bar shadows, no sun patches, no leaf shadows.\n"
            f"One flat rectangular panel, {b['orientation']}, {b['lean_or_hang']}; its proportions are {b['ask_ratio']} "
            f"({_shape_words(b['ask_ratio'])}). The panel's whole front face and its thin edges are one flat sheet "
            f"of solid matte magenta (#FF00FF): no frame moulding, no mat, no glass, no pattern, no image, no text. "
            f"The magenta receives the same soft light as the wall; the panel casts only a soft contact shadow.\n"
            f"All four corners of the panel are visible and nothing overlaps it. No other artwork, no posters, no "
            f"screens showing images, no text, no logos, no people, no animals.\n" + AVOID_V2)
    return (
        _persona_text(b) +
        f"Light: {b['light']} at {b['time']}, the main light. A window just out of frame on the {b['side']} "
        f"throws a crisp shadow of its window bars (mullions) as a skewed grid of light and shadow across the wall "
        f"(parallelograms that follow the wall's perspective, not upright squares). The frame hangs inside that patch "
        f"of sunlight, so the same grid continues across the frame and the picture: one vertical and one horizontal "
        f"window-bar shadow (both skewed like the rest of the grid) cross the picture as soft darker bands, while "
        f"most of the picture stays in bright sun. Everything in the image follows that one light direction. The rest of the room is in soft natural shade, not overexposed.\n"
        f"One picture frame, {FRAME_V2[b['frame']]}, {b['orientation']}, {b['lean_or_hang']}. The picture area inside the "
        f"frame has the exact proportions {b['ask_ratio']} ({_shape_words(b['ask_ratio'])}); keep those proportions. "
        f"The frame casts a soft natural shadow on the wall behind it, on the side away from the window.\n"
        f"The picture area inside the frame is a single flat sheet of matte magenta paper (#FF00FF): no pattern, "
        f"no image, no text, no mat, no glass glare. The magenta paper receives the room's light exactly like the "
        f"wall: it is brighter where the sun hits it and darker where the window-bar shadow and the frame's edge "
        f"shadow fall on it.\n"
        f"All four corners of the picture area are visible. No other artwork, no posters, no screens showing images, "
        f"no text, no logos, no people, no animals.\n" + AVOID_V2)


def _warp_art(art_path, quad, shape_aspect, W, H):
    """Real print pixels warped into the quad. The print's own shape is used (crop only if it differs)."""
    import cv2
    import numpy as np
    from PIL import Image
    from .mockups import fit_art
    q = np.asarray(quad, "float32")
    qh = max(math.dist(q[0], q[3]), math.dist(q[1], q[2]))
    ah = max(64, round(qh * 1.6))
    aw = max(64, round(ah * shape_aspect))
    with tempfile.TemporaryDirectory() as td:
        fitted = Path(td) / "fit.png"
        cropped = fit_art(art_path, (aw, ah), fitted)
        art = np.array(Image.open(fitted).convert("RGB")).astype("float32") / 255
    src = np.array([[0, 0], [aw - 1, 0], [aw - 1, ah - 1], [0, ah - 1]], "float32")
    M = cv2.getPerspectiveTransform(src, q)
    warped = cv2.warpPerspective(art, M, (W, H), flags=cv2.INTER_AREA if ah > qh else cv2.INTER_CUBIC,
                                 borderMode=cv2.BORDER_REPLICATE)
    return warped, cropped, M, (aw, ah)


def _luma(x):
    import numpy as np
    return x @ np.array([0.299, 0.587, 0.114], "float32")


def composite_v2(scene_path, quad, art_path, out_path, shape_aspect, frame="oak", quality=92, settings=None):
    """Guide 4c compositing. Returns a report dict (light range, shadow cover, hue drift, flags).
    Steps: light map from the magenta itself (V / 95th pct, 0.2-1.05, sigma ~1.2 px, 100%); exposure match
    (art 99th pct luma = 0.92 x lit-wall 95th pct luma); white balance 60%; frame lip shadow; faint sheen for
    dark frames only; grain match; accuracy guard. The art pixels are only scaled, never redrawn."""
    import cv2
    import numpy as np
    from PIL import Image
    s = settings or {}
    scene8 = np.array(Image.open(scene_path).convert("RGB"))
    scene = scene8.astype("float32") / 255
    H, W = scene.shape[:2]
    q = np.asarray(quad, "float32")
    c = q.mean(axis=0)
    grown = q + (q - c) / np.linalg.norm(q - c, axis=1, keepdims=True) * 1.5     # cover the magenta fringe
    warped, cropped, M, (aw, ah) = _warp_art(art_path, grown, shape_aspect, W, H)
    poly = np.zeros((H, W), "uint8")
    cv2.fillConvexPoly(poly, grown.round().astype("int32"), 255, lineType=cv2.LINE_AA)
    alpha = cv2.GaussianBlur(poly, (0, 0), 0.7).astype("float32")[..., None] / 255
    inside = poly > 250

    # 1. light map from the magenta, normalised by its 95th percentile. (R+B)/2 rather than max(R,G,B): in sun
    #    the magenta's red channel clips at 255, which would flatten the window-bar shadow pattern.
    V = (scene[..., 0] + scene[..., 2]) / 2
    core = cv2.erode(poly, np.ones((7, 7), "uint8")) > 250                # away from the frame's fringe
    mag = core & magenta_mask(scene8)
    good = mag if mag.sum() > 0.5 * core.sum() else core
    p95 = float(np.percentile(V[good], 95)) if good.any() else 1.0
    L = np.clip(V / max(p95, 1e-3), 0.2, 1.05)
    m = core.astype("float32")
    fillL = cv2.GaussianBlur(L * m, (0, 0), 6) / np.maximum(cv2.GaussianBlur(m, (0, 0), 6), 1e-4)
    L = np.where(core, L, fillL)                                              # extend the light to the fringe
    # magenta fringe just outside the quad (paper peeking out under the frame lip, often in deep shade): it is
    # the print too, so the art is extended over it (warp uses edge-replicate) at that pixel's own light
    near = cv2.dilate(poly, np.ones((7, 7), "uint8")) > 0
    fringe = near & ~inside & loose_magenta(scene8)
    fringe = cv2.morphologyEx(fringe.astype("uint8"), cv2.MORPH_CLOSE, np.ones((3, 3), "uint8")) > 0
    fringe &= near & ~inside
    L = np.where(fringe, np.clip(V / max(p95, 1e-3), 0.2, 1.05), L)
    alpha = np.maximum(alpha, fringe[..., None].astype("float32"))
    L = cv2.GaussianBlur(L, (0, 0), float(s.get("room_light_sigma", 1.2)))
    L = np.clip(L, 0.2, 1.05)

    # 2. exposure match against a lit wall sample just outside the frame
    ring_out = cv2.fillConvexPoly(np.zeros((H, W), "uint8"),
                                  (c + (q - c) * 1.45).round().astype("int32"), 255)
    ring_in = cv2.fillConvexPoly(np.zeros((H, W), "uint8"), (c + (q - c) * 1.18).round().astype("int32"), 255)
    ring = (ring_out > 0) & (ring_in == 0) & ~magenta_mask(scene8)
    sat = (scene.max(axis=2) - scene.min(axis=2)) / np.maximum(scene.max(axis=2), 1e-3)
    wall = ring & (sat < 0.35)
    if wall.sum() < 200:
        wall = ring
    wl = _luma(scene)[wall]
    wall95 = float(np.percentile(wl, 95)) if wl.size else 0.9
    lit = wall & (_luma(scene) >= np.percentile(wl, 80)) if wl.size else wall
    art_l = _luma(warped)[inside]
    art99 = float(np.percentile(art_l, 99)) if art_l.size else 1.0
    gain = 0.92 * wall95 / max(art99, 1e-3)
    # shadow depth check: if the model drew the paper's shadows shallower than the wall's (sun vs shade luma),
    # deepen the light map with a power curve so the art's shade matches the wall's (capped, never flattened)
    depth_gamma = 1.0
    if wl.size and good.any():
        wall_depth = float(np.percentile(wl, 10) / max(wall95, 1e-3))
        mag_depth = float(np.percentile(L[good], 10))
        if mag_depth > 0.85 and 0.2 < wall_depth < mag_depth - 0.1:     # only when the paper came out flat
            depth_gamma = min(math.log(wall_depth) / math.log(min(mag_depth, 0.99)), 2.5)
            L = np.clip(L ** depth_gamma, 0.2, 1.05)

    # 3. white balance toward the lit wall's colour, 60 %
    wrgb = scene[lit].mean(axis=0) if lit.any() else np.ones(3, "float32")
    tint = wrgb / max(float(_luma(wrgb)), 1e-3)
    tint = 1 + 0.6 * (tint - 1)
    tint = tint / float(_luma(tint))

    art = warped * gain * tint * L[..., None]

    # 5. frame lip shadow on the light side (the side whose lit wall is brighter)
    lum = _luma(scene)
    left_side = (np.arange(W)[None, :] < c[0]) & wall
    right_side = (np.arange(W)[None, :] >= c[0]) & wall
    light_left = (lum[left_side].mean() if left_side.any() else 0) >= (lum[right_side].mean() if right_side.any() else 0)
    Minv = np.linalg.inv(M)
    ys, xs = np.nonzero(inside)
    pts = np.stack([xs, ys, np.ones_like(xs)], 0).astype("float64")
    uv = Minv @ pts
    u = uv[0] / uv[2] / aw                                                    # 0 = art's left edge, 1 = right
    v = uv[1] / uv[2] / ah
    lipw = float(s.get("room_lip_width", 0.025))
    edge = u if light_left else 1 - u
    lip = 0.85 + 0.15 * np.clip(edge / lipw, 0, 1) ** 0.7
    top = np.clip(v / (lipw * 0.6), 0, 1)                                     # a whisper of top-lip shade too
    lip = lip * (0.93 + 0.07 * top)
    lipmap = np.ones((H, W), "float32")
    lipmap[ys, xs] = lip
    art = art * lipmap[..., None]

    # 6. glass sheen, dark frames only, <= 5 %
    if frame in DARK_FRAMES:
        sheen = np.zeros((H, W), "float32")
        sheen[ys, xs] = np.clip(1 - np.abs((u + v) - 0.7) / 0.25, 0, 1) * 0.05
        art = 1 - (1 - art) * (1 - sheen[..., None])

    # 7. grain match: noise level of the wall next to the frame
    hp = scene - cv2.GaussianBlur(scene, (0, 0), 1.5)
    noise = float(np.median(np.abs(_luma(hp)[wall])) * 1.4826) if wall.any() else 0.0
    rng = np.random.default_rng(int(s.get("room_seed", 7)))
    art = art + rng.normal(0, max(noise, 0.002), (H, W, 1)).astype("float32")
    art = np.clip(art, 0, 1)

    # magenta spill on the frame's inner rail (the model tints the wood's inside face red/pink next to the
    # paper): keep each pixel's brightness, give it the frame's own colour sampled a little farther out
    band = (cv2.dilate(poly, np.ones((25, 25), "uint8")) > 0) & ~inside
    far = (cv2.dilate(poly, np.ones((61, 61), "uint8")) > 0) & ~band & ~inside
    sf = scene8.astype("float32")
    rg = (sf[..., 0] + 4) / (sf[..., 1] + 4)
    frame_px = far & (rg > 1.15) & (rg < 1.8)
    spill = band & (rg > 1.9) & (alpha[..., 0] < 0.5)
    spill_px = int(spill.sum())
    if spill_px and frame_px.sum() > 100:
        fc = scene[frame_px].mean(axis=0)
        fc = fc / max(float(fc.max()), 1e-3)
        Vs = scene.max(axis=2)[spill] * 0.85
        scene = scene.copy()
        scene[spill] = Vs[:, None] * fc[None, :]
    out = scene * (1 - alpha) + art * alpha

    # 8. accuracy guard: art colour with the light map divided out vs the source file
    sel = inside & core
    src = warped[sel]
    got = (out[sel] / np.maximum(L[sel][:, None] * lipmap[sel][:, None], 1e-3))
    hs = cv2.cvtColor(src.reshape(-1, 1, 3), cv2.COLOR_RGB2HSV).reshape(-1, 3)
    hg = cv2.cvtColor(np.clip(got, 0, 1).astype("float32").reshape(-1, 1, 3), cv2.COLOR_RGB2HSV).reshape(-1, 3)
    colourful = hs[:, 1] > 0.25
    if colourful.sum() > 50:
        d = np.angle(np.exp(1j * np.radians(hg[colourful, 0] - hs[colourful, 0])), deg=True)
        hue_drift = float(np.median(np.abs(d)))
    else:
        hue_drift = 0.0
    shadow_cover = float((L[inside] < 0.6).mean()) if inside.any() else 0.0     # deep shadow (bars, lip)
    out_of_sun = float((L[inside] < 0.8).mean()) if inside.any() else 0.0
    flags = []
    if hue_drift > 8:
        flags.append(f"art colour drifted {hue_drift:.1f} degrees from the file")
    if shadow_cover > 0.35:
        flags.append(f"shadow covers {shadow_cover:.0%} of the art (limit 35%)")
    Image.fromarray((out * 255).round().astype("uint8")).save(out_path, "JPEG", quality=quality, dpi=(72, 72),
                                                               optimize=True)
    return {"cropped": round(cropped, 3), "gain": round(gain, 3), "wall95": round(wall95, 3),
            "magenta_p95": round(p95, 3), "light_min": round(float(L[inside].min()), 3),
            "shadow_cover": round(shadow_cover, 3), "depth_gamma": round(depth_gamma, 2), "out_of_sun": round(out_of_sun, 3), "hue_drift_deg": round(hue_drift, 2),
            "tint": [round(float(x), 3) for x in tint], "noise": round(noise, 4),
            "light_from": "left" if light_left else "right", "fringe_px": int(fringe.sum()), "spill_px": spill_px, "magenta_found": round(float(mag.sum() / max(core.sum(), 1)), 3),
            "flags": flags}


def scene_file_v2(settings, brief):
    h = hashlib.sha1(scene_prompt_v2(brief).encode()).hexdigest()[:8]
    base = cache_dir(settings) / f"v2_{brief['slot']:02d}_{brief['profile']}_{h}"
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        if base.with_suffix(ext).is_file():
            return base.with_suffix(ext)
    return base.with_suffix(".png")


def light_readable(rgb, quad):
    """True when the magenta inside the frame carries a usable light pattern (some of it is clearly in sun)."""
    import cv2
    import numpy as np
    H, W = rgb.shape[:2]
    poly = cv2.fillConvexPoly(np.zeros((H, W), "uint8"), np.asarray(quad).round().astype("int32"), 255)
    core = cv2.erode(poly, np.ones((7, 7), "uint8")) > 0
    mag = core & magenta_mask(rgb)
    return mag.sum() > 0.6 * max(core.sum(), 1), round(float(mag.sum() / max(core.sum(), 1)), 3)


def ensure_scene_v2(settings, brief, adapter, attempts=2):
    """Cached v2 scene for this brief, else kie.ai draws it (retry once if the corners or light cannot be read).
    Returns (path, quad, info, calls) or (None, None, reason, calls)."""
    import numpy as np
    from PIL import Image
    path = scene_file_v2(settings, brief)
    calls, reason = 0, "scene could not be made"

    def read(p):
        with Image.open(p) as im:
            rgb = np.array(im.convert("RGB"))
        quad, info = find_frame(rgb)
        if quad is None:
            return None, info
        ok, frac = light_readable(rgb, quad)
        if not ok:
            return None, f"the magenta paper could not be read for light ({frac:.0%} found)"
        return quad, {**info, "magenta_frac": frac}

    if path.is_file():
        quad, info = read(path)
        if quad is not None:
            return path, quad, info, 0
        reason = info
    for i in range(attempts):
        if adapter is None:
            return None, None, "scene is not cached and no image engine is available", calls
        calls += 1
        target = path if i == 0 else path.with_name(f"{path.stem}_r{i}{path.suffix}")   # never overwrite
        res = adapter.generate(scene_prompt_v2(brief), target, "1:1", _cfg(settings, "room_resolution"))
        got = Path(res["path"])
        if not got.is_file():
            continue
        quad, info = read(got)
        if quad is not None:
            return got, quad, info, calls
        reason = info
    return None, None, reason, calls


def pick_print_v2(arts, planned_shape, info, tolerance):
    """Print for an off-axis frame. Foreshortening only makes a frame look NARROWER on screen, and the
    perspective solve is noisy on AI-drawn frames (their perspective is rarely exact), so the planned shape is
    kept whenever it lies between the on-screen aspect and the solved true aspect (with tolerance), and the
    whole print is used. Otherwise the nearest print is cover-cropped to the solved aspect (never squeezed).
    Returns (path, tag, fit_aspect, note)."""
    lo = min(info.get("screen_aspect", info["aspect"]), info["aspect"]) * math.exp(-tolerance)
    hi = max(info.get("screen_aspect", info["aspect"]), info["aspect"]) * math.exp(tolerance)
    if lo <= RATIO[planned_shape] <= hi:
        p = next((a for a in arts if f"_{planned_shape}_" in a.name), None)
        if p:
            return p, planned_shape, RATIO[planned_shape], ""
    p, tag, note = pick_print(arts, planned_shape, info["aspect"], tolerance)
    note = "" if tag == planned_shape else note
    if lo <= RATIO[tag] <= hi:
        return p, tag, RATIO[tag], note
    return p, tag, info["aspect"], (note + "; " if note else "") + (
        f"the drawn frame is {info['aspect']:.2f} wide:tall, so the {tag} print was cropped to fit")


def build_hero_v2(arts, subject, out_path, settings=None, adapter=None):
    """Slot 8 'hero room A' with the v2 recipe for one print. Returns a report dict (raises on failure)."""
    tol = float(_cfg(settings, "room_shape_tolerance"))
    shape = "2x3"
    planned = next((p for p in arts if f"_{shape}_" in p.name), None) or arts[0]
    analysis = analyze_print(planned)
    brief = brief_v2(subject, analysis, shape)
    path, quad, info, calls = ensure_scene_v2(settings, brief, adapter)
    if path is None:
        raise RuntimeError(f"hero room not built: {info}")
    art, tag, fit_aspect, note = pick_print_v2(arts, shape, info, tol)
    rep = composite_v2(path, quad, art, out_path, fit_aspect, brief["frame"],
                       int(_cfg(settings, "room_jpg_quality")), settings)
    if rep["cropped"] > 0.08:
        rep["flags"].append(f"{rep['cropped']:.0%} of the art was cropped because the drawn frame has the wrong shape")
    return {"out": str(out_path), "scene": str(path), "print": tag, "note": note, "analysis": analysis,
            "brief": brief, "prompt": scene_prompt_v2(brief), "frame": info, "composite": rep,
            "quad": [[round(float(x), 1) for x in p] for p in quad], "new_scene_calls": calls}
