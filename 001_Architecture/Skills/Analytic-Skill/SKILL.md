---
name: Analytic-Skill
description: General-purpose method for doing analytics and opportunity research on ANY topic (market/niche research, SEO, revenue streams, content or product strategy, audience/retention analysis, story and character-arc analysis, competitor analysis). Invoke when Tony asks to analyze, research, rank, score, prioritize, find opportunities or outliers, or build an analytics dashboard/artifact. Domain-agnostic. It sets HOW to think and what proof counts; pair it with Full-Picture (breadth), Tool-Manager (which tools exist) and artifact-design (visual output).
---

# Analytic-Skill

Designed with Tony, 2026-10-20, from the Revenue Priority Board work. It is a method, not a tool list. It works for Etsy niches, SEO keywords, TikTok products, story arcs, audience retention, anything that has data. Load it whenever the task is "find out what is true / what to prioritize," and compose it with other skills (Full-Picture, Tool-Manager, artifact-design, domain skills).

## The standard it holds you to
Tony judged earlier analytics as "basic": generic searches, prose walls, scores from opinion, his own examples copied back. This method exists so output is evidence-first, structured, and surprising in a useful way.

## Principles (apply to every domain)

1. **Real evidence only, sourced and dated.** A claim is a number or observed fact plus source plus date. Opinions, blog posts, forum sentiment and "someone said they like it" are never proof. Always record: what the number is (absolute estimate, relative index, count, rate), where it came from, when it was pulled. If a domain has no numbers (story, arcs), the evidence is observed structure from proven comparables (what works in works that demonstrably succeeded), not taste.
2. **Distrust any single source.** Different tools disagree, sometimes by 100x. Cross-check at least two sources. Use a volatile estimate for ranking only, and rank on the sturdier proof (actual sales, actual completions, actual counts, official statistics). State which is which.
3. **The user's examples are seeds, not checklists.** Never just verify or repeat what the user named. Treat every example as a starting point: expand it breadth-first, then let the data surface outliers. Show where the user's own ideas landed, even if low.
4. **Go broad, then narrow (funnel).** Category level first, then a long list (50+ candidates when the domain allows), score everything the same way, then narrow to top outliers. Skipping the long list is how you only find what you already expected.
5. **Hunt outliers, not averages.** Look for anomalies: high demand with weak incumbents, fast growth with no dominant player, small supply with proven sales, an underserved audience, a format that converts. Define the anomaly in numbers.
6. **Proof means someone is already winning.** Demand alone is not proof. Find real comparables (competitors, creators, works, pages) that succeed, measure how concentrated the winning is, and compare field by field against the thing being judged.
7. **Check the user's own data first, with the full history.** Own orders, analytics, reviews, search terms, retention. Never base a baseline on one short window that may hold an outlier. Follow every number down to what it is made of (aggregate to parts to the real thing) until another question reveals nothing new.
8. **Screen against the user's actual model before ranking.** Learn the constraints (stores, tools, capacity, brand, audience, what they will not build). Remove or quarantine what does not fit (show it in a small collapsed "excluded" box) instead of ranking it.
9. **Score potential, show effort separately.** Past neglect must not depress the score of something with real potential. Project the outcome at a stated consistent cadence; show effort-to-date as its own informational column. Rank on ceiling and speed together; deadlines are often soft.
10. **Score each stage separately, then combine.** Break the thing into stages (for a product: ideation, production, automation, listing, promotion, ads, startup time, startup cost, competition, likelihood; for other domains choose the real stages), score each 0-10 from cited data, then weight into a final. Keep a short contrarian note per item: the strongest reason it fails.
11. **Granular beats generic.** Narrow by the real dimensions of the domain (audience, color, motif, place, format, intent modifier, season, stage). "Family reunion shirts" is generic; a specific place or experience with a visual identity is granular.
12. **Plan first, then run.** Before a big research pass, show the user the planned queries/sources (about five representative searches) and let them judge. Do not start the pass until approved.

## Workflow
1. **Read context first:** memory, project docs, prior artifacts and raw data, TOOLBOX.md and API_Directory.md (what connectors exist: Composio, OpenRouter, Perplexity, Firecrawl, Alura, Pinterest Trends, Google Trends, Kalodata, GA4, Xero, YouTube API, etc.). Never re-pull what is already on file.
2. **Define the question and the money/success metric** in the user's terms, plus constraints from principle 8.
3. **Show the research plan** (principle 12) and wait for judgment.
4. **Seed, expand, long-list** (principles 3-5). Save every raw number to a data file with tool, query, timestamp.
5. **Pull proof and own data** (principles 6-7).
6. **Score, then sanity-check the top results against a real proven comparable** (principle 6, 10).
7. **Build the output** (below). Verify it renders and every number has a source tag.
8. **Save findings** to memory and the relevant plan/doc in the same pass; log tool findings in TOOLBOX.md.

## Output standard
- Visual and minimal words: leaderboard with bars, scoring heatmap, demand-vs-competition scatter (bubble = growth), trend sparklines, proof bars, cost/time bars, and a data-freshness panel. No paragraphs of "why": each why is a chart or a one-line data note (number, unit, source, date).
- Any data that is not live carries a visible amber "last updated" badge plus its refresh path.
- Footer: assumptions, data gaps, method, in minimal form. Tool gaps list exactly what login or permission each needs.
- Publish with the artifact skills (artifact-design first); update the same artifact URL when revising.

## Domain adapters (examples, not a closed list)
- **Etsy/e-commerce niches:** search volume (Alura, eRank, EverBee), Pinterest Trends, Google Trends, listing counts, top-listing lifetime sales, own shop history.
- **SEO:** query volume and trend, SERP difficulty and who ranks, content gap vs top pages, click-through and conversion of own pages.
- **Video/social:** retention and traffic-source data, search-driven vs recommended views, creator benchmarks in the category, winning-format comparison.
- **Story and character arcs:** structure of proven works in the target genre (beats, turning points, stakes ladder), audience response data (retention curves, comments by timestamp, ratings by chapter), contrast against the user's draft field by field. Evidence is observed structure plus audience data, never taste.
- **Code/product decisions:** real usage, error and performance data, comparable open-source or market products.

## Anti-patterns
- Ranking from LLM opinion; scoring before pulling data.
- Copying the user's examples back as the candidate list.
- One-month baselines; one-tool numbers; relative indexes presented as absolute volumes.
- Paragraph explanations instead of a visual with a data note.
- Re-raising items the user already settled or excluded (check memory for stop-mentioning lists).
- Starting a large pull without showing the plan.
- Saving findings to only one place.

## Composes with
Full-Picture (breadth and follow-the-trail), Tool-Manager (which tool to use), artifact-design and artifact-capabilities (the dashboard), openrouter-jev-calls (cheap bulk clustering, never as a source of facts), plus any domain skill.
