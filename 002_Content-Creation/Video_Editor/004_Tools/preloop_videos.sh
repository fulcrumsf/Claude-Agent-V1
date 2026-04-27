#!/usr/bin/env bash
# Pre-loops AI video clips to match their narration audio durations.
# Output: scene_XX/video_looped.mp4 — ready for Remotion single-video playback.
# Uses -stream_loop + re-encode so keyframes are clean and seeking works perfectly.

set -e
BASE="002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon"

declare -A DURATIONS=(
  ["scene_01"]="14.0"
  ["scene_03"]="19.8"
  ["scene_04"]="21.2"
  ["scene_05"]="40.2"
  ["scene_06"]="36.7"
  ["scene_07"]="53.4"
  ["scene_08"]="54.8"
  ["scene_09"]="48.2"
  ["scene_10a"]="16.4"   # ≈ 49.1 / 3
  ["scene_10b"]="16.4"
  ["scene_10c"]="16.3"   # remainder
  ["scene_11"]="67.7"
)

echo "=== Pre-looping video clips ==="
echo ""

for scene in "${!DURATIONS[@]}"; do
  dur="${DURATIONS[$scene]}"
  input="$BASE/$scene/video.mp4"
  output="$BASE/$scene/video_looped.mp4"

  if [ ! -f "$input" ]; then
    echo "  ✗ $scene — source not found, skipping"
    continue
  fi

  if [ -f "$output" ]; then
    # Check if existing looped file is correct duration
    existing_dur=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$output" 2>/dev/null)
    existing_rounded=$(printf "%.0f" "$existing_dur" 2>/dev/null || echo "0")
    target_rounded=$(printf "%.0f" "$dur" 2>/dev/null || echo "1")
    if [ "$existing_rounded" -ge "$target_rounded" ] 2>/dev/null; then
      echo "  ✓ $scene — already looped (${existing_rounded}s)"
      continue
    fi
  fi

  # Calculate loops needed: ceil(duration / 8)
  loops=$(python3 -c "import math; print(math.ceil($dur / 8))")

  echo "  → $scene: looping to ${dur}s (${loops}x of 8s clip)..."
  ffmpeg -y \
    -stream_loop "$loops" \
    -i "$input" \
    -t "$dur" \
    -c:v libx264 \
    -preset fast \
    -crf 18 \
    -an \
    "$output" \
    -loglevel error

  actual=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$output" 2>/dev/null)
  actual_rounded=$(printf "%.1f" "$actual")
  size=$(du -k "$output" | cut -f1)
  echo "  ✓ $scene — ${actual_rounded}s, ${size}KB"
done

echo ""
echo "=== All clips pre-looped ==="
