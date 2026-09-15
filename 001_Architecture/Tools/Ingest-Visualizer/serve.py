import os
import sys
import uuid
import importlib.util
import pathlib
import webbrowser
import threading
from flask import Flask, request, jsonify, send_file, Response, abort

# In-memory ingest job tracker - a batch of hundreds of images can take a
# long time (one vision call per image), so /api/ingest starts a background
# thread and returns immediately; the frontend polls /api/ingest_status for
# live progress instead of blocking on one giant request with no feedback.
JOBS = {}
JOBS_LOCK = threading.Lock()

_here = pathlib.Path(__file__).parent


def _load(name):
    key = f"iv_{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[key] = m
    spec.loader.exec_module(m)
    return m


config = _load("config")
items = _load("items")
video_thumb = _load("video_thumb")
ingest_runner = _load("ingest_runner")

_APP_FILE = _here / "App.html"
APP_HTML = (_APP_FILE.read_text(encoding="utf-8") if _APP_FILE.is_file()
            else "<!doctype html><title>Ingest Visualizer</title><p>App.html missing</p>")


def _safe_abspath(rel):
    """Resolve a card's rel path back to an absolute path under 000_Ingest/,
    refusing anything that would escape it."""
    base = os.path.realpath(config.INGEST_DIR)
    p = os.path.realpath(os.path.join(config.INGEST_DIR, rel))
    if p != base and not p.startswith(base + os.sep):
        abort(400)
    return p


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def home():
        return Response(APP_HTML, mimetype="text/html")

    @app.get("/api/items")
    def api_items():
        return jsonify(items.build_index())

    @app.get("/api/vocab")
    def api_vocab():
        pii = ingest_runner._load_pii()
        return jsonify({
            "folders": list(pii.load_folder_vocabulary().keys()),
            "tags": list(pii.load_tag_vocabulary().keys()),
        })

    @app.get("/thumb")
    def thumb():
        rel = request.args.get("path", "")
        abspath = _safe_abspath(rel)
        if not os.path.isfile(abspath):
            abort(404)
        low = abspath.lower()
        if low.endswith(config.IMG_EXT):
            return send_file(abspath)
        if low.endswith(config.VIDEO_EXT):
            t = video_thumb.ensure_thumb(abspath)
            if not t:
                abort(404)
            return send_file(t, mimetype="image/jpeg")
        if low.endswith(".md"):
            # A bare bookmark note - resolve via the same cascade build_index()
            # already computed (embedded local image only; remote/lazy cases
            # are served straight from their own URL by the frontend instead).
            _, thumb_kind, thumb_value = items._text_thumb_info(abspath)
            if thumb_kind == "local" and thumb_value and os.path.isfile(thumb_value):
                # must still resolve under 000_Ingest/ - never serve an arbitrary path
                real = os.path.realpath(thumb_value)
                base = os.path.realpath(config.INGEST_DIR)
                if real == base or real.startswith(base + os.sep):
                    return send_file(real)
        abort(404)

    @app.get("/url_thumb")
    def url_thumb():
        rel = request.args.get("path", "")
        abspath = _safe_abspath(rel)
        if not os.path.isfile(abspath):
            abort(404)
        _, thumb_kind, thumb_value = items._text_thumb_info(abspath)
        if thumb_kind != "lazy" or not thumb_value:
            abort(404)
        image_url = items.rl_url_preview.get_preview_image(thumb_value)
        if not image_url:
            abort(404)
        from flask import redirect
        return redirect(image_url)

    @app.get("/api/text")
    def api_text():
        rel = request.args.get("path", "")
        abspath = _safe_abspath(rel)
        if not os.path.isfile(abspath):
            abort(404)
        return jsonify({"text": open(abspath, encoding="utf-8", errors="ignore").read()})

    @app.post("/api/save_tags")
    def api_save_tags():
        body = request.get_json(force=True)
        rel = body.get("path")
        if not rel:
            abort(400)
        _safe_abspath(rel)  # validates it's a real in-scope path
        entry = {
            "title": (body.get("title") or "").strip(),
            "description": (body.get("description") or "").strip(),
            "url": (body.get("url") or "").strip(),
            "folder": (body.get("folder") or "").strip(),
            "tags": [t for t in (body.get("tags") or []) if t],
            "note": (body.get("note") or "").strip(),
        }
        items.save_state_entry(rel, entry)
        return jsonify({"ok": True})

    @app.post("/api/batch_tags")
    def api_batch_tags():
        """Apply the same folder (and optionally tags) to many items at once."""
        body = request.get_json(force=True)
        paths = body.get("paths") or []
        folder = (body.get("folder") or "").strip()
        tags = [t for t in (body.get("tags") or []) if t]
        for rel in paths:
            _safe_abspath(rel)
            existing = items.get_state_entry(rel)
            entry = dict(existing)
            if folder:
                entry["folder"] = folder
            if tags:
                entry["tags"] = tags
            entry.setdefault("title", "")
            entry.setdefault("description", "")
            entry.setdefault("url", "")
            entry.setdefault("note", "")
            items.save_state_entry(rel, entry)
        return jsonify({"ok": True, "count": len(paths)})

    def _ingest_one(rel):
        abspath = _safe_abspath(rel)
        if not os.path.isfile(abspath):
            return {"path": rel, "status": "missing"}
        entry = items.get_state_entry(rel)
        low = abspath.lower()
        try:
            if low.endswith(config.VIDEO_EXT):
                r = ingest_runner.ingest_video(abspath, entry.get("tags"), entry.get("note"))
            elif low.endswith(".md"):
                r = ingest_runner.ingest_text(abspath, entry)
            elif low.endswith(config.IMG_EXT):
                r = ingest_runner.ingest_image(abspath, entry)
            elif low.endswith(".pdf"):
                r = ingest_runner.ingest_pdf(abspath, entry)
            else:
                r = {"status": "error", "message": "no ingest handler for this file type yet"}
            r["path"] = rel
            if r.get("status") in ("written", "undetermined"):
                items.clear_state_entry(rel)
            return r
        except Exception as e:
            return {"path": rel, "status": "error", "message": str(e)}

    def _run_job(job_id, paths):
        for rel in paths:
            result = _ingest_one(rel)
            with JOBS_LOCK:
                job = JOBS[job_id]
                job["results"].append(result)
                job["done"] += 1
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "complete"

    @app.post("/api/ingest")
    def api_ingest():
        body = request.get_json(force=True)
        paths = body.get("paths") or []
        job_id = uuid.uuid4().hex
        with JOBS_LOCK:
            JOBS[job_id] = {"total": len(paths), "done": 0, "results": [], "status": "running"}
        threading.Thread(target=_run_job, args=(job_id, paths), daemon=True).start()
        return jsonify({"job_id": job_id, "total": len(paths)})

    @app.get("/api/ingest_status")
    def api_ingest_status():
        job_id = request.args.get("job_id", "")
        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if not job:
                abort(404)
            return jsonify(dict(job))  # shallow copy - results list itself is fine to share for reading

    return app


def main():
    app = create_app()
    threading.Timer(0.8, lambda: webbrowser.open(f"http://localhost:{config.PORT}")).start()
    print(f"Ingest Visualizer -> http://localhost:{config.PORT}")
    app.run(port=config.PORT, debug=False, threaded=True)


if __name__ == "__main__":
    main()
