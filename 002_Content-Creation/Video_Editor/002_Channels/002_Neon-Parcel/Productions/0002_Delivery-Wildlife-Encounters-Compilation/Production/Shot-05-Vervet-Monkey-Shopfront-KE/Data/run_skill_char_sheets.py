import sys
from pathlib import Path
sys.path.insert(0,'/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Character-Sheet-Generation/scripts')
from character_sheet_generation import build_character_sheet_prompt, generate_character_sheet
PROP="Character_Sheets/Props_Sheet_Skill_v1.png"
REF=("Reference image 1 is the approved prop sheet: use it ONLY for the exact design of the pale beige clipboard "
     "(silver metal clip, exactly one white paper slip, black pen on a short string) wherever the clipboard appears in this sheet; "
     "it is not a reference for any person or animal. ")
J={
"Courier":dict(role="the bicycle parcel courier", stype="person", out="Character_Sheets/Courier_Character_Sheet_Skill_v1.png", notes="",
 desc=REF+"An adult East African man in his late 20s to 30s, average build, plain navy short-sleeve collared shirt with a chest pocket, dark trousers, black sandals, black crossbody shoulder bag, carrying the pale beige clipboard from reference image 1 in his right hand; no logos, no readable text or brand marks anywhere"),
"Monkey":dict(role="the recurring vervet monkey", stype="creature", out="Character_Sheets/Vervet_Monkey_Character_Sheet_Skill_v1.png",
 notes="Two arms with two small dexterous black hands, five fingers on each hand. Two legs with two black feet. One long tail with a darker tip. Black face with a white brow band and pale cheek fur; grey-green coat with lighter chest fur. Cat-sized body, about 40-60 cm excluding the tail.",
 desc=REF+"A real wild vervet monkey (Chlorocebus pygerythrus): grey-green-tinged fur, black face with a white brow band and pale cheek fur, small dexterous black hands and feet, long tail, cat-sized body about 40-60 cm excluding tail. The key feature for this production is its hands gripping the clipboard from reference image 1; the movement pose is climbing a vertical weathered rusty steel post"),
}
k=sys.argv[1]; s=J[k]
p=build_character_sheet_prompt(s['desc'],s['role'],s['stype'],s['notes'])
open(f"Prompts/{k}-Character-Sheet-Skill-GPT-Image-2-v1.md",'w').write(f"---\nmodel: gpt-image-2\nparams: image-to-image, 16:9, 2K\nreference_images: 1 = {PROP} (prop sheet, clipboard design only)\nscript: Character-Sheet-Generation/scripts/character_sheet_generation.py (subject_type={s['stype']})\nsaved: 2026-09-20 BEFORE submission\n---\n{p}\n")
generate_character_sheet(s['desc'],Path(s['out']),s['role'],s['stype'],'16:9','2K',[PROP],s['notes'])
print('done',k,s['out'])
