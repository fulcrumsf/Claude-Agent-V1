---
title: "LTX 2.5 BBox Animator is AMAZING! Control any Object in ComfyUI"
tags:
  - Guide
created: 2026-09-13
---

![](https://www.youtube.com/watch?v=gMdnCfUYSp0)

Take precise control of your LTX 2.5 videos with BBox Animator IC-Control LoRA in ComfyUI!\*\* In this tutorial, I show you how to control the position and movement of objects using animated bounding boxes with LTX 2.5  
  
Instead of relying completely on the AI to decide where subjects move, BBox Control lets you guide individual objects through the scene giving you much more control over your image-to-video generations.  
  
In this tutorial I cover downloading the BBox Control lora and installing the node and using the Bounding Box.  
🎬 Text-to-Video (T2V)  
🖼️ Image-to-Video (I2V)  
  
This is the best motion guide or motion path tool for LTX 2.5!  
I'm using the distilled GGUF version of LTX-2.5, which makes this especially interesting for those of us running AI video locally without the latest high-end GPUs.  
  
  
  
  
If you're into local AI video generation, ComfyUI workflows, GGUF models and getting the most out of your GPU.  
  
Installation, Setup, Configuration, Workflow, Automation, Python, Script, Coding. Guide, Course, Masterclass, Professional, Advanced, Editing, Design.  
Make videos for Business, Monetize, and make a Passive Income.  
earning AI easy. Image to AI video Tutorial. Anything is now possible with this updated node  
  
https://huggingface.co/Abiray/LTX-2.5-GGUF/tree/main  
https://huggingface.co/realrebelai/LTX-2.5\_GGUFs/tree/main  
https://huggingface.co/EllaPriest45/LTX2.5\_base/tree/main  
https://docs.comfy.org/tutorials/video/ltx/ltx-2-5  
https://ltx.io/model/ltx-2-5  
  
lora  
https://huggingface.co/yuvraj108c/LTX-2.5-22b-IC-LoRA-BBox-Control  
node  
https://github.com/yuvraj108c/ComfyUI-LTX-BBox-Animator  
  
workflows  
https://drive.google.com/file/d/16dQZV6Om48BHKk\_sqVYNknD6nuSaFkNw/view?usp=sharing  
  
  
prompt director pro  
https://www.patreon.com/posts/prompt-director-150726418?utm\_medium=clipboard\_copy&utm\_source=copyLink&utm\_campaign=postshare\_creator&utm\_content=join\_link  
  
https://www.heygen.com/?sid=rewardful&via=doggis  
  
Buy me a Coffee! http://coff.ee/ailatetoclass  
https://www.patreon.com/cw/ailatetoclass

## Transcript

**0:09** · Hi, welcome to a quick AI light to class new tool tutorial LTX 2.5 bounding box control Laura and node. This node and Laura allow you to upload an image draw a box or boxes around items in the image and guide their motion path with editable key frames. This is the most accurate motion guide path tool I've seen yet and you can even save templates for the repetitive task that you may want to apply to multiple images. It can also do text to video and here's the global prompt separated from the region similar to prompt relay.

**0:38** · It's a very easy install and download so stay watching. If you haven't got LTX 2.5 running go to my channel and watch this video. It'll show you everything you need to know. Firstly, you need this B box animator node to work with the B box Laura. So come over here, click on copy, go to your custom nodes folder inside comfy UI and get clone in there. As it says here, draw, resize and animate boxes. You've got regional prompting for those boxes.

**1:06** · You can change key frames sort of like if you're using Adobe After Effects. You can move forward and change a frame or go back delete frames. Got multiple objects moving and you can save anything you do as a template and you can bring in your reference images so it's not guesswork. You can actually see it working. Here's a guide for your global prompt. First you've got the style. It's got your visual style lighting camera and color treatment and then it's got scene underneath environment and seating. We are number general type of objects.

**1:39** · In my one I've just got a 1950s scene so I've described that in there. They've got their example underneath. Then you've got your regional object prompts. Object one, a businessman wearing a tailored charcoal gray three piece suit.

**1:54** · Object two, a businesswoman wearing a fiery scarlet red silk dress. Here's the lore on hugging face. You can see these examples here. Don't really need to describe them. You can see what's going on. Here's some important information on its training. Here's an example. Only been trained on 768 \* 448 resolution and it's only been trained on 121 frames.

**2:17** · So, if you go past that it might not work so well. Click in here and you've got the lore.

**2:23** · It's down here. Just click that. Put that in your lore's folder. When you load up the workflow it looks quite big, but there's not a lot you need to know.

**2:30** · Just this area here and this box over here. When you load up the workflow it looks quite big, but there's not a lot you need to know. Just this area here and this box over here. Just click into this open B box animator. Up here you got your templates. I've made this one here, but there's one single walking person. There's a two-person walking.

**2:49** · Once you've done something like in here, always save current scene as a template.

**2:53** · I found it wasn't really working so well if I didn't do that. Load image down here. I've got two objects loaded. If you want to add more you just click add object. So, these are the ones I've already pre-made. These people walking.

**3:04** · Let's just watch that play head.

**3:07** · And that's my prediction of where I want them to walk. Now, when I moved it over here, I actually made this box smaller when it got to there just to try and have a guess at as they move they're going to get smaller. Notice when I just did that then because I stopped here it automatically puts a key frame. So, if I move that here and I do something change to the box then it puts a key frame there. If you move back over something you can just click delete key and that'll get rid of that one there.

**3:34** · But, because I'm changing each key frame there when it gets to the end, see it's going to change its size and then move because the last one was smaller. If we move onto the car, you can see the same thing.

**3:48** · I've got the car there and I'm predicting that it's going to get bigger towards the screen. So, I'm just making a guess. There is a global prompt up here with style and scene as I explained in the GitHub. This top style one I've just got cinematic street photography with crisp afternoon sunlight, soft natural shadows, etc. And in the scene, I'm being a little bit more detailed on what's going on here. 1950s American street with cars parked at the sidewalk and people on the concrete paving and reflective glass buildings where two people walk steadily across the frame.

**4:22** · On my region prompt, I've just written 1950s car driving towards the camera.

**4:27** · And when I'm clicking the walking people, I've just got a couple holding hands walking naturally with a relaxed upright posture and a steady stride.

**4:35** · There's nothing else you need to do. You just click save and close and then click run. And that's it. It does it exactly as you want it to do. I was getting these error messages all the time, but it still worked anyway, so I just ignored them. Here's where you load your Laura here.

**4:49** · Up here is where you put in your reference image. Now, make sure this part here says false cuz if it's ticked to true, it will ignore the image and just do text a video. And you should also see your prompt transferred from your B box animator to this preview prompt window. Good thing about this output is it gives you your original video, your boxes preview window, and then it's got the mixed with the boxes on top of it. So, you can see how accurate it was. I didn't think it would get my people very accurate, but it has.

**5:19** · It's followed them right the way through. And this car as well, even though I was just making guesswork on the three-dimensional view of this. I've used box nodes in the past, but this is the most accurate one where you can move it forward and back, delete and add keyframes, and and once the end result comes out, it followed it exactly as you did. You don't have to do another prompt. So, this is definitely the best one I've seen. Anyway, it's another tool to use in the LTX 2.5 series. Like, subscribe, leave some comments, and we'll see you in the next video.