# Grounding Coverage Check — one checklist per generation call (Shot 06)
Facts source: Research/Plausibility_Facts.md (Phase 1 Q1-15 + Phase 2 table), Data/Site_Plan.md v2, Blocking_Plan.md.

## Call 1: Env panel, TOP-DOWN (Prompts/Env-Panel-2-TopDown-GPT-Image-2-v1.md)
| Fact | In prompt? |
|---|---|
| Brazilian gated condo service entrance, dusk, light drizzle | yes |
| Guardhouse ~4.5 m wide, flat concrete roof, awning projecting 2.5 m, slab ~6 m wide, drip line parallel to bay | yes |
| Slab dry/lighter, asphalt wet/darker | yes |
| Delivery bay ~4 m wide, near curb, sidewalk, lamp post + camera bracket at bottom center | yes |
| Grass verge ~4.5 m at RIGHT of slab, perimeter wall, flush ramp, no curb/step | yes |
| Motorcycle ~2 m, 150cc class, top-box, parked parallel to curb at lower-left, FRONT toward LEFT, on sidestand (left side) | yes |
| Streetlight (sodium/orange) + trees | yes |
| Tinted window / parcel drawer / window position | EXCLUDED here (plan view from above cannot show a facade; shown in eye-level/POV/landmark panels) |
| Courier, capybara, backpack, helmet | EXCLUDED (no people/animals in environment panels by skill rule; their positions are marked later by the deterministic renderer) |
| Camera height ~3 m, wide-angle, 2016 HD quality | EXCLUDED here (plan view; applied to the POV panel) |
| Scale (motorcycle 2 m, slab 2.5x6, verge 4.5) | yes |

## Call 2: Env panel, TOP-DOWN v2 (Prompts/Env-Panel-2-TopDown-GPT-Image-2-v2.md), edit of v1 with the real Honda CG photo
| Fact | In prompt? |
|---|---|
| Everything from Call 1, reproduced identically from the approved v1 layout | yes (reference image 2) |
| Motorcycle = Honda CG 150 Titan-class commuter styling, top-box, front toward LEFT, on sidestand (left side), no logos | yes (reference image 1 named as the exact model) |
| Fix reason: era/region-appropriate form (v1 rendered a sporty naked bike) | yes |
Result: v2 accepted (bike is CG-like, layout unchanged).

## Call 3: Env panel, EYE-LEVEL (Prompts/Env-Panel-3-EyeLevel-GPT-Image-2-v1.md)
| Fact | In prompt? |
|---|---|
| Guardhouse facade, tinted window 1.4 m / sill 1.1 m, parcel drawer, buzzer panel | yes |
| Awning 2.5 m, drip line straight and parallel, dry lighter slab, cool-white light under awning | yes |
| Wet asphalt bay reflecting sodium streetlights; drizzle | yes |
| Verge + shrubs + perimeter wall RIGHT of slab, flush ramp, no curb/rail/step | yes |
| Streetlight, trees, twilight sky | yes |
| Motorcycle | EXCLUDED on purpose (separate prop; own sheet) |
| Courier, capybara, backpack, helmet | EXCLUDED (no people/animals in environment panels) |
| Camera height 3 m / wide-angle / 2016 quality | EXCLUDED here (eye-level reference at 1.6 m; applied in the POV call) |

## Call 4: Env panel 1, CAMERA POV (Prompts/Env-Panel-1-CameraPOV-GPT-Image-2-v1.md)
| Fact | In prompt? |
|---|---|
| Fixed CCTV on a lamp-post bracket at the near curb, ~3 m high, facing the guardhouse across the bay, slight downward tilt, ~80 deg wide-angle, mild barrel distortion | yes |
| 2016 HD IP quality (compression, noise), dusk colors, no text/timestamp | yes |
| Frame layout: bay foreground, guardhouse center-left with window/drawer/awning/slab, drip line horizontal, verge+wall at right, flush ramp | yes |
| Light drizzle, wet outside awning, dry slab under it | yes |
| Straight awning edge; slab not a wedge (named failure shape) | yes |
| Motorcycle, courier, capybara | EXCLUDED (unpopulated plate) |

## Call 5: Env panel, REVERSE (Prompts/Env-Panel-4-Reverse-GPT-Image-2-v1.md) [spatial reference only]
| Fact | In prompt? |
|---|---|
| Viewpoint on the dry slab beside the window looking back across the bay to the near curb | yes |
| Awning underside + fluorescent light, slab, straight drip line, wet bay, curb, sidewalk | yes |
| Lamp post + camera bracket at the near sidewalk center, pointing at the viewer | yes |
| Verge + shrubs + wall now at the LEFT edge, flush to slab (mirror consequence of turning around) | yes |
| Twilight, sodium light, faint drizzle | yes |
| Explicitly "spatial reference only, not camera output" | yes |
| Motorcycle, people, animals | EXCLUDED |

