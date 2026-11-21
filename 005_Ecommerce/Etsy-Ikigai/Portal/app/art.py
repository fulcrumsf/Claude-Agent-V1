"""Stage 2 of the funnel: idea to art (the Build art flow in the Details panel).

  1. Tony opens a banked idea, clicks Build art, picks up to 2 style cards (config/style_cards.json) and
     optional chips (palette, accent, mood, composition, texture, subject treatment) and an engine.
     No card picked = "Surprise me": the prompt writer picks 2 cards that fit the idea.
  2. The prompt writer (headless `claude -p`, no tools, same pattern as app/assistant.py) turns the idea,
     the card fragments, the live Style_Profiles details and the chips into one painterly prompt per image.
  3. A worker thread makes 4 images (2 cards x 2, or 4 of one card) on the chosen engine (app/engines.py),
     after a credit check. Files land in <db folder>/art/<idea_id>/ (data/art/ for the real DB).
  4. Tony clicks an image to pick it, gives feedback in the chat (action `art_iterate`) and gets 4 new
     variations of the picked one, then approves the art (button or chat `art_approve`).

Every step is written to `art_log` (Etsy's individual human-oversight rule: prompt, engine, cards/chips,
source images, every pick, every feedback text verbatim). Picks, passes, feedback and approvals also go to
taste_events, and taste.py summarises card and chip picks for the writer and the research job.
"""
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from . import assistant, engines, taste
from .db import DB_LOCK as LOCK
from .db import ROOT, load_config

RUNNING = ("writing", "generating")
DEFAULTS = {"art_images_per_round": 4, "art_writer_model": "sonnet", "art_writer_fallback_model": "haiku",
            "art_writer_timeout_s": 180, "style_profiles_dir": "../Creative_Inspiration/Style_Profiles"}
CONSTRAINTS = ("No text, letters, numbers, signature or watermark anywhere. The artwork alone, filling the "
               "whole frame edge to edge: not a mockup, no frame, no wall, no room, no border.")


class ArtError(Exception):
    """Plain reason an art action was refused (shown to Tony)."""


def cfg(settings, key):
    return (settings or {}).get(key, DEFAULTS.get(key))


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ---------- style cards, chips, live profiles ----------

def library():
    return load_config("style_cards")


def card_map():
    return {c["id"]: c for c in library()["cards"]}


def chip_map():
    return {g["id"]: {c["id"]: c for c in g["chips"]} for g in library()["chip_groups"]}


def profiles_dir(settings):
    p = Path(cfg(settings, "style_profiles_dir"))
    return p if p.is_absolute() else (ROOT / p).resolve()


def read_profile(folder, pid):
    """Frontmatter of Style_Profiles/<pid>_*.md. Each line is `key: <json>` (written by inspiration_scan.py)."""
    hits = sorted(Path(folder).glob(f"{pid}_*.md")) if Path(folder).is_dir() else []
    if not hits:
        return None
    parts = hits[0].read_text().split("---")
    if len(parts) < 3:
        return None
    out = {}
    for line in parts[1].strip().splitlines():
        k, _, v = line.partition(": ")
        try:
            out[k.strip()] = json.loads(v)
        except ValueError:
            out[k.strip()] = v.strip()
    return out


def _undigital(text):
    return re.sub(r"\s{2,}", " ", re.sub(r"\bdigital(ly)?\b\s*", "", str(text or ""), flags=re.I)).strip()


def card_detail(card, settings):
    """Card + what its source profiles say about brushwork, paint, palette and what to preserve."""
    lib = library()
    profs = [p for p in (read_profile(profiles_dir(settings), pid) for pid in card["sources"]) if p]
    drop = {d.lower() for d in card.get("avoid_drop", [])}
    avoid, hexes, brush, paint, keep, colors, images = [], [], [], [], [], [], []
    for p in profs:
        sj = p.get("style_json") or {}
        images.append(p.get("new_filename") or p.get("image_path"))
        for a in p.get("avoid") or []:
            a2 = _undigital(a)
            if a.lower() not in drop and a2 not in avoid:
                avoid.append(a2)
        hexes += [h for h in p.get("palette_hex") or [] if h not in hexes]
        if sj.get("brushwork"):
            brush.append("; ".join(f"{k.replace('_', ' ')}: {_undigital(v)}" for k, v in sj["brushwork"].items()))
        if sj.get("paint_behaviour"):
            paint.append("; ".join(f"{k}: {_undigital(v)}" for k, v in sj["paint_behaviour"].items()))
        keep += [_undigital(x) for x in sj.get("what_to_preserve") or []]
        colors += [c.get("name") for c in (sj.get("palette") or {}).get("dominant_colors") or [] if c.get("name")]
    for a in lib.get("global_avoid", []):
        if a not in avoid:
            avoid.append(a)
    return {"id": card["id"], "name": card["name"], "fragment": card["fragment"], "brushwork": brush,
            "paint_behaviour": paint, "preserve": keep, "own_palette": colors, "palette_hex": hexes[:6],
            "avoid": avoid, "source_images": [i for i in images if i]}


