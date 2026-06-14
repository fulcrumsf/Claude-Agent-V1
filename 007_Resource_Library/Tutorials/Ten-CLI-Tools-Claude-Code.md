---
title: "Ten CLI Tools Claude Code"
type: tutorial
category: ai-agents
tags:
  - claude-code
  - cli-tools
  - ai-agents
created: 2026-05-08
source: local
---

![](https://www.youtube.com/watch?v=3NzCBIcIqD0)

10 CLI Tools I’m Using with Claude Code (LazyGit, Glow, Zoxide, Btop, eza + More)  
  
Blog Post guide with Links:  
https://blog.starmorph.com/blog/10-cli-tools-for-ai-coding#1-lazygit  
  
Browse Starmorph Config files library https://starmorph.com/config  
  
Overview  
The video covers 10 command-line tools ive been using alongside Claude Code while spending more time in the terminal. It demonstrates LazyGit for monitoring repo status and reviewing changes Claude makes, Glow as a CLI markdown reader (with NeoVim mentioned for deeper navigation and editing), and LLM Fit for estimating which local AI models can run on the current hardware. It also shows the Models CLI for comparing model providers, pricing, context, agent changelogs, and benchmark results. Additional tools include Taproom for browsing Homebrew casks and installed packages, Ranger as a terminal file explorer for remote/Linux workflows, Zoxide for smarter fuzzy directory jumping instead of manual cd paths, Btop (and MacTop on macOS) for viewing system resources and processes, Shah for rendering images directly in the terminal, CSV Lens for viewing CSVs in a TUI, and eza as an enhanced ls alternative with icons and grid/grouping options. The creator closes by inviting comments for deeper future videos on individual tools.  
  
  
Chapters  
00:00 Intro: 10 CLI Tools I Use with Claude Code  
00:13 LazyGit: Track Repo Changes as Claude Edits  
01:06 Glow + Neovim: Read & Navigate Markdown in Terminal  
02:21 LLM Fit: What Models Can Run on Your Hardware?  
03:11 Models CLI: Providers, Pricing, Benchmarks & Agent Changelogs  
04:16 Taproom: Browse Homebrew Casks & Formulae  
05:04 Ranger: Terminal File Manager for Remote/Linux Work  
05:25 Zoxide: Smarter \`cd\` with Fuzzy Jumping  
06:11 Btop & MacTop: Monitor System Resources and Processes  
07:24 Terminal Viewers: Render Images (shaa) + Inspect CSVs (csvlens)  
08:18 eza: A Better \`ls\` for Busy Terminal Workflows  
09:23 Wrap-Up: More Tool Deep Dives + Viewer Requests  
  
Links to packages mentioned  
\- \[LazyGit\](#1-lazygit) https://github.com/jesseduffield/lazygit  
\- \[Glow\](#2-glow) https://github.com/charmbracelet/glow  
\- \[LLM Fit\](#3-llm-fit) https://github.com/AlexsJones/llmfit  
\- \[Models CLI\](#4-models-cli) models https://github.com/arimxyer/models  
\- \[Taproom\](#5-taproom) https://github.com/hzqtc/taproom  
\- \[Ranger\](#6-ranger) https://github.com/ranger/ranger  
\- \[Zoxide\](#7-zoxide) https://github.com/ajeetdsouza/zoxide  
\- \[Btop\](#8-btop) https://github.com/aristocratos/btop  
\- \[Chafa\](#9-chafa) https://github.com/hpjansson/chafa  
\- \[CSV Lens\](#10-csv-lens) https://github.com/YS-L/csvlens  
\- \[Bonus: eza\](#bonus-eza) https://github.com/eza-community/eza  
  
📡 Starmorph AI: https://Starmorph.com  
🐦 Follow us on Twitter: https://twitter.com/StarmorphAI

## Transcript

### Intro: 10 CLI Tools I Use with Claude Code

**0:01** · Hey everyone.

**0:01** · Thank you for watching Star morph.

**0:02** · In this video, I want go over 10 CLI tools that I've been using recently alongside Claude Code as I've been spending more time in the terminal.

**0:10** · So let's go ahead and jump in.

### LazyGit: Track Repo Changes as Claude Edits

**0:13** · So the first tool that I want to show you is called Lazygit, and what this CLI allows us to do is monitor the current git repo that we're in, which is really nice when you have Claude code running because as Claude is making changes to your code base, you can see them pop up here.

**0:30** · So it's a little overwhelming at first this ui, but we have these hot keys here to go to these four or five different views.

**0:39** · So I can look at the overall status of Lazy Git.

**0:43** · This is my favorite view, the files view, where you can see here that I have one file that's been changed So Claude just made this change.

**0:50** · And then I can go in here and get a quick view on what Claude changed.

**0:54** · You can also manage your branches and look at commit history.

**0:58** · And what you have stashed.

**1:00** · So this is a nice little tool to monitor, get progress as you work with Claude Code.

### Glow + Neovim: Read & Navigate Markdown in Terminal

**1:06** · The next tool I wanna mention is called Glow.

**1:09** · And what Glow is it's a markdown reader in the CLI.

**1:12** · So as you know, Claude works with a lot of markdown files and sometimes you want to be able to read them on the command line.

**1:19** · So if you type glow, and then I choose one of these markdown files, it will print this out to the command line.

**1:28** · To the terminal, and it also adds some formatting that doing something like CAT might not have.

**1:33** · So this is a way to quickly read some markdown documents.

**1:36** · If I want to do a little more in depth view, then I'll probably use Nvim, Neovim, and then I can have hotkey for things such as jumping to each header, which is pretty nice, or going to the top of the page or the bottom of the page.

**1:57** · So this gives you a little bit more control on reading and editing markdown documents, but it also can take you know, more time to ramp up on the Vim hotkeys and everything there.

**2:09** · So Glow is great just as a simple tool for reading markdown exports that come from Claude or reading Claude md files and things like that.

### LLM Fit: What Models Can Run on Your Hardware?

**2:21** · The next tool that I wanna show you is called LLMFit.

**2:25** · I just discovered this recently and it's kind of cool.

**2:29** · What LLMFit does is it prints this table out and it shows you what hardware you're currently running on and what models you could locally run on your computer.

**2:38** · And it ranks them on different things like this score that they make how much memory of your machine it's gonna use, how many parameters the model is, and then you can also click into a model and look at more details of this model.

**2:53** · One thing I've noticed about this is I do think that it's not going on my full system memory, but just what I have available, I need to confirm that.

**3:02** · But it looks like it's only calculating this based on what I currently have available.

**3:06** · So I should probably close everything and then look at this again, but pretty cool interface here.

### Models CLI: Providers, Pricing, Benchmarks & Agent Changelogs

**3:11** · Similar to that, I found another CLI tool called models.

**3:17** · And this prints out another table.

**3:18** · But this one has a list of a bunch of different AI model providers, and you can take a look at what models they have available, and then a pricing chart of how much they're charging for tokens, how much context you have, and some other model details here.

**3:36** · A-P-I-U-R-L.

**3:38** · So this is a quick way to look at.

**3:41** · Different model data.

**3:42** · I actually didn't know this, but it looks like they have a tab for agents as well.

**3:48** · Okay, so they also have another tab for agents.

**3:51** · Where it looks like they have change logs for different agents to see what's changing.

**3:59** · And then we also have a table here of different benchmarks and how models did on these benchmarks.

**4:09** · So pretty cool CLI to get a quick view in the terminal of different model details.

### Taproom: Browse Homebrew Casks & Formulae

**4:16** · The next tool that I wanna show you is called Taproom.

**4:18** · And what Taproom does is if you're familiar with Home Brew, the package manager for Mac, then taproom shows you all of the brew packages or flasks and formula that you have installed on your machine.

**4:35** · So actually you can not only view the ones on your machine, but right here we're just viewing the.

**4:41** · Casks that exist.

**4:43** · And if I click I, then it will take me to the ones that I have installed.

**4:46** · And this is a really nice way to just, sometimes you forget what packages you install.

**4:52** · So this is a nice way to, see what you have on your machine and find new things that you might want to install as well.

**4:58** · And get a reminder of, what packages are here.

**5:01** · So I've been enjoying using this.

### Ranger: Terminal File Manager for Remote/Linux Work

**5:04** · And then the next CLI tool I wanna show you is called Ranger.

**5:08** · Ranger is a file browser explorer in CLI and if you're working on a Linux machine or something like that and you don't have finder or you don't have a UI for browsing files, this can be really helpful to get around on the machine, The next tool that I wanna show you is called Z oxide.

### Zoxide: Smarter \`cd\` with Fuzzy Jumping

**5:27** · So instead of doing CD and then writing out the full path, Z oxide has a smart history that accumulates more knowledge of how you use CD into directories.

**5:38** · And then you can do like a fuzzy search on it.

**5:41** · So for example, if I go to my home directory and then I type Z muse.

**5:46** · It's gonna know that I often go to the Pixel News GitHub repo, and it's gonna take me right there.

**5:52** · Even though I was on my home directory, it knew that I wanted to go to this full path.

**5:57** · So that's just really convenient and nice.

**5:59** · I use that all the time, like plenty of times a day because it's just easier than CD and writing out the whole path, it actually saves like a lot of time just adding up over time.

### Btop & MacTop: Monitor System Resources and Processes

**6:11** · The next CLI tool I wanna show you, this is another one that if you're running cloud code in something like a Linux vm you might want to view the system processes and just get an overall view on what's happening on that machine.

**6:22** · So for this we can use Btop and Btop makes this really nice view.

**6:27** · I like to keep this up when I'm SS Hing into Linux to just see what's going on in the system.

**6:33** · You get an overview of what's happening with the memory different system processes that are running, and then your CPUs, and you can configure this as well.

**6:43** · So if I go in here.

**6:45** · I take out net, it's gonna remove this bandwidth chart on the bottom left and you can customize what you want your view to look like in B top.

**6:53** · So this is a great way to just get an overall macro view and kind of analytics as things are happening on your machine.

**7:00** · Maybe you're spinning up Clyde code, you wanna see how much memory it's taking, things like that.

**7:06** · So that's Btop.

**7:07** · Similar to Btop, there's another package called Mac Top.

**7:11** · Specific to people on Mac, And yeah, this is gonna show you just another view of a little more hardware centric on what's happening on your system.

### Terminal Viewers: Render Images (shaa) + Inspect CSVs (csvlens)

**7:24** · The next tool I want to show you is another convenient one.

**7:26** · It's called Shaa.

**7:28** · And if I go here into the public directory and I type shaa and then an image.

**7:39** · It will render that image in the CLI.

**7:41** · So this is nice.

**7:42** · Just a nice convenience to have to be able to check images while you're working with different files in the CLI.

**7:47** · Or you could have Claude show you images in the CLI while you're having Claude work with them.

**7:52** · I made an alias for this, so I can just take image and then the image, and then it renders it on the screen.

**8:00** · Similar to that, another tool I wanna show you is called CSV Lens.

**8:05** · I made a CSV, and this is A TUI for viewing CSV files.

**8:13** · There's one for Mongo and Postgres and things like that.

### eza: A Better \`ls\` for Busy Terminal Workflows

**8:18** · Okay.

**8:18** · And then the last one, and you might've already seen this a little bit, is this.

**8:22** · Tool called EZ a. EZ A is a alternative to LS with improved options.

**8:28** · I actually have LS alias to EZ A, so that's why when I type LS, you see that I have this grid.

**8:37** · So you can see here in the command we, enabled icons, grid and grouping directories first, and that's why I have this nice detailed Ls.

**8:47** · Where it's in multiple rows, I have nice icons, which can help you just find files when you're looking at a large amount of files that Claude is producing or across multiple machines.

**8:57** · These little details add up.

**8:59** · When you have 10 terminal screens open and you're on five VMs, it really helps to have things color coded and organized so you know what you're looking at having multiple windows that are colored differently, or it tells you.

**9:12** · I've been setting up a lot of conveniences like that to help me work with Claude Orchestration at a larger scale.

**9:19** · So that is why I have ZA hooked up.

### Wrap-Up: More Tool Deep Dives + Viewer Requests

**9:23** · I think I could keep going on different terminal tools, but these are some of the cool ones I've been running into.

**9:29** · So I'm going to end this video here if you want me to go specifically into any part of this.

**9:35** · Please let me know in the comments and I could make one video about, one of these tools definitely like working with En Vim and everything.

**9:41** · So yeah, this was just a dive into some of the CLI tools I've been playing with.

**9:46** · I hope you found this video useful.

**9:47** · Thank you for watching and I'll see you in the next video.