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
# Usage:
#   bash 004_Tools/pipeline_orchestrator.sh
#   bash 004_Tools/pipeline_orchestrator.sh 2>&1 | tee /tmp/biolum_pipeline.log

set -e

PROMPTS="002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon/new_clips_prompts.json"
DONE_FILE="/tmp/biolum_pipeline_done.txt"
LOG="/tmp/biolum_pipeline.log"

echo "========================================"
echo " BIOLUMINESCENCE v4 PIPELINE"
echo " Started: $(date)"
echo "========================================"
echo ""

# ── Stage 1: High priority video generation ───────────────────────────────────
echo "── STAGE 1: High priority video gen ──"
python3 -u 004_Tools/run_new_clips_batch.py "$PROMPTS" --priority high --type video
echo ""

# ── Stage 2: Preloop clips that arrived ───────────────────────────────────────
echo "── STAGE 2: Preloop high-priority clips ──"
python3 -u 004_Tools/preloop_new_clips.py 002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon/
echo ""

# ── Stage 3: Medium priority video generation ─────────────────────────────────
echo "── STAGE 3: Medium priority video gen ──"
python3 -u 004_Tools/run_new_clips_batch.py "$PROMPTS" --priority medium --type video
echo ""

# ── Stage 4: Preloop all new clips ────────────────────────────────────────────
echo "── STAGE 4: Preloop all new clips ──"
python3 -u 004_Tools/preloop_new_clips.py 002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon/
echo ""

# ── Stage 5: Preloop original clips (idempotent) ──────────────────────────────
echo "── STAGE 5: Preloop original clips ──"
bash 004_Tools/preloop_videos.sh
echo ""

# ── Stage 6: Status check ─────────────────────────────────────────────────────
echo "── STAGE 6: Final status ──"
python3 tools/check_pipeline_status.py
echo ""

# ── Done ──────────────────────────────────────────────────────────────────────
echo "========================================"
echo " PIPELINE COMPLETE: $(date)"
echo "========================================"
echo "PIPELINE_COMPLETE at $(date)" > "$DONE_FILE"
