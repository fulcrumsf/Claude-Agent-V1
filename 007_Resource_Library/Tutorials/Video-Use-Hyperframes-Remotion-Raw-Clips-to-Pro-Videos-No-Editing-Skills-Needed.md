---
title: "Video-Use + Hyperframes + Remotion Raw Clips to Pro Videos (No Editing Skills Needed)"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=4-WdZpFreOc)

video-use — edit videos with Claude Code. 100% open source.  
  
Drop raw footage in a folder, chat with Claude Code, get final.mp4 back. Works for any content — montages, tutorials, travel, interviews — without presets or menus.  
  
links:  
https://github.com/browser-use/video-use/  
  
Disclaimer:  
This video is for educational and entertainment purposes only. I am not a financial advisor, and nothing here constitutes financial, investment, tax, or legal advice. Past performance is not indicative of future results. Always do your own research and Consult a qualified professional for your specific situation  
  
Kaggle notebooks:  
Notebook is only created for demonstration and serve as a guidance for those who were interested using similar methods to build projects. It is NOT a free giveaway for a few reasons. 1. it works while the video is recorded, However it does not guarantee to work at a later date as tech communities make code changes all the time. Please follow the tutorial and create your own version of it if needed. 2. If you have any questions or need help, please join the discord server community to discuss or subscribe to the channel. 3. if you need further professional assistance, please feel to book a consulting call. Thanks for understanding  
  
Discuss:  
https://discord.gg/EXjaZnudHu  
  
Discovery Call:  
https://cal.com/productdeploy  
  
Follow me on x.com:  
https://x.com/jacobcdev  
  
  
\[Helpful links\]:  
  
\[Must Watch\]:  
How to Setup OIlama On Kaggle  
https://youtu.be/W6nMkzVcELQ  
  
How to setup Ollama with multi GPUs on Kaggle  
https://youtu.be/In8jMEXRDwA  
  
How to Use Free GPU on Kaggle:  
https://www.youtube.com/watch?v=djbjDOBkz1k  
  
How to Use Free Premium LLMs on Kaggle:  
https://youtu.be/W2luKfMM3Xk  
  
How to Setup Visual Studio Code Web on Kaggle  
https://youtu.be/tGKz3zLwnd0  
  
Transform Kaggle Notebook to Virtual Machine with Good GPU, CPU and RAM  
https://www.youtube.com/watch?v=n-USPtP9H3I  
  
How to Setup VLLM On Kaggle Notebook  
https://www.youtube.com/watch?v=Quwf1TBycgM  
  
How to Setup OpenWebUI On Kaggle Notebook  
https://youtu.be/0jAhK3hlIbM  
  
How to Setup the Best Open Source Manus AI Agent (Kortix Suna) Locally  
https://youtu.be/q9xeHfdTcdQ?si=4q4zZ8sGqc39GlMq  
  
How to Setup ComfyUI on Kaggle Free GPU  
https://youtu.be/orhLPlVRUMc?si=MH9BcAijVPf-FYFJ  
  
How to Setup Gradio Tunnel on Kaggle  
https://youtu.be/vmPYKWRV4xo?t=206  
  
\[You might also like\]:  
  
PlayList  
https://www.youtube.com/playlist?list=PLn32cjH9B2Bqub\_kg74d-U4EfiexZ6ILi  
https://www.youtube.com/playlist?list=PLn32cjH9B2BoiOj\_qYE1o-WFzyLdLb3Hr  
https://www.youtube.com/playlist?list=PLn32cjH9B2Bqc9iRDrq2uDGBZmxljsAvT  
https://www.youtube.com/playlist?list=PLn32cjH9B2BoU8393rCUbqbKLFb4Oc4Op  
https://www.youtube.com/playlist?list=PLn32cjH9B2Bp\_rSIQRt8V37XISvZ\_WjEq  
https://www.youtube.com/playlist?list=PLn32cjH9B2Bqp27lvFGzCBKyZaJg9mljY  
https://www.youtube.com/playlist?list=PLn32cjH9B2BpbOu1M1C8zyNPel2eYrdLB  
  
  
Music from #Uppbeat (free for Creators!):  
https://uppbeat.io/t/21-on-the-block/...  
License code: MKM7BDGHR8BXIH2S  
  
