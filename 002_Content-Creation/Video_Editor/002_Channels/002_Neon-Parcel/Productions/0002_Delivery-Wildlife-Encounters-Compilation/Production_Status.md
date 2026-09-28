# Production Status — 0002 Delivery Wildlife Encounters Compilation

## ⚠️ Known issue to fix before building more shots (flagged 2026-09-27)

**The scale checker can pass a storyboard it never actually measured.** `check_storyboard_scale.py` checks that things in a storyboard are believable sizes — e.g. a delivery van doesn't grow between panels, an animal isn't way too big or small next to something you can judge its size by. Right now, if the checker can't find a reference object to measure against, or can't find a required animal/object in a panel, it just prints a warning and still marks the storyboard as PASSED. This is exactly how Shot 07 got approved for paid video generation with a parked van that grew ~55% and a van/fishmonger that looked 40–100% oversized next to the harbor — the checker had no way to catch it because "couldn't check this" wasn't treated as a problem.

**The fix:** make those "couldn't check" cases actually block approval instead of silently passing, and write the scale spec (what's real-size, what to measure against) before the storyboard image is generated, not after.

A first attempt at this was drafted by an unreviewed Codex session on 2026-09-27 (touched `check_storyboard_scale.py`, `pipeline.yaml`, `SKILL.md` in `Neon_Parcel_Longform_Compilation_v2`) but was reverted — it wasn't authorized to run yet and had no tests. Before building Shots 08–15, either redo this properly (with tests proving the new blocking logic actually catches a bad case) or at least manually double-check scale on each new storyboard, since the current checker can still wave through an unmeasured one.

---

## Runtime target: over 3:00 (logged 2026-09-27)

**Decision:** 8 more shots needed. That clears 3:00 even if both weak shots (01, 04) are cut.

### Current shots (best take per shot, raw clip length via ffprobe)

Paths below are relative to each shot's folder, which lives in `Production/Shot-NN-Name/` since the 2026-09-27 re-scaffold. Build Shots 08–15 with `scaffold_new_production.py <this production> --shot Shot-NN-Name`.

| Shot | Best take | Length | Grade |
|---|---|---|---|
| 01 Movers + Fox (UK) | `Video_Clips/Shot-02-Seedance-2-Mini-480p-v1.mp4` | 10.1s | Ungraded (480p test only) |
| 02 Kangaroo Doorbell (AU) | `Data/Seedance_v1_Full_Action_Test.mp4` | 14.1s | A |
| 03 Moose Dashcam (CA) | `Data/Seedance_Mini_v1_Full_Action_Test.mp4` | 14.1s | C (passes) |
| 04 Tanuki Camcorder (JP) | `Data/Seedance_Mini_v1_Full_Action_Test.mp4` | 14.1s | C (narratively flat) |
| 05 Vervet Monkey Shopfront (KE) | `Data/Seedance_Mini_v7_1080p_FINAL.mp4` | 14.1s | B+ |
| 06 Capybara Motoboy Gate (BR) | `Video_Clips/Shot-06-1080p-v1.mp4` | 14.1s | B+ (final) |
| 07 Walrus Fishmonger Truck (GB) | `Data/Shot07_Full_v2_1080p_FINAL.mp4` | 23.1s | B+ (final, extended) |
| **Total** | | **1:43.6** | |

### Math (new shots at ~14s each)

| Scenario | New shots | Projected runtime |
|---|---|---|
| Keep all 7 | 7 | ~3:22 |
| Drop Shot 01 | 7 | ~3:12 |
| Drop Shots 01 + 04 | 7 | ~2:57 (short) |
| Drop Shots 01 + 04 | **8** | **~3:11** |

Extended shots (~23s, like Shot 07) reduce the count needed. Raw lengths only: trims, title cards and the end card in the final cut will change the total.

### Next
- Build Shots 08–15 (8 new Diversity Matrix cells).
- Writing quality: the Storytelling-Library master skill is designed but on hold (waiting on Tony's Jev router plan). The comedy step is currently just the matrix's one-line "comedic hook" cell. Shots 04 and 06 were marked down on storyline, not execution.
