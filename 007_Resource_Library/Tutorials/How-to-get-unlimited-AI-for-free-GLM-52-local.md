---
title: "How to get unlimited AI for free (GLM 5.2 local)"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=mhOqhMuYxWE)

GLM 5.2 is incredible and crushes Opus. Here is how it works and how I am running it locally and more information on local models  
  
FULL GLM 5.2 bootcamp in the Vibe Coding Academy coming up: https://www.skool.com/vibe-coding-academy  
2nd Youtube Channel: https://youtube.com/@AlexFinnLabsOfficial  
Sign up for my free newsletter: https://www.alexfinn.ai/subscribe  
Follow my X: https://x.com/AlexFinn  
Henry Intelligent Machines (my new startup): https://meethenry.ai  
My $300k/yr AI app: https://www.creatorbuddy.io/  
  
Timestamps:  
0:00 Intro  
1:18 Demo of GLM  
2:25 What makes GLM special  
4:14 Computer you need  
5:45 The upsides of running GLM locally  
6:42 The downsides  
7:33 What are local models  
10:53 Which local models you can run  
11:55 Setting up GLM locally  
14:04 Pricing  
14:45 The future of AI

## Transcript

### Intro

**0:00** · I have unlimited free superintelligence running on my desk. GLM 5.2 launched a few days ago and it is taking the world by storm. Benchmarks and many people's own experiences are saying this is just about as good as Opus 4.8, definitely or right around 4.6 or 4.7. But something major just happened today. Unsloth released a version of GLM 5.2 that you can run locally on just 250 GB of memory.

**0:32** · I downloaded and tested it on my Mac Studio and I'm going to be honest with you, I am completely blown away. It is just about as good as Opus 4.8. It is very very good. In this video I'll cover why this model is so good, show you some demonstrations, show you how to set it up so you can have unlimited AI as well.

**0:51** · If this is your first time working with local models, I'll give you what local models are, how to set them up for your first time, what kind of computers you need. I'll tell you why I believe all of this is the future and everyone will be running their own local models very very soon. And I'll tell you how to start preparing for that future today. You are going to learn so much in this video. It will blow your brains out your wazoo. So let's lock in and get into it. So anyone who's watched my live streams before, by the way they're coming back soon, you know the 3D first-person shooter test.

### Demo of GLM

**1:24** · This what I'm about to show you is the 3D first-person shooter that GLM 5.2 ran completely locally on my Mac Studio.

**1:34** · It is a good-looking game. You can see a great environment, good enemies. You can see a lot of video effects. The colors are nice. You can see hit counters and all of that. It is a very good test and is just as good for me as my Opus 4.8 test I did. It has waves, it has points, it has ammo, it has score, it has everything. It is really really good.

**1:54** · This was all built by GLM 5.2 running locally, which is powering this Hermes agent I have right here. I told my Hermes agent to build the game. It built it out, said the game is fully working, and on top of that, it even tested itself, played the game itself, and then self-improved. So, it actually made its own skills for creating 3 JS games. This is a completely self-improving agent running on my Mac Studio. That is like mind-blowing to think the most powerful technology on planet Earth is just sitting on my desk right now.

**2:23** · So, let's talk about GLM5.2 and running it locally and what makes it so special. It is open weights. That means you can run it on your computer. By the way, we're going to cover a ton in this video. Feel free to look down below at the different chapters and skip wherever you need to.

### What makes GLM special

**2:39** · I'm going to cover you some beginner stuff, some advanced stuff, like what local models are, how to run them. If that's not relevant to you, feel free to skip around. But, if you are brand new to local models, stick around for that in a second as well. But, it is a local model. It is open weight. So, that means you can right now download it, load it onto your computer. I'll also talk about what kind of computer you need to do this, and start using it completely for free locally. Based on my tests, it is comparable to Opus 4 8. There are weaknesses compared to it. I'll go into that as well very shortly.

**3:08** · But, some of the things it's done, some of the tests I've given it, like that 3D first-person shooter, basically matched what Opus 4 8 was giving to me. It's running on my Mac Studio, one singular Mac Studio. I didn't have to link my different Mac I didn't have to make a cluster or anything like that. One singular Mac Studio. I'll talk about how much memory you need in a second. And what's amazing is it can power your Hermes agent or your Codex. So, right now, as I showed you, I have a Hermes agent running.

