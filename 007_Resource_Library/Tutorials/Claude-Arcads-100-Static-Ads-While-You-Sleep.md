---
title: "Claude + Arcads = 100 Static Ads While You Sleep"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=5RGmaT1ZVww)

🎬 Try Arcads: https://arcads.ai/?via=crudy  
  
⚡ Learn to automate your ad workflow with AI agents. Join One Prompt Club: https://www.skool.com/one-prompt-club/about  
  
🔗 Work with my team directly: https://adacted.com  
  
📁 FREE PROMPTS: https://adacted.notion.site/Arcads-Workflows-Prompts-36dc78bb1ad580869a71dd92a0837d88  
  
Static ads are still the highest ROI format on Meta, and most brands are still using them wrong. In this video I show the exact system I built with Claude and Arcads that generates 100+ on-brand static ad variations from a single product image.  
  
The workflow:  
\- Claude as the strategist (brand research, angles, prompts for both 1x1 and 9x16)  
\- Arcads as the visual engine (node-based workflows, GPT Image 2, automatic variation)  
\- One-click generation across multiple aspect ratios  
\- Webhook support so you can plug it into your agent stack or trigger it from a launch sheet  
  
CONNECT WITH ME  
X: https://x.com/chrisrudy

## Transcript

**0:00** · When you look at the top brands out there, it's easy to see that static ads are still the highest ROI format on Meta. Simple graphics are driving hundreds of thousands in sales every day. The problem is most brands still don't understand how to use AI \[music\] to make them. I speak to tens of business owners every week and this is what I see. People are struggling with low visual quality and boring flat \[music\] ad copy, which obviously results in not getting good results on Meta. The good news is that if you use the right tools, it's actually really easy to start making good statics \[music\] right away.

**0:30** · Arcads recently introduced their workflows, which is basically like an ad engine for AI visuals and it's changing how people build their creative processes. I built a system with Claude and Arcads that generates over 100 plus static ad variations from just a single product image, completely tailored to your brands and ready to go inside that account. And in this video, I'll break everything down for you step by step.

**0:52** · So, keep watching if you don't want to get left behind. Let's get started. So, for this process, we're going to be using Claude as the main strategist.

**1:00** · Keep in mind, you can also use the same prompt that I'm going to give you in a moment with other LLMs in the future.

**1:06** · So, this process isn't really tied to specific model per se. So, I'm going to be giving you this strategist prompt that you can just paste into your Claude to get the prompts needed for the statics. You'll see the result in a moment. It's really mind-blowing. So, what you do is you come in here, you can just copy the prompt from here, and we're going to go to Claude. What I really recommend is that you set up a project. It's just going to be easier to find your materials in the future and your learnings. So, we're going to click on new project here and we're going to call it YouTube project and create.

**1:38** · And so, in the future, all the chats will keep appearing here and you can also start adding any context. Main thing with these prompts, as usual, is that you want to play around with them. So, of course, the existing one is already going to work really well, but you can start making tweaks to it and personalize it more to your own product and brand. So, what we have here are some fields that you need to fill out now. So, for the products we're going to use an example, we're going to use Grooms.

**2:09** · So, let's go to their website and I'll just select the first one. So, what we have here is what your product is, what it does, the website, so the LM can then go to your website and pull the branding, colors, all the important information and also come up with the angles. So, for the product I'm just going to take the product name here. I'm going to drop it in here. For the what it does section, I'm just going to copy this here. And you could either write it yourself or if you have it on your website, even better. And now I'm going to drop in the URL.

**2:42** · And for the target audience, I'm just going to ask lot to pick for itself. So, pick ourself based on what you think is the best option. And that's literally it. Now we just get the prompt going and it will start doing the research and the strategy. So, Claude has now finished with the research prompt. Let's check it out. So, it has the colors, brand tone, aesthetic, and it has come up with top five visual angles for us.

**3:07** · And you know, if you don't like these, you can also just ask it to come up with more visual angles and apply your own knowledge that maybe you know some specific angles that work. And now it has the ready-made prompts for us here. And a cool thing to do with your prompts in general is if you want AI to go a bit further and you know, really improve its outputs, I really suggest implementing this scoring system.

**3:34** · And you can do the same for your ads copy as well or if you're building a landing page, you can ask your AI to analyze your assets based on a score system and also kind of give an explanation of why it thinks the score is what it is. So, we have the prompts here and we're going to jump to the next step now. So, now we're going to come to our cats and we're going to click on new workflow up here.

**3:56** · So, what this does is it opens up the node-based workflows, which is basically like N8N but made specifically for creatives and they've added all of their powerful options inside this view. For example, you can generate images, you can even generate videos, you can have AI edit your videos, you can have an LLM there, you can enhance a prompt. And so the options are really incredible. They also have their video editing tools that you can just put inside the chain.

