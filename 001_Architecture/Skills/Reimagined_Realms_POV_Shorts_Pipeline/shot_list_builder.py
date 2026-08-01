import re
from pathlib import Path

NEGATIVE_PROMPT_CLOSER = "- No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text."

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


def build_video_prompt(scene_description: str, sound_events: str, camera_fixed: bool) -> str:
    _raise_if_quoted_dialogue(scene_description)
    _raise_if_quoted_dialogue(sound_events)

    camera_note = "static camera, fixed position" if camera_fixed else "handheld camera motion"

    return (
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
            shot["scene_description"], shot["sound_events"], shot["camera_fixed"]
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
