"""Window-light pattern continued across the art (Tony 2026-11-18).

The scene generator draws the orange print area evenly lit, so the sun patches and window mullion bars that fall on the
wall stop dead at the canvas edge, and the old Light Shadow was one angled sun line. Real art on that wall would be
crossed by the same bars. Sunlight through a window is a distant source, so on a flat wall the pattern is a grid of
parallel bands: brightness = f(a) * g(b), where a and b are the coordinates across the two sets of band edges.
The two band directions are read from the wall's own edges, f and g are fitted to the wall's brightness around the
canvas (log domain, alternating medians over 4 px bins), and the product is continued over the canvas. Output is an
alpha (0 = lit, 1 = deepest shade) for a black-fill Multiply layer: a measurement, no photo pixels are copied.
Returns None when the wall shows no usable pattern (no strong edges, bad fit): the caller keeps the old sun line.
"""
import math

import numpy as np

BIN = 4.0
POST_K = 0.8                       # the post's (first family's) shade vs the diagonal one: never darker than it (Tony 2026-11-18)
LIT_AT, SHADED_AT = 0.9, 0.62       # profile value above = sunlit, below = fully shaded
SHADE_LO, SHADE_HI = 0.15, 0.62   # fitted profile values in this band are bar shadows; their median is the common level
MIN_EDGE_STRENGTH = 0.012      # gradient magnitude (0..1 luminance per px, after blur) counted as a band edge
MAX_FIT_RMS = 0.14           # log-brightness residual on the wall above which the pattern model is rejected
DEBUG = {}                      # last fit's profiles, for diagnostics only
MIN_DEPTH = 0.04               # shallower than this the wall has no visible pattern


def _dominant_directions(Y, mask):
    import cv2
    g = cv2.GaussianBlur(Y.astype("float32"), (0, 0), 3.0)
    gx, gy = cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1)
    mag = np.hypot(gx, gy)
    sel = mask & (mag > MIN_EDGE_STRENGTH)
    if sel.sum() < 400:
        return []
    ang = np.arctan2(gy[sel], gx[sel])                       # gradient direction = across the band edge
    w = mag[sel]
    hist, edges = np.histogram(np.mod(ang, math.pi), bins=90, range=(0, math.pi), weights=w)
    hist = np.convolve(np.r_[hist[-2:], hist, hist[:2]], np.ones(5) / 5, "same")[2:-2]
    dirs = []
    for i in np.argsort(hist)[::-1]:
        phi = (edges[i] + edges[i + 1]) / 2
        if hist[i] < 0.06 * hist.max():
            break
        if all(abs(math.remainder(phi - p, math.pi)) > math.radians(25) for p in dirs):
            dirs.append(phi)
        if len(dirs) == 2:
            break
    return dirs


def _fit(coords, logY, nbins_list):
    """Alternating medians: logY ~ c + F1(a1) + F2(a2) (+ ...). Returns (c, [profiles], residual rms)."""
    k = len(coords)
    idx = [np.clip(((c - c.min()) / BIN).astype(int), 0, n - 1) for c, n in zip(coords, nbins_list)]
    prof = [np.zeros(n, "float64") for n in nbins_list]
    c0 = float(np.median(logY))
    for _ in range(25):
        for j in range(k):
            other = c0 + sum(prof[i][idx[i]] for i in range(k) if i != j)
            r = logY - other
            sums = np.bincount(idx[j], weights=r, minlength=nbins_list[j])
            cnt = np.bincount(idx[j], minlength=nbins_list[j])
            new = np.where(cnt > 0, sums / np.maximum(cnt, 1), np.nan)
            ok = ~np.isnan(new)
            if ok.sum() < 2:
                return None
            new = np.interp(np.arange(nbins_list[j]), np.nonzero(ok)[0], new[ok])
            prof[j] = new - new.mean()
            c0 = float(np.median(logY - sum(prof[i][idx[i]] for i in range(k))))
    res = logY - c0 - sum(prof[i][idx[i]] for i in range(k))
    return c0, prof, float(np.sqrt(np.mean(res ** 2)))


