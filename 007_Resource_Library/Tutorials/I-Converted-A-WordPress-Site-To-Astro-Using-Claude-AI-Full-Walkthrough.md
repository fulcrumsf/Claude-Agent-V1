---
title: "I-Converted-A-WordPress-Site-To-Astro-Using-Claude-AI-Full-Walkthrough"
type: tutorial
category: video-production
tags:
  - tutorial
  - how-to
  - claude-code
  - web-development
  - video-production
created: 2026-06-06
source: 000_Ingest/I Converted a WordPress Site to Astro Using Claude AI (Full Walkthrough).md
---
![](https://www.youtube.com/watch?v=QdgfS41Tr3I)

WordPress works. But it's slow, bloated, and you're paying for hosting you don't always need. In this video I take a real WordPress website and rebuild it in Astro — and I use Claude AI to do most of the heavy lifting.  
This isn't a tutorial about whether you should migrate. It's a real walkthrough of how it actually gets done, including the parts that don't go perfectly.  
What you'll see:  
  
How I approach pulling apart an existing WordPress site  
Using Claude to generate Astro components from real WordPress pages  
Handling layouts, navigation, and content structure  
What Claude gets right (and where you still need to step in)  
The final result — a faster, cleaner, static site  
  
If you're a developer or agency owner thinking about moving clients away from WordPress, this one's worth watching.  
Who this is for:  
  
Web developers tired of WordPress overhead  
Freelancers looking to modernise their stack  
Anyone curious how AI fits into a real dev workflow — not a demo, an actual build  
  
🔔 Subscribe if you want more honest takes on web development, AI tools, and running a small digital agency.  
Tools used: Astro, Claude AI, VS Code

## Transcript

**0:05** · Hey everyone. Today we are what are we going to do? We're going to look at taking an existing site. We're on our mission to rid the world of WordPress.

**0:17** · Not really. WordPress is fine. I've got most of my site still sitting on WordPress. So, it's fine. Nothing wrong with it. It's just old and slow and takes a lot of work to get things where they need to be, unfortunately, and there's security issues obviously with it. So, I don't want to do that anymore. I'm sick of it. I did an initial video before about why I'm swinging over and thanks to AI, this is kind of what we're doing now, right?

**0:47** · I want to offer something really good for my clients that they don't have to worry about.

**0:57** · they just leave it to me.

**1:00** · Do the whole lot for them.

**1:03** · So, what we're going to do today, this is a this is a fun one. We're going to take an existing site, which is really simple. It was done yonsks ago, like a decade ago maybe, and I just need to recreate it. I'm going to let Claude Code kind of do the bulk of the decision- making when it comes to design. We're going to go with Astro.

**1:25** · We're going to go uh don't need a CMS plugin, so that's fine. But we're going to essentially rebuild the site. See how quickly we can do it. Okay, so this is our site.

**1:40** · This was done a long time ago, so please don't please don't get angry. There's actually some broken links in here.

**1:49** · Yikes. Okay, not my proudest moment. Anyway, we are going to take this and make it something special. So, we'll see. You'll be able to see with me how Claude can sort that out, right? I think it's it's the way of the future whether people like it or not.

**2:08** · And if you look at it, if we like brand it in another way or phrase it in another way before the internet, we were very much like a closed relatively closed society. Like if you wanted to order something, you really had to rely on what was around you, right? The um your location. It was location specific.

**2:39** · Then the internet kind of came along.

**2:40** · E-commerce came along and it opened up you know not just our towns but also in cities but you know nationwide and it opened up you know worldwide. We can now order from Amazon and it's amazing.

**2:54** · So that's what it's like. That's how big this jump is to AI.

**3:01** · And we don't know where it's going to go. I don't know where it's going to go.

**3:04** · Nobody knows. But I do know that it's not going away.

**3:10** · So that's my thoughts on it. You need to start playing with this stuff now. So if you're any kind of knowledge worker, you need to get your hands dirty. Okay.

**3:21** · New session there. Get rid of that.

**3:24** · Okay. And if you don't know, the only way to work with LLMs is to talk to the bloody things.

**3:32** · So, I've got Super Whisper here, and that's how I like to talk to these things because my brain works that way. It feels like I'm I work here in my office, and I feel like it is working with somebody and I can collaborate with people in a way that we haven't been able to do before.

**3:52** · Now, I understand in an office that's going to make you a little bit crazy.

**3:56** · So, you know, um work with that as you as you feel comfortable. If you if you're in a closed office, you can probably go to town. But if you're in an open office and you got other people around, you're going to bug them really quickly. So maybe try it at home first.

**4:11** · So what we're going to do here, we're going to I'm going to launch Super Whisper. Give it the prompt. It will type it out and I'll show you kind of how I work with it. So the first thing I need to do is get Astro set up. I've got the local um the uh local repo ready to go. All plugged in. So, let's go. Hey, Claude.

**4:34** · Um, can you please set up a Astro and Tailwind local development in this folder, please? So, what I want to do is give Claude the URL and say, "Hey, this is the company.

**4:53** · I'm going to need you to create a new design based on this."

**4:59** · and see what it can come up with. Okay, so it hasn't kicked it off. So we can run this command npm space run space dev and it's going to kick that off for us and it's going to give us a local host.

**5:13** · Okay, so going to go back over here.

**5:17** · So this is it's Astro's installed. Okay, so that's fantastic. It's what we want.

**5:22** · So now we need to tell it what we need and we're going to give it the the existing site and let's just go with it.

**5:40** · Hey Claude, um I need to create recreate this existing WordPress site. So, there's only four pages to the site, but I want you to utilize the clawed front-end design skill to come up with something that looks stylish, looks modern, and will based on what the existing colors are will kind of blend in nicely.

**6:12** · Let's start off with the homepage first.

**6:15** · So utilize that. But you can kind of get of an idea what these guys do is a spigot making company. So they they handle the the spigots. They sell spigots and and and custom spigots for uh glass ballastrating.

**6:36** · So that wasn't a great prompt. Anyway, let's see what it can kick off with. Because the nice thing about having this environment is that once you start once you start you can start adjusting things. Okay.

**6:53** · So you do have to give it give it access to be able to go on the internet. That's what all it's doing. It's just fetching the page and the layout and the information that's on there and then it's going to fire up do its thing. Okay. So, while that's doing its thing, there's been lots and lots of videos online about the future of web development.

**7:19** · Wow, that's that's a that's a heavy heavy topic. Um, and still needs to be around because that's where all the information is coming from. These LLMs need it. They still need all this information and they need to know about you and about your company and about what your services are. So, that's not going anywhere.

**7:38** · What is different is how we build these things. So I for years and for a couple of decades I was happy to either do you know something like square Squarespace at the very beginning or web flow and utilize kind of page builders like that.

**7:56** · I went over to uh WordPress and started using Elementor and then I went from Elementor over to bricks and then bricks more recently over to Etch which is Etch is a really amazing program and uh Kevin's doing amazing stuff and the team are doing extraordinary stuff over there and it's not that far removed from what we're doing here really.

**8:19** · Uh the difference is the is WordPress and I think till the team can get it shifted over to something else which I think is only a matter of time. I think that's probably a time to take another look at it. I'm keeping my eye on it and it's very exciting and very interesting.

**8:40** · Anyway, we'll see how that plays out. But in the last month, not even maybe month, I started playing around around with with Claude and to see what was out there. And this is cool. This is energized me again for web development, web design, and what functionality and cool stuff that we can build that I can help clients work out and build for them.

**9:12** · So, you know, that's that's cool. That's really cool. I love that. Love that idea.

**9:19** · And it's getting people into the tech side, which I guess some of them may never have thought about it.

**9:27** · They might have had a great idea and went, "Oh, gez, it'd be good if we we did this." And you know on that I'm seg I'm jumping around here but on that thought is the people that are knowledge experts in a certain field or industry they aren't going to have to look for another job because they've got the knowledge that that industry still needs.

**9:55** · Okay.

**9:57** · This is its first pass.

**10:04** · Uh, so the nice thing about Claude is that it gives you a bit of a rundown of what it did when it's a a large chunk.

**10:32** · It's told us about the fonts. It's told us about the pages as well.

**10:41** · Okay.

**10:47** · I mean, look, come on.

**10:52** · So if we go products let's see. So it hasn't actually created any other it's created pages but no content on it.

**10:58** · Okay. So it has taken this which is dog and created this which is now needs uh needs some adjusting obviously and we've got you know we've got the pages here.

**11:27** · Don't know about this line down the middle, you know, but that's just a that's an easy fix you know um like out of the box like really um I'm going to say I'm going to see.

**11:44** · Let's see. Hey Claude, that looks amazing. Can we please grab the logo from the existing site and bring it in please?

**11:58** · it do its thing. It's now it's going to ask me again for permission here.

**12:06** · Fetching. Fetching. Looking.

**12:14** · It's just going to ask if that's okay.

**12:16** · It's going to download that, import it, and it's as it saves, it does a rebuild, and we're going to see it in in a moment. Momentarily. There we go.

**12:34** · Okay. So, there's problems like it's not there. Um, okay. What do we got here?

**12:45** · Okay, it's still going. Just chill. Just relax.

**12:52** · It's coalesing.

**12:58** · Okay.

**13:03** · Let's do hard refresh on that. No. Okay.

**13:06** · I'm going to say um copy that. Just a screenshot.

**13:15** · normally can help claw it out.

**13:18** · Okay, I can't see it. There's a bit of a screenshot for you to have a look.

**13:24** · So, this is, you know, as a developer, you would hit walls all the time and there we go. You'd hit walls all the time and you would then need to do something in order to to, you know, get a logo change or SVG or anything, you know, something.

**13:47** · There'd be some you're always constantly hitting walls.

**13:51** · AI is the wall puncher barrier. It smashes those walls, you know, which is cool. Um, I'm not sure about the accent color.

**14:08** · Look, it's not horrible.

**14:12** · Okay. Um, all right. So, let's move on. So, thanks Claude. Um, can we please go ahead with the about page?

**14:32** · If you find what's on the existing site, let's let's go with that for now. I don't want lots of content. Just just just um you know, some images or something. Just expand a little bit on what's currently there.

**14:49** · Sometimes you forget what, you know, Claude makes you all nervous. All right, so we're going to put that in there. Let it do its thing. Um, Claude's done its thing. Let's have a bit of a look.

**15:06** · Okay.

**15:10** · So, that doesn't look right.

**15:15** · Doesn't look great.

**15:21** · Claude's been a bad boy. All right.

**15:26** · If we just give it a picture.

**15:32** · Hey, that's a good start. Uh, we've got some major issues with spacing with padding. I've attached a screenshot. Can you just have a look at that for me, please?

**15:47** · Poor Claude. He's got a lot to do.

**15:50** · And it tells you I can see the issues.

**15:52** · Hero section needs more bottom padding.

**15:53** · Text is too close. story section stat text is going to come. It knows. Okay, it knows. Don't be mean to Claude, but it's going to go and it's going to find the issues that it needs to fix and it's going to fix those things. Damn it.

**16:12** · Okay, let's have a bit of a squiz here.

**16:14** · Oh wow. Okay.

**16:17** · Um I don't really know what it's doing here.

**16:25** · That's all right.

**16:27** · Couple of product images.

**16:29** · Okay, let's go.

**16:33** · Let's keep going. We're going to go products. Let's go here.

**16:44** · Okay, let's go with our products page.

**16:47** · This is just a big grid of the options available. And we don't need a single product. So literally everything's on this grid. So can you import all those images and all the content and work some magic?

**17:05** · You don't have to be a toss. It'll work it out. It's cool. Um now you'll see here it's using uh it's telling you how much context it's it's being used. So the way it works is all LLMs have a context window and Gemini I think has the biggest at the moment.

**17:30** · Yes, let's do that. Um has the biggest and basically think of it like a memory.

**17:37** · Okay, as you start talking about a conversation, that's the memory that it's holding. Okay, doesn't mean it can't look up other spots and get help, but when you're having a conversation and it's doing a lot of code, it's doing all that in one context, one session, one chat session. So, it's showing you kind of it's it's 53% used and once it hits 100% it will compact it and then just keep going. Does it all automatically. It's cool.

**18:08** · Okay, so it's working out the product page.

**18:12** · It's building it out.

**18:14** · Now, you know, depending on your skill as a say developer or or web designer, there are ways to make different components and things on the site. So, there's a there's a proper web best practice to how to these sites should be set up. I'm not doing this in this video. We're literally seeing how quickly we can go from one to one, you know, from WordPress over to Astro and just get it done quickly.

**18:50** · Okay. So, I would typically have a lot more work with it a lot more to get make sure that as you know it's a client site as lots of updates happen to a site you want to make sure that it's using proper components and and the layouts and collections and everything else. So, we're not doing that right now, but this is just a bit of an exercise. I've got a heap of sites that I need shifted over from WordPress, and I don't want to do that stuff by hand. So, I just want to see what I can do with it.

**19:20** · And I've got a lot of these types of sites that just need to be shifted.

**19:26** · Okay, so we will see.

**19:31** · Okay, she's done. Let's have a look here.

**19:35** · Refresh.

**19:43** · Well, we've we've even got filters. Get out far out.

**19:54** · Okay. So, I don't know where it got that information from.

**20:02** · Let's have a look here.

**20:05** · Let's inspect that. It can make up Don't worry. The Rio SBP-P.

**20:16** · That's that one.

**20:20** · Okay.

**20:22** · Far out.

**20:24** · That's amazing. Need a bit of padding fixing up there. Okay.

**20:29** · Um, let's just do that. We'll copy that over.

**20:35** · Looks great. Can we just fix up this padding here uh below the filters, please?

**20:45** · But like seriously, yeah, there's no point having a plus. We that doesn't there's no cart or anything.

**20:59** · That's good. And then at the bottom of that grid, we also need some padding as well, please.

**21:10** · It's clotting. It's doing its thing.

**21:21** · Okay. Did it actually do that? No, it didn't. Okay.

**21:29** · Stop it. Stop it.

**21:33** · You missed it. Here's a screenshot.

**21:43** · Come on, Claude. You can do it, buddy.

**21:54** · Come on.

**22:06** · Nope.

**22:13** · Copy that. Let's go here.

**22:17** · Still not showing.

**22:21** · All right. You got to be gentle with Claude sometimes.

**22:34** · Okay.

**22:39** · So, we're going to Sometimes you need to be clear because the Claude is gaslighting you.

**22:56** · And we're going to do that, right, Claude? Okay.

**23:00** · Copy that. And we're going to say, see the highlight at the bottom of the product grid.

**23:17** · Come on. Come on, Claude.

**23:23** · Hey, bravo. Nice work, Claude. Fantastic. Um, okay. Let's You got it. All right. Can we please remove that little plus button um on the cards? Product cards. We don't need it. There's no cart.

**23:50** · Now, as it's building um here, it's actually building those components out.

**23:58** · That's cool. Already doing that.

**24:04** · Cool. Okay, that's done. All right.

**24:08** · Okay. So, we're done there. Now, we're going to go to FAQs.

**24:18** · That's that's fantastic. Um, let's move on to the FAQs. Can you pull the existing FAQs down on the site that's there and do your thing?

**24:31** · So, how this would work um, from a client's perspective, they don't want to do this. Okay? No, no one wants to do this unless it's what you do.

**24:41** · So, you need to have another way for them to update. And that's why WordPress was so good, right?

**24:48** · Is it gave business owners and, you know, people that that were running page builders and and whatnot a chance to edit what they saw on the site when they wanted to. So, this isn't really for that. You know, I you would never let a customer come in here and do this and nor would they want to, right? They wouldn't want to do that. So, this is really for how quickly you can build things.

**25:16** · Now, the nice thing about offloading this sort of stuff is it enables and this is for every this is every industry that will use AI.

**25:29** · Okay, let me let me be clear here.

**25:33** · Every industry that uses AI and user of AI need to understand that this will free up your time so you can offer a better service, a better product, whatever that is, doesn't matter.

**25:53** · But that's the point is if you're just kind of doing the same thing that you were doing before and going, "Oh, cool.

**26:01** · I can get rid of staff and I can go and sit on the beach all day.

**26:06** · I don't think those types of businesses will continue to exist because everyone else that's using it correctly, which is the way I think is you offload the stuff that sucks, which enables you to have the time to be a better better with your clients or customers to offer, you know, to improve with what products you offer, what service you offer.

**26:34** · That's that's the whole point.

**26:38** · That's what I think. All right. Where are we going? Where are we going for?

**26:43** · That's not it.

**26:45** · All right. Okay.

**26:49** · All right. So, we've got some Got something happening pages. Okay.

**27:07** · Thank you. Um, something odd is happening with the accordians for the FAQs. There's a button there to expand, but it isn't hooked up. Can you take a look at that, please?

**27:21** · So, let it do its thing. Now, obviously, you need to know what you what you're asking for, otherwise it doesn't understand. You know, pictures are good because sometimes they can just see it straight away, but you need to kind of know what you're doing.

**27:40** · All right, it's fixed. Let's have a look if it's fixed.

**27:45** · See, not really.

**27:58** · Just give it a refresh to make sure that I'm not telling him he's wrong or her. Sorry.

**28:05** · Um, okay. Copy that.

**28:08** · Put that in there. Uh, no, it's not been updated. Can you please have a look at the screenshot that I sent and we're going to need some more padding or see if you can fix the accordion functionality first before we worry about the layout.

**28:26** · Okay.

**28:28** · If you if you worked If you worked with a developer like this, they would punch you in the face.

**28:36** · They would leave and never come back, you know. So, this is Yeah, that's dear.

**28:53** · All right. hell are we doing?

**29:03** · It's still doing its thing.

**29:12** · It's shimmying. I love that.

**29:16** · Love a good shimmy.

**29:25** · Okay. There we go. All right.

**29:29** · So, it's doing its thing.

**29:41** · That's working now. Uh, can we get some spacing, a bit of padding between the number and the question?

**29:50** · And on the right hand side you'll see there's uh where the where the toggle is for the drop down that is really hard up against that. So I think we just need some padding all around.

**30:03** · And can we also uh align the number to the question as well?

**30:15** · Do we say pleased Claude?

**30:19** · Sometimes most of the time you got to be nice to those people that are going to conquer.

**30:26** · All right.

**30:31** · So, you can kind of see here in real time what it's doing, how it's changing the code, which is cool. I like that.

**30:40** · Okay. It still needs a bit of bit more padding, I think.

**30:48** · Okay, those uh toggles still need some padding. They're right on the line there. Can you give it some padding, please? Breathing space.

**30:56** · All right, now you can see here we're at 98% used of this context window. So, at some point, it's going to freak out.

**31:04** · Now, the nice thing about Claude is that it's as in the project when you're using VS Code, it's going to keep all of that together. So, it kind of knows what it's been doing.

**31:18** · Okay, Claude, what are you doing, mate? That's not right.

**31:27** · Okay.

**31:31** · Okay. Copy. That's going I'm referring to the padding just below this toggle which is that square box. Um that's right on the line. I need some spacing between both of those. Um below the box and below the toggle and then above the toggle for the next line. I need some spacing there.

**31:54** · Also, can you make sure all those questions are left aligned for text alignment?

**32:06** · Okay, you can do it maybe.

**32:15** · So, it's kind of telling you what it's thinking, right? So, I need to increase the vertical P. It's saying toggle box is sitting right on the border line because PY8 on the button gives padding, but the toggle but box itself has no margin from the border. need to increase the vertical padding on each FAQ item so the toggle has room above and below.

**32:37** · Okay.

**32:42** · All right. We're getting closer.

**32:48** · Okay. And we're going to grab that too.

**32:56** · Left align this these line the text for the headings, please.

**33:08** · Sometimes you got to ask. Now, here we go. Compacting. So, it's got it takes a little while. Takes a couple of minutes to compact that um discussion we've had.

**33:19** · But it once it's finished, it just keeps going, keeps on going.

**33:26** · All right, let's see if we can fix up our little text alignment issue. Ah, you know, that's cool. Now, obviously, we want to have schema on these.

**33:48** · So, we can get our good friend Claude to do the same thing.

**33:53** · Let's just finish off the contact us page. So, if you grab the Let's close that thing.

**34:08** · Perfect. Can we just finish off the last page? That's the contact us page.

**34:16** · Oh, got to give it the link. Got to give it the link.

**34:27** · Look, all in all, we've probably got an hour all up, you know, including setting this up. We need to connect the form. We need to upload it to to Cloudflare to GitHub and then Cloudflare where we're going to put it.

**34:43** · But that's pretty quick to turn these things around.

**34:49** · Now, would a non experienced person, just a lay person, be able to make those changes? Probably not. I mean, you can certainly talk to Claude and try and finangle something, but don't doesn't have that experience, right, to kind of make calls on certain things.

**35:13** · Now, this is incredible though what what we can kind of generate and it's like I said, it's going to open up our time to do more work, to help more people, and to in the end have a better product. And I think that's what the goal should be. You know, the goal should be that.

**35:41** · So, I won't go over in this video, but I'll I'll show you how it looks on mobile because it handles all of that. It does it out of the box really. There's no issues. Content still, your content game still needs to be on point. Has to be.

**35:57** · Otherwise, it doesn't matter how good things look because they're not going to intrigue people or convince people. And now we've obviously got our the AI side and LLMs to deal with Google's AI search results.

**36:15** · So lot more work needs to happen now obviously with this this how how it works as well. You know we got products here that don't really go anywhere but you know next step we push it up to GitHub put it up on our hosting and we're kind of there. um you know sorting out the form.

**36:37** · You do need to have um some form stuff sort out sorted out rather.

**36:45** · But wow, that's cool.

**36:51** · Um I've got my next month sorted out of work, you know, just to get all of these up and running. And interesting times, you know, we've got updates coming out for these models each week just about and they're fighting and they're they're they're trying to get our money. I think, and I'll do a video on this, that the one to watch out for, ironically, is going to be Apple.

**37:22** · The reason why is they're they want to keep as much of the LLM stuff on the phone or device and they're doing amazing stuff when it comes to their PCs and laptops.

**37:44** · So, I think it's just a matter of time before we stop relying on external LLMs and we start to create our own. you know, phones will have a a a clamp down version, but our Macs will have everything that's just as capable as what we're using now. Especially when it comes to stuff like this to code, it's it's very straightforward and there's lots and lots of examples of it everywhere.

**38:13** · Anyway, that's cool. That's what's kind of exciting me um changing totally pivoting me to a place where I never thought I'd be.

**38:22** · But if you aren't using it, definitely give it a go. You know, whether it's Claude or or Gemini, um Codeex, which is from our friends at Chat GPT, OpenAI, give them a go and see what you think.

**38:37** · It's pretty cool stuff and I'm excited to be develop developing again.

**38:44** · It's going to be cool.

**38:46** · Catch you next