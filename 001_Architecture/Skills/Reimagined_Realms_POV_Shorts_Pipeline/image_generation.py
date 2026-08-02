# image_generation.py
import json
import subprocess
import time


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
