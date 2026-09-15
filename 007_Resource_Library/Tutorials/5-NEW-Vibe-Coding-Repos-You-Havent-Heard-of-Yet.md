---
title: "5 NEW Vibe Coding Repos You Haven't Heard of Yet"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=UnzD_bwylWs)

⚡Build & launch your app in 30 days:  
https://www.skool.com/tech-snack-pro  
  
🔥Join my FREE community with full guides & tons of prompts from past videos: https://www.skool.com/tech-snack  
  
⌚Timestamps:  
00:00 Intro  
00:29 Draw.io  
08:00 Ponytail  
12:06 Handy  
15:12 Improve  
22:25 Skill Spector  
  
🗄️ Resources:  
  
https://github.com/Agents365-ai/drawio-skill  
https://github.com/DietrichGebert/ponytail  
https://github.com/cjpais/Handy  
https://github.com/shadcn/improve  
https://github.com/nvidia/skillspector  
  
💪 Who Am I?  
  
My name is Sean... I went from tech bootcamp grad to startup Sales Engineer, scaled a marketing agency to 8-figure ARR, and exited a small CRM along the way (sustained $250K ARR).  
  
This channel is for fusing tech skills with business building experiences and sharing what I learn along the way.  
  
👇 My Other social accounts  
  
📸 Instagram: https://www.instagram.com/seankochel/  
🐦 X/Twitter: https://x.com/IAmSeanKochel  
👨‍💻 Linkedin: https://www.linkedin.com/in/sean-kochel/

## Transcript

### Intro

**0:00** · There are five new GitHub repos that I've come across recently that are pretty awesome and half of them don't even have 10,000 stars yet, which is pretty surprising to me because these things solve some pretty big problems that I deal with on a daily basis trying to build apps with AI. So, we're going to go through each one, we're going to demo it, and we're going to talk about like where this can fit in your process and where some of these things can actually be used together. Starting with my favorite of the bunch that you might make fun of me for, draw.io.

**0:28** · So, one of the things that really tends to suck about vibe coding things, especially if you're not an engineer by background, is that you tend to not know, number one, what you've built realistically, but number two, how those different things that you've built actually connect together.

### Draw.io

**0:47** · And that can be a big problem because when you want to go through and make improvements or just generally understand where an issue might be coming from or an area that should be improved, you're kind of relying purely on the language model to figure that thing out for you when in reality you do need to have an understanding of how those things work. And so, what this skill does specifically is that it uses the draw.io command line interface, but it uses it to help you build actual architecture diagrams of your app.

**1:18** · So, we can see that in an example here where we can see the the mobile surface, the web surface, maybe the admin surface, it all gets routed through this API back end, which passes it off to all of these different services depending on what's happening, and then they have, you know, different databases depending on the service and how you've structured your app.

**1:38** · And so, having this type of understanding can be super valuable because again, it's going to give you the understanding of like what is actually happening inside of your app, where do things live, and in my opinion, the best way to approach vibe coding or vibe engineering is to approach it from the perspective that we want to be learning at all times about how this stuff works so that we can build better and better and better things in the future.

**2:02** · The worst thing that could possibly happen is that your skills stay where they are now and this in my opinion is the type of tool that helps you do that. So let me show you how it works specifically. So the first thing that you need to do is just pop in a command depending on, you know, if you're on Mac, Windows, or maybe you're a complete Chad and you're on Linux.

**2:22** · Make sure that you install this thing first. I'm not going to go through that cuz it is very straightforward and then after you've done that, all you need to do is install the skill. So if you're not using Claude Code, you could just use the general skills add command and then pass this in, but if you want to install this via like a Claude Code plugin or whatever, you can just use the slash plugin command, add the marketplace, and then install the skills out of the marketplace. And so the first thing you're going to do is you're going to come down and you're just going to invoke the skill, the draw.io skill, and then you're going to give it a command.

**2:51** · And so one of the things that's really nice about this is you can give it a natural language description of exactly what you want to see visualized and it is going to move through and do that. So in this example that I'll show you first, I said, "I'd like to visualize the different layers of the services inside of my repo." And so this thing moved through, it explored the codebase, which realistically, I mean, didn't take that many tokens, and then from that it basically drew us an editable architecture diagram. So if we were to go down now into draw.io and pop it open, we can see exactly that.

