"""Revision Round 1 — regenerate storyboards for the shots being re-shot.
Presents to Tony BEFORE any paid video generation."""
import sys
from pathlib import Path

SK = "/Users/tonymacbook2025/.claude/skills/Storyboard-Generation/scripts"
sys.path.insert(0, SK)
import image_generation  # noqa: E402
_orig_poll = image_generation.poll_image_task
image_generation.poll_image_task = lambda tid, **kw: _orig_poll(tid, poll_interval_seconds=15.0, max_attempts=40)
from storyboard_generation import build_spec, generate_storyboard  # noqa: E402

PROD = Path("/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/0003_Glass_Frog_Transparency")
OUT = PROD / "Images" / "Storyboards" / "RevisionRound1"
OUT.mkdir(parents=True, exist_ok=True)
CHAR_SHEET = str(PROD / "Images" / "Character_Sheets" / "Glass_Frog_Main_Character_Sheet.png")

STYLE = ("Anomalous Wild dark neon nature-documentary hybrid: cinematic wildlife-documentary "
         "macro photography combined with AI 3D-render inserts for internal anatomy/mechanism shots. "
         "Deep teal, forest dark-green, and amber lighting; National Geographic-quality lighting on "
         "real/photoreal shots; no gore, no viscera. Photoreal, shallow depth of field.")

ANAT = (" Anatomy check: in every panel the glass frog has all four legs attached to its body and "
        "both eyes present and correctly placed — never a missing or detached limb, never a single-eyed frog.")
CONSIST = ("Keep the storyboard readable and visually consistent. Every panel shows the SAME glass frog "
           "with identical coloring, markings and proportions, as one continuous shot." + ANAT)

