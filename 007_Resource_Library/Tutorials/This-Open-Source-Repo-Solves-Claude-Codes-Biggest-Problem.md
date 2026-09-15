---
title: "This Open Source Repo Solves Claude Code's Biggest Problem"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=aTPTUYC44ds)

⚡Master Claude Code, Build Your Agency, Land Your First Client⚡  
https://www.skool.com/chase-ai  
  
🔥FREE community🔥  
https://www.skool.com/chase-ai-community  
  
💻 Need custom work? Book a consult 💻  
https://chaseai.io  
  
Your custom Claude Code Agentic OS can be yours in just three simple steps.  
  
In this video I breakdown how to setup the architecture, memory, and observability pieces of your Claude Code Agentic OS, giving you the ability to push your Claude Code efficiency to the limit.  
  
⏰TIMESTAMPS:  
  
0:00 - Ponytail  
2:16 - How it Works  
4:24 - Benchmarks  
9:11 - Final Thoughts  
  
RESOURCES FROM THIS VIDEO:  
➡️ Master Claude Code: https://www.skool.com/chase-ai  
➡️ My Website: https://www.chaseai.io  
➡️ Ponytail: https://github.com/DietrichGebert/ponytail  
  
#claudecode

## Transcript

### Ponytail

**0:00** · Can a single skill make claude code wildly more efficient? Can it make claude code faster, cheaper, and write less code while still giving us the same sort of highle results we're used to?

**0:10** · Well, that is exactly what Ponytail is claiming to be able to do, and it's caused it to hit 40,000 stars only 7 days after its release. Now, Ponytail is not the first tool that we have seen claim to do something like this. We've talked about Caveman in the past, and all of these tools tend to have the same idea. The idea is that claude code is naturally verbose and if we tell it, hey, stop talking so much, we can get a much more concise answer that is ultimately just as correct or like we remember with caveman might even be more correct.

**0:39** · Ponytail is simply the latest version of it, but it's a version that's claiming numbers that are better than anything we've seen in the past. And we can see those numbers right here. We can see lines of code versus tokens versus cost and versus time. And across the board, gray being sort of the baseline with none of these tools and green being ponytail. Ponytail pretty much leads the pack everywhere or gets pretty close.

**1:03** · Now, the numbers you've seen here are aggregates. This is the average taken across a number of different tests. And this is also done using Haiku 4.5. And don't worry, later we're going to a validate these tests and b take a look at a real model because none of us are using Haiku 4.5 really. We're using Opus 4.8. So, let's see what those numbers look like. And when it comes to lines of code, it's about 50% less lines. And we're looking in terms of tokens, cost, and time about 22 30% improvements versus the baseline.

**1:30** · And that's no small amount, especially when we extrapolate this to something like Fable, which is wildly expensive. So, if I could tell you, hey, if you using something like Fable, it's going to be faster and cheaper, well, we would love that, wouldn't we? Now, before I go into how this works and showing you what the benchmark scores looked like when I tested it, a quick word from today's sponsor, me. So, inside of Chase AI Plus, I have my Claude Code Masterass, which is the number one way to go from zero to AI dev, especially if you don't come from a technical background.

**1:57** · I update this every single week, and it also includes master classes on codecs and how to build your own agentic OS.

**2:06** · You can find a link to it in the pinned comment. And again, I update this every single week, and we focus on real use cases. So, if you want to begin to master cloud code, this is the place for you. So, how does ponytail work? Well, it goes through this six-step process before it writes code. So, the first question is, does this even need to exist? If the answer is no, well, then we just don't write code for it at all.

### How it Works

**2:28** · Relatively obvious. After that, we ask, does the standard library do it? If the answer is yes, we're going to use the standard library. The big thing that you're going to see with the benchmarks is there are instances where Claude Code will recreate features from scratch that already exist either within some sort of library or as a platform feature. So Claude Code has the problem where hey the wheel's already been built. We have the wheel here in this program and it's like you know what I'm going to build a wheel from scratch. And because of that that's how you get lots of code when you don't necessarily need it.

**3:00** · That's something you see over and over again in these benchmarks. And to step away for a second, these six steps all are pretty much asking Claude code like, "Hey, does this feature already exist natively? Do we need to create some something custom?" Because Claude likes to create custom things even if it doesn't have to. So if the standard library doesn't do it, then it's saying, "Hey, is this a native platform feature? Is this an installed dependency? Can this be one line? Do we need to be verbose?" And if it gets through all that and it's essentially like, "No, no, no, no, no."

**3:31** · Then we're saying whatever you write, just do the minimum that works. Don't go over the top. Don't create it if we don't need it. And if we do need it, do the bare minimum. So the idea here is to make cloud code lazy but not negligent.

**3:44** · Anything that has to do with trust boundary validations, data loss handling, security, and accessibility are never on the chopping block. So it's kind of smart about what it applies this process to. Now, in terms of install, relatively straightforward. You're just going to copy this command right here.

**3:57** · And I'll put a link down in the description for this repo, obviously.

**4:00** · And this is going to install it for you.

**4:01** · And you can also use this for codecs or really any AI agent out there. There's a few commands when it comes to ponytail, namely light, full, ultra, and off. I get very reminiscent to caveman, like the levels of caveman we're going for.

