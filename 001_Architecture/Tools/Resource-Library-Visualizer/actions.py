import os
import re
import shutil
import importlib.util
import pathlib
import yaml

_here = pathlib.Path(__file__).parent


def _load(name):
    spec = importlib.util.spec_from_file_location(f"rlv_{name}", _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


config = _load("config")
notes = _load("notes")
queue = _load("queue")

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.S)


def move_to_delete(note_rel_path):
    src_md = os.path.join(config.RESOURCE_LIB, note_rel_path)
    dst_dir = os.path.join(config.DELETE_DIR, os.path.dirname(note_rel_path))
    os.makedirs(dst_dir, exist_ok=True)
    moved = []
    stem = os.path.splitext(src_md)[0]
    candidates = [src_md] + [stem + e for e in config.IMG_EXT]
    for src in candidates:
        if os.path.isfile(src):
            dst = os.path.join(dst_dir, os.path.basename(src))
            shutil.move(src, dst)
            moved.append(dst)
    queue.log_delete(note_rel_path)
    return moved


def _coerce_tags(v):
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [t.strip() for t in str(v).split(",") if t.strip()]


def rewrite_note(note_rel_path, fields):
    path = os.path.join(config.RESOURCE_LIB, note_rel_path)
    text = open(path, encoding="utf-8").read()
    m = FM_RE.match(text)
    fm_text, body = (m.group(1), m.group(2)) if m else ("", text)
    fm = (yaml.safe_load(fm_text) or {}) if fm_text else {}
    if not isinstance(fm, dict):
        fm = {}
    for key in ("title", "summary", "url"):
        if key in fields and fields[key] is not None:
            fm[key] = str(fields[key])
    if "tags" in fields and fields["tags"] is not None:
        fm["tags"] = _coerce_tags(fields["tags"])
    if fields.get("body") is not None:
        body = fields["body"]
        if not body.endswith("\n"):
            body += "\n"
    new_fm = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
    open(path, "w", encoding="utf-8").write(f"---\n{new_fm}\n---\n{body}")


def estimate_rerun_cost(n):
    return round(n * 0.01, 2)


def _default_vision(image_abspath):
    p = pathlib.Path(config.WORKSPACE) / "001_Architecture/Scripts/process_image_ingest.py"
    spec = importlib.util.spec_from_file_location("rlv_pii", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "process_image"):
        return mod.process_image(image_abspath) or {}
    raise NotImplementedError("wire process_image_ingest vision entrypoint")


def rerun_ai(note_rel_path, vision_fn=None):
    vision_fn = vision_fn or _default_vision
    path = os.path.join(config.RESOURCE_LIB, note_rel_path)
    before, _ = notes.parse_note(path)
    img = notes.find_sibling_image(path)
    after_raw = vision_fn(img) if img else {}
    after = dict(before)
    for k in ("title", "summary", "url", "tags"):
        if k in after_raw and after_raw[k]:
            after[k] = after_raw[k]
    return {"before": before, "after": after, "applied": False}
