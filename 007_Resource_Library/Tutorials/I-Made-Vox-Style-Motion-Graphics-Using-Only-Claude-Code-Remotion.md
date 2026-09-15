---
title: "I Made Vox-Style Motion Graphics Using Only Claude Code & Remotion"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=7wuYBfE131U)

Free Skool Community + Asset Pack: https://www.skool.com/ai-visual-production-lab-4976  
  
I built a fully narrated, broadcast-quality "Vox-style" motion graphic using ONLY Claude Code + Remotion.  
  
No After Effects. No Premiere. No timeline. I didn't edit a single frame. Every animated cut-out, every chart that draws itself, every cut that lands right on the word… it's all code that Claude Code wrote from plain prompts. In this video I walk you through the exact workflow, start to finish, so you can do it yourself.  
  
🛠️ Tools used:  
• Remotion (make videos with React/code) — https://remotion.dev  
• Claude Code — https://claude.com/claude-code  
  
⏱️ Chapters  
0:00 — Intro: the finished explainer (no editor!)  
1:30 — Planning: the script & visual style  
2:26 — Building the scenes with Claude Code + Remotion  
8:00 — Assembling & fine-tuning the edit  
11:01 — Voiceover, music & final render  
  
🔔 If this made AI feel a little more easy, hit subscribe — that's the whole point of this channel.  
  
#Remotion #ClaudeCode #AIVideo #MotionGraphics #VideoEditing #AImadeeasy

## Transcript

### Intro: the finished explainer (no editor!)

**0:00** · I made this entire Vox style explainer video using only Claude code and Remotion.

**0:05** · The US and Iran are signing a peace deal. But the downfall of the American Empire has already begun. And it started when a far weaker nation held the Strait \[music\] of Hormuz hostage. Oil prices skyrocketed to $116 a barrel. Pushing American inflation to a 3-year high. And it hit a nation already owing trillion. A debt now bigger than its entire economy. Where the interest \[music\] alone costs more than its entire military.

**0:41** · And the world is quietly leaving the dollar \[music\] behind. Empires don't end with a war. They end with a bill they can no longer pay.

**0:52** · In this video, I'll show you the exact step-by-step on how to recreate this scene. And you don't need an expensive motion designer or know how to use After Effects. In fact, you don't even need to know how to code. So, let's get right into it. So, in order to create this 47-second Vox style explainer, what we need to do is we need to follow a few steps. Now, the number one is obviously your storyboard and script. And essentially, you need your script that acts as the timeline. So, my script over here was obviously the the US and Iran peace deal, which I made a video out of.

**1:23** · What happens here is that each beat maps to a visual. So, this is my entire script over here in a table. So, you can see the voice-over lines, the US and Iran are signing a peace deal, held the Strait of Hormuz hostage, oil prices \[music\] skyrocketed. So, the entire thing is just based off of the voice-over first. And then after that, you can see I've got all of the the foreground assets. There's a midground asset. I've got the prompt as well for both the midground and the foreground.

### Planning: the script & visual style

**1:53** · Because essentially, what I'll be using here is I'll be using an image generator, most probably GPT 2.0 because that's one of the best image generators that's out there. And moving on from there, once you have your \[music\] voice over, the next thing you need to do is you need to lock a visual system. So, in my example over here, I'm using one common background across all of the scenes. I'm using the same fonts, the same accent palette, but what changes is the the mid ground and the foreground where you have these different cutouts that appear.

**2:24** · So, the first thing we have to do is I'm going to open up Cloud Code. Now, over here I'm setting up a new session. Before I start setting up Remotion, what I need to do is I need to make sure I have a few connectors. So, over here I've got my Higgs Field and Magnific MCP service connected. And in order to do that, what you need to do is you need to go to settings. You can go to capabilities, sorry, connectors, and then you can go to customize. And over here you'll find all of your MCP connectors. Now, if you want to add a new connector, what you can essentially do is you can add a custom connector, and then you can get the MCP server address for Magnific, post it in here.

### Building the scenes with Claude Code + Remotion

**2:59** · And essentially what this allows Cloud Code to do is instead of you going to Magnific and getting all of these images, you can just prompt it directly through Cloud Code, and it'll be able to like get all of those images for you.

