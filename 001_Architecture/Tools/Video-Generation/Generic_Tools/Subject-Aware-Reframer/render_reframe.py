"""Streaming OpenCV/FFmpeg rendering for an explicit crop plan."""
from __future__ import annotations

import json
import math
import subprocess
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

from diagnose import FFMPEG, FFPROBE, decode, save_json, sha256


class Encoder:
    def __init__(self, path, width, height, fps, count, cfg):
        self.path = path
        self.partial = path.with_suffix(".incomplete.mp4")
        self.log = path.with_suffix(".log").open("x")
        tb = Fraction(cfg["time_base"])
        start, end = cfg["shots"][0]["start_pts"], cfg["shots"][-1]["end_pts"]
        args = [FFMPEG, "-nostdin", "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "bgr24",
                "-s", f"{width}x{height}", "-r", str(fps), "-i", "pipe:0",
                "-ss", str(float(start*tb)), "-t", str(float((end-start)*tb)), "-i", cfg["source"],
                "-map", "0:v:0", "-map", "1:a:0?", "-af", "asetpts=PTS-STARTPTS,apad",
                "-t", str(count/fps), "-c:v", "libx264", "-threads", "2", "-preset", "fast",
                "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000",
                "-ac", "2", "-b:a", "192k", "-movflags", "+faststart", str(self.partial)]
        self.proc = subprocess.Popen(args, stdin=subprocess.PIPE, stderr=self.log)

    def write(self, frame):
        self.proc.stdin.write(frame.tobytes())

    def finish(self):
        self.proc.stdin.close()
        code = self.proc.wait()
        self.log.close()
        if code:
            raise RuntimeError(f"Encoder failed; retained partial output and log: {self.path}")
        if self.path.exists():
            raise FileExistsError(self.path)
        self.partial.rename(self.path)

    def stop(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        self.log.close()


def group_frame(frame, width, height, brightness, blur):
    import cv2
    import numpy as np
    sh, sw = frame.shape[:2]
    # Blur a small cover crop, then enlarge; keep the foreground at full source quality.
    crop_width = sh*width/height
    x = max(0, round((sw-crop_width)/2))
    small = cv2.resize(frame[:, x:sw-x], (max(32, width//8), max(32, height//8)))
    blurred = cv2.GaussianBlur(small, (blur, blur), 0)
    background = cv2.resize(blurred, (width, height), interpolation=cv2.INTER_LINEAR)
    background = (background.astype(np.float32)*brightness).astype(np.uint8)
    scale = min(width/sw, height/sh)
    fw, fh = round(sw*scale), round(sh*scale)
    foreground = cv2.resize(frame, (fw, fh), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
    left, top = (width-fw)//2, (height-fh)//2
    background[top:top+fh, left:left+fw] = foreground
    return background


def compose(frame, entry, output, backgrounds):
    import cv2
    import numpy as np
    width, height = output["width"], output["height"]
    if entry["layout"] == "fit_blur":
        key = (width, height, entry["background_brightness"], entry["background_blur"])
        if key not in backgrounds:
            backgrounds[key] = group_frame(frame, *key)
        return backgrounds[key]
    x1, y1, x2, y2 = entry["crop_xyxy"]
    # Sample floating crop coordinates directly to avoid integer rounding jitter.
    transform = np.array([[(x2-x1)/width, 0, x1], [0, (y2-y1)/height, y1]], dtype=np.float32)
    return cv2.warpAffine(frame, transform, (width, height),
                          flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)


def text_line(canvas, text, point, size=0.55, color=(235,235,235)):
    import cv2
    cv2.putText(canvas, text, point, cv2.FONT_HERSHEY_SIMPLEX, size, (0,0,0), 3, cv2.LINE_AA)
    cv2.putText(canvas, text, point, cv2.FONT_HERSHEY_SIMPLEX, size, color, 1, cv2.LINE_AA)


def debug_frame(source, preview, entry):
    import cv2
    import numpy as np
    canvas = np.zeros((704, 1320, 3), dtype=np.uint8)
    canvas[:540, :960] = cv2.resize(source, (960,540))
    canvas[:640,960:] = cv2.resize(preview, (360,640))
    sx, sy = 960/source.shape[1], 540/source.shape[0]
    for subject in entry["subjects"]:
        x1,y1,x2,y2 = subject["box"]
        cv2.rectangle(canvas, (round(x1*sx),round(y1*sy)), (round(x2*sx),round(y2*sy)),
                      (100,240,100) if subject["family"]=="person" else (255,180,60), 1)
    x1,y1,x2,y2 = entry["crop_xyxy"]
    cv2.rectangle(canvas, (round(x1*sx),round(y1*sy)), (min(959,round(x2*sx)),min(539,round(y2*sy))), (30,240,255), 3)
    text_line(canvas, f"{entry['shot']} | master {entry['source_seconds']:.3f}s | {entry['layout']}", (16,575), .65)
    text_line(canvas, entry["reason"], (16,609), .60)
    text_line(canvas, "Yellow: source area shown. Green: person. Blue: animal. Lookahead/held boxes may precede or outlast visibility.", (16,672), .52)
    return canvas


def verify_video(path, width, height, frames, fps):
    info = json.loads(subprocess.run([FFPROBE,"-v","error","-show_streams","-of","json",str(path)],
                                    check=True, capture_output=True, text=True).stdout)
    video = next(s for s in info["streams"] if s["codec_type"]=="video")
    if video["codec_name"] != "h264" or video["pix_fmt"] != "yuv420p":
        raise RuntimeError(f"Output codec verification failed: {path}")
    if (video["width"], video["height"], int(video["nb_frames"]), video["avg_frame_rate"]) != (width,height,frames,f"{fps}/1"):
        raise RuntimeError(f"Output format/timing verification failed: {path}")
    if float(video["start_time"]) != 0 or abs(float(video["duration"])-frames/fps) > .002:
        raise RuntimeError(f"Output start/duration verification failed: {path}")
    audio = next((s for s in info["streams"] if s["codec_type"]=="audio"), None)
    if audio and (audio["codec_name"] != "aac" or audio["sample_rate"] != "48000" or audio["channels"] != 2):
        raise RuntimeError(f"Output audio format verification failed: {path}")
    if audio and (float(audio["start_time"]) != 0 or abs(float(video["duration"])-float(audio["duration"])) > 1/fps):
        raise RuntimeError(f"Audio alignment failed: {path}")
    subprocess.run([FFMPEG,"-v","error","-xerror","-i",str(path),"-f","null","-"], check=True, capture_output=True)
    return {"width": width, "height": height, "frames": frames, "fps": fps,
            "video_start": video["start_time"], "video_duration": video["duration"],
            "audio_start": audio.get("start_time") if audio else None,
            "audio_duration": audio.get("duration") if audio else None,
            "sha256": sha256(path), "full_decode_passed": True}


def render(plan, cache, out, security):
    import cv2
    import numpy as np
    from reframe import checked_file, resource_check
    cv2.setNumThreads(2)
    started = time.monotonic()
    job, variants = plan["job"], plan["variants"]
    names = list(variants)
    output = job["output"]
    fps, width, height = output["fps"], output["width"], output["height"]
    reference = variants[names[0]]
    mapping = reference["source_record_per_output_frame"]
    count = len(mapping)
    if any(v["source_record_per_output_frame"] != mapping or v["output"] != output for v in variants.values()):
        raise ValueError("Variants must share source timing and output geometry")
    picks = []
    for shot in cache["config"]["shots"]:
        ids = [i for i,f in enumerate(reference["frames"]) if f["shot"] == shot["id"]]
        picks.extend(ids[round((len(ids)-1)*t)] for t in (0, .25, .5, .75, 1))
    featured = next((name for name in names if variants[name]["settings"]["mode"]=="hybrid"), names[0])
    encoders, paths, thumbs = {}, {}, {}
    comparison_path, debug_path = out/"Framing-Comparison-v1.mp4", out/"Framing-Debug-v1.mp4"
    generator = decode(cache["config"], cache["stream"])
    try:
        for name in names:
            paths[name] = out/f"{job['output_stem']}-{name}-v1.mp4"
            encoders[name] = Encoder(paths[name], width,height,fps,count,cache["config"])
        comparison = Encoder(comparison_path, 360*len(names),720,fps,count,cache["config"])
        encoders["_comparison"] = comparison
        debug = Encoder(debug_path,1320,704,fps,count,cache["config"])
        encoders["_debug"] = debug
        decoded_index, source = -1, None
        for i, record_index in enumerate(mapping):
            while decoded_index < record_index:
                source = next(generator)
                decoded_index += 1
            backgrounds, previews = {}, {}
            combined = np.zeros((720,360*len(names),3),dtype=np.uint8)
            for n, name in enumerate(names):
                entry = variants[name]["frames"][i]
                preview = compose(source, entry, output, backgrounds)
                previews[name] = preview
                encoders[name].write(preview)
                combined[:640,n*360:(n+1)*360] = cv2.resize(preview,(360,640))
                text_line(combined, f"{name} | {entry['layout']}", (n*360+10,665), .55)
                text_line(combined, f"master {entry['source_seconds']:.3f}s", (n*360+10,697), .48)
            comparison.write(combined)
            featured_entry = variants[featured]["frames"][i]
            debug.write(debug_frame(source,previews[featured],featured_entry))
            if i in picks:
                tile = np.zeros((414,216,3),dtype=np.uint8)
                tile[:384] = cv2.resize(previews[featured],(216,384))
                text_line(tile, f"{featured_entry['source_seconds']:.2f}s {featured_entry['layout']}", (5,404), .35)
                thumbs[i] = tile
            if i % 90 == 0:
                resource_check(job["output_root"])
                print(f"Rendered {i+1}/{count} frames across {len(names)} variants", flush=True)
        for encoder in encoders.values():
            encoder.finish()
    finally:
        generator.close()
        for encoder in encoders.values():
            encoder.stop()
    rows = math.ceil(len(picks)/5)
    sheet = np.zeros((rows*414,5*216,3),dtype=np.uint8)
    for n,i in enumerate(picks):
        sheet[n//5*414:(n//5+1)*414,n%5*216:(n%5+1)*216] = thumbs[i]
    contact = out/"Framing-Contact-Sheet-v1.jpg"
    if contact.exists() or not cv2.imwrite(str(contact),sheet,[cv2.IMWRITE_JPEG_QUALITY,95]):
        raise RuntimeError("Contact sheet write failed")
    checked_file(job["source"],job["source_sha256"])
    for path,fingerprint in job["protected_media"].items():
        checked_file(path,fingerprint)
    verified = {name: verify_video(path,width,height,count,fps) for name,path in paths.items()}
    verified["comparison"] = verify_video(comparison_path,360*len(names),720,count,fps)
    verified["debug"] = verify_video(debug_path,1320,704,count,fps)
    report = {"stage": "gate_3", "status": "rendered_and_verified_awaiting_tony_review",
              "job_id": job["job_id"], "security": security, "source_unchanged": True,
              "protected_media_unchanged": True, "elapsed_seconds": round(time.monotonic()-started,3),
              "outputs": verified, "resources": resource_check(job["output_root"]),
              "layout_counts": {name: dict(Counter(f["layout"] for f in v["frames"])) for name,v in variants.items()},
              "reason_counts": {name: dict(Counter(f["reason"] for f in v["frames"])) for name,v in variants.items()},
              "contact_sheet_frames": picks, "contact_sheet_sha256": sha256(contact),
              "crop_plan_sha256": sha256(out/"Crop-Plan-v1.json")}
    save_json(out/"Run-Report-v1.json",report)
    print(json.dumps(report,indent=2),flush=True)
