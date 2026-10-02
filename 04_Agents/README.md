# Module 04: Agents

[Workshop home](../README.md) · [Setup](../docs/00_prework.md) · [Endpoint reference](../docs/inference.md)

**45 minutes.** The model stops answering directly and starts asking your code to do
things.

| Notebook | Covers | Time |
|---|---|---|
| [1_tool_calling.ipynb](1_tool_calling.ipynb) | Describing a tool, the call and response exchange, the loop, `tool_choice`, parallel calls, failing tools | 20 min |
| [2_build_the_agent.ipynb](2_build_the_agent.ipynb) | Document search as a tool, a trace you can debug, typed answers, the refusal path | 25 min |

Run them in order.

## Before you start

[Module 01](../01_Inference_APIs/) for the basics. Notebook 2 uses the retrieval
index from [module 02](../02_Embeddings_and_RAG/), imported from
`workshop_utils/retrieval.py`, so you do not have to have run that module. Running it
first will make notebook 2 make more sense.

## No framework

The loop is about fifteen lines and you write it yourself. A framework would hide
exactly the part worth understanding, and a loop you wrote is a loop you can debug.
Everything here is plain `chat.completions.create`.

## Why qwen3-8b and not the biggest model

Every exercise uses `qwen3-8b`. `gemma-4-26b-a4b-it` is larger and worse at this. In
testing across five agent workloads, ten runs each:

| Model | tool_loop | handoff | websearch | long_session |
|---|---|---|---|---|
| gemma-4-26b-a4b-it | 0/10 | 0/10 | 0/10 | 10/10 |
| qwen3-4b | 10/10 | 10/10 | 10/10 | 10/10 |
| qwen3-8b | 10/10 | 10/10 | 10/10 | 10/10 |

Gemma calls a tool, gets a valid result, fails to read a value out of it, and calls
the same tool again with the same arguments until it hits the turn cap. It passes the
pure conversation workload, which rules out configuration, so this is a model
capability limit. If you swap the model and your agent breaks, this is why.

## What you should take away

- Branch on `msg.tool_calls`, not on `finish_reason`. A named `tool_choice` returns
  `finish_reason: "stop"` while still carrying a call.
- `tool_choice: "none"` is unreliable here. It can leak the model's internal
  `<tool_call>` syntax into `content`. Omit `tools` instead.
- Always cap the turns.
- **Never set `response_format` on a request where the model might still need to call
  a tool.** The schema makes a tool call impossible, so the model either stalls or
  invents the answer. Notebook 2 demonstrates it inventing a number and citing a file
  that does not exist.
- Arguments arrive as a JSON **string** chosen by the model. Parse and validate them
  like any untrusted input.

## Next

You are done with the workshop. Optionally, [deploy](../deploy/) puts this agent
behind an HTTP endpoint on a Linode.
