"""Wall colour for a room mockup, chosen like an art director: complementary but subtle, tailored to the art's
colours and the room's furniture, from realistic interior paints only (config/wall_palettes.json).
Never random. Returns ranked paints with plain reasons (same style as app/frames.py)."""
import colorsys

from .db import load_config


def rules():
    return load_config("wall_palettes")


def _hue_family(rgb):
    r, g, b = (x / 255 for x in rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    deg = h * 360
    if s < 0.18:
        return "neutral"
    if deg < 55 or deg >= 330:
        return "warm"
    if 70 <= deg < 170:
        return "green"
    if 170 <= deg < 270:
        return "cool"
    return "other"


def choose(analysis, furniture="warm_wood", n=3, cfg=None):
    """analysis = rooms.analyze_print(...) result. Returns [{name, rgb, score, reasons}] best first."""
    cfg = cfg or rules()
    tone = cfg["furniture_tones"].get(furniture, cfg["furniture_tones"]["warm_wood"])
    fams = [_hue_family(a["rgb"]) for a in (analysis.get("accents") or [])]
    warm_art = "warm" in fams or not fams
    cool_art = "cool" in fams
    green_art = "green" in fams
    key = analysis.get("value_key", "mid")
    out = []
    for p in cfg["paints"]:
        s, why, fam = 5.0, [], p["family"]
        if fam in tone["likes"]:
            s += 1.5; why.append(f"sits well with {furniture.replace('_', ' ')} furniture")
        if fam in tone["dislikes"]:
            s -= 2.0; why.append(f"clashes a little with {furniture.replace('_', ' ')} furniture")
        if warm_art and fam in ("warm_neutral", "earth", "neutral"):
            s += 1.5; why.append("echoes the art's warm accents quietly")
        if warm_art and fam in ("blue", "cool_neutral"):
            s -= 1.5; why.append("cool wall against warm art")
        if cool_art and fam in ("blue", "cool_neutral", "neutral"):
            s += 1.5; why.append("supports the art's cool accents")
        if green_art and fam in ("green", "neutral", "warm_neutral"):
            s += 1.0; why.append("goes with the art's greens")
        if green_art is False and fam == "green":
            s -= 0.8; why.append("green wall has no link to this art")
        if key == "light":      # light art needs a little more depth behind it to read, never a dark wall
            s += 0.6 if 0.2 <= p["depth"] <= 0.6 else 0
            s -= 1.5 if p["depth"] >= 0.9 else 0
            if 0.2 <= p["depth"] <= 0.6:
                why.append("slightly deeper than the print so it reads")
        if key == "dark":
            s += 1.0 if p["depth"] <= 0.2 else (-0.5 if p["depth"] >= 0.9 else 0)
        if fam in ("dark_neutral",) and key != "dark":
            s -= 0.5
        if key == "light":      # tie-break (2026-11-07): among equals, a quiet mid-depth neutral (~0.4) reads best
            s -= round(0.5 * abs(p["depth"] - 0.4), 2)  # behind light art; oat/warm white are too close to the paper
        out.append({"name": p["name"], "rgb": p["rgb"], "score": round(s, 2), "reasons": why})
    out.sort(key=lambda x: -x["score"])
    return out[:n]
