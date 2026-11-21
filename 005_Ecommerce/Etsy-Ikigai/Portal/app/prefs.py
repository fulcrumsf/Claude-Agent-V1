"""Tony's live Production controls (controls addendum G, 2026-11-21): the reference-share and closeness sliders, the
panel's room-scene engine and the Generate-all cap. Stored in the DB `meta` table under `ui.<key>` as JSON; the
defaults come from config/settings.json, which code never writes. Validated: share 0-100 in steps of 10, closeness
0-100, cap 0-1000, the engine must exist (an engines.json id or a kie_edit short id such as "nbpro")."""
import json

from .db import DB_LOCK as LOCK, get_meta, set_meta

DEFAULTS = {"planner_reference_share": 80, "planner_reference_closeness": 60, "room_scene_engine": "nbpro",
            "generate_all_cap_credits": 120}
KEYS = {"reference_share": "planner_reference_share", "reference_closeness": "planner_reference_closeness",
        "scene_engine": "room_scene_engine", "generate_all_cap": "generate_all_cap_credits"}


class PrefError(ValueError):
    """A plain reason a value was refused."""


def default(settings, key):
    s = KEYS[key]
    return (settings or {}).get(s, DEFAULTS[s])


def validate(key, value):
    if key not in KEYS:
        raise PrefError(f"unknown setting {key}")
    if key == "scene_engine":
        from . import engines, kie_edit
        v = str(value or "").strip()
        if not (engines.scene_engine_id(v) or v in kie_edit.MODELS):
            raise PrefError(f"unknown engine {v}")
        e = engines.raw_engine(engines.scene_engine_id(v) or "") or {}
        if engines.scene_engine_id(v) and not (e.get("scene_id") or (e.get("uses") or {}).get("room")):
            raise PrefError(f"{e.get('label', v)} does not make room scenes")
        return engines.scene_engine_id(v) or v
    try:
        n = int(round(float(value)))
    except (TypeError, ValueError):
        raise PrefError(f"{key} must be a number")
    if key == "reference_share":
        if not 0 <= n <= 100 or n % 10:
            raise PrefError("the reference share is 0 to 100 in steps of 10")
    elif key == "reference_closeness":
        if not 0 <= n <= 100:
            raise PrefError("closeness is 0 to 100")
    elif key == "generate_all_cap":
        if not 0 <= n <= 1000:
            raise PrefError("the Generate-all cap is 0 to 1000 credits")
    return n


def get(con, settings, key):
    with LOCK:
        raw = get_meta(con, f"ui.{key}") if con is not None else None
    if raw is not None:
        try:
            return validate(key, json.loads(raw))
        except (ValueError, PrefError):
            pass
    return default(settings, key)


def put(con, key, value, settings=None):
    v = validate(key, value)
    with LOCK:
        set_meta(con, f"ui.{key}", json.dumps(v))
    return v


def all_prefs(con, settings):
    return {k: get(con, settings, k) for k in KEYS}
