---
title: "AI Essentials Transcript"
type: doc
category: ai-agents
tags:
  - ai-fundamentals
  - ai-agents
  - llms
  - machine-learning
created: 2026-05-08
source: local
---

AI Essentials: Building Foundational Knowledge

View course

Video 1 - Intro

[00:00:00]  Welcome  to  your  essential  guide  to  Artiﬁcial  Intelligence.  AI  is  already transforming how we work, and it's rapidly
shifting  task  automation,  content  generation,  and  other  capabilities  across  all  industries  globally.  But  we  may  not  fully
understand  what  AI  is,  how  it  works,  and  the  potential  risks  and  mindsets  associated  with  it.  This  course will give you the
foundational knowledge that you need to embrace this change in the rush to adopt AI. By the end of this course, you'll be able
to  deﬁne  Artiﬁcial Intelligence. Differentiate key concepts in the ﬁeld. Explain the basic process of how AI models learn from
data,  as  well  as  recognize  common  applications,  opportunities  and  risks  associated  with  AI.  Importantly,  you'll  be  able  to
distinguish between an "AI-ﬁrst" and a "Data-ﬁrst" approach. Let's jump right in.

Video 2 - What is AI? Deﬁning the core concepts

[00:00:00] Artiﬁcial Intelligence has rapidly become an active partner in our daily work, but to work effectively with it, we ﬁrst
need to understand some important underlying concepts and deﬁnitions. In its broadest deﬁnition, Artiﬁcial Intelligence is the
science and technology dedicated to creating computer systems that can simulate human-like intelligence. Early AI used explicit
rules to make decisions based on strict inputs. Simple commands like "If the current time is between 8:00 PM and 6:00 AM, turn
the headlights on." These decision trees can get much more complex. Consider opponents in a computer game reacting to the
player as a great example. This sort of deterministic decision making is still incredibly relevant and it'll continue to power the
majority  of  software,  but  the  emergence  of  Machine  Learning  has  opened  up new possibilities. It allows machines to learn,
reason,  and  solve  much  more  complex  problems  with  a  much  broader  set  of  information  at  its  disposal.  Instead  of
programming  explicit  rules,  we  now  feed  a system data and it learns to ﬁnd patterns and make [00:01:00] predictions on its
own. For example, modern credit card fraud detection can't be manually programmed for every scenario. Instead, it analyzes
millions of transactions to uncover normal spending versus suspicious activity, and does so in real time, constantly evolving to
identify potential issues. Machine Learning can be divided down into a few, several specialized ﬁelds. So let's deﬁne a few of

1

these  and  get  familiar  with  the  concepts.  Some  of  the  most  important  areas  of  development  and  innovation  are  around
classiﬁcation  and  Natural  Language  Processing.  This  is  allowing  software  to  understand  natural  human  language and extract
concepts,  topics,  emotions,  sentiment,  and  more.  For  example,  when  your  email  provider  automatically  gets  an  incoming
message and buckets it into "promotional" or "social" or "spam," and does so without human input. That classiﬁcation process is
using natural language processing to understand the text of that message.

We  also  look  at  pattern  and  anomaly  detection.  This  is  using  machines  to  process  massive  amounts  of  data  and  identify
patterns that would otherwise be difﬁcult or impossible to [00:02:00] ﬁnd. This enables really cool stuff like ﬁnding thousands of
new planets and other solar systems by analyzing the patterns of light coming from the stars. For recommendation engines, this
is  something you'll have seen in action regularly on your favorite streaming platforms, online retailers, and more. They're the
reason that you've been recommended every single season of Love Island after watching Married At First Sight that one time.
The last specialized area of machine learning we'll cover is Generative AI. These are applications that can create media, whether
that's text, video, images, audio, or more using Large Language Models and other neural networks. We're gonna talk a lot more
about Generative AI and how we can use it and interact with it throughout the rest of this course. The recent surge in interest in
Artiﬁcial Intelligence started with Generative AI. ChatGPT was released a number of years ago, and on the back of that, every
consumer suddenly had access to a Large Language Model. These foundational models that use neural networks and enormous
data  sets  can  start  to  provide  human-like  outputs.  In  addition  to  ChatGPT,  things  like  [00:03:00]  Google  Gemini, Anthropics
Claude, are all chat interfaces that have contributed to this rise in public awareness. When a user interacts with these chat bots,
they  input  what's  called  a  prompt.  It's  often  a  natural language or sometimes an image or a video, and that large language
model  or  other  models,  takes  that  prompt  and  then  tries  to  generate  a  response.  This  response  can  come  back  in those
multiple forms of media as well. It's important to recognize that even though these interactions can feel very human-like, and
they can result in interesting, creative, and valuable conversations, a Large Language Model crafts its response very differently
to how a human would, and we need to understand that difference in order to understand how to best work with these tools.
Now let's talk about Agentic AI. Put simply an agent is any program that is able to take a goal as an input and without additional
human guidance, use the tools at its disposal to achieve that goal. Historically, this has been limited by the kinds of inputs that
an agent is programmed to accept. For example, a recommendations agent at Netﬂix takes in the records of what you [00:04:00]
watched and liked in a very rigid format. It is very good at taking the steps to then return a list of things that you should watch
next, ranked by relevance, but that's also coming back to you in a very rigid format, it's a list. So how do we then take that and
make  it  Agentic  AI?  The  answer  comes  from  the ability of Generative AI to interpret and understand a much wider range of
inputs,  like  a  prompt,  extract meaning and intention, and then decide on what the most appropriate response is. Unlike our
Netﬂix recommendations agent, our new agent can be a generalist and it can handle all sorts of scenarios. So let's interact with
our generalist. Instead of clicking a button and seeing a list of recommended ﬁlms, I can ask for what I want. I'm looking for a
ﬁlm I would love, but I'm in the mood for a comedy, not too goofy, and I'm not ever in the mood for Vince Vaughn.

