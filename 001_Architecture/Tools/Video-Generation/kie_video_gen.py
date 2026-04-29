import requests
import time
from config import KIE_API_KEY

def generate_video(prompt, output_filename="scene_video.mp4", model="google/veo-3.1", duration=5, aspect_ratio="16:9"):
    """Hits KIE.ai unified API to generate a video and polls until complete."""
    if not KIE_API_KEY:
        raise ValueError("KIE_API_KEY is missing from .env")

    # Map the generic slugs to Veo3 exact model name
    actual_model = "veo3_fast" if "veo" in model.lower() else model

    url = "https://api.kie.ai/api/v1/veo/generate"
    headers = {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": actual_model,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "generationType": "TEXT_2_VIDEO"
    }
    
    print(f"Queueing KIE video task for: '{prompt[:40]}...'")
    response = requests.post(url, headers=headers, json=payload)
    if not response.ok:
        raise Exception(f"Failed to create task: {response.text}")
        
    data = response.json()
    task_id = data.get("taskId") or data.get("data", {}).get("taskId")
    if not task_id:
        raise Exception(f"Failed to extract taskId. Response: {data}")
        
    status_url = f"https://api.kie.ai/api/v1/veo/record-info?taskId={task_id}"
    print(f"Polling task ID {task_id} with exponential backoff...", flush=True)
    
    attempts = 0
    poll_interval = 20
    
    while True:
        try:
            status_resp = requests.get(status_url, headers=headers, timeout=15).json()
            data_block = status_resp.get("data") or {}
            flag = data_block.get("successFlag")
            
            if flag == 1:
                urls = data_block.get("response", {}).get("resultUrls", [])
                vid_url = urls[0] if urls else data_block.get("url")
                print(f"Generation complete! Downloading from {vid_url}...")
                download(vid_url, output_filename)
                break
            elif flag in [2, 3]:
                raise Exception(f"Video generation failed: {status_resp}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed/timed out: {e}. Passing and will retry...")
            flag = 0
            
        print(f"Flag: {flag}... sleeping {poll_interval}s", flush=True)
        time.sleep(poll_interval)
        attempts += 1
        if attempts > 3:
            poll_interval = 30 # Back off to 30s
            
    return output_filename
    
def download(url, filename):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Saved {filename}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate a video via KIE.ai")
    parser.add_argument("prompt", help="Text prompt for video generation")
    parser.add_argument("output", nargs="?", default="output.mp4", help="Output filename")
    parser.add_argument("model", nargs="?", default="google/veo-3.1", help="Model slug")
    parser.add_argument("--aspect_ratio", default="16:9", help="Aspect ratio (e.g. 16:9 or 9:16)")
    args = parser.parse_args()
    generate_video(args.prompt, args.output, args.model, aspect_ratio=args.aspect_ratio)
