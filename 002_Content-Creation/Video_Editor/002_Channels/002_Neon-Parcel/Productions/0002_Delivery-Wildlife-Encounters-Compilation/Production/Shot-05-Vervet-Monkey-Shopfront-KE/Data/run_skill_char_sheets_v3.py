import sys
from pathlib import Path
sys.path.insert(0,'/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Character-Sheet-Generation/scripts')
from character_sheet_generation import build_character_sheet_prompt, generate_character_sheet
J={
"Courier":dict(role="the bicycle parcel courier", stype="person", out="Character_Sheets/Courier_Character_Sheet_Skill_v3.png", notes="",
 desc="An adult East African man in his late 20s to 30s, average build, plain navy short-sleeve collared shirt with a chest pocket, dark trousers, black sandals, black crossbody shoulder bag. He carries a small pale beige clipboard (silver metal clip, exactly one white paper slip, black pen on a short string) in his right hand, and his plain unbranded dark-steel parcel bicycle (rear cargo rack, kickstand down, standing upright on it) appears with him in the wide/environment row; no logos, no readable text or brand marks anywhere"),
"Monkey":dict(role="the recurring vervet monkey", stype="creature", out="Character_Sheets/Vervet_Monkey_Character_Sheet_Skill_v3.png",
 notes="Two arms with two small dexterous black hands, five fingers on each hand. Two legs with two black feet. One long tail with a darker tip. Black face with a white brow band and pale cheek fur; grey-green coat with lighter chest fur. Cat-sized body, about 40-60 cm excluding the tail.",
 desc="A real wild vervet monkey (Chlorocebus pygerythrus): grey-green-tinged fur, black face with a white brow band and pale cheek fur, small dexterous black hands and feet, long tail, cat-sized body about 40-60 cm excluding tail. Plain neutral light-grey studio background in every panel except the movement/environment row (no pole or props in the studio panels). The monkey holds a clipboard in ONLY TWO panels: the key-feature close-up of its two hands gripping it, and the resting pose. In every other panel its hands are empty. The clipboard is realistically large for a monkey this size: a standard clipboard about 23 x 32 cm, roughly half the monkey's body length, with one white A4 sheet of paper covering the ENTIRE board face edge to edge under a silver clip, and a black pen on a short string. The movement pose is the monkey walking on the ground in its natural setting"),
}
k=sys.argv[1]; s=J[k]
p=build_character_sheet_prompt(s['desc'],s['role'],s['stype'],s['notes'])
open(f"Prompts/{k}-Character-Sheet-Skill-GPT-Image-2-v3.md",'w').write(f"---\nmodel: gpt-image-2\nparams: text-to-image, 16:9, 2K, NO reference images\nscript: Character-Sheet-Generation/scripts/character_sheet_generation.py (subject_type={s['stype']})\nsaved: 2026-09-20 BEFORE submission\n---\n{p}\n")
generate_character_sheet(s['desc'],Path(s['out']),s['role'],s['stype'],'16:9','2K',None,s['notes'])
print('done',k)
