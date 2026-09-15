---
title: "Claude Code + Hermes Agent = $10,000 AI Agents"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=gYzlgK5Dw1s)

Join my FREE Webinar on 23rd August: https://go.jmsolutionss.digital/afbf5bdc  
  
Get my 1-1 support to Start and Scale your AI Agency: https://go.jmsolutionss.digital/435a6962  
The fastest way to go from beginner → AI Automator: https://go.jmsolutionss.digital/2fda5e7a  
  
Join my newsletter where I share more about how I made over a $100k with my AI agency: https://go.jmsolutionss.digital/712162dd  
  
Timestamps:  
  
0:00 – Intro: The $10,000 AI Agent Strategy  
0:48 – Proof of Concept & Real Client Contract  
1:08 – The System Blueprint: Speed-to-Lead Automation Breakdown  
2:07 – Setting Up the Hosting: VS Code & Hostinger VPS Configuration  
3:46 – Inside the Hermes Agent Dashboard  
4:02 – Gathering Your Infrastructure API Keys (Anthropic, Twilio, 11 Labs, Cal.com)  
6:56 – Setting Up the Lead Capture: Typeform & GitHub Repo Prep  
7:58 – Deep Dive: Getting Your Google Sheets API Credentials  
9:54 – Prompting Claude Code Live to Build the App Scaffold  
10:56 – Configuring Environment Variables (.env) & Connecting APIs  
12:00 – Pushing Code to GitHub Safely (Without Leaking Secrets)  
13:00 – Terminal Execution: Running the Docker Container & Going Live  
15:16 – Connecting the Webhook to Typeform  
15:57 – Live Test: The Ultimate Speed-to-Lead Voice Demo  
17:21 – Packaging, Pricing, and Selling AI Systems to High-Ticket Clients  
  
  
Learn how to build and deploy a high-ticket B2B voice automation system using the Hermes Agent and Claude Code developer stack. This video covers the step-by-step implementation of a speed-to-lead conversational AI phone agent designed for local service businesses and roofing contractors. The technical workflow demonstrates how to host a persistent autonomous server on a Hostinger VPS via Docker Compose, configure APIs for serverless triggers, and orchestrate multiple software connections without writing manual code.  
  
The software architecture integrates Typeform lead capture hooks, real-time telephony routing through Twilio, low-latency natural speech generation using ElevenLabs, and multi-variable calendar scheduling via the Cal.com API. Data management is handled by writing dynamic lead profiles directly to Google Sheets using the Google Cloud Platform (GCP) Console and service account credentials. The final segment outlines B2B sales pricing strategies, customer acquisition models, performance retainers, and client implementation pricing structures tailored for artificial intelligence consulting.

## Transcript

### Intro: The $10,000 AI Agent Strategy

**0:00** · Businesses are paying $10,000 for AI agents that realistically now only take an afternoon to build. Thanks to Hermes, which is by far one of the most powerful agentic platforms in the world right now. And it becomes even stronger when you pair it up with Claude code, which is why in this video I'm going to be breaking down this exact tool \[music\] stack and build one of these agents live

**0:22** · right in front of you start to finish on this screen. \[music\] And the best part is that I'm not going to use any code, I'm not going to have any team behind me, and I'm not going to skip through any of the boring but important parts of the actual build. And at the end of the video, I'm also going to go through the part which most people struggle with, which is how you can actually sell these systems for thousands of dollars to businesses. \[music\] So, if it sounds like something that you want to learn, let's dive in.

**0:46** · All right, so before we get to the actual build, I want to show you that we've done this, meaning that we've sold AI agents to dozens of different companies, one of which was a service company and we closed the deal for $18,000 across four different months. On the screen right now, you should see a signed contract as proof that we've done this and hopefully you can do it too. So, with that said, let's get into the build. Okay, so we're going to use Claude code and Hermes agent to build a $10,000 AI agent, which in this case is Speed to Lead.

### Proof of Concept & Real Client Contract

### The System Blueprint: Speed-to-Lead Automation Breakdown

**1:12** · Now, there was a study that came out that reported that the average business owner takes 47 hours to respond to a lead and responding in 5 minutes instead of 30 makes you about 100 times more likely to reach them and 21 times more likely to qualify them. Meaning that every single lead that they don't follow up with is lost revenue for the business. Hence why you are able to charge $10,000 plus for this exact system right here. So, the way that it works is that we have a form, in this case it can be a Facebook ads, or Google ads, or just a simple form on the website.