**3:37** · Every prompt I give this Hermes agent stays local, is unlimited, doesn't limited work on my computer.

**3:44** · It is powering this whole Hermes agent.

**3:46** · I still have Hermes running on Opus 4 8 and another Hermes on GPT 5 5. I'll go over when you want to local models, when you want to use frontier models a little bit later as well. But now I have a third agent on my computer that's running completely locally. And as I said, Codex, which shout out to OpenAI, they allow you to use any model you want inside Codex. You can now do vibe coding in Codex with GLM 5.2, a model that is very, very good.

**4:12** · Now for those newer to local models, they don't know much about it, let's talk about how they work and what type of hardware you need. You can run local models on any hardware you want. If you have a Mac mini with 16 GB of memory, there are local models out there that you can run on there. And I'll tell you how to do that a little bit later as well. But for this model specifically, GLM 5.2, it is a beefy model. It is a chunky boy. You need hardware for it.

### Computer you need

**4:42** · I am running the two-bit quant version of it. We'll talk about that a little bit as well. That version of the model is about 250 GB in size. That means you need 250 GB of memory, which means you can technically run this on a Mac Studio with 256 GB.

**5:03** · You won't have much room left. It might crash. But if you were one of the people who listened to me early on back in January when I was spouting about how incredible Mac Studio 512 GB were, you can run this easily on a Mac Studio 512 GB. So you also have the DGX Station which Nvidia just started releasing across many different providers. That has 750 GB of unified memory, so you can run it pretty easily on there as well.

**5:30** · That is just a very expensive computer.

**5:32** · So you still do need a good computer to run this. But again, no matter what computer you have right now, there is a local model out there that you can run.

**5:42** · And I will go over that very, very shortly. So let's talk about real quick the upsides and downsides here. Then we'll go into the more educational what are local models and how to set them up for the first time. The upsides of this model is it's free and unlimited if you're running it locally. It does cost if you run it through the cloud. I'll tell you about cloud versus local in a second as well. But if you run it locally, it's free, it's unlimited, it's private and secure. None of your messages go to the cloud. So if you want to have personal conversations with your AI, which I know some of you want to do, it is private, secure, no one else can read it.

### The upsides of running GLM locally

**6:13** · And it unlocks way more use cases. When you have unlimited private and secure AI, you can do a lot of things. Like for instance, I have my AI, my GLM 5.2 running on a loop right now.

**6:25** · It is going through my code base of the new SaaS I'm building, Henry Intelligent Machines. It's making sure it's secure.

**6:31** · It's fixing any bugs it finds. And it's doing this 24/7 365. These are the benefits of running local models is you unlock these incredible use cases. The downsides to local models are one, it's slow. I'll admit it. This is a very slow model. This is not going to be as fast as Chat GPT 5.5 or Opus 4.8 running on the cloud. It just won't be. That doesn't make it useless. It still has incredible uses. If it is passively working in the background doing things for you, you don't need snappy in the moment decisions to be made.

### The downsides

**7:02** · It's doing work for me constantly around the clock in the background. So I don't need it to be lightning fast. I still use Opus and Chat GPT for the things I need done very fast. It does have a smaller context window. It just is what it is. And the more you shrink it, the smaller it gets, the dumber it gets. This is a two-bit quant version, which on most models would make it very, very dumb. But with this onslaught version, they actually found it has 82% accuracy, which is really nice.

### What are local models

**7:33** · In a second, I'm going to go over how to set this up if you have the correct hardware. If you are newer to local models, I want to go through a few things first. I want to go through what local models are, and even if you don't have great hardware, how you can set them up. Again, if you're familiar with all this, feel free to skip down below to the different chapters. I'm throwing everything local models at you in this video. So, a lot of interesting information if you want to skip around.

**7:59** · But, what are local models exactly? Just so we're on the same page. So, as I talk about how to set this up, it all makes sense. Local models are Local models are LLMs that run on your computer. When you talk to ChatGPT or when you talk to Claude right now, you write a prompt.

**8:18** · Your prompt gets sent from your computer over the internet to the cloud or a data center like you see right here. This data center is filled with thousands, if not millions, of hyper-powerful GPUs. In a very, very, very simplistic explanation, basically what's happening on these GPUs is they get your prompt.

**8:39** · It takes the prompt and turns it into numbers. It takes those numbers and runs a whole bunch of calculations, which gets you a response in numbers. The GPUs then take those numbers, turn it back into letters and words, and give it back to you on your computer. Basically, at the end of the day, all these GPUs are just doing a tremendous amount of math.

