---
title: "GLM 5.2 in Claude Code is Blowing My Mind"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=2OD14-0cot4)

My FREE AI OS Course: https://www.skool.com/ai-automation-society/about?el=glm-5.2-claude&hcategory=youtube-videos&utm\_campaign=free-group  
Full courses + unlimited support: https://www.skool.com/ai-automation-society-plus/about?el=glm-5.2-claude&hcategory=youtube-videos&utm\_campaign=ais-plus  
Apply for my YT podcast: https://podcast.nateherk.com/apply  
Work with me: https://uppitai.com/  
  
My Tools💻  
FREE MONTH voice to text: https://get.glaido.com/nate  
Code NATEHERK for 10% off VPS (annual plan): https://www.hostinger.com/vps/claude-code-hosting  
  
I switched Claude Code over to GLM 5.2 and ran it all day. It's a 756 billion parameter open source model you can route straight into the Claude Code harness for about five times cheaper than Opus, and for most of my knowledge work it held up fine.  
  
In this one I show you what it can build, where it beats Opus and where it doesn't, and exactly how to set it up so you can switch between models per project.  
  
Here's the config I use. Drop this into your .claude/settings.local.json and swap in your own Z.ai key:  
  
"env": {  
"ANTHROPIC\_BASE\_URL": "https://api.z.ai/api/anthropic",  
"ANTHROPIC\_AUTH\_TOKEN": "your-z-ai-api-key-here",  
"ANTHROPIC\_API\_KEY": "",  
"API\_TIMEOUT\_MS": "3000000",  
"ANTHROPIC\_DEFAULT\_OPUS\_MODEL": "glm-5.2",  
"ANTHROPIC\_DEFAULT\_SONNET\_MODEL": "glm-5.2",  
"ANTHROPIC\_DEFAULT\_HAIKU\_MODEL": "glm-5.2",  
"ANTHROPIC\_SMALL\_FAST\_MODEL": "glm-5.2",  
"CLAUDE\_CODE\_SUBAGENT\_MODEL": "glm-5.2"  
}  
  
Sponsorship Inquiries:  
📧 nate@smoothmedia.co  
  
Connect with me:  
https://www.linkedin.com/in/nateherkelman/  
https://x.com/nateherk  
https://www.instagram.com/nateherk/  
  
TIMESTAMPS  
0:00 Intro  
0:56 What GLM 5.2 Can Do  
2:40 When You Actually Need Opus  
3:39 Creative One-Shot Builds  
5:21 Storm Research With GLM  
7:36 Why Open Source Matters  
8:21 Benchmarks And Pricing  
9:19 Renting vs Owning Your Model  
10:33 How To Set It Up  
14:48 Final Thoughts

## Transcript

### Intro

**0:00** · So, I've been playing around with GLM 5.2 inside of Cloud Code all day, and it's incredible. It feels faster. It's significantly cheaper, and it just fits right into the Cloud Code harness pretty well. It's been doing so well, in fact, that it edited this entire intro that you're watching right now from raw video all the way to what you're watching. So, in today's video, I'm going to show you just how quick and easy you can get set up with GLM 5.2 in Cloud Code. So, let's not waste any time and just get straight into the video. So, obviously that intro wasn't perfect, but that was literally one prompt. It was one/goal right here.

**0:27** · It took a little over an hour, an hour and 15 minutes for, you know, a 23 second video. So, that did take a little bit long, but this was the session that we did it in. It was GLM 5.2 1 million context. As you can see right here, it used about 357,000 tokens. But, as I've been playing around with it more and more, there are some tasks where it finishes way faster than Opus. And then there are some like this one where Opus would have done this much quicker. So, I'm going to show you guys exactly how to get set up. But before that, let me just show you a few of the things that I've played around with and what GLM has been able to do. So, it's actually like really solid at design.

### What GLM 5.2 Can Do

**0:57** · I want you guys to look right here and see which one of these do you think was designed by GLM 5.2 and which one was designed by Opus.

**1:06** · So, as we sort of scroll down here, you can see that we have, you know, similar style branding and it's obviously the same company, but we have elements on both that are very similar. We have all of these things come up dynamically as well on either side. And there's even a CTA at the bottom. I think the dead giveaway here is this right side was opus because it has these weird Fs that it loves to do. It loves that font. But either way, these are both very solid for a oneshot prompt. Especially when you consider the fact that you are getting this output for like five times cheaper.

**1:35** · So these are the actual terminal sessions where we did those website designs. On the left side with GLM, we got this done in 3 minutes and 59 seconds. On the right side with Opus, we got this done in 14 minutes and 59 seconds. And not only did the lefth hand side GLM use less tokens, but its cost per token is also five times cheaperish.

