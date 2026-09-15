---
title: "I Made Vox-Style Motion Graphics Using Only Claude Code & Omni"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=dqtfk8iINXI)

🚀 Join the Applied AI Mastermind: https://go.its-applied-ai.com/go/g2ewqg7  
  
In this video I show you the full pipeline for creating Vox-style animation videos using AI with Claude Fable 5, GPT Image 2, and Google Omni.  
  
FREE RESOURCES  
✅ Vox style video pipeline: https://link.its-applied-ai.com/k5jk  
✅ Top 100 AI Tools: https://link.its-applied-ai.com/xczvwa  
✅ 100 Claude Code Skills: https://link.its-applied-ai.com/pdm3ou  
  
0:00 The One-Shot Result  
0:24 Researching the Vox Style  
1:39 The Free Pipeline Files  
2:21 Writing the Script  
3:39 Image & Video Models  
4:36 Creating the First Image  
5:31 Prompting the First Video  
8:00 First Scene Result  
8:11 Chaining the Scenes  
9:47 Finishing the Video  
10:40 The Final Result  
11:16 Process Recap  
12:35 Outro

## Transcript

### The One-Shot Result

**0:00** · I just one-shotted this with AI.

**0:02** · This ship has been at war for 260 years, and she's still in commission. Meet HMS Victory, 104 guns, 27 mi of rigging, 820 men crammed.

**0:16** · So, today I'm going to show you how I created this Vox style video using GPT Image 2 and Google Omni. And I'm going to show you how you can create it, too.

### Researching the Vox Style

**0:24** · So, let's get into it. Okay. Okay, so the first thing we need to do in order to create a Vox style video is to define what a Vox style video is. We need to give uh Claude a load of information about what this actually means. Now, there are different ways that you can do this. The way that I did it was that I used Ampify to go and find a bunch of YouTube videos that talk about Vox's editing style and video production. I said perhaps 10 of them, then put them in a notebook, LM notebook, and then from that give me a comprehensive breakdown of what the editing style is.

**0:54** · I found this is one of the best ways to do research. You could alternatively just go and take screenshots and ask it to like analyze it. But I used this method instead. So it created me a notebook that looked a little bit like this. You can see it pulled some sources and it created a notebook. And then I asked it to create me a comprehensive style prompt and an animation prompt because we're going to be doing two things here. We're going to be creating images and we're going to be prompting animations. We're going to be doing both of those things. And it went ahead and it made that style prompt and that animation prompt.

**1:23** · Now, these prompts are part of the video production pipeline that I've created as well as a bunch of skills which basically fix problems that I came up against whilst building it. If you want access to this entire pipeline, so like the skills, the prompts, everything like that, then there's a link down below where you can download that absolutely for free. But here are my files. You can see I've got a folder called Vox video. And if I open that up, I've got a load of different information in there. And this is the main one here, the Vox sequential scene workflow. And if I open this up, you can see it basically gives the instructions of this entire video which I'm showing you.

### The Free Pipeline Files

**1:52** · Now, what this allows you to do is create the video in one shot. You simply say create a video by X and it will create it.

**1:59** · However, what I'm going to show you in this video is step by step. I'm going to show you the different steps so that if you want to create this yourself, then you can. Or if you want to be able to, you know, uh reverse engineer what I created. So, maybe you can like take parts of what I've done and apply it to your own project, then you can do that.

**2:13** · Um, and also it provides a better result because you can check it at every step along the way rather than just saying, "Hey, create this and letting it do everything." But that is an option. So, let's hop into Claude and let's actually get started creating it. I'm going to use Fable 5. I'm within this folder.

### Writing the Script

**2:28** · That's the same folder as linked down below. And I want to create a video about the HMS Victory. I'm a proud Brit.

**2:34** · So, let's create it about that fine bit of British history. And I'm going to say, I want to create a Vox style video all about the HMS Victory. Please, can you create me a 30-cond script broken up into three chunks of 10 seconds or less?

**2:48** · uh just give me the script for now.

**2:52** · Okay. So um as I said it can do everything but I want to check in this pass through. So it's going to tell me what the script is going to be and then I can edit it because the script is what is going to guide everything. Okay. So here we are. Here are the three sections. They seem okay. They seem a little bit long and I need a little bit more punch. So I'm just going to say can we cut down the size of each one of these? You can rewrite it completely if you need to. Um, and also the first section, can we start it with like something a little bit more punchy, please?

