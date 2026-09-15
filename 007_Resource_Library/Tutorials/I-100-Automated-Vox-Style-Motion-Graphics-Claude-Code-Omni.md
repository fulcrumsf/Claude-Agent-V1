---
title: "I 100% Automated Vox-Style Motion Graphics (Claude Code + Omni)"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=TiycelzfzC0)

🌟 Want this exact system? Join the Syndicate 👇  
https://www.skool.com/acs-syndicate/about  
  
📌 I drop early updates here before anywhere else: https://t.me/koen\_agi  
  
📸 IG: https://www.instagram.com/koen.agi/  
  
1️⃣ Project Links:  
  
Drive link with files for the project: https://drive.google.com/drive/folders/1uCVp8Q8ZE98qwy2N4ClPpdbR55xl36UJ?usp=sharing  
Kie AI: https://kie.ai?ref=fd68b969aac43115412a0c5484f24113  
Elevenlabs: https://try.elevenlabs.io/t0v4praq5lct  
Framework Explained: https://www.youtube.com/@FRMWRKD-EXPLAINED  
  
\--  
  
2️⃣ System Build Prompt:  
  
I need a project local skill that will execute this each time, including an optional guidance prompt.  
\-Guidance prompt can include the story itself and the amount of chapters. Default is 1 chapter.  
\-The videos are for journalism about news and politics, the goal is an enticing story and video script based on current events. (If no event is provided, choose one based on what you believe to be best based on current events. Always do research for the story)  
\-A chapter is roughly 30 seconds. Can have multiple chapters by prompting how many. (Up to 4, for example “Generate a vox style animation video about the current state of the US economy, with 3 chapters”) The chapters should be coherent and create an understandable story if there are multiple.  
\-Roughly 30s is generated for a chapter (4-8 clips)  
\-30s of speech is generated first, then it is analyzed and distributed into groups for separate clips. PRIORITY is ALWAYS for the speech to line up with what’s being shown on screen. Use the API features like word level timestamps.  
\-The clips are generated using the context of the speech. The prompts of the clips include timestamps for that specific clips speech. (Ex. in a 6s clip, if “door” is said at 3s, that would be included in the video prompt) Ensure these specific timestamp prompts are for prominent events in the video that would genuinely improve the output of the video. Only do if necessary (ex, the clip is long and what’s on screen wouldn’t line up with what’s being said). Regardless, always line up parts of the speech script with the prompts for the images and videos to ensure it’s aligned with what’s on screen.  
\-Only generate in either 4s or 6s.  
\-The clips are generated with one of two models: Gemini Omni Flash and Seedance 2.0 Fast. Seedance 2.0 Fast is only used for clips of public figures. For Omni, input images are “references” only for the model. For Seedance 2.0 Fast, they are direct first frame inputs.  
\-Images for the video generation are always generated the same way: a style reference image is pre-made and put into the project files, and this is used as the input image for the GPT-2 Image model to generate the images which will be used for each ai generated video.  
\-If a clip in a chapter requires a public character: The image should always be generated with a black bar over the characters eyes. Also important: the character should not be generated close to the camera, they should always be off in the distance to not include too many details of their complexion. When generating the video, use Seedance 2.0 Fast model, and do not ever include the public figure’s name anywhere in the video prompt.  
\-Use the image and video prompt guidelines markdown files for the process of generating prompts to be used. (Always be aware of public figure tasks as mentioned earlier to avoid generation failures with videos) Clip prompts include vox-style context to remain consistent.  
\-Music is added on top at the end when all clips are combined using ffmpeg. (Song is chosen randomly if multiple)  
\-Use elevenlabs for voice and kie ai for images and video.  
\-Remove the first 0.25s off of every video before combining. Keep the audio from the clips in but at a low volume instead of muted, the clips include sound effects.  
API Docs:  
https://elevenlabs.io/docs/api-reference/introduction  
https://kie.ai/gemini-omni  
https://kie.ai/seedance-2-0  
https://kie.ai/gpt-image-2  
\-Install any dependencies needed automatically, ask clarifying questions until you are ready to build, and create a .env for any api keys  
  
\--  
  
  
00:00 Intro  
  
00:07 Example Video  
  
00:46 Intro  
  
02:02 Costs  
  
02:34 Claude Build (1)  
  
06:20 How Does It Work?  
  
08:42 Claude Build (2)  
  
13:44 Outro  
  
  
In this video I go over how to build a Claude project that can produce Vox-Style motion graphic story videos. Enjoy  
  
Subscribe!  
  
🔻  
Savfk - The Age Of Wood is under a Creative Commons BY 3.0 license.  
https://creativecommons.org/licenses/...  
/ savfkmusic  
Music powered by BreakingCopyright: • 'The Age Of Wood' by Savfk 🇮🇹 | Cello Musi...  
🔎 Find more music here: https://breakingcopyright.com  
🔺

## Transcript

### Intro

**0:00** · I fully automated the creation of a full Vox style motion graphic video using just Claude code and Gemini Omni.

### Example Video

