# Self-Review — 2026-09-23

## What went wrong
- **Misread the spatial concept (Shot 07 env v1).** I built a shopfront street when Tony meant a CCTV overlooking the bay. I didn't restate the camera direction before building. My v1 plans also contradicted each other (the blocking plan had the camera on the shop; the site plan had the shop across the street) and I didn't catch it until I reread them. Fix: restate the camera facing and the background in one sentence to Tony before any site plan.
- **Deviated from the proven Seedance template.** I added a "later panels" sentence and changed "every panel of @Image 1" to "panel 1 of @Image 1" to carry Tony's notes. The first video reproduced the grid. Even after restoring the wording, v2 reproduced the sheet frame, so the template alone isn't a guarantee, but deviating was avoidable.
- **Designed an end frame whose state was far from the last frame** (water behind the quay wall). The extend model pulled the water onto the road. Tony's simpler route (no end frame, a local path) worked first time.
- **Tool friction:** assumed the `wavespeed upload` JSON shape (`url` vs `urls`), which sent one empty call (rejected with 400, no charge). Also hit a missing Generation_Log.json (guard blocked it, no charge) and several provider timeouts. None cost money, but each cost a round trip.
- **Scale drift not caught before video:** storyboard v2 still had the van inconsistently sized, and the final came out 1.5-2x too large. Numeric sizes in prompts weren't enough.

## What worked
- claude-mem diagnosis: read the actual worker code instead of guessing, found the real cause (env file, not shell env), and fixed it without duplicating the key.
- Always checking the real artifact frame by frame caught every failure (grid, sheet frame, water on tarmac, zoomed end frame) before any upscale spend.
- Salvage by crop saved a paid regeneration.
- Using the Magnific MCP when the script lacked the capability (Topaz model choice); the CLI-first rule allows this.
- Verified the fal upscale change with a real ~$0.06 end-to-end test before calling it done.

## Recurring patterns / automation ideas
- Seedance 2 Mini reference mode has now reproduced reference layouts twice in a row on one shot. Worth an automated post-generation check (detect a grid or border in the first frame) before anyone reviews or pays for an upscale.
- The Tool-Manager catalog is stale on upscalers (no fal/WaveSpeed prices); a refresh would make cost choices automatic.
- WaveSpeed uploads need a hosting helper (Cloudinary) in the tooling, not ad-hoc code.

## Codex Seedance clarification — 2026-09-23
- Read actual skills before recommendations. Earlier advice duplicated existing exclusions and conflicted with labeled-sheet requirements; user clarification distinguished accepted risk from prompt instructions.