**3:22** · So in this case, we can see the overarching architecture of an MVP that we've been building and we're going to be taking it to market inside of my paid community.

**3:33** · And so we can see exactly what that looks like. We have our presentation layer, which is purely responsible for just displaying things to the user. So we have the mobile surface, we have all of like the navigation and chrome inside of this thing, all of our different like feedback states and icons and badges and the different overlays we have in our app, and everything that's responsible for actually presenting something to the user lives here. So, then if you continue to move through, we can see like the presentation layer then is interacting directly with our front-end state management.

**4:02** · So, we can think of that like where does all the data from the front end like actually live or exist when the presentation layer is calling it? This front end then is like resolving everything inside of it against our service layer. So, accessing the data, all of the business logic. Um in this case, it's like a natural language food logging app, and so there's a lot of like resolving of the expressions that a user kind of chats in with.

**4:30** · So, if someone says like, "Log me my chicken and rice bowl." it needs to be able to resolve that expression and then go out and search it. And so then we can see all of the different functions inside of this. We have this resolver, we have this recipe function, right? We have a bunch of other like functions and services in this layer.

**4:45** · So, the reason that something like this is valuable is I think what a lot of people do when they run into some sort of issues, we just say, "Hey Claude code, go fix this problem." And you know, it can typically do that pretty effectively, but to force it to go out and explore a bunch of stuff, at the end of the day, if we could have pointed them to what we knew was the area that the problem most likely lived, we're going to end up saving on tokens in the long term, and we're going to actually build an understanding of how things work.

**5:12** · So, for example, if I'm running into a bunch of issues with relation \[snorts\] to like how the chats that a user sending get actually parsed, and whether or not it's calling like the agent effectively and things like that, I know that that like is most likely going to start with like, "Hey, we need to go check this like resolver layer inside of our app." So, it would be really dumb if we sent it off to like read our analytics or telemetry files.

**5:37** · That would just be dumb and a waste of time. So, then we can see, okay, well, the service layer then interacts with like our our back-end database specifically. So, the different foods, different food entries, recipes, macro targets, like all that stuff related to our app specifically, uh live inside of this database layer. And so, then the last piece is that we have these different edge functions where we're connecting to like external services.

**5:58** · So, PostHog for like capturing product events, we're using OpenAI for like chat completions, and then we're using edge functions to handle some of the the other things that happen. So, now this is just one example of what this could look like. If we wanted to see how these different services, for example, like actually connect into very specific databases and like what that logic actually looks like, uh we could ask this skill in this case to come through and actually like make that type of update to our diagram.

**6:24** · And so, to drive this point home, there was a a tweet recently from the CEO of Microsoft. And basically, to wrap all of this up in a a too long, don't read, we tend to be like really focused on, you know, the best model and trying to like one-shot things and do all of this like hand-wavy type of like demonstrations of these tools.

**6:49** · But, if you really want to succeed in the long term, you need to use these tools as uh learning loops. Because you will only ever be able to push these models as far as your expertise goes.

**7:02** · That's why people that are like incredibly talented engineers already can build really complex things with these tools, whereas people that more are more beginners, you know, it's pretty awesome that they can build their remind me to walk my puppy app. But, the reason that it can't really extend beyond that is because they don't have the language or the understanding to know where they can push these things in the first place.

**7:24** · And so, while it may seem basic, having a tool like this that can actually start moving you in the direction of like learning exactly what is going on inside of your projects, I think is an incredibly incredibly valuable thing that everybody should be doing. But, even with having something like this in place, you may inevitably run into the situation that maybe even what we have here is unnecessarily complicated.

**7:48** · Like sure, we've built all of these things and technically it works, but the one thing that language models love to do is over-engineer solutions to problems, and that is what the next tool helps us with. So, the next tool up is called Ponytail, and it has one of the best avatars, I think, that I have ever seen for GitHub repo.

### Ponytail

