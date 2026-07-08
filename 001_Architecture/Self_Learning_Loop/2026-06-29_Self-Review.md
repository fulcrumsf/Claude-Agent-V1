# Self-Learning Review — 2026-06-29

## What Went Wrong

### Proposed Looping — Major Mistake
I suggested looping 5-second clips to fill slots up to 12 seconds. This is obviously wrong — any viewer can see a looped clip restart. I should have recognized this immediately. The fact that `assemble.py` had looping logic built in does not make looping correct; it was a design flaw in that script. I followed the script's logic instead of thinking about what the output would actually look like.

**Fix going forward:** Before proposing any video technique, think about what the viewer sees. Looping = visible reset = immediately noticeable. Never propose it.

### Didn't Read Existing Files First
I started planning the video assembly (trim/loop operations, file sizes, etc.) without reading what was actually in the production folder. Tony had to say "You're assuming we don't have any of this." The Beatmap.json, Shot_List.md, and narration files were all already there. I was treating the project as if it needed to be built from scratch.

**Fix going forward:** On any production task, start by listing and reading the key production files. Map what exists. Then plan.

### Missed the DURATION Bug in Initial Analysis
When I first read `batch_generate_videos.py`, I saw `DURATION = 5` with the comment "trim in post per beatmap." I also knew the beatmap had `target_final_duration_s` up to 12s. I should have flagged immediately: "this is wrong — the script ignores the beatmap duration and generates everything at 5 seconds, but most clips need more than 5 seconds." Instead I only discovered it later when checking file sizes.

**Fix going forward:** When reading any generation script, cross-check its hardcoded parameters against the data source (beatmap/config) it's supposed to serve.

---

## What Worked

### Padding Rule Solved C13–C16 Cleanly
Tony was worried about held frames or beatmap changes for C13–C16 (5.04s source, 5.5s target). I recognized that the 1s padding rule solves this automatically: generate 7s → trim to 5.5s = real footage. No freeze frame, no beatmap edit, no workaround. Tony accepted this.

### Film Composer Audio Framing
When Tony described how he wanted audio to work — building tension, impact hits, layered stems — I framed it as "how a film composer approaches a score" rather than "background music + SFX." This resonated. Naming the mental model correctly made the direction clearer for both of us.

### Model Selection Logic Was Clean
The `generation_params()` function is self-documenting: ceiling of (target + 1s), min 4s, Seedance 1.5 if ≤12s else 2.0. This logic is correct, simple, and handles all cases including the C8–C12 edge case where the generated duration exceeds Seedance 1.5's limit.

---

## Patterns to Watch

- I tend to work from existing script structure rather than questioning whether the script design is correct. Scripts can have bugs or flawed design decisions. Always validate the script's assumptions against the source of truth.
- Production tasks require checking existing asset state first — always, every session, no exceptions.
- For video output quality questions, think like a viewer first, then think like an engineer.
