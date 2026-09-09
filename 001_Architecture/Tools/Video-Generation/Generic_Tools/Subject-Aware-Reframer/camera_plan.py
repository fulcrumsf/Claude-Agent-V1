"""Pure camera planning over timestamped detections; no channel or provider knowledge."""
from __future__ import annotations

import bisect
import math
from collections import defaultdict
from fractions import Fraction

from diagnose import output_indices, validate_shots

MODES = {"group", "subject", "hybrid"}
NUMERIC_LIMITS = {
    "subject_hold_seconds": (1, 30), "group_hold_seconds": (1, 30),
    "end_group_seconds": (0, 10), "gap_hold_seconds": (0, 1),
    "lookahead_seconds": (0, 1), "opening_lookahead_seconds": (0, 2),
    "smoothing_seconds": (0, 2), "dead_zone_fraction": (0, 0.2),
    "max_pan_fraction_per_second": (0.05, 3),
    "max_zoom_fraction_per_second": (0.05, 2), "max_zoom": (1, 3),
    "subject_margin_fraction": (0, 0.3), "fallback_hold_seconds": (0.5, 10),
    "background_brightness": (0.1, 1), "background_blur": (3, 51),
}


def settings_for(defaults, profile, overrides=None):
    allowed = set(NUMERIC_LIMITS) | {"mode", "priority", "switch_policy"}
    result = dict(defaults)
    for layer in (profile, overrides or {}):
        unknown = set(layer) - allowed
        if unknown:
            raise ValueError(f"Unknown framing settings: {sorted(unknown)}")
        result.update(layer)
    if set(result) != allowed:
        raise ValueError("Framing settings are incomplete")
    if result["mode"] not in MODES or result["switch_policy"] not in {"priority", "alternate"}:
        raise ValueError("Invalid framing mode or switching policy")
    if sorted(result["priority"]) != ["animal", "person"]:
        raise ValueError("Priority must order person and animal exactly once")
    for name, (lo, hi) in NUMERIC_LIMITS.items():
        value = result[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not lo <= value <= hi:
            raise ValueError(f"Invalid {name}: expected {lo} through {hi}")
    if type(result["background_blur"]) is not int or result["background_blur"] % 2 != 1:
        raise ValueError("Background blur must be an odd integer")
    return result


def area(box):
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def intersection(a, b):
    return area([max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])])


def clamp_box(box, width, height):
    return [max(0, min(width, box[0])), max(0, min(height, box[1])),
            max(0, min(width, box[2])), max(0, min(height, box[3]))]


def deduplicate(candidates):
    # A current observation takes precedence over a stale held identity.
    ordered = sorted(candidates, key=lambda t: (t["origin"] == "observed", t["confidence"]), reverse=True)
    kept = []
    for t in ordered:
        if any(t["family"] == other["family"] and
               intersection(t["box"], other["box"]) / max(1, min(area(t["box"]), area(other["box"]))) > 0.8
               for other in kept):
            continue
        kept.append(t)
    return kept


def observations(records, source_seconds, settings, width, height):
    """Bridge only short gaps within a shot; retain provenance for predicted/held boxes."""
    by_id = defaultdict(list)
    for record in records:
        for track in record["tracks"]:
            if not track.get("confirmed", False):
                continue
            box = clamp_box(track["bbox_xyxy"], width, height)
            if area(box) > 0:
                by_id[track["id"]].append((record["source_seconds"], {
                    "id": track["id"], "family": track["family"], "box": box,
                    "confidence": track["confidence"], "origin": "observed",
                }))
    result = []
    start = records[0]["source_seconds"]
    for t in source_seconds:
        candidates = []
        for values in by_id.values():
            times = [v[0] for v in values]
            k = bisect.bisect_right(times, t + 1e-8) - 1
            prev = values[k] if k >= 0 else None
            future = values[k+1] if k+1 < len(values) else None
            if prev and abs(prev[0] - t) < 1e-7:
                candidate = dict(prev[1])
            elif prev and t - prev[0] <= settings["gap_hold_seconds"]:
                candidate = {**prev[1], "origin": "held"}
                if future and future[0] - t <= settings["lookahead_seconds"]:
                    fraction = (t - prev[0]) / (future[0] - prev[0])
                    candidate["box"] = [a + (b - a) * fraction for a, b in zip(prev[1]["box"], future[1]["box"])]
                    candidate["origin"] = "interpolated"
            elif future and future[0] - t <= (
                settings["opening_lookahead_seconds"] if t - start < settings["opening_lookahead_seconds"]
                else settings["lookahead_seconds"]
            ):
                candidate = {**future[1], "origin": "lookahead"}
            else:
                continue
            candidates.append(candidate)
        result.append(deduplicate(candidates))
    return result


