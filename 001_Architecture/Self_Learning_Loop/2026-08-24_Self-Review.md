# 2026-08-24 Self-Review

Scope: closing out the 0002_Mantis_Shrimp_Color_Vision overlay-build arc (spans 2026-08-23 into 2026-08-24) — Tony explicitly asked for this analysis, framed around one question: why did this video need so much iteration, and what has to change so the *next* one needs less.

## Tony's framing (verbatim intent)
"Each new video we generate, no matter what channel, should constantly have fewer and fewer iterations... the idea is to get these 99.9% autonomous and now what we've currently done is about 50% autonomous. I've had to spend hours and days reiterating this particular video just to get it to a grade A."

## Pattern across every mistake this session

Every single miss this session — the digit-grid misread, the off-screen/overlapping labels, the "which end is the very end" assumption — shares one root shape: **a plausible internal signal was trusted as if it were the actual verified outcome.**

- Detected coordinates *looked* grounded (real feature, real pixel) → trusted as "the label will be readable." It wasn't — layout quality is a separate property from coordinate accuracy.
- A verbal description *sounded* like enough to generate from → trusted as "this matches the existing asset." It didn't — the real file diverged from the paraphrase.
- `astats` output *looked* like a real measurement → trusted as ground truth. It returned identical values across different timestamps and was silently wrong.
- "The very end" *sounded* unambiguous → trusted as "the file's last frame." The actual audio content ended ten seconds earlier.

None of these were reasoning errors in the moment — each decision was locally sensible. The miss was skipping the step of checking the claim against the actual rendered/measured artifact before presenting it as done. Where that verification step *was* done (pixel-measuring crest positions, numpy RMS scans, extracting real frames for mockups), the fix landed correctly on the first or second try. Where it wasn't, it took a Tony correction to surface.

## What actually worked, and should generalize

1. **Cheap-first iteration.** Tony's own suggestion — static mockup before a Remotion render — is the general pattern worth defaulting to for *any* visual layout question: iterate on the cheapest artifact that can actually be judged, before spending a full render/generation cycle. This should be a reflex, not something that needs suggesting.
2. **Asking targeted clarifying questions before a second guess.** When "Matrix waterfall... don't take it literally" was still ambiguous, asking two concrete multiple-choice questions (flip motion, full-bleed method) got it right on the very next generation — no third miss. Compare to the first miss, where a vague brief ("zeros and ones... basically the attached signal pattern") was generated from without first confirming what was actually meant.
3. **Self-caught issues before presenting.** The "very end of the audio" ambiguity and the astats unreliability were both caught *before* telling Tony something was fixed, by actually measuring rather than assuming. This is the behavior to scale up, not the exception.

## Concrete changes made (not just noted — written into governing files)

- `Diagram-Generation` SKILL.md: label-layout-safety checklist + mockup-first workflow + real-asset-as-reference rule.
- `Anomalous_Wild_Video_Pipeline` SKILL.md: mandatory audio-continuity scan with the correct measurement method, end-card CTA VO as a standard step.
- Cross-session memory: Seedance version default correction, naming-convention scope clarification.

## What would most reduce iteration count next time

If there's one single practice to carry forward, it's this: **before presenting any generated/positioned/mixed output as finished, verify the specific claim being made against the actual artifact — a real extracted frame, a real measured amplitude, a real pixel position — not the code, the prompt, or the plausible-sounding description that produced it.** Every miss this session would have been caught by that one discipline applied earlier. The skill-file updates above are the attempt to make that verification step structural (built into the documented process) rather than something that has to be remembered fresh each production.

## Honest gap

This review is being written *after* the fact, from one production's worth of evidence. Whether the skill updates actually reduce iteration count on the next Anomalous Wild video (or any other channel's diagram/audio work) is unconfirmed — worth checking explicitly on the next production that touches diagram labeling or end-card audio, rather than assuming the fix worked.

---

## Addendum, same-day afternoon session — Thumbnail Generation Arc

Direct continuation of the pattern above, and a clean instance of the exact same root shape recurring in a completely different domain (image compositing instead of diagrams/audio): **a plausible internal signal (PIL math against guessed pixel coordinates) was trusted as "the arrow points at the eyes" without checking the actual rendered pixels for overlap.** Same failure shape as the digit-grid misread and the off-screen labels from the diagram arc two days earlier — the fix that worked was identical too: stop trusting the generation method's internal logic and look at the real output.

**What was different this time, and worth noting as progress:** Tony's correction didn't just fix the immediate image — it pointed at a *process* gap ("you really should have references from the last video... why does your vision not really inspect those things?"). Checking the real `0001_Bioluminescence_Weapon` reference file (not just my own visual judgment of my own output) revealed the actual right method — image-to-image editing via the model itself, not hand-coded overlay math — which a purely "look harder at your own output" fix would never have surfaced. **Generalizable lesson: when a visual/creative output style needs to match a precedent, locate and inspect the actual precedent file before inventing an approach, even when a written spec (the JSON template) exists** — the spec and the real historical practice had drifted apart (the script never actually implemented what the JSON described), and only the real file exposed that gap.

**Second-order finding:** this also caught a latent pipeline bug that had nothing to do with the immediate task — `generate_youtube_package.py` had *never* produced a finished (text+arrow) thumbnail for any production; the one example that looked finished was hand-built off-script in a past session and never fed back into the tool. This is worth generalizing: when a "reference example" is found, verify it was actually produced by the documented/automated path before trusting that path to reproduce it — an example produced by manual intervention proves the *result* is achievable, not that the *pipeline* achieves it.

**What converted this into a lasting fix, not just a one-off correction:** the session didn't stop at "Tony approved the images" — it went one step further per his explicit ask ("this style should always be the thumbnail generation so lock that in") and rewrote the actual generator script + JSON template + SKILL.md so the next production gets this automatically. This matches the meta-principle from the diagram/audio arc above: write the lesson into the file that governs the step, not just a memory note. Two days in a row, the same discipline (verify against the real artifact, then encode the fix structurally) resolved a materially different class of problem — that's a reasonable signal the discipline itself, not the specific fixes, is the transferable skill.
