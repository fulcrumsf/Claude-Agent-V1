#!/usr/bin/env python3
"""Upscale a finished video to 1920x1080 with automatic fallback (locked 2026-09-20, Tony; order changed 2026-09-23, Tony).

Order of attempts:
  0. fal.ai Topaz (fal-ai/topaz/upscale/video), DEFAULT since 2026-09-23 (Tony: half Kie's price, $0.02/s up to 1080p vs Kie $0.04/s,
     and it exposes the model choice). Model = Proteus with Topaz's automatic settings, 2x: Topaz's docs describe Proteus as the model for
     "low to medium-quality footage"; Iris (their face model) is not offered on fal, and the Starlight models are generative (more face morphing risk).
     2x keeps the output at or under 1080p (fal's cheapest tier; above 1080p costs $0.08/s). Up to TWO attempts. Key: FAL_AI_API_KEY.
  1. Backup: Kie.ai Topaz 2x (scale factor only, no model/face settings), up to TWO attempts (a failed provider call spends no credits).
  2. If BOTH Kie attempts fail: Magnific video upscaler (API, MAGNIFIC_API_KEY in ~/.env-secrets), 1k / 'natural' / creativity 0.
  3. FFmpeg normalize to exactly 1920x1080 (scale-decrease + pad), the same final step for either provider.
Never overwrites an existing output. Refuses the Magnific fallback if its estimated cost exceeds --max-magnific-usd (default 5.00) so a long clip needs Tony's OK.
Magnific cost estimate: output frames x $0.007 (720p/1k, secondary source; check your Magnific credit balance).
Known weakness of the Magnific route (first run, monkey shot v7): even at creativity 0 it can add fine detail that was not in the source (a striped tail); review the result.

The final FFmpeg step takes the AUDIO from the original raw clip (a provider may drop or re-encode it).

Usage: python3 upscale_video.py <raw.mp4> --stem Seedance_Mini_v7 --out-dir <shot>/Data [--log <Generation_Log.json>] [--dry-run] [--skip-fal] [--skip-kie]
Outputs: <out-dir>/<stem>_FalTopaz_Proteus_2x.mp4 OR <stem>_Topaz_2x.mp4 OR <stem>_Magnific_1k.mp4, then <stem>_1080p_FINAL.mp4."""
import argparse, json, os, subprocess, sys, time
from pathlib import Path
import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
load_dotenv(Path.home() / ".env-secrets")
KIE_ATTEMPTS = 2
FAL_ATTEMPTS = 2
FAL_TOPAZ_MODEL = "Proteus"
FAL_TOPAZ_PER_SEC_USD = 0.02  # up to 1080p output, fal pricing page 2026-09-23
MAGNIFIC_PER_FRAME_USD = 0.007


