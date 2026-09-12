import os
import sys
import collections
import importlib.util
import pathlib
import webbrowser
import threading
from flask import Flask, request, jsonify, send_file, Response, abort

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
thumbs = _load("thumbs")
render = _load("render")
queue = _load("queue")
actions = _load("actions")

_APP_FILE = _here / "App.html"
APP_HTML = (_APP_FILE.read_text(encoding="utf-8") if _APP_FILE.is_file()
            else "<!doctype html><title>Resource Library Visualizer</title>"
                 "<p>app.html missing</p>")


def _safe_abs(rel):
    base = os.path.realpath(config.RESOURCE_LIB)
    p = os.path.realpath(os.path.join(config.RESOURCE_LIB, rel))
    if p != base and not p.startswith(base + os.sep):
        abort(400)
    return p


def _card_public(c):
    d = {k: c[k] for k in ("path", "title", "summary", "folder", "tags", "kind",
                           "source_label", "vision_risk", "glyph_color",
                           "ingested_at", "youtube_id")}
    if c["kind"] == "image" and c["image_abspath"]:
        d["thumb"] = "/thumb?path=" + c["path"]
    elif c["kind"] == "youtube" and c["youtube_id"]:
        d["thumb"] = thumbs.youtube_poster_url(c["youtube_id"])
    else:
        d["thumb"] = None
    return d


def create_app():
    app = Flask(__name__)
    print("scanning 007_Resource_Library …", flush=True)
    app.config["INDEX"] = notes.build_index()
    print(f"indexed {len(app.config['INDEX'])} notes", flush=True)

    def idx():
        return app.config["INDEX"]

    @app.get("/")
    def home():
        return Response(APP_HTML, mimetype="text/html")

    @app.get("/api/notes")
    def api_notes():
        if request.args.get("refresh"):
            app.config["INDEX"] = notes.build_index()
        return jsonify([_card_public(c) for c in idx()])

    @app.get("/api/filters")
    def api_filters():
        folders = sorted({c["folder"] for c in idx() if c["folder"]}
                         | set(config.CATEGORY_FOLDERS))
        # top tags from the gallery-visible notes (image / youtube), not text-only
        gallery = [c for c in idx() if c["kind"] != "text"]
        tag_counts = collections.Counter(t for c in gallery for t in c["tags"])
        vocab = config.tag_vocabulary()
        # off-vocab audit: any tag on ANY note (text-only included) that isn't in
        # the locked vocabulary - leftovers from before the vocab existed, or a
        # model slip that validation should have caught but didn't.
        all_tag_counts = collections.Counter(
            t for c in idx() if c["folder"] != "OpenAI_History" for t in c["tags"])
        off_vocab = sorted(
            ((t, n) for t, n in all_tag_counts.items() if t not in vocab),
            key=lambda x: -x[1])
        return jsonify({"folders": folders,
                        "move_targets": config.CATEGORY_FOLDERS,
                        "top_tags": [t for t, _ in tag_counts.most_common(8)],
                        "tag_vocab": sorted(vocab),
                        "off_vocab_tags": off_vocab})

    @app.get("/api/note")
    def api_note():
        rel = request.args["path"]
        ab = _safe_abs(rel)
        fm, body = notes.parse_note(ab)
        raw_fm, _ = notes.raw_frontmatter_text(ab)
        body_html = render.render_body(body, os.path.dirname(rel))
        card = next((c for c in idx() if c["path"] == rel), None)
        if card and card.get("youtube_id") and card["youtube_id"] not in body_html:
            body_html = (f'<iframe class="yt" src="https://www.youtube.com/embed/'
                         f'{card["youtube_id"]}" frameborder="0" allowfullscreen></iframe>'
                         + body_html)
        return jsonify({
            "path": rel,
            "frontmatter": fm,
            "frontmatter_raw": raw_fm,
            "frontmatter_html": render.frontmatter_html(fm),
            "body_html": body_html,
        })

    @app.get("/thumb")
    def thumb():
        c = next((x for x in idx() if x["path"] == request.args["path"]), None)
        if not c or not c["image_abspath"]:
            abort(404)
        t = thumbs.ensure_thumb(c["image_abspath"])
        if not t:
            abort(404)
        return send_file(t, mimetype="image/jpeg")

    @app.get("/img")
    def img():
        ab = _safe_abs(request.args["path"])
        if not os.path.isfile(ab):
            abort(404)
        return send_file(ab)

    @app.patch("/api/note")
    def patch_note():
        body = request.get_json(force=True)
        rel = body.pop("path")
        if body.get("raw_frontmatter") is not None:
            try:
                actions.rewrite_note_raw(rel, body["raw_frontmatter"], body.get("body"))
            except Exception as e:  # noqa: BLE001 - bad hand-edited YAML is expected
                return jsonify({"ok": False, "error": str(e)}), 400
        else:
            actions.rewrite_note(rel, body)
        for c in idx():
            if c["path"] == rel:
                fm, _ = notes.parse_note(os.path.join(config.RESOURCE_LIB, rel))
                c["title"] = str(fm.get("title") or c["title"])
                c["summary"] = str(fm.get("summary") or "")
                c["tags"] = [str(t) for t in (fm.get("tags") or [])]
        return jsonify({"ok": True})

    @app.post("/api/delete")
    def delete():
        paths = request.get_json(force=True)["paths"]
        moved = {p: actions.move_to_delete(p) for p in paths}
        app.config["INDEX"] = [c for c in idx() if c["path"] not in set(paths)]
        return jsonify({"ok": True, "moved": moved})

    @app.post("/api/move")
    def move():
        b = request.get_json(force=True)
        paths, dest = b["paths"], b["dest"]
        moved, errors = {}, {}
        for p in paths:
            try:
                new_rel = actions.move_note(p, dest)
                for c in idx():
                    if c["path"] == p:
                        c["path"] = new_rel
                        c["folder"] = dest
                        c["abspath"] = os.path.join(config.RESOURCE_LIB, new_rel)
                        if c.get("image_abspath"):
                            c["image_abspath"] = os.path.join(
                                config.RESOURCE_LIB, dest, os.path.basename(c["image_abspath"]))
                        break
                moved[p] = new_rel
            except Exception as e:  # noqa: BLE001 - surface to UI
                errors[p] = str(e)
        return jsonify({"ok": not errors, "moved": moved, "errors": errors})

    @app.post("/api/rerun-ai")
    def rerun():
        body = request.get_json(force=True)
        paths = body["paths"] if "paths" in body else [body["path"]]
        results = {}
        for p in paths:
            try:
                results[p] = actions.rerun_ai(p)
            except Exception as e:  # noqa: BLE001 - surface any wiring/vision failure to the UI
                results[p] = {"error": str(e)}
        return jsonify({"ok": True, "results": results,
                        "est_cost": actions.estimate_rerun_cost(len(paths))})

    @app.post("/api/comment")
    def comment():
        b = request.get_json(force=True)
        queue.add_comment(b["path"], b["text"])
        return jsonify({"ok": True})

    @app.post("/api/queue/finalize")
    def finalize():
        return jsonify({"ok": True, "batch": queue.finalize()})

    return app


def main():
    app = create_app()
    url = f"http://localhost:{config.PORT}"
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    print(f"Resource Library Visualizer -> {url}  ({len(app.config['INDEX'])} notes)")
    app.run(port=config.PORT, debug=False)


if __name__ == "__main__":
    main()
