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
def find_frame(rgb):
    """Corners of the magenta picture area as a float32 (4,2) array ordered tl,tr,br,bl, plus checks.
    Returns (quad, info) or (None, reason)."""
    import cv2
    import numpy as np
    a = rgb.astype("int16")
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mask = ((r - g > 60) & (b - g > 60) & (abs(r - b) < 110)).astype("uint8") * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), "uint8"))
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cs:
        return None, "no magenta picture area found"
    c = max(cs, key=cv2.contourArea)
    area = cv2.contourArea(c)
    H, W = mask.shape
    if area < 0.02 * W * H:
        return None, "the frame is too small in the picture"
    hull = cv2.convexHull(c)
    quad = None
    for eps in (0.01, 0.015, 0.02, 0.03, 0.04, 0.06):
        ap = cv2.approxPolyDP(hull, eps * cv2.arcLength(hull, True), True)
        if len(ap) == 4:
            quad = ap.reshape(4, 2).astype("float32")
            break
    if quad is None:
        quad = cv2.boxPoints(cv2.minAreaRect(hull)).astype("float32")
    quad = order_quad(quad)
    qarea = cv2.contourArea(quad)
    fill = area / qarea if qarea else 0
    if fill < 0.88:
        return None, f"the frame is partly hidden (only {fill:.0%} of it is clear)"
    if quad[:, 0].min() < 2 or quad[:, 1].min() < 2 or quad[:, 0].max() > W - 3 or quad[:, 1].max() > H - 3:
        return None, "the frame touches the edge of the picture"
    top = math.dist(quad[0], quad[1])
    bottom = math.dist(quad[3], quad[2])
    left = math.dist(quad[0], quad[3])
    right = math.dist(quad[1], quad[2])
    return quad, {"aspect": ((top + bottom) / 2) / ((left + right) / 2), "px": [round((top + bottom) / 2),
                  round((left + right) / 2)], "fill": round(fill, 3)}


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
