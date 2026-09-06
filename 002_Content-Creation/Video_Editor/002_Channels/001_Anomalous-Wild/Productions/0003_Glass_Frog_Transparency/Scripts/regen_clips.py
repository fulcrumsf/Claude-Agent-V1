"""Revision Round 1 — regenerate the 5 re-shot clips via Seedance 1.5 Pro
(start-frame + end-frame), then trim to target. Reuses pipeline_supervisor's
tested generate_seedance / kie_poll / download and clip_durations' pad+trim."""
import sys, subprocess, json
from pathlib import Path

AW = "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild"
SK = "/Users/tonymacbook2025/.claude/skills/Storyboard-Generation/scripts"
PROD = Path("/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/0003_Glass_Frog_Transparency")
FRAMES = PROD / "Images" / "Start_End_Frames"
CLIPS = PROD / "Video_Clips"

sys.path.insert(0, SK); sys.path.insert(0, AW)
sys.argv = ["pipeline_supervisor.py", str(PROD)]  # satisfy its module-level BASE
import image_generation                       # noqa: E402
import pipeline_supervisor as ps              # noqa: E402
import clip_durations as cd                   # noqa: E402

NEG = ("- No cut, no scene change, no jump cut, no hard cut, no camera cut. One single continuous "
       "unbroken take. No on-screen text, no captions, no watermark, no music, no human voice.")
ANAT = ("The glass frog's four legs stay fully attached to its body and feet at all times; "
        "anatomically correct amphibian limbs; no detaching, no warping, no extra digits, no missing eye. ")

SHOTS = {
 "scene_04/Scene_04D_looped.mp4": dict(
   start="Scene_04D_Start.png", end="Scene_04D_End.png", target_s=6.07,
   prompt=("Night rainforest macro. A glass frog sits perfectly still in an ambush crouch on the edge of a "
     "wet leaf, then strikes: it lunges forward and its long tongue flicks out at full stretch to catch a "
     "small moth in mid-air, then the tongue snaps back. Fast explosive tongue strike, the frog's body "
     "otherwise low and controlled. " + ANAT +
     "Camera holds a steady close side view, only a tiny natural push. Native audio: quiet night-forest "
     "ambience, faint insect wingbeat, a soft wet click on the strike. " + NEG)),

 "scene_06/Scene_06A_looped.mp4": dict(
   start="Scene_06A_Start.png", end="Scene_06A_End.png", target_s=6.3,
   prompt=("One single continuous, unbroken camera pull-back that starts as a close macro shot of a glass "
     "frog resting on a rain-wet leaf in a misty cloud-forest and smoothly, continuously flies backward "
     "and upward the whole time until it becomes a sweeping high aerial wide shot of the Amazon river "
     "basin, a huge river winding through unbroken rainforest to the horizon. The move never stops and "
     "never cuts — one flowing crane-and-drone pull-back from macro to aerial. " + ANAT +
     "Native audio: cloud-forest ambience rising into open wind. " + NEG)),

 "scene_06/Scene_06F_looped.mp4": dict(
   start="Scene_06F_Start.png", end="Scene_06F_End.png", target_s=8.07,
   prompt=("Warm backlit macro, side view. A glass frog clings to the underside of a glowing backlit leaf "
     "and slowly, over the whole shot, becomes transparent — its body gradually blends into the leaf "
     "until it is almost invisible, only the faint shadow of its spine left. A single water droplet "
     "forms and rolls off the leaf edge at the end. " + ANAT +
     "Very slow, smooth push toward the frog, no stopping. Native audio: soft rainforest ambience, a "
     "single water drip. " + NEG)),

 "scene_06/Scene_06G_looped.mp4": dict(
   start="Scene_06G_Start.png", end="Scene_06G_End.png", target_s=6.07,
   prompt=("One single continuous camera move at dawn: it starts on an extreme wide vista of a misty "
     "cloud-forest ravine with golden light and a distant waterfall, then smoothly and continuously "
     "pushes in and cranes down the whole time until it settles on a medium shot of one tiny glass frog "
     "resting beneath a single overhanging leaf. The move is one unbroken flight, never a cut. " + ANAT +
     "Native audio: dawn forest, birdsong, distant water. " + NEG)),

 "scene_06/Scene_06H_looped.mp4": dict(
   start="Scene_06H_Start.png", end="Scene_06H_End.png", target_s=5.07,
   prompt=("Very slow macro push-in. A glass frog hangs upside-down beneath a pale leaf, completely "
     "still, and over the whole shot it slowly becomes invisible — its pale translucent body merges with "
     "the pale underside of the leaf until the frog and the leaf read as one surface. Minimal, gentle "
     "camera drift only. " + ANAT +
     "Native audio: very quiet still rainforest ambience. " + NEG)),
}

def upload(p: Path) -> str:
    return image_generation._resolve_to_public_url(str(p))

targets = sys.argv[2:] if len(sys.argv) > 2 else list(SHOTS)
for rel in targets:
    s = SHOTS[rel]
    raw = CLIPS / rel.replace("_looped", "")
    looped = CLIPS / rel
    raw.parent.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {rel}  (target {s['target_s']}s) ===", flush=True)
    dur = cd.request_duration(s["target_s"], "bytedance/seedance-1.5-pro")
    entry = {
        "scene_id": Path(rel).stem, "video_prompt": s["prompt"],
        "first_frame_url": upload(FRAMES / s["start"]),
        "last_frame_url": upload(FRAMES / s["end"]),
        "duration_s": dur, "aspect_ratio": "16:9", "generate_audio": True,
    }
    print(f"  request duration {dur}s; frames uploaded", flush=True)
    res = ps.generate_seedance(entry)
    if not res.get("ok"):
        print(f"  ✗ FAILED [{res.get('error_category')}]: {res.get('reason')}", flush=True)
        continue
    if not ps.download(res["url"], raw):
        print("  ✗ download failed", flush=True); continue
    real = cd.probe_duration(raw)
    print(f"  ✓ raw {raw.name}  {real:.2f}s", flush=True)
    trim = cd.trim_to_target(raw, looped, s["target_s"])
    print(f"  trim → {trim}", flush=True)
