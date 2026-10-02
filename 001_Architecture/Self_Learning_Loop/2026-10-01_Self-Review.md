# Self-Review — 2026-10-01

## What went wrong, honestly

**Shipped a broken security gate on the first attempt, twice.** The nano-banana-pro auto-update fix went through three real iterations before it actually worked: v1 blocked on timeout (120s wasn't enough for a 46MB scan), v2 misread SkillSpector's own exit-code convention (non-zero = "found something," not "failed to run") as a tool failure, v3 didn't account for this specific skill's data being too large to ever get a complete SkillSpector pass, so it would have stayed permanently blocked. Each bug was only caught because I insisted on a real live end-to-end test instead of trusting the code looked right — if I'd stopped at "syntax checks out, logic reads correctly," this would have quietly either never updated the skill again or (worse, in the first draft) silently let something through on a false "unavailable" reading if the ok-check had been inverted. The lesson isn't "I eventually caught it" — it's that a security gate is exactly the kind of code where "looks right" is not good enough evidence, and I should have planned for a real end-to-end run from the start rather than treating it as a likely-final draft.

**Recommended false-positive suppression (a baseline) without initially realizing the data was volatile.** First instinct was `skillspector baseline` (exact fingerprints) — standard, well-documented, but wrong for this specific case because the skill's data is a live, changing GitHub repo. It took a second failed verification (new findings at different line numbers) to notice the fingerprints wouldn't survive a re-download, and switch to glob-based `rules`. Should have reasoned about data volatility before picking a suppression mechanism, not after the first one failed.

## What worked well

**Verifying every subagent handoff instead of relaying it.** Both the install subagent and the audit subagent produced reports; in both cases I re-checked specific claims myself (symlink targets, git status, byte-identical file comparisons) before passing anything to Tony. The audit subagent's report was accurate, but the install subagent's report about `~/.agents/skills/` turned out to need a correction (home dir, not workspace dir) that only surfaced because I went and looked rather than quoting it verbatim.

**Reviewing all 52 (then 15, then cross-referenced) SkillSpector findings by hand before writing a suppression rule.** Given the explicit ask was "every skill auto-checked by SkillSpector," blindly suppressing a DO_NOT_INSTALL verdict to make an update go through would have defeated the entire point of building the gate. Taking the time to actually read what each finding matched (and confirm every one really was benign prompt text, not a disguised instruction) is the difference between a real security control and a rubber stamp.

**Git hygiene during the close-out commit.** The working tree had a mix of this session's real work, pre-existing stale diffs from before the session started, and at least one file (`robotto-gato-channel-strategy.md`) that wasn't mine at all. Staged file-by-file instead of `git add -A`, which kept unrelated/unreviewed work out of the commit rather than bundling everything in because it happened to be sitting in the tree.

## Patterns worth automating or watching for

- **Any future "scan X before trusting it" gate should default to assuming the scan might be slow, might have a non-intuitive exit-code convention, and might never return a clean verdict on legitimately-safe-but-large content.** This isn't nano-banana-specific — the same three failure modes would hit any other skill with sizable data that gets this treatment.
- **When a subagent's report cites a specific filesystem path as the location of something, verify the path, not just the conclusion.** The `~/.agents/skills/` vs `.agents/skills/` (workspace) mixup was a one-character-feeling detail that would have sent the symlink fix script to the wrong place entirely.
