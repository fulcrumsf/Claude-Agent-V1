# Session Handoff, 2026-11-15 (Claude Code, later part), PhotoCraft generative fill: OpenFill installed, Nano Banana chosen as default

Written for the next session. Read this first. Earlier handoff the same day (Docker, Cloudflare, n8n cleanup): `2026-11-15_Session-Handoff_Claude_Docker-Cloudflare-N8N-Cleanup-And-Ikigai-Decisions.md`.

## What Tony wants (the goal)
Replace the Photoshop subscription's Generative Fill, **manually, inside PhotoCraft**:
1. Draw a **square (rectangular) selection** around an item.
2. **Right-click, choose "Generative Fill".**
3. A **text box** appears; he types what he wants (remove it, replace with X, etc.).
4. The result comes back as a **new masked layer**, in seconds to about a minute, not minutes.
It must behave like Photoshop: speed, quality, shadows. Later the same engine should power the Ikigai Portal "Edit with chat" (templates, maybe artwork).

## DECISION: Nano Banana 2.1 on kie.ai is the default engine
Tested 2026-11-15 on the Ikigai living-room template (stool and lamp). Cloud edit models beat every local engine:
- **kie.ai Nano Banana 2.1 (about $0.03 a call, 30 to 50 s)** is the best: old shadow gone, new object gets a believable shadow matching the window light, art frame and wall untouched, crisp result. Nano Banana Pro was slightly worse (turned the baseboard into white molding, faded eucalyptus tips). fal Nano Banana Pro is fastest (about 25 s) but costs more.
- **The method that makes it work:** send a **wide crop** (about 1200 x 800 including the floor and wall where a shadow falls), put the shadow request in the instruction, and composite the result back through a **wide soft mask** (object plus shadow zone). Everything outside the mask stays the original pixels (0 pixels changed outside in every run). Tight crops were what clipped shadows earlier. The model redraws the whole crop but we keep only the masked part.
- **Removal with a long shadow:** Ideogram object removal (fal, about $0.03) removed the stool's whole shadow; Bria Eraser (fal, about $0.04) did not (only the contact shadow) but is clean and fast (about 6 s) for lamps. Difference-image trick works with Ideogram: pixels that got brighter outside the mask and touch the object give an automatic old-shadow mask.
- **Local engines stay as the free fallback:** LaMa (removal, about 5 s), FLUX.2 klein 4B (about 70 to 80 s with grow, not good for lamp to vase), Qwen Image Edit Lightning (about 160 s, best local quality).
- Cloud spend this session: about $1.20 total (kie.ai credits left about 605 of 701.7 before the Nano test; check balance). Eraser test cost $0.15 vs the $0.07 quoted (Bria tested in two modes), told Tony.

## What is installed and working
- **PhotoCraft 0.23.1** in /Applications/PhotoCraft.app (the old ArtCraft 0.5.0 used by the Ikigai Portal is untouched, leave it).
- **OpenFill 0.2.6** patched, launch with `~/Applications/PhotoCraft with OpenFill.app`. Panel has a Model pull-down: local (klein default for Fill, Qwen Edit Lightning, stock Qwen, LaMa default for Remove, DreamShaper) and cloud (kie.ai Nano Banana Pro/2.1, Ideogram 3 Edit; fal.ai Qwen inpaint, Nano Banana Pro). Cloud entries only got a crop and clip back to the selection, which is why they lost on shadows; the wide-crop flow above is NOT yet built into the panel.
- ComfyUI (Pinokio, `/Users/tonymacbook2025/pinokio/api/comfy.git/app`) has the models: Qwen Image Edit 2511 Q4_K_M GGUF + Lightning 4-step LoRA, qwen vae + text encoder, LaMa in `models/inpaint/`, DreamShaper 8, FLUX.2 klein 4B, SAM 3.1 (runs on the Mac GPU; "lamp" selects a lamp in about 4 s).
- Patch additions made this session to OpenFill (in `001_Architecture/Tools/Image-Generation/OpenFill_AgentOS_Engines.patch`, applier `openfill_agentos_patch.py`): engine pull-down; **grow fix** (`grow_object_percent`, default 40, "Allow object to grow (%)": a prompted fill may paint past the selection); **LaMa pre-removal** of the old object (`preremove_object`); **room for new shadow** (`shadow_reach_percent`, default 100, "Room for new shadow (%)", picks light direction from the brightest area). SAM bridge: `001_Architecture/Tools/Image-Generation/photocraft_sam_select.py` (typed word to PhotoCraft selection, script only, no button).

