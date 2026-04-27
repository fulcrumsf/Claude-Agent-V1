---
description: Character sheet creation workflow. Run this when a video has recurring characters, animals, or subjects that must look visually consistent across all scenes. Generates multi-view reference images using Nano Banana 2, then sets up element references for use in Kling 3.0 and reference images for other models.
---

# Character Sheet Workflow

Run this workflow for EACH recurring character, animal, or subject before storyboarding begins. A "character" is anything that must look EXACTLY the same across multiple scenes — a specific animal, a human character, an object with a specific design.

## Step 1: Collect Character Details

For each recurring character, ask the user:

---

For character **[Name/Label]**, please describe:

1. **Species / Type** — What is it? (e.g., "adult male jaguar", "young woman", "robotic drone")
2. **Key Physical Traits** — Distinctive physical features that MUST be consistent (markings, colors, scars, size, shape). Be as specific as possible.
3. **Outfit / Gear** (if applicable) — Specific clothing, accessories, or equipment. Include colors, materials, style.
4. **Mood / Expression Default** — What is the character's default demeanor? (e.g., "alert and watchful", "calm and confident", "curious")
5. **Any reference images?** — Do you have any existing photos or images of this character/animal I should use as input?

---

Wait for the user to respond before generating anything.

## Step 2: Build the Character Sheet Prompt

Using the user's answers, construct a Nano Banana 2 prompt that generates a **multi-view character sheet** — showing the character from front, 3/4 angle, side, and a close-up of distinctive features.

### Character Sheet Prompt Template

```
Character reference sheet — [CHARACTER NAME/LABEL]. Multiple views on a clean neutral dark background:
Top row (left to right): full-body front view, full-body 3/4 angle, full-body side profile.
Bottom row (left to right): close-up of face/head showing key markings, close-up of distinctive feature [SPECIFY], detail shot of [outfit/markings/texture].

[FULL PHYSICAL DESCRIPTION — include every detail the user provided: species, size, coloring, markings, outfit, accessories. Be exhaustive. This description will be copy-pasted into every future scene prompt.]

Consistent lighting across all views: soft studio-style diffused light, neutral grey or dark background, no shadows obscuring details. Scientific illustration precision combined with [CHANNEL VISUAL STYLE — e.g., "cinematic wildlife documentary aesthetic" for Anomalous Wild].

Output style: clear, high-fidelity reference sheet, each view cleanly separated. Not an action shot — this is a reference document.
```

### Example (Anomalous Wild — Wildlife Subject)

```
Character reference sheet — MANTIS SHRIMP ALPHA. Multiple views on a clean dark navy background:
Top row: full-body front view showing full length, full-body 3/4 angle showing shell depth, side profile showing full appendage length.
Bottom row: extreme close-up of compound eyes (showing the rainbow iridescent banding), close-up of striking appendages (showing the raptorial clubs), detail of dorsal shell coloring.

Adult peacock mantis shrimp (Odontodactylus scyllarus), approximately 18cm length. Vivid iridescent shell displaying electric teal on dorsal surface, deep orange on lateral segments, cobalt blue on the rostral plate. Distinctive rainbow-banded compound eyes mounted on independent stalks. Striking appendages (raptorial clubs) visible and articulated. No injuries or unusual markings. Body in neutral resting posture.

Consistent neutral dark navy background, soft even lighting from above, no harsh shadows, scientific reference quality. Cinematic documentary aesthetic — National Geographic precision.
```

## Step 3: Generate the Character Sheet

Run the Nano Banana 2 API call via `run_command`:

```bash
python tools/nano_banana_gen.py "[FULL CHARACTER SHEET PROMPT]" "references/characters/[CHARACTER_LABEL]/character_sheet.jpg" --aspect_ratio "16:9" --resolution "2K"
```

If the tool script does not exist yet, use the kie.ai API directly:

```python
# POST to https://api.kie.ai/api/v1/jobs/createTask
{
  "model": "nano-banana-2",
  "input": {
    "prompt": "[FULL CHARACTER SHEET PROMPT]",
    "aspect_ratio": "16:9",
    "resolution": "2K",
    "output_format": "jpg",
    "image_input": []  # Add user-provided reference URLs here if any
  }
}
```

Save output to: `references/characters/[CHARACTER_LABEL]/character_sheet.jpg`

