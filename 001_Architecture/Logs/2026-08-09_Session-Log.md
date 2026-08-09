## POV Pipeline v2 — final lock-in and production hardening
- Folded all confirmed findings from prior manual test productions (Titanic Stoker, Roman Gladiator round 1) into real code, per Tony's "prove it before you build it" instruction from earlier in this session.
- `prop_sheet_generation.py` (new) — front/back/held-from-POV panels per prop; revised same day to `held_left`/`held_right` (hand-specific) after a real thumb-orientation bug on the Roman Gladiator shield.
- `environment_sheet_generation.py` — rebuilt to one sheet per location, one panel per scene, strictly people-less, no panel reuse.
- `storyboard_generation.py` — panels write to `Assets/Images/Scenes/` (new subfolder convention, enforced in code); added per-beat `sheet_labels`/`input_urls` overrides.
- `video_generation.py` — **confirmed live 2026-08-08 that `first_frame_url` and `reference_image_urls` are mutually exclusive on kie.ai's real endpoint** (previous architecture note assumed both could combine; never tested end-to-end). Fixed: `submit_video_task`/`generate_video` now raise `ValueError` if both are passed; normal path uses `first_frame_url` alone since the sheet-driven image stage already bakes in consistency.
- `shot_list_builder.py` — clarified `@Image1`/`@Image2` ordinal tagging only applies to the `reference_image_urls` fallback path, never alongside `first_frame_url`.
- `Seedance-Prompting-Guide/SKILL.md` — added "Hand/limb laterality in POV and multi-character shots" (cross-tool, applies beyond Seedance) after a real Scene 6 handshake bug (mismatched hand/arm laterality); added the first_frame_url/reference_image_urls mutual-exclusivity correction.
- `POV_Style_Guide.md` scene-writing checklist grew to 9 items this session: hand/limb laterality check, perspective-distortion/foreshortening check (Scene 13 "looking up" read as lying down due to fisheye + foreshortened raised arm).
- Fixed a real Remotion bug: `POVShort` composition in `Root.tsx` hardcoded `durationInFrames={1560}` (65.0s), silently truncating any render whose actual video ran longer — added `calculateMetadata` to size it from `props.durationInFrames`, computed live in `text_overlay.py` via `measure_video_duration_seconds()`.
- Full pipeline test suite: 126/126 passing, `validate_build.py` clean on every touched file.

## Two full productions, image gen through publish
- **Roman Gladiator (0005)**: regenerated Prop Sheet (hand-specific), regenerated scenes 6/7/8/9/10/13 after direct visual critique (handshake laterality, shield grip, sword placement away from centerline, perspective/foreshortening on the victory shot), assembled 13-scene video, Suno music bed, text overlay, published to YouTube/TikTok/Instagram/Facebook via Blotato.
- **Titanic Stoker (0004)**: regenerated shots 2/9/13 video clips from already-corrected first-frame images (this production never had those 3 shots' videos generated before), full assembly + text overlay + publish, same 4 platforms.
- Both productions' live URLs are in this session's chat history; not duplicated here.

## Social copy work (non-pipeline)
- Rewrote Reimagined Realms' Facebook page description and Instagram/TikTok bios after Tony's channel-concept pivot (alt-history "what if" → accurate-but-immersive visual storytelling) — iterated twice to strip language that reads like a documentary-accuracy claim ("real historical events") in favor of "imaginative glimpse" framing that doesn't invite nitpicking.

## YouTube stats research
- Pulled ReimaginedRealms channel stats via YouTube Data API (198 subs, 131K views, 244 videos).
- **Found and corrected a real methodology bug of my own**: `search.list?order=viewCount` is an approximate/algorithmic ranking, not an exact sort — it silently omitted a video (Megalexandros, 1,716 views) that belonged in the true top 10. Fixed by pulling the full 244-video uploads playlist and sorting exact `statistics.viewCount` locally. Tony caught this by cross-checking against YouTube Studio.
- Brainstormed monetization/growth angles given the channel-concept pivot: flagged the tension between top-performing old "what if" content and the new direction, noted the Shorts-specific monetization path (1,000 subs + 10M Shorts views/90 days) is likely faster than the watch-hours path given current channel shape.

## Session close-out
- New feedback captured: image QA must check whole-composition plausibility not just element-presence; prop sheets need hand-specific held panels; first-frame-is-the-reference (never re-attach sheets at the video stage); always back up a superseded asset to a sibling `Rejected/` folder before overwriting (Tony's standing rule going forward, workspace-wide).
- `Skill-Index.md` re-synced to register `reimagined-realms-pov-shorts-pipeline-v2`.
- Graphify auto-updates via the Stop hook — no manual trigger needed this session.
