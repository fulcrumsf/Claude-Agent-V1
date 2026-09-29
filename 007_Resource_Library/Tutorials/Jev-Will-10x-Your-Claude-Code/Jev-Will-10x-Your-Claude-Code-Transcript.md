---
title: "Jev will 10x your Claude Code (Here's How) - Transcript"
type: transcript
category: ai-agents
tags:
  - transcript
  - jev
  - claude-code
  - agentic-ai
created: 2026-09-27
source: https://www.youtube.com/watch?v=tTnUcSj-QPA
---

# Jev will 10x your Claude Code (Here's How) — Full Transcript

**[00:00:00,000]** There's a new AI model in town from the co-inventor of ChatGPT and it is insanely cheap and incredibly fast.

**[00:00:06,600]** It's called Jev and just to show you how fast it is, I'll send this prompt and that is real time.

**[00:00:12,560]** It gave me an output for less than a second and a diffraction of the cost.

**[00:00:16,880]** So today I'll explain Jev for you simply and also some of the best ways by which you can integrate Jev

**[00:00:22,080]** with the agentic harnesses you use like Cloud Code to make your set of faster, your systems cheaper

**[00:00:27,280]** and even build new things and automate parts of your business that weren't possible before.

**[00:00:32,080]** Let's dive into it.

**[00:00:32,880]** So first of all, what is Jev?

**[00:00:34,640]** And I won't go super deep into this, but basically Jev is a new AI model that is quite interesting

**[00:00:40,240]** because it was released by a co-inventor of ChatGPT.

**[00:00:43,840]** So this person, Diogo, he made this post that already has something like 38 million views

**[00:00:48,560]** and he says here that Jev is a new type of frontier AI model that is 20 to 200 times faster

**[00:00:54,720]** and 40 to 400 times cheaper.

**[00:00:57,040]** And if you look at the rate card for this model, that is indeed the case.

**[00:01:00,240]** It is around 24 times cheaper than Haiku and around 230 times cheaper than Fabo5.1.

**[00:01:05,440]** And a big part of why that is is because it's output tokens,

**[00:01:08,800]** basically it's response to you as the user is always free.

**[00:01:12,800]** And they only charge for the input tokens, which is essentially your prompt.

**[00:01:16,720]** And it's super cheap, it's only 4 cents per million tokens.

**[00:01:19,920]** Now a big part of why it's so fast and so inexpensive

**[00:01:23,200]** is because Jev can only answer in three shapes.

**[00:01:26,240]** So when you ask a question, it can either give you a binary response,

**[00:01:29,360]** whether that statement is true or false.

**[00:01:31,280]** It can provide a selection against a menu of options.

**[00:01:34,480]** Or it can also give you a response that is based on scale, let's say from 0 to 10.

**[00:01:38,960]** And even though this sounds like a big limitation for the model,

**[00:01:41,840]** this is actually the genius behind why it's so effective in the use cases that we'll go through later.

**[00:01:46,560]** But before we go to that, one key thing to remember is that Jev

**[00:01:49,920]** is not actually a large language model.

**[00:01:52,560]** And the way that typesafe, which is the company behind Jev talks about this,

**[00:01:55,920]** is that they're saying that Jev is the first system one model,

**[00:01:59,120]** whereas all the other AI models like Fable, Astra, and the others

**[00:02:03,200]** are what they're called in system two models.

**[00:02:05,440]** Now in case you've read this book called Thinking Fast and Slow,

**[00:02:08,160]** that system one and system two dichotomy of how humans and people think

**[00:02:12,400]** might be familiar to you.

**[00:02:13,600]** But essentially the difference between these systems is that system one

**[00:02:16,800]** is all about thinking fast and making snap decisions.

**[00:02:19,600]** And so Jev as an AI model just optimizes against this.

**[00:02:22,800]** And so it just outputs classifications and can do that really, really fast

**[00:02:26,640]** and really, really cheaply.

**[00:02:28,080]** Whereas LLMs and other general purpose models like Fable or Astra,

**[00:02:31,920]** they can output text and they do that by writing each word one by one.