2

Our original Netﬂix agent wouldn't know what to do with this, but our AI agent has no problems. Here's what happens at a very
high level. The AI agent received my prompt and it understands what I'm asking for. It breaks down the question into its parts
and  [00:05:00]  decides  what  tools  are  best  to  solve  the  problem.  Because  I  asked  for  a  ﬁlm  I  would  love,  called  the
recommendation  agent,  our  basic  list  returning  agent  we  looked  at  earlier.  Because  I  speciﬁed comedy, it ﬁlters that list of
recommendations by genre, and then it ﬁlters out ﬁlms starring Mr. Vaughn. Not goofy is tricky and it's subjective, but our agent
can handle it because it can read the descriptions and reviews for the ﬁlms that are still left on my recommended list, and then
it can interpret those reviews and those descriptions and decide for itself what is likely to be a goofy ﬁlm. Our AI agent now has
its answer, a list of ﬁlms that ﬁt my criteria. And it got there by completing a complex set of tasks. As a ﬁnal ﬂourish, it can then
respond in natural language to me, listing those ﬁlms and even justifying and telling me why it came up with that list. The ﬁnal
aspect of an agent is that they can be given feedback and often they can be given tools to then take action in the real world.
Great, that second ﬁlm on the list looks perfect. Turn on my smart TV, start streaming. With that ﬂexible foundation, [00:06:00]
imagine all the things that we can start to build agents around. This creates risk and opportunity that's important to understand
how these technologies work and how they're trained. Next, we'll take a closer look at how these models are created and we'll
understand the importance of the data that creates and empowers them.

Video 3 - How AI learns

[00:00:00]  If  Machine  Learning  is  the  engine  of  AI,  data  is  the  fuel,  and  just  like  fuel,  it's  important  to consider the quality
alongside the quantity of data available. While the models themselves are built on very large data sets that can be relatively
messy, to successfully implement AI in our systems, we need to augment that with well-structured data, enriched by context
and available at scale. The best way to understand the importance of these data sets is to take a look at how the models that
power Generative AI are created. The process is a bit different depending on the type of model, but in general consists of two
key stages: training and tuning. These steps are typically handled by the model builders themselves, like OpenAI, and there are
many thousands of available models, ChatGPT-5, Claude Sonnet being very popular examples. Once a model is ready, it can
then be implemented into a range of different applications and products. It's this implementation stage where the data unique
to the task at hand becomes very important. Let's look at the process used to create Large Language Models, or LLMs, a bit
[00:01:00]  closer. These are the models that generate primarily text, although you will see multimodal models based on this
process that can create almost any type of media. First, the training stage. In this stage, the model learns patterns from massive
amounts  of  text  data.  We're  talking  about  billions  of  words  scraped  from  books,  websites,  articles,  and  other sources. The
model's  not  memorizing  this  content.  Instead,  it's  learning  to  predict what word comes next by recognizing patterns in how
natural  language  works.  Grammar  rules, common facts, and how words and ideas typically relate to each other. The training
process is self-supervised, which means the model teaches itself. It does this by predicting the next word in a sentence over

3

