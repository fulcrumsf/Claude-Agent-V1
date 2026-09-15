---
title: "I Built a Claude Skill That Instantly WATCHES Any Video"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=2eOXhxcgA6s)

🚀 Access 600+ Claude Code Skills for FREE: https://www.its-applied-ai.com/landing/claude-code-skills  
  
Link to this skill: https://github.com/ston6919/matts-peeker  
  
In this video I show you a skill that I've built that can watch videos of any kind. Most of the time when AI 'watches' a video it simply looks at the transcript. But that way you are missing so much of the context.  
  
Shout out to Brad | AI & Automation for the initial idea.

## Transcript

**0:00** · I've just created this Claude code skill which can actually watch videos for you.

**0:04** · And I don't just mean read the transcript, it can really watch them.

**0:08** · You can feed it YouTube videos, X videos, short form videos, whatever, and it will see what's on the screen, not just read the transcript. This means that now I can fully analyze videos, not just analyze what is being said. In this video, I'm going to show you it in action. I'm going to show you the problem and how it solves the problem.

**0:24** · I'm going to show you how you can use it yourself and download this plugin \[music\] yourself for free. And I'm also going to show you how it works technically behind the scenes. So, if you want to make \[music\] any tweaks to it, you want to change it so it can solve whatever problem you're trying to solve, then you can do that, too. So, let's get into it. Let's start with the problem. So, let's take this video for example. This is a video explaining how LLMs work. This guy's really good and he has a load of visuals in his videos, too, which are really helpful. But, if I want to ask AI, \[music\] "Hey, I don't understand this part here.

**0:52** · I don't understand what these percentages are." Let me try and do that. So, let me take the URL, go over to Gemini, and I'm going to use Super Whisper to say, "Hey, can you look at this video and tell me what the percentages mean at the 2-minute 52 mark? I don't really understand it."

**1:08** · So, we will paste that in here, send it off. So, it's going to go, it's going to try and have a look. However, it's just going to make things up. So, it says mat, floor, cloud. Let's have a look over here. They're they're not there at all. They're not before, they're not after. It's just completely guessed and made it up. What's even worse is that it hasn't even said, "Hey, I can't watch the video." It's just made up, which like is the worst part of AI. So, now let's have a look at what I have made and the solution.

**1:35** · So, here we are within Claude code and I'm going to use this command called peak cuz we're going to have a peek at the video and I'm going to say, "Can you have a look at this video and \[music\] tell me what the percentages actually mean at the 2-minute 52 mark? I don't quite understand it." Okay, and I'll paste in the URL of the video. It's going to go over. It's going to peek at that video. And it's going to tell us what actually is going on. So, it takes a minute to process the video. So, while it's waiting, let me show you this. So, these are 643 Claude code skills that I have put together. You can use them, download them absolutely for free.

**2:05** · They do a load of things such as enhancing images, SEO a CEO advisor, PDF work, creating motion videos, which I do a lot like re-motion, \[music\] just a load of skills which really help you speed up your workflows. Absolutely for free. I'll leave a link down in the description where you can go and get access to all of these plus the one that I'm showing you in this video now. Cool, so here we are. It's come back and it's given me a load of text as AI always does, but we can see that it says, "This is what it shows at 2:52." And let's go back and check that that is correct.

**2:40** · \[music\] That is exactly correct. We've got worst age and worst. And if we have a look, that is precisely what it says.

**2:47** · \[music\] And then it goes on to explain how these actually link to it and what that means in terms of LLMs. So, you can see here it is actually looking at the video, not just reading the transcript and then just making something up. Now, you might be asking, "Matt, what's the point of this?" Let me give you some examples. So, firstly, I use this for research because if you are just researching by the transcript of a video, you're essentially missing out on half of the information, like all of the visual information. In a lot of cases, there is a lot of information which is not said, \[music\] but it's shown instead. And this way, you capture all of it if you want to research.

**3:16** · Also, I can use it for analyzing other YouTube videos. So, if I find a video that I really like, I can throw in the video, I can get AI to analyze it, and it's not just analyzing the script and everything like that, it's analyzing what's being shown, what graphics are being shown, when they're switching graphics, when they're speaking head, how the layout looks like. Are they Do they have like talking head and like me in the corner?

**3:37** · What does it all look like? I'm getting AI to understand all of this so I can better recreate videos.

**3:42** · Also, another use of this is transcription of videos. So, it's very easy to transcribe the audio of a video, but \[music\] if you're taking something from English and turning it into Spanish, you also need to see when is there English in the video, which you then need to change to Spanish in the video so that actually the entire video itself and the visuals are translated, not just the audio.

**4:03** · Also, if you want to duplicate a video, then you can duplicate not just the audio, but also the visuals, too, because AI can understand everything there. And these are just a handful.

**4:11** · There are a load more applications out there. So, let me talk you through how to set this up for yourself. So, come to this link here. This is my GitHub. And this is a public repo, so you can use this absolutely \[music\] for free. Come here. I'll put a link in the description and you can copy this.

**4:26** · And essentially, all we're going to do is come over to Claude. We're going to go over to code, go on new session.

**4:31** · Make sure you create a new folder. I've called this one picker. And when you're in a new folder, you simply want to say, "Install this skill here in this GitHub repo." And I'm going to paste in that.

