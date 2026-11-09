# Portal — Directory

Local Ikigai portal + listing pipeline (FastAPI, SQLite, Docker). Input: `../Pipeline_Docs/Ikigai_Portal_Pipeline_Brief.md`.

- `app/` — dashboard shell (`main.py`), Ikigai Studio module (`studio.py`), idea pool logic (`ideas.py`), taste profile (`taste.py`), chat window (`chat.py`), chat brain via headless Claude CLI with validated dashboard actions (`assistant.py`), sales channels (`channels.py`), research import CLI (`import_ideas.py`), image engines on kie.ai (`engines.py`), stage 2 idea-to-art (`art.py`: style cards, prompt writer, rounds, picks, approval, oversight log), stage 3 upscale + resize for the Art tab (`prints.py`), `pipeline/` step runner + steps (generate_art check, upscale, resize, mockups built; package / listing_text / etsy_draft still stubs); Production tab (stage 4, 2026-11-08): `production.py` (cards, tags, one job at a time, Archive moves), `room_slots.py` (slot plan + art-to-room compatibility + ratio weights), `scene_templates.py` (AI scene -> insert corners -> PhotoCraft PSD -> auto-saved template; manifests for Tony's PSDs)
- `data/Taste_Profile.md|json` — auto-written taste profile the research job reads (git-ignored with the DB)
- `config/` — engines (kie.ai models, credits, default), style cards + chip groups (`style_cards.json`), print sizes (verified 2026-11-05 against 00120 Pastel Waves), pipeline steps, settings
- `tests/` — pytest
- `data/` — local DB and output (git-ignored); generated art in `data/art/<idea_id>/`, upscaled masters in `data/upscaled/<idea_id>/` (both made at runtime)
- `../Designs/<NNNNN>-<Name>/01-Printables/` — the 5 print JPGs written by the resize step (one folder per design)