def options(settings):
    """Everything the Build art setup needs."""
    lib = library()
    cards = []
    for c in lib["cards"]:
        d = card_detail(c, settings)
        cards.append({k: c[k] for k in ("id", "name", "paint", "motif", "default_palette", "default_texture",
                                         "textures_ok")} | {"swatch": d["palette_hex"], "sources": d["source_images"]})
    eng = engines.list_engines()
    default = next((e["id"] for e in eng if e["default"]), eng[0]["id"] if eng else None)
    return {"cards": cards, "chip_groups": lib["chip_groups"], "engines": eng, "default_engine": default,
            "images_per_round": cfg(settings, "art_images_per_round"),
            "aspect_ratio": engines.config().get("aspect_ratio", "2:3"),
            "resolution": engines.config().get("resolution", "1K")}


def clean_chips(chips):
    """{group: chip id} from Tony. Accent is a toggle (truthy -> red_pop). Unknown group/chip -> ArtError."""
    groups = chip_map()
    out = {}
    for g, v in (chips or {}).items():
        if v in (None, "", False, "default"):
            continue
        if g not in groups:
            raise ArtError(f"unknown chip group {g}")
        if g == "accent" and v is True:
            v = next(iter(groups[g]))
        if v not in groups[g]:
            raise ArtError(f"unknown {g} chip {v}")
        out[g] = v
    return out


def resolve_chips(card, tony, composition=None):
    """Final chip set for one image of `card`, each with who set it: tony | default | agent."""
    out = {"palette": {"id": tony["palette"], "by": "tony"} if "palette" in tony
           else {"id": card["default_palette"], "by": "default"}}
    if "accent" in tony:
        out["accent"] = {"id": tony["accent"], "by": "tony"}
    for g in ("mood", "treatment"):
        out[g] = {"id": tony[g], "by": "tony"} if g in tony else {"id": None, "by": "agent"}
    if "composition" in tony:
        out["composition"] = {"id": tony["composition"], "by": "tony"}
    else:
        out["composition"] = {"id": composition, "by": "agent"}
    t = tony.get("texture")
    if t and t in card["textures_ok"]:
        out["texture"] = {"id": t, "by": "tony"}
    else:
        out["texture"] = {"id": card["default_texture"], "by": "default"}
        if t:
            out["texture"]["note"] = f"{t} does not suit this card"
    return out


def plan_setup(card_ids, tony, n=4):
    """Slots for a setup round. 2 cards -> 2 each, 1 card -> n. The variations inside a card change one thing:
    the composition (unless Tony locked it), else the palette, else small details chosen by the writer."""
    cards = card_map()
    per = n // len(card_ids)
    slots = []
    for cid in card_ids:
        c = cards[cid]
        if "composition" not in tony:
            axis, values = "composition", c["compositions"][:per]
        elif "palette" not in tony:
            pal = [c["default_palette"]] + [p for p in chip_map()["palette"] if p != c["default_palette"]]
            axis, values = "palette", pal[:per]
        else:
            axis, values = "detail", [None] * per
        for v in values:
            ch = resolve_chips(c, tony, v if axis == "composition" else None)
            if axis == "palette":
                ch["palette"] = {"id": v, "by": "agent"}
            slots.append({"slot": len(slots) + 1, "card_id": cid, "chips": ch, "varies": axis})
    return slots


def plan_iterate(parent, changes, n=4):
    """n slots of the picked image's card, chips carried over with Tony's changes on top."""
    card = card_map()[parent["card_id"]]
    base = json.loads(parent["chips"] or "{}")
    for g, v in changes.items():
        base[g] = {"id": v, "by": "tony"}
    if "texture" in changes and changes["texture"] not in card["textures_ok"]:
        base["texture"] = {"id": card["default_texture"], "by": "default", "note": f"{changes['texture']} does not suit this card"}
    return [{"slot": k + 1, "card_id": card["id"], "chips": json.loads(json.dumps(base)), "varies": "feedback"}
            for k in range(n)]


# ---------- prompt writer ----------

