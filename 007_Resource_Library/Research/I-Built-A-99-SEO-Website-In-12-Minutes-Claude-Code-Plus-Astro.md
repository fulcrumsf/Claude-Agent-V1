---
title: "I-Built-A-99-SEO-Website-In-12-Minutes-Claude-Code-Plus-Astro"
type: research
category: app-dev
tags:
  - research
  - case-study
  - web-development
  - seo
created: 2026-06-06
source: 000_Ingest/I Built a 99% SEO Website in 12 Minutes (Claude Code + Astro).md
---
![](https://www.youtube.com/watch?v=78-A8UvGxI8)

I built a complete, SEO-optimized local business website in under 15 minutes using Claude Code, Astro, and Cloudflare — and it scored 98% on PageSpeed Insights.  
  
This isn't bolt.dev or lovable.dev. This is a proper framework-based build that actually ranks...  
  
RESOURCES:  
\- Prompt used : https://docs.google.com/document/d/1acH5YldQPOJ7s9KbkbCj-gwA7S3hgG2npNyZ87qI67Q/edit?usp=sharing  
\- GitHub Repo : https://www.skool.com/ai-ranking/classroom/8e4415ae?md=0718afa0f94a470f9a6c1708ece316f6  
  
  
TIMESTAMPS  
0:00 - Intro: what we're building and why  
0:28 - Why Astro beats every other builder for SEO  
1:35 - The project: rebuilding a real page 2 website  
2:50 - The prompt and Claude Code build process  
5:00 - First look at the finished site  
8:25 - Deploying live to Cloudflare Pages  
10:04 - PageSpeed, GTmetrix and schema results  
11:52 - The full local business builder agent (community bonus)

## Transcript

### Intro: what we're building and why

**0:00** · I'm going to show you how to build websites like this which are almost SEO perfect in a matter of minutes with an extremely professional framework. This website here, as you can see, is loading extremely quickly in GTMetrics in page speed insights. It's got all the technical SEO components done correctly, and I'm just been so impressed by the quality of this. So, I'm going to show you how to build an entire website that is SEO optimized and will rank very well with Astro, Claude Code, and Cloudflare.

### Why Astro beats every other builder for SEO

**0:28** · Astro is the one thing that you probably haven't heard this and this is a new web framework or slightly new website framework for contentdriven websites.

**0:38** · I've been absolutely falling in love with this framework because it is just kind of made for SEO. It's made for a lot of things, speed and whatnot, but the SEO that it kind of generates is fantastic. And because we're giving Claude Code this as a template, then Claude Code doesn't kind of go off the rails and do its own thing. Now, compared to building sites on things like lovable.dev dev and bolt.ai. This is 100 times better. Trust me, I've built websites on all these things. This is by far the best. So, we're choosing Astro because it's an SEO powerhouse.

**1:08** · It's very quick. We're using Claude Code because it's arguably one of the smartest models. You can use Opus or you can use uh Sonnet 4.6, the brand new one. Both will do, which is fine.

**1:17** · Remember, we're not doing rocket science. We're just doing SEO, so both models are more than okay. And we're using Cloudflare. One, because they can give you free hosting, but two because you can also connect this directly from claude code, meaning it'll build this on your computer and it'll publish itself to Cloudflare, which is so good. For this project, I am recreating this website here, which is called Texas Plumbing Solutions. If we go to it, it looks terrible. The reason why I'm recreating this is because, well, the content already exists online, and it's actually on page two of Google.

### The project: rebuilding a real page 2 website

**1:47** · You can see here down to when I'm searching for the keyword plumbers in Texas. So this would be a fantastic way for me to realize well this website clearly need improvement when I build the website and completion. I can see here one of the problems is they don't really have a location uh area serve served. Let's see how quickly this is loading. So let's get straight to it. I'm going to start a brand new folder in my desktop.

**2:11** · I'm going to call it um Texas farmer build YouTube example and then I'm going to open up a new terminal. In that terminal I've got here, let me make this a little bit bigger. I'm going to start claude.

**2:30** · If you don't like using clawed code in the terminal, I highly recommend that you give it a go because it just opens up to so many more opportunities. Now, I haven't installed anything here. I natively have clawed code with access to Nana Banana Pro. I've done a lot of videos about that, but uh I'm going to give it a simple prompt to rebuild the website, but I'm going to be very specific about it. So, I've pasted the URL in there. Now, I've got a prompt here that's essentially telling it what and how it needs to build this particularly with Astro.

### The prompt and Claude Code build process

**2:57** · I've just given it the link to the Astro website uh and said, "Hey, install the requirements and this is also how I want you to build this website."

**3:07** · Now, first it needs to understand all the context of the site that we're rebuilding, which is fine. Then it should start making a plan for this entire build. And this is the unreal thing about this that it's been going for 15 minutes. It still has enough kind of context about it and it's going through all the phases cuz it planned everything. So phase one was the scaffold project. Uh phase two was the all the config files. Phase three is the layout and the core components. Now it's building all the templates and the blog content and then even the images because remember we've given it it access to Nano Banana Pro uh from Google.

**3:39** · So now it's asking me because it's in the instructions if it can run a Python script to turn those images that Nanobanana generated from a PNG to a WEBP file. If you don't know, a web p file is just an image format that keeps everything a lot lighter in terms of image sizes. Doesn't uh impact the quality of the images, but it's just perfect for SEO. You can see perfect. It even says the WEBP compression brought them down massively. Uh yeah. Okay.

**4:08** · I need to approve a couple more things here. And I'm actually going to get it to um because this at the moment is in my desktop. Then we can push it through directly to Cloudflare. But at the moment that I'm going to ask it just to see it locally in my device. And now that it's kind of finished everything, it's even kind of suggesting here. You can see at the bottom run npm uh dev.

**4:31** · And let me see how it looks. I'm just going to press the arrow. And uh I like those instructions that it's given me as a suggestion. Now it should run uh the command npm rundev. If this is a little complicated, do not worry. is just essentially allows you to see your website from your local uh drive as opposed to having to update it into Cloudflare because this allows us then to see what it looks like before we decide to push it live or even to a dev staging site. Okay. And here it is. Uh the first version, right? Our plumbing services.

### First look at the finished site

**5:02** · Uh tiny little animations which is nice. Areas that we service need a plumber. Fantastic. So this already has the service areas, more services than the original page. So if you take a look at this one here, um this looks kind of old. We are the best plumbing solution. Whereas the other one says your trusted uh Bamman plumber for every job. A nice call to action. Call plumbing services.

**5:30** · So if we go to the services area and we go to Belleville for example, plumber in Belleville, Texas, I can call right away. Nice call to action. Services available here.

**5:41** · Fantastic. So, if I go to leak repair, I should go to Yeah, leak repair in Belleville. Fantastic. Uh, this is this is looking a lot better than the other site, right? I can guarantee that it's going to uh rank the other site. If we were to kind of swap the websites here, this would be so much better. Uh, fantastic. It's even has uh let's see if it I can see if it's got the schema or not. Probably structured data. Yeah.

**6:08** · So, it's got the service schema, the breadcrumb schema, the plumber schema, FAQ p section because it does have an FAQ section at the end, I think. Um yeah, perfect. And this just allows us all the content to be very specific for that area and not get done for content duplication. Uh so, this isn't, you know, we could probably work on it a little bit more just here.

**6:32** · Um, like for example, let's see if on the homepage above the areas we service, we can add a a strip of reviews. Right now, all I got to do is ask it here um on the homepage uh just above the areas we service, can we have a strip of reviews uh for this business?

**6:57** · The only thing that we need to do is now what I want to do is upload it into just a devstaging site and do some speed optimization to make sure that the images aren't heavy and it wasn't just uh hallucinating the fact that it made WEBP files. I mean if we have a look at that right away um probably they're not WEBP files or PNG files. Sorry. Old tags. Perfect. So if we Oh, it already Cool. So it added the review strip.

**7:24** · Fantastic. already without us having to do much. Uh I also want to add a uh maybe a how we work section just below our plumbing services. So again, I'm going to go back to the same chat that I've been having with it and saying, can we add a section on how we work just below the our plumbing services section on the homepage? Can we add some images in there or some interactive elements as well just to not make it so boring?

**7:51** · The whole thing here is just to try and add some sort of differentiation between this website and any other competitor's website. And in a matter of minutes, uh, if we go to below, it's added the how we work section, it has a kind of stepby-step guide, give us a call, even an interactive kind of sliding banner there, uh, which looks quite nice. It's using different images here, uh, expert repair, final walk through, like it looks very professional. So, I'm already really liking this site.

**8:22** · Uh, now I want to push it to a uh Cloudflare instance.

### Deploying live to Cloudflare Pages

**8:30** · So, I can leave a link below and you can have actually have a look at the website. So, you know, this isn't just, you know, kind of done on my desktop.

**8:37** · Uh, and that's relatively easy.

**8:41** · Now, I'm going to say, hey, can you please push this to Cloudflare on a staging dev site so I can see it and I can share it with people. Hit enter.

**8:51** · Now, if you haven't already kind of uh installed or connected CloudFlare with um Claude, then it's probably going to ask you to do that. It's very, very simple. I've already got it connected. I just want to show you how this looks like when it's actually live. Now, you can see I'm authenticated with the Cloudflare. Uh it's got right permission. It's successfully created the project. So, that let me actually go on Cloudflare and see the job that it's doing. And already on Cloudflare, I can see that it's got here Texas Plumbing Solutions, which was the project that we started working on.

**9:22** · I'm going to click on this. And Jesus, it looks like it already did that in, yeah, two minutes ago, in a matter of seconds. So, let's check it out.

**9:32** · Cool. And now, as you can see at the top here, it's in a pages.dev staging site.

**9:37** · I'll leave it below so you can have a look at it. Um, which is pretty kind of unreal. The call telephone works, the contact us is a form. Uh, fantastic.

**9:48** · Now, to do the form submission, uh, if you want it free, you could also use resend as well. I'll do a specific, um, whole tutorial about this, but I just wanted to show you how incredible easy it is to create a very, very good website with this stuff. Now, I want to do some SEO tests because, you know, this is what this channel is all about, and I like that stuff. So, I like the overall aesthetic of it. Um, I'm going to see how quickly this thing's loading.

### PageSpeed, GTmetrix and schema results

**10:17** · Um, and I'm going to do two tests here.

**10:19** · I'm going to do GTMetrics and page speed results from Google. And I'm also going to see if it's got the right schema because just because I told it to add the schema, there might be some problems with it. And you see there isn't. So, this has all of the local business schemas. Uh there are some minor non-critical issues but that's fine. Um it's got the correct schema for this which really helps you as well to rank high in the AI search engines.

**10:46** · So the desktop is loading 98% which is blazingly quick. The mobile could use some fixes but it's loading extremely quickly. And GTMetric says this thing is blazingly quick. So, as opposed to something like bolt.dev or lovable.dev or whatever they call these days, this actually is built on a specific system, Astro, which is built for high quality SEO websites. This is why I love this so much.

**11:17** · Um, if you want a more detailed tutorial on then how I would turn this into how I would add blog posts and how I would do more to this, let me know. But now all you got to do is add all your um your tracking components and push it to a real domain that you buy from Cloudflare and that's it. I just built a professional website which I would be very very comfortable selling to absolutely anyone and I know it's going to rank really high uh in what a couple of minutes under 15 minutes which is insane.

### The full local business builder agent (community bonus)

**11:52** · Now, if you want an even more professional and a better way to do this whole thing, I have uh in our community a GitHub repo with an agent with a plug-in essentially that will do all this for you with best practices and whatnot. You can have the prompt that I'll leave link below. I'll leave this inside the community, but essentially it's a local business builder for claude websites that can generate, you know, websites up to 80, 100 pages or more in a matter of minutes with perfect SEO as well. It's got all the installation guides here.

**12:20** · Uh it's got all the parameters that it needs building and it's going to ask you questions as well, the agent. So it's going to be interactive back and forth uh parameter and all the things are there that it needs. I'll leave that in our community.

**12:33** · If you want me to do more videos about this, please let me know. Cheese.