---
title: "Obsidian and Gemini CLI One AI Brain That Works With Everything"
type: tutorial
category: architecture
tags:
  - tutorial
  - architecture
  - obsidian
  - gemini-cli
  - second-brain
created: 2026-05-01
source: https://www.youtube.com/watch?v=eXmedaRNGc8
---
![](https://www.youtube.com/watch?v=eXmedaRNGc8)

📚 Skool Community: https://www.skool.com/easymachineai  
🤖 Let's Work Together: https://easymachineai.com/contact  
eric@easymachineai.com  
  
In this video, I walk you through how to build a permanent, local AI Second Brain using Obsidian and the Gemini CLI. By creating a "Single Source of Truth" in plain-text Markdown, you give all your AI agents (Claude Code, Antigravity, Gemini) perfect, cross-platform memory. I cover the 2-Vault "Church and State" architecture, the Windows Symlink hack to sync your agent skills, and how to use a custom Python script to instantly convert your entire ChatGPT history into a fully searchable local memory bank.  
  
Timestamps:  
\[00:00\] How to Build an AI Second Brain in Obsidian  
\[00:31\] Obsidian vs Notion: The Best Note-Taking App for AI  
\[01:24\] Why Your AI Agents Need Long-Term Memory  
\[03:16\] Obsidian Setup Tutorial: Step-by-Step for Beginners  
\[03:47\] Top Obsidian Community Plugins for AI Workflows  
\[04:48\] Using Gemini CLI to Auto-Generate Obsidian Folders  
\[06:16\] AI-Generated Daily Notes Templates in Obsidian  
\[07:21\] Context Logging: Giving AI Perfect Memory  
\[08:02\] Syncing AI Workflows & Skills with Symbolic Links  
\[09:34\] How to Import ChatGPT History to Obsidian (Python Script)  
\[11:30\] Why Local AI Memory is the Future  
  
🛠️ Tools & Tech Stack Used  
Obsidian (Markdown Second Brain)  
Gemini CLI  
Python  
Antigravity / Claude Code  
  
\================================  
Why watch? I'm Eric — I run Easy Machine AI and built my AI automation business to consistent five figures monthly by learning to build my own tools instead of renting broken ones. This channel is about real workflows, live builds, and skipping the stuff that doesn't matter so you can ship faster.

## Transcript

### How to Build an AI Second Brain in Obsidian

**0:00** · In this video, I'm setting up Obsidian as my single source of truth for my whole life. I'm going to use it as an AI second brain. I'm also using it as a memory layer for my AI agents and workflows moving forward. We're going to talk about why you need AI memory, why Obsidian is the best option, and I'm going to show you how to set it up with Gemini, so you don't have to build it all yourself. Let's get it. First of all, I'm going to do this entirely live.

**0:19** · I've only gone as far as to install Obsidian. You and I were going to be able to walk through this at the same time together. I guess I'll start off with what is Obsidian and why is it the best option? Obsidian is essentially a note-taking app, but it's got a couple advantages to things like notion or Evernote or whatever. Firstly, the data is yours. It's all local files, so you don't have to get locked behind subscriptions or calling out to the cloud for the information that you want to get access to. Secondly, they're all plain text markdown files, which is fantastic if you're working with AI.

### Obsidian vs Notion: The Best Note-Taking App for AI

**0:49** · All the skills and plugins that you hear about with cloud code and anti-gravity, those are all markdown files. So, this natively speaks the same language as your LLMs. So, it makes a lot of sense to have your notes and things be in that format. The other thing that I think is really cool and unique to Obsidian is the graph. You can visualize relationships between different notes that you take or make connections that AI can see later. So, you're not pulling from a mass of text to get one little bit of information.

**1:17** · It can find related notes and connect the dots for you natively in the platform, which is awesome. Just for some housekeeping, you might be asking, why do we need to go through any of this in the first place?

### Why Your AI Agents Need Long-Term Memory

**1:28** · Which is a really good question, and it's probably because you're used to the consumer like front-facing models for these LLMs. Take chat GPT for example.

**1:36** · When you talk to chat GPT, it takes insights from each of these conversations to put it into a context file, like a user profile that it can pull from and know a little bit about you. That doesn't happen out of the box.

**1:48** · AI and these agents only have session memory. So anytime you use cloud code or anti-gravity or any of these coding agents, it's like starting fresh. So we don't want that. And we also don't want it to get your entire life story when you have one question about what you did last week or something like that. We want to make sure AI has that user profile so it has access to that context and gives you proper answers for your circumstance. We want to also make sure it has the tools to pinpoint just what it needs. There are a lot of ways to do that and I've experimented with many of them. Most recently and I guess most notably is my notion database. Before I was an AI guy, I was a notion guy.

**2:21** · So I hooked my AI with my notion database and it was really handy having access to a lot of that different context. But as the AI capabilities that I was integrating grew, so did the trouble I had with Notion. Because I've been using Yosian for such a long time, it was difficult for AI to pinpoint just what it needed like I was saying.

**2:40** · And also with the notion MCP sometimes we get some wires crossed where I would search for a log or something and it wasn't limited to the database that I was or sorry the workspace that I was looking at. It would find something somewhere else across my entire notion account. So things were getting wires were getting honestly notion wasn't a bad answer. It did the job pretty well. It's just that moving forward I see Obsidian as a stronger choice for a couple reasons. It makes more sense to have control over my files locally.

**3:08** · Makes more sense to keep them in markdown. and it makes more sense not to have to call an MCP in order to actually access my own data.

### Obsidian Setup Tutorial: Step-by-Step for Beginners

**3:16** · Oh, we're going to Obsidian. So, we're going to go to obsidian.md and download for Windows or whatever platform, right?

**3:22** · You can get it for Linux and Apple and all that stuff. All right, so you've downloaded and installed Obsidian. We are both looking at the exact same screen. Like I said, we're doing this together. I haven't set this up for myself yet. So, we're going to go over to create and we're going to name this sucker whatever it is you want to call it. I'm going to call it EMAI. Location, we're going to move. I'm going to go to documents and sounds good for me right there. And we're going to go create.

**3:46** · Sweet. So, here we are in our very first vault. So, there's a couple settings we're going to want to change. Making sure that we can download certain plugins to make this work. Community plugins. Turn on community plugins.

### Top Obsidian Community Plugins for AI Workflows

**3:56** · Then, we're going to go browse and get the stuff we need. First things first, we need the terminal, which is pivotally important. This is what allows us to access Cloud Code, Google CLI, that kind of thing. Oop, says failed to install.

**4:07** · Why? There we go. Okay, enabled. Anyway, this gives us direct terminal access to cloud code, Gemini CLI, codec, that kind of thing. The next one is go calendar.

**4:18** · So, we can actually see the dates, make changes, and do all that. We can also add templator, which is what helps you create automations for all this stuff.

**4:29** · So, that's perfect. I'm going to go over here to appearance as well. Oops, that's back in settings. Pardon me. Appearance.

**4:35** · And I like Dracula. It's just my style.

**4:39** · You can go through and find one that works for you, but this is uh this is good for me. Great. So, now we are here.

**4:45** · We're going to open the terminal right here. And make sure we put it into integrated mode. And it'll just be on the bottom half of your Obsidian dashboard like this. And we can use anything, but I'm going to go with Gemini here for today. There we go.

### Using Gemini CLI to Auto-Generate Obsidian Folders

**5:05** · So, I don't know if you can see it. It's actually running parallel with my terminal here, which is kind of cool, but it's nice that you can do it directly in Obsidian. I'm going to open this up a little bit bigger. Great. So, we're going to say yes, we trust the folders here. I'm going to go enter.

**5:19** · Gemini CLI is applying the trust changes just like it would in other terminals.

**5:23** · It doesn't really matter which platform you use, whether it's Cloud Code or Codeex or Gemini or whatever. The idea here is we just want to use AI to help us build the folder structure. So, you can prompt it however you'd like. I am going to make sure that I'm separating church and state essentially. I want my own ideas in their own folder. Um, there was a guy on the Greg Eisenberg podcast that talked about this and it just made a lot of sense to me. So, I'm making sure that the second brain is its own thing and I don't have AI polluting anything. And then I'm also making sure that I've got a completely AI folder for my agent skills, my workflows, all my templates and that kind of thing.

**5:53** · So, I'm going to make sure that those are separate but also easily accessible and organized. I just talked about what I needed. So, we're just going to allow Gemini access to this folder for our purposes. Right here, it is currently generating everything we need. Machine is agents, other skills, research results, SOPs, workflows. Perfect. This is my second brain. Journal, logs, project, user context, voice notes.

**6:15** · Fantastic. So, do we have daily notes and stuff? No, we don't. Right. So, I'm going to see if it can create a template for our notes. Just uh just going to see. Like I said, we're finding out together. template for my daily notes.

### AI-Generated Daily Notes Templates in Obsidian

**6:28** · Please allow for this section. Okay, cool. So, it's generated a daily notes template. I can always mess with this later. But now, when I say create daily note, it's going to go to this template inbox. We can keep going with this, too.

**6:42** · But you see how easy this is to just tell Gemini to make the thing and you don't have to go in and do it. It's amazing. Okay, so go into settings, go to core plugins. No, that's not it. Go to daily notes and we can change the format. This is working out fine by me.

**6:56** · Um, and then when we go new file location, we'll go human human daily notes and the template file location is daily template like that. That is saved.

**7:08** · So now when I move forward with my second brain, I can go and just add the notes like this. It's perfect. So this is stuff you can fiddle with on your own time. I just wanted to show you the Gemini makes this really easy to just punch in what you're thinking and it makes it happen in reality. So the next thing that's really important is we're going to make sure we initialize this entire project just like you would with any other AI workflow. Making sure that context is logged. Anything that the AI touches, it's going to write down in the claude or Gemini.m MD just as a log and memory of what it is that we're actually doing here. So let's go slashinit to initialize this folder.

### Context Logging: Giving AI Perfect Memory

**7:40** · There's your gemini.md right there.

**7:44** · Anything that happens is going to be written to this file. Restart so these changes take effect.

**7:50** · And I think we're good. Okay. See, so now it's got all of the context of what we just did and the folder structure so that I can come back later, AI will read this Gemini.md file and know what's going on. All right, this is moving along really well. But the next step is to actually give it the information that it needs to run properly. I want to set it up so that no matter where I am, what AI agent I'm using, we pull from the same skills file and they can use them the same way. As it stands, anytime I found a skills file or a workflow that I wanted to use, I've brought it in through anti-gravity. So, at the moment, they're all sitting in a hidden folder on my C drive.

### Syncing AI Workflows & Skills with Symbolic Links

**8:20** · So, what I need to do is to bring this all into this Obsidian vault so that any agent can actually pull from these and use them in the same way. The issue with this though is that the AI is still going to look in that hidden folder for the skills. So, I need a way to tell it that they're now over here. And for that, we're going to create a symbolic link. I've typed out this prompt in advance, but I'm just going to paste it here in the terminal so that I can actually run this task.

**8:42** · So, I'll give you something that you can use for yourself in the description, but for now, we'll just get this going so that this can connect to all of my skills files right now. Essentially, how this is going is I want to move my anti-gravity workflows into my Obsidian vault and set up a symbolic link. First, move all the files into the Obsidian vault. Second, delete the old now empty folder. Third, create a symbolic link between the two items. Make sure to use absolute paths. That's what it's doing.

**9:07** · I'm going to allow for this session.

**9:08** · Oops, I got to click into the thing.

**9:10** · allow for the session.

**9:15** · I have successfully moved your anti-gravity workflows into workflows.

**9:19** · I've got all of my skills right here.

**9:22** · Ready to go. So now I'm going to tell it to update Gemini context or let's just go gemini.md so it doesn't get confused.

**9:30** · It's going to update with what we did.

**9:32** · Excellent. Love it. It's all done. So this is moving on the AI side of things.

### How to Import ChatGPT History to Obsidian (Python Script)

**9:35** · Now for the human side of things, you got to bring in some context. I've already exported my chat GBT conversation history. I've got it in a big old folder in my downloads. So, we need to get that into the user context, but we don't want to just like copy paste that giant wall of text. What I'm going to do is I'm going to copy conversations.json as path. I'm going to copy where it goes and just give that to AI to generate a prompt to do the following. I want to break these down into individual markdown files, memory files from Obsidian that AI can read. I also want to make sure we're picking out keywords that are related.

**10:06** · So, if it's anti-gravity, it's going to go into the memory brackets. If it's video editing, it's going to go into those memory brackets and so forth. The other thing is I want to make sure that we're not doing it in Gemini. That AI isn't the one reading all of these files off the bat. We can generate a Python script to run this straight away. The the reason being is that the context here is huge.

**10:26** · So, we're going to run into rate limit issues if we run this directly into the AI. After this is all sorted out, then we can have AI maybe some check some stuff out, make sure that it's working properly. but we're going to run a Python script instead. So, I've already written out a a prompt that would do just that. We can paste this into the Gemini CLI right here, just like this.

**10:44** · And it's going to run. So, essentially, I have an export file. I need a Python script to parse into Obsidian Markdown files at the user context path right here. For every conversation, create a separate markdown file containing the back and forth dialogue. Add a front matter with the title, the date, and the history. before writing that text to the file, it scans for the following keywords. Um, different things that we we need, right? Okay. So, it's created the script. I'm going to see if it can run it from here. I might have to give it access to that or we can run it in that directory. But let's say you run it.

**11:15** · Easy as that. Then all of a sudden, we've got 340 memories in the user context. Okay. So, I have successfully processed 324 markdown files from my chat GBT export. Pardon me. So, now it's got all of my memory from chatgbt. I'm going to do the same with Gemini, with Claude, with uh my other platforms that I use. I'm excited. This is the bones of it. I'm going to keep adding templates and, you know, skills and just build this out a lot more, make it more awesome.

### Why Local AI Memory is the Future

**11:39** · But the beauty of this is I can take this now as one chunk and no matter what happens with AI or the different platforms, I can take this and apply it and it'll work exactly the same across the board. Whether it's OpenAI or Anthropic or Gemini or somebody new, this is all here and it's got full context, full ideas as to how my skills have worked and it's all local. It's not hidden behind a subscription or, you know, I might run out of storage or anything like that. This is the whole system.

**12:03** · So, subscribe if you want to see how this gets built out into my personal assistant and how it's used to run my business dayto-day. and hit the link in the description to get some templates and downloads for free for