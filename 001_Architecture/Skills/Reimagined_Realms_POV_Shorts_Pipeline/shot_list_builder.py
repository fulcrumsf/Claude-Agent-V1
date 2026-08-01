import re

NEGATIVE_PROMPT_CLOSER = "- No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text."

_QUOTED_DIALOGUE_PATTERN = re.compile(r'"[^"]{3,}"')


def _raise_if_quoted_dialogue(text: str) -> None:
    if _QUOTED_DIALOGUE_PATTERN.search(text):
        raise ValueError(
            f"Detected quoted dialogue in prompt text — this triggers Seedance's lip-sync mechanism, "
            f"which is forbidden for this no-dialogue format: {text!r}"
        )


def build_video_prompt(scene_description: str, sound_events: str, camera_fixed: bool) -> str:
    _raise_if_quoted_dialogue(scene_description)
    _raise_if_quoted_dialogue(sound_events)

    camera_note = "static camera, fixed position" if camera_fixed else "handheld camera motion"

    return (
        f"{scene_description}, {camera_note}. "
        f"Sound: {sound_events}. "
        f"{NEGATIVE_PROMPT_CLOSER}"
    )
