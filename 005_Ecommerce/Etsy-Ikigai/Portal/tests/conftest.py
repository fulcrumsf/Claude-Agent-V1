"""Shared test fakes. SAM 2 runs in its own venv (torch) and PhotoCraft renders are faked in the tests, so the
template builder's SAM corner detection and the black/white card test are replaced here by stand-ins: the corners
come from the synthetic scene's own drawn insert (legacy detector, test scenes only) and the card test passes.
The SAM geometry itself (alpha refinement, sub-pixel quad fit, coverage) is tested for real in test_sam_frames.py."""
import numpy as np
import pytest
from PIL import Image


def fake_sam_detect(scene_png, work, settings=None, box=None, wall=True, canvas=False, paper=False):
    from app import sam_frames as sf
    from app import scene_templates as stp
    rgb = np.asarray(Image.open(scene_png).convert("RGB"))
    q, info = stp.find_insert(rgb, 2 / 3)
    if q is None:
        raise stp.TemplateError(f"no clean blank frame insert (SAM 2: {info})")
    H, W = rgb.shape[:2]
    return {"corners": np.float32(q).tolist(), "model": "fake-sam", "device": "test"}, sf.poly_coverage(q, W, H), None


@pytest.fixture(autouse=True)
def _no_sam_no_cards(monkeypatch):
    from app import scene_templates as stp
    monkeypatch.setattr(stp, "sam_detect", fake_sam_detect)
    monkeypatch.setattr(stp, "card_verify", lambda psd, quad, settings=None, work=None, opening=None: {"max_px": 0.0, "faked": True})


@pytest.fixture(autouse=True)
def _checker_without_sam(monkeypatch):
    """The checker tests use synthetic renders; their opening comes from the old edge search (SAM is the subprocess)."""
    from app import template_checker as tc
    monkeypatch.setattr(tc, "sam_opening", lambda bg_png, V, settings=None, work=None, psd=None, canvas=False: (None, "test", None))


@pytest.fixture(autouse=True)
def _no_scene_scan_no_balance(monkeypatch):
    """Realism addendum: the output scan (Vision OCR + Gemini) and the kie.ai balance read are network / OS tools;
    run_slot gets a clean scan and an unknown balance unless a test swaps them in."""
    from app import production, scene_templates as stp
    monkeypatch.setattr(production, "scan_scene", lambda png, settings=None, overlay=None:
                        {"pass": True, "severity": "none", "findings": [], "overlay": None, "mode": "test",
                         "notes": []})
    monkeypatch.setattr(stp, "kie_balance", lambda settings=None: None)


@pytest.fixture(autouse=True)
def _engine_status_in_tmp(monkeypatch, tmp_path_factory):
    """Controls addendum: data/engine_status.json (measured costs, room gates) is written by code; tests never touch
    the real one."""
    from app import engines
    monkeypatch.setattr(engines, "STATUS_PATH", tmp_path_factory.mktemp("engine_status") / "engine_status.json")
