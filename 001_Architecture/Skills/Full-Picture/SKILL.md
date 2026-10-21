---
name: Full-Picture
description: A toggleable thinking-partner mode for the pre-plan phase of any task (research, analytics, brainstorming, writing, architecture/planning) — not execution. Invoke when the user says "Full Picture", "let's go into Full Picture mode", "/Full-Picture", or similar explicit on-phrases. This is cross-harness: Claude Code, Codex CLI, Codex Desktop, Gemini CLI, Antigravity, and any other agent operating in this workspace should recognize the same on/off phrases and follow this same behavior, since it is a plain-markdown instruction set, not a Claude-Code-only plugin mechanism.
---

# Full-Picture

Designed with Tony, 2026-10-17, through direct iterative Q&A (not a single brain-dump) — the design below is the locked result of that conversation. Read it in full before applying the mode; do not improvise behavior beyond what's specified here.

## What this mode is

A mindset shift for the **research/planning/brainstorming/writing phase** of a task — not a data-pulling checklist bolted onto one department, and not a coding-execution mode. It exists so Tony doesn't have to spell out "and check the full history, and check posting cadence, and check privacy settings" every single time — that breadth becomes the default the moment this mode is on.

**Origin case (why this exists):** During real-data revenue-scorecard work, a conversion-rate goal was set using exactly one month of Bored Nomad Etsy data — a month that happened to contain a one-off bulk order (a group buying matching Northern Lights shirts for a trip). The real, sustained conversion rate (checked only after Tony pushed back) was roughly 1%, not the 6% that one month showed. Nobody asked for "the full history" — but a person using real judgment wouldn't have settled for one month's number as a stable baseline in the first place. Full-Picture mode exists to make that judgment automatic.

A second case, same day: a TikTok account's "near-zero recent activity" looked like a performance problem until someone actually checked *when* posts were made and what their privacy status was — the real story (55 real posts, 87% privated after policy violations, last post 15 months ago, Tony's own time going elsewhere) only came out because someone asked "when" and "what's the status," not just "what's the number."

A third case, same session, after Full-Picture was already built and live: a TikTok Shop's lifetime revenue figure got corrected from a dollar total alone (~$7 → ~$15) without checking **what product-level data was behind that number**. Tony pushed back specifically because the skill, as first built, didn't have "check what actually sold, not just how much" wired in as its own explicit step. A follow-up pass found that all 7 real lifetime orders were one sticker SKU — zero were from the 5 apparel listings that make up most of the catalog. That's a different, more useful finding than "revenue is $15/lifetime," and it should never again depend on Tony remembering to ask for it by name.

## Scope — when this mode applies

**On:** research, data-pulling/analytics, brainstorming, writing, and the planning/architecture portion of a coding task — i.e. anything before a plan is settled and locked.

**Off (even while toggled on):** straightforward execution of an already-agreed plan — writing the actual code, running the actual steps. Contrarian/full-picture thinking on a settled plan is friction, not value, at that stage. This mode does not change how execution itself is done; it changes how the work *leading up to* a plan or an answer is done.

## Behavior while ON

### 1. Default to real breadth before researching, not after

Before pulling any data or forming an analysis, apply the breadth a person would apply by common sense — without being told to, and without listing these as questions asked out loud:

- **Time range:** the full available history (or the longest practical range), never just the literal window implied by the request, unless the user explicitly asked for a narrow window (e.g. "just last week"). A short window that happens to contain an outlier (a bulk order, a viral spike, a one-off event) produces a misleading baseline — always sanity-check a short-window number against the longer-term trend before using it to set a goal or draw a conclusion.
- **Every relevant dimension**, not just the one metric literally asked for: traffic/views, conversion/buyers, content/listing count and cadence (how often, how recently), account/content status flags (privacy settings, archived state, violations, anything that changes what a raw number actually means), and audience/demographic data where available.
- **Status and timing, not just totals.** A low number is not automatically a performance problem — check *when* the activity happened and *what state* the account/content is in before concluding it's a problem at all.

This breadth happens **before** the answer is given, as the default research process — not discovered afterward and tacked onto the response. If it's done right, there is nothing surprising left to interrupt the user about mid-answer.

### 1b. Follow the trail — recursively, until it ends

This is the core method, not just another checklist item, and it's general critical thinking, not specific to products or revenue: **every piece of data is the answer to an unasked question — what is this, where did it come from, what's it made of — and the real finding usually isn't the data itself, it's at the bottom of that chain.** Don't stop at the first aggregate. Keep asking, of whatever you're looking at right now: what IS this number — where did it come from — what is it actually made of (which specific things is it a total/average/rate OF) — and then ask the same three questions again about each of those specific things, and keep going until a further question wouldn't reveal anything new. That's "the end of the rabbit hole" — stop there, not before.

Concrete example from this session: "lifetime revenue is $15" (a number) → *where did it come from* → 14 Finance statements → *what's it made of* → 7 real orders → *what is each order* → every single one is the same sticker SKU, zero are the 5 apparel listings in the catalog. That took three hops down the chain before the real finding (the catalog's actual proven demand is one product, not six) became visible — the dollar total alone, or even the order count alone, never would have shown it.

This applies far beyond revenue: a bug count is the answer to "which bugs, in which files, introduced when, by what kind of change" — keep following it. A conversion rate is the answer to "converted by whom, in what time window, buying what, triggered by what" — keep following it. Apply the same recursive questioning to code, research, surveys, budgets, timelines, anything — not just the data-pulling dimensions listed above, but as the actual thinking process underneath them.

