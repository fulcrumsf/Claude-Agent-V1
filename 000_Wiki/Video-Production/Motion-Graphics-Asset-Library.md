# Motion Graphics Asset Library — Cross-Production Index

Running index of reusable isolated component assets (true-alpha or chroma-matted) built for motion-graphics/diagram compositing, across every channel and production. Check here before generating a new component asset — a recurring element (an icon, a recurring diagram piece, a reusable background texture) should be reused, not regenerated from scratch.

Built alongside the [`Motion-Graphics-Compositing`](../../001_Architecture/Skills/Motion-Graphics-Compositing/SKILL.md) skill. Each production also keeps its own `Production/Motion_Graphics_Asset_Library.json` (structured, per-production detail); this page is the human-readable, cross-production search surface — graphified for `graphify query` retrieval.

**How to use:** searching for an asset? Check the table below first. Building a new one? Add a row here once it's locked, linking back to its file in the production folder.

---

## Anomalous Wild

### 0002 — Mantis Shrimp Color Vision

| Asset | Subject | Style-lock reference | Matte method | Path |
|---|---|---|---|---|
| Mantis_Eye_External | Mantis shrimp compound eye, external view, rainbow-faceted | `Scene_02_Diagram.png` | Recraft AI matte (near-black source bg) | `002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/0002_Mantis_Shrimp_Color_Vision/Images/Diagrams/Scene_02_Components/Alpha/Mantis_Eye_External.png` |
| Human_Eye_External | Human eye, external close-up, green iris | `Scene_02_Diagram.png` | Recraft AI matte (near-black source bg) | `.../Scene_02_Components/Alpha/Human_Eye_External.png` |
| Human_Eye_CrossSection | Human eyeball anatomical cutaway | `Scene_02_Diagram.png` | Recraft AI matte (near-black source bg) | `.../Scene_02_Components/Alpha/Human_Eye_CrossSection.png` |
| Mantis_Receptor_Fan | Mantis shrimp 16-photoreceptor fan cross-section | `Scene_02_Diagram.png` | Recraft AI matte (near-black source bg) | `.../Scene_02_Components/Alpha/Mantis_Receptor_Fan.png` |

**Note (2026-08-18):** these 4 assets were built before the chroma-screen / native-transparent method order was locked in the Motion-Graphics-Compositing skill spec — they use the "last resort" near-black + Recraft-matte method (Step 3, method 3), left as-is per Tony's instruction (they look correct as built). Future Anomalous Wild diagram assets should try native transparent generation first, then chroma-screen, per the skill's documented order.

---

*(Add new productions/rows here as they're built — one section per channel, one sub-section per production.)*