def choose_subject(candidates, priority, previous=None, previous_box=None, avoid=None):
    if not candidates:
        return None
    match = next((t for t in candidates if t["id"] == previous), None)
    if match:
        return match
    # Reassociate a fragmented ID geometrically before making an editorial switch.
    if previous_box is not None:
        overlapping = [t for t in candidates if intersection(t["box"], previous_box) / max(1, area(previous_box)) > 0.5]
        if overlapping:
            return max(overlapping, key=lambda t: intersection(t["box"], previous_box))
    preferred = [t for t in candidates if t["id"] != avoid]
    if preferred:
        candidates = preferred
    return min(candidates, key=lambda t: (priority.index(t["family"]), -area(t["box"]), -t["confidence"], t["id"]))


def crop_for(box, width, height, aspect, settings):
    mx = (box[2] - box[0]) * settings["subject_margin_fraction"]
    my = (box[3] - box[1]) * settings["subject_margin_fraction"]
    safe = clamp_box([box[0]-mx, box[1]-my, box[2]+mx, box[3]+my], width, height)
    crop_height = max(height / settings["max_zoom"], safe[3]-safe[1], (safe[2]-safe[0])/aspect)
    if crop_height > min(height, width/aspect) + 1e-6:
        return None
    crop_width = crop_height * aspect
    cx = max(crop_width/2, min(width-crop_width/2, (safe[0]+safe[2])/2))
    cy = max(crop_height/2, min(height-crop_height/2, (safe[1]+safe[3])/2))
    return [cx, cy, crop_height]


def smooth_camera(target, previous, box, width, height, aspect, settings, dt):
    if previous is None:
        return target
    tau = settings["smoothing_seconds"]
    alpha = 1 if not tau else 1 - math.exp(-dt/tau)
    cx, cy, ch = previous
    goal_x, goal_y, goal_h = target
    dx, dy = goal_x-cx, goal_y-cy
    dx = math.copysign(max(0, abs(dx)-ch*aspect*settings["dead_zone_fraction"]), dx)
    dy = math.copysign(max(0, abs(dy)-ch*settings["dead_zone_fraction"]), dy)
    speed = width * settings["max_pan_fraction_per_second"] * dt
    zoom = height * settings["max_zoom_fraction_per_second"] * dt
    nh = max(ch-zoom, min(ch+zoom, ch+(goal_h-ch)*alpha))
    # Expand enough to contain the actual subject, subject to the zoom speed.
    required = max(box[3]-box[1], (box[2]-box[0])/aspect)
    nh = max(nh, min(ch+zoom, required))
    if required > nh + 1e-6:
        return None
    nw = nh*aspect
    lower_x, upper_x = max(nw/2, box[2]-nw/2, cx-speed), min(width-nw/2, box[0]+nw/2, cx+speed)
    lower_y, upper_y = max(nh/2, box[3]-nh/2, cy-speed), min(height-nh/2, box[1]+nh/2, cy+speed)
    if lower_x > upper_x or lower_y > upper_y:
        return None
    return [max(lower_x, min(upper_x, cx+dx*alpha)),
            max(lower_y, min(upper_y, cy+dy*alpha)), nh]


def rect(camera, aspect):
    x, y, h = camera
    return [x-h*aspect/2, y-h/2, x+h*aspect/2, y+h/2]


