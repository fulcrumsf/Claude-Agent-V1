---
title: "Claude Changed Marketing"
type: tutorial
category: content-strategy
tags:
  - claude-code
  - marketing
  - ai-automation
created: 2026-05-08
source: local
---

![](https://www.youtube.com/watch?v=la1dkCFgj1k)

Work with me: https://www.skool.com/claude  
My Resource Hub: https://www.skool.com/aianswers  
If you like this video please subscribe so I can continue making more!  
\-----------------------------  
✉️ For Business Inquiries: samin@bookedin.ai  
  
Some featured tools  
Heygen: https://heygen.com?via=samin  
FireCrawl: https://firecrawl.link/samin-yasar  
  
  
Skills needed for the training  
https://saminator1.gumroad.com/l/npwws  
  
But why even listen to me?  
I’ve have helped 200+ business use AI Automations generating and saving them millions (look at my case studies)  
My company was featured in Bloomberg business week for innovative use of AI Agents.  
I’m an Ex-Amazon software engineer with over 6 years of experience  
I have a computer science degree from NYU  
  
Chapters:  
  
0:00 Intro  
1:02 The setup  
2:19 Install the e-com static image ads skill  
3:43 The 3 API keys you'll need  
5:55 Create professional static image ads  
7:39 Video ads  
8:06 Clone yourself in HeyGen  
10:16 Connect Seedance to Claude  
12:16 Generate creative briefs and shot lists  
14:06 Generate your first cinematic video ad  
16:15 Autopilot  
17:43 Scrape competitor winning ads  
20:01 Claude routines  
22:47 Local vs remote routines

## Transcript

### Intro

**0:00** · Claude just changed advertising forever and it's because of this new skill that lets you take a single product photo and generate professional ad creatives from it and even turn those into cinematic video ads. I've actually been using this for the past couple of weeks to make ads for my own product. And to show you how it works, we're going to be creating a bunch of image and video ads for this pink bottle that I stole from my wife.

**0:19** · Where's my water bottle?

**0:20** · So, in this video, I'm going to be breaking down how you can set this up for yourself in three levels. First, we're going to start with the setup.

**0:26** · I'll walk you through how to get Claude set up in the right way so you can generate ads and content like this. Then in level two, I'll show you how to create professional static image ads and then connect seance and claude to make these cinematic video ads all from that one product photo. And in level three, I'm going to be showing you how to put this entire thing on autopilot. So, it's generating fresh ad variations without you having to lift a finger. I'll also show you how Claude can actually scrape your competitor's products winning ads and then recreate them for your own product. and then we'll break down what this costs and how you can optimize that.

**0:56** · And even if you have no technical background, you'll be able to do this because all we're doing is simply speaking to Claude. Let's get into it.

### The setup

**1:04** · All right. So, to get our environment set up, first what we need to do is go to Claude AI. And right here, the first thing you need to do is make sure you download the desktop app. And you can find that in the bottom right if you hit this button. And then right here, hit download for Mac OS. And then open that up. All right. So, after you download the Claude desktop app, so what you're going to do after you have your desktop app installed is you're going to go right here, hit this button, and then right here, there's going to be chat, there's going to be co-work, and there's going to be code.

**1:35** · We're going to be needing code for this. So, I want you to hit that button, right? And it's as easy as just speaking to here. To do this, make sure you have either at least the pro or the max versions for Claude because we're going to be generating a lot of cool stuff with it. All right.

**1:49** · So, after you have clot set up, now what we need to do is collect all the little tools we're going to be using that's going to help us creating the really nice image ads. All right. So, first things first, what we want to do is get organized. And to get organized, we're going to go down in the bottom right here, click this thing, and then open a new folder. So, all our ads and everything will be in that folder. So, I'm just going to make a new folder called pink drink ads.

### Install the e-com static image ads skill

**2:19** · and uh let's open that. Okay, so now you see I'm going to be working in this pink drink ads folder. Okay, so Claude is super smart. But to get actually good content and output from Claude, what we need to do is now teach Claude a skill to make actually good images, right? So just to save you some time, I've actually made you a skill that you can be using and I'll show you how to use that, but you can use this either way.

**2:42** · Okay. So, in my clot club in if you go to the classroom and the skills vault, I have this e-commerce static image ads.

**2:50** · All right. So, what we want to do is copy this and then go back to our claude. And now we're going to be teaching it this skill inside this project file. All right. So, all we have to do is just paste this in and be like, "Hey, can you download this skill and help me set this up?"

**3:09** · By the way, guys, if you wanted to follow along with this tutorial right here in my resource hub, if you check for this video's title, and I made a doc that you can use to follow along, and it's completely free for anybody, and you can use this to follow along with what I'm going to be doing in this video. All right. All right. So, it just outputed this to me. So, let's just go over this so you understand. So, this skill essentially will slowly help you get started. And notice how it wants a couple things from you. Before we build anything, I need three API keys from you. And here's what each one does.

**3:39** · The Gemini API key. So, we're going to use Nano Banana Pro for this. So, this Nano Banana Pro is the image model that generates these images for you and that it's going to build all the text and everything around it. Then we need the Tavly API key which searches the web for any reference images and actually like you know pulls like for example images from Google images so that your end product the end ad you get is grounded in real world truth.

### The 3 API keys you'll need

**4:08** · Okay that means it's going to look a lot more premium instead of generic. And lastly it needs the scrape creator API key. Remember how I mentioned that we can pull ads from competitors. So, if we have a similar product to creators, this skill is going to go look up what other creators how their ads are doing and make similar ones like that. All right. So, I'm going to show you how to get each one of these. So, so for Gemini, um, it makes it really simple. All you have to do is click this button and it takes you to this place called ai.dev. And here, what you want to do is hit create API key.

**4:43** · And then let's call this uh, pink drink. And hit create key. I'm going to copy this key. I'm going to go back to my cloud and I'm going to say Gemini and I'm going to make a new line. Don't hit all of them. Enter at the same time.

**5:03** · Then I'm going to go to tabi.com and then right here where it says API keys, this plus button. What I want you to do is let's make a new key for this pink drink and then create that and then hit copy right here. Go back to our claude tavi paste that in. And then uh by the way these two are optional. Okay. So you don't technically need these but it'll look a lot better. So then we go to scrape creators. Let's join. Then you want to go to API keys.

**5:35** · And then you want to copy your API key and then paste it here. And then I'm going to say scrape creators and paste it here. And don't worry, I will rotate all these keys right after this. And then you want to hit enter.

**5:51** · Okay.

**5:54** · You're going to paste all these keys. And then what we want to do is then I'm going to take this cup and then take a picture of it. And then right here, I just air dropped it and I'm going to drop it in here. So, it's right here. And I want to make sure that I say, "Hey, I attached the image.

### Create professional static image ads

**6:18** · Can you save that in this folder as well?" And then start creating the ads with all of these resources. Okay. And then I'll wait. Great. So, it says ads are done. Now, if I open up this folder, can you open this in my Finder? And I like being lazy. Uh, I could have just as easily done it, but this is just a bit more fun. But here, okay, so if I open this up, go right here, and then right here, you can see all the ads.

**6:44** · And if I open it up, hopefully you'll be able to see. So you can see right here, just a quick little thing. It has all these reference images that it used throughout just so it looks a lot better, right? So right here, you can see this is an ad it made for this. It used all these ICE images and used them as reference images. So, it looks a lot better.

**7:05** · And it also went out and then went for Stanley and looked at and it looked at, you know, cool looking ads and funny angles and it's done all of that research and built all of these ads out that easily. Right? So, that was the first part where I wanted to make sure that you can get a product and then get output image ads out of it. So, that's step one. Now, let's move on to level two where I'm going to show you how you can actually use this product and all these tools to make cinematic video ads.

### Video ads

**7:39** · All right.

**7:42** · Okay. Now, what we need is to make sure we can insert ourselves into these video ads, create these videos, and make sure everything is consistent. And what I found to be the best thing to use for this is Heyen. If you go to hijen.com, you'll be met with this, right? Okay.

**8:01** · So, first after we make a hijen account, what we need to do is make a character like us. So, to do that, what you want to do is you want to go to avatar and then you want to hit avatars right here and then hit create avatar. Okay? And then you want to clone a real person.

### Clone yourself in HeyGen

**8:16** · Cool. Now, um I'm going to make sure my camera doesn't turn off. But right here, what you want to do is record yourself for 15 seconds and then move around a little bit and then talk as if you would because what this is going to let you do is basically it creates a clone of yourself that we're going to be putting into those ads. All right? So, make sure you do that. And after you do that and have that done, you'll see yourself in avatars like this.

**8:40** · So you see right now right right now I have an avatar of myself that got generated and I can use this now to create videos and even put it into my cinematic ads with this product. All right, I'm just going to give you a quick tour of how I've been using this through the UI and then we're going to connect Claude with this so it can create these things on autopilot.

**9:01** · All right, so to do that uh this third option right here is I want to go to avatar shots. You see, I've already made a couple, but right now, what you can do is click this and then select your avatar and then come here and then select your scene element, whatever it could be. So, for me, it's this photo of this pink drink thing. And then you hit add item and then you want to make a prompt. And then whatever you prompt it, it's going to make that.

**9:27** · So, let me show you how to actually prompt this just so you get really, really good product videos. So, I'll show you this example that I just generated recently. Okay, so let me play this. So, you can see already this is me. It's pretty good. And it's the cup.

**9:46** · 6 a.m. 30 things on the list. By 9:00, I've already emailed more people than I've spoken to this week.

**9:50** · Still going.

**9:51** · No way.

**9:51** · One cup all day.

**9:52** · Is that thing surgically attached?

**9:53** · Basically, 15 hours later, yes.

**9:57** · So, it's pretty good. I like it. Uh, it's pretty accurate in terms of how it looks like me. And then it also got the scene in the image. And you know, whatever in your heart's desire, you can make videos of right now. And you can put any references that you'd need. Okay. Now that that's done, let me show you how to do this only with Claude. All right.

### Connect Seedance to Claude

**10:20** · So to do that, what we're going to need to do is get an API key and connect Claude to Hen. So let me show you how to do that. And a quick little disclaimer for this. We're going to need either the creator plan or the pay as you co plan where it starts at like $5. And this one you can use with your API so it can connect to cloud and start generating these things, right? So make sure you have one of these. And after you have one of these, you need to make an API key. All right.

**10:49** · And to make an API key on the bottom left right here, you want to hit developers and then API dashboard. Okay. Then what you want to do is create a new API key and call it let's say pink drink and then hit agent because you can actually get your agents to create these on autopilot. Agent thought of that which I like a lot. And then hit create an API key.

**11:13** · Okay. Then you want to copy this and store this somewhere safe because we're going to need it in a little bit. All right. Okay. After you have that, then you want to hit the next thing which says agentic skills. And what I like is that they make it really easy to get started with the stuff. So right here, what I'm going to do is I'm going to copy this prompt and then I'm going to go back to my claude and then paste it here and make sure you put in your API key. All right. So I'll put in mine right here and then hit enter.

**11:39** · And then I'll wait so my claude project can install that skill and also knows about my API. All right. All right. So step two now is we want to make really good prompts for C dance. And to do that I actually built another skill for you just so it's a lot easier. So if I go back to my cloud club in classrooms and in vault in the bottom you'll see C dance prompting skill.

**12:02** · And all I need you to do is just copy this and you know I've done a lot of research on how to actually prompt Cance to get the best results especially for UGC and creating ads like this that are more realistic looking. So for here first um just to take you through the process let's just go a little slower. So I'll use this to create the prompt for the uh C dance prompt for the ad right.

### Generate creative briefs and shot lists

**12:25** · So hey can you install the skill and I want you to use the skill to create an ad angle that's let's say 4 seconds long uh for this pink Stanley Cup. And then I will hit go. Okay. So it just got done. And you don't need to technically do this step. You can just tell it to make it. But I wanted to show you kind of like under the hood just so you understand a bit better. What this skill kind of does is if I open it back in my finder, um, you see right here, it created a couple different files.

**12:56** · It created a a creative brief, it created the prompt that it's going to be using, uh, read read me and why even this works, like why this ad would be a good ad in the first place, right? Like it sells the benefits. it go went through all that you know thinking whatnot to make sure that this ad may

**13:18** · perform well and that's how we want to do it because when we want to put an ad engine on autopilot we want to make sure we can embed our strategy our ad creative strategy into it right and this lets us audit why our ads may be doing well and all the prompts and little things so you're not just going blind okay and you can see Um, when it makes the prompt, it gives you a shot by shot. So, shot one, shot two. It even like dissects the seconds, all these things.

**13:49** · You see, I asked it for 4 seconds. So, it's like four shots. And then all the lighting and all the acts, all the stuff. So, that's pretty cool. I just wanted to show you how the prompts I make with my skill are and how we can stay very organized when we're actually building these stuff out. But now, let me just make the video and then show you what that kind of looks like. Hey. Okay, this is really cool.

### Generate your first cinematic video ad

**14:13** · Can now you use the Hen to build out this avatar and this ad with this prompt with the avatar summon Yasar and um use also that the pink energy uh the pink cup that I initially attached. All right. inside the folder. Okay. So, I'm going to hit go and then I'll wait for that. Let's check it out. I'm gonna open my Finder. All right. So, let me watch this.

**14:48** · Wait, that is still ice cold. Yes. 6 a.m. 30 things on the list by 9. I've already All right. So, it's pretty good. And then you can see it just said it, you know, used me and my hijen avatar and still cold sentence and it used my product to do that. And it even says why I think this ad will work. Psychological anchor. Uh, okay. Having me in the ad, 4 second length for just a short one.

**15:17** · Okay, a lot of this stuff is cool. And then it gives you some recommendations as well as, hey, maybe run this with this much budget. Okay. And you know, if you've noticed in my finder, what it did is it put add gen one and then put it here. And then, you know, it's going to keep generating things if I make more and keep it very very organized in my finder. Now, we can generate image ads and we can generate video ads in the same project. So, this is just one way to do the ads.

**15:47** · But you see the limitation is we actually got clawed to do the thinking and the being the creative strategist. Now if you want to take it a step further and this is what actual uh media buyers do is they actually look for their competitors ads see which one's working well and then replicate that and try that out for their own product. So I'm going to show you how to take this to the next level to build that out so your clot can now automatically go scrape your competitor's ads and then make them for yourself. All right.

### Autopilot

**16:19** · So, to do that, first what we want to do is we want to go to firecrawl.dev.

**16:23** · And then right here, let's look at the pricing. You can actually start with the $0 plan. I think you should be good enough if you're just starting out, and you can increase if you need to, but uh after you have your fire crawl, what you want to do is you want to set up the firecrawl mcp. So, let me show you how to do that. So after you do that, what I want you to do is go to API keys, create another API key. Let's call it pink drink. Take the API key. Okay? So you want to copy this and then what you want to do is you want to go back to cloud.

**16:55** · You hit this button. You write and then you want to go to customize. In customize, you'll see there's connectors. In connectors, you want to right here. You want to add custom connectors. And then you can go to docs if you want to know where that is. And then right here if you hit MCP server uh and then copy this right here. Copy. And then go back to claude. Paste this here.

**17:20** · And then your name is fire crawl crawl pink. I'm just renaming it. And then paste your API key here. And then hit add. What you'll see is firecrawl pink right here. And then right here make sure you hit always allow. Okay.

**17:34** · Then you're good to go. Okay, if you go back to your thing and then in the bottom, if you hit this plus button and then hit connectors right here, you will see Firecrawl pink. Turn this on. All right. So, what I want you to do is use the Firecrawl MCP to go look through meta ads and scrape and find any performing ads that are similar to the Stanley and show me all the links. Put it here. Uh, make a folder so I can go through those ads. All right. Um, I want to see what competitive winning products are.

### Scrape competitor winning ads

**18:09** · Okay, I'll hit go and I'll let that happen. But the idea for this is now Firecrawl is so good at scraping that it can like spin up its own browsers, get past bot protectors and all these. So, I like this to use as a tool that does all the competitor research for me on autopilot. And then if I put this on a routine, what I can see is over time if competitors just have really cool winning ads, this firecrol will detect that and then automatically it can make an ad that is similar to that outlier.

**18:41** · So we can always have basically really cool winning ideas and take those and then make these ads and test them on autopilot. Right. So I'll wait it for this to get done. Okay. So let me see.

**18:54** · open up my finder and we can see there's a competitor research folder and there's a competitive analysis. So if I open that up, we can see what it's saying is what works is a spec dump, an influencer lifestyle ads or color drop. Okay, interesting. And even tells me what it's not running. And this is actually the cooler part is right here. Uh there are actually references to outlier ads. So you can see it's saying Lululemon is running these ads. It was saying Stanley is running these type of ads. Very interesting.

**19:27** · And if we can use those and then combine these keywords, these might do well.

**19:33** · Okay, this is a nice way to go about it and do some competitor research and have some inspiration to make new ads. And you know, this is super super smart. And the fact that Claude can do this now is kind of taking the job away from a media buyer. If you have your specific strategies that you do, you can connect these tools and set up these workflows really simply. So now let's say we want to take this entire thing and then make sure it's running on its own. How do we do that? Right? So let me show you that.

### Claude routines

**20:03** · And the way we do that is with this concept of routines. So just to make sure we take stock of what we just did.

**20:10** · So look at the middle of the circle right here. This is the entire job of a media buyer. What they really do is they scrape competitors, they come up with new ideas, they see what's working, brainstorm angles, and then they generate new creatives. Then they test it. They look what hits and then what didn't. And then they iterate and do that over and over and over again, right? And that's literally what we just put together manually. We pulled the competitor ads from Meta's library and then we came up with like new angles of how we can advertise this cup right here. Right?

**20:41** · Then we used Hen to make our own thing. And that loop what we can do is we can put it inside this pink ring which is essentially a routine. And a routine is this new feature cla dropped and which means we can use this to ship the ads on its own and scale infinitely without us having to touch it. So instead of us being the media buyer, we can get claw to do that for us and that runs forever. So that's the move and I'm going to show you how to do that next. So next what we want to do is take everything we just did and then make it into a routine.

**21:08** · The nice part is because we've been working in this folder for so long, Claude will have context of everything we just did. So what I can say is, hey, I would like you to take this process and make it a routine. Let's say every day I want you to create four image ads and one video ad that I can review and I want you to test in

**21:35** · uh so I can review that and then I want you to generate that every day and then store it in the folders like we just did um for maybe make two video ads actually. One of them I want you to see what competitors do are doing and then recreate that. And another one I want you to actually come up with your own angle and then make that happen. All right. So can you create just that routine right now?

**22:02** · Okay. So I'll wait for that to complete and then we'll take it from there. Awesome. So it just got done. Says I can view it in the UI. Let's go look at it by clicking this button. And we can see pink drink daily ads. It's run all the stuff right here. Cool.

**22:20** · Um, and you know, if you want to see it right here, if you go to routines right here, you should be able to see that as well. And right here, you can see this routine uh inside this folder right here. Okay, so that's where the routines are stored. But this is really cool. Uh, notice this because it's really important that hey, this is how it's going to do it. It's telling me what's going to happen and it's going to generate the video one and the video two for original and it's saying it's going to be using my API keys. But this is really important guys.

### Local vs remote routines

**22:48** · Look, the one limitation is that your computer has to stay on and fire for this Mac uh for this to fire, right? This is a limitation of the routines if we do it for local. So if you did want it to run without your computer having to stay on, what you want to do is make a remote routine and then schedule that as well.

**23:08** · All right. Okay. You can do that. Or if you want to actually dive into routines and really really take claw to the next level, watch this video right here where I laid out everything you would possibly need to know for becoming a master at clot. And in terms of cost and how to optimize it, I actually built this for you guys. This is like a little tool.

**23:28** · And if you if you're curious where it is, it's inside the cloud club inside the cost optimizer. And what this tool is, you can use the sliders with what model you're using to basically see how you can optimize your prompt, how you can see what it may end up costing if you want to try this a lot. All right, so if you want to do any of this stuff or want access, it's in the cloud club below. But with that, thanks