WRITER_SYSTEM = """You write image-generation prompts for printable wall art sold by Tony's Etsy shop Ikigai \
Digital Studio. Each prompt goes to an image model with no reference image, so your words carry everything.

The art must look like a real hand-made painting or hand-pulled print photographed flat, never vector art and \
never a generic AI image. Describe the physical making: the medium, how the paint or ink sits on the surface \
(opacity, dry-brush drag, scumbling, pigment pooling, chalky or ragged edges, knife ridges, slight print \
misregistration), the paper or canvas tooth, edge quality and small human irregularities. Concrete material \
language beats hype words: never write 8K, masterpiece, ultra-detailed, award-winning or trending.

Order inside each prompt: 1) the artwork as a whole (medium, surface, a vertical 2:3 artwork filling the frame), \
2) the subject and what it is doing, 3) composition and negative space, 4) palette, 5) paint or print \
behaviour and texture, 6) mood, 7) constraints. End every prompt with: no text, letters, numbers, signature or \
watermark; the artwork alone filling the frame edge to edge, not a mockup, no frame, no wall, no room.

Rules: never name an artist, studio, brand, franchise or trademarked character; never write "in the style of"; \
never use the words "digital" or "vector"; no real people. Keep the subject of the idea but drop shop and \
marketing words (who buys it, gift, Valentine print): paint the scene itself. Respect every chip that Tony set. \
Each prompt 120 to 220 words, plain English, one or two paragraphs. Follow the slot plan exactly; prompts in a \
round share the idea and differ only as the plan says.

Reply with ONLY one JSON object, no prose:
{"cards": [{"card_id": "...", "why": "one short line"}],
 "prompts": [{"slot": 1, "card_id": "...", "composition": "<composition chip id>", "note": "what this variation tries, max 8 words", "prompt": "..."}]}"""


def _chip_text(group, chip_id):
    c = chip_map().get(group, {}).get(chip_id)
    return f"{c['label']}: {c['text']}" if c else None


def _card_block(d):
    out = [f"Card {d['id']} ({d['name']})", f"  Style fragment: {d['fragment']}"]
    if d["brushwork"]:
        out.append("  Brushwork (from the inspiration profiles): " + " | ".join(d["brushwork"]))
    if d["paint_behaviour"]:
        out.append("  Paint behaviour: " + " | ".join(d["paint_behaviour"]))
    if d["preserve"]:
        out.append("  What makes it not generic: " + "; ".join(d["preserve"][:6]))
    if d["own_palette"]:
        out.append("  Its own palette (used when the palette chip is the style default): " + ", ".join(d["own_palette"]))
    out.append("  Avoid: " + ", ".join(d["avoid"]))
    return "\n".join(out)


def _slot_block(s):
    lines = [f"Slot {s['slot']}: card {s['card_id']}; varies by {s['varies']}"]
    for g, v in s["chips"].items():
        if g == "palette" and v["by"] == "default":
            lines.append("  palette: the card's own palette, unless the idea names its own colours")
        elif v.get("id"):
            lines.append(f"  {g} ({'set by Tony, must follow' if v['by'] == 'tony' else v['by']}): {_chip_text(g, v['id'])}")
        else:
            lines.append(f"  {g}: your choice, to suit the idea")
    return "\n".join(lines)


def writer_input(idea, settings, n, plan=None, surprise=False, tony_chips=None, parent=None, feedback="",
                 taste_lines=None):
    lib = library()
    cards = card_map()
    parts = ["<idea>", f"Title: {idea['title']}", f"Description: {idea['description'] or '-'}", "</idea>", ""]
    if surprise:
        parts += ["Tony picked no style card (Surprise me). Choose the 2 cards below that best fit this idea, then "
                  f"write {n} prompts: {n // 2} per card, the two of a card differing in composition (pick a "
                  "composition chip id for each). Subject hints: "
                  + "; ".join(v["hint"] for v in lib.get("subject_defaults", {}).values()), ""]
        if tony_chips:
            parts += ["Chips Tony set (follow them in every prompt):"] + [
                f"  {g}: {_chip_text(g, v)}" for g, v in tony_chips.items()] + [""]
        parts += ["Composition chips: " + ", ".join(f"{k} = {c['text']}" for k, c in chip_map()["composition"].items()), ""]
        details = [card_detail(c, settings) for c in cards.values()]
    else:
        used = list(dict.fromkeys(s["card_id"] for s in plan))
        details = [card_detail(cards[c], settings) for c in used]
    parts += ["<style_cards>"] + [_card_block(d) for d in details] + ["</style_cards>", ""]
    if parent is not None:
        parts += ["<picked_image>", f"Tony picked this image (card {parent['card_id']}). Its prompt was:",
                  parent["prompt"], "</picked_image>", "",
                  "<feedback>", feedback, "</feedback>", "",
                  f"Write {n} revised prompts for the same card that keep what he picked and apply his feedback. "
                  "Slot 1 = the closest revision; slots 2+ apply the feedback with one small different push each "
                  "(say which in note).", ""]
    if plan:
        parts += ["<slot_plan>"] + [_slot_block(s) for s in plan] + ["</slot_plan>", ""]
    if taste_lines:
        parts += ["<tony_taste>"] + taste_lines + ["</tony_taste>", ""]
    parts.append(f"Write the {n} prompts now as the JSON object.")
    return "\n".join(parts)


