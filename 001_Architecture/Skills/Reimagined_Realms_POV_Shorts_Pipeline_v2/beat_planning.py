import json
from pathlib import Path

def scenes_needed_for_floor(current_scene_count: int, seconds_per_scene: float = 5.0, floor_seconds: float = 65.0) -> int:
    if seconds_per_scene <= 0:
        raise ValueError("seconds_per_scene must be greater than 0")

    current_total = current_scene_count * seconds_per_scene
    if current_total >= floor_seconds:
        return 0

    additional = 0
    total = current_total
    while total < floor_seconds:
        additional += 1
        total += seconds_per_scene
    return additional

def write_beat_table(out_dir: Path, beats: list[dict]) -> Path:
    out_dir = Path(out_dir)
    data_dir = out_dir / "Data"
    data_dir.mkdir(parents=True, exist_ok=True)

    beat_table_path = data_dir / "Beat_Table.json"
    beat_table_path.write_text(json.dumps(beats, indent=2))
    return beat_table_path
