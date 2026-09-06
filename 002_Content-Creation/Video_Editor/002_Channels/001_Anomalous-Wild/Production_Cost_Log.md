# Anomalous Wild — Production Cost Log

Running record of real kie.ai API spend per production. Updated whenever a production finishes, or whenever fresh kie.ai usage-export data (`Account > Usage` CSV) is shared for reconciliation. Append new rows — never overwrite prior entries.

## Methodology

- **Credit-to-USD rate:** 1 credit = **$0.005** (confirmed 2026-08-29 by matching kie.ai's own live pricing_cache.json rates against usage-export credit values — e.g. GPT-Image-2 2K image-to-image is $0.05/image and shows as 10 credits; Seedance 1.5 Pro 1080p-with-audio is $0.075/s and shows as 15 credits/second).
- **Two confidence tiers**, always stated per row:
  - **High** — every credit is matched to a specific generated file on disk via timestamp cross-reference (minute-level), so the number is call-by-call reconciled, not just date-bounded.
  - **Lower (window-based)** — cost is bounded by the production's overall file-activity date range in the kie.ai usage CSV, but not verified call-by-call. Can include unrelated dev/test calls or other concurrent work (e.g. a parallel Codex session) that happened to fall in the same window.
- **kie.ai balance check:** `curl -s -H "Authorization: Bearer $KIE_API_KEY" "https://api.kie.ai/api/v1/chat/credit"` returns the current live credit balance (not a spend history — kie.ai's API doesn't expose a usage-history endpoint directly; usage-export CSVs must be pulled from the web dashboard and shared here for reconciliation).
- One shared kie.ai API key covers this entire workspace, not just Anomalous Wild — a usage CSV's grand total will always be larger than the sum of rows in this log; the difference is other channels/productions/Codex work on the same key.

---

## Production Cost History

| Production | Video | Usage-data window checked | Real cost | Confidence | Notes |
|---|---|---|---|---|---|
| 0001 | Bioluminescence Weapon | Jul 30 – Aug 29, 2026 usage CSV | **Not recoverable from available data** | — | Production predates the earliest usage-export data pulled so far (built Apr/Jul 2026); no billing record survives in the Jul 30–Aug 29 CSV. |
| 0002 | Mantis Shrimp Color Vision | Aug 15–24, 2026 (production's full active file-date range) | **~$36.97** (7,393.4 credits, 152 calls) | Lower — window-based | Not built in a session with direct file-by-file tracking; bounded by date range only. Could be tightened later by isolating activity bursts the way 0003 was, if worth the effort. |
| 0003 | Glass Frog Transparency | Aug 26–29, 2026 (minute-level reconciliation against real generated files) | **$9.65** (1,930 credits, 70 calls) | High — call-by-call reconciled | Includes $0.45 of wasted spend from one killed/re-submitted Seedance clip (a subagent scope-overrun caught mid-run) — see `Productions/0003_Glass_Frog_Transparency/RESUME_NOTES.md` for the full incident. |

**Running total across all 3 productions:** **~$46.62** (excluding 0001's unrecoverable figure)

---

## Reference — full usage-CSV grand total for context

The Jul 30 – Aug 29, 2026 usage-export CSV's grand total across the entire kie.ai key (all channels, all work, including non-Anomalous-Wild activity and any concurrent Codex sessions) was **19,336.4 credits ≈ $96.68**. Only ~$46.62 of that (about 48%) is attributable to the three Anomalous Wild productions above — the rest is other work sharing the same API key.

---

## How to update this log

1. Pull a fresh usage-export CSV from the kie.ai dashboard (Account > Usage), covering the period since the last update.
2. Identify the production(s) that generated new content in that period.
3. Cross-reference real file timestamps in that production's folder (`Video_Clips/`, `Images/`, `Assembly/`) against the CSV's `Create Time` column to build minute-level windows — same method used for 0003 above. Higher effort, higher confidence.
4. If file-by-file reconciliation isn't practical, fall back to a date-range window bound and mark the row "Lower — window-based."
5. Add a new row to the table above. Never edit or delete a prior row — if a number needs correcting, add a note explaining the correction rather than silently changing history.