def call_writer(text, settings):
    return assistant.run_cli(text, WRITER_SYSTEM, cfg(settings, "art_writer_model"),
                             cfg(settings, "art_writer_fallback_model"), cfg(settings, "art_writer_timeout_s"),
                             settings, who="The prompt writer")


def parse_writer(raw):
    raw = (raw or "").strip()
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.S)
    body = m.group(1) if m else raw[raw.find("{"): raw.rfind("}") + 1]
    try:
        obj = json.loads(body)
    except ValueError:
        raise ArtError("the prompt writer gave an unreadable answer")
    if not isinstance(obj, dict) or not isinstance(obj.get("prompts"), list):
        raise ArtError("the prompt writer gave no prompts")
    return obj


def clean_prompt(text):
    t = _undigital(text)
    t = re.sub(r"\bin the style of\b[^,.;]*[,.;]?\s*", "", t, flags=re.I).strip()
    if "no text" not in t.lower():
        t = t.rstrip() + " " + CONSTRAINTS
    return t[:6000]


def finish_plan(obj, plan, surprise, tony_chips, n):
    """Match writer prompts to slots. Surprise: the writer's cards/compositions become the plan (validated)."""
    prompts = sorted([p for p in obj["prompts"] if isinstance(p, dict) and str(p.get("prompt", "")).strip()],
                     key=lambda p: int(p.get("slot") or 0))
    if len(prompts) < n:
        raise ArtError(f"the prompt writer wrote {len(prompts)} prompts, not {n}")
    prompts = prompts[:n]
    cards = card_map()
    comps = chip_map()["composition"]
    if surprise:
        ids = list(dict.fromkeys(str(p.get("card_id")) for p in prompts))
        if not 1 <= len(ids) <= 2 or any(i not in cards for i in ids):
            raise ArtError("the prompt writer picked cards that don't exist")
        plan = []
        for k, p in enumerate(prompts):
            c = cards[str(p["card_id"])]
            comp = p.get("composition") if p.get("composition") in comps else None
            ch = resolve_chips(c, tony_chips, comp)
            if ch["palette"]["by"] == "default":                 # the writer chose colours to suit the idea
                ch["palette"] = {"id": None, "by": "agent"}
            plan.append({"slot": k + 1, "card_id": c["id"], "chips": ch, "varies": "composition"})
    out = []
    for s, p in zip(plan, prompts):
        out.append({**s, "prompt": clean_prompt(p["prompt"]), "note": str(p.get("note") or "")[:80]})
    why = "; ".join(f"{cards[c['card_id']]['name']}: {c.get('why', '')}" for c in obj.get("cards") or []
                    if isinstance(c, dict) and c.get("card_id") in cards)
    return out, why


# ---------- storage ----------

def art_root(con):
    path = con.execute("PRAGMA database_list").fetchone()[2]
    return (Path(path).parent if path else ROOT / "data") / "art"


def log(con, idea_id, action, detail=None, round_id=None, image_id=None):
    con.execute("INSERT INTO art_log(idea_id, round_id, image_id, action, detail) VALUES (?,?,?,?,?)",
                (idea_id, round_id, image_id, action, json.dumps(detail or {}, ensure_ascii=False)))
    con.commit()


def _idea(con, idea_id):
    r = con.execute("SELECT * FROM ideas WHERE id=?", (idea_id,)).fetchone()
    if not r:
        raise ArtError(f"no idea #{idea_id}")
    return r


def busy(con, idea_id):
    q = ",".join("?" * len(RUNNING))
    return con.execute(f"SELECT COUNT(*) FROM art_rounds WHERE idea_id=? AND status IN ({q})",
                       (idea_id, *RUNNING)).fetchone()[0] > 0


