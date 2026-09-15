---
title: "We Open Sourced World Generation"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=eJuYBNrD8HI)

You can now turn a single image, or just a text prompt, into a fully explorable 3D world. Locally. For free.  
  
If you like my work, please consider supporting me on Patreon: https://www.patreon.com/Mickmumpitz  
Follow me on Twitter: https://twitter.com/mickmumpitz  
  
You can find the FREE WORKFLOWS here: https://www.patreon.com/Mickmumpitz/posts/167647096  
INSTALLATION GUIDE ComfyUI: https://mickmumpitz.ai/posts/comfyui-getting-153738117?l=de-DE  
You can find the ADVANCED WORKFLOW, GUIDE & EXAMPLE FILES here: https://www.patreon.com/Mickmumpitz/posts/167646149  
  
We spent weeks building a pipeline that turns one 360 degree panorama into a full Gaussian Splat scene. Along the way we tested Apple's SHARP, Insta360's UniSHARP, Tencent's HY-World 2.0 and NVIDIA's Lyra before landing on Matrix-3D, which we rebuilt from scratch as custom ComfyUI nodes.  
  
The core idea: you pilot a virtual 360 degree drone through your scene to draw the exact path the AI should invent. Wan 2.1 then hallucinates everything the original photo never saw, including entire rooms on the other side of a wall. Instead of upscaling the 720p result, we reproject the original 8K panorama back onto the generated video using the camera data we already have, which is sharper and faster than running SeedVR2 over everything.  
  
The output is a standard COLMAP dataset, so you can take it into any Gaussian Splatting trainer you like.  
  
🎯 WHAT YOU'LL LEARN:  
\- What a Gaussian Splat actually is, and why spherical harmonics keep reflections alive  
\- Why single image models like SHARP fall apart the moment you start moving  
\- How Skywork trained the Matrix-3D LoRA on 116,759 panoramic sequences rendered inside Unreal Engine 5  
\- How to generate seamless equirectangular panoramas from text, or expand a single photo into a full 360 environment, with the two Krea 2 LoRAs I trained  
\- How to fly custom drone paths and build a synthetic training dataset in ComfyUI  
\- How to train the final splat in Brush  
  
⚡ MODELS & TOOLS COVERED:  
\- Matrix-3D by Skywork AI  
\- Wan 2.1 video model  
\- LightX2V speedup model  
\- MoGe for scene geometry  
\- Krea 2 plus two custom 360 LoRAs  
\- SplatKit custom nodes for ComfyUI  
\- Sage Attention and Triton (plus our patch for 2x1 video)  
  
🔗 TOOLS:  
\- ComfyUI https://www.comfy.org/  
\- Matrix-3D (Skywork AI) https://github.com/SkyworkAI/Matrix-3D  
\- Matrix-3D Project Page https://matrix-3d.github.io/  
\- Matrix-3D Paper https://arxiv.org/abs/2508.08086  
\- Wan 2.1 https://github.com/Wan-Video/Wan2.1  
\- LightX2V https://github.com/ModelTC/LightX2V  
\- MoGe (Microsoft) https://github.com/microsoft/MoGe  
\- Krea 2 Technical Report https://www.krea.ai/blog/krea-2-technical-report  
\- LichtFeld Studio https://github.com/MrNeRF/LichtFeld-Studio  
\- Brush https://github.com/ArthurBrussee/brush  
\- Postshot (Jawset) https://www.jawset.com/  
\- COLMAP https://colmap.github.io/  
\- SageAttention https://github.com/thu-ml/SageAttention  
\- Triton https://github.com/triton-lang/triton  
\- Poly Haven (free HDRIs and 360 images) https://polyhaven.com/hdris  
  
🔬 ALSO TESTED IN THIS VIDEO:  
\- Apple SHARP https://github.com/apple/ml-sharp  
\- Apple SHARP Project Page https://apple.github.io/ml-sharp/  
\- Apple SHARP Paper https://arxiv.org/abs/2512.10685  
\- UniSHARP (Insta360) https://github.com/Insta360-Research-Team/UniSHARP  
\- UniSHARP Project Page https://insta360-research-team.github.io/Unisharp-website/  
\- HY-World 2.0 (Tencent Hunyuan) https://github.com/Tencent-Hunyuan/HY-World-2.0  
\- NVIDIA Lyra https://github.com/nv-tlabs/lyra  
\- SeedVR2 https://github.com/ByteDance-Seed/SeedVR  
\- Marble (World Labs) https://marble.worldlabs.ai/  
  