def plan_shot(records, indices, output_start, shot, cfg, stream, settings, fps, aspect):
    width, height = stream["width"], stream["height"]
    tb = Fraction(cfg["time_base"])
    start = float(shot["start_pts"]*tb)
    end = float(shot["end_pts"]*tb)
    seconds = [float(output_start + Fraction(i, fps)) for i, _ in indices]
    # Subjects correspond to the displayed source frame, not an invented interpolated image.
    candidates_by_frame = observations(records, [r["source_seconds"] for _, r in indices], settings, width, height)
    previous_id = previous_box = previous_family = camera = previous_layout = None
    previous_phase = None
    fallback_until = -1
    focus_epoch = 0
    last_subject_id = None
    seen_multiple = False
    planned = []
    for (output_index, source), t, candidates in zip(indices, seconds, candidates_by_frame):
        elapsed = t - start
        duration = settings["subject_hold_seconds"]
        cycle = duration + settings["group_hold_seconds"] if settings["mode"] == "hybrid" else duration
        phase = int((elapsed + 1e-8) / cycle) if settings["mode"] == "hybrid" or settings["switch_policy"] == "alternate" else 0
        group = settings["mode"] == "group"
        reason = "group_profile" if group else "subject_view"
        seen_multiple = seen_multiple or len(candidates) >= 2
        if settings["mode"] == "hybrid" and seen_multiple:
            if elapsed % cycle >= duration:
                group, reason = True, "hybrid_group_hold"
            if end-t <= settings["end_group_seconds"]:
                group, reason = True, "hybrid_payoff_group"
        switched = phase != previous_phase
        if switched:
            previous_phase = phase
            previous_id = previous_box = previous_family = None
        priorities = list(settings["priority"])
        if settings["switch_policy"] == "alternate" and phase % 2:
            priorities.reverse()
        eligible = candidates
        if previous_family:
            eligible = [c for c in candidates if c["family"] == previous_family] or candidates
        focus = choose_subject(eligible, priorities, previous_id, previous_box,
                               last_subject_id if switched and settings["switch_policy"] == "alternate" else None)
        target_changed = switched and focus and focus["id"] != last_subject_id
        if target_changed:
            focus_epoch += 1
            camera = None
        if not group and focus:
            if previous_id and focus["id"] != previous_id and (
                previous_family != focus["family"] or intersection(focus["box"], previous_box)/max(1, area(previous_box)) < 0.2
            ):
                # A real target replacement is a deliberate edit, not a fast pan across empty space.
                focus_epoch += 1
                camera = None
            previous_id, previous_box, previous_family = focus["id"], focus["box"], focus["family"]
            last_subject_id = focus["id"]
        if group:
            camera = None
        elif not focus:
            group, reason, camera = True, "no_reliable_subject", None
            fallback_until = max(fallback_until, t+settings["fallback_hold_seconds"])
        elif t < fallback_until:
            group, reason, camera = True, "fallback_minimum_hold", None
        else:
            target = crop_for(focus["box"], width, height, aspect, settings)
            if target_changed or previous_layout != "crop":
                camera = None
            next_camera = smooth_camera(target, camera, focus["box"], width, height, aspect, settings, 1/fps) if target else None
            if next_camera is None:
                group, reason, camera = True, "subject_or_motion_does_not_fit", None
                fallback_until = t+settings["fallback_hold_seconds"]
            else:
                camera = next_camera
        layout = "fit_blur" if group else "crop"
        crop = [0, 0, width, height] if group else rect(camera, aspect)
        segment = f"{shot['id']}:wide" if group else f"{shot['id']}:{focus_epoch}:crop"
        cut = not planned or planned[-1]["camera_segment"] != segment
        planned.append({
            "output_frame": output_index, "output_seconds": round(output_index/fps, 9),
            "source_frame": source["source_frame"], "source_pts": source["pts"],
            "source_seconds": source["source_seconds"], "shot": shot["id"],
            "layout": layout, "reason": reason, "camera_segment": segment, "cut": cut,
            "crop_xyxy": [round(v, 6) for v in crop],
            "focus": focus if not group else None, "subjects": candidates,
            "background_brightness": settings["background_brightness"],
            "background_blur": settings["background_blur"],
        })
        previous_layout = layout
    suppress_short_crop_returns(planned, settings["fallback_hold_seconds"], width, height)
    return planned


def suppress_short_crop_returns(frames, minimum_seconds, width, height):
    """Use offline look-ahead to avoid a brief crop between wider layouts."""
    i = 0
    while i < len(frames):
        end = i + 1
        while end < len(frames) and frames[end]["camera_segment"] == frames[i]["camera_segment"]:
            end += 1
        # A short scene with a single view is valid; suppress only crops adjoining a wide view.
        next_wide = end < len(frames) and frames[end]["layout"] == "fit_blur"
        prior_wide = i > 0 and frames[i-1]["layout"] == "fit_blur"
        duration = (frames[end-1]["output_seconds"] - frames[i]["output_seconds"]) + 1/30
        if frames[i]["layout"] == "crop" and duration < minimum_seconds-1e-6 and (prior_wide or next_wide):
            for f in frames[i:end]:
                f.update(layout="fit_blur", reason="short_crop_suppressed", focus=None,
                         crop_xyxy=[0,0,width,height], camera_segment=f"{f['shot']}:wide")
        i = end
    for i, f in enumerate(frames):
        f["cut"] = i == 0 or f["camera_segment"] != frames[i-1]["camera_segment"]


def build_plan(cache, settings, shot_overrides, output):
    cfg, records, stream = cache["config"], cache["frames"], cache["stream"]
    validate_shots(cfg["shots"])
    if not cfg.get("family_tracking"):
        raise ValueError("Camera planning requires family-aware detection records")
    if len(records) != cfg["expected_source_frames"] or any(b["pts"] <= a["pts"] for a,b in zip(records, records[1:])):
        raise ValueError("Detection timestamps/count are invalid")
    shot_ids = {s["id"] for s in cfg["shots"]}
    if set(shot_overrides) - shot_ids:
        raise ValueError("An override names an unknown shot")
    mapping = output_indices(records, cfg["shots"][0]["start_pts"], cfg["shots"][-1]["end_pts"], cfg["time_base"], output["fps"])
    origin = cfg["shots"][0]["start_pts"] * Fraction(cfg["time_base"])
    frames = []
    resolved = {}
    for shot in cfg["shots"]:
        local = [r for r in records if r["shot"] == shot["id"]]
        selected = [(i, records[k]) for i,k in enumerate(mapping) if records[k]["shot"] == shot["id"]]
        shot_settings = settings_for(settings, {}, shot_overrides.get(shot["id"], {}))
        resolved[shot["id"]] = shot_settings
        frames.extend(plan_shot(local, selected, origin, shot, cfg, stream, shot_settings,
                                output["fps"], output["width"]/output["height"]))
    if len(frames) != len(mapping):
        raise ValueError("Shot mapping did not cover every output frame")
    return {"settings": settings, "resolved_shot_settings": resolved, "frames": frames,
            "source_record_per_output_frame": mapping, "output": output,
            "duration_seconds": len(mapping)/output["fps"]}