def picked_image(con, idea_id):
    return con.execute("SELECT i.*, p.text AS prompt FROM images i LEFT JOIN prompts p ON p.id=i.prompt_id "
                       "WHERE i.idea_id=? AND i.outcome='picked' AND i.status='done' ORDER BY i.id DESC LIMIT 1",
                       (idea_id,)).fetchone()


def taste_lines(con):
    a = taste.art_stats(con)
    out = [f"- {c['name']}: shown {c['shown']}, picked {c['picked']}, passed {c['passed']}, approved {c['approved']}"
           for c in a["cards"] if c["shown"]]
    out += [f"- feedback: {f['text']}" for f in a["feedback"][:6]]
    return out


# ---------- rounds ----------

def start_round(con, settings, idea_id, cards=None, chips=None, engine_id=None, feedback="", chip_changes=None,
                summary=""):
    """Validate and record a round (status writing). The caller runs `run_round` in a worker.
    With `feedback`: an iterate round on the picked image. Returns the round id."""
    n = int(cfg(settings, "art_images_per_round"))
    with LOCK:
        idea = _idea(con, idea_id)
        if idea["status"] != "approved":
            raise ArtError("only ideas in the Idea bank get art")
        if idea["art_state"] == "approved":
            raise ArtError("the art for this idea is already approved")
        if busy(con, idea_id):
            raise ArtError("a round for this idea is still running")
        parent = None
        if feedback:
            parent = picked_image(con, idea_id)
            if not parent:
                raise ArtError("pick an image first, then tell me what to change")
            chips = clean_chips(chip_changes)
            cards = [parent["card_id"]]
            engine_id = engine_id or parent["engine"]
        else:
            chips = clean_chips(chips)
            cards = list(dict.fromkeys(cards or []))
            if len(cards) > 2:
                raise ArtError("pick at most 2 style cards")
            bad = [c for c in cards if c not in card_map()]
            if bad:
                raise ArtError(f"unknown style card {bad[0]}")
        engine_id = engine_id or engines.config().get("default")
        e = engines.get_engine(engine_id)
        if not e:
            raise ArtError(f"unknown engine {engine_id}")
        if not e["ready"]:
            raise ArtError(f"{e['label']}: {e['env_key']} is missing on this Mac")
        no = con.execute("SELECT COALESCE(MAX(round_no), 0) + 1 FROM art_rounds WHERE idea_id=?", (idea_id,)).fetchone()[0]
        cur = con.execute(
            "INSERT INTO art_rounds(idea_id, round_no, kind, parent_image_id, engine, cards, chips, surprise, feedback, "
            "feedback_summary) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (idea_id, no, "iterate" if parent else "setup", parent["id"] if parent else None, engine_id,
             json.dumps(cards), json.dumps(chips), int(not cards), feedback or "", summary or ""))
        rid = cur.lastrowid
        con.execute("UPDATE ideas SET art_state='in_progress' WHERE id=?", (idea_id,))
        con.commit()
        lib = card_map()
        srcs = sorted({s for c in cards for s in card_detail(lib[c], settings)["source_images"]})
        log(con, idea_id, "round", {"round_no": no, "kind": "iterate" if parent else "setup", "engine": engine_id,
                                    "cards": cards, "chips_set_by_tony": chips, "surprise": not cards,
                                    "source_images": srcs, "images": n,
                                    "parent_image_id": parent["id"] if parent else None}, round_id=rid)
        if parent:
            log(con, idea_id, "feedback", {"text": feedback, "summary": summary, "chip_changes": chips,
                                           "about_image": parent["id"]},
                round_id=rid, image_id=parent["id"])
            taste.record(con, idea_id, "art_feedback", feedback)
        return rid


def _fail(con, rid, msg):
    with LOCK:
        r = con.execute("SELECT idea_id FROM art_rounds WHERE id=?", (rid,)).fetchone()
        con.execute("UPDATE art_rounds SET status='failed', message=?, finished_at=? WHERE id=?", (msg, now(), rid))
        con.commit()
        log(con, r["idea_id"], "error", {"message": msg}, round_id=rid)


def run_round(con, settings, rid, writer=None, adapter_for=None):
    """Write the prompts, check credits, make the images. Never raises; failures land on the round."""
    writer = writer or call_writer
    adapter_for = adapter_for or (lambda eid: engines.adapter_for(eid, settings))
    try:
        _run(con, settings, rid, writer, adapter_for)
    except Exception as e:  # noqa: BLE001  a worker must never die silently
        print("art round", rid, repr(e))
        _fail(con, rid, f"Something went wrong: {e}"[:300])


