---
name: google_veo_kie_api
description: Best practices for using Google Veo 3, Kling, Runway, and Kie AI APIs for video and image generation.
---

# Kie AI Unified Video API Integration

When instructed to use Kie AI for video generation (instead of Blotato), follow these best practices.

## Overview
Kie.ai provides a unified API platform that offers access to elite text-to-video and image-to-video generator models without needing separate API keys for each provider.

**Available Models:**
*   `grok-imagine/text-to-video` (xAI, multimodal, synchronized audio)
*   `kling-3.0/text-to-video` or `kling-2.6/text-to-video` (Cinematic, up to 15s)
*   `google/veo-3.1` (DeepMind cinematic visuals)
*   `runway/v3` or Aleph (In-context video editing)
*   `wan-2.5` (Image-to-video and text-to-video generation)
*   `seedance-2.0` (ByteDance cinematic videos)

## Implementation Patterns

- **Endpoint**: Use the unified task creation endpoint: `https://api.kie.ai/v1/jobs/createTask` (or specific provider endpoints if required by the API doc updates).
- **Authentication**: Pass your API key in the `Authorization: Bearer <KIE_API_KEY>` header.
- **Payload Structure**: 
  Generally requires specifying the model and common parameters:
  ```json
  {
      "model": "kling-3.0/text-to-video",
      "prompt": "Highly detailed visual description...",
      "aspectRatio": "16:9",
      "duration": 5,
      "quality": "high"
  }
  ```
- **Asynchronous Execution**: Video generation is heavily asynchronous. You must implement exponential backoff polling on the task ID returned by `createTask` until the status is "completed".
- **Hosting**: If doing Image-to-Video, the start frame must be a publicly accessible URL. Pass images to a public cloud storage or the Kie file upload API first.

## Content Safety & Consistency
- Models like Google Veo have strict content safety filters. Avoid explicit terms.
- For character consistency across scenes, ensure the same detailed prompt block (e.g., "A specific adult brown echidna with light-tan spines and a dark slim snout") is appended to every single scene's video generation prompt.