**1:42** · The lead will fill out the form and then we have an AI agent that calls them within 10 seconds of them opting in. It will ask them some questions, it will book a property inspection because it's a roofing company. So, my roof is broken, it's leaking, X Y and Z. So, it will ask questions about that, and it will book the the actual inspection, the free inspection for the for the lead itself.

**2:04** · And then we add details to a database, which will be a Google Sheet. Now, the first step is actually uh setting up the hosting platforms for both different uh softwares. So, we have VS Code for Clock Code, and we have Hostinger for the Hermes Agent. To download VS Code, you can go to visualstudio.com/download, download it for your desktop, and then you'll be able to get on a page that looks like this. You can go to extensions, and then you can download the Clock extension right here. Press install, and you'll see that you have it right here. And then we want to add or open a new folder in our desktop in this case, um and we can name this Hermes Agent.

### Setting Up the Hosting: VS Code & Hostinger VPS Configuration

**2:40** · There we go.

**2:41** · Open.

**2:42** · Yes. Open this. And we're all set up for the Clock Code that we're using as an extension inside of VS Code. Now, in terms of Hostinger, you can go to hostinger.com/applications/hermesagent, and you'll get here. I recommend that you get the KVM2 plan option just because it gives you the most flexibility with the power, but also the memory itself. And once you log in, you get the plan, you'll get on a page that looks like this, where you have your Docker um installed. And you can go to manage, and then you can go to Docker Manager. You can install this, it will take about a minute. And once you have this here, you can go to compose.

**3:12** · You can go to one-click deploy. Look for Hermes Agent inside of the catalog here.

**3:18** · So, you can do Hermes Agent select. So, make sure to copy this and save this somewhere safe. You can press deploy, and now it will take about 30 seconds to 1 minute to actually deploy in this server itself. All right, now the Hermes Agent is opened, it's finished. We can go here to open, and it will ask us for a username and password, which is the one that we had before. So, we can paste Hermes here, and we can also paste the password that we had, as well.

**3:44** · And now we're inside the actual system.

### Inside the Hermes Agent Dashboard

**3:46** · As you can see from the beautiful interface, this is Hermes uh dashboard, is where you chat to Hermes. You can say hello.

**3:52** · And it says error because we have not connected the AI model yet, which is fine. But, this is what you should see.

**3:56** · If you don't see this, something went wrong. Go back into me. All right, so that's it in terms of the hosting for Hermes agent and Claude code. Now, we get to the actual softwares that we need to use. So, the first one here is Anthropic for the API key. So, you can go to platform.cloud.com, setting workspaces default keys. You can press create key, and you can name this Hermes agent or whatever it is that you want to name it. You can press copy key, and you find them actually you have enough credits here. I currently have $17 because you're going to need this to run the agent itself. Then we have Twilio.

### Gathering Your Infrastructure API Keys (Anthropic, Twilio, 11 Labs, Cal.com)

**4:25** · So, Twilio is a platform that we use to buy the number that we're going to use. I recommend that you're on the plan of pay-as-you-go because numbers obviously are not completely free to use. So, you want to go to the search bar, look for phone numbers, and then you can go to phone numbers here, and then you can go to set up a new phone number, choose your country.

**4:45** · Again, not all the countries are going to be in Twilio, so heads-up. But, the ones that we want to use in this case, US is fine. You can choose voice as SMS is not what we need right now. Toll-free is fine, and then you can press search, and then you can go through the whole setup of buying the number itself. Put your credit card there, buy it, and then you're good to go. It's only $2.15 per month, so it's all good. It's not going to be anything crazy. Now, once we have this, in this case I already have a number here, copy your number and paste it somewhere safe as well because we're going to add all of these into Claude code itself.

**5:11** · We also want the developer want to go to API keys and off tokens, off token, and we want to copy the account SID. And then we also want to copy the primary off token. So, these are the passwords and the way that, you know, Hermes agent is able to access the number and it's able for the number to call the lead whenever, you know, a form is submitted.

**5:30** · All right, so now that we're done with the actual Twilio, which is the number that we're going to use, we go to Eleven Labs. So, Eleven Labs, you can get the $6 a month plan. You can go down to developers, you can go to API keys, and then you can press create key, name this Hermes. I'm not going to put any restrictions, create a key, and then you have the key right here. We also need a voice, so in this case you can go to voices. You can choose your voice. I can go to English.

**5:53** · I can choose American accent.

**5:55** · And then I can choose Hi friends, I'm Lydia.

**5:59** · Lydia is fine.