def _run(con, settings, rid, writer, adapter_for):
    n = int(cfg(settings, "art_images_per_round"))
    with LOCK:
        r = con.execute("SELECT * FROM art_rounds WHERE id=?", (rid,)).fetchone()
        idea = dict(_idea(con, r["idea_id"]))
        tony = json.loads(r["chips"])
        cards = json.loads(r["cards"])
        parent = None
        if r["parent_image_id"]:
            parent = dict(con.execute("SELECT i.*, p.text AS prompt FROM images i JOIN prompts p ON p.id=i.prompt_id "
                                      "WHERE i.id=?", (r["parent_image_id"],)).fetchone())
        surprise = bool(r["surprise"])
        plan = plan_iterate(parent, tony, n) if parent else (None if surprise else plan_setup(cards, tony, n))
        tl = taste_lines(con)
    fb = r["feedback"]
    if r["feedback_summary"] and r["feedback_summary"].strip() != fb.strip():
        fb += f"\n(In short: {r['feedback_summary']})"
    text = writer_input(idea, settings, n, plan, surprise, tony, parent, fb, tl)
    slots, why, last = None, "", None
    for _ in range(2):                                    # one retry on an unusable answer
        try:
            slots, why = finish_plan(parse_writer(writer(text, settings)), plan, surprise, tony, n)
            break
        except assistant.ChatUnavailable as e:
            last = f"{e}. Nothing was spent."
            break
        except ArtError as e:
            last = f"{str(e).capitalize()}. Nothing was spent."
    if not slots:
        return _fail(con, rid, last)

    with LOCK:
        ids = []
        for s in slots:
            p = con.execute("INSERT INTO prompts(idea_id, text, kind, round_id, card_id, created_at) VALUES (?,?,?,?,?,?)",
                            (r["idea_id"], s["prompt"], "art", rid, s["card_id"], now())).lastrowid
            i = con.execute("INSERT INTO images(idea_id, engine, path, round_id, prompt_id, slot, card_id, chips, note, "
                            "status, created_at) VALUES (?,?,?,?,?,?,?,?,?, 'queued', ?)",
                            (r["idea_id"], r["engine"], "", rid, p, s["slot"], s["card_id"], json.dumps(s["chips"]),
                             s["note"], now())).lastrowid
            ids.append((i, s))
            srcs = card_detail(card_map()[s["card_id"]], settings)["source_images"]
            log(con, r["idea_id"], "prompt", {"slot": s["slot"], "card": s["card_id"], "chips": s["chips"],
                                              "note": s["note"], "prompt": s["prompt"], "engine": r["engine"],
                                              "source_images": srcs},
                round_id=rid, image_id=i)
        con.execute("UPDATE art_rounds SET status='generating', writer_note=? WHERE id=?", (why, rid))
        con.commit()

    e = engines.get_engine(r["engine"])
    # controls addendum D.4: the up-front check uses the engine's estimate (the upper bound for a token-billed engine)
    # and compares only when the balance comes back as a number in the same unit; fal has no balance API (skipped)
    need = (e.get("upper_per_image") or e["credits_per_image"] or 0) * len(ids)
    try:
        ad = adapter_for(r["engine"])
        bal = engines.balance_of(ad)
    except engines.EngineError as ex:
        _fail_images(con, ids, str(ex))
        return _fail(con, rid, f"{ex}. Nothing was spent.")
    before = bal["amount"] if bal.get("unit") == "credits" else None
    if before is not None and before < need:
        _fail_images(con, ids, "not enough credits")
        return _fail(con, rid, f"kie.ai has {before:g} credits; this round needs about {need:g}. Nothing was spent.")
    if bal.get("unit") == "usd" and bal.get("amount") is not None:
        need_usd = need * engines.config().get("usd_per_credit", 0.005)
        if bal["amount"] < need_usd:
            _fail_images(con, ids, "not enough balance")
            return _fail(con, rid, f"the balance is ${bal['amount']:.2f}; this round needs about ${need_usd:.2f}. "
                                   "Nothing was spent.")
    with LOCK:
        con.execute("UPDATE art_rounds SET credits_before=? WHERE id=?", (before, rid))
        con.commit()

    with LOCK:                                            # every use of the shared connection is under LOCK
        root = art_root(con)
    folder = root / str(r["idea_id"])
    cfg_e = engines.config()

    def one(item):
        iid, s = item
        with LOCK:
            con.execute("UPDATE images SET status='running' WHERE id=?", (iid,))
            con.commit()

        def on_task(t):
            with LOCK:
                con.execute("UPDATE images SET task_id=? WHERE id=?", (t, iid))
                con.commit()
        try:
            res = ad.generate(s["prompt"], folder / f"r{r['round_no']:02d}_{s['slot']}_{iid}.png",
                              cfg_e.get("aspect_ratio", "2:3"), cfg_e.get("resolution", "1K"), on_task=on_task)
        except engines.EngineError as ex:
            with LOCK:
                con.execute("UPDATE images SET status='failed', error=? WHERE id=?", (str(ex)[:300], iid))
                con.commit()
                log(con, r["idea_id"], "error", {"image": iid, "message": str(ex)}, round_id=rid, image_id=iid)
            return False
        rel = Path(res["path"]).relative_to(root).as_posix()
        with LOCK:
            con.execute("UPDATE images SET status='done', path=?, task_id=? WHERE id=?", (rel, res["task_id"], iid))
            con.commit()
            log(con, r["idea_id"], "image", {"file": rel, "task_id": res["task_id"], "engine": r["engine"]},
                round_id=rid, image_id=iid)
        return True

    with ThreadPoolExecutor(max_workers=len(ids)) as pool:
        ok = sum(pool.map(one, ids))
    after = None
    if before is not None:
        try:
            after = engines.balance_of(ad)["amount"]
        except engines.EngineError:
            after = None
    if before is not None and after is not None and ok and e.get("price_unit") == "tokens":
        engines.record_cost(r["engine"], "art", (before - after) / ok)      # token-billed: measured per image
    status = "done" if ok == len(ids) else ("partial" if ok else "failed")
    msg = "" if ok == len(ids) else f"{len(ids) - ok} of {len(ids)} images failed"
    with LOCK:
        con.execute("UPDATE art_rounds SET status=?, message=?, credits_after=?, finished_at=? WHERE id=?",
                    (status, msg, after, now(), rid))
        con.commit()
        log(con, r["idea_id"], "round_end", {"status": status, "credits_before": before, "credits_after": after,
                                             "images_ok": ok}, round_id=rid)