and over again millions of times. And when it gets the prediction wrong, it adjusts. When it gets them right, it reinforces what it
learned  and  stores  that  correctly.  Through  this  repetition,  the  model  builds  a  sophisticated understanding of how language
works. This stage is computationally expensive. It requires powerful hardware and it can take weeks or months, but at the end,
you have a foundational model that can work with language effectively, [00:02:00] but it isn't ready yet for speciﬁc tasks. Next is
the tuning stage. The foundation model knows its language, but it doesn't yet know how to behave or what its purpose is. It
might complete sentences, but it won't necessarily answer questions in a useful way or follow instructions, and this is where
tuning comes in. Model builders use smaller, carefully curated data sets to shape the model's behavior and to give it direction.
This  includes  instruction  tuning,  which  is  training  on  examples  of  questions  and  responses,  so  the  model  learns  to  follow
directions  and  to  interact  conversationally.  Behavioral  alignment  teaches  the  model  to  behave  in  a  speciﬁc  way  through
feedback from human reviewers, whether that be helpful or informative, persuasive and creative, or technical. This stage gives
the model its personality and purpose, and different organizations will tune models differently based on their goals. A model
might  be  tuned  to  be  a  careful  research  assistant  or  an  aggressive  sales  agent,  or  a  creative  writing  partner. It's faster and
cheaper  than  the  training  stage  because it uses much less data, but that data needs to be high quality because it'll directly
shape how the model [00:03:00] will act.

Finally, we have the implementation stage. This is where an organization's unique data comes into play. Once a model's ready,
it can be integrated into actual applications: customer service chat bots, content generators, research assistants, and more. At
this  stage,  the  quality  and structure of your speciﬁc data becomes critical. You might connect the model to your company's
knowledge  base  so  it  can  answer  questions  about  your  product.  You  could  ﬁne  tune it on your industry's terminology and
process or provide context about your customers, your workﬂows, and your business rules. The model of general knowledge
from training gives a capability. Then this ongoing training of well-structured context-rich data being fed to it is how you get it to
serve your speciﬁc needs. And this is why an organization that wants to heavily invest in AI has to heavily invest in their data. To
make sure that the model is useful for a particular use case and is relevant to the context. Understanding this process matters
because it shows you where you have control and where you don't. You can't change how a foundation model was trained, and
you often don't know exactly what data went into it or what [00:04:00] biases might have been baked in during tuning. But you
absolutely control how it gets implemented in your organization, what data it has access to, and how it ﬁts into your workﬂows.
Now that we understand how these models learn and develop, let's look at what happens when we actually put them to work.
The real world use cases, the opportunities they create, and the risks that we need to manage.

4

Video 4 - AI in action: use cases, opportunities, and risks

[00:00:00]  AI  promises  to  fundamentally  change  the  way  we  work,  but let's look beyond the hype for a moment and get a
deeper  understanding  of  what  it  can and can't do, and how we can leverage its strengths and avoid some common pitfalls.
We're going to continue focusing on Generative AI as this is the broadly applicable AI tool available to most. Part of what makes
Gen  AI  tools  like  ChatGPT,  Gemini,  Dall-E,  and  Claude,  so  exciting  is  the  breadth  of  potential  applications.  These tools are
generalists  and in many ways, their use is limited only by your imagination. Let's start by grouping some of the opportunities
that we have with Generative AI. We'll start with automation. The push for automation has been one of the key drivers and use
of the technology for all of history. Generative AI presents a signiﬁcant leap forward in this area. Because of its ability to process
a much wider range of inputs in natural language, we're able to automate time consuming tasks that have historically been very
difﬁcult  to  standardize.  Think  of  AI  automatically  categorizing  and  [00:01:00]  processing  thousands  of  support  tickets,
summarizing  long  documents,  processing  expense  reports.  The  most  obvious  usage  of  Generative  AI  is  to  have  it  generate
content.  Whether  it's  text  or  image  or  video  or  audio,  we've  all  become very familiar, very quickly with this new ability for
software  to  create  compelling  content.  And  this  ability  comes  with opportunity as well as challenges. The right application,
Generative AI, can enhance the customer experience, offer faster and more relevant responses, or deliver a service that feels
like it knows you or your customer. The wrong application often results in just the opposite, and we'll talk about the difference
shortly. This combination of automation and content generation is powerful. When you add Agentic abilities, allowing AI tools to
take actions like sending emails, creative ﬁles, and commenting on posts, we really start to see the potential unfold. Workﬂows
and tools have proliferated around these agents. From straightforward, personal assistant type use cases to a series of agents
orchestrated to run entire business units. What parts of your day-to-day involve translating an ask [00:02:00] into an output? Like
an email or a spreadsheet or a calendar invite. These are likely candidates for introducing Gen AI tools and AI Agents to improve
outcomes and productivity. It's important to keep our eyes open to the limitations and dangers inherent in this new technology
as well.

