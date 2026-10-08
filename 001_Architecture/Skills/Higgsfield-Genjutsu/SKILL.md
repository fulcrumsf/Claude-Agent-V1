---
name: higgsfield-genjutsu
description: API reference and usage guide for Higgsfield's Genjutsu Motion Transfer model (video2video motion transfer using image references). Use when Tony asks to transform/restyle an existing video using Genjutsu, Higgsfield motion transfer, or wants to swap characters/locations/style in a video while preserving original motion and camera movement.
---

# Higgsfield Genjutsu — Motion Transfer

Transforms an existing video using image references for different characters, locations, and styles, while preserving the original motion, camera movement, and timing throughout the resulting clip.

## Overview

- **Endpoint**: `https://api.higgsfield.ai/higgsfield/genjutsu/motion-transfer/v1.0`
- **Model ID**: `higgsfield/genjutsu/motion-transfer/v1.0`
- **Category**: video2video
- **Kind**: inference

**Constraints:**
- Source video must be **at least 4 seconds**.
- Videos **longer than 30 seconds are trimmed to 30 seconds**; output duration follows the prepared (trimmed) source video.
- Provide **1–8 image references** (`image_urls`).
- `prompt` is optional and defaults to `""`.

## Pricing

Per-second pricing based on **input video duration**, rounded up to the nearest whole second (rates before any applicable discount):

| Resolution | Price per input-second |
|---|---|
| 480p | $0.318 |
| 720p | $0.681 |
| 1080p | $1.632 |

## Authentication

