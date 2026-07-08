import json
from pathlib import Path


def test_every_tool_has_at_least_one_source():
    data = json.loads((Path(__file__).parent / "data" / "motion_graphics_capabilities.json").read_text())
    for tool in data["tools"]:
        assert tool["sources"], f"{tool['name']} has no cited source — this is a guess, not research"
        assert tool["strengths"], f"{tool['name']} has no strengths listed"
        assert tool["best_for"], f"{tool['name']} has no best_for listed"


def test_expected_tools_present():
    data = json.loads((Path(__file__).parent / "data" / "motion_graphics_capabilities.json").read_text())
    names = {t["name"] for t in data["tools"]}
    assert {"Remotion", "video-use", "Hyperframes", "Manim"}.issubset(names)