**8:08** · And so, like I said earlier, one of the biggest problems with AI coding tools is that they will 100% over-engineer solutions to problems. Despite your best efforts, despite like trying, maybe you try to rein that in, maybe you don't care at all, but it will go out there and build like abstractions and things that you do not need for where your project is at now.

**8:29** · And so, this library is meant to help us solve that problem, so you can kind of think of it like those caveman plugins that we see flying around everywhere where it's meant to have the models speak to you in like less lines, but this is doing that like for the actual implementation. Like, can what you are doing be done away with entirely or be done a lot more simply?

**8:54** · So, if you've ever worked inside of like a SAS company, you might know someone like this. Long ponytail, oval glasses.

**9:01** · He's been at the company longer than version control itself. You show him 50 lines, he looks at them, shakes his head, he says nothing, and he replaces them with one. That's what we're trying to do with this library. So, let's go in and actually look at how it works.

**9:14** · Obviously, you're going to install this thing the way you would install a plugin, so you add the marketplace and then install the plugin. So, there's actually a few different uh commands inside of this. They have the the straight-up ponytail command, and this is going to be helpful if you're like actually attempting to implement something. Then they have this audit command that will look through everything you have and try to understand like where you have unnecessary things in place, where you could simplify, where you could delete things entirely, and then you can also run this for like actual code reviews.

**9:45** · So, for example, if we were to come down inside of this project and run the audit command, this thing is going to run through and hopefully, maybe hopefully, maybe hopefully not, tear my code base apart and tell me that I've done a horrible job. All right, guys. So, now that this thing is done, we can see that it came up with a bunch of things to potentially fix. So, one, two, three things that it would recommend deleting entirely because they're either like not actually used. So, in this case, it's like an Expo project, and so we're importing like default Expo things that don't actually get used.

**10:14** · So, we would want to remove those um along with some other files. There's a few areas. I think this is the biggest find. We have one, two, three, four, five, six, seven things that should be shrunk down. So, an example of like what one of those things to shrink down might look like is in our case in this app, my philosophy with the planning process is that you should be planning for all of the different like error states way ahead of time before you start building.

**10:40** · And so, in this case, we have uh at least three different error states uh specifically as it pertains to this strip thing that we have in our app. And so, we have an error strip, we have a correction error strip, and then we have a safe error strip. And these are all individual components. And the only thing that's really different about them is the copy that's used and like the color and the handler that's inside of it. And so, in this case, we should just have one error strip component that accepts these as like properties inside of them.

**11:09** · So, that's an example of what you might find with the shrink command. And then we have this uh YAGNI, you ain't going to need it, which are typically situations when you've like over-engineered something that like, yeah, okay, you're maybe planning for like some way off in time thing that like is never going to actually happen. And so, why create the complexity when you could just do something that again is simpler, which is again the point of this entire library.

**11:33** · So, in a bit I'm going to show you like a different take on this type of tool because this is incredibly valuable again, especially if you're not an engineer by by background, but even if you are an engineer and you want to be able to like drive this thing in a certain direction, I personally think this type of tool is is really really really awesome.

**11:52** · You just need to find like based on your experience level where this fits best in your specific process, like what skills you use to build things, like what spectrum and tools you use, and again where this is going to make sense in the context of all that. But before we get to that other kind of like implementation of something like this, I want to show you a an open-source tool that I found recently that is a a huge quality-of-life improvement if you don't already do it, and it is free.

### Handy

**12:18** · And so you've probably heard the stat before that we can speak things out I think three times faster than we can type them out. And so that's why you see a lot of people like going all in on tools like WhisperFlow where they're just speaking into the model what they want to happen instead of sitting there and having to type the thing because what ends up happening is that when you are typing things out you tend to like cut down on the context that you probably would have otherwise given the thing if you were able to like get that context out of your brain a lot more quickly.

**12:49** · And so there's a lot of like paid tools for this that I try. I currently use WhisperFlow, which we can see down here.

