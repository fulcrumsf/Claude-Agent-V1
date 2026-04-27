"""
Batch AI video generator — reads ai_prompts.json, generates Kling/Veo videos for each scene.
Skips scenes where video.mp4 already exists.
Usage: python3 004_Tools/run_video_gen_batch.py 002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon/ai_prompts.json [--priority critical|high|medium|all]
"""
import os
import sys
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

HOME_SECRETS = Path.home() / ".env-secrets"
load_dotenv(HOME_SECRETS)
KIE_API_KEY = os.getenv("KIE_API_KEY")

POLL_INTERVAL = 20
MAX_POLLS = 90  # 30 minutes max per scene


def generate_video(scene: dict) -> bool:
    output_folder = Path(scene["output_folder"])
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / "video.mp4"

    if output_path.exists():
        print(f"  ✓ Already exists, skipping: {scene['scene_id']}")
        return True

    prompt = scene["video_prompt"]
    model = scene.get("model", "veo3_fast")
    aspect_ratio = scene.get("aspect_ratio", "16:9")

    print(f"\n  → Queuing: {scene['scene_id']} [{scene.get('priority','?')}]")
    print(f"    Prompt: {prompt[:80]}...")

    url = "https://api.kie.ai/api/v1/veo/generate"
    headers = {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "generationType": "TEXT_2_VIDEO",
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if not resp.ok:
        print(f"  ✗ Failed to queue: {resp.status_code} {resp.text[:200]}")
        return False

    data = resp.json()
    task_id = data.get("taskId") or data.get("data", {}).get("taskId")
    if not task_id:
        print(f"  ✗ No taskId in response: {data}")
        return False

    print(f"    Task ID: {task_id} — polling every {POLL_INTERVAL}s...")
    status_url = f"https://api.kie.ai/api/v1/veo/record-info?taskId={task_id}"

    for attempt in range(MAX_POLLS):
        time.sleep(POLL_INTERVAL)
        try:
            status_resp = requests.get(status_url, headers=headers, timeout=15).json()
            block = status_resp.get("data") or {}
            flag = block.get("successFlag")

            if flag == 1:
                urls = block.get("response", {}).get("resultUrls", [])
                vid_url = urls[0] if urls else block.get("url")
                if not vid_url:
                    print(f"  ✗ No video URL in response: {block}")
                    return False
                print(f"    Downloading from: {vid_url[:60]}...")
                dl = requests.get(vid_url, timeout=120)
                dl.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(dl.content)
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"  ✓ Saved: {output_path} ({size_mb:.1f} MB)")
                return True

            elif flag == -1:
                error_msg = block.get("response", {}).get("failedMsg", "unknown error")
                print(f"  ✗ Generation failed: {error_msg}")
                return False

            else:
                elapsed = (attempt + 1) * POLL_INTERVAL
                print(f"    [{elapsed}s] Status: pending...")

        except Exception as e:
            print(f"    Poll error: {e}")

    print(f"  ✗ Timed out after {MAX_POLLS * POLL_INTERVAL}s")
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/run_video_gen_batch.py <ai_prompts.json> [--priority critical|high|medium|all]")
        sys.exit(1)

    prompts_file = Path(sys.argv[1])
    if not prompts_file.exists():
        print(f"File not found: {prompts_file}")
        sys.exit(1)

    priority_filter = "all"
    if "--priority" in sys.argv:
        idx = sys.argv.index("--priority")
        priority_filter = sys.argv[idx + 1]

    scenes = json.loads(prompts_file.read_text())

    if priority_filter != "all":
        scenes = [s for s in scenes if s.get("priority") == priority_filter]

    print(f"\n=== AI Video Batch Generator ===")
    print(f"Scenes to generate: {len(scenes)} (filter: {priority_filter})")
    print()

    success, failed = 0, []
    for scene in scenes:
        ok = generate_video(scene)
        if ok:
            success += 1
        else:
            failed.append(scene["scene_id"])

    print(f"\n=== Done ===")
    print(f"Generated: {success}/{len(scenes)}")
    if failed:
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