**6:00** · Lydia is fine. We can go here, copy voice ID, and then you can paste it somewhere safe as well. By the way, in case you're wondering where I'm looking, I'm looking at a doc that I'm going to paste everything in. And we're done with 11 Labs, we can go to cal.com to set up the event for the voice agent to actually schedule. So you make an account on cal.com, it's completely free. Make an event, in this case I called it free property inspection. You can go here, make it 30 minutes. All the settings are pretty standard, you know, availability and so on. And you want to copy the event ID. So it's the number that you see on the URL on the top.

**6:28** · Paste the number somewhere, then go to settings, go to profile, copy your username right here, cuz we're going to need this. And then we also want an API key, which you can find down here, API keys. New, Hermis. As you can see, I already have four Hermis agents.

**6:43** · Uh press create, and you have the API key here. So we're essentially laying the foundations for the whole system, and making sure that the system has access to all the softwares that we need. Typically I do do this in the first step, just because it doesn't bite me in the ass later, cuz it's much easier. The next step is Typeform. So this right here is the software that we're going to use to be able for the lead to fill out the form, and then get called in 10 seconds uh by the actual system. Go to Typeform, make an account, and then you want to create a form.

### Setting Up the Lead Capture: Typeform & GitHub Repo Prep

**7:06** · In this case, the form that I made uh contains the full name, phone number, email, services do you need, describe your issue, where is your property located, and also when do you need help by? Um that's fine. So make sure you have this. All right, once you make the actual form, we can go to forms here, and we can go to profile, we can go to account settings, we can go to personal tokens, and we can generate a new token.

**7:28** · Name this Hermis. All scopes is fine. You can copy this, and that will be your API key. All right, the last step is making a GitHub repository, uh where we go to make an account, we press new, name this uh Hermis.

**7:41** · And then you can press create a And then you can copy the link right here. And you can keep it. All right, with that said, we're done with getting the API keys and passwords from all the softwares. I wanted to show you that part just because it is actually important uh to cover cuz you might be stuck actually finding these yourself.

**7:57** · So, I hope that was helpful. Now, let's go to building the app on Cloud Code and start there. Hey guys, quick one here.

### Deep Dive: Getting Your Google Sheets API Credentials

**8:02** · If you are working 9:00 to 5:00 and you do want to start and scale your own AI agency, then check out the first thing down below which walks you through a full video on how you can do that step-by-step by working with me one-to-one. Now, let's get back to the video. All right, so the next step is getting the Google Sheets credentials to be able for the system to access Google Sheets to add the details of the lead that called in. So, go to console.cloud.google.com.

**8:24** · And by the way, all the links are below.

**8:26** · You can go to select a project. You can make a new project. In this case, I already made one. Once you make the name, you should see the name right here. It will take about a few seconds to to download. You want to go to API and services. You want to go to the enable API and services and go to Google Sheet. When you're in the Google Sheets, you can press enable and then you're enabling the connection of Google Sheets. The next step is making the credentials, so you can go to API and services credentials. And then you'll be able to create credentials, service account. You can name the service account Hermes 123.

**8:56** · Create and continue. You can press done. Once you made this, you can see it here. I already made two before, so once you go here, you can press this. You can copy the email here that we have. And then we need to go to keys. We need to go to add a key.

**9:11** · Create a key here, JSON, create it. Uh and now it might get a bit bit technical, but don't worry. Um because all we have to do is open the file. So, you should open the actual JSON thing uh in front of you. By the way, this makes no sense to me whatsoever, so don't worry. But, I've just done it so many times that I know what to do here. Uh you can copy everything from here.

**9:30** · Let me zoom in. Everything from the start until the end and paste it somewhere safe. And essentially, now that this is active, this system is able to access our Google Sheet, which is actually the next step. So, we're going to go to sheets.new, create a Google Sheet, and then name this lead agent.

**9:48** · And we can copy the ID of the sheet right here, which is the anything from the D until the edit, and paste it somewhere. So, we made the folder in Clock Code. We're going to go here, and we're going to paste this prompt right here, which tells exactly Clock Code the structure of the project, how it's supposed to look, the different files that it's meant to have here, and how everything goes together. All right.

### Prompting Claude Code Live to Build the App Scaffold

**10:06** · Now, if you're wondering where you can get the prompt, it's in the second link down below in my free School community.

**10:11** · You can go to the classroom section, templates vault, and you'll find everything there. We have this here. We can press go, and we can do bypass permissions. And by the way, you can also screenshot this, and you can give it to ChatGPT, and it will give you the prompt itself. As you can see, now it's starting to make the actual folders and files, which is great. All right. It just finished making the different folders. This is what we call the file directory, where all the different folders are and files. I can now paste the next prompt, which again, you can find in the same document. This right here is going to tell it to create a .env file, not exam, just .env file.

