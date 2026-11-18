"""SAM precision geometry (app/sam_frames.py) without torch: anti-aliased coverage, material-edge alpha refinement
from a deliberately wrong (SAM-like, few px off, rounded corners) mask, sub-pixel four-corner fit and the loud
failure when the corners disagree with the mask."""
import math

import cv2
import numpy as np
import pytest

from app import sam_frames as sf

Q = np.float32([[300.3, 150.7], [612.6, 168.2], [606.1, 640.4], [304.8, 632.9]])     # sub-pixel, slight perspective


def render(q=Q, size=(900, 800), ss=8):
    """Wood frame around a white insert, a dark frame-lip shadow on the paper's top/left edge, rendered 8x
    supersampled (true anti-aliased edges at sub-pixel positions)."""
    W, H = size
    big = np.zeros((H * ss, W * ss, 3), "float32")
    big[:] = (196, 182, 160)                                                  # wall
    qq = np.float32(q) * ss
    c = qq.mean(0)
    cv2.fillPoly(big, [np.int32(np.round(c + (qq - c) * 1.12))], (182, 140, 96))   # wood frame
    cv2.fillPoly(big, [np.int32(np.round(qq))], (236, 234, 228))                   # paper
    img = cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA)
    cov = sf.poly_coverage(q, W, H)
    d = sf_side_dist(q, W, H)
    lip = 1 - 0.35 * np.exp(-np.clip(d[0], 0, None) / 2.0) * np.exp(0) - 0.0
    lip = np.minimum(lip, 1 - 0.35 * np.exp(-np.clip(d[3], 0, None) / 2.0))
    img = img * (1 - cov[..., None]) + img * cov[..., None] * lip[..., None]      # shadow darkens the paper only
    return np.clip(img, 0, 255).astype("uint8")


def sf_side_dist(q, W, H):
    from app.scene_templates import side_distance
    return side_distance(q, W, H)


def sam_like_mask(q, W, H, shrink=2.5):
    """What SAM gives: a few px inside the true edge (it stops at the lip shadow), rounded corners."""
    from app.template_checker import offset_quad
    m = (sf.poly_coverage(offset_quad(np.float32(q), -shrink), W, H) > 0.5).astype("uint8")
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    return m.astype(bool)


def test_poly_coverage_is_antialiased_and_exact_in_area():
    cov = sf.poly_coverage(Q, 900, 800)
    assert 0 < cov[156, 400] < 1                                  # the top edge (y 156.3 at x 400) is partly covered
    assert cov.sum() == pytest.approx(cv2.contourArea(Q.reshape(-1, 1, 2)), rel=1e-3)


def test_alpha_and_corners_reach_the_frame_not_the_shadow_and_are_subpixel():
    rgb = render()
    H, W = rgb.shape[:2]
    m = sam_like_mask(Q, W, H)
    alpha = sf.refine_alpha(rgb, m)
    assert ((alpha > 0.02) & (alpha < 0.98)).sum() > 500          # smooth anti-aliased edge, not a binary step
    q0 = sf.quad_from_mask(m)
    q, stats = sf.fit_quad(alpha, q0)
    err = sf.corner_error(q, Q)
    assert err["max_px"] <= 0.5, err                               # SAM-like mask was 2.5 px inside, rounded
    assert sf.verify_quad(q, alpha, q0, stats)["iou"] > 0.99


def test_corners_that_disagree_with_the_mask_fail_loudly():
    rgb = render()
    H, W = rgb.shape[:2]
    m = sam_like_mask(Q, W, H)
    alpha = sf.refine_alpha(rgb, m)
    q0 = sf.quad_from_mask(m)
    q, stats = sf.fit_quad(alpha, q0)
    wrong = q + np.float32([[0, 0], [0, 0], [14, 9], [0, 0]])
    with pytest.raises(sf.QuadError):
        sf.verify_quad(wrong, alpha, q0, stats)


def test_edge_truth_is_independent_and_agrees():
    rgb = render()
    t = sf.edge_truth(rgb, Q + 2.0)
    assert sf.corner_error(t, Q)["max_px"] <= 0.5
    assert math.isfinite(float(t.sum()))


