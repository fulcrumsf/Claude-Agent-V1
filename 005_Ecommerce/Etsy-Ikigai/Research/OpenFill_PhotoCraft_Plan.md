# OpenFill in PhotoCraft: Plan (2026-11-15)

Goal: Photoshop-style generative fill on Tony's Mac (M3 Max, 36 GB). Tony selects an area in PhotoCraft, types a prompt or presses Remove, and the result comes back as a new masked layer. Installed and tested 2026-11-15: see `## Results` at the bottom for what runs, timings and the patch.

Sources: OpenFill repo (commit e3fa1e1, 2026-11-08; OpenFill for PhotoCraft 0.2.6), PhotoCraft repo and release notes v0.17 to v0.23.1, the local Pinokio ComfyUI, and the Ikigai Portal code.

## What we found (short)

- **Versions.** OpenFill 0.2.6 is tested on PhotoCraft 0.12 to 0.20.2. Nothing upstream says 0.21 to 0.23.1 breaks it. There are three risky changes:
  - **0.21:** new TIFF "Save Transparency" option. OpenFill reads your selection from a TIFF alpha channel.
  - **0.23.0:** "ordered automation read roots" and save provenance. OpenFill opens and saves files through the automation roots.
  - **0.23.0:** Save in the unsaved-changes prompt now counts as an automation save.
- **The PhotoCraft you already have is a different app.** It lives at `/Applications/ArtCraft/PhotoCraft.app` and reports version 0.5.0 (the ArtCraft bundle, built Oct 8). OpenFill only looks in `/Applications/PhotoCraft.app` or `~/Applications/PhotoCraft.app`. Install the upstream DMG there, and leave the ArtCraft copy alone, because the Portal's "Open in PhotoCraft" uses it. Both copies share `~/Library/Application Support/Photocraft`.
- **OpenFill works with the Pinokio ComfyUI.**
  - Folder: `/Users/tonymacbook2025/pinokio/api/comfy.git/app`. It has `main.py` and `env/`, and OpenFill's folder check accepts `env`.
  - If something healthy already answers on 127.0.0.1:8188, OpenFill uses it and never starts a second copy. It only ever stops a ComfyUI it started itself, so it cannot clash with Pinokio.
  - If 8188 is down and "Start the AI engine with PhotoCraft" is on, OpenFill starts ComfyUI from that folder itself, without Pinokio's `PYTORCH_ENABLE_MPS_FALLBACK=1`. So turn that option off and always start ComfyUI from Pinokio.
- **Python.** The python.org Python 3.13 on PATH already has Pillow and Tk, so `install.sh` picks it up by itself. The Pinokio env (Python 3.10, Pillow, no Tk) also works as a fallback.
- **Models.** Fill and Expand use Qwen-Image-Edit 2511 Q4 (Apache-2.0). Remove uses LaMa (Apache-2.0). Create needs an SD model, because Qwen Edit cannot make an image from nothing. DreamShaper 8 Inpainting is 2 GB and CreativeML OpenRAIL-M, which allows commercial use. Stay away from FLUX Fill, MAT and the FLUX removal LoRA, which are non-commercial.
- **The Lightning LoRA you are downloading is not used by OpenFill.** OpenFill runs Qwen at 20 to 30 steps with cfg 2.5 and adds no LoRA (`app.py` `sampling()`, `workflow.py` `build_qwen_edit`). Expect minutes per Fill on Apple Silicon (step 6 measures it). The LoRA is still useful for the Portal path.
- **The LaMa copy in Docker cannot be reused.**
  - `/Users/tonymacbook2025/Documents/Docker/AI_Models/inpaint/big-lama/big-lama.ckpt` is the 410 MB training checkpoint.
  - OpenFill and its inpaint nodes need `models/inpaint/big-lama.pt` (205 MB TorchScript). Get it from OpenFill's model manager.
  - `models/inpaint/` does not exist in the Pinokio app yet. The model manager would create it. That is a new folder, so Tony must OK it first.