**10:37** · So, that we're able to paste all the different credentials and API keys that we just had. And in here, it's saying it, "Hey, when this happens, do this. When this goes wrong, do this." to make sure that we have those guardrails when we're actually doing this. I'm going to press go, and now it's going to implement the next set of rules. All right. So, Clock Code just finished making all the different files.

### Configuring Environment Variables (.env) & Connecting APIs

**10:58** · \[music\] One important thing is that we have to replace the keys here. So, this is the .env. This is the way that this system takes all our credentials, all our passwords, and it uses it to access the softwares when the system is running.

**11:09** · So, now we want to paste all the API keys that we had before onto here. So, everything from here and out, you should probably have, right? Cuz we went through it before. The one thing that does change is the port, server URL, and time zone. So, time zone, you can use your time zone. In this case, I have Asia/Dubai, cuz I'm here right now. Server URL is something you can get by going to the Hermes agent, and you can actually just copy everything from before chat up until dot cloud and you can paste this here.

**11:38** · And then the port will be 3000, which is fine. And all of these others we can uh simply just copy this. You can either copy this here or you can just paste it right here. It's blurred right now, but this should be the Anthropic API key, 11 Labs, Twilio, call.com, Google, Typeform, and the server URL, which I already have, and my phone number as well. No, I'm not showing it, so don't try.

### Pushing Code to GitHub Safely (Without Leaking Secrets)

**12:00** · I'm going to go here, file, save, and now we're good to go. The next step here is to push everything to GitHub. So, we want to take all the code and push it here because that is going to be the middleman between uh cloud code and Hermes agent, right? So, copy this and say "Hey, I want you to take all this code and push it directly to GitHub. Here's the URL of my repository. Um let me know when it's done." And we paste the link.

**12:23** · There we go. So, now it should take all of this, push it to GitHub, so that Hermes agent is able to read it as well.

**12:29** · All right, so just as expected, it's going to ask me if I want to actually push the dot ENV. I'm going to say, "No, don't push the dot ENV, but you can push everything else." So, the reason why we don't want to push the dot ENV is because our dot ENV contains all our service secrets, API keys, passwords. Uh it's like your credit card number.

**12:45** · You're not going to put it in the web, right? So, we don't want that going through. So, very good for asking, and uh everything else, yes. All right, so everything has been pushed to GitHub.

**12:54** · So, if I go here and I refresh, then I should see different files. Perfect. All right, so the next part is actually using the terminal. Now, for those of you who are not technical at all, this might scare you, but stay with me. It's actually very, very easy, and I'm going to give you the full thing to add as well, so don't worry. Um cuz I'm also not technical, so we're on the same page here, okay? We want to go to terminal here, so make sure you're in Hostinger, go to terminal, and then and then you can press and you can type exit here.

### Terminal Execution: Running the Docker Container & Going Live

**13:19** · And you have the actual thing itself. Now, it's listening for any commands or any prompts that we give it. All right, so this right here is going to be the code that we have to paste inside the terminal right here for it to actually download everything. So, we need to replace all the keys that we have here.

**13:31** · So, the first one is the GitHub repo URL. So, if you remember before, I mentioned to copy the repo URL and paste it here, which I can do right now. I can paste it here. There we go. And now we have the API keys. So, Anthropic, Eleven Labs, Voice ID, all that stuff. You can go and copy each one. All right, I just pasted all my credentials here.

**13:50** · Make sure you go through each one step by step, and you can also just copy this whole thing, paste it into ChatGPT and ask it, "Hey, what are some things that I need to replace?" And you can go back and forth, uh which is fine. And we have this at the end as well. Okay? Now, in the doc that I'm going to give you, it has all the instructions as to what the network is. It will tell you all the different naming conventions of these different variables that we have to put here. Okay? Once you're done, you can copy this whole thing. We can go to the terminal. Again, you can put exit here.

**14:17** · And the first thing we want to do is we want to make a folder and open a file editor. So, we do this by pasting this command right here.

**14:23** · Just copy everything step by step. mkdir p docker lead up docker lead up and nano docker-compose.yml um for us to be able to do this. And then we can press run. And then here we can include all the different ENVs and all the different passwords and keys and all that stuff. Okay? So, paste this whole thing from the Google Doc that we made.