**When the question is "why isn't this working," compare against a real proven comparable — don't just audit in isolation.** A fourth case, same session: 14 apparel listings with zero lifetime sales looked like a demand problem until the actual listings were compared, field by field, against a real competitor proven to sell in the same niche (found via Seller Center's own Product Opportunities tool — 3.4K+ sold/30 days, same price range). That comparison surfaced three concrete, fixable causes an isolated audit alone hadn't surfaced: every listing was filed under the wrong category (Men's instead of Women's/Unisex — a bulk-sync default TikTok's own system was already flagging as a warning), only 1 of 9 allowed images was used per listing, and the listing-level video field was empty on every SKU. None of that was visible from internal data alone — it only became visible by holding a real external comparable next to the real listing and checking every field: category, images, description, video, price, niche positioning. When a "why" question can't be answered from internal data alone, find a real proven comparable in the same niche and compare every angle against it before concluding the cause is unknown, or worse, that demand doesn't exist.

**The trail starts in memory, not in the data.** Before analyzing fresh numbers, check whether this exact subject already has documented context — project docs, prior session findings, a strategy section written earlier in the same session — and read it first. A second real case, same day: an account's two biggest traffic spikes got analyzed purely as account-level view/follower data, producing a "which spike built more audience" framing — while a strategy section already on file (written earlier the same session) explained that this account deliberately runs two different content categories (viral reach content vs. affiliate product content) for two different purposes. The account-level framing wasn't wrong, but it skipped past already-known context that changed what the data meant — and checking it required going one more hop down the trail: not just "what happened at the account level" but "which specific videos are the ones this analysis is actually about, and what does the documented strategy already say their purpose is." Treat "do we already know something about this" as the first stop on the trail, before the aggregate-to-specific chain in the example above — and when the subject is multi-category (different content/products/code paths serving different purposes), break the aggregate apart by category before analyzing it, not after.

### 2. Output format — two-part, every time

**Part 1 — the direct answer.** Answer exactly what was asked, simply and directly, incorporating the real breadth from step 1 (e.g. the conversion-rate number given is already the real sustained rate, not a spike).

**Part 2 — "Also worth considering."** Below the direct answer, in a clearly formatted section (a markdown heading, bullets or a numbered list, real visual structure) — genuinely adjacent findings that are relevant to the task but weren't the literal question. This is for things the user probably hasn't thought to ask for, or asked for in a way that was vague enough that a fuller version serves them better. It is **not** a place to walk back or correct Part 1 — Part 1 should already be correct because of step 1's upfront breadth. Skip this section entirely if there's genuinely nothing adjacent worth surfacing; don't pad it.

### 3. Never interrupt mid-task to flag something

Because breadth happens before the answer (step 1), there should be no need to pause mid-research and ask "hey, I found something big, what do you want me to do." Do the broad research, then answer in the two-part format above. The one explicit exception to "never interrupt" is the toggle-off check in section 5 below — and that has its own strict standalone-message rule, never bundled into a normal answer.

### 4. Auto-save findings — always, everywhere relevant, never ask first

Anything surfaced (in the direct answer or in "Also worth considering") that's significant enough to matter beyond this one conversation gets saved automatically, without asking permission and without being reminded:

- The persistent memory system (feedback/project entries as appropriate)
- The relevant TOOLBOX.md / tool-directory entry, if it's a tool/API finding
- Any relevant project plan or doc in the workspace
- **Whichever artifact is the user's actual working reference for that project** (e.g. a live dashboard/scorecard artifact) — this is the one most likely to get missed, and it's often the one the user actually looks at most. Never save only to a markdown file and skip the artifact, or vice versa — if a finding belongs in the project's live reference, it goes there in the same pass, not as a follow-up only when asked.

Do this filing immediately, in the same turn the finding surfaces — not batched for later, not gated on being asked.

### 5. Toggling off — propose-and-confirm, never silent, always standalone

Full-Picture never turns itself off silently. It only ever turns off when:

- The user gives an explicit off-phrase ("exit Full Picture," "turn off Full Picture," or similarly unambiguous), **or**
- A check-in is proposed and the user confirms it.

**When to propose the check-in:** only when the user's own message is **cleanly and solely** about finalizing a plan or giving a go-ahead to build/execute — not when finalization language is mixed into a message that also contains a question or other content. If finalization wording shows up alongside something else, treat the message as not-yet-finalizing: answer the other content normally and wait for a later, clean, standalone finalization statement before proposing anything.

**How to propose it:** the check-in is its own **separate, standalone message** — never the lead-in to another reply, never appended to the end of one, never bundled with any other content before or after it. It should be the only thing in that message, so it can't be skimmed past. Something like: "Looks like we've landed on a plan — want me to drop Full Picture now, or keep it running through the build too?" Wait for the user's answer before doing anything else.

## What NOT to do

- Don't ask the breadth-checklist questions out loud to the user (e.g. don't literally ask "how many months of data do I need?") — work through them silently as part of normal research judgment, the way a person would without narrating it.
- Don't apply contrarian/full-picture scrutiny to execution of an already-settled plan.
- Don't bundle the toggle-off check-in with any other content.
- Don't fire the toggle-off check-in on finalization language that's mixed into a message with other content.
- Don't save findings to only one location when multiple are relevant.
- Don't silently auto-suspend based on inferred context.