def _slats(Yr, m, px, py, lo_deg=105.0, hi_deg=155.0, min_amp=0.02):
    """Thin regular stripes on the rectified wall (Yr, wall mask m). Returns {"factor": multiplier (0..1] at the points
    (px, py), "deg", "period_px", "amp"} or None when the wall shows no stripes. A measurement, no photo pixels kept."""
    import cv2
    L = np.log(Yr.astype("float32") + 0.02)
    hp = cv2.GaussianBlur(L, (0, 0), 1.0) - cv2.GaussianBlur(L, (0, 0), 8.0)
    ys, xs = np.nonzero(m)
    if len(xs) < 5000:
        return None
    sub = slice(None, None, 3)
    xs_, ys_, h_ = xs[sub].astype("float64"), ys[sub].astype("float64"), hp[ys, xs][sub].astype("float64")
    best = None
    for deg in np.arange(lo_deg, hi_deg + 0.01, 0.25):
        a = math.radians(deg)
        s_ = xs_ * math.cos(a) + ys_ * math.sin(a)
        i = (s_ - s_.min()).astype(int)
        cnt = np.bincount(i)
        P = np.bincount(i, weights=h_) / np.maximum(cnt, 1)
        ok = cnt > 25
        if ok.sum() > 100:
            Pi = np.interp(np.arange(len(P)), np.nonzero(ok)[0], P[ok])
            Pb = Pi - np.convolve(Pi, np.ones(15) / 15, "same")     # fine stripes only (period ~10-30 px)
            score = float(np.var(Pb[ok][10:-10]))
        else:
            score = 0.0
        if best is None or score > best[0]:
            best = (score, deg)
    a = math.radians(best[1])
    fx = lambda x, y: x * math.cos(a) + y * math.sin(a)   # noqa: E731
    # smooth ALONG the stripes (they stay, leaf shadows and plaster texture do not), and keep only the patch where the
    # wall shows them: the median over a whole stripe line would be mostly un-striped wall and read as no stripe at all
    k = 41
    ker = np.zeros((k, k), "float32")
    c = k // 2
    cv2.line(ker, (int(round(c - c * math.cos(a + math.pi / 2))), int(round(c - c * math.sin(a + math.pi / 2)))),
             (int(round(c + c * math.cos(a + math.pi / 2))), int(round(c + c * math.sin(a + math.pi / 2)))), 1.0, 1)
    ker /= ker.sum()
    r = cv2.filter2D(hp, -1, ker)
    en = cv2.GaussianBlur(np.abs(r), (0, 0), 6.0)
    full = cv2.GaussianBlur(np.abs(hp), (0, 0), 6.0)
    coh = en / (full + 1e-4)                               # ~1 where the wall is striped along this angle, low on edges and blobs
    patch = m & (coh > 0.55) & (en > 0.006)
    inner = cv2.erode(m.astype("uint8"), np.ones((41, 41), "uint8")) > 0        # not the mask's own border or the hole's rim
    patch = patch & inner
    patch = cv2.morphologyEx(patch.astype("uint8"), cv2.MORPH_CLOSE, np.ones((15, 15), "uint8"))
    nl, lab, st, _ = cv2.connectedComponentsWithStats(patch, connectivity=8)
    if nl < 2:
        return None
    patch = lab == (1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))                # the one big sun patch (not blobs, macrame)
    DEBUG.update(patch=patch, en=en)
    ys, xs = np.nonzero(patch)
    if len(xs) < 2000:
        return None
    # the angle found on the whole wall is a few tenths of a degree off for this patch; re-pick it on the patch alone
    # (stripes stack to full depth only at the right angle, anything else smears them out over the patch's length)
    hv = hp[ys, xs].astype("float64")
    xf, yf = xs.astype("float64"), ys.astype("float64")
    best2 = None
    for deg in np.arange(best[1] - 8.0, best[1] + 8.01, 0.1):
        a2 = math.radians(deg)
        s2 = xf * math.cos(a2) + yf * math.sin(a2)
        i2 = (s2 - s2.min()).astype(int)
        c2 = np.bincount(i2)
        P2 = np.bincount(i2, weights=hv) / np.maximum(c2, 1)
        ok2 = c2 > 12
        if ok2.sum() < 60:
            continue
        Pi = np.interp(np.arange(len(P2)), np.nonzero(ok2)[0], P2[ok2])
        sc = float(np.var((Pi - np.convolve(Pi, np.ones(15) / 15, "same"))[10:-10]))
        if best2 is None or sc > best2[0]:
            best2 = (sc, deg)
    best = (best[0], best2[1] if best2 else best[1])
    a = math.radians(best[1])
    fx = lambda x, y: x * math.cos(a) + y * math.sin(a)   # noqa: E731
    s_all = fx(xf, yf)
    s_pts = fx(px.astype("float64"), py.astype("float64"))
    lo_s = min(s_all.min(), s_pts.min())
    n = int(max(s_all.max(), s_pts.max()) - lo_s) + 3
    i = (s_all - lo_s).astype(int)
    cnt = np.bincount(i, minlength=n)
    sm = np.bincount(i, weights=hv, minlength=n)
    prof = np.where(cnt > 12, sm / np.maximum(cnt, 1), np.nan)
    okp = ~np.isnan(prof)
    if okp.sum() < 50:
        return None
    prof = np.interp(np.arange(n), np.nonzero(okp)[0], prof[okp])
    prof = np.convolve(np.r_[prof[:1], prof, prof[-1:]], [0.25, 0.5, 0.25], "valid")
    # Blind slats are a regular stripe pattern, but their depth is only trustworthy where the wall shows a lot of them
    # (the patch's upper edge is full of leaf shadows and penumbra). So: find the strongest run of stripes, take the
    # period and the mean stripe shape from it, and continue that same periodic pattern over the whole patch band
    # (from the patch's upper edge, s_edge, down), which is how the real slats continue behind the art.
    win = 41
    loc = np.sqrt(np.convolve((prof - np.convolve(prof, np.ones(win) / win, "same")) ** 2, np.ones(win) / win, "same"))
    strong = loc > 0.35 * float(np.percentile(loc[okp], 95))
    DEBUG['strong'] = int(strong.sum())
    if strong.sum() < 40:
        return None
    idx = np.nonzero(strong)[0]
    runs = np.split(idx, np.nonzero(np.diff(idx) > 3)[0] + 1)
    run = max(runs, key=len)
    z0, z1 = int(run[0]), int(run[-1]) + 1
    zs = np.arange(z0, z1)
    zp = prof[z0:z1] - np.convolve(prof, np.ones(win) / win, "same")[z0:z1]
    best_t = None
    wide = np.arange(n)[okp & (np.arange(n) >= int(s_all.min() - lo_s))]          # period from the whole patch, not the short strong run
    wp = prof[wide] - np.convolve(prof, np.ones(win) / win, "same")[wide]
    for T in np.arange(12.0, 34.0, 0.05):
        ph = (wide / T) % 1.0
        b8 = np.minimum((ph * 12).astype(int), 11)
        cb = np.bincount(b8, weights=wp, minlength=12) / np.maximum(np.bincount(b8, minlength=12), 1)
        sc = float(np.var(cb[b8]))
        if best_t is None or sc > best_t[0]:
            best_t = (sc, T)
    T = best_t[1]
    core = np.nonzero(loc > 0.7 * float(np.percentile(loc[okp], 95)))[0]           # depth only from where the stripes are clearest
    zs = core
    zp = prof[core] - np.convolve(prof, np.ones(win) / win, "same")[core]
    ph = (zs / T) % 1.0
    b12 = np.minimum((ph * 12).astype(int), 11)
    cb = np.bincount(b12, weights=zp, minlength=12) / np.maximum(np.bincount(b12, minlength=12), 1)
    cb = np.convolve(np.r_[cb[-1:], cb, cb[:1]], [0.25, 0.5, 0.25], "valid")
    # the folded cycle averages away depth (small phase drift, smoothing): rescale it to the real stripe contrast, read
    # from the pixels themselves in the clearest stripe zone (10th to 90th percentile of the high-passed wall)
    in_core = np.isin(i, core)
    if in_core.sum() > 500:
        real = float(np.percentile(hv[in_core], 90) - np.percentile(hv[in_core], 10))
        if cb.max() - cb.min() > 1e-4:
            cb = cb * min(max(real / (cb.max() - cb.min()), 1.0), 4.0)
    allp = (np.arange(n) / T) % 1.0
    cs = np.interp(allp * 12 - 0.5, np.arange(-1, 13), np.r_[cb[-1:], cb, cb[:1]])
    amp = float(cb.max() - cb.min())
    s_edge = float(s_all.min() - lo_s)
    ramp = np.clip((np.arange(n) - s_edge) / T, 0, 1)                   # none above the patch's upper edge, full a stripe later
    mult = np.exp((cs - cb.max()) * ramp)
    gate = ramp
    DEBUG.update(sprof=prof, sgate=gate, smult=mult, s_pts=(s_pts - lo_s), s_all=(s_all - lo_s))
    DEBUG.update(T=T, amp=amp, zone=(z0, z1), cb=cb)
    if amp < 0.02:
        return None
    return {"factor": np.interp(s_pts - lo_s, np.arange(n), mult).astype("float32"), "deg": round(best[1], 2),
            "period_px": round(float(T), 2), "amp": round(amp, 4), "s_edge": round(s_edge, 1)}


