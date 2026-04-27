"""
Production Supervisor — bioluminescence_weapon video generation.

This is the production manager. It does not stop until every clip is done.

Behavior:
  - Works through every clip in new_clips_prompts.json one at a time
  - Classifies every API error using the official Kie.ai error codes
    (sourced from Obsidian Vault: /003_Tools/docs/kie.ai_api/Veo3.1_Video.md and Kling 3.0.md)
  - Takes the correct action for each error type:
      FATAL   → stop immediately, notify you — something needs your attention
      CREDITS → stop immediately, notify you to top up credits
      SKIP    → prompt was rejected by content policy, move to next clip
      RATE    → rate limited, wait 90s then retry
      WAIT    → service maintenance, wait 2 min then retry
      RETRY   → transient server error, retry with backoff
      UNKNOWN → logs full error details, escalates to you via notification
  - If the supervisor genuinely can't diagnose an error, it tells you exactly
    what the raw error was and asks for guidance, then pauses that clip and
    continues with the rest rather than sitting stagnant
  - After each successful video, immediately creates video_looped.mp4
  - Sends macOS notifications at key milestones
  - Only gives up on a clip after MAX_CLIP_RETRIES consecutive failures

API docs:  Obsidian Vault /003_Tools/docs/kie.ai_api/
  Kling:   Kling 3.0.md         → POST /api/v1/jobs/createTask
  Veo3:    Veo3.1_Video.md      → POST /api/v1/veo/generate

Usage:
  python3 -u 004_Tools/pipeline_supervisor.py          # run (blocks — use nohup &)
  python3 -u 004_Tools/pipeline_supervisor.py --status # print status and exit
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

HOME_SECRETS = Path.home() / ".env-secrets"
load_dotenv(HOME_SECRETS)

# ── API keys ──────────────────────────────────────────────────────────────────
KIE_API_KEY = os.getenv("KIE_API_KEY")
FAL_API_KEY = os.getenv("FAL.AI_API_KEY")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE           = Path("002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon")
PROMPTS_FILE   = BASE / "new_clips_prompts.json"
DONE_FILE      = Path("/tmp/biolum_pipeline_done.txt")
SUPERVISOR_LOG = Path("/tmp/biolum_supervisor.log")
FAILURES_FILE  = Path("/tmp/biolum_failures.json")

# ── Tuning ────────────────────────────────────────────────────────────────────
MAX_CLIP_RETRIES  = 4     # give up on a specific clip after this many failures
POLL_INTERVAL     = 10    # seconds between status polls
POLL_TIMEOUT      = 1800  # 30 min max wait per clip
BETWEEN_CLIPS     = 5     # seconds between starting new clips (API breathing room)
NOTIFY_EVERY      = 10    # send a progress notification every N completed clips

# ── Error classification (sourced from API docs) ───────────────────────────────
# references/docs/kie.ai_api/Veo3.1_Video.md + Kling 3.0.md
#
# Category → what the supervisor does:
#   FATAL   → stop immediately, notify user, exit (don't waste more credits)
#   CREDITS → stop immediately, notify user to top up credits, exit
#   SKIP    → prompt rejected by content policy — mark failed, move on
#   RATE    → rate limited — wait 90s then retry
#   WAIT    → service maintenance — wait 2 min then retry
#   RETRY   → transient server error — retry with backoff (normal path)
#   UNKNOWN → can't diagnose — log full details, escalate to user, then continue
#
# Source: Veo3.1 error codes (HTTP 200 body with code field):
#   200  success
#   400  1080P processing / content policy rejection / image fetch error
#   401  Unauthorized — invalid API key
#   402  Insufficient Credits
#   404  Not found
#   422  Validation error / content policy / prompt rejected
#   429  Rate limited
#   455  Service maintenance
#   500  Server error
#   501  Generation failed (task-level)
#   505  Feature disabled
#
KIE_ERROR_MAP = {
    400: ("SKIP",    "Content policy rejection or bad request"),
    401: ("FATAL",   "Invalid API key — check KIE_API_KEY in .env"),
    402: ("CREDITS", "Insufficient credits — top up at kie.ai/pricing"),
    404: ("RETRY",   "Endpoint not found — transient routing error"),
    422: ("SKIP",    "Prompt rejected by content policy or validation failed"),
    429: ("RATE",    "Rate limited by Kie.ai"),
    455: ("WAIT",    "Kie.ai service is under maintenance"),
    500: ("RETRY",   "Kie.ai server error — transient"),
    501: ("RETRY",   "Generation task failed on server — transient"),
    505: ("SKIP",    "Feature disabled on Kie.ai — cannot generate this clip"),
}

WAIT_FOR_RATE      = 90   # seconds to wait when rate-limited
WAIT_FOR_MAINT     = 120  # seconds to wait when service is in maintenance


# ── Logging ───────────────────────────────────────────────────────────────────

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(SUPERVISOR_LOG, "a") as f:
        f.write(line + "\n")


def notify(title: str, body: str, sound: str = "Glass"):
    subprocess.run(
        ["osascript", "-e", f'display notification "{body}" with title "{title}" sound name "{sound}"'],
        capture_output=True
    )


# ── KIE.AI helpers ────────────────────────────────────────────────────────────

def kie_headers() -> dict:
    return {"Authorization": f"Bearer {KIE_API_KEY}", "Content-Type": "application/json"}


def kie_poll(task_id: str, endpoint: str) -> dict:
    """Poll until success/fail/timeout. Returns completed data block."""
    url   = f"https://api.kie.ai{endpoint}?taskId={task_id}"
    start = time.time()
    interval = POLL_INTERVAL

    while time.time() - start < POLL_TIMEOUT:
        time.sleep(interval)
        interval = min(interval + 5, 30)
        try:
            resp = requests.get(url, headers=kie_headers(), timeout=20)
            data = resp.json().get("data") or {}
        except Exception as e:
            log(f"  Poll warning ({task_id[:16]}): {e}")
            continue

        state = data.get("state")
        flag  = data.get("successFlag")

        if state == "success" or flag == 1:
            return {"ok": True, "data": data}
        if state in ("fail", "failed") or flag in [2, 3, -1]:
            return {"ok": False, "reason": f"state={state} flag={flag} data={json.dumps(data)[:200]}"}

        elapsed = int(time.time() - start)
        log(f"  [{task_id[:20]}] {elapsed}s — state={state}")

    return {"ok": False, "reason": f"Timeout after {POLL_TIMEOUT}s"}


def extract_video_url(data: dict) -> str:
    """Extract video URL from completed task data block."""
    result_str = data.get("resultJson", "{}")
    try:
        obj  = json.loads(result_str) if isinstance(result_str, str) else result_str
        urls = obj.get("resultUrls", [])
        if urls:
            return urls[0]
        if obj.get("url"):
            return obj["url"]
    except Exception:
        pass
    # Veo3 fallback
    resp = data.get("response") or {}
    urls = resp.get("resultUrls", [])
    return urls[0] if urls else (data.get("url") or data.get("videoUrl") or "")


# ── Per-clip generators ───────────────────────────────────────────────────────

def _classify_kie_response(http_status: int, body: dict) -> tuple:
    """
    Returns (category, message) from a Kie.ai response.
    Checks both HTTP status and the JSON body 'code' field — Kie.ai often
    returns HTTP 200 with an error code inside the body.
    Categories: OK | FATAL | CREDITS | SKIP | RATE | WAIT | RETRY | UNKNOWN
    """
    # Body-level code takes priority (Kie.ai uses HTTP 200 + body code for errors)
    body_code = body.get("code", 0)
    body_msg  = body.get("msg", "")

    check_code = body_code if body_code not in (0, 200) else http_status

    if check_code in (200, 0):
        return ("OK", "")

    category, desc = KIE_ERROR_MAP.get(check_code, ("UNKNOWN", f"Undocumented error code {check_code}"))
    reason = f"[{check_code}] {desc}" + (f" — {body_msg}" if body_msg and body_msg != "success" else "")
    return (category, reason)


def generate_veo3(entry: dict) -> dict:
    """Submit Veo3 job. Returns {ok, url, error_category} or {ok:False, reason, error_category}."""
    try:
        resp = requests.post(
            "https://api.kie.ai/api/v1/veo/generate",
            headers=kie_headers(),
            json={
                "model": entry.get("model", "veo3_fast"),
                "prompt": entry["video_prompt"],
                "aspect_ratio": entry.get("aspect_ratio", "16:9"),
                "generationType": "TEXT_2_VIDEO",
            },
            timeout=30,
        )
    except requests.exceptions.ConnectionError as e:
        return {"ok": False, "error_category": "RETRY", "reason": f"Network error: {e}"}
    except requests.exceptions.Timeout:
        return {"ok": False, "error_category": "RETRY", "reason": "Request timed out"}

    try:
        body = resp.json()
    except Exception:
        body = {}

    category, reason = _classify_kie_response(resp.status_code, body)
    if category != "OK":
        return {"ok": False, "error_category": category, "reason": reason}

    nested  = body.get("data") or {}
    task_id = body.get("taskId") or nested.get("taskId")
    if not task_id:
        return {"ok": False, "error_category": "UNKNOWN", "reason": f"No taskId in response: {str(body)[:200]}"}

    log(f"  Veo3 task: {task_id}")
    result = kie_poll(task_id, "/api/v1/veo/record-info")
    if not result["ok"]:
        return result

    url = extract_video_url(result["data"])
    return {"ok": True, "url": url} if url else {"ok": False, "error_category": "RETRY", "reason": "No URL in completed response"}


def generate_kling(entry: dict) -> dict:
    """Submit Kling 3.0 job. Returns {ok, url, error_category} or {ok:False, reason, error_category}."""
    try:
        resp = requests.post(
            "https://api.kie.ai/api/v1/jobs/createTask",
            headers=kie_headers(),
            json={
                "model": "kling-3.0/video",
                "input": {
                    "prompt": entry["video_prompt"],
                    "sound": False,
                    "duration": str(entry.get("duration_s", 8)),
                    "aspect_ratio": entry.get("aspect_ratio", "16:9"),
                    "mode": "pro",
                    "multi_shots": False,
                },
            },
            timeout=30,
        )
    except requests.exceptions.ConnectionError as e:
        return {"ok": False, "error_category": "RETRY", "reason": f"Network error: {e}"}
    except requests.exceptions.Timeout:
        return {"ok": False, "error_category": "RETRY", "reason": "Request timed out"}

    try:
        body = resp.json()
    except Exception:
        body = {}

    category, reason = _classify_kie_response(resp.status_code, body)
    if category != "OK":
        return {"ok": False, "error_category": category, "reason": reason}

    nested  = body.get("data") or {}
    task_id = body.get("taskId") or nested.get("taskId")
    if not task_id:
        return {"ok": False, "error_category": "UNKNOWN", "reason": f"No taskId in response: {str(body)[:200]}"}

    log(f"  Kling task: {task_id}")
    result = kie_poll(task_id, "/api/v1/jobs/recordInfo")
    if not result["ok"]:
        return result

    url = extract_video_url(result["data"])
    return {"ok": True, "url": url} if url else {"ok": False, "error_category": "RETRY", "reason": "No URL in completed response"}


def generate_flux_image(entry: dict) -> dict:
    """Submit Flux Pro image job. Returns {ok, url} or {ok:False, reason}."""
    size_map = {"16:9": "landscape_16_9", "9:16": "portrait_16_9", "1:1": "square_hd"}
    image_size = size_map.get(entry.get("aspect_ratio", "16:9"), "landscape_16_9")

    try:
        resp = requests.post(
            "https://fal.run/fal-ai/flux-pro",
            headers={"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"},
            json={
                "prompt": entry["image_prompt"],
                "image_size": image_size,
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
                "num_images": 1,
                "safety_tolerance": "2",
                "output_format": "png",
            },
            timeout=120,
        )
    except requests.exceptions.Timeout:
        return {"ok": False, "reason": "Fal.ai timeout"}

    if not resp.ok:
        return {"ok": False, "reason": f"HTTP {resp.status_code}: {resp.text[:200]}"}

    images = resp.json().get("images", [])
    if not images or not images[0].get("url"):
        return {"ok": False, "reason": f"No image in response: {resp.text[:200]}"}

    return {"ok": True, "url": images[0]["url"]}


# ── Clip manifest ─────────────────────────────────────────────────────────────

MANIFEST_FILE = BASE / "clip_manifest.json"


def _load_manifest() -> list:
    if MANIFEST_FILE.exists():
        try:
            return json.loads(MANIFEST_FILE.read_text())
        except Exception:
            pass
    return []


def write_clip_manifest_entry(entry: dict, status: str, notes: str = "") -> None:
    """
    Append or update one entry in clip_manifest.json after generation.

    Schema per entry:
      scene_id       — e.g. "scene_03b"
      reference_image — "✓" if reference_image path exists, "✗" otherwise
      source         — "kie.ai" | "fal.ai"
      model          — from entry["model"] or entry["generation_type"]
      status         — "ok" | "failed" | "skipped"
      notes          — any failure reason or human note
    """
    manifest = _load_manifest()

    ref_path = entry.get("reference_image", "")
    ref_ok = "✓" if ref_path and Path(ref_path).exists() else "✗"
    gen_type = entry.get("generation_type", "video")
    source = "fal.ai" if gen_type == "image" else "kie.ai"
    model = entry.get("model", gen_type)

    record = {
        "scene_id": entry["scene_id"],
        "reference_image": ref_ok,
        "source": source,
        "model": model,
        "status": status,
        "notes": notes,
    }

    # Update existing or append
    for i, existing in enumerate(manifest):
        if existing.get("scene_id") == entry["scene_id"]:
            manifest[i] = record
            break
    else:
        manifest.append(record)

    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))


# ── Three-layer audio pre-flight check ────────────────────────────────────────

def check_audio_layers() -> None:
    """
    Warn if any of the three required audio layers are missing.
    Does not block production — just informs.

    Layers:
      1. Narration  → beat_sheet.json must exist (built by audio_tts.py)
      2. Score      → score/ folder must contain at least one file
      3. Ambient    → Kling clips will be regenerated with sound:true in next pass
                       (sfx/ folder or note in log)
    """
    beat_sheet = BASE / "beat_sheet.json"
    score_dir  = BASE / "score"
    sfx_dir    = BASE / "sfx"

    issues = []
    if not beat_sheet.exists():
        issues.append(
            "  ⚠ Layer 1 MISSING: beat_sheet.json not found.\n"
            "    Run: python3 tools/audio_tts.py <script.md> <audio_dir>"
        )
    if not score_dir.exists() or not any(score_dir.iterdir()):
        issues.append(
            "  ⚠ Layer 2 MISSING: No score files in score/ folder.\n"
            "    Generate a full-length instrumental via Suno and save to score/"
        )
    if not sfx_dir.exists() or not any(sfx_dir.iterdir()):
        issues.append(
            "  ⚠ Layer 3 MISSING: No sfx files in sfx/ folder.\n"
            "    Kling clips with sound:true will populate this layer"
        )

    if issues:
        log("── THREE-LAYER AUDIO CHECK ──────────────────────────────────")
        for issue in issues:
            log(issue)
        log("─────────────────────────────────────────────────────────────")
    else:
        log("✓ Three-layer audio check passed (narration + score + sfx)")


# ── Preloop ───────────────────────────────────────────────────────────────────

def preloop(src: Path, dst: Path) -> bool:
    """Re-encode src → dst with clean keyframes. Duration = natural clip length."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(src)],
        capture_output=True, text=True
    )
    try:
        duration = float(result.stdout.strip())
    except ValueError:
        duration = 8.0

    r = subprocess.run([
        "ffmpeg", "-y",
        "-stream_loop", "1",
        "-i", str(src),
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an",
        str(dst), "-loglevel", "error",
    ])
    return r.returncode == 0