**3:22** · Always say pleased to AI. You never know when the AI overlords are going to come and uh they're going to remember who said please and who didn't. So, \[laughter\] let's see what we get after that. Okay, this ship has been at war for 260 years and still in commission. Meet HMS Victory. Yeah. Okay, that is much much better. Good. Okay, so now the next step is we were going to create the first image. Now let me talk about the tools that we're using here and the models. Um we're creating the first image so that we can feed that image into the video model which will produce the video.

### Image & Video Models

**3:50** · The image model that we're using is um OpenAI's image GPT image 2 which at the moment is the best image model out there. It's not that expensive either. And then we're using Google's Omni um as the video model. Now to create these images and videos I am connecting to Kai AI. I'm not connecting directly to OpenAI's API and to Google's API.

**4:12** · Instead, I'm just doing it through one API. It just makes it easier as um you don't have to deal with a load of API keys and a load of, you know, making sure everything's got credits. Kai is good, equally good like foul and other things like that. In order to set this up, all that I did was to ask Claude to look over Kai's documentation and set up the API routes for Google Omni and for GPT2. Okay, so now we're back in Claude and I simply going to say, "Okay, that looks good. Please can you create me just the image um of the first scene?

### Creating the First Image

**4:42** · Okay. And we'll send that off. Now, if you are running this workflow, let me give you one little tip. Fable 5 is good and the claude models are good. They are incredibly slow. So, if you actually want to produce something quickly and like time is important, then don't use claude. Use something like codeex or use something like cursor or like the grock models. However, we are going to keep using claude. It is pretty good. Okay.

**5:02** · So, I had to reset my EMV variable. But I've got that image. Let's have a look at it. So, here it is. That is pretty good. Now, part of what the prompt says is in the first image of the first video, don't put any overlays of any text or anything because we need to add that in later. Good. So, now I'm going to say now that I'm happy with that, if you are not happy with that, then you can obviously request any changes. It is far cheaper and quicker to request changes to images like this than it is to request changes to videos. So, if you've got changes to make, make it here. Cool. So, I'm going to say that looks good.

### Prompting the First Video

**5:33** · Now, can you tell me the prompt that you're going to use to create the first video from this image?

**5:39** · So, again, you can just run this through all the way without being involved, but because this is kind of like a little bit of a walk through and showing you how it works, I'm doing it step by step.

**5:46** · Okay, so here we go. It's giving us the prompt for this first video and we can look it over just to make sure that we like um what it's going to show us. So, um let's see. As the narration says, at war for 260 years, a large stamp appears with 260 years. Yep. Still in commission. rack focus gently on the ship. The ship sharpens and lifts slightly in contrast with the sea. Okay.

**6:07** · Yeah, that looks fine. I'm going to say great. Go ahead and create this first video clip for me and then show it to me. Don't create more videos after this.

**6:17** · Okay. So, again, we're just doing this first video and then we're going to go on from that and create the the second videos. And essentially, I haven't said before, this 30 second long clip is going to be three separate videos which we're going to stitch together. Now, while that generates, if you are interested in creating content with AI for your business, for your marketing, whatever it may be, then inside the applied AI mastermind, I've got some assets which can be very useful. There's a full course all about AI content fundamentals, covering everything from image creation to um hyperframes.

**6:42** · And actually, I give you my own software which I have built bespokely to edit my own videos, but essentially from creating videos, creating images, there's also a full course about hyperframes and how to use AI to edit videos for you. And this is just a small selection of what is included within the applied AI mastermind. You can see that what is inside is a selection of full-length courses on things from Claude and AI vibe coding, Hermes, AI marketing to how to generate leads, NAT, which is still a very important tool.

**7:12** · But most importantly, there is the AI applied to business module, which is how to see the opportunities within your business or a client's business where you can actually use AI and apply it to a business so that the business can move forward. Whether that's in terms of sales and increasing topline or cutting costs and essentially improving the bottom line, we are seeing some great results inside the mastermind for some of our members. And there is a 14-day money back guarantee. So, you can join and if you don't like what you see, if it's not for you, absolutely fine. Just request your money back and there is zero risk.

**7:44** · And also, we're about to increase the prices. So, if you want to join and potentially save a load of money, lock in your price, then you can join with the link down below in the description, and I'd love to see you inside. Anyway, let's get back to it. Okay, so this first scene is generated. Let's have a little look at it.

### First Scene Result

**8:00** · This ship has been at war for 260 years, and she's still in commission. Meet HMS Victory.