**0:07** · 10 companies now make up 41% of the entire S&amp;P 500, more concentrated than the peak of the dot-com bubble. This year alone, Big Tech will pour 725 billion dollars into AI data centers. But look closer. \[music\] Nvidia invests 100 billion in OpenAI. OpenAI buys 250 billion of computing from Microsoft. The money just loops in a circle. And OpenAI spends 60 billion a year on compute while earning just 13.

**0:43** · So, what happens when the music stops?

### Intro

**0:46** · This is the system that made that video that we're going to create in this video together. All I did was say {slash} Vox video to activate it, and then I said what I wanted it to be about, which was the AI bubble in this case.

**0:58** · And it sent us back the final video once it was done right here, which we can click on to watch and download. This one was only 38 seconds, but you can make it longer if you specify that in the prompt. Gemini Omni is the number one AI video model right now, and this is what's allowing us to make videos like this. In this video, we're going to build the system step by step just with text right here in Claude code.

**1:22** · Framework Explained has a great video on some of the prompts for these kinds of videos. I reverse-engineered some of the prompts from his video to create this system. So, definitely go show him some love. I'll leave a link down in the description.

**1:35** · His video's also good for going into why the prompts work and what works best between different AI video models. If you've never heard of Vox before, this is the YouTube channel. These are their most popular videos. As you can see, they do really, really well. And at this point, when you have a a this big, you basically have your own company. This channel is now a company and an entire business in itself. So, how much does it cost? Claude code is $20 a month to actually build the system itself.

### Costs

**2:06** · Then you have Key AI, which is $3.50, roughly around there, per 35-second chapter. So, if you wanted four chapters, all 35 seconds, in one longer video, that would be 4 \* 3.5 for that full video.

**2:26** · And Eleven Labs is free, and the next plan up, if you end up using a lot of credits, is only about $6. So, that's pretty cheap. So, let's get started on the build. You're going to need to download the Claude desktop app, if you haven't already. You can just search for Claude download, and make sure it's on the official Claude website, claude.com/download, and then download it for your operating system. Once you're logged in, you're going to want to make sure you're on code up here in the top left.

### Claude Build (1)

**2:54** · Then you can go ahead and collapse the sidebar for now. And down here, click on this little file icon right here, and click on open folder. Now, wherever you want on your computer, I'm just going to do my desktop just for simplicity.

**3:12** · You can right click, go new folder, and create a new folder, and that's where your project is going to be built. So, I already have an empty one right here called Vox videos. I'm just going to select that and click on select folder. Now, over here on the sidebar, just make sure you're on a new session, and I'm going to be using Fable 5, but you can use Opus 4.8 if you want.

**3:35** · And I'm on a bypass permissions mode just to kind of speed things up, but that is optional as well. So, in the description, you will find this entire prompt, which you can go ahead and copy. And once you paste that in, you can essentially just hit enter and let it get to work. Now, it's going to start asking you some questions, but before you answer any, there's one thing we need to do.

**3:59** · We need to go to the spot where we the same folder that we just selected for the project to be built in. So, again, I selected on my desktop, so that's it. This is it right here.

**4:10** · And we're going to need to download these four files, which I've set up and there's a link in the description to download these four files. And what these are, we'll get into all of this a little bit later, but essentially, it's just how to prompt the videos, how to prompt the images, and an example style reference. So, we open this up, this is the style reference for the videos, so that it understands how to make the videos and the images, right?

**4:43** · Um and so, you're just going to want to select all of these and go ahead and click on download. Once you've downloaded those, again, this is the same folder that we selected in Claude, we're just going to put it right in here, and now Claude has access to all of that information. So, we can go back into Claude, and so, it's going to it's asking us about them right now.

**5:06** · A reference image prompt guideline, but the folder is empty. How should I handle these?

**5:13** · So, we'll just say, I'll add them myself. Or we could write, I added them or whatever. I'll just say, I'll add them myself, right? Boom.

**5:22** · What aspect ratio should the videos be?

**5:23** · So, I'm going to go 16 by 9 landscape. For the 11 Labs narration voice, do you have a specific voice in mind? I'm just going to say, pick a good default, but if you have a specific one, you can always choose that.

**5:38** · For background music, where do the songs come from?

**5:41** · I'll drop files in a music folder. So, I am going to click this one right here. I actually haven't done that yet, so I'm going to add that right now. So, in the same folder, I'm just going to paste in a song. I just searched on YouTube intense violin, and I eventually found this one song. You can paste in whatever song you want.

**6:01** · Okay, so where did the songs come from?

**6:03** · Now, we can say, I'll drop the files in a music folder, but it'll find the song regardless because we put it in the project files. So, we can say, I'll drop it in there.

**6:15** · And now we've answered the questions and added all the files, and we can let it do its work. While that's running in the background and building it, let's quickly go over how it works because we pasted in that big block of text, but what is that actually telling Claude to do?

### How Does It Work?

**6:29** · So, essentially, what it's telling Claude to do is build a system that does these five steps right here.

