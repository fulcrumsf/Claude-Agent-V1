#!/bin/bash
export PATH="/Library/Frameworks/Python.framework/Versions/3.13/bin:$PATH"

VAULT="/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault"

echo "Generating Scene 4..."
mkdir -p scene_4
python3 "$VAULT/003_Tools/Video-Generation/kie_video_gen.py" "A specific adult brown echidna with light-tan spines and a dark slim snout, photographed from behind to showcase its bizarre backward-facing hind claws resting on red dirt. Highly detailed." scene_4/video.mp4 google/veo-3.1

echo "Generating Scene 5..."
mkdir -p scene_5
python3 "$VAULT/003_Tools/Text-To-Speech/audio_tts.py" "Even crazier? They don't have a stomach. That's right. Their throat connects straight to their intestines, so they just grind up insects using hard pads at the back of their mouth." scene_5/audio.mp3
python3 "$VAULT/003_Tools/Video-Generation/kie_video_gen.py" "A clean, educational and futuristic bioluminescent scientific diagram showing a simple digestive tract that skips the stomach entirely, formatted like a sleek documentary graphic." scene_5/video.mp4 google/veo-3.1

echo "Generating Scene 6..."
mkdir -p scene_6
python3 "$VAULT/003_Tools/Text-To-Speech/audio_tts.py" "But their ultimate superpower is hidden in their snout. They have electroreceptors that can literally sense the electrical impulses of an ant's heartbeat underground." scene_6/audio.mp3
python3 "$VAULT/003_Tools/Video-Generation/kie_video_gen.py" "A striking cinematic visualization of electrical glowing waves subtly radiating from an echidna's long dark snout as it sniffs the ground in the outback, sensing life beneath the dirt." scene_6/video.mp4 google/veo-3.1

echo "Generating Scene 7..."
mkdir -p scene_7
python3 "$VAULT/003_Tools/Text-To-Speech/audio_tts.py" "They are essentially walking, breathing metal detectors looking for snacks! It is basically a real-life superhero mutation." scene_7/audio.mp3
python3 "$VAULT/003_Tools/Video-Generation/kie_video_gen.py" "A surreal, high-quality 3D render of a futuristic, high-tech metal detector blending organically with an echidna's snout. Clean studio lighting." scene_7/video.mp4 google/veo-3.1

echo "Generating Scene 8..."
mkdir -p scene_8
python3 "$VAULT/003_Tools/Text-To-Speech/audio_tts.py" "It is one of nature's rarest anomalies! If you want to learn more weird facts about our crazy planet, hit that subscribe button, drop a like, and comment what animal we should cover next!" scene_8/audio.mp3
python3 "$VAULT/003_Tools/Video-Generation/kie_video_gen.py" "A specific adult brown echidna with light-tan spines and a dark slim snout, looking directly at the camera, wearing a tiny red \"Subscribe\" bandana around its neck. A YouTube 'Like' thumb icon is subtly propped up next to a rock nearby. 4k, vibrant colors." scene_8/video.mp4 google/veo-3.1

echo "All generation tasks finished!"
