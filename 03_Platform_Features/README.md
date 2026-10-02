# Module 03: Platform Features

[Workshop home](../README.md) · [Setup](../docs/00_prework.md) · [Endpoint reference](../docs/inference.md)

**25 minutes.** Three capabilities that sit on top of plain chat.

| Notebook | Covers |
|---|---|
| [03_vision_reasoning_json.ipynb](03_vision_reasoning_json.ipynb) | Image input, reasoning mode, and schema-constrained JSON |

## Before you start

[Module 01](../01_Inference_APIs/), or a working `.env`. This module is independent
of 02 and 04, so you can run it whenever.

Short on time? This is the module to skip. [Module 04](../04_Agents/) recaps the one
thing it borrows from here.

## What you will do

**Image input** with `gemma-4-26b-a4b-it`, the only model here that accepts it.
Images go in as base64 data URLs. You will also watch a remote URL fail with `422`,
because the endpoint does not fetch images from the internet.

**Reasoning mode** on `qwen3-8b`, where the model works through a problem before
answering. The notebook uses a question with a trap in it, so you can see the direct
answer get it wrong and the reasoning answer get it right.

**Typed output** with `response_format` and a Pydantic schema. The notebook shows a
call that fails first, because the failure is the most useful thing in the module.

## What you should take away

- Reasoning is written before the answer and spends the same token budget. Too small
  a `max_tokens` gives you reasoning and **empty content**.
- Reasoning arrives in `message.reasoning`, separate from `message.content`.
- A JSON schema does not constrain whitespace, so an uncertain model can emit
  whitespace until it hits `max_tokens`. Tell it to reply with compact JSON and the
  problem goes away.
- Base64 for images. Resize before encoding, because base64 adds about a third.

## Next

[Module 04: Agents](../04_Agents/)
