---
title: "Claude Code's Biggest Problem"
type: tutorial
category: ai-agents
tags:
  - tutorial
  - ai-agents
  - claude-code
  - memory
  - productivity
created: 2026-05-01
source: https://www.youtube.com/watch?v=0-AosS67IGU
---
![](https://www.youtube.com/watch?v=0-AosS67IGU)

⚡Master Claude Code, Build Your Agency, Land Your First Client⚡  
https://www.skool.com/chase-ai  
  
🔥FREE community with the prompts🔥  
https://www.skool.com/chase-ai-community  
  
💻 Need custom work? Book a consult 💻  
https://chaseai.io  
  
Frontend design is one of Claude Code's greatest weakness, but this open source repo might be able to solve that.  
  
Impeccable gives Claude Code a proper design vocabulary, and shows it what good design, and bad design, actually looks like. We can also edit our web pages in a live browser, test variants, and quiclly iterate between different design directions.  
  
⏰TIMESTAMPS:  
  
0:00 - Intro  
0:51 - Impeccable  
4:23 - Building From Scratch  
16:11 - Editing Existing Website  
22:11 - Final Verdict  
  
RESOURCES FROM THIS VIDEO:  
➡️ Master Claude Code: https://www.skool.com/chase-ai  
➡️ My Website: https://www.chaseai.io  
➡️ Repo: https://github.com/pbakaus/impeccable  
  
#claudecode #impeccable

## Transcript

### Intro

**0:00** · AI has no taste and it's your fault. The reason your visual outputs are so mediocre is because your prompts are so mediocre. You aren't using the type of terminology, language, and nomenclature that an actual designer would be using.

**0:13** · But luckily for us, I found a solution.

**0:16** · It's called Impeccable, and it's an open-source GitHub repo that for all intents and purposes is a single skill that we can import into Cloud Code that fixes this exact problem. It provides Cloud Code a design language that teaches it what good design actually looks like while also telling it what sort of bad designs to avoid. And today I'm not only going to show you how the skill works, we are going to use it to build a brand new website and to edit one of my websites that already exists.

**0:45** · So by the end of this video, you are going to have no excuse when it comes to creating mediocre front-end designs. So, Impeccable is an open- source GitHub repo that gives us a single skill that allows us to create front-end designs that don't suck. Now, it's a single skill, but that's underplaying it a little bit because this single skill includes 23 different commands. It has seven domain specific reference files.

### Impeccable

**1:10** · It tells us, you know, what sort of anti-atterns to avoid and it even allows us to edit things inside of our browser.

**1:17** · So, this is actually a very robust tool.

**1:20** · This isn't just the front-end design skill that goes on for a few paragraphs about what Claude Code should be doing, but that complexity can be a little overwhelming because there is literally 23 different commands that do a number of different things as it relates to your design. Now, it breaks them all down here inside of the repo, but the truth is you're never going to remember all these, but there's two things that help out here. One, obviously Claude Code's going to do a pretty good job of figuring out which one you should use, but secondly, they have an entire website that also shows us what it is each of these 23 skills do.

**1:51** · So, the GitHub links to the website, which is impeccable.style. And the cool thing is for every single applicable skill, we can see what something looks like before, which is plaincloud code, and what it looks like after using that specific impeccable command. So, pretty neat. Now, Impeccable really has seven pillars of design. Typography, color, spatial design, responsiveness, interactions, motion, and UX writing.

**2:17** · So, it isn't just going for, you know, like colors, and things like that. It's pretty comprehensive. And right here, we can scroll through all of these different commands and like I said, see what they look like using the skill and not using the skill. So, if you're ever like, "Hey, what exactly does this do?

**2:34** · Can I see it in action?" Well, this is the place to do it. The website also includes a case study showing how they created this website with impeccable and a single image and I think it looks pretty cool. And lastly, they show off this live mode which we will play around with a little bit which is an alpha and lets us actually mess with our website via the browser like I talked about earlier. Now it also has a Chrome extension and a CLI but to be honest we get about 99% of the value through the skill. So that's what we'll be focusing on today.

**3:00** · Now to install this thing, it's a single line of code which all you have to do is copy this, go into your terminal and paste it in. Now when it comes to using Impeccable, there's really two paths to go down. One is green field where we are building a website from scratch and two is editing an existing site. Now today we will be doing both of these and more because I'm not only going to show you how to build it from scratch, I will also show you what it looks like when we build from scratch with some sort of reference image with like a mood board, so to speak.

**3:29** · After we do that, we'll then go on to my actual website and we'll see what Impeccable has to think about it and and what sort of sloth stuff we can slay on my own work. Lastly, we'll take a look at Impeccable Live, which is in its alpha, and see how good this thing actually is as it stands today. But before we dive into the actual build, a quick word from everybody's favorite sponsor, me.

**3:52** · So last month I released my cloud code master class and it is the number one way to go from zero to AI dev especially if you don't come from a technical background. I update this course every single week. So it is the best place to figure out how to actually use this wild tool. We focus on real use cases. I just came out with my entire cloud code agentic OS lesson plan. So if you want to get your hands on it, you can find it inside of Chase AI plus.

**4:20** · There is a link to that in the pinned comment. So let's get started and we are going to kick it off with the green field project. So we're going to build a website from scratch. Now again there's so many commands it can get a little bit confusing. If you are starting something from scratch I suggest opening up with Impeccable Craft because it's going to include some of these subsidiary commands like Impeccable Teach. Now what do all these things mean?

### Building From Scratch

**4:44** · Well, impeccable craft pretty much means it's going to go through its own version of plan mode and ask about our website, our product, what it is we're actually trying to build. And in that process, it's going to create two files. It's going to create a product.mmarkdown and a design domarkdown. Now, the design is pretty much the same thing we've seen in Google Stitch. You guys remember Google Stitch, right? Google's free design tool.

**5:12** · You have this whole design system thing and you have this design.md file which is this, you know, very in-depth markdown file telling AI how to build something. This whole design construct is becoming somewhat of an industry standard, so to speak. You're seeing this all over the place these days. And Impeccable follows that approach. So, it's essentially going to interview us and figure out what it is we're building and how do we want it to look. And once it's conducted the interview, it's going to go ahead and build the landing page for us. So, inside of Claude Code, I'm in a new directory called impeccable- test.

**5:41** · The command is impeccable spacecraft, and the prompt is, let's build a landing page for my fake SAS product, Lighthouse. It's an analytics platform for solo founders/s small teams. Ask me any questions you want. This is pretty much the same prompt that I gave Huashu Design in my last video. If you haven't checked that out, definitely do so, which is essentially a claw design clone. So, it'll be interesting to see how impeccable holds up to that design system. And if you haven't checked that video out, I'll I'll link it above.

**6:12** · So, it came back with 13 questions. The first four are all about the product, like who is the actual customer? How would you describe Lighthouse? What's the visitor mindset? And what's the primary CTA? What's the actual point of this landing page? The next few questions are all about the voice and the look before it goes into the scope.

**6:29** · Are we just doing the hero only, full scroll, real screenshots? Like, do you have any other assets for me? And what I like here is the depth of the questions.

**6:36** · This is more questions than what Huashu Design asked us in the last video. And this is pretty close to the amount of questions you would get from something like Claw Design. Like this is very in-depth and I like to see this. So what I'm going to do is I'm just going to fill these out. I'll keep it pretty standard. I'm not going to have it do anything crazy. And we're going to ask for a full scroll. So here's what Impeccable gave us on its very first attempt with pretty minimal guidance.

**6:57** · All we really did was answer its questions. We didn't give it any sort of assets or even examples. Now, right away, I definitely don't think AI slop off the bat when I see this. Although, you are starting to see this like cream color and Sarah font kind of everywhere in these more modern front-end designs, especially stuff like claw design. I do like this dashboard it came up with.

**7:16** · Definitely like this. I do like that I'm not just seeing your standard, you know, four bento boxes that you see in every single AI design website. This part looks pretty good. We have the quote, uh, full pricing, and then kind of like a, hey, go ahead and give us your email.

**7:33** · So, for first pass, pretty good. But what I really like to do as of late when it comes to my web designs with Claude Code is I don't let it just give me a single output like this. So, what I went ahead and told impeccable, aka Claude Code, was I don't want just one layout of the website like you see here. This was the first pass it gave me. I want to see three different variants that I can choose and I want them all to be pretty different. On top of that, I want to be able to click through all them and I want to see them all side by side.

**8:01** · So, I want to see some sort of like macro layouts before we really dive in into the nitty-gritty and start playing with components. And so, Impeccable gave me this. So, we have the editorial one that we just looked at. It created one that it called drenched right here.

**8:17** · Definitely a different style, a lot more color. And then we had the brutalist. So here's a look at the drenched.

**8:24** · Definitely a lot more different. I will say we have some overlap here on the front, but this looks pretty dissimilar from most AI generations. And as we go through, you know, I do kind of like the boldness of this website, although I don't really know the colors. But I will say I do like this brutalist one. Like it's very grayscale, but I like how the numbers are set up. I like kind of how the boxes are kind of like offset, like the lines don't totally match. I actually really like this one.

**8:54** · I think this looks really cool and very different.

**8:59** · And so I think what we're going to do is we're going to go with this one for now.

**9:04** · And just so you know, this whole like triple design thing and seeing it all at once, that isn't something inherent to Impeccable. This is something I do. This is just a single prompt. And I highly suggest you do this no matter what sort of designs or skills you're using. I think this is something I kind of picked up from Stitch because Google Stitch makes it really easy to do this sort of thing where you can see all these different variations on the same page and compare and contrast. And for me personally, I have to see these visual things to have any idea of kind of like where I want to go.

**9:35** · So highly suggest you do this. You don't have to do three.

**9:39** · You could do six. You could do a million. And also when you prompt claude code to do this sort of thing, just tell it, I want to be able to see all three on the same page. I want to be able to open them in full screen one by one. And you can also ask it to give you a bunch of different macro options and then you can just choose from from them and then have it create these cuz obviously it takes a little time to gen these up. So now that we have a landing page we like, now is the time to start editing some stuff which is where the new impeccable live comes in. So all we have to do is say, "Hey, let's run impeccable live on this brutalist page."

**10:09** · Now once you run that command, Claude Code will tell you that live mode is up. It should give you a link to the local host that you need to be on or you can just refresh your browser. And so inside here, you can now see as I kind of like scroll around, stuff is now highlighted. And at the bottom here, we have some stuff as well.

**10:29** · So first of all, we have design.

**10:32** · It pops up this sidebar on the right hand side. And if I hit raw, I can see everything it actually created. Now, if I click on a particular component like this primary copy, we have some options that pop up. First of all, we have free form, which is hey, I kind of just give it a text prompt. Or I have access to essentially all these different impeccable commands. So, bolder, quieter, distill, polish, adapt. These are all are just part of those 23 impeccable commands we were talking about earlier. So, let's say I do something like bolder.

**11:02** · So bolder is essentially a pre-esigned prompt. And if we look here inside the impeccable documentation, what bolder is going to do is it's going to make it bolder. So this is the before. This is the after.

**11:18** · It's just making it almost a bit more flashier. So the exact definition is it pushes safe designs towards impact without sliding into chaos. Says when to use it and how it works and all this stuff. So if we do bolder on this, and to be honest, I feel like this is already pretty bold. I don't know if this is the best one. I can refine that further. So I can do bolder plus whatever prompt I want to do. Let's say I write add color. I then have this thing here that says x 3 x 4\* 2. That's how many variations it's going to show me. And then we hit go.

**11:50** · So this in a way is kind of like a micro version of what we were doing here in terms of variations where I'm like, all right, give me this one thing. Let's change it.

**12:01** · Show me variations.

**12:04** · Now, we're doing this at a micro level, and we can be even more specific in terms of what we're going for, right? In this case, we're doing bolder. We could have picked any one of those like 12 options. And here's what it came up with. So, yeah, very bold compared to the other options. This is variant one.

**12:20** · Variant two, a little more subdued. And then variant three, kind of wild, right?

**12:25** · Also have this ability to tune the variant. So, if I click on tune, right, we can kind of change the offset, for example, of this, like how wild do you want it to look? What do you want the colors to look like? So, again, if we're thinking back to my last video or you're thinking back to claw design, like tweaks, again, this is pretty much like micro tweaks and that applies to all variants. Hide the key, show the key.

**12:51** · So, a lot we can do. Let's say we want to go with this. So, if I want to go with that, what am I going to do? I just have to hit accept and it's now applied. Now, if you hit accept and it bugs out like that, just check in the cloud code, it's basically applying your changes and reloading it.

**13:06** · And here's what it looks like with the changes enacted. Now, the one thing I didn't talk about was detect. So, if I hit detect here, what it's going to look for is essentially it's trying to see is there any AI slop here. Is it detecting any of these anti-atterns we talked about earlier? Now, because this was com created completely with Impeccable, I highly doubt it's going to find anything and that's why we're not seeing anything show up. But we'll see later when we take a look at my own website if that's the case. But that's pretty much how the live system works.

**13:33** · And I think this part is really cool and what sets it apart, I think, from other frontend design skills and repos that you've seen in the past, especially the fact that we can create extra variants. I'm super bullish on being able to see all these different variants at once and and kind of tweak them at this very micro micro micro level. So, I love this. But again, it's alpha, so, you know, maybe you'll run into some errors. There are a little like couple things that seem to be a little rough around the edges like the reload you just saw, but hey, I think this is super cool.

**14:03** · So, definitely check this out if you use Impeccable. Don't just have it create and be done with it.

**14:09** · Go into Live and mess with this. Now, once you get the web page to a place you like, there are more commands you have the ability to run. So, we can run something like polish where it does a final design system pass. We can do something like harden where it's going to take a look at edge cases and errors and make sure everything's working. Like I said, this is very, very sophisticated and pretty deep in terms of the amount of commands we can run. But for the sake of time, what we're going to do now is I'm going to show you how to build from scratch.

**14:35** · But this time, we are going to be using essentially like a mood board or a mockup of the type of vision we want to push to impeccable because I want to see what this looks like when we kind of copy what their case study was because what they did is they took this image, shoved it into cloud code, put it into Impeccable, and like all right, create us this website and they're able to get something that looked pretty awesome. So, I went ahead and created some images that match the aesthetic Impeccable used in their case study, but we're using Lighthouse instead. So, we can at least kind of get a test that is somewhat of a one toone comparison.

**15:07** · So, I kind of like this one, so I think we'll go with this. Just like before, I'm running Impeccable Craft as the skill. It then asked me a similar series of questions as before, and I pretty much told it just stick with sort of the mood and vibe that you got from the image I give you. So, this is what it came up with. And honestly, it leaves a bit to be desired. I think just throwing this sort of like mood board at it and telling it, "Hey, let's create a website from this." It it struggled. Um, I think it did its best.

**15:37** · Like, we still got the dashboard. It has the colors, but it's not as good as what they created because I think since I just gave it that one asset and I didn't include additional assets, it didn't really like chop it up in the same way that Impeccable did with their case study. But, you know, it might be a prompting issue. But even with that, you can kind of see the bones of something that would that would work here. Um, I do like how they do the dashboard.

**16:01** · So, you know, definitely not as impressive, I think, as the raw one we did at the beginning, but hey, I figured I'd try it out. So, now let's see how this does when we edit an existing site. So, we're going to use my website, my actual AI agency website, and we're going to run a few commands on it.

### Editing Existing Website

**16:20** · We'll do the impeccable document so it can actually reverse engineer a design.md file from the code and then we'll do stuff like run the audit and do a critique and we'll actually do the live thing again on my actual website and kind of see um what sort of ads we can make. So for reference this is the website for my AI agency. I have like kind of a standard hero section.

**16:42** · And I go into services, talk about my philosophy for how we do AI implementation before having a sort of call to action, a place where people can fill out their information if they want to work with me. I have some additional pages like my blog, but we will just stick with the homepage for now. So the first thing I did is I said, let's run impeccable document on this codebase and see what impeccable has to say about my current website.

**17:07** · So, it's going through the entire codebase and it's going to create a design.md for what we have already and it's from that foundation that we can begin to edit things. So, after impeccable went through the codebase, it wrote three files that are basically like strategic context for what's going on. It talks about the winds, the north star, but it also talks about seven different violations it found. So, the blue sphere, it says the service card mockups are basically a clip art variety pack.

**17:40** · Um, intentional card grid. It hates glass morphism, so it doesn't like that.

**17:46** · Um, it says we've loaded um a certain font, but we never used it. Um, as well as some other stuff. So, there were some sort of features that are essentially in the code, but actually don't show up in the actual UI. Um, and then some issue with some of the colors. It also talks about the strategic gap of me basically not putting myself the person Chase on the website itself very much at all which is that's fair. Now we can actually get an even deeper critique if we run the critique command. And so let's do that now. So I'm telling it to run the critique command.

**18:17** · Didn't even spell critique correctly. Telling it to run the critique command on the landing page. So it ran its critique and its verdict was it is yes borderline AI slob. It gave me a design health score across 10 different things and each one was out of four and didn't score above three on any of them, but I didn't get any ones, so that's good. Overall was a 25 out of 40, which ranks as acceptable.

**18:43** · For cognitive load, it gives me a five out of eight fail. It says the background motion competes with the content.

**18:51** · Yeah, I think it's kind of subdued, but I see where it's coming from. two equal weight CTAs in here with ambiguous priority. Service section has four different visual schemas along with some other things. And overall impression is that it has good bones, but it could do a bit more. And then at the end, it kind of breaks it down into three different places we could go. So, honestly, I I like this critique. This is very, very in-depth and gives us a lot to work off of and gets pretty specific about what it thinks is wrong.

**19:21** · Now, whether or not I agree with some of it, I think is kind of besides the point, but it gives us things to think about. You know, I'm not just going to blindly assume everything it's telling me is correct, but we can kind of go through these or if I wanted to, I can go through all these like, all right, let's change this and that. So, let's see what happens if we do B and say we want to kind of like play around with what it calls a decoration discipline and see what changes it makes.

**19:46** · And after we see what changes it makes, we'll hop into the live session just like we did with the first landing page we built and mess around with that.

**19:55** · So, let's look at some of the changes it made. And the changes were very subtle.

**19:59** · So, we can see right here in the services section. This is the updated version. They kind of subdued the colors and kept it to just sort of this like terracotta orange and white. You will notice there's no longer like sort of a blue haze on the bottom left. For reference, this is the previous one where you kind of have this blue on the bottom left and then blue and then green. So, it's kind of keeping it just to two colors, right? The kind of white, well, really three colors, I'd say, like white, gray, and then the orange.

**20:28** · You can also see that down here in the approach section. So, as I go over the cards, we still have that orange glow, but on the original, it had, you know, some orange down here. It kind of had the card upline up top and it thinks that's sort of like an AI slop type thing. And that's the extent of the decoration discipline changes. So rather subtle. It has some other ones it wants to try as well that have to do sort of with like trust and conversion and potentially adding things like head shot. But what we'll skip ahead to now is going into the live mode.

**21:00** · So let's take a look at the website now in the live mode. So let's say I wanted to change these cards a bit. And just like before, what would I do? I can do free form or I can go ahead and pick one of these preloaded commands. So, let's try delight for this one. And then we'll go ahead and go for three variants. And what delight does is it adds some actual personality to that particular component. And here's a look at some of the variants it gave us. So, this one's just a little bit bigger.

**21:31** · Has sort of this thing down here on the right. It changes the actual text here.

**21:38** · Adds this little thing as well. And obviously like these we have the tunes to mess with too. Oh, that's supposed to be a number. It's a little off. Um, so yeah, pretty much the exact same scenario as the first website we created. I think this live thing for Impeccable is actually its most powerful tool by far. The fact that we can do these micro adjustments from essentially a graphic interface versus having to do everything in the command line. So, I'm glad to see that it's pretty much the same exact setup even when we're using a codebase that already exists.

**22:10** · So, overall, I really liked Impeccable. I think it is 100% a skill you should add to your stack and definitely test out when you're doing your next round of front end design, whether it's for a website you're creating from scratch or for something that already exists and 100% try out the live tool. This is something they just added, I think about a week ago, and I think it's a big differentiator from all these other things.

### Final Verdict

**22:35** · I think when you combine these micro adjustments with sort of the macro layouts that I told you to do via prompting at the beginning, I think you have a really powerful workflow. As always, let me know what you thought.

**22:47** · The link to this repo will be down in the description. There's also the link in the pin comment to Chase AI Plus if you want to get your hands on my Cloud Code Masterass. And besides that, I'll see you