⏱️ CHAPTERS:  
00:00 Intro  
00:50 Inspiration  
01:50 Gaussian Splatting  
03:05 Apple SHARP Experiments  
04:00 The Search 04:40 Matrix-3D  
05:00 Highres Fix  
08:00 Tutorial: 360 Panoramas  
11:30 Tutorial: Synthetic Dataset Creation  
15:45 Training a Gaussian Splat  
  
🎨 PERFECT FOR:  
AI Filmmakers, Virtual Production, Previz Artists, Game Environment Artists, VFX Supervisors, Concept Artists, VR Creators, Museum and Heritage Projects  
  
🙏 SPECIAL THANKS:  
Massive thanks to our Patreon supporters, who are the reason we can spend weeks on R&D and then give the pipeline away for free. And huge thanks to the researchers and open source teams publishing their papers and open weights models. None of this would exist without Skywork AI, the creators behind MoGe and Wan 2.1, and the wider open source community.

## Transcript

### Intro

**0:00** · Imagine feeding your computer one image and watching AI generate a full 3D environment for you, all locally and free. With all the crazy progress in AI, you'd think that generating a 3D world should be pretty easy by \[music\] now, right? But instead of finding a quick solution, we ended up spending weeks building our own custom pipeline and ComfyUI node pack.

**0:19** · Along the way, we tested completely different approaches, dug through a lot of dense research papers, and found a couple of techniques that almost nobody is using \[music\] yet. The final method we landed on even involves piloting a virtual 360° AI drone to map out your scene, which is insanely fun. But before we fly drone, this video and the free workflows are made possible by our amazing Patreon supporters. If you want to get your hands on an advanced guide, the example files, and beta workflows, as well as our amazing Discord community, consider supporting and thanks for making weeks of R&amp;D possible.

**0:49** · Ever since I started this channel, I've been obsessed with the idea of generating entire worlds. 3 years ago, I actually hacked together a workflow for this. Like, I generated a 360° image, projected it onto a sphere, estimated the depth information, and distorted the sphere to create a rough 3D environment.

### Inspiration

**1:05** · I even generated deflickered normal map so I could relight myself in the scene.

**1:09** · Now, it's all very clumsy, but at the time I thought it was pretty cool. And having a 3D environment like this to ground your scene has so many different applications. For example, in virtual production studios, or if you want to make AI movies. You could even build like a dummy scene like this in Blender with holdout characters to get your blocking exactly right.

**1:25** · So, this is my garden. I put a lot of effort in it. Should I show you around?

**1:30** · Grandpa, I live here, too.

**1:32** · Now, what inspired me to get back into this project was Apple's December 2025 release called Sharp Monocular View Synthesis in less than a second. You just give it a 2D photograph, and in one single pass, a neural network predicts an entire 3D Gaussian representation of that scene.

**1:48** · But wait, what actually is a Gaussian splat? In traditional 3D photogrammetry, you would take hundreds of thousands of pictures of your location, and the software then calculates the camera position and the final geometry as a polygon mesh. And that's like fine for like walls and buildings and stuff, but for soft things like hair, foliage, or even for like reflective or transparent surfaces, it will break. But Gaussian splatting throws out polygons entirely.

### Gaussian Splatting

**2:11** · Instead, the scene is a cloud of millions of tiny semi-transparent 3D blobs, and technically they're called ellipsoids, and each one of them stores a position, a size, a rotation, and an opacity. For color, it uses a math function called spherical harmonics, which is just a really fancy way of saying that the color and brightness change depending on the angle you look at the blob. And this is why all the like the specular and reflective properties of the scene still work using Gaussian splatting. And because there's no ray tracing or shaders, it's also super lightweight and runs in real time even on an iPhone.

