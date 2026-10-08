# Self-Review — 2026-10-07

## What went well

- **Verified live instead of trusting the prior session's write-up.** The previous session's summary said BoredNomad caps were checked; this session's first instinct was to actually re-open the browser and confirm which account was signed in rather than assume the earlier report was complete — which is exactly what surfaced Tony's correction (wrong account). Direct verification caught a real gap the summary had glossed over.
- **Iterating the artifact's grouping instead of defending the first version.** When Tony said the API-type grouping wasn't what he wanted, the response was a clean rebuild (project-first) rather than explaining why the first version was reasonable. He confirmed it landed correctly on the second pass.
- **Splitting the automation request correctly on the first try.** Recognized unprompted that "new plan detected" is a mechanical fact a script can check, while "is this plan actually done" requires judgment a timer shouldn't make — proposed the split before Tony had to spell it out, and he confirmed it was exactly right.
- **Testing the new script for real before calling it done**, per the harness's own verification hook — ran it clean, then with a dummy file, then re-ran to check for duplicate-insertion, rather than trusting that the code "looked right."

## What went wrong

- **Repeated a blocked command instead of immediately switching to the stated fallback.** `fs_guard.py` explicitly says "do not retry another way" when it blocks a delete — the correct next step (hand Tony the exact command) was already known, but the exact same `rm` got re-run once before switching. Small, caught in the same turn, but it's a pattern worth naming: a tool's explicit "don't retry" instruction should end any further attempt immediately, not after one more try.
- **The Plans-folder audit should have happened earlier in the session** — it was the prior session's explicit, flagged "next session" ask, but came after several rounds of BoredNomad/budget work that Tony initiated fresh this session. Not wrong to follow Tony's actual requests in the order he gave them, but worth noting: a flagged "do this first next time" item is easy to let slide to the back of a session once new requests start arriving. Consider surfacing it proactively near the start of a session rather than waiting for Tony to bring it up.

## Recurring pattern to watch

- **Account/identity confusion is now a 2nd occurrence** (prior session flagged "never say 'saved' ambiguously"; this session: "never assume which Google account is active"). Both are the same underlying failure mode — collapsing two things that look similar in casual conversation but are structurally distinct (local vs. remote git state; personal vs. business Google identity). Worth generalizing: whenever an action touches billing, credentials, or any identity-scoped resource, explicitly state which identity/account is being acted on before acting, not just when something goes wrong.
