---
title: "OpenRouter Client SDKs"
type: api-doc
category: app-dev
tags:
  - openrouter
  - api
  - sdk
created: 2026-05-08
source: local
---

The Client SDKs give you a thin, type-safe layer over the OpenRouter REST API. It handles authentication, request validation, and response typing so you can call any of 300+ models with a single function call — no boilerplate, no provider-specific quirks.

## Install instructions

| Language | Package | Install |
| --- | --- | --- |
| TypeScript | [`@openrouter/sdk`](https://www.npmjs.com/package/@openrouter/sdk) | `npm install @openrouter/sdk` |
| Python | [`openrouter`](https://pypi.org/project/openrouter/) | `pip install openrouter` |
| Go | [`go-sdk`](https://pkg.go.dev/github.com/OpenRouterTeam/go-sdk) | `go get github.com/OpenRouterTeam/go-sdk` |

All three SDKs are auto-generated from the OpenRouter OpenAPI spec, so new models, parameters, and endpoints appear immediately after each API release.

## When to use the Client SDKs

Choose the Client SDKs when you need **direct, efficient access to model inference** and want to manage your own application logic:

- **Single-turn completions** — send a prompt, get a response
- **Streaming responses** — real-time token-by-token output
- **Embeddings, video, and rerank** — generate vector representations, create videos, and rerank results
- **API key and credit management** — programmatic control over your account
- **Custom orchestration** — you handle conversation loops, tool dispatch, and state yourself

The Client SDKs are intentionally lean. It mirrors the OpenRouter API surface 1:1 with full type safety, so there is no abstraction to fight when you need fine-grained control.

If you want higher-level primitives for building agents — multi-turn loops, tool definitions, stop conditions, and conversation state management — see the [Agent SDK](https://openrouter.ai/docs/agent-sdk/overview) instead.

## Quick example

```
1import OpenRouter from '@openrouter/sdk';
2
3const client = new OpenRouter({
4  apiKey: process.env.OPENROUTER_API_KEY,
5});
6
7const response = await client.chat.send({
8  model: 'openai/gpt-5.2',
9  messages: [
10    { role: 'user', content: 'Explain quantum computing in one sentence.' },
11  ],
12});
13
14console.log(response.choices[0].message.content);
```

## Client SDKs vs Agent SDK

|  | Client SDKs | Agent SDK |
| --- | --- | --- |
| **Focus** | Lean API client — mirrors the REST API with full type safety | Agentic primitives — multi-turn loops, tools, stop conditions |
| **Use when** | You want direct model calls and manage orchestration yourself | You want built-in agent loops, tool execution, and state management |
| **Conversation state** | You manage it | Managed for you via `callModel` |
| **Tool execution** | You dispatch tool calls | Automatic with the `tool()` helper |
| **Languages** | TypeScript, Python, Go | TypeScript |

## Next steps

- [TypeScript SDK reference](https://openrouter.ai/docs/client-sdks/typescript)
- [Python SDK reference](https://openrouter.ai/docs/client-sdks/python)
- [Go SDK reference](https://openrouter.ai/docs/client-sdks/go)
- [Agent SDK overview](https://openrouter.ai/docs/agent-sdk/overview) — for building agents with multi-turn loops and tools