**2:42** · To train a Gaussian splat, an optimizer looks at all the blobs in your scene and adjusts their values until they match every camera position and image in your data set. And this can take a long time, so Apple doing it in like a second is really cool. But there's a catch. Apple's model can only turn a single image into 3D, but I want an entire 3D scene. So I had an idea. What if we take a 360° panorama, slice it up into multiple views, and then run Apple's sharp on each of them individually and stitch them all back together.

### Apple SHARP Experiments

**3:12** · Turns out it's not that easy. Like some angles, some parts of the scene look really good, but since everything generates individually, you get these really ugly seams. So my next idea was to estimate the scene geometry first using a model called Mogi, and then use it to correct and line up the different views by Apple sharp. And I was actually making some really good progress on this, but I ran into two problems that killed this approach. First of all, it's not flexible enough. Like the scene looks good from the initial perspective, but once you start moving around here, it's falling apart.

**3:41** · And that's because sharp is designed to preserve the scene and not to generate too much new detail. And second, the license. I want to build a tool that is permissive, that our audience of small studios and individual CG artists can actually build upon and use for their commercial work. So, I went looking for another solution.

**3:58** · UniSharp is a research project by Insta360, and it's basically the same idea as Apple's project, but for 360° world. It's super fast, but unfortunately, the world's fall apart really quickly once you start moving.

### The Search Matrix-3D

**4:12** · Still a lot of fun to try out though, and there's even like a hugging face demo if you want to try it in your browser. Next, Honai and 2.0 looked really promising, but it demands two massive models loaded into memory at once, and it's designed to run on four GPUs. So, um next, then I tried Nvidia's Lyra. I actually managed to get it running, but it's 91 GB of checkpoints, Linux only, and starting it the first time uh took 6 minutes alone. It's really cool, but not really for consumer hardware.

**4:38** · But then I followed the white rabbit and found Matrix 3D, which is not a PS2 tie-in game for the movie. It's actually a really smart piece of engineering. You start with a single 360° panorama, estimate its depth, and then turn it into a rough 3D mesh. When you now move a camera through that mesh, it of course breaks, falls apart, because anything the original photo couldn't see becomes this black hole. But then you feed this into the 12.1 video model, which then hallucinates all the missing pieces and more.

### Highres Fix

**5:08** · Skywork did two brilliant things here. First of all, they used a nice mix of real 3D geometry with clever inpainting to maximize consistency, and second of all, they didn't train a whole new model for this.

**5:21** · They just trained a lightweight Laura on top of the 12.1 video model. But to train that Laura, they needed a massive data set of 360° video with perfect camera tracking along custom paths. And since that didn't exist, they built it themselves inside of Unreal Engine 5.

**5:37** · They programmed a virtual 360° drone to autonomously fly through 500 different video game environments hundreds of thousands of times. So, using the model that they trained, we can now set our own custom path, and the model will generate perfect 360° videos. So, what I find strange about this paper is that it dropped in August 25th, but almost nobody built anything around it. Maybe because it's not that easy to install.

**6:01** · So, we rebuilt the entire thing inside of ComfyUI. Getting it to work was a bit tricky, like the Laura didn't match ComfyUI's format, and we had to build a few custom nodes for it to work. But, once we converted everything, we realized we could use this with a Light X2B speed up model, which massively speeds up render times. We also built our own custom path editor on top of it.

**6:21** · This gives you a top-down and side preview of your scene, letting you become a virtual drone pilot. And one funny thing is that you can even fly through walls. The model will actually generate a new fitting scene on the other side. But, I can instantly tell the resolution is too low. And that's because one maxes out at 720p video, and imagine stretching this across a full 360° field of view. So, if we trained a Gaussian splat on this data, the structure would work really well, but you can see it's like really soft. The first thing we tried to improve this was upscaling all the different views using Seed VR.

**6:51** · And this helped, but it's so slow, and it also didn't do too much.

**6:56** · So, I figured it was time for some industrial espionage. I checked out Marble by World Labs, a closed-source model for generating 3D worlds. And I was really impressed by how fast it was and how crisp the results were. But, you can see the movement area is still really restricted, and there are also no working reflections, which is something that I would really like to keep. But, that gave us the idea to reproject the original high-quality renderings onto the Mogi environment. All the drone shots we created start from the same position. And for this position, we have a high-quality image.

