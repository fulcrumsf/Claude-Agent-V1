"""Golden locks for the realism addendum (Pipeline_Docs/Slot_Set_Planner_Realism_Addendum.md 8.1.1), written BEFORE
any behaviour changed: every brief saved before the addendum (no "pv" key = pv1) must assemble byte-identically, and
the saved slot 16 / 19 templates of Book Club Cat must replay their sent prompt exactly."""
import hashlib
import json
from pathlib import Path

import pytest

from app import slot_planner as sp
from test_slot_planner import brief

LIB = Path(__file__).resolve().parents[2] / "Room_Templates" / "Portrait_Templates"

# sha1 of the prompt each saved template.json recorded (= what kie.ai received)
SAVED = {"AI_Kids_Kids_20261120_122955": "9e3524ac6c52cc59ac869380145d6244314cd8fb",          # slot 16, rev 1
         "AI_Nursery_Kids_20261120_134709": "0b34908953695437448ca29ceea2aebd264a59fa"}        # slot 19, rev 6

# pv1 fixture prompts (test_slot_planner.brief) per presentation x wall (orange / blue marker), locked 2026-11-20
PV1 = {
    ('frame', '#F2EEE6'): "c50507429131d4b9505c22a54d06484a60fd106e",
    ('frame', '#8C3A1E'): "f57fe6da314c3c16ded73f852c5a18591835b522",
    ('mat', '#F2EEE6'): "6287316434042d4df80c939c2a98eaa42510f006",
    ('mat', '#8C3A1E'): "846ffb8869e200c54fc9662c36b69e420bc5df10",
    ('canvas', '#F2EEE6'): "229bbd9a3f7ed083db4e7b360f78fcc04883733a",
    ('canvas', '#8C3A1E'): "5f047235da7f9e77eb9397249654cfe65691443a",
    ('canvas_bare', '#F2EEE6'): "2cd21de72344abeaa3f91c549c0e0e6cc73529a8",
    ('canvas_bare', '#8C3A1E'): "9e81b1dde4618ee74e15a93dbf1204cb95953054",
}
PV1_NORMALISED = "b947a45c126d79ba7326815f14b4dd5f27ddfef5"


def _sha(t):
    return hashlib.sha1(t.encode()).hexdigest()


def _pv1(pres, hx):
    fin = {"frame": "walnut_frame", "mat": "black_frame", "canvas": "natural_wood_floater", "canvas_bare": "none"}[pres]
    kw = dict(presentation=pres, frame_finish=fin, wall={"name": "w", "hex": hx, "treatment": "limewash"})
    if pres.startswith("canvas"):
        kw.update(print_size="12x16", shot="medium", setting="dresser_top", display="lean_on_surface",
                  camera_height="counter", props=["a cup"])
    if hx != "#F2EEE6" and pres in ("frame", "mat"):
        kw["frame_finish"] = "white_frame"
    return brief(**kw)


@pytest.mark.parametrize("key", sorted(PV1))
def test_pv1_briefs_assemble_byte_identically(key):
    b = _pv1(*key)
    assert b["lint"]["pass"], b["lint"]["why"]
    assert "pv" not in b
    assert _sha(sp.assemble(b)) == PV1[key]


def test_pv1_normalise_output_is_unchanged():
    assert hashlib.sha1(json.dumps(brief(), sort_keys=True).encode()).hexdigest() == PV1_NORMALISED


@pytest.mark.parametrize("name", sorted(SAVED))
def test_saved_slot_16_and_19_templates_replay_their_prompt(name):
    hits = list(LIB.rglob(f"{name}/template.json")) if LIB.is_dir() else []
    if not hits:
        pytest.skip("Room_Templates library not present")
    man = json.loads(hits[0].read_text())
    assert _sha(man["prompt"]) == SAVED[name]
    assert _sha(sp.assemble(man["brief"])) == SAVED[name]
