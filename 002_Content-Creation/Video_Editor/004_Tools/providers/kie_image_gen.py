import os
import sys
import time
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

def generate_image(prompt, output_file, model="nano-banana-2"):
    HOME_SECRETS = Path.home() / ".env-secrets"
    load_dotenv(HOME_SECRETS)
    KEY = os.getenv('KIE_API_KEY')
    if not KEY:
        print("Error: KIE_API_KEY not found in references/.env")
        sys.exit(1)
        
    headers = {
        'Authorization': f'Bearer {KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
       "model": model,
       "input": {
          "prompt": prompt,
          "aspect_ratio": "16:9",
          "resolution": "4K",
          "output_format": "png"
       }
    }
    
    print(f"Requesting image generation from {model}...")
    try:
        response = requests.post("https://api.kie.ai/api/v1/jobs/createTask", headers=headers, json=payload, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to submit task: {e}")
        if 'response' in locals(): print(response.text)
        sys.exit(1)
        
    data = response.json()
    task_id = data.get("taskId") or data.get("data", {}).get("taskId")
    if not task_id:
        print(f"Failed to extract taskId. Response: {data}")
        sys.exit(1)
        
    print(f"Polling task ID {task_id} with exponential backoff...", flush=True)
    status_url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}"
    
    attempts = 0
    poll_interval = 5
    
    while True:
        try:
            status_resp = requests.get(status_url, headers=headers, timeout=15)
            status_json = status_resp.json()
            data_block = status_json.get("data", {})
            state = data_block.get("state")
            flag = data_block.get("successFlag") 
            
            if state == "success" or flag == 1:
                result_str = data_block.get("resultJson", "{}")
                try:
                    result_obj = json.loads(result_str)
                    urls = result_obj.get("resultUrls", [])
                    img_url = urls[0] if urls else result_obj.get("url")
                except:
                    img_url = data_block.get("url")
                
                if not img_url:
                    img_url = data_block.get("url")
                
                if not img_url:
                    print(f"Task completed but no URL found! Data: {data_block}")
                    sys.exit(1)
                    
                print(f"Generation complete! Downloading from {img_url}...")
                r = requests.get(img_url, stream=True)
                if r.status_code == 200:
                    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
                    with open(output_file, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Saved {output_file}")
                    sys.exit(0)
                else:
                    print("Failed to download image file.")
                    sys.exit(1)
                    
            elif state == "fail" or flag in [2, 3]:
                print(f"Generation failed: {data_block}")
                sys.exit(1)
                
            else:
                print(f"State: {state} or flag: {flag}... sleeping {poll_interval}s", flush=True)
                
        except Exception as e:
            print(f"Polling warning: {e}", flush=True)
            
        time.sleep(poll_interval)
        attempts += 1
        if attempts % 3 == 0 and poll_interval < 20:
            poll_interval += 5

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python kie_image_gen.py <prompt> <output_file> [model]")
        sys.exit(1)
        
    prompt = sys.argv[1]
    output_file = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "nano-banana-2"
    generate_image(prompt, output_file, model)
