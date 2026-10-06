---
title: "Shot-02 Kangaroo Doorbell (AU): Iteration Notes"
type: report
domain: video-production
tags: [report, neon-parcel, video-production, iteration-notes]
---

# Shot-02 Kangaroo Doorbell (AU): Iteration Notes

Tony's own words, pinned to the exact image and prompt he was reacting to, one
section per step and attempt. This is Layer 2 of the Quality_Ledger design: the
ledger keeps the grade and the numbers, this file keeps the words.

**How this was made (2026-10-04).** Every "Tony said" block and every inline prompt
was copied by script, unchanged, from the Claude Code session transcript
`~/.claude/projects/-Users-tonymacbook2025-Documents-Agent-OS/5b2d0e37-cd75-48b5-905a-b018d3c2714f.jsonl`
(2026-09-19 to 2026-09-20 UTC). That transcript is auto-deleted around
2026-10-19, so this file is the surviving copy. Nothing is reworded, typos
included. Line numbers point into that transcript.

**Notes for reading.**
- In that session this shot was called "Test Shot 03" and lived at
  `Productions/Test_Shot_03_Kangaroo_Doorbell_AU/` until the 2026-09-27 move. All
  paths below are relative to this shot folder.
- "Shown" is what Tony was looking at: a file sent to him, or an image the agent
  opened in the session. "(overwritten)" means that file now holds a later version.
- Prompts that were only typed inline into a generation command (never saved to a
  file) are kept verbatim in the collapsed boxes.
- Tony pasted 9 images in this session. His edited POV was already saved as
  `Character_Sheets/POV_Panel_Final_Tony_Edit.png`. The other 8 were decoded from
  the transcript on 2026-10-04, byte for byte in their original format, and saved
  next to this file: `Session_Example_Environment_Sheet_1.webp` and `_2.png`
  (environment attempt 2), `Session_Reference_House_1` to `_4.webp` (environment
  attempt 5), `Session_Markup_Panel_1` and `_2.webp` (environment attempt 8).
- Times are UTC.

## character_sheet.delivery_driver, attempt 1

**Shown:** `Character_Sheets/Delivery_Driver_Character_Sheet.png`, first version, sent 2026-09-19 00:44 UTC (overwritten twice since; only the final version survives). One panel showed the courier on a bicycle in a dense city.

**Prompt sent:** Inline in the Character-Sheet-Generation call (below).

> [!note]- Description passed to character_sheet_generation.py (the script wraps it in its sheet template): 2026-09-19 00:43 UTC, transcript line 4287, typed inline, never saved to a file; kept here verbatim
> A food-delivery courier in their mid-to-late 20s, average build, wearing a casual insulated delivery backpack with a plain unbranded strap (no real company logo), a plain zip jacket, jeans, and sneakers, short practical haircut. Regional Australian casual streetwear, plain and unbranded.
>
> --role: the delivery driver in Test Shot 03

**Tony said:**

> [!quote] Tony, 2026-09-19 00:47 UTC (transcript line 4337)
> Okay, the one problem I have with this is: how likely is the delivery guy going to be riding a bike if he's out in the middle of a rural outback area? But my other question is: why did the plausibility study not pick that out? What's wrong here? Don't guess, really dissect the problem, and don't just try harder. Figure out what's wrong.
>
> The plausibility should be reading the script, right, or it should be reading the prompt that's going to be generated for the video, right? It needs to understand that "rural" would mean that it's not a dense area, so likely the delivery person would be in a car, most likely not a bicycle, because it's not a city-dense area. The Kangaroo  character sheet look fine.

**Changed next:** Agent traced the miss to the Plausibility research checking only whether the service exists, not which transport fits a low-density area; added a logistics/vehicle-mode rule to `Neon_Parcel_Longform_Compilation_v2/SKILL.md`, fixed `Research/Plausibility_Facts.md` and `Blocking_Plan.md`, and regenerated with "drives a car, not a bike" pinned.

**Worked?:** Partly. Attempt 2 showed a parked car and no bike, but kept the courier backpack, which Tony caught next.

## character_sheet.delivery_driver, attempt 2

**Shown:** `Character_Sheets/Delivery_Driver_Character_Sheet.png`, second version, sent 00:50 UTC (overwritten). Tony's comment came after he had also seen storyboard v1, which used this sheet, so it covers both.

**Prompt sent:** Inline in the Character-Sheet-Generation call (below).

> [!note]- Description passed to character_sheet_generation.py (the script wraps it in its sheet template): 2026-09-19 00:49 UTC, transcript line 4383, typed inline, never saved to a file; kept here verbatim
> A food-delivery courier in their mid-to-late 20s, average build, wearing a casual insulated delivery backpack with a plain unbranded strap (no real company logo), a plain zip jacket, jeans, and sneakers, short practical haircut. Regional Australian casual streetwear, plain and unbranded. This courier drives a car (not a bike or motorbike) between deliveries -- a low-density, spread-out bushland-fringe regional setting, not a dense city. Any full-body/environment panel must show a plain parked car and a quiet suburban-fringe street/driveway with houses spaced apart and bushland nearby -- never a bicycle, never a dense urban streetscape.
>
> --role: the delivery driver in Test Shot 03 -- arrives by car, not bike

**Tony said:**

> [!quote] Tony, 2026-09-19 01:59 UTC (transcript line 4902)
> After. Two things. So, really, I probably should have checked the character sheet again, but he wouldn't have that bag if he's a driver, right? I know we didn't do a new character sheet based off of the new plausibility study, but that's one thing I want to note.
>
> The other thing I want to note is his car is not present in the driveway. Why don't we rerun the character sheet for him, but base it off of the plausibility study and see what the output is? You need to have some sort of check in your storyboard that uses all the elements that are noted in the matrix. Really, it should come after the matrix, right? It should come from the plausibility study.

**Changed next:** Agent added the mandatory Grounding Coverage Check to the v2 pipeline skill (every audit fact must be in each generation prompt or excluded with a reason, logged in `Data/Grounding_Coverage_Check.md`) and regenerated the sheet: local takeaway driver, hand-carried insulated bag, no backpack, parked car shown.

**Worked?:** Yes. Attempt 3 was approved and used in the A-grade final video.

## character_sheet.delivery_driver, attempt 3

**Shown:** `Character_Sheets/Delivery_Driver_Character_Sheet.png` (the current file), sent 02:02 UTC.

**Prompt sent:** Inline in the Character-Sheet-Generation call (below).

> [!note]- Description passed to character_sheet_generation.py (the script wraps it in its sheet template): 2026-09-19 02:00 UTC, transcript line 4974, typed inline, never saved to a file; kept here verbatim
> A food-delivery driver in their mid-to-late 20s, average build, working for a small local takeaway shop (NOT a gig-app aggregator courier) -- this driver drives a car between deliveries and hand-carries the order to the door. He is NOT wearing any hands-free courier backpack or delivery bag strapped to his back -- that look belongs to a foot/bike courier, not a driver. Instead he carries the order directly in his hands: a plain unbranded insulated delivery bag held by its handle, or a stack of plain foil/plastic takeaway containers. Plain zip jacket, jeans, sneakers, short practical haircut, generic unbranded regional Australian casual streetwear appropriate to 2019. Any full-body/environment panel must show him standing beside his parked car -- an ordinary older-model sedan or hatchback, not rideshare-branded, not new or luxury -- on a quiet bushland-fringe regional street with houses spaced apart, never a bicycle, never a dense urban streetscape.
>
> --role: the delivery driver in Test Shot 03 -- local takeaway driver, carries order by hand, no backpack

**Tony said:**

> [!quote] Tony, 2026-09-19 02:02 UTC (transcript line 5007)
> Proceed with both

(Reply to the agent asking whether to proceed with the environment plate and storyboard regeneration or look first.)

**Changed next:** Nothing; kept as is.

**Worked?:** Yes, final. `Data/Session_Handoff_2026-09-19.md` lists it as "already corrected and approved"; it was `@Image2` in `Data/Seedance_v1_Full_Action_Test.mp4` (Grade A, `Data/Generation_Log.json`).

## character_sheet.kangaroo, attempt 1

**Shown:** `Character_Sheets/Kangaroo_Character_Sheet.png`, sent 00:44 UTC.

**Prompt sent:** Inline in the Character-Sheet-Generation call (below).

> [!note]- Description passed to character_sheet_generation.py (the script wraps it in its sheet template): 2026-09-19 00:43 UTC, transcript line 4290, typed inline, never saved to a file; kept here verbatim
> A single adult grey kangaroo (Macropus giganteus), realistic wild-animal proportions and coloration -- grey-brown fur, powerful hind legs, thick muscular tail used for balance and as a fifth limb when stationary, small forelimbs held close to the chest, long pointed ears that rotate independently, dark eyes. Wild, alert, natural bushland-adjacent animal, not tame or domesticated-looking.
>
> --role: the kangaroo in Test Shot 03
> --anatomy_notes: One thick tail used as a balance prop and fifth limb when upright and stationary. Two small forelimbs (paws) held close to the chest, not used for locomotion. Two large powerful hind legs and feet used for hopping. Two independently-rotating ears. Adult standing height: roughly chest-to-shoulder height on an average adult human -- much larger than a dog, shorter than a person.

**Tony said:**

> [!quote] Tony, 2026-09-19 00:47 UTC (transcript line 4337, one sentence from a longer message)
> The Kangaroo  character sheet look fine.

**Changed next:** Nothing; never redone.

**Worked?:** Yes, final. `@Image3` in the A-grade final video.

## environment, attempt 1

**Shown:** `Character_Sheets/Environment_Plate_1.png`, first version, sent 00:44 UTC (overwritten at 02:04 UTC). No car in frame.

**Prompt sent:** `Data/Environment_Location.json`, first version (overwritten at 02:03 UTC), fed to `environment_sheet_generation.py`. Its text is preserved below.

> [!note]- Environment_Location.json, first version: 2026-09-19 00:43 UTC, transcript line 4276, saved then, overwritten since; kept here verbatim
> {
>   "location": "Suburban Australian front porch, fixed wide-angle doorbell-camera frame, bushland-fringe regional town, midday",
>   "scenes": [
>     {
>       "scene": 1,
>       "description": "Wide-angle fisheye frame from door height, looking down and out over the porch. A doormat sits centered in the lower-frame foreground, directly below camera. Porch steps lead down from the mat toward screen-left, ending at a driveway/street edge just visible at the frame's left edge. A low garden bed/hedge line borders an open lawn on screen-right. The open lawn occupies the mid-frame background between the steps and the hedge line. A single letterbox sits near the screen-right edge of the lawn as a fixed scale reference. Midday sun, regional Australian suburban house exterior, bushland visible in the distant background beyond the hedge. No people, no animals, no vehicles in this plate -- an empty establishing view of the fixed frame only."
>     }
>   ]
> }

**Tony said:**

> [!quote] Tony, 2026-09-19 01:59 UTC (transcript line 4902, one sentence from a longer message)
> The other thing I want to note is his car is not present in the driveway.

(Tony said this about storyboard v1, which used this plate; he made no direct comment on the plate itself.)

**Changed next:** Blocking Plan changed so the parked car is visible at the frame edge; `Environment_Location.json` rewritten (car, Hills Hoist, water tank, house type, clear dry weather, no dog); plate regenerated.

