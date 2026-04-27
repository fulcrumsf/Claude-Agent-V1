"""
Batch TTS runner — reads narration_tts.json, generates ElevenLabs audio for each scene.
Usage: python3 004_Tools/run_tts_batch.py 002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon/narration_tts.json
"""
import os
import sys
import json
import requests
from pathlib import Path

# Load env from centralized secrets
from dotenv import load_dotenv
HOME_SECRETS = Path.home() / ".env-secrets"
load_dotenv(HOME_SECRETS)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

def generate_scene_audio(scene: dict, voice_id: str, model_id: str, voice_settings: dict) -> bool:
    output_path = Path(scene["output_file"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        print(f"  ✓ Already exists, skipping: {output_path.name}")
        return True

    text = scene["text"].strip()
    if not text:
        print(f"  ⚠ No narration text for {scene['scene_id']}, skipping.")
        return True

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": voice_settings,
    }

    print(f"  → Generating: {scene['scene_id']} ({len(text.split())} words)...")
    resp = requests.post(url, json=payload, headers=headers, timeout=60)

    if not resp.ok:
        print(f"  ✗ ElevenLabs error {resp.status_code}: {resp.text[:200]}")
        return False

    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    size_kb = output_path.stat().st_size // 1024
    print(f"  ✓ Saved: {output_path} ({size_kb} KB)")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/run_tts_batch.py <path/to/narration_tts.json>")
        sys.exit(1)

    tts_file = Path(sys.argv[1])
    if not tts_file.exists():
        print(f"File not found: {tts_file}")
        sys.exit(1)

    config = json.loads(tts_file.read_text())
    voice_id = config["voice_id"]
    model_id = config["model_id"]
    voice_settings = config["voice_settings"]
    scenes = config["scenes"]

    print(f"\n=== TTS Batch Runner ===")
    print(f"Voice:  {voice_id}")
    print(f"Model:  {model_id}")
    print(f"Scenes: {len(scenes)}")
    print()

    success = 0
    failed = []

    for scene in scenes:
        ok = generate_scene_audio(scene, voice_id, model_id, voice_settings)
        if ok:
            success += 1
        else:
            failed.append(scene["scene_id"])

    print(f"\n=== Done ===")
    print(f"Generated: {success}/{len(scenes)}")
    if failed:
        print(f"Failed:    {failed}")


if __name__ == "__main__":
    main()
