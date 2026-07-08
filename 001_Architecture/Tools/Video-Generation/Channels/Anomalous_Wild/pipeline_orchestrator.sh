#!/usr/bin/env bash
# Full generation + preloop pipeline for bioluminescence_weapon v4.
# Runs sequentially to keep M3 Max load manageable.
#
# Stages:
#   1. High priority video gen (Veo3 + Kling)
#   2. Preloop high-priority clips that arrived
#   3. Medium priority video gen (Kling)
#   4. Preloop medium-priority clips
#   5. Preloop original clips (ensures all video_looped.mp4 are fresh)
#   6. Write done signal
#
# Usage (run from anywhere — all paths below are absolute):
#   bash pipeline_orchestrator.sh
#   bash pipeline_orchestrator.sh 2>&1 | tee /tmp/biolum_pipeline.log

set -e

AGENT_OS="/Users/tonymacbook2025/Documents/Agent-OS"
GENERIC_TOOLS="$AGENT_OS/001_Architecture/Tools/Video-Generation/Generic_Tools"
CHANNEL_TOOLS="$AGENT_OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild"
PROD_DIR="$AGENT_OS/002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/0001_Bioluminescence_Weapon"

PROMPTS="$PROD_DIR/Production/new_clips_prompts.json"
DONE_FILE="/tmp/biolum_pipeline_done.txt"
LOG="/tmp/biolum_pipeline.log"

echo "========================================"
echo " BIOLUMINESCENCE v4 PIPELINE"
echo " Started: $(date)"
echo "========================================"
echo ""

# ── Stage 1: High priority video generation ───────────────────────────────────
echo "── STAGE 1: High priority video gen ──"
python3 -u "$GENERIC_TOOLS/run_new_clips_batch.py" "$PROMPTS" --priority high --type video
echo ""

# ── Stage 2: Preloop clips that arrived ───────────────────────────────────────
echo "── STAGE 2: Preloop high-priority clips ──"
python3 -u "$GENERIC_TOOLS/preloop_new_clips.py" "$PROD_DIR/"
echo ""

# ── Stage 3: Medium priority video generation ─────────────────────────────────
echo "── STAGE 3: Medium priority video gen ──"
python3 -u "$GENERIC_TOOLS/run_new_clips_batch.py" "$PROMPTS" --priority medium --type video
echo ""

# ── Stage 4: Preloop all new clips ────────────────────────────────────────────
echo "── STAGE 4: Preloop all new clips ──"
python3 -u "$GENERIC_TOOLS/preloop_new_clips.py" "$PROD_DIR/"
echo ""

# ── Stage 5: Preloop original clips (idempotent) ──────────────────────────────
echo "── STAGE 5: Preloop original clips ──"
bash "$CHANNEL_TOOLS/preloop_videos.sh"
echo ""

# ── Stage 6: Status check ─────────────────────────────────────────────────────
echo "── STAGE 6: Final status ──"
python3 "$CHANNEL_TOOLS/check_pipeline_status.py"
echo ""

# ── Done ──────────────────────────────────────────────────────────────────────
echo "========================================"
echo " PIPELINE COMPLETE: $(date)"
echo "========================================"
echo "PIPELINE_COMPLETE at $(date)" > "$DONE_FILE"
