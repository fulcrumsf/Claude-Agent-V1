### This AI Machine automatically clips & posts 100+ Shorts from 1 Video

> [!info] This AI Machine automatically clips & posts 100+ Shorts from 1 Video (n8n NO CODE tutorial 🥚)  
> 🍳 Join 1500+ AI practitioners in The RoboNuggets Community: https://www.  
> [https://youtu.be/LiWf_BGg87o?si=f2hj0ZvlZr3VLIpA](https://youtu.be/LiWf_BGg87o?si=f2hj0ZvlZr3VLIpA)  

> [!info] The ULTIMATE Agent to Auto-Publish Content Hourly - 9 Social Platforms in 1! (n8n NO-CODE tutorial🥚)  
> In this lesson, you'll learn how to set up the best publishing agent available right now - as it seamlessly integrates with not 2, not 3, but 9 Social Media Platforms - all in one system 😉  
> [https://youtu.be/MNYx_0a2XqI?si=XI36VC_eJx369Jnf](https://youtu.be/MNYx_0a2XqI?si=XI36VC_eJx369Jnf)  
![[RoboNuggets_Clipping.png]]
### **AI Clipping System Overview**
- Built an AI system that automatically generates 100+ shorts from long-form videos
- System publishes clips across multiple social platforms (TikTok, Instagram, YouTube Shorts, LinkedIn)
- Market context: Content creators paying ~$140k/month for manual clipping services
- Industry rate: $15 per one-minute video clip (per Upwork data)
### **Technical Implementation**
- Built using n8n (no-code automation tool)
- Core components:
    
    - Input: Long-form video source
    
    - Analysis: AI processing via CLAP API
    
    - Export: Short clip generation with auto-subtitles
    
    - Publishing: Auto-distribution to social channels
    
- Key integrations:
    
    - Klap AI for video processing
    
    - Klap API Url: [https://api.klap.app/v2/tasks/video-to-shorts](https://api.klap.app/v2/tasks/video-to-shorts)
    
    - Blotato for social media publishing
    
    - Google Sheets for tracking
    
- Cost structure:
    
    - Variable: ~$0.85 per clip (CLAP AI)
    
    - Fixed: $24/month (n8n), $29/month (Blotato)
    
### **Monetization Opportunities**
- Direct Business Services
    
    - Target YouTube content creators
    
    - Offer automated clipping services
    
    - Standard rate: $15 per clip
    
- WAP Platform
    
    - Monetize through view-based rewards
    
    - Access to both content creators and AI tools companies
    
- Affiliate Programs
    
    - School communities offering up to 50% lifetime commissions
    
    - Multiple revenue streams possible
    
### **Implementation Steps**
- Set up Google Sheet template for tracking videos
- Configure n8n workflow with Klap API integration
- Establish publishing schedule (e.g., every 3 hours)
- Split workflow into two parts:
    
    - Clip production (daily runs)
    
    - Social media publishing (scheduled intervals)
    
- Add tracking for production status and publishing dates
### **System Capabilities**
- Auto-generates contextually relevant clips
- Adds automatic subtitles and captions
- Properly frames speakers using AI
- Customizes captions per social platform
- Handles video processing and publishing automation
- Tracks production and publishing status
- Operates with minimal technical knowledge required
### Klap API
Klap POST: [https://api.klap.app/v2/tasks/video-to-shorts](https://api.klap.app/v2/tasks/video-to-shorts)
Klap GET: [https://api.klap.app/v2/tasks/](https://api.klap.app/v2/tasks/){{ $[json.id](http://json.id/) }}
GET Shorts Details: [https://api.klap.app/v2/projects/](https://api.klap.app/v2/projects/){{ $json.output_id }}
Export Shorts: [https://api.klap.app/v2/projects/](https://api.klap.app/v2/projects/){{ $json.folder_id }}/{{ $[json.id](http://json.id/) }}/exports
```json
{
  "preset_id": "123"
}
```
GET Shorts: [https://api.klap.app/v2/projects/](https://api.klap.app/v2/projects/){{ $json.folder_id }}/{{ $[json.id](http://json.id/) }}/exports/{{ $[json.id](http://json.id/) }}
**Date Produced**:
```json
{{ new Date().toISOString().split('T')[0] }}
```
**Update Longform Status**: ID Values “**=ROW() - 1**”
### Analyze Longform
```json
{
  "source_video_url": "{{ $json.longform_links }}",
  "language": "en",
  "target_clip_count": 2,
  "max_clip_count": 2,
  "editing_options": {
    "captions": true,
    "reframe": true,
    "emojis": true,
    "remove_silences": true,
    "intro_title": false
  },
  "dimensions": {
    "width": 1080,
    "height": 1920
  },
  "min_duration": 15,
  "max_duration": 60,
  "target_duration": 30
}
```
---
Chat with meeting transcript: [https://notes.granola.ai/d/24f91027-c8ea-4389-b1bb-9fd5e6882609](https://notes.granola.ai/d/24f91027-c8ea-4389-b1bb-9fd5e6882609)

> [!info] How To Make Money with Clipping (for free)  
> I saw the comments on my last video—so many of you kept asking about this in my YouTube livestreams.  
> [https://youtu.be/H-QUdBMihUk?si=FXoelTu23ybgcpaZ](https://youtu.be/H-QUdBMihUk?si=FXoelTu23ybgcpaZ)  

> [!info] How I Made 100 YouTube Shorts in Minutes | No-Code n8n Tutorial  
> This AI YouTube Automation clips Videos on Autopilot.  
> [https://youtu.be/lo0e0IQqUwM?si=Xe-zcGpezugjhGzp](https://youtu.be/lo0e0IQqUwM?si=Xe-zcGpezugjhGzp)  

> [!info] This AI Machine automatically clips & posts 100+ Shorts from 1 Video (n8n NO CODE tutorial 🥚)  
> 🍳 Join RoboNuggets when you're ready to learn & earn from AI: https://www.  
> [https://youtu.be/LiWf_BGg87o?si=E1JECipRewt6sysI](https://youtu.be/LiWf_BGg87o?si=E1JECipRewt6sysI)  

> [!info] This AI System Generates Viral Clips from any YouTube Video (n8n + Vizard)  
> 📌 Join my FREE Skool community to download this n8n template and ALL of our other automations!  
> [https://youtu.be/Yb-mZmvHh-I?si=-aQnB9SHr3fb-W7S](https://youtu.be/Yb-mZmvHh-I?si=-aQnB9SHr3fb-W7S)  

> [!info] Build Your Own FREE AI Video Clipping Tool with n8n (Localhost)  
> 📌 All AI Agent Templates & Tech Support (for builders)  
> [https://youtu.be/YmTp0P4RsMs?si=vYXM0PviHw0zjhsi](https://youtu.be/YmTp0P4RsMs?si=vYXM0PviHw0zjhsi)  

> [!info] Step by step how to clip content 👀 \#onlinebusiness \#clipping  
>  
> [https://www.tiktok.com/t/ZTjfCq6bV/](https://www.tiktok.com/t/ZTjfCq6bV/)  

> [!info] Replying to @trendplugs \#greenscreenvideo this is the process I go through to help avoid violations when I’m using clips on TikTok shop  
>  
> [https://www.tiktok.com/t/ZP8MddbVV/](https://www.tiktok.com/t/ZP8MddbVV/)  

> [!info] Promote Fun  
> Launch a clipping campaign instantly, drive traffic and go viral.  
> [https://promote.fun/](https://promote.fun/)  
### Archive
### How To Make Your First $1,000 Clipping With Whop

> [!info] How To Make Your First $1,000 Clipping With Whop  
> I earned $1000 with just 30 minutes of work with Whop and I show you how you can do the same too!  
> [https://youtu.be/IwLX2_MaBok?si=1_c7juTc7HiPZS5f](https://youtu.be/IwLX2_MaBok?si=1_c7juTc7HiPZS5f)  
TodayMeAdd to folder**WAP Platform Overview**  
• Platform pays creators for content across multiple social platforms  
• Earned $1,000 for 30 minutes of work  
• Payment goes directly to bank account  
• Two main content types:  
◦ Clipping (using others’ content)  
◦ UGC (original content with creator’s face)**Community Selection Criteria**  
• Platform coverage:  
◦ Prefer communities offering multiple platforms (YouTube, TikTok, Instagram)  
◦ Multi-platform posting can triple earnings  
• Key metrics to evaluate:  
◦ RPM (Revenue Per Mille): $0.30-$3.00 per 1000 views  
◦ Total prize pool: Minimum $10,000-$20,000 recommended  
◦ Current completion percentage  
◦ Minimum view counts (5,000-10,000 views preferred)  
• Accessibility factors:  
◦ Instant join vs. waitlist  
◦ Geographic requirements (50% USA audience common)  
◦ Platform-specific requirements**Top 5 WAP Communities**  
• Bez’s Trades  
◦ $2.50 RPM  
◦ Simple requirements  
◦ $1,000 total prize pool  
• Dubb  
◦ $26,000 prize pool  
◦ $1.50 RPM  
◦ Requires 50% USA audience  
◦ Maximum payout: $1,000  
• ScanProfit  
◦ $2.00 RPM  
◦ $8,000 prize pool  
◦ Available on Instagram, TikTok, YouTube  
• Brez Scales  
◦ $2.00 per 1000 views  
◦ Currently awaiting prize pool update  
◦ Examples of $500 earnings per video  
• WAP Official  
◦ $50 per 1000 views for UGC content  
◦ Focuses on long-form WAP-related content  
◦ Requires primarily USA audience**Content Strategy Tools**  
• Verlo SaaS tool features:  
◦ Tracks viral YouTube Shorts and TikTok content  
◦ Dedicated clipping niche section  
◦ Shows top-performing clips and view counts  
◦ Available with 10% discount code “10”  
• Submission requirements:  
◦ Post content on social platforms first  
◦ Submit to WAP within 1 hour  
◦ Include required platform tags and brandingChat with meeting transcript: [https://notes.granola.ai/d/d2086a5d-f8c0-4473-9033-ce0861d5a83c](https://notes.granola.ai/d/d2086a5d-f8c0-4473-9033-ce0861d5a83c)AutoShare
  
### He makes $1600 month with AI whop clipping

> [!info] He makes $1600 month with AI whop clipping  
> Links in the Video:  
> [https://youtu.be/m5Kb6U8m0AY?si=XdAKlvpN5fTaMmL_](https://youtu.be/m5Kb6U8m0AY?si=XdAKlvpN5fTaMmL_)  
### **Financial Results & Overview**
- Revenue: $839 earned in first 15 days
- Projected monthly earnings: ~$1,600
- Time investment: 30-90 minutes per day
- Platform: WAP (Watch and Profit) content rewards program
- Primary strategy: High volume AI-generated clips vs manual editing
### **Technical Process**
- Tool stack:
    
    - OpusClip ($12/month) - AI clip generation
    
    - CapCut - Adding required CTAs
    
    - [Repurpose.io](http://repurpose.io/) - Cross-platform posting
    
- Workflow:
    
    - Find long-form content from approved creators
    
    - Input video link into OpusClip
    
    - Generate 20+ AI clips per video
    
    - Add CTA overlay in CapCut
    
    - Upload to YouTube
    
    - Submit links to WAP campaigns
    
### **Campaign Selection Strategy**
- Look for:
    
    - Low view requirements (under 3,000 views)
    
    - Quick approval times (2-3 days normal)
    
    - Active admin communication
    
    - Clear payment history
    
- Red flags:
    
    - Delayed approvals (8-10+ days)
    
    - Negative chat feedback
    
    - Unclear requirements
    
- Example campaign: Carlton Dennis Clips ($1-3 CPM)
### **Channel Optimization**
- Create dedicated clip channels
- Match channel branding to original creator
- Include clickable source links
- Age/warm up channels before heavy posting
- Can create multiple YouTube channels under one email
- Consider cross-posting to Instagram/TikTok for 2-3x earnings
### **Monetization Tips**
- Payment requires Stripe access
- Alternative withdrawal options available through trusted Discord middlemen
- Flash CPM campaigns offer higher rates temporarily
- Trial multiple campaigns initially
- Focus scaling on proven campaigns
- Consider outsourcing submission process
---
Chat with meeting transcript: [https://notes.granola.ai/d/ab3fa047-b43f-4ac1-8e3c-9f4de848437f](https://notes.granola.ai/d/ab3fa047-b43f-4ac1-8e3c-9f4de848437f)
### How I Make $3,000/day Clipping

> [!info] How I Make $3,000/day Clipping (with Whop)  
> Work w/ Me 1on1 : https://www.  
> [https://youtu.be/taYn_gkfYHU?si=dJvfB93mLOeZPM4V](https://youtu.be/taYn_gkfYHU?si=dJvfB93mLOeZPM4V)  
### **Overview of WAP Platform**
- WAP is an online platform for monetizing content creation
- Recently acquired by Amman Godsey
- Launched “Content Rewards” feature allowing creators to pay for short-form clips
- Platform automatically pays content creators hourly
- Accessible at [wap.com/discover](http://wap.com/discover)
### **Revenue Model & Payment Structure**
- Payment rates vary from $1-3 per 1,000 views
- Example campaigns:
    
    - Rob the Bank: $1/1k views (35M views, $18k budget)
    
    - Ambro: $3/k views (6M views, $28k paid out)
    
    - TJR: $1/k views (8M views)
    
- Personal earnings claim: $70k monthly via Stripe + $30k via bank wire
### **Income Progression Path**
- Beginner Level ($500-1k/month):
    
    - Start by claiming rewards
    
    - Use basic tools like CapCut
    
    - Focus on learning content creation
    
- Intermediate Level ($1k-5k/month):
    
    - Transition to Adobe Premiere Pro
    
    - Build reputation in WAP chats
    
    - Receive bonus opportunities
    
- Advanced Level ($5k-10k/month):
    
    - Secure direct client contracts
    
    - Typical rate: $2k/month for 2 daily clips
    
    - Launch own WAP groups
    
- Expert Level ($10k+/month):
    
    - Manage editing teams ($10/video cost, $30-40/video revenue)
    
    - Focus on creator onboarding
    
    - Take 20-25% of campaign budgets
    
    - Manage large budgets ($20k-39k range)
    
### **Technical Process**
- Content creation steps:
    
    - Access training through Learn tab
    
    - Download videos using Cobalt Tools
    
    - Edit with CapCut or Premiere Pro
    
    - Add subtitles and hooks
    
    - Submit through Earn function
    
- Group creation process available through Dashboard > WAPs > New WAP
### **Additional Resources**
- Free Discord community available
- Clipper Academy offered:
    
    - $50/month membership
    
    - Private Discord access
    
    - Potential earnings: $100/day within first week
    
    - Processed through WAP platform
    
---
Chat with meeting transcript: [https://notes.granola.ai/d/511b21b7-02a4-4e59-a50e-574955872c02](https://notes.granola.ai/d/511b21b7-02a4-4e59-a50e-574955872c02)