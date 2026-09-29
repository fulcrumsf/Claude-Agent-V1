---
title: "Claude Code + OpenRouter: Auto-Pick the Best Model — Original Ingest Note"
type: tutorial
category: ai-agents
form: youtube-video
summary: "Original web-clip bookmark for a 16:50 YouTube tutorial showing how to build a Claude Code skill and agent that reads OpenRouter docs and rankings, routes tasks to cost-effective models, and benchmarks four models on the same Remotion video prompt."
url: https://www.youtube.com/watch?v=Z52I8ha35Vs
tags:
  - claude-code
  - openrouter
  - model-routing
  - agentic-ai
  - benchmarking
created: 2026-09-29
source: https://www.youtube.com/watch?v=Z52I8ha35Vs
---

![](https://www.youtube.com/watch?v=Z52I8ha35Vs)

## YouTube Description

The actual YouTube description could not be downloaded in this session because the sandbox could not resolve `www.youtube.com` and `yt-dlp --write-description` failed with DNS/connection errors. No description text was captured directly, and none was guessed.

From the transcript, the creator says the following build references are linked "in the comments"/description:

1. `openrouter.ai/models` — OpenRouter model list.
2. The OpenRouter rankings board.
3. "AI Arena", described as a comprehensive leaderboard showing all models.
4. The OpenRouter API v1 models listing exposed as an `.md` file.

Exact URLs for items 2–4 were not visible in the captured transcript, so they were not fabricated.

## Transcript

### Why paying for the most expensive AI isn't always worth it

**0:00** · So, I just gave Claude AI [music] a project, but guess what? It didn't run the latest model like Fable 5 or Opus.

**0:05** · What it did is it went into a leaderboard, selected the best and most efficient model for the task, figured out which one was going to give me the same results or the best results for a lesser price. And guess what? The results are pretty incredible, very similar, but for a fraction of the price. And today, I'm going to show you how to do the same exact thing. We are going to build an agent that is going to go look at a leaderboard, pick all the models available to us, find the best one, and then give us the actual result.

### Build an AI model router that selects the best LLM

**0:32** · And then, it's going to learn every week to update its models so it knows that it's always picking the best model for the best task at the best, most effective cost. So, if you want to know how to use other AI models, and you want to learn how to build at the most effective token usage that you [music] possibly can with having the absolute best results with the best model for the job, then make sure you watch this video all the way to the end. I'm going to show you exactly how I did it. So, stay tuned and build along with us.

### Project overview: Claude Code + OpenRouter

**0:58** · So, today, what we're going to do is we're going to build a Claude code agent and skill that involves connecting OpenRouter, which is basically a connector that connects all models and allows us to use these models without any hesitation. Now, the greatest part about this is is that I'm also going to include documents about the models and a leaderboard that's going to allow the AI to make a decision based on the task that we give them. So, at every given time, what we're going to be doing is when we give it a task, it will then select a model that it feels will do the similar job.

**1:30** · And at times, we might ask two models to work on the project at the same time to see which one is going to get the best results. This way, my Claude code projects or agents are never going to be limited to a specific model, and I'm always going to be looking at cost to save money. We're going to build the skill, we're going to build the agent, and we're going to use documents provided by OpenRouter and certain leaderboards in order to do it. Then after, what we're going to do is create a test by creating the 30-second videos using Remotion to allow us to basically see what results gave us which.

### Testing Kimi, GPT, Claude Opus & Fable 5

**2:01** · And I will be testing the latest models between Kimi 3, Sole 5.6, and Fable 5 and Opus 5 to see which one did a better job in making the video or [snorts] if there was massive cost differences. And then we're going to test the time and the cost of each model and to see how they all perform.

**2:20** · You're [snorts] actually going to be pretty surprised about how the results are going to show you that it's not always Opus and Fable 5 that give you the best results even though they're good, but sometimes they're not as cost-effective to get the same results from a cheaper model that can do the test just as well. So, let's go ahead and jump to it. So, the first thing I'm going to do is I'm going to pull up my VS Code. So, if you have any questions about how to install Claude Code or VS Code, I have other videos showing how to do that, so please make sure to check those out. All right, so the first thing I'm going to do is I'm just going to clear my conversation here.

### Creating the AI agent in VS Code

**2:49** · All right, I'm in the terminal in VS Code, and as you can see I got Fable 5. Now, Fable 5 and Claude Code are still my main operator for creating agents. And I still will use nine times out of 10 Fable 5 or Opus 5 to be the orchestrator or the leader or the person that's kind of organizing my project.

**3:06** · So, what I'm going to do is I'm going to tell it that we want to create an agent and a skill that will use Open Router and it will look at the leaderboard to decide which model to use for certain tasks. Now, I'm going to dictate this so you guys can just follow along, and then I'll try to keep the screen. Just try to screenshot it so then you can do it for yourself. But I'll try to include some of this in the comments. All right, so what we're going to be doing today is we're going to be building a skill and an agent that will act as a model selector for whenever we're doing particular projects.

### Designing the model selection skill

**3:36** · Now, the goal is to give you access to the documentation on Open Router. Open Router is basically a connection that allows us to use multiple models throughout our projects and basically have the ability connecting it to any of those at any point in time. I'm going to give you the documentation for OpenRouter on all the models it has access to. I'm then going to give you the leaderboard of these models and what they can do.

**3:59** · And more importantly, then what we're going to do is create a cron job or a scheduled task inside our computer that will update this regularly so we're always up to date with the latest model fixes. So then what we're also going to do is run a test afterwards to ensure that we're using the best model to create the task that we have at hand and we're going to do some comparisons. Whenever you're using any of these models, part of your job is to identify the time and the cost per model usage.

**4:26** · Now again, the pricing of all these models is located on OpenRouter, so you'll be able to see it inside there. Let me know when you're ready for the documents. So, clear pretty sustainable task. I'm using WhisperFlow to basically dictate all of this and I'm going to paste this. So then later on you all I'll clean it up a little bit and later all and you all can have it. Okay? And we're going to let this thing run for a hot minute and when it's ready for the documents, then what I'll do is I'm going to come in here and we're going to give a set of links. All right, great. Now it's asking for the particular documents and basically it's going to be links.

### Adding OpenRouter documentation & leaderboards

**4:57** · So I already have them up. First thing is you're going to go to openrouter.ai/models and it gives you a list of all the models. So I'm going to copy this and go back to my VS Code, come in here and I'm going to drop it right there. Then I'm going to go to the actual rankings board. I'm going to provide you both the one inside of OpenRouter, okay? And I'll try and include these links all there for you so you guys can build these out on your own. All right, I'm going to come over here.

**5:23** · I'm going to drop the ranking boards and then I'm going to use AI Arena, which is a pretty good comprehensive one that shows all of them. And I'm going to copy this and I'm going to go to again my VS Code. And then the last one I'm going to do, believe it or not, OpenRouter provides an API version one that shows basically all the models that are available to it with basically the language that again the AI would like to read, which is an MD file with different codes in here.

**5:50** · So, I'm going to copy this, too, and I'm going to again, I will link all these files into the comments, so please make sure you check those out. And then, what I'm going to do is I'm going to come right in here. I'm going to paste those links. Now, based on that before, remember, in order for me to use OpenRouter, I'm going to need to get an API key, and I'm going to walk you through that process on how to do that.

### Building the agent before connecting the API

**6:09** · But first, I want to build the skill in the agent and then create the API connection later. Because once I have the API, most of this is pretty easy, but let's go ahead and do this now, and I'm going to go ahead and hit enter.

**6:19** · Okay? Now, it's going to work through reading through all these different models and all these different pages, and basically, this is going to be the ammunition I need in order for it to build the skill and the agent. Because a lot of us, when we're building skills, we're not leveraging, you know, again, the documentation that's out there. And the better we make it, and easier we make it for the AI to go get the documents that it needs to build these things, the better off your agents are going to be. So, we're going to give it a few seconds to run this and help format and create the agent. Then, we're going to connect the API and then finally run our tests. All right? So, now it's leaving me with two tasks.

**6:51** · One, it needs the Open API key in the .env, and then we have to run .py because then it's going to be able to do the comparison. So, we're going to do those two tasks. First, let's get the API key so you can understand how that works.

### Creating an OpenRouter API key

**7:03** · So, we are going to come directly to our browser, same browser we're using here.

**7:09** · We're going to go to OpenRouter. Okay?

**7:11** · You can just type that in. There's only one OpenRouter, so you're going to click on that, and then you're going to create an account if you don't have one. I already have one, or you can just click on this get API, and you will always see the prices. When you click on prices, it will actually show you the models per pricing in here. From pricing, and then there's a couple of them in here, and again, it has the rankings and ratings, but what we want to do is create an API key.

### Verifying the setup and scheduling updates

**9:02** · What we got to do is we got to open up the PowerShell and we got to basically run this PowerShell command. So, what I'm going to do is I'm going to go ahead and click on my Windows key. If you're running a Mac, just make sure you tell the AI that you're running a Mac and then they'll tell you the specific instructions for the Mac, but it's going to be very similar, right? So, I'm going to go ahead and open the PowerShell and I usually like to just go in the search window and type in PowerShell.

### Scheduling weekly model updates

**9:26** · You're going to want to right click, run as administrator and then we're going to say yes and then once we say yes, we're going to come back over here and grab the command right here. So, I'm going to come back to the PowerShell, come over here, control V, and I'm going to hit enter. And what it basically did is create a scheduled task on my computer to update this every week in order to do that, right? Now, to confirm that it's there, we're going to grab this, control C, okay?

**9:53** · And we are going to come in here, control V. Oh, going to give me an error. So, anytime anything gives me an error, I just copy it and I throw it in here and I find out what the error is.

**10:04** · And then it'll tell me something stupid that I did.

**10:06** · Yep, see your prefix is in there and it's going to run the shell command and it's going to figure out what it did wrong or right and what I have to copy differently. But again, nine times out of 10, it's because you, like you personally, typed in something wrong or copied the wrong thing. See, register correctly, log on trigger, okay? And then the other step is then just ask cheapest model to run PDF and call tools or go through me.

**10:24** · So, it's saying that it's ready to go, the API's connected, we have the AI trained, and it created a folder on right here that's called the model router in what I call my AI agent team where I build all these agents that do different things for me. So, what I'm going to do, just to make it super simple, is I'm going to go ahead file, whoop, I'm going to open the folder, and I'm going to go into my agent team, and I'm going to select the model router, and what I'll do is I'm going to select it to run the first test.

### Running the AI model comparison test

**10:53** · So, what I'm going to do here is I'm going to go ahead and open my terminal. So, I'm going to type in Claude, okay? Now that I typed in Claude, we're going to run our test, right? So, let us pull up. I want to use the model router because I want to run a test on all the latest models and using a remotion skill or the hyperframe skill to create a 30-second video explaining how to install Claude code.

**11:17** · I want you to use Kimi 3.0, I want you to use Sole 5.6 Ultra, I want you to use Opus 5, and I want you to use Fable 5. Then, I want you to record the time it takes to produce all those videos, and I want you to also put the cost based on open router's model cost.

### Testing four AI models with the same prompt

**11:38** · All right, so can you do that task?

**11:40** · Please confirm. All right, and then we're going to hit enter. Because now what I want to see is really compare whether or not it's going to be able to do all of this, and it will go ahead and select the models, look up everything, use the skill in the task in order to do so. But again, what this will do going forward is give you the best of the best to use across all models to be as token efficient as possible while also getting the best results based again on model benchmarks and what's actually happening out there, right?

**12:08** · And again, really good to use if you're working on complex projects where you also want to use this tool to validate that your project is working right, or you want to have a secondary AI like a second opinion go through your entire application. All right, so we're going to let this run, and we're going to see what it comes up with. All right, let's see the finalized test. Every model received the identical prompt. This is the comparison by chart.

### Cost and speed comparison results

**12:30** · So, model in and out cost and everything else, we're looking at 6 cents for Moonshot. We are looking for OpenAI 24, Anthropic 33, Anthropic Fable 5 44.

**12:41** · Okay, and the total $1.09.

**12:44** · Again, cheapest was K3, literally 6.5 times cheaper than 5%. Fable 5 cost the most while writing 40% less code than Opus 5. And then this is basically the model cost altogether. Time comparison measured, Moonshot 26 seconds, Anthropic Cloud Fable 5 76, OpenAI GDP sold 92.8, Anthropic Cloud Opus 5 119 seconds. Kimi again faster output. The four ran in parallel, so these times were measured concurrently.

**13:13** · All right, these are all the still So again, you have it all here, but again, it doesn't matter until we see the finalized result, right?

**13:20** · Because they could say all that, and let's see it. So, first let's look at Fable 5, obviously the most pristine model.

### Fable 5 output review

**13:27** · All right, very smooth, looks great.

**13:31** · Look at that.

**13:34** · Fantastic. Great command. I mean, honestly, this is completely accurate.

**13:38** · Great graphics, right all there. Look at this.

**13:43** · This is awesome.

**13:45** · This is awesome. All right, so Fable 5 really setting the, you know, the bar here. But again, it is the best model, in my opinion, right now. And look at that. I mean, perfectly, same prompt, same to everything, and we got it. Let's try Opus, and let's see if there was a difference.

### Claude Opus 5 output review

**13:59** · Okay, also looks pretty good.

**14:03** · Uh different two layers, which is pretty cool. I don't know if everyone is going to do that.

**14:12** · Same kind of like bar that we saw before.

**14:21** · Pretty good. This kind of went a little bit over it, but not bad.

**14:24** · Again, pretty solid. All right, now let's get into Sole 5.6 GPT GPT. Huh.

### GPT Sole 5.6 output review

**14:32** · Again, looking really good.

**14:36** · I mean, the variation of this so far is not that overwhelming or different, right? So, we're starting to see that there's a lot of similarities. Okay, that doesn't have the cool bar that we saw before. A little slight difference.

**14:53** · Okay, a little bit of a different screen. I actually like that. I think that's pretty cool. That's pretty cool.

**14:58** · Again, not a real big difference when it came to the video processing. All right, now the cheapest and fastest model.

### Kimi 3 output review

**15:08** · I mean, is it worth the cost? Because this looks pretty darn good.

**15:18** · It is using an older model of the install command.

**15:21** · So, I don't know if that's a good or bad thing.

**15:25** · But, the quality of this is not bad at all.

**15:31** · Going a little faster in time. So, overall, you guys kind of saw it. This was the prompt that was sent to all four, so you guys understand that like again, the prompt was the same exact thing. It gave a very specific layout of exactly what it wanted. Again, I do think Fable 5 and Opus 5 actually did a really good decent job. And again, just quick cost comparison. I mean, it's kind of there of where it was. Opus 5 is 33 cents, Fable was 44, 10 cents more. GPT was 24, and again, Kimi coming in at six with having absolutely the fastest time.

### Comparing quality vs cost

**16:02** · With Fable showing in the second fastest time, and then GPT sold 5.6 and everything else. Now, again, I just ran these very simple comparisons, but now you personally have access to all the models. So, you can test whatever models you want, and again, you can always have it come in here and say, "Okay, what model would you like, and which one would be most cost-effective, and which one is the best for task A or task B?"

### Which AI model should you use?

### Final thoughts on saving tokens and money

**16:26** · So, hopefully this gives you guys an absolute ammunition of had a baguette like the absolute best results and have the best token management in cloud code or cursor. You could do this with any kind of model going forward, and now you'll have an agent that basically can you can invoke at any point in time to not only give you the best results, but give you the cheapest most effective token management that there is out there. So, hopefully this helps, and we'll see you in the next one.

**16:50** · [music]
