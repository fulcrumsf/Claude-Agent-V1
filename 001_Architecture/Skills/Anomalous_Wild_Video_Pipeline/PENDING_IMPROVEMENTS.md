# Anomalous Wild Pipeline — Pending Improvements

Generated 2026-08-26 from the 0003_Glass_Frog_Transparency test run. Nothing here has been implemented yet — this is the punch list to work from next.

---

## 1. NEW CAPABILITY — NotebookLM as a reference/diagram-grounding source (Tony-approved 2026-08-26)

**What to add:** Document NotebookLM's `generate infographic` (and optionally `generate video` explainer) as an available, non-mandatory reference-material option for diagram beats — same tier as the existing Wikimedia reference-image search, not a replacement for the Scientific Diagram sub-pipeline's own illustration/label/animate steps.

**Where it goes:**
- `Anomalous_Wild_Video_Pipeline/SKILL.md`, Phase 1 Step A3 — after the existing NotebookLM briefing-doc paragraph, add: NotebookLM can also generate a `scientific`-style infographic (or short explainer video) of a specific mechanism/anatomy beat once sources are loaded — useful as an *additional* reference image for Phase 6B's `diagram_research_and_illustrate.py`, alongside Reference_Images/. Not mandatory; use it when it would genuinely improve grounding for a complex mechanism (e.g. an internal process a plain photo reference can't show).
- `Anomalous_Wild_Video_Pipeline/SKILL.md`, Phase 6B — cross-reference: if a NotebookLM infographic exists for this beat's mechanism, pass it alongside (not instead of) the Openverse reference image into `diagram_research_and_illustrate.py`'s reference step.
- Clarify explicitly: NotebookLM's own generated visual (infographic or video) is **never** cut into the final video directly — it doesn't match the channel's locked dark-neon hybrid brand and isn't synced to real word-level timestamps. It's grounding input only, same restriction that already applies to Reference_Images/.

**Verified working (2026-08-26 test):** generated a `scientific`-style landscape infographic of the glass frog's mirrored-liver blood-hiding mechanism from the production's own NotebookLM notebook sources — Tony approved the output as visually accurate and useful reference-grounding material. Command pattern confirmed:
```
notebooklm generate infographic "<detailed mechanism description>" --orientation landscape --detail standard --style scientific --notebook <id> --json
```
(long-running — 5-15 min — use the same background-agent wait/download pattern as the briefing-doc report.)

---

## 2. FIX — `new_video.py` is fully interactive, incompatible with non-interactive execution

**Problem:** Format/duration/topic-pick/folder-name prompts all use `questionary.select()`/`.text()` with arrow-key input and a blocking `.ask()` call. There's no way to answer these programmatically or via piped stdin in this harness. Every pipeline run hits this wall at Phase 1 Step A.

**What was done as a workaround (this run only, not persisted anywhere):** imported `new_video` as a module and called `research_ideas_perplexity()` directly, bypassing the interactive UI entirely; used `AskUserQuestion` for format, duration, and topic selection instead.