SHOTS = {
  "Scene_04D_Tongue_Strike": dict(
    duration_s=6.07,
    scene_description=("Night. A single glass frog ambush-hunts from a broad wet leaf: it sits perfectly "
      "still, then catches a moth with one explosive flick of its tongue, then settles back to stillness. "
      "One continuous ~6-second shot." + ANAT),
    frames=[
      "Medium shot at night, the glass frog perched on the edge of a broad rain-wet leaf, all four legs folded and gripping the leaf, both large eyes open and fixed forward, completely motionless in an ambush crouch, a small moth hovering a short distance in front of it.",
      "Slow push to a tighter medium close-up, the frog's head and both eyes locked onto the moth, body coiled and still, one front foot adjusting its grip on the leaf.",
      "Close-up, the instant of the strike: the frog's mouth open and its long tongue launching forward at full extension toward the moth, head thrust forward, all four legs still anchored to the leaf.",
      "Extreme close-up, the tip of the tongue making contact with the moth in mid-air, the moth's wings folding against it.",
      "Close-up, the tongue retracting into the mouth carrying the moth, the frog's head pulling back to centre, all four legs still planted on the leaf.",
      "Medium shot, the frog settled back into its original still ambush posture on the leaf, moth gone, both eyes open and forward, dark night-forest bokeh behind it.",
    ]),
  "Scene_06A_PullBack_To_Amazon": dict(
    duration_s=6.3,
    scene_description=("Daytime cloud-forest. One single unbroken camera pull-back that starts close on a "
      "glass frog resting on a leaf and ends on a sweeping wide of the Amazon basin. NO internal cut, "
      "NO scene change — one continuous move start to finish." + ANAT),
    frames=[
      "Close-up, the glass frog resting on a large rain-wet leaf in a misty cloud-forest, all four legs tucked under its body, both eyes open, soft daylight, a mountain stream just visible behind.",
      "The camera begins a smooth continuous pull-back — medium shot now, the whole frog and its leaf in frame with more of the mossy stream bank around it.",
      "The same unbroken pull-back continues, medium-wide, the frog now small on its leaf, foliage and the stream filling more of the frame.",
      "Still the same continuous move, wide shot, the frog a tiny pale speck on one leaf among dense green rainforest, the stream widening below.",
      "The pull-back continues to a sweeping wide, the cloud-forest opening toward a broad river valley, mist over the canopy, the frog's leaf no longer distinguishable.",
      "Final frame of the same unbroken shot: an expansive aerial-style wide of the Amazon basin, a huge river winding through unbroken rainforest to the horizon.",
    ]),
  "Scene_06F_Backlit_Transparency": dict(
    duration_s=8.07,
    scene_description=("Warm backlight. A side-angle shot of the glass frog on the underside of a glowing "
      "leaf, its body becoming transparent and blending into the leaf. This is the 'camouflage trick' "
      "beat — DISTINCT from the wide shot and the upside-down close that follow it." + ANAT),
    frames=[
      "Side-angle medium shot, the glass frog clinging to the underside of a broad green leaf lit from behind so the leaf glows, all four legs splayed and gripping, both eyes closed, body pressed flat.",
      "Push in to a medium close-up on the frog's translucent belly against the backlit leaf, a faint suggestion of mirrored internal organs, skin taking on the leaf's green.",
      "Close-up, the frog's outline beginning to blend into the leaf, the edges of its legs becoming hard to separate from the leaf surface.",
      "Extreme close-up on the skin surface, light passing through it, the boundary between frog and leaf almost gone.",
      "Slow pull back to medium, the frog now reads almost entirely as part of the leaf, only the faint shadow of its spine giving it away.",
      "Medium side shot held, the frog nearly invisible against the glowing leaf, a single water droplet rolling off the leaf edge, shallow depth of field.",
    ]),
  "Scene_06G_Grand_Wide": dict(
    duration_s=6.07,
    scene_description=("Dawn. A grand WIDE establishing shot of the whole cloud-forest that slowly finds one "
      "leaf with the tiny frog beneath it. DISTINCT from the backlit-transparency shot and the "
      "upside-down close — this one is about scale and the vastness of the forest." + ANAT),
    frames=[
      "Extreme wide establishing shot from across a ravine, looking at a towering wall of misty cloud-forest canopy at dawn, a thin waterfall and stream far below, no frog visible.",
      "The same wide, camera drifting slowly, thousands of leaves catching the low light, the scale of the forest emphasised.",
      "Wide, a slow push toward one particular tree among many, its broad leaves overhanging the stream.",
      "Medium-wide, closing on a single overhanging branch, one leaf standing out, a barely-perceptible pale shape on its underside.",
      "Medium shot, the overhanging leaf clearly in frame, the glass frog just resolvable beneath it, all four legs gripping, both eyes closed.",
      "Medium close-up settling on the frog under the leaf, tiny and still, the vast forest implied in the soft-focus background.",
    ]),
  "Scene_06H_Final_Upside_Down": dict(
    duration_s=5.07,
    scene_description=("The final, intimate closing image of the video: a close shot of the glass frog "
      "hanging UPSIDE-DOWN beneath a leaf, asleep, slowly becoming invisible against it. DISTINCT from "
      "the two shots before it — this one is close, quiet, and still." + ANAT),
    frames=[
      "Close-up, the glass frog hanging upside-down beneath a leaf, all four legs spread and gripping the leaf edge, body pressed flat against it, both eyes closed, pale and almost shadowless.",
      "Very slow push in, tighter close-up on the frog's flattened translucent body, the leaf's veins visible through it.",
      "Extreme close-up on the frog's face and one front foot, utterly still.",
      "Slow pull back to close-up, the frog's pale form beginning to merge with the pale underside of the leaf.",
      "Medium close-up, the frog now barely distinguishable from the leaf, the whole frame soft and low-contrast.",
      "Final held frame, the leaf and the frog reading as one, the frog effectively invisible, upside-down, asleep.",
    ]),
}

targets = sys.argv[1:] or list(SHOTS)
for name in targets:
    d = SHOTS[name]
    spec = build_spec(
        scene_id=name, duration_s=d["duration_s"],
        scene_description=d["scene_description"], visual_style=STYLE,
        frame_actions=d["frames"], consistency_directive=CONSIST,
    )
    (PROD / "Data" / f"storyboard_spec_{name}.json").write_text(__import__("json").dumps(spec, indent=2))
    out = OUT / f"{name}_Storyboard.png"
    print(f"→ {name} ({spec['frame_count']} frames) …", flush=True)
    generate_storyboard(spec, out, reference_image_urls=[CHAR_SHEET])
    print(f"  ✓ {out}", flush=True)
