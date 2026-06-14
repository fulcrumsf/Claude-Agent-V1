# Self-Review — 2026-05-09

## What Went Well

**Multi-agent audit was the right call.** Running Gemini (large-context coherence) + Claude embed scanner in parallel surfaced contradictions that a single-model pass would have rationalized away. Gemini caught the Asset_Notes dead path (C4) that had been silently broken for weeks. The embed scanner gave exact BAD→FIX pairs rather than a vague "some embeds are broken." This is the pattern to repeat for any pipeline that has been iterated across multiple sessions.

**Staged batching for re-vision.** Moving bad-named files to `_staging_bad_names/` before running the vision pipeline was correct — it isolated the problem set, made progress visible, and made recovery possible if the script crashed mid-run. Don't skip this staging step for large batches.

**Fix-first, run-second discipline.** When the Title-Case bug was discovered mid-run, killing the process and fixing before restarting was right. The cost of running with a known bug is always higher than the delay to fix it.

## What Went Wrong / Should Be Done Differently

**C4 was a months-old broken gate.** `check_vision_needed.py` was pointing at `Asset_Notes/` — a directory that never existed in the current pipeline — since at least May 1. Every "already cataloged: 0" audit result was a silent lie. This should have been caught the first time it returned an implausibly low count. Going forward: if an audit script returns 0 for a category that should have hundreds of entries, that is a red flag — investigate the script, not the data.

**Dead fields in the AI prompt.** The `kebab_case_image_name` field was still in the PROMPT JSON spec long after the code stopped using it. This creates genuine AI confusion about which format to return. Rule: if a field is removed from the consuming code, remove it from the prompt on the same commit. Never let the prompt and the parser diverge.

**Documentation lag.** SKILL.md and TOOLBOX.md both said "Gemini vision first" for months after the pipeline switched to OpenRouter. These docs are the single source of truth for agents and should be updated in the same session as the code change, not weeks later during an audit. Rule: when a script's primary API changes, update SKILL.md, TOOLBOX.md, and MEMORY.md in that same session.

**rename_screenshots.py had no deprecation notice.** It was left active and callable with no warning that it produces lowercase filenames and uses an incompatible API. Any agent picking it up would have broken the naming convention. Always deprecate legacy scripts immediately when superseded.

## Patterns to Carry Forward

1. **After any pipeline run, spot-check the output before declaring done.** Count: does the "already cataloged" number look plausible? Do the filenames follow Title-Case? Did notes land in the right folder? One minute of spot-checking prevents the kind of long-tail cleanup that took hours today.

2. **Prompt ↔ parser must stay in sync.** If the parser doesn't read a field, the prompt shouldn't ask for it. If the prompt asks for a field, the parser must handle it.

3. **Category-folder note lookup is the correct pattern.** Notes live in `Tools/`, `Research/`, etc. — never in a flat `Asset_Notes/` dir. Any script that reads notes must search category folders.

4. **Embed fix script (`fix_embeds.py`) is now a standard cleanup tool.** Run it after any batch rename or ingest that might have created case mismatches. 549 fixes in one pass — it's fast and safe.

5. **Multi-model audits before declaring a pipeline stable.** Before saying "the pipeline works," do one Gemini coherence pass across all related scripts. The cost of an audit pass is far less than discovering contradictions in production.

## Open Items Deferred

- 2,702 not-found embeds — images were semantically renamed but paired notes still reference old filenames. Needs a rename-log → embed mapping approach or manual review. Deferred to Tony.
- 435 ChatGPT export images in `007_Resource_Library/OpenAI_History/ChatGPT_Image_Generator/` still need vision ingest — in Todo.md.
- Agent-OS rename + build — in Todo.md.
- Meta Graph API key — in Todo.md.