Music from #Uppbeat (free for Creators!):  
https://uppbeat.io/t/theo-gerard/the-good-life  
License code: ATVBJRKCLBUUMZYA  
  
Music from #Uppbeat (free for Creators!):  
https://uppbeat.io/t/rahul-popawala/vacay-vibes  
License code: KMBSTRNDE4NR5A9I

## Transcript

**0:06** · Hello guys, welcome to another video. So in today's tutorial, we're going to introduce a very interesting project, which is called Video Use from Browser Use. I think you guys already familiar with the Browser Use, but the Video Use project is very interesting. And what it does is to edit videos with coding agent. So, to edit the video, usually you need to use a video model. And for this project, it does not need any of the models.

**0:31** · Instead, it's actually using the coding agents, which is the LLM to edit videos.

**0:36** · And uh it's going to be working with the cloud code, code acts, so on and so forth.

**0:41** · So, this project only have 18 commits, as you can see here, but it already have 15K stars, which is crazy. So, in this tutorial, we're going to show you guys how this works and how to use it, how to install it. So, that being said, let's get started.

**0:55** · So, if you look at the readme, so there's a pretty good instructions about how to set this up. You can use prompt to set it up, but we're going to show you guys how to use the manual to set it up on Linux. And uh so also, you have a introduction of how it works. So, this actually show you guys a pretty much a high-level overview of how this uh Video Use works, but we'll break this down into very detail to show actually how this works step by step later in this video.

**1:23** · And so, first, let's show you an example of how this works. So, because it's actually using the LLM to generate or edit videos. So, a very important concept is that the edited video is different than generate videos. So, edited video is actually edit the existing generated video. So, you can use a video model to generate a really good video, uh such as the Sit Dance 2.0 or Sit Dance 1.5 Pro, so on and so forth.

**1:55** · You can create video using those video volumes, but for editing, there's many ways. So, if you use the video use to edit a video, in fact, it's not going to generate any frames or edit a frame using the uh video model.

**2:13** · So, but what it does is combining the video composition technology such as hyperframes with motions, so and so forth, to generate a certain piece of the videos and blend it into the existing video that you're trying to edit. So, it's very different.

**2:33** · And so, to edit the existing videos, you will actually read the audio and video frames of the existing video.

**2:45** · So, it will actually make the edits based on effects such as make it lighter or darker or transparent, something like that. So, it's not going to change the entire frame of the video, but it's going to edit like the coloring and some stuff like that. So, that's what they called the added videos with code engines.

**3:09** · Instead of generating new videos, it's going to make the video more towards what you want it to be and we want to put it on production. So, let me demonstrate what this means. So, if you create a video, for example, using Synthens uh 1.5 Pro. So, for example, it says shoe video. Let's play it.

**3:35** · So, you can see that there's no audio uh for like a sound or human speaking. It's just a little bit uh music. And because it's very simple, 4 seconds, what we want to do is want to extend it to a 10-second video.

**3:52** · And without any uh crazy changes. So, just make it better, more uh production-looking.

**4:02** · So, after that, you'll see something like this if you actually run this with ClockOut.

**4:18** · As you can see that, it creates a 10-second video without changing the existing frame of video. Instead, it switch the lightning a little bit, and also switch the different pieces of the video actually to put the pieces um that's generated by the hyper frames or the remotions inside exit video, and also put them together. So, it's actually called segments. We're going to talk about this later in this video.

**4:45** · So, it's segmented all different parts from the video, and put new segments inside it, and then put them together to generate this new video. So, how this works is that there's uh a few steps to get to start from finish. So, let's uh go through that to understand how this actually works. So, first, if you have a voice, it will first do the transcript.

**5:13** · So, this will use the ElevenLabs to transcribe the voice, but word by word with timestamps. Then, it will pack in different words to different segments.

**5:25** · So, like different phrases. So, it's called packing layer. So, this actually uh it's going to pack different words, or you can say group different words together to generate uh different groups. So, you can see that um there's uh different words, and they put them together as a segment. Also, uh you can say that different segments. So, that's the step two. Step three is for video inspection. So, this very interesting.

**5:54** · So, it actually generate a summary of the video. So, to demonstrate what it means, we can go to video views and if you generate video, you can have edit folder. So, inside the folder, there is a subfolder called verify. So, you can see that it's actually generate different PNG files. It represents the video uh like a summary. So, it's not entire video, but it's actually like a summary.

