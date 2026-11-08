# Room_Templates

Reusable room-mockup templates for Ikigai listing images (slots 8-19), rendered headless with photocraft-cli.

Each room lives in its own folder: `<NN>_<Room_Name>/`
- `Room_Template.psd`: the layered PhotoCraft template (art smart object "Place Artwork Here", mat, frame, shadow, glass and wall-colour layers, switched by name)
- `template.json`: corners, smart-object size, light side, layer names
- the room plate image

Approved by Tony 2026-11-07 (path `005_Ecommerce/Etsy-Ikigai/Room_Templates/`). PSDs and images are git-ignored (large); `template.json` and this file are committed. Style rules: `../Mockup_Style_Guide.md`. Code: `../Portal/app/rooms.py`, `../Portal/app/frames.py`.
