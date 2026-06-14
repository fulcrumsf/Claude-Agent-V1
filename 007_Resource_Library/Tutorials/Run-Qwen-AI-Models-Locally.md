---
title: "Run Qwen AI Models Locally"
type: tutorial
category: ai-agents
tags:
  - local-ai
  - qwen
  - vision
created: 2026-05-08
source: local
---

What if you could run an AI model that outperforms GPT-5 Nano on vision benchmarks, understands images, charts, and documents, supports over 200 languages, and fits in your pocket? And what if you could run it entirely on your laptop, offline, for free?

That's Qwen3.5. This guide walks you through getting it running on your machine in under ten minutes.

## What is Qwen3.5?

[Qwen3.5](https://qwen.ai/blog?id=qwen3.5) is Alibaba's latest generation of open-weight AI models, released in February 2026. It is not just a text model. Qwen3.5 is natively multimodal, meaning it can understand and reason about text, images, charts, documents, and video all within a single model.

Here is what makes it stand out:

- **Beats GPT-5 Nano on key benchmarks.** On MMMU-Pro (visual reasoning), Qwen3.5-9B scores 70.1 compared to GPT-5 Nano's 57.2. On MathVision it leads by 17 points. On document understanding it leads by over 30 points. A 9 billion parameter model running on a laptop outperforms a cloud-hosted OpenAI model on these tasks.
- **Natively multimodal.** It processes text, images, and video through a unified architecture, not bolted-on vision adapters. You can drop in a screenshot, a chart, or a photo and ask questions about it.
- **256K context window.** That is the equivalent of a full novel or a large codebase in a single conversation.
- **201 languages supported.** Up from 119 in the previous generation.
- **Two inference modes.** A "thinking" mode for deep step-by-step reasoning, and a fast "non-thinking" mode for everyday tasks.
- **Fully open-weight under Apache 2.0.** Download it, run it, fine-tune it, no strings attached.

The models range from 0.8B parameters (fits on almost any machine) to 397B (for serious infrastructure). For a laptop, the sweet spot is the 9B model.

## What is Ollama?

[Ollama](https://ollama.com/) is the easiest way to run large language models locally. It handles all the complexity behind the scenes, from model quantization to GPU routing to serving a local API. You install it, pull a model, and start chatting.

On Apple Silicon Macs, Ollama takes full advantage of the unified memory architecture, which means your CPU and GPU share the same memory pool. This is why even large models run surprisingly well on a MacBook.

## What you need

- A Mac with Apple Silicon (M1/M2/M3/M4), or a Windows/Linux machine with a decent GPU
- At least **8 GB of RAM** for the smaller models, **12 GB+** recommended for the 9B model
- [Homebrew](https://brew.sh/) installed (for Mac)

## Step 1: Install Ollama

On Mac, install via Homebrew:

```
brew install ollama
```

Once installed, start the Ollama background service:

```
brew services start ollama
```

Ollama is now running silently in the background, ready to serve models.

## Step 2: Choose your model size

Qwen3.5 comes in several sizes. Pick based on your hardware:

| Model | Download size | RAM needed | Best for |
| --- | --- | --- | --- |
| `qwen3.5:0.8b` | ~1 GB | 4 GB | Very fast, basic tasks |
| `qwen3.5:2b` | ~2.7 GB | 6 GB | Fast, decent quality |
| `qwen3.5:4b` | ~3.4 GB | 8 GB | Good balance |
| `qwen3.5:9b` | ~6.6 GB | 12 GB | **Sweet spot, recommended** |
| `qwen3.5:27b` | ~17 GB | 32 GB | High quality, slower |

For most people, **`qwen3.5:9b`** is the right choice. It is the model that beats GPT-5 Nano on vision benchmarks, and it runs comfortably on a modern laptop.

If you have 32 GB+ RAM (like a MacBook Pro M4 Pro with 48 GB), go for `qwen3.5:27b`. The quality jump is noticeable, especially for complex coding tasks and long-form writing.

## Step 3: Download and run the model

Pull the 9B model:

```
ollama pull qwen3.5:9b
```

This downloads the model to your machine (~6.6 GB). Once complete, start chatting:

```
ollama run qwen3.5:9b
```

You will see a `>>>` prompt. Type your message and hit Enter.

```
>>> Tell me something interesting about black holes
```

That is it. You are now talking to a local AI model, completely offline.

## Thinking mode vs non-thinking mode

One of the best features of Qwen3.5 is that you can switch between two inference modes depending on what you need.

**Thinking mode (default):** The model works through the problem step by step before answering. You will see a `<think>...</think>` block in the response showing its reasoning. This is powerful for tasks like debugging code, solving math problems, or working through complex logic. The downside is it takes longer.

**Non-thinking mode:** The model skips the internal reasoning and responds directly. It is significantly faster, and for most everyday tasks like writing, summarising, answering questions, and general chat, the quality is excellent.

To switch to non-thinking mode during a session, type:

```
/set nothink
```

To switch back to thinking mode:

```
/set think
```

**Recommendation:** Start with `/set nothink`. For most things, you will not miss the extra reasoning, and the speed difference makes the whole experience feel snappier. Switch thinking on only when you hit a problem that actually needs it.

## Useful commands in the chat session

| Command | What it does |
| --- | --- |
| `/set nothink` | Disable thinking mode (faster responses) |
| `/set think` | Enable thinking mode (deeper reasoning) |
| `/bye` | Exit the chat |

## Switching between model sizes

Want to try the 27B model?

```
ollama pull qwen3.5:27b
ollama run qwen3.5:27b
```

Or go smaller if you need more speed:

```
ollama run qwen3.5:4b
```

You can have multiple models downloaded and switch between them freely. Use `ollama list` to see what you have:

```
ollama list
```

## Why run AI locally?

- **Privacy:** your conversations never leave your machine. Great for sensitive work, client data, or anything you would rather keep off the cloud.
- **No cost:** no API bills, no monthly subscription, no usage limits.
- **Offline:** works on a plane, a train, anywhere without internet.
- **Speed:** no network round trips once the model is loaded.
- **Control:** pick exactly which model version you run, and keep it there.

The trade-off is that local models are smaller than the largest frontier cloud models. But Qwen3.5-9B beating GPT-5 Nano on multiple benchmarks while running on a laptop shows how fast that gap is closing. For a huge range of real tasks, local is now good enough.

## Wrapping up

Three commands and under ten minutes is all it takes to have Qwen3.5 running locally. Ollama handles all the hard parts, and the model itself is one of the most capable open-weight models available today. Run it offline, keep your data private, and use `/set nothink` to get fast, snappy responses for most of what you need.