**6:22** · So, like a uh for example, there's a final wave and you can basically see there's actually a image of a wave and there's different parts of the frames. So, that's how the LLM understand it. So, you can see there's also like different uh key frames 01, key frames 02.

**6:40** · So, it just represents uh different parts of the video instead of inside uh put the entire frames to a LLM or a video model, it basically give a summary.

**6:57** · So, and then after uh you generate different the different the summaries, and then it will uh go to a step four.

**7:11** · So, step four does is to reason this um editing. So, using the agent. So, that's where the coding agent comes in. So, it actually follow this skill.md file. So, in the skill.md file, you can see there's a skills inside this project.

**7:32** · So, it's called skill.md. So, this file basically instruct the coding agent to edit the video. So, you can check out more on the GitHub repo.

**7:43** · Uh so, but but this is what the agent does.

**7:47** · And then after that, it will start and it generate a EDL JSON file. So, this actually give the architecture of the video. So, the EDL stands for edit decision list. So, this is turned video to a DOM similar object. So, to demonstrate what that is, let's just go to the EDL JSON file. So, you can see that uh basically it says the start is zero and it's 4 seconds.

**8:15** · So, it's a 4-second video. We'll turn that into a 10-second video without changing the existing frames or basically change them or update the frames entirely. It will still do some grading and also coloring, but I doesn't change the pictures.

**8:32** · So, then that's where it changes and then you can see there's this uh overlays.

**8:37** · So, this actually going to put the different uh I say hyper frames or different uh new frames into the existing existing video. So, so, basically it's going to give the LM a concept of where to update the video. So, after all that, it basically start to render. So, this is step five to render it.

**9:02** · So, the rendering is basically for each segment uh that we generated in the past, it will apply color and also the uh filters and all that stuff. So, then it will uh generate the or refine the segments. And also to concat all the segment uh without any loss.

**9:25** · So, it's almost to generate the video, but before that it will basically uh using the uh animations. If you say if you want to create more frames, as we saw earlier for this example, it will use the hyper frames and the remote motion and also my name to create all the different frames and which is called a overlays to add or pad to the existing video. And this is stored in the added animation folder. So, you can see there's a animation folder.

**9:56** · There's called edit animations. And you can see in this folder, there's different segment or different parts um that's generated by the hyper frames.

**10:08** · So, if you expand some of it, so you can see that there is a frames here. So, so images um this is generated. So.

**10:17** · And lastly, they will do the self-evaluation and to check out if everything looks good, then it will generate a preview or final MP4. So, you can see there's a final video that's generated, which we saw earlier.

**10:35** · Uh so, that's the final video we saw.

**10:37** · So, and after this session, it will also store everything that's talked about that's generated into a file called project. So, the project MD stores what's generated in this session.

**10:51** · So, um this is going to be helpful when we want to generate the next one. So, that's the last step. So, it's a very decent, very good structure and concept so that it makes uh this editing more interesting and more uh more uh nicer if you want to make this video uh productionized. So, So, that's it. So, this is how this works.

**11:18** · And for example, if you actually saw what we generated, uh basically what we did is to uh as we mentioned earlier, to actually use this video use as a skill to uh update this shoe video and make a better shoe brand promo video for 10 seconds.

**11:38** · So, that's the prompt we use in the clock out. So, you can see the before and after effect of the video. And this is basically the key frames we talked about earlier. So, that's it.

**11:54** · So, after everything is completed, you can see there's uh files updated. So, it will give you a summary.

**12:03** · So, it's pretty decent. Uh so, there's no really anything uh video model related. It's all really just outlines. So, and hopefully this helpful. And last but not the least, if you want to install it, so there's also document in the GitHub read me, but also I have put something useful for you um in here. So, you can just follow this to install it. It's pretty much uh very straightforward. Just a few lines. So, you have to clone the GitHub repo, then you have to uh do a git pull, and then basically install the dependencies.

**12:34** · I can use the UV or use pip install. And then you have to install the FM MPEG.

**12:44** · And it might be TRP is optional. Then you have to basically do a soft link uh from the video use skills to your cloud, which is your uh coding agent, to the skills folder. And that's it. So, hopefully this helpful. And if you do like this video, please subscribe, like, and comment. If you have any questions, thank you so much for supporting the channel, and see you in the next one.