- **Where the Qwen files land.**
  - In Pinokio, `unet`, `vae` and `loras` are links into `~/pinokio/drive/drives/peers/d1794763467438/`. `text_encoders` is a real folder.
  - The file names match OpenFill's catalog exactly, so the model manager should show Qwen as installed with no second download.
  - At planning time the VAE and LoRA were present. The 13.2 GB unet and 9.4 GB text encoder were still downloading.

## Preconditions

1. The Qwen download is finished. Check that both files exist in Pinokio's models folder:
   - `unet/qwen-image-edit-2511-Q4_K_M.gguf` (13.2 GB)
   - `text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors` (9.4 GB)
2. At least 15 GB of disk is free. It was 90 GB at planning time.
3. Pinokio ComfyUI starts and answers on http://127.0.0.1:8188.
4. **Qwen runs at all on this Mac.** Test this in plain ComfyUI before OpenFill:
   - Load the stock "Qwen Image Edit 2511" template in the ComfyUI page and run one edit at 1024 px.
   - If it errors with an fp8 or Float8 message, or the image comes back black, add `--bf16-text-enc` to the `python main.py` line in `/Users/tonymacbook2025/pinokio/api/comfy.git/start.js`. The flag exists in this ComfyUI's `cli_args.py`. This changes Pinokio's config, so Tony must OK it.
   - If the image is still black, also add `--fp32-vae`.
5. Tony OKs the new folder `/Users/tonymacbook2025/pinokio/api/comfy.git/app/models/inpaint/` (for LaMa).

## Install steps (macOS)

1. **PhotoCraft 0.23.1** (latest).
   - Download from https://github.com/storytold/photocraft/releases/tag/v0.23.1 : `photocraft-0.23.1-macos-universal.dmg` (274 MB).
   - Check it against `SHA256SUMS.txt`, then drag `PhotoCraft.app` into `/Applications/` (not into `ArtCraft/`).
   - Open it once by hand to clear Gatekeeper, then quit.
2. **OpenFill for PhotoCraft 0.2.6.**
   - Download `openfill-photocraft-0.2.6.zip` from https://github.com/beckettharriman/openfill/releases/tag/photocraft-v0.2.6 and unzip it into the scratchpad or Downloads, not into the workspace.
   - In that folder run `sh install.sh`. This adds `~/Applications/PhotoCraft with OpenFill.app` and `~/Applications/Uninstall OpenFill for PhotoCraft.app`. It does not replace PhotoCraft or change file associations.
   - If `~/Applications` does not exist yet, the installer creates it. That is a new folder, so ask Tony first.
3. **Start ComfyUI from Pinokio.**
4. **Point OpenFill at the Pinokio ComfyUI.**
   - Open "PhotoCraft with OpenFill".
   - Panel, then **Choose folder**: `/Users/tonymacbook2025/pinokio/api/comfy.git/app`.
   - Gear, then **Engine**: turn off "Start the AI engine with PhotoCraft". Leave the address at `http://127.0.0.1:8188`.
5. **Models tab (gear, then Models).**
   - Qwen should show as installed. If it says "Needs extra parts", press **Install nodes**. This adds pinned ComfyUI-GGUF (city96 @ 6ea2651), comfyui-inpaint-nodes (Acly @ 5b76817) and openfill-nodes into `app/custom_nodes`, and opencv into `app/env`.
   - Get **LaMa** (0.2 GB) and, for Create, **DreamShaper 8 Inpainting** (2 GB).
   - Restart ComfyUI from Pinokio after any node install.

## Decide: stay on 0.23.1 or go back

Run these on PhotoCraft 0.23.1, in this order. Each needs a freehand Lasso selection, not a rectangle, so OpenFill's selection-from-TIFF path is really used.

| # | Test | Pass means |
|---|---|---|
| A | **Remove** with LaMa on a small object | The new layer has a mask that matches the lasso, the original layers are untouched, and one Edit > Undo removes the whole result. It takes seconds, so it tests the PhotoCraft bridge without waiting on Qwen. |
| B | **Fill** with Qwen, prompt "a small green plant in a pot" | Same checks as A, and the fill sits only inside the lasso. |
| C | **Expand**, 64 px on one side | The canvas grows and the new edge is filled. |
| D | **Create** with DreamShaper, prompt "beige linen texture" | A new layer appears. |

Rules:

