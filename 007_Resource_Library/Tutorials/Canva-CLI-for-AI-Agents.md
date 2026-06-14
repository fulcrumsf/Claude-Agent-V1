---
title: "Canva CLI for AI Agents"
type: "tutorial"
category: "app-dev"
tags:
  - app-dev
  - canva
  - ai-agents
  - automation
  - tutorial
created: 2026-05-12
source: local
---

Trusted by teams at

30 min · no commitment · see it on your stack

### Connect Canva without Auth hassles

We manage OAuth, API Key, token refresh, and scopes, you just build.

[Try for Free](#)

## Introduction

CLIs are eating MCPs. The industry is converging on the very same idea. MCPs for all their merit can be token hungry, slow, and unreliable for complex tool chaining. However, coding agents have become incredibly good at working with CLIs, and in fact they are far more comfortable working with CLI tools than MCP.

With Composio's Universal CLI, your coding agents can talk to over 1000+ SaaS applications. With Canva, agents can create a new instagram post design, list your brand templates for social use, start a folder for this project’s assets, and more — all without worrying about authentication.

This guide walks you through Composio Universal CLI and explains how you can connect it with coding agents like Claude Code, Codex, OpenCode, etc, for end-to-end Canva automation.

## What is Universal CLI and why use it?

The idea behind building the universal CLI is to give agents a single command interface to interact with all your external applications. Here's what you'll get with it:

- **Agent-friendly**: Coding agents like Claude Code, Codex, and OpenCode can use CLI tools natively — no MCP setup required.
- **Authentication handled**: Connect once via OAuth or API Key, and all CLI commands work with your credentials automatically.
- **Tool discovery**: Search, inspect, and execute 20,000+ tools across 1000+ apps from one interface.
- **Trigger support**: Use triggers to listen for events across your apps, powered by real-time webhooks or polling under the hood.
- **Type generation**: Generate typed schemas for autocomplete and type safety in your projects.

## Prerequisites

Install the Composio CLI, authenticate, and initialize your project:

```bash
# Install the Composio CLI
curl -fsSL https://composio.dev/install | bash

# Authenticate with Composio
composio login
```

During login you'll be redirected to sign in page, finish the complete flow and you're all set.

![Composio CLI authentication flow](https://composio.dev/toolkits/_next/image?url=%2Ftoolkits%2Fcli%2Fcomposio-cli-auth.png&w=1920&q=75)

## Connecting Canva to Coding Agents via Universal CLI

Once it is installed, it's essentially done. Claude Code, Codex, OpenCode, OpenClaw, or any other agent will be able to access the CLI. A few steps to give agents access to your apps.

1. Launch your Coding Agent — Claude Code, Codex, OpenCode, anything you prefer.
2. Prompt it to "Authenticate with Canva"
3. Complete the authentication and authorization flow and your Canva integration is all set.
4. Start asking anything you want.

## Supported Tools & Triggers

Tools

Access user specific brand templates listThis year, brand template ids will change; integrations storing them must update within 6 months.

Create canva design with optional assetCreate a new canva design using a preset or custom dimensions, and add an asset with \`asset id\` from a user's project using relevant apis.

Create comment reply in designThis preview api allows replying to comments within a design on canva, with a limit of 100 replies per comment.

Create design comment in preview apiThis api is in preview and may change without notice; integrations using it won't pass review.

Create user or sub folderThis api creates a folder in a canva user's projects at the top level or within another folder, returning the new folder's id and additional details upon success.

Delete asset by idYou can delete an asset by specifying its \`assetid\`.

Exchange oauth 2 0 access or refresh tokenThe oauth 2.

Fetch asset upload job statusSummarize asset upload outcome by repeatedly calling the endpoint until a 'success' or 'failed' status is received after using the create asset upload job api.

Fetch canva connect signing public keysThe api for verifying canva webhooks, 'connect/keys,' is in preview, meaning unstable, not for public integrations, and provides a rotating jwk for signature verification to prevent replay attacks.

Fetch current user detailsReturns the user id, team id, and display name of the user account associated with the provided access token.

Fetch design metadata and access informationGets the metadata for a design.

Get design export job resultGet the outcome of a canva design export job; if done, receive download links for the design’s pages.

Initiate canva design autofill jobUpcoming brand template id updates require migration within 6 months.

Initiates canva design export jobCanva's new job feature exports designs in multiple formats using a design id, with provided download links.

List design pages with paginationPreview api for canva: subject to unannounced changes and not for public integrations.

List folder items by type with sortingLists the items in a folder, including each item's \`type\`.

List User DesignsProvides a summary of canva user designs, includes search filtering, and allows showing both self-created and shared designs with sorting options.

Move item to specified folderTransfers an item to a different folder by specifying both the destination folder's id and the item's id.

Remove folder and move contents to trashDeletes a folder by moving the user's content to trash and reassigning other users' content to their top-level projects.

Retrieve app public key setReturns the json web key set (public keys) of an app.

Retrieve a specific design commentThis preview api is subject to unannounced changes and can't be used in public integrations.

Retrieve asset metadata by idYou can retrieve the metadata of an asset by specifying its \`assetid\`.

Retrieve brand template dataset definitionCanva's brand template ids will change later this year, including a 6-month integration migration.

Retrieve canva enterprise brand template metadataUpcoming update will change brand template ids; integrations must migrate within 6 months.

Retrieve design autofill job statusApi users with canva enterprise membership can retrieve design autofill job results, potentially requiring multiple requests until a \`success\` or \`failed\` status is received.

Retrieve design import job statusGets the status and results of design import jobs created using the \[create design import job api\](https://www.

Retrieve folder details by idGets the name and other details of a folder using a folder's \`folderid\`.

RetrieveuserprofiledataCurrently, this returns the display name of the user account associated with the provided access token.

Revoke oauth tokensRevoke a refresh token to end its lineage and user consent, requiring re-authentication.

Update asset s name and tags by idYou can update the name and tags of an asset by specifying its \`assetid\`.

Update folder details by idUpdates a folder's details using its \`folderid\`.

Validate oauth token propertiesCheck an access token's validity and properties via introspection, requiring authentication.

## Universal CLI Commands for Canva

You can also manually execute CLI commands to interact with your Canva.

### Connect your Canva account

Link your Canva account and verify the connection:

```bash
# Connect your Canva account (opens OAuth flow)
composio connected-accounts link canva

# Verify the connection
composio connected-accounts list --toolkits canva
```

### Discover Canva tools

Search and inspect available Canva tools:

```bash
# List all available Canva tools
composio tools list --toolkit canva

# Search for Canva tools by action
composio tools search "canva"

# Inspect a tool's input schema
composio tools info CANVA_ACCESS_USER_SPECIFIC_BRAND_TEMPLATES_LIST
```

### Common Canva Actions

#### Access user specific brand templates list — This year, brand template ids will change; integrations storing them must update within 6 months

```bash
composio tools execute CANVA_ACCESS_USER_SPECIFIC_BRAND_TEMPLATES_LIST \
  --query "<string>" \
  --dataset "<string>" \
  --sort_by "<string>" \
  --ownership "<string>"
```

#### Create canva design with optional asset — Create a new canva design using a preset or custom dimensions, and add an asset with \`asset id\` from a user's project using relevant apis

```bash
composio tools execute CANVA_CREATE_CANVA_DESIGN_WITH_OPTIONAL_ASSET \
  --title "<string>" \
  --asset_id "<string>"
```

#### Create comment reply in design — This preview api allows replying to comments within a design on canva, with a limit of 100 replies per comment

```bash
composio tools execute CANVA_CREATE_COMMENT_REPLY_IN_DESIGN \
  --message "<string>" \
  --commentId "<string>"
```

#### Create design comment in preview api — This api is in preview and may change without notice; integrations using it won't pass review

```bash
composio tools execute CANVA_CREATE_DESIGN_COMMENT_IN_PREVIEW_API \
  --message "<string>"
```

## Generate Type Definitions

Generate typed schemas for Canva tools to get autocomplete and type safety in your project:

```bash
# Auto-detect language
composio generate --toolkits canva

# TypeScript
composio ts generate --toolkits canva

# Python
composio py generate --toolkits canva
```

## Tips & Tricks

- Always inspect a tool's input schema before executing: `composio tools info <TOOL_NAME>`
- Pipe output with jq for better readability: `composio tools execute TOOL_NAME -d '{}'  | jq`
- Set `COMPOSIO_API_KEY` as an environment variable for CI/CD pipelines
- Use `composio dev logs tools` to inspect execution logs and debug issues

## Next Steps

- Try asking your coding agent to perform various Canva operations
- Explore cross-app workflows by connecting more toolkits
- Set up triggers for real-time automation
- Use `composio generate` for typed schemas in your projects

## FAQ

### What is the Composio Universal CLI?

The Composio Universal CLI is a single command-line interface that lets coding agents and developers interact with 1000+ SaaS applications. It handles authentication, tool discovery, action execution, and trigger setup — all from the terminal, without needing to configure MCP servers.

### Which coding agents work with the Composio CLI?

Any coding agent that can run shell commands works with the Composio CLI — including Claude Code, Codex, OpenCode, OpenClaw, and others. Once the CLI is installed, agents automatically discover and use the composio commands to interact with Canva and other connected apps.

### How is the CLI different from using an MCP server for Canva?

MCP servers require configuration and can be token-heavy for complex workflows. The CLI gives agents a direct, lightweight interface — no server setup needed. Agents simply call composio commands like any other shell tool. It's faster to set up, more reliable for multi-step tool chaining, and works natively with how coding agents already operate.

### How safe is my Canva data when using the Composio CLI?

All sensitive data such as tokens, keys, and configuration is fully encrypted at rest and in transit. Composio is SOC 2 Type 2 compliant and follows strict security practices so your Canva data and credentials are handled as safely as possible. You can also bring your own OAuth credentials for full control.

### Used by agents from

![Letta](https://composio.dev/toolkits/logos/letta.svg) ![Letta](https://composio.dev/toolkits/logos/letta.svg) ![Letta](https://composio.dev/toolkits/logos/letta.svg)

## Never worry about agent reliability

We handle tool reliability, observability, and security so you never have to second-guess an agent action.[Harsha GaddipatiCo-founder, Slashy](https://composio.dev/case-study/slashy)

[

Karan skipped his own birthday party to fix our critical issue. It was 10 pm and he diverted his Waymo to help us instead. This really sets the bar, shows you the commitment you need to have when users rely on your software.

](https://composio.dev/case-study/slashy)[Abhi AryaCo-founder, Opennote](https://composio.dev/case-study/opennote)

[

A lot of students tell us that the moment their connected tools start talking to each other inside Opennote feels almost magical. The agent just knows them, and it has immensely helped in keeping new users on the platform.

](https://composio.dev/case-study/opennote)[Nirman DaveCEO, Zams](https://composio.dev/case-study/zams)

[

We chose Composio over Pipedream because it delivered depth where it mattered. It supported niche tools and tricky edge cases that other platforms simply ignored. Giving us confidence to scale without compromising.

](https://composio.dev/case-study/zams)[Ryan YuFounder, Extra Thursday](https://composio.dev/case-study/extra-thursday-case-study)

[

As a solo builder, shipping fast is life or death. The only way I can outcompete incumbents is by outmanoeuvring them. Getting bogged down in the complexities of managing agent auth would have been a death sentence for Extra Thursday.

](https://composio.dev/case-study/extra-thursday-case-study)[Tomisin JenrolaFounder & CEO, SwarmZero](https://composio.dev/case-study/swarmzero-case-study)

[

Before partnering with Composio, adding tool integrations was a slow, resource-intensive process. Each integration could take weeks or months of engineering time, and maintaining them meant constantly keeping up with API changes.

](https://composio.dev/case-study/swarmzero-case-study)[Jerome LeclancheCo-Founder, Ingram Technologies](https://composio.dev/case-study/ingram-case-study)

[

With hands-on help from their founder, we integrated Gmail and Google Drive in just 30 minutes. This level of personal support and commitment is exactly what startups should strive for.

](https://composio.dev/case-study/ingram-case-study)[Harsha GaddipatiCo-founder, Slashy](https://composio.dev/case-study/slashy)

[

Karan skipped his own birthday party to fix our critical issue. It was 10 pm and he diverted his Waymo to help us instead. This really sets the bar, shows you the commitment you need to have when users rely on your software.

](https://composio.dev/case-study/slashy)[Abhi AryaCo-founder, Opennote](https://composio.dev/case-study/opennote)

[

A lot of students tell us that the moment their connected tools start talking to each other inside Opennote feels almost magical. The agent just knows them, and it has immensely helped in keeping new users on the platform.

](https://composio.dev/case-study/opennote)[Nirman DaveCEO, Zams](https://composio.dev/case-study/zams)

[

We chose Composio over Pipedream because it delivered depth where it mattered. It supported niche tools and tricky edge cases that other platforms simply ignored. Giving us confidence to scale without compromising.

](https://composio.dev/case-study/zams)[Ryan YuFounder, Extra Thursday](https://composio.dev/case-study/extra-thursday-case-study)

[

As a solo builder, shipping fast is life or death. The only way I can outcompete incumbents is by outmanoeuvring them. Getting bogged down in the complexities of managing agent auth would have been a death sentence for Extra Thursday.

](https://composio.dev/case-study/extra-thursday-case-study)[Tomisin JenrolaFounder & CEO, SwarmZero](https://composio.dev/case-study/swarmzero-case-study)

[

Before partnering with Composio, adding tool integrations was a slow, resource-intensive process. Each integration could take weeks or months of engineering time, and maintaining them meant constantly keeping up with API changes.

](https://composio.dev/case-study/swarmzero-case-study)[Jerome LeclancheCo-Founder, Ingram Technologies](https://composio.dev/case-study/ingram-case-study)

[

With hands-on help from their founder, we integrated Gmail and Google Drive in just 30 minutes. This level of personal support and commitment is exactly what startups should strive for.

](https://composio.dev/case-study/ingram-case-study)[Harsha GaddipatiCo-founder, Slashy](https://composio.dev/case-study/slashy)

[

Karan skipped his own birthday party to fix our critical issue. It was 10 pm and he diverted his Waymo to help us instead. This really sets the bar, shows you the commitment you need to have when users rely on your software.

](https://composio.dev/case-study/slashy)[Abhi AryaCo-founder, Opennote](https://composio.dev/case-study/opennote)

[

A lot of students tell us that the moment their connected tools start talking to each other inside Opennote feels almost magical. The agent just knows them, and it has immensely helped in keeping new users on the platform.

](https://composio.dev/case-study/opennote)[Nirman DaveCEO, Zams](https://composio.dev/case-study/zams)

[

We chose Composio over Pipedream because it delivered depth where it mattered. It supported niche tools and tricky edge cases that other platforms simply ignored. Giving us confidence to scale without compromising.

](https://composio.dev/case-study/zams)[Ryan YuFounder, Extra Thursday](https://composio.dev/case-study/extra-thursday-case-study)

[

As a solo builder, shipping fast is life or death. The only way I can outcompete incumbents is by outmanoeuvring them. Getting bogged down in the complexities of managing agent auth would have been a death sentence for Extra Thursday.

](https://composio.dev/case-study/extra-thursday-case-study)[Tomisin JenrolaFounder & CEO, SwarmZero](https://composio.dev/case-study/swarmzero-case-study)

[

Before partnering with Composio, adding tool integrations was a slow, resource-intensive process. Each integration could take weeks or months of engineering time, and maintaining them meant constantly keeping up with API changes.

](https://composio.dev/case-study/swarmzero-case-study)[Jerome LeclancheCo-Founder, Ingram Technologies](https://composio.dev/case-study/ingram-case-study)

[

With hands-on help from their founder, we integrated Gmail and Google Drive in just 30 minutes. This level of personal support and commitment is exactly what startups should strive for.

](https://composio.dev/case-study/ingram-case-study)