**4:24** · And most importantly, when your workflow is ready, you can even link it up with a webhook. So, for example, if if you have the webhook, you can then add it into your automations. So, for example, if you work with a new client or if you have a new product launch, you can link it up in your other automations or even have your agent trigger it and it will run through the creative workflow that we're going to build here. So, first thing we're going to put our product image in here.

**4:52** · So, we right click and click on uploads and I'm going to just drag this one product image in here and that's going to be enough. So, you're going to see the outputs are going to be really powerful and we literally don't need anything else. And we're also going to add some information about the brand and you'll see in a moment why we do this. So, I'm just going to add this in here and we're going to come to the notion board.

**5:17** · I'm going to copy the context prompt from here and we're just going to fill it out with the brand information. So, we'll put the URL in here and product name in here. And now we're going to build another prompt that Claude generated for us. So, I have this here. First, we'll add the context header. And this is something that you can later just copy-paste from node to node to save time. And then we're going to come to Claude. I'm just going to select the prompt here, the first one that we generated.

**5:48** · I'm going to click on copy, and we're going to drop it here.

**5:52** · And so, what this does now is it uses the LLM from our cards to enhance the prompt even further to make it even more branded to your specific brand colors and aesthetics. So, now we're going to add the LLM chain. This is what makes it all work. We're going to start connecting things. So, we're going to connect our cloth prompt, and we're going to connect the brand information.

**6:17** · And finally, we're also going to connect the image here. Now, most of it is ready. We're just going to add the image generation model in here. So, I'm going to click on image, and under settings, we're going to want to choose GPT image two. This is the best one at the moment, and we're going to select aspect ratio 1 by 1, and we're going to connect this output here, and we're also going to drag the product image here. And now, what makes this workflow extremely powerful is that we can also make the 9 by 16 version inside the same workflow.

**6:53** · So, we're going to add another image generation box here, and do the same motions. We're going to check We're going to select GPT image two. We're going to keep the aspect ratio at 9 by 16 now, and we're going to come here, and we're going to paste the 9 by 16 prompt. So, we're going to add the prompt in here. This will make the generation into 9 by 16, so you can have the full asset package ready for you.

**7:19** · So, we're just going to link these images here, and the workflow is ready.

**7:24** · So, I'm going to build this out for all five prompts now, and I'll be here with you in a moment.

**7:31** · \[music\] So, now we have all of the cloth generator prompts ready, and now it's time for action. So, we're going to run it. We're going to click the button here, and we're going to click here on generate. And we have the generations ready. So, let's check them out. Wow. This looks really, really good. And everything is on brand, as you can see. There are some cool creative elements in here that make it more interesting.

**7:59** · There's a lot of motion here happening, plus the benefits, features, everything that we need. And it has even picked up some statistics from the website. And as you can see, we have the 9 by 16 versions as well. And there's a lot of creative variety here as well, different sceneries. Now, if we wanted to improve on this, we would just go back to Claude, and we would ask Claude to change certain things, or maybe to introduce or focus them more on certain visuals, or, you know, talk more about a certain benefit that we want to show.

**8:35** · And so, as you saw, I just built this out in like 2 minutes, and we have five completely ready to go statics that we can then go and put into our testing A B O, or if you're using C B O testing, you can put them in there and see which ones get spent. And once you have the winner, you can also take that information um to Claude, ask Claude to generate more variations based on those winning ads, and then go through the same process here. Now, what I recommend is to treat these more like collectible packs.

**9:06** · So, for example, I have a pack of five here right now. I wouldn't delete any of this. I would just start a new workflow, and then in the future, you'll also have your own inspiration board that you can then either recreate for other brands, or you can take ideas from here. If If you just wanted to extend this process, you could add video generation option in here. You could add a video generation option in here. I would select length 3.0, and you could add your static as the start frame.

**9:38** · So, you would then have video version of the same static as well in one generation. And so, I hope you can kind of start seeing how powerful and visual a flow like this can be.

**9:52** · Which like if you're working inside Claude code or key or vowel, any of those generation tools, the main thing that they're often lacking is this visual interaction. And when you're working with creatives, you want to see things visually to be able to, you know, iterate on them properly. So, just to recap this workflow. So, it takes your cost per static ad down to less than a dollar.

**10:18** · It really depends on, you know, how many times you regenerate, but compared with a typical designer, you know, who might charge 50 to 100 bucks per static or even more, this is almost nothing. Turnaround time was like 2 minutes to generate all of these. You can generate as many variations as you like. And because of the LLM in the loop system, it's always consistent to your brand. And because of Claude's, you basically have an infinite format variety as well.

**10:49** · A cool trick that you can do is also you can take an example ad and give it to Claude and ask it to make similar variations around that one.

**10:59** · That's a way you can get more. And of course, like with revision rounds, you can also have unlimited revisions inside this tool. So, if you like this video, please feel free to support me by trying out Arcade's with my link. And if you have any questions about this workflow or if you have any other ideas that you would like to see in the future, I would be happy to help you out down in the comments below. Thank you so much for watching and I'll see you soon. Bye.