# ---------- the opening = the frame's hard inner edge (Tony 2026-11-12) ----------

def render_wall_frame(q=Q, size=(900, 800), ss=8, frame=(182, 140, 96), wall_col=(100, 72, 48), wall_px=4.0,
                      strip=0.5, width=4.0, blur=1.8, warm=True):
    """Like LVRM_Midcentury_Sideboard_2x3 (measured 2026-11-12): a 3/4 view shows the frame's dark INNER WALL (a
    `wall_px` band just outside the opening's left side), and the frame casts a shadow on the paper's left edge: a
    near-flat strip (`strip` darkening, warm bounce from the wood) `width` px wide that blurs out by `blur`. The other
    three sides are crisp paper -> frame. Rendered 8x supersampled (true anti-aliased edges)."""
    from app.scene_templates import band, side_distance
    W, H = size
    qq = np.float32(q) * ss
    c = qq.mean(0)
    big = np.zeros((H * ss, W * ss, 3), "float32")
    big[:] = (196, 182, 160)
    cv2.fillPoly(big, [np.int32(np.round(c + (qq - c) * 1.12))], frame)
    wq = sf.offset_quad(np.float32(q), [0, 0, 0, wall_px]) * ss            # the inner wall: left band only
    cv2.fillPoly(big, [np.int32(np.round(wq))], wall_col)
    cv2.fillPoly(big, [np.int32(np.round(qq))], (236, 234, 228))
    img = cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA)
    cov = sf.poly_coverage(q, W, H)
    d = side_distance(q, W, H)[3]
    D = (strip * band(np.clip(d, 0, None), width, blur)).astype("float32")
    tint = np.float32([1.0, 0.93, 0.85]) if warm else np.float32([1, 1, 1])
    shade = (1 - D[..., None]) * (1 - (1 - tint) * np.clip(D[..., None] / max(strip, 1e-6), 0, 1))  # darker, warmer
    img = img * (1 - cov[..., None]) + img * cov[..., None] * shade
    return np.clip(img, 0, 255).astype("uint8")


def test_opening_reaches_the_hard_inner_wall_not_the_shadowed_paper():
    """SAM's paper edge stops ~5 px short on the shadowed side (the grey strip Tony saw); the opening must sit on the
    frame's hard inner edge on every side, sub-pixel."""
    rgb = render_wall_frame()
    q_paper = sf.offset_quad(Q, [0.2, -0.1, 0.15, -4.8])          # where SAM's refined paper edge landed
    qo, info = sf.opening_quad(rgb, q_paper)
    err = sf.corner_error(qo, Q)
    assert err["max_px"] <= 0.35, (err, info)
    assert info["offset_px"]["left"] == pytest.approx(4.8, abs=0.35)
    assert all(abs(info["offset_px"][s]) <= 0.4 for s in ("top", "right", "bottom"))
    assert all(st["mode"] == "chroma" and st["rms_px"] < 0.3 for st in info["sides"].values())


def test_opening_on_a_neutral_black_frame_uses_brightness():
    rgb = render_wall_frame(frame=(28, 28, 28), wall_col=(14, 14, 14), warm=False, strip=0.45)
    qo, info = sf.opening_quad(rgb, sf.offset_quad(Q, [0, 0, 0, -4.5]))
    assert sf.corner_error(qo, Q)["max_px"] <= 0.4, info
    assert info["sides"]["left"]["mode"] == "lum dark"


def test_opening_fails_loudly_without_a_hard_frame_edge():
    plain = np.full((800, 900, 3), 230, "uint8")                   # no frame at all: nothing to find
    with pytest.raises(sf.QuadError, match="neither a colour nor a brightness"):
        sf.opening_quad(plain, Q)
    # a frame edge that only fades in softly (no hard step within reach) is not guessed either
    W, H = 900, 800
    from app.scene_templates import side_distance
    d = np.min(np.stack(side_distance(Q, W, H)), 0)
    soft = np.clip(1 + d / 30.0, 0, 1)[..., None]                   # 30 px ramp from paper to wood, no step
    img = soft * np.float32([236, 234, 228]) + (1 - soft) * np.float32([182, 140, 96])
    with pytest.raises(sf.QuadError, match="no hard frame edge"):
        sf.opening_quad(img.astype("uint8"), Q)


