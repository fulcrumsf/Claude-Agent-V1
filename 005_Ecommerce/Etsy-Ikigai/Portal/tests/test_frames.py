"""Frame chooser (app/frames.py + config/frame_styles.json): tasteful, rule-based, explainable, deterministic."""
from app import frames

BOOK_CLUB_IDEA = ("Cat curled on an open book under a reading lamp: book-club cat print",
                  "A ginger or tabby cat asleep across an open book beside a mug and a stack of books under a warm "
                  "lamp, in faceted impasto or mid-century gouache. For readers and book-club members, and as a "
                  "gift for the friend who reads in a cozy corner.")
LIGHT_WARM = {"value_key": "light", "accents": [{"name": "tomato red"}, {"name": "warm walnut brown"}]}
DARK = {"value_key": "dark", "accents": [{"name": "deep plum"}, {"name": "ochre"}]}


def _set(idea_text, analysis, card_text=None, profile_text=None, size=3):
    src = {"idea": idea_text}
    if card_text:
        src["card"] = card_text
    if profile_text:
        src["profile"] = profile_text
    tags, _ = frames.detect_tags(src)
    return tags, frames.choose_set(tags, analysis, size)


def test_book_club_cat_gets_wood_and_white_with_a_mat_never_ornate():
    tags, out = _set(" ".join(BOOK_CLUB_IDEA), LIGHT_WARM,
                     card_text="Palette Knife Planes. Heavy impasto, geometric colour blocking. Moonlit Storybook: "
                               "storybook painting in matte gouache, aged layered-print quality, sharp graphic silhouettes.",
                     profile_text="Contemporary modernist figurative abstraction with mid-century influences. impasto geometric")
    ids = [f["id"] for f in out["frames"]]
    assert ids[0] in ("oak", "walnut") and set(ids) <= {"oak", "walnut", "white"} and len(ids) == 3
    assert not {"gold_ornate", "carved_dark"} & set(ids)
    assert any(f["mat"] for f in out["frames"]) and not all(f["mat"] for f in out["frames"])
    assert all(f["reasons"] for f in out["frames"])                      # explainable
    gold = next(r for r in out["rejected"] if r["id"] == "gold_ornate")
    assert gold["why"].startswith("vetoed")


def test_book_club_cat_through_the_real_cards_and_profiles():
    r = frames.frames_for_print(*BOOK_CLUB_IDEA, LIGHT_WARM, ["moonlit_storybook", "palette_knife"])
    ids = [f["id"] for f in r["frames"]]
    assert ids[:2] == ["oak", "walnut"] and "gold_ornate" not in ids
    assert "impasto" in r["tags"] and r["evidence"]["impasto"]


def test_gothic_oil_art_gets_an_ornate_frame():
    tags, out = _set("Raven on a skull: gothic vintage oil painting, dark moody still life", DARK)
    ids = [f["id"] for f in out["frames"]]
    assert ids[0] in ("gold_ornate", "carved_dark")
    assert len({f["family"] for f in out["frames"]}) == len(ids)          # distinct families in a set
    assert "white" not in ids                                             # white clashes with dark moody


def test_ornate_is_vetoed_for_modern_graphic_minimal_and_kids():
    for text in ("Bold geometric pop art poster with flat shapes", "Minimalist single line art face",
                 "Kids nursery print: cute bunny for a baby's room"):
        tags, out = _set(text, LIGHT_WARM)
        ranked = frames.score_frames(tags, LIGHT_WARM)
        for f in ranked:
            if f["id"] in ("gold_ornate", "carved_dark"):
                assert f["vetoed"], text
        assert not {"gold_ornate", "carved_dark"} & {f["id"] for f in out["frames"]}


def test_a_weak_vintage_mention_does_not_unlock_ornate():
    tags, _ = frames.detect_tags({"idea": "A cat on a cushion", "card": "aged print texture"})
    assert 0.5 <= tags["vintage"] < frames.REQUIRE_MIN
    gold = next(f for f in frames.score_frames(tags) if f["id"] == "gold_ornate")
    assert gold["vetoed"] and "needs" in gold["vetoed"]


def test_thin_black_is_not_the_default():
    for text in ("Botanical fern print in soft gouache", "A cozy cat reading a book", "Japandi ink wash branch"):
        tags, out = _set(text, LIGHT_WARM)
        assert out["frames"][0]["id"] != "black", text
    tags, out = _set("Bold graphic typographic poster, screenprint colour blocking", LIGHT_WARM)
    assert "black" in [f["id"] for f in out["frames"]]                   # still offered where it fits


def test_mats_on_some_not_all_and_deterministic():
    a = _set("Botanical tulip print, minimalist gouache", LIGHT_WARM)[1]
    b = _set("Botanical tulip print, minimalist gouache", LIGHT_WARM)[1]
    assert a == b
    n = sum(f["mat"] for f in a["frames"])
    assert 1 <= n <= 2 and n < len(a["frames"])


def test_tag_detection_is_word_bounded():
    tags, ev = frames.detect_tags({"idea": "A popular poppy field"})          # 'pop' must not fire on these
    assert "pop" not in tags
