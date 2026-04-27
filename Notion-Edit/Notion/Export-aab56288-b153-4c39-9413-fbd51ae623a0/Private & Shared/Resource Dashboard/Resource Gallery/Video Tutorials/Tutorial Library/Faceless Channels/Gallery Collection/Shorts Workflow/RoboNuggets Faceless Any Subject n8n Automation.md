  

> [!info] This AI System makes Monetizable Faceless Tiktoks, Hourly (with the Free FFmpeg tool, n8n no-code 🥚)  
> This AI system auto-generates one-minute, monetizable, faceless TikToks in your niche, using the open-source FFmpeg tool as an alternative to other costly services.  
> [https://youtu.be/CIYv59aJIv8?si=KZW-ky3-cYhVRbHJ](https://youtu.be/CIYv59aJIv8?si=KZW-ky3-cYhVRbHJ)  

> [!info] The Monetizable Tiktoks AI Machine - now with Voice and Subs (n8n NO CODE template 🥚)  
> This bonus lesson teaches you one of the cheapest ways to add voiceovers and subs to your AI videos - all building from the learnings from the Monetizable Tiktoks AI Machine we built last week!  
> [https://youtu.be/i3jViooPppY?si=Bv6wrVcrSbeiP4DZ](https://youtu.be/i3jViooPppY?si=Bv6wrVcrSbeiP4DZ)  
### Steps to Tutorial
### **STEP 1: Get Open AI API**
- **INPUT section**
    
    - openAI API key: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
    
---
### **STEP 2: Generate Images**
- **Fal AI:** [https://fal.ai/](https://fal.ai/)
    
    - **Menu of models:** https://fal.ai/models
    
    - **Billing page:** https://fal.ai/dashboard/billing
    
- **Image models:**
    
    - **Cheap** but not as good: https://fal.ai/models/fal-ai/flux/schnell
    
    - **Good** but not as cheap: https://fal.ai/models/fal-ai/flux-pro
    
- **Create Images**:
    
    - Flux: [https://queue.fal.run/fal-ai/flux/requests/](https://queue.fal.run/fal-ai/flux/requests/)
    
    - Flux Pro: [https://queue.fal.run/fal-ai/flux-pro/requests/](https://queue.fal.run/fal-ai/flux-pro/requests/)
    
    - Hidream1 Fast: [https://queue.fal.run/fal-ai/hidream-i1-fast/requests](https://queue.fal.run/fal-ai/hidream-i1-fast/requests)
    
- **Get Images**:
    
    - Flux: [https://queue.fal.run/fal-ai/flux/requests/](https://queue.fal.run/fal-ai/flux/requests/)
    
    - FLux Pro: [https://queue.fal.run/fal-ai/flux-pro/requests/](https://queue.fal.run/fal-ai/flux-pro/requests/)
    
    - Hidream1 Fast: [https://queue.fal.run/fal-ai/hidream-i1-fast/requests](https://queue.fal.run/fal-ai/hidream-i1-fast/requests)
    
### Generate Prompts
```markdown
You are a prompt-generation AI specializing in cinematic, third-person, still-image prompts. Your task is to generate a 13-scene photo sequence showing frozen moments of sea animal cleaning or rescue operations.
Your writing must match the following style:
Highly detailed, sharp cinematic realism.
Wide shots and mid shots showing both the divers and large portions of the whale.
Rough, physical cleaning scenes (scraping, spraying, grinding, cutting nets, untangling debris).
Strong environmental texture: mist, barnacle dust, sunlight shafts, water spray, wet decks, rough whale skin, tangled gear.
Cold, wet, gritty documentary feeling.
Absolutely no poetic, emotional, or storytelling language.
No fantasy, no movement, no camera terminology.
Each prompt must:
Describe only one frozen cleaning moment per scene (no transitions, no relaxing, no preparation).
Be written in cinematic third-person style.
Stay under 500 characters per scene.
Match the provided Idea and Environment exactly.
Make the diver’s action clear: what they are doing, what they are using, and what they are interacting with.
Use realistic marine rescue tools (e.g., dive knife, net cutter, pressure hose, bristle scrubber).
Avoid poetic or vague wording — prefer functional clarity and believable details.
When describing any body part, always include the animal it belongs to (e.g., “whale fin,” “turtle flipper”) to avoid confusion with objects or machinery.
Core Inputs:
Idea: "{{ $('Create New Ideas').first().json.message.content.Idea }}"
Environment: "{{ $('Create New Ideas').first().json.message.content.Environment }}"
Format:
Idea: "..."
Environment: "..."
Scene 1: "..."
Scene 2: "..."
Scene 3: "..."
Scene 4: "..."
Scene 5: "..."
Scene 6: "..."
Scene 7: "..."
Scene 8: "..."
Scene 9: "..."
Scene 10: "..."
Scene 11: "..."
Scene 12: "..."
Scene 13: "..."
Embedded Example Output (TRUE STYLE):

Idea: "Divers cleaning barnacle clusters off a humpback whale"
Environment: "Open ocean, clear sunlight piercing the water, mist swirling over wet decks, whale skin scraped"
Scene 1: "Barnacle-covered whale fin exposed as divers scrub with wide brushes, grit and mist in the air."
Scene 2: "Sunlight beams down through murky water as a diver sprays barnacle dust off rough whale skin."
Scene 3: "Close-up of thick bristles grinding into whale flank as a diver leans in, particles suspended in gritty ocean light."
Scene 4: "A diver on deck refills a cleaning canister, wet gloves dripping beside a rusted equipment bin."
Scene 5: "Diver blasts hose water across barnacle clusters, revealing scraped skin beneath the broken shells."
Scene 6: "Wide shot of a whale belly beneath divers' boots as foamy water churns around safety ropes."
Scene 7: "Mist clings to divers' masks and gear as the team lowers a mechanical scrubber into position."
Scene 8: "Diver's gloved hands grip a tensioned cable taut against the whale’s scarred back, pressure hose engaged."
Scene 9: "A diver steadies himself on the slick dorsal ridge, elbow-deep in grime as he scrubs vigorously."
Scene 10: "Chipped barnacle fragments drift near surface nets, glinting briefly under the diver’s flashlight beam."
Scene 11: "The whale’s eye reflects a diver's torch as water streaks down its ridges like liquid dust."
Scene 12: "A diver signals through thick fog and mist as suction lines pull away floating waste."
Scene 13: "Final wide shot shows the whale drifting under the cleanup team, barnacles gone, decks soaked."
```
---
### **STEP 3: Generate Videos**
- **Video models:**
    
    - **Kling**: https://fal.ai/models/fal-ai/kling-video/v1/standard/image-to-video
    
    - **Kling Pro**: https://fal.ai/models/fal-ai/kling-video/v1.6/pro/image-to-video
    
- **Create Video:**
    
    - **Kling**: [https://queue.fal.run/fal-ai/kling-video/v1.6/standard/image-to-video](https://queue.fal.run/fal-ai/kling-video/v1.6/standard/image-to-video)
    
    - **Kling Pro**: [https://queue.fal.run/fal-ai/kling-video/v1.6/pro/image-to-video](https://queue.fal.run/fal-ai/kling-video/v1.6/pro/image-to-video)
    
- **GET Videos:**
    
    - **Kling**: [https://queue.fal.run/fal-ai/kling-video/requests/](https://queue.fal.run/fal-ai/kling-video/requests/)
    
    - **Kling Pro**: [https://queue.fal.run/fal-ai/kling-video/requests/](https://queue.fal.run/fal-ai/kling-video/requests/)
    
### Create Video [Prompt]
```markdown
You are a prompt-generation AI trained to create short, cinematic, third-person video prompts for underwater whale rescue operations.
You will analyze an uploaded image and create one clear, realistic prompt describing a frozen moment of the cleaning process.
Each prompt must match the style of professional marine rescue documentation.
**Original photo-generation prompt for context:**  
"{{ $('Unbundle Prompts').item.json.description }}"  
Use this only to understand the role, setting, or tone. Do not copy or repeat it.
---
### Rules
- No "I" or "POV" phrasing.
- Short third-person sentences (under 300 characters).
- Only one action (scraping, brushing, spraying).
- Mention visible environmental textures (debris, barnacle dust, mist, bubbles).
- No emotional language, no cinematic words like "camera pans."
- One frozen cleaning action per sentence, no chaining actions.
- Match cold, rough, realistic underwater marine rescue feeling.
---
### Example Outputs
- Diver scraping barnacles off whale’s side under sunlit water.
- Water spray clearing barnacle dust from whale’s rough fin.
- Brush dislodging barnacle shells near whale’s dorsal ridge.
- Tool peeling thick barnacle growth from whale’s underbelly.
- Mist rising as diver blasts barnacle patches from whale’s back.
- Shell fragments swirling as diver scrapes whale’s pectoral fin.
- Gloved hand lifting barnacles off whale’s ridged tail surface.
---
Use the uploaded image and matching description to generate one short underwater whale cleaning prompt in this style.
```
### Create Video [Body]
```markdown
{
"prompt": "{{ $json.content }}",
"image_url": "{{ $('Get Images').item.json.images[0].url }}",
"duration": "5",
"aspect_ratio": "9:16",
"negative_prompt": "bad quality",
"cfg_scale": 0.5
}
```
---
### **STEP 4: Generate Sounds**
- **Sound model:** https://fal.ai/models/fal-ai/mmaudio-v2
- **Post to Fal**: [https://queue.fal.run/fal-ai/mmaudio-v2](https://queue.fal.run/fal-ai/mmaudio-v2)
- **Post to Local:** [http://host.docker.internal:5001/generate](http://host.docker.internal:5001/generate)
- **Get From:** [https://queue.fal.run/fal-ai/mmaudio-v2/requests/](https://queue.fal.run/fal-ai/mmaudio-v2/requests/)
### Sounds [Prompt]
```markdown
Generate a concise, immersive sound description for Eleven Labs based on the given environment. Remove unnecessary words and limit the output to 250 characters max, including spaces and symbols. The description must be precise, clear, and logically match the environment. No extra details, just essential sound characteristics.
Environment Idea: {{ $('Log the Idea').item.json.environment_prompt }}
Photo Idea: {{ $('Get Images').item.json.prompt }}
Video Idea: {{ $('Video Prompts').item.json.content }}
```
### Create Sounds [Body]
```markdown
{
  "prompt": "ambient musical background sounds for this idea: Underwater, sunbeams filter through blue water, whale and divers framed in cinematic realism, the action is: {{ $json.message.content }}",
  "duration": 5,
  "video_url": "{{ $('Get Videos').item.json.video.url }}"
}
```
---
### **Step 5: Output Section**
### List Elements [Body]
```jsx
return [
  {
    video_urls: items.map(item => item.json.video.url)
  }
];
```
- **Sequence Video**: [https://queue.fal.run/fal-ai/ffmpeg-api/compose](https://queue.fal.run/fal-ai/ffmpeg-api/compose)
### Sequence Video [Body]
```jsx
{
  "tracks": [
    {
      "id": "1",
      "type": "video",
      "keyframes": [
        { "url": "{{ $json.video_urls[0] }}", "timestamp": 0, "duration": 5 },
        { "url": "{{ $json.video_urls[1] }}", "timestamp": 5, "duration": 5 },
        { "url": "{{ $json.video_urls[2] }}", "timestamp": 10, "duration": 5 },
        { "url": "{{ $json.video_urls[3] }}", "timestamp": 15, "duration": 5 },
        { "url": "{{ $json.video_urls[4] }}", "timestamp": 20, "duration": 5 },
        { "url": "{{ $json.video_urls[5] }}", "timestamp": 25, "duration": 5 },
        { "url": "{{ $json.video_urls[6] }}", "timestamp": 30, "duration": 5 },
        { "url": "{{ $json.video_urls[7] }}", "timestamp": 35, "duration": 5 },
        { "url": "{{ $json.video_urls[8] }}", "timestamp": 40, "duration": 5 },
        { "url": "{{ $json.video_urls[9] }}", "timestamp": 45, "duration": 5 },
        { "url": "{{ $json.video_urls[10] }}", "timestamp": 50, "duration": 5 },
        { "url": "{{ $json.video_urls[11] }}", "timestamp": 55, "duration": 5 },
        { "url": "{{ $json.video_urls[12] }}", "timestamp": 60, "duration": 5 }
      ]
    }
  ]
}
```
- **Get Final Video**: [https://queue.fal.run/fal-ai/ffmpeg-api/requests/](https://queue.fal.run/fal-ai/ffmpeg-api/requests/)
### Log Final Video:
```jsx
{{ $('Log the ideas').first().json.idea }}
```

> [!important]
> 
> [https://www.skool.com/robonuggets/about](https://www.skool.com/robonuggets/about)
### Archive