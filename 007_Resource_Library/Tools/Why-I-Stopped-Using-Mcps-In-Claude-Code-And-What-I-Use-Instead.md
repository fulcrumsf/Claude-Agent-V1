---
title: "Why-I-Stopped-Using-Mcps-In-Claude-Code-And-What-I-Use-Instead"
type: tool-doc
category: app-dev
tags:
  - tooling
  - reference
  - claude-code
  - mcp
  - ads
created: 2026-06-06
source: 000_Ingest/Why I Stopped Using MCPs in Claude Code (And What I Use Instead).md
---
![](https://www.youtube.com/watch?v=Xs2CkHEpIrM)

There's a really big problem with using MCP servers with Claude Code. In this video I show how connecting just 7 MCP servers consumes 50% of my context window, before I even type a single prompt. I'll show you how you can still give Claude Code access to the same number of MCPs without losing any context.  
  
Join my free newsletter for AI tips and techniques to automate repetitive work  
https://theailaunchpad.substack.com/  
  
🎥 Watch Next  
1\. Make Claude Code 100x BETTER (Context Engineering)  
https://youtu.be/ySA9tJ8RfVM  
2\. These 2 Tools Will Change How You Use Claude Code  
https://youtu.be/imw8MkwW9xw  
3\. How I Turned Claude Code Into My Personal Assistant... You can too!  
https://youtu.be/aYAVSG4Ra40  
  
Apps I use:  
Get Wisper Flow Pro FREE for 14 days! https://ref.wisprflow.ai/kenneth-liao  
  
Support me making more content and free coding projects like this.  
https://buymeacoffee.com/kennyliao  
Thank you so much for your support!  
  
🛠️ Resources  
1\. MCP Launchpad: https://github.com/kenneth-liao/mcp-launchpad  
2\. Get any of my plugins, free! https://github.com/kenneth-liao/ai-launchpad-marketplace  
  
🕒 Sections   
00:00 - Intro  
00:27 - The Problem  
03:35 - The Solution  
05:32 - MCP Launchpad  
06:50 - MCP Launchpad Demo  
12:20 - MCP Launchpad with Claude Code  
16:07 - MCP Launchpad Setup  
  
✉️ For Business Inquiries:  
kennyliao@theailaunchpad.io  
  
#claudecode #mcp #aiagents

## Transcript

### Intro

**0:00** · I've been saying this for a while. There is a massive problem with using MCP servers right now, especially with Claude Code or other coding agents, and that is how much context they take up.

**0:14** · This is what my Claude Codes context window looks like when I'm connected to these seven MCP servers, which I use on a daily basis. Claude's context window, as we know, has a 200,000 token limit.

### The Problem

**0:28** · And if you look at this line here for the MCP tools, you can see we have with these seven servers taken up around 100,000 tokens or 50% of that context window, which is insane. You can see that visually over here by all of these blue token stack icons taking up about half of the graph.

**0:51** · So, this is a real problem because we obviously need to give our agents access to all of these really powerful tools, but doing it this way just doesn't work well and it definitely doesn't scale. If I added just a couple of more MCP servers, I would potentially just take up the entire context window and not be able to chat with Claude at all. I'm only left with about 36,000 tokens of free space in order to now start my conversation.

**1:23** · So today I'm going to show you a better way where you can still give Cloud Code access to these MCP servers. Actually access to dozens and dozens of MCP servers with potentially thousands of tools across them. all while retaining 100% of this context. So instead of looking like this, your context window will look more like this.

**1:54** · If you're like me, you've been really amazed by how far Frontier models have come. They're so good at thinking through problems now, and their improved reasoning allows them to more effectively solve long horizon tasks.

**2:09** · both more autonomously and reliably, making them feel more intelligent. Now, in order to take advantage of all of this and get them to do more work for you, we need to give them access to tools, lots and lots of tools. And MCPs are the typical way to do this. They're easy to set up and instantly give your agent access to hundreds of new capabilities. But connecting them directly to Claude like this, which is the typical way, you get this problem like we just saw.

**2:41** · And from looking at this, you might think that your biggest problem is the fact that you don't have a ton of free space here for your conversation with Claude. And that is true, but there's another really big problem with this. In my last video on context engineering, I discussed a paper published by Chroma on this idea of context rot.

**3:02** · And we saw that in that paper they did a bunch of tests and showed in many different ways that the performance of agents degrades as you fill up more and more of the context window. And even worse than that, if the context is filled with a bunch of irrelevant information, then it tends to distract the agent and degrades the performance even more. I highly recommend checking out that video if you haven't to understand the importance of context engineering and how we can use it to optimize cloud code's performance.

### The Solution

**3:37** · In my last video, I also mentioned this idea of instead of using a bunch of MCP servers, what if we just created a bunch of CLI tools or scripts and then tell Claude that it has access to a bunch of different tools and capabilities through the terminal, effectively giving Claude access to thousands of tools, but initially only taking a very small amount of tokens in the system prompt.

**4:06** · And this idea of letting cloud do its own tool discovery just follows the principles of progressive disclosure where cloud only needs a certain context for a tool if it has already decided it needs a certain tool to perform an action. So going back to this example, if I'm asking Claude to look into an error I got in the application I'm building and ask it to go into Sentry, it potentially would only need one or two tools from this Sentry MCP server.

**4:38** · But again, by having all of these MCP servers connected directly to Claude, we're diluting the important information by stuffing in all of the tool definitions for these irrelevant MCP tools. So, here's an actual working example where I've had Cloud Code build different CLI tools for me using UV. And so, they're all installed as UV tools.

**5:03** · So in the terminal, if Claude was just to run UV tool list, it would see all of these different CLI tools. And at this point, Claude could just run any one of these CLI commands. Let's use thumb as an example in order to see what that CLI tool does. So here it would see that this is a YouTube thumbnail generator using Gemini and decide whether it needs to use one of these tools or not. So, how does this help us with MCPs?

### MCP Launchpad

**5:33** · Because MCPs, as we mentioned, are already available. They're super easy to use and set up and really convenient. So, you don't have to build your own CLI tools or connect them to APIs and stuff. The best way that I've found is to have one unified tool that all of your MCP servers are connected to and where Cloud Code only needs to interact with that one tool. So this is what Claude Code and I built together.

**6:03** · It's the MCP Launchpad and it's essentially one CLI tool to rule them all. And I have been using this now for several weeks and it works amazingly. I've been improving it over time and am really excited to share it with you. So let's first see it in action and then I will show you how to set it up for yourself. Once MCP Launchpad is installed on your system, it will be available globally. So you can access it from any project and any terminal.

**6:34** · And most importantly, Cloud Code can access it from anywhere on your system. So whatever project you're working on, it will be able to use all of these different MCP servers that you connect. So I'm just in this test folder to show you this example. But if I run MCPL, which stands for the MCP Launchpad, you'll see we get this initial help menu on usage. And you can play around with this to learn how it works. There's also good documentation in the repo, but I'll just walk you through some useful commands.

### MCP Launchpad Demo

**7:05** · So, if we do mcpl config, you can actually see what's in the mcp json file and all of the servers that are configured. You'll also see next to each server whether it's enabled or disabled. So since we're using this as a gateway, sometimes we want to turn some servers on and off depending on our needs. And so if we go back up to the help menu again, you can see that you can enable or disable servers really easily with just these two commands.

**7:36** · So looking at the configuration is going to be useful for debugging or figuring out what environment variables are required by each server. We can also use this command to list all of the servers themselves as well as look at all the tools within a server. So by typing mcpl list, you'll get a list of the servers and you might see something like this if it's your first time running it where it'll say that the servers are not cached. This just means that the servers haven't been connected to.

**8:07** · But once you connect to the MCP servers, it'll cache all of the tools. So you don't have to actually connect to the MCP servers themselves every single time you want to browse the tools. So in order to actually connect to the MCP servers and then cache all of the tools that are available, you can run MCPL list and pass the option for refresh.

**8:30** · So once you do that, you'll see it just connect to every server, get all of the tool definitions, and then cache them locally. Once that's done, we can explore what tools are available in each server. So again, you can run mcpl list and this time pass in the name of a server. So we can do the first one, render, and you'll see all of the tools in this server.

**8:59** · You can also get more details for any given tool, including the full tool schema by using the inspect command. So, mcpl inspect and then because we have multiple servers connected, you first want to pass in the server name and then the tool. So, let's just get one of these. Uh, let's say get service. So, here we're going to inspect the get service tool in the render MCP server. And if we do that, you get the actual JSON schema for that tool.

**9:30** · And this is how Claude Code will be using the MCP Launchpad to discover tools and learn how to use them on the fly as it needs to. But I want to show you the coolest part about this. I'm going to bring up the help menu once again by just running MCPL. And you'll notice that there's this search function.

**9:57** · Remember that we connected to each MCP server and cached all of the tools in that server. So, we now have all of the tool schemas for every single tool that we have access to across all of our MCPS and have built a semantic search using BM25.

**10:14** · Don't worry if you don't know what that means. It's just a fancier search than normal keyword search where it's going to look for something that's related more semantically to what you're looking for. So, as an example, we can do MCpl and then pass in a search term. So, let's say something like um issues and we'll get the top five tools that are most similar to our search term issues.

**10:44** · So, we get a ton of tools from Sentry, but we also get issues for linear. What if I wanted to look for tools for connecting to a database? I could type in MCplarch SQL and then you can see we get our execute SQL tool from Superbase. Now, this makes the MCP Launchpad so much more powerful because Claude doesn't even have to navigate all of the menus that I just showed you in order to find these tools manually.

**11:15** · It can just search for tools based on the task that it's trying to accomplish. And you can see how this makes it so much more scalable.

**11:26** · In this example, I've only connected seven MCP servers, but almost every week I'm thinking of another MCP server that I want to be using. But you can imagine if you have again dozens and dozens of MCP servers adding up to thousands and thousands of tools, it's going to be pretty tedious to hierarchically move through these menus to find specific tools and that's also going to take up context.

**11:55** · So having something like this search function where you only get the specific information you're looking for and the exact tool for the given task makes things way more efficient. By the way, I am super curious what MCP servers you guys find the most useful for your workflows. Let me know in the comments below what they are cuz I'm always looking to try new MCP servers. I want to show you just a really tiny preview of Claude using the MCP Launchpad to discover tools.

### MCP Launchpad with Claude Code

**12:28** · So, I'm going to spin it up and I'm going to just start by asking what MCPS it has access to.

**12:37** · So, you can see because I mentioned MCPS, it knows that it has access to the MCP Launchpad because I've mentioned it in the cloud MD file. So, so there's a very small amount of context, just kind of an overview talking about the MCP Launchpad and how it can discover and connect to different MCP servers that I put into the CloudMD file. So, that's all the context it has. In order to see what's actually in them, it calls the MCPL list tool.

**13:09** · It can also see what servers are active and disabled. So now we can ask it for a specific tool. Do you have any tools for querying databases?

**13:26** · So here you can see it runs two searches. So it first runs a search for query database and then it runs another search specifically for SQL. And then it's able to come up with this exhaustive list of tools available for querying our databases either on Superbase or on render. Now this is a contrived example because I'm asking it specifically questions about these tools.

**13:55** · But you can imagine as it's working and realizes it needs some functionality, it will also be able to use this search tool to do exactly what it just did and essentially look for a SQL execution tool, for example, when it needs to query the database. And as a real use case for where Cloud Code is actually using the MCP Launchpad CLI every single day is in this project that I have for a production app.

**14:25** · This is my linear for this project and I have a ton of tasks here that Claude has been working on and helping me fix. So you can see I have a huge backlog and because Claude is connected to linear it's obviously able to see all of these issues.

**14:47** · So for example I can ask what's the most urgent issue that we have for the app and it should be able to search linear to understand uh what the top issues are. So there you saw it it calls the uh list issues tool from linear and it'll be able to summarize all of the important issues we have. And from this I could just tell it to work on whatever highest priority we have in the backlog.

**15:21** · And you can imagine if it's a bug or an issue in the database, it's going to leverage again the MCP Launchpad CLI to interact with the database on Superbase or Sentry to find uh errors and traces. Linear for managing all of the tickets, etc. Now, obviously, this is an example for coding because it's what I've been using it a lot for lately, but you can imagine connecting any kind of MCP.

**15:50** · And whatever your workflow is, whatever you're working on, tying together many different functionalities through MCP servers, all through the MCP Launchpad and having Claude be able to accomplish all kinds of tasks. So now I'll show you how you can set this up and start using it to connect your cloud to thousands of tools. Using MCP Launchpad is super easy.

### MCP Launchpad Setup

**16:17** · Head to the repo which is linked in the description and you can follow the instructions on here, but I'll just walk you through it right now. You're going to need to have Python and UV installed. If you don't, just head over to this link. It'll take you less than a minute to install UV. Once you have that, we're going to be installing MCP Launchpad as a UV tool using this command. So, you can literally just copy this and then open any terminal and paste this command in.

**16:46** · You'll see that it installs two executables and then you should be able to run the command mcpl from the terminal and see the help menu that pops up. This confirms that you installed it properly. Next, you want to configure your MCP servers.

**17:02** · So, you might already have an MCP.JSON file laying around, but if not, you're just going to want to create this file either in the project directory that you're working in or in your user level.cloud folder, which I'll show you in a bit. So, as an example, if this was my config, I would just copy this and go to a project folder like this is for this MCP Launchpad project. And you can see I have no MCP configuration yet.

**17:32** · So I'm just going to create a new file and call it MCP.json and then paste this in. Now this is important. It has to be named MCP.json.

**17:48** · You don't want to put a dot before MCP because that is the naming convention that Cloud Code uses and Cloud Code will be looking for a MCP.json JSON in this project folder. So to avoid colliding with cloud code MCP servers, we just omit the period in the beginning of this name.

**18:08** · So if you create the MCP JSON configuration in a project like this, then MCP Launchpad will only be able to connect to the MCP servers when you're using it in this specific project directory. So if you want your MCP servers to be available across your entire system, basically wherever cloud code is working, then I highly recommend doing this in the user level.Cloud folder, which I'll show you after this.

**18:37** · But before that, if your MCP configs require any environment variables, you can use this notation with the dollar sign, curly brackets, and then the name of the secret. And then you want to create av file and define your key in here. So let's say this is my API key.

**18:59** · So when MCP Launchpad uses this configuration to connect to your MCP servers, it's automatically going to load any environment variables from this file and parse it into this config to connect properly.

**19:18** · Now, just like with the mcp.json, thisv file can be created both here or in your userle.cloud folder if you want it to be available systemwide. So, the EMV file you create here again will only be available for configurations in this project.

**19:38** · And just like in cloud code, this works using a priority system where any MCP servers that you configure in your project here will take precedence over servers defined globally. So just keep that in mind. That's a nice way to control project specific configurations.

**19:59** · Now, if you want to make your MCP servers available globally all the time, which is the way I recommend to set this up because again, we're not worried about taking up additional context, then what you want to do is go to your user level folder. So, on a Mac, it's just going to be in your users directory and then your username. It should be similar on Windows. And you're going to need to expose hidden folders because the docloud folder is hidden. So on Mac, that's shift command period. And then you're going to open this.cloud folder.

**20:35** · And in here is where you would create your MCP JSON file, which you can see I already have one set up here. And just to make it easier to see, I've opened this.cloud folder in VS Code. And you can see I have my MCP.json file here. So again, anywhere you run Claude in any terminal, any project, these MCP servers are going to be loaded. And then you can see I have my MV file here, which is going to have all of the secrets required for these MCP servers.

**21:08** · Now, once you have your config set up and your environment variables, you can go back to the terminal and now run MCpl space config. And you should see that the config has been properly loaded. And then the next step that you want to do is type mcpl space list.

**21:31** · And then you should see the list of MCP servers along with the tools in them. If it's your first time running it, you might not see that the tools have been cached yet. So you can run an MCPL list space d-refresh.

**21:47** · And this is going to go ahead and reconnect to all of the servers that are enabled at least and then go and then cache those tools.

**21:57** · And you should see a helpful message at the bottom too that points to the exact location of where it's loading this uh MCP config from. So you can see this is my global config, not in any specific project. And it's also loading the EMV file from that user level.cloud cloud folder. And that's it. You can now start exploring all of the tools that are in each MCP server. Try calling some just to make sure that the connections work.

**22:26** · And you can go crazy adding as many MCPS as you want. Now, the final piece to get it to work with Cloud Code is to tell Cloud Code that it has access to the MCP Launchpad CLI tool. And so I've also included in the repo the instructions to do that down here which is basically just to copy this claude.md file which I already created for you. I'll scroll up.

**22:54** · You can see it's right here. So if I click into that cloud MD file. This is just a very highle prompt that describes what the MCP Launchpad is and gives it a few example commands in order to start using the MCP Launchpad and discovering tools. So all you want to do is copy this Claude MD file. If you don't already have one, you can copy it into your project level.

**23:19** · Or if again you're configuring this to be global, which I highly recommend, then you want to copy this into your cloud. MD file inside of your user level directory. So I'll switch back over to mycloud user level folder and open this up. I have some of my own other working instructions, but I'll just scroll down so you can see it here. So, here's the exact text from that cloud MD file that's been pasted in.

**23:49** · I also just added this extra piece myself because I already know what MCP servers I've connected. So, so it's definitely helpful if you list the MCP servers that are available. So, it doesn't have to list them and guess what's there. And it would probably help even more to add a little snippet or description of what it should use those servers for. But that's it.

**24:15** · Cloud Code will now be able to use the MCP Launchpad really effectively just with this small amount of instructions. Now, my feeling is that this should already exist and I wouldn't be surprised if Cloud Code implements something similar in the near future because it's kind of just a no-brainer to use some kind of tool discovery method that really preserves the context window. So, I'm sure we'll be seeing an update soon that will build something similar into Claude Code.

**24:47** · But until then, feel free to use the MCP Launchpad. That is going to do it for today's video. I hope you learned something. I hope you found this useful.

**24:57** · In the next video, I'm going to do a follow-up on my personal assistant since I've made a lot of upgrades to it and it's working a lot better. It's evolving, so I want to share that with you guys. So, make sure to subscribe and turn on the notifications. Thank you guys again so much for watching and I'll see you in the next one.

**25:18** · \[music\] \[music\]