---
title: "Claude-Code-Just-Fixed-MCP-S-Biggest-Problem"
type: tutorial
category: video-production
tags:
  - tutorial
  - how-to
  - claude-code
  - mcp
  - video-production
created: 2026-06-06
source: 000_Ingest/Claude Code Just Fixed MCP's Biggest Problem.md
---
![](https://www.youtube.com/watch?v=itS3f1Y52t0)

Claude Code just shipped a feature that solves one of the biggest headaches with MCP servers: context window bloat. If you've been loading multiple MCP servers into your coding agent, you might be burning through 25% or more of your context window before you even send your first prompt.  
  
In this video, I break down why MCP tools consume so much of your context window, what "context rot" means for your coding sessions, and how Claude Code's new tool search feature loads tools on-demand instead of all at once. I'll show you exactly how to enable it and demonstrate the token savings in a real project.  
  
What You'll Learn  
✅ Why MCP servers eat up your context window (and why that matters)  
✅ How to use Claude Code's /context command to see exactly what's consuming tokens  
✅ The tool search setting that cut my MCP token usage from 25% to 14%  
✅ Best practices for managing MCP servers in your projects  
✅ How this fits into the bigger picture of context window optimization  
  
🌐 Resources  
Model Context Protocol: https://modelcontextprotocol.io  
Claude Code Documentation: https://code.claude.com/docs  
Anthropic's Advanced Tool Use Article: https://www.anthropic.com/engineering/advanced-tool-use  
  
If you're building with MCP servers in Java or Spring, check out my other videos on this channel for getting started tutorials.  
  
👍 Found this helpful? Subscribe for more Claude Code and Spring development content.  
💬 Let me know in the comments what Claude Code topics you want me to cover next!  
#ClaudeCode #MCP #ModelContextProtocol #AI #CodingAgent #ContextWindow #Developer #AITools  
  
👋🏻Connect with me:  
Website: https://www.danvega.dev  
Twitter: https://twitter.com/therealdanvega  
Github: https://github.com/danvega  
LinkedIn: https://www.linkedin.com/in/danvega  
Newsletter: https://www.danvega.dev/newsletter  
  
SUBSCRIBE TO MY CHANNEL: http://bit.ly/2re4GH0 ❤️

## Transcript

**0:00** · Claw Code just fixed one of the biggest issues with MCP. Now, if you're new here and don't know what MCP is, check out modelcontextprotocol.io.

**0:08** · If you're a Java developer and a Spring developer, I have a bunch of videos on this channel to kind of introduce you how to build MCP servers in Java. But that's not the point of this video. The point is I want to talk about what the problem is with MCP when it comes to using coding agents and how we can go ahead and solve it using a newest version of clawed code. So I have this graphic here the context window. This is an important thing to understand. A lot of what we do is trying to overcome some of the limitations of the context window.

**0:39** · And you can think of the context window as like our memory during our conversation with a chatbot with a coding agent. And as we start to use the context window, so we define some system rules or a tool does, we define a prompt, we send a prompt to an LLM, we get an answer back, we define some tools. All of these things go into the context window. The context window has a fixed size. So if we're using something like claw is 4.5, it's like 200,000 tokens.

**1:09** · And we need to remember that because as we're adding stuff to the context window, this becomes uh critical to understand. So tools are a way to get information uh add information to the context or perform some action like send an email, send a slack message, whatever the case may be. Tools can be defined individually. So I can just define a couple of tools or I can package them up into an MCP server. And now I have a bunch of tools in a single MCP server.

**1:37** · The reason this is so important is because of something called context rot.

**1:42** · As we start to fill the window up, if we get to whatever that number is, 60%, 70%, 80%, there are a bunch of scientific papers out there that kind of talk about this, but as we start to fill it up, not all the way, but as it starts to fill up, performance will start to decline. And so, what we want to do is we want to have a limited context window. Anytime we're working on a task, we clear that context window and work on the next task. Now, as the context window fills all the way up, then we can go ahead and compact it. We can clear it.

**2:14** · But the problem with that is it's going to forget things that it previously knew. Say that you went to a co-orker and said, "Hey, go ahead and work on task one." And then after task one, that co-orker forgot everything he or she just did and had to start on task two. That's not what we do. What we want to do is keep the context window limited and spawn sub aents with new context windows to go ahead and work on those tasks. So this is the idea with the context window.

**2:43** · As it fills performance degrades, the model struggles to utilize all information again context rot especially in the middle before the oldest content is finally dropped. So that's the problem we're trying to solve and I want to take a look at how claude code has solved this. So here I'm in a project and I'll go ahead and run claude with dangerously skip permissions or yolo. Claude code has this really great slash command called context.

**3:09** · And what it does is it will show you everything that's in the current context window which is really nice to see. So here we see that we have 200,000 token context window. before we've even done anything, before we've sent a prompt, we have 73,000 tokens or 37% eaten up already. And the reason for this one is our MCP tools, but I'll get to that in a second. So, first off, we have a system prompt. I like to see here. Okay, it's 3.3K.

**3:39** · Now, you can't actually go find the Claude code system prompt. If you want to find the Claude AI system prompt, it's out there. But you can come down here and say what is in your system prompt if you're ever curious to just kind of get some insight as to what that system prompt is doing.

**3:59** · It's not super important, but I like to tinker and I like to know what's going on behind the scenes. So, this will kind of give you that answer. It'll tell you like here are the goals. Here's what uh this system prompt is designed to do. Uh the tools it has access to, safety and security, uh GitHub protocols, etc.

**4:19** · So that's really nice. Then we have system tools. So we can see that that chews up 8.5%.

**4:25** · Now again, system tools are a way to augment the the large language model, right? A lot of times it won't have access to current information or it was only trained on a certain set of data and so you need to be able to augment it with information or perform some action.

**4:43** · So if we want to see this, we can say what system tools do you have access to?

**4:50** · So if you ever curious what's kind of built into cloud code to make all of these happens to go out and fetch information from the web to be able to write files to disk, uh this is a good kind of list to kind of look at. So when we're in context, we can drill down into each of these things. So this is new. We have uh task management, file operations, being able to read, write, edit, etc.

**5:13** · We want to execute bash scripts. Um, we want to be able to kill the shell. If we want to get information, we can do a web fetch or a web search. Uh, we have this user interaction. So, if it needs to clarify some questions, it can use this ask user question. Skills are another important part of Claude and Claude code and now kind of more uh general in the ecosystem, but being able to execute a skill. Uh, planning mode is really important in Claude. If you've seen any of my videos on cloud code, I don't do anything without planning mode.

**5:44** · So, you have a enter and exit plan mode. And then you have MCP resources, being able to list, uh, being able to read. So, these tools, we can't do anything about those. We actually need here's where it gets interesting. So, MCP tools, uh, 49.1,000 tokens, uh, I'm eating 25% of the context window with all of my MCP tools.

**6:10** · Now, I will say this is a little bit of an over contrived example because I loaded a bunch of MCP servers in here on purpose. Some of them I use, some of them I don't. Um, Claud and Chrome is a really good one. Uh, if you haven't added that extension to Chrome, that's a really good one to have that can also run here in Claude. I built a silly one to kind of get latest information from my content. Uh, the Century one I really like. I use Century on this application.

**6:38** · So, it's nice to have. Uh there's Figma, there's Chrome DevTools, there's Notion, uh there's a bunch of other ones. So, my first tip here is when you're using MCP servers. They're great, but make sure you're only defining MCP servers that you actually are using. If you're not using them in this project, go ahead and disable them. If you're not using them at all, go ahead and uninstall them. So, we'll take a look at how to fix that in a second.

**7:04** · uh memory files that is the claw.md. So anytime you create a new project, you should do an an init which will create a claw.mn. This is like your memory. It tells you about the project. You can also add like custom instructions to it.

**7:18** · We just talked about skills. There's some skills in there. Messages. Here's the messages in here. And here is our free space. Okay. So what we want to get away from is this. And the reason this happens is remember back to our graphic here. We have all these things in the context window. One of those is tools.

**7:39** · So the way that um the context window works is the large language model loads or we load a list of tool definitions and the tool definition has a name, a description and an input schema. And all of those are loaded into memory. And now when we make a prompt, we send it off to the LLM. the uh LLM can see that list of tools and go, "Okay, um I don't know about Dan Vega's last three videos, but I see you've defined a tool that can help me with that. Go ahead and execute that on your end.

**8:09** · Send that information back to me, and now I can answer that query." What we want to get away from is loading all of this into context.

**8:19** · Anthropic has a really good article on this, introducing advanced tool use on the Cloud Developer Platform. they go into the problem. Um, and then this solution here, which is tool search tool. So instead of loading everything at once, they have a solution here for being able to search for tools on demand. When the LM needs something, then we can go ahead and search for it.

**8:39** · So the way that we enable this in Claude Code, let's go back to the browser.

**8:43** · Actually, if you go over to Cloud Code docs and go into settings, there are a bunch of settings that we can set. Now, we can set these at a global level. So we can say hey um everything every account or every project that we work in on this system is going to use these uh settings. We can do it at a user level.

**9:03** · We can do it at a project level. We can do it at a local level. For this particular thing, I would probably do it at a global level. I'm just going to do it in this project just to make it easier to show off. Um but you can go down and see like all of the things that we can go ahead and set in our settings file here. There are a bunch of things that we can set. And if we go down here and actually let me see where it is. Uh enable tool search is one of these uh settings that we can go ahead and set.

**9:34** · So this is under I believe the environment. Um but let's go ahead and try that. So uh what I want to do is go into my project and go into my settings file. And what I'll do is go ahead and say EMV Let's say env. And then in here, I'll go ahead and set enable tool search true.

**9:57** · Right. And I think I saw this somewhere.

**9:59** · I haven't done this yet. Um I think I I think it actually needs to be a string, but I'm not sure. So, we'll double check on that. Let's go back to the docs. Stan um auto auto true or false. So, it should just be true. No reason for it not to be a boolean. So, now that I'm going to go ahead and set that, I'm going to come back here and I'm going to exit Claude code. So, we're going to go ahead and do this again. And now we're going to go ahead and look at the context.

**10:29** · And we'll scroll back up.

**10:33** · And now we see that we uh for our MCP tools, we've gone down from 49,000 tokens, which was really 25% of the context window, down to 28,000 tokens or 14.1% of the window. And if we want to be sure that this still works, let's go ahead and say, uh, can you give me Dan Vega's last three videos? Right. Let's see if it does that. No, it won't. It wouldn't be able to do this without the MCP server.

**11:05** · It can go search the web, but it actually messes up. And you see that it's using the MCP server there. Uh, go ahead and give me the latest videos that count as three. And here are the last three videos. So, that is still working even though everything isn't getting loaded into the context at one time. So, again, this is a really big deal.

**11:23** · I love MCP servers, but one of the problems with MCP servers, if you loaded too many of them, they're eating up the context window. we quickly lose that context window, performance degrades and then eventually like things fall off and that is going to cause issues when we're trying to uh create some new features or create a project, right? So, uh I really love this from cloud code. Uh I believe that others are starting to implement this too. Um so this is an important future for MCP servers and I I hope to see more of that this year.

**11:56** · Again, all of this all of these things that we're doing uh when you see a lot of these new features come up, all of them are trying to fix this problem, right, with the context window. Like sure, some some uh large language models out there have a million token context window, which is great, but we're always going to run into this problem no matter how big the context window is, right? Because we're just going to be throwing more and more at it. So, we have to find more uh elegant ways to solve for these problems. And I think this really is one of them.

**12:27** · So, uh, I'm a big fan of Cloud Code. If you want to see more Cloud Code videos, let me know in the comments below. I had a lot of fun. I like learning. I like teaching back to you.

**12:36** · So, hopefully you learned something new today. If you did, give me a thumbs up, subscribe to the channel, and as always, happy coding.