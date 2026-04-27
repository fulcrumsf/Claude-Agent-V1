---
description: Fetch and save API documentation for any fal.ai model by scraping the official docs. Use this whenever you need API details for a fal.ai model before generating content. Produces a structured API reference file ready for immediate use.
trigger: User asks to use a fal.ai model, user says "fetch the fal.ai API for [model]", or a fal.ai model is referenced with no existing doc in references/docs/.
---

# Skill: Fetch fal.ai API Documentation

Use this skill to pull live API documentation for any fal.ai model and save it as a structured reference file in `references/docs/`. Run this before writing prompts or API calls for any fal.ai model.

## When to Use
- A fal.ai model is referenced but no MD file exists in `references/docs/`
- User asks to "use fal.ai for [task]" without specifying which model
- You need input schema, endpoint, or parameter constraints for a fal.ai model
- An existing fal.ai doc may be outdated and needs refreshing

## Step 1: Check if the doc already exists

```bash
ls "/Users/tonymacbook2025/Documents/App Building/Video Editor/references/docs/"
```

If a file exists for this model, read it first. Only proceed if missing or user wants a refresh.

## Step 2: Identify the model

fal.ai model IDs follow a pattern like:
- `fal-ai/flux/dev`
- `fal-ai/kling-video/v1.6/image-to-video`
- `fal-ai/stable-diffusion-v3-medium`
- `fal-ai/aura-flow`

If the user provided a partial name (e.g., "Flux on fal.ai"), use WebSearch to find the exact model ID:
```
Search query: "fal.ai [model name] API"
OR: site:fal.ai [model name]
```

## Step 3: Fetch the model's documentation page

fal.ai model documentation URLs follow this pattern:
```
https://fal.ai/models/[model-id]
https://fal.ai/models/[model-id]/api
```

The `/api` suffix shows the full API schema. Always try the `/api` URL first — it contains the structured input/output schema.

Use WebFetch on:
1. `https://fal.ai/models/[model-id]/api` — API schema (preferred)
2. `https://fal.ai/models/[model-id]` — Model overview and examples

If the page is JavaScript-rendered and WebFetch returns incomplete content, use Firecrawl:
```
Skill: firecrawl-scrape
URL: https://fal.ai/models/[model-id]/api
```

## Step 4: Also check the fal.ai Python/JS client docs if needed

For calling fal.ai programmatically:
```
https://fal.ai/docs/client-libraries/python
https://fal.ai/docs/client-libraries/javascript
```

The REST API pattern for fal.ai:
```
POST https://queue.fal.run/[model-id]
Authorization: Key [FAL_KEY]
Content-Type: application/json
```

Or using the fal client:
```python
import fal_client
result = fal_client.run("[model-id]", arguments={...})
```

Extract from the documentation:
- Exact model ID string
- All input parameters, types, and constraints
- Required vs. optional fields
- Output structure (where to find generated URLs)
- Supported image/video formats
- Resolution and aspect ratio options
- Any rate limits or queue behavior
- Webhook support (if async)

## Step 5: Format and save the API reference

Save to: `references/docs/FAL_[Model_Name].md`

Use this standard format:

```markdown
# [Model Display Name] — fal.ai API Reference
**Source:** [URL scraped from]
**Last fetched:** [today's date]
**Model ID:** `[exact fal.ai model ID]`
**REST Endpoint:** `POST https://queue.fal.run/[model-id]`

---

## Authentication

\`\`\`
Authorization: Key [FAL_KEY]  ← stored in .env as FAL_KEY
Content-Type: application/json
\`\`\`

## Request Structure

\`\`\`json
{
  "[param1]": "[value]",
  "[param2]": "[value]"
}
\`\`\`

## Parameters

| Field | Type | Required | Default | Values / Constraints | Notes |
|---|---|---|---|---|---|
| [param] | [type] | Yes/No | [default] | [allowed values] | [notes] |

## Output Structure

\`\`\`json
{
  "[output_field]": "[description of what's returned]"
}
\`\`\`

Result URL location: `[path to the generated file URL in the response]`

## Python Client Example

\`\`\`python
import fal_client

result = fal_client.run(
    "[model-id]",
    arguments={
        [example parameters]
    }
)
print(result["[output_field]"])
\`\`\`

## REST Example (curl)

\`\`\`bash
curl -X POST https://queue.fal.run/[model-id] \\
  -H "Authorization: Key $FAL_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{[example payload]}'
\`\`\`

## Key Notes
- [Resolution constraints]
- [Supported formats]
- [Queue vs. sync behavior]
- [Any model-specific limitations]
- [Pricing tier if noted in docs]
```

## Step 6: Check for the FAL_KEY in .env

```bash
grep "FAL_KEY" "/Users/tonymacbook2025/Documents/App Building/Video Editor/.env"
```

If `FAL_KEY` is not present, note this in your report — the user will need to add it before using fal.ai models.

## Step 7: Report to user

After saving, confirm:
- File saved to: `references/docs/FAL_[filename].md`
- Exact model ID string
- Minimum required parameters to make a working call
- Whether `FAL_KEY` is present in `.env`
- Any queue/async behavior the user should know about

## Notes

- fal.ai uses a queue-based system for most models — responses may be async with a request ID to poll
- The `/api` page on fal.ai often has a live interactive schema — Firecrawl handles this better than WebFetch
- fal.ai model IDs are case-sensitive and slash-separated — get the exact string from the docs
- fal.ai updates models frequently — if a model starts erroring, re-fetch the doc
- Some fal.ai models have both a `sync` and `async` endpoint — document both if present
- Save the file even if the scrape is partial — mark it with "INCOMPLETE — needs update" at the top
