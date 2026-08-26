---
name: environment-sheet-generation
description: Use whenever a video production has a location that appears in more than one scene and needs to look identical every time — "build an environment sheet", "location reference sheet", "make a sheet for the burrow/reef/palace", or any pipeline step generating shots set in the same recurring location across multiple scenes. Generates one people/creature-less panel per scene set there via GPT-Image-2 — never one generic room shot.
---

# Environment/Location Sheet Generation

Generates a single reference-sheet image locking a recurring location's appearance — but structured per-scene, not per-location-in-general. One sheet per location, with exactly one panel for each scene that happens there.

Production-proven origin: generalizes `environment_sheet_generation.py` from `Reimagined_Realms_POV_Shorts_Pipeline_v2` (v2 revision, built after two confirmed real failures — see below). Applies to any channel with a recurring setting, not just POV human productions — e.g. Anomalous Wild's reef burrow, palace throne room, whatever recurs across a production's scenes.

## Before using this skill

Read [`GPT-Image-2-Prompting-Guide`](../GPT-Image-2-Prompting-Guide/SKILL.md) first for the underlying model's prompting conventions.

## Why one panel per scene, never a single generic shot (the failures this fixes)

The original v1 approach — one shared reference image per location — failed twice on a real production:

1. **Merging two scenes into one shared panel silently dropped an action.** A door-push scene got skipped entirely when merged with the "already inside" scene next to it — the panel showed the aftermath, not the actual physical moment.
2. **A panel meant to be an empty room reference had crowd figures and hands creep in**, even though nothing in the prompt asked for people.

Both are fixed by structuring the sheet as **one panel per scene**, never merged or reused, with people/creatures explicitly excluded by default.

## Usage

```bash
python3 scripts/environment_sheet_generation.py <location.json> \
  --out "<production_folder>/Images/Environment_Sheets/<Location>_Sheet.png"
```

`location.json`:
```json
{
  "location": "the mantis shrimp's reef burrow",
  "scenes": [
    {"scene": 1, "description": "wide establishing shot, burrow entrance at dusk"},
    {"scene": 6, "description": "close angle at the burrow mouth, raptorial claw visible in frame"}
  ]
}
```

- One entry per scene set in this location — **never merge two scenes into one panel, even if they're similar.** A real camera never holds the exact same framing twice; each panel must show a visibly different angle, zoom, or height.
- Each panel shows the scene's actual physical action moment, not its aftermath (a door mid-push, not the already-open room beyond it).

## Rules enforced by the prompt itself

- **No people, no hands, no arms, no held objects, no animals/creatures in any panel by default** — these are pure empty-location camera references. The one exception: a location reference that's deliberately meant to include a stationary environmental creature (e.g. background reef life for an underwater establishing shot) — state that explicitly per-panel in the scene description if needed, otherwise assume none. Practice dummies/mannequins are fine, they're not people.
- Panel labels (scene number only) sit in a reserved blank margin strip beneath each panel — never overlapping the image content.
- Consistent style/lighting across every panel, as if genuinely the same physical location.
- No watermark.

## Feeding the sheet forward

Pass the relevant panel (or the full sheet, cropped to the needed scene) as an input reference on any shot-generation call set in that location — see [`Seedance-Prompting-Guide`](../Seedance-Prompting-Guide/SKILL.md)'s environment reference section for both the pre-compositing approach (environment + character composited into one starting frame before Seedance runs) and the direct tagged-reference approach (environment passed as its own `@ImageN` alongside character sheets in one Seedance call).
