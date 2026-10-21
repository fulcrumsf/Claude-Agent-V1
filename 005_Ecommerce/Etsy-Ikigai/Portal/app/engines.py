import os

from .db import load_config


def list_engines():
    out = []
    for e in load_config("engines")["engines"]:
        out.append({**e, "ready": bool(os.environ.get(e["env_key"]))})
    return out


def run_prompt(engine_id, prompt):
    """Stub. Returns a list of image paths. Implement one adapter per provider (fal, openai)."""
    engine = next((e for e in list_engines() if e["id"] == engine_id), None)
    if not engine:
        raise ValueError(f"unknown engine {engine_id}")
    if not engine["ready"]:
        raise RuntimeError(f"{engine['env_key']} not set; add it to .env")
    raise NotImplementedError("engine adapters not implemented yet")