**6:37** · So, we'll send in the prompt, for example, the AI bubble, right? Whatever we want the video to be about, and it's going to generate a speech, but it's going to separate the speech into four or more separate parts, and then what it's going to do is for the reference images, each image is going to be based on the speech. So, if it's about a door, for example, a door in image in speech one, if he says, "The door opened."

**7:11** · then in image one, it might be a door, right?

**7:15** · Or a door opening, or whatever. And each of these images is being generated using that reference image from earlier, so that they're all in the same style. So, now you have a bunch of images based on the speech and what's being said, but they're not moving yet, so that's the fifth step. Each image is going to be turned into a video using Gemini Omni.

**7:42** · And the speech itself is also going to be used as context for the video. So, if in the middle of the video it says, "The door opens." That's going to go into the prompt. So, right when that is said, the door opens.

**7:59** · And then it's going to combine all of those clips into the final video. The good thing about Claude is let's say you don't like the video number two, you can tell Claude regenerate this one and it will regenerate just that video and still combine all of the other videos into the final video. Here is the full reference image that I'm talking about.

**8:20** · In the Google Drive, there is also this master prompt. Again, credit to Framework Explained, link in the description. He's an absolute legend. This is the kind of image that this is going to make. And you can go ahead and change this or generate your own. Here's a few other examples, right? Like this one's kind of like a rush hour. This one's like a murder mystery, etc.

### Claude Build (2)

**8:42** · All right, it looks like our project is done and it's asking us to do one more thing, which is to fill in the 11 Labs API key and the key API key. So, 11 Labs is for the speech and key is for the images and the videos. So, the first thing we're going to do is go to 11 Labs to get the API key to authenticate for speech.

**9:05** · So, you can find a link to 11 Labs in the description. Once you are signed in, in the bottom left, just click on developers. Then click on API keys here at the top. Click on create key over here on the right. Just turn off restrict key. And then in the bottom right down here, just click on create key.

**9:30** · Now, that's going to give you a API key on screen. It's only going to pop up once. Just click on copy and bring that over here back into Claude. So, back in our project files, right? These are the project files. I made mine on my desktop, wherever you made yours. You're going to want to look for .env. So, go ahead and open up .env. You can right-click, open with Notepad.

**10:01** · And it's going to look something like this. So, 11 Labs API key equals right after the API key equals right after the equal sign, you're going to want to paste that key you just copied. Go ahead and paste it right there. Now, once you've pasted it in, go ahead and click file, save. Then, we're going to need the key API key. So, for that, you can find a link to key in the description.

**10:27** · Once you are signed in on here, you're going to want to go to billing over here on the left and add a little credits. You can add as little as $5. Once you've added some credits, you can come on the left over here to API keys, click on create new key, all models, enter a name right here, and click on create. That's also going to give you the API key, which you can then copy.

**10:55** · You can also copy it just by clicking this little button next to it right here. Now, once you've copied it, you're going to go back into your .env. And you're going to paste it right after the equal sign, as well. I'm not going to put it on here, but you would just paste it right there after the equal sign in the Notepad.

**11:16** · Then, what you're going to do is click file and save. Now that those are both saved to .env, you can see here this is the command we're going to use, right?

**11:24** · Which is /vox video. Now, often this won't show up unless you restart Claude. So, we're just going to close it up here in the top right.

**11:32** · Close.

**11:34** · And then reopen Claude. Okay. So, we're going to make sure we're still on our session here. CL3 Vox Videos is the name of mine. Make sure you're still on your folder. And so, this is our old chat over here, but we're in a new session now, but we're still in the same project. So, we can test it out. We can do {slash} Vox video. And let's do the same thing. We'll do the AI bubble.

**12:01** · And we'll just send that off. All right. Looks like Claude is done making our video, so let's check it out. Now, it's not letting me full screen it right here. So, we can find all our past videos right here in the output folder. Here it is, AI bubble and final.

**12:18** · This year, five tech giants will pour 725 billion dollars into AI data centers, up 77% in 1 year. But the money moves in a circle. Nvidia invests in Open AI. Open AI pays Oracle for compute. Oracle buys Nvidia's chips. Over 800 billion dollars in circular deals, while Open AI loses 14 billion this year. Central bankers are calling it dot-com deja vu. If demand doesn't catch up, this bubble could sink the whole economy.

**12:53** · And there you go. I think that was pretty good, personally. A few notes for the prompt is you can actually leave it empty and it will just come up with a random news politics-based video. You can put in the USA and it'll make do stuff about the USA, whatever's happening currently uh and recently, that's what it will go off of.

**13:16** · And if you want it to be longer, just say make it three chapters, make it four chapters, whatever, cuz each chapter is about 30 to 40 seconds. And if you do want to make any personal changes, just make sure you come back into this same session that you built it in just so it has context.

**13:33** · And it might let you know that you don't have enough credits. So, if you need more credits, you can do that right here on Key AI. And for 11 Labs, it's just up here in the top right. That's going to do it for this video. Be sure to subscribe if you want to see more like this, and I'll see you in the next one.

### Outro

**13:49** · Peace.