def preloop_originals():
    """Run the original preloop_videos.sh using homebrew bash (supports declare -A)."""
    log("Prelooping original clips...")
    r = subprocess.run(
        ["/opt/homebrew/bin/bash", "tools/preloop_videos.sh"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        log(f"  preloop_videos.sh warning: {r.stderr[:200]}")
    else:
        log("  Original clips prelooped OK")


# ── Download helper ───────────────────────────────────────────────────────────

def download(url: str, dest: Path) -> bool:
    try:
        r = requests.get(url, timeout=180, stream=True)
        r.raise_for_status()
        dest.write_bytes(r.content)
        return True
    except Exception as e:
        log(f"  Download error: {e}")
        return False


# ── Status printer ────────────────────────────────────────────────────────────

def print_status():
    entries     = json.loads(PROMPTS_FILE.read_text())
    vid_entries = [e for e in entries if e.get("generation_type") == "video"]
    img_entries = [e for e in entries if e.get("generation_type") == "image"]

    looped  = sum(1 for e in vid_entries if (Path(e["output_folder"]) / "video_looped.mp4").exists())
    raw     = sum(1 for e in vid_entries if (Path(e["output_folder"]) / "video.mp4").exists()
                  and not (Path(e["output_folder"]) / "video_looped.mp4").exists())
    pending = len(vid_entries) - looped - raw
    imgs    = sum(1 for e in img_entries if (Path(e["output_folder"]) / "image.png").exists())

    failures = {}
    if FAILURES_FILE.exists():
        try:
            failures = json.loads(FAILURES_FILE.read_text())
        except Exception:
            pass

    print(f"\n=== SUPERVISOR STATUS ===")
    print(f"  Videos looped  : {looped}/{len(vid_entries)}")
    print(f"  Videos raw     : {raw}  (awaiting preloop)")
    print(f"  Videos pending : {pending}")
    print(f"  Images done    : {imgs}/{len(img_entries)}")
    if failures:
        print(f"  Permanent fails: {len(failures)}")
        for sid, reason in failures.items():
            print(f"    ✗ {sid}: {reason[:80]}")
    print(f"  Pipeline done  : {'YES ✓' if DONE_FILE.exists() else 'no'}")
    print(f"  Supervisor log : {SUPERVISOR_LOG}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    log("=" * 56)
    log("PRODUCTION SUPERVISOR — bioluminescence_weapon v4")
    log("=" * 56)
    notify("🎬 Production Supervisor", "Starting — will not stop until all clips are done.")

    check_audio_layers()

    entries     = json.loads(PROMPTS_FILE.read_text())
    vid_entries = [e for e in entries if e.get("generation_type") == "video"]
    img_entries = [e for e in entries if e.get("generation_type") == "image"]

    # Sort: critical → high → medium
    priority_order = {"critical": 0, "high": 1, "medium": 2}
    vid_entries.sort(key=lambda e: priority_order.get(e.get("priority", "medium"), 2))

    failures: dict[str, str] = {}  # scene_id → reason for permanent failure
    completed = 0
    total_vid = len(vid_entries)
    total_img = len(img_entries)

    # ── Video clips ───────────────────────────────────────────────────────────
    log(f"Processing {total_vid} video clips ({total_img} images already handled)...")

    for entry in vid_entries:
        scene_id = entry["scene_id"]
        folder   = Path(entry["output_folder"])
        raw_path = folder / "video.mp4"
        lp_path  = folder / "video_looped.mp4"
        model    = entry.get("model", "kling_v2")
        is_veo   = "veo" in model.lower()

        # Already fully done
        if lp_path.exists():
            log(f"  ✓ {scene_id} — already looped, skipping")
            completed += 1
            continue

        folder.mkdir(parents=True, exist_ok=True)
        attempts = 0
        success  = False

        while attempts < MAX_CLIP_RETRIES:
            attempts += 1

            # If raw exists but not looped, skip generation and go straight to preloop
            if raw_path.exists():
                log(f"  → {scene_id} — raw exists, prelooping...")
            else:
                log(f"  → {scene_id} [{entry.get('priority')}] attempt {attempts}/{MAX_CLIP_RETRIES} ({model})")

                result = generate_veo3(entry) if is_veo else generate_kling(entry)

                if not result["ok"]:
                    reason   = result.get("reason", "unknown")
                    category = result.get("error_category", "UNKNOWN")
                    log(f"  ✗ {scene_id} attempt {attempts} [{category}]: {reason[:140]}")

                    if category == "FATAL":
                        # Bad API key — nothing will work, stop everything
                        notify("🚨 SUPERVISOR STOPPED", f"Fatal API error: {reason[:80]}", sound="Basso")
                        log(f"  FATAL error — supervisor stopping. Check KIE_API_KEY in .env")
                        sys.exit(1)

                    elif category == "CREDITS":
                        # Out of credits — pause and wait for user action
                        notify("💸 OUT OF CREDITS", "Kie.ai credits exhausted. Top up at kie.ai/pricing then restart supervisor.", sound="Basso")
                        log(f"  CREDITS error — stopping. Add credits at kie.ai/pricing then re-run supervisor.")
                        sys.exit(1)

                    elif category == "SKIP":
                        # Prompt rejected by content policy — no point retrying
                        log(f"  Prompt rejected (content policy) — skipping {scene_id}, moving on")
                        notify("⚠️ Prompt Rejected", f"{scene_id} rejected by content policy — skipped.", sound="Basso")
                        failures[scene_id] = f"SKIP: {reason}"
                        FAILURES_FILE.write_text(json.dumps(failures, indent=2))
                        write_clip_manifest_entry(entry, "skipped", f"Content policy: {reason[:120]}")
                        success = True   # don't count as retry-able failure
                        break

                    elif category == "RATE":
                        log(f"  Rate limited — waiting {WAIT_FOR_RATE}s before retry...")
                        time.sleep(WAIT_FOR_RATE)
                        attempts -= 1    # don't burn a retry on rate limiting
                        continue

                    elif category == "WAIT":
                        log(f"  Kie.ai maintenance — waiting {WAIT_FOR_MAINT}s before retry...")
                        time.sleep(WAIT_FOR_MAINT)
                        attempts -= 1    # don't burn a retry on maintenance
                        continue

                    elif category == "UNKNOWN":
                        # Can't diagnose — log full error, escalate to user, pause then continue
                        log(f"  UNKNOWN error for {scene_id}. Full details: {reason}")
                        log(f"  API docs: references/docs/kie.ai_api/")
                        notify(
                            "❓ Unknown API Error",
                            f"{scene_id}: {reason[:80]} — check supervisor log for full details.",
                            sound="Basso"
                        )
                        # Pause this clip, let user investigate, but keep going with others
                        if attempts < MAX_CLIP_RETRIES:
                            backoff = 60 * attempts
                            log(f"  Pausing {backoff}s then retrying (attempt {attempts}/{MAX_CLIP_RETRIES})...")
                            time.sleep(backoff)
                        continue

                    else:
                        # RETRY — transient server error, standard backoff
                        if attempts < MAX_CLIP_RETRIES:
                            backoff = 30 * attempts
                            log(f"  Retrying in {backoff}s...")
                            time.sleep(backoff)
                    continue

                # Download
                log(f"  Downloading {scene_id}...")
                if not download(result["url"], raw_path):
                    log(f"  ✗ {scene_id} download failed (attempt {attempts})")
                    raw_path.unlink(missing_ok=True)
                    time.sleep(15)
                    continue

                mb = raw_path.stat().st_size / 1024 / 1024
                log(f"  ✓ {scene_id} downloaded ({mb:.1f} MB)")

            # Preloop immediately after download
            log(f"  → {scene_id} prelooping...")
            if preloop(raw_path, lp_path):
                mb = lp_path.stat().st_size / 1024 / 1024
                log(f"  ✓ {scene_id} looped ({mb:.1f} MB)")
                write_clip_manifest_entry(entry, "ok")
                success = True
                completed += 1

                # Milestone notification
                if completed % NOTIFY_EVERY == 0:
                    remaining = total_vid - completed
                    notify("📹 Progress Update", f"{completed}/{total_vid} clips done. ~{remaining} remaining.")
                break
            else:
                log(f"  ✗ {scene_id} preloop failed — retrying generation")
                raw_path.unlink(missing_ok=True)
                lp_path.unlink(missing_ok=True)

        if not success:
            reason = f"Failed after {MAX_CLIP_RETRIES} attempts"
            log(f"  ✗✗ {scene_id} PERMANENTLY FAILED: {reason}")
            failures[scene_id] = reason
            FAILURES_FILE.write_text(json.dumps(failures, indent=2))
            write_clip_manifest_entry(entry, "failed", reason)
            notify("⚠️ Clip Failed", f"{scene_id} gave up after {MAX_CLIP_RETRIES} attempts — check log.", sound="Basso")

        time.sleep(BETWEEN_CLIPS)

    # ── Any images that weren't generated yet ─────────────────────────────────
    for entry in img_entries:
        scene_id = entry["scene_id"]
        img_path = Path(entry["output_folder"]) / "image.png"
        if img_path.exists():
            continue

        Path(entry["output_folder"]).mkdir(parents=True, exist_ok=True)
        log(f"  → {scene_id} [image] generating...")
        attempts = 0

        while attempts < MAX_CLIP_RETRIES:
            attempts += 1
            result = generate_flux_image(entry)
            if not result["ok"]:
                log(f"  ✗ {scene_id} image attempt {attempts}: {result.get('reason','')[:100]}")
                time.sleep(20 * attempts)
                continue
            if download(result["url"], img_path):
                kb = img_path.stat().st_size / 1024
                log(f"  ✓ {scene_id} image saved ({kb:.0f} KB)")
                break
            img_path.unlink(missing_ok=True)

    # ── Preloop originals ─────────────────────────────────────────────────────
    preloop_originals()

    # ── Final report ──────────────────────────────────────────────────────────
    entries     = json.loads(PROMPTS_FILE.read_text())
    vid_entries = [e for e in entries if e.get("generation_type") == "video"]
    looped = sum(1 for e in vid_entries if (Path(e["output_folder"]) / "video_looped.mp4").exists())

    log("=" * 56)
    log(f"DONE. {looped}/{total_vid} clips looped. {len(failures)} permanent failures.")
    if failures:
        log(f"Permanent failures: {list(failures.keys())}")

    DONE_FILE.write_text(f"COMPLETE at {datetime.now().isoformat()}\n{looped}/{total_vid} clips\nFailed: {list(failures.keys())}")

    if failures:
        notify(
            "🎬 v4 Done (with failures)",
            f"{looped}/{total_vid} clips ready. {len(failures)} failed — check supervisor log.",
            sound="Basso"
        )
    else:
        notify(
            "🎬 Bioluminescence v4 READY",
            f"All {looped} clips looped. Open Remotion Studio at localhost:3001.",
            sound="Glass"
        )

    log("Supervisor complete.")


if __name__ == "__main__":
    if "--status" in sys.argv:
        print_status()
        sys.exit(0)

    # Prevent duplicate supervisors
    result = subprocess.run(["pgrep", "-f", "pipeline_supervisor"], capture_output=True, text=True)
    pids = [p for p in result.stdout.strip().split() if p != str(os.getpid())]
    if pids:
        print(f"Supervisor already running (PID {pids[0]}). Use --status to check.")
        sys.exit(0)

    run()