**8:58** · The downside to all of this is you are paying for the GPU usage, right? You're paying for those tokens. And also, it's not very private at all. All your chat logs get sent to the cloud, get stored on servers, and anyone can read them at the companies for these frontier labs.

**9:14** · Local models are different. Now, these LLMs are running on your computer. So, whether you're running on a Mac mini or you're running on a Mac Studio, now instead of prompts going to these servers, they're just staying on the computer, and these computers are doing the math of your prompts. That has many benefits. Now, your prompts are not leaving your computer. They're all being stored locally, so it's very, very private. And you're not paying a toll booth as your prompts go in and out of data centers. They're all local, so it's completely for free. It just costs the electricity going into your computer.

**9:46** · The challenge with local models has been it's been hard for these AI companies that to make local models that are powerful on your hardware. The GPUs in these data centers are super, super powerful. But luckily, over the last year, these AI companies have done a great job of making the models more efficient, so they're still powerful on cheaper hardware, and figuring out ways to make the models smaller as well, so they're still smart even though the size is getting smaller.

**10:15** · Those advancements have allowed things like today that have happened, which is GLM 5.2, the super Opus-level model, being just as good on your local device. Now again, downsides, it is pretty slow, so you're probably not going to be using this as your main daily drive. You're still going to use Frontier Cloud models to do things you need done quickly, right? Like if I was relying on this for live coding, I'd be sitting here forever.

**10:41** · But because I'm using it passively to kind of review code in the background, it's not a big deal, and it's still super helpful. So let's talk about the computers you need to run local models, even if you're just running on a Mac mini, it's really dependent on the memory of your computer. When you load local models, they load into memory, right? So the more memory you have, the bigger the models you can run, the more intelligence you get.

### Which local models you can run

**11:05** · If you're on a Mac mini, if you're on a smaller Mac mini, you're probably going with Google's Gemma 4, which is a really, really small, but still pretty smart and efficient model, or NemoTron, which is a model from Nvidia, very happy to see Nvidia getting into local model game. If you're on better hardware, so you have like a good Nvidia chip like a 5090, or you have a DGX Spark, or a DGX Station, or a Mac Studio, you can run bigger models like GLM.

**11:31** · If you're not on like the top-tier hardware like the 512 GB Mac Studio, I'd recommend for most people Qwen 3.6 27B. You're going to get excellent intelligence out of that. It's going to be pretty fast as well, and it can run on most kind of mid-tier hardware. So, let's get back to GLM 5.2 and how to set it up locally. I do basically all technical work through Hermes Agent. You can use OpenClaw for this as well. This is why I highly recommend everyone have a Hermes or an OpenClaw on their computer.

### Setting up GLM locally

**12:03** · And basically all I did was message my Hermes Agent, give it a link to the tweet from Unsloth, which I will put down below if you're running on good hardware, and say, "Can you get this exact model running on my second Mac Studio?" It went in, it built a plan, it researched it, and by the end of all of this, if we scroll down to the bottom, boom, brand new Hermes Agent set up with GLM 5.2 running. And so, now I can use the model, and I have a Hermes Agent powered by it as well.

**12:32** · Basically all complex technical work is taken care of if you have a Hermes Agent or an OpenClaw running on your computer.

**12:40** · Because it is pretty technical loading these local models up. You have to download them, you have to set up a server, you have to do a whole bunch of things. But if you just tell your Hermes Agent to do it, it just goes and does it and figures it out for you. One step, I hit enter, it was done and all set up.

**12:53** · From there, now I have a Hermes Agent I can go to, ping anytime I want, and get it to do any work that I think would be appropriate for a local model to do.

**13:02** · Which again, for those wondering at home, okay, what do I do with local models? What do I do with frontier models? Frontier, anything that requires the top-tier intelligence, right? Fable 5 is going to be better than all of this. Or if you need speed, right? If you're vibe coding, you're building something out accurately, you probably need speed. I'm using frontier for that.

**13:19** · But local models, again, something where I want privacy, I'm having some sort of private conversation that I don't want Sam Altman reading in the servers, I will go and do that here, too, if it's something that can be done passively throughout the day. So, for instance, I have it checking every 2 hours my code base of my new SaaS looking for security issues, looking for bugs to fix, and it just fixes that passively 24 hours a day. It's just going and chugging through the code. It's doing it pretty slow, but because it's just a passive act, I don't care about the speed.