## Step 4: Present and Confirm with User

Show the generated character sheet to the user and ask:

---

Here is the character sheet for **[CHARACTER NAME]**.

- Does this match your vision?
- Are there any features that need to be adjusted (colors, markings, outfit details)?
- Should I regenerate with any changes?

If confirmed → proceed to Step 5.
If changes needed → adjust the prompt and regenerate. Do not proceed until user approves.

---

## Step 5: Extract Reference Frames

Once the character sheet is approved, extract 3–4 individual reference frames from it for use as element references. These should be:

1. **Full body front view** — crop from character sheet
2. **3/4 angle view** — crop from character sheet
3. **Close-up of distinctive feature** — crop from character sheet
4. **Side profile** (if available)

Save each crop to: `references/characters/[CHARACTER_LABEL]/ref_[1-4].jpg`

If the character sheet tool returns a single composite image, inform the user:
*"To extract individual reference frames for Kling element references, I'll need to crop the character sheet. You can also provide separate images of the character from different angles if you have them — 2–4 images work best."*

## Step 6: Upload Reference Images to kie.ai

Upload each reference frame to kie.ai's file hosting to get public URLs:

```bash
python tools/kie_file_upload.py "references/characters/[CHARACTER_LABEL]/ref_1.jpg"
# Returns: https://tempfileb.aiquickdraw.com/kieai/...
```

Store all returned URLs in the character record below.

## Step 7: Create Character Record

Save a character record file at `references/characters/[CHARACTER_LABEL]/character.md`:

```markdown
# Character: [CHARACTER NAME/LABEL]

## Canonical Description
[COPY THE FULL PHYSICAL DESCRIPTION HERE — this exact text must be used in EVERY scene prompt that features this character]

## Reference Images
- ref_1.jpg — [what angle/view this is]
- ref_2.jpg — [what angle/view this is]
- ref_3.jpg — [what angle/view this is]
- ref_4.jpg — [what angle/view this is]

## kie.ai Hosted URLs (for element references)
- ref_1: [URL]
- ref_2: [URL]
- ref_3: [URL]
- ref_4: [URL]

## Kling 3.0 Element Config
Use this block in any Kling 3.0 API call that features this character:

```json
{
  "name": "[CHARACTER_LABEL]",
  "description": "[one-line description, e.g., 'adult peacock mantis shrimp with iridescent teal and orange shell']",
  "element_input_urls": [
    "[ref_1 URL]",
    "[ref_2 URL]",
    "[ref_3 URL]"
  ]
}
```

## Model Usage Guide
| Model | How to use this character |
|---|---|
| Kling 3.0 | Use kling_elements block above + @[CHARACTER_LABEL] in every prompt |
| Kling 2.6 I2V | Use ref_1 as image_url, include [CANONICAL DESCRIPTION, action] bracket syntax |
| Veo 3.1 REFERENCE_2_VIDEO | Use ref_1–3 as imageUrls (max 3), include action in prompt |
| Veo 3.1 TEXT_2_VIDEO | Paste CANONICAL DESCRIPTION into every prompt |
| Wan 2.6 I2V | Use ref_1 as image_url, include full CANONICAL DESCRIPTION in prompt |
| Sora 2 I2V | Use ref_1 as image_url, include full CANONICAL DESCRIPTION in prompt |

## Character Sheet
![Character Sheet](character_sheet.jpg)

## Created
[Date]
```

## Step 8: Confirm and Hand Off

Tell the user:

---

**Character sheet complete for [CHARACTER NAME].**

- Character record saved to `references/characters/[CHARACTER_LABEL]/`
- Reference images ready for Kling element references
- Canonical description locked in — I'll use this in every scene

[If more characters remain]: *"Let's build the next character sheet. What's the next character?"*

[If all characters are done]: *"All character sheets are complete. Ready to move to the video creation workflow. Let's start the script."*

---

## Notes

- Always complete ALL character sheets before beginning any scripting or storyboarding.
- If the user only has 1 reference image of a real animal (e.g., a photo they found), use it as `image_input` in the Nano Banana 2 call — the model will generate additional angles from it.
- The CANONICAL DESCRIPTION in the character record is the single source of truth. Never paraphrase or shorten it when writing scene prompts.
