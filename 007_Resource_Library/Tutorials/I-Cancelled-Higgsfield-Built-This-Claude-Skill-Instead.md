---
title: "I Cancelled Higgsfield & Built This Claude Skill Instead"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=P7Aruo5J3BQ)

👉 GET THE SKILL HERE: https://skool.com/vic  
\*\*\*The file from the Video is in my Free Skool Community within the 'Classroom' section  
  
Higgsfield AI is a super popular AI tool that lets creators generate images and videos. It's pretty expensive, and most times creators waste credits on a monthly plan. I built the core components of Higgsfield in this Claude Skill and show off what it can do here in this video.  
  
Secret Sauce: https://fal.ai  
Free Skool: https://skool.com/vic  
Instagram: https://instagram.com/systemsbyvic  
TikTok: https://tiktok.com/@systemsbyvic  
All other links: https://viclaranja.com  
  
Subscribe for more! 🚨  
  
#AI #Creator #HiggsfieldAI

## Transcript

**0:00** · I rebuilt Higgs field using Claude code.

**0:03** · this is saving me personally over $100 a month.

**0:08** · I was using Higgs field actively for about six months.

**0:11** · and really I was just using image generation.

**0:14** · then using some of the video models to turn those images into videos, and that's pretty much so now instead of paying $100 a month or more.

**0:22** · I'm using one API key that ties into Claude code.

**0:26** · That generates whatever I want, I only pay for what I So I actually created a Claude skill to do this.

**0:34** · And if you stick around until the end of this video, I will give you that Claude skill completely for you don't know who I am, my name is Vic. Creating content is my business.

**0:42** · I've gotten well over 100 million views.

**0:45** · I've made millions of dollars as a professional creator.

**0:47** · this channel is all about providing AI systems for human creators.

**0:52** · if that sounds like something you want to be a part of, make sure you subscribe.

**0:55** · All right.

**0:55** · So I got the Claude desktop app open, and I'm going to trigger my media gen skill.

**1:03** · the media gen skill can do a bunch of different things.

**1:06** · First off, it can generate an image based just off of a description.

**1:11** · Now, the way that I programed it is pretty interesting.

**1:14** · So I'm able to just kind of tell Claude my general idea.

**1:17** · And then Claude goes in and writes my prompt for me in a way that it knows the image generation model will understand the best.

**1:27** · So let's try an example here.

**1:28** · Generate me an image of a dog that is dressed like Superman, and is also playing some sort of game console, maybe like a Nintendo Switch, make it really cool.

**1:41** · I want to use Nano Banana two because that's the best image generation model on the market, and want it to be a square image and absolute max quality that you can right.

**1:51** · So that came out of Whisper Flow.

**1:53** · We'll hit now Claude is cooking in the back end.

**1:56** · here it is rewriting my prompt for It says a photorealistic studio portrait of a golden retriever wearing a tailored Superman costume, the iconic red cape draped over its shoulder.

**2:07** · So it's like, literally take took my garbage prompt and made it an amazing prompt for And now it's running Nano Banana Pro 1 to 1 ratio at max 4K resolution.

**2:18** · Image gen is cheap, so to generate this image probably gonna cost me like $0.08, maybe a little less, which is way less obviously than what you would have paid if you had a Higgs field subscription.

**2:27** · And another really cool thing about Media Gen is that it will create a media gen folder in your documents, and then it will actually save everything locally for Okay.

**2:36** · We got an image back and it gave us our file path.

**2:40** · So I'll just open that And here's our image of a dog in a superhero outfit playing a Nintendo Switch.

**2:48** · And this is this is dialed.

**2:50** · I really like it.

**2:51** · It came out super But we can also provide images to Claude as reference.

**2:55** · And it knows how to handle these images in a way where it doesn't destroy them.

**2:59** · So sometimes if you give a picture of yourself, you'll come out as like another person.

**3:04** · This knows how to handle reference images. I've programed it like that.

**3:07** · I work with it a So I'm going to try to pull off is I'm going to take this image of Trump where he's like got grills on and I'm gonna make that Christiana Ronaldo.

**3:16** · I want Cristiano Ronaldo with all the grills and stuff like that.

**3:19** · So let's see if we can pull that off I'll drop both images here.

**3:22** · I'll also have to get the file path for each of them.

**3:25** · or else I will know where to download from.

**3:26** · let's give it a okay.

**3:27** · So the first image is Christiana Ronaldo.

**3:30** · The second image is Donald Trump.

**3:31** · And Donald Trump has like grills and a watch and you know, has this kind of rapper thing going on about basically want to replace Trump with Ronaldo and I want him doing the same pose.

**3:44** · I want him having the same jewelry.

**3:45** · I want him still looking like a rapper with the black background.

**3:48** · Everything about the Trump image should be the same, but it should be Ronaldo instead.

**3:51** · So again, if you do give it an image as reference, give the file path so it knows where to source the file from, download the file and provide it to nano nano banana Pro Max quality one by one ratio.

**4:04** · So I'm always going to tell the skill what model I want to use to make sure it uses the right model, but it will probably suggest the best when we get into video models, this matters a little more because the cost differences are pretty big, when we're talking about images, it's pennies, so it's not a big So it's using the Nano Banana Pro edit model, which allows Claude to actually edit the images that we provide it.

