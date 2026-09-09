# 2026-09-09 Self-Review

## Local subject-aware reframer, Gate 2

- What worked: isolated hash-locked dependencies, explicit offline enforcement,
  source fingerprints, and versioned diagnostics made the approved experiment
  concrete without touching protected videos. Original PTS handling avoided the
  prior Short's audio/video start offset.
- Detection lesson: AI-generated bears can confidently receive dog/cat labels.
  A species-only filter silently discards usable localization. Inspect all-class
  evidence before changing models; keep raw labels while tracking animal groups.
- API lesson: the installed ByteTrack constructor takes a frame-count buffer,
  not the older frame-rate argument. Inspect pinned implementations before
  assuming an API from memory. The mismatch was corrected before full analysis.
- Limits: separate family association prevents person/animal class switching but
  does not establish individual identity. Contact sheets and counts cannot prove
  smooth reframing; normal-speed review and a distinct approved camera-planning
  gate remain necessary.
- Scope discipline: Gate 2 approval covered the named dependencies and diagnostics.
  A successful install, a resume request, or promising detections do not authorize
  camera planning, global pipeline adoption, or publishing.

---

## Resource Library thread (Claude, Sep 8–9) — honest review

**What went wrong:**
1. **The orphan-image "fix" broke 3 pre-existing notes.** Tried to auto-ingest 5 "orphan" images;
   the ingest tool renames + copies, so it created duplicate notes AND when I cleaned up the
   duplicate images I deleted files that older notes depended on. Should have checked what
   referenced each image before touching anything. Recovered, but cost a detour.
2. **Triage over-flagged 108 notes as "hard fails" when only 13 were real.** The `<40 body words`
   stub threshold caught already-enriched-but-terse notes. Fixed by adding an `enriched:` marker
   check — but I presented the inflated number to Tony first and he had to push back.
3. **Auto-fixing the 28 "renamed image" links matched too loosely** — pointed 9 `Job-Boards-N`
   series notes at one image. Caught it in review, reverted, kept only 5 genuine renames.
4. **Truncation:** twice handed Tony a paste that exceeded 50k chars. Added Download buttons
   to the review pages — should have done that from the first tool.

**What worked:**
- The review-page pattern (local HTML, localStorage, Keep/Junk, folder filters, download list)
  scaled from 13 → 108 → 1,044 → 9,135 items cleanly. Reusable.
- Backup-then-move-to-Desktop/Delete (never rm) meant every mistake above was recoverable.
- The co-location brainstorm: naming the root cause (fragile filename links edited by many
  processes) before proposing structure led to a decision Tony agreed with fast.

**Recurring pattern to fix:** I default to comprehensive answers. Tony repeatedly wants the
narrow answer to the narrow question. Verbosity is the #1 friction this session.