**[00:02:35,440]** But it gives them more flexibility of what it can output, obviously.

**[00:02:38,880]** But that would have the drawback of these system two models

**[00:02:41,920]** thinking slower versus its system one counterparts.

**[00:02:44,960]** And so really if there's one takeaway from all of this,

**[00:02:47,280]** I think the best way that you can use Jev right now

**[00:02:50,000]** is to combine both.

**[00:02:51,120]** Combine a system one model like Jev with a system two model

**[00:02:54,400]** like the Claude models.

**[00:02:55,920]** And so I'll show you some use cases of how you can get started

**[00:02:58,240]** and actually get value from this today.

**[00:03:00,000]** But first let's get you set up so that you can actually use Jev.

**[00:03:02,880]** And as with any other AI model,

**[00:03:04,560]** it's actually available to a variety of platforms.

**[00:03:07,440]** You can obviously use it by connecting to type, save,

**[00:03:09,760]** who is the company behind Jev.

**[00:03:11,680]** And as per their ex-post at the time of this recording today,

**[00:03:14,960]** they just announced that Jev is now actually available to everyone

**[00:03:17,600]** because previous two days just hours ago,

**[00:03:19,600]** there used to be a wait list to access it.

**[00:03:21,680]** So if you go to this URL,

**[00:03:22,960]** you'll be able to sign up there

**[00:03:24,080]** and actually get your API key to connect it to Claude.

**[00:03:27,200]** At least when I was testing it personally

**[00:03:28,800]** and throughout the use cases that I'll go through here,

**[00:03:30,800]** I connected to Jev via OpenRouter,

**[00:03:32,880]** which is the service that always gets updated

**[00:03:34,960]** with the newest AI models as they get released.

**[00:03:37,200]** So you can just access that to this URL.

**[00:03:39,120]** And so to set it up with Claude or any agentic harness

**[00:03:41,360]** that you're using is just one prompt away as usual.

**[00:03:43,920]** And you can just take a screenshot of this

**[00:03:45,520]** if you need a starter prompt to set that up.

**[00:03:47,600]** Or if you want to prompt and the setup guide

**[00:03:49,200]** for everything that I'll cover here in this lesson,

**[00:03:51,920]** I also made this PDF guide,

**[00:03:53,200]** which you can just grab for free below

**[00:03:54,880]** and you can just send it to your agent

**[00:03:56,480]** for all of the good nuggets that you can pick up in this video.

**[00:03:59,440]** So once you set that up and you confirm with Claude

**[00:04:01,680]** that you have access to Jev, like what I did here,

**[00:04:03,680]** now we can get to actually using it.

**[00:04:05,680]** And I'll actually talk about this through three levels

**[00:04:07,920]** by which you can use Jev.

**[00:04:09,520]** And by the way, if you want to learn how to build and sell AI systems

**[00:04:12,320]** that businesses actually pay for,

**[00:04:14,080]** then that's pretty much all we do

**[00:04:15,520]** over at the RoboNuggets community.

**[00:04:17,040]** We are not only do you get access to the Claude Living Master class,

**[00:04:20,080]** which we update every week and takes you from zero

**[00:04:22,320]** to a mastery with the latest on AI,

**[00:04:24,000]** but you also get access to our agents as a service course,

**[00:04:26,720]** which walks you to how to actually get paid

**[00:04:28,960]** for all these AI skills that you are learning.

**[00:04:31,120]** You also get to be part of a genuinely great community

**[00:04:33,760]** of AI builders.

**[00:04:34,720]** In fact, you can see just some of the recent wins

**[00:04:36,640]** our members are getting from the program right here.

**[00:04:38,880]** So if you want to start earning from AI,

**[00:04:40,320]** then check that just in the pinned comment below.

**[00:04:42,000]** Now back to the video.

**[00:04:43,200]** And the first one is to integrate Jev

**[00:04:44,960]** with your own agentic operating system,

**[00:04:46,720]** basically the way you work with your agents

**[00:04:48,720]** so that you can get faster results and cheaper systems.

**[00:04:51,920]** So less token burn.

**[00:04:53,280]** Now because the way we use agents differ

