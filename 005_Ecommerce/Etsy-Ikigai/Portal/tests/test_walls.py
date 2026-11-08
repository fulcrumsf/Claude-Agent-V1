from app import walls

LIGHT_WARM = {"value_key": "light", "mean": 0.7, "accents": [{"rgb": [200, 60, 40]}, {"rgb": [110, 70, 40]}]}
DARK_COOL = {"value_key": "dark", "mean": 0.2, "accents": [{"rgb": [60, 90, 150]}]}


def names(a, f="warm_wood"):
    return [p["name"] for p in walls.choose(a, f, n=11)]


def test_book_club_cat_gets_subtle_warm_neutrals_not_purple_pink_or_blue():
    top = names(LIGHT_WARM)[:3]
    assert all(n in ("Warm White", "Oat", "Warm Sand", "Soft Putty", "Greige", "Muted Clay") for n in top)
    assert "Blue Grey" not in top and "Charcoal" not in top and "Deep Olive" not in top
    assert not any("pink" in n.lower() or "mauve" in n.lower() or "purple" in n.lower() for n in names(LIGHT_WARM))


def test_cool_dark_art_prefers_light_cool_supporting_walls_and_returns_reasons():
    best = walls.choose(DARK_COOL, "black_metal", n=3)
    assert best[0]["reasons"] and best[0]["score"] >= best[2]["score"]
    assert best[0]["name"] in ("Warm White", "Stone Grey", "Blue Grey", "Greige")


def test_deterministic():
    assert walls.choose(LIGHT_WARM) == walls.choose(LIGHT_WARM)