**Worked?:** Partly. The car appeared, but the step/patio layout was wrong, which Tony caught at attempt 2 after six storyboards had been built on it.

## environment, attempt 2

**Shown:** `Character_Sheets/Environment_Plate_1.png` (the current file), sent 02:04 UTC and re-sent 03:49 UTC when Tony asked to see the environment sheet. This plate was the reference for storyboards v2 to v6. With his reply Tony pasted two example environment sheets of the kind he wanted: [Session_Example_Environment_Sheet_1.webp](Session_Example_Environment_Sheet_1.webp) and [Session_Example_Environment_Sheet_2.png](Session_Example_Environment_Sheet_2.png).

**Prompt sent:** `Data/Environment_Location.json` (the current file).

**Tony said:**

> [!quote] Tony, 2026-09-19 04:00 UTC (transcript line 6390)
> Okay, there are two things I've noticed with this environment photo:
>
> 1. It's just from the perspective of the Ring doorbell, which is fine. I don't have a complaint about that.
> 2. I do wonder if we want more than just this and this as a label, because I feel like if we have multiple images and we label what that image is in a clear way, that would be better.
> 3. The other thing I would like to mention is that this layout for the steps and the patio really does not make sense if you just look at it logically. The doormat is really where the step should come up more centered to the door, or at least in a way that just looks weird. The handrail looks weird, and it doesn't look like it would be in place. 
> 4. I feel like there should almost be a top-down view from a wide establishing shot showing:
>    * the front of the house
>    * where the Ring camera would be, which would be next to the door
>    * where the stairs would be
>    * where the car would be
>  All in relation, kind of like an opposite of this shot, just to see if it gives the model more context.
> 5. These are just examples, but a real environment sheet should explain the environment like a blueprint, right? You should be able to walk through it in your brain. Each image should be explained, like, "This image is from the Ring's camera point of view," etc. It just needs to be more fully encompassing.
>
> *[Tony pasted 2 image(s) with this message, saved from the transcript as [Session_Example_Environment_Sheet_1.webp](Session_Example_Environment_Sheet_1.webp), [Session_Example_Environment_Sheet_2.png](Session_Example_Environment_Sheet_2.png).]*

> [!quote] Tony, 2026-09-19 04:08 UTC (transcript line 6404)
> Yeah, I agree with creating almost like a blueprint schematic rather than the photorealistic rendering. Save that for the POV shot, and then maybe do a wide of the opposite, but add certain notations:
>
> * Add a notation: "This is a reverse shot of the doorbell for spatial reference only."
> * With the blocking, there should be something that checks where the steps and stairs go. This is just not architected very well for very many reasons. It's not architected very well, even in a real-life situation. Nobody would ever put the steps there. They're offset from the main door. That makes no sense. Not to say that there are never offsets on stairs, but the way that it's done in this visual doesn't make sense. It also makes it harder for the actor to do his job because he's stepping on the steps and going a very weird route to then get to the doormat where he's going to place the food. Even for a real hummock, it would be awkward to do that. That's the other thing that is working against us.
>
>  Think about it this way, and I'm just using an analogy.
>
> When someone builds a house, they wouldn't build a house with a front patio and then the steps all the way to the right on one side of the patio, and then, on the left, have this little mini half-patio floor. The patio goes up another level, right? That's already wrong, right? When you generated this frame, being that it generated it in FishEye first, maybe it screwed up that logic, right? That's the first thing. 
>
> I'm not sure if you can create an environment sheet all at once or if you need to create the first asset in the environment sheet and so forth to keep it consistent. I would try creating it all at once if you can. 
>
> But let's lock in what I was saying, right? What we'll do is I'll have you generate another environment sheet, and then I'll look at it and either iterate upon it or approve it.

**Changed next:** Agent generated a two-panel sheet in one call: a photoreal POV with a single centered staircase, plus a labeled schematic reverse view carrying Tony's exact notation.

**Worked?:** Partly. Tony: "Okay, this is better." but he rejected the two-panel layout (attempt 3).

## environment, attempt 3

**Shown:** `Character_Sheets/Environment_Plate_2.png`, sent 04:11 UTC.

**Prompt sent:** Inline (below).

> [!note]- Prompt sent: 2026-09-19 04:09 UTC, transcript line 6432, typed inline, never saved to a file; kept here verbatim
> Create a two-panel architectural environment reference sheet for the same regional-Australian house exterior, both panels depicting the exact same physical structure and geometrically consistent with each other. No people, no animals, no held objects, no hands/arms in either panel -- pure empty-location references. Each panel has its own clearly readable label in a blank margin strip beneath it, never overlapping the image content.
>
> PANEL 1 -- label reads exactly: "RING DOORBELL POV -- photorealistic camera reference"
> Photorealistic, full color, wide-angle fisheye lens distortion matching a mainstream 2018/2019-era Ring-style doorbell camera mounted at door height, looking down and out over the porch. Doormat centered in the lower-frame foreground directly below the camera. A SINGLE, DIRECT, CENTERED STAIRCASE runs straight from ground level up to the porch landing immediately in front of the door -- the same axis as the door and doormat. Do NOT offset the staircase to one side. Do NOT add a second, mismatched, separate half-level patio strip beside it -- that is a real construction-logic error, not a stylistic choice. The staircase handrail is structurally attached to and runs directly alongside that single staircase. Steps lead down to a driveway visible at the screen-left edge of frame, with an ordinary older-model sedan/hatchback parked there. Single-story brick-veneer or weatherboard house with a corrugated-iron roof. A low garden bed/hedge line borders an open lawn on screen-right, native/bushland-style plantings. A letterbox near the screen-right edge of the lawn. A Hills Hoist rotary clothesline and a rainwater tank visible as yard set dressing. Clear, dry, midday sun, hard shadows. Bushland visible in the distant background.
>
> PANEL 2 -- label reads exactly: "REVERSE ESTABLISHING VIEW -- spatial reference only, not the camera's actual output"
> Also bake this exact sentence as a second line of text directly on this panel, inside the image area near the top, in a small clear caption strip: "This is a reverse shot of the doorbell for spatial reference only."
> A wide-angle SCHEMATIC ARCHITECTURAL BLUEPRINT/DIAGRAM style rendering -- NOT photorealistic, clean line-art/technical-illustration style with labeled callouts -- taken from the OPPOSITE vantage point: standing out at the driveway, looking back toward the house and front door. Show, each with a small text label and a leader line: the front door itself (labeled "FRONT DOOR"), the Ring doorbell camera's mount position directly beside the door (labeled "RING CAMERA"), the single centered staircase running straight from the door down to ground level with no offset (labeled "STAIRCASE"), the driveway (labeled "DRIVEWAY"), and the parked car (labeled "CAR") -- all drawn in correct, consistent spatial relation to each other and to Panel 1's geometry. This panel exists purely to let a human or another model visually verify the spatial layout is architecturally sound, not to be used as a lighting/style reference.
>
> Both panels must be checkable against each other: the staircase position, door position, and driveway/car position must match exactly between Panel 1's photoreal view and Panel 2's schematic view. No watermark beyond the stated labels.

**Tony said:**

> [!quote] Tony, 2026-09-19 04:14 UTC (transcript line 6475)
> Okay, this is better. Now, the photorealistic camera reference always needs to be in the ratio that we're going to create the video in: 16:9. Make that a rule.
>
> The other rule: I hate this two-frame thing that you're doing. The environment sheet should be consistent with the other sheets. It should be in landscape mode, and there should be at least four different... whatever. You could do another top-down diagram. You can add more notation or notes that help explain the spatial awareness. Things like that: you can mark the mailbox, where the clothes hanger thing is, and where the front lawn is. It just needs to look better than this. 
>
> So why don't you lock in what notes I made, make a better environmental plate (however many version numbers you're on), and then pause? I want to look at it and then pause.

**Changed next:** Locked "photoreal camera panel is always 16:9" and "full sheet is 4+ panels, landscape" into `Environment-Sheet-Generation/SKILL.md`; then generated the panels one at a time, chained, starting with the photoreal POV.

**Worked?:** No. Starting from the photo gave a 10+ step staircase on a single-story house (attempt 4).

## environment, attempt 4

**Shown:** `Data/Env_Panel_1_POV.png` (photoreal POV, generated first), then `Data/Env_Panel_2_TopDown.png` (chained from it). `Data/Env_Panel_3_Reverse.png` finished after Tony said stop and was never reviewed. Shown in-session as the agent opened each one.

**Prompt sent:** Inline, one per panel (below).

> [!note]- Prompt sent, Env_Panel_1_POV: 2026-09-19 04:16 UTC, transcript line 6511, typed inline, never saved to a file; kept here verbatim
> Photorealistic doorbell-camera reference image, full color, wide-angle fisheye lens distortion matching a mainstream 2018/2019-era Ring-style doorbell camera mounted at door height, looking down and out over the porch. No people, no hands, no arms, no animals, no held objects. Doormat centered in the lower-frame foreground directly below the camera. A SINGLE, DIRECT, CENTERED STAIRCASE runs straight from ground level up to the porch landing immediately in front of the door -- the same axis as the door and doormat. Do NOT offset the staircase to one side. Do NOT add a second, mismatched, separate half-level patio strip beside it. The staircase handrail is structurally attached to and runs directly alongside that single staircase, continuous on both sides. Steps lead down to a driveway visible at the screen-left edge of frame, with an ordinary older-model sedan/hatchback wagon parked there. Single-story brick-veneer or weatherboard house with a corrugated-iron roof. A low garden bed/hedge line borders an open lawn on screen-right, native/bushland-style plantings. A letterbox/mailbox near the screen-right edge of the lawn. A Hills Hoist rotary clothesline and a rainwater tank visible as yard set dressing. Clear, dry, midday sun, hard shadows. Bushland visible in the distant background. No watermark, no text, no labels in this image.

> [!note]- Prompt sent, Env_Panel_2_TopDown: 2026-09-19 04:17 UTC, transcript line 6532, typed inline, never saved to a file; kept here verbatim
> Using the attached reference image (a doorbell-camera photo of this exact house) as the ground truth for what exists and its rough spatial arrangement, create a TOP-DOWN BIRD'S-EYE SITE PLAN of the same property -- clean architectural schematic/blueprint line-art style, NOT photorealistic. No people, no animals.
>
> Show, from directly overhead: the house footprint (roof outline) with the front door marked, a single centered staircase running straight down from the door to the driveway (matching the reference image -- centered, not offset), the driveway with the parked car, the front lawn, the hedge line, and every yard landmark visible in the reference: the mailbox, the Hills Hoist rotary clothesline, and the rainwater tank.
>
> Label every element with small text callouts and thin leader lines: "HOUSE", "FRONT DOOR", "RING CAMERA" (at the door, doorbell mount position), "STAIRCASE", "DRIVEWAY", "CAR", "MAILBOX", "CLOTHESLINE (HILLS HOIST)", "WATER TANK", "FRONT LAWN", "HEDGE LINE". All labels in a consistent small clean font, leader lines thin and precise, never overlapping other labels.
>
> This is a spatial reference diagram only, for checking geometry, not a real camera shot.