## Measured (M3 Max 36 GB)
LaMa remove 4 to 6 s; klein fill 30 s small, 70 to 80 s with grow; Qwen Lightning about 160 to 170 s; stock Qwen about 18 min (do not use); Nano Banana 2.1 30 to 50 s; Ideogram 29 s; Bria 6 s; SAM "lamp" 9 s end to end. Quit Docker Desktop before Qwen (12 to 14 GB swap seen).

## NEXT STEPS (in this order)
1. **Build the Nano Banana wide-crop flow into the panel as the default engine** (kie.ai Nano Banana 2.1): rectangular selection, auto wide crop around it (include floor/wall so shadows fit), instruction text from the panel text box, composite through a wide soft mask, original pixels outside. Reuse the scripts from the test (scratchpad `scripts/nano_test.py`, `nano_layers.py`, `eraser_test.py`; they are in `/private/tmp/claude-501/.../scratchpad/scripts`, copy anything worth keeping into `001_Architecture/Tools/Image-Generation/`). Optional second step: Ideogram removal plus the difference-image shadow mask when a long old shadow must go.
2. **Right-click "Generative Fill" with a text box inside PhotoCraft.** NOT YET RESEARCHED. OpenFill today is a separate panel (web page, `page-url.txt`, `web.py`) next to PhotoCraft, not a context-menu item. The XP bar/fork Tony first saw is Windows-only. First find out whether PhotoCraft 0.23.1 can host a context-menu command or a docked panel with a text box via its control protocol (`--control`, `edit.*` commands), a plugin/action mechanism, or whether the practical form is a panel plus keyboard shortcut. Do this before promising Tony a right-click item, and tell him plainly what is possible.
3. **Keep the protect-the-art-frame idea:** subtract the SAM-measured art frame (`Portal/app/sam_frames.py`) from every area the fill may change (cheap reliable fix for the frame artifacts Tony saw).
4. **Blur at the top of new objects (local engines):** crop-and-stitch at the model's native size, mask growth upward, light second pass on the new object only. Lower priority once Nano Banana is the default.
5. **Ikigai Portal "Edit with chat"** generative fill and the amber test card are still not built (Tony approved the amber tint earlier).
6. PhotoCraft's own **Edit > Content-Aware Fill** exists but is early (issue storytold/photocraft#14190, bands and stripes not continued, not scriptable). Not AI, cannot fix shadows. Optional quick test for plain wall/floor removals only, if Tony asks.

## Tony's assessments (his words, summarized)
- Stool (local Qwen): object works, shadow still broken. Vase: better, slightly blurry at the top, artifacts appeared on the mock-up art frame. Grow fix was "80% better".
- He wants no folder of unlabeled images: show one labeled comparison, not file lists. A labeled comparison was sent (`Compare_Results.png` in the scratchpad).

## State: uncommitted
- Committed earlier: `ad71c668` (OpenFill patch, SAM bridge, plan, TOOLBOX, Tool_Catalog, first results). **Not committed since:** grow fix, shadow work, regenerated patch, `Research/Shadow_Aware_Fill_Research.md` (new, with test results appended), TOOLBOX.md and plan Results addenda, this handoff. Commit these (not `.obsidian/*`, `Skills/.system/*`, `Tool-Manager/data/model_catalog.json`, `.tmp.driveupload/`, `Skills/gepeto/`, which belong to other work).
- Open PhotoCraft documents: LVRM_grow_test, LVRM_shadow_test, LVRM_nano_test, LVRM_eraser_test (labeled layers, best visible, rest hidden). LVRM_test_copy, LVRM_cloud_copy, LVRM_expand_copy were closed during a test run and their layers are lost unless Tony saved them (the original template is untouched). Crops live in `~/Library/Application Support/OpenFill for PhotoCraft/exchange/` (Nano_Test_*, Eraser_Test_*, Shadow_Test_*, Grow_Test_*).
- Optional cleanup for Tony to delete: e2e-*.png and sam-*.png in that exchange folder, and `agentos_test` / `agentos_sam` in ComfyUI `output/`.

## Gotchas
- Agents never delete files or create folders on their own (fs_guard); put work in existing folders.
- Never print keys or tokens. The build agent once printed OpenFill's local panel key from a log (local-only, harmless). Cloud keys: kie.ai and fal.ai in `~/.mcp-secrets.env`.
- Report cloud spend honestly and stay near what Tony approved.
- Hide irrelevant to-dos (n8n is backup only), keep answers short and plain, verify claims by looking at the result images yourself before saying it works.
- Research findings and licence notes (do not use ObjectClear, OmniEraser, OmniPaint, FLUX Kontext/FLUX.1 Fill: non-commercial; OSOR-SDXL is commercial-safe but Nvidia only, needs a Mac port) are in `005_Ecommerce/Etsy-Ikigai/Research/Shadow_Aware_Fill_Research.md`.