**4:43** · And I'm also going to say, "Explain to me what API keys I need to collect and where I need to put them." And I'm going to send that off. And I wonder what it's going to do cuz I actually already have this skill installed. So, it might tell me that I've already got it installed.

**4:55** · But essentially, that's all you need to do. Then just follow the instructions and you'll just get it all set \[music\] up. The only API keys you need are from OpenRouter, this one here, \[music\] and also from Deepgram. And Deepgram is great because if you go into the pricing, you can see they give you $200 worth of free credits, which is very nice. Like with any skill, you need to click through and allow it to install a few things, but uh simply just go through this process \[music\] and you'll have it installed within no time at all.

**5:23** · Okay, so for my fellow nerds out there who want to know what's going on behind the scenes, let me explain it. So, firstly, what we need to do is download the video. When we're running this skill, we are downloading video. And to do this, we're using yt-dlp. You can pretty much download any tool \[music\] on the internet with this, like YouTube, X, Instagram, TikTok, whatever. It's basically the same as like a right-click \[music\] save as sort of feature, except when you're doing it by code. So, once we have downloaded the video, what we need to do is we need to strip the two components. So, there is audio and there is visual.

**5:55** · \[music\] And we need to get AI to understand both of these. So, let's start with the audio as that's the easier one. What we're looking for here is the transcript. And sometimes, especially with YouTube videos, we can just grab the transcript with that same tool. And if we can, sweet, we don't need to do anything else. We've just got the transcript.

**6:11** · However, if it's not a YouTube video or I think sometimes \[music\] if it's a smaller YouTube video and the captions haven't been generated, then we need to use another method. So, essentially, we need to strip the audio from the video. So, we're using FFmpeg to take the MP4 and strip the MP3 file from it.

**6:29** · The reason we're doing this is that we're going to send this MP3 file off to an API and we only want to send the MP3. If you send the entire MP4, you're going to send like a gigabyte file instead of like a 10-megabyte file. So, it just speeds up dramatically. Okay, so we send it off to an API. I use Deepgram.

**6:45** · Deepgram's great cuz they give you like $200 worth of credit for free when you sign up, which like is a load. You should like rarely need more than that.

**6:53** · But, feel free to use ElevenLabs or whatever you want to use. I then have a second backup built into this system, which is Super Data. Essentially, what this does is you give it the URL of the video and it generates the transcription \[snorts\] by itself doing lots of different things. That's like if everything else fails, it uses Super Data. But usually, it doesn't need to do that. Okay, so that's the audio side, right? We've either got the transcript directly from YouTube or we've generated it with Deepgram or something else. Now, the trickier part, which is the video. And actually, it's not tricky at all. So, let me explain how it works. So, AI doesn't understand video, but it does understand images.

**7:25** · And as you know, videos are just a collection of images. So, what we're going to use is FFmpeg to essentially rip some screenshots, some stills from this video. And then what we're going to do is take those stills and we're going to send them off and get them described essentially by AI.

**7:43** · There's several other things going on here as well, though. So, there's a polling process, which essentially means how often are we grabbing a screenshot from the video? The way that I've got it set up is that if it's a longer video, it's going to grab a screenshot every couple of seconds. If it's like a 10-minute-long video, it would do a screenshot every second. If it's just a short clip, it \[music\] would do it even up to 10 a second because sometimes if you want a short clip, you want to see exactly how things are moving. So, like you want to see exactly how a motion graphic is appearing so you can duplicate it, for example.

**8:12** · So, once we get all of those screenshots, we're going over to a vision model and getting it to describe \[music\] all of those and give us the descriptions back. Now, for this, I played around with it. I am using OpenRouter and I am using Gemini 2.5 flashlight. The reason for this is that Yes, you can use Claude. You might be saying, "Matt, why are you running it in Claude? Why don't you just use Claude's vision anyway?" Yeah, you can do that.

**8:36** · However, Claude's super expensive. It's just going to tear through your tokens.

**8:39** · And actually, Gemini 2.5 flashlight is super economical. This is it here using Gemini 2.5 flash. And this is for like a batch of images, too, cuz we send a batch cuz it's more economical. We are basically spending no money at all, which \[music\] is sweet. And that's essentially it. We're getting back all those descriptions of the images. And then we've got description of what is happening and a description of what's being said.

**9:04** · Also, what is in the tool is making sure that we've got the timestamps for every frame so that we can \[music\] reference and say, "Hey, what's happening here? What's happening here? What's happening when the audio is saying this?" And we can actually match it up with what is being said. And that's basically it. Not that tricky.

**9:20** · You just have to do a little bit of wiring up, or you don't cuz you can use this skill. But, I just have to do a little bit of wiring up in order to get it all to work. \[music\] The only things which you might have to do after downloading the skill are getting your OpenRouter API key and your Deepgram API key and then going into Claude here, wherever you have Claude saved, then going into settings.json, and putting those into your ENV section.

**9:42** · I \[music\] won't show you this cuz you'll see my API keys. If you're unsure on how to do it, just ask Claude on how to do it. So, that's it for this video. I hope you found it useful. If you want access to a load more Claude code skills absolutely for free, then as I said, link in the description. I will see you in the next one. Adios.