**3:11** · \[music\] So, for example, this is my Magnific MCP server that's set up over here, and you can see that's the server address right there. Okay, so once you've set up your MCP servers, what you need to do is you need to have a proper architecture, a proper folder structure for your project. So, essentially each scene lives in its own folder. Each scene has multiple props that that come up, and obviously they have a shared background. So, I'll show you what that looks like in terms of a folder structure. So, this is what the scenes look like.

**3:41** · So, if you look at scene one, these are the cutouts that I got from Magnific, and this is obviously the White House, and this is the shared background over here. And then you will see the shared background is in every scene. So, essentially this is the oil tanker \[music\] scene and you've got a shared background here as well. So, it's there in all of them. And then, the only thing that changes is that in each scene, you've got a different cutout, right? And I'll show you how that plays in once we start building these scenes.

**4:08** · So, the next thing I'm going to do now is I'm going to set up the Remotion project. So, I'll just copy this prompt and I'll go here and I'll just set that up. Oh, before I do that, I need to actually select a folder. So, what I'm going to do is I'm going to select the scenes folder over here. Select folder and then just run that prompt again.

**4:33** · So, while the Remotion project is being set up, I'll show you how this worked.

**4:37** · Now, the reason why we have a locked background is because it gives that whole vox style animation where the the background is static, but then things are like moving in. So, it looks like it's one continuous shot instead of like having a \[music\] lot of different cuts in the middle. And essentially, the way how it works is each scene is made up of three layers. So, you have the background over here and then you have the midground, which I choose, you know, as a black and white half tone pattern of characters popping up. And then the foreground structures essentially, right?

**5:07** · So, they can be structures and they can be some sort of scenery, ships, whatever it may be. That's just how I do it and I've seen a few vox animations where they use this style. There are many different styles and \[music\] this is just the one that I've I've gone for.

**5:21** · So, the next thing you want to do is you want to get cutouts of your scenes. For example, over here of Donald Trump and Kamin-A. You don't have to actually go and do this yourself. So, essentially what you can do is you can get a transparent image of Donald Trump or whoever that the character might be. And essentially, what you can do is you can tell Claude code to make the image of Donald Trump in the folder as black and white and give it a half tone pattern to finish. You can see over here as well, like do the same for the image of Kamina.

**5:51** · And this is what you get out of \[music\] it, right? So, it gives that magazine sort of feel, that papery feel, a texture that you would get. Uh so, it doesn't look all digital. I mean, I'm a huge fan of the way how Vox does their animations, and this is just like one way to sort of simulate that. If you go to the scene file over here, and this is what it actually looks like. Okay. So, the way how we're going to do this is we're going to be animating with intent.

**6:20** · And what I mean by that is we're going to be using just two functions. Again, you don't have to know these function calls, you don't have to to necessarily know how to code. But just for you to understand, there's a spring function, and then there's a interpolate. So, essentially, spring is what does the whole pop-up effects and all that. And what happens over here is you don't even have to say to use a spring function over here. So, you can essentially say plain English, "Animate scene one with the White House spring up first, followed by Donald Trump and Kamina right after. Stagger them so they don't all move at once.

**6:49** · Give me an offset red marker stroke behind each cutout \[music\] for the midground characters." And this gives you that signature sort of red sort of stroke just to give it that a little bit of a 3D illusion, and it just honestly just looks nice. So, I will copy this prompt here. So, it looks like Claude Code is still running, setting up the Remotion dependencies. Okay. So, now what it's done is \[music\] it set up the first scene with our characters in the midground and White House in the foreground.

**7:20** · So, I'm just going to let it complete, and then what we will do is we will get it to start a Remotion server for us, or Remotion Studio. And then we'll go inside Remotion Studio, and we need to make a few fine adjustments. All right. So, it's giving me some commands to start the Remotion Studio.

**7:40** · But what I can do is I can just ask it in \[music\] plain English to stop the studio for me. Stop the Remotion studio for me, please. All right. So, this is what the first scene looks like.

**7:52** · And you can see it's not actually the best because we \[music\] need to go make some changes here. So, that's exactly what we're going to do. So, one thing if you notice over here, we've got this error. So, I'm I'm just going to go and sort out this error. So, I'll go back to my Claude code. Uh fix this error, please.

