# 2026-07-10 — Self-Review

## What went wrong (and got caught)

### 1. Defaulted to "the one color already in nearby code" instead of checking fit
The very first render reused the channel's brand-green accent purely because it was the only color present in the existing `SceneOverlay.tsx` component I was pattern-matching against. I never asked "is this color actually right for *this* image" before using it — I asked "is there a color already established," found one, and stopped there. That's a shallow form of consistency-seeking that skips the actual judgment call. The fix (sample the real image) was easy once prompted, but I should have run that check before the first render, not after a correction.

### 2. Optimized for "prove the technical claim" over "look at the whole composition"
When placing the two callout targets, I picked coordinates I'd already confirmed were glowing pixels (from an earlier color-sampling pass) — which proved the color was right, but I never stepped back and looked at whether the two labels, together, made a clean composition. Same pattern repeated one level up: after fixing crossing lines, I didn't check whether the fix (two parallel vertical lines) was actually good, just that it wasn't the old bug. Twice in one build, I treated "not exhibiting the previously-flagged problem" as equivalent to "good," instead of independently asking "does this look right" each time.

### 3. Trusted the first search result without checking genre-fit
Asked to ground a leader-line composition decision externally, the first web search returned patent/technical-drawing convention (uniform parallel callout lines) — which is a real, citable principle, just for the wrong genre, and it directly contradicted the reference image Tony had already given me. I did catch this before applying it (checked whether it matched the reference), but it's worth naming as a real failure mode: a citation being real and relevant-looking doesn't mean it's the right citation for the specific context.

## What worked well

### Verifying every color/placement claim against actual pixel data, not eyeballing
Every color decision and every "is this open space" placement decision in this build was checked by sampling the actual image with PIL rather than guessing from a description or a rendered thumbnail. This turned "I think that's black" into a verified fact, and it's exactly the kind of check that should generalize as a habit for any future diagram/callout work — cheap, fast, removes an entire class of avoidable error.

### Correctly separating "isolation" from "expertise" when asked about a subagent
Tony asked whether a specialized motion-graphics subagent should exist. It would have been easy to say "yes" reflexively, since he framed it as wanting a "God-level" expert. Instead the honest answer was that a subagent doesn't carry taste on its own — only what's written in files it reads — so the actual lever was a skill (durable, readable knowledge), with a subagent being a separate, optional decision about isolation/parallelism. This distinction turned out to be the right call: the skill is what Tony asked to build.

### Treating this session's own corrections as the primary source for the new skill, not inventing content
When researching the vault for the new Motion-Graphics skill, the honest finding was that the vault's own style docs (Kinetic Typography, Vox Documentary, Kurzgesagt Animated) are placeholders with no real validated content — and rather than papering over that gap by inventing confident-sounding rules, the skill was structured with explicit confidence tiers (proven ledger > general principles > unvalidated aesthetic direction) so a future agent can tell the difference. This matters because the whole point of tonight's work was to stop presenting guesses with the same authority as corrections.

## Pattern to watch going forward

Tony ran this session as a structured interview before deciding what to build — asking process questions (subagent usage, pipeline invocation, whether a skill was needed) rather than jumping straight to a request. He explicitly held back one piece of feedback (bigger spring, more label glow) until he said "lock it in." That's a deliberate pacing pattern worth recognizing quickly in future sessions: when he says "hold onto that, I'll tell you when to act," the right move is to stop building immediately and wait, even mid-flow — not to fold the feedback in "while I'm at it."
