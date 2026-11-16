# Shadow-Aware Fill Research (PhotoCraft + OpenFill)

Date: 2026-11-15. Research only: nothing installed, downloaded, run on cloud, or committed.
All pages below were fetched on 2026-11-15 (repo, model card, paper or provider page). fal prices come from fal's free pricing API (`api.fal.ai/v1/models/pricing`), read the same day.
Context: `OpenFill_PhotoCraft_Plan.md` (## Shadows). SAM 3.1 cannot select shadows; old shadows survive outside the selection; new shadows get clipped; big areas come back soft; the art frame gets artifacts.

Workspace check first: TOOLBOX.md (OpenFill section, cloud edit models researched 2026-11-15) and Tool_Catalog.json / model_catalog.json list no shadow-aware eraser, shadow detector or relight model. Nothing relevant in 000_Ingest or 004_Research.

License rule used: commercial use must be allowed. Anything built on FLUX.1-dev (Non-Commercial License) is excluded, the same as the existing TOOLBOX rule ("Do not add FLUX.1 Fill/Kontext dev").

---

## Recommendation (ranked)

| Job | Pick | Why | Cost / speed |
|---|---|---|---|
| Remove object + shadow, #1 | **Bria Eraser FIBO-Edit-1.5 on fal** (`bria/fibo-edit-1.5/eraser`) | Mask the object only. In the default context-aware mode it also removes the shadow or reflection outside the mask (fal page examples: a bike's shadow, a kayak's reflection). Trained on licensed data for commercial use (vendor claim). Has a pixel-perfect mode too. | $0.04/image |
| Remove object + shadow, #2 | **Ideogram object removal** (fal `fal-ai/ideogram/object-removal`, or Ideogram's own `POST /v1/remove-object`) | Mask only. Ideogram says it "may update pixels outside your mask to remove shadows and reflections". | $0.03/image |
| Local removal + shadow (to test) | **OSOR-SDXL** (ECCV 2026) | Only commercial-safe local model built for effects. One step, and an "alpha head" grows the edit past a tight object mask. CUDA-tested only, no ComfyUI node. | Under 1 s on an A100 (paper). Mac speed unknown. |
| Select shadow automatically | **OpSeg** (SAM 2.1 b+ fine-tuned for object + shadow), Apache-2.0 | The only open, commercial-safe model found that segments an object together with its shadow. Trained on SOBA (mostly outdoor), so indoor soft shadows are a risk. | Not measured |
| Replace object with correct shadow | **Keep Qwen-Image-Edit-2511 (installed), add the shadow-aware removal first**, and optionally the dx8152 Relight LoRA (Apache-2.0) | No commercial-safe open model was found that does insertion with physically correct cast shadows. The best route is: clean removal (object and shadow) first, then insert with Qwen in the shadow-reach zone OpenFill already has. | Same as today |

A cheaper alternative to a shadow detector (idea, untested): run the Bria eraser once on the object mask, then compare the result with the original. Pixels outside the mask that got brighter are the old shadow. That difference is a ready shadow mask that SAM can't produce, and it could feed a local fill or show Tony what will change.

---

## 1. Removal models that handle shadows and reflections

| Model | Weights | License (commercial?) | Base / size | Mac / ComfyUI | Mask need | Shadow evidence | Source (fetched 2026-11-15) |
|---|---|---|---|---|---|---|---|
| **OSOR** (2026-06, ECCV 2026) | Yes, HF `QinmingZhou/OSOR` | Code MIT. **SDXL checkpoints CreativeML Open RAIL++-M (commercial OK, with use restrictions).** FLUX-Fill checkpoints FLUX.1-dev Non-Commercial (no). | SDXL-Inpainting 0.1 + LoRA `.pth` (raw state dict, needs the OSOR loader). Sizes not listed. | Tested on CUDA 12.4 only. MPS not mentioned. No ComfyUI node. | Binary object mask; the alpha head learns "an appropriate editing region beyond a conservative object mask". Paste-back off by default because it "can preserve unwanted effects outside the input mask". | Claims removal of "the target together with associated shadows, reflections, and residual traces". 4-30x faster than multi-step baselines, about 10x faster than ObjectClear. No independent test found. | github.com/Zhouqm-Git/osor, huggingface.co/QinmingZhou/OSOR, arxiv.org/abs/2606.28094 |
| **ObjectClear** (CVPR 2026) | Script download + HF demo | **NTU S-Lab License 1.0, non-commercial: no** | SDXL-Inpainting + CLIP | Not mentioned | Object mask (SAM2 suggested) | Removes the object and "associated effects" | github.com/zjx0101/ObjectClear |
| **OmniEraser** (2025-04) | Yes, HF `theSure/Omnieraser` | Card says Apache-2.0, but it is a **FLUX.1-dev finetune: no** under the workspace rule | FLUX.1-dev | Not mentioned | Object mask only | Removes shadows and reflections "using only object masks" (Video4Removal data) | github.com/PRIS-CV/Omnieraser, HF card |
| **OmniPaint** (ICCV 2025) | Yes, HF `yeates/OmniPaint` | LoRA MIT, but **needs FLUX.1-dev: no** | FLUX.1-dev + LoRA | Not mentioned | Object mask | Removes "visual effects (shadows, reflections) using only object masks"; insertion aims for "harmonious lighting" | github.com/yeates/OmniPaint, HF card |
| **ReFocusEraser** (ICLR 2026) | Code on GitHub | **FLUX.1-dev based: no** (not opened; from search result only) | FLUX.1-dev | - | - | Small objects + "object shadows" | search result only, unverified |
| **ObjectDrop** (Google, 2024-03) | **No code, no weights** | - | - | - | - | Trained on before/after photos so it removes shadows and reflections; strong paper results | arxiv.org/abs/2403.18818 |
| **ObjectMover** (Adobe, CVPR 2025) | **No release found** | - | Video-model DiT | - | - | Paper says it edits lighting and shadow together with the moved object | research.adobe.com publication page (search), project page empty |
| **SmartEraser** (CVPR 2025) | Released 2025-06-27 (page also lists it as TODO, inconsistent) | MIT (base SD1.5-inpainting, CreativeML OpenRAIL-M): yes | SD 1.5 inpainting | Not mentioned | Mask | No shadow claim; authors add RORD data to cover "object shadows" | github.com/longtaojiang/SmartEraser |
| **RORem** (CVPR 2025) | Yes, HF `LetsThink/RORem` (3B, F16) | Apache-2.0 (base SDXL inpainting): yes | SDXL-Inpainting; 4-step LCM LoRA variant | Not mentioned | Mask + optional dilation | **No shadow claim.** A HF forum user (2026-09-07) saw floor texture warping. | github.com/leeruibin/RORem, HF forum thread |
| **Attentive Eraser** (AAAI 2025) | Diffusers community pipeline | Apache-2.0: yes | SDXL, tuning-free | Diffusers (MPS likely, unverified) | Mask | No shadow claim | github.com/Anonym0u3/AttentiveEraser |
| **PowerPaint v2-1** (2024) | Yes | MIT: yes | SD 1.5 / BrushNet | Not mentioned | Mask, removal tab | No shadow claim | github.com/open-mmlab/PowerPaint |
| **QIE-2511 Object Remover v2** (2026) | Yes, HF `prithivMLmods/QIE-2511-Object-Remover-v2` | Apache-2.0 (base Qwen-Image-Edit-2511, Apache-2.0): yes | LoRA for Qwen-Image-Edit-2511, which is **already installed** (GGUF) | LoRA loads in ComfyUI on the existing graph (expected, untested) | Red highlight drawn on the object + prompt "Remove the red highlighted object from the scene." | Card says lighting and shadows stay consistent; no claim that the old cast shadow is removed | HF card |
| **FLUX.2 klein 4B object-remove LoRA** (fal) | Yes, HF `fal/flux-2-klein-4B-object-remove-lora` (~58 MB, ComfyUI file included) | Apache-2.0: yes | LoRA for the installed FLUX.2 klein 4B | ComfyUI file provided | Highlighted object + "Remove the highlighted object from the scene" | **Card limitation: "Reflections and shadows of removed objects may persist."** Trained on only 100 pairs. | HF card |
| **PredErase** (2026-09) | Code on GitHub | Not checked | Frozen FLUX.2 + I-JEPA, training-free | - | - | Object-and-effect removal; authors say paired-data erasers still score better | search result only, unverified |

Local verdict: OSOR-SDXL is the only commercial-safe local model built for shadows. It still needs a port: a custom loader, CUDA-only testing, and no ComfyUI node. The two LoRAs (Qwen, klein) drop into the existing ComfyUI with almost no work, but neither claims to remove the old shadow. The klein card says shadows may persist.

## 2. Shadow detection / segmentation

| Model | License | Weights | What it gives | Mac | Source |
|---|---|---|---|---|---|
| **OpSeg** (IJCNN 2025) | **Apache-2.0** (SAM 2 is Apache-2.0 too) | ModelScope `deyang2000/SAM2_Shadow`, Google Drive | SAM 2.1 b+ fine-tuned on SOBA to segment an object and its shadow together. The prompt format isn't stated; ISAT (an annotation tool) integration means the usual SAM 2 point/box prompts. | No hardware stated. SAM 2 is PyTorch; MPS unverified. | github.com/deyang2000/OpSeg |
| SSIS / SSISv2 (CVPR 2021, TPAMI) | Not stated on page | Google Drive | Shadow instances paired with object instances (best on the SOBA benchmark) | AdelaiDet + CUDA build; impractical on Mac | github.com/stevewongv/SSIS |
| FastInstShadow (2025) | - | Repo 404 on 2026-11-15 | Instance shadow detection | - | - |
| SDDNet (MM 2023) | **No license**: not usable | Baidu/Drive | Shadow detection (best BER on SBU-Refine) | CUDA 11.1 env | github.com/rmcong/SDDNet_ACMMM23 |
| Benchmarks hub | No license | - | Lists SDDNet, FDRNet, SSISv2, HomoFormer (shadow removal) etc., GPU timings only | - | github.com/xw-hu/Unveiling-Deep-Shadows |

Verdict: OpSeg is the one to test. Risk: SOBA is mostly outdoor sun shadows, and Tony's templates have soft indoor window light. Tony's own test showed the stool's shadow looks the same as ordinary room shade, which may defeat any detector. The eraser-difference trick (top of the file) avoids that problem.

## 3. Replacement with a correct shadow

| Option | License | Mac | Notes | Source |
|---|---|---|---|---|
| **Qwen-Image-Edit-2511** (installed) | Apache-2.0 | Running already (GGUF, MPS) | Card: lighting-enhancement LoRA built in, less "image drift". No claim about shadows of inserted objects. | HF Qwen/Qwen-Image-Edit-2511 |
| dx8152 Qwen-Image-Edit-2509 Relight LoRA | Apache-2.0 | ComfyUI LoRA | Trigger "重新照明" (relight); trained for 2509, so 2511 compatibility is not stated | HF dx8152/Qwen-Image-Edit-2509-Relight |
| IC-Light v1 | Code Apache-2.0; SD1.5 weights (OpenRAIL-M). Its BRIA RMBG 1.4 component is non-commercial; swap in BiRefNet. | SD1.5, light | Relights a foreground cutout to match a background; does not paint cast shadows on the floor | github.com/lllyasviel/IC-Light |
| OmniPaint insertion | FLUX.1-dev: no | - | - | above |
| ObjectMover / ObjectDrop insertion | No weights | - | Best published shadow results, but not usable | above |
| Cloud: Nano Banana Pro (kie) | Commercial API | Cloud | Tony's 2026-11-15 test: best removal of the day; reference-only (no true mask) | OpenFill plan |

Verdict: no new model is needed for replacement. The clipped and wrong shadows come from the pipeline order. Do the remove-with-shadow step first (Bria or OSOR), then the Qwen insert with the existing `shadow_reach_percent` zone. This stops the old shadow and the new shadow from fighting.

## 4. Cloud (fal / kie) for removal with shadows

| Endpoint | Shadow claim (provider page) | Input | Price (fal pricing API, 2026-11-15) |
|---|---|---|---|
| `bria/fibo-edit-1.5/eraser` | **Yes**: context-aware mode removes the shadow or reflection outside the mask; pixel-perfect mode (`composite: true`) keeps the outside untouched but leaves the shadows | image + mask, `composite`, `seed` | $0.04/image |
| `fal-ai/ideogram/object-removal` | Yes ("erasing objects with their shadows and reflections") | image + mask | $0.03/image |
| `fal-ai/finegrain-eraser` (prompt) and `/mask`, `/bbox` | Yes ("shadows, reflections, and lighting artifacts") | prompt, or mask, or box | API: $0.045/image. The page shows tiers: $0.04-0.22 (mask) and $0.18-0.36 (prompt). |
| `fal-ai/flux-pro/v1/erase` (BFL FLUX Erase, 2026-05-21) | BFL blog: removes "traces like shadows"; fal page has no claim | image + mask, `dilate_pixels` (default 10) | API: $0.004/MP. The page says $0.03 for the first MP plus $0.004 per extra MP. The API and the page disagree. |
| `fal-ai/bria/eraser` (older) | No claim | image + mask | $0.04 |
| kie.ai | **No dedicated eraser** on kie.ai/market. Only general edit models (Nano Banana Pro/2, GPT Image 2.x, Seedream 5.5, Flux 3) plus Ideogram v3 Edit (already in OpenFill). | - | - |

Compared with local: the cloud erasers are mask-only, cost 3-4.5 cents, and claim shadow handling out of the box. Locally, only OSOR claims the same, and it needs a CUDA-to-MPS port. For a few dozen templates, cloud is cheaper than the porting time.

## 6. Side issues

**(a) Blur at the top of a prompted new object**
- Cause (from the OpenFill plan): Qwen works at a 1024 px long side, and the growth limit plus feathered mask fades out exactly where a taller object needs room. Photoshop has the same cap. Adobe community experts state that Generative Fill generates at most about 1024x1024 at full resolution and upsamples bigger selections (community.adobe.com threads, 2023-24; current limit unverified).
- Fixes used elsewhere: (1) Tile like Photoshop users do: fixed 1024x1024 selections overlapping by 10-20 px (PhotoshopCafe / photoshoproadmap tutorials). (2) ComfyUI **Inpaint Crop and Stitch** (GPL-3.0, updated 2026-05-25): crop only the mask plus context, resize the crop up to the model's native size, then downscale when stitching back. A smaller context gives more pixels per object. (3) Make the mask taller than the object (grow upward, not only sideways), so the top isn't in the feather fade. (4) Run a low-denoise second pass (about 0.2-0.35) on just the new object's crop, or upscale the crop before stitching.

**(b) Unwanted artifacts on a nearby picture frame when the area is large**
- Cause: the whole crop goes through VAE encode/decode and the model may repaint anything in context. Tony's test saw Qwen move the art frame when every change in the zone was kept.
- Fixes: (1) Crop and Stitch never passes unmasked pixels through the VAE and composites back pixel-exactly. (2) **Protected mask**: the templates already have SAM-measured art openings and frame edges (`Portal/app/sam_frames.py`). Subtract the frame plus a few px from every allowed-change zone (selection, growth zone, shadow zone) before compositing. This is the cheapest, most reliable fix. (3) Bria eraser `composite: true` (pixel-perfect) for jobs next to the frame. (4) Keep the context crop from reaching the frame when possible. Photoshop applies the result as a layer masked to the selection, so nothing outside changes.

## What I could not verify

- No model was run. Every shadow claim is the vendor's or the paper's own; no independent side-by-side on indoor room shots was found.
- OSOR on Apple MPS: unverified (CUDA-only testing, custom `.pth` loader, no ComfyUI node). Its file size and RAM need are not listed.
- OpSeg on MPS, its prompt format, and how well it works on soft indoor shadows: unverified.
- QIE-2511 Object Remover v2 removing an old cast shadow outside the highlight: unverified (the card claims only consistent lighting).
- dx8152 Relight LoRA (made for 2509) on 2511: unverified.
- FLUX Erase price: fal pricing API ($0.004/MP) and fal page ($0.03 first MP) disagree.
- Finegrain price: API $0.045 vs page tiers.
- Bria "licensed data for commercial use" is Bria's own statement.
- ReFocusEraser, PredErase, GeoRemover: seen only in search results, pages not opened.
- ObjectMover code/weights: none found; the project page returned no content.
- Photoshop's current generation size limit (1024 vs 2000 px): forum statements only.

## Test results (2026-11-15, fal.ai, Ikigai template LVRM_Minimal_ISO copy)

Input: wide crop (stool 1200 x 800 incl. its floor shadow; lamp 1200 x 900 incl. the art frame), SAM 3.1 object-only mask, no shadow in the mask.

| Model, mode | Object | Time | Old shadow | Changed outside the mask | Notes |
|---|---|---|---|---|---|
| Bria FIBO-Edit-1.5 eraser, default (context-aware) | stool | 5.9 s | **Not removed** (only the contact shadow at the feet) | 7,863 px | Clean floor and baseboard; cast shadow on the floor stays |
| Bria, `composite: true` | stool | 5.5 s | Not removed | 3,636 px | As above |
| Ideogram object removal | stool | 28.7 s | **Removed**, sun patch rebuilt | 101,026 px (mostly the shadow; also a brightened patch of the rug in the doorway) | Best stool result |
| Bria, default | lamp | 6.7 s | (the lamp has no distinct cast shadow) | 1,168 px | Art frame untouched, clean wall |

Difference-image shadow mask: works with Ideogram. Pixels outside the mask that got brighter by more than 10 (83,237 px), kept only where connected to the stool, give 78,269 px that cover the stool's cast shadow; the 11,063 px rug patch drops out. With Bria there is no shadow change to measure (8,127 px, contact shadow only).

Spend: Bria 3 x $0.04 + Ideogram 1 x $0.03 = $0.15 (fal list prices).