## Call 6: Env panel, LANDMARK DETAIL board (Prompts/Env-Panel-5-LandmarkDetail-GPT-Image-2-v1.md)
| Fact | In prompt? |
|---|---|
| Service window 1.4 m / sill 1.1 m, parcel drawer, buzzer panel, awning light | yes (cell 1) |
| Slab-to-verge flush ramp, NO curb/rail/step, shrubs, wall corner | yes (cell 2) |
| Motorcycle: Honda CG 150 commuter (real photo ref), top-box, LEFT side view, FRONT wheel LEFT, sidestand, wet asphalt, no logos | yes (cell 3) |
| Lamp post + CCTV bracket + sodium streetlight | yes (cell 4) |
| Dusk drizzle lighting | yes |
| Courier, capybara, backpack, helmet | EXCLUDED (no people/animals/character props in the environment board) |

## Call 7: MOTOBOY character sheet (Data/Motoboy_Sheet_Spec.json -> Prompts/Motoboy-Character-Sheet-Spec-v1.md)
| Fact (Plausibility_Facts) | In prompt? |
|---|---|
| Adult Brazilian man, late 20s-30s, 2016 Sao Paulo motoboy, ~1.70 m, lean/average | yes |
| Gear: reflective-stripe jacket, jeans, sneakers, gloves in pocket, plain black insulated backpack ~40 cm | yes |
| Open-face matte-black helmet with reflective strip, held in RIGHT hand at start, put on at the end | yes (description + extra panels) |
| Unbranded: no logos, no readable text, no delivery-company marks | yes |
| Natural-setting pose: under a concrete guardhouse awning at dusk in drizzle | yes |
| Hands: LEFT and RIGHT separate close-ups (spec hands=both) | yes |
| Motorcycle | EXCLUDED here (own prop sheet; parked at the curb, not on his sheet) |
| Capybara, guardhouse details | EXCLUDED (other sheets) |

## Call 8: CAPYBARA creature sheet (Data/Capybara_Sheet_Spec.json -> Prompts/Capybara-Creature-Sheet-Spec-v1.md)
| Fact | In prompt? |
|---|---|
| Adult, ~50 kg, ~1.2 m long, ~0.55 m at the shoulder | yes |
| Coarse tawny reddish-brown coat, darker head/ears, paler belly | yes |
| Barrel body, blunt squarish snout, high-set nostrils/eyes, small rounded ears, NO visible tail | yes |
| Toes: 4 front / 3 hind, slightly webbed (countable anatomy) | yes (anatomy_notes baked on the sheet) |
| Damp fur (drizzle) | yes |
| Lying-down pose on flat concrete (the shot's key action) and grazing on grass verge (frame-1 pose) | yes (extra panels) |
| Not sheltering from rain (behavior note) | n/a to an image sheet; carried in Blocking_Plan/video prompt |

## Call 9: MOTORCYCLE prop sheet (Data/Motorcycle_Prop_Spec.json -> Prompts/Motorcycle-Prop-Sheet-Spec-v1.md), after the character sheets per Prop Routing
| Fact | In prompt? |
|---|---|
| Honda CG 150 Titan-class commuter: round headlight, flat seat, silver tank/side covers, chrome-and-black engine, spoked wheels (real photo labeled as reference 1) | yes |
| Small plain black rear top-box on the rack | yes |
| No logos / readable text | yes |
| LEFT side faces the camera in the shot; FRONT wheel toward the LEFT of that panel; sidestand down on the left side; leaning toward the viewer | yes (extra panel) |
| RIGHT side panel (front wheel toward the right, no sidestand visible) | yes (extra panel) |
| Front and rear views | yes |
| Wet dark asphalt / drizzle | yes (left-side panel) |
| Held/worn panels showing a hand | none (not needed; no holder_reference required) |

## Call 9b: MOTORCYCLE prop sheet v2 (Data/Motorcycle_Prop_Spec_v2.json)
v1 was accurate (left side: front wheel LEFT + sidestand; right side; front; rear) but the model invented two "held from POV" handlebar panels with a light-skinned generic hand (not the motoboy's). Fix: sheet_spec.py now appends "no hand/arm/held-from-POV panels, object-only" to any prop spec with no held panel. All Call 9 facts unchanged.
