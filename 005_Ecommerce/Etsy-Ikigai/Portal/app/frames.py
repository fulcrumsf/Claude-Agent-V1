"""Frame chooser for room mockups (Mockup_Docs/Mockup_Style_Guide.md 2.7, 3c, section 6 item 3 and Tony's addition 8).

Frames are chosen by rules, never at random: the print's style tags (from the idea title and summary, the
style cards it was painted with and those cards' Style_Profiles), its value key and accent colours
(rooms.analyze_print) score every frame in config/frame_styles.json. Ornate gold / carved frames are vetoed for
modern, graphic, minimal or kids art and need a vintage / oil / classical / gothic / dark-moody tag to be
considered at all. A listing gets a SET of 2-3 frames from different families, some with a white mat.
Deterministic: the same inputs always give the same frames, each with plain-English reasons.
"""
import re

from .db import load_config

TAG_MIN = 0.5          # a tag counts once its strength reaches this
REQUIRE_MIN = 0.8      # an ornate frame's 'requires_any' tag must be at least this strong (not a stray mention)


def rules():
    return load_config("frame_styles")


def _norm(text):
    return " " + re.sub(r"[^a-z0-9\- ]+", " ", str(text or "").lower().replace("_", " ")) + " "


def detect_tags(sources, cfg=None):
    """sources: {"idea": text, "card": text, "profile": text} (any subset). Returns (strengths, evidence):
    strength = sum of the source weights that mention a keyword of the tag (capped at 2); evidence names
    which keyword was found where, so every tag can be explained."""
    cfg = cfg or rules()
    weights = cfg.get("source_weights", {})
    strength, evidence = {}, {}
    for src, text in sources.items():
        t = _norm(text)
        w = float(weights.get(src, 0.5))
        for tag, words in cfg["tags"].items():
            hit = next((k for k in words if re.search(r"(?<![a-z])" + re.escape(k.lower()) + r"(?![a-z])", t)), None)
            if hit:
                strength[tag] = min(2.0, strength.get(tag, 0.0) + w)
                evidence.setdefault(tag, []).append(f"'{hit}' in the {src}")
    return {k: round(v, 2) for k, v in strength.items()}, evidence


def _accent_family(analysis, cfg):
    names = " ".join(a.get("name", "") for a in (analysis or {}).get("accents") or []).lower()
    af = cfg.get("accent_fit", {})
    warm = any(w in names for w in af.get("warm_words", []))
    cool = any(w in names for w in af.get("cool_words", []))
    return "warm" if warm and not cool else "cool" if cool and not warm else ("mixed" if warm else None)


def score_frames(tags, analysis=None, cfg=None):
    """Every frame with its score, reasons and veto (if any), best first."""
    cfg = cfg or rules()
    on = {t: s for t, s in tags.items() if s >= TAG_MIN}
    value_key = (analysis or {}).get("value_key")
    accent = _accent_family(analysis, cfg)
    out = []
    for f in cfg["frames"]:
        reasons, score = [], float(f.get("base", 0))
        why = []
        bad = [t for t in f.get("veto", []) if t in on]
        if bad:
            why.append(f"it never goes on {', '.join(t.replace('_', ' ') for t in bad)} art")
        req = f.get("requires_any") or []
        if req and not any(tags.get(t, 0) >= REQUIRE_MIN for t in req):
            why.append(f"it needs {'/'.join(t.replace('_', ' ') for t in req)} art and this print is none of those")
        vetoed = f"vetoed: {f['name']}: " + "; ".join(why) if why else None
        for t, s in sorted(on.items()):
            w = f.get("fits", {}).get(t, 0) + f.get("poor", {}).get(t, 0)
            if w:
                score += w * min(s, 1.0)
                reasons.append(f"{'suits' if w > 0 else 'clashes with'} {t.replace('_', ' ')} ({w * min(s, 1.0):+.1f})")
        if value_key:
            v = cfg.get("value_fit", {}).get(value_key, {}).get(f["id"], 0)
            if v:
                score += v
                reasons.append(f"{value_key} art ({v:+.1f})")
        if accent in ("warm", "cool"):
            if (accent == "warm") == bool(f.get("warm")):
                b = cfg["accent_fit"][accent]
                score += b
                reasons.append(f"{'warm' if accent == 'warm' else 'cool'} accent colours echo a "
                               f"{'warm' if f.get('warm') else 'cool'} frame ({b:+.1f})")
        out.append({"id": f["id"], "name": f["name"], "family": f["family"], "tone": f.get("tone"),
                    "prompt": f.get("prompt"), "score": round(score, 2), "reasons": reasons, "vetoed": vetoed,
                    "mat_affinity": f.get("mat", 0.5)})
    out.sort(key=lambda x: (x["vetoed"] is not None, -x["score"], x["id"]))
    return out