**7:26** · So, what if we just reproject the original high-resolution image back on top of the 360° videos at a high resolution. I mean, we have the camera data and the 3D environment, so in theory, we should know exactly how every single pixel moves. And this worked so well. The transitions between full resolution and one are now much smoother, and overall quality improved dramatically. So, let me show you step-by-step how you can run this on your own computer.

**7:56** · First, we need a 360° start image, and this can be a real image you download from Poly Haven or take yourself with a 360° camera, or you can generate this image. There are a lot of AI tools that can do this, but I created this free Creality workflow. So, once you started ComfyUI, just drag and drop the workflow into the ComfyUI interface, and install the missing custom nodes. Now, you need to come to the left here and download these models.

### Tutorial: 360 Panoramas

**8:22** · And you can find all the download links for the models and where to put them in your ComfyUI folder structure right in these nodes to the left of the model order nodes. You'll also need these two LoRAs right here that I trained for this workflow. And of course, these will be download links once I publish this video. So, let's come to the top here. If this is set to true, the workflow will create a panorama based on your text prompt. If it's set to false, you can upload your own image. So, let's start with the text prompt.

**8:48** · For this, I created my own 360° Creality LoRA by showing Creality 2 hundreds of different images of 360° images so the model could learn what they look like. The trigger caption for this LoRA is this beginning right here, so leave that, and after that, you can fill out your own prompt. Right now, it's this creepy cave here, so maybe let's just try that and click run. And what will happen then is first, the image will be created, but sometimes the seam is not perfect, so this second group right here fixes the seam.

**9:19** · And you can see that pretty well here in the preview. \[clears throat\] So, it only regenerates this seam area right here.

**9:27** · Once that is done, you have a seamless image, but it's not high resolution enough, so it gets fed into this group right here, and this is the upscaling group. You can find all your saved out panoramic images in ComfyUI output panorama and uh then there they are. And below here, you also have this preview node that allows you to just take a look around. But it's a bit creepy, so let me try something else. Maybe like this Alpine Village.

**9:54** · Click run. And here you can see the seam fix working really well, so it's only denoising that part of the image. Now, let me stop this and change the upscaling prompt. Usually, you should keep this very uh simple. For now, I will just change this to high-resolution photography and don't even put in uh scene detail. And yeah, this scene looks so cool. I love that it added this little cute pond here and the windmill.

**10:15** · So, all of my elements in the prompts are here. But maybe you already have an image and you want to generate the full environment around that. For this, go to the top here and change the workflow mode to folds. And then come down here to this red group. Upload an image right here. And what will then automatically happen is this image will be distorted according to the lens and placed on this green background. Now, I created a dataset of thousands of these crops in front of a green background with the corresponding real 360° image.

**10:43** · Over the course of 16 hours, I was able to retrain Creaya 2 to understand that if it sees an image like this, it should replace only the green with the rest of the scene as 360° image. So, now all you need to do is come here to this prompt group and describe the surrounding scene. And if we click run, you can see that the middle stays the same and then around that there is the village. And here you can see the seamless image.

**11:10** · But of course, some areas look really weird because they are stretched out like that. So, make sure to check them out in this node right here. The lamp, for example, doesn't look half as bad. And here's the part of the original scene that it kept really well. Now that we have our panorama, we can drag and drop in the dataset creation workflow into the ComfyUI interface. Again, make sure to install the missing custom nodes, especially Splat Kit and the Make Mopeds node, and then come to the left of the workflow and download all these models and put them in the correct folder in your ComfyUI folder structure.

### Tutorial: Synthetic Dataset Creation

**11:43** · Double-check if the correct models are loaded in this model loader group right here. And then you can upload your image right here. Below the image, you can set an output folder for your scene. Next, scroll to the right and on this node, click compute geometry. Now you get this rough preview of your scene from the top and from the side. This little star here is the starting position of your drone.

**12:06** · And now you can just change these paths and send the drone off to different areas in your scene. There are different modes. Let's start with the look forward mode. Here the drone will just always look in the direction of the path. But you can also change it to per point look, and then you have these yellow points right here, and you can actually make the drone look in different directions. And I'm sending the drone into this alley here. We can also change the height a little bit, so maybe we want to to go a bit higher.