The key is a `KEY_ID:KEY_SECRET` pair, stored in `~/.env-secrets` (sourced by shell, per the workspace's API Key Rule — see [[feedback_api_keys]]) exactly as the official docs expect:

```bash
export HF_KEY="YOUR_KEY_ID:YOUR_KEY_SECRET"
export HF_CREDENTIALS="$HF_KEY"
```

`HF_CREDENTIALS` is used by the TypeScript SDK; `HF_KEY` is used by the Python SDK and cURL. Both env vars already exist in this workspace's shell — no mapping or renaming needed in scripts.

**Never hardcode the key value in any script.**

Request header format:
```http
Authorization: Key $HF_KEY
```

## API Pattern

Use `subscribe` to submit the model request and wait for a terminal result. The TypeScript SDK performs automatic polling with `withPolling: true`; Python's synchronous `subscribe` call also waits. See **Workflow pattern for this workspace** below for when to use the lower-level status/result/cancel calls instead.

### Input Parameters

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `prompt` | `string` | No | `""` | Max length 10000 |
| `video_url` | `string` | Yes | — | Public URL. Min length 1, max length 2083 |
| `image_urls` | `array<string>` | Yes | — | 1–8 public URLs |
| `resolution` | `string` | No | `"720p"` | Options: `480p`, `720p`, `1080p` |

### Input JSON Schema

```json
{
  "type": "object",
  "title": "MotionTransferParams",
  "required": [
    "video_url",
    "image_urls"
  ],
  "properties": {
    "prompt": {
      "type": "string",
      "title": "Prompt",
      "default": "",
      "maxLength": 10000
    },
    "video_url": {
      "type": "string",
      "title": "Video Url",
      "format": "uri",
      "maxLength": 2083,
      "minLength": 1
    },
    "image_urls": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "uri",
        "maxLength": 2083,
        "minLength": 1
      },
      "title": "Image Urls",
      "maxItems": 8,
      "minItems": 1
    },
    "resolution": {
      "enum": [
        "720p",
        "480p",
        "1080p"
      ],
      "type": "string",
      "title": "Resolution",
      "default": "720p"
    }
  },
  "additionalProperties": false
}
```

### Required Parameters Example

```json
{
  "prompt": "",
  "video_url": "https://example.com/input.mp4",
  "image_urls": [
    "https://example.com/input.jpg"
  ],
  "resolution": "720p"
}
```

A saved copy of this example request body lives at [references/Example-Prompt.md](references/Example-Prompt.md).

### Output Schema

The shared polling endpoint returns one of these status shapes:

```json
{
  "title": "RequestStatus",
  "oneOf": [
    {
      "title": "PendingRequestStatus",
      "type": "object",
      "properties": {
        "request_id": { "type": "string", "format": "uuid" },
        "status_url": { "type": "string", "format": "uri" },
        "cancel_url": { "type": "string", "format": "uri" },
        "status": {
          "type": "string",
          "enum": ["queued", "in_progress", "nsfw", "canceled"]
        }
      },
      "required": ["status", "request_id"]
    },
    {
      "title": "FailedRequestStatus",
      "type": "object",
      "properties": {
        "request_id": { "type": "string", "format": "uuid" },
        "status_url": { "type": "string", "format": "uri" },
        "cancel_url": { "type": "string", "format": "uri" },
        "status": { "type": "string", "const": "failed" },
        "error": { "type": "string" }
      },
      "required": ["status", "request_id", "error"]
    },
    {
      "title": "CompletedRequestStatus",
      "type": "object",
      "properties": {
        "request_id": { "type": "string", "format": "uuid" },
        "status_url": { "type": "string", "format": "uri" },
        "cancel_url": { "type": "string", "format": "uri" },
        "status": { "type": "string", "const": "completed" },
        "video": {
          "type": "object",
          "properties": { "url": { "type": "string", "format": "uri" } },
          "required": ["url"]
        },
        "zip": {
          "type": "object",
          "properties": { "url": { "type": "string", "format": "uri" } },
          "required": ["url"]
        },
        "mov": {
          "type": "object",
          "properties": { "url": { "type": "string", "format": "uri" } },
          "required": ["url"]
        },
        "jsx": {
          "type": "object",
          "properties": { "url": { "type": "string", "format": "uri" } },
          "required": ["url"]
        },
        "fbx": {
          "type": "object",
          "properties": { "url": { "type": "string", "format": "uri" } },
          "required": ["url"]
        },
        "ply": {
          "type": "object",
          "properties": { "url": { "type": "string", "format": "uri" } },
          "required": ["url"]
        }
      },
      "required": ["status", "request_id", "video"]
    }
  ]
}
```

Completed requests return the generated video in the `video.url` field; `zip`/`mov`/`jsx`/`fbx`/`ply` are optional additional export formats when applicable.

## SDK Installation

```bash
npm install @higgsfield/client
# or
pip install higgsfield-client
```

## Usage Examples

`HF_KEY` and `HF_CREDENTIALS` are both already exported in this workspace's shell (`~/.env-secrets`), so the examples below match Higgsfield's docs verbatim — no mapping needed.

### TypeScript

```typescript
import { config, higgsfield } from "@higgsfield/client/v2";

config({
  credentials: process.env.HF_CREDENTIALS,
});

const result = await higgsfield.subscribe(
  "higgsfield/genjutsu/motion-transfer/v1.0",
  {
    input: {
      "prompt": "",
      "video_url": "https://example.com/input.mp4",
      "image_urls": [
        "https://example.com/input.jpg"
      ],
      "resolution": "720p"
    },
    withPolling: true,
  },
);

console.log(result);
```

### Python

```python
import higgsfield_client

result = higgsfield_client.subscribe(
    'higgsfield/genjutsu/motion-transfer/v1.0',
    arguments={'prompt': '',
         'video_url': 'https://example.com/input.mp4',
         'image_urls': ['https://example.com/input.jpg'],
         'resolution': '720p'},
)

print(result)
```

### cURL

```bash
curl --request POST \
  --url 'https://api.higgsfield.ai/higgsfield/genjutsu/motion-transfer/v1.0' \
  --header "Authorization: Key $HF_KEY" \
  --header "Content-Type: application/json" \
  --data @- <<'JSON'
{
  "prompt": "",
  "video_url": "https://example.com/input.mp4",
  "image_urls": [
    "https://example.com/input.jpg"
  ],
  "resolution": "720p"
}
JSON
```

### Explicit lifecycle control (Python)

Use when a worker needs explicit status, result, or cancellation control for an existing request, instead of the blocking `subscribe` call.

```python
import higgsfield_client

request_id = "{request_id}"
status = higgsfield_client.status(request_id=request_id)
result = higgsfield_client.result(request_id=request_id)
higgsfield_client.cancel(request_id=request_id)
```

## Workflow pattern for this workspace

- **Default**: submit via `subscribe` (with `withPolling: true` in TypeScript, or Python's synchronous `subscribe`) and let it block until the job reaches a terminal state (`completed` or `failed`). This is the simplest and correct choice for one-off or small-batch jobs.
- **Only** reach for the explicit `status` / `result` / `cancel` calls when a long-running batch needs manual control — e.g. firing off several Genjutsu jobs in parallel and polling them independently, or needing to cancel a job mid-flight.
- Both `video_url` and every entry in `image_urls` must already be public URLs — upload local files to existing hosting (e.g. the kie.ai upload helper or another already-used public bucket in this workspace) before calling this API.

## Additional Resources

- [Model page](https://console.higgsfield.ai/models/higgsfield/genjutsu/motion-transfer/v1.0)
- [Full Higgsfield documentation](https://docs.higgsfield.ai/docs/llms.txt)
