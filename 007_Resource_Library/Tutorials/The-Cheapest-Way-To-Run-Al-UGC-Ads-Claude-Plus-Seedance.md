---
title: "The-Cheapest-Way-To-Run-Al-UGC-Ads-Claude-Plus-Seedance"
type: tutorial
category: video-production
tags:
  - tutorial
  - how-to
  - claude-code
  - seedance
  - ugc
created: 2026-06-06
source: 000_Ingest/The CHEAPEST way to run Al UGC Ads (Claude +Seedance).md
---
![](https://www.youtube.com/watch?v=M1NsJHcX9rY)

Get up to 75% off Seedance 2 API — use code SAVE25 at checkout: https://app.enhancor.ai/api-dashboard or https://app.enhancor.ai/video-generator for in-app generations. Same price.  
  
API AVAILABLE ONLY IN THE $45/m plan.  
  
Get the free UGC Ads Pipeline and start building today: https://github.com/sirioberati/Seedance-2.0-AI-UGC  
  
In this video I build a complete AI UGC ad testing pipeline using Claude and the Seedance 2 API from scratch. I show you how to access Seedance 2 at 45% off inside Enhancor.ai (0.155$ per second at 720p) with full human face upload support, 720p resolution, and unlimited concurrency — and how to stack code SAVE25 on top for up to 75% off total. Then I walk through a free GitHub project I spent three weeks building that lets you generate, AB test, and organize entire UGC ad campaigns directly inside Claude with no subscriptions, no UI clicking, and no complicated setup.  
  
You will learn⤵️  
  
1\. How to access Seedance 2 API at 45% off inside Enhancor.ai and stack code SAVE25 for up to 75% off total  
2\. How to set up the Seedance 2 API inside Claude using just a text file and the documentation  
3\. What a payload is and why you need to review it before every generation  
4\. How to download and run the free UGC Ads Pipeline GitHub project inside Claude  
5\. How to build a brand profile that Claude saves and reuses across every single generation  
6\. How to upload product images, subject photos, and audio references through the control center  
7\. How to generate 8 ad variations across 4 formats including UGC, podcast, lifestyle, and green screen  
8\. How Claude polls the API automatically and downloads completed videos without you touching anything  
9\. How to iterate, add new formats, and keep generating without resetting context  
10\. How to verify every generation independently in your Enhancer API dashboard  
  
Tools and workflows in this tutorial⤵️  
Seedance 2 inside Enhancor (45% off): https://app.enhancor.ai/video-generator  
Seedance 2 API Dashboard (use code SAVE25 for up to 75% off): https://app.enhancor.ai/api-dashboard  
Free UGC Pipeline on GitHub: https://github.com/sirioberati/Seedance-2.0-AI-UGC  
  
Free resources⤵️  
PublicAI Community: https://www.skool.com/publicai  
Free Seedance 2 Prompt Engineering Guide: https://seedance-prompt-guide.sirioberati.com  
Seedance 2 Resource Hub: https://seedance.sirioberati.com  
AI UGC ads: https://ugc.sirioberati.com  
Wan Animate: https://docs.comfy.org/tutorials/video/wan/wan2\_2  
Camera Control Guide for Kling: https://camera.sirioberati.com  
Guide to Fix Fake AI Voice: https://influencer.sirioberati.com  
FREE Nano Banana Light Presets: https://presets.sirioberati.com  
Build landing pages with Claude: https://design.sirioberati.com  
  
  
Connect with me on:  
https://instagram.com/heysirio  
https://instagram.com/saysirio  
  
Chapters  
Theory  
00:00 – 00:53 Intro: What We're Building and Why  
00:53 – 01:36 The Real Problem With Seedance 2 API Pricing  
01:36 – 02:34 Why This Tutorial Is Different  
02:34 – 03:20 What You Need and How to Think About This  
Practice  
03:20 – 04:32 Step 1: Creating Your Project Folder and API Key  
04:32 – 04:57 Grabbing the Seedance 2 API Documentation for Claude  
04:57 – 05:52 Pricing Breakdown: Enhancor vs Every Competitor  
05:52 – 06:34 Setting Up the API Inside Claude  
06:34 – 07:30 Hosting Your Image and Testing the API Live  
07:30 – 08:44 Reviewing the Payload Before You Submit  
08:44 – 10:38 Verifying Generations in Your Enhancer Dashboard  
10:38 – 11:22 Step 2: Downloading the Free UGC Pipeline from GitHub  
11:22 – 12:50 Running the Pipeline and the Onboarding Flow  
12:50 – 14:22 Building Your Brand Profile with Claude  
14:22 – 15:52 Audience, Goals, Discount Code and CTA Setup  
15:52 – 17:12 Step 3: The Control Center Explained  
17:12 – 19:22 Uploading Product, Subject, and Audio Assets  
19:22 – 21:06 Analyzing Assets and Confirming Brand Profile  
21:06 – 22:32 Finalizing the Brand Profile and Voice Matching  
22:32 – 24:52 Generating 8 Ad Variations Across 4 Formats  
24:52 – 26:16 Reviewing Payloads and Approving the $22 Generation  
26:16 – 27:56 Submitting All 8 Variants to the API  
27:56 – 29:14 Polling, Auto-Download, and Reviewing Results  
29:14 – 31:06 Adding New Formats Without Resetting Context  
31:06 – 32:52 Honest Take on Raw AI Output and How to Iterate  
32:52 – 34:20 Where Your Files Live and the Matrix JSON Log  
34:20 – 35:14 75% Off Seedance 2 API and How to Get It  
35:14 – 36:14 Outro + PublicAI Pilot Program

## Transcript

### Intro: What We're Building and Why

**0:00** · Hey friend, today I want to show you how to build a UGC ad testing pipeline using Claude and Seedance 2 API that you can charge thousands of dollars. Coming from someone who built a $400,000 per month AI app. All right, so here's the thing.

**0:14** · I used to take like eight different supplements every morning. I was today years old when I realized I do not need to carry 10 bottles to stay on top of my nutrition. Real gut health support with probiotics and digestive enzymes all in here. I used to have a whole drawer of pills and I genuinely am obsessed. The fact that it has 75 vitamins, minerals, and whole food sourced ingredients.

**0:37** · Really?

**0:37** · Yeah, and so I was like, "Okay, I need to try everything possible."

**0:39** · And how did you stumble upon it? Okay, okay, so true story. My doctor told me I needed more vitamins. I said, "Doc, I can barely remember to eat breakfast."

**0:45** · He said, "Try AG1." So I get asked all the time, "What's my one health secret?"

**0:48** · And honestly, it's this, AG1. One scoop every morning, 75 vitamins. Now, you can use this pipeline for your brand, or you can sell it to clients who need creatives. Anything works. But here is the real problem. Right now, you can access Seedance 2 through API at 3 cents per second. This is what most people are paying with limited functionalities. You cannot upload faces. And if you're generating volume, this thing adds up.

### The Real Problem With Seedance 2 API Pricing

**1:14** · We're talking about almost $5 for 15-second clip. But today, I'm going to show you how to get a 46% discount. So from 3 cents down to 18 cents per second with full access to upload human faces, 720p resolution, and unlimited concurrency for those who want to scale. Anywhere in the market, this is the lowest price you will find with all the features that I just mentioned.

### Why This Tutorial Is Different

**1:38** · Now, every video that you are seeing on screen was made with this exact method, and I'm going to share the whole thing with you. I want to be clear about what kind of tutorial this is because this is not what you are used to seeing. This is not a walk-through of features inside some subscription app that you already have.

**2:00** · I'm not going to click around UI and call this the tutorial. This is an in-depth detailed breakdown for people who don't just want to ship AI ads, but they want to build an actual product around C dance. They want to build workflows, they want to build pipelines, things that you can plug into your own app or maybe sell to your clients. And if that's you, you should stay until the end. And if not, watch along because you'll learn a lot of cool things that might change the way that you're thinking about utilizing AI in your business.

**2:28** · Honestly, if you don't get any value from this, I will personally pay you for the time that you spent watching. I've been building with AI and this kind of stuff for the last year, if you know me. And recently, I've made a commitment to myself that I'm not going to gatekeep any of this because the the big guys, the well-funded apps, they shill everything behind features, behind UI, behind workflows.

### What You Need and How to Think About This

**2:56** · They have teams that are figuring this out every single day, and I want to share with you exactly what they're doing, how they're doing it so that you can do it yourself, build your own thing without needing teams, big budgets, or so many subscriptions. I believe in democratizing knowledge and access to all these pipelines that can change your life like they changed mine. Now, there are three things that you need for this tutorial. First, you need Claude, either the app or Claude code. Second, you need C dance to API.

### Step 1: Creating Your Project Folder and API Key

**3:25** · And third, you need your creativity and something that's worth advertising, or your product. The very first thing that we're going to do here is that we're going to create a folder in your computer, and we're going to call this something like C dance AB testing. And inside this folder, we're going to create a text file, okay?

**3:44** · This is where you're going to store your API key that we're going to get in second, and your API documentation. So, let's get into that. We're going to head over to Enhancer. We're going to go to the API dashboard by clicking under the settings over here. And we will create a new API key. We're going to call this key C dense test.

**4:08** · And we're going to copy this in the text file that we saved inside our test folder.

**4:14** · Perfect. Now we're going to grab the C dense 2 documentation. Here's the documentation. There's a version that's optimized for Claude. If you don't know how to set up APIs, so all you have to do is copy the documentation and paste it inside the same file where we also have our API key, so right here. We're going to save this and this is your test project file. Now I want to show you exactly what you're paying for before we go any further. Enhancer C dense 2 pricing is on the left and every competitor is on the right.

### Grabbing the Seedance 2 API Documentation for Claude

**4:44** · And this is by far the lowest price in the market right now with unlimited API calls, which we call concurrency, with no queue and with full support for human faces. Okay, now that we have our text file ready, let's head over to Claude and click on the code tab.

### Pricing Breakdown: Enhancor vs Every Competitor

**5:04** · This is your coding interface. Uh this is where everything will happen. Now the reason I do not use Claude code terminal or a VS code is very simple. I personally just find Claude the app to be way more user-friendly.

**5:18** · I'm not a technical founder. Uh I don't like things that look scary to me. And especially for the purpose of this use case, I don't really need complicated setups. Uh and I'm not sure what your favorite vibe coding bro is telling you to do. But as someone who runs a $4 million per year AI app, um Claude the app works just fine. Uh this is where I actually vibe code Enhancer 2 every single day.

**5:45** · But you do you. Whatever it for you, the workflow is exactly the same. So, before we jump into our AB testing flow, we need to test that our API works and that everything is set up correctly. In your new session inside Claude, drag and drop your folder that you've created in the beginning of this video that holds your API key and your documentation and ask Claude to simply set up the API. Very simple, okay? So, we're going to say, "Set up the API."

### Setting Up the API Inside Claude

**6:16** · Hit enter. So, now we're seeing it go through the text file, the API key, the documentation, and it's setting it up in the back end. Done. So, after it does so, we need to test that the API key works. Very simple, I'm going to grab this image of myself and I'm going to drop it in our test folder, this one over here. I will ask Claude to host it for me temporarily using tmpfiles.org.

### Hosting Your Image and Testing the API Live

**6:42** · What does this mean? This means that I need to grab a link to my image so that we can use it inside C dense as an input. Right now, my image lives in my local computer and C dense requires a link to process generation, not only for images, but for any inputs, audio, video, images. This will host your image temporarily online and the link should expire in the next 10 minutes. And it gave us the link. You can click on this.

**7:09** · So, now it's time to run a generation and actually test the API. So, we have our API set up, we have our image URL, and we're going to ask it in the chat to run a 5-second clip, multi-reference feature, 720p resolution, fast, 9 by 16 aspect ratio with a subject saying, "Hi, thank you for being here, friend, and thanks for watching.

### Reviewing the Payload Before You Submit

**7:33** · Please give me the payload before you submit the generation, including a webhook URL so that we can get the final generation directly inside Claude. This is our entire prompt. Now, if you're confused at what the hell is a payload? A payload is simply what AI gets. The settings, right? You know, when you're going to those apps and you have to select the aspect ratio, the resolution, and all of that. I've covered this in this other video if you want to watch.

**8:01** · Structure of this payload comes from our documentation, which we saved in our text file, and Claude is already a where on how to structure that. So, we will hit enter and wait for Claude. And this is our payload. This is what AI will get. So, let's just go over it and make sure that everything is accurate. We have the type, which is image to video.

**8:25** · That's what we want to do. Great. We have the model, which is multi-reference. We have our prompt. We have our duration. We have our resolution. And we have our aspect ratio with our image links. In this case, it's just one link.

**8:43** · So, everything looks good and we are just going to ask it to generate the video for us. It's giving us a 200 OK response, which means that the request went through and it was accepted. So, our payload was good to go. And the generation is being processed in the back end. And also, if you see right here, it's giving us a request ID, which corresponds to the particular payload that we sent, which means that we can track our generation.

### Verifying Generations in Your Enhancer Dashboard

**9:13** · So, that when our generation is done, Claude can tell us, "Hey, this is done.

**9:16** · It took 5 minutes and here's your link to your video." That's why we always need to have that ID, so that we can talk to Claude and then we can check whether the video is ready for us to get or not. Now, something that's very interesting that happens in the back end is that if you go into your Enhancer account right now, where you got your API key in the beginning, under usage, and if you click C dense 2 API, you will see that the same exact request that you talked to Claude about is pending and is generating.

**9:49** · The second that your request is completed, it will show both inside your Enhancer account and also inside Claude. Because sometimes Claude might give you API errors if things are not set up properly, and sometimes it might tell you that the service is unavailable, that it's not going through. The only source of truth that you need, whether your generation went through, how much it charged you, how long it took, etc., lives inside your API dashboard inside Enhancer.

**10:15** · So, in here you can see the errors, the the actual file that was generated, especially if you are building apps and you want to track every request for your user. This is where it's going to live.

**10:30** · So, if Claude fails, at least you know if the request went through and how to get them. Our API is working. This is step number one. Now, step number two, this is where the fun begins, we're going to create our A B UGC ad testing pipeline that you can sell tomorrow. So, I've spent 3 weeks to perfect the pipeline and I'm giving it away for free. I built this agentic system that's powered by Claude that lets you generate UGC ads entirely through your Claude interface here.

### Step 2: Downloading the Free UGC Pipeline from GitHub

**11:01** · Maybe I'll cover in another video the steps that I took to build this, but today I will simply share with you the entire project. I'll show you how to set this up, how to start it, how to use it, and run it for yourself so it's not so complicated to follow through this video. The project is called UGC ads pipeline with C dense 2. You can find this for free on GitHub.

### Running the Pipeline and the Onboarding Flow

**11:23** · So, this is the link, whatever you're seeing right now on screen is the GitHub project. So, we're going to download it. You can read the project for yourself and see what it does. We're going to download this as a zip file.

**11:36** · We're going to unzip it and we're going to get a folder that's called C dense to UGC. We got our folder. This will be our main folder for this project. And we're going back into Claude and this time we're going to drop the said folder and we're going to type run this in the prompt. What happens now is that the project starts its onboarding flow. This is set up in the back end.

**12:01** · The very first thing that the pipeline does is that it onboards you. It checks the setup status and it gives us a welcome message that says, "Welcome to the UGC ad pipeline." And then, as you can see right now, it is laying everything out for us. All the models available from this API, the full pricing breakdown by resolution, the credit system. So, you can see for example that C dense to fast at 480p is $0.073 and all of this is visible right here before you spend a single dollar.

**12:33** · It's also giving us the direct link to Enhancer API dashboard, which is very convenient. We can use the same API key like before. So, we can head back to Claude and we can paste it in the chat and we're going to type this is the API key. Save this in an ENV file. So, paste your API key in there.

### Building Your Brand Profile with Claude

**12:56** · Now, an ENV file is just a small configuration file that lives inside our folder. It stores sensitive things like the API key so you don't have to paste them every single session from now on.

**13:07** · Uh Claude edits that file automatically and adds our key. That's it. So, now our key is saved and we never have to touch this again. Step two from our onboarding is our product file. Claude is asking us for more information about our product. What is the product name? I'm going to say AG1.

**13:26** · What's the category?

**13:29** · It's a wellness product. It's a wellness. What is the description? What does it do? I'm going to say that it boosts energy. The key selling points here, honestly, I I don't really know them off the top of my head, so I'm just going to type help me figure it out. And I'm going to let Claude do it. That's the reason why we're using agents, either way. The price point, $99.

**13:52** · And what makes it stand out from competitors? High-quality 75 vitamins. I'm going to hit enter and it comes back with suggested selling points for AG1, which says 75 vitamins and minerals, clean high-quality ingredients, all-day energy boost, gut health and immunity support.

**14:12** · This is good. Um it also is asking if these work for us or if we want to adjust them, we can, but I think that for the purpose of this video they work just fine. So, I'm going to type yes. Great. So, now step three from the onboarding is the audience and the goals.

### Audience, Goals, Discount Code and CTA Setup

**14:29** · So, our target audience, the ad objective, the platform, the tone, the discount code, or any custom notes that we want to add. I'm going to type here help me out with a section because the purpose of this test is I want to see what Claude can do, uh and I want Claude to recommend everything. And since it already knows the product, AG1 is a popular product, it comes back with the target audience, which is health-conscious adults, the objective, which is conversion, uh platforms are TikTok and Instagram.

**15:01** · Tone is energetic and aspirational. No discount code. And custom note emphasizes the morning routine. I'm going to keep most of this as is, but I'm going to add a discount code. I'm going to say 25% off. I literally do this by typing in the chat.

**15:17** · I hit enter and now it's doing something very interesting. It is saving the brand profile for us as a JSON file inside the configuration folder. So, JSON is simply a structured text format. Think of it as a digital profile card for your brand.

**15:34** · So, anytime that you want to come back to this product, Claude already knows your brand. It knows who you're targeting, how you're targeting them. He knows your selling points, your discount, your CTA. All of this is saved and pulled automatically every single time when you mention your brand, in this case AG1. Step number four, the control center. And this is the bread and butter. This is my favorite part of this tutorial.

### Step 3: The Control Center Explained

**16:01** · It's going to spin up and it's going to give us a link, an HTTP localhost, which in my case is going to be in the port 8099. And if we click this link, it's going to open a site in our browser. Here it is. This is our control center for our ads pipeline. Now, I want you to understand what this actually is before we go any further because this is simpler than it looks.

**16:26** · This is not a separate app. This is not a cloud-based. This is not a subscription to anything. This is literally just our project folder, so this one that we downloaded from GitHub. This has turned into a clean interface that we can manage from our browser. That's it. It's your It's your folder just way easier to work with.

**16:48** · So, in here, we can upload product images, we can upload subject images, mood references, audio clips. We can browse and manage everything. We can add products, and we can view and download every single video that our API generates. All of it is locally living inside your computer or your machine. So, let's start uploading. I'm going into the product section and uploading our AG1 image. And I'm going to name this AG1.

### Uploading Product, Subject, and Audio Assets

**17:19** · I'm going to the subject and I'm going to upload a photo of myself. I'm going to name this Cereo. And now I'm uploading our audio. This is a 6-second clip of me talking. The reason that this matters is that the pipeline is going to use this clip, this audio clip, to match the tone and pacing of whoever is speaking in the ad, which in this case is me.

**17:41** · So, if you are building for a brand with a consistent face or spokespersons, so you want them to to have a consistent voice, this is how you keep that voice the same across every single variation that you're going to be generating. Everything that you upload through the control center gets automatically dropped into the right subfolder inside your project directory.

**18:08** · So, if we go into our main folder right now and we click into assets, we click into products, and look, it created a folder that's called AG1.

**18:17** · And it put our image there of the product automatically. We didn't do that. The control center did. The same thing for for our subject. So, we click into subjects, and here there's a Cereo folder, and our subject image that is sitting right there. And now, watch this. I'm going to delete the subject image from the control center, and we see the subject folder in our directory, it's gone from there, too. So, it's deleted from the control center and at the same time is deleted from our folder. They are fully linked both ways.

**18:52** · So, if you want to add it back, we just have to upload it, name it Cereo, and boom. Folder is back, image is back.

**19:00** · You'll also notice that there's a brand JSON file that's sitting in the assets folder. That's a brand profile that we just built with Claude that I was talking to you about, which has a product name, the category, the selling points, a discount code, the CTA, everything we told it, it lives inside this folder right here. It's all saved as a simple file. So, you can come back to it at any time with the context waiting for you. Fine.

**19:21** · So, now that we have everything uploaded, the product, the subject, and the audio, we are going to copy the analyze new assets command from the control center, and we're going to paste it into Claude, and we're going to let Claude find all the three assets and start analyzing them. So, we can add more context, which will be helpful for when we generate our scripts for our ads. As you can see, Claude found three assets and is analyzing our product and our subject.

### Analyzing Assets and Confirming Brand Profile

**19:51** · Taking a look at what the product and the subject look like, and it's giving a detailed description to each one. Analysis is now complete, and here is what it found. It found that the product is AG1, it found that the the subject is Sirio, and described me as a young man with curly hair and a beard and a smile. And it also found the audio clip. Now, if you're going to the control center and you click on AI context for any asset, except audio, it's going to give you the full description of that asset.

**20:22** · For the product, it's giving us the visual elements, the the the ad notes, everything it was able to analyze from that image, and it does the same thing for the subject. So, if you click the AI context under Sirio, you're seeing the description, the visual elements, the the notes. It's not going to describe the audio because it's not transcribing it, and we don't really need to. It just knows that the file is there, and it's going to reference it for tone and pacing in every single generation, so that we keep our audio across the board the same.

**20:49** · We have everything, we have our assets, our descriptions, our brand profile, um but before we generate, I want to confirm that the brand profile is complete and solid. Okay? So, I'm going to type confirm the brand profile for us.

**21:04** · Let's see what it does. So, it's reading everything back to us, the product name, the category, the description, the price, the unique selling points, the target audience, the goals. Now, when I look at this, I'm wondering, is this enough, or should I add more information so that AI has as much context as possible? And I can ask it directly, is this enough, or should we add more? This is what it's doing.

### Finalizing the Brand Profile and Voice Matching

**21:26** · It's analyzing the JSON profile that we have in our folder, and it's coming back and saying that it's worth adding a specific CTA, or a discount code, or more subject images, or mood images, if you want to reference those. And in this case, I don't need any of the extra images, um but I'm going to add a discount code. I'm going to type add discount code save 25, and also, I'll add a link in bio, so that we have that mentioned in our scripts. Hit enter.

**21:58** · Now, it's editing the JSON file, and it's updated it both the discount code, save 25, and the CTA link in bio, which is both confirmed to be included in every single generation going forward.

**22:13** · You see how it's noticing that we have an audio file? It's asking whether the AI should match the actor's voice to the audio clip. And I'm going to say yes. Of course, you should match the voice, but only the tone of the voice, not the direct copy of what the audio is saying, okay? So, this is what I'm saying in the prompt. Now, I'm ready, so let's AB test this. It's asking us a few more questions.

### Generating 8 Ad Variations Across 4 Formats

**22:39** · How many videos do we want to generate?

**22:42** · I'll say eight.

**22:43** · How many seconds each of them? 15 seconds. What aspect ratio? 9 by 16.

**22:50** · How many formats?

**22:51** · Uh it's giving us a list of options, and I'll I'm just going to say all four, and I think that we're done. This is a whole flow. Again, it's set up inside your folder. You You not have to do anything.

**23:01** · It has eight videos across four formats and it's now reading the prompt templates that exist in the back end inside the GitHub folder that you downloaded. And those prompt templates are what tell the AI how to structure each ad format. It is also reading a prompt markdown file in the same main folder. The actual system prompts that power the AI are called through a gated API, so you cannot see them directly, but that's fine cuz you don't need to.

**23:31** · But what matters is the output of those prompts, which you can approve and control. Also, it's uploading our assets to the temporary hosting, if you remember from earlier, Cedendo URL to process images or videos or audio, so you cannot pull from your local machine, and that's what it's doing right now. And also, it's setting up the webhook, which is an automated notification, like think of that as a notification.

**23:54** · So, the moment that a video finishes generating, Cedendo sends a signal back to Claude, so it knows to go and download it, and it sends you a link. Perfect. We have all of our assets URLs, as you can see. We have our product image, our subject image, and our audio.

**24:08** · And we have our webhook. And now, all the prompts and all the different variations of our product. Variation one is a podcast ad. It's giving us full prompt of the payload. It's giving us the timeline, what the subject is saying, and the reference to the audio with the exact pacing. We also have the payload. Variation two is another podcast ad. Variation three is a UGC ad.

**24:34** · Variation four, again, a UGC ad, but with social proof concept. Variation five is a lifestyle ad. Variation six and seven are TikTok green screen formats. Variation eight, it's a green screen, but comparison style, and it's giving us the cost estimate for all eight. I notice something here. I I see that it's setting the resolution to be 480p. That's not what I want. I never actually set that. I want it to be 720p.

### Reviewing Payloads and Approving the $22 Generation

**25:01** · That's a reason why we see play loads before we generate. We want to make sure that everything is correct. So, I'll just type change the resolution to 720p on all variants. It's revisiting all eight variants and it's recalculating the cost as you can see. So, everything's now updated. And before I submit everything, I want to see the final payload one more time. As I said, these steps matters. You need to approve everything that's going from the AI agent to C dense API before the submission because any mistake in the payload would cost you credits. Always review.

**25:34** · Always make sure that it looks right before you say go. And I would recommend doing this every single time. And never let AI decide for you or send the payload without explicit approval.

**25:45** · And now the resolution is 720p across the board. It's asking us to approve with an estimated cost of about $22 for eight videos at 15 seconds 720p. And just to be clear, this is not the fast mode. This is standard quality. The fast mode is cheaper and I would recommend using that for any ads or social media assets. It's about 30% cheaper than this actual price here. So, I'm going to type I approve. And now it's sending the official final payloads to C dense API.

### Submitting All 8 Variants to the API

**26:17** · It's submitting eight variants. Just checking the API key. Here's variant one. It's asking us to authorize. And version one is submitted. Also, you can see that it wants to wait five seconds before submitting the rest of the videos. Version two is submitted now as well. I'm going to fast forward so that you can see all eight get submitted. And here we go. All eight got submitted. We have a request ID for every single one.

**26:42** · And the moment that you see that a request ID comes back, that means that the video is in processing. The same thing that we did in the beginning of this video. Again, if you you to verify that these actually went through, you go and log into Insight Enhancer, you select C Dance 2 full access, and you can see all variations inside your dashboard with the exact same request ID that Claude gave you. Costs match, the credits match, the dollar amounts match.

**27:08** · That's your independent source of truth, completely separate from anything that Claude says in the chat, so that you know 100% that these requests went through the API, and Claude isn't just telling you what you want to hear. What Claude is doing in the back end is called polling.

**27:25** · Polling just means that it's automating or checking in with the API every 2 minutes, and it's asking, "Hey, buddy, is the video done yet?" Claude is doing this for you without you having to touch anything. It does this automatically.

**27:36** · And the moment that a video completes, it downloads it and it adds it to the control center. Also, it adds it in your folder. You can also refresh your Enhancer dashboard manually to check. I do both. Polling version one status, and as you can see, Claude just detected version one is complete and it's downloading it. Still waiting for seven more. This can take anywhere from 3 to 12 minutes depending on the size of your assets and the complexity of the prompt.

### Polling, Auto-Download, and Reviewing Results

**28:04** · Refresh again. Now, most of them are done, and Claude is catching up to and it's seeing that there's five more just completed. So, now we have seven out of eight completed. So, now when everything is complete, all the videos will show up in our control center where we can preview them live. It's also showing us the prompt for each one. So, let's hear some of them very briefly.

**28:29** · All right, so here's the thing. I used to take like eight different supplements every morning. Then I found AG1. 75 vitamins, my energy is up, my gut feels incredible. Use code save25 for 25% off. Link in bio. Everyone kept telling me to try this, and I finally get the hype.

**28:44** · AG1 75 vitamins in one scoop. My energy has been insane and my digestion is is the best it's ever been. One scoop of AG1 before anything else. 75 vitamins, prebiotics, probiotics, all in one drink. It takes 30 seconds and I feel the difference all day. This is how you start your morning right. Save25 for 25% off, link in bio. That first scoop in the morning. Gut health, probiotics, 75 vitamins.

### Adding New Formats Without Resetting Context

**29:22** · One This is pretty cool. It's also giving us a cost for everything we just generated. Now we can keep going. We can add more tests, more formats, more styles. I can say give me a 720p fast mode, 10 seconds, 16 by 9 podcast style with guests, and a news anchor format.

**29:40** · And the beauty of this is that it already has all our branded information and it has a subject image, and it has a product image, the brand profile, the discount code, all of this. Everything is in the memory folder and it's not starting over. It's just taking the same context and it's applying it to new formats. We don't have to go back and forth copying and pasting the same things over and over because it is saved and you can pull everything from the folder.

**30:03** · I'm going to hit generate and now it gave us two new variants with the prompt and payloads and it's re-uploading the assets because those temporary links expired. If you remember, they're only good for about 10 minutes. So we have a new podcast ad with guests and a news anchor format.

**30:22** · Cost estimated to be about 1.5 per video, which is about $3 in total for both. So to put this in context, a single 15-second video through most of the other APIs at standard pricing runs about $4.5.

**30:39** · So we're getting two videos for less than the price of one. Now, the request IDs came back for both and I can keep going. I can say that I need a cinematic HBO Game of Thrones style video. This is the beauty of this whole thing. We're just talking to it. The project has been set up so that it deeply understands Seedance and prompt engineering for Seedance specifically for ads and UGC.

**31:02** · You don't have to know any of that. You just describe what you want and it's going to do it for you. Gut health support, probiotics, prebiotics, and digestive enzymes 75 plus vitamins, minerals, and whole food nutrients in one scoop has been a game-changer for me. Plus, replaces multiple supplements, one product total coverage. This is what I start every morning with. One scoop, 75 vitamins. My guest tried it last month and hasn't stopped talking about it. Code save 25, link in bio.

### Honest Take on Raw AI Output and How to Iterate

**31:29** · Breaking in wellness, AG1 just dropped a new formula. 75 vitamins in one scoop.

**31:34** · Experts call it the most complete daily supplement on the market. Use code save 25, link in bio. Now, this doesn't have to just be for ads. It can work on anything, but you have to fine-tune the pipeline as it goes. Here's a free guide for you to go through and maybe feed Claude. I built this so you can understand how prompt engineering works for Seedance, too. Link is in the description. Now, I want to be straightforward with you here because honesty is more useful than a polished demo and by no means this is a polished demo.

**32:05** · Some of these videos are going to have issues, spelling errors on screen, subject that looks slightly off, that didn't quite land. This is raw AI output and it's never going to be perfect on the first pass. I haven't gone through every single prompt in this video. Um, I haven't actually quality controlled what went through. That's not the point. The point is to show you the pipeline. My recommendation is that you always start with 720p fast at 5 seconds before you commit to a full 15 second standard quality run.

**32:35** · And honestly, I don't even recommend the standard quality. Fast is pretty much the same and cheaper. This is enough to tell you whether your prompt is heading in the right direction. Test first, iterate, then scale. Then continue with AB testing.

**32:49** · That's how you avoid burning credits. I can keep pushing this. I can ask for a Super Bowl ad or different types of commercials. Your body is a system. Most people run it on bad inputs. I I upgraded mine. AG1, 75 vitamins, minerals, and probiotics. One scoop, system optimized. While they lag, I operate at full capacity. This is the upgrade. Code save 25, link in bio.

### Where Your Files Live and the Matrix JSON Log

**33:10** · Vitamin D at 8:00 a.m., zinc at noon, probiotics with dinner. My friend staged an intervention. They said just drink the green stuff. So, I did. AG1, one scoop, 75 vitamins. I got my life back and my friends. Code save 25, link in bio. In terms of where your files actually live, the control center that you've been looking at in the browser is just, as I told you, a visual layer on top of your project folder that's running locally on your machine. So, all the videos that you've generated are downloaded inside the project folder.

**33:40** · Your specific project folder in this case is AG1 AB test. It has all the video files, plus a matrix JSON file, which is a complete log of every payload you sent and every request that you've made during the session, which is useful for going back to recreate something or troubleshoot if anything went wrong. And as mentioned before, everything lives in your Enhancer API dashboard. Every video that you've generated with your API key is visible there, so you can view it, download it, track the costs, see the request IDs. All of it is tied to your account.

**34:12** · So, this, my friend, is a full 30-minute tutorial on how you can use SeedAndSow API to automate your ad creation process. You can find SeedAndSow API at up to 50% by simply heading to Enhancer, getting a $45 subscription, and you get premium prices, full access, unlimited concurrency, so you can start scaling today. And if you want another discount on top of the 50% you can use the code save 25 for an extra 25% off your subscription plan. So that's a total of 75% off C dense 2 API limited time only.

### 75% Off Seedance 2 API and How to Get It

**34:46** · Friend, this is only the tip of the iceberg. There's so much more that you can do and in the next video I'll show you how to create cinematic commercials like this one that I've created from one single prompt. We'll go over the prompt the structure, how to build it yourself so turn on the notifications, hit that like and subscribe button because it helps not only me but also other people find this type of content.

**35:05** · If you want more prompt formulas like the ones that I showed you today and if you want to learn more about how to actually build a product like the agent or or the UGC on top of C dense 2 for your own clients, come join my free community it's called public AI. The link is in the description as well. It is completely free and again here's a part I'm most excited to tell you because right now inside public AI we are running a pilot where my team is helping five students build five real SaaS apps. Full-time AI stack engineers working on projects for free.

### Outro + PublicAI Pilot Program

**35:38** · We literally assign engineers to your ideas and we help you build it even if it's from scratch. We draw every month there's a real interest and if you have an idea and you just want to throw your name in join in the community apply worst case you will learn a ton from everyone else building in there and the best case my team will build the product for you. If this video was useful to you hit that like button. It sounds small but it genuinely helps other people find this kind of content and that means a lot to me. Now links for everything are in the description.

**36:06** · I'm going to see you in the next one and do not forget my friend create without limits because you can. This is Syria.