---
title: "Vast.ai GPU Cloud for Rent"
tags:
  - App
  - LLM
created: 2026-09-13
---

## Real-time GPU infrastructure

Prices set by supply and demand across 20,000+ GPUs. Transparent. Programmatically queryable.

[View All GPUs](https://vast.ai/pricing)

## How it works

From sign-up to running GPU workloads in under five minutes.

1

### Add credit & get your API key

Start with as little as $5. Grab your API key from the console — no contracts, no sales calls.

2

### Search GPUs

Filter by model, VRAM, price, and availability — via console or API.

3

### Deploy

Launch instances in seconds. Scale up or down programmatically.

[Get Started for $5](https://cloud.vast.ai/)

## Compare. Launch. Exit. Repeat.

Every GPU on Vast.ai is provisioned through code. The same API that developers use to deploy in seconds is the interface agents use to procure and optimize at scale.

Python SDK & CLI

`pip install vastai`

One install gives you both the CLI and Python SDK.

SDK — Programmatic compute provisioning in five lines of code.[Docs →](https://docs.vast.ai/sdk/python/quickstart)

CLI — Search, filter, and deploy from your terminal.[Docs →](https://docs.vast.ai/cli/get-started)

REST API [Docs →](https://docs.vast.ai/api-reference/introduction)

The interface agents call to provision infrastructure.

`curl -H "Authorization: Bearer $VAST_API_KEY" https://cloud.vast.ai/api/v1/bundles/`

[Explore Developer Tools](https://vast.ai/developers)

```
$ vastai search offers "gpu_name=H100_SXM num_gpus=8"  ID     CUDA  Num  Model      VRAM    $/hr  8842   12.4   8   H100_SXM   80 GB   5.12  9103   12.4   8   H100_SXM   80 GB   5.44 $ vastai create instance 8842 --image vllm/vllm-openai:latest  Started. Instance ID: 12847 $ vastai show instance 12847  Status: running | Cost: $5.12/hr | Uptime: 3m 22s
```

## One platform. Three ways to deploy.

GPU Cloud for full control. Serverless for zero-ops inference. Clusters for large-scale training.

### GPU Cloud

On-demand instances across 40+ data centers and 20,000+ GPUs. Deploy in seconds via CLI, SDK, or API.

[Explore GPU Cloud](https://vast.ai/products/gpu-cloud)

### Serverless

Deploy models as endpoints with automatic benchmarking and optimization across GPU types. Autoscale to zero, pay only for compute time.

[Try Serverless](https://vast.ai/products/serverless)

### Clusters

Dedicated multi-node GPU clusters with InfiniBand networking for large-scale training.

[View Clusters](https://vast.ai/products/clusters)

![Case Studies](https://vast.ai/_next/image?url=%2Fuploads%2Faurora%2Fimages%2Fimg-home-caseStudies.png&w=2048&q=75)

Built for Every AI Workload

From training to inference, fine-tuning to rendering — run any GPU workload on Vast.

[Use Cases](https://vast.ai/use-cases)

[AI/ML Frameworks](https://vast.ai/use-cases/ai-ml-frameworks) [AI Text Generation](https://vast.ai/use-cases/ai-text-generation) [AI Image + Video Generation](https://vast.ai/use-cases/ai-image-video-generation) [AI Agents](https://vast.ai/use-cases/ai-agents) [Batch Data Processing](https://vast.ai/use-cases/batch-data-processing) [Audio-to-Text Transcription](https://vast.ai/use-cases/audio-to-text-transcription) [AI Fine Tuning](https://vast.ai/use-cases/ai-fine-tuning) [Virtual Computing](https://vast.ai/use-cases/virtual-computing) [GPU Programming](https://vast.ai/use-cases/gpu-programming) [Graphics Rendering](https://vast.ai/use-cases/3d-rendering)

> “Vast.ai reduced our GPU costs by over 60% while giving us the flexibility to scale training jobs on demand. We serve 200K daily users without breaking the bank.”

## How teams build on Vast.ai

See how teams use Vast.ai to scale AI infrastructure and accelerate production workloads.

[![Creatix Technology](https://vast.ai/_next/image?url=%2Fcase-studies%2Fimg-caseStudy-creatix-sm.webp&w=2048&q=75)](https://vast.ai/case-studies/creatix-technology)

Creatix Technology

### [Creatix Technology Scales to 200K Daily Users with Vast.ai's GPU Cloud](https://vast.ai/case-studies/creatix-technology)

How a fast-growing AI app company cut infrastructure costs by over 60% and powered millions of new users with Vast.ai.

Tech

[View Case Study](https://vast.ai/case-studies/creatix-technology)

[![PAICON](https://vast.ai/_next/image?url=%2Fcase-studies%2Fimg-caseStudy-paicon-sm.webp&w=2048&q=75)](https://vast.ai/case-studies/paicon)

PAICON

### [PAICON Accelerates Global, Data-Centric Cancer Diagnostics with Vast.ai](https://vast.ai/case-studies/paicon)

How a global oncology data platform used Vast.ai’s GPU cloud to rapidly iterate on Athena—validating that diversity can matter more than scale—while significantly reducing research-phase training costs.

Medical AI

[View Case Study](https://vast.ai/case-studies/paicon)