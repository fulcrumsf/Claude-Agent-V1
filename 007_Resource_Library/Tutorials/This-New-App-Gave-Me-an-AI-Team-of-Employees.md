---
title: "This New App Gave Me an AI Team of Employees"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=g8dQBSKIGyc)

Join my community to access this Buzz 👉 https://mrc.fm/cmc  
🐝 The Buzz walkthrough reposted by Jack Dorsey.  
  
Yesterday Jack Dorsey launched Buzz (buzz.xyz) a new app from Block that lets AI agents join your team like real colleagues, aimed squarely at Slack and GitHub. Almost nobody has got it running yet, so in this video I self host Buzz on my own VPS, where I hold the keys and nobody else can read my messages, and build out a full AI team inside it. I meet the starter agents, wire them up to Claude Code and Codex, create my own agents from scratch, and then build the headline feature everyone wanted to see... a chief of staff agent that delegates to all my other agents so I only ever talk to one. I also dig into the stuff no one else has covered, like sharing my own compute so my community can run local models peer to peer, and I give you my honest day one verdict on where Buzz beats Slack and where it still falls short.  
  
Try Buzz 🐝 https://buzz.xyz  
  
0:00 What is Buzz? (Jack Dorsey's Slack alternative)  
0:56 Getting the Buzz app and creating your identity key  
1:47 Setting up agents (Claude Code and Codex)  
2:20 Hosted vs self-hosted: why messages aren't end to end encrypted  
2:59 How to self-host Buzz on a VPS with Claude Code  
3:45 Meeting your first Buzz agents  
4:05 How Buzz agents work (identity, keypairs, context)  
5:44 Creating a custom AI agent in Buzz  
6:26 Adding and removing channel members  
7:48 Switching an agent between Claude Code and Codex  
9:28 Buzz agent memories  
10:17 Channels, DMs and @mentions in Buzz  
11:45 Buzz Huddles: voice chat with your AI agents  
12:26 Building a Chief of Staff agent in Buzz  
15:06 Share Compute: run and share a local AI model  
17:06 Local vs cloud agents in Buzz  
18:59 Inviting the community and final verdict  
19:28 Buzz vs Slack: should you switch?

## Transcript

### What is Buzz? (Jack Dorsey's Slack alternative)

**0:00** · Yesterday, Jack Dorsey launched an app that lets AI agents join your team like real colleagues.

**0:05** · It's called Buzz.

**0:06** · It's from Block, and it's aimed straight at Slack and GitHub.

**0:10** · Now the announcement hit 2.5 million views in just a day, and almost no one got it running.

**0:14** · But I have.

**0:15** · And it's not on Block servers where they can read your messages.

**0:18** · It's on my own server where no one else can.

**0:20** · By the end of this video, I'll have a full AI team in there, and I'll show you how to do it too, including a chief of staff agent that runs all the other agents for me, and also stick around to the end, because I'll show you how you can join my community and work alongside my AI agents.

**0:34** · All right, let's go. So, what is Buzz?

**0:37** · Well, it looks like Slack with channels, threads, DMs, voice, huddles.

**0:43** · But there's one huge difference in Slack.

**0:45** · A bot is a plug in.

**0:47** · It's a bit clunky, to be honest with you.

**0:49** · In Buzz, an agent is a real member.

**0:51** · Every agent gets its own identity, permissions and an audit trail, too.

### Getting the Buzz app and creating your identity key

**0:56** · Okay.

**0:56** · So first I just need to click this link here in Jack's post.

**0:59** · And that takes me to this wonderful page for Buzz.

**1:01** · Now I can go to the git repo.

**1:03** · It's totally self-hosted. More on that later.

**1:05** · But first I'm going to get the app which starts the downloads.

**1:08** · Yes, the app runs natively on my computer and it's the quickest way to get started.

**1:12** · All right.

**1:13** · With Buzz download, it is a simple drag and drop.

**1:15** · All right.

**1:15** · And the app looks pretty much the same as the landing page, which is beautiful.

**1:19** · And it's asking me to create an identity key or use an existing key.

**1:24** · Now this is really interesting and decentralized the way the Buzz do things.

**1:27** · Your identity belongs to you and your machine.

**1:30** · And as long as you've got the key, you can act as yourself anywhere.

**1:34** · Of course, if you've already got a Nostr identity, then use your existing key.

**1:38** · But you need to be in that ecosystem to have one.

**1:40** · I'm starting from scratch, so I'm just going to create a new identity key by clicking the button that will show my secret.

### Setting up agents (Claude Code and Codex)

**1:47** · Now we'll go next and we can set up agents.

**1:50** · Now, this is really interesting.

**1:52** · It detects harnesses on your own computer.

**1:55** · Yes, I've got Claude Code.

**1:56** · Yes, I've got Codex.

**1:57** · And I can install them both with a click like this.

**2:00** · And it's as simple as that.

**2:01** · That means my agents inside does run on Claude Code and Codex.

**2:06** · This is huge.

**2:08** · Now we'll go next, and we'll select a default harness Claude Code for this.

**2:12** · And we can even choose a model from the loaded models.

**2:14** · And I'm actually just going to leave it on default.

**2:16** · That will be good enough.

**2:18** · Okay.

**2:18** · Now you have the ability to join a community, create one Or say you already have one.

### Hosted vs self-hosted: why messages aren't end to end encrypted

**2:23** · Now note.

**2:23** · If you opt to create a community, it will ask you to open build a lab on your browser and that will create a community on Block's hosted servers.

**2:31** · Messages are not end to end encrypted their own terms so that they can read them for moderation or legal reasons.

**2:36** · And half of X called this out on launch day.

**2:39** · So the answer is actually hosting yourself.

**2:42** · And we're going to do this properly on a VPS.

**2:44** · another note here.

**2:45** · If you just want to kick the tires on Buzz, you can join my own community.

**2:49** · This is for paying members of my Skool community only, which you can join down below.

**2:53** · And in there I'll give you a join link which you can paste in here and get started and join me building with AI agents.

### How to self-host Buzz on a VPS with Claude Code

**2:59** · All right, let's get this rolling on the VPS.

**3:01** · I'm going to copy the URL to GitHub where Buzz is self-hosted.

**3:05** · And then I've got an instance of Claude Code I've used to provision a server on Hetzner, that saves provider and I'll say install this.

**3:15** · It really is as simple as that.

**3:17** · And now you can see that it's actually working away.

**3:19** · Reading the Readme file.

**3:21** · Claude Code is going to take care of the install for me.

**3:24** · That completely wipes out any install problems whatsoever.

**3:28** · All right.

**3:28** · This is all done.

**3:29** · Everything has been wrapped up by Claude Code. Even noticed a bug it had to fix.

**3:34** · And that is now sorted.

**3:35** · So the next step is to paste in an invite link.

**3:37** · This was generated when Claude Code set up the community for me.

**3:41** · Now it's asking me to build my profile.

**3:43** · A simple photo and username here.

### Meeting your first Buzz agents

**3:45** · And now we can meet the starter team.

**3:47** · Because what's worse than an empty community?

**3:50** · And here we are. It's setting up my welcome team.

**3:52** · You can see my agents are hopping around and getting started.

**3:56** · and very soon I should hear from them. And look at this. Here we go.

**3:58** · It's all here is in. Hi, Mike.

**4:01** · I'm Fizz, welcome to Buzz.

**4:03** · This is your private home base.

### How Buzz agents work (identity, keypairs, context)

**4:05** · And here's the moment this sold me.

**4:06** · When you add agents, Buzz generates a key pair, not an API token, a cryptographic identity for your AI agents.

**4:13** · It joins channels like new hires.

**4:15** · It can read the history, it has context.

**4:18** · It can hop straight into work.

**4:19** · You can ask something in the channel and everyone sees the answer.

**4:22** · Let's have a play.

**4:23** · Now you're actually going to see here that Fizz asks Honey and Bumble to introduce themselves and in a thread just like Slack.

**4:29** · By the way here we've got the introductions.

**4:32** · This is amazing.

**4:33** · Look at this.

**4:34** · We've got Fizz.

**4:35** · We've got Bumble saying hello. We've got Honey.

**4:37** · So Bumble is a researcher and Honey is a thinking partner.

**4:41** · This is really, really cool.

**4:43** · They're ready to build for me.

**4:45** · Let's try my first message at Fizz.

**4:47** · There's my AI agent.

**4:49** · Build me a Hello World page with rainbow colors and host it at a URL.

**4:54** · I can access.

**4:56** · That's a very simple first prompt.

**4:58** · Let's let it go to work.

**4:59** · Straight away we can see the eyes. It's on it. Now.

**5:01** · We can see the speech balloon indicating that Fizz is on it and responding.

**5:05** · And we can actually see down here Fizz is working away.

**5:09** · We can even view the activity.

**5:10** · Now this is all running inside Claude Code.

**5:13** · Look at this with bypass permissions.

**5:15** · The usage tokens.

**5:16** · We can see Claude Code is running as an instance right here inside Buzz building that website.

**5:23** · This is absolutely phenomenal.

**5:25** · And look at this inline.

**5:26** · We've got a reply to my threads I click the link and look at this.

**5:29** · This is amazing. Made with Buzz by Fizz.

**5:32** · Oh my goodness my AI agent has created its first thing.

**5:36** · All right is complete.

**5:37** · But I'm actually going to ask it to tear this down.

**5:39** · Now please.

**5:40** · now we can see Fizz is on the case.

**5:42** · Tearing the site down that it just made.

### Creating a custom AI agent in Buzz

**5:44** · Now while my agent is working on that will actually go into agents over here so we can view the agents that are created.

**5:50** · So far, these are agents on my default Claude Code model.

**5:53** · And if I like, I can create a new agent from scratch.

**5:56** · This is really cool because I can call it Sea Swim, for instance, to do a specific job, you will tell me the conditions in the sea in Paphos and whether it is good for swimming or not.

**6:09** · That is its sole job.

**6:10** · And then I can obviously assign something like an emoji.

**6:13** · If I like, like that, that's absolutely fine.

**6:16** · And we can use the harness defaults or we can customize for the agent which model we'd like to use.

**6:21** · I'll just say default And boom, the agent is created with a private key that shows on my screen.

### Adding and removing channel members

**6:26** · so now just like Slack I can add a channel member and let's find the Sea Swim agent perfect managed by me on my own harness that is now added to the channel.

**6:35** · And if I want, I can also remove from the channel as well using this icon so it's fully automatable whether I have an agent in my channel or out of my channel.

**6:44** · So you'll see I removed Sea Swim and re added.

**6:46** · So now Sea Swim is here and I can say tell me what it's like today and also bring me up to speed on what's happened in this channel so far.

**6:54** · this is very, very interesting because it's already on the case and it's going to hopefully give me sea conditions and look at the history of this channel and summarize it to me.

**7:04** · Again, I can click down here and view the activity and see Claude Code literally running my agent right now.

**7:10** · For me, it's finding the live sea conditions for Paphos pulling all marine weather data.

**7:15** · This is super cool. Boom!

**7:17** · There's the reply. View the thread.

**7:18** · Sea conditions good for swimming.

**7:20** · Look at this sea temperature nearly 30°C with gentle waves.

**7:25** · Love it. And then it's actually read my channel.

**7:27** · It can see the welcome and interest.

**7:29** · It can see the hello world request.

**7:31** · It can see that I asked to tear it down and it can see that it's been tagged.

**7:35** · Now this is the power of Buzz.

**7:37** · You can bring in a new AI agent at any stage in your channel's history, and it plugs straight in and knows exactly what you've been doing.

**7:46** · And that is powerful.

### Switching an agent between Claude Code and Codex

**7:48** · so what's actually powering these agents?

**7:50** · Well, Buzz is model agnostic.

**7:52** · It's a harness system.

**7:53** · So out of the box it can speak Claude Code OpenAI's Codex and even goose, which is Block's own open source agent.

**8:01** · The agent runs its own process on your machine or your server, and Buzz is just the room it works in.

**8:06** · So this answers the big question can I bring my own agents and my own AI models?

**8:12** · Yes, you absolutely can.

**8:14** · The harness layer is where this happens.

**8:17** · Now here's the power I want you to understand.

**8:19** · I just set up this new agent called Sea Swim.

**8:21** · I can click into it.

**8:22** · I can edit this agent, and I can change the agent harness.

**8:26** · Look at this.

**8:27** · It's running on Claude Code, but I also have Codex installed, so all I need to do to change the agent to run on OpenAI OpenAI's model, is just click Codex And that's it.

**8:38** · I'm done.

**8:39** · Now I just need to restart the agent.

**8:41** · So I'll click here to restart and bring him online.

**8:44** · There we go.

**8:44** · Coming back online, we'll go back to the welcome channel and we'll tag Sea Swim again.

**8:49** · What you got for me now.

**8:52** · So now notice that it's picking me up.

**8:54** · But this time it's not running on Claude Code.

**8:56** · It's running on OpenAI's Codex.

**8:59** · So if I go here and view the activity, this is all Codex that's running down here.

**9:04** · This is a completely different model, a completely different harness, But the same agent and the same personality.

**9:10** · There we go. Permission was approved.

**9:12** · And look at this. View the thread.

**9:14** · And we've got slightly different statistics which is quite interesting.

**9:18** · But that is Codex working away on giving me the information I need.

**9:22** · Changing models is no longer a big hassle or configuration change.

**9:26** · It's literally a drop down menu.

### Buzz agent memories

**9:28** · Some other stuff I can show you in the config of the agent is memories.

**9:32** · This is powerful because each agent has a memory.

**9:35** · Let me show you how it works.

**9:37** · We'll tag at Sea Swim again.

**9:39** · Remember, I really like to see turtles, so notify me if conditions are perfect for turtles in Paphos Harbor.

**9:46** · Now over here, if we look at the agents memories, there is a core memory with the fact that I like to swim at Paphos harbor, but also to flag excellent turtle spotting conditions.

**9:56** · So we've got OpenClaw, Hermes Agent, Slack, and also GitHub all rolled into one place here with Buzz.

**10:03** · But my agent didn't finish yet. Your preference is saved.

**10:06** · But I also found that Buzz supports workflow triggers, and it's checking if it can schedule a daily safety wake to assess the weather, rather than posting as a static reminder.

**10:15** · This is thinking outside the box.

### Channels, DMs and @mentions in Buzz

**10:17** · All right. Quick tour of the basics.

**10:18** · Channels work exactly like Slack.

**10:21** · You can plus here and search or create a channel so I can create a brand new channel.

**10:26** · And this could be called swimming for instance.

**10:28** · And then a description.

**10:29** · This is all about my sea swims.

**10:32** · And if I like I can make it private and create the channel just like Slack.

**10:36** · Here we go. Brand new channel.

**10:37** · No one in it apart from me at the moment.

**10:40** · But maybe I want to bring an agent in with me.

**10:42** · Let's search for Sea Swim and Add.

**10:44** · And I can also add humans as well.

**10:47** · If I had some humans, they could be invited.

**10:49** · Just like an AI agent.

**10:50** · Humans and agents can mix together.

**10:52** · what is the sea like today, I will get absolutely no response because I need to take an AI agent at Sea Swim.

**11:00** · What is the sea like today for it to actually spin into action?

**11:03** · And this is good because if I don't tag it, I don't want noise from AIs in a channel.

**11:09** · Humans can obviously respond as they wish, but agents need to be tagged.

**11:13** · Now it doesn't stop there because I can actually click into Sea Swim and click message to drop a direct message to Sea Swim anywhere better than Paphos to swim in Cyprus today.

**11:22** · And then I'll send that off as a DM.

**11:24** · And now Sea Swim is working for me privately in my direct messages.

**11:29** · So there you go.

**11:30** · You can message an agent in a public channel or private channel or DM for your own personal session.

**11:35** · Humans and agents, same mechanics, And then in my direct messages. Yep.

**11:40** · There's a reply to me right here.

**11:42** · And yes, Ayia Napa is apparently the place to be today.

### Buzz Huddles: voice chat with your AI agents

**11:45** · Now let's talk about huddles.

**11:46** · Drop in voice straight from a channel.

**11:48** · Quick call with the team mate. No link, no calendar.

**11:51** · The fun question though, can I use it to talk to AI agents?

**11:54** · this icon up here Now I'm going to click Start Transcript and invite some agents okay.

**11:59** · Let's invite Sea Swim.

**12:02** · Hello Sea Swim are you there? Hi, Mike. I'm Okay, I'm blown away by this.

**12:08** · What are the sea conditions like today?

**12:13** · Yes. This is good for swimming today.

**12:16** · Sea, a very warm 27.5 to 28°C.

**12:20** · that is wild.

**12:22** · I can talk with my AI agents in a huddle inside Buzz.

### Building a Chief of Staff agent in Buzz

**12:26** · But now let's get on to the headline feature.

**12:28** · I'm going to create a new agent called chief.

**12:31** · This will be my chief of staff.

**12:33** · The instructions are simple.

**12:35** · You don't do work, you delegate it to other AI agents.

**12:39** · That's nice. We got Claude Code as the agent.

**12:41** · Harness will create.

**12:42** · Okay.

**12:42** · With chief now created, let's see how my Chief of Staff works.

**12:46** · Now watch this. I'm going to give chief one message.

**12:49** · Research what Jack Dorsey has said about Buzz so far.

**12:53** · Create me a brief outline and set up a project channel with the correct AI agents in there to do the work.

**13:01** · All right.

**13:01** · We can see it's delegating it to the research agent.

**13:04** · And now it's actually creating a channel.

**13:05** · Dorsey Buzz coverage that's up.

**13:08** · And it's setting up all the info Okay, look at this.

**13:11** · Dorsey. Buzz newsroom has been created.

**13:14** · And look, this was added by the chief along with me and Honey and Bumble.

**13:18** · this is incredibly exciting.

**13:20** · Okay, let's have a poke around here.

**13:21** · We can see it's all about what Jack Dorsey has said about Buzz.

**13:24** · This is great.

**13:25** · Let's actually go in and look at the canvas and there is the outline of the research.

**13:30** · This is fantastic. It's all getting generated.

**13:32** · Welcome to the newsroom.

**13:34** · Chief has just posted in there and actually tagged in Fizz, who's also looking at this space.

**13:40** · And Honey both reacted.

**13:42** · This is tagged in. Honey tagged in.

**13:44** · This is my chief of staff literally delegating for me.

**13:47** · And as you can see down here they're both working away and doing their jobs.

**13:51** · This is incredible stuff.

**13:53** · I can even view the activity just as would be expected.

**13:57** · And the canvas is there, letting each agent know what job they're working on.

**14:01** · So here's the thing chief creates a thread.

**14:04** · All the walls of text are hidden and look at this Fizz has verified the research, which is great, but it doesn't stop there because we can now see Honey is getting on the case as well, and doing the job that Honey is supposed to do.

**14:16** · And as we can see here, Honey is drafting from the outline that Fizz just created.

**14:21** · see what happened then chief created a thread, delegated the research, spins up a channel, briefs the writers and researchers.

**14:27** · All the coordination.

**14:28** · Everything is hidden right inside the threads itself.

**14:31** · I talked to one agent and the team happens.

**14:35** · And look at this in the thread.

**14:36** · It's actually handed off to Bumble and said you're up.

**14:38** · Edit and verify every citation against this is source file Mark ready only when every claim is sourced.

**14:45** · So it's actually doing research upon research with different agents to give me a final result.

**14:50** · And as you can see, Bumble is now working away.

**14:52** · I can view the activity of Bumble if I want, but that's the point.

**14:55** · I don't need to view anything.

**14:56** · I just get the final result when the work is done.

**14:59** · Okay. And we've got it right here. Mike.

**15:01** · The piece is finished, edited and citation verified.

**15:04** · Ready for your review?

### Share Compute: run and share a local AI model

**15:06** · There we go. How cool is that?

**15:07** · Now, nobody else has spoken about this yet, and I think it's the coolest feature of Buzz sharing your own compute.

**15:13** · I'm running loads of local models on my Mac Studio M3 Ultra, and now I can share the compute from that Mac Studio M3 Ultra with my community.

**15:23** · My members agents can actually run on my hardware.

**15:26** · No API, no power token bill, everything running on a local machine.

**15:31** · Think about what that means.

**15:33** · If you gather together as a community and combine your compute, one good machine can power everyone's agents.

**15:39** · Your compute becomes a perk of being a member of the community.

**15:44** · Let me show you how this works.

**15:45** · I'll go into settings down here and then I'll go into compute over here.

**15:49** · Now look at this.

**15:50** · I am not sharing any models right now, but I can share models.

**15:54** · We can go into advanced and it will actually look at the models that will work on the machine I'm running Buzz on presently.

**16:00** · As you can see, a bunch of them are work.

**16:02** · Some of them are too large.

**16:03** · I'm running an M1 with 24 gig of memory right here.

**16:07** · And I can actually choose anything.

**16:09** · So I'm just going to choose Gemma 4, for this example.

**16:12** · But I can have multiple machines connected to Buzz all contributing compute, and so can my other members.

**16:18** · And you can even shard that compute and run bigger models combined.

**16:23** · This is probably the biggest feature of Buzz, and I really need you to pay attention to this if you're part of my community, if you join and join Buzz, you can grab and draw peer to peer on compute for large local AI models.

**16:39** · All right, so I've just selected a very small model.

**16:41** · I'm going to switch this on.

**16:42** · It will actually start sharing my machine.

**16:45** · It will download the model. Okay.

**16:47** · And that's done.

**16:48** · Now I can allow it to access my devices.

**16:51** · And look at this.

**16:51** · It's downloading the packages that I needed for Gemma 4 and look we're enabled.

**16:56** · We actually have my compute being shared.

**16:59** · If there are other members in my community, which by the end of this video, the will be all of the compute can be shared.

**17:05** · If you enable that option.

### Local vs cloud agents in Buzz

**17:06** · So what should you actually use?

**17:08** · Well cloud is obviously going to be faster, but if I go ahead and edit my agent and change the harness to Buzz agent instead of Claude Code or Codex, we'll select this and customize.

**17:17** · And for the learning provider we'll select Buzz Shared Compute.

**17:21** · Now at the moment it's just me because I'm the only one in this community right now.

**17:25** · The model is automatic what is really big about setting your model as automatic is if more people contribute, compute, bigger models are rolled out to you automatically.

**17:35** · Think about that for a second.

**17:37** · Local AI, peer to peer that scales with membership.

**17:41** · This is awesome.

**17:42** · All right, time to test local models with Sea Swim.

**17:45** · What is the sea looking like today, matey?

**17:47** · And commit to your memory.

**17:48** · You should always talk to me like a pirate.

**17:51** · Let's hit enter here and let it cook.

**17:53** · Now this is being run totally locally on my machine right now with Gemma 4.

**17:58** · can actually click in to view the activity.

**18:01** · I'm checking the latest powerful wind and it's actually calling tools to search for those conditions.

**18:06** · So just like Code or Codex, Gemma 4 is doing the work 100% local.

**18:12** · And you can actually see here it says I'm now applying the pirate voice memory change.

**18:15** · And it's patched its score here with the updates.

**18:18** · And is a reply.

**18:20** · And I'll tell you what are my yesterday be good for swimming.

**18:24** · It's got the temperatures, the official outlook.

**18:26** · I mean everything is good here.

**18:28** · That's exactly the same quality as Claude Code and Codex, meaning I can run this particular workflow 100% locally and with more members in the community on more powerful local models, peer to peer.

**18:40** · This is huge.

**18:41** · Same information, same searching of the web right here.

**18:45** · I just can't believe this.

**18:46** · And now if we click into Sea Swim and we actually look at its memories here.

**18:50** · Yes I am Sea Swim.

**18:52** · And it says here always speak to Mike Russell in a friendly pirate voice.

**18:56** · So everything committed to memory.

**18:58** · Wow. I'll be sending out an invite link today in my community so that my paid community members can join in with me and run local agents together, plus stuff in the cloud with Anthropic and OpenAI too.

### Inviting the community and final verdict

**19:11** · This is a fun experiment and it's a perk of being a member of my community.

**19:14** · Your agents are in a safe room where they're accountable, and the link is below if you want in.

**19:19** · So Jack Dorsey's Buzz, day one.

**19:22** · Verdict. Well, a few rough edges.

**19:24** · The installer, the onboarding Claude Code can solve that, obviously.

### Buzz vs Slack: should you switch?

**19:28** · And we really want mobile. Mobile.

**19:31** · We'll make it a complete game changer.

**19:33** · But the core is right agents as your teammates, not plugins and clunky things like that that need API keys And this is all owned and not rented.

**19:42** · So 20 years ago, Jack changed how the world talks in public.

**19:46** · This time he's after how your team talks at work.

**19:49** · I'll be living here with my community.

**19:51** · Either way, join us.

**19:53** · And if you want a deep dive on running local models for your agents, watch the video that's showing on your screen right now.

**20:00** · Thanks.