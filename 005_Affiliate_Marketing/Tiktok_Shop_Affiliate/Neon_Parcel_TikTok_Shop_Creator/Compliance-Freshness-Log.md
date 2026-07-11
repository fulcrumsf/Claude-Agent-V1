---
title: "TikTok Shop Compliance Freshness Log"
type: compliance-log
created: 2026-07-11
---

# TikTok Shop Compliance Freshness Log

Tracks every Phase 2 live-freshness check run against `Compliance-Sources.json`.
`check_tos_freshness.py` appends one dated section per run. A gap of more
than 14 days since the last entry (or an always-escalate category) triggers
the next run automatically.
