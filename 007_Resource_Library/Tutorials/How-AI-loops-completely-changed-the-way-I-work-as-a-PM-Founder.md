---
title: "How AI loops completely changed the way I work (as a PM & Founder)"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=Jb6rEBmymz4)

Quick video (not my normal style but I wanted to get this out) - because I spent the last week levelling up my setup to be using more "loops" and I wanted to share it with you all!  
  
  
🤖 Struggling to find the time to get hands on with AI? Join the AI Build Day for PMs on June 26th — high impact, hands on day to accelerate you with AI: https://wellcome.me/product-build-day  
  
🚀 Of if you're after more day-to-day support, being able to as questions and bounce ideas. Let's work together in the Product Mentorship 👉 https://www.productpathways.com/mentorship  
  
  
FREE STUFF:  
🗞️ Join 15,000+ product leaders who get hype-free practical product advice every week:  
https://www.antmurphy.me/newsletter  
  
🧰 20+ Free Resources & Templates: https://www.productpathways.com/resources  
  
📺 Subscribe to this channel - of course!  
  
  
  
New here? Hi, I’m Ant. I’ve spent the last 15 years building products, launched a multiple 0→1, owned strategy and pricing, and founded 4x businesses (not counting the ones that didn't make $$). I share the lessons I learned the hard way here in the hope it helps you build better products.  
  
  
  
DESCRIPTION  
You might have heard people like the creator of Claude Code and the creator of OpenClaw say "Stop prompting your agents and start running loops instead." So I wanted to know what they meant by it and what it means for changing how I work with AI.  
  
In this video I walk through what that actually means for a PM and founder (not a developer), how I went from managing 12 terminal windows to a clean autonomous setup, and the process I now go through to create loops.  
  
  
CHAPTERS  
0:00 Intro  
0:38 Why you should stop prompting AI agents  
2:17 Wtf is a loop?  
4:33 Before vs after - changing how I work with AI  
5:05 How to get started with loops  
6:40 Autonomous loops  
8:22 Real examples I'm using every day  
10:38 Making loops self-improve, evals and wrap up  
13:29 AI Build Day in Sydney (link below)  
  
  
LINKS TO FULL VIDEOS SHARED  
\- Stop babysitting your agents: https://www.youtube.com/watch?v=wI0ptqCSL0I  
\- Reflecting on a year of Claude Code: https://www.youtube.com/watch?v=Hth\_tLaC2j8  
  
  
LINKS MENTIONED  
\- /goal in Claude Code: https://code.claude.com/docs/en/goal  
\- /goal in Codex: https://developers.openai.com/cookbook/examples/codex/using\_goals\_in\_codex  
\- Agent View Claude Code: https://code.claude.com/docs/en/agent-view  
\- Managed Agents Claude Code: https://platform.claude.com/docs/en/managed-agents/overview  
\- Routines in Claude Code: https://claude.com/blog/introducing-routines-in-claude-code  
\- Automations in Codex: https://developers.openai.com/codex/app/automations

## Transcript

### Intro

**0:00** · You might have seen the creator of Claude code and the creator of open claw talk about how you should stop prompting your agents and you should start writing loops instead. And I've been interested in all this and I've spent a decent amount of time over the last week or so leveling up my own setup so I can take that next step in my AI journey and work out what all the fuss is about. So, what I want to do is I want to walk you through what that means, what it looks like, how things have changed for me, and how you can get yourself set up this way and whether it even makes sense for you.

**0:29** · So, think of this as a bunch of learning of trying to apply this not just to coding but also to product management and business operations like how I run my business, too.

### Why you should stop prompting AI agents

**0:38** · \[music\] Why does this even matter? Why do we want to try to run loops? Why do we want to stop prompting AI for us? The best way I can illustrate this is to just go back to what my desktop used to look like. So, this is what my desktop used to look like. It was a plethora of of terminal windows, right? So, I actually prefer the terminal, believe it or not.

**1:01** · I used to be a software developer over 10 years ago. Uh so, maybe that's the reason why I still have a little bit of a techie bone in me, I guess. Um but I also get it's not for everyone. But, the problem with this is that they all need my attention.

**1:16** · And I have gotten to a very bad situation before where I had 10, 12, maybe even windows open. And let's just be real, there is no way that you can be given all of those windows your attention and actually be able to manage it. The problem here is that if you are prompting and you are always still involved, you are the limit. Your cognitive load is the limit. And it's not just me, I've also heard multiple engineers over at Anthropic talk about how, you know, four to five different windows tends to be the cognitive limit that you can handle.

**1:48** · I personally find that more than four to five sessions open simultaneously takes a big load on my on on my on my brain and I I can't really function beyond that.

**1:58** · Harvard Business Review also did a study into this where they found that once you got to about three AI tools, productivity would increase and then after that it would start to decrease. And this is just because we're not built for multitasking, right? Like it's hard to handle all of this going on at once.

**2:14** · \[music\] So this is where loops come into the picture. Uh so the whole idea behind a loop and to be honest, it's a bit of a funny name, but the idea behind it is that we create of structure where we can then have agents going off and doing things and we can have an agent then go and verify what those agents have done and then basically prompt what needs to happen next. And the new {slash} goal is an example of all of that packaged up together. Because what goal will do is it'll keep working on itself until it essentially reaches that goal.

### Wtf is a loop?

**2:45** · So it will keep prompting itself, it'll work out what the next steps are and it'll just keep working towards it. And the way that this differs from what you've done in the past is in the past you've prompted the agent to go do something, it's come back to you with an output and a result. You don't have to verify that output and result and then tell it what to do next. Think of it like building a webpage. It's going to go and build a first version of it. You're going to have some feedback or things that you disagree with. It's then going to act on that feedback and we're going to have this cycle.

**3:16** · But the problem with that cycle, as I mentioned right at the start, is that you are constantly involved. You are anchored to waiting for that agent to finish and to then respond and do something. And a lot of this actually made sense because of the model's capability at the point in time.

**3:33** · And this is the thing, you know, people used to talk about prompt engineering, they used to talk about context engineering. This is sort of matching where the model was at the time. Back in the days of Sonic 3.5 you had to prompt engineer. Back in the days of Opus 4 you had to context engineer. But with the models of today you don't do any of this. You give it the minimal possible system prompt, the minimal possible tools, and then you let the model figure it out. Like you just have to give the model some way to pull in the context. I think that's the most important thing.

**4:00** · This could be as simple as a single AI doing a task and verifying itself. That is a form of a very basic loop, and I think that is actually a logical place to start. I'm going to talk about that and share how I've changed the way that I work around that. But a more advanced version of that is to actually have two different AIs, even two different models. One model's more of the executor, and one's more of the verifier. And the verifying agent can then review and then prompt the other agent on what needs to happen next.

**4:29** · Claude Anthropic has released a whole bunch of tools to help you with this. I haven't got so deep into their managed agents view, which is a whole 'nother level, which is going to be my next step to basically get involved. But just using the agent view has already helped me massively. So, like just look at this. So, over here on the left is what my desktop used to look like, which I showed you a second ago. And now this is what agent view looks like. So, basically my desktop now looks like this. Where I just have this agent view, and it's a lot more a lot more cleaner.

### Before vs after - changing how I work with AI

**4:57** · And these agents can run a little bit more autonomously.

**5:01** · \[music\] So, how am I starting to use all of this in my day-to-day, and how where do I recommend that you start? Well, the first thing that I recommend that you start is just by doing it as a single agent setup. The next time you go to prompt Claude or Code X or whatever AI you're using, I want you to think about the prompt in a different way.

### How to get started with loops

**5:22** · I want you to think about it from the perspective of, how do I create a clear articulation of the end state that I want, and how do I give it a little bit of criteria that it can test itself against? And then I want you to instruct it to do that, right? So, before it presents the results to you, get it to verify itself against this criteria and against the a review it, and try again until it feels as though it has satisfied all of that.

**5:51** · And what you'll find is that it will run a little bit longer without you, and it should increase the quality that comes out the other side. If it doesn't increase the quality, then I would want you to reflect on the criteria and the end state that you gave it, and how do you improve that? And try to improve, and this is probably the big shift, and this has been the mind shift for me, think about how do you improve the verification criteria and the goal, not the prompt, right? So, in the past we'd be like, how do I prompt better? This whole And this is the whole point about like moving away from prompt engineering. It's not about like, how do I prompt this better?

**6:22** · It's what was missing? Is it context that's missing, or did I do a bad job of articulating the end state and the criteria that I wanted to test itself against? The second component of all this, of trying to create more agents and more autonomous um situations, is I am I have a lot more stuff running in the background. So, I've got a lot of things that you don't see here, which are routines and agents that literally sit in the cloud, and they run autonomously, and they do several things. So, what I do is my flow of work now is to do things manually the first time.

### Autonomous loops

**6:57** · So, I always still stay this way. I actually was responding to Ed, who had a comment on on somebody else's post. I can't remember whose post it was. It'll come up on the screen when I share it.

**7:06** · Um asking about how like loops and all of this is different. And and his point was, which I absolutely agree with, hence why I'm sharing it, is that this back and forth and learning and refinement that happens is still absolutely important. So, for me, I don't get rid of that, cuz I don't think you can.

**7:24** · And I don't think you should. I You definitely can, sorry. I don't think you should. So, I still have that. So, anytime I'm doing something for the first time, I'm still doing something very manually, and I'm still kind of reviewing it as I go.

**7:36** · Then what I want to do is once I get to a position where I feel like this is pretty good, and it's something that I can then kick it off into either a loop where an agent has the test and it can kind of run itself or where it is something that I can then push into a cloud routine that can run more autonomously um on a regular basis. I will then do that. So, what I want to do is still do things manually first. I then turn it into a skill that we can then test um with. And then you take that skill and then you automate it basically is what you do.

**8:07** · \[snorts\] And you either automate it by getting an agent to run straight away um just straight from a Claude Code session or you graduate it into the cloud where it can then run on basically a cron job or on a regular cadence and it can actually, you know, do do something for you, right? Some real product examples of things that would graduate to like routines that can run in the background, um you could have customer feedback coming in. I literally have this going on right now where customer feedback comes in, it gets pulled, it gets pulled into my like second brain hub of Claude.

### Real examples I'm using every day

**8:36** · So, it all gets pulled into Claude Code.

**8:39** · Um it gets saved, it gets synthesized against everything else, and then it can flag me. I want it to tell me when things come in. It can give me like a summary, so I'm not getting pinged every single time. And it can also push insights to me, right? So, if it picks up something that I thought was interesting or if it's starting to see a new theme emerge, it'll push all those insights to me. Other things I have running in the background too is metrics. So, metrics are coming in.

**9:01** · Again, it's doing the same thing. It's doing health checks against my benchmarks for my metrics. It's telling me whether things are if things are all good, it's not telling me anything like no news is good news. Uh and if things are starting to go, you know, start to need concern or things are going red, it pushes those insights to me. Um other things that you can have uh that I also have going on, I've got a hypothesis tracker, so I've got hypothesis going on. I've got experiments running.

**9:26** · So, I can have a regular routine running in the background that is basically just looking at all those hypotheses, look going and checking how they're doing and then basically reporting back type thing, right? So, I don't have to manually be on top of all of that at all times. A new one that I built just the other week is one that helps me predict basically disengagement and churn in in some of my products.

**9:48** · So, like the product mentorship is my flagship product, and um what this does is it basically looks at the members and the engagement inside the product mentorship community that we have, and whether they're like what whether they're disengaging, when was the last time they logged in, that type of stuff.

**10:04** · So, basically, you can do this if you own Definitely if you own like a SaaS product, this would be really good. Kind of track that daily active users, or weekly, or monthly active users. You can start to look at inactivity. You can start to look at predictors towards churn, and you can get get it to flag you about that.

**10:20** · And then you can even put that on autopilot, where it can start to push things and start to try to re-engage disengaged users, right? So, you can do those types of things. They're all great examples of things that you can run in the background that you don't need to have a lot of oversight on. And they can just kind of ping you, and you can get involved every now and then. Pro tip to just add on to all of this that I've done on all of those those agents is to make sure that there is some type of mechanism for feedback and self-improvement.

### Making loops self-improve, evals and wrap up

**10:45** · So, I've added all of this to all my agents that basically it looks for it looks for opportunities for improvement. I've got an agent that runs every single week, and it just does a big sweep of my workspace. It looks for opportunities to basically refactor, to improve, to just clean up. This is actually would be a nice thing to do on documentation, right?

**11:05** · Like And that's really what I'm doing with my code code setup, but you could make it go through confluence, just clean up everything, make it go through Slack channels, clean up Slack channels, just kind of maintain everything for you. But have some type of mechanism where you can feed it feedback, and also it can kind of push potential improvements to you as well.

**11:27** · You can also put that on autopilot. I have intentionally not put that on autopilot yet, because there's a real danger that if it just keeps right into itself, um it might lose its own intent or it it you know, it can it can create a mess out of itself and get itself into like a quagmire, right? I I want to still be in control and try and maintain the quality of it.

**11:47** · Uh but you could also put that on autopilot as long as you had really strong evals against that agent, it could self-improve and then you could have confidence that as long as those evals are still are still within the threshold that um that self-improvement is working. You can even make it and this is the point of trying to move more towards these loops and this whole like loop concept, at least how I've understood it and somebody can correct me if I've totally misunderstood this, too.

**12:14** · But um part of the idea is like, okay, can um if there is evals, if I did do a self-improvement and it made the evals go out of whack, then I need to fix it until the evals go back to normal, right? Like and then it would just kind of keep keep fixing itself and then it and then it would just keep running like it normally runs and keeps fixing itself and keeps running like it normally runs.

**12:35** · Uh that's kind of like where you want to get to, but it's just really profound. I thought it's very interesting that it's kind of brought me back a lot to my engineering days where I've started to bring back practices around you know, just good coding practices, right? Refactoring, test-driven development, that side of the fence. So uh if anything, maybe this is going to be an interesting shift as well where you know, we got this whole spec-driven development happening on happening right now. I'm starting to see myself go spec to test and then test-driven development. So that's an interesting thing in itself.

**13:08** · Uh so I don't know, take it what you will. Uh I'll watch this space, I guess, over the next couple of weeks. Anyways, this has been quite a profound week for me. I just thought it was worth sitting down and recording a quick video on it just to show you how it all looks and and how things change. If you're interested in learning more about doing this and this level of like AI work, um hit me up. I'm also co-hosting a AI build day on the 26th of June. So, if you're interested in that, there'll be some details and links somewhere that you can go check out around that. I'd love to see you there. Um we're going to be building this type of stuff.

### AI Build Day in Sydney (link below)

**13:39** · You can ask me questions in person there as well. So, yeah, go check that stuff out. And hopefully this was interesting and useful for you. I just wanted to make this was kind of like a hasty video. Thought I'd do it. Make it super quick uh and get it out. Awesome. We'll leave it at that.