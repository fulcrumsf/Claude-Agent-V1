# image_generation.py
import argparse
import json
import subprocess
import time
from pathlib import Path

import requests


def submit_image_task(prompt: str, aspect_ratio: str = "9:16", resolution: str = "1K") -> str:
    result = subprocess.run(
        [
            "kie-cli", "gpt_image_2",
            "--prompt", prompt,
            "--aspect_ratio", aspect_ratio,
            "--resolution", resolution,
            "--json",
        ],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)["task_id"]


def poll_image_task(task_id: str, poll_interval_seconds: float = 15.0, max_attempts: int = 12) -> str:
    for attempt in range(max_attempts):
        if attempt > 0:
            time.sleep(poll_interval_seconds)

        result = subprocess.run(
            ["kie-cli", "get_task_status", "--task_id", task_id, "--json"],
            check=True, capture_output=True, text=True,
        )
        data = json.loads(result.stdout)
        status = data.get("status")

        if status == "completed":
            return data["result_urls"][0]
        if status == "failed":
            raise RuntimeError(f"Image generation task {task_id} failed: {data.get('error')}")

    raise TimeoutError(f"Image generation task {task_id} did not complete within {max_attempts} attempts")


def download_image(url: str, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path


def generate_image(prompt: str, output_path: Path, aspect_ratio: str = "9:16", resolution: str = "1K") -> Path:
    task_id = submit_image_task(prompt, aspect_ratio, resolution)
    image_url = poll_image_task(task_id)
    return download_image(image_url, Path(output_path))


def main(prompt: str, out: str, aspect_ratio: str = "9:16", resolution: str = "1K") -> None:
    generate_image(prompt, Path(out), aspect_ratio, resolution)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a POV scene image via GPT-Image-2 (kie.ai).")
    parser.add_argument("prompt", help="Image prompt")
    parser.add_argument("--out", required=True, help="Output image file path")
    parser.add_argument("--aspect_ratio", default="9:16", choices=["auto", "1:1", "9:16", "16:9", "4:3", "3:4"])
    parser.add_argument("--resolution", default="1K", choices=["1K", "2K", "4K"])
    args = parser.parse_args()
    main(args.prompt, args.out, args.aspect_ratio, args.resolution)
