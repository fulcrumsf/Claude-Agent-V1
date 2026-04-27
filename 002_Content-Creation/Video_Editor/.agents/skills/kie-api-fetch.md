---
description: Fetch and save API documentation for any kie.ai model by scraping the official docs. Use this whenever you need API details for a model that doesn't have an existing MD file in references/docs/. Produces a structured API reference file ready for immediate use.
trigger: User asks to use a kie.ai model with no existing doc in references/docs/, or user says "fetch the API for [model]", or a model name is referenced that isn't documented yet.
---

# Skill: Fetch kie.ai API Documentation

Use this skill to pull live API documentation for any kie.ai model and save it as a structured reference file in `references/docs/`. Run this before writing any prompts for a model that lacks an existing doc.

## When to Use
- A model is referenced (e.g., "use Wan 3.0") but no MD file exists in `references/docs/`
- The user asks to "fetch the API for [model name]"
- You need API parameters, input schema, or endpoint details for a kie.ai model
- An existing doc may be outdated and needs refreshing

## Step 1: Check if the doc already exists

```bash
ls "/Users/tonymacbook2025/Documents/App Building/Video Editor/references/docs/"
```

If a file exists for this model (e.g., `Kling 2.6_Image_to_Video.md`), read it first. Only proceed if the doc is missing or the user explicitly wants a refresh.

## Step 2: Identify the model's documentation URL

kie.ai documentation lives at: `https://kie.ai/docs`

Use WebSearch to find the specific model page:
```
Search query: "kie.ai [MODEL_NAME] API documentation"
OR: site:kie.ai [MODEL_NAME]
```

Also try direct URL patterns:
- `https://kie.ai/docs/api/[model-slug]`
- `https://docs.kie.ai/[model-slug]`

If the model is accessed via the `/api/v1/jobs/createTask` endpoint (most models), also check the general API reference for the model's `input` schema:
- `https://kie.ai/docs/api-reference`

## Step 3: Scrape the documentation page

Use the WebFetch tool on the identified URL to retrieve the page content.

If the page is JavaScript-rendered and WebFetch returns incomplete content, use the Firecrawl scrape skill instead:
```
Skill: firecrawl-scrape
URL: [documentation URL]
```

Extract the following information from the scraped content:
- API endpoint URL
- Model identifier string (exact value for the `model` field)
- All input parameters and their types
- Required vs. optional fields
- Parameter constraints (min/max values, allowed strings, etc.)
- Output format (what the response contains, where to find the result URL)
- Any model-specific notes or limitations
- Example request payloads if present

## Step 4: Also fetch the general createTask endpoint schema

All kie.ai models share the same base endpoint. If not already documented, fetch:
```
https://kie.ai/docs/api-reference
```

Look for:
- The `POST /api/v1/jobs/createTask` request structure
- The `GET /api/v1/jobs/recordInfo` polling structure
- How `resultJson` and `resultUrls` are structured in the response
- State values: `waiting`, `generating`, `success`, `fail`
- `successFlag` values: 1 = success, 2/3 = fail

## Step 5: Format and save the API reference

Save to: `references/docs/[Model_Name].md`

Use this standard format:

```markdown
# [Model Display Name] — API Reference
**Source:** [URL scraped from]
**Last fetched:** [today's date]
**Endpoint:** POST https://api.kie.ai/api/v1/jobs/createTask
**Model identifier:** `[exact model string]`

---

## Request Structure

\`\`\`json
{
  "model": "[model identifier]",
  "input": {
    "[param1]": "[type] — [description]",
    "[param2]": "[type] — [description]"
  }
}
\`\`\`

## Parameters

| Field | Type | Required | Values / Constraints | Notes |
|---|---|---|---|---|
| [param] | [type] | Yes/No | [allowed values] | [notes] |

## Output / Polling

\`\`\`
GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=[taskId]

Response fields:
- state: "waiting" | "generating" | "success" | "fail"
- successFlag: 1 = success, 2/3 = fail
- resultJson.resultUrls[0]: URL of generated output
\`\`\`

## Key Notes
- [Any model-specific limitations or gotchas]
- [URL expiry warnings if applicable]
- [Audio/sound behavior]
- [Resolution options]

## Example Payload
\`\`\`json
{
  [complete working example]
}
\`\`\`
```

## Step 6: Report to user

After saving, confirm:
- File saved to: `references/docs/[filename].md`
- Model identifier string (exact value to use in `model` field)
- Key parameters summary (what the model needs at minimum)
- Any gotchas or limitations found

## Notes

- The kie.ai API key is stored in `.env` as `KIE_API_KEY`
- All kie.ai models poll the same `recordInfo` endpoint — only the `input` schema differs per model
- If the documentation page requires login to view, use WebSearch to find cached versions, GitHub issues, or community posts with the schema
- kie.ai may update model parameters without notice — re-fetch if a model starts returning unexpected errors
- Save the file even if the scrape is partial — a partial doc with a "INCOMPLETE — needs update" header is better than no doc
