# Reference Examples — Diagram / Label / Callout Aesthetic

Visual references for how diagram labels, callouts, and supporting graphics should
look. Inspiration targets, not pixel-exact specs. Check these before building a
diagram's motion graphics (`DiagramLabels.tsx`, `SceneOverlay.tsx`, camera
blocking).

Established from the 0003 Glass Frog edit review, 2026-08-31 / 09-01.

## Files

| File | Type | What it shows |
|---|---|---|
| `Label_Aesthetic_Red_Blood_Cells.png` | ✅ **TARGET** | GPT-Image-2 reference (Tony). Large clean white sans-serif term ("RED BLOOD CELLS"); parenthetical qualifier in a subject-derived accent colour ("(awake)" red); thin white leader line, one right-angle bend, small end dot; soft glowing halo/ring at the feature; short 2–3 line white description; high contrast from size/weight/glow, **no backing plate**. Restrained editorial "science-doc" tone — not gamer-HUD, not neon. |
| `Anti_Example_Labels_And_Callout_Crystal_Pouch.png` | ❌ **AVOID** | Glass Frog scene 03, current build. Two failures in one frame: (1) "Guanine Crystal Surface" / "Mirrored Pouch" labels are tiny, thin, low-contrast, and stacked almost on top of each other; (2) the green "MIRRORED ORGAN POUCHES" callout blends into the blue crystals with no backing plate. |
| `Anti_Example_Range_Map_No_Background.png` | ❌ **AVOID** | Glass Frog scene 04, current build. A lone green zigzag line + bottom caption on near-black where a real regional map (S. Mexico → Central America → Andes → Amazon) should sit underneath. Geography beats need a real map asset, sourced in research. |

## Rules these references lock in

Full written rules: `../SKILL.md` (Label & Callout Aesthetic section) and
`002_Content-Creation/Video_Editor/003_Remotion/src/skills/design-rules-learned.md`.

1. **Label style:** white sans-serif term; subject-accent qualifier; thin leader
   line + end dot; soft glowing target dot; optional short description. Contrast
   from size / weight / glow. Sized to read comfortably at 1080p — the Glass Frog
   labels were ~1.5x too small.
2. **Label spacing:** stacked labels keep a minimum vertical gap; offset the text
   boxes (not the leader targets) so text never collides.
3. **Coloured callouts** (brand green, etc.): reusable backing plate — 50% black
   `rgba(0,0,0,0.5)`, small even padding tracking the text size, eases in/out in
   sync with the text. Built into the `callout` component, applied to every
   instance automatically.
4. **Camera holds still while any label is on screen.** Blocking pattern:
   move → settle → label in → hold → label out → move. All camera moves slow
   ease-in / ease-out.
5. **Geography / real-place / route / range beats need a real map asset** —
   sourced by the research phase (Production-Research-Agent) and handed to the
   motion-graphics build. A synthetic stylized line on black is not acceptable as
   the only visual; the animated path must trace the real geography on the map.