def _mat_score(frame, tags, analysis, cfg):
    m = cfg["mat"]
    on = {t for t, s in tags.items() if s >= TAG_MIN}
    s = frame["mat_affinity"]
    s += min(1.0, 0.25 * len(on & set(m["tags_for"])))
    s -= 0.5 * len(on & set(m["tags_against"]))
    vk = (analysis or {}).get("value_key")
    if vk == "light":
        s += m.get("light_art_bonus", 0)
    if vk and frame.get("tone") == vk:
        s += m.get("same_tone_bonus", 0)          # a mat separates a frame that is as light/dark as the art
    return round(s, 2)


def choose_set(tags, analysis=None, size=None, cfg=None):
    """2-3 distinct frames that all fit (different families, score >= min_score), with a mat on 1-2 of them.
    Returns {"frames": [...], "rejected": [...]}; each frame has mat (bool) and reasons."""
    cfg = cfg or rules()
    size = size or cfg.get("set_size", 3)
    ranked = score_frames(tags, analysis, cfg)
    picked, families, rejected = [], set(), []
    for f in ranked:
        if f["vetoed"]:
            rejected.append({"id": f["id"], "why": f["vetoed"]})
        elif f["score"] < cfg.get("min_score", 1.0):
            rejected.append({"id": f["id"], "why": f"score {f['score']} is below {cfg.get('min_score', 1.0)}"})
        elif f["family"] in families:
            rejected.append({"id": f["id"], "why": f"same family ({f['family']}) as a better-scoring frame"})
        elif len(picked) < size:
            picked.append(dict(f))
            families.add(f["family"])
        else:
            rejected.append({"id": f["id"], "why": "set already full"})
    if not picked:                                 # nothing passed: fall back to the best non-vetoed frame
        best = next((f for f in ranked if not f["vetoed"]), ranked[0])
        picked = [dict(best, reasons=best["reasons"] + ["fallback: no frame reached the minimum score"])]
    for f in picked:
        f["mat_score"] = _mat_score(f, tags, analysis, cfg)
    lo, hi = cfg["mat"].get("per_set", [1, 2])
    order = sorted(range(len(picked)), key=lambda i: (-picked[i]["mat_score"], i))
    want = sum(1 for f in picked if f["mat_score"] >= 2.0)
    n_mat = max(min(lo, len(picked)), min(want, hi, len(picked) - (1 if len(picked) > 1 else 0)))
    for rank, i in enumerate(order):
        picked[i]["mat"] = rank < n_mat
        picked[i]["reasons"] = picked[i]["reasons"] + [
            f"white mat {'on' if picked[i]['mat'] else 'off'} (mat score {picked[i]['mat_score']})"]
    return {"frames": picked, "rejected": rejected}


def gather_sources(title, description="", cards=None, settings=None):
    """Text per source for detect_tags: the idea, its style cards (name + fragment) and those cards'
    Style_Profiles (tags, era, medium, title). Missing cards or profiles are skipped, never invented."""
    src = {"idea": f"{title or ''}. {description or ''}"}
    if cards:
        from . import art
        cmap = art.card_map()
        found = [cmap[c] for c in cards if c in cmap]
        if found:
            src["card"] = " ".join(f"{c.get('name', '')}. {c.get('paint', '')} {c.get('fragment', '')}" for c in found)
            folder = art.profiles_dir(settings)
            profs = [p for c in found for p in (art.read_profile(folder, pid) for pid in c.get("sources", [])) if p]
            if profs:
                src["profile"] = " ".join(
                    f"{p.get('title', '')}. {p.get('era_feel', '')}. {p.get('medium', '')}. "
                    f"{' '.join(p.get('tags') or [])}" for p in profs)
    return src


def frames_for_print(title, description="", analysis=None, cards=None, settings=None, size=None):
    """One call for the pipeline: tags (with evidence) + the frame set with reasons."""
    cfg = rules()
    tags, evidence = detect_tags(gather_sources(title, description, cards, settings), cfg)
    out = choose_set(tags, analysis, size, cfg)
    return {"tags": tags, "evidence": evidence, **out}
