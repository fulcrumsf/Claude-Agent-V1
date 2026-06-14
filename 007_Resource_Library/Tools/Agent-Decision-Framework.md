---
title: "Agent Decision Framework"
type: tool-doc
category: ai-agents
tags:
  - ai-agents
  - agent-design
  - agentic-ai
created: 2026-05-08
source: local
---

We handle the rest.

Just-in-time tool calls, secure delegated auth, sandboxed environments, and parallel execution across 1,000+ apps.

[GET STARTED FOR FREE](https://dashboard.composio.dev/login?utm_source=landing-page&utm_campaign=hero-cta)

## Watch Composio In Action

[ADD TO MY AGENT](https://docs.composio.dev/?utm_source=landing-page&utm_campaign=hero-add-to-agent)

Claude Cowork

Summarize everything important from Slack in the last 48 hours and send a digest to #daily-digest

COMPOSIO SEARCH TOOLS

COMPOSIO SANDBOX

Processed 2,480 messages across 12 channels in sandbox. Classified by urgency — 3 critical, 12 important.

COMPOSIO EXECUTE TOOL

Reply...

Sonnet 4.6

composio\_search\_tools

fetch slack messages and summarize3 found

SLACK\_FETCH\_MESSAGES

Fetch messages from a Slack channel

match

SLACK\_LIST\_CHANNELS

List all channels in a workspace

match

SLACK\_GET\_THREAD

Get replies in a message thread

Plan

1List all channels

2Fetch messages from last 48h

3Classify and summarize in sandbox

Warnings

!Large output auto-saved to file if >40k chars

!Rate limit: 50 req/min

composio\_manage\_connections

USER\_ID: usr\_9x2kLm7

SlackOAuth 2.0

Connected

composio\_execute\_tool

SESSION: sx-7k2m

SLACK\_SEND\_MESSAGE

channel#daily-digest

textsummary (1,240 chars)

200 OK · message sent

AGENT\_CONFIG

AGENTClaude Cowork

PROVIDERAnthropic

MODELclaude-sonnet-4-6

composio\_sandbox

sandbox · python 3.11

Fetch & process messages

2,480 msgs across 12 channels

```
channels = run_composio_tool(
  'SLACK_LIST_CHANNELS'
)
for ch in channels:
  msgs = run_composio_tool(
    'SLACK_FETCH_MESSAGES',
    channel=ch['id'],
    limit=500
  )
  smart_file_extract(msgs,
    out=f'/tmp/{ch["name"]}.json'
  )
```

Classify & summarize

3 critical, 12 important → 1.2k chars

```
files = glob('/tmp/*.json')
all_msgs = []
for f in files:
  all_msgs += json.load(open(f))

ranked = invoke_llm(
  f'Classify {len(all_msgs)} messages'
  ' by urgency: P0, P1, P2'
)
summary = invoke_llm(
  f'Summarize the {len(ranked["P0"])}'
  ' critical items concisely'
)
```

WHY COMPOSIO

## Your agents are smart.Their tools should be too.

list sentry errors and create linear issuesresolving intent...

01

### Search that thinks

Save your agent's context for what matters. Only give it the right tools, at the right time.

Tools resolved by intent, not configuration

Proposed execution plans for complex workflows

Built-in guardrails so your agent gets it right the first time

02

### Tools that learn

Your tools get sharper every day. Real agent behavior at scale is what makes Composio tools the most accurate available.

Accuracy driven by millions of real-world tool calls

Account-level optimization for your usage patterns

API-stable, agent-optimized

Agent Chat

connected

Ask your agent something...

03

### Auth that works

Stop debugging auth flows. Composio handles OAuth end-to-end: on the fly, scoped to exactly what your agent needs.

Fully managed OAuth for every connector, out of the box

Inline auth triggered by user intent, not pre-configured

Granular permission scoping that tightens as you go

Fetch & triage errors

sandbox · py 3.11

```
issues = run_composio_tool(
  'SENTRY_LIST_ISSUES',
  project='api-prod',
  status='unresolved'
)

for issue in issues:
  issue['trace'] = run_composio_tool(
    'SENTRY_GET_EVENT',
    issue_id=issue['id']
  )

ranked = invoke_llm(
  f'Classify these {len(issues)} errors.'
  ' Return P0/P1/P2 with reasoning.'
)

for error in ranked['P0']:
  run_composio_tool(
    'LINEAR_CREATE_ISSUE',
    title=error['title'],
    team_id='ENG',
    priority=1
  )
```

04

### Programmatic execution

Remote sandboxed environments where tools run as code and results live in a navigable filesystem.

Compose tools as code. Multi-step workflows, sub-LLM invocations

Secure, ephemeral sandboxes for every execution

ZERO CODE TO FULL CONTROL

## One product, every workflow

ComposioFOR YOU

Turn Claude Code, Cursor, or any MCP client into an agent that executes across all your apps. Go from asking questions to doing work.

Every tool comes production-ready — authenticated, optimized, and reliable. No setup required.

[LEARN MORE](https://composio.dev/for-you)

user — ✻ Claude Code — claude

██████╗██╗ █████╗ ██╗ ██╗██████╗ ███████╗ ██╔════╝██║ ██╔══██╗██║ ██║██╔══██╗██╔════╝ ██║ ██║ ███████║██║ ██║██║ ██║█████╗ ██║ ██║ ██╔══██║██║ ██║██║ ██║██╔══╝ ╚██████╗███████╗██║ ██║╚██████╔╝██████╔╝███████╗ ╚═════╝╚══════╝╚═╝ ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝ ██████╗ ██████╗ ██████╗ ███████╗ ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██║ ██║ ██║██║ ██║█████╗ ██║ ██║ ██║██║ ██║██╔══╝ ╚██████╗╚██████╔╝██████╔╝███████╗ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝

v2.1.50

Opus 4.6 · Claude Max

/Users/dev/projects/app

❯try "fix lint errors"

? for shortcuts/ide for Cursor

Create a PR and post to #engineering

File a ticket for this bug

Monitor uptime and alert on Slack

Draft replies to this week's emails

Check errors and create tickets

Summarize unread messages

Deploy to staging

ComposioPLATFORM

Your agent has the intelligence. Now let it execute. Go from chatbot to general-purpose agent in five lines of code.

```
tools = session.tools()
agent = Agent(
  name="Assistant",
  tools=tools,
)
```
[LEARN MORE](https://dashboard.composio.dev/?utm_source=landing-page&utm_campaign=composio-platform-card)

Support Agent

Closed 3 tickets

Email Agent

Scheduled follow-up

Slack Agent

Flagged @mention

SQL Agent

Exported CSV

Research Agent

Saved to workspace

```
░█████╗░░█████╗░███╗░░░███╗██████╗░░█████╗░░██████╗██╗░█████╗░░░░░░░██████╗██████╗░██╗░░██╗██╔══██╗██╔══██╗████╗░████║██╔══██╗██╔══██╗██╔════╝██║██╔══██╗░░░░░██╔════╝██╔══██╗██║░██╔╝██║░░╚═╝██║░░██║██╔████╔██║██████╔╝██║░░██║╚█████╗░██║██║░░██║░░░░░╚█████╗░██║░░██║█████═╝░██║░░██╗██║░░██║██║╚██╔╝██║██╔═══╝░██║░░██║░╚═══██╗██║██║░░██║░░░░░░╚═══██╗██║░░██║██╔═██╗░╚█████╔╝╚█████╔╝██║░╚═╝░██║██║░░░░░╚█████╔╝██████╔╝██║╚█████╔╝░░░░░██████╔╝██████╔╝██║░╚██╗░╚════╝░░╚════╝░╚═╝░░░░░╚═╝╚═╝░░░░░░╚════╝░╚═════╝░╚═╝░╚════╝░░░░░░╚═════╝░╚═════╝░╚═╝░░╚═╝
```

[TRY IT OUT](https://dashboard.composio.dev/?utm_source=landing-page&utm_campaign=sdk-section-cta)

SAFETY & SECURITY

## Protected from every angle with first-in-class security

![](https://composio.dev/images/security/holographic-1.png) ![](https://composio.dev/images/security/holographic-2.png)

[LEARN MORE ABOUT OUR SECURITY](https://trust.composio.dev/?utm_source=landing-page&utm_campaign=security-section)

OUR COMMUNITY

## Agents from Opennotechoose Composio

STORIES

[ALL COMMUNITY STORIES](https://composio.dev/case-studies)

“A lot of students tell us that the moment their connected tools start talking to each other inside Opennote feels almost magical. The agent just knows them”

![Opennote logo](https://composio.dev/_next/image?url=%2Fimages%2Fcommunity%2Fopennote-logo.png&w=256&q=75) ![Abhi Arya](https://composio.dev/_next/image?url=%2Fimages%2Fcommunity%2Fabhi-arya.jpeg&w=640&q=75)

Abhi Arya

Co-founder | Opennote

## Your agents are ready. Are you?

[TRY COMPOSIO TODAY](https://dashboard.composio.dev/login?utm_source=landing-page&utm_campaign=homepage-cta)