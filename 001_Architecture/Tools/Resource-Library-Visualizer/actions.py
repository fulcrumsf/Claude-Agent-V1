import os
import re
import sys
import shutil
import importlib.util
import pathlib
import yaml

_here = pathlib.Path(__file__).parent


def _load(name):
    key = f"rlv_{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[key] = m
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


def move_note(note_rel_path, dest_folder):
    """Move a note .md + its co-located image(s) into dest_folder (a top-level
    Resource Library category). Returns the new rel path. Same-name stem is kept."""
    if dest_folder not in config.CATEGORY_FOLDERS or "/" in dest_folder or dest_folder.startswith("."):
        raise ValueError(f"bad destination folder: {dest_folder!r}")
    src_md = os.path.join(config.RESOURCE_LIB, note_rel_path)
    if not os.path.isfile(src_md):
        raise FileNotFoundError(note_rel_path)
    dst_dir = os.path.join(config.RESOURCE_LIB, dest_folder)
    os.makedirs(dst_dir, exist_ok=True)
    stem = os.path.splitext(src_md)[0]
    base_stem = os.path.basename(stem)
    if os.path.exists(os.path.join(dst_dir, base_stem + ".md")):
        raise FileExistsError(f"{dest_folder}/{base_stem}.md already exists")
    for src in [src_md] + [stem + e for e in config.IMG_EXT]:
        if os.path.isfile(src):
            shutil.move(src, os.path.join(dst_dir, os.path.basename(src)))
    return os.path.join(dest_folder, base_stem + ".md")


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


def rewrite_note_raw(note_rel_path, raw_yaml_text, body=None):
    """Replace a note's frontmatter with hand-edited raw YAML text verbatim
    (preserves block scalars / formatting instead of round-tripping through
    yaml.safe_dump). Validates it parses to a mapping before writing."""
    try:
        parsed = yaml.safe_load(raw_yaml_text)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}") from e
    if not isinstance(parsed, dict):
        raise ValueError("Frontmatter must be a YAML mapping (key: value pairs)")
    path = os.path.join(config.RESOURCE_LIB, note_rel_path)
    text = open(path, encoding="utf-8").read()
    m = FM_RE.match(text)
    old_body = m.group(2) if m else text
    new_body = old_body if body is None else body
    if not new_body.endswith("\n"):
        new_body += "\n"
    fm_text = raw_yaml_text.strip("\n")
    open(path, "w", encoding="utf-8").write(f"---\n{fm_text}\n---\n{new_body}")
    return parsed


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