### Assembling & fine-tuning the edit

**8:17** · All right. So, it's fixed that error for us. Now, the next thing we want to do is we want to start adjusting our characters. And this is where it's really important if you don't see these prop controls over here. So, make sure you go back to your Claude code and ask it to give you a prop control for all the elements on the screen. So, this is the prop control for Kamala Harris. What I'm going to do is I'm going to start tweaking some of these scale controls.

**8:42** · So, for example, I can put the scale to 1.4 and you'll see Donald Trump just becomes a bit bigger over there. So, I can change the XY positions. And what you need to do, guys, is also you need to save these numbers as well. So, if I do the scale as 1.4, so you'll see that it's changed the scale, but make sure you save it. So, it stays like that. And then I can change the XY positions here.

**9:04** · But before we do this, we might have to actually change the size and scale of the White House. So, I'll set this to a scale of 1.5.

**9:13** · Okay, maybe I'll make it slightly bigger, 1.6. Save that. And then I'm going to set this uh Y axis maybe all the way down here. So, let's see what that looks like. So, the White House comes first and then Donald Trump and Kamala Harris. So, the White House is fine. Now, I just need to fix both of these characters here. Maybe make the White House slightly bigger, 1.8.

**9:43** · So, I think that scene is done, and that's what that looks like. So, just to run it again, so you have the White House pop up first, and then you have the two \[music\] characters pop up right behind. So, now that we've made those changes, so what you get is a bunch of different scenes. Now, let me show you what those scenes look like. So, you'll see this is like a debt transition scene. So, this is an oil tanker scene.

**10:06** · Now, for this one, what I did was this there's an actual like green screen ocean video that you can download off of Magnific, and essentially, it's just an animated or or like an actual video of an ocean with the background just removed. And this is what that looks like.

**10:28** · And you can see there's a number that comes up right after just to show that oil prices have shot up. So, each scene, guys, would be like in a different file, essentially, right? So, this is the scene for the debt inflation, for example. And you'll see a bar chart, or sorry, a line chart just pops up along with a US map. And then we have a transition scene over here, as well.

**10:51** · \[music\] So, once you have all of these scenes, what you need to do is you need to put them together. After you've done all of your fine adjustments, the next thing you want to do is you want to make you want to assemble a master sequence. So, now you can get Claude code to stitch all of these scenes together in one video in order, each one playing for as long as it's part of the voiceover, so they run back-to-back as a single film.

### Voiceover, music & final render

**11:15** · The next thing you want to do, right after this, is you want to do your voiceovers. \[music\] Now, you can obviously use Claude code to do your voiceovers, but then I go separately to 11 Labs, and I generate my voiceover just because I've got like these saved voices on there. So, let me show you how that works. So, you can go into 11 Labs and you can go to text-to-speech and I use Kate, which is cinematic British RP narrator, and then you can generate the speech.

**11:41** · The US and Iran are signing a peace deal.

**11:43** · Okay.

**11:43** · So, once you have this, you can download it and put it into the same folder, and you can come back to your Claude code, and you can ask Claude code to sync your entire clip to this voice-over. So, this is the prompt for that. So, I'm going to say, "Embed the voice-over into the composition and sequence the scenes to it. Each scene should start and end on its own narration." And once you've done that, once you've done the voice-overs, the next step is just some music. You need a bit of polish, and you might even need uh some Foley, some background sounds as well.

**12:13** · Sometimes what happens is when you're scrubbing through uh Remotion Studio, what might happen is the audio might sound jerky. Um don't worry about this. This is This is just like a Remotion thing, but then once you render it, it's it's going to sound clean. So, once you've done all of that, you can literally ask Claude code to render the whole thing as a 1080p MP4 video with the music and voice-over mixed in. If you'd much rather do the music and voice-over later in Adobe Premiere Pro, you can do that, too.

**12:43** · You can just get the composition by itself, and then do the music and voice-over separately. So, there you have it. A fully animated motion design in just a few minutes. If you're interested in these kind of videos, then do subscribe. \[music\] I have a whole lot more Claude code and motion graphics videos planned, so you won't want to miss that. But until then, have a good one.