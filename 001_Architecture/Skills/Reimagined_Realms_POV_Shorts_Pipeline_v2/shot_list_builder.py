import re
from pathlib import Path

NEGATIVE_PROMPT_CLOSER = "- No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text."

POV_LOCK_CLAUSE = (
    "Strict first-person POV: the camera IS the character's own eyes, exactly like a body-worn "
    "camera. Never show what is physically impossible for the character's own eyes to see: their "
    "own face, the back of their own head, their own shoulder, or their own back. Whether hands, "
    "forearms, or legs are visible depends entirely on what this specific scene's action and gaze "
    "direction actually show — describe exactly what the character would see doing this specific "
    "action, never a fixed default set of body parts."
)

# Straight and smart/curly double quotes as interchangeable pair delimiters
# (word processors and some LLM output emit “ ” or the low/reversed variants
# „ ‟ instead of ASCII ").
_DOUBLE_QUOTE_DIALOGUE_PATTERN = re.compile(r'["“„‟][^"“”„‟]{3,}["”„‟]')

# Curly single quotes (‘ ’) are unambiguous pair delimiters — unlike the
# straight apostrophe, ‘ is never used to render a contraction, so no
# word-boundary heuristic is needed here.
_CURLY_SINGLE_QUOTE_DIALOGUE_PATTERN = re.compile(r'‘[^‘’]{3,}’')

# Straight single quote (') is ambiguous with the apostrophe in contractions
# ("don't", "it's"). Only treat it as a dialogue-quote pair when the opening
# quote is preceded by whitespace/start-of-string and the closing quote is
# followed by whitespace/punctuation/end-of-string — a bare contraction's
# apostrophe never satisfies both sides of that boundary requirement.
#
# The content class deliberately allows internal apostrophes (contractions
# inside quoted dialogue, e.g. 'don't go', 'I'm scared') rather than
# excluding '. Combined with the non-greedy {3,}?, the engine walks past
# a contraction's apostrophe (which fails the closing-boundary lookahead)
# and keeps extending until it finds the real closing quote.
_STRAIGHT_SINGLE_QUOTE_DIALOGUE_PATTERN = re.compile(
    r"(?:^|(?<=\s))'([^\n]{3,}?)'(?=[\s.,!?;:]|$)"
)


def _raise_if_quoted_dialogue(text: str) -> None:
    if (
        _DOUBLE_QUOTE_DIALOGUE_PATTERN.search(text)
        or _CURLY_SINGLE_QUOTE_DIALOGUE_PATTERN.search(text)
        or _STRAIGHT_SINGLE_QUOTE_DIALOGUE_PATTERN.search(text)
    ):
        raise ValueError(
            f"Detected quoted dialogue in prompt text — this triggers Seedance's lip-sync mechanism, "
            f"which is forbidden for this no-dialogue format: {text!r}"
        )


def build_multi_character_reference_note(character_roles: list[str] | None) -> str:
    """Builds the @Image1/@Image2 ordinal-referencing clause confirmed live via ByteDance's own
    BytePlus ModelArk docs (see Seedance-Prompting-Guide/SKILL.md, 2026-08-06) — required whenever
    more than one character reference image is passed in reference_image_urls, or Seedance has
    nothing but the single reference to draw every person in a multi-person shot from and will
    duplicate the same face across all of them (confirmed failure mode on Titanic Stoker shot 9).

    character_roles order MUST match the order images are passed to reference_image_urls —
    character_roles[0] describes image 1, character_roles[1] describes image 2, etc.

    ONLY meaningful when the video call actually passes reference_image_urls. Confirmed live
    2026-08-08: kie.ai's bytedance_seedance_video endpoint rejects first_frame_url and
    reference_image_urls together, and this pipeline's primary path always uses first_frame_url
    (character/prop/environment consistency is already baked into that image at the
    image-generation stage) — so character_roles/this @Image note should NOT be passed when
    building a video_generation call that also sets first_frame_url. There is simply no
    reference_image_urls array left for the tags to point at in that case.
    """
    if not character_roles:
        return ""
    tags = " ".join(f"@Image{i + 1} shows {role}." for i, role in enumerate(character_roles))
    return f"{tags} "


def build_video_prompt(
    scene_description: str,
    sound_events: str,
    camera_fixed: bool,
    character_roles: list[str] | None = None,
) -> str:
    _raise_if_quoted_dialogue(scene_description)
    _raise_if_quoted_dialogue(sound_events)

    camera_note = "static camera, fixed position" if camera_fixed else "handheld camera motion"
    reference_note = build_multi_character_reference_note(character_roles)

    return (
        f"{POV_LOCK_CLAUSE} "
        f"{reference_note}"
        f"{scene_description}, {camera_note}. "
        f"Sound: {sound_events}. "
        f"{NEGATIVE_PROMPT_CLOSER}"
    )


def write_shot_list(out_dir: Path, shots: list[dict]) -> Path:
    out_dir = Path(out_dir)
    production_dir = out_dir / "Production"
    production_dir.mkdir(parents=True, exist_ok=True)

    lines = []
    for shot in shots:
        video_prompt = build_video_prompt(
            shot["scene_description"], shot["sound_events"], shot["camera_fixed"],
            shot.get("character_roles"),
        )
        lines.append(f"## Shot {shot['index']}")
        lines.append("")
        lines.append(f"**Image prompt:** {shot['image_prompt']}")
        lines.append("")
        lines.append(f"**Video prompt:** {video_prompt}")
        lines.append("")

    shot_list_path = production_dir / "Shot_List.md"
    shot_list_path.write_text("\n".join(lines))
    return shot_list_path
