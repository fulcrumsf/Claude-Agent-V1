#!/usr/bin/env bash
# Render the Anomalous Wild Bioluminescence Weapon documentary via Remotion
# Usage: bash 004_Tools/render_bioluminescence.sh [--preview]
#
# Prerequisites:
#   - All scene_XX/video.mp4 files present (run_video_gen_batch.py + fetch_cc0_footage.py)
#   - All scene_XX/audio.mp3 files present (run_tts_batch.py)
#   - The symlink 003_Remotion/public/bioluminescence_weapon → 002_Channels/.../bioluminescence_weapon

set -e

VIDEO_DIR="002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon"
REMOTION_DIR="003_Remotion"
OUTPUT_FILE="002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon/final_render.mp4"

echo "=== Bioluminescence Weapon — Render Check ==="
echo ""

# Check all required video files
MISSING_VIDEO=()
for scene in scene_01 scene_03 scene_04 scene_05 scene_06 scene_07 scene_08 scene_09 scene_10a scene_10b scene_10c scene_11; do
  if [ ! -f "$VIDEO_DIR/$scene/video.mp4" ]; then
    MISSING_VIDEO+=("$scene")
  fi
done

# Check all required audio files
MISSING_AUDIO=()
for scene in scene_01 scene_03 scene_04 scene_05 scene_06 scene_07 scene_08 scene_09 scene_10a scene_11 scene_12; do
  if [ ! -f "$VIDEO_DIR/$scene/audio.mp3" ]; then
    MISSING_AUDIO+=("$scene")
  fi
done

if [ ${#MISSING_VIDEO[@]} -gt 0 ]; then
  echo "⚠ Missing video files:"
  for s in "${MISSING_VIDEO[@]}"; do echo "  - $s/video.mp4"; done
  echo ""
  echo "Run: python3 004_Tools/run_video_gen_batch.py $VIDEO_DIR/ai_prompts.json --priority all"
  echo ""
fi

if [ ${#MISSING_AUDIO[@]} -gt 0 ]; then
  echo "⚠ Missing audio files:"
  for s in "${MISSING_AUDIO[@]}"; do echo "  - $s/audio.mp3"; done
  echo ""
  echo "Run: python3 004_Tools/run_tts_batch.py $VIDEO_DIR/narration_tts.json"
  echo ""
fi

if [ ${#MISSING_VIDEO[@]} -gt 0 ] || [ ${#MISSING_AUDIO[@]} -gt 0 ]; then
  echo "Complete the above steps before rendering."
  exit 1
fi

echo "✓ All required assets present."
echo ""

# Verify symlink
if [ ! -L "$REMOTION_DIR/public/bioluminescence_weapon" ]; then
  echo "Creating public symlink..."
  cd "$REMOTION_DIR/public" && ln -sf "../../002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon" bioluminescence_weapon && cd ../..
fi

# Preview mode
if [ "$1" = "--preview" ]; then
  echo "Starting Remotion Studio for preview..."
  cd "$REMOTION_DIR" && npm run remotion -- studio
  exit 0
fi

# Full render
echo "Rendering BioluminescenceDoc (390s @ 30fps = 11700 frames)..."
echo "Output: $OUTPUT_FILE"
echo ""
mkdir -p "$(dirname "$OUTPUT_FILE")"

cd "$REMOTION_DIR" && npx remotion render BioluminescenceDoc "../$OUTPUT_FILE" \
  --codec h264 \
  --crf 18 \
  --fps-override 30

echo ""
echo "=== Render Complete ==="
echo "Output: $OUTPUT_FILE"
ls -lh "../$OUTPUT_FILE" 2>/dev/null || true
