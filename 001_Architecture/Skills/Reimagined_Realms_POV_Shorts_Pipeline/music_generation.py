import json
import shutil
import subprocess
import time
import requests
from pathlib import Path

def submit_music_task(prompt: str, instrumental: bool = True, model: str = "V4_5") -> str:
    result = subprocess.run(
        [
            "kie-cli", "suno_generate_music",
            "--prompt", prompt,
            "--customMode", "false",
            "--instrumental", "true" if instrumental else "false",
            "--model", model,
            "--json",
        ],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)["task_id"]


def poll_music_task(task_id: str, poll_interval_seconds: float = 20.0, max_attempts: int = 12) -> str:
    for attempt in range(max_attempts):
        if attempt > 0:
            time.sleep(poll_interval_seconds)

        result = subprocess.run(
            ["kie-cli", "get_task_status", "--task_id", task_id, "--json"],
            check=True, capture_output=True, text=True,
        )
        data = json.loads(result.stdout)
        status = (data.get("status") or "").lower()

        if status in ("completed", "success"):
            return data["result_urls"][0]
        if status in ("failed", "fail"):
            raise RuntimeError(f"Music generation task {task_id} failed: {data.get('error')}")

    raise TimeoutError(f"Music generation task {task_id} did not complete within {max_attempts} attempts")


def download_music(url: str, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path


def generate_music(prompt: str, output_path: Path, instrumental: bool = True, model: str = "V4_5") -> Path:
    task_id = submit_music_task(prompt, instrumental, model)
    music_url = poll_music_task(task_id)
    return download_music(music_url, Path(output_path))


def fit_music_to_duration(music_path: Path, output_path: Path, target_seconds: float) -> Path:
    music_path = Path(music_path)
    output_path = Path(output_path)

    duration_result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(music_path)],
        check=True, capture_output=True, text=True,
    )
    duration = float(duration_result.stdout.strip())

    if abs(duration - target_seconds) < 0.5:
        shutil.copy(music_path, output_path)
        return output_path

    if duration > target_seconds:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(music_path), "-t", str(target_seconds), "-c", "copy", str(output_path)],
            check=True, capture_output=True, text=True,
        )
        return output_path

    # duration < target_seconds: loop the track to cover the target, then trim to the exact length
    subprocess.run(
        ["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(music_path), "-t", str(target_seconds),
         "-c:a", "libmp3lame", str(output_path)],
        check=True, capture_output=True, text=True,
    )
    return output_path