**1:53** · So in this case, it was quicker and it was much cheaper and it was a relatively similar result. I also shot off this prompt on each side where I gave them a homework assignment. You can see right here we've got GLM and then right here we've got Opus 4.8. I had Codeex create the homework assignment just so there was no like crosscontamination or anything like that. And then when they finished, I had Codeex judge both results and tell us what it thought.

**2:13** · Now, in this case, it said that agent 2, which was opus, was better because it handled one subtle edge case that agent one missed, which were duplicate records with values like true versus one or one versus 1.0. So, the short version is that agent 1, GLM 5.2 was good, but agent 2 here was more precise. And generally, the way that I feel about this so far is that GLM 5.2 is really solid and it's pretty quick for most tasks that don't require heavy reasoning. Obviously, at the end of the day, Opus 4.8 is a better model. It's a closed source model. But realistically ask yourself how often do you actually need the power of Opus?

### When You Actually Need Opus

**2:44** · Probably only maybe 10 to 20% if that of the tasks that you do all day. You could probably handle 80% or more of your knowledge work with something like GLM 5.2 or something more like sonnet 3.7. So that's really going to be a key skill as we move into the future of AI is understanding which models to use per task. But here's an example where you can see Opus took about 5 minutes and GLM 5.2 took about 24 minutes. And this was me on a $60 a month plan for um Z.AI for GLM 5.2.

**3:13** · And I've played around with this for this was about four or five hours straight of just literally hammering it. Five different sessions open, testing GLM 5.2. And my 5-hour quota is a little bit over halfway used.

**3:26** · And my weekly quota is about 10% used.

**3:28** · I'll talk about the billing and how to get set up in just a sec. Let me show you guys what else I did with it. So I did a few more/goal prompts. And I hate when the terminal does this, but this first one that I did was I did /goal and I literally said like, "Hey, get creative. Show me how good your design skills are and just build me whatever you want. Just make me an HTML document." And then this is what it gave me. It gave me the anatomy of attention.

### Creative One-Shot Builds

**3:48** · You can see we've got like some stars moving around in the background. This obviously looks a little bit vibe coded up here, but not too bad. And as we sort of scroll down, we can see a language model has no grammar book and no dictionary. And then on this thing, the animal didn't cross the street because it was too tired. This is kind of like an interactive element here. We see the query word and then we see where it points. So tired was pointing to it. It was pointing to the animal. Cross was pointing to the street. So kind of interesting. First the sentence is broken. Every token gets a place in space. So we've got a little bit of like a relationship graph here.

**4:17** · We've got some charts down here and some different elements. So anyways, this is what GLM came up with when I said, "Hey, just be creative and just give me whatever you want. Show me whatever interests you, I And then I did the exact same prompt into Opus to see what kind of differences we would get. And Opus came up with the life of a Death Star. Here once again, you can see that classic F that Opus loves to do. But anyways, this one is more of like a timeline where we go through the actual kind of like life cycle of a Death Star. And we can see this one is also pretty good as well.

**4:48** · But once again, pay attention to the fact that from a design perspective with one shot, is Opus that much better? Is Opus five times better? Because you're paying five times more. However, with this one, the goal took about 35 minutes, and for Opus, this goal only took about 11. So, it's really a hit or miss as far as when is GLM 5.2 actually faster. Typically, the more reasoning, the slower it's going to be. And so, just remember, cloud code is a harness.

**5:11** · It's a harness for AI models, and typically cloud models are going to use the harness the best. But, GLM 5.2 does pretty decent. It's able to use the SLG goal. It's able to read my cloudmd. It's able to use my skills. Right here I said /goal I need you to use the storm research skill which I'll have a video coming out about that very soon to research open source AI models versus closed source and the end deliverable is an HTML report. So it goes through it does a bunch of sub aents all the sub aents were using GLM 5.2 as well and it had a bunch of different personas. This took about 27 minutes and I got this report back.

### Storm Research With GLM

**5:41** · This was our storm research and you see it says V2. That just means that it had one pass and then it has another set of agents come and read that and then it makes some changes. So anyways, this is the HTML report that we got. I'm not going to read every single word of this, but it is very thorough.

**5:56** · It's very solid. It looks decent. You can see we had five different lenses going through this, which you'll probably see a little bit sprinkled throughout. We have a 60-second summary.

**6:04** · We have five key findings. This one was supported by the academic and the skeptic. This one was supported by the practitioner, economist, and the academic. And it was challenged by the skeptic and the historian. So basically we're just leveraging like you know a mixture of experts here or a mixture of different you know styles of agents to help us do the research and help us debate over how this thing is actually constructed. We have the hidden connection. We have the assumption that the briefing rests on what to actually do different. So if you guys want to pause this and actually read through it.