**13:48** · If I were to do this with Opus or if I was to do this with ChatGPT, it cost me a lot of money. It would cost a tremendous amount of money to have Claude or ChatGPT running 24 hours in the background. So, it's perfect for local models. Now, if you were to use GLM 5.2 in the cloud, which you totally can do, so you use it like a regular model, the pricing is pretty good. It's much cheaper than ChatGPT and Claude. You're getting a lot of usage for a better price. It's pretty good.

### Pricing

**14:16** · Now, there's questions that come up, okay, can I trust, you know, Chinese models? That's up to you to decide. I'm running it locally. When you run models locally, the data never leaves your computer, so you don't have to worry about going into other governments' hands to read. If you run locally, it's fine. If you run in the cloud, it's up to you. Although, I do know there are a lot of companies out there that are hosting GLM 5.2 on American servers if that's something you're concerned about.

**14:43** · So, let's real quick talk about the future, why I think local models are the future, and how you can prepare for it. I think this is important for everyone to watch. By the way, if you learned anything so far, make sure to leave a like down subscribe, turn on notifications. I'm also going to do a full live boot camp on local models in the Vibe Coding Academy, the number one community for people in AI. Make sure to sign up for that down below. It's the best decision you'll ever make. Link for that down below. So, the future, everyone has their own super intelligence on their desk.

### The future of AI

**15:15** · This has all been converging in one way. Over the last couple years, local models have gotten smarter and faster and been able to run on cheaper and cheaper hardware. We are going to hit the point in the next year is my prediction where you can have amazing amazing intelligence running on the cheapest Mac mini out there. And at that point, I think that level of intelligence will be good enough for 90% of people.

**15:39** · And so I believe in the near future everyone will have their own super intelligence sitting on their desk, none their data going to the cloud. It will be completely private and secure. It'll be your own personal intelligence. No Nobody working at OpenAI or Anthropic will be reading your chats and it will be doing work for you 24/7. So it'll be monitoring everything you do on your computer, helping you out where it can, building decks and documents and writing code all for you 24/7 passively in the background. I think this is a future that's coming within the next 12 months.

**16:09** · So how do you prepare for that future? What do you need to do? Well, first you need to understand how local AI works. I just gave you a pretty good explanation, but make sure you understand how it works.

**16:21** · If you watch my videos, you'll be in a good place. You'll understand how it works. Experiment with the hardware you have. So even if you have a crappy Mac mini right now, just install something that goes on it. What you can do is go to your Hermes or Open Claw agent say, "Hey, take a look at our computer.

**16:37** · Figure out what local models we can run on it and what use cases would be good for that type of local model." Even if you're on a small Mac mini, you will still be able to run some version of Gemma 4 and do small tiny little tasks on it. So go to your Hermes or Open Claw now and do that and experiment with the hardware you have. The best way to learn about AI is just by taking action. Just by doing it.

**17:00** · So install the model, even if it sucks, even if it can't take care all your vibe coding, still install it and use it and you will learn so much about AI and how it works. And then just keep up with what comes available. AI moves so freaking fast. New models dropping every single day. Make sure you keep up with AI, with local models, what's coming available for the hardware you're using, and stay on top of it to stay on the cutting edge.

**17:26** · I really believe the only way to win right now in this new world is to stay up-to-date on the most trending latest technology and use it as quickly as you can. If you watch my channel, if you watch my videos the moment they come out, leave likes on them, you will be up-to-date on all the latest tech and using the latest tech and have a distinct advantage to your competition. So, make sure you subscribe down below as well. I'm going to be doing way more tests and showing you way more use cases with this GLM 5.2 running locally.

**17:58** · I want to show you the coding loop I set up. So, if you want more information on coding loops, let me know down in the comment section below. I'll make that my next video if I get enough demand for it. I'm not sure if people are into like loops and coding loops.

**18:11** · So, let me know down below about that. I hope this was helpful. I have the greatest job in the entire world. All I do is experiment and create videos on my experiments and teach you guys about it.

**18:21** · It means the world you'd sit here and watch these videos and learn from me.

**18:24** · So, thank you. Thank you. Thank you so much. I'm so appreciative you watch these videos. Hope that was helpful.

**18:29** · I'll see you in the next video.