
## Seedance prompting guide audit

Avoid treating a plausible official recommendation as grounds to erase useful local production methods. Preserve observed evidence and uncertainty separately. Existing paid-call wrapper uses exact numbered uppercase section headings; reviewer caught mismatch in drafted examples, corrected before completion. Preserve historical guide as evidence but mark it superseded, not active instructions.

## Claude Code session (2026-09-26 evening → 2026-09-27)

**What went well**
- Measured instead of argued: running YOLO/YOLOE on the real Shot 07 storyboard turned Tony's "the van grows" into numbers (+56% while parked) and made the scale gate's design obvious. Showing the boxed image let Tony spot what he cared about.
- Tested every gate with dry runs on a scratch copy of a real shot (missing / failed / stale / valid / keyframe mode) — no paid calls, production folders untouched.
- Found root causes instead of cleaning symptoms: stray model copies came from bare-name `YOLO("x.pt")` calls; the "hung" skill-index sync was reading stdin.
- Caught a latent cost bug while updating prices: the monthly refresh would have overwritten fal Topaz with the wrong tier. Pinned it.

**What went wrong**
- Secret scan and `git commit` ran in one command, so the scan's result (2 hits) was read after the push. Hits were harmless (graphify cache hashes), but the order was wrong. Fix: scan → read → commit, always separate steps.
- Under-estimated the YOLOE download (said 50–100 MB, actual ~640 MB incl. text encoder + two pip packages auto-installed). Should have checked the download size before quoting it.
- Early answers were too long for questions Tony asked to be "short and sweet"; he had to ask twice in layman's terms (the "outdated note" explanation). Answer the narrow question first.
- Initially said the Seedance guide said things that were actually in the Neon Parcel skill (Shot 12 / monkey citations). Name the exact file when citing.

**Patterns / automation ideas**
- Any script that loads a model by bare filename will litter the cwd — worth a lint/grep in validate_build.
- Chained background commands hide failures (the TOOLBOX/log steps waited behind a hung sync). Run slow or stdin-reading scripts with `</dev/null` and on their own.