**8:08** · Okay, there we go. So, um, let's close that. And now what we're going to do within this process is that it's going to read, uh, in order to create the next video. So, we've got three videos stitched together. We will do um in order to create the first frame for the next video, we're going to take this last frame here. We're going to have AI look at it because what AI is going to do is it's going to look at this and then it's going to plan on the next things that should happen from this frame here. Because I've tried it before where you just ask it to create all the prompts without seeing what's happening.

### Chaining the Scenes

**8:38** · And because it can't see what's happening, it creates prompts which don't really make a lot of sense. So, what in fact we're going to do is feed it this last image here. It's going to use ffmpeg to strip it. It's going to analyze it. Um, and then it's then going to take this and be able to plan on the next steps. So, I'm going to say, great, use ffmpeg to do your process and look at the last frame of that video that we created. And then using that, please plan out the next video for us. Don't actually create it. Just tell me the prompt.

**9:06** · Now, whilst we're waiting for this, I will mention that in the description below, I've got a list of free AI resources. If you're looking to help AI uh improve your business or clients businesses, then those might just help you, and they're free. So, go ahead, check them out. Great. Okay, so here is the second prompt. So, it's got some text in it. It's going to keep this text exactly the same, but it's going to render on some more text as well. Uh, no hard cuts. Um, the narration is going to say 104 guns while rough pencil circles are drawn around two or three gunports on the ship's hull. Okay, cool.

**9:36** · Yeah, I'm not going to read through all of that. I'm just going to assume the fable has done a good job. And actually, I'm going to say that looks good. I want you to go ahead and just uh finish the entire process for me. So, create this second video and then um take the last frame of that and create the third video from that. And then go ahead and stitch all three of those videos together. I want you to just give me the finished video. So here we're going to use that automation process which is built into this sort of like skill or project that I've built where we can just say okay just go ahead and do it.

### Finishing the Video

**10:07** · And I've given it some detail here about what it should do. Um but that's only just to make sure it stays on track. I have described before what it needs to do. So it should it should know if I just say complete it that it just needs to complete it and do duh in order to get it working. So, it's going to take probably like 5 minutes for it to create um that image to create that video. Then strip the image, analyze the image, create the prompt, create the other video, stitch them all together. So, let's come back when that's done. Let's see how it fares.

**10:36** · Okay, so it's come back all of those three scenes stitched together into one video. It's put them all together with FFmpeg. Let's have a little look and see what it looks like.

### The Final Result

**10:44** · This ship has been at war for 260 years, and she's still in commission. Meet HMS Victory 4 guns, 27 mi of rigging, 820 men crammed inside a floating fortress. Trafalgar 1805 Nelson's flagship shattered two fleets and he died on her deck victorious.

**11:07** · There you go. Pretty good. There are definitely some things we could change and we could improve, but you know, it's pretty staggering what we can now create for, you know, about a dollar. Just a little over a dollar is what that costed. So, that's the entire process.

### Process Recap

**11:20** · The entire process is creating a script using the Vox style guide which we created via pulling it from a load of YouTube videos. Um, first creating the first image and then turning that first image into a video. And then we take the last frame of that video and use it as the first frame for the next video. And we do that for however many bits of video you want to create. I've just done three here, but you can do as many as you like. Then once all of those video files are created, in fact, let me show you all of those video files. So here we can see if we go in here we've got uh scene one, scene two, and scene three.

**11:52** · And we've got their raw files as well.

**11:54** · And simply they just stitched together using ffmpeg which is just how you manipulate video files or image files as well. Um and stitched it together into one video. Now we have gone through this step by step. But you can simply say create me a video about the Napoleonic War or whatever it is you want to create a video about. walk away for 10 minutes and come back and it will create you a video 30 seconds long or 3 minutes long or 30 minutes long, however long you want. So, there we go. I hope you have found this useful.

**12:19** · If you do want kind like the file that I used and the skill that I used, the project that I used to create this with all the prompts and all the star guides and everything like that, then I'll leave that down below in the description. All you need to do is add your own API key for Kai or FAL or whichever one you want to use. is about applying AI to your business, creating content with AI or generally improving your business with AI with PRM strategies, then do check out the applied AI mastermind which will be linked down below in the description.

### Outro

**12:45** · Found this video interesting? Then please do give it a like, subscribe if you want to see more videos like this and I would highly recommend going and watching this video next. I think you'll find it very interesting. in the next video.