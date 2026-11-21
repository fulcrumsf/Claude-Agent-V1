"""Controls addendum B + C (tests B.4, C.6): the reference-share maths and enforcement, the tag sentence, the four
closeness bands, image prep, the clauses, registers_ok and the A/B variant planning. Pure functions and canned planner
replies: no model, no credits."""
import hashlib
import json

import numpy as np
import pytest
from PIL import Image

from app import references as R, slot_planner as sp
from test_slot_planner_realism import b2, ref_entry


# ---------- B.1 share maths ----------

@pytest.mark.parametrize("n_open,want", [(1, 1), (2, 2), (3, 2), (4, 3), (5, 4), (8, 6)])
def test_share_80_rounds_half_up(n_open, want):
    assert sp.n_image(80, n_open) == want


def test_share_edges_and_clamps():
    assert sp.n_image(0, 5) == 0 and sp.n_image(100, 5) == 5
    assert sp.n_image(80, 5, n_capable=2) == 2                 # only 2 slots on an engine that takes a photo
    assert sp.n_image(80, 5, n_refs=1) == 1                    # only 1 usable image-capable reference


def _brief(slot, **kw):
    b = b2(slot=slot, **kw)
    b["source"] = "new"
    return b


def test_enforce_share_swaps_by_need_score_and_text_only_engines_are_tags():
    refs = [ref_entry("0024"), ref_entry("0025"), ref_entry("0026", light="blind_stripes")]
    bs = {9: _brief(9, reference="0024"), 10: _brief(10, reference="0025"),
          11: _brief(11, reference="0026", light_type="blind_stripes",
                     window={"covering": "venetian_blind", "view": "street"})}
    for b in bs.values():
        b["reference"] = {9: "0024", 10: "0025", 11: "0026"}[b["slot"]]
    notes = sp.enforce_share(bs, 1, {9: True, 10: True, 11: True}, refs)
    assert [s for s, b in sorted(bs.items()) if b["reference_mode"] == "image"] == [11]       # blind stripes needs it
    assert all(bs[s]["ref_tag_text"] for s in (9, 10)) and notes
    bs2 = {9: _brief(9), 10: _brief(10)}
    bs2[10]["reference"] = "0025"
    sp.enforce_share(bs2, 2, {9: True, 10: False}, refs)
    assert bs2[9]["reference_mode"] == "image" and bs2[10]["reference_mode"] == "tags"        # text-only engine


def test_tags_brief_prompt_has_no_image_clause_and_has_the_tag_sentence():
    b = _brief(9)
    sp.enforce_share({9: b}, 0, {9: True}, [ref_entry()])
    p = sp.assemble(b)
    assert "Image 1" not in p and b["ref_tag_text"] in p
    assert b["ref_tag_text"].startswith("Photographed like a careful phone photo from eye level with a normal lens")
    assert "in flat overcast light" in b["ref_tag_text"]


def test_a_no_art_reference_is_an_image_only_below_50():
    refs = [dict(ref_entry(), has_art=False)]
    b = _brief(9)
    sp.enforce_share({9: b}, 1, {9: True}, refs, closeness=60)
    assert b["reference_mode"] == "tags"
    b = _brief(9)
    sp.enforce_share({9: b}, 1, {9: True}, refs, closeness=30)
    assert b["reference_mode"] == "image"


# ---------- C bands, clauses, derivation ----------

@pytest.mark.parametrize("v,band", [(0, "essence"), (24, "essence"), (25, "loose"), (49, "loose"), (50, "balanced"),
                                    (79, "balanced"), (80, "close"), (100, "close")])
def test_band_edges(v, band):
    assert sp.band_of(v) == band


def test_balanced_is_the_realism_prompt_close_and_loose_have_their_wording():
    base = b2()
    bal = b2()
    bal.update(ref_band="balanced", ref_closeness=60, reference_mode="image")
    assert sp.assemble(bal) == sp.assemble(base)                                   # default 60 = byte-identical
    close = dict(base, ref_band="close")
    assert "do not copy individual objects" in sp.assemble(close)
    loose = dict(base, ref_band="loose")
    assert "Choose a new composition" in sp.assemble(loose) and sp.REF_CLAUSE not in sp.assemble(loose)


