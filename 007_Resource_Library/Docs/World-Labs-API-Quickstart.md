---
title: "World Labs API Quickstart"
type: api-doc
category: app-dev
tags:
  - world-labs
  - api
  - 3d-generation
created: 2026-05-08
source: local
---

[Skip to main content](#content-area)

[World Labs home page![light logo](https://mintcdn.com/worldlabs/WWPzNmLk3Vvj-qdk/logo/light.svg?fit=max&auto=format&n=WWPzNmLk3Vvj-qdk&q=85&s=51e3312eddb56b926d8f1ef2d4887000)![dark logo](https://mintcdn.com/worldlabs/WWPzNmLk3Vvj-qdk/logo/dark.svg?fit=max&auto=format&n=WWPzNmLk3Vvj-qdk&q=85&s=48561556ea072215e950d9ca0269f7a0)](https://docs.worldlabs.ai/)

##### Get started

- [
	Quickstart
	](https://docs.worldlabs.ai/api)
- [
	Models
	](https://docs.worldlabs.ai/api/models)
- [
	Tools & examples
	](https://docs.worldlabs.ai/api/examples)

##### Reference

- - [
		POST
		Prepare media asset upload
		](https://docs.worldlabs.ai/api/reference/media-assets/prepare-upload)
		- [
		GET
		Get media asset
		](https://docs.worldlabs.ai/api/reference/media-assets/get)
- - [
		POST
		Generate a world
		](https://docs.worldlabs.ai/api/reference/worlds/generate)
		- [
		GET
		Get a world
		](https://docs.worldlabs.ai/api/reference/worlds/get)
		- [
		POST
		List worlds
		](https://docs.worldlabs.ai/api/reference/worlds/list)
		- [
		DEL
		Delete a world
		](https://docs.worldlabs.ai/api/reference/worlds/delete)
- - [
		POST
		Depth to RGB
		](https://docs.worldlabs.ai/api/reference/pano/depth_to_rgb)
- - [
		GET
		Get an operation
		](https://docs.worldlabs.ai/api/reference/operations/get)
- [
	OpenAPI spec
	](https://docs.worldlabs.ai/api/reference/openapi)

##### Support & billing

- [
	Pricing
	](https://docs.worldlabs.ai/api/pricing)
- [
	Rate limits
	](https://docs.worldlabs.ai/api/rate-limits)
- [
	Frequently asked questions
	](https://docs.worldlabs.ai/api/faq)

- [
	Discord
	](https://discord.gg/jSSSgXWT3v)
- [
	Company
	](https://worldlabs.ai/)
- [
	Go to Marble
	](https://marble.worldlabs.ai/)

[World Labs home page![light logo](https://mintcdn.com/worldlabs/WWPzNmLk3Vvj-qdk/logo/light.svg?fit=max&auto=format&n=WWPzNmLk3Vvj-qdk&q=85&s=51e3312eddb56b926d8f1ef2d4887000)![dark logo](https://mintcdn.com/worldlabs/WWPzNmLk3Vvj-qdk/logo/dark.svg?fit=max&auto=format&n=WWPzNmLk3Vvj-qdk&q=85&s=48561556ea072215e950d9ca0269f7a0)](https://docs.worldlabs.ai/)

- [Discord](https://discord.gg/jSSSgXWT3v)
- [Company](https://worldlabs.ai/)
- [Go to Marble](https://marble.worldlabs.ai/)

[Marble

](https://docs.worldlabs.ai/)[API

](https://docs.worldlabs.ai/api)

[Marble

](https://docs.worldlabs.ai/)[API

](https://docs.worldlabs.ai/api)

Get started

# Quickstart

Learn how to use the World API

> ## Documentation Index
> 
> Fetch the complete documentation index at: [https://docs.worldlabs.ai/llms.txt](https://docs.worldlabs.ai/llms.txt)
> 
> Use this file to discover all available pages before exploring further.

## 

[​

](#quickstart)

Quickstart

1

[

](#)

Get an API key

1

[

](#)

Sign in to the [World Labs Platform](https://platform.worldlabs.ai/) with your Marble account.If you don’t have a Marble account, you’ll be prompted to create one.

2

[

](#)

Visit the [billing page](https://platform.worldlabs.ai/billing).Add a payment method to your account and then purchase some credits to get started.

3

[

](#)

Generate an API key from the [API keys page](https://platform.worldlabs.ai/api-keys).

Save your API key in a secure location and never share it with anyone.

2

[

](#)

Create your first world

To verify your development setup is working, we recommend creating a world from only a text prompt.You can also create a world from an image, multiple images of the same scene, or a video.

This example uses `marble-1.1`, which corresponds to Marble 1.1.For the largest worlds, use `marble-1.1-plus`. Marble 1.1 Plus uses more credits to create a bigger world when prompted for outdoor or larger indoor spaces.

- Text input
- Image input
- Multi-image input
- Video input

1

[

](#)

Make a `POST` request to the [`/marble/v1/worlds:generate`](https://docs.worldlabs.ai/api/reference/worlds/generate) endpoint.

Request

```
curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
  -H 'Content-Type: application/json' \
  -H 'WLT-Api-Key: YOUR_API_KEY' \
  -d '{
    "display_name": "Mystical Forest",
    "model": "marble-1.1",
    "world_prompt": {
      "type": "text",
      "text_prompt": "A mystical forest with glowing mushrooms"
    }
  }'
```

This will return an Operation object.

```
{
  "operation_id": "20bffbb1-4ba7-453f-a116-93eaw1a6843e",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "expires_at": "2025-01-15T11:30:00Z",
  "done": false,
  "error": null,
  "metadata": null,
  "response": null
}
```

2

[

](#)

Poll the [`/marble/v1/operations/{operation_id}`](https://docs.worldlabs.ai/api/reference/operations/get) endpoint until the operation is done.

```
curl -X GET 'https://api.worldlabs.ai/marble/v1/operations/20bffbb1-4ba7-453f-a116-93eaw1a6843e' \
  -H 'WLT-Api-Key: YOUR_API_KEY'
```

This will return an Operation object. If the operation is not done, it will return a `200` status code and the Operation object will have a `done` field set to `false`:

```
{
  "operation_id": "20bffbb1-4ba7-453f-a116-93eaw1a6843e",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "expires_at": "2025-01-15T11:30:00Z",
  "done": false,
  "error": null,
  "metadata": {
    "progress": { "status": "IN_PROGRESS", "description": "World generation in progress" },
    "world_id": "dc2c65e4-68d3-4210-a01e-7a54cc9ded2a"
  },
  "response": null
}
```

World generation should take **about 5 minutes** to complete. Once the world is generated, the `done` field will be set to `true` and the `response` field will contain the generated World:

```
{
  "operation_id": "20bffbb1-4ba7-453f-a116-93eab1a6843e",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:35:00Z",
  "expires_at": "2025-01-15T11:30:00Z",
  "done": true,
  "error": null,
  "metadata": {
    "progress": {
      "status": "SUCCEEDED",
      "description": "World generation completed successfully"
    },
    "world_id": "dc2c65e4-68d3-4210-a01e-7a54cc9ded2a"
  },
  "response": {
    "id": "dc2c65e4-68d3-4210-a01e-7a54cc9ded2a",
    "display_name": "",
    "tags": null,
    "world_marble_url": "https://marble.worldlabs.ai/world/dc2c65e4-68d3-4210-a01e-7a54cc9ded2a",
    "assets": {
      "caption": "The scene is a fantastical forest...",
      "thumbnail_url": "<thumbnail_url>",
      "splats": {
        "spz_urls": {
          "500k": "<500k_spz_url>",
          "100k": "<100k_spz_url>",
          "full_res": "<full_res_spz_url>"
        }
      },
      "mesh": {
        "collider_mesh_url": "<collider_mesh_url>"
      },
      "imagery": {
        "pano_url": "<pano_url>"
      }
    },
    "created_at": null,
    "updated_at": null,
    "permission": null,
    "world_prompt": null,
    "model": null
  }
}
```

The `response` field contains a snapshot of the World at the time the operation completed. This allows you to access the generated assets without making a separate API call. Note that some fields like `display_name`, `created_at`, `updated_at`, `world_prompt`, and `model` may be empty or null in this snapshot. Use the [`GET /marble/v1/worlds/{world_id}`](https://docs.worldlabs.ai/api/reference/worlds/get) endpoint to fetch the complete, up-to-date world.

You can view the generated world in Marble at `https://marble.worldlabs.ai/world/{world_id}`.

3

[

](#)

(Optional) Get the latest world

If you need to fetch the most up-to-date version of the world later, use the `world_id` to retrieve it.

Request

```
curl -X GET 'https://api.worldlabs.ai/marble/v1/worlds/dc2c65e4-68d3-4210-a01e-7a54cc9ded2a' \
  -H 'WLT-Api-Key: YOUR_API_KEY'
```

This returns the latest version of the world:

```
{
  "world": {
    "id": "dc2c65e4-68d3-4210-a01e-7a54cc9ded2a",
    "display_name": "Mystical Forest",
    "tags": null,
    "world_marble_url": "https://marble.worldlabs.ai/world/dc2c65e4-68d3-4210-a01e-7a54cc9ded2a",
    "assets": {
      "caption": "The scene is a fantastical forest...",
      "thumbnail_url": "<thumbnail_url>",
      "splats": {
        "spz_urls": {
          "500k": "<500k_spz_url>",
          "full_res": "<full_res_spz_url>",
          "100k": "<100k_spz_url>"
        }
      },
      "mesh": {
        "collider_mesh_url": "<collider_mesh_url>"
      },
      "imagery": {
        "pano_url": "<pano_url>"
      }
    },
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:35:00Z",
    "permission": null,
    "world_prompt": {
      "type": "text",
      "text_prompt": "The scene is a fantastical forest..."
    },
    "model": "marble-1.1"
  }
}
```

The world object includes:
- `assets.splats.spz_urls`: 3D Gaussian splat files in SPZ format (100k, 500k, and full resolution)
- `assets.mesh.collider_mesh_url`: Collider mesh in GLB format
- `assets.imagery.pano_url`: Panorama image
- `assets.caption`: AI-generated description of the world
- `assets.thumbnail_url`: Thumbnail image for the world
- `world_prompt`: The prompt used to generate the world (may be recaptioned)
- `model`: The model used for generation

You can create a world from a single image using either a public URL or by uploading a local file.Recommended image formats: `jpg`, `jpeg`, `png`, `webp`.

- From URL
- From local file

If your image is already hosted at a public URL, you can reference it directly.

1

[

](#)

Make a `POST` request to the [`/marble/v1/worlds:generate`](https://docs.worldlabs.ai/api/reference/worlds/generate) endpoint with your image URL.

Request

```
curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
  -H 'Content-Type: application/json' \
  -H 'WLT-Api-Key: YOUR_API_KEY' \
  -d '{
    "display_name": "My Image World",
    "world_prompt": {
      "type": "image",
      "image_prompt": {
        "source": "uri",
        "uri": "https://example.com/my-image.jpg"
      },
      "text_prompt": "A beautiful landscape"
    }
  }'
```

This returns an Operation object. Poll the operation as shown in the text input example until `done` is `true`. The completed operation’s `response` field will contain the generated World.

To use a local image file, first upload it as a media asset, then reference it in your generation request.

1

[

](#)

Prepare the upload

Make a `POST` request to [`/marble/v1/media-assets:prepare_upload`](https://docs.worldlabs.ai/api/reference/media-assets/prepare-upload) to get a signed upload URL.

Request

```
curl -X POST 'https://api.worldlabs.ai/marble/v1/media-assets:prepare_upload' \
  -H 'Content-Type: application/json' \
  -H 'WLT-Api-Key: YOUR_API_KEY' \
  -d '{
    "file_name": "my-image.jpg",
    "kind": "image",
    "extension": "jpg"
  }'
```

This returns the media asset and upload information:

```
{
  "media_asset": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "file_name": "my-image.jpg",
    "kind": "image",
    "extension": "jpg",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": null,
    "metadata": null
  },
  "upload_info": {
    "upload_url": "<signed_upload_url>",
    "upload_method": "PUT",
    "required_headers": {
      "x-goog-content-length-range": "0,1048576000"
    }
  }
}
```

2

[

](#)

Upload the file

Upload your image to the signed URL using the method and headers from the response.

Request

```
curl -X PUT '<signed_upload_url>' \
  -H 'x-goog-content-length-range: 0,1048576000' \
  --data-binary '@/path/to/my-image.jpg'
```

3

[

](#)

Generate the world

Use the `media_asset_id` from Step 1 to generate a world.

Request

```
curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
  -H 'Content-Type: application/json' \
  -H 'WLT-Api-Key: YOUR_API_KEY' \
  -d '{
    "display_name": "My Image World",
    "world_prompt": {
      "type": "image",
      "image_prompt": {
        "source": "media_asset",
        "media_asset_id": "550e8400-e29b-41d4-a716-446655440000"
      },
      "text_prompt": "A beautiful landscape"
    }
  }'
```

This returns an Operation object. Poll the operation as shown in the text input example until `done` is `true`. The completed operation’s `response` field will contain the generated World.

The `text_prompt` field is optional. If omitted, a caption will be automatically generated from your image.

Set `is_pano: true` in the `image_prompt` if your input image is a panorama.

You can create a world from multiple images of the same scene, each with an optional azimuth (horizontal angle in degrees).Recommended image formats: `jpg`, `jpeg`, `png`, `webp`.

- From URLs
- From local files

If your images are already hosted at public URLs, you can reference them directly.

1

[

](#)

Make a `POST` request to the [`/marble/v1/worlds:generate`](https://docs.worldlabs.ai/api/reference/worlds/generate) endpoint with your image URLs and their azimuth positions.

Request

```
curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
  -H 'Content-Type: application/json' \
  -H 'WLT-Api-Key: YOUR_API_KEY' \
  -d '{
    "display_name": "My Multi-Image World",
    "world_prompt": {
      "type": "multi-image",
      "multi_image_prompt": [
        {
          "azimuth": 0,
          "content": {
            "source": "uri",
            "uri": "https://example.com/front.jpg"
          }
        },
        {
          "azimuth": 180,
          "content": {
            "source": "uri",
            "uri": "https://example.com/back.jpg"
          }
        }
      ],
      "text_prompt": "A cozy living room"
    }
  }'
```

This returns an Operation object. Poll the operation as shown in the text input example until `done` is `true`. The completed operation’s `response` field will contain the generated World.

To use local image files, first upload each as a media asset, then reference them in your generation request.

1

[

](#)

Prepare and upload each image

For each image, prepare the upload and upload the file as shown in the [image input example](#from-local-file).

Request

```
# Prepare upload for first image
curl -X POST 'https://api.worldlabs.ai/marble/v1/media-assets:prepare_upload' \
  -H 'Content-Type: application/json' \
  -H 'WLT-Api-Key: YOUR_API_KEY' \
  -d '{
    "file_name": "front.jpg",
    "kind": "image",
    "extension": "jpg"
  }'

# Upload the file to the returned upload_url
curl -X PUT '<upload_url>' \
  -H 'Content-Type: image/jpeg' \
  --data-binary '@/path/to/front.jpg'

# Repeat for each additional image
```

2

[

](#)

Generate the world

Use the media asset IDs to generate a world.

Request

```
curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
  -H 'Content-Type: application/json' \
  -H 'WLT-Api-Key: YOUR_API_KEY' \
  -d '{
    "display_name": "My Multi-Image World",
    "world_prompt": {
      "type": "multi-image",
      "multi_image_prompt": [
        {
          "azimuth": 0,
          "content": {
            "source": "media_asset",
            "media_asset_id": "<front_image_id>"
          }
        },
        {
          "azimuth": 180,
          "content": {
            "source": "media_asset",
            "media_asset_id": "<back_image_id>"
          }
        }
      ],
      "text_prompt": "A cozy living room"
    }
  }'
```

This returns an Operation object. Poll the operation as shown in the text input example until `done` is `true`. The completed operation’s `response` field will contain the generated World.

The `azimuth` field specifies the horizontal angle (in degrees) where the image was taken. Use `0` for front, `90` for right, `180` for back, `270` for left.

The `text_prompt` field is optional. If omitted, a caption will be automatically generated.

You can create a world from a video using either a public URL or by uploading a local file.Recommended video formats: `mp4`, `mov`, `mkv`.

- From URL
- From local file

If your video is already hosted at a public URL, you can reference it directly.

1

[

](#)

Make a `POST` request to the [`/marble/v1/worlds:generate`](https://docs.worldlabs.ai/api/reference/worlds/generate) endpoint with your video URL.

Request

```
curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
  -H 'Content-Type: application/json' \
  -H 'WLT-Api-Key: YOUR_API_KEY' \
  -d '{
    "display_name": "My Video World",
    "world_prompt": {
      "type": "video",
      "video_prompt": {
        "source": "uri",
        "uri": "https://example.com/my-video.mp4"
      },
      "text_prompt": "A scenic mountain landscape"
    }
  }'
```

This returns an Operation object. Poll the operation as shown in the text input example until `done` is `true`. The completed operation’s `response` field will contain the generated World.

To use a local video file, first upload it as a media asset, then reference it in your generation request.

1

[

](#)

Prepare the upload

Make a `POST` request to [`/marble/v1/media-assets:prepare_upload`](https://docs.worldlabs.ai/api/reference/media-assets/prepare-upload) to get a signed upload URL.

Request

```
curl -X POST 'https://api.worldlabs.ai/marble/v1/media-assets:prepare_upload' \
  -H 'Content-Type: application/json' \
  -H 'WLT-Api-Key: YOUR_API_KEY' \
  -d '{
    "file_name": "my-video.mp4",
    "kind": "video",
    "extension": "mp4"
  }'
```

This returns the media asset and upload information:

```
{
  "media_asset": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "file_name": "my-video.mp4",
    "kind": "video",
    "extension": "mp4",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": null,
    "metadata": null
  },
  "upload_info": {
    "upload_url": "<signed_upload_url>",
    "upload_method": "PUT",
    "required_headers": {
      "x-goog-content-length-range": "0,1048576000"
    }
  }
}
```

2

[

](#)

Upload the file

Upload your video to the signed URL using the method and headers from the response.

Request

```
curl -X PUT '<signed_upload_url>' \
  -H 'x-goog-content-length-range: 0,1048576000' \
  --data-binary '@/path/to/my-video.mp4'
```

3

[

](#)

Generate the world

Use the `media_asset_id` from Step 1 to generate a world.

Request

```
curl -X POST 'https://api.worldlabs.ai/marble/v1/worlds:generate' \
  -H 'Content-Type: application/json' \
  -H 'WLT-Api-Key: YOUR_API_KEY' \
  -d '{
    "display_name": "My Video World",
    "world_prompt": {
      "type": "video",
      "video_prompt": {
        "source": "media_asset",
        "media_asset_id": "550e8400-e29b-41d4-a716-446655440000"
      },
      "text_prompt": "A scenic mountain landscape"
    }
  }'
```

This returns an Operation object. Poll the operation as shown in the text input example until `done` is `true`. The completed operation’s `response` field will contain the generated World.

The `text_prompt` field is optional. If omitted, a caption will be automatically generated from your video.

Was this page helpful?

[

ModelsHow Marble model names map to World API model parameters

Next

](https://docs.worldlabs.ai/api/models)

⌘I

[x](https://x.com/theworldlabs)[linkedin](https://linkedin.com/company/world-labs)

[Powered byThis documentation is built and hosted on Mintlify, a developer documentation platform](https://www.mintlify.com/?utm_campaign=poweredBy&utm_medium=referral&utm_source=worldlabs)

- [Quickstart](#quickstart)

Assistant

Responses are generated using AI and may contain mistakes.

[

Contact support

](mailto:support@worldlabs.ai)