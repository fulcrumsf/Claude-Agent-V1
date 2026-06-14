---
title: "OpenAI Post Harness Layer"
type: research
category: ai-agents
tags:
  - openai
  - ai-agents
  - agentic-ai
created: 2026-05-08
source: local
---

![](https://www.youtube.com/watch?v=5p6h23Md4Zw)

👉 Access our AI Architects course & join hundreds of serious AI builders in our community  
https://www.theaiautomators.com/?utm\_source=youtube&utm\_medium=video&utm\_campaign=tutorial&utm\_content=openai\_symphony  
  
Links:  
https://www.youtube.com/watch?v=YJCe8hvZrxs  
https://openai.com/index/open-source-codex-orchestration-symphony/  
https://martinfowler.com/articles/harness-engineering.html  
https://github.com/openai/symphony  
https://openai.com/index/harness-engineering/  
  
OpenAI just open-sourced Symphony, their internal orchestration spec for scaling autonomous coding agents, and it highlights one of the biggest shifts happening in AI engineering right now. As coding agents become more capable, humans become the bottleneck, and the real work moves from writing code to building the scaffolding around the agents.  
  
In this video, I break down the mental models behind agent harness engineering and show you how to think about building reliable autonomous systems at scale. Whether you're trying to scale Claude Code beyond a few chat sessions, or designing orchestration into your own AI powered apps, these frameworks will help you architect systems that actually work in production.  
  
What's covered:  
\- The definition of an agent harness and why the term has become so broad  
\- The inner harness vs outer harness mental model from Brigetta Berkeler's harness engineering article  
\- How the AI model acts like a CPU while the harness manages memory, sub agents, tool execution, and more  
\- Why metaprompting frameworks like Superpowers, GSD, and BMAD only get you so far  
\- Guides vs sensors: steering agents forward and feeding deterministic and inferential checks back in  
\- Why computational sensors like linters, types, and schemas are heavily underused by AI builders  
\- LLM as a judge and inferential sensor patterns for feedback loops  
\- Ralph Wiggum loops as a simple example  
\- Extending the mental model to harness layers in AI apps that you build  
\- The deterministic vs probabilistic spectrum for harnesses  
\- The orchestrator and scheduler layer sitting above inner and outer harnesses  
  
How OpenAI's Symphony spec uses Linear as the human interface for ticket-based agent work  
Solving the two biggest problems with parallel agents: clashing and human in the loop design  
  
The future of AI engineering is less about prompting and more about scaffolding. The model is the CPU, but the harness is where the real engineering happens.  
  
If you want to go deeper on AI architecture, harness engineering, and agentic retrieval, check out our AI Architects course linked above.  
  
Chapters:  
0:00 - Overview  
0:47 - OpenAI Symphony spec  
2:35 - What is an agent harness  
4:20 - Inner vs outer harness  
5:24 - Guides and sensors  
7:34 - Harness layers in AI apps  
8:37 - The orchestrator layer  
9:46 - Getting started with Symphony

## Transcript

### Overview

**0:00** · OpenAI just published a fascinating article about their new open-source agent orchestrator to help overcome the biggest bottlenecks they encountered when trying to scale autonomous coding agents. And there are some interesting insights here that could really help us all when we're building our own agentic systems. Back in February, OpenAI showed a relatively controversial experiment they were running internally to create software with zero lines of manually written code.

**0:24** · Instead of micromanaging the coding agents, the primary job of the engineer was now to create scaffolding around the coding agent to enable it to do work with less supervision. As these systems became increasingly efficient, humans could no longer keep up with coding agents and all of a sudden the humans were now the biggest bottleneck in the process. And that was the birth of OpenAI's open-sourced Symphony orchestration spec. So what exactly is Symfony? Well, at its core, Symfony is an agent orchestrator that takes an issue tracker like Linear here and turns it into a tool that can trigger coding agents.

### OpenAI Symphony spec

**0:55** · The concept here is pretty simple. For every ticket on this board, Symphfony makes sure there's a coding agent running for it in its own isolated workspace, working continuously until the ticket is done. And OpenAI are essentially creating a state machine flow using linear here. This can then potentially allow teams to work at a higher level of abstraction rather than just babysitting and supervising individual coding sessions. And in theory, less technical staff members can also get involved in the process.

**1:22** · When you go to the GitHub repo, the first thing you'll notice is that this is mostly just a spec.md file, but they also have a prototype version you can use created in Elixir, which I'll talk about in a few minutes. OpenAI encourage you to point your favorite coding agent at the spec and then have it implement its own version in whatever language you want and also get it to orchestrate against whatever coding agent you want, not just codecs. So you don't have to have a codec subscription to run this. Surprisingly enough, even the OpenAI article shows some post on X where people are showing how they implemented this to orchestrate cloud code sessions.

**1:53** · So you have two options to run with here. If you want to use their reference elixir implementation, you can clone the repo and then get your coding agent to help with the setup.

**2:02** · Then you can connect that to a linear account using your personal API key and then that will continuously pull the tickets here. That then calls Codeex in app server mode and app server mode runs the codeex CLI as a longived process and then Symfony can then call that programmatically. There's certainly plenty of OpenAI marketing within this article. Like they've stated that this has resulted in a 500% increase in landed pull requests on some teams, but countless devs have converged on similar types of systems to this.

**2:28** · And OpenAI are certainly not the first dev team to build orchestration around coding agents. I think the most important lesson here is unpacking the architectural layers that make a system like this work and how we can then make effective use of those systems in our own projects. And many of you watching this will already know that attempting to scale AI coding agents beyond a few concurrent chat sessions definitely comes with its own set of challenges. So you may be staring at a coding chat window wondering how do I turn this into a reliable autonomous agent at scale for my project.

### What is an agent harness

**3:00** · Or you may want to build advanced orchestration features into your AI powered apps but you're getting lost in the architecture. I'm going to share some great mental models and resources that I find really useful.

**3:11** · Let's start by clearing up some ambiguity about the term agent harness, which at this point could mean many different things. As Philip Schmid put it, "An agent harness is the infrastructure that wraps around an AI model." As you can see from his clearly AI generated image here, the agent harness manages the vast majority of the work within our AI systems. And he compares the AI model to that of the CPU of a computer in that it is very important, but it has a very specific function. An LLM is really only able to reason about its responses and then generate an output such as text.

**3:40** · Everything beyond that from the illusion of memory and chat history to managing sub agents to actually managing the execution of tool calls that's all actually managed within the harness code. So the definition of an agent harness is incredibly broad. And to make better sense of this we're going to borrow some mental models from Vetta Berkeler's great article on harness engineering where she suggested that we should view agent harnesses in two separate layers. The first is the inner harness. The inner harness is everything that ships inside your AI coding agent, whether it be cloud code or cursor or codecs.

**4:11** · Of course, they're very powerful out of the box already. They ship inside with the ability to manage sub agents, sandbox code execution, skills, hooks, tools, permissions, and more. But as Brigitta writes in this article, to let coding agents work with less supervision, we need ways to increase our confidence in their result. But how exactly do we do that? As a starting point, we can try and give our coding agents better context of the overall code base. We can try and convince them to do a better job via better prompting.

### Inner vs outer harness

**4:41** · And we can also use meta prompting frameworks such as superpowers or GSD version one or VMAD. And those things absolutely help, but they only go so far. And that's where the real engineering of the outer harness comes into play. Coding agents such as Claude or Codeex expose features that let us build an outer harness around them. And these harnesses are actual code that controls the agent life cycle programmatically.

**5:02** · So instead of using a meta prompting framework where we might ask the AI agent to reset the context, the outer harness can actually deterministically terminate the session, clear the context, read the task state from disk, inject the relevant files, and then work from there. So Ralph loops or projects like Gas Town or Archon are all examples of systems that act as outer harnesses. In this article, it said that the harness acts like a cybernetic governor combining feed forward and feedback to regulate the codebase towards the desired state.

### Guides and sensors

**5:31** · That feedback mechanism is one of the most important parts of this process. There's a very useful distinction between guides and sensors here where the guides help steer the agent in the right direction.

**5:43** · So these are anything that tries to make the agents first attempt better. So your agent might read from an agent's MD file or you may provide skills and playbooks and examples that they can work from.

**5:53** · But the AI agent is not always going to get things right and even if so not necessarily according to your own behaviors and rules and that's where the very important feedback loop comes in and these are referred to as sensors. So we might have deterministic computationalbased sensors such as llinters and types and schemas. So for example whenever your coding agent creates code you can run those through deterministic checks without using AI at all and then feed that back to the model.

**6:20** · And one of the main arguments made within this article is that these computational type checks are heavily underused by AI builders. Of course, you can also have sensors powered by AI known as inferential sensors such as you can feed code generated by an LLM into another call to an LLM, ideally another model where it can act as a judge and then that can be fed back into the model and humans then continuously steer and optimize the components of this outer harness.

**6:46** · If we go back to our OpenAI article on harness engineering, they've run with this type of concept where the agent is called in a Ralph Wigum loop until all human reviewers are satisfied.

**6:56** · Running an external Ralph Wigum loop, not the one built into Claude code directly, by the way, is a very simple example of an outer harness. It can just keep spawning Claude sessions again and again and again through brute force iteration until a certain goal has been met. and other outer harnesses can just take this thin orchestrator concept as a starting point and bring it many steps further and potentially in many different directions. Archon is a great example of a tool that allows you to create your own outer harnesses which can enforce your agents to act in a certain deterministic way.

**7:26** · It already includes a lot of out ofthe-box workflows and it even allows for parallel executions of tasks. We use this inner outer harness distinction as a mental model not only for coding agents but also for agentic systems we build. In our full stack AI builder series, Daniel walks through the creation of a contract review harness that adds deterministic aspects to the agentic workflow. And this can essentially be seen as an outer harness, a configurable aspect that's layered on top of the inner harness core functionality of the agentic system.

### Harness layers in AI apps

**7:54** · It can have guides and sensors that are automatically fed back into the agent such as automated computational document checks that don't use AI at all as well as inferential checks such as LLM as a judge. And these harnesses will lie on a spectrum between either being very deterministic or very probabilistic.

**8:13** · That contract review harness tends to follow a very specific workflow. But many other harnesses will be a lot more open-ended, such as deep research harnesses. And these are essentially the opposite shape. They're broad, open-ended, and agentic throughout, but they can still have plenty of deterministic scaffolding around them, such as computational checking of citations or multiple layers of LM reviews before they're passed back for human review. As we start building upon the scaffolding on top of our AI agents, you may even consider that they start becoming their own layer on top of the mental model we've talked about already.

### The orchestrator layer

**8:47** · And this layer could be seen as the overarching orchestrator or scheduler layer. And that's very much where OpenAI positions systems created using their new symphony spec as this is really multi-agent orchestration at a higher level. These are all mental models and metaphors. They just help our general understanding of the concepts and the lines can very much be blurred between them. For example, Gas Town is an orchestration framework where it takes the concept of a Ralph Wiggum loop have many of them running at once along with automated orchestration around those instances.

**9:17** · And this can certainly get quite chaotic. But frameworks like this are trying to solve the problem of getting many agents to work reliably in parallel. And the two biggest issues that people face other than their intense token usage and AI builds with systems like this is twofold. It's making AI agents work reliably together without clashing and adding in the correct human in the loop layers where humans are in the most important parts of the process without micromanaging everything because that becomes the biggest bottleneck and again that's where we come back to this Symfony spec.

### Getting started with Symphony

**9:49** · Symfony started with a concept that any open task should get picked up and completed by an agent instead of developers managing codec sessions in multiple tabs. They made this issue tracker in linear and use that as the human interface. Those tickets then trigger the coding agent to work autonomously on those tasks as required and then report back to the user when required. If you want to get started with the Symfony open-source spec, it's available on the GitHub repo linked below.

**10:14** · And you can get your own coding agent to create an orchestration system based on this spec in whatever language you want, or you can also use their out-of-the-box demo example. In this video, we went through a lot of AI architecture concepts. If you found that useful, you should definitely check out our AI architects course linked below, which will help give you a deeper understanding of AI systems, technical foundations, harness engineering, agentic retrieval, and more.

**10:36** · And if you like this video, you'll love the previous video on our channel where Daniel goes through a deep dive into the various agent frameworks and services you can use when building out AI systems.