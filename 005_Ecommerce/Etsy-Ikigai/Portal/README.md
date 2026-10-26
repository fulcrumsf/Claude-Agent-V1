# Ikigai Portal (scaffold)

Run locally: `pip install -r requirements.txt && python -m app.seed && uvicorn app.main:app --port 8800`, or `docker compose up --build`. Tests: `pytest`.

## Status
Working: 10-idea list, approve/deny with instant refill from pool, pool-low warning, prompt on approve, engine dropdown from config, step tracker per listing.
Stubs (raise NotConfigured, step shows "blocked"): art engines, Upscayl, PhotoCraft mockups, resize, Drive/PDF package, listing text, Etsy draft.

## Connect on the Mac, in this order
1. PhotoCraft CLI: prove it opens the mockup PSDs headless (`steps.mockups`).
2. Upscayl CLI (`steps.upscale`).
3. Verify the 5 print sizes from a live listing (`config/print_sizes.json`), then `steps.resize`.
4. Supply PDF + description templates, Drive credentials (`steps.package`, `steps.listing_text`).
5. Engine adapters (`engines.run_prompt`), `.env` keys.
6. Etsy developer app, then `steps.etsy_draft`.
Also pending: research job feeding `ideas.add_to_pool`, performance feedback into idea scoring, Frame TV variant, fidelity check on AI room mockups.
