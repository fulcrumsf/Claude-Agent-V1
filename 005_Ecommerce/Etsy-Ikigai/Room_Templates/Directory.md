# Room_Templates

Reusable room-mockup templates for Ikigai listing images (slots 8-19), rendered headless with photocraft-cli.

Each room lives in its own folder: `<NN>_<Room_Name>/`
- `room.json`: manifest read by the Portal (furniture tone, frame layers, lights with rank and suited moods)
- `Room_Template_<light>.psd` + `template_<light>.json`: one layered PhotoCraft template per light (art smart object "Place Artwork Here", mat, frame, shadow, glass and wall-colour layers, switched by name)
- `template.json`: corners, smart-object size, light side, layer names
- the room plate image

Approved by Tony 2026-11-07 (path `005_Ecommerce/Etsy-Ikigai/Room_Templates/`). PSDs and images are git-ignored (large); `template.json` and this file are committed. Style rules: `../Mockup_Style_Guide.md`. Code: `../Portal/app/room_templates.py` (renders looks), `frames.py`, `walls.py`. Authoring scripts sit in each room folder (`build_template_v2.py` + `build_template.py`, `kie_edit.py`, `quads.py`, `soften_light.py`). `Cache_*.png` files are layer exports made on first render (safe to regenerate).

`Tony_Portrait_Templates/`: copy of Tony's own Photoshop portrait room mockups (originals in iCloud, never touched), standardised 2026-11-08: 44 templates, every art layer named `Place Artwork Here`, filed by nearest standard ratio. Pick by nearest standard ratio, not exact slot ratio; table, layer structure and picker weighting in its `Directory.md`.