def test_a_wood_band_inside_the_paper_quad_is_frame_and_the_opening_stops_at_its_inner_edge():
    """If SAM's paper quad reaches over a strip of frame material (wood colour), that strip is frame, not shadowed
    paper: the opening is its INNER edge (never outward across it)."""
    rgb = render_wall_frame(strip=0.0)
    from app.scene_templates import side_distance
    W, H = 900, 800
    inner = sf.offset_quad(Q, [0, 0, 0, -4.0])                      # 4 px of wood colour inside the left edge
    cov = sf.poly_coverage(Q, W, H) - sf.poly_coverage(inner, W, H)
    img = rgb * (1 - cov[..., None]) + cov[..., None] * np.float32([182, 140, 96])
    qo, info = sf.opening_quad(img.astype("uint8"), sf.offset_quad(Q, [0, 0, 0, -4.5]))
    assert sf.corner_error(qo, inner)["max_px"] <= 0.35, info


def test_offset_quad_and_side_offsets_round_trip():
    q2 = sf.offset_quad(Q, [1.5, 0.0, -2.0, 3.25])
    assert sf.side_offsets(Q, q2) == pytest.approx([1.5, 0.0, -2.0, 3.25], abs=0.01)


def canvas_scene(side_band=14, W=900, H=800):
    """A stretched canvas in a pale wood floater frame, 3/4 view from the right: the orange face x 280..600,
    y 170..650, and on the right (camera-facing) side a `side_band` px side edge that darkens from orange to dark
    brown (same hue, so SAM took face + side edge as one shape); a dark gap, then the wood lip. Returns (rgb float32,
    face quad, face + side edge quad)."""
    a = np.zeros((H, W, 3), "float32")
    a[:] = (200, 195, 185)                                              # wall
    a[140:680, 250:600 + side_band + 56] = (196, 170, 140)             # wood floater frame
    a[152:668, 262:600 + side_band + 44] = (110, 90, 70)               # the gap (soft shadow)
    a[170:650, 280:600] = (229, 182, 127)                              # the orange face
    c0, c1 = np.float32([205, 140, 80]), np.float32([91, 39, 17])    # (a gentler onset than c0 reads as face for
    for k in range(side_band):                                           # ~1-2 px in both detectors) the side edge ramp
        a[170:650, 600 + k] = c0 + (c1 - c0) * k / max(side_band - 1, 1)
    face = np.float32([[280, 170], [600, 170], [600, 650], [280, 650]])
    both = np.float32([[280, 170], [600 + side_band, 170], [600 + side_band, 650], [280, 650]])
    return a, face, both


def test_canvas_face_search_moves_the_opening_off_a_same_colour_side_edge():
    """Tony 2026-11-17: SAM's canvas shape included the right side edge; the inward search finds where the flat face
    ends and moves that side there + 0.5 px inward. Sides already on the face edge keep SAM's line."""
    img, face, both = canvas_scene()
    q, info = sf.canvas_face_quad(np.uint8(img), both)
    offs = sf.side_offsets(both, q)                                      # + = outside SAM's side
    assert -15.0 <= offs[1] <= -13.75, (offs, info)                      # right: 600 - 0.5 = 599.5 (SAM had 614)
    assert info["sides"]["right"]["moved_px"] == pytest.approx(offs[1], abs=0.05)
    assert all(abs(o) < 0.01 for i, o in enumerate(offs) if i != 1), offs     # top, bottom, left: SAM's line kept
    q2, info2 = sf.canvas_face_quad(np.uint8(img), face)                 # SAM already right: nothing moves
    assert max(abs(o) for o in sf.side_offsets(face, q2)) < 0.01, info2


def test_canvas_face_search_ignores_soft_shading_on_the_face():
    img, face, both = canvas_scene(side_band=0)
    h = np.arange(170, 650, dtype="float32")
    img[170:650, 280:600] *= (1 - 0.12 * (h - 170) / 480)[:, None, None]   # a gentle light falloff on the face
    q, info = sf.canvas_face_quad(np.uint8(img), face)
    assert max(abs(o) for o in sf.side_offsets(face, q)) < 0.01, info
