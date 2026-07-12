import json
import subprocess
from pathlib import Path

from normalize_loudness import build_normalize_filter, measure_loudness, normalize_audio


def make_tone(path: Path, db: float, duration: float = 3.0):
    subprocess.run(
        ["ffmpeg", "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}",
         "-af", f"volume={db}dB", "-ar", "44100", str(path), "-y"],
        capture_output=True, check=True,
    )


def test_build_normalize_filter_includes_measured_values():
    measured = {
        "input_i": "-34.90", "input_tp": "-16.80", "input_lra": "2.60",
        "input_thresh": "-45.09", "target_offset": "0.43",
    }
    filt = build_normalize_filter(measured, target_i=-14.0, target_tp=-1.5, target_lra=7.0)
    assert "measured_I=-34.90" in filt
    assert "measured_TP=-16.80" in filt
    assert "measured_LRA=2.60" in filt
    assert "measured_thresh=-45.09" in filt
    assert "offset=0.43" in filt
    assert "I=-14.0" in filt
    assert "TP=-1.5" in filt
    assert "LRA=7.0" in filt
    assert "linear=true" in filt


def test_measure_loudness_returns_real_measurements(tmp_path):
    quiet = tmp_path / "quiet.wav"
    make_tone(quiet, db=-30)
    measured = measure_loudness(quiet)
    assert "input_i" in measured
    # A -30dB sine tone should measure well below the -14 LUFS target
    assert float(measured["input_i"]) < -20


def test_normalize_audio_brings_quiet_tone_closer_to_target(tmp_path):
    quiet = tmp_path / "quiet.wav"
    normalized = tmp_path / "normalized.wav"
    make_tone(quiet, db=-30)

    before = measure_loudness(quiet)
    normalize_audio(quiet, normalized, target_i=-14.0, target_tp=-1.5, target_lra=7.0)
    assert normalized.exists()

    after = measure_loudness(normalized)
    target = -14.0
    before_distance = abs(float(before["input_i"]) - target)
    after_distance = abs(float(after["input_i"]) - target)
    assert after_distance < before_distance
    # Should land close to the target, not just "somewhat closer"
    assert after_distance < 2.0


def test_normalize_audio_does_not_exceed_true_peak_ceiling(tmp_path):
    loud = tmp_path / "loud.wav"
    normalized = tmp_path / "normalized_loud.wav"
    make_tone(loud, db=-3)

    normalize_audio(loud, normalized, target_i=-14.0, target_tp=-1.5, target_lra=7.0)
    after = measure_loudness(normalized)
    # true peak must stay at or below the ceiling (small tolerance for measurement variance)
    assert float(after["input_tp"]) <= -1.5 + 0.5