**12:56** · This is me using WhisperFlow down in the bottom, but it costs money. And so this tool, which is called Handy, is basically a completely free and open-source version of something like WhisperFlow with like technically like a little bit less functionality inside of it. Like I don't think it has like AI rewriting capabilities and some things like that, which WhisperFlow does, but if you don't care about that and you just want like an easy way to be able to dump your thoughts, this is a really great tool for that.

**13:24** · And so the way that we can install this thing, there's two options. You can go through and like install it via Homebrew. You can also just go to their website, download it for whatever platform you are on.

**13:36** · Downloads very quickly. Then all you need to do is drag it into your application folder. Again, in this case on a Mac, you do whatever it is for your your operating system. So, then we can pop the thing open, accept the permissions. And now, one thing that's pretty cool about this, if we look at it, is that we can choose the type of model that gets used like based on the machine that we actually have. So, whether you care more about like the accuracy or the the speed, you can choose which you want to actually use.

**14:01** · Um Parakeet seems to be a model that is getting a lot of traction for people lately. There's also Whisper large, which is slower to process things, but it's very accurate. But we could come through and try, for example, something like Parakeet. And now, just to demonstrate how this thing works, I didn't configure any other settings. We can just come through and do command spacebar. And now, as we're sitting here typing out, we could be talking about anything, talking about what our feedback is on like a specific spec that we were looking at inside one of our projects. Maybe we didn't like the direction that it was taking.

**14:31** · Maybe we wanted to zoom out and like explain things in a different way, whatever it might be. We can see that we got that entire thing, and it is uh pretty accurate. Now, as we're sitting here typing out, we could be typing anything.

**14:42** · Blah blah blah. Again, pretty accurate.

**14:43** · There are some differences between something like this and Whisper flow.

**14:46** · Whisper flow will take out like fluff words and like filler words. So, if you're rambling or saying like uh a lot, it will take those types of things out.

**14:54** · But for purposes of using a language model, I don't really think that matters that much. So, if you've been interested in using something like Whisper flow, but you can't stomach paying the $20 per month or whatever it is for Whisper flow, uh this is a really cool open-source option that you can use. But it would be helpful in this situation to like actually put this to the test with something valuable. So, how can we combine this with the next skill on the list to really improve our overall like efficiency as we're moving through and building things.

### Improve

**15:25** · So, the next skill that I want to show you is called improve and it is developed by Shad CN or Shade CN.

**15:33** · I still don't know how to pronounce it.

**15:34** · Comment below and tell me the proper way to pronounce it so I stop butchering it on my YouTube videos. But basically what this thing is is it is a code base auditor. So, if you remember all that time ago when we had access to Fable 5 for like 2 and 1/2 days or whatever it was, uh this was an example of one of the skills that I was using non-stop in order to improve my projects. Because in my experience, Fable 5 by itself was really good at improving things where you had like an existing project or there were existing patterns.

**16:05** · I know a lot of people were showing off like one shots of new things, which is cool, but I thought it was really great at fixing existing things. The fact of the matter is I think I like every model jump, we should be using those opportunities to like actually improve things we've already built. But until they decide to give that back to us, this skill is still pretty dope. So, let's look at how it works. So, in this case what we're going to do is we're going to call this improve command, but then we could come down and we could use a tool like Handy that we found in the uh in the last video.

**16:36** · I need you to do a code base audit of our app, but I want you to specifically look at the like effectiveness of our resolver functions.

**16:46** · So, how are we parsing the information that comes through on the front end from the user via the chat and deciding whether or not that needs to actually be processed by a uh language model and it needs to like go off to the agent or if that's something that can actually resolve down to something like a simple search.

**17:03** · So, this is primarily going to be a language model token optimization exercise, but it is important in whatever recommendations you make that we're still optimizing for for accuracy so that we are taking the proper actions when we need to. Boom, and there we go.

**17:20** · So, if I was going to have to type all of that out, I probably would have said, "I need you to optimize our code base for language model calls, right?" But, now that I have this capability, I can get a lot more context in there and really flesh out my ideas more. If I wasn't doing this like in a video, I probably would have spent more time doing like several of these thought drops into like a text file and then pasting it over.