def _fail_images(con, ids, msg):
    with LOCK:
        con.executemany("UPDATE images SET status='failed', error=? WHERE id=?", [(msg, i) for i, _ in ids])
        con.commit()


def spawn(fn, *args):
    threading.Thread(target=fn, args=args, daemon=True).start()


def recover(con):
    """On startup: rounds left running by a restart are marked failed (their threads are gone)."""
    with LOCK:
        q = ",".join("?" * len(RUNNING))
        con.execute(f"UPDATE art_rounds SET status='failed', message='stopped by a Portal restart', finished_at=? "
                    f"WHERE status IN ({q})", (now(), *RUNNING))
        con.execute("UPDATE images SET status='failed', error='stopped by a Portal restart' "
                    "WHERE status IN ('queued','running')")
        con.commit()


# ---------- picks and approval ----------

def _summary(card_id, chips):
    c = card_map().get(card_id, {"name": card_id})
    bits = [c["name"]] + [f"{g} {v['id']}" for g, v in (chips or {}).items() if v.get("id") and v.get("by") != "default"]
    return " · ".join(bits)


def pick(con, image_id):
    with LOCK:
        im = con.execute("SELECT * FROM images WHERE id=?", (image_id,)).fetchone()
        if not im or im["round_id"] is None:
            raise ArtError(f"no image #{image_id}")
        if im["status"] != "done":
            raise ArtError("that image is not ready")
        if _idea(con, im["idea_id"])["art_state"] == "approved":
            raise ArtError("the art for this idea is already approved")
        con.execute("UPDATE images SET outcome='passed' WHERE round_id=? AND status='done' AND id<>?",
                    (im["round_id"], image_id))
        con.execute("UPDATE images SET outcome='picked' WHERE id=?", (image_id,))
        con.commit()
        chips = json.loads(im["chips"] or "{}")
        log(con, im["idea_id"], "pick", {"card": im["card_id"], "chips": chips, "prompt_id": im["prompt_id"],
                                         "file": im["path"]}, round_id=im["round_id"], image_id=image_id)
        taste.record(con, im["idea_id"], "art_pick", _summary(im["card_id"], chips))
        return im["idea_id"]