def pattern_alpha(img, canvas_q, wall, reach=520, keep_out=90):
    """img: HxWx3 float 0..1; canvas_q: the art quad (a wall-parallel rectangle seen in perspective); wall: SAM wall
    mask (HxW float). The wall is first RECTIFIED with the canvas's own corners (a distant sun's bars are parallel on
    the wall but converge in the photo, which is why a fit in photo space was messy), the bars are fitted there and
    continued over the canvas, and the result is warped back. Returns (alpha HxW float32 0..1, info) or (None, why)."""
    import cv2
    H, W = img.shape[:2]
    if wall is None:
        return None, "no wall mask"
    q = np.float32(canvas_q)
    Y = (img @ np.float32([0.2126, 0.7152, 0.0722])).astype("float32")
    cw = float(np.mean([math.dist(q[0], q[1]), math.dist(q[3], q[2])]))
    ch = float(np.mean([math.dist(q[0], q[3]), math.dist(q[1], q[2])]))
    # rectified canvas = [0,w]x[0,h] with the print's own ratio (so true wall geometry); origin offset keeps the wall
    w_r, h_r = cw, cw * (14.0 / 11.0) if False else ch
    ox, oy, RW, RH = 0.9 * w_r, 0.9 * w_r, int(3.6 * w_r), int(h_r + 1.8 * w_r)
    dst = np.float32([[ox, oy], [ox + w_r, oy], [ox + w_r, oy + h_r], [ox, oy + h_r]])
    Hm = cv2.getPerspectiveTransform(q, dst)
    Yr = cv2.warpPerspective(Y, Hm, (RW, RH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    wr = cv2.warpPerspective((wall > 0.5).astype("float32"), Hm, (RW, RH), flags=cv2.INTER_NEAREST) > 0.5
    valid = cv2.warpPerspective(np.ones((H, W), "float32"), Hm, (RW, RH), flags=cv2.INTER_NEAREST) > 0.5
    hole = np.zeros((RH, RW), "uint8")
    hole[int(oy):int(oy + h_r), int(ox):int(ox + w_r)] = 1
    keep = cv2.dilate(hole, np.ones((2 * keep_out + 1, 2 * keep_out + 1), "uint8"))
    m = wr & valid & (keep == 0)
    if m.sum() < 5000:
        return None, "too little wall around the canvas"
    all_dirs = _dominant_directions(Yr, m)
    if len(all_dirs) < 1:
        return None, "no band edges on the wall"
    ys, xs = np.nonzero(m)
    L = Yr[ys, xs].astype("float64")
    A0 = float(np.percentile(L, 4))
    S0 = float(np.percentile(L, 96)) - A0
    if S0 < 0.05:
        return None, "the wall shows no sun pattern"
    N = np.clip((L - A0) / S0, 0, 1.2)                      # ambient + sun * f(a) * g(b): N ~ f * g
    gy, gx = np.mgrid[0:RH, 0:RW].astype("float32")
    sel = hole > 0
    cs_all = [(xs, ys)]
    xs_f, ys_f = xs.astype("float64"), ys.astype("float64")

    def fit_dirs(dirs, step=1, iters=30, binw=BIN):
        """ALS for N ~ prod f_j(a_j). Returns (rms, full coords, lo, nb, profiles)."""
        sub = slice(None, None, step)
        x_, y_, N_ = xs_f[sub], ys_f[sub], N[sub]
        ca = [x_ * math.cos(p_) + y_ * math.sin(p_) for p_ in dirs]
        full = [gx * math.cos(p_) + gy * math.sin(p_) for p_ in dirs]
        lo = [min(c.min(), f[sel].min()) for c, f in zip(ca, full)]
        hi = [max(c.max(), f[sel].max()) for c, f in zip(ca, full)]
        nb = [int((h - l) / binw) + 2 for l, h in zip(lo, hi)]
        idx_w = [np.clip(((c - l) / binw).astype(int), 0, k - 1) for c, l, k in zip(ca, lo, nb)]
        prof = [np.ones(k) for k in nb]
        for _ in range(iters):
            for j in range(len(dirs)):
                other = np.ones_like(N_)
                for i in range(len(dirs)):
                    if i != j:
                        other = other * prof[i][idx_w[i]]
                num = np.bincount(idx_w[j], weights=N_ * other, minlength=nb[j])
                den = np.bincount(idx_w[j], weights=other * other, minlength=nb[j])
                new_p = np.where(den > 1e-6, num / np.maximum(den, 1e-6), np.nan)
                ok = ~np.isnan(new_p)
                if ok.sum() < 2:
                    return None
                new_p = np.interp(np.arange(nb[j]), np.nonzero(ok)[0], new_p[ok])
                prof[j] = np.clip(np.convolve(np.r_[new_p[:1], new_p, new_p[-1:]], [0.25, 0.5, 0.25], "valid"), 0, 1)
        pred_w = np.ones_like(N_)
        for i in range(len(dirs)):
            pred_w = pred_w * prof[i][idx_w[i]]
        return float(np.sqrt(np.mean((N_ - pred_w) ** 2))), full, lo, nb, prof

    tried = []
    one = fit_dirs(all_dirs[:1])
    if one is None:
        return None, "fit failed"
    tried.append(("1 dir", round(one[0], 3)))
    best = (one[0], all_dirs[:1], one[1], one[2], one[3], one[4], A0, S0)
    d1 = all_dirs[0]
    cand = [math.radians(t) for t in range(0, 180, 3) if abs(math.remainder(math.radians(t) - d1, math.pi)) > math.radians(20)]
    scored = []
    for t in cand:                                           # crossbar angle search on a subsample
        r = fit_dirs([d1, t], step=6, iters=8)
        if r is not None:
            scored.append((r[0], t))
    if scored:
        scored.sort()
        t2 = scored[0][1]
        two = fit_dirs([d1, t2])
        if two is not None:
            tried.append((f"2 dirs, crossbar {math.degrees(t2):.0f} deg", round(two[0], 3)))
            if two[0] < best[0] * 0.85:
                best = (two[0], [d1, t2], two[1], two[2], two[3], two[4], A0, S0)
    rms, dirs, full, lo, nb, prof, A0, S0 = best
    DEBUG.update(prof=[np.array(x) for x in prof], dirs=dirs, A0=A0, S0=S0)
    if rms > MAX_FIT_RMS:
        return None, f"the wall's light is not a clean band pattern (fit rms {rms:.3f}, tried {tried})"
    # Tony 2026-11-18: every bar shadow of one window is cast by the same light, so all of them are the SAME darkness
    # (the post between the panes must not be darker than the mullions). The product fit can leave one bar deeper than
    # the rest (and cross points deeper still), so: take the common shade level from the fitted plateaus, floor every
    # bar at it, and combine the two bar sets with min (a point is shaded or not, shadows do not stack).
    vals = np.concatenate([pr[(pr > SHADE_LO) & (pr < SHADE_HI)] for pr in prof])
    shade = float(np.median(vals)) if vals.size >= 8 else SHADE_LO
    # Every shaded area (the post, the mullions, the big diagonal shadow at the top that cuts the windows off) is
    # the same shade: a profile value is mapped to "how shaded" 0..1 (lit above LIT_AT, fully shaded below SHADED_AT,
    # smooth between, so penumbra edges stay soft) and every shaded point gets the one common level.
    bw = BIN
    u = np.zeros(int(sel.sum()))
    vprod = np.ones(int(sel.sum()))
    for j, (f, l, k, pr) in enumerate(zip(full, lo, nb, prof)):
        v = pr[np.clip(((f[sel] - l) / bw).astype(int), 0, k - 1)]
        vprod = vprod * v
        t = np.clip((LIT_AT - v) / (LIT_AT - SHADED_AT), 0, 1)
        u = np.maximum(u, (POST_K if j == 0 else 1.0) * t * t * (3 - 2 * t))
    pf = 1 - (1 - shade) * u
    lit = A0 + S0                                           # the lit level; shade = ambient only
    # Fine blind slats (Tony 2026-11-18, bedroom): thin regular stripes a few % deep, parallel to the patch edges, that the
    # smooth band model above cannot hold (its crossbar angle is a few degrees off, so over the canvas length they wash
    # out). Measure them directly: high-pass the wall in log brightness, find the angle that stacks the stripes best,
    # take the stripe profile along that axis from the wall around the canvas, and continue it through the canvas.
    total = A0 + S0 * pf
    slat_info = None
    sl = _slats(Yr, m, gx[sel], gy[sel])
    if sl is not None:
        total = total * sl["factor"]
        slat_info = {k: v for k, v in sl.items() if k != "factor"}
    dark = np.clip(1 - total / lit, 0, 1)
    depth = float(A0 and (1 - A0 / lit))
    if depth < MIN_DEPTH:
        return None, f"the wall pattern is too shallow ({depth:.3f})"
    ar = np.zeros((RH, RW), "float32")
    ar[sel] = (dark / max(depth, 1e-6)).clip(0, 1)
    alpha = cv2.warpPerspective(ar, np.linalg.inv(Hm), (W, H), flags=cv2.INTER_LINEAR)
    cov = np.zeros((H, W), "uint8")
    cv2.fillConvexPoly(cov, np.round(q).astype(np.int32), 1)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.0) * (cov > 0)
    return alpha.astype("float32"), {"kind": "window pattern", "rectified": True,
                   "dirs_deg": [round(math.degrees(p_), 1) for p_ in dirs], "tried_rms": tried,
                   "fit_rms": round(rms, 4), "opacity": round(float(np.clip(depth, 0.06, 0.6)), 3),
                   "measured_depth": round(depth, 3), "slats": slat_info, "common_shade": round(shade, 3), "searched_on": "SAM wall mask, rectified with the canvas corners"}
