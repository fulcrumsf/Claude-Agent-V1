---
Status: In progress
Priority: High
Task type:
  - Automation
Effort level: Large
"Priority #": P1
---
### Task description
Here is your **"Bird's Eye View" Construction Plan**. We will treat each bullet point as a separate building phase.
### **Phase 1: The Master Workflow (The Producer)**
- **Goal:** The central command center. It doesn't "do" the creative work; it hires the right teams (sub-workflows) to do it.
    
    1. **Manual Trigger:** You click a button to start.
    
    1. **Cast Lookup (Google Sheet):** You input a "Topic" and "Avatar Name." It looks up that avatar's personality, voice ID, and style from your database.
    
    1. **The Router (Traffic Cop):**
        
        - If Style = "Vlog", it sends data to the **Vlog/Hedra** path.
        
        - If Style = "Standard", it sends data to the **Green Screen** path.
        
    
    1. **Execute Sub-Workflow A:** It hires the Writers Room to generate the script and visual plan.
    
    1. **Execute Sub-Workflow B:** It hires the Talent to create the Green Screen performance.
    
    1. **Execute Sub-Workflow C:** It hires the B-Roll Unit to make the background videos.
    
    1. **Execute Sub-Workflow D:** It hires the Editor to stitch it all together.
    
---
### **Phase 2: Sub-Workflow A (The Writers Room)**
- **Goal:** Turn a niche topic into a polished script and a visual plan.
    
    1. **Trend Hunter:** Finds a specific, viral story idea based on your niche.
    
    1. **The Gatekeeper:** Approves or rejects the idea to ensure quality.
    
    1. **The Hook Master:** Writes a 3-second attention-grabbing intro.
    
    1. **The Architect:** Breaks the video into 15-second "beats" or chapters.
    
    1. **Lead Writer:** Writes the full script in the requested persona (e.g., "The Neon Naturalist").
    
    1. **Red Pen:** Polishes the text to remove "AI fluff."
    
    1. **The Director:** Reads the final script and creates a **Visual Manifest** (a list of scenes with visual prompts for the B-roll team).
    
---
### **Phase 3: Sub-Workflow B (The Talent)**
- **Goal:** Create the "Host" video (Green Screen).
    
    1. **Audio Gen (ElevenLabs):** Converts the script text into an MP3 file using the specific Voice ID.
    
    1. **Image Gen (Fal/Flux):** Generates the _static_ waist-up image of your host (Grandma/Axolotl) on a green background.
    
    1. **Animator (InfiniteTalk/SadTalker):** Combines the Audio + Image to make the character lip-sync.
    
    1. **Output:** Returns the URL of the "talking head" video.
    
---
### **Phase 4: Sub-Workflow C (The B-Roll Unit)**
- **Goal:** Create the scientific/cinematic backgrounds.
    
    1. **Manifest Reader:** Takes the **Visual Manifest** from the Director (Workflow A).
    
    1. **Loop/Splitter:** Goes through every single scene in the list.
    
    1. **Video Gen (Fal/Minimax/Kling):** Generates a 4-5 second clip for each scene based on the Director's prompt.
    
    1. **Output:** Returns a list of video URLs matched to each scene.
    
---
### **Phase 5: Sub-Workflow D (The Editor)**
- **Goal:** The final assembly.
    
    1. **Asset Gathering:** Takes the Green Screen Video (Workflow B) + B-Roll Clips (Workflow C).
    
    1. **Background Stitcher:** Merges all B-Roll clips into one long background video.
    
    1. **Compositor (FFmpeg):** Removes the green from the Host video and layers it on top of the background.
    
    1. **Captioner:** Generates subtitles and burns them onto the video.
    
    1. **Final Render:** Saves the final `.mp4` to Google Drive.
    
---
Your Next Step:
Start with Phase 2 (The Writers Room). It is the brain of the operation. Once that is outputting good scripts and visual manifests, the rest is just "rendering."
Ready to build Phase 2?
  
## Sub-tasks
- [ ]
- [ ]
- [ ]
  
