# Upscale Models Research (Upscayl / upscayl-ncnn), 2026-11-21

Read-only research. Nothing downloaded or installed. Items marked UNVERIFIED or INFERENCE are not documented in an official source.

## 1. Which models exist as ready NCNN files in Upscayl's official custom-models repo

Source: GitHub API listing of https://github.com/upscayl/custom-models/tree/main/models and README https://github.com/upscayl/custom-models (fetched 2026-11-21). Raw base: https://raw.githubusercontent.com/upscayl/custom-models/main/models/

| Model | In repo? | .bin | .param |
|---|---|---|---|
| 4x_NMKD-Siax_200k | YES | 4x_NMKD-Siax_200k.bin, 66,793,352 B (~63.7 MiB) | 4x_NMKD-Siax_200k.param, 108,037 B |
| 4xNomos8kSC | YES | 4xNomos8kSC.bin, 33,424,520 B (~31.9 MiB) | 4xNomos8kSC.param, 108,039 B |
| 4xHFA2k | YES | 4xHFA2k.bin, 33,424,520 B | 4xHFA2k.param, 108,039 B |
| 4x-UltraSharp | NO (not in repo). Built into the Upscayl app as ultrasharp-4x. The repo only mentions UltraSharp in the note about `unknown-2.0.1`, which was shipped by accident in its place in v2.0.1. | n/a | n/a |
| 4x-Remacri | NO (not in repo). Built into the app as remacri-4x. | n/a | n/a |

Other ready files in the same folder (all .bin + .param pairs): 4x_NMKD-Superscale-SP_178000_G (66.8 MB), 4xLSDIR, 4xLSDIRplusC, 4xLSDIRCompactC3 (1.2 MB), RealESRGAN_General_x4_v3, RealESRGAN_General_WDN_x4_v3, realesr-animevideov3-x2/x3/x4, uniscale_restore, unknown-2.0.1.

Whether the repo's "4x_NMKD-Siax_200k" is the same weights as OpenModelDB's "4x NMKD Siax (CX)" (200,000 iterations): the names and README description match ("universal upscaler for clean and slightly compressed images"), but the repo does not state it. INFERENCE, treat as the same model but UNVERIFIED.

Where the OpenModelDB entries are PyTorch only (would need conversion, not needed for the three above since NCNN files exist): OpenModelDB downloads for Siax, Nomos8kSC, HFA2k, UltraSharp, Remacri are all .pth (63.9 MB each). Conversion route if ever needed: https://github.com/upscayl/upscayl/wiki/Model-Conversion-Guide (chaiNNer v0.21.0 + pth2bin.chn workflow, then edit the .param first "input" entries to "data"; only ESRGAN .pth models guaranteed).

## 2. Licences

OpenModelDB pages (fetched 2026-11-21):

| Model | Licence on OpenModelDB | Page |
|---|---|---|
| 4x NMKD Siax (CX) | WTFPL | https://openmodeldb.info/models/4x-NMKD-Siax-CX |
| 4xNomos8kSC (author listed: Helaman) | CC-BY-4.0 | https://openmodeldb.info/models/4x-Nomos8kSC |
| 4xHFA2k (author listed: Helaman) | CC-BY-4.0 | https://openmodeldb.info/models/4x-HFA2k |
| 4x-UltraSharp (Kim2091) | CC-BY-NC-SA-4.0 | https://openmodeldb.info/models/4x-UltraSharp |
| 4x Remacri (FoolhardyVEVO) | CC-BY-NC-SA-4.0 | https://openmodeldb.info/models/4x-Remacri |

Does the NC licence reach the OUTPUT? OpenModelDB's licence guide states "the license of a model does not extend to the upscaled images produced by the model"; the output's licence follows the original image, and "commonly used licenses" do not add terms for outputs. It lists "Commercial use: Not allowed" for CC-BY-NC(-SA) as a property of the model itself. Source: https://openmodeldb.info/docs/licenses. So by OpenModelDB's own reading, selling prints made with Remacri/UltraSharp output is not restricted by the model licence. This is OpenModelDB's interpretation, not legal advice and not a statement by the model authors (UNVERIFIED for authors' intent).