**[00:04:55,040]** depending on the work that we do,

**[00:04:56,720]** I'm sure that you can also find ways to use Jev

**[00:04:58,640]** outside of what I'll talk about.

**[00:05:00,160]** But just to give you an idea,

**[00:05:01,360]** here are two use cases that I am testing out

**[00:05:03,600]** so far using this model.

**[00:05:05,360]** The first one is around model routing,

**[00:05:07,200]** which is basically letting Jev automate

**[00:05:09,120]** the choice of the model,

**[00:05:10,560]** depending on the task that we are giving Claude.

**[00:05:12,800]** And this is important because remember,

**[00:05:14,400]** it is not really practical for you to use

**[00:05:16,560]** Fable all the time because out of all the models,

**[00:05:18,800]** that is the most expensive.

**[00:05:20,240]** Same thing with Opus,

**[00:05:21,040]** if you just default to Opus every time,

**[00:05:23,200]** then that can also drain your usage quite a lot.

**[00:05:25,520]** And for a lot of tasks,

**[00:05:26,560]** sometimes Sonnet and Haiku,

**[00:05:28,640]** which are the cheaper models,

**[00:05:30,160]** are actually enough.

**[00:05:31,440]** But the problem there is,

**[00:05:32,560]** for you to switch to these models

**[00:05:34,480]** and decide the right model for each task,

**[00:05:36,720]** that the decision usually lies with you as the user.

**[00:05:39,360]** And so there wasn't really a quick

**[00:05:40,880]** and cost-effective way for us to automate model routing

**[00:05:43,680]** up until Jev.

**[00:05:44,880]** And so to set this up,

**[00:05:45,760]** you can just use this prompt for you to get started.

**[00:05:47,920]** And just to give you a visual demo

**[00:05:49,600]** of the tasks that I set up,

**[00:05:51,120]** essentially what I ask Claude to do,

**[00:05:52,800]** is to do a comparison of around 12 prompts with Jev,

**[00:05:56,240]** and another one where it's running

**[00:05:57,440]** with Fable 5.1 every time.

**[00:05:59,040]** And you can see here that because of Jev,

**[00:06:00,880]** and the fact that it's actually routing

**[00:06:02,640]** to the right model,

**[00:06:03,680]** depending on the task,

**[00:06:04,800]** it actually resulted to 70% savings,

**[00:06:07,120]** because nine out of those 12 tasks

**[00:06:09,200]** never needed the top model anyway.

**[00:06:10,960]** So that is quite useful,

**[00:06:12,160]** but obviously you have to try it out

**[00:06:13,440]** for the work that you do specifically.

**[00:06:15,360]** Just to see if the output that you are getting

**[00:06:17,120]** is still good enough in exchange

**[00:06:18,800]** for the tokens that you are saving.

**[00:06:20,480]** But it's just great that we now have this new class

**[00:06:22,560]** of AI models that can actually do

**[00:06:24,400]** these types of decisions for us.

**[00:06:26,160]** Now in practice, if you're testing this out,

**[00:06:27,920]** I do advise you to make a skill command first,

**[00:06:30,400]** where you can switch Jev off or on.

**[00:06:32,560]** For example, here in this Claude session,

**[00:06:34,160]** you can see I typed in slash Jev on.

**[00:06:36,400]** And so for this whole session,

**[00:06:37,360]** whenever I assign it tasks,

**[00:06:38,880]** Claude will now use Jev in order to find

**[00:06:40,960]** the right model for that task.

**[00:06:42,560]** One example of that is this where I ask it

**[00:06:44,640]** to find the file path,

**[00:06:45,760]** where the Jev router script lives.

**[00:06:47,520]** You can see that for that task,

**[00:06:49,120]** Jev actually assigned a high-go helper,

**[00:06:51,120]** which is the cheapest model,

**[00:06:52,400]** to find that file path,

**[00:06:53,760]** which is much more efficient for your token usage.

**[00:06:56,240]** Because if Jev wasn't there routing to high-go,

**[00:06:58,880]** then we would have used Opus 5 here,

**[00:07:00,640]** which is the default that I'm using for this session.