## Supporting files
[](https://www.notion.soundefined)
[](https://www.notion.soundefined)
[](https://www.notion.soundefined)
---
# 📦 Project: Neon Parcel Viral Agency (AI Agent Swarm)
### **Objective**
To automate the creation of high-retention, non-generic video scripts using a chain of specialized AI Agents, each checking the work of the previous one.
### **The Agent Roster**
|   |   |   |   |   |
|---|---|---|---|---|
|**Node #**|**Agent Name**|**Role**|**Model (Provider)**|**Why?**|
|**01**|**The Trend Hunter**|Research & Ideation|**Perplexity (Sonar-Pro)**|Has live internet access to find _current_ curiosity gaps.|
|**02**|**The Gatekeeper**|Quality Control|**GPT-4o (OpenAI)**|High reasoning; acts as the "Mean Boss" to reject boring ideas.|
|**03**|**The Hook Master**|Intro Specialist|**Claude 3.5 Sonnet** (via OpenRouter)|Best at creative nuance; writes non-salesy, human hooks.|
|**04**|**The Architect**|Pacing & Structure|**Kimi k2-thinking** (via OpenRouter)|Excellent at complex formatting and long-chain logic for beat sheets.|
|**05**|**Lead Writer**|Script Drafting|**Gemini 1.5 Pro**|Conversational tone; free tier utilization.|
|**06**|**The Red Pen**|Editor & Polish|**GPT-4o Mini**|Fast, cheap efficient critique to remove "AI fluff."|
---
### **Agent Directives (System Prompts)**
### **1. Trend Hunter**

> "You are a viral trend analyst. Do not generate generic topics. Search for 'Curiosity Gaps' or 'Contrarian Truths' in the user's niche. Find something people believe is true, and pitch a video about why it's wrong. Output 3 distinct concepts."
### **2. The Gatekeeper**

> "You are a cynical YouTube producer. Review the 3 ideas. Reject any that feel 'AI-generated' or 'Boring.' Pick ONLY the one that triggers a strong emotional response (Fear, Greed, Surprise). If all are bad, output 'REJECT'."
### **3. The Hook Master**

> "Write 3 variations of the intro (first 5 seconds) for the approved idea. Use the 'Pattern Interrupt' technique (Visual, Audio, or Curiosity Hook). Do not use questions like 'Have you ever wondered?'—be direct."
### **4. The Architect**

> "Do not write the script. Write the Beat Sheet. Break the video into 15-second chunks. Assign a 'Retention Spike' (Joke, Reveal, Fast Cut) to every 30-second mark. Use a Sawtooth Narrative structure."
### **5. Lead Writer**

> "Write the full script based strictly on the Beat Sheet. Use a conversational, 5th-grade reading level. No corporate jargon. Use short, punchy sentences. Use the 'But/Therefore' rule for flow."
### **6. The Red Pen**

> "Scan the script for 'AI-isms' (delve, unleash, unlock, realm, game-changer). Delete them immediately. Rewrite any sentence longer than 15 words. Ensure the tone matches the 'Neon Parcel' cyberpunk aesthetic."
### **7 The Director**

> "Reads the polished script and generates the **Visual Manifest**.”
7.
---
### **Part 2: The n8n Workflow (JSON)**
**Instructions:**
1. Copy the code block below.
1. Open your n8n canvas.
1. Press `Ctrl+V` (or `Cmd+V`) to paste.
1. **Important:** You will see red warning triangles on the nodes. Click each node to select your specific Credentials (e.g., Connect your OpenAI account to Node 2, your Google Gemini account to Node 5, etc.).
## Define Niche Node
To explain your niche to the "Researcher" (Node 1), you don't just give it a keyword like _"Marketing."_ You must give it a **Persona** and a **Lens**.
In the JSON I provided previously, I included a node called **"Define Niche"** at the very start. This is the specific place where you "explain" your niche.
Here is the strategy for defining your niche so the Researcher finds _actual_ viral gaps instead of generic noise.
### **1. The "Define Niche" Node (Your Control Center)**
Locate the **"Define Niche"** node (Node #00 in the flow). Currently, it probably just has a single field `niche`.
You should expand this node to include **3 specific fields** to give the researcher full context.
- **Field 1:** `**niche_topic**` (Broad)
- **Field 2:** `**target_audience**` (Who are we talking to?)
- **Field 3:** `**contrarian_angle**` (The "Lens")
### **Example Setup for "Neon Parcel":**
- `**niche_topic**`: "AI Automation & No-Code workflows."
- `**target_audience**`: "Overwhelmed agency owners and freelancers who are tired of 'get rich quick' AI hype and want real engineering tutorials."
- `**contrarian_angle**`: "Most AI influencers are grifters selling generic prompts. We believe in building complex, robust backends. We value 'Building' over 'Prompting'."
### **2. How to Update the Node in n8n**
1. Double-click the **"Define Niche"** node (it's an `Edit Fields` or `Set` node).
1. Click **"Add Value"** to create the new fields listed above.
1. Fill them in with your specific details.
### **3. Updating the Researcher Prompt**
Now, you must update the **Trend Hunter (Perplexity)** node to _read_ these new details.
**Old Prompt:**

> "Search for trends regarding {{ $json.niche }}..."
**New "Deep Context" Prompt (Copy & Paste this into Node 1):**

> "You are a viral trend analyst for a channel focusing on {{ $('Define Niche').item.json.niche_topic }}.
> 
> Target Audience: {{ $('Define Niche').item.json.target_audience }}
> 
> Our Perspective: {{ $('Define Niche').item.json.contrarian_angle }}
> 
> Task: Search the live internet for 'Curiosity Gaps', 'new feature releases', or 'industry complaints' from the last 7 days.
> 
> Find something the 'Mainstream' is saying, and pitch a video about why they are wrong or missing the bigger picture.
> 
> **Output:** 3 distinct video concepts that fit our specific perspective."
### **Why this works better:**
If you just say "AI Automation," Perplexity will find "Top 10 ChatGPT Prompts."
By adding the Contrarian Angle ("We hate grifters"), Perplexity will instead find: "Why ChatGPT Wrappers are dying and what to build instead."
### **Quick JSON Update**
If you want to auto-update your "Define Niche" node to have these fields, copy this JSON and paste it over your existing "Define Niche" node:
JSON
# A - Workflow Writers
```jsx
{
  "nodes": [
    {
      "parameters": {},
      "id": "manual-trigger",
      "name": "Start Writers Room",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [
        -200,
        0
      ]
    },
    {
      "parameters": {
        "modelId": "sonar-pro",
        "messages": {
          "values": [
            {
              "content": "You are a viral researcher. Search for 'Curiosity Gaps' in: {{ $json.niche }}. Output 3 concepts."
            }
          ]
        }
      },
      "id": "trend-hunter",
      "name": "01 Trend Hunter",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [
        0,
        0
      ],
      "credentials": {
        "openAiApi": {
          "id": "YOUR_PERPLEXITY_CREDENTIAL_ID",
          "name": "Perplexity API"
        }
      }
    },
    {
      "parameters": {
        "modelId": "gpt-4o",
        "messages": {
          "values": [
            {
              "content": "You are the Gatekeeper. Pick the best idea from these 3: {{ $json.content }}. Output ONLY the approved idea."
            }
          ]
        }
      },
      "id": "gatekeeper",
      "name": "02 Gatekeeper",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [
        220,
        0
      ],
      "credentials": {
        "openAiApi": {
          "id": "YOUR_OPENAI_CREDENTIAL_ID",
          "name": "OpenAI Account"
        }
      }
    },
    {
      "parameters": {
        "modelId": "anthropic/claude-3.5-sonnet",
        "messages": {
          "values": [
            {
              "content": "Write 3 viral hooks for: {{ $json.content }}."
            }
          ]
        }
      },
      "id": "hook-master",
      "name": "03 Hook Master",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [
        440,
        0
      ],
      "credentials": {
        "openAiApi": {
          "id": "YOUR_OPENROUTER_CREDENTIAL_ID",
          "name": "OpenRouter"
        }
      }
    },
    {
      "parameters": {
        "modelId": "moonshotai/kimi-k2-thinking",
        "messages": {
          "values": [
            {
              "content": "Create a Beat Sheet for this idea and hooks. Split into 15s chunks."
            }
          ]
        }
      },
      "id": "architect",
      "name": "04 Architect",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [
        660,
        0
      ],
      "credentials": {
        "openAiApi": {
          "id": "YOUR_OPENROUTER_CREDENTIAL_ID",
          "name": "OpenRouter"
        }
      }
    },
    {
      "parameters": {
        "modelId": "gemini-1.5-pro",
        "messages": {
          "values": [
            {
              "content": "Write the full script based on this beat sheet: {{ $json.content }}."
            }
          ]
        }
      },
      "id": "lead-writer",
      "name": "05 Lead Writer",
      "type": "n8n-nodes-base.googleGemini",
      "typeVersion": 1,
      "position": [
        880,
        0
      ],
      "credentials": {
        "googlePalmApi": {
          "id": "YOUR_GEMINI_CREDENTIAL_ID",
          "name": "Google Gemini"
        }
      }
    },
    {
      "parameters": {
        "modelId": "gpt-4o-mini",
        "messages": {
          "values": [
            {
              "content": "Polish this script. Remove AI fluff. Output ONLY the final spoken text."
            }
          ]
        }
      },
      "id": "red-pen",
      "name": "06 Red Pen",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [
        1100,
        0
      ],
      "credentials": {
        "openAiApi": {
          "id": "YOUR_OPENAI_CREDENTIAL_ID",
          "name": "OpenAI Account"
        }
      }
    },
    {
      "parameters": {
        "modelId": "gpt-4o",
        "messages": {
          "values": [
            {
              "content": "You are The Director. \n\n**Input Script:** {{ $json.content }}\n\n**Task:**\n1. Split the script into scenes (every 1-2 sentences).\n2. For each scene, write a `visual_prompt` for an AI video generator. Describe the lighting, camera angle, and subject.\n3. Output a valid JSON Object with this structure:\n\n```json\n{\n  \"final_script\": \"(The full text)\",\n  \"manifest\": [\n    {\n      \"scene_number\": 1,\n      \"text_segment\": \"(Text for this scene)\",\n      \"visual_prompt\": \"(The prompt)\"\n    }\n  ]\n}```\n\nOutput ONLY the JSON."
            }
          ]
        },
        "jsonOutput": true
      },
      "id": "the-director",
      "name": "07 The Director",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [
        1320,
        0
      ],
      "credentials": {
        "openAiApi": {
          "id": "YOUR_OPENAI_CREDENTIAL_ID",
          "name": "OpenAI Account"
        }
      }
    }
  ],
  "connections": {
    "Start Writers Room": {
      "main": [
        [
          {
            "node": "01 Trend Hunter",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "01 Trend Hunter": {
      "main": [
        [
          {
            "node": "02 Gatekeeper",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "02 Gatekeeper": {
      "main": [
        [
          {
            "node": "03 Hook Master",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "03 Hook Master": {
      "main": [
        [
          {
            "node": "04 Architect",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "04 Architect": {
      "main": [
        [
          {
            "node": "05 Lead Writer",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "05 Lead Writer": {
      "main": [
        [
          {
            "node": "06 Red Pen",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "06 Red Pen": {
      "main": [
        [
          {
            "node": "07 The Director",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```
# A-Niches
This is a smart addition. "Blue Collar Animals" and "Animal Olympics" are huge viral trends (e.g., the "Cat doing construction" or "Fat Bear Olympics" memes).
Here is your **Finalized "Network Roster"** of 8 Shows.
- **Shows 1–5:** The Core Niches (Facts/Heartwarming/Compilations).
- **Shows 6–8:** The "Brain Dump" Derivatives (Grandma/Pixar/True Crime).
I have formatted these strictly as **Niche Definitions** (Topic, Audience, Angle) so you can paste them directly into your "Define Context" nodes later.
---
### **The Viral Core (Shows 1–5)**
### **Show 1: The "Neon Naturalist" (Strange Facts)**
- `**niche_topic**`: `Evolutionary Oddities & Bizarre Biology`
- `**target_audience**`: `Curious Gen Z & Millennials (18-35). Fans of "Casual Geographic" or "TierZoo".`
- `**contrarian_angle**`: `"Don't just list facts. Frame evolution as a 'Software Update' that went wrong. Focus on the logic behind the weirdness (e.g., 'Why nature nerfed the sloth')."`
### **Show 2: "The Dodo" Remix (Heartwarming)**
- `**niche_topic**`: `Unlikely Friendships & Hero Journeys`
- `**target_audience**`: `Broad Appeal (25-65). People looking for a 'Faith in Humanity' dopamine hit.`
- `**contrarian_angle**`: `"Focus on the 'Emotional Utility' of the bond. A bear and wolf don't hunt together because it's cute; they do it because they cracked a survival code. Frame it as a strategic alliance."`
### **Show 3: The "Surreal Olympics" (Compilations)**
- `**niche_topic**`: `Anthropomorphic Activities (Blue Collar & Sports)`
- `**target_audience**`: `Viral/Meme Crowd (TikTok/Shorts). Visual-first viewers who watch without sound.`
- `**contrarian_angle**`: `"Hyper-Real Surrealism. It shouldn't look like a cartoon; it should look like a GoPro strapped to a horse diving into a pool. The humor comes from the gritty realism of the impossible."`
### **Show 4: "Sleepy Time Zoo" (ASMR / Cozy)**
- `**niche_topic**`: `Animal ASMR & Relaxation`
- `**target_audience**`: `Insomniacs and people needing background visuals for studying.`
- `**contrarian_angle**`: `"Zero narration. 100% Sound Design. Rain on a Capybara's back. A cat purring in 8D audio. The 'Angle' is purely sensory texture."`
### **Show 5: "History's Pets" (Time Travel)**
- `**niche_topic**`: `Animals in Historical Contexts`
- `**target_audience**`: `History Buffs & Trivia Nerds.`
- `**contrarian_angle**`: `"The 'Forrest Gump' of animals. Show a pigeon delivering a message in WWI, but frame it from the pigeon's perspective. 'The secret agents of history'."`
---
### **The "Brain Dump" Derivatives (Shows 6–8)**
### **Show 6: Grandma's Vlogs (The Influencer)**
- `**niche_topic**`: `Absurdist Pet Lifestyle Vlogging`
- `**target_audience**`: `Short Attention Span Scrollers. Fans of 'Florida Man' energy.`
- `**contrarian_angle**`: `"Normalize the Absurd. Grandma never acknowledges that her 'dog' is a 500lb Grizzly Bear. The comedy relies entirely on her nonchalance vs. the viewer's panic."`
### **Show 7: "Little Science" (Pixar Style)**
- `**niche_topic**`: `Kids Science & Developmental Biology`
- `**target_audience**`: `Kids (6-12) & Homeschool Parents.`
- `**contrarian_angle**`: `"Superpower Training Montage. Don't explain 'limb regeneration' as a medical process; explain it like a superhero unlocking a new ability. Use bright, high-saturation 3D animation."`
### **Show 8: "Wild Crimes" (True Crime Mockumentary)**
- `**niche_topic**`: `Noir Mystery & Animal Mischief`
- `**target_audience**`: `True Crime fans needing a palate cleanser.`
- `**contrarian_angle**`: `"High-Stakes Seriousness for Low-Stakes Crimes. Use 'Dateline NBC' pacing, grainy night-vision footage, and suspenseful music to describe a Raccoon stealing a sock. The contrast creates the comedy."`
---
### **Summary of Your "Master Switch"**
When you eventually build the Master Workflow, your **Router Node** will simply look like this:
|   |   |
|---|---|
|**IF Style ==**|**THEN Route To**|
|**"Facts" / "History"**|Green Screen Sub-Workflow (Writer + Host)|
|**"Heartwarming" / "True Crime"**|Narrative Sub-Workflow (Writer + Voiceover + B-Roll)|
|**"Grandma"**|Vlog Sub-Workflow (Hedra/SadTalker Single Shot)|
|**"Pixar"**|Animation Sub-Workflow (Writer + 3D Generator)|
|**"Compilations"**|Visual Sub-Workflow (No Script, Just Prompts + Music)|