def approve(con, idea_id, image_id=None):
    with LOCK:
        idea = _idea(con, idea_id)
        if idea["art_state"] == "approved":
            raise ArtError("the art for this idea is already approved")
        if image_id is None:
            im = picked_image(con, idea_id)
            if not im:
                raise ArtError("pick an image first")
        else:
            im = con.execute("SELECT * FROM images WHERE id=? AND idea_id=?", (image_id, idea_id)).fetchone()
            if not im or im["status"] != "done":
                raise ArtError(f"no finished image #{image_id} for this idea")
        if im["outcome"] != "picked":
            pick(con, im["id"])
        con.execute("UPDATE images SET approved=1 WHERE id=?", (im["id"],))
        con.execute("UPDATE ideas SET art_state='approved', art_image_id=? WHERE id=?", (im["id"], idea_id))
        con.commit()
        log(con, idea_id, "approve", {"image_id": im["id"], "file": im["path"], "card": im["card_id"]},
            round_id=im["round_id"], image_id=im["id"])
        taste.record(con, idea_id, "art_approve", _summary(im["card_id"], json.loads(im["chips"] or "{}")))
        return im["id"]


# ---------- views ----------

def file_url(prefix, rel):
    return f"{prefix}/art-files/{rel}" if rel else None


def idea_art(con, idea_id, prefix="/ikigai"):
    with LOCK:
        idea = _idea(con, idea_id)
        cards = card_map()
        rounds = []
        for r in con.execute("SELECT * FROM art_rounds WHERE idea_id=? ORDER BY round_no DESC", (idea_id,)):
            imgs = []
            for i in con.execute("SELECT i.*, p.text AS prompt FROM images i LEFT JOIN prompts p ON p.id=i.prompt_id "
                                 "WHERE i.round_id=? ORDER BY i.slot", (r["id"],)):
                imgs.append({"id": i["id"], "slot": i["slot"], "card_id": i["card_id"],
                             "card_name": cards.get(i["card_id"], {}).get("name", i["card_id"]),
                             "chips": json.loads(i["chips"] or "{}"), "note": i["note"], "status": i["status"],
                             "error": i["error"], "url": file_url(prefix, i["path"]) if i["status"] == "done" else None,
                             "outcome": i["outcome"], "approved": bool(i["approved"]), "prompt": i["prompt"]})
            cost = (r["credits_before"] - r["credits_after"]) if r["credits_before"] is not None and r["credits_after"] is not None else None
            eng = engines.get_engine(r["engine"]) or {}
            est = False
            if cost is None and eng.get("price_unit") == "usd":     # fal / WaveSpeed: the price table, marked est.
                done = sum(1 for i in imgs if i["status"] == "done")
                cost, est = (eng.get("credits_per_image") or 0) * done, True
            rounds.append({"id": r["id"], "round_no": r["round_no"], "kind": r["kind"], "status": r["status"],
                           "message": r["message"], "engine": r["engine"],
                           "engine_label": eng.get("label", r["engine"]), "credits_est": est,
                           "cards": [cards.get(c, {}).get("name", c) for c in json.loads(r["cards"])],
                           "chips": json.loads(r["chips"]), "surprise": bool(r["surprise"]),
                           "feedback": r["feedback"], "writer_note": r["writer_note"], "created_at": r["created_at"],
                           "credits_spent": round(cost, 2) if cost is not None else None, "images": imgs})
        return {"idea_id": idea_id, "title": idea["title"], "status": idea["status"], "art_state": idea["art_state"],
                "art_image_id": idea["art_image_id"], "busy": busy(con, idea_id), "rounds": rounds,
                "production": "not built yet"}


def oversight_log(con, idea_id):
    with LOCK:
        return [dict(r) | {"detail": json.loads(r["detail"])} for r in
                con.execute("SELECT * FROM art_log WHERE idea_id=? ORDER BY id", (idea_id,))]


def snapshot_lines(con, idea_id):
    """Art state of the idea open in Details, for the chat prompt."""
    try:
        a = idea_art(con, idea_id)
    except ArtError:
        return []
    if a["status"] != "approved":
        return []
    out = [f"Art for #{idea_id}: state {a['art_state'] or 'not started'}"
           + (f", approved image #{a['art_image_id']}" if a["art_image_id"] else "")
           + (", a round is running" if a["busy"] else "")]
    for r in a["rounds"][:2]:
        out.append(f"- round {r['round_no']} ({r['kind']}, {r['status']}, {r['engine_label']})"
                   + (f" feedback: {r['feedback'][:120]}" if r["feedback"] else ""))
        for i in r["images"]:
            out.append(f"  - image #{i['id']} {i['card_name']} {i['status']}"
                       + (f" [{i['outcome']}]" if i["outcome"] else "") + (f" ({i['note']})" if i["note"] else ""))
    p = picked_image(con, idea_id)
    out.append(f"Picked image: #{p['id']}" if p else "No image picked yet.")
    return out