def test_essence_derives_only_the_takeaway_fields():
    raw_camera = dict(camera_side="right", camera_height="counter")
    b = b2(**raw_camera)
    assert b["camera_side"] == "left"                              # balanced: from the reference
    e = b2(**raw_camera)
    e.update(ref_band="essence", ref_takeaways=["light", "mood"], camera_side="right", camera_height="counter")
    sp.apply_reference(e, ref_entry())
    assert e["camera_side"] == "right" and e["camera_height"] == "counter" and e["ref_use"] == ["light", "mood"]
    assert "Take from it only the quality of its light and its mood" in sp.assemble(e)
    c = dict(e, ref_takeaways=["camera"], camera_side="right")
    sp.apply_reference(c, ref_entry())
    assert c["camera_side"] == "left"


def test_loose_bands_accept_any_display_group():
    b = b2()
    e = ref_entry(display="floor")
    assert not sp.ref_fits(e, b)
    assert sp.ref_fits(e, dict(b, ref_band="loose")) and sp.ref_fits(e, dict(b, ref_band="essence"))


# ---------- C.2 image prep ----------

def _board(tmp_path):
    d = tmp_path / "refs"
    d.mkdir()
    Image.new("RGB", (1200, 900), (180, 170, 160)).save(d / "0901_X.png")
    Image.new("RGB", (1200, 900), (180, 170, 160)).save(d / "0901_X_Blank.png")
    return d, {"source": "0901_X.png", "blank": "0901_X_Blank.png", "marker": "orange", "fill_polygon": [[0, 0]] * 4}


@pytest.mark.parametrize("v,L", [(0, 384), (24, 672), (25, 672), (49, 960)])
def test_prep_sizes_and_blur(tmp_path, v, L):
    d, e = _board(tmp_path)
    s = {"reference_dir": str(d)}
    out = R.prep_for(e, "orange", False, v, tmp_path, s)
    with Image.open(out) as im:
        assert max(im.size) == L
    assert R.prep_size(v)[1] == pytest.approx((50 - v) / 50 * 0.012 * L, abs=1e-3)


@pytest.mark.parametrize("v", [50, 60, 100])
def test_prep_at_50_and_above_sends_the_blank_bytes_unchanged(tmp_path, v):
    d, e = _board(tmp_path)
    out = R.prep_for(e, "orange", False, v, tmp_path, {"reference_dir": str(d)})
    assert out == d / "0901_X_Blank.png"


# ---------- A.4 registers ----------

def test_registers_ok_parsed_and_a_mismatched_reference_is_reassigned():
    got = sp.parse(json.dumps({"briefs": [{"slot": 9}], "registers_ok": ["ordinary_apartment", "small_rental", "bad"]}))
    assert got.registers_ok == ["ordinary_apartment", "small_rental"] and 9 in got
    grand = dict(ref_entry("0024"), tags=dict(ref_entry()["tags"], register="grand_period"))
    flat = dict(ref_entry("0025"), tags=dict(ref_entry()["tags"], register="ordinary_apartment"))
    b = b2()
    b["reference"] = "0024"
    notes = sp.validate_references({16: b}, set(), [grand, flat], registers_ok=["ordinary_apartment"])
    assert b["reference"] == "0025" and "does not fit the home" in notes[0]
    b = b2()
    b["reference"] = "0024"
    sp.validate_references({16: b}, set(), [grand, flat], registers_ok=None)       # no list: all allowed
    assert b["reference"] == "0024"


def test_pv1_briefs_never_get_the_new_keys():
    from test_slot_planner import brief
    b = brief()
    assert not {"reference_mode", "ref_closeness", "ref_band", "ref_takeaways"} & set(b)


def test_planner_prompt_carries_the_share_closeness_and_registers_lines():
    ctx = {"controls": {"share": 80, "closeness": 20, "n_image": 3}, "refs": [ref_entry()]}
    t = sp.controls_text(ctx)
    assert "exactly 3 of the open slots" in t and "20 of 100 (essence)" in t and "registers_ok" in t
    assert sp.controls_text({"controls": None}) == ""