**Cross-harness requirement (Tony, 2026-08-26):** this pipeline needs to run identically across Claude Code, the Antigravity VS Code plugin, plain VS Code, Codex, Claude Code Desktop, Warp terminal, and any terminal inside any of those — plus possibly Hermes in the future. That rules out a Claude-Code-only bypass (e.g. relying on `AskUserQuestion`, which doesn't exist outside this harness) as the real fix — it only ever papers over the problem in one environment.

**Recommended fix — Option B is now the real requirement, not just a nice-to-have:**
Add a genuine non-interactive mode to `new_video.py` itself:
- CLI flags for format and duration (e.g. `--format long --duration 3-5min`), skipping the `questionary.select()` calls entirely when passed.
- `--json` output mode for the researched topic ideas (print the list, exit 0) instead of blocking on `questionary.select()` for the topic pick — whatever orchestrator/agent is driving the script (Claude Code, Codex, a human at a Warp prompt, etc.) presents those choices in its own native way and re-invokes the script with the chosen topic/title/hook as flags to proceed.
- Keep the existing interactive `questionary` flow as the default when no flags are passed, so a human running it directly from any of these terminals by hand still gets the guided prompts — only skip it when the caller explicitly passes machine-driven flags.
This makes the script itself portable across every harness rather than requiring each harness's orchestrator to know a special bypass trick.

**Superseded:** the lighter "just document the Claude-Code-specific bypass in SKILL.md" option — still fine as an interim note, but not the actual fix given the multi-harness requirement.

---

## 3. FIX — Phase 1 step ordering: Step A3 needs `production_folder` before Step C creates it

**Problem:** SKILL.md's Phase 1 lists Step A3 (Production-Research-Agent + NotebookLM, requires `production_folder` to already exist) *before* Step C (scaffolds the production folder). Every run has to silently reorder this in practice.

**Fix:** Reorder Phase 1 in SKILL.md so Step C (scaffold) runs immediately after topic selection (end of Step A) and before Step A3 — i.e., new order: Step A (questionnaire+research+topic pick) → Step C (scaffold folder) → Step A3 (research agent + NotebookLM, now has a real folder to write into) → Step B (script, saved into the now-existing `Scripts/` folder). Renumber the lettered steps to match reading order so a future run doesn't have to solve this ordering puzzle again.

---

## 4. PROCESS RULE — Banned-word list needs an explicit exception path

**Problem:** `Anomalous-Wild-Scriptwriter.md`'s banned-words list includes "blood" — fine for the channel's general tone-policing goal (avoid gore/shock language), but it will conflict with any topic where a banned word is also the accurate scientific term for the subject (glass frogs, this run; likely to recur — e.g. anything involving venom/predation could hit "attack" or similar).

**Fix:** Add a short rule to `Anomalous-Wild-Scriptwriter.md`'s banned-words section: "If a banned word is also the accurate, necessary scientific term for the chosen topic (e.g. 'blood' for a topic literally about blood physiology), flag it to Tony for an explicit per-production exception before scripting — do not silently include it, and do not silently write around it with awkward euphemisms without asking first." This just codifies what already happened correctly this run (asked before proceeding) so it's not left to be re-derived from judgment alone next time.

---

## 5. ENVIRONMENT — Two one-time fixes worth documenting, not re-doing

Neither of these needs pipeline code changes — they're machine/environment state, already fixed on this machine. Worth a one-line note in `TOOLBOX.md` or a `requirements.txt` for the AW tool folder so a fresh environment doesn't hit them blind:

- `questionary` (Python package) was missing — required by `new_video.py`. Installed via `pip install --break-system-packages questionary`.
- `notebooklm-py` was on v0.3.4, which has a known bug ([teng-lin/notebooklm-py#865](https://github.com/teng-lin/notebooklm-py/issues/865)) — right after a fresh login, Google may not have yet minted the `__Secure-1PSIDTS` session-rotation cookie, and 0.3.4 doesn't recover from that, so `notebooklm login` looks like it silently fails no matter how many times you retry it. Fixed in v0.5.0+. Upgraded to v0.8.1 on this machine — the upgrade alone (no re-login needed) fixed the existing session.

**Suggested fix:** add a note to `TOOLBOX.md`'s NotebookLM entry: "if `notebooklm auth check --test` shows `token_fetch: false` after a normal-looking login, check `notebooklm --version` first — anything before 0.5.0 has a known session-cookie recovery bug; upgrade before troubleshooting the login flow itself."

---

## Already resolved this session (no action needed)

- `pipeline_supervisor.py`'s hardcoded `/tmp/biolum_*` state paths and hardcoded `BASE` production folder — fixed and verified (compile check + `validate_build.py` + live test with a scratch production folder) before this pipeline run started. `BASE` now comes from CLI arg 1, state files live under `<production>/Production/_supervisor_state/`.