**[00:07:02,960]** The second use case is making Claude become more efficient

**[00:07:05,440]** when finding the right skills.

**[00:07:06,960]** So again, this is just a visual demo of a test that I ran.

**[00:07:09,920]** But essentially, what this shows is 14 tests,

**[00:07:13,120]** where if you send it a prompt,

**[00:07:14,640]** and you ask it to find a specific skill in my workspace,

**[00:07:17,920]** you can see here that Jev takes much less time

**[00:07:20,640]** to find the right skills,

**[00:07:22,080]** versus if you just default to something like Opus 5, for example.

**[00:07:26,000]** And so in total, for those 14 tests,

**[00:07:28,640]** Jev was able to find the right skill within five seconds,

**[00:07:31,360]** while Opus 5 took around 30 seconds.

**[00:07:33,680]** And just to show you how Jev was used

**[00:07:35,520]** in this specific use case,

**[00:07:37,120]** basically your input is the test that you are trying to do.

**[00:07:39,840]** Jev then looks at that,

**[00:07:41,200]** and the options that it can choose from

**[00:07:43,280]** would be your skills itself.

**[00:07:44,720]** So at least for me, if you can see,

**[00:07:46,400]** I have something like 145 skills in my workspace.

**[00:07:49,840]** And so because Jev is really quick,

**[00:07:51,440]** it can almost instantly output the right skill

**[00:07:54,000]** from that list, which Claude then loads.

**[00:07:56,480]** And so if you want to test that out for yourself,

**[00:07:58,320]** then you can just copy this prompt

**[00:07:59,840]** and send it to your agent.

**[00:08:01,120]** Now beyond just level one of giving you

**[00:08:02,960]** faster and cheaper systems,

**[00:08:04,320]** if we get to level two,

**[00:08:05,440]** this is actually how we use Jev

**[00:08:07,360]** for more business use cases.

**[00:08:09,120]** Because with Jev, you can actually make automations

**[00:08:11,120]** that are almost at lightning speed

**[00:08:12,880]** and doesn't cost as much as the other AI models.

**[00:08:15,840]** And just to give a visual demo,

**[00:08:17,120]** let's say you have 800 emails,

**[00:08:19,040]** and the automation that you are building

**[00:08:20,560]** needs to answer a business question,

**[00:08:22,240]** which for this case,

**[00:08:23,040]** we want to know which of these emails

**[00:08:24,720]** are actually leads that we can contact.

**[00:08:26,560]** But obviously it can be others,

**[00:08:27,840]** like if these are customer support tickets,

**[00:08:29,840]** then you can triage,

**[00:08:30,720]** which ones are needing the most support.

**[00:08:32,560]** But at least for this demo,

**[00:08:33,760]** what will show is Jev doing the classification here

**[00:08:36,560]** in this column,

**[00:08:37,360]** and then we'll also use Haikou as well as Fable

**[00:08:40,320]** in order to show the difference

**[00:08:41,760]** between the speed and cost of these models.

**[00:08:44,400]** So when I click run,

**[00:08:45,360]** these will now show the time it took

**[00:08:47,040]** for these models to classify each of these emails in full.

**[00:08:50,400]** So let's go ahead and run that.

**[00:08:51,920]** And as you can see,

**[00:08:52,880]** that took Jev like no time at all.

**[00:08:54,800]** Within less than a second,

**[00:08:56,320]** it was able to classify all of those leads,

**[00:08:58,640]** whether they're warm,

**[00:08:59,520]** whether it's not a lead,

**[00:09:00,480]** whether it's cold,

**[00:09:01,360]** which is much faster and much cheaper

**[00:09:03,600]** versus these other models.

**[00:09:05,360]** And so when it comes to business automations,

**[00:09:07,120]** that is where Jev really shines.

**[00:09:09,040]** If you have a huge volume of things,

**[00:09:11,200]** and there's a business question

**[00:09:12,480]** that's associated to those things,

**[00:09:14,160]** then this is a good candidate for you to use Jev in.

**[00:09:16,880]** So for example, in Enterprise,

**[00:09:18,480]** there's a huge industry