Leveraging AI requires vigilance, and we need to be aware of the core risks and pitfalls in addition to these opportunities. We'll
talk  about some of the primary areas to watch out for: hallucinations, low-quality and generic outputs, and data and privacy
issues.  Remember,  Gen AI is not a replacement for or even on par with human intelligence. While it's an incredibly powerful
thinking  partner,  it  is  not  capable  of  original  thought,  and  its  intentions  are  to create a response most likely to answer the
prompt that is given. It doesn't have a frame of reference that is anything remotely human, and it doesn't really have what we
refer  to  as  common  sense.  The quality of the output is highly-dependent on the prompts that are given, and the answer in
content generated should be reviewed and taken with a grain of salt. More practically, don't just copy and paste the [00:03:00]
responses. We've all seen examples of the issues that can arise from this, and they're often humorous, but they can cause huge

5

issues for individuals and for companies that're quoting incorrect information, relying on potentially hallucinated sources, and
just  producing  generic,  non-engaging  AI  slop.  So  what  is  hallucination?  An  AI  hallucination  is  very  different  from  a  human
hallucination. In Generative AI, a hallucination is when the model generates an output that is factually incorrect or completely
fabricated. For example, an AI might conﬁdently cite a non-existent legal case or invent a plausible sounding, but completely
false  company  policy.  It  always  makes  the  output  sound  convincing,  which  is  where  the  biggest  risk  lies  and  why  it's  so
important that you as the user check and verify. There are two important strategies for dealing with hallucinations. One, use the
right  tool for the job. Between the marketing from the big AI companies and the conﬁdence with which chatbots respond to
every query, it is very easy to think that Generative AI is the answer to every problem. But don't fall into this trap. [00:04:00] If
you're doing math, use a calculator or a spreadsheet. Always check numbers in particular produced by Generative AI. These are
content producing machines and they should be used as such. Check any quoted sources and do your own research. Google is
still the best starting point for ﬁnding articles written by experts, and as a bonus, you'll get the information in the context it was
meant for and the ability to do your own digging in your own research. Read and reason through all Gen AI outputs. Don't copy
them verbatim. Thinking of Gen AI tools as thinking partners rather than copywriters is key here. They can be used to reﬁne and
enhance,  and  they're  capable  of  producing  simple  instructions  based  on  known  documentation.  But  when  you  use Gen AI
outputs  without  modiﬁcation  or  review,  you  risk  spreading  misinformation,  alienating  your audience, and potentially causing
reputational damage for yourself and your organization. Never trust an AI output that includes facts, ﬁgures, dates, or citations
without  independent  veriﬁcation.  By  now,  we've  all interacted with bad uses of Generative [00:05:00] AI, whether it's generic
ChatGPT-sounding  copy,  hallucinations,  fake  imagery,  and  video,  or  spammy  social  media  comments.  Avoid  adding  to  the
problem and get the most of these powerful tools by using them intelligently and thoughtfully.

Now let's touch on data privacy and security. The good news is that all the standard data security practices that you all already
have learned are still applicable. Company and customer data should not ever be put into software tools or communications
that  are  not  company  controlled  and  approved.  AI  is  no  exception.  Don't  put  company  data  into  your  personal  ChatGPT
conversation.  Ensure  that  you're  following  your organization's security practices when using company or customer data in all
internally approved tools, especially in AI. Remember what we covered in the last video. AI models thrive on massive amounts
of  data and without strong protections, any and all data can be used for training and tuning. Unless you are certain that the
interaction you are having with any given Gen AI tool or LLM is protected under contract, assume that your conversation and
any  data  referenced  in it [00:06:00] are available to and going to be used by the owner of that tool. If you're ever in doubt,
double check with the organization's data and security compliance teams beforehand. With that understanding of the uses and
risks of Generative AI tools, we are ready to shift our thinking and start to take a more strategic approach. In our last video of
this series, we will look at the difference between a "Data-ﬁrst" and an "AI-ﬁrst" mindset, and think about how we can start to
design features and agents to better serve our customers and deliver better outcomes across our teams.

6

Video 5 - Mindset shift: AI-ﬁrst vs data-ﬁrst