**4:27** · So it has to change models, but still nano banana Pro.

**4:30** · Okay, result is coming in now we have the Goat Ronaldo grilled he's also still wearing the suit Trump suit which is pretty funny.

**4:39** · But I mean that looks pretty okay.

**4:41** · So Claude knows that I typically convert images to videos.

**4:45** · That's what I like to do in some of my so saying do you want to animate it into a video.

**4:50** · So I'm going to tell it for Animate this into a video.

**4:53** · Use cling three.

**4:55** · No audio max quality only do three seconds.

**4:58** · So the video models actually charge per second.

**5:01** · So I would be pretty precise about how long you want these videos to the difference between like a five second video and a ten second video is a few dollars.

**5:08** · Sometimes I like to use cling three because it's the best, cheapest model.

**5:13** · could also use Seed Dance two, but Seed Dance two is definitely way more expensive.

**5:19** · Now, the really dope thing about this is that we're actually using file AI as our API call, which always has the best model.

**5:27** · So even when a new model comes out like cling four or whatever, in the future we'll be able to use it without actually changing the skill, because all we got to do is prompt it for that model.

**5:37** · So this is file AI and you will need to go and make an account for this to work because you'll need an API key.

**5:43** · They don't have any free credits available.

**5:45** · So you do actually have to pay per use.

**5:47** · But if you have like $10 or $20 on here, this will last you a long time.

**5:52** · If you're just generating images and videos here and there.

**5:55** · But you can see here they have the best models out.

**5:58** · They have seed dance two, nano banana two, cling three.

**6:02** · Happy horse which is newer pics.

**6:04** · Verse six dab nano banana.

**6:06** · Edit like they have flux, they have everything you need.

**6:08** · So Falei definitely is amazing at bypassing Higgs right.

**6:12** · So now we know the secret sauce.

**6:14** · Let's tell Claude to animate this video and see what the video looks like.

**6:18** · So a really cool thing is that it will actually tell you how much it's going to cost before you run it.

**6:24** · So it's telling me $0.34 for three seconds, one video, it's also giving me the prompt before it runs it and it's asking me to confirm.

**6:33** · So I will Okay.

**6:35** · So we did actually get an error.

**6:36** · And that's because the specific model cling three that we're using can't handle image files over ten megabytes.

**6:43** · So Claude recognized that it on its own compressed the image to a 1.4MB size.

**6:50** · And now it's rerunning the image completely on its own.

**6:53** · that's just a limitation on cling which Claude handled on its here is the video.

**6:59** · Let's take a look.

**7:02** · So just a three second animated video.

**7:05** · It looks crazy.

**7:06** · Just shaking her head.

**7:07** · No like no bro, you don't get okay.

**7:09** · So cling output this at 1080.

**7:12** · But what if I want to upscale two 4K.

**7:14** · Well I can actually do it right in this skill using the Topaz upscale video model which is also built right into file.

**7:23** · right.

**7:23** · So I'm just going to tell Claude upscale this to A2K resolution.

**7:28** · Using Topaz should be built right into the skill.

**7:31** · If it strips the audio that's fine.

**7:33** · I don't need the audio, but if it keeps it, whatever, that's okay So now that's moving.

**7:37** · this is going to cost us $0.24 to upscale, which is really not a Topaz subscription for the year is like $400 or something. Bro.

**7:48** · $400 for Topaz.

**7:50** · And I just used it for $0.24.

**7:54** · Come here is the upscaled video.

**7:57** · Like you can see like the quality is actually drastically better here.

**8:02** · The detail in his hair, the detail in his face.

**8:04** · definitely looks like a much better render.

**8:07** · this comes in handy especially if you download some like low quality video off of YouTube or something.

**8:12** · And you need upscaled, drop it right into Claude and say upscale.

**8:17** · This like it doesn't need to work with just your generations.

**8:19** · It can work with any video at all.

**8:22** · So installation on this is so easy.

**8:25** · All you need to Is come over and join my free school community.

**8:29** · Click classrooms up at the top and go to AI automations, and you will find this video and the file to download.

**8:36** · It's a zip file.

**8:37** · You just literally drop the zip file in Claude and tell it to download it.

**8:41** · It's a skill. It will know exactly what to do it.

**8:43** · If you don't trust it, then just ask Claude to scan it for security first.

**8:47** · I always do that with anything I put into Claude to download.

**8:49** · I say scan this for security and then I install it.

**8:52** · So you can do that if you then you'll need to load up some money on file AI.

**8:55** · Get your API key which is very simple to find.

**8:59** · You literally just click your image up at the top and go to API keys and create a new API key.

**9:03** · Claude will tell you exactly where to put that key.

**9:06** · It's probably in an envoy file. Don't give it to Claude.

**9:09** · Get Claude to tell you where to put then it will just work and you can do it ever you want with this skill completely for free.

**9:16** · All that I ask is that you join my school community, subscribe to the channel, turn on notification bells because I am dropping more dope skills just like this.

**9:24** · take your creator business to the next level.

**9:27** · My name is Vic.

**9:28** · Thank you so much for watching and I will see you in the next one.

**10:52** · You. Do.