> [!note]- Prompt sent, Env_Panel_3_Reverse: 2026-09-19 04:19 UTC, transcript line 6565, typed inline, never saved to a file; kept here verbatim
> Using the attached reference image (a top-down labeled site plan of this exact property) as the ground truth for the spatial layout, create a WIDE REVERSE ESTABLISHING VIEW -- standing out at the driveway, looking back toward the house and front door. Clean architectural schematic/line-art illustration style, NOT photorealistic, matching the reference's line-art style. No people, no animals.
>
> Show the house front elevation, the front door, the single centered staircase running straight down from the door to the driveway (matching the reference exactly -- centered, not offset), the driveway with the parked car, the front lawn, hedge line, mailbox, Hills Hoist clothesline, and water tank, all in the same spatial arrangement as the reference top-down plan.
>
> Label with small text callouts and thin leader lines: "FRONT DOOR", "RING CAMERA", "STAIRCASE", "DRIVEWAY", "CAR".
>
> Also bake this exact sentence as a caption strip near the top of the image: "This is a reverse shot of the doorbell for spatial reference only."
>
> This is a spatial reference diagram only, not real camera output.

**Tony said:**

> [!quote] Tony, 2026-09-19 04:19 UTC (transcript line 6539)
> So let me ask you this: when you're putting this thing together, are you starting off with the photorealistic shot first?

> [!quote] Tony, 2026-09-19 04:19 UTC (transcript line 6562, typed while the agent was still working)
> So you really should think about this more like an architect, right? See how long your stairs are? That's for one ridiculous, right? Stop.

> [!quote] Tony, 2026-09-19 04:20 UTC (transcript line 6575)
> Okay, just stop, stop, stop.

> [!quote] Tony, 2026-09-19 04:23 UTC (transcript line 6592)
> Okay, you need to generate the diagrams. First, you need to understand the walkway that a driver would need to get to the steps. You need to not make the steps so long. The house is not that high. It needs 4 to 5 steps. All of this stuff needs to be thought about first. 
>
> So none of these decisions you've made are even grounded. 
>
> But the diagram and the blueprints are what dictate what the Ring doorbell POV should look like, so they should be done in that order. 
>
> So yes, maybe you should search up a real street view, get a screen grab of that via the API, and then don't exactly duplicate that house, but use that as a reference to build your diagrams, your walkways, your stairs, your steps, your porches. 
>
> And then you need some check that checks it to make sure that it's correct, because you're just throwing random bushes. You're not even thinking about how somebody would even walk to get to the walkway. 
>
> You need something that checks your diagram plan or work before it even gets created. You know, this is what the whole blocking, plausibility, all of that stuff is. I don't know. You're just really getting on my nerves right now.

**Changed next:** Agent pulled Street View frames of Sutton NSW (now `Research/Reference_Images/Sutton_NSW_Streetview.jpg` and `heading_*.jpg`), wrote `Data/Architectural_Site_Plan.md` (4-5 steps, a real walkway) before any image, locked the Architectural Plausibility Check (diagram before photo) into the skill, and generated a top-down diagram first.

**Worked?:** Partly. Right step count, but the diagram's hedge sealed the driveway off from the walkway (attempt 5).

## environment, attempt 5

**Shown:** `Data/Env_Diagram_1_TopDown_v2.png` (the agent had already flagged the unbroken hedge before Tony replied). With his reply Tony pasted four photos of real Australian houses as layout references (stock photos with watermarks, for reference only): [Session_Reference_House_1.webp](Session_Reference_House_1.webp), [Session_Reference_House_2.webp](Session_Reference_House_2.webp), [Session_Reference_House_3.webp](Session_Reference_House_3.webp), [Session_Reference_House_4.webp](Session_Reference_House_4.webp).

**Prompt sent:** Inline (below).

> [!note]- Prompt sent: 2026-09-19 04:29 UTC, transcript line 6705, typed inline, never saved to a file; kept here verbatim
> Create a TOP-DOWN BIRD'S-EYE ARCHITECTURAL SITE PLAN, clean schematic/blueprint line-art style, NOT photorealistic. No people, no animals.
>
> This is a single-story house on a raised bearer-and-joist floor (common for a sloped regional-Australian block), floor height roughly 450-900mm above ground. The front door is centered on the street-facing wall. Directly in front of the door is a small flat porch landing at floor height. A SINGLE, DIRECT, CENTERED STAIRCASE OF EXACTLY 4 TO 5 STEPS runs straight down from that porch landing to ground level, same axis as the door -- this is a short, ordinary residential stair run, NOT a long or tall staircase, matching a normal single-story house. No offset, no second mismatched patio level.
>
> A single continuous paved walkway connects the base of the staircase to the driveway where a car is parked at screen-left. This is the actual route a person walks: door, porch landing, down 4-5 steps, straight along the short connecting path, to the driveway. Nothing blocks this path -- hedges and garden beds sit beside the walkway and driveway, never across them.
>
> Include, each labeled with small text and a thin leader line: "HOUSE", "FRONT DOOR", "RING CAMERA" (doorbell mount beside the door), "PORCH LANDING", "STAIRCASE (4-5 STEPS)", "WALKWAY", "DRIVEWAY", "CAR", "MAILBOX", "CLOTHESLINE (HILLS HOIST)", "WATER TANK", "FRONT LAWN", "HEDGE LINE". Labels never overlap each other or the drawing.
>
> This is a spatial reference diagram only, for checking geometry before any photo is generated.

**Tony said:**

> [!quote] Tony, 2026-09-19 04:36 UTC (transcript line 6747)
> Why is there no path to the front steps from the driveway? You got a row of bushes there. These are better examples of real Australian suburban or rural houses.
>
> *[Tony pasted 4 image(s) with this message, saved from the transcript as [Session_Reference_House_1.webp](Session_Reference_House_1.webp), [Session_Reference_House_2.webp](Session_Reference_House_2.webp), [Session_Reference_House_3.webp](Session_Reference_House_3.webp), [Session_Reference_House_4.webp](Session_Reference_House_4.webp).]*

> [!quote] Tony, 2026-09-19 04:37 UTC (transcript line 6781, typed while the agent was still working)
> Stop.

> [!quote] Tony, 2026-09-19 04:39 UTC (transcript line 6800)
> I never asked you to bind those images. I'm making a statement in reference to your diagram. I'm showing you examples of what real houses in Australia look like. We can use those as references to build your diagram. You can create a prompt or a JSON prompt based on those images to then create your own image in GPT Image 2. That's what I was trying to point out.

> [!quote] Tony, 2026-09-19 04:39 UTC (transcript line 6808)
> But don't build anything yet.

**Changed next:** Hedge-gap requirement added to the site plan; a regeneration (`Env_Diagram_1_TopDown_v3.png`) failed on its own and produced no file; on Tony's follow-up the plausibility check's first step now invokes Production-Research-Agent for tailored real reference photos; `Data/Session_Handoff_2026-09-19.md` was written and work paused overnight.

**Worked?:** Yes for the path. The next day's `Data/Env_v2_Panel_1_TopDown.png` had a verified hedge gap at the walkway.

## environment, attempt 6

**Shown:** `Data/Env_v2_Panel_1_TopDown.png`, then `Data/Env_v2_Panel_2_POV.png` chained from it, shown in-session 2026-09-19 15:33-15:36 UTC.

**Prompt sent:** Inline (below). The top-down also had `Research/Reference_Images/Queenslander_Front_Steps_01.jpg` attached as a step-count reference.

> [!note]- Prompt sent, Env_v2_Panel_1_TopDown: 2026-09-19 15:32 UTC, transcript line 7225, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is a real historic photo of a Queenslander-style Australian house on a raised floor -- use it ONLY to ground the realistic proportion and step-count of a raised-floor entry staircase (a short, modest run, well under 10 steps), not for its architectural style, color, or era.
>
> Create a TOP-DOWN BIRD'S-EYE ARCHITECTURAL SITE PLAN, clean schematic/blueprint line-art style, NOT photorealistic. No people, no animals.
>
> Single-story house on a raised bearer-and-joist floor, floor height roughly 450-900mm above ground -- matching reference image 1's real proportions. Front door centered on the street-facing wall. Small flat porch landing directly in front of the door at floor height. A SINGLE, DIRECT, CENTERED STAIRCASE OF EXACTLY 4 TO 5 STEPS runs straight down from that landing to ground level, same axis as the door -- a short ordinary residential stair run matching reference image 1, NOT a long or tall staircase. No offset, no second mismatched patio level.
>
> CRITICAL -- the walkway, this is the single most important requirement: a continuous paved concrete walkway runs from the driveway, directly across the front lawn, to the base of the staircase -- a real connected path a visitor actually walks. Any hedge, garden bed, or border along the driveway or lawn edge MUST have a clear, visible GAP or OPENING exactly where this walkway crosses it. Do NOT draw one continuous unbroken hedge line sealing the driveway off from the rest of the yard -- this is a hard requirement, check it before finishing. Garden beds and low plantings run ALONGSIDE the walkway as edging, never AS a wall blocking it.
>
> Include, each labeled with small text and a thin leader line: HOUSE, FRONT DOOR, RING CAMERA (doorbell mount beside the door), PORCH LANDING, STAIRCASE (4-5 STEPS), WALKWAY (with visible hedge gap), DRIVEWAY, CAR, MAILBOX, CLOTHESLINE (HILLS HOIST), WATER TANK, FRONT LAWN, HEDGE LINE (with gap at walkway). Labels never overlap each other or the drawing.
>
> This is a spatial reference diagram only, for checking geometry before any photo is generated.

> [!note]- Prompt sent, Env_v2_Panel_2_POV: 2026-09-19 15:34 UTC, transcript line 7258, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is the ground-truth top-down site plan for this exact property -- match its geometry exactly: door/staircase/walkway/driveway/car/hedge-gap/mailbox/clothesline/water-tank positions and relationships must all be consistent with it.
>
> Generate a photorealistic doorbell-camera reference image, full color, wide-angle fisheye lens distortion matching a mainstream 2018/2019-era Ring-style doorbell camera mounted at door height, looking down and out over the porch. No people, no hands, no animals, no held objects.
>
> Doormat centered in the lower-frame foreground directly below the camera. A single, direct, centered staircase of exactly 4-5 steps runs straight from the porch landing down to ground level, same axis as the door -- matching reference image 1 exactly, a short ordinary residential stair run. A continuous paved walkway connects the base of the staircase straight across the lawn to the driveway, with a clear visible gap in the hedge line exactly where the walkway crosses it -- matching reference image 1's layout precisely, the hedge must NOT be one unbroken line. Driveway visible at the screen-left edge with an ordinary older-model sedan/hatchback parked there. Single-story brick-veneer or weatherboard house with a corrugated-iron roof. Hedge line and open lawn on screen-right with native/bushland-style plantings, a gap in the hedge at the walkway. A letterbox/mailbox near the screen-right edge past the hedge gap. A Hills Hoist rotary clothesline and a rainwater tank visible as yard set dressing, matching reference image 1's positions. Clear, dry, midday sun, hard shadows. Bushland visible in the distant background. No watermark, no text, no labels in this image.

