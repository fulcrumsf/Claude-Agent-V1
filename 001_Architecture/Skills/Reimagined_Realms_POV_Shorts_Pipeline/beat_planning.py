import math

def scenes_needed_for_floor(current_scene_count: int, seconds_per_scene: float = 5.0, floor_seconds: float = 65.0) -> int:
    current_total = current_scene_count * seconds_per_scene
    if current_total >= floor_seconds:
        return 0

    additional = 0
    total = current_total
    while total < floor_seconds:
        additional += 1
        total += seconds_per_scene
    return additional