- **A and B pass:** stay on 0.23.1. A failure in C or D alone does not justify going back. Note it and report it upstream.
- **A or B fails because of PhotoCraft, not the model:** go back to PhotoCraft **0.20.2**, the highest tested version (`photocraft-0.20.2-macos-universal.dmg` from that release). Signs that PhotoCraft is the cause:
  - wrong or empty mask
  - "control" or "automation root" errors in OpenFill's log (gear > Engine > Logs)
  - the temporary document left open
  - the result landing in the wrong image

  To go back, quit both apps, replace `/Applications/PhotoCraft.app` with 0.20.2, and run A and B again. Nothing in OpenFill changes.
- **The model fails in B** (black image, out of memory, fp8 error): that is not a PhotoCraft problem. Go back to precondition 4.

## Timing test (a real Ikigai image)

Image: `005_Ecommerce/Etsy-Ikigai/Room_Templates/Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/001_Japandi_Minimalist/LVRM_Minimal_ISO/LVRM_Minimal_ISO.png` (2655 x 2000). Open a copy, never the template itself.

1. **Remove** (LaMa): lasso a small decor object, about 200 px. Time it.
2. **Fill** (Qwen): lasso the same area and use the prompt "a ceramic vase with dried pampas grass". Time the first run (cold: models load) and the second run (warm).
3. **Big Fill** (Qwen): lasso about 1200 px wide (for example a whole side table) and check sharpness at 100% zoom.
4. Write the times and a pass or fail for sharpness under `## Results` at the bottom of this file.

What counts as usable: warm Qwen Fill under about 3 minutes, LaMa under about 15 s.

**If Qwen is too slow,** there are two choices. Tony picks:
- **(a)** Use DreamShaper 8 Inpainting for quick fills (seconds, lower quality) and keep Qwen for finals.
- **(b)** A small local patch to OpenFill. In `app.py` `sampling()`, when the arch is `qwen_image`, use 4 steps and cfg 1.0. In `build_qwen_edit`, add a `LoraLoaderModelOnly` with the Lightning LoRA. The patch is lost on every OpenFill update.

**Soft results on big areas.** OpenFill runs Qwen on a crop with its longest side at most 1024 px. A small selection keeps full sharpness. A selection wider than about 1000 px comes back upscaled and soft. Ways around it:
- Fill large areas in two or three smaller selections.
- Use LaMa for plain removals (full resolution).
- Or upscale the result layer and blend it in.

## Rollback

- **OpenFill:** quit PhotoCraft, then open `~/Applications/Uninstall OpenFill for PhotoCraft.app` (or run `sh install.sh --uninstall`). Settings, PhotoCraft and the models stay.
- **The nodes OpenFill added** to `app/custom_nodes` (ComfyUI-GGUF, comfyui-inpaint-nodes, openfill-nodes) stay. If they cause trouble, Tony disables them in ComfyUI-Manager or removes them himself. Agents do not delete.
- **PhotoCraft 0.23.1:** Tony drags `/Applications/PhotoCraft.app` to the Trash. The ArtCraft copy is untouched.
- **Pinokio `start.js`** (only if changed in precondition 4): remove the added flag.

## Security notes