**6:34** · It has some really good information in here. But anyways this is what it came up with. This made me start to wonder like okay where would I actually use GLM 5.2 over something like Opus 4.8 because I do think that after I did a ton of knowledge work with this today and testing, it's pretty solid. And so I think for something like this, I would 100% be comfortable with GLM 5.2 doing this because I felt comfortable with the way that I orchestrated that storm skill. Bunch of different agents, bunch of different verification checks. And that is way more important ultimately than the model, than the underlying model.

**7:02** · It's all about the way that you prompt them, the way that you use them, the way that you have your skills and your harness and your context layer. So I would trust GLM 5.2 here big time to do me a bunch of research. And by research, I mean like gathering a bunch of opinions and gathering data and pulling in sources. But I probably would want Opus to actually help me think through based on all this data what really matters and how do I apply it to my life. That's where I'd probably lean on a heavier reasoning model, a stronger model like Opus. So I feel like everyone needs to be thinking about that kind of stuff. It's not binary.

**7:31** · It's where in each process, what steps should I use what model for? Anyways, why am I talking about GLM 5.2? Because it is an open- source model, right? So like chatbt or claude but those are those are closed source models meaning you rent it you pay directly to the provider in order to access it. Now yes you guys saw earlier I am paying a subscription to access GLM 5.2 and that is just because it is so massive. It is a massive model 753 billion parameters which is very big which means that I couldn't actually run that on my machine. Yes it is open source.

### Why Open Source Matters

**8:02** · Yes you could run it locally but you would need the hardware you would need the infrastructure to support that.

**8:07** · Most of us don't have that just lying around. So what we can do is we can rent it online. So kind of very similar the way that you pay Anthropic for Claude, but it's so much cheaper than Claude. So everyone is freaking out because it's basically yours. You're able to download it or get it for much cheaper. It's very smart. I'll show you guys some benchmarks in a sec. And it is very cheap. If you did a heavy day of coding, it'd be about five times cheaper than Opus 4.8 for the same job. You can see here, here is the input and output tokens. Opus 4.8 is $5 on the input, $25 on the output, whereas GM 5.2 is $1.40 40 cents on the input and $4.40 on the output.

### Benchmarks And Pricing

**8:40** · So this is where I got the numbers where I said it's about five times cheaper. So if you go to something like Olama, which is somewhere where you can actually download and pull in local models, you can see here that we have GM 5.2. It's got the 1 million context window and the size is 756 billion parameters in this case. Now they don't actually let you pull this in. They let you run it from their cloud, which is nice because it is such a big model. But take a look at some of these benchmarks compared to Cloud Opus 4.8 8 and GBD 5.5 which are like the two best models right now. Look where GLM 5.2 is stacking up.

**9:11** · It is really comparable to all of these other top tier close source models which is why obviously a lot of people are freaking out about it right now and looking at it. Think about the fact that Fable got pulled away from us, right?

### Renting vs Owning Your Model

**9:21** · That just tells you that we are renting something that could be taken away from us for, you know, out of nowhere. And what I'm worried about is Enthropic and Openi aren't profitable companies right now. We're paying $200 a month for a clawed max plan, but we're getting like $8,000 worth of inference out of that if we actually utilize it all the way. So, they are not profitable. So, what happens when we finally maybe we get Fable back, they're obviously not profitable on that either. So, what they might do is bring it back and say, "Hey, but you can't use this in your subscription. You can only use this via API billing." That's more expensive than Opus.

**9:51** · So, if you can start to understand these open source models and you can start to deploy them locally for basically like completely free, then it is really going to help you stay ahead of the game here. Take a look at this bench, Frontier S. SWE. It performed better than GPT 5.5 in this benchmark, which is just absolutely crazy. If you guys liked Opus 4.7, which a lot of you guys did, some of you guys didn't. GLM 5.2 was beating that model in a lot of these evaluations. And it beats the most recent Sonnet model in a ton of these evaluations as well. So, just think about it like that. Think about truly how decent this model really is. Here's some more benchmarks. Aenta coding.

**10:21** · I'm not going to go through all these because I, you know, we all know that you should always take these with a grain of salt. It's more about the feel and how you actually use them, but they are interesting to look at every once in a while. So, anyways, let's talk about how you get set up. What you do is you're going to go to z.ai and you might pull into something that looks like this. You can go ahead and chat. You can make landing pages right here. You can do 3D modeling. You can build your own mini game. And it's really good at this stuff. It's really impressive on the front-end design stuff. So, come in here, play around with it if you want to just test it out and see how it feels.

### How To Set It Up