**4:14** · We can have it review our code. We can have it audit a repo. And then we also have the debt, gain, and help skills.

**4:20** · Again, you can really drill down to these if you want to inside the GitHub repo. But none of this really matters if the benchmarks don't hold up. And the nice thing about this repo is they give us the benchmarks. We can run this for ourselves. And guess what? That's exactly what I did. You can do this yourself, too. There is a full write up on how they got the benchmarks right here on the readme. And it also gives you the ability to reproduce these. And so, what I'm going to show you is the numbers I got when I reproduced all of these benchmarks.

### Benchmarks

**4:47** · And I reproduced them not only with Haiku 4.5, which is what you see in the repo, but also did it with Opus 4.8 8 because again none of us are using Haiku. I don't really care about Haiku. I care about Opus. And the results were honestly pretty interesting. So here's the tests and here's the scores. You see their published numbers. You see our run with Haiku and then over here on the far right is our run with Opus. At the bottom you have the aggregate. So the 54% this is again looking at lines of code. It is 54% less lines of code according to ponytail.

**5:20** · When we ran it, it was 56% on Haiku. So essentially the exact same. And on Opus, it was 71%. So we saw even greater gains or more efficient code using Ponytail when using Opus. Why is that? Because these more powerful models kind of like to talk, right? They like to be verbose. Again, kind of a call back to caveman.

**5:42** · You'll remember one of the studies that is talked about in there is this whole idea that very verbose models like to talk a lot. and to the point that sometimes they talk themselves out of the right answer. So kind of interesting and actually like it's sort of a boost to this thing and it's interest and they talk about why they used haiku in the testing and it was for costs. I really think they should have done this whole thing with opus because when we ran it opus actually makes it look better you know and this is the model people are using.

**6:10** · So if anything they sort of undersold its efficiency in regards to lines of code and this also applies to costs. When we looked at Haiku 4.5, what was the aggregate on our tests? We saw about a 25% reduction in the cost versus Opus 4.8, a 53% reduction, which is wild. 53% less it's costing us. Imagine this was Fable. And you can see all the tests and the numbers across the board.

**6:36** · And the lowest one was 13% and in some cases it was high as 73%. For a multi-step wizard. Now, you might be like, do we even need Opus for some of these? Fair point, but just understand what's being sort of illustrated here.

**6:48** · What would it cost at a $139 normally using standard opus without the skill instead cost us 38 using ponytail? And if we look at haiku, these smaller models in some instances actually ended up costing more using ponytail. So this whole idea of cutting down the lines of code and making it more effective is way better when we're talking about more powerful models. In some cases, we have an opposite effect with the smaller models because they were already going to be efficient because they're kind of just like dumb and quick. You can see here in the count items benchmark.

**7:19** · It was 21% more expensive to use ponytail with haiku. Now, we're talking about a difference of 2 cents. But still, point remains, the stronger the model, the more effective this architecture is. And I would love to see what this looks like using Fable. Again, 53% is no joke. And what about speed? Again, we're seeing the same thing play out with Haiku. How much faster was it? About 31% more 31% quicker to use Haiku with ponytail versus not with Opus. 71% faster.

**7:55** · 71% faster. And again, what do we see with Haiku? There are instances, three in fact, where it was slower using Ponytail. you know in some cases 22% slower versus every single benchmark across the board on Opus up to 88% in some instances it was always faster right again we see multi-step wizard 78% date picker 88% and in the worst scenario was a 27% difference

**8:22** · so we look at these numbers with ponytail and we're like uh taken with a grain of salt even though I can do the benchmarks like what really is 20% and then you're like oh it's ha too. So, this is kind of BS. Then, we test on Opus and it's wildly different. It's wildly more effective. And I think the obvious question becomes like, well, what about the benchmarks themselves?

**8:41** · Like, how effective are these benchmarks? Are they realistic? First of all, go to the repo, test these out for yourself or run your own benchmarks that you think fit the bill for what you deem legitimate. Either way, I think when we're talking about, I think the 19 different benchmarks it ran, we're starting to see the same thing across the board. When we look at a more powerful model like Opus, I mean, honestly, I kind of like ignore these for Haiku. I don't care about Haiku.

**9:06** · It's cheaper, it's faster, and therefore it's more efficient. And again, since we're talking about what is essentially just a skill, what's the downside for trying this out? These numbers look really good. I highly suggest you go to this repo, download, and start using it yourself. In the worst case scenario, let's say for your particular project, it's so complicated that telling it to be, you know, less verbose actually sort of backfires. Well, I mean, I think it's kind of like a no harm, no foul scenario, right? So, that's the worst case.

### Final Thoughts

**9:36** · The best case is you're saving like 50%.

**9:41** · Oopus usage and it's 70% faster. So, really interesting stuff. I'm definitely going to be using this in my day-to-day.

**9:47** · I've been using Caveman for like a month or two now for all the time just automatically loaded and I'm going to be switching over to Ponytail and see how I like it. Um I think the more stuff that comes out like this the better. Alls you hear about these days is token cost token to cost token cost. So anything that can lower that for us is going to be wellreceived. So that's where I'm going to end this video. As always make sure to check out Chase AI Plus if you want to get your hands on my Cloud Code Masterass. Let me know what you think in the comments and I'll see you