[00:00:00] When we are thinking about applications of Generative and Agentic AI in the software that we build, it is important to
ﬁrst  consider  the  applicability  of  AI  to  the  problem.  It's  exciting  to  ask  a  natural  language  question  of a bot that would've
previously required an hour of messing with a spreadsheet or pulling a report to understand, but is that the right tool for the
job? There are many ways to automate reporting and data manipulation. A model specializing in Natural Language Processing
probably isn't gonna be the best choice. But efﬁciency isn't even the ﬁrst consideration that we need to take into account here.
Even more important is the underlying data. Generative and Agentic AI, by their very nature, obscure their inner workings. It is
much  more  difﬁcult  to troubleshoot a hallucination than it is a traditional software bug or an incorrect calculation. The best
way  to  navigate  this  issue  is  by taking a data-ﬁrst approach to the design and implementation of AI systems. So what is this
mindset?  A  data-ﬁrst  mindset  focuses  on  starting  with  clean,  trusted data as the [00:01:00] primary strategic asset, and then
applying  that  data  to artiﬁcial intelligence to make it accurate, actionable, and accountable. This approach ensures trust and
reliability, prioritizing data governance and quality above all else. Without this foundation, any AI project, no matter how clever,
is  doomed  to  fail.  If  the  underlying  data  that  you're  operating  on  is  not  correct,  then  your  AI  systems  will  learn  incorrect
information and they'll conﬁdently try to respond and solve problems a hundred percent sure that what they know is correct.
Remember,  these  systems  don't  possess  common sense, and even though they come across as very human-like, they don't
have  any  of  the  natural  skepticism  and  history  of  critical  thinking  that  humans  do.  And  so  it  falls to us, the designers and
implementers of AI systems, to apply our common sense along with our knowledge of the underlying data set and the context
in  which  it  was  gathered  and  prepared  and  the  goals  for  the  system.  Successfully  adopting  AI is about establishing a clear
process  available  to  the  AI  system.  If  it  is  a  [00:02:00]  large  data  set  in  a  database  or  a CSV ﬁle, then we should consider
supplying  tools  to  our  agent  to  manipulate  that  data  using  non-generative  AI  methods.  For  example,  ﬁnding  the  sum of a
column or pivoting the table. Now we're ready to take the third step and to start working on the agent itself. Crafting prompts
and enabling agentic tool calls to gather context from our data and make decisions or provide user responses. Don't make the
mistake of leaping straight to that last step. We've spoken about a data-ﬁrst mindset, and once we've adopted that mindset, we
can start to take on a much more useful AI-ﬁrst mindset.

AI-ﬁrst does not mean that we blindly rush to apply AI as a solution to every problem. Rather, it means that we consider the
problems  that  we  are  trying  to  solve  for  our  customers  and  our  company  and  ask,  "is  this something that we could more
effectively or efﬁciently use an agent to support or deliver?" The answer to that question will not always be yes, but when the
answer is yes, the next question must be, "does our dataset support this use case?" Successfully adopting [00:03:00] AI is about

7

establishing  a  continuous  loop.  Data-ﬁrst  provides  the  clean,  ethical  foundation,  and  AI-ﬁrst  provides  the  future  vision  for
transformation. If you take the time to apply these mindsets and thought processes to your work, you'll be creating safer, more
effective AI solutions. Most importantly, these solutions will be properly aligned with the needs of your end user and capable of
delivering truly satisfying Agentic AI experiences they'll be excited to come back to. We'll dive deeper into how impact.com is
working in this rapidly evolving world of Agentic AI, as well as Agentic Commerce in our next course.

Video 6 - Recap

[00:00:00] As a recap, in this course you learned how to deﬁne artiﬁcial intelligence and differentiate key concepts. Explain the
basic process of how AI models learn from data, recognize common applications, opportunities and risks associated with AI, and
adopt an "AI-ﬁrst" and "Data-ﬁrst" approach. AI is a technology that has broad applicability, and it gives us the potential to create
unique solutions to longstanding technology challenges across every industry. This broad applicability has led to a lot of hype.
At  the  end  of  this  course,  I hope you have taken away a more fundamental understanding of the underlying principles that
power  this  new  tool  and  can  approach  generative  and  agentic  AI,  in particular with practicality and pragmatism. I'm looking
forward to seeing what you build. Thanks for joining us here at PXA. Join us again soon for a deeper dive into impact.com's AI
product capabilities and the shift towards Agentic Commerce as the industry rapidly [00:01:00] expands and we lean into the
different capabilities available to us.

8