**12:37** · And once you have set the path, you can click on the save video node right here and click play. This will then give you this preview video right here, so you can check out if the camera is flying in the correct way. And you can see I'm crashing into this building here, so let me fix that. Ah, right here. That was a mistake. So I want to keep flying forward like this.

**12:59** · So this looks pretty good. Now let's scroll down to this next drone right here. This one I want to send off in a different direction. Maybe this one's circling around the pond in the middle of the market square here. And yeah, pretty pretty close to that house, but this works. And let's create the next drone. And maybe let's make it fly like really high up. And this looks pretty cool.

**13:24** · We're flying way up in the air before crashing down into this alleyway. And you can really be creative with your camera paths here. Make sure to capture the areas that are important to your scene. Now we have four different drones flying through that village. And if you want to add more, you could unmute this group right here. And every time you run this, this clip will be added to the data set. But these four clips are usually more than enough. So now what we can do is just click run.

**13:52** · And this will then get sent over to the One Inpainting group where all the missing pieces will be filled in with the One video model and the Laura. And this looks pretty cool. Like it invented the roofs. All this is not in the original image. Okay, I might have overdone it with this camera move. That's a bit too crazy. But one cool thing you can see here is that the pond is actually not just a flat surface, but it's reflecting. So it's actual water. And so if we train the splat, the pond will also have reflections.

**14:22** · Oh, and since this workflow is One based, you can do all the typical optimizations that you can do with the One video model. For example, you can install Sage Attention and Triton, which are ways to speed up the workflow immensely. Uh we have free installers that will set everything up automatically for your ComfyUI installation. Make sure to check that out. But it's important that if you use it with this workflow, that you also install the Sage Attention patch because otherwise it will break the workflow and it will generate only black frames. So if you get any black frames, make sure to install that one as well.

**14:53** · Once the final video is generated, it is fed into the high-res composite where the original 8K texture is projected back onto this video. Now here are a lot of settings, but you don't need to change anything here. If you want more information, you can find this in the advanced guide. But usually for this workflow, you just drag and drop your image, set the output folder, create your paths, and then you can just click run and leave the workflow alone. The final step, once all these videos is done, it will get fed to this node right here.

**15:23** · Again, you don't really have to do anything and this will build your actual data set for training. So, it creates different views from these panoramic videos in the cool map format, which is a format that most Gaussian Splat trainers can understand. Once it's done, you can come to your ComfyUI output folder and here you find the folder with all the information that you need for training. Now, you can take this data set to pretty much any Gaussian Splat trainer that you like. There are some great paid ones like Postshot, for example.

### Training a Gaussian Splat

**15:50** · We used a lot of Lichtfeld for training, which is an open source tool, but the easiest one is probably Brush.

**15:58** · To install it, you just need to go to the GitHub page, click on releases and down here you can find the different versions. Go into the folder and start the app. Now, I can click directory, go to output and select the Bavarian Village that we just created and now we have a few settings. But for now, I don't change anything and I just click start. And now it starts training and you can see on the top here, you can see the Gaussians point cloud and down below, you can see the actual image that this view is training against.

**16:29** · Now, training's only like half done yet, but we can already start floating around and exploring the scene. Now, you can see the areas where we sent our drone to look better than the rest of the scene, of course, because these are mapped out properly. If you want like a really high quality large scene that you want from multiple angles, just send in a few more drones and map out this area even more.

**16:54** · And here is the Italian like alleyway that we generated earlier as well. So, just so you see some realistic scene as well. Again, thank you to our lovely Patreon supporters for making this possible. As an additional thank you for your support, our advanced Patreon supporters get a super in-depth step-by-step guide for this whole process, all the example data and splats we trained and the workflow files we created for this video, as well as the advanced and beta versions of this workflow. Right now, for example, we're playing around with segmentation to improve quality of reflections.

**17:23** · Massive thanks also to the amazing researchers and open-source teams publishing their papers and open weights models. Projects like this truly stand on the shoulders of open research, and none of this would have been possible without the incredible work coming out of teams like Skywork AI and the creators behind Moge and Wand 2.1. And, of course, the entire open-source community. So, thank you to you all, and thanks for watching. See you next time.