def frames_and_fps(p: Path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate,duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip().split(",")
    num, den = out[0].split("/"); fps = float(num) / float(den); dur = float(out[1])
    return int(round(fps * dur)), fps


def kie_public_url(p: Path) -> str:
    key = os.environ["KIE_API_KEY"]
    with p.open("rb") as h:
        r = requests.post("https://kieai.redpandaai.co/api/file-stream-upload", headers={"Authorization": f"Bearer {key}"},
                          data={"uploadPath": "neon-parcel", "fileName": p.name}, files={"file": (p.name, h)}, timeout=180)
    r.raise_for_status(); url = (r.json().get("data") or {}).get("downloadUrl")
    if not url:
        raise RuntimeError(f"Kie upload returned no URL: {r.text[:200]}")
    return url


def try_kie_topaz(url: str, out: Path, log):
    from kie_market_api import create_task, poll_task, download
    for attempt in range(1, KIE_ATTEMPTS + 1):
        try:
            tid = create_task("topaz/video-upscale", {"video_url": url, "upscale_factor": "2"})
            res = poll_task(tid); urls = res.get("resultUrls") or []
            if not urls:
                raise RuntimeError("no result URL")
            download(urls[0], out); log({"stage": "topaz-2x", "provider": "kie", "attempt": attempt, "task_id": tid, "status": "success", "output": str(out)})
            return True
        except Exception as e:
            log({"stage": "topaz-2x", "provider": "kie", "attempt": attempt, "status": "provider_failed", "error": str(e)[:250]})
            print(f"  Kie Topaz attempt {attempt}/{KIE_ATTEMPTS} failed: {str(e)[:120]}", flush=True)
            time.sleep(20)
    return False


def try_fal_topaz(url: str, out: Path, log):
    key = os.getenv("FAL_KEY") or os.getenv("FAL_AI_API_KEY") or os.getenv("FAL.AI_API_KEY")
    if not key:
        log({"stage": "fal-topaz-2x", "provider": "fal", "status": "skipped", "error": "no fal key in ~/.env-secrets"}); return False
    os.environ["FAL_KEY"] = key
    import fal_client
    args = {"video_url": url, "model": FAL_TOPAZ_MODEL, "upscale_factor": 2, "H264_output": True}
    for attempt in range(1, FAL_ATTEMPTS + 1):
        try:
            res = fal_client.subscribe("fal-ai/topaz/upscale/video", arguments=args, with_logs=False)
            vurl = ((res or {}).get("video") or {}).get("url")
            if not vurl:
                raise RuntimeError(f"no video url in fal response: {str(res)[:200]}")
            with requests.get(vurl, stream=True, timeout=600) as rr:
                rr.raise_for_status(); out.write_bytes(rr.content)
            log({"stage": "fal-topaz-2x", "provider": "fal", "attempt": attempt, "params": args, "status": "success", "output": str(out)})
            return True
        except Exception as e:
            log({"stage": "fal-topaz-2x", "provider": "fal", "attempt": attempt, "params": args, "status": "provider_failed", "error": str(e)[:250]})
            print(f"  fal Topaz attempt {attempt}/{FAL_ATTEMPTS} failed: {str(e)[:120]}", flush=True)
            time.sleep(20)
    return False


def magnific(url: str, out: Path, log):
    H = {"x-magnific-api-key": os.environ["MAGNIFIC_API_KEY"], "Content-Type": "application/json"}
    body = {"video": url, "resolution": "1k", "creativity": 0, "fps_boost": False, "sharpen": 0, "smart_grain": 0, "flavor": "natural"}
    r = requests.post("https://api.magnific.com/v1/ai/video-upscaler", headers=H, json=body, timeout=60); r.raise_for_status()
    tid = r.json()["data"]["task_id"]; print("  Magnific task", tid, flush=True)
    for _ in range(120):
        j = requests.get(f"https://api.magnific.com/v1/ai/video-upscaler/{tid}", headers=H, timeout=60).json().get("data", {})
        if j.get("status") == "COMPLETED" and j.get("generated"):
            with requests.get(j["generated"][0], stream=True, timeout=600) as rr:
                rr.raise_for_status(); out.write_bytes(rr.content)
            log({"stage": "magnific-1k", "provider": "magnific", "task_id": tid, "params": body, "status": "success", "output": str(out)})
            return True
        if j.get("status") in ("FAILED", "ERROR"):
            log({"stage": "magnific-1k", "provider": "magnific", "task_id": tid, "status": "failed", "error": str(j.get("error"))}); return False
        time.sleep(15)
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("raw", type=Path); ap.add_argument("--stem", required=True); ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--log", type=Path); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--skip-kie", action="store_true", help="testing: skip fal AND Kie, go straight to the Magnific fallback")
    ap.add_argument("--skip-fal", action="store_true", help="skip the fal default and start at the Kie backup")
    ap.add_argument("--max-magnific-usd", type=float, default=5.0)
    a = ap.parse_args()
    falv = a.out_dir / f"{a.stem}_FalTopaz_{FAL_TOPAZ_MODEL}_2x.mp4"
    topaz = a.out_dir / f"{a.stem}_Topaz_2x.mp4"; mag = a.out_dir / f"{a.stem}_Magnific_1k.mp4"; final = a.out_dir / f"{a.stem}_1080p_FINAL.mp4"
    for p in (falv, topaz, mag, final):
        if p.exists():
            sys.exit(f"BLOCKED: {p} already exists; never overwrite. Use a new --stem.")
    frames, fps = frames_and_fps(a.raw); est = frames * MAGNIFIC_PER_FRAME_USD
    fal_est = frames / fps * FAL_TOPAZ_PER_SEC_USD
    print(f"Plan: fal Topaz {FAL_TOPAZ_MODEL} 2x x{FAL_ATTEMPTS} (est ${fal_est:.2f}) -> Kie Topaz x{KIE_ATTEMPTS} -> (if both fail) Magnific 1k (~{frames} frames, est ${est:.2f}) -> FFmpeg 1920x1080")
    if est > a.max_magnific_usd:
        print(f"NOTE: the Magnific fallback would exceed --max-magnific-usd ({a.max_magnific_usd}); it will be refused and Tony asked instead.")
    if a.dry_run:
        print("DRY RUN: nothing uploaded or submitted."); return

    def log(entry):
        if a.log:
            d = json.loads(a.log.read_text()); d.setdefault("processing", []).append(entry); a.log.write_text(json.dumps(d, indent=2))
    url = kie_public_url(a.raw)
    src = None
    if not a.skip_kie and not a.skip_fal and try_fal_topaz(url, falv, log):
        src = falv
    elif not a.skip_kie and try_kie_topaz(url, topaz, log):
        src = topaz
    else:
        if est > a.max_magnific_usd:
            sys.exit(f"STOP: fal and Kie failed and Magnific would cost ~${est:.2f} (> ${a.max_magnific_usd}). Ask Tony.")
        print("Falling back to Magnific...", flush=True)
        if magnific(url, mag, log):
            src = mag
    if not src:
        sys.exit("BOTH providers failed; ask Tony.")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-i", str(a.raw), "-map", "0:v:0", "-map", "1:a:0?",
                    "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", str(final)], check=True)
    log({"stage": "ffmpeg-normalize-1920x1080", "source": str(src), "output": str(final), "status": "success"})
    print("FINAL", final, "(via", {falv: "fal Topaz " + FAL_TOPAZ_MODEL, topaz: "Kie Topaz", mag: "Magnific"}[src], ")")


if __name__ == "__main__":
    main()