- **Network use.** OpenFill only goes online to download models (Hugging Face and GitHub, each file checked against the catalog's SHA-256 and size), to fetch custom nodes (GitHub zip of a pinned commit), and to check PhotoCraft's latest release. It sends no telemetry. Image generation stays local unless the optional cloud backend (OpenRouter or OpenAI key) is turned on. Keep it off.
- **Code it installs.** It adds Python packages and nodes into the Pinokio ComfyUI. All are pinned.
- **Tokens.** The PhotoCraft control token sits in a 0600 file and is never logged or printed. No Hugging Face token is needed for these models.

## SAM selection ("remove the cat")

### 1. What is already here

- **SAM 2.1**, in a venv outside the workspace: `~/.cache/ikigai-sam`, Python 3.11, torch 2.15, MPS available.
- **Checkpoints:** `~/.cache/ikigai-sam/checkpoints/sam2.1_hiera_large.pt` (898 MB) and `sam2.1_hiera_small.pt` (184 MB).
- **Harness:** `Portal/app/sam_frames.py`. It takes **box prompts**. The box comes from Gemini vision (cloud) or from `--box`. It does not take text directly. Gemini turns text into a box.
- **Edges:** a guided filter refines the mask to full-resolution, anti-aliased edges, which meets Tony's pixel-perfect standard. It runs on MPS with a CPU fallback.
- **The harness is tuned for blank frame inserts**: its Gemini prompt and its corner fitting.
- **PhotoCraft's own Select Subject and Object Selection are not SAM.** They are a classic algorithm (`crates/algo/src/segment`).

### 2. Text-prompted options (commercial-safe, Apple Silicon)

| Option | License | Size | Runs on MPS? |
|---|---|---|---|
| **SAM 3**, built into ComfyUI 0.45 (`SAM3_Detect` node in `comfy_extras/nodes_sam3.py`, loaded as a checkpoint, takes text and box and point prompts) | Meta "SAM License" (Nov 2025): free and worldwide, commercial use not excluded; no military use, no reverse engineering, include the license with copies | about 850M parameters, about 1.7 to 3.4 GB file | Probably. ComfyUI's port is plain PyTorch. Meta's own repo is CUDA-only. Not tested here. |
| **Gemini box + SAM 2.1** (what the Portal already does) | SAM 2.1 Apache-2.0; Gemini is a paid cloud API (the image goes to Google) | Already installed | Yes, verified on this Mac |
| **Grounding DINO + SAM** (ComfyUI `comfyui_segment_anything`) | Apache-2.0 | about 0.7 GB plus the SAM model | Partly. Grounding DINO's custom op falls back to CPU, which is slower but works. |
| **Florence-2 + SAM 2.1** (kijai nodes) | MIT and Apache-2.0 | 0.2 to 0.8 GB plus SAM | Yes, generally |

### 3. Integration

**(a) In PhotoCraft.** This is possible through the control protocol, with a small bridge script:

1. Read the open image (with `app.save` to the automation write root, as OpenFill does).
2. Run SAM 3 through the ComfyUI API on 8188, with the text "cat", to get a full-size grayscale mask PNG.
3. `app.open` the mask.
4. On the photo, run `select.loadSelection {"document": <mask doc>, "channel": "red", "operation": "new"}`. That command takes another open document as its source, so you get a soft, pixel-exact selection.
5. Close the mask document.
6. Tony presses Fill or Remove in OpenFill.

Notes:
- The script can reuse the control port and token file OpenFill launches PhotoCraft with. It must never print the token.
- `doc_place` is refused in bridge mode, so use `app.open` plus `select.loadSelection`, not place.
- Not built. About a day of work.

**(b) In the Ikigai Portal (Edit with chat).** Text goes to SAM, which gives a mask, which goes to LaMa (remove) or Qwen (edit). Everything runs in the same Pinokio ComfyUI as one graph:
- remove: `SAM3_Detect`, then LaMa inpaint
- edit: `SAM3_Detect`, then Qwen Edit with the Lightning LoRA at 4 steps

This replaces the 18-credit kie.ai call in `template_edit.py` with a free local one. Keep the existing SAM 2.1 harness as the fallback when SAM 3 misses.

### 4. Recommendation and smallest first test

- **Recommendation:** use SAM 3 inside the Pinokio ComfyUI. It is one engine for selection, removal and editing, it is local, it takes text directly, and its license allows commercial use. Build the Portal path (b) first, since it needs no PhotoCraft scripting. Add the PhotoCraft bridge (a) after OpenFill passes test B.
- **Smallest test (about 30 minutes, once Tony OKs the download):**
  1. Put the SAM 3 checkpoint (Comfy-Org repackaged) into the existing `models/checkpoints` link. No new folder.
  2. In the ComfyUI page, build Load Checkpoint, then CLIP Text Encode ("lamp"), then `SAM3_Detect` on `LVRM_Minimal_ISO.png`, then save the mask.
  3. Check: does it run on MPS, how long does it take, and are the edges as clean as the SAM 2.1 harness output on the same object?
  4. If MPS fails, fall back to the Gemini box + SAM 2.1 path, which already works.

## Open risks

1. Qwen on MPS (fp8 text encoder, black images, speed). Precondition 4 and the timing test decide this.
2. PhotoCraft 0.21 to 0.23 changes to TIFF transparency and automation roots may break selection reading. Test A catches it. Fallback is 0.20.2.
3. OpenFill ignores the Lightning LoRA, so Qwen fills are slow. Fix with option (a) or (b) above.
4. Fills come back soft on selections larger than about 1000 px, because Qwen works at 1024 px.
5. Two PhotoCraft apps share one settings folder. The newer one may change preferences the ArtCraft copy reads.
6. SAM 3 on MPS is not proven yet. The SAM 2.1 path is the fallback.
7. OpenFill is a beta from one developer. Mac support has been tested only on an M3 Air.

## Results

Run 2026-11-15 on the M3 Max (36 GB), all on copies of `LVRM_Minimal_ISO.png` opened from OpenFill's exchange folder. Pinokio ComfyUI 0.45.0 (started from Pinokio, `PYTORCH_ENABLE_MPS_FALLBACK=1`), PhotoCraft **0.23.1**, OpenFill 0.2.6 plus the Agent-OS patch.

### What was installed

- PhotoCraft 0.23.1 in `/Applications/PhotoCraft.app` (DMG SHA-256 matched `SHA256SUMS.txt`; notarized, no quarantine, so no Gatekeeper step). The ArtCraft copy was not touched.
- OpenFill 0.2.6 via `install.sh` (code in `~/Library/Application Support/OpenFill for PhotoCraft/app`, launchers in `~/Applications`). Settings: ComfyUI folder = the Pinokio app, "start the engine" off.
- Nodes (OpenFill's own pinned installer): ComfyUI-GGUF @6ea2651, comfyui-inpaint-nodes @5b76817, openfill-nodes v2, opencv-python-headless 5.0.0.93 in the Pinokio env. ComfyUI was restarted in place (Manager reboot, same Pinokio process).
- Models, each checked by SHA-256: LaMa `inpaint/big-lama.pt` (new folder, approved), DreamShaper 8 Inpainting, FLUX.2 klein 4B (diffusion model, `qwen_3_4b` text encoder, flux2 VAE, Apache-2.0), SAM 3.1 `checkpoints/sam3.1_multiplex_fp16.safetensors` (SAM License, commercial use allowed). Qwen files were already there.
- **Qwen gguf note:** unsloth re-uploaded `qwen-image-edit-2511-Q4_K_M.gguf` (now 12,842,830,432 bytes, SHA-256 `07951f61...`, matches Hugging Face). OpenFill's catalog had the old hash; the patch updates it.
- `start.js` was **not** changed: fp8 Qwen works on MPS with no black image.

### The patch (re-apply after every OpenFill update)

`001_Architecture/Tools/Image-Generation/OpenFill_AgentOS_Engines.patch`, applied with `python3 001_Architecture/Tools/Image-Generation/openfill_agentos_patch.py` (dry-run first, keeps `.pre-agentos` backups). Adds to the panel's **Model** menu:

| Engine | Where | Use |
|---|---|---|
| FLUX.2 klein 4B, 4 steps (local) | new `flux2_klein_edit` template | **default Fill** (fast) |
| Qwen Edit 2511 Lightning, 4 steps (local) | catalog entry + LoRA in `build_qwen_edit`, cfg 1.0 | better finals, slow |
| Qwen-Image-Edit 2511 (stock, 20 steps) | unchanged | not recommended (minutes) |
| LaMa | unchanged | **default Remove** (small objects) |
| Nano Banana Pro / Nano Banana 2.1 / Ideogram 3 Edit (cloud, kie.ai) | `backends/cloud.py` + per-job engine in `app.py`, `service.py`, `bar.py` | big removals, hard fills |
| Qwen Edit inpaint / Nano Banana Pro (cloud, fal.ai) | same | alternatives |

Cloud engines say "(cloud, ...)" and the price in the menu. Only the selection's surroundings (at most 1536 px) are sent; the result is always put back through the selection mask, so pixels outside the selection stay untouched (measured: 0 changed pixels outside the lasso on all cloud tests). Keys are read from `~/.env-secrets` and never logged.

### Tests A to D (PhotoCraft 0.23.1, freehand lasso through `select.lasso`)

| # | Result |
|---|---|
| A Remove (LaMa) | **Pass.** New layer "Object Removal" with a layer mask, Background untouched, one Edit > Undo removes it (layers 1 → 2 → 1). 5.6 s. |
| B Fill (Qwen) | **Pass.** Same checks; the fill stays in the lasso plus OpenFill's soft edge. |
| C Expand 64 px right (Qwen Lightning) | **Pass.** Canvas 2655 → 2719, edge continued the window frame. 197 s. |
| D Create (DreamShaper 8) | **Pass.** New 768 x 512 layer. 20 s cold, 15 s warm. |

Decision: **stay on 0.23.1** (A and B pass; no automation-root or TIFF selection problems).

### Timings (warm = model already loaded)

| Job | Time |
|---|---|
| LaMa Remove (lamp, stool, small print) | 3.6 to 5.7 s |
| SAM 3.1 "lamp" mask in ComfyUI | 10.3 s cold, 3.7 s warm (MPS); whole "type lamp → selection" bridge 8.6 s |
| FLUX.2 klein 4B Fill through OpenFill | 35.9 s first, 28.2 s warm; big 1230 x 540 fill 38.7 s |
| Qwen + Lightning (4 steps) plain ComfyUI, 1024 x 768 | 226 s cold, 153 s warm (33.6 to 41 s per step) |
| Qwen + Lightning Fill through OpenFill | 163 to 181 s |
| Qwen stock (cfg 2.5): 53 s per step | about 18 min for OpenFill's 20 steps (measured 3 steps, extrapolated) |
| DreamShaper 8 quick Fill | 14 to 16 s |
| Cloud: Ideogram 3 Edit (kie.ai, true mask) | 21 s, 1 credit ($0.005) |
| Cloud: Nano Banana Pro (kie.ai) Remove of the stool | 66 s, 18 credits ($0.09) |
| Cloud: Qwen inpaint (fal.ai) | 11 to 12 s, about $0.03 per megapixel |

Target "warm Qwen under 3 minutes": Lightning just makes it (153 to 181 s); stock Qwen fails badly. klein is about 5x faster than Qwen Lightning. Memory: ComfyUI uses about 14 GB, the Docker VM 8 GB; the Mac was using 12 to 14 GB of swap during Qwen runs, which slows every step. Quitting Docker Desktop while filling should help Qwen.

### Quality on the real template

- LaMa: lamp removal clean; the stool (big object over floor and baseboard) comes back as a smeared blur. Fail for big objects.
- Nano Banana Pro (cloud) stool removal: door frame, baseboard and herringbone floor rebuilt; small flaws (baseboard turned marble-like, a dot on the wall). Best removal of the day.
- Qwen Lightning: lamp → white vase with eucalyptus looks real; stool → oak side table is good but soft at 100%.
- klein: vase with pampas looks real, but klein follows the prompt less tightly (unmasked test added extra plants).
- Ideogram 3 Edit (cloud): fills strictly inside the lasso shape, so the new object takes the old object's outline (eucalyptus shaped like the lamp shade).
- DreamShaper: fast but oversaturated and does not match the light; drafts only.
- Big fill sharpness (selection about 1200 px wide): **fail** at 100% for all local models. OpenFill works at 1024 px and scales up. Fill big areas in 2 or 3 parts, or raise `max_side_sdxl` in OpenFill settings (slower).

### SAM

- SAM 3.1 runs in the Pinokio ComfyUI on MPS. Text "lamp" found the lamp only (shade and body, not the books), edges follow the object; a guided filter softens the 1008 px staircase. A little edge noise where the shade and wall have the same brightness.
- Bridge built: `python3 001_Architecture/Tools/Image-Generation/photocraft_sam_select.py "lamp"` turns the word into a PhotoCraft selection (plan 3a). SAM selection + LaMa Remove of the lamp: about 14 s total, clean result.
- Not compared pixel by pixel with the SAM 2.1 harness yet.

### Object growth fix (2026-11-15, later)

Problem: a prompted fill was masked to the selection plus about 16 to 24 px, so a bigger new object was cut off with a soft edge and parts of the old object stayed visible.

Change (in the patch): new settings `grow_object_percent` (panel label "Allow object to grow (%)", default 40) and `preremove_object` (default on). For a prompted local fill, LaMa first removes the old object inside the selection (3 to 4 s, same job, still one Undo). The model may then paint up to 40% of the selection's larger side past it. The layer mask is the selection plus only the pixels that changed out there (difference against the cleaned image, holes closed, 2 px soft rim), so no repainted band shows. Removal and cloud engines are unchanged (cloud results still stay inside the selection).

Test document `LVRM_grow_test.png` (a copy), before/after 100% crops in OpenFill's exchange folder (`Grow_Test_*`):

| Engine | Lamp to vase with eucalyptus | Stool to oak side table with bowl |
|---|---|---|
| klein, 40% | 79.6 s, not clipped, lamp gone; the books under the lamp were dropped | (30% run) 75.1 s, complete table and bowl, stool gone |
| Qwen Lightning, 40% | 162.1 s, vase stands on the books, branches complete, lamp gone | 165.7 s, complete table and bowl, stool gone; baseboard repainted white |

Log numbers (40%): lamp selection 404 x 492, growth 197 px, context 1684 x 1772 at scale 0.58, kept 89,292 to 237,584 px outside the selection; stool selection 489 x 484, growth 196 px.

Verdict: no clipping, no leftover lamp or stool, no pale band at 100%. Costs: fills take about 2x longer for klein (bigger context), results are a little softer (lower scale), and things inside the growth zone can change (books dropped by klein, baseboard repainted by Qwen). At 30% the klein vase was still cut at the growth limit, so 40% is the default.

### Shadows (2026-11-15, later)

- **Finding the old shadow automatically failed on this template.** SAM 3.1 text prompts ("the stool and its shadow", "shadow of the lamp", "shadow") select only the object, a window light stripe, or the sofa's shadow. Brightness against a LaMa probe fails too: LaMa fills a large area with grey mush, and the stool's shadow (the gaps in the sun stripes) has the same brightness as the room's ordinary shade. Not shipped. Old shadows are still removed when they lie inside the selection or the 40% growth zone; for a longer old shadow, lasso the object and its shadow together (what Photoshop's Remove also needs).
- **Shipped: room for the new shadow.** Setting `shadow_reach_percent`, label "Room for new shadow (%)", default 100 (0 = off). The brightest area (here the window, found at about (2430, 820)) gives the direction; the model may paint up to 100% of the selection's size past it on the far side, and the prompt gets a hint ("casts a natural shadow toward the left and down"). In that zone only darkening of the same colour is kept, applied to the original pixels, so nothing else moves; the new object keeps every change connected to the selection and fades toward the 40% limit.
- Tried and dropped: keeping every change in the zone (Qwen moved the art frame and ghosted the stool; klein painted a floor-standing vase), and allowing brightening near the object (pale ghost leaves).
- Test document `LVRM_shadow_test.png`, crops `Shadow_Test_*` in the exchange folder. Final (visible): Qwen Lightning v5, lamp 167.6 s, stool 159.0 s. klein v5: 80.3 s and 70.1 s, but its lamp result is a floor vase in front of the table (not usable).
- Verdict, Qwen v5: stool, old shadow gone near the table, new leg shadows run left along the floor like the room's other shadows; one invented plant-like shadow on the floor. Lamp: frame, books and stool untouched; leaf shadow on the wall to the lower left is plausible but partial; faint ghost leaf outlines left and right of the branches (visible at 100%).

### Still short of Photoshop

1. Speed: Photoshop's Generative Fill returns 3 variations in about 10 to 20 s. Local here: klein about 30 s (one variation), Qwen 2.5 to 3 min. Cloud Nano Banana Pro about 60 s.
2. Big areas come back soft (1024 px work size).
3. Big removals: LaMa smears; only the cloud engines rebuild structure well.
4. No "Select Subject" button in PhotoCraft yet: SAM is a script, not a menu item.
5. The Fill menu has no live preview of cost per engine beyond the label.
