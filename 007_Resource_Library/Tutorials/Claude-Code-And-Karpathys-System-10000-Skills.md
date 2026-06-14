---
title: "Claude Code and Karpathys System 10000 Skills"
type: tutorial
category: ai-agents
tags:
  - tutorial
  - ai-agents
  - claude-code
  - skills
  - memory
created: 2026-05-01
source: https://www.youtube.com/watch?v=pCqpuHA8kHM
---
![](https://www.youtube.com/watch?v=pCqpuHA8kHM)

## Transcript

### Intro

**0:00** · Skills are Cl code's most important feature, but 99% of people are using them incorrectly. Using Andre Kapathy's system, I found a new way to build these super skills that are self-improving, have infinite memory on the kinds of things that clients pay me thousands of dollars for. And in this video, I'll show you exactly how to build them for any output, so you can stop wasting your time, make more money, and unlock Claude Code's full powers, even if you've never done this before. And if you don't know who I am, my name is Jack Roberts.

**0:29** · I built and sold my last tech startup with tons of customers and now I build AI startups and show you exactly the stuff that works. So if you haven't already, grab that beautiful coffee and let's dive straight in. So let's talk about how we use Claude Code and Carpathy system to make skills that are worth thousands and thousands of dollars and will drive those cool things for your business. So first thing to understand about skills that most people get wrong is that skills are like superpowers.

**0:56** · when so does super strength, flight, and laser vision. These are the things that we're going to use most of the time in our business to accelerate everything forward. But here's the difference is that most people are just using basic MD files and they're not configuring them properly. And that essentially means imagine having Superman that couldn't fly, couldn't use laser vision or any of these things. It wouldn't really be worth doing. And the bad part is most people don't realize this has happened.

**1:20** · And this brings on to the concept of something called super skills. Now, super skills themselves basically have three things in common. And what that effectively means is that every conversation is indexed and recallable.

**1:30** · And Claude wakes up smarter every session. So, say for example, you have a YouTube intro skill and you give it feedback, but then the next time you open it back up, it just forgets everything you said. That would be a really bad skill. So, we wanted to have this memory it can come back and use.

**1:45** · It's going to use actual tools that are specific for the job. And crucially, it's self-improving. It scores its own output and it improves over time. So every time you use a skill, it gets way better. An example of that, for example, would be something like this signal dashboard here that improves time after time after time. And we're going to build something similar to this in this video. I'll show you exactly how you set this up. And I'm also going to show you how you get your own memory operating system that looks something like this that connects everything from your long-term memory, short-term memory, uh, skills, and everything.

**2:14** · So you get a sense of what that actually physically looks like. So when I'm talking about super skills, what I'm effectively meaning now, there are two types of skills that we're going to use in Claude code. One is going to be what I call the utility skill. So that's going to be something that's really easy and dead straight. Now there are two types of skills that we're going to be using within Claude. Again, this can work in any model. One is going to be what I call the utility skill. So that's going to be something that's really easy and dead straightforward. It be something like my bitly skill, right? My Bitly skill, for example, just takes URL and shorten it. I could say something like, "Hey there. Um, just create a URL, a shortened URL for glido.com."

### Super skills

**2:46** · All right, I give it a link and it just goes ahead and shorten for me. Utility skills are very wrong, very, very easy to get correct. It's very difficult to get them wrong. They're dead simple. There you go. It's now used my bitly skill. I can click this for example. I open it up and then I see Glad the speech to text service that I'm using to kick butt with this. And then we have super skills that are built on Karpathy's foundation, his mental models for basically the four big things holding you back with models. It leverages data. It improves itself and it's just significantly helpful for driving your business forward.

**3:18** · We call these super skills. There's the stuff that actually works and that's what I'm going to show you exactly how to build inside this video. So when you're thinking of super skills, it's stuff that listens, it remembers, and it improves over time and it's actually set up correctly cuz most people don't get that correct. Okay? It could be stuff like an insight a outlier analysis, sponsorship, replying, anything that you can think of. Now, here's the reason why most skills don't work. And when we understand that, we know exactly how to improve skills that actually do. First of all, they're just markdown files.

**3:46** · Most people I see, they just download markdown files and they never use them again or they don't work properly. And they're generic. For example, a skill that might help me with my YouTube is going to be so completely different than yours cuz it doesn't have that strategic context. It's like a business adviser trying to give you help and advice, but doesn't know what the hell he's talking about. lay out. This guy needs some coffee. He's not thinking clearly. The static, in other words, the second you make it, it's exactly the same as it is like a thousand times later. Businesses evolve. Your needs change. It needs to reflect those dynamic changes to it properly. And again, it just forgets everything every time you use a skill.

**4:18** · It's the exact same thing again and again. And if you're wondering who Andre Kopathy is, he's a guy that if you ever want to feel bad about your CV, just look at what this guy has done. All right. So, he co-founded Open AI. Yeah.

**4:29** · Okay. We'll we'll take it. Ran Tesla AI.

**4:32** · done lots of really cool stuff and he basically started the tweet that authored part of the reason why I wanted to make this video with this brand new system. So he basically posted on a his philosophy and mental models around the big four limitations with models that affect everything that we do whether we're coding with it or in this case using skills that can quietly hold you back. This was then very kindly turned into a skill that got over 88 8,000 uh stars on GitHub and is part of the foundation and one of the components of what makes these super skills.

**5:01** · So just to explain the TLDDR what it is um it's essentially instructing it's a very simple markdown file but explains to models that you need to think before you code. Okay, keep it simple again don't overengineer code surgical trenches only touch what you must trace every line and goal driven execution. The idea is these are four guiding principles to drastically improve the quality of outputs because these are the four big limitations essentially and this is something you can use for skills anything else. Now to get access to this all you're going to do is shoot over to this GitHub repo right here. You're going to come over to code.

**5:31** · You're going to click on copy GitHub repo just being fancy word of saying where we keep all our files. Then you're going to open up anti-gravity or claude code. Cool. So I'm in the CL code section. I'm going to say hey there go ahead and install this repo for me. Okay. Then you're going to come down and you're going to drop in the GitHub repo. And all it's going to do is literally install it into your environment. Explaining what it is is dead simple. Again, it's just four principles. Think before coding.

### Karpathy's foundation

**5:53** · And that tries to attack things like wrong assumptions, hidden confusion, missing trade-offs, simplicity first, don't over complicate things, no bloated abstractions, orthogonal edits, touching code that you shouldn't. In other words, if I want to change the color, I don't need you to change anything else on the page apart from my specific ask. And again, leverage through test first verifiable success data. Now, the beauty of this is the fact that it is very short. That's it. It doesn't need to be overly complicated. That's why this is so cool. Beautiful. So, I've just created a brand new folder called memory OS. So, I can show this looks like.

**6:23** · Now, if you click on the little thing at the top here, uh, and you're going to come down here to files, which is one of the coolest things that Claude just added is the ability to see your own files. I click on files. I've got all my files here. I'm going to come down and click on memory OS. Going to come down, click on claude.md. And once I've got that, you can see now that you can actually check what the claw.md is. Think before coding. Simplicity first, surgical changes, goal- driven execution. Then whenever you give a prompt, it will then follow these for you basically meaning that it will apply in anything that you're building. All right, so real talk for a second.

**6:54** · How many of you have got several skills that kind of sort of do the same thing? Or you like me and you have a graveyard of like a thousand skills that you never touch? They sound good on paper. I mean, everything looks good on paper. Fish and chips looks great on paper, but it doesn't mean it can run a business. When I built it this way, I don't build skills any other way than the way I'm going to show you with this super skill methodology that's actually built on these carpathy principles. And there are four legs to it. Just like chairs can't step up with three legs or maybe they can, I don't know. If you take one away, the whole thing falls apart.

**7:24** · So the first one is that we want to create the skills properly in tier one. The idea of this is that if we don't write the skills properly with the requirements, it's never going to achieve what we actually need to do. And so what this means is that we're going to stop writing skills by hand and use the actual proper way of doing that. And so you're going to show over to Claude and going to give it the following prompt. Hey there, I would like for you to create for me a skill.

**7:45** · Use your skill creator skill in Claude and my stated intention and outcome of this is now at that point you want to go ahead and basically explain what it is that you want. So for example, if we are building here my uh signal dashboard here, which basically is something that I get on a daily basis that gets information from all of these sources, Anthropic, OpenAI, Y Combinator, Google.

**8:07** · It's like my agentic morning brief. Now, everyone talks about, hey, you should create a morning brief. Fair enough.

**8:13** · This is completely different than this.

**8:15** · This takes it to a completely new level.

**8:17** · It's interactive. It's self-refining.

**8:19** · And I perfect it over time. It's something that actually drives actions and decisions. So, if I want a signal dashboard, I'd come over and I would say this, right? I'd say, I would like a signal dashboard. The idea of this is to drive my content strategy. I want to understand signal from the noise. I want to know about things that happen before anybody else does. I want you to assess sentimentality and trending signals and understand different news sources. What I would like this to do is understand the best places to get that information.

### Level 1: Creation

**8:48** · And then you go on and on and on. Then you'd basically come down and explain the tools that you want to use. She'd say something like, "Have a think about first of all clarifying your understanding about everything that I want from this skill. Then we're going to have a conversation about all the different tools and data sources that we're going to use to create this skill.

**9:05** · And then once you've got that, you're going to assign what it looks like. And then you want to be specific about the format." So you just say, "Hey, I want this to be in a beautiful HTML format."

**9:13** · Then once you've done this, essentially what happens here is this will then go ahead and create a skill. Now, the cool thing about using anthropic skill generator is it tests its performance against anthropic by itself, which is really wonderful. And we know then that it's actually going to be better than if we just ask claw to do it itself. And once you've given it that prompt, you'll get these questions to say topical scope. Um, what does early mean to you?

**9:34** · Output shape, cadence, signals that you care about, sentiment, death, memory, and action layer. So, I would encourage you to go back and forth with Claude about this specific thing so you can get really detailed on the skill. Now bear most people just download skills and press play. This actor gets a completely different level of depth and it's worth architecting this initially because that will mean that the full strength of the skill is going to work for you. And everybody's skill should be different if it's a super skill like this.

**10:00** · Now having the blueprint is incredible but if we don't give it the correct tools it's like having you know a Ferrari and trying to drive it on hopes and dreams.

**10:09** · Hopes and dreams are wonderful but they won't drive our car anywhere. So, what we need to do is give it the correct tools. But this is the big problem that a lot of people have with these tools is you're essentially limited by your imagination because there are different levels of data. And I'm going to show you how to get so much data you won't know what on earth to do with it. But your AI will and it will make his skill super epic. So, the idea here is that skills need eyes. Okay? And what we're going to do now is basically connect Claude with all these data sources.

**10:34** · So, if I come back over to Claude now, for example, there are three levels that I follow when I'm trying to get Claude the correct information. The first thing that I've done is defined what I would call priority one resources. So for instance, if I'm looking at data for things that are breaking, one of the questions I might be asking on my signal dashboard here is what is the most important information? And you can even ask, you can say, "Hey there, if I'm trying to get the correct insights and data, what would you consider to be examples of primary data sources, the best places to get this information?"

**11:07** · And then Claude will literally give you that as insights. Now, why is that important? Because whatever skill that you're building, sometimes some manipulation or scraping of data is going to be important. Maybe you only need one connection. That is completely fine. But I can tell you right now that for a lot of the really interesting ones, you're going to want to grab and access data from somewhere on the internet. And just like that, it's come back and look at the degree of information. We've got tier 0, tier one, tier 2, tier three. Now, here's the sequence that I always think about connectors. The first thing you do is come down to the plus sign. Okay? Click on connectors.

**11:38** · Then click on manage connectors. Here we can add in everything that we want to. Your first question should always be have they do they got a connector to that as the queens of English would wonderfully say.

**11:49** · You're going to click on browse connectors. And here you can just type in stuff like Gmail. Awesome. Maybe you're doing a skill that leverages your you know you want to look at your pipeline your pipeline um you know deals. Well we can just use Gmail for that. Awesome. Maybe we got Figma. We want to leverage Figma. We first of all look to see if it exists within there.

**12:06** · You even got Spotify. you know you can create you can now listen to your terrible music via code now some say it's terrible some say Jack you got the best music taste on the planet now the one that we're going to use here is firecrawl this one is better now the reason why I really love firecraw for this is mainly because it saves on token cost when you're doing that and websites are optimized for humans they're not optimized for AI so I personally use fire crawl you don't have to use it but I use it because I find it easier to do that to do this one you just come on add custom connector and basically you type in fc crawl here all right and then your remote mc TP server URL.

### Level 2: Data

**12:36** · You enter in this here and in brackets you just get your basically you get your API key from firecrolot there. And then all you're going to do guys is just literally copy this and you see it says fire crawl MCP API key. You just replace that with whatever you have on your dashboard here and effectively that will work for you.

**12:53** · And so once you've got that you add that as a custom connector and then literally you click down here it's all fully authenticated and you can use it. For example, I might say something like, "Hey there, I want you to use my firecrawl connector to go onto product hunt and get me some interesting insights on three speechtoext AIs." And then just I want you to pull up for me a nice little beautiful HTML overview, make it super quick. All right. And then Claude will literally go ahead and do that for us cuz it can go deeper and deeper on the website. So the question then becomes, well, if I can't find a connector here, how do I get it?

**13:23** · Well, one way around this is using a tool like Zapia. I used Zapia when I built my first business. was super duper cool.

**13:30** · And what we're going to do is think of it as a um kind of like a universal um remote control in the sense that if you can't c if you cannot find it on Claude, you can use a tool like Zapia. You don't have to use it, but it's cool if you want to find those additional ones that you don't have access to. So, what you're going to do is come down and click on other real quick. And then you're going to see something that looks a little bit like this. And you got all the tools that you want. What you're going to do is pick the tool that you like. Say for example, us want to be able to connect to school. We just type in school and we click there, which is cool. So basically Zaka is the bridge that connects us to everything else.

**13:59** · So here I can invite members, I can lock courses just as a for instance connect this one together. Then once that's done, you're going to come down here and click on connect like so. And then you're going to have your own custom URL and you click on generate to basically build that one out. And then you're going to copy that. Come back over to Claude. Now to add that MCP connector, you're going to click on the plus at the top. Click on add custom connector at the top. Type in Zapia and then literally paste that MCP server URL.

**14:25** · Then what this means is that we've given Claude the tools to access data from any resources that we need to even if they're not directly integrated within Claude. Now the big issue with Claude is that sometimes it has amnesia and it can reliably forget things and not only that it isn't just about what can it remember it's the ability to store those memories, show you those visually in a gorgeous and interactive dashboard and then be able to use those memories to actually improve the output.

**14:51** · And this is a system that I see extremely few people using and yet it is unbelievably powerful. Now the chances are that you've seen different ideas of these memory systems, right? Or what I call here the memory operating system which is actually skill that you can download.

**15:06** · So if you head over to the school community, I'll put a link for this down below for you so you can grab this uh completely for free. All you're going to do is come down here and you're going to click on what I call the memory system OS. You're going to open this bad boy up and you're going to see something that looks like this. Come over here, click on this, click on download, and then you can literally head over to Claude and then within Claude, you can add this as a skill. You can even say to Claude, "Hey, go to the last thing I downloaded and add this for me as a skill." Now, why do this? And let me just show you one interesting thing as well that I think is really important to understand here. So, you may have seen obsidian rag and you've seen pine cone wrap.

**15:38** · So, let me explain to you the three different levels of memory we've got here and exactly how we're going to use this within our system. Okay. So, for example, there's three things to understand. Number one is we have what I call bucket one which is the memory.

**15:50** · Okay, this is every single conversation you've had with Claude. Okay, append only wrap-up skill session. So the idea here is that let's say that you have a big long conversation with Claude about the strategy for your business or it could be uh what you're planning to do this year. What we can do within Claude now is if I come back over here, I have this really cool skill called the wrap-up skill which I do for/ wrap-up

**16:12** · and you can see here what this will do is it will capture the whole conversation and store it in long-term memory which means that when I'm having conversations I have this infinite archive of anything that I've saved and it's selective too. So it will be based on the conversations I think are important. That is bucket one which is wrapping up and storing conversations from within Cycllo to our long-term memory. Okay. The second one here is we got lot is knowledge. This is foundational stuff. So for example, if I show you an the dashboard that I built for my community in awe withjack.com.

### Level 3: Memory system

**16:40** · If I come over here to YouTube chat, this has every video I've ever done. Has every single school post, everything from my community. That is my long-term memory. Maybe you want to chat to Homozybot, right? You want to find out stuff about his books. Well, every book he's written, all this sort of stuff underpins and underlines all this information. I call this thing here your long-term memory. This is immutable stuff that never changes. So, this could be strategists that you respect, um, YouTube videos, content creators, whatever it is, there are long-term memories.

**17:12** · So, if I'm talking about hooks, for example, and I want to know what the best hooks are, I have knowledge and databases from those guys.

**17:18** · And then, interestingly, we have the third bucket here, which is profile. So, this is stuff that you're working on right now. Current strategy, focus, decisions. Now, the interesting thing is that buckets one and two sit in long-term memory, okay, pine cam, but bucket three doesn't because this actually changes over time. This is what we're working on right now. It's our current strategy, our focus, our decisions. It's one markdown file. It is mutable and Claude can read it every session. So, what this means is when you do this, you'll actually be able to open up this dashboard using the skill.

**17:49** · And I thought this would be really cool cuz the big problem that we have now with memory is that you can't actually see what Claude's view is on your strategic awareness. So what I've done here is got this basically for/strategy awareness that you get with the skill. There's actually three commands. One is wrap-up which basically wraps everything up. The second one is recall again which lets you call any of the knowledge from your databases. And finally strategy awareness. Now obviously if you're using natural language it will do these anyway but you've got the command set if you want to. And effectively what this does is gives us a visual overview of our memory and our current strategy.

**18:20** · So it's a it's the visual overview of what you're currently working on, right? How many sessions you've had, your memories, it shows you customer insights, it could be subscriber growth, activity heat map, how much you're adding to it.

**18:32** · Effectively, this will build out based on everything you're talking about. So you can add and remove different pieces of insights and knowledge from this database. So I can look at, hey, here's all the things that it's working on and adapt it accordingly, which is excellent. And just one of the reasons why I prefer pine cone over obsidian is I know it's not the popular opinion.

**18:50** · Obsidian does work. By the way, of course, both these things work. I'm not here to tell you which one you should or shouldn't use. Personally speaking, I do opt for Pine Cone in this system because it is easier and it actually works very well with it. And just to give you a bit of an overview so you can make your own informed decision on it. Um, setup is like a couple of commands. It's a vector search. Now, when you're using Obsidian, it's really good if it's like less files. But the problem is the longer the file is, the more tokens that you burn every single time you use it because you have an index file.

**19:20** · Without going into details, I've done a full video link on screen to show you how cool it is. But basically, your token burns as you go.

**19:26** · With Pine Cone, it's extremely extremely scalable. So, for this memory system, I find it really easy to use it. But if you want to use Obsidian, that's completely your preference. You can absolutely do that with this system, too. Then what this effectively means is that when I pull together my signal dashboard or whatever your skill is, we're now consulting long-term memory.

**19:44** · So maybe you've got experts on, I don't know, how cool blue phone cases are, well, we're going to call that knowledge and we also have knowledge of your current strategy, which we can now view and amend in our memory operating system, which effectively means any skill you've got. Again, it could be the creation of content, whatever the thing is, we're leveraging your knowledge base across three different levels in this entire system. So we again, we're creating the skill properly. We've got the data and connectors and then we've got persistence either in Obsidian or Pine Code based on your actual preferences.

### Level 4: Self-improvement

**20:12** · And this is really cool for me especially with skills that you're producing things like this because I've often found that if it lacks your current awareness of what you're actually working on, it just it just forgets really basic things. But actually giving it this long-term memory, the strategic short-term memory really sharpens up its actual execution.

**20:30** · Now, I just got back from LA and it made me think like imagine jumping on a plane with somebody that's only flown once or done it in a simulator. You and I would probably grab our coffees and freaking sprint back to the airport. And it's kind of the same way with skills that are really important. The biggest mistake I see is people use a skill and then they never give it feedback. And the skill itself never improves over time and all the value sits when you get these improvement cycles. And that's why this fourth pillar here is what I call the refinement loop. The idea is that the skill runs itself.

**20:58** · You grade it, you give it feedback, the model actually looks at it and improves it within its own code. So effectively what this school system will do is let's say that you do produce something that looks like this, not the memory OS, but maybe you produce this signal dashboard and you're like, dude, I really like it, but I think that you know this short list isn't very good or you're giving me too many ideas like XYZ. Go ahead and improve that skill. So not only do we have context, it's been written properly. It doesn't only have data, it has all the memory systems, but you can improve it over time. And that is where all of the value actually sits.

**21:29** · And so essentially what happens is you can literally see as you give it the feedback it will literally update the core information in the file in the skill. So every time you run in the future it just gets better and better for you. This sits across four tiers and obviously if you want to go deeper I've actually pulled together a full claude code course. It goes through foundation setup builder website um power features memory systems claude bots apps build anything design systems compliance maintenance and turning that into cash.

**21:57** · I'm releasing it this month inside the community. So, you can click the link down below and check that one out if you want to. Wanted to mention it because it's one of the biggest questions I get and this is going to be so powerful. I can't it's just it's going to be incredible. So, you can check that one out if you'd like to. And again, we're leveraging carpathy as a foundation. By using these principles in the skill itself. So, it isn't just in the coding.

**22:17** · When we're actually building and executing the skill, we have these things woven into the fabric of how it's operating. And now we know how to build these skills. Watch this video right here to learn five epic skills.