**14:42** · And then once you have this here, you can press control O, enter, control X, and we're back here. And then all we have to do is paste this right here. docker-compose up -d. And now you can see it's pulling up the document. It says plus 12 out of 12 container lead up. Okay, started, pulled. Okay, cool. So, that's all good. There's one more thing we have to do in terms of the terminal. We going to have to paste this uh thing right here, which is going to allow us to take the code, clone it, and actually use it inside the agent. I can press run. All right, cool. So, if you see Hermes agent listening on 0000 3000, that means that the agent is now live.

**15:15** · So, Hermes agent, Claude code, GitHub, all the softwares are connected and we're good to go. The last step here is the Typeform. So, we got the scopes, but all we have to do now is actually create the webhook so that when we fill out the form, it sends the data directly into the system itself. So, you go to the form, you go to connect, you go to webhook here. You press add a webhook. And then here, you want to go back to the actual thing here. You want to copy everything up until cloud.

### Connecting the Webhook to Typeform

**15:45** · Paste it here and put {slash} webhook {slash} Typeform. And press save form or save webhook.

**15:53** · Turn this on.

**15:55** · And now, we can test it. Moment of truth. We can test it. If it doesn't work, we'll fix it. If it does, amazing. All right, finally, we want to paste this command right here to watch this live and we can now run the actual Typeform. So, we go here, start, name this James Michael. Okay, I'll put my phone number here. I'll put my email here. Press okay. I need roofing services.

### Live Test: The Ultimate Speed-to-Lead Voice Demo

**16:17** · That's fine. And then, my roof is leaking. I can press okay. Dallas is fine. And then, this week, submit. All right, so as you can see, I'm getting a call from the agent right now on the screen. Hopefully, you guys can hear it.

**16:32** · Hi James Michael. This is Hermes from Home Inspection Pros. Thank you for reaching out to us. Can you tell me a bit more about the issue or the inspection you need help with?

**16:40** · Yeah, my roof is leaking. It's broken.

**16:42** · There was a storm the other night. We need this done ASAP.

**16:45** · Got it. I understand. We'd love to get an inspector out to you as soon as possible. What day and time work best for you?

**16:52** · Um tomorrow.

**16:53** · The earliest available slot I have is Tuesday, June 9th at 3:30 p.m. Would you like me to book that for you?

**17:00** · Sure.

**17:00** · yes or no.

**17:01** · Yes. Yes, that's fine.

**17:02** · You're all set. Your inspection is booked for Tuesday, June 9th at 3:30 p.m. Our inspector will be there on time. If you need to reschedule, just give us a call. Have a great day.

**17:13** · Boom, done, finished. Let's go. We can see it on my calendar right here. Everything else is blurred, but we have the free property inspection at 3:30 p.m. my time, James Michael, uh with my email as well, and my phone number, too.

### Packaging, Pricing, and Selling AI Systems to High-Ticket Clients

**17:24** · All right, so back to it. There's one more thing that I want to show you, uh which is the packaging, pricing, and selling it to businesses. So, one important concept about the system is that it is kind of based on how much a lead is worth for the business. Because if we are converting more leads, we have to understand what is the number, what is the amount that the lead is worth for the business. And so, you can charge anywhere from 3K all the way to 20K for the system. Because if a lead is worth a lot more for Y business than X business, you can charge them a lot more. And that's exactly how it works with these kinds of clients.

**17:53** · Now, in terms of packaging, your offer can literally be as simple as we build a speed-to-lead voice system that calls and qualifies your ad leads in under 5 minutes and books them into your calendar without hiring extra staff or changing your ad setup, completely done for you. And like I mentioned, in terms of pricing, you can either charge per booked appointment or you can charge a setup fee plus a monthly retainer, which can be anywhere from a 3K setup fee to a 10K setup fee and a 1 to 2K a month retainer as well, depending on the business. All right, so there we there is a full build.

**18:21** · You've now taken two softwares and you have built a working agents that businesses are actually willing to pay thousands of dollars for. Uh but that's the build, right? The build is the easy part. The hard part is not so much can we build this, but it's can we sell this and get clients, which is exactly what I'm covering in my free live workshop later this month. If you want to check it out, you can check it out in the second link down below. It'll be there. You can apply and I'll see you there. All right, and once again, if you guys want the resources and templates and prompts of this whole video, then check it out in the link down below in my free school community.

**18:53** · Uh you can go to the classroom section, you can go to the templates vault, and you'll find everything there. And now that you've actually built and packaged one specific offer for a business, check out this video on the screen where I show you 20 AI agency offers that actually make money in 2026. With that being said, I really hope you guys found value from this video, and as always, I'll see you in the next one.