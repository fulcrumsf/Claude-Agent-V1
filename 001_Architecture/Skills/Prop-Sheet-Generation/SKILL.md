---
name: prop-sheet-generation
description: Use whenever a video production has a recurring handheld/worn object that appears in more than one scene and needs to look and orient identically every time — "build a prop sheet", "prop reference sheet", "make a sheet for the sword/shield/tool", or any pipeline step generating shots where a character or creature holds or wears the same object across multiple scenes. Generates front/back/held-from-POV panels via GPT-Image-2, explicitly per-hand where relevant.
---

# Prop Sheet Generation

Generates a single reference-sheet image locking a recurring prop's appearance across every orientation a shot might actually show — front, back, and how it's physically held or worn. One sheet per production covering all its recurring props (not one sheet per prop) — see usage below.

Production-proven origin: generalizes `prop_sheet_generation.py` from `Reimagined_Realms_POV_Shorts_Pipeline_v2`, built after two confirmed real failures on the Roman Gladiator production (see "Why every orientation matters" below). Applies to any channel with recurring physical objects, not just POV human productions.

## Before using this skill

Read [`GPT-Image-2-Prompting-Guide`](../GPT-Image-2-Prompting-Guide/SKILL.md) first for the underlying model's prompting conventions.

## Why every orientation matters (the failures this fixes)

1. **Front-only sheet → backwards prop on screen.** A shield sheet showing only its decorative front face caused every scene needing that shield in-hand to render it backwards — a held shield's front always faces *away* from the person carrying it; true first-person view only ever sees the back/strap side with the forearm threaded through it. The model had no other reference to work from, so it guessed wrong every time.
2. **Generic "held" panel → wrong-hand anatomy.** A single unlabeled "held" panel produced a wrong thumb orientation on a shield that's always carried in the left hand — because the panel never said which hand, the model had a coin-flip chance of rendering right-hand grip anatomy onto a left-hand grip. Fixed by requiring `held_left`/`held_right` to always name the specific hand explicitly, never a generic "held" field.

Both are now hard requirements in this skill, not optional polish.

## Usage

```bash
python3 scripts/prop_sheet_generation.py <props.json> \
  --out "<production_folder>/Images/Prop_Sheets/<Production>_Props.png" \
  --input_urls <optional character sheet URL, for consistent hand/arm in held panels>
```

`props.json` — a list of prop dicts:
```json
[
  {
    "name": "Gladius Sword",
    "front": "double-edged steel blade, bone grip, bronze pommel",
    "held_right": "gripped upright in a right fist, blade angled forward"
  },
  {
    "name": "Scutum Shield",
    "front": "curved rectangular shield, red field, gold eagle motif",
    "back": "unpainted wooden interior, horizontal grip bar, leather strap",
    "held_left": "left forearm threaded through the strap, palm wrapped around the grip bar"
  }
]
```

- `back` — omit only for props with no meaningful distinct back (e.g. a flat coin).
- `held_left` / `held_right` — omit whichever hand never actually carries this prop; **always name the specific hand explicitly**, never a generic "held" field.
- Front/back panels show the object alone, no hands. Held panels are the deliberate exception — object gripped/worn by the named hand, matching the production's character sheet.

## Rules enforced by the prompt itself

- Panel labels sit in a reserved blank margin strip beneath each panel — **never overlapping the image content** (per a direct correction: labels covering image content is unacceptable on any sheet type in this pipeline).
- All panels for the same object stay visually consistent with each other — same material, wear, color grade — as if genuinely the same physical item across every panel.
- No watermark, no panel borders.

## Feeding the sheet forward

Pass this sheet as an input reference (`reference_image_urls` / `@ImageN` ordinal tag) on any shot-generation call where the prop appears — see [`Seedance-Prompting-Guide`](../Seedance-Prompting-Guide/SKILL.md) for how multi-reference calls combine a prop sheet with character and storyboard references in one request.