> [!note]- Prompt sent, Env_v2_Panel_3_Reverse (pre-flip, superseded): 2026-09-19 15:37 UTC, transcript line 7291, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is the photorealistic doorbell POV of this exact property -- use it as ground truth for every element, material, and position. Reference image 2 is the top-down site plan -- use it for exact spatial layout.
>
> Create a WIDE REVERSE ESTABLISHING VIEW -- standing out at the driveway, looking back toward the house and front door. Clean architectural schematic/line-art illustration style, NOT photorealistic. No people, no animals.
>
> Show the house front elevation, the front door, the single centered staircase (matching reference image 1's step count and proportions exactly), the continuous walkway connecting the staircase to the driveway with a clear gap in the hedge line at the crossing point (matching reference image 1 exactly -- do not draw an unbroken hedge), the driveway with the parked car, the front lawn, mailbox, Hills Hoist clothesline, and water tank, all in the same spatial arrangement as both reference images.
>
> Label with small text callouts and thin leader lines: FRONT DOOR, RING CAMERA, STAIRCASE, WALKWAY (hedge gap), DRIVEWAY, CAR.
>
> Also bake this exact sentence as a caption strip near the top of the image: This is a reverse shot of the doorbell for spatial reference only.
>
> This is a spatial reference diagram only, not real camera output.

**Tony said:**

> [!quote] Tony, 2026-09-19 15:37 UTC (transcript line 7298)
> You have the driveway on the wrong side, so you really need to flip the image horizontally.

> [!quote] Tony, 2026-09-19 15:40 UTC (transcript line 7332)
> Update those now, then redo panel 3, however, you need to fix whatever detects the image because you're placing the driveway on the wrong side in the prompt. Do you understand how to read the original diagram that we are basing the images off of?

**Changed next:** Agent mirrored the POV with PIL (`Data/Env_v2_Panel_2_POV_Flipped.png`, no new prompt), wrote the compass/mirror rule into the site plan, swapped every screen-left/right in `Blocking_Plan.md` and `Storyboard_Spec.json`, and regenerated panel 3 as `Data/Env_v2_Panel_3_Reverse_Fixed.png` with an explicit mirror rule.

**Worked?:** Partly. Sides were fixed, but landmarks sat in the wrong places (attempt 7).

## environment, attempt 7

**Shown:** `Character_Sheets/Environment_Sheet_v2.png`, sent 15:48 UTC: PIL composite of `Env_v2_Panel_2_POV_Flipped.png`, `Env_v2_Panel_1_TopDown.png`, `Env_v2_Panel_3_Reverse_Fixed.png` (the "front black-and-white diagram") and `Env_v2_Panel_4_Landmarks.png`.

**Prompt sent:** Inline for the two new panels (below); the composite itself had no prompt.

> [!note]- Prompt sent, Env_v2_Panel_3_Reverse_Fixed: 2026-09-19 15:45 UTC, transcript line 7439, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is the CORRECTED photorealistic doorbell POV of this exact property -- in it, the driveway/car is on the RIGHT side of frame, the hedge/mailbox/lawn is on the LEFT side. Reference image 2 is the top-down site plan.
>
> Create a WIDE REVERSE ESTABLISHING VIEW -- standing out at the driveway, looking BACK toward the house and front door (the opposite direction from reference image 1). Clean architectural schematic/line-art illustration style, NOT photorealistic. No people, no animals.
>
> CRITICAL ORIENTATION RULE: since this view faces the OPPOSITE direction from reference image 1 (the doorbell POV), every left/right position must be MIRRORED relative to reference image 1. Reference image 1 has the driveway/car on its RIGHT -- therefore THIS reverse view must show the driveway/car on its LEFT side of frame, and the hedge/mailbox/lawn on its RIGHT side of frame. Do not copy reference image 1's left/right directly -- mirror it, because this camera faces the opposite way.
>
> Show the house front elevation, the front door, the single centered staircase (matching reference image 1's step count and proportions exactly), the continuous walkway connecting the staircase to the driveway with a clear gap in the hedge line at the crossing point, the driveway with the parked car on the LEFT side of frame, the front lawn, mailbox, Hills Hoist clothesline, and water tank on the RIGHT side of frame.
>
> Label with small text callouts and thin leader lines: FRONT DOOR, RING CAMERA, STAIRCASE, WALKWAY (hedge gap), DRIVEWAY (left side), CAR (left side).
>
> Also bake this exact sentence as a caption strip near the top of the image: This is a reverse shot of the doorbell for spatial reference only.
>
> This is a spatial reference diagram only, not real camera output.

> [!note]- Prompt sent, Env_v2_Panel_4_Landmarks: 2026-09-19 15:46 UTC, transcript line 7464, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is the photorealistic doorbell POV of this exact property -- use it as ground truth for the exact appearance of the mailbox, Hills Hoist clothesline, and rainwater tank shown in it.
>
> Create a LANDMARK/DETAIL CALL-OUT PANEL, clean schematic/technical-illustration line-art style, NOT photorealistic. No people, no animals.
>
> Show three isolated close-up detail views, side by side, each individually labeled: (1) the mailbox -- matching reference image 1's exact design, mounted on a post; (2) the Hills Hoist rotary clothesline -- matching reference image 1's exact design, the classic rotary umbrella-style Australian clothesline; (3) the rainwater tank -- matching reference image 1's exact design, a cylindrical corrugated-metal tank. Each detail rendered clearly enough to lock its exact appearance for reuse in later shots of this same location. Plain white background between the three details, clear separation, small text label beneath each one.
>
> This is a spatial/object reference panel only, not real camera output.

**Tony said:**

> [!quote] Tony, 2026-09-19 15:51 UTC (transcript line 7506)
> Okay, this is good. However, you have the rotary clothesline and the rainwater tank in the wrong place on the top-down overview, as well as the front black-and-white diagram. You need to fix those two so they match the POV reference. So your spatial reference is incorrect, and the top-down overview is incorrect. Again, another thing that I have to keep telling you and reminding you had you done a thorough check, you would know these are wrong.

**Changed next:** Agent re-read the POV, put the water tank on the driveway side and the clothesline on the lawn side in the site plan, and regenerated `Data/Env_v3_Panel_1_TopDown.png` and `Data/Env_v3_Panel_3_Reverse.png` chained from the POV.

**Worked?:** No. Tony: still incorrect (attempt 8).

## environment, attempt 8

**Shown:** `Character_Sheets/Environment_Sheet_v3.png`, sent 15:56 UTC and re-sent 16:33 UTC: `Env_v2_Panel_2_POV_Flipped.png`, `Env_v3_Panel_1_TopDown.png`, `Env_v3_Panel_3_Reverse.png`, `Env_v2_Panel_4_Landmarks.png`. Tony's "front perspective ... the frame right underneath it" is the bottom-left panel, `Data/Env_v3_Panel_3_Reverse.png`. Tony's red-pen markups (pasted with his 16:43 UTC message): [Session_Markup_Panel_1.webp](Session_Markup_Panel_1.webp) marks up the top-down `Env_v3_Panel_1_TopDown.png` (water tank and clothesline circled, arrows moving them toward the street); [Session_Markup_Panel_2.webp](Session_Markup_Panel_2.webp) marks up the front/reverse view `Env_v3_Panel_3_Reverse.png` (water tank and clothesline circled, hedge extended right, "Bush" written by the mailbox).

**Prompt sent:** Inline for the two new panels (below).

> [!note]- Prompt sent, Env_v3_Panel_1_TopDown: 2026-09-19 15:53 UTC, transcript line 7544, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is the ground-truth photoreal doorbell POV of this exact property. Match its landmark positions EXACTLY -- do not group landmarks by assumption.
>
> Create a TOP-DOWN BIRD'S-EYE ARCHITECTURAL SITE PLAN, clean schematic/blueprint line-art style, NOT photorealistic. No people, no animals.
>
> Single-story house on a raised bearer-and-joist floor. Front door centered on the street-facing wall, small porch landing, a single centered staircase of 4-5 steps running straight down, same axis as the door. A continuous paved walkway runs from the driveway across the lawn to the base of the staircase, with a clear visible gap in the hedge line exactly where the walkway crosses it -- do not draw an unbroken hedge.
>
> Driveway with the parked car on the WEST side (page-left, matching reference image 1's right-side POV placement, per this shot's locked mirror rule). CRITICAL LANDMARK PLACEMENT, checked directly against reference image 1: the RAINWATER TANK is on the WEST side, near the driveway -- NOT grouped with the clothesline. The HILLS HOIST CLOTHESLINE is on the EAST side (page-right), with the lawn, hedge, and mailbox. These two landmarks are on OPPOSITE sides of the property -- do not place them next to each other.
>
> Include, each labeled with small text and a thin leader line: HOUSE, FRONT DOOR, RING CAMERA, PORCH LANDING, STAIRCASE (4-5 STEPS), WALKWAY (hedge gap), DRIVEWAY (west), CAR (west), WATER TANK (west, near driveway), MAILBOX (east), CLOTHESLINE / HILLS HOIST (east), FRONT LAWN, HEDGE LINE (gap at walkway).
>
> This is a spatial reference diagram only, for checking geometry before any photo is generated.

> [!note]- Prompt sent, Env_v3_Panel_3_Reverse: 2026-09-19 15:54 UTC, transcript line 7563, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is the ground-truth photoreal doorbell POV (driveway/car/water tank on its RIGHT, clothesline/mailbox/lawn on its LEFT). Reference image 2 is the corrected top-down site plan.
>
> Create a WIDE REVERSE ESTABLISHING VIEW -- standing at the driveway, looking BACK toward the house (the opposite direction from reference image 1). Clean architectural schematic/line-art illustration style, NOT photorealistic. No people, no animals.
>
> MIRROR RULE: since this view faces the opposite direction from reference image 1, left/right must be MIRRORED. Reference image 1 has driveway/car/water tank on its RIGHT -- so THIS view must show driveway/car/water tank on its LEFT. Reference image 1 has clothesline/mailbox/lawn on its LEFT -- so THIS view must show them on its RIGHT.
>
> CRITICAL LANDMARK PLACEMENT: the water tank stays WITH the driveway/car group (left side of this view) -- do NOT place it with the clothesline. The Hills Hoist clothesline stays WITH the lawn/mailbox group (right side of this view).
>
> Show the house front elevation, front door, centered staircase (4-5 steps), the walkway with a clear hedge gap at the crossing point, driveway/car/water tank on the LEFT, lawn/mailbox/clothesline on the RIGHT.
>
> Label with small text callouts and thin leader lines: FRONT DOOR, RING CAMERA, STAIRCASE, WALKWAY (hedge gap), DRIVEWAY (left), CAR (left), WATER TANK (left), MAILBOX (right), CLOTHESLINE (right).
>
> Also bake this exact sentence as a caption strip near the top: This is a reverse shot of the doorbell for spatial reference only.
>
> This is a spatial reference diagram only, not real camera output.

**Tony said:**

> [!quote] Tony, 2026-09-19 16:20 UTC (transcript line 7592)
> They are still incorrect. Do you not understand how to read a diagram? Don't redo anything yet. Just answer my question. You're getting it wrong every time. Answer my question.

> [!quote] Tony, 2026-09-19 16:22 UTC (transcript line 7605)
> So then, what can we do to fix this? Not by trying harder, but by giving you the tools to actually see what's going on and why you are wrong.

> [!quote] Tony, 2026-09-19 16:35 UTC (transcript line 7761)
> Okay, you're wrong on all accounts, and the other thing that you're wrong about is that the car is facing the wrong direction in the POV. The thing is, I can mark in red what's wrong on the diagram, but that doesn't help you learn how to fix it in the future. That's the problem I see.

> [!quote] Tony, 2026-09-19 16:43 UTC (transcript line 7774)
> Okay, so your front perspective, right? Not the POV, but the frame right underneath it. I'm just going to tell you what's wrong with it.
>
> * If you look at the hedges in the front, the right-side hedges are supposed to go all the way to the right. You have them cut off.
> * The clothesline thing is supposed to be a lot closer to the hedges, so a lot closer to the street, almost.
> * The water tank is supposed to be closer to the road.
>
>  At least that's how you have them shown in the POV, right? That's also wrong in the top-down. You have the car pulled in forward in the top-down and the front diagram view, but in the POV, you have the car backed in. That's really what's wrong.
>
> Don't build or do anything yet. I'm not asking you to. We're brainstorming how to do this correctly. You keep building stuff that's incorrect and doesn't work, so we need to strategize this with a real plan.
>
> *[Tony pasted 2 image(s) with this message, saved from the transcript as [Session_Markup_Panel_1.webp](Session_Markup_Panel_1.webp), [Session_Markup_Panel_2.webp](Session_Markup_Panel_2.webp).]*

> [!quote] Tony, 2026-09-19 16:46 UTC (transcript line 7792)
> I have told you a hundred times you need to create the diagrams first. The diagrams always need to be created first. Here's the order:
>
> 1. Top-down
> 2. Front view diagram
> 3. POV
>
>  Everything from the top down is the truth of source, so you have to build everything else off of your truth of source. If you do this again, I'm firing you.

> [!quote] Tony, 2026-09-19 16:48 UTC (transcript line 7800)
> You need to lock it in first in your rules or the pipeline. Always do the order that I told you to first. If this happens again, I swear to God I'm going to kill you. 
>
> Then you need to strengthen your depth. When you're comparing, you need to understand depth, not just left and right. 
>
> Once you fix all that, we can proceed.

> [!quote] Tony, 2026-09-19 16:55 UTC (transcript line 7883)
> Okay, so we know the top-down that we built already is fine. Even though it's different from the front view and the POV, that's fine. It's because you built them in the wrong order anyway. Let's treat our current top-down as the truth of source, and then you go through the process you normally would, which would then create the front view. You check it, and then you create the POV and check it. Remember, everything has to match the top-down. And that includes right and left camera view, whether it's viewing it from north to south, south to north, or east to west. You need to judge depth and spatial awareness. If something's supposed to be close to a bush, it can't be different in the other images.

**Changed next:** Built `check_landmark_positions.py` (OWL-ViT: works on photos, not on line-art); locked the order top-down, then front view, then POV, plus the depth/extent/orientation rule, into the skill; rewrote the site plan as an x/y/extent/orientation spec; kept `Env_v3_Panel_1_TopDown.png` unchanged as the source of truth and rebuilt the front view and POV from it.

**Worked?:** Yes in the end. The top-down went into the final sheet unchanged; the front view was approved at its attempt 4; the POV was settled by Tony's own edit.

## environment.front_view, attempt 1

**Shown:** `Data/Env_v4_Panel_2_Front.png` (schematic), shown in-session about 16:58 UTC. The agent flagged that the clothesline depth was still wrong.

**Prompt sent:** Inline (below), with `Data/Env_v3_Panel_1_TopDown.png` attached.

> [!note]- Prompt sent: 2026-09-19 16:57 UTC, transcript line 7910, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is the top-down site plan for this exact property -- the SOURCE OF TRUTH for all geometry. Match it exactly.
>
> Create a WIDE REVERSE ESTABLISHING VIEW -- standing at the driveway, looking BACK toward the house (facing north, up the page of reference image 1). Clean architectural schematic/line-art illustration style, NOT photorealistic. No people, no animals.
>
> MIRROR RULE (x-axis only): reference image 1 has west (driveway/car/water tank) on page-LEFT, east (hedge/mailbox/clothesline) on page-RIGHT. Since this view faces north (same direction as looking up the top-down page), it does NOT mirror -- match reference image 1's left/right directly: driveway/car/water tank on this view's LEFT, hedge/mailbox/clothesline on this view's RIGHT.
>
> DEPTH (y-axis, house-to-street) -- this is critical, check it explicitly for every element:
> - Water tank: near the STREET/camera end (close to where you are standing), NOT near the house.
> - Clothesline: near the STREET/camera end (close to where you are standing), NOT mid-yard or near the house.
> - Mailbox: near the street/camera end, at the property's east edge.
> - The house, front door, and staircase are far in the background (near end of the property).
> - The hedge on the east side runs the FULL length of the property, from near the house all the way to the street -- it must reach the far edge, not stop short partway.
> - A low bush/shrub sits beside the mailbox.
>
> CAR ORIENTATION (independent fact, check separately from position): the car is BACKED IN to the driveway -- its REAR (trunk, tail lights) faces the house/background, its FRONT （nose, headlights) faces the camera/street, as if ready to drive forward and out. This is critical -- do not draw it nose-in.
>
> Label with small text callouts and thin leader lines: FRONT DOOR, RING CAMERA, STAIRCASE, WALKWAY (hedge gap), DRIVEWAY, CAR (backed in), WATER TANK (near street), MAILBOX, CLOTHESLINE (near street), BUSH.
>
> Also bake this exact sentence as a caption strip near the top: This is a reverse shot of the doorbell for spatial reference only.
>
> This is a spatial reference diagram only, not real camera output.

**Tony said:**

> [!quote] Tony, 2026-09-19 16:59 UTC (transcript line 7937)
> Yes, and the one reminder is when you're prompting for the POV: since the camera is facing the road and the water tank is behind you, you don't need to prompt a water tank in the shot. Is that understood? Also, are you sending these as reference images as well, included with your prompt, because you probably should?

> [!quote] Tony, 2026-09-19 17:01 UTC (transcript line 7950)
> Yes, and to be honest with you, maybe the front view shouldn't be a diagram. Maybe it should be more photorealistic. 
>
> I think what happens is, when you send the prompt to create the front view image, you should send it with the diagram and just explain the shot where it's coming from. Let it use the diagram to interpret where things are supposed to be. 
>
> And then you would do that with the POV as well. 
>
> Let's try it first with the front view in a more photorealistic style, and then you add the labels later. Unless you think the GPT image 2 can handle adding the labels

> [!quote] Tony, 2026-09-19 17:05 UTC (transcript line 7958)
> Yes, go ahead

**Changed next:** Generated a photorealistic, unlabeled front view with the top-down attached as the geometry reference; labels to be added afterwards with PIL.

**Worked?:** Partly. The agent reported the clothesline depth fixed and Tony did not raise it again, but the car faced the wrong way (attempt 2).

## environment.front_view, attempt 2

**Shown:** `Data/Env_v5_Panel_2_Front_Photoreal.png`. Tony's "Panel 2 version 4" is `Data/Env_v4_Panel_2_Front.png`.

**Prompt sent:** Inline (below), with `Data/Env_v3_Panel_1_TopDown.png` attached.

> [!note]- Prompt sent: 2026-09-19 17:05 UTC, transcript line 7967, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is a top-down architectural site plan of this exact property -- the source of truth for all geometry. Interpret every position, distance, and orientation from it.
>
> This shot is: standing at the driveway/street end of the property, looking back north toward the house -- the reverse angle from the front door's own camera. Generate a PHOTOREALISTIC image, full color, natural daylight, regional-Australian residential setting. No people, no animals, no text, no labels, no captions, no watermark -- a clean photographic reference only.
>
> Interpreting reference image 1's layout: the house, front door, and staircase are in the background (far from this camera). A driveway runs along the LEFT side with a car parked on it, BACKED IN -- the car's front/headlights face this camera (toward the street), its rear/trunk faces the house. A water tank sits near this camera's end of the property, on the left side near the driveway. A hedge line runs along the RIGHT side of the property, reaching the full length from near the house all the way to the street end near this camera -- it must not stop short partway. A rotary Hills Hoist clothesline sits near THIS camera's end of the property (near the street), on the right side with the lawn -- not set back near the house. A mailbox sits at the street end on the right, with a low bush beside it. A paved walkway runs from the driveway across the lawn to the base of the staircase, with a visible gap in the hedge exactly where it crosses.
>
> Clear, dry, midday sun, hard shadows, single-story brick-veneer or weatherboard house with a corrugated-iron roof, native/bushland-style plantings, bushland visible in the distance beyond the property.

**Tony said:**

> [!quote] Tony, 2026-09-19 17:09 UTC (transcript line 7994)
> No, did you base this off of the overhead? Did you give it the overhead reference?

> [!quote] Tony, 2026-09-19 17:12 UTC (transcript line 8007)
> Well, if you look at the front view, it's got the car backwards again. The water tank should be closer to the car, at least if you're looking at the top down, and the grass on the left side is angled. It should be straight. The image looks closer to Panel 2 version 4, which is not correct. It needs to be closer to the latest top-down version. 
>
> Try it again with a better prompt.

**Changed next:** Prompt rewritten to describe the car by visible parts (bumper, headlights, tail lights), put the water tank right beside the car, and keep every lawn edge straight.

**Worked?:** Partly. Tony did not repeat the water-tank note, but found the car still wrong and the left lawn still a triangle (attempt 3).

## environment.front_view, attempt 3

**Shown:** `Data/Env_v6_Panel_2_Front_Photoreal.png`.

**Prompt sent:** Inline (below), with `Data/Env_v3_Panel_1_TopDown.png` attached.

> [!note]- Prompt sent: 2026-09-19 17:14 UTC, transcript line 8031, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is a top-down architectural site plan of this exact property -- the ONLY source of truth for geometry, shapes, and relative distances. Match its straight rectilinear lines and proportions exactly -- do not add artistic angling, curves, or perspective distortion to any lawn edge, hedge line, or boundary that is drawn straight in reference image 1.
>
> This shot is: standing at the driveway/street end of the property, looking back north toward the house -- the reverse angle from the front door camera. Generate a PHOTOREALISTIC image, full color, natural daylight, regional-Australian residential setting. No people, no animals, no text, no labels, no captions, no watermark.
>
> CAR -- describe by visible parts, this is critical: the car's REAR BUMPER AND TAIL LIGHTS are the end closest to the HOUSE/staircase (background of this shot). The car's FRONT BUMPER, HEADLIGHTS, AND WINDSHIELD face this camera / the street (foreground of this shot) -- as if the car reversed into the driveway from the street and is now facing outward, ready to be driven straight out. Do not draw the headlights facing the house.
>
> WATER TANK: positioned immediately next to the car, close together on the same side of the driveway -- not far apart, not near the street end, right beside where the car is parked.
>
> LAWN AND BOUNDARIES: every lawn edge, hedge line, and driveway edge is a STRAIGHT line matching reference image 1's rectilinear layout -- no diagonal or curved edges. The property is a simple rectangle from this angle, not an angled or trapezoidal shape.
>
> The house, front door, and staircase are in the background. A hedge line runs along the right side of the lawn, reaching the full length from near the house to the street. A rotary Hills Hoist clothesline sits near this camera's end of the property (near the street) on the right side. A mailbox sits at the street end on the right with a low bush beside it. A paved walkway runs straight from the driveway across the lawn to the base of the staircase, with a visible gap in the hedge where it crosses.
>
> Clear, dry, midday sun, hard shadows, single-story brick-veneer or weatherboard house with a corrugated-iron roof, native/bushland-style plantings, bushland visible in the distance.

**Tony said:**

> [!quote] Tony, 2026-09-19 17:17 UTC (transcript line 8058)
> You are incorrect. Car orientation is still wrong. And the left-side lawn is still not correct. It's a triangle shape. It is not straight. It does not understand how to render that perspective.

> [!quote] Tony, 2026-09-19 17:18 UTC (transcript line 8064, typed while the agent was still working)
> Maybe in the overhead diagram, you need to label which way the car is facing.

**Changed next:** Car flipped (front toward the house, rear to the street), 50mm-equivalent lens, lawn strips spelled out as rectangles; separately drew CAR FRONT / CAR REAR arrows onto the top-down with PIL (`Data/Env_v3_Panel_1_TopDown_Annotated.png`). The annotated top-down was made just after attempt 4 was launched, so it was first used for the POV.

**Worked?:** Yes. Attempt 4 was approved.

## environment.front_view, attempt 4

**Shown:** `Data/Env_v7_Panel_2_Front_Photoreal.png`.

**Prompt sent:** Inline (below), with `Data/Env_v3_Panel_1_TopDown.png` (not the annotated copy) attached.

> [!note]- Prompt sent: 2026-09-19 17:18 UTC, transcript line 8063, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is a top-down architectural site plan of this exact property -- the ONLY source of truth for geometry and proportions.
>
> This shot is: standing at the driveway/street end of the property, looking back north toward the house. Generate a PHOTOREALISTIC image, full color, natural daylight, regional-Australian residential setting, shot on a standard 50mm-equivalent lens (NOT a wide-angle lens) to keep perspective distortion minimal and natural. No people, no animals, no text, no labels, no watermark.
>
> CAR -- described by visible parts, corrected: the car's FRONT BUMPER, HEADLIGHTS, AND WINDSHIELD are the end closest to the HOUSE/staircase (background). The car's REAR BUMPER AND TAIL LIGHTS face this camera / the street (foreground) -- as if the car pulled straight in nose-first from the street and parked facing the house. Do not draw the headlights facing the street/camera.
>
> WATER TANK: positioned immediately next to the car, close together on the same side of the driveway.
>
> LAWN GEOMETRY -- this is critical, a real defect to fix: the lawn strips on BOTH sides of the central walkway (between the walkway and each hedge line) are simple RECTANGLES of consistent, even width from the foreground (near camera) all the way to the background (near the house) -- like the top-down reference shows. They must NOT narrow into a triangle, wedge, or pinched shape at either end. The hedge lines bordering them run straight and parallel to the walkway the entire distance, never converging or angling inward. Check this specifically on the LEFT side lawn strip (between the driveway and the walkway) before finishing -- it must be a clean rectangle, not a triangle.
>
> The house, front door, and staircase are in the background, centered. A hedge line runs along the right side of the lawn, reaching the full length from near the house to the street, straight. A rotary Hills Hoist clothesline sits near this camera's end of the property (near the street) on the right side. A mailbox sits at the street end on the right with a low bush beside it. A paved walkway runs straight from the driveway across the lawn to the base of the staircase, with a visible gap in the hedge where it crosses.
>
> Clear, dry, midday sun, hard shadows, single-story brick-veneer or weatherboard house with a corrugated-iron roof, native/bushland-style plantings, bushland visible in the distance.

**Tony said:**

> [!quote] Tony, 2026-09-19 17:21 UTC (transcript line 8117)
> Yes, that's correct, lock in the new rules, or whatever you did to create this. Lock that in. That is what we want. Make sure it is reflected in the pipeline. Lock it in.

**Changed next:** The five techniques that worked were locked into `Environment-Sheet-Generation/SKILL.md`; at Tony's request the pain points were logged before going on; later labeled with PIL as `Data/Env_v7_Panel_2_Front_Labeled.png`.

**Worked?:** Yes, final. Bottom-left panel of `Character_Sheets/Environment_Sheet_Final.png`.

## environment.pov, attempt 1

**Shown:** `Data/Env_v8_Panel_3_POV_Photoreal.png`.

**Prompt sent:** Inline (below), with `Data/Env_v3_Panel_1_TopDown_Annotated.png` and `Data/Env_v7_Panel_2_Front_Photoreal.png` attached.

> [!note]- Prompt sent: 2026-09-19 17:28 UTC, transcript line 8257, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is the top-down site plan (annotated with the car front/rear orientation) -- the source of truth for geometry and orientation. Reference image 2 is the approved photorealistic front/reverse-angle view of this same property, taken from the opposite end -- match its house design, materials, colors, and landscaping style exactly, just from the opposite camera position.
>
> This shot is: the doorbell camera's own forward view -- mounted at the front door at door height, looking down and out over the porch toward the street (facing south, the opposite direction from reference image 2). Generate a PHOTOREALISTIC image, full color, wide-angle FISHEYE lens distortion matching a mainstream 2018/2019-era Ring-style doorbell camera, natural daylight. No people, no animals, no text, no labels, no captions, no watermark.
>
> MIRROR RULE (x-axis): reference image 1 has the driveway/car on page-LEFT (west). Since this camera faces the opposite direction from reference image 2 (which matched the top-down directly), THIS view mirrors it: driveway/car on screen-RIGHT. Hedge/clothesline/mailbox on screen-LEFT.
>
> DO NOT include the water tank in this shot -- it sits beside the house near where this camera is mounted, out of the camera's own forward field of view (you cannot see something positioned behind/beside yourself).
>
> CAR -- described by visible parts, matching reference image 1's locked orientation: the car's FRONT BUMPER, HEADLIGHTS, AND WINDSHIELD face this camera / the house (since the front faces north/the house per reference image 1). The car's REAR BUMPER AND TAIL LIGHTS face away from this camera, toward the street.
>
> Doormat centered in the lower-frame foreground, directly below the camera. A single, direct, centered staircase of 4-5 steps runs straight down from the porch landing, same axis as the door, matching reference image 2's exact staircase and railings. A continuous paved walkway connects the base of the staircase to the driveway, with a clear visible gap in the hedge line exactly where it crosses -- the hedge must not be unbroken. The hedge on the left side reaches the full length of the property, from near the house to the street. A rotary Hills Hoist clothesline sits near the street end of the property on the left side, with the lawn. A mailbox sits at the street end on the left with a low bush beside it. Lawn strips are clean rectangles of consistent width, not triangular or wedge-shaped.
>
> Clear, dry, midday sun, hard shadows, single-story brick-veneer or weatherboard house with a corrugated-iron roof matching reference image 2, native/bushland-style plantings, bushland visible in the distance.

**Tony said:**

> [!quote] Tony, 2026-09-19 17:32 UTC (transcript line 8279)
> It is close. The only thing wrong is, if you're looking at the image on the left side, the bushes need to extend the whole width. The bushes on the right side, where the street is, need to stop at the driveway. Right now, they're almost halfway into the driveway.

**Changed next:** Regenerated with the two hedge fixes spelled out, attaching attempt 1 as the second reference.

**Worked?:** Partly. Left side fixed, right side still wrong (attempt 2).

## environment.pov, attempt 2

**Shown:** `Data/Env_v9_Panel_3_POV_Photoreal.png`.

**Prompt sent:** Inline (below), with the annotated top-down and attempt 1 attached.

> [!note]- Prompt sent: 2026-09-19 17:32 UTC, transcript line 8284, typed inline, never saved to a file; kept here verbatim
> Reference image 1 is the top-down site plan (annotated with car orientation) -- the source of truth for geometry. Reference image 2 is the previous version of this exact shot -- match it almost exactly, only fixing the two specific hedge issues described below.
>
> This shot is: the doorbell camera's own forward view, mounted at the front door at door height, looking down and out over the porch toward the street. Generate a PHOTOREALISTIC image, full color, wide-angle FISHEYE lens distortion matching a mainstream 2018/2019-era Ring-style doorbell camera, natural daylight. No people, no animals, no text, no labels, no watermark. No water tank in this shot.
>
> TWO SPECIFIC HEDGE FIXES, checked against the street-side boundary line at the back of the property:
> 1. The LEFT-side hedge (bordering the lawn, clothesline, and mailbox) currently stops short partway across -- it must extend the FULL width of the property on that side, reaching all the way to the left edge of frame, matching reference image 1's hedge line exactly.
> 2. The RIGHT-side hedge (near the street, on the driveway side) currently extends too far and overlaps INTO the driveway -- it must stop exactly at the driveway's own edge/boundary and not cross into the driveway surface at all. The driveway must be completely clear of hedge encroachment along its street-facing edge.
>
> Keep everything else the same as reference image 2: driveway/car on the right (car's front/headlights facing this camera, rear/tail lights facing the street), hedge/clothesline/mailbox on the left, clothesline near the street end, mailbox with a small bush beside it, staircase of 4-5 steps, walkway with a clear hedge gap where it crosses, clean rectangular lawn strips (not triangular), single-story brick-veneer/weatherboard house with a corrugated-iron roof, native/bushland-style plantings, bushland in the distance.

**Tony said:**

> [!quote] Tony, 2026-09-19 17:35 UTC (transcript line 8311)
> You fixed the left side, but the right side is incorrect. Can you just use the inpainting to fix the right side?

> [!quote] Tony, 2026-09-19 17:36 UTC (transcript line 8345, typed while the agent was still working)
> You built an inpainter earlier.

> [!quote] Tony, 2026-09-19 17:42 UTC (transcript line 8394)
> Hi Ben, I've added credits to my OpenAI API platform.

**Changed next:** Built `inpaint_image_region.py` (OpenAI masked edit); the first run failed because the OpenAI account had no credits, then ran after Tony added credits.

**Worked?:** No. The inpaint repainted the car too (attempt 3).

## environment.pov, attempt 3

**Shown:** `Data/Env_v10_Panel_3_POV_Inpainted.png` (opened in-session about 17:43 UTC; the agent also flagged that the mask had swallowed the car).

**Prompt sent:** Inpaint prompt on `Env_v9_Panel_3_POV_Photoreal.png` (below).

> [!note]- Inpaint prompt sent: 2026-09-19 17:42 UTC, transcript line 8404, typed inline, never saved to a file; kept here verbatim
> [mask region 0.70 0.33 1.0 0.72] Remove the tall hedge running alongside this section of the driveway. Replace it with open gravel driveway surface continuing naturally, matching the driveway's existing texture and color, with the bushland/trees visible beyond the property boundary in the background, same as the rest of the scene. The hedge should only exist as a short segment capping the street-facing edge, not running down the length of the driveway.

**Tony said:**

> [!quote] Tony, 2026-09-19 17:44 UTC (transcript line 8428, typed while the agent was still working)
> You painted out the yard on the right. That is incorrect.

> [!quote] Tony, 2026-09-19 17:44 UTC (transcript line 8429, typed while the agent was still working)
> And the car is in the wrong orientation.

**Changed next:** Re-ran the inpaint with a narrower mask (0.70 0.33 1.0 0.49) that leaves the car out.

**Worked?:** No. Tony still rejected the result and fixed the image himself (attempts 4-5).

## environment.pov, attempt 4

**Shown:** `Data/Env_v10a_hedge_top.png`, sent 17:46 UTC.

**Prompt sent:** Inpaint prompt on `Env_v9_Panel_3_POV_Photoreal.png` (below).

> [!note]- Inpaint prompt sent: 2026-09-19 17:44 UTC, transcript line 8427, typed inline, never saved to a file; kept here verbatim
> [mask region 0.70 0.33 1.0 0.49] Remove the hedge in this region so it does not extend down alongside the driveway. Replace with open gravel driveway surface continuing naturally and bushland/trees in the background, matching the rest of the scene. Only a short hedge segment should cap the street-facing edge, not extend down the driveway.

**Tony said:**

> [!quote] Tony, 2026-09-19 17:47 UTC (transcript line 8481)
> Uploaded. Still not right. I'm sick of dealing with your incorrectness and not doing things correctly, so I just edited and changed it myself. Use the uploaded image as the new pOv panel.
>
> *[Tony pasted 1 image(s) with this message, saved from the transcript as [../Character_Sheets/POV_Panel_Final_Tony_Edit.png](../Character_Sheets/POV_Panel_Final_Tony_Edit.png).]*

**Changed next:** Agent found Tony's upload at `~/Desktop/image-1789839883172.jpg`, copied it to `Character_Sheets/POV_Panel_Final_Tony_Edit.png`, and locked it in `Data/Architectural_Site_Plan.md` as ground truth, no further regeneration.

**Worked?:** Yes. Tony's own edit became the final POV (attempt 5).

## environment.pov, attempt 5 (Tony's own edit)

**Shown:** `Character_Sheets/POV_Panel_Final_Tony_Edit.png`, made by Tony, not generated. This is the real case the ledger's `director_edit` source was added for.

**Prompt sent:** None. Tony edited the image by hand (he did not say which version he started from).

**Tony said:**

> [!quote] Tony, 2026-09-19 17:47 UTC (transcript line 8481)
> Uploaded. Still not right. I'm sick of dealing with your incorrectness and not doing things correctly, so I just edited and changed it myself. Use the uploaded image as the new pOv panel.
>
> *[Tony pasted 1 image(s) with this message, saved from the transcript as [../Character_Sheets/POV_Panel_Final_Tony_Edit.png](../Character_Sheets/POV_Panel_Final_Tony_Edit.png).]*

(Same message as attempt 4: the upload is this file.)

**Changed next:** Labeled with PIL as `Data/Env_POV_Labeled.png` (the DRIVEWAY label was moved after it clipped) and composited into the final sheet; only the clean, unlabeled file went to Seedance.

**Worked?:** Yes, final. First frame of the establishing test and `@Image1` of the A-grade final video.

## environment_sheet.final, attempt 1

**Shown:** `Character_Sheets/Environment_Sheet_Final.png`, sent 2026-09-20 00:34 UTC: `Env_POV_Labeled.png`, `Env_v3_Panel_1_TopDown_Annotated.png`, `Env_v7_Panel_2_Front_Labeled.png`, `Env_v2_Panel_4_Landmarks.png`.

**Prompt sent:** None. PIL composite.

**Tony said:**

> [!quote] Tony, 2026-09-20 01:03 UTC (transcript line 8643)
> Okay, let's try creating the Seedance video. Hopefully, it will ignore the labels on the POV ring camera.

**Changed next:** Agent sent only the clean, unlabeled POV to Seedance, never the labeled sheet, so labels could not bleed into the video.

**Worked?:** Yes. No label bleed in either video.

## storyboard, attempt 1

**Shown:** `Storyboard_v1.png`, sent 01:57 UTC. The agent flagged first that frame 5 was missing the kangaroo.

**Prompt sent:** `Data/Storyboard_Prompt_v1.md`. Attached: `Character_Sheets/Delivery_Driver_Character_Sheet.png`, `Character_Sheets/Kangaroo_Character_Sheet.png`, `Character_Sheets/Environment_Plate_1.png` (driver sheet attempt 2, plate attempt 1).

**Tony said:**

> [!quote] Tony, 2026-09-19 01:59 UTC (transcript line 4902)
> After. Two things. So, really, I probably should have checked the character sheet again, but he wouldn't have that bag if he's a driver, right? I know we didn't do a new character sheet based off of the new plausibility study, but that's one thing I want to note.
>
> The other thing I want to note is his car is not present in the driveway. Why don't we rerun the character sheet for him, but base it off of the plausibility study and see what the output is? You need to have some sort of check in your storyboard that uses all the elements that are noted in the matrix. Really, it should come after the matrix, right? It should come from the plausibility study.

(Same message as driver sheet attempt 2.)

**Changed next:** Grounding Coverage Check added; driver sheet and plate regenerated; `Storyboard_Spec.json` hard-constrained against the v1 defects.

**Worked?:** Partly. v2 fixed those, but showed a new defect (attempt 2).

## storyboard, attempt 2

**Shown:** `Storyboard_v2.png`, sent 02:07 UTC.

**Prompt sent:** `Data/Storyboard_Prompt_v2.md`. Attached: `Character_Sheets/Delivery_Driver_Character_Sheet.png`, `Character_Sheets/Kangaroo_Character_Sheet.png`, `Character_Sheets/Environment_Plate_1.png`.

**Tony said:**

> [!quote] Tony, 2026-09-19 02:38 UTC (transcript line 5156)
> In frame 4, the kangaroo looks like it has jumped on the mailbox and looks slightly deformed. The other thing I want to mention is that the delivery driver guy would not leave his whole heating bag. He would take out the item from his heating bag to then place it on the porch.

**Changed next:** Bag-versus-item logic written into `Research/Plausibility_Facts.md`, `Blocking_Plan.md` and `Storyboard_Spec.json`; kangaroo kept clear of the letterbox.

**Worked?:** Partly. v3 fixed the bag and letterbox, but put the kangaroo in frame 1.

## storyboard, attempt 3

**Shown:** `Storyboard_v3.png`. The agent described its defects at 02:42 UTC but only sent the image at 02:46 UTC after Tony asked.

**Prompt sent:** `Data/Storyboard_Prompt_v3.md`. Attached: `Character_Sheets/Delivery_Driver_Character_Sheet.png`, `Character_Sheets/Kangaroo_Character_Sheet.png`, `Character_Sheets/Environment_Plate_1.png`.

**Tony said:**

> [!quote] Tony, 2026-09-19 02:46 UTC (transcript line 5318)
> Yeah, let me look at it first.

> [!quote] Tony, 2026-09-19 02:46 UTC (transcript line 5326)
> Then I need to see it first. You haven't shown it to me.

> [!quote] Tony, 2026-09-19 02:48 UTC (transcript line 5343)
> Well, yes, you need to fix frame 1 because the kangaroo is there, then it disappears, and then it comes back. You need to fix frame 4. In frame 4, he's closer to the car, and in frame 5, he's further away from the car.
>
> I don't understand. You have to look at these frames, dude. What is wrong with you? Can't you run the yellow detection or something to show you where everything is, and then say, "Oh, that can't be true. Things can't disappear, and then they move forward, and then they move back"? Whatever you're doing, if I could grade it, it's a grade D. We need to be at a grade A level of quality.

> [!quote] Tony, 2026-09-19 02:54 UTC (transcript line 5411)
> That is incorrect. In frame 4, he is on the second step down. He's actually off the second step and on the driveway. In frame 5, he is on the second step, looking toward the kangaroo, closer to the ring bow, and in frame 6, he's almost identically where he's at in frame 4. However, the kangaroo has jumped further away, which is consistent with what the real world would be like. 
>
> But what you need to do is zoom in and crop each frame: frame 1, frame 2, frame 3, 4, 5, 6, right? Then you run that through the YOLO tool. Run up. Can it detect things like driveway, steps, sidewalk, etc.?

> [!quote] Tony, 2026-09-19 02:57 UTC (transcript line 5532)
> So let me ask you this, because Yolo basically just puts a bounding box around the object. Can you then add a control net mask, like a black-and-white mask or something like that, that detects the edges of the object, so you can see it and understand its orientation? Can you add that with the little point thing that we had that detected the bone structure? It's got dots and lines in it, whatever that is. Can you implement all those three in the tool? Would that help? Let's start thinking like a grade A student, not a grade C student.

**Changed next:** Built `check_subject_positions.py` (YOLO positions); foot-level positions for frames 4-6 and an explicit "no kangaroo in frames 1-3" constraint.

**Worked?:** No. Tony graded it D; v4 still had the kangaroo in frame 1.

## storyboard, attempt 4

**Shown:** `Storyboard_v4.png` (opened in-session, never sent as a file; Tony reacted to the agent's written findings), plus `Data/Panel1_Replacement.png`, a repaint of frame 1 without the kangaroo reference that the agent held back because of a scale jump.

**Prompt sent:** `Data/Storyboard_Prompt_v4.md`. Attached: `Character_Sheets/Delivery_Driver_Character_Sheet.png`, `Character_Sheets/Kangaroo_Character_Sheet.png`, `Character_Sheets/Environment_Plate_1.png`. The frame-1 repaint prompt was inline (below).

> [!note]- Frame-1 repaint prompt (Panel1_Replacement.png): 2026-09-19 03:07 UTC, transcript line 5678, typed inline, never saved to a file; kept here verbatim
> Fixed wide-angle fisheye doorbell-camera view, mounted at door height, mainstream 2018/2019-era Ring-style consumer hardware, modest dynamic range, no pan/tilt/zoom. Looking down and out over a regional-Australian front porch. A local takeaway delivery driver (see reference image 1 for his exact appearance) crosses the porch from screen-left toward a doormat centered in the lower-frame foreground, carrying a plain insulated delivery bag by its handle -- bag still closed/full, nothing placed on the doormat yet. He is the ONLY subject in this image. Do not include any kangaroo, any other animal, or any other person anywhere in this image -- none exists in this moment of the shot. Background environment must exactly match reference image 2: single-story brick-veneer/weatherboard house with corrugated-iron roof, porch steps leading down to a driveway with the drivers ordinary older-model car parked and visible at screen-left, Hills Hoist clothesline, rainwater tank, native/bushland garden plantings, hedge line, open lawn, letterbox on screen-right, bushland background, clear dry midday sun with hard shadows. No text, captions, borders, watermarks, or graphics anywhere in the image.

**Tony said:**

> [!quote] Tony, 2026-09-19 03:03 UTC (transcript line 5594)
> Okay, I'm fine with you repainting. If you can create that tool, let's make that tool a global tool so any video pipeline can use it and only use it as needed. Maybe we make a rule where you can only use it after a certain amount of attempts. 
>
> The other thing is, you went ahead and did some things without me approving, right? I asked you questions. When I ask you questions, you answer the questions first. I never answered your question, "Want me to build that?" You just started doing stuff, so you never even let me get to the point where I could even read stuff. You just started doing stuff. 
>
> But yes, like I said, you need to think like an A-grade student. An A-grade student would build in those things that are missing and that are not getting you to detect the human, the animal relation, things like that. Whatever tools you can build that make me stop asking you less to fix everything that's going wrong, that's what I want. 
>
> Whether that's a tool that makes you prompt better or structure the prompt better, whether it's a tool that makes you reread the Seedance prompting guides before you start prompting (and then, when you do start prompting, build yourself some sort of schema or JSON or whatever to keep things consistent), those are practices that you should have instilled, not only in you, but in the video pipeline, right?
>
> You shouldn't have to reinvent this every time I ask you to do a video and you get things completely wrong. I'm not holding that all on you, but the point of these reiterations is that we get better, right? Making these videos should get better. They should be easier over time, right? I feel like we're working backwards, like they're getting worse.

> [!quote] Tony, 2026-09-19 03:09 UTC (transcript line 5710)
> Yes, why don't you pause for a minute?

> [!quote] Tony, 2026-09-19 03:10 UTC (transcript line 5717)
> Let me see the exact prompt you're giving to KIE for the storyboard. What are you using to create the storyboard? GPT image 2?

> [!quote] Tony, 2026-09-19 03:11 UTC (transcript line 5744)
> Show me the prompt. Don't make me open a .md file.

> [!quote] Tony, 2026-09-19 03:14 UTC (transcript line 5752)
> Now, why aren't you tagging the reference items, like driver? @driver_character_sheet, etc per scene
>
> Does GPT image 2 not accept those as references? I feel like you need to be explicit with that, and maybe you need a refresher on GPT image 2 prompting. Do we need to build a prompting guide skill? Or do we already have a skill that needs to be refreshed? Are you even reading the skill? These things need to be injected when you use these tools.

> [!quote] Tony, 2026-09-19 03:19 UTC (transcript line 5778)
> Okay, since you didn't follow it and you keep having this problem, what we need to do is make some sort of rule that applies to any video pipeline: if we use a specific tool, you must search to see if there's a skill for that tool. You must read that skill, or inject the skill, or invoke the skill, so you properly prompt for that tool every time, so it's always consistent, no matter which video pipeline I'm using. You're the brain that's supposed to do it, but you're not doing it, so we need a rule that makes you do it. 
>
> And like I said, we need to do this for every tool:
>
> * If you ever need to use Seedance, you must read the Seedance skill or guide.
> * If you ever use VO3, you must read the guide.
> * If you ever use GPT-Image-2, you need to read the guide.
>
>  That needs to be mandatory. If there is not a guide, then you need to tell me, "Hey, I do not have a guide for this, so I don't know how to prompt it correctly." Then the tool manager or something needs to go gather all of that info to then create a guide based off real documents that are tried and true from the creator of that model or engine.

**Changed next:** Reference images now labeled by role: `reference_images` became a required field in `storyboard_contract.py`, the rule went into GPT-Image-2-Prompting-Guide, and `Video_Editor/CLAUDE.md` now requires reading a model's prompting guide before every generation.

**Worked?:** Partly. In v5 the kangaroo was gone from frame 1.

## storyboard, attempt 5

**Shown:** `Storyboard_v5.png` (opened in-session; the agent reported it as passing).

**Prompt sent:** `Data/Storyboard_Prompt_v5.md` (first version with the REFERENCE IMAGES block). Attached: `Character_Sheets/Delivery_Driver_Character_Sheet.png`, `Character_Sheets/Kangaroo_Character_Sheet.png`, `Character_Sheets/Environment_Plate_1.png`.

**Tony said:**

> [!quote] Tony, 2026-09-19 03:32 UTC (transcript line 6034)
> Okay, you're wrong about frame 5. He's actually on the front porch, so let's pause because I want to figure out why you keep determining him to be in the wrong spot. You just analyzed it, and you keep getting it wrong. You're saying on frame 5 his feet are still on the driveway, so that is not correct.

> [!quote] Tony, 2026-09-19 03:35 UTC (transcript line 6069)
> In okay the check function, tool, or Python script that you built needs to zoom in on each frame so it can see it as a full frame, not look at the whole storyboard as a whole. It needs to look at frame 1, understand what it is, look at frame 2, and compare them. If it has to place one on another and compare them like an onion screen, kind of like in real animation, do that. If you need to build a tool to do that, do that. You need to get this thing correct. I'm sick of asking you. Do I need to switch you to a higher model? Do you have a learning problem?

> [!quote] Tony, 2026-09-19 03:37 UTC (transcript line 6116, typed while the agent was still working)
> There's no need to use it on the storyboard you just built because you're just going to give me a canned response with the correct answer, because you already know the correct answer.

> [!quote] Tony, 2026-09-19 03:37 UTC (transcript line 6140, typed while the agent was still working)
> Why don't you do a version 6 of the storyboard that's correct with a better prompt, and then we could do the check?

**Changed next:** `check_subject_positions.py` gained `--save-panels` and `--onion-skin`; Blocking Plan and spec now name three ground surfaces (porch concrete, step tile, driveway gravel).

**Worked?:** No (attempt 6).

## storyboard, attempt 6

**Shown:** `Storyboard_v6.png` plus the onion-skin overlay `onion_4_5.png`, sent 03:46 UTC (the overlay was in `/tmp/v6_panels/` and no longer exists).

**Prompt sent:** `Data/Storyboard_Prompt_v6.md`. Attached: `Character_Sheets/Delivery_Driver_Character_Sheet.png`, `Character_Sheets/Kangaroo_Character_Sheet.png`, `Character_Sheets/Environment_Plate_1.png`.

**Tony said:**

> [!quote] Tony, 2026-09-19 03:46 UTC (transcript line 6347)
> Okay, in order to look at it, I need to see it, so show it to me.

> [!quote] Tony, 2026-09-19 03:49 UTC (transcript line 6363)
> Okay, there are even more inconsistencies. He's larger, way larger. The food disappears in frames 4, 5, and 6. 
>
> And in frame 5, he always moves back up and then back down, so just pause. Don't do anything yet. 
>
> We're just going to go through brainstorming mode right now, so we're going to iterate, and I'm just going to ask you questions. 
>
> Show me what the environment sheet looks like.

**Changed next:** Tony paused the storyboards and turned to the environment sheet as the root cause.

**Worked?:** No. The storyboard track was dropped: the handoff says v1-v6 all reference the flawed plate, and the final video was made without a storyboard (`Data/Generation_Log.json`).

## video.establishing_test, attempt 1

**Shown:** `Data/Seedance_v1_Establishing_Test.mp4`, sent 2026-09-20 01:10 UTC.

**Prompt sent:** Inline kie-cli Seedance 2 call (below): 5 s, 720p, first frame = `POV_Panel_Final_Tony_Edit` (clean, unlabeled).

> [!note]- Prompt sent: 2026-09-20 01:06 UTC, transcript line 8795, typed inline, never saved to a file; kept here verbatim
> Fixed wide-angle fisheye doorbell-camera shot, mounted at door height, mainstream 2018/2019-era Ring-style consumer hardware -- modest dynamic range, no artificial sharpening. Empty regional-Australian suburban-fringe front yard at midday, clear dry sunlight, hard shadows. Nothing moves except subtle natural ambient motion: a light breeze stirs the native garden plantings and the Hills Hoist rotary clothesline, the hedge line sways almost imperceptibly. No people, no animals, no kangaroo. The parked older-model car sits stationary on the gravel driveway the entire time. Camera is completely static -- no pan, no tilt, no zoom, no reframing. Diegetic ambient sound only: light wind, distant bushland birds, no footsteps, no dialogue. - No dialogue, no spoken words, no voiceover, no music, no on-screen text, no logos, no captions, no people, no animals.

**Tony said:**

> [!quote] Tony, 2026-09-20 01:11 UTC (transcript line 8848)
> There's no kangaroo or delivery driver. Did you forget to add those assets as reference documents?

> [!quote] Tony, 2026-09-20 01:12 UTC (transcript line 8863, typed while the agent was still working)
> Okay, well, the environment looks fine. But run the real test.

**Changed next:** Ran the full driver-plus-kangaroo call; the first submission failed on kie.ai credits until Tony topped up.

**Worked?:** Yes. Marked approved in `Data/Generation_Log.json`.

## video.full_action, attempt 1

**Shown:** `Data/Seedance_v1_Full_Action_Test.mp4`, sent 01:20 UTC.

**Prompt sent:** Inline kie-cli Seedance 2 call (below): 14 s, 720p; `@Image1` `POV_Panel_Final_Tony_Edit`, `@Image2` driver sheet, `@Image3` kangaroo sheet. The identical earlier submission (transcript line 8862) failed on credits.

> [!note]- Prompt sent: 2026-09-20 01:14 UTC, transcript line 8885, typed inline, never saved to a file; kept here verbatim
> Reference roles: @Image1 = the fixed doorbell-camera environment plate (porch, steps, driveway, car, lawn, hedge line, letterbox, clothesline, water tank -- this exact geography, never redrawn). @Image2 = the delivery driver character sheet -- his exact face, build, and clothing, carrying a plain insulated delivery bag. @Image3 = the kangaroo character sheet -- a grey kangaroo (Macropus giganteus), realistic wild proportions, standing roughly chest/shoulder height on the driver, never house-cat/dog-sized, never larger than the driver.
>
> Fixed wide-angle fisheye doorbell-camera shot, mounted at door height, mainstream 2018/2019-era Ring-style consumer hardware, modest dynamic range, no artificial sharpening. Camera is completely static the entire clip -- no pan, no tilt, no zoom, no reframing. Clear dry midday sunlight, hard shadows, regional-Australian suburban-fringe front yard, matching @Image1 exactly throughout -- same doormat, steps, house, hedge line, letterbox position, and the driver's own parked older-model car stationary at the driveway/screen-right edge the entire time.
>
> Action timeline:
> [00:00-00:02] The delivery driver (@Image2) crosses the porch from screen-right, carrying the closed insulated delivery bag by its handle, approaching the doormat centered below the camera.
> [00:02-00:04] The driver bends slightly, opens the bag with one hand, takes out just the food item/container with the other, and places it on the doormat -- the bag itself stays gripped in his hand the whole time, never set down.
> [00:04-00:06] The driver straightens up, turns, and starts back down the porch steps toward screen-right, bag still in hand, only the food item left behind on the mat.
> [00:06-00:08] As the driver finishes descending the stairs and steps onto the light gray gravel driveway surface beside the parked car, a grey kangaroo (@Image3) hops into frame from the garden bed on screen-left, landing at the edge of the lawn -- clearly separated from the letterbox, not overlapping or touching it.
> [00:08-00:11] The driver notices the kangaroo mid-stride and freezes, half-turning to look with a small stutter-step, feet still on the gravel driveway surface beside the car. The kangaroo pauses too, upright, weight settling back on its haunches and tail, ears rotating toward the driver -- both hold a real, quiet mutual-watch moment, not a scripted standoff.
> [00:11-00:14] The kangaroo continues on its own path across the lawn toward the rear/side of the yard, still visible as it moves; the driver resumes walking along the gravel toward the car and begins exiting screen-right, bag still in hand -- it is never set down anywhere in this shot.
>
> Diegetic sound only: footsteps on porch concrete then gravel, faint doorbell-camera microphone quality, ambient light wind and distant bushland birds, the kangaroo's paws/thump on the lawn, the driver's quiet surprised exhale when he notices the kangaroo. - No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text, no logos, no captions, no duplicate drivers, no duplicate kangaroos, no other people or animals, no dog.

**Tony said:**

> [!quote] Tony, 2026-09-20 01:14 UTC (transcript line 8882)
> Try again. I've got auto-refresh credits, and now I have 1,290.

> [!quote] Tony, 2026-09-20 01:22 UTC (transcript line 8967)
> That did extremely well. I'm going to give that a grade A. Let's lock in that recipe or that process for a successful video, which means everything we did to keep the environment sheet consistent, all of that locking in.

**Changed next:** `Data/Report_Card.md` and `Data/Generation_Log.json` written; the recipe was locked into Seedance-Prompting-Guide.

**Worked?:** Final, Grade A (`Data/Report_Card.md`). One soft note: the kangaroo holds still for about 2 s in the watch beat.
