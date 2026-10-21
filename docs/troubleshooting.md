# Troubleshooting

[Workshop home](../README.md) · [Setup](00_prework.md) · [Endpoint reference](inference.md)

Find your symptom. If none of these match, run `python scripts/check_setup.py`, which
tests each piece separately and names the one that failed.

## Setup

**`ModuleNotFoundError: No module named 'openai'` in a notebook**

Jupyter is running a different Python than the one you installed into. Pick the
kernel for this project's `.venv`. In Jupyter, use **Kernel > Change Kernel**. To
confirm which Python a notebook is using:

```python
import sys; print(sys.executable)
```

That path should be inside the workshop directory.

**`python3 -m venv` fails on Ubuntu**

```bash
sudo apt install -y python3-venv
```

**`KeyError: 'AKAMAI_API_KEY'`**

Either `.env` does not exist, or the notebook was started from a different directory.
Run `cp .env.example .env`, fill it in, and start Jupyter from the workshop
directory.

## Authentication and connection

**`401`**

The key is wrong, expired, or has whitespace around it. Open `.env` and check for a
trailing space or a line break in the middle of the key. Confirm the key still exists
in Cloud Manager. See [get an API key](get-an-api-key.md).

**`404` on every request**

The base URL is missing its `/v1` suffix. It must be:

```ini
AKAMAI_BASE_URL=https://api.akamai-inference.com/v1
```

This looks like a bad model name and is not.

**`404 The model 'x' does not exist`**

A real model name typo. List what is actually served:

```bash
curl -s $AKAMAI_BASE_URL/models -H "Authorization: Bearer $AKAMAI_API_KEY"
```

**Connection timeout**

Check the endpoint is reachable and that you are not behind a proxy that blocks it:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" $AKAMAI_BASE_URL/models \
  -H "Authorization: Bearer $AKAMAI_API_KEY"
```

## Requests

**`429`**

You are rate limited. Wait, then retry with a bounded number of attempts. The
response headers carry your limits. The notebooks in module 01 print them.

**`400 Estimated input token count (N) exceeds the model limit (M)`**

Your prompt is too long. Note that `N` is the endpoint's own estimate and will not
match your local tokenizer, so a prompt you measured as fitting can still be
rejected. Shorten the input or move to `gemma-4-26b-a4b-it`, which enforces a 262,143
token limit.

**The answer stops mid-sentence**

`finish_reason` is `length`. Raise `max_tokens`, or shorten the input. Always check
`finish_reason` before you use a response.

**`finish_reason: length` and the content is mostly whitespace**

You set `response_format` on a request where the model still needs to call a tool.
The schema prevents it from emitting a tool call, so it stalls and burns the output
budget. Remove `response_format` from the tool-calling turns and add it only on the
final request, after the tool results are in the conversation. See
[structured output](inference.md#structured-output).

**`json.loads` fails on a structured response**

Check `finish_reason` first. A truncated response is still invalid JSON. If it is
`stop` and parsing still fails, print the raw string before parsing it.

## Models

**`message.content` is empty but the call succeeded**

Check `message.tool_calls`. If the model asked for a tool, `content` is empty by
design. Also check `finish_reason`, which will be `tool_calls`.

**Reasoning text appears where I expected the answer**

Read `message.reasoning` for the thinking and `message.content` for the answer. They
are separate fields. If you did not want thinking at all, leave `enable_thinking`
off, which is the default.

**The model ignores my tool and makes something up**

Use `qwen3-8-27b`. `gemma-4-26b-a4b-it` is unreliable at tool calling: it fails several
`tool_choice` modes and can return an empty message after a tool result. If you need
images and tools in one application, use both models for the parts they are good at.

**The model calls the same tool over and over**

Usually gemma. It can fail to read a value out of a tool result and will call the same
tool again with the same arguments. Switch to `qwen3-8-27b`, and cap the number of turns
in your loop so a stuck model fails fast.

**A tool returned an error and the model did not recover**

Expected. No model here reliably recovers from a tool error on its own. Validate
arguments before you execute anything, and put retry logic in your code.

## Images

**`422` on an image URL**

The endpoint does not fetch images from the internet. Download the file and send it
as a base64 data URL. See [image input](inference.md#image-input).

**An error about images on a text model**

Only `gemma-4-26b-a4b-it` accepts images.

## Embeddings

**`400` on the `dimensions` parameter**

Not supported. This model returns 4,096 dimensions and cannot be truncated without
degrading the vectors.

**Retrieval returns nothing useful**

Check that documents and queries were embedded with the same model. Mixing models,
or changing models without re-embedding, produces vectors that cannot be compared.

## Still stuck

Open an issue on the repo with the module, the cell, the full error, and the output
of `python scripts/check_setup.py`. Remove your key from anything you paste.