**[00:09:19,600]** with regard to detecting invoice fraud,

**[00:09:21,680]** spam detection software,

**[00:09:22,880]** also has a good use case for this.

**[00:09:24,720]** Community moderation is another,

**[00:09:26,720]** saying when it comes to high volume requests

**[00:09:28,640]** for any refunds,

**[00:09:29,600]** and even classifying your customers

**[00:09:31,520]** if they are churning or not.

**[00:09:32,960]** If you're running a subscription software business,

**[00:09:35,040]** for example, and so that's the pattern

**[00:09:36,640]** that I think would be good for you to think about

**[00:09:38,320]** in your company or in your business.

**[00:09:40,000]** What are the things that you are receiving in volume

**[00:09:42,400]** that you need to classify?

**[00:09:43,680]** And if you introduce Jev in there,

**[00:09:45,040]** and because it is so quick and it is so cheap,

**[00:09:47,440]** then you'll be able to upgrade your automations

**[00:09:49,840]** to just a few prompts.

**[00:09:51,440]** And finally, we get to level three,

**[00:09:53,120]** which is building apps

**[00:09:54,480]** that have now just become possible

**[00:09:56,080]** and cost effective

**[00:09:57,200]** because of system one models like Jev.

**[00:09:59,600]** And again, this differs per person,

**[00:10:01,040]** but just to give you an idea

**[00:10:02,240]** of what I immediately use it for.

**[00:10:04,240]** In our line of work, as you might expect,

**[00:10:06,000]** I generate a lot of images as well as videos.

**[00:10:08,800]** And I put them all here in my OS,

**[00:10:10,480]** which I name as rubric.

**[00:10:11,920]** Now, because I have hundreds of images on here,

**[00:10:14,320]** it's often the case that I need

**[00:10:15,440]** to search for specific images.

**[00:10:17,280]** And let's say if I type in cloud in here,

**[00:10:19,280]** unfortunately, what this will give me

**[00:10:21,280]** are images where the file names contain the word cloud.

**[00:10:24,240]** So it's sort of like your standard control F.

**[00:10:26,480]** But if we integrate Jev into that image search,

**[00:10:28,880]** and this is just a quick demo

**[00:10:30,080]** so that I can show you side by side,

**[00:10:31,920]** five-type cloud in here,

**[00:10:33,360]** you can see that the file name search here

**[00:10:34,960]** returns only a few results,

**[00:10:36,880]** but the search powered by Jev actually enables us

**[00:10:39,520]** to search images and videos by meaning

**[00:10:41,840]** instead of just the file name.

**[00:10:43,280]** And so if you have an application

**[00:10:44,480]** where users need to search for things a lot,

**[00:10:46,560]** then Jev might be good to try to see

**[00:10:48,320]** if that is going to improve user experience for your app.

**[00:10:51,680]** Another application that I found

**[00:10:53,120]** that is powered by Jev is this one from Kitsi,

**[00:10:55,760]** who made this app called Unclutter.

**[00:10:57,680]** And basically what it does is it's a Chrome extension

**[00:11:00,240]** where whenever you toggle it on,

**[00:11:01,880]** it basically auto cleans up pages from any elements

**[00:11:05,120]** that are classified as Slop.

**[00:11:06,960]** And the one that is doing that classifying

**[00:11:09,040]** is Jev under the hood.

**[00:11:10,240]** And it basically just looks at all of the elements

**[00:11:12,040]** in the page, gives a quick decision

**[00:11:13,800]** if they are ads, if they are cookie banners,

**[00:11:15,920]** and it just removes all of that

**[00:11:17,360]** when this switch is toggled.

**[00:11:18,680]** And so there you go, that is what Jev is

**[00:11:20,480]** and a few use cases and ideas for you to take advantage

**[00:11:23,760]** of this new paradigm by which AI models are created and used.

**[00:11:27,760]** I hope that was useful and as usual,

**[00:11:29,360]** thanks for watching until the end.

**[00:11:30,720]** And I'm also curious like what would you use Jev for?

**[00:11:33,480]** Let me know down below and I'll see you all next time.

**[00:11:35,680]** Cheers.
