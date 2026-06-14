---
title: "This-AI-Agent-Builds-Full-Video-Ads-For-You-Claude-Code-Plus-Seedance-2.0"
type: tutorial
category: video-production
tags:
  - tutorial
  - how-to
  - claude-code
  - seedance
  - video-production
created: 2026-06-06
source: 000_Ingest/This AI Agent Builds Full Video Ads For You (Claude Code + Seedance 2.0).md
---
![](https://www.youtube.com/watch?v=BVK3mF7Ssxc)

Step 1: Install Claude Desktop on your computer here https://claude.com/download  
  
Step 2: grab the Claude Agent here: https://mrpaidsocial.myflodesk.com/osbpm4r8wv  
  
Step 3: open the Claude Desktop App  
  
Step 4: navigate to the "code" section of the desktop app  
  
Step 5: Paste in that github link from above and tell Claude Code to help you set everything up.  
  
Step 6: Start cloning video ads for your own brand  
  
DONE  
  
This Claude agent also works with other models like Nano Banana, VEO 3.1, Sora 2 and more! It can create image and video ads without you needing to write a single prompt.  
  
This agent currently is connected to the arcads api so you'll need an account. If you don't have one, you can sign up here:https://arcads.ai/?via=caleb  
  
I'm currently building out this system to support even more APIs. If you want to level up your media buying systems, consider joining my private skool community.  
  
Join my skool: https://skool.com/mrpaidsocial  
  
If you have any ideas on how to make this better or a use case you want to try. Let me know in the comments!  
  
Chapters  
00:00 Intro  
01:42 How To Use Seedance 2.0 With Arcads  
06:24 Seedance 2.0 Examples  
08:58 Unboxing Video Ad  
09:31 App Ads  
10:48 Outfit Try On Ads  
11:50 Real Estate Walkthrough  
14:34 Green Screen Video  
15:55 Street Interview Ads  
17:38 Claymation Style Ad  
19:07 Post It Note Ads  
21:43 Time Lapse Ads  
24:10 Prompting With Claude  
24:41 Claude Code Integration  
28:20 Repo Installation  
32:08 Claude Code + Arcads  
38:07 Studio Quality Ads  
41:18 Live Demo Walkthrough  
52:12 Reference Audio Use  
53:21 Outro

## Transcript

### Intro

**0:00** · I just found a way to clone any winning ad on the internet in minutes. No writing prompts, no copy-pasting between chat GPT and your ad tools, and no hiring creative strategist. I literally mean grab an ad that you found in the wild, drag it into Claude code, point it at your product, and it spits out a full-blown video ad that matches the vibe, the pacing, the shots, the dialogue, all of it. And the craziest thing is this all exists as a free repo that I'm going to give you in this video. Literally, all you have to do is copy the link, throw it into Claude code, and it will do all the setup for you.

**0:31** · This Claude code agent connects Arc Ads AI and SeaDance 2.0 to create next-level AI content that has never been able to be done before. In this video, I'm going to show you some wild use cases for SeaDance 2.0, which is arguably the best video model out there right now, and it just dropped. This model is so good that it literally got banned from the US until they could figure out their copyright issues. They got into tons of trouble early on making celebrity videos and deepfakes and stuff. So, you can imagine all the legal issues that they've had to work through.

**1:02** · The model is finally live through Arc Ads, and with this Claude agent, what you can create will absolutely blow your mind. I'm going to show you a bunch of wild use cases inside of Arc Ads.

**1:13** · Unboxing videos, street interviews, real estate walk-throughs, ASMR videos, claymation ads, green screen hacks, time lapses, you name it. Then I'm going to show you exactly how you can set up Claude code on your machine to recreate any ad you can imagine. No more burning through credits trying to figure out how to prompt correctly. I've distilled this entire process down to a perfect science within Claude. And if you run ads, this is the video you've been waiting for.

**1:39** · Five creative is here, let's get into it. All right, so I'm going to show you exactly how prompting this thing works inside of Arc Ads. So, I'm in my Arc Ads account. I've got a project here for SeaDance 2.0. You can see all the videos that I've been generating. And on the bottom here, we've got settings. Right now, we're selected in video.

### How To Use Seedance 2.0 With Arcads

**1:58** · And there's all these different models.

**2:00** · You've got Sora 2, Sora 2 Pro, Kling, Kling 3.0, uh Vio 3.1, uh SeaDance 1.5, and Grok video. Obviously, today we're talking about SeaDance 2.0, so you can select that. There's different aspect ratios. You can be 9 by 16 or 16 by 9.

**2:16** · Length, it can go from 4 seconds all the way to 15 seconds. The price varies depending on how long you make it, so keep that in mind. Also, the price, I believe, varies between 480p and 720p.

**2:29** · So, right now, if we do a 10-second, I'll just say like blah blah blah blah blah, whatever. Um it's 0.6 credits. And then if we switch to 480p, it drops in half. So, if you're making content for social and for ads, you really don't always need it to be high quality anyway. So, quick tip for you if you're trying to save on credit costs is generating in 480p because it's going to be on social media anyway, it's going to be on mobile devices, it'll look just that much more realistic and not AI.

**2:55** · I think sometimes if it's like 4K, it's actually easier to tell that something's AI versus lower quality. So, anyway, quick tip for you there. And then, yeah, as in terms of like how you prompt this thing, it can take multiple reference images, multiple audio references, and multiple video references. So, a lot of this is brand new. Brand new to how you can create AI-generated content. We had with Vio 3 that you could have reference images, but we couldn't have uh reference videos yet.

**3:22** · I think this is the first model out that's released that allows you to have both audio and video now, which opens up a whole like so many opportunities for generating um AI content, and we'll go over those later in the video. But, essentially, the way this works in Arc Ads is I can include uh like a video here, so I'll just include a video.

**3:47** · I can include a image, so I'll just let's find a random image. I guess, yeah, it doesn't really matter.

**3:55** · I'll include an image here, and I can include an audio. So, I'll do this audio. So, I can prompt this and say, "I want you to take the reference video in" and then we do slash, and then you can see here now we can select which image, video, and audio we're referencing. So, I can say video one.

**4:18** · So, I want you to take the reference video in video one as the vibe for the video we're going to recreate. I want you to replace it with the product from image one using the audio from audio one.

**4:37** · So, in this example, like I didn't include the right references here. I just wanted to kind of use this as a generic example where you can dynamically reference different reference images, videos, and audios throughout your prompt, which makes this thing so incredibly powerful. Where like if you had yourself or another influencer or another video or whatever, like saying a script you really loved the way that they they delivered that script or like like the way their voice sounded or whatever, you could include that as the audio for the video you're creating.

**5:07** · But maybe you wanted to swap them out with a different character or in a different vibe or holding a different product or whatever, that's where you include a different image reference and say swap out the product.

**5:16** · Or really, there's just like so many different ways you can slice and dice those three variables to create unique videos almost every single time. You can also use that video reference to expand or extend videos using this model. So, within Vio 3.1, you know, they do have the extend feature where you can extend a video. That's basically all you can do with it.

**5:36** · But here, I could say, "I want you to continue {slash} video one and have the girl in the video saying" and then you could like, you know, XY you could include the dialogue that you wanted them to say in the next section of the video. Or you can say, "I want them to move into this room." Or I want them to pick up this product. Or I want them to fly into outer space.

**5:59** · Like, you can change the scene dynamically, um but have it continue based off of that reference video so that it keeps the character, the lighting, the voice, like everything will maintain consistency from your reference video. This is insane. You can also have it edit videos now, too. So, I could say, um you know, let's say there was Actually, I'll just show you on the SeaDance website super quick a really good example of this. So, here's a really good example of how you can actually edit videos within SeaDance. So, here in the bottom frame, this is the original.

### Seedance 2.0 Examples

**6:30** · There's like a camera in it, and the prompt is remove any visible production mistakes from the video. So, this is the reference video, and you can see like kept everything about the video the same, but it removed the camera from the video. So, you can actually edit videos now. Here's another super cool one where it's using reference images.

**6:48** · So, we've got a starting frame of an empty kind of like, you know, concrete room, and then you include the image of the end frame of like a super well-designed living room, and this is creating a time lapse of that entire transition in real time, which is super cool, looks super slick. If you're doing anything with like real estate or anything like that, this would be really cool to play with. This example is super cool.

**7:13** · Basically, it's you up you're uploading a green screen video of two people fighting with reference images of the characters and saying, "I want you to recreate their motion basically with these two characters in this setting."

**7:26** · So, you can imagine just like how crazy you can get with this kind of stuff. So, now that you know what this model can do, let me show you some examples of videos I've already created specifically for ads. All right, so to kick this video off, we're going to go through some of the examples that I've already put together using SeaDance 2 within arcads.ai. This first example is an influencer video of somebody unboxing a fictional pair of Mr. Paid Social Vans that I put together. Check this out.

**7:53** · know what time it is. It's that time again for another first look. Today, we got the Mr. Paid Social sneakers. These are super dope. I'm a big fan of the black and white colorway. These are super clean. I can't wait to rock these. I'm a big fan of these.

**8:08** · Pretty incredible. I mean, the prompt I used was literally create an influencer try-on video promoting these shoes. And the way you, you know, do this in Arc Ads, I'll show you, is you upload your reference image here, and then you reference your image in the prompt for Arc Ads. So, this is image one. If I had a second image in here, maybe of some, you know, the shoes in like a street setting or on a bedroom floor or whatever, um you can include, I believe, it's up to nine reference images here.

**8:38** · And then you can say exactly how you want each one of those reference images to be used in the prompt, which is pretty insane.

**8:46** · Um you can also add things like audio, um video. We'll get into how to use all of that later in the video, but you can do some pretty incredible things with prompting. All right, next up we've got unboxing videos. Here's the prompt: Create an unboxing video for image one having it be a POV style video, ASMR style, with high gain on the sounds of the box opening, paper crinkling, etc.

### Unboxing Video Ad

**9:11** · No music, just the sound of the packaging. Check this out. You've got the sound of the crinkling tissue paper, sound of the plastic. That turned out pretty awesome, I would say. All right, this next one is really a cool use case.

### App Ads

**9:35** · So, if you're promoting an app, you can essentially go to your website, grab, you know, any screenshots you have of your app in the phone, and then use that as a reference image. So, here, I'll show you in the actual prompt, I have "Using image one, create a creator style video of an influencer holding their phone and showing off this app." And then I include the URL to the app with a reference image of the actual app. So, I'll show you what that looks like. So, I literally grabbed this like hero image of multiple screens from the app and just downloaded that.

**10:05** · So, here's what that looks like. This app is amazing. It has so many features that make studying so much easier. I can highlight important information, add my own notes, and even create flash cards to help me remember everything. Go check it out and download it to your phone. Like the fact that it put this the like crappy screenshot even it wasn't even like a cropped screenshot or anything. It was a crappy screenshot.

**10:31** · It was able to put that into the iPhone.

**10:33** · It wrote the script for it. It had bouncing shots from the influencer back to the phone, back to the influencer, wide angle, close up. Like it just did it all like a 15-second clip. And literally this was the prompt. Use the image of and create a creator-style video of the influencer holding their phone. All right, this next example is also pretty crazy. Um it's basically I'll I'll show you how I put the prompt together and what I used for it. So, here I don't know if you can tell if I zoom in. There's like this collage image here of like a bunch of products.

### Outfit Try On Ads

**11:05** · Basically, I just This is a fictional collage of photos, but I was like make a outfit that a Gen Z would wear basically. And it was like make it Mr. Paid Social branding. So, I said a lifestyle ad that looks like something you might see on Instagram of an influencer wearing these products, fast paced, natural lighting, iPhone quality. Check out how good this turned out. She's wearing the sweatshirt. The sunglasses, the jeans, the shoes.

**11:34** · It added music.

**11:37** · Like it's got Like that looks like a legit content creator put on that outfit and just like put something together for TikTok.

### Real Estate Walkthrough

**11:50** · Insane. All right, this next one's a cool use case for any real estate folks out there. So, literally all I did I went to like Zillow. I grabbed three images of like here's the kitchen, here's the living room, here's the front of the house. Like this is an actual house on listing right now on Zillow. Um and I said a real estate walk-through video of image one, image two, image three. And here's how that turned out.

**12:12** · Check this out.

**12:14** · Welcome to this 1969 mid-century modern home in the desirable Lake Wilderness neighborhood. The main level features a gorgeous kitchen with stainless steel appliances and quartz countertops. The great room has vaulted ceilings and a gas fireplace. Welcome to So, obviously like it messed up saying counter taps or whatever.

**12:34** · Um but like I didn't even include the dialogue. If I wanted to be really specific here, I could have included exactly what I wanted them to say. I could have included all I could have included a link to the listing and it probably would have scraped it for more info. I could have included the description from the listing in here, but I think the takeaway here is like you can just kind of throw in real estate photos and say create a walk-through video and it will turn out pretty pretty good.

**12:56** · Um and an awesome like hack here with C Dance 2.0 is I could actually if I wanted to continue this like if I wanted longer than a 15-second video, I could download this video. So, I'll show you real quick. I'm going to download this video and then I'm going to go to remix here. And then basically what you can do is you can include the video. So, if I remove these images, select C Dance again.

**13:25** · Select 15 seconds. And then I include this video. So, you can actually include Welcome videos now. You can include videos now as references for your prompts. So, I can rewrite this prompt and say continue the walk-through video from and then I can hit slash and select this video as the reference into the following rooms.

**13:54** · And then I could say I could include three more images here from the listing and say go into this room and say this, go into this room and say that, go into this room and say that. And you could just basically build out an entire walk-through. It could be like a minute long and it would be totally consistent. Like you'd have the same person doing the voiceover, it'd be the same style. And you could end up with like a full-blown walk-through video for like 40 bucks, which is insane.

**14:17** · Considering normally you'd have to hire a crew to come to you the listing with their expensive camera and gear, pay them to film it, pay them to edit it. I have videographer friends in the real estate industry that do this and they charge thousands of dollars to do basically this. So, pretty insane.

### Green Screen Video

**14:34** · All right, for this one I want to see how C Dance would do with a green screen video. Um it didn't quite get it exactly, but I'm going to show you a little hack that I did to get really the end result that I was looking for with very minimal effort. Here I said using image one. So, image one is basically a screenshot that I took of my private school community like the about page. Um I want to generate a TikTok-style green screen video of an influencer talking about why you should join my community on school, points out different parts of the landing page behind him the influencer. Um perspective is selfie style with arm extended towards the camera, iPhone quality.

**15:04** · So, I liked what it gave me in terms of the influencer, but obviously it messed up on the whole like green screen concept of it. It just kind of like threw it on the wall behind them. So, what I did was I downloaded this video from our cats, just tossed it into CapCut. There's a button that lets you just remove the background. And then I just threw my actual what I put here behind it as a green screen. I just created the green screen video, but check out how good this turned out.

**15:29** · Inside the AI Ad Alchemist community.

**15:30** · This is where you can come to leverage AI and automation to finally scale your ads. So, you can increase your ROS, save time, and scale your ad operations. The influencer's performance here or like the AI avatar's performance here, it looks like a real person. Like his hands are moving. He's looking He looks like he's talking into his camera. Like if I didn't know this was AI, Inside the AI Ad Alchemist community. This is where you can come to leverage AI and automation to finally scale your ads.

**15:52** · Like I probably wouldn't know. Pretty incredible. All right, this next one's kind of fun and honestly it's a ad style that I've been seeing work really really well for folks.

### Street Interview Ads

**16:02** · buddy in the industry who's like pivoted his entire business to literally just doing street interview creatives for brands. So, I wanted to see if we could recreate this with C Dance. So, here's the prompt. Generate a street interview style video of two young males approaching a group of young females and asking them what they think about Mr.

**16:19** · Paid Social. So, obviously like we could have prompted this to like ask them about your product or I could have put in more dialogue here to ask some specific questions and you could use that for your ads. But like just look at how good this turned out.

**16:31** · Today we're asking people what they think about Mr. Paid Social. What do you ladies think about Mr. Paid Social?

**16:36** · I think he's really innovative. I don't think his targeting is as effective as it could be. I heard he's a vegetarian.

**16:44** · I'm actually not a vegetarian, so she's wrong. But yeah, that I mean that turned out super good. And again like this prompt was very very simple. Like I didn't go too crazy with it. You can create ASMR-style videos with this model. So, this prompt. ASMR-style unboxing of image one, which image one was just a product image of this Mr.

**17:04** · Paid Social Cola. No music, just high mic gain and influencer whispering. So, check this out. It's probably going to make you I don't really like ASMR, so it makes I don't really like listening to it. But check this out. slaps. You know what I mean? Like that's what I'm talking about. That's what I want to see.

**17:25** · Oh my gosh.

**17:28** · Look at that.

**17:31** · It's the fingers. like that. Yeah. The fingers on the can and everything. It just like it nailed it. So, I've been seeing a ton of these like Pixar or claymation-style cartoony ads out in the wild. Um mainly for like supplement brands, health and wellness brands, pharmaceutical companies, um what have you. Because it's really easy to create with AI and they're a little bit more engaging and and whatnot.

### Claymation Style Ad

**17:56** · I think Dara Denney made some content recently talking about like the breakdown effect of like why these actually perform really really well for brands right now.

**18:05** · But I wanted to see if we could recreate it with AI using C Dance. So, check this out. Um create a claymation-style narrative ad explaining the risks of heart disease in men and how image one can make all the difference. So, image one here is a supplement fictional supplement that I made with Nano Banana with Mr. Paid Social branding. So, check out how this one turned out.

**18:23** · Heart disease is the number one killer of men. But the right vitamins can make all the difference. Introducing Mr. Paid Social, the premium daily multivitamin that helps support a healthy heart.

**18:38** · Heart So, that one I mean I thought it turned out pretty good. The motion was good. There's like a voiceover, the guy looks concerned. You bring in the product. Obviously like we could have gotten way more descriptive in our prompt and probably had like some variances in the cuts and everything.

**18:54** · But also if you wanted to continue this story, this is where again we can simply download the video, include it as a reference for the next prompt, and just continue the story along. So, there's a lot you could do with this. Okay, this one is a really interesting use case and I think something that a lot of people can actually use pretty well for their ads. So, I found an ad in the wild from a brand called Javy. They're like a coffee brand or whatever.

### Post It Note Ads

**19:22** · And I wanted basically the video was like a real person. There was posted notes on it with like callouts. And the person is just ripping off one posted at a time and it's revealing like, you know, it's like real coffee, it's good for you. Like the feature benefits of it basically. And so, I was like I feel like I could recreate this using C Dance. So, I gave it a try. So, first thing I did is this is a screenshot of the video of just like the vibe and the brand you know the the the coffee, all that stuff.

**19:54** · And so, what I did is I tossed it into Nano Banana 2, again with an Arc Ads, and I prompted it to change the brand name to Mr. Paid Social, have the girl be blonde, have the post-it say, "This is 100% AI." right? Um so, if you had a completely different product here, you could have put a completely different product. If you wanted to change the appearance more, like there's a lot you could do with it. But, just check this out. So, uh this first one I say, "Have this ad be 100% AI." Then, I continue prompting it, "But, you would never know."

**20:25** · So, then it creates the next frame, and this one says, "I'm about to show you how." right? So, we've got three images with three different post-its. This is where SeaDance gets really, really cool in what you can do.

**20:37** · So, here, I've got a prompt that says, "The shot start" I should have said starts, so I had a typo there, but um with image one, then the woman's hand pulls off the first post-it note to reveal image three, and finally pulls off the next post-it to reveal image two. So, um here, like image two and three is just the reference of the way that they uploaded into Arc Ads. Um but, check this out. It actually worked.

**21:06** · Like it did what I wanted it to do. It had the person pulling off the post-its notes. Um you know, if you wanted to, like you probably I probably could have gotten a little bit more creative with my Nano Banana prompting in terms of like the font, making it look a little bit more um messy. I think this turned out like a little robotic or a little like printed-looking. I think it still looks great.

**21:29** · Um but, like compared to the original, it's like, you know, real handwriting is a little bit you know, I can tell the difference, maybe not everybody can.

**21:38** · Um Anyway, I thought that actually turned out really solid. So, this next one, you know, I see these videos all over the place on like Facebook and Instagram, but there's these like time-lapse videos that show people like doing construction work or doing a home remodel or whatever. Um there's a lot of use cases.

### Time Lapse Ads

**21:59** · I feel like you could use this with ads, like if you were like a home design company, and you want to show off like how you can transform a space and have it be like a a time-lapse and all that. But, um so, what I did here is I had a picture on my phone of like the woods, you know?

**22:18** · Um and so, I just uploaded it, and I said, "Nano Banana 2, put a beautiful treehouse in the woods with a spiral wooden stair going up." So, I have a bunch of these to choose from, right?

**22:29** · So, what I did is I took the starting frame, so basically the picture of the woods without the treehouse in the woods. And then, I had the second reference image be the treehouse complete. And the prompt is, "A time-lapse video showing the constructing of the treehouse, where image one is where it should start, image two is where the time-lapse should finish, and the video with a walk-through of the interior." Check this out.

**23:14** · Pretty sweet.

**23:16** · Pretty sweet. And then, um I wanted to actually see if this would work. So, there was another one of these videos in here. So, in this version, I have it end with this walk-through, and it kind of like goes in, right? And I wanted to see if I could continue this.

**23:30** · So, I downloaded this video, uploaded it back into SeaDance, and said, "Continue the walk-through of the treehouse from video one, add dialogue of people talking about how happy with how the treehouse turned out." Let's check this out. So, it's continuing on where that video left off.

**23:47** · It's so much better than we ever thought it would be. You think the kids will like it? I know they're going to love it. Like pretty crazy. Like it's just continuing on from where it left off, even like had the same like piano vibe from the music from the first video. So, you could put them together, and it would feel like one fluid, continuous video. All right.

**24:09** · So, now we're going to like switch gears a little bit here, and I'm going to show you some crazier use cases here, right?

### Prompting With Claude

**24:15** · As you can see with this one I have up here, this prompt is significantly longer than the ones I've been showing you so far. The ones I've been showing you were kind of like my lazy prompts, like I wanted to just see what the model would do, giving it kind of more creative freedom. Here, I wanted to see how the model would do with a very refined prompt. I don't write these prompts from scratch. Nobody does.

**24:34** · Nobody's sitting here like writing out paragraphs for prompting. Um so, this is where Claude Code comes into play. And I'm going to show you how we can connect Claude Code directly into Arc Ads AI through their API, where Claude Code

### Claude Code Integration

**24:51** · will write the prompts for you, it will structure the videos, and it will upload them into the API to process all the videos and the creatives for you, so you can do everything within Claude Code and not have to be copying and pasting back and forth and like sending screenshots back and forth from AI or like the way we've historically done this is I've put together like a custom GPT or something, where there's prompting guidelines, and then you're kind of bouncing back and forth between a chat and Arc Ads. Now, you can just do it all within Claude Code, and it works so freaking well. All right.

**25:23** · So, the first step here is you're going to go to this repo on GitHub. I've published the entire Claude Code agent with the skills and everything in here. So, literally all you have to do is copy a URL, throw it into Cod- Claude Code, and it's going to set everything up for you perfectly. Um this comes with kind of instructions here inside of GitHub. If you've never used GitHub or Claude Code, I promise you it's not that hard, and this is probably the use case you've been waiting for to give it a try.

**25:53** · The link for this is in the description below, so grab that right now. And then, once you have the link, essentially all you're going to do is copy the link. You're going to go into Claude, and at the This is Claude Desktop, so you want to download the Claude Desktop app on your computer, not go like don't do it through Claude on the mobile or sorry, on the web app.

**26:17** · Um there's more power that you get from the desktop app um for this use case. Like it'll actually download things to your drive, and you'll you'll see why it matters. Um you don't You could also run this in terminal. If you're one of those folks that uses Claude Code in terminal, I personally prefer using the desktop app. It's just a little bit cleaner, and terminal scares me um probably like most of you watching this video.

**26:39** · So, anyway, here's how it works. You're going to first go into your computer somewhere, right? And I want you to just make a folder somewhere, call it like coding projects or Arc Ads or AI or whatever. You just make a folder somewhere in your computer. I have one that's called coding projects, and my folder for Claude and Arc Ads is called Arc Ads and Claude Code. So, this is the folder that I work out of whenever I'm using this tool. So, you're going to create a folder, and then you're going to go here, click new session, right?

**27:13** · So, there's nothing in here. At the bottom within Claude Code, you select a folder. So, here's where you can select that folder you just created. So, I'm going to go to coding projects, Arc Ads and Claude Code, open. So, now you can see we've got a folder selected here. We want it to be local, and don't worry about this stuff yet. So, here um is where literally all you're going to do is paste in that URL from GitHub, and tell Claude, "Please set up this repo on my machine."

**27:44** · And then, it will like the the repo already has all of the instructions and everything that's needed to set this up for you, and it's just going to go. Um I'm going to show you what that looks like. Just to show you the full example, I'm going to create a new folder on my computer and call it Arc Ads plus Claude um demo, just so you can see how this will work in your own computer. Let me pop back into Claude. I'm just going to change it to that folder.

### Repo Installation

**28:20** · Okay. So, we've got our folder open. You can see like there was no GitHub connection here because there currently isn't a repo installed in this folder yet. Um so, yeah, we've got this GitHub link. I'm saying, "Please set this re- repo up on my she- my machine." And I'm just going to click go. I like running my Claude Code in bypass mode, um which basically just means you don't have to constantly like approve things when it asks you for them.

**28:45** · It is more dangerous, so just make sure you understand the risks before doing that. Otherwise, you're going to have to kind of sit here and babysit it and be like approve, approve, approve, approve, approve. Um so, right now, it's, you know, it cloned the repo for me, and we're setting up the instructions on setting this all up. So, while it's working on that, pop over back to Arc Ads, log in or sign up if you don't have an account, just log in.

**29:12** · Now that you're logged in, you're going to go to settings, and then here in settings, there's this public API. So, here, you would click get new credentials, and then it would give you a client ID and a client secret.

**29:27** · So, here, we're back in Claude Code. It looks like it set everything up for me, and now it's just saying that we need that Arc Ads API key, and to add it to the .env for you. Um normally, it's supposed to open the .env file for you and show you where to paste it in. It didn't this time, so I'll make sure that's fixed, but if it doesn't do that for you, just say, "Please open the .env file on my desktop so I can paste it securely in there."

**29:59** · Um by rule of thumb, when it whatever you're working in something like Claude Code, you don't want to paste API keys in the chat windows. It's just less secure. Okay, so I asked it to open up the .env file and you can see it all opened up here just in a text editor and it has a couple things where it's like shows you where to paste it in. So, here is where you would paste in your API key. Um you can also include your client ID and all that good stuff here. Um but once that's done, all you have to do is close it and then you're set up.

**30:29** · So, it all it needs is that API key in that .env file and then it can basically structure all the calls for you to upload everything into Claude or into Arcads. This Claude Code agent is loaded with the prompting guidelines as well as multiple templates for everything I'm about to show you where you can recreate it just by simply asking it to create a video with your product. So, here's an example of what I was able to create using the Claude Code connection here. Check out this video.

**31:00** · Bro, these finally came. Look at this. The details are crazy. Suede on the front, the blue pop on the back. Come on. The fit is perfect, too. Not even going to lie.

**31:14** · These are not leaving the rotation. Like it had multiple shots. I didn't write the dialogue. I didn't do anything. All I did was popped over into Claude Code, added a reference image of my product, and said, "I want you to create a UGC style video for me." And then it went and crafted this prompt, fired it off into Arcads for me.

**31:37** · Like I didn't even have to copy paste anything. Insane. All right, here's another one with that same pair of Vans like Mr. Paid Social branded Vans. Check this out. Bro, these finally came. Look at this. The details are crazy. Suede on the front, the blue pop on the back. Come on. Fit is perfect, too. Not even going to lie. These are not leaving the rotation.

**32:00** · Also, if you want if you think I should make Mr. Paid Social branded Vans, let me know in the comments cuz I kind of want those. All right, so here is where this can get really, really cool using Claude Code and Arcads. So, I found this ad in the wild and I wanted to see if I could just have Claude Code recreate it for me.

### Claude Code + Arcads

**32:21** · Check this out.

**32:22** · Classic crew tricks by Mott &amp; Bow. By far my favorite tees. So comfortable.

**32:27** · They hide my belly and my man boobs and enhance my pecs and shoulders. They have a super sturdy binded neck that will last for years. So, So, you get the point. It's like a bunch of shots of people like touching the fabric and there's like dialogue over it, voice over, music, all that good stuff. So, what I did, and this is something I just added to this repo and you can use it right now.

**32:50** · Um if I scroll up here, I had it create a new skill where it will analyze the video for you.

**33:01** · Like I'll I'll show you exactly what it did. I wanted it to So, I I referenced the the like video that I just showed you and then I wanted to see how it would work with this Mr. Paid Social T-shirt that I This again, this is fake. I just used Nano Banana 2 to put this together, but I wanted to see if it would basically recreate that video but with my product and have it look and feel almost exactly the same. So, first, it analyzes that source video. So, it's like 39 seconds long, eight beats, 118 words. So, Claude Code is able to transcribe the video.

**33:31** · It uses something called FFmpeg to extract multiple frames from the video so it can actually like understand what's going on visually. And then it does this whole like analysis of that video. We're basically going to clone it. So, what transfers to my product, it's going to keep the hands-on face, the beat structure, the physical proof, jump cut, per beat pacing, all this good stuff. It's going to change the Mott &amp; Bow tees to my Mr.

**34:01** · Paid Social. The future claim's going to be different, all this good stuff. Um it asked me like to approve the dialogue, so I could have put in my own dialogue. I just had it write dialogue, so it handled that handled that all for me.

**34:14** · But part of this is you actually like get presented with a full like script and dialogue to approve. Um I approved it all and then it fires it all off into Arcads for me. So, it creates a new folder here and you can see like all of the different um video clips that it made for me. And then what I had it do is I tested and this is what's crazy.

**34:40** · I wanted it to create a 15-second version that was just kind of like the essence of it but like a shorter version. And then I wanted to it to recreate the entire video with multiple clips and then also as a last step, stitch every single video back together for me into a folder. Long story short, went through all this stuff and it did it all and let me show you the final result. Okay, so it opened the folder for me so I could see everything that it made. So, I've got all of those assets finished right here on the left. This is Claude Code on the right.

**35:10** · I'm going to show you the fully stitched version first. So, this took the three different videos that it generated for me in Arcads, stitched them together. Check this out. This is the Mr. Paid Social T by Gen Z Threads. By far my favorite graphic T. Vintage wash, super soft, heavyweight cotton. Look at this collar. It's thick. It's binded. No bacon neck ever. 100% organic cotton. This thing is built to last.

**35:39** · Row AS emoji, master of the algorithm, driving clicks and conversions. If you run ads, this is your T. Goes with everything. Jeans, joggers, layer it under a hoodie. It's a So, we've already gone through two separate clips and you probably didn't even tell that we switched to new clip. It was flawless. Vintage wash, so it looks broken in from day one. Size medium fits perfect. Not too slim, not boxy.

**36:07** · If you run paid social, you need this T. Link in bio. So, it put together a whole script. It generated all the videos. The vibe I would say was like pretty spot-on in terms of what it was able to do from that reference video that I gave it.

**36:22** · There's a couple little things, right?

**36:23** · Like the the tag or you know, that text got kind of jumbled. Um you know, I might have Like if I wanted to solve for that, probably what I would do is include a reference image of the starting frame and approve that first so that you're happy with the way like all the text on your products looks before the like the full video gets created.

**36:44** · Um that's one way that you could kind of safeguard against that. And that's something that you could tell Claude that you wanted to do. Like you could literally just say like, "I want you to generate the starting scene images using Nano Banana 2" and it would just do that for you. Um I'd fire those off into Arcads, give them back to you to uh so you can review them. This is basically like vibe coding but instead of vibe coding, you're vibe AI creative-ing.

**37:08** · Vibe creating. Like it's just so crazy now how far we've come from like having like custom GPTs to now having full-blown like AI agents that learn with you. Like as I use this, if there's something that I'm like, "Oh hey, um commit this to a skill." It'll just save it as a skill and then it will do that exact same thing again for me. So, now if I if I after all this, if I was like, "Okay, I want you to save this exact like creative template as a skill that I can call back and use again."

**37:40** · And I've done this. I'll show you exactly. Like in the project files, there's all of these skills and like I have one for a feature walk-through, a premium reveal, a product hero, a studio look back, a UGC video. Like anytime you clone a video with this, you can have it commit that clone to a skill and then call back to that skill as a template, which is pretty incredible. I'm going to show you a couple more examples here. All right, so here's another example where I found this video ad in the wild. It's like very like studio quality.

### Studio Quality Ads

**38:14** · You know, there's like shots of someone trying on the product in front of a studio backdrop with studio lighting and there's audio and all that good stuff.

**38:25** · And what I did, same process we just went through, I took this video, I tossed it into Claude Code and was like, "I want to recreate this video and I want it to be a template that I can use again." So, it did that and then all I had to do was have it recreate this video but for this brand of Mr. Paid Social hat. Again, fictional product that I just created, but like I'm going to play both here, but I'm going to play this one without sound so you can get a sense of like how well this nailed the vibe. So, here's the reference. Here's the new one.

**38:57** · I've been looking for a hat that actually has some character. The corduroy, the color blocking, the patch, the Mr. Paid Social camp cap just hits different. I've been looking for a hat that actually has It's so good. It did such a good job with everything. The lighting, the pacing, the multiple shots, like the zoom on the actual product. Like look how good that Like it looks like a real hat. You can see the stitching.

**39:25** · This was a image. This was like an image that I just made on Nano Banana 2. This This doesn't even exist. This product is not real. And it made it look so freaking good. All right, here's another example where I found this like um Solo Stove ad in the wild, it was like super cinematic and I just tossed it into Claude code, asked it to recreate it with my hat.

**39:49** · Check this out.

**40:07** · Like did a pretty freaking good job at making a cinematic high-quality looking product shot style ad. Okay, so here's another one that I had Claude code clone for me. Um, essentially this is like an influencer talking about like all of the different product features and benefits of a product while demoing it out. Um, so here's the Claude code Arc ads clone with C Dance 2.0. If I could only wear one hat for the rest of my life, this is it, no question.

**40:36** · Three-tone corduroy, woven patch, and this adjustable strap, so it fits anyone.

**40:43** · Absolute staple.

**40:44** · And that was only a 10-second long video. Like, we could have done a 15-second long video, we could have done multiple of these where like it continued on with like I think this video what is like 36 seconds long.

**40:58** · Um, so like we could have had this, you know, continue on with more of the feature call outs. I could have lit had it list all of them. Um, but you know, like I mean, in this video you saw how he takes the hat off, he like stretches the band, like talks about the features as he puts it back on.

**41:17** · Flawless. All right, so let's run through an example of using Claude code with Arc ads live so you can see the entire process from end to end. And to get the examples that we're going to use and where I often look for like good inspiration for ads is I'll pop into Motion. Uh, if you've never checked it out, Motion and Analytics, they've got this um, Inspo tab here and it's so insanely helpful. They've got this visual format here.

### Live Demo Walkthrough

**41:42** · So if like I want to find examples of any of these styles of ads, I can just click on one, so I can click on like testimonial and it'll show me all these testimonial style ads. So for this, I want to be doing video since that's what we're doing for this video.

**41:59** · Um, I can filter by days active. Let's say it's been active for 3 months, so that's, you know, more likely to be a top winner. Product type, we can choose between all these different styles. I'll leave it open for now. Okay, so I just found this ad from Motion. It's for like a anti-wrinkle face mask.

**42:17** · You're not just losing your smooth I like the vibe. It's like, you know, voiceover, she's talking about the problem, demoing the product, all that good stuff.

**42:27** · Um, so I'm going to download it and we're going to try and clone it. So I've downloaded it onto my desktop. Now all I have to do is drag it into Claude code and I'm going to ask it, please clone this video for my product. And for this one, I'm going to use my Mr. Paid Social Collagen Peptides powder. So I'm going to drag that image back over to Claude code, drag it in, and so I'm So I'm saying literally just, please clone this video for my product.

**42:54** · I'm going to press enter. So you can see it's starting to extract the frames.

**42:59** · It's going to transcribe the audio with Whisper, analyze the frames, and present a summary, decide the mode, adopt the prompt dialogue gate. Um, it's going to tell us the audio it's going to use, an estimated cost. So you can see look, it's like taking screenshots of all of the frames to understand the video dynamically. And this process might take a couple minutes in Claude code, but here's the beautiful thing. I you can have multiple agents doing this for multiple videos for me in parallel within Claude code. What does that even mean?

**43:30** · It means that I can create a new session, have my folder selected for Arc ads in Claude, and I can just whip up a whole new session where it's creating a new ad for me in this session. So I could have really unlimited number of different instances of Claude code all creating different clones of different ads for me in real time. So it literally Yeah, this is wild.

**43:56** · It literally extracted 12 screenshots from the video so it could better understand the context. Now it's done that, you can see it's kind of like put all this information up here, but it's prompting me, how should we handle 26 seconds to 15 sec- seconds compression?

**44:11** · It's asking me if I want to create a 15-second clip or if I want to do two clip series problem payoff or both versions. Um, for this, since we're doing some show and tell here, let's do both versions where it's going to create a 15-second version and it's going to create a two clip series for me. This is wild. It shows like the entire beat map of the video defining traits.

**44:35** · There's a problem problem solution narrative arc, mixed media cuts, voiceover narration, and we've got handheld phone, multiple locations from the bathroom, bed, couch, white wall, mixed framing, face close-ups, overhead lifestyle shots. The tone is empathetic, confident, aspirational. Starts with I feel your pain, shifts to here's the answer, ends with you deserve this. Like it's putting that video into a formula.

**45:02** · Like it is recreating how that video works and like I'm I'm really excited to see what it comes up with. Okay, so we've got both versions. Version A, here's the 15-second clip. It gives us the dialogue to approve. So problem, your skin is losing collagen every single day. Um, and again, I just include a product image of my like Mr. Paid Social Collagen supplement thing that I made up. Like, you could include so much more context.

**45:27** · You could include the website URL, you could include like the description of your product, you could include like so much context so that it could write even better dialogue that would be like specific. Right now it's kind of making assumptions based off of just the image that I gave it. Uh, the pain point, expensive serums, treatments not cutting it. Silent scoops collagen powder. Uh, one scoop a day, visibly healthier skin in weeks. Mr.

**45:53** · Paid Social Collagen, your skin back.

**45:55** · Cool.

**45:56** · So 30 words, going to be 15 seconds, fits at natural pace. Cool. Then we've got the two clip version, which is basically just longer with more dialogue. I'm going to go ahead and say yes that I approve the dialogue. If I didn't, I could just say, hey, change this, actually I want to say this. Like you can go back and forth with it.

**46:14** · That's another thing that's I think really awesome about using Claude code for this is there's it's like you're working with an employee, like a creative strategist, really. Like an AI creative strategist that you're just like iterating on in real time to get hopefully what will be the perfect output here. And like I don't know how this is going to turn out. This might be a complete failure and I might be like really embarrassed, but we'll find out soon. It's firing off all three clips into Arc ads right now.

**46:44** · So if I go, it makes like a new folder for the API calls. So let's see. Okay, it's giving us an estimated credit cost now saying like what each is going to cost within Arc ads so that you're not just getting surprised with a crazy amount of credits being taken from your account. I accepted, so let's take a look at Arc ads. All right, so here we can see it's generating the media in Arc ads. We've got the whole prompt here. So take a look at. Yeah, this is something like you could also ask Claude to give you before if you wanted to review like the entire prompt.

**47:16** · If you've ever done any like vibe coding or any then or anything like that using APIs, you know like they can be kind of a pain in the ass sometimes and this is another thing that's just so awesome with Claude code is like it ran into an issue where like the image it was using as the reference expired in the API and so now it's just like retrying for like it's just going to keep iterating and re- trying until it gets you to what you're looking for.

**47:42** · All right, so we have one of the versions done. Looks like it's still working on some of the like multiple variation ones, but let's check out this one. Your skin is losing collagen every single day and you can Damn.

**47:59** · Expensive serums, treatments, creams not cutting it. We found a better solution. Mr. Paid Social Collagen Peptides powder. Your skin That I mean, I feel like it nailed the vibe pretty well. Like there was a couple things I noticed like all of these products said Mr. Paid on them. Um, so like you know, maybe I would have included a reference image of a counter or something um, that we could have used.

**48:29** · But the actress looks UGC. She's on her couch, you know, she's in her bathroom, like she's got blemishes, shadows under her eyes, like she's flipping us off. The phone she's holding looks like a real iPhone. It's not like weird. Overall, very, very impressed with how well this did at at cloning that original vibe. Okay, so now it's taking this version.

**48:56** · This is like the B1 and it's uploading that as a video for the second one for B2. So cool. It's so cool it's just doing that. So if I refresh Arc ads now, I should see the second video starting to generate. And yeah, here it is. You can see it's starting to generate. You can see the prompt that's with it.

**49:22** · Um, it includes the video as the reference and now we're just waiting for the second video to generate.

**49:29** · And it's going to pull it, download it, stitch it with the first one, and give it to us to review. While we're waiting on the last video to finish generating, I wanted to quickly highlight that I do have a private community on school called the AI ad alchemist. This community is up to 459 members as of filming this video and we are currently nerding out on all things generative AI for advertisers. This is a vibrant community full of media buyers, agency owners, CEOs, and AI enthusiasts.

**49:56** · I've got hours and hours of content in here as well as guides and templates to help you scale your ads with AI. If you want to check it out, the link is in the description below. All right, looks like the second video finished generating.

**50:08** · Claude code automatically saw that and is downloading them and stitching them together for us. All right, let's see how it turned out. So we've got all of the files here in our computer that Claude downloaded from Arc Ads for us on its own and then we have this stitched version that's 30 seconds long that had like the multiple shots. Let's see how it turned out. Your skin is losing collagen every single day and you can see it.

**50:38** · Expensive serums, treatments, creams, not cutting it. We found a better solution, Mr. Paid Social Collagen Peptides Powder. No more guessing, no more overspending. This is the second video.

**50:53** · in your coffee or smoothie.

**50:55** · Bioavailable, type one and three, visibly healthier skin in weeks. Your time, your money, your skin back.

**51:05** · Dang.

**51:06** · Um that's wild. It like made a full-blown ad for us on its own from giving it a reference. Just think about like how little we had to do to make that happen.

**51:18** · Found a video we liked, threw it into Claude code, said, "Hey, clone this ad for me." Gave it the reference, gave it the product. Like literally all I gave it was this image and it created that video. I could have given it so much more context if this was a real product and I had like Ah, I'm just I'm blown away by how well that worked. So anyway, if you want to use this with Arc Ads, the repo's in the description below. Super easy to set up, you'll be up and running probably in like 10 minutes and then again, yeah, you can run multiple agents, have multiple projects going. This works with um not just C Dance but also VO 3.1.

**51:50** · You can generate images with Nano Banana Pro, Nano Banana 2. Really any of the features that are available in Arc Ads right now are pretty much you can use this for once you give it your API key. So, yeah. This is like the ground floor for you to use an AI agent to do all of your AI creative work inside of Arc Ads.

### Reference Audio Use

**52:12** · All right, one more crazy example of how you can use this model is including reference audio. So, I can record myself saying something, uploaded it as a reference, and then have an AI character say exactly what I said. So, here's an example. I just recorded myself saying something stupid but check this out. So this is my original voice. Holy you guys. This is my real voice and I'm recording it.

**52:38** · But this AI avatar is holding this product while using my voice.

**52:44** · I what?

**52:47** · Holy Okay, so I included that as the reference audio with this image of the Mr. Paid Social um like Vans sneakers. Listen to the voice on this character.

**52:58** · Holy guys. This is so crazy.

**53:01** · I don't This is my voice. Like I'm talking here. Holding my voice.

**53:09** · Wow. Okay.

**53:11** · I don't really know what else to say. Holy When I laughed, it laughed.

**53:16** · He laughed. Whatever. Like what? So crazy. All right, that's all I got today for this video but if you got anything out of it at all, consider subscribing to the channel because I make a lot of content showing you how you can level up your advertising with AI and automation. Also, be sure to check out that private community on school. I'm dropping a lot of awesome stuff in the community right now including this repo that we just talked about. I have a bulk ad system that I'm dropping in the community shortly and so much more fun stuff.

### Outro

**53:42** · As you know, the world of AI and automation right now is changing literally daily so there's always something new dropping in that community. As always, thanks for watching. It means the world to me. I'll see you on the next video.