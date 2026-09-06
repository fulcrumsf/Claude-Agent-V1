"""Revision Round 1 — regenerate start/end frame pairs for the re-shot clips.
Frames grounded in the RevisionRound1 storyboards + the character sheet.
Near-black backgrounds (never chroma-green) per Seedance frame-quality rules."""
import sys
from pathlib import Path

SK = "/Users/tonymacbook2025/.claude/skills/Storyboard-Generation/scripts"
sys.path.insert(0, SK)
import image_generation  # noqa: E402
_orig = image_generation.poll_image_task
image_generation.poll_image_task = lambda tid, **kw: _orig(tid, poll_interval_seconds=15.0, max_attempts=40)
from image_generation import generate_image  # noqa: E402

PROD = Path("/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/0003_Glass_Frog_Transparency")
FRAMES = PROD / "Images" / "Start_End_Frames"
SB = PROD / "Images" / "Storyboards" / "RevisionRound1"
CHAR = str(PROD / "Images" / "Character_Sheets" / "Glass_Frog_Main_Character_Sheet.png")

STYLE = (" Anomalous Wild nature-documentary style: photoreal cinematic wildlife macro, "
         "National Geographic-quality lighting, shallow depth of field, deep teal / forest-green / "
         "amber palette. Near-black background, NOT a green screen, no chroma green.")
ANAT = (" The glass frog has all four legs attached to its body and both eyes present and correctly "
        "placed — never a missing or detached limb, never a single eye.")

JOBS = {
 "Scene_04D_Start": dict(sb="Scene_04D_Tongue_Strike_Storyboard.png", char=True, prompt=(
   "Night. A single glass frog perched on the edge of a broad rain-wet green leaf in a rainforest, "
   "clean side view, in a low still ambush crouch — mouth closed, both eyes open and fixed forward, "
   "all four legs folded and gripping the leaf. A single small brown moth hovers in the air a short "
   "distance in front of the frog's face. Dark night-forest bokeh behind." + ANAT + STYLE)),
 "Scene_04D_End": dict(sb="Scene_04D_Tongue_Strike_Storyboard.png", char=True, prompt=(
   "Night. The SAME glass frog, the SAME leaf, the SAME side-view framing and camera position. The frog "
   "has lunged: its mouth is wide open and its long pink tongue is extended forward at full stretch, the "
   "tip touching a small brown moth in mid-air, the moth's wings folding against it. Head thrust forward, "
   "all four legs still anchored and gripping the leaf, both eyes half-closed. Same leaf, same dark "
   "night-forest bokeh, same lighting." + ANAT + STYLE)),

 "Scene_06A_Start": dict(sb="Scene_06A_PullBack_To_Amazon_Storyboard.png", char=True, prompt=(
   "Daytime misty cloud-forest. Close-up of a single glass frog resting on a large rain-wet green leaf, "
   "three-quarter front view, all four legs tucked under its body, both eyes open, calm. Behind it, "
   "softly out of focus, a misty mountain stream and green foliage. Soft overcast daylight." + ANAT + STYLE)),
 "Scene_06A_End": dict(sb="Scene_06A_PullBack_To_Amazon_Storyboard.png", char=False, prompt=(
   "Expansive high-altitude aerial wide shot of the Amazon basin — a huge brown-green river winding "
   "through unbroken dense rainforest canopy stretching to the misty horizon, low clouds catching "
   "sunlight, no animals visible. Cinematic nature-documentary aerial cinematography, daytime." + STYLE)),

 "Scene_06F_Start": dict(sb="Scene_06F_Backlit_Transparency_Storyboard.png", char=True, prompt=(
   "Warm backlight. Clean side view of a single glass frog clinging to the underside of a broad green "
   "leaf that is lit from behind so the leaf glows amber-green. All four legs splayed and gripping the "
   "leaf, both eyes closed, body pressed flat. The frog is a clearly visible distinct shape. Dark bokeh "
   "behind the leaf." + ANAT + STYLE)),
 "Scene_06F_End": dict(sb="Scene_06F_Backlit_Transparency_Storyboard.png", char=True, prompt=(
   "Warm backlight. The SAME glass frog, the SAME backlit glowing leaf, the SAME side-view framing. Now "
   "the frog has become almost fully transparent and blends into the leaf — its outline is barely "
   "distinguishable from the leaf surface, only the faint shadow of its spine and the two eye bumps "
   "giving it away. A single water droplet on the leaf edge. Same amber-green glow." + ANAT + STYLE)),

 "Scene_06G_Start": dict(sb="Scene_06G_Grand_Wide_Storyboard.png", char=False, prompt=(
   "Dawn. Extreme wide establishing shot looking across a forested ravine at a towering wall of misty "
   "tropical cloud-forest canopy, a thin waterfall and stream far below, warm low golden sunlight "
   "breaking through mist. No animals. Cinematic, epic scale." + STYLE)),
 "Scene_06G_End": dict(sb="Scene_06G_Grand_Wide_Storyboard.png", char=True, prompt=(
   "Dawn light. Medium shot of a single glass frog resting beneath a broad overhanging leaf on a mossy "
   "branch, tiny and still, all four legs gripping, both eyes closed. The vast cloud-forest soft and out "
   "of focus behind it. Warm golden backlight, shallow depth of field." + ANAT + STYLE)),

 "Scene_06H_Start": dict(sb="Scene_06H_Final_Upside_Down_Storyboard.png", char=True, prompt=(
   "Macro. Close-up of a single glass frog hanging UPSIDE-DOWN beneath a pale green leaf, all four legs "
   "spread wide and gripping the edges of the leaf, body pressed flat against the underside, both eyes "
   "closed, pale and almost shadowless. The frog is clearly visible. Soft even light, low contrast, the "
   "leaf's veins faintly visible through the frog." + ANAT + STYLE)),
 "Scene_06H_End": dict(sb="Scene_06H_Final_Upside_Down_Storyboard.png", char=True, prompt=(
   "Macro. The SAME upside-down glass frog beneath the SAME pale leaf, same framing. Now the frog has "
   "become nearly invisible — its pale translucent body has merged almost completely with the pale "
   "underside of the leaf, only the faintest outline and a hint of the two closed eyes remaining. Very "
   "soft, very low contrast, the leaf and frog reading as one surface." + ANAT + STYLE)),
}

targets = sys.argv[1:] or list(JOBS)
for name in targets:
    j = JOBS[name]
    refs = [str(SB / j["sb"])] + ([CHAR] if j["char"] else [])
    out = FRAMES / f"{name}.png"
    print(f"→ {name}  (refs: {len(refs)}) …", flush=True)
    generate_image(j["prompt"], out, "16:9", "2K", refs)
    print(f"  ✓ {out}", flush=True)
