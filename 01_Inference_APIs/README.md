# Module 01: Inference APIs

[Workshop home](../README.md) · [Setup](../docs/00_prework.md) · [Endpoint reference](../docs/inference.md)

**25 minutes.** Your first request, and the rest of what you need to call this
endpoint properly.

| Notebook | Covers |
|---|---|
| [01_inference_apis.ipynb](01_inference_apis.ipynb) | Raw HTTP, the SDK, chat, streaming, sampling parameters, model selection, errors |

## Before you start

An inference key in `.env`, and `python scripts/check_setup.py` passing. See
[get an API key](../docs/get-an-api-key.md) if you do not have one yet.

## What you will do

Send one request with `requests` first, so you see the status code, the rate limit
headers, and the JSON shape before any SDK hides them. Then make the same call
through the OpenAI client with `base_url` pointed at Akamai, which is the two line
change that moves existing code onto this platform.

After that: streaming with a time to first token measurement, the four parameters
that control output, what `/v1/models` does and does not tell you, and a tour of the
errors you are most likely to cause.

## What you should take away

- `finish_reason` tells you whether a response is usable. Check it before you use one.
- `/v1/models` returns ids and nothing else. No context windows, no capabilities.
- A base URL missing its `/v1` suffix returns `404` on everything and looks like a
  bad model name.
- Use `qwen3-8b` for anything involving tools.

## Next

[Module 02: Embeddings and RAG](../02_Embeddings_and_RAG/)
