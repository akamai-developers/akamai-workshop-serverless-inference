# Workshop proposal: Getting started with Akamai Cloud Inference

Internal review document. Delete before the repo is published.

Repo: `akamai-developers/akamai-workshop-serverless-inference`
Status: built. All six notebooks execute against the live endpoint as of 2 October 2026
Style reference: [akamai-workshop-hackmidwest](https://github.com/akamai-developers/akamai-workshop-hackmidwest)
Structure reference: [amazon-bedrock-workshop](https://github.com/aws-samples/amazon-bedrock-workshop)

## What this is

A hands-on workshop that takes a developer from an API key to a working agent on
Akamai Cloud Inference. Four modules, six notebooks, all run against the live
endpoint. No GPU, no Kubernetes, no Docker.

The workshop answers four questions in order. How do I call a model. How do I make it
answer from my own documents. What else does this platform do. How do I put those
pieces together into something that acts on its own.

Deployment is a folder in the repo rather than a module in the workshop. The
reasoning is in [Why deployment is not a module](#why-deployment-is-not-a-module).

## Who it is for

A developer who writes Python and has used an HTTP API, and who has not used this
platform. No machine learning background needed.

Participants create their own Akamai Cloud account and their own inference key. The
README carries the signup link and the credit offer, following the hackmidwest
pattern. The key is the only thing the notebooks need. Nothing in the guided workshop
creates a billable resource.

## What they leave with

- A working local environment pointed at the inference endpoint
- A retrieval index over their own documents, with citations and a refusal path
- A tool-calling loop they wrote themselves, so they can debug it
- An agent that chooses when to search its documents and returns a typed answer
- A reference page for the endpoint's real limits
- A deploy folder they can run when they want it

## Three paths

| Path | Modules | Time | Use it for |
|---|---|---|---|
| Lightning | 01, and notebook 1 of 02 | 35 minutes | A conference session or a lunch and learn |
| Guided | 01, 02, 04 | 1 hour 40 minutes | A half-day workshop, with 03 as homework |
| Full | 01 through 04 | 2 hours 5 minutes | Self-serve |

Modules 02, 03, and 04 are independent once 01 is done. Each opens with a short recap
cell, so skipping 03 does not break the agent in 04. The only hard order is inside
02 and 04, where the second notebook builds on the first.

## Module map

| Module | Notebook | Teaches | Model | Time |
|---|---|---|---|---|
| 01_Inference_APIs | `01_inference_apis.ipynb` | Models endpoint, raw HTTP, the SDK, chat, streaming, sampling, errors | qwen3-8b | 25 min |
| 02_Embeddings_and_RAG | `1_embeddings_basics.ipynb` | Embeddings, cosine similarity, chunking, the token budget | qwen3-embedding-4b | 10 min |
| 02_Embeddings_and_RAG | `2_build_a_rag_index.ipynb` | Chunk, embed, retrieve, ground the answer, cite the source, refuse when there is none | qwen3-embedding-4b, qwen3-8b | 20 min |
| 03_Platform_Features | `03_vision_reasoning_json.ipynb` | Image input, reasoning mode, structured output, context windows | gemma-4-26b-a4b-it, qwen3-8b | 25 min |
| 04_Agents | `1_tool_calling.ipynb` | The tool-call loop by hand, tool_choice, parallel calls | qwen3-8b | 20 min |
| 04_Agents | `2_build_the_agent.ipynb` | Retrieval as a tool, multi-step chains, typed final answers, the full trace | qwen3-8b | 25 min |

### 01_Inference_APIs

Opens with one `requests.post` so the participant sees the wire format, the status
code, and the rate-limit headers before any SDK hides them. Then the same call
through the OpenAI Python client with `base_url` overridden. Existing code moves to
this platform by changing two variables, and that is the first thing a participant
should see.

Covers `/v1/models` and what it does and does not report, a non-streaming completion
with `finish_reason` and `usage`, a streaming completion with time to first token,
and the sampling parameters.

The error section uses the platform's real error strings rather than invented ones.
The breakage sweep graded 60 malformed and oversized requests and scored the messages
6 or 7 out of 7 on nearly all of them, so there is good material to quote:

| Mistake | Response |
|---|---|
| Bad JSON body | `422` Invalid JSON in request body at character 78 |
| Model name typo | `404` The model 'definitely-not-a-real-model-9000' does not exist |
| No `model` field | `422` Missing required parameter: 'model'. |
| Empty `messages` | `400` Cannot apply chat template to an empty conversation. Provide at least one message. |
| `messages` not a list | `422` 'messages': input should be a valid list. |
| Prompt too long | `400` Estimated input token count (318947) exceeds the model limit (262143). |

One validation gap gets a footnote. A user message with `content: null` is accepted
with HTTP 200 on all three models instead of being rejected, so the participant
should validate message objects in their own code.

Ends with a model selection table, so the participant knows which of the four served
models to use for the rest of the workshop.

### 02_Embeddings_and_RAG

Two notebooks. The concepts separate cleanly, and the first one is short enough to
fit the lightning path.

`1_embeddings_basics.ipynb` embeds a batch of strings and shows that similar meaning
produces similar vectors. It establishes the two limits that govern every real index:
the per-request input count, and the 8,192 token budget that forces chunking.

`2_build_a_rag_index.ipynb` builds a retrieval pipeline with no vector database and
no framework. Chunk a document, embed the chunks, keep them in a NumPy array, embed
the question, rank by cosine similarity, put the top matches in the prompt, answer
with a citation. It includes a question the documents do not answer, so the
participant sees the refusal path.

The index is a function the participant can call. Module 04 turns that function into
a tool the model decides to call on its own.

### 03_Platform_Features

The platform capabilities that sit on top of chat.

Image input to `gemma-4-26b-a4b-it` as a base64 data URL. Reasoning mode on
`qwen3-8b` through `extra_body={"chat_template_kwargs": {"enable_thinking": True}}`,
with the token cost shown both ways. Structured output with `response_format` and a
JSON schema, validated with Pydantic. The context windows, which differ by a factor
of eight across the served models and are the first wall a participant hits.

This is the module to cut for a 90 minute session. The agent in 04 uses structured
output, so its second notebook recaps the JSON schema call in one cell for anyone who
skipped ahead.

### 04_Agents

Two notebooks. The first teaches the mechanism, the second builds something with it.

`1_tool_calling.ipynb` has the participant write the loop. Send tools, read
`tool_calls`, execute the function, append a `tool` message carrying the matching
`tool_call_id`, repeat until the model stops asking. Then `tool_choice` set to auto,
none, required, and a named function. Then two calls in one turn.

`2_build_the_agent.ipynb` is the capstone. It assembles the earlier modules into one
agent:

| Piece | Comes from |
|---|---|
| The loop | 04 notebook 1 |
| A `search_documents` tool wrapping the retrieval index | 02 notebook 2 |
| A typed final answer with a JSON schema | 03 |
| qwen3-8b | The model selection table in 01 |

The agent decides when to search instead of having documents pushed into every
prompt, which is the more useful mental model and costs fewer tokens.

It runs in two phases, and the ordering is the point:

1. The tool loop, with no `response_format`. The model searches, reads results, and
   decides when it has enough.
2. One final request that adds the `response_format` JSON schema, now that the tool
   results are in the conversation, to shape the typed answer.

Setting the schema during phase one deadlocks the request. The participant gets one
sentence on why and one diagnostic to recognise: output that stalls into whitespace
and ends at `finish_reason: length`. See [structured output works, the ordering is
what matters](#structured-output-works-the-ordering-is-what-matters).

No agent framework. The loop is hand-written throughout.

The notebook prints the full trace on every run: the question, the tool the model
chose, the arguments it passed, the tool result, the next call, and the typed answer.
That trace is the teaching artifact. A participant who can read it can debug an agent.

Two failure cases close the notebook. One question the documents cannot answer, so
the agent searches, comes back empty, and says so rather than inventing a citation.
Then a tool that returns an error, to show that the model will not recover on its own
and the retry belongs in the loop the participant just wrote.

### Why deployment is not a module

The Bedrock workshop this repo borrows its structure from is notebooks end to end.
There is no module that ships anything. hackmidwest had Linode and LKE labs, and that
was a hackathon where attendees needed a running project for judging. Even there the
deploy work sat under "Build your project" as an optional track.

An inline deploy module costs more than it teaches:

| Cost | Detail |
|---|---|
| Prerequisites | Linode CLI, a personal access token with 5 to 7 scopes, an SSH keypair, ssh-agent loaded, Docker |
| The blocker | Account activation. The hackmidwest prework says "allow extra time" and tells people to use the notebooks while waiting |
| Billing | A billable resource, a costs doc to read first, teardown discipline afterward |
| Wall clock | 30 minutes that is roughly 10 of teaching and 20 of provisioning and debugging SSH |
| Failure mode | An attendee with an unloaded ssh-agent learns nothing about inference |

So `deploy/` is an unnumbered folder. Numbered directories are the workshop,
unnumbered ones are extras, and the README links it as an optional next step.

```
deploy/
├── README.md          <- what it creates, what it costs, how to remove it
├── app/
│   ├── main.py        <- a small HTTP wrapper around the module 04 agent
│   ├── agent.py       <- the loop, lifted from the notebook
│   └── corpus/        <- the documents, embedded at startup
├── Dockerfile
└── cloud-init.yaml    <- provisions the Linode, installs Docker, starts the app
```

Three decisions inside that folder:

- **No database.** The app re-embeds its corpus at startup, which takes seconds at
  workshop scale. That removes Managed PostgreSQL, pgvector, a provisioning wait, a
  second billable resource, and a database lesson that was scope creep.
- **Docker on the Linode, not the laptop.** cloud-init installs it. One Dockerfile,
  no Compose, because there is one service. Anyone who does have Docker can run the
  app locally first without touching the cloud.
- **A real lab, not a stub.** The README states what it creates and what it costs
  before it creates anything, and ends with teardown. Someone should be able to
  follow it alone.

## Where the content comes from

The content is grounded in the evaluation suite in `inference-performance-testing`.
That suite ran 173 compatibility probes across the four served models, 93 passing and
10 failing, plus load, soak, multi-turn, breakage, and agent runs, with an OpenRouter
control for comparison. Every capability the workshop teaches was verified against
the live endpoint. Every warning it gives is a recorded finding with a reproduction
command.

Five decisions came directly out of that data.

| Decision | Reason from the test data |
|---|---|
| Teach image input as base64, not a remote URL | A remote `image_url` returns HTTP 422 because the fetch is blocked. OpenRouter fails the same probe, so this is the model or the serving stack rather than Akamai. Either way the participant needs base64. |
| Skip the embeddings `dimensions` parameter | Rejected with HTTP 400 on `qwen3-embedding-4b`, native dimension 2560. The error message explains that the model has no Matryoshka representation. Worth showing as an example of a clear error. |
| Use `qwen3-8b` for every tool-calling exercise | Gemma fails `tool_choice` none, required, and named, and fails the tool result round trip by returning an empty message. Qwen3-8b passes all of them. A workshop that reached for the biggest model would fail in front of the room. |
| Put retry and validation logic in application code rather than the prompt | Sound practice regardless. Note the August finding behind this did **not** reproduce: see [what changed since August](#what-changed-since-august). |
| Write the agent loop by hand, with no agent framework | Team decision, and the loop is the concept being taught. Worth recording that the OpenAI Agents SDK does work on qwen3-8b for four of five workloads, so this is a teaching choice rather than a workaround. |
| Attach `response_format` only after the tool results are in the conversation | Setting it while the model still needs to call a tool deadlocks the request. Measured directly on 2 October 2026. Details below. |

### Why qwen3-8b and not gemma

Five agent workloads, ten runs each, through the OpenAI Agents SDK. From
`reports/agents.md`:

| Model | tool_loop | handoff | websearch | long_session | structured_output |
|---|---|---|---|---|---|
| gemma-4-26b-a4b-it | 0/10 | 0/10 | 0/10 | 10/10 | 0/10 |
| qwen3-4b | 10/10 | 10/10 | 10/10 | 10/10 | 0/10 |
| qwen3-8b | 10/10 | 10/10 | 10/10 | 10/10 | 0/10 |

Gemma calls a tool, gets a valid result, fails to read a value out of it, and calls
the same tool again with the same arguments until it hits the turn cap. The tool_loop
run shows ten identical calls to `look_up_order` and an empty final answer. It passes
`long_session` 10 out of 10, which rules out configuration and connectivity, so this
is a model capability limit.

qwen3-8b passes everything except `structured_output`, and it is faster than qwen3-4b
on the workloads both pass: 2,068 ms against 3,477 ms at p50 on tool_loop. It is the
model for every tool exercise in the workshop. Gemma appears only in module 03, for
image input, where no tools are involved.

### Structured output works. The ordering is what matters.

Structured output on this platform is solid. `response_format` with a JSON schema
returns correct, parseable JSON on qwen3-8b, with or without `strict: true`, with
thinking on or off, and with tools attached. The hackmidwest notebooks use the same
mechanism and work.

The agent workload failures were not a structured output problem. Five single
requests on 2 October 2026 isolated the real cause:

| Test | Setup | Result |
|---|---|---|
| A | Tools attached, `response_format` set, required data only available through the tool | Deadlock. `finish_reason: length` |
| B | Tools attached, no `response_format` | Works. `finish_reason: tool_calls` |
| C | Tool result in the conversation, then a toolless `response_format` request | Works. Correct values |
| D | Tool result in the conversation, `response_format` and tools both attached | Works. Correct values |

In test A the model returned `{"order_id": "ORD-4417"` followed by roughly 1,500
characters of whitespace until it hit the token cap. Guided decoding constrains the
output to the schema, so the model cannot emit a tool call. It also cannot fill
`customer_name` or `monthly_request_limit`, because those values live behind the tool
it is not allowed to call. So it stalls and spends the whole output budget on
whitespace.

That explains both agent failures. Gemma filled the forced schema with invented
values, including a request limit 5x below the real one. The `Invalid JSON when
parsing model output` error on qwen3-8b is this truncated whitespace JSON.

A control run the same day shows this is not specific to Akamai:

| Request | Akamai qwen3-8b | OpenRouter qwen/qwen3-8b, served by Alibaba |
|---|---|---|
| `strict: true`, `tool_choice` default | Deadlock, 300 tokens burned, `length` | No deadlock, but invented a customer name and limit and omitted a required field |
| No `strict`, `tool_choice` default | Identical deadlock | Called the tool correctly |
| `strict: true`, `tool_choice: "required"` | Called the tool, 27 tokens, clean | not run |

Both stacks mishandle tools combined with constrained decoding, and neither does what
the OpenAI API does, which is leave the tool call reachable while a schema is set.
Two differences are worth noting. Akamai ignores `strict` where OpenRouter honours
it, and Akamai's failure bills the full output budget while OpenRouter's terminates
after 154 tokens. On a request with `max_tokens: 4096` that is 4,096 output tokens
for whitespace.

**The rule the workshop teaches:** set `response_format` only once the tool results
are already in the conversation. Test D shows the tools can stay attached on that
final request. What breaks is asking for a schema while the model still has work to
do. `tool_choice: "required"` is a second way out, and the notebook mentions it in
one line.

So the capstone runs the tool loop with no `response_format`, then adds it on the
formatting request at the end. This gets one short note in the notebook, not a
section. It is a sharp edge worth naming, not a headline, and the workshop should not
open by cataloguing platform defects.

Separately from the workshop, this is worth a low or medium severity finding in
`inference-performance-testing`. The narrow claim is that a request which cannot
succeed should fail fast rather than billing the full output budget, and the control
above belongs in it.

Four things the workshop can state as verified:

- Streaming is compliant across seven probes, including the usage block and agreement
  between streamed and non-streamed output.
- `response_format` with a JSON schema passes on all three chat models, and on
  qwen3-8b it holds with `strict: true`, with thinking either way, and with tools
  attached once the tool results are in the conversation.
- The `enable_thinking` toggle reaches the chat template on Akamai. The OpenRouter
  control ignores it.
- Error messages are specific and quote the relevant numbers. The breakage sweep
  passed 54 of 60 probes, and the two failures are listed below.

Two limits the workshop will state plainly, because finding them yourself costs an
afternoon:

- A prompt sized to the advertised context limit was rejected on all three chat
  models. The materials tell participants to leave headroom instead of treating the
  advertised number as usable.
- Repeating an identical long prompt produced no prefix cache speedup. The materials
  do not present prompt caching as an optimization on this platform.
- Setting `response_format` while the model still needs to call a tool deadlocks the
  request, which spends the full output budget on whitespace and ends at
  `finish_reason: length`. The materials teach the ordering that avoids it.

### What changed since August

Building the notebooks meant running every claim against the live endpoint, which
turned up five differences from the August data. All are already corrected in the
materials.

| Claim from August | What the endpoint does now |
|---|---|
| `/v1/models` reports `max_model_len` | It no longer does. The response carries only `id`, `object`, `created`, and `owned_by`. Module 01 now teaches finding the limit from the error message instead |
| gemma's context is 262,144 | The enforced limit is 262,143. qwen3-8b and qwen3-4b confirmed at 32,768 |
| Models do not recover from a tool error | qwen3-8b recovers cleanly, with a bare error and with an informative one. Module 04 teaches what to put in an error rather than claiming the model cannot cope |
| `tool_choice: "none"` passes | It leaks the model's internal `<tool_call>` syntax into `content` instead of answering. Module 04 says to omit `tools` rather than use `none` |
| The `response_format` plus tools failure is a whitespace stall | It is either a stall or a clean fabrication, depending on the schema. The fabrication is worse and is what module 04 demonstrates |

Two new findings came out of the build, neither of which was in the August data.

**Structured output can stall with no tools involved.** A JSON schema says nothing
about whitespace, because JSON permits it anywhere, so "emit another space" is always
a legal next token. An uncertain model takes that move repeatedly until `max_tokens`
runs out. Reproduced three times out of three on a three-field schema, burning the
full 300 token budget each time.

The fix is one line in the prompt: tell the model to reply with compact JSON on a
single line. That took the same request from 300 wasted tokens to 53 useful ones,
three times out of three. Module 03 shows the failure and then the fix, because this
will happen to anyone using `response_format` seriously.

**The tools plus schema failure can be silent.** Asked a question whose answer was
only available through its search tool, with `response_format` set, the model
returned `answer: "768 dimensions"` (the real answer is 2,560), `answer_found: true`,
and cited `https://developer.akamai.com/.../embeddings.html`, a URL that does not
exist. `finish_reason` was `stop`. Nothing in the response indicates a problem. The
notebook catches it by checking the cited sources against the real file list.

## Repo layout

```
akamai-workshop-serverless-inference/
├── README.md                      <- overview and routing table, kept short
├── PROPOSAL.md                    <- this file, deleted before publishing
├── requirements.txt
├── .env.example
├── docs/
│   ├── get-an-api-key.md          <- account signup and creating an inference key
│   ├── 00_prework.md              <- laptop setup, venv, env vars, verification
│   ├── inference.md               <- endpoint reference: models, limits, shapes
│   └── troubleshooting.md
├── 01_Inference_APIs/
│   ├── README.md
│   └── 01_inference_apis.ipynb
├── 02_Embeddings_and_RAG/
│   ├── README.md
│   ├── 1_embeddings_basics.ipynb
│   ├── 2_build_a_rag_index.ipynb
│   └── assets/sample-docs/
├── 03_Platform_Features/
│   ├── README.md
│   ├── 03_vision_reasoning_json.ipynb
│   └── assets/sample-image.png
├── 04_Agents/
│   ├── README.md
│   ├── 1_tool_calling.ipynb
│   └── 2_build_the_agent.ipynb
└── deploy/
    ├── README.md
    ├── app/
    ├── Dockerfile
    └── cloud-init.yaml
```

Numbered module directories with a README each, from the Bedrock workshop. The
`docs/` folder, the short routing README, and the writing voice, from the hackmidwest
workshop. `costs.md` moved into `deploy/README.md`, since deployment is now the only
thing that spends money.

Every notebook uses the same internal shape, following the hackmidwest pattern: a
header with the time estimate and breadcrumb links, numbered steps, a validation cell
that asserts the module worked, a cleanup cell when it created anything, and a
"continue with" footer.

## Prerequisites

| For | Needs |
|---|---|
| The whole workshop | Python 3.11 or newer, an Akamai Cloud account, an inference API key |
| The deploy folder, optional | The Linode CLI, an SSH key |

Two environment variables carry the whole workshop:

```ini
AKAMAI_BASE_URL=https://api.akamai-inference.com/v1
AKAMAI_API_KEY=paste_your_key_here
```

Nothing else. No database URL, no cloud token, no Docker.

### Getting an API key

`docs/get-an-api-key.md` is the page a participant hits before anything else works,
so it gets its own doc instead of a line buried in the setup steps. It covers signup
with the credit offer, account activation, where the inference service lives in Cloud
Manager, creating a key, and scoping it. The README links it as step 1 and
`00_prework.md` points at it rather than repeating it.

Two things to fill in before this ships:

- The Cloud Manager click path for creating an inference key, with screenshots. I
  have not verified the current path, so the doc goes in with those steps marked as
  placeholders.
- A signup link for this workshop. The hackmidwest README used
  `promo=akm-dev-git-300-72326-P153`, which belongs to that event. This workshop
  needs its own promo link, or a plain signup link with no credit claim.

## Draft README overview

The README stays close to the hackmidwest length. The overview is the addition.

> # Getting started with Akamai Cloud Inference
>
> Call a model, build retrieval over your own documents, and put both into an agent.
> Four modules of runnable notebooks, about two hours end to end, or 35 minutes for
> the lightning path. You need an Akamai Cloud account and an inference key. You do
> not need a GPU, and the workshop creates no cloud resources.
>
> Akamai Cloud Inference serves open models behind an OpenAI-compatible API. If you
> have written code against the OpenAI SDK, change the base URL and the key and your
> code runs. This workshop starts there, then covers the rest of the platform:
> embeddings, image input, reasoning mode, structured output, and tool calling.
>
> ## Start here
>
> > ### Free credit for Akamai Cloud
> > Sign up here: **[signup link to be confirmed]**
>
> 1. **[Get an API key](docs/get-an-api-key.md)** for Akamai Cloud Inference.
> 2. **[Set up your laptop](docs/00_prework.md)** before the session.
> 3. **[Call your first model](01_Inference_APIs/)** and see the request on the wire.
> 4. **[Build retrieval](02_Embeddings_and_RAG/)** over your own documents.
>
> ## Find what you need
>
> | Topic | Module |
> |---|---|
> | Chat, streaming, sampling, errors | [01 Inference APIs](01_Inference_APIs/) |
> | Embeddings and retrieval | [02 Embeddings and RAG](02_Embeddings_and_RAG/) |
> | Image input, reasoning, JSON output | [03 Platform Features](03_Platform_Features/) |
> | Tool calling and agents | [04 Agents](04_Agents/) |
> | Running the agent on Akamai Cloud | [deploy](deploy/) |
>
> [Get an API key](docs/get-an-api-key.md) · [Endpoint reference](docs/inference.md) · [Troubleshooting](docs/troubleshooting.md)

## Decisions made

| Question | Choice |
|---|---|
| Product name | "Akamai Cloud Inference" throughout, including in the repo whose name says `serverless-inference` |
| Key distribution | Participants sign up for Akamai Cloud and create their own key. The README carries the signup link and the credit offer |
| API key instructions | Their own doc at `docs/get-an-api-key.md`, linked as step 1 of the README |
| Test data | The workshop ships on the August measurements. No re-run before launch |
| Deployment | A single Linode, in an unnumbered `deploy/` folder, not a module |
| Docker | Not a workshop prerequisite. Installed on the Linode by cloud-init |
| Vector storage | In memory, re-embedded at startup. No Managed PostgreSQL, no pgvector |
| Ending | A capstone agent in `04_Agents/2_build_the_agent.ipynb` |
| Agent framework | None. The loop is hand-written, so no `openai-agents` dependency |
| Structured output | Works. `response_format` goes on the final request, after the tool results are in the conversation |

## Still open

1. **The API key instructions.** `docs/get-an-api-key.md` has a marked `TODO` where
   the Cloud Manager click path or the CLI command goes. I did not verify either, so
   nothing was invented. This is the one thing that blocks an attendee completely.
2. **The deploy folder is partly unverified.** `app/agent.py` and `app/main.py` were
   both run and tested, including the HTTP endpoints. The `Dockerfile`,
   `cloud-init.yaml`, and the `linode-cli` commands in `deploy/README.md` were not,
   because Docker was unavailable on the machine that built this. Run one deployment
   before pointing anyone at that folder.
3. **Funnel goals.** Moving deployment out of the numbered modules means resource
   creation is now opt-in. The signup callout keeps account creation in the funnel.
   If the team counts resources created, this is the tradeoff to argue about.
4. **Two findings worth filing** in `inference-performance-testing`, both new and
   both with short reproductions: the whitespace stall in plain structured output,
   and the silent fabrication when `response_format` is set alongside tools. The
   first has a one-line mitigation and is the more useful of the two to report.