Risk flags:
- Remacri and UltraSharp: NON-COMMERCIAL on the model. Using them as a private tool to produce files you sell is covered by OpenModelDB's reading, but do NOT redistribute the model files or bundle them in anything sold or shared (also SA: derivatives under same licence). Tony's current default (remacri-4x) is in this category. Low-to-moderate risk, worth a conscious decision.
- Nomos8kSC, HFA2k: CC-BY-4.0 means commercial use allowed with attribution when you redistribute the model. Phhofm's own repo README states no licence for them (https://github.com/Phhofm/models), so the CC-BY-4.0 comes from OpenModelDB only. Note OpenModelDB lists author "Helaman"; Upscayl's README credits @Phhofm. They appear to be the same person (INFERENCE).
- Siax: WTFPL (permissive), lowest risk.
- Built-in Upscayl models: the app code is AGPL-3.0 (https://github.com/upscayl/upscayl-ncnn). I found NO official Upscayl page stating a licence for the bundled model weights (remacri-4x, ultrasharp-4x, digital-art-4x, high-fidelity-4x, ultramix-balanced-4x, upscayl-lite-4x, upscayl-standard-4x). UNVERIFIED. remacri-4x and ultrasharp-4x are named for the CC-BY-NC-SA models above; ultramix-balanced is named for the Kim2091 UltraMix collection (its OpenModelDB page was not found, 404). digital-art-4x, high-fidelity-4x, upscayl-lite/standard: licence unknown, treat as unstated.

## 3. What each model is for, failure modes, per-style recommendation

DOCUMENTED (OpenModelDB / Upscayl custom-models README):
- Siax: "Universal upscaler for clean and slightly compressed images (JPEG quality 75 or better)"; trained on DIV2K, ESRGAN 64nf23nb; tags General Upscaler, Compression Removal. README: CX loss + PatchGAN.
- Nomos8kSC: "4x photo upscaler with otf jpg compression and blur"; trained on Nomos8k_sfw (6,118 images), 85k iterations; tags Realistic, JPEG, Restoration. Phhofm's author notes call the SC (no-noise) variant community-preferred.
- HFA2k: "4x anime image upscaler with a bit of otf jpg compression and blur"; trained on HFA2k (2,568 images); tag Anime. Phhofm README gives no painting/illustration note.
- UltraSharp: "generates a lot of detail and leaves a nice texture", mostly trained on JPEG compression; dataset incl. author RAW photos, DIV2K, rock/stone images; page points to UltraMix for "a more balanced output".
- Remacri: "BSRGAN with more details and less smoothing", created by interpolating Siax/Superscale/Pixel Perfect models; no training set listed.
- Superscale-SP (same repo): "perfect upscaling of clean (artifact-free) real-world images".

Failure modes: OpenModelDB/READMEs do not list failure modes. Everything below is INFERENCE plus Tony's own tests (Portal README, stage 3: remacri best on Book Club Cat gouache art; high-fidelity softer; ultramix adds fake canvas-weave grid; digital-art plastic and colour shift pink; second 4x pass wiry/over-combed).
- Detail-adding models (Remacri, UltraSharp): oversharpening, invented micro-texture, halos on high-contrast edges (INFERENCE from "lots of detail/less smoothing").
- Photo-trained models on painted/flat art: can invent photographic texture in flat areas; JPEG-removal models can smooth fine paint grain (INFERENCE).
- Anime models (HFA2k): flatten gradients and brushwork into cel-like plastic, clean lines good (INFERENCE, matches Tony's digital-art-4x result).

Per-style recommendation (all INFERENCE except where noted; to be confirmed by section 5 test):

| Style | First pick | Challengers | Why |
|---|---|---|---|
| Gouache / painterly impasto | remacri-4x (documented in Tony's test) | Siax | Remacri kept ridges and paper texture; Siax is the permissive-licence, less aggressive alternative |
| Clean line art / calligraphy | HFA2k | Siax, upscayl-standard-4x | Anime-trained models usually keep crisp lines and flat fills (INFERENCE); watch for banding in soft gradients |
| Flat graphic / poster | HFA2k or Siax | digital-art-4x (known colour shift pink on Tony's test, so check colour) | Few textures to invent, want clean edges |
| Photographic | Nomos8kSC | Siax, Superscale-SP, remacri | Trained for real photos with JPEG/blur (documented) |
| AI-generated art (Midjourney/GPT Image look) | Siax | remacri, Nomos8kSC | Source is clean and uncompressed, fits Siax/Superscale description ("clean images") (INFERENCE) |

## 4. Custom models folder and scale/tile

Documented:
- upscayl-ncnn usage (from `upscayl-ncnn -h` on Tony's Mac and source https://github.com/upscayl/upscayl-ncnn/blob/master/src/main.cpp): `-m model-path` = folder path to models (default `models`); `-n model-name`; `-z model-scale` (2,3,4; default 4); `-s output-scale` (default 4); `-t tile-size` (>=32, 0 = auto); `-c compress`; `-f format`; `-x` TTA; `-r`/`-w` resize; `-g` gpu id; `-j` threads.
- Layout: a plain folder holding `<name>.bin` + `<name>.param` pairs; the model name passed to `-n` is the file stem (INFERENCE from the app's folder listing and the Guide; the Guide only says: "Put your NCNN models (in .bin + .param format) into the models folder", the filename becomes the type shown in the app). https://github.com/upscayl/upscayl/blob/main/docs/Guide.md
- Tony's built-in models sit in /Applications/Upscayl.app/Contents/Resources/models (verified locally: 7 .bin/.param pairs).
- Scale detection: "Upscayl will use the model file name to detect the scale... If the model file name has 'x2' or '2x'... target resolution set accordingly" (custom-models README). The Guide: unsupported scales are emulated by downscaling the 4x result (since v2.8). So custom files like 4xNomos8kSC are handled as 4x; do not put "x2" or "2x" in a 4x name.
- Proposed use (INFERENCE, consistent with flags): create a Tony-owned models folder outside the app bundle, copy 3 .bin/.param pairs in, then run `upscayl-ncnn -i in.png -o out.png -m <that folder> -n 4xNomos8kSC`. Set Portal setting `upscayl_models_dir` to that folder (or keep the app folder for built-ins). Creating the folder and downloading is left to Tony (workspace rule: no new folders by agents).
- Tile size: `-t 0` is auto; a tile only affects memory, not the result in principle (tiles are processed with padding); smaller tiles = less GPU memory, slower, small risk of seams (INFERENCE from standard Real-ESRGAN behaviour; the usage text only defines the flag).
- 1024 to 4096: a 4x model with default `-z 4 -s 4` gives exactly 4096 px. For 7200 px on the short side of 24x36 the remaining 1.76x via Lanczos is sane (this is already what Tony's pipeline does; his test rejected a second 4x pass). Alternative worth testing: `-s 2` or `-r` options only downscale from 4x, not upscale beyond.

## 5. Proposed test plan

Models to compare against remacri-4x (baseline): 4x_NMKD-Siax_200k, 4xNomos8kSC, 4xHFA2k (optional 4th: ultrasharp-4x, already installed, but NC-licensed like remacri).

Images (three real ones from different styles): 1) gouache/impasto (Book Club Cat or similar), 2) clean line art or calligraphy, 3) a photographic piece. Optionally a 4th GPT Image/Midjourney-look piece.

Procedure: run each model at 1 pass (4x), then Lanczos to the print size as the pipeline does. Judge crops at 100% of the final size on the same 3 regions per image: a high-contrast edge (halos), a flat area (invented texture or banding), and fine detail (brush ridges, hairlines, paper grain). Also compare colour against the original (digital-art-4x shifted pink). Score each 1-5 for edge cleanliness, texture honesty, colour fidelity; keep the winner per style. Check the model's licence row before adopting.

Suggested mapping to try:
- gouache/impasto: remacri-4x (control) vs Siax
- line art/calligraphy: HFA2k vs Siax
- flat graphic/poster: HFA2k vs Siax
- photographic: Nomos8kSC vs Siax
- AI-generated: Siax vs remacri

Licence note: if Tony wants a clean commercial position, Siax (WTFPL) and Nomos8kSC/HFA2k (CC-BY-4.0 per OpenModelDB) are preferable to Remacri/UltraSharp (CC-BY-NC-SA-4.0), though OpenModelDB's guide says output is not covered by the model licence.

## Source list
- https://github.com/upscayl/custom-models and API listing of /models
- https://github.com/upscayl/upscayl/blob/main/docs/Guide.md
- https://github.com/upscayl/upscayl/wiki/Model-Conversion-Guide
- https://github.com/upscayl/upscayl-ncnn (AGPL-3.0) and src/main.cpp
- https://openmodeldb.info/models/4x-NMKD-Siax-CX, /4x-Nomos8kSC, /4x-HFA2k, /4x-UltraSharp, /4x-Remacri
- https://openmodeldb.info/docs/licenses
- https://github.com/Phhofm/models
- Tony's earlier test results: /Users/tonymacbook2025/Documents/Agent-OS/005_Ecommerce/Etsy-Ikigai/Portal/README.md (stage 3 upscale)
