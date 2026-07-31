---
title: "TikTok_V1 Vision Scan — FLAG Resolution"
type: compliance-resolution
created: 2026-07-31
---

# Resolution: FLAG on frames 0.50s and 34.27s (product box branding)

**Scan verdict:** FLAG — "QIFOR GLASS GUARD" brand name/logo visible on product box.

**Resolution: False positive. Verdict downgraded to CLEAR by manual review.**

**Reasoning:**
- RULE-001 (Compliance-Ledger.md) prohibits *unrelated third-party* trademarks —
  competitor products, background signage, platform watermarks — used without
  permission.
- RULE-002 explicitly *requires* the product shown in content to match the listed
  product on TikTok Shop, including its logo/graphics/packaging.
- This video is the Neon Parcel affiliate listing for QIFOR Glass Guard itself.
  Showing the product's own box and branding is the entire premise of an
  affiliate demo video — it is not a foreign trademark, it's the product being
  sold via this creator's own TikTok Shop link.

**Known tool gap:** `compliance_vision_scan.py`'s prompt asks the model to flag
"any third-party brand name, logo, trademark" without excluding the promoted
product's own brand. This will false-positive on every TikTok Shop affiliate
video that shows product packaging (i.e. nearly all of them). Worth tightening
the prompt in a future pass to explicitly exclude the product being promoted in
this specific listing — flagged here rather than silently patched, since Tony
should decide whether/how to adjust the shared script.

**Frame at 8.70s and 28.57s:** no issue (hand/tool, ceiling — no branding).

**Transcript scan:** CLEAR (see Transcript-Scan/TikTok_V1-transcript-scan.md).

**Final gate status:** CLEAR to package, pending Tony's sign-off on this
resolution.
