---
title: "Claude and Obsidian Full AI Operating System"
type: tutorial
category: architecture
tags:
  - tutorial
  - architecture
  - claude-code
  - obsidian
  - memory
created: 2026-05-01
source: https://www.youtube.com/watch?v=eIXheJcxDIg
---
![](https://www.youtube.com/watch?v=eIXheJcxDIg)

## Transcript

### Building a Local AI Operating System

**0:01** · In this video, I'm going to show you how to wire Claude Code directly into Obsidian to build an AI operating system that literally runs my business and keeps me on track. I'll explain both platforms for those of you coming in fresh, and I'll also explain why I don't use either in isolation. Then, I'll show you how to set it up from scratch. I'll show you the architecture, I'll show you what my current iteration looks like and how I use it day-to-day. Let's get it.

**0:19** · So, for my AI friends that are already using Claude Code, you've most likely heard people talking about Obsidian and vice versa. If you're already an Obsidian expert, you've most likely heard people talking about Claude Code.

**0:28** · This video is for both of you because these two platforms are absolutely best friends. And here's why. If you're coming from the AI side, you already know that Claude Code is awesome. You can build things, you can write code, automate stuff, just an incredible tool.

### Why Claude Code Needs Obsidian (The Amnesia Problem)

**0:41** · Except the biggest downside with Claude Code is every time you use it, everything's gone. Everything you talked about, every decision, your clients, your projects, all that stuff, gone.

**0:49** · You're re-explaining yourself every single time. And a lot of folks open Claude Code inside individual project folders, right? Which is fantastic, but it's very much like having one specific employee for one specific task and no way for all of those different employees to meet in the middle and talk to each other. That's specifically what I'm using Obsidian for. I've got one large, like umbrella folder that I'm treating almost like the whole organization, right?

**1:11** · Everything is broken down into their own separate departments, um and it doesn't matter what agent I'm talking to, whether it's Claude, Gemini, or Codex, it doesn't matter what project or task or anything like that, we've always got full context, always full memory, always up-to-date, always fully aware.

**1:25** · That's what Obsidian gives you. It's a home base, right? All your agents, all the time, knowing exactly what's going on as a whole. Otherwise, Claude Code is brilliant, but it's an amnesiac. So, if you're coming in from the Obsidian side, you kind of already know what you're sitting on. It's a fantastic app with all the plugins and markdown files and local storage and all that stuff.

### The Problem with Traditional Productivity Apps

**1:41** · Except, be honest, like every productivity app, you tend to spend more time scrolling around, customizing than it actually saves you, right? Like, so for example, I'm looking for something, I'm scrolling through all these different sub-folders, I'm trying to find something. Where was that note about whatever? You know, you're updating wikis, you're doing all that stuff just to make sure that this works as advertised, and that is a massive time sink. Instead of navigating and fighting with this stuff, what if you could just talk to it? It handles all the filing, the routing, organization, all of it. That's what Claude Code gives you in Obsidian.

**2:12** · It like gives your vault a little librarian that can go and like sort things out, pull up different documents on request. It makes the experience seamless. Hopefully, you guys can see where I'm going with this. So, let's set this up and we can get into the nuts and bolts of it. So, step one would be download Obsidian. If you go to obsidian.md, you'll be met with this.

### Obsidian Vault Setup for AI Agents

**2:29** · Defaults to Windows, but if you click this guy here, you can find it for Windows, Mac, Linux, whatever you need, okay? And then you're going to be met with the, once you install it, that is, you're going to be met with this page right here. They'll be empty on the left. We need to start a new vault, okay? So, we're going to create a new vault. I recommend keeping this somewhere easy. Like, I just put this in the documents in my Windows environment, and tada. Okay, so we're going to find somewhere that's easy to find or just like kind of out of the way that you won't accidentally delete or anything wild like that. So, I'm just going to go yeet, and let's find where we're going to put it. Click folder.

**3:00** · Create. All right, so this is our brand new Obsidian vault. Hey-yo. We will be looking at the same thing. None of these plugins come preloaded or anything. This is essentially just like the empty folder. But we're going to go over to the settings, go to community plugins, and then go turn on. Tada. And we are going to browse.

### Best Obsidian Plugins for Claude Code Integration

**3:19** · The very first thing we're going to download is the terminal plugin.

**3:25** · Click install and enable.

**3:29** · Good to go. Then we're going to get Templater, which is right here, and enable that one. It's going to give us this. Then I want you to go over to the core plugins here, and we're going to find web browser, and just turn that on. Web viewer, boop, right there. So, for your web viewer settings, you get to choose your search engine. DuckDuckGo is what they use by default, and I find that's fine. Uh you can go to Brave, Bing, Google, or something different.

**3:52** · Open external links, allow, yeah, okay, cool. Um this is honestly all you really need to get started because this will allow you to pull in Claude Code or some other AI agent and you have it interact with this vault, okay? So, I'm going to go over here and just show you appearance as well if you want to change the themes. The one I'm using is called PLN. Uh I like the rainbow sidebar cuz I'm vain like that. So, we're just going to install and and use. Tada.

**4:16** · There you go. Realized I didn't cover this, you do need to install Claude Code on your computer, so just search up Claude Code, and then go to the the first result, the one with Anthropic, and then check out documentation.

### Installing Claude Code & Anthropic Setup

**4:27** · Um so, find the one that's appropriate for your platform. If you're on Mac, it'll be this one, Windows PowerShell, command, whatever. And then go down and click the quick start guide that'll walk you through the exact steps needed to log in to your Anthropic accounts and get this going, okay? Okay, so I'm going to move the terminal down to the bottom so I know where it is exactly. Open this up. Make sure to click integrated like so.

### Initializing Your AI Assistant Inside Obsidian

**4:50** · And here we are.

**4:52** · So, I'm going to start by going with Claude, and this will start Claude Code.

**4:57** · Easy as that, okay? So, you see how we're like almost almost there. So, very first thing we're going to do is I'm going to go slash init, and all this does is, if, I don't know if you guys can read this, initialize a new claude.md file with code base documentation. This is where Claude writes down its memories and what not.

**5:15** · Do that, it is digging in. So, now what we're doing here is Claude is just getting acquainted with what's going on in this vault here. I've got the terminal window here as well. Okay, so you're just going to go through and just allow it permissions to make edits inside the main folder. Um it's just getting acquainted like we were saying here, okay? All right, we are getting there.

**5:32** · Do you want to create a claude.md file?

**5:35** · Heck yes, I do. Great. So, now you can see this has been added to the graph.

**5:39** · We've got Claude at the root, and we're ready to get rolling. Something else I want to address, the terminal plugin sometimes has some trouble \[laughter\] out of the box. Like, it doesn't get sized properly. There are two issues that I've run into where that happens.

### Fixing Obsidian Terminal Resizing Errors

**5:53** · It's either the error 9009 where the plugin resizer doesn't really work properly, or it renders incorrectly with the wrong sizes. I've got the prompt in order to fix both of those situations that I'll leave down below. I'm actually just going to run that in my other vault right here just to make sure that it is, you know, looks nice cuz you can see this is all garbled, which means we ran into that issue, which is why we have this here, and it's going to work just fine. Okay, awesome. Says both fixes are done.

**6:20** · Here's the summary. Fix this, fix that.

**6:22** · Next step, restart Obsidian for the data.json to take effect. Fantastic.

**6:28** · So, we've made all of our basic changes, right? You can see that now we have the option to check out the web browser, search whatever you want. You can even like run design apps from the top. This is like an advantage of \[clears throat\] of doing things like this. You've got your UI down up here and your back end right here. But like, this is this is all fine, but if we're looking at it, it's it's still pretty empty. Like, what do we do from here? So, this is kind of the exciting part. You can literally just sit and type to this AI agent and explain the folder structure that you want it to have. You can talk to it about its manners, tell it how you want to behave, and all that stuff, and it'll actually just set it up for you.

### Structuring Folders for AI Memory & Context

**6:59** · You can import existing folders, you can open Obsidian in your existing project folder. However it works for you, however you want this to be organized, I guess, that's the beauty of it. Tell Claude exactly what you want to have happen, and it'll just go forth and do that. This here is the brain. This is what tells your AI agent what's going on, tells it its rules, all that sort of stuff. It's what your agent will actually look at first just to get a lay of the land, okay? So, you can tell Claude whatever it is that you want it to do, how to behave. Like, I call it, you know, giving the AI manners, and it'll update this claude.md file, right?

**7:33** · As you can see, it says you've got these plugins to work with, the vault structure is like this. Working in this vault, everything is in markdown files, you got wiki links, and it knows exactly what to do, okay? So, I'm going to go over to my other already established vault here, and I'll give you an idea as to the structure that like works for me, okay? So, the one thing I really wanted to make sure was that my ideas were just my ideas. I never wanted to be looking through my journal, and it was a summary of what I said, like the AI was just paraphrasing for me or like helping me out. I wanted to make sure that my voice was preserved at all costs.

### My Vault Architecture: Human vs. Machine Brain

**8:01** · So, I've broken this down into like left and right hemisphere of this like AI second brain. This side is just my voice, things I have explicitly said, tasks that I'm doing, and like AI can read that, but it can't write to it unless I give it specific instructions, okay? The other side is the machine side, and like that's everything else. That has all of my AI content. So, any research it does, any sort of skills, SOPs, code, that kind of thing, that all lives in the other folder. This is also where I put my templates and SOPs um for the AI agents to read later.

**8:34** · So, that was the main idea behind how I organize my folders, right? Just making sure there was a clear distinction between human and AI content. Everything else just kind of fell into place from there, right? So, the human side is my relationships, my daily notes, my projects, you know, things like that.

**8:49** · The machine side is all the SOPs, templates, scripts, research results, and different things that the AI actually comes up with and helps me out with. Um that includes workflows and just different automated tasks. I put that in here, too. And it's working out really well for me. So, let me show you how they work together. Uh I'm just going to go with It's going to be slash new. And this is just like new idea. So, I can I can type whatever I want. I can even like rapid-fire and really try and break this thing and give it like six different things to deal with.

### Live Demo: Automated Task Routing & Data Logging

**9:12** · It'll route that to the appropriate file or folder or project or whatever, and I don't have to go through and mess around with opening these different sub-folders and all that other action like that, okay? So, I'm just going to type something in, and it'll know exactly what to do. Okay, so for example, I gave it a couple different things. I said, "Send a message to this person waiting for her to schedule a meeting, had four cups of coffee, ate a pork chop in a burger bun, 30 minutes on the exercise bike, I'm filming the Obsidian Claude Code video right now at this time, and I want to look into optimizing the cold email campaign." It'll know exactly what all that means, right?

**9:42** · It's looking through the people in the folder, looking through the daily notes, it's looking through my projects, looking through my content calendar, all that stuff, and it's automatically routing, and I don't have to do anything. I can just leave now, right? Which is the biggest single unlock for people already in the Obsidian vault. This is what you've been waiting for. This is why people in the Obsidian communities are talking a lot about Claude code is because it solves the biggest pain point that you folks had. Okay, so check out the results here. Done. Movement. 30 minutes bike logged.

**10:10** · My food has been logged, hydration logged, confirmed the update to that person, confirmed the update to my content calendar, and created a task regarding the templatization of my cold email pipeline. Everything done. It keeps going though. So, you might be wondering how I got here and literally it just came from talking to Claude code. I worked backwards from my ideal outcome and just told it what I wanted to have happen. When I type this, I want you to organize it for me, right? So, another thing that was really important to me was how I start my day.

### Using Claude Code to Generate Daily Prep Lists

**10:40** · I was really big on lists, like coming from restaurant world and, you know, being organized in logistics and uh residential commercial moving, that kind of thing. Uh organization is huge, but most of my mornings would be like I'd go work out and then come back and spend 30 minutes writing down like a prep list for the day or like things that I'm supposed to do. So, I wanted AI to do that for me, right? And it's really beneficial having it do so in this Obsidian environment where it's got access to everything that I'm doing and my daily notes and all sorts of stuff like that. So, I did the same thing with starting my day.

**11:11** · I go {slash} today and it'll go and run this workflow that brings in my email, my calendar, run through my daily notes, my project, like the whole vault, everything like that, and then it'll assess and output my tasks for the day, what I should start with, where I'm maybe slipping or if there's something that I said I was going to do and haven't, that's been on the docket for a couple days, it'll give me trash and be like, "You need to do this first." kind of thing. Just keeping me completely on track and honest with it. Okay, so check this out. This is my actual notes and plan for the day.

**11:38** · I can open this up in the the daily notes where it's nicely formatted and I can like, you know, cross things off, but essentially it's like, "Check it out. No major meetings to check out. Here's some emails that might need your attention.

**11:48** · Um frogs to eat. Things that need my attention first in the day are these things, right?" And it's not just the productivity or like note-taking side of things. You can actually go and build tools in this platform as well. This is why I like this so much is because every I don't ever have to leave this window.

### Building Coding Workflows & Apps Inside Obsidian

**12:03** · Whether I'm building a tool, whether I'm running, you know, different email campaigns, answering stuff, building out like web apps with Stitch, that's why I brought this up was just to show you how everything is in one window. I can do whatever I want. For example, just the other day I built out a cold email pipeline for someone, that's what I was kind of talking about before, where it goes and it scrapes 7,000 leads a week, goes and validates those with True List straight from our scrape, and then generates different campaigns, 24 in fact, and runs those campaigns from Instantly. We also use Reply Rate as a success metric and it improves copy as time goes on. I did that all from here.

### Automated Cold Email Pipeline Build

**12:34** · Like this is a fully functioning dev tool. Claude code kicks ass. It's not like it's watered down because it doesn't look the same as uh what you're used to. There's also the VS Code editor plugin, right? Where you can go and read or edit code right here. It works gangbusters anyway. But the nice thing is that anything you do, you can turn into templates or workflows. So, that anything I do repeatedly, I can just go and give it that command and my Claude code instance will know exactly what to do without this massive prompt. Just for yet another example, something I do a lot of is I'll look through YouTube comments for video ideas.

**13:02** · So, instead of going through and looking at comments manually to find patterns or having Claude code watch my YouTube channel and uh do that with a prompt every single time, I just go {slash} comments and it'll read my comments and what you guys are talking about and I can get ideas for the next video. Anyway, the TLDR of it is these two programs complement each other perfectly because they fill the gaps the others leave. The other beautiful part of this is that this is all local. Let's say I run out of Claude rate limits, I don't have to wait. I can use the exact same architecture with a different agent. Or like let's say Anthropic goes belly up.

### Why Local AI Architecture is Future-Proof

**13:32** · Or for some reason I don't have that access anymore.

**13:36** · I'm just using the terminal. So, as long as there are AI agents, I can use this exact architecture moving forward. So, anyway, that's the big deal. That's why if you're in the Claude code community, you're hearing about Obsidian. That's why if you're in the Obsidian community, you're hearing about Claude code because these things are perfect for each other.

**13:50** · So, I really want you guys to keep me posted and let me know how you guys are using these together. Talk to me about how you're organizing stuff. That's really cool. But if you want this exact workflow that I've uh just laid out right here, you can go to my school community in tools and agents and you can download it for yourself. It comes with install, so you just honestly double click or run a script and everything loads for you just like that.

**14:09** · It'll ask for an interview, so you can tell it the uh way you want it to behave in different manners and stuff. And you also with that get all of these different workflows that I was talking about. It It comes with it. We're updating this all the time so that it's current with what I'm actually using.

**14:22** · It's not just that, you get all the other AI tools that I'm building out for myself and others. And you get access to a growing network of almost 700 other members that are in here doing the exact same thing. It's a fantastic place to be. Links to that will be in the description. Thanks for hanging out.

**14:34** · Subscribe for more and I'll catch you in the next one.