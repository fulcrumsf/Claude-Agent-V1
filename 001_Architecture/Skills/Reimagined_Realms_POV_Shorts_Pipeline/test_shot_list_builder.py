import pytest
from shot_list_builder import build_video_prompt

NEGATIVE_CLOSER = "- No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text."


def test_build_video_prompt_appends_negative_closer():
    result = build_video_prompt(
        scene_description="POV walking down a medieval dirt road carrying a wooden bucket of water, handheld camera motion",
        sound_events="water sloshing rhythmically with each step, footsteps on packed dirt, distant birds",
        camera_fixed=False,
    )
    assert result.endswith(NEGATIVE_CLOSER)
    assert "water sloshing rhythmically with each step" in result
    assert "POV walking down a medieval dirt road" in result


def test_build_video_prompt_raises_on_quoted_dialogue_in_scene_description():
    with pytest.raises(ValueError, match="quoted dialogue"):
        build_video_prompt(
            scene_description='A peasant says, "Good morning" to a passerby',
            sound_events="birds chirping",
            camera_fixed=True,
        )


def test_build_video_prompt_raises_on_quoted_dialogue_in_sound_events():
    with pytest.raises(ValueError, match="quoted dialogue"):
        build_video_prompt(
            scene_description="POV sitting by a fire",
            sound_events='someone whispers "stay warm" nearby',
            camera_fixed=True,
        )


def test_build_video_prompt_allows_short_quoted_fragments_that_are_not_dialogue():
    # A short quoted fragment (< 3 chars) should not false-positive as dialogue
    result = build_video_prompt(
        scene_description='A sign reading "V" hangs on the door',
        sound_events="wind",
        camera_fixed=True,
    )
    assert result.endswith(NEGATIVE_CLOSER)


def test_build_video_prompt_raises_on_smart_quoted_dialogue_in_scene_description():
    with pytest.raises(ValueError, match="quoted dialogue"):
        build_video_prompt(
            scene_description="A peasant says, “Good morning” to a passerby",
            sound_events="birds chirping",
            camera_fixed=True,
        )


def test_build_video_prompt_raises_on_smart_quoted_dialogue_in_sound_events():
    with pytest.raises(ValueError, match="quoted dialogue"):
        build_video_prompt(
            scene_description="POV sitting by a fire",
            sound_events="someone whispers “stay warm” nearby",
            camera_fixed=True,
        )


def test_build_video_prompt_raises_on_low_and_reversed_smart_quote_variants():
    with pytest.raises(ValueError, match="quoted dialogue"):
        build_video_prompt(
            scene_description="A peasant says, „Good morning‟ to a passerby",
            sound_events="birds chirping",
            camera_fixed=True,
        )


def test_build_video_prompt_raises_on_curly_single_quoted_dialogue():
    with pytest.raises(ValueError, match="quoted dialogue"):
        build_video_prompt(
            scene_description="A peasant says, ‘Good morning’ to a passerby",
            sound_events="birds chirping",
            camera_fixed=True,
        )


def test_build_video_prompt_raises_on_straight_single_quoted_dialogue():
    with pytest.raises(ValueError, match="quoted dialogue"):
        build_video_prompt(
            scene_description="'Good morning,' said the traveler",
            sound_events="birds chirping",
            camera_fixed=True,
        )


def test_build_video_prompt_raises_on_straight_single_quoted_dialogue_in_sound_events():
    with pytest.raises(ValueError, match="quoted dialogue"):
        build_video_prompt(
            scene_description="POV sitting by a fire",
            sound_events="a voice murmurs 'stay warm' nearby",
            camera_fixed=True,
        )


def test_build_video_prompt_allows_contraction_doesnt_without_false_positive():
    result = build_video_prompt(
        scene_description="The peasant walks, doesn't stop to look back",
        sound_events="footsteps on gravel",
        camera_fixed=False,
    )
    assert result.endswith(NEGATIVE_CLOSER)


def test_build_video_prompt_allows_contraction_its_without_false_positive():
    result = build_video_prompt(
        scene_description="It's a cold morning",
        sound_events="wind whistling",
        camera_fixed=True,
    )
    assert result.endswith(NEGATIVE_CLOSER)


def test_build_video_prompt_allows_multiple_contractions_without_false_positive():
    result = build_video_prompt(
        scene_description="The peasant doesn't know it's late, wasn't told",
        sound_events="crickets",
        camera_fixed=True,
    )
    assert result.endswith(NEGATIVE_CLOSER)


def test_build_video_prompt_raises_on_straight_single_quoted_dialogue_with_internal_contraction():
    with pytest.raises(ValueError, match="quoted dialogue"):
        build_video_prompt(
            scene_description="she said 'don't go'",
            sound_events="birds chirping",
            camera_fixed=True,
        )


def test_build_video_prompt_raises_on_straight_single_quoted_dialogue_with_internal_contraction_in_sound_events():
    with pytest.raises(ValueError, match="quoted dialogue"):
        build_video_prompt(
            scene_description="POV sitting by a fire",
            sound_events="a voice murmurs 'I'm scared' nearby",
            camera_fixed=True,
        )