**10:51** · But then if you want to plug it into Cloud Code or Open Code or Hermes Agent or wherever you want to plug it in, you're going to click on this button up in the top right and that's going to take you to the actual API console. And so you've got the option to just pay per token which obviously is not too expensive. If you come here and I go to my billing and I go to the model pricing, you can see on the input it's $1.4 and on the output it is where'd it go? $4.4. But you could also just get a plan. So you could go on 16 bucks a month, 64 bucks a month or 144 bucks a month. And if you go yearly, you can save even more money. Obviously, they're not a sponsor.

**11:21** · I'm not working with them, but you can also get on a plan.

**11:24** · So, maybe you can be on a Claude plan for maybe 100 bucks a month, and then you can be on a Z plan for 64 bucks a month. And then just switch between them. Whenever you need a certain type of task, then you can bounce back and forth. And that way, you're getting way more out of your subscriptions. Once you get a plan, what you would do is you would go to API key and you would go ahead and grab one. So, you would add an API key here. And then you're going to be able to start just using that inside of Cloud Code. and then you'll be able to watch your usage limit here. Now, the five- hour quota and the weekly quota work very similar to claude code subscription.

**11:53** · They also have peak hours where it consumes, you know, a higher multiple of your quota. And then what's interesting is they have like web search quota as well. So, if you were doing a lot of web searching, um it will eat this up, but you could obviously connect it to maybe like perplexity or a different API to do more web searching.

**12:08** · So, it's not a huge deal, but I did think that that was kind of interesting.

**12:11** · So anyways, all you're going to do is you are just going to edit your config file within cloud code, which sounds a little bit scary or technical, but it's really not. Let me just pull up my cloud real quick and show you what that looks like. So inside of yourcloud, you should have a settings.local.json.

**12:26** · And this is where you can play with your permissions and your MCP servers and all that kind of stuff. And you can also set environment variables. So if you guys have activated agent teams, this might live here like mine or it might live globally. Wherever it lives, that's an environment variable. And all you need to do is you need to come in here and you need to set these. So what I'm going to do is I'm going to have this exact thing, paste it in the description of this video. So all you have to do is copy this, put it into your environment variables. You can also say, hey, cloud code, put this into my settings.local.json, and then all you have to do is switch out your own API key.

**12:55** · So this is where you will put your Z API key that you just got in here when you go to API keys, and you added one right there. Because what you're doing here is you can see we have enthropic base URL and we are routing that to Z's API rather than to an anthropic API. So we're just switching out the engine of the car. If the harness is the car and the engine's AI model, we're just switching out the engine. And you can see right here I have left the enthropic API key blank. We put this in as the enthropic o token and that is my Z API key. And then we changed all of these default models to GLM 5.2.

**13:26** · And then when you open up your new claude, if I go in here, claude, we open that up and what do we see right here? We see GLM 5.2 with 1 million context API usage billing. And so that is just like on a per project setting. So if I come into this other one and I show you guys like you know on this lefth hand side we have GLM. On this right hand side we have um opus. The way I did that is I just have these in two different directories. And this is a very ugly view. I'm sorry about that. But what I did is in here I have two folders.

**13:58** · I have GLM and I have opus. So in the GLM folder, my settings.local.json shows this stuff, right? And then in my opus folder, I don't even have a settings.local.json. And that's how I'm able to open up claude in this directory. And we just have the regular Claude. And this looks absolutely awful.

**14:16** · So let me just show you. There we go.

**14:18** · Because we are not in a directory that has a settings.local.json JSON with this routing. It just pulls up automatically with Opus on my Cloud Max plan. So that's how you can sort of, you know, tweak which projects are using which AI model. And also, if you guys were wondering, this entire slide deck, of course, was built by GLM 5.2. It's funny cuz it keeps referring to me as Herk, and I think by this it just means Herk 2, like my project called Herk 2. But this was made by GLM 5.2. And you'll notice it looks like a lot of my other slide decks because it used my skill for that.

### Final Thoughts

**14:48** · Anyways, I know this one was a quick one, but I wanted to make it quick and show you guys how to get set up so you can play with it. I am planning on bringing you guys a ton more content on local models and maybe even some other stuff like open code because you don't always want to be locked into maybe cloud code's hardest. So, please let me know in the comments what you want to see around open-source AI because trust me, I can definitely see a future where every company is just running their own local models. And I think Enthropic is starting to realize that too. OpenAI is starting to realize that too.

**15:14** · That's why they're investing into other things like services and other ways that they can integrate into companies like their forward deployed engineers because they know that the model might not be the moat at the end of the day. Right now there's a huge gap, but we see this gap closing super quickly and it's really fun to watch in real time. So, let's start playing around more with open source models. If you guys enjoyed the video or you learned something new, please give a like. Helps me out a ton.

**15:38** · And as always, I appreciate you guys making it to the end of the video and I'll see you all in the next one. Thanks everyone.