**17:40** · But, again, one of the reasons this all of these things kind of come together is because if we were to go back to the draw.io skill that we were looking at earlier, again, the reason that I was able to know like specifically where I think this like inefficiency actually comes from, it's because I have this type of architecture diagram and I've like paid attention to the types of things that were being built inside of the app, reading the specs, and trying to understand what it was doing and why.

**18:08** · So, I know that all of this logic lives inside of this resolver, and so if I'm able to point the model there, then we're going to get a much better analysis straight out of the gate. And so, one of the reasons I really like tools like this, it doesn't have to be this specific one, but any tool like this, is that it finds these edge cases. So, what happened previously in the context of this app is that I already asked Opus to fix this thing for me. And what it did was it fixed this in one spot.

**18:34** · So, the code base already has this thing that I'm basically asking it to optimize, but it only put it in one place. It's only in the recipe composition function inside of this app. So, if someone's like on their phone talking via natural language and saying, "Hey, I need a chicken rice bowl. I had 100 g of chicken. I had 50 g of rice, and I had my homemade buffalo sauce." That's like the only place that it gets used, and there's a lot of places in the app where this type of optimization should take place.

**19:05** · But, in reality, what's happening is that most of this stuff is just being sent directly to the language model, when in reality, a lot of this stuff could resolve deterministically, meaning we don't need to use a language model to do that. And so, that is exactly what it found here, and now it's moving through, and it's enumerating like all of those things that it found. So, we have 1 2 3, at least four different things that it is pretty confident in what it found is an issue.

**19:34** · It's relatively low effort, and it's a relatively low risk area to go in and try to refactor. And now, one of the things that I I really do like about this tool is that it will not go through and implement things like I think a lot of these tools like try to implement the thing in the same breath.

**19:51** · This is just going to build you a plan, so that you can go and implement this in any tool that you could possibly want to implement it in. So, now that it has these plans built out to fix all of these different issues that it found, just to show you guys like what my concrete next steps for a workflow would be, is to create these as GitHub issues.

**20:09** · Now, the reason that I like to do this specifically goes back to a video I did last week on agent loops, which get a lot of for some reason, but one of the really valuable workflows that I personally use is anytime I want to

**20:25** · build something and I have a clear concept behind that thing, whether it's a bug, whether it's a feature request, an optimization that needs to be made, like whatever it is, I create those as GitHub issues, and then I make sure that I'm really on board with what the plan is to implement against that issue, and then I can create a giant backlog of these things, and then as I'm working throughout the week, I can just have something in the background moving through, pulling any issues that are open out, implementing them, creating a pull request, reviewing the pull request, and then I can step in and do

**20:56** · any sort of review that I need to before it actually gets merged into the main project. And so, for me, this is like where that type of thing starts if I'm using a tool like Improve, and I want to be able to create that backlog. Um this is how I do it. I see no reason not to use something like GitHub. There are other tools you can use like linear and other project management tools, but since my repo is hosted on GitHub and it works for that, I don't need some super complicated solution. That's what I use and this is exactly how that process works.

**21:25** · So later on today after I'm done with this video, I'm going to be kicking off agents to move through and actually implement on these things. If you guys want to see any other like types of videos about the types of agent loops like this that I use, you can comment below and let me know and I I can put a video together on something like that.

**21:42** · But now, if we were to pop into the GitHub repo, we can see that we created all four of those issues right here. And then I would move through like what I would do is add labels to them depending on like exactly what needs to be done.

**21:53** · So anything with a backlog tag for example, won't get implemented when I have these automated runs moving through. So you can come up with your own system for how you want to manage these things, but this is a really solid process. And now if we pop in, we know like exactly where the plan lives. We can see like exactly why we're making this change, what we are doing. And then you can come through if you want to and you can have more of a back and forth chat. You could tag Claude for example and tell it to go out and research something. A lot of different things you can do, but overall, this is a really solid process.

**22:23** · Now the last thing that I'm going to show you guys is kind of unrelated to all of this, but I think it's a really dope tool that everybody should be using in certain situations.

### Skill Spector

**22:34** · And so that skill, I guess maybe it's not technically a skill, it is a scanner of skills that was released by Nvidia.

**22:42** · So what this is is this is a security auditing toolkit for scanning skill libraries specifically. So I want to give you a really concrete example of how I would use something like this. So there's this repo I came across recently that's going really hard and trending.

**22:59** · The only issue that I have with it is that the entire thing is in Chinese and I'm the type of person that when I want to use a new library, I will typically go through and try to understand how it works first before I dip in and decide to start building this thing. You could try to maybe swap the repo to English and move through and try to read the thing, but in this case, this is a a prime example of where like I don't know what could live inside of this script library. Like I don't know what could be in here.

**23:25** · Like yeah, I could go through maybe and read some of this, but realistically if it's in a language you don't understand, there's going to be like so many potential like issues realistically that could crop up. And so this is an example of where I would want to scan a repo. And so what we can do is we can come through and copy the URL and then we can pop down into our terminal and in this case we are inside of the skill spector project.

**23:45** · One thing that I will say, just popping back to this, the way that you need to install this and get it to work is that you need to actually clone this repository and then you need to have Python on your machine and I mean you could have a language model help you with this if you're not comfortable with it, but you need to kick off a virtual environment inside of that project. You need to install the dependencies and then the last thing that you do need to run this, you can run it for free, but you will get a ton of false positives to the point that it's not even really helpful.

**24:13** · In this case, I am using an open AI API key to run this scan. So we're going to pop down in here and then I'm going to run skill spector scan and then I'm just going to paste in the repo and now this thing is off and running doing this scan. And so especially if you are like a open claw Hermes Chad, you know, that's automating their entire life allegedly making a million dollars a day doing no work cuz you know, the Hermes bot goes out and sells stuff for you.

**24:42** · But even if you just like to experiment with things, skills are a huge like attack surface for people that live in their parents basements and eat Cheetos.

**24:52** · And also for serious talented hackers that just want to take advantage of whatever it is that you've built. And so, being able to like scan things like this is is incredibly valuable. So, in this case, I mean, I'm actually somewhat surprised. This says that this is a critical issue, this repo, and do not install it. Um so, that's interesting.

**25:09** · Let's try to move through and understand like why that's the case because again, it could be something that like maybe you are willing to, I don't know, like bypass that and just do it anyway. So, I think the biggest issue is that it has a lot of functions inside of it, which I mean, makes sense that are executable, right? So, this thing can go out and use like XSS search and GitHub search and all these other search functions. You're giving like executable access to these scripts on your machine. Now, in this case, there's like 63 different issues that it found.

**25:37** · And for me, I I mean, I think to be able to read through all of these things and parse that out, it's like, yeah, you could do it, but this is like a ton of stuff. And so, for me, what I did in this case was I pasted all these into Claude and asked it to like describe realistically like based on the design of things like what would the attack situations actually be?

**25:52** · Um number one, they have these things where you need to like paste your cookies in, and that is obviously like a very, very, very risky thing to do because that can give like any attacker realistically that gets access to those things complete control over any of the things that you pasted in, your Twitter sessions, your Reddit sessions, like any of that stuff they can gain access to.

**26:15** · So, number two, uh which I think is probably like seems to be for me like a bigger issue, is that you can just allow remote code execution through unverified install and update scripts. So, in this script file that they have, there's an external install script that you are basically downloading and piping straight into your machine. And that again is a serious, serious issue. And I feel like we've seen enough of these like supply chain compromises recently that even if this person wasn't malicious, that just seems like a very easy way to get yourself completely pwned.

**26:46** · So, that being said, while Seal Specter wasn't like as related to all the other ones, I do think this is like an incredibly valuable thing. And if we were to pop in and see like how much did that actually cost to run? I've done a few of these scans, and I've been using my OpenAI stuff for other things this month. So, that did cost actually about $5 for me to run. I've done other ones on smaller repos, and it cost more like 20 to 30 cents. And so, just for full context, like that is what it cost to do that type of security scan on a like a relatively larger, I guess, project.

**27:17** · There we have it. Five like, I think relatively new repos that I hadn't heard really of any of these. So, I think they're pretty dope. If you found this video helpful, make sure to subscribe, but that's it for this video. I will see you in the next one.