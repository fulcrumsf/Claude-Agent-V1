# Session Handoff, 2026-11-16, Ikigai template-fix rollout (approvals pending)

Read this first. Follows the 2026-11-15 PhotoCraft/Edit-with-chat handoff (that work is done, pushed and verified by Tony).

## What's next for Tony
1. **Approve or deny the 4 new templates** in Portal (http://127.0.0.1:8800, hard-refresh Cmd+Shift+R) > Templates > tick "New to approve":
   - LVRM_Japandi_Simple_ISO
   - LVRM_Modern_BLue_ISO
   - 001_Walnut_LVRM_ISO
   - LVRM_Modern_Leather_4x5 (photo still has the old print; frame-edge shadows only)
   Approve moves the old PSD/json/preview to the folder's Archive; Deny moves the new files to Archive.
2. **Duplicates confusion (open question, not investigated).** Tony sees duplicate template cards, one PASS and one FAIL. Likely explanation (UNVERIFIED): the old template (still FAIL) and the pending "Rebuild" version (PASS) both show until approved, and rebuilt files sit beside the old ones as `<name>_Rebuild_2026-11-16.psd/.json/_Scene.png`. Next agent: open the Templates tab, list the duplicate pairs, and confirm whether each is (a) old + pending rebuild, (b) a template + a leftover in Archive, or (c) a real duplicate. If (a), make the card say clearly "replaces X" and hide the old FAIL card while a rebuild is pending, or group the pair. Check `template_gallery.py`.

## State
- Portal restarted on 8800 with all rollout code (178 tests pass). Pending/unapproved templates are never used by Production or the + template picker.
- Credits: 54 spent on regenerated scenes (kie.ai balance about 485.7).
- Rollout code committed in this session's commit (Portal app + tests, `Scripts/template_rebuild.py` etc., spec docs).

## What the rollout did
- Opening pad 0.5 px; SAM edge rule 1 px to 3 px; sun-line guard; placement check for wall molding; wainscoting rule in scene prompt (waist-and-below, or larger panels with art centered; optional, best in elegant rooms).
- Approve/Deny moves files to the folder Archive (nothing deleted).
- 4 rebuilds built (above). 23 builder refusals: SAM found no clean opening on 21 (no files written), plus Victorian_Floor and Wabi_ISO (frame/ratio mismatch).
- 3 wainscoting rooms regenerated without wainscoting (LVRM_Trendy_Girl_5x7, LVRM_Trendy_Girl_4x5, 003_BC_White_Bar_Cart): scenes saved in each template's `Archive/` as `Regenerated_Scene_No_Wainscoting_2026-11-15.png`, but none built (two drew same-color mat/floating paper, bar cart came out as two photos side by side).
- Mat build is written but untested end to end (10 templates have mats).
- BDRM_Japandi_Beige_4x5 rebuilt, failed checker, archived. It looked fine by eye, so the checker may be a false alarm.

## Decisions waiting on Tony
1. Wainscoting rooms: regenerate with "no mat, single photo, no floating paper" (about 54 credits, needs his OK) OR allow SAM's paper edge as the opening when mat and paper match (code change).
2. The 21 SAM refusals: fix by hand in PhotoCraft, regenerate scenes, or retire.
3. Mats (10 templates): by hand or new scenes.

## Lower-priority carryovers
Art-frame protection via SAM, blur at top of new objects on local engines, Ikigai items from 2026-11-12 handoff, slot-3 template (Tony fixed by hand; checker passed it anyway, so checker is not the final judge).

## Read first
`005_Ecommerce/Etsy-Ikigai/Mockup_Docs/Template_Layer_Rules_And_Checker_Spec.md` (sections "Decisions applied 2026-11-15", "Rollout 2026-11-16"); memory `feedback_wainscoting_scene_rule_2026-11-15.md`.
