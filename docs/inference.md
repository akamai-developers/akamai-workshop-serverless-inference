# Endpoint reference

[Workshop home](../README.md) · [Setup](00_prework.md) · [Troubleshooting](troubleshooting.md)

What this endpoint serves, what it accepts, and where it differs from the OpenAI API.
Everything here was measured against the live endpoint. Model availability and limits
change, so confirm anything load bearing against the
[official documentation](https://techdocs.akamai.com/cloud-computing/docs/ai-inference).

## Connection

```ini
AKAMAI_BASE_URL=https://api.akamai-inference.com/v1
AKAMAI_API_KEY=sk_aka_your_key_here
```

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env", override=True)
client = OpenAI(
    base_url=os.environ["AKAMAI_BASE_URL"],
    api_key=os.environ["AKAMAI_API_KEY"],
    timeout=60.0,
)
```

`override=True` makes the workshop settings win even if your shell already exports
another provider's key. The OpenAI client reads environment variables but does not
read `.env` on its own.

Every request is `Authorization: Bearer <key>` and a JSON body. Keep the key on a
server in anything you ship.

## Models

```bash
curl -s $AKAMAI_BASE_URL/models -H "Authorization: Bearer $AKAMAI_API_KEY"
```

| Model | Use it for | Enforced context limit |
|---|---|---|
| `qwen3-8-27b` | Chat, tool calling, reasoning mode. The default for this workshop | 32,768 |
| `gemma-4-26b-a4b-it` | Image input, and long documents | 262,143 |
| `qwen3-embedding-8b` | Embeddings. 4,096 dimensions | 8,192 |

`/v1/models` returns only `id`, `object`, `created`, and `owned_by`. It reports no
context window and no capability information, so everything in the table above comes
from measuring the endpoint rather than asking it.

To confirm a context limit yourself, send a prompt that is obviously too long and
read the number out of the `400`. An earlier version of this endpoint did report
`max_model_len` and has since stopped, so re-check rather than trusting this page.

Use `qwen3-8-27b` for anything involving tools. `gemma-4-26b-a4b-it` is the only model
that accepts images, and it is unreliable at tool calling. See
[model specific behavior](#model-specific-behavior).

## Chat

```python
response = client.chat.completions.create(
    model="qwen3-8-27b",
    messages=[{"role": "user", "content": "Explain an API key in two sentences."}],
    max_tokens=150,
)
print(response.choices[0].message.content)
print(response.choices[0].finish_reason)
```

`messages` carries the conversation. Your application stores the history and resends
it. `finish_reason` of `length` means the answer was cut off, and `tool_calls` means
the model wants you to run a function.

These all work as the OpenAI API documents them: `temperature`, `top_p`, `stop`, `n`,
`seed`, `logprobs`, `max_tokens`, `presence_penalty`, `frequency_penalty`. Unknown
parameters are ignored rather than rejected.

Streaming works, including the usage block at the end of the stream, and a streamed
answer matches the non-streamed one.

```python
for chunk in client.chat.completions.create(
    model="qwen3-8-27b",
    messages=[{"role": "user", "content": "Count to five."}],
    max_tokens=40,
    stream=True,
):
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## Embeddings

```python
response = client.embeddings.create(
    model="qwen3-embedding-8b",
    input=["A document paragraph", "A second paragraph"],
)
vectors = [item.embedding for item in response.data]
print(len(vectors), len(vectors[0]))
```

4,096 dimensions. Use the same model for documents and for queries, and re-embed
everything if you ever change models.

The `dimensions` parameter is rejected with `400`, because this model has no
Matryoshka representation and truncating its vectors would degrade them. If you need
smaller vectors, use a different model rather than slicing these.

Each request has an 8,192 token budget across all its inputs, so chunk long documents
before sending them. [Module 02](../02_Embeddings_and_RAG/) covers chunking.

## Structured output

```python
schema = {
    "type": "object",
    "properties": {"name": {"type": "string"}, "city": {"type": "string"}},
    "required": ["name", "city"],
    "additionalProperties": False,
}
response = client.chat.completions.create(
    model="qwen3-8-27b",
    messages=[{"role": "user", "content": "Extract: Ada works in Nairobi."}],
    response_format={"type": "json_schema", "json_schema": {"name": "person", "schema": schema}},
    max_tokens=200,
)
```

Both `{"type": "json_object"}` and `{"type": "json_schema"}` work. Check
`finish_reason` before parsing, because a truncated response is still invalid JSON.

**One sharp edge.** Do not set `response_format` on a request where the model still
needs to call a tool. The schema constrains every token the model can produce, so it
cannot emit a tool call, and it cannot fill in fields whose values live behind that
tool. The request stalls, pads the output with whitespace until it hits `max_tokens`,
and returns `finish_reason: length`. You are billed for the whole budget.

Run the tool loop first with no `response_format`, then add it on a final request
once the tool results are in the conversation. Tools may stay attached on that last
request. `tool_choice: "required"` also works if you want to force the tool call.
[Module 04](../04_Agents/) builds this.

## Tool calling

`tool_choice` accepts `auto`, `none`, `required`, and a named function. Arguments
come back as valid JSON, and the model can request more than one call in a turn.

Send the result back as a `tool` message carrying the matching `tool_call_id`:

```python
messages.append(assistant_message)
messages.append({
    "role": "tool",
    "tool_call_id": call.id,
    "content": json.dumps(result),
})
```

Models do not reliably recover when a tool returns an error. In testing, all three
chat models either repeated the identical failing call or gave up. Validate arguments
and handle retries in your own code rather than asking the model to cope.

## Image input

`gemma-4-26b-a4b-it` only. Send a base64 data URL:

```python
import base64
b64 = base64.b64encode(open("photo.png", "rb").read()).decode()
response = client.chat.completions.create(
    model="gemma-4-26b-a4b-it",
    messages=[{"role": "user", "content": [
        {"type": "text", "text": "What is in this image?"},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
    ]}],
    max_tokens=200,
)
```

A remote `https://` image URL is rejected with `422`, because the endpoint does not
fetch images from the public internet. Download the image and encode it yourself.
Sending an image to a text only model returns a clear error.

## Reasoning mode

`qwen3-8-27b` has a thinking mode, off unless you ask for it:

```python
response = client.chat.completions.create(
    model="qwen3-8-27b",
    messages=[{"role": "user", "content": "If 3 machines take 3 minutes, how long for 100?"}],
    max_tokens=600,
    extra_body={"chat_template_kwargs": {"enable_thinking": True}},
)
print(response.choices[0].message.reasoning)
print(response.choices[0].message.content)
```

Reasoning arrives in a separate `reasoning` field, so your `content` stays clean. It
spends output tokens and adds latency. Leave it off for short factual work and raise
`max_tokens` when you turn it on.

## Model specific behavior

| Behavior | qwen3-8-27b | gemma-4-26b-a4b-it |
|---|---|---|
| Tool calling, all `tool_choice` modes | works | unreliable |
| Sending a tool result back | works | can return an empty message |
| Image input | not supported | works, base64 only |
| Reasoning mode | works | no |

Use `qwen3-8-27b` for tools and `gemma-4-26b-a4b-it` only for images.

## Errors

The endpoint's error messages are specific and quote the numbers you need.

| What you did | What comes back |
|---|---|
| Bad key | `401` |
| Model name typo | `404` The model 'x' does not exist |
| Missing `model` | `422` Missing required parameter: 'model'. |
| Malformed JSON body | `422` Invalid JSON in request body at character 78 |
| Empty `messages` | `400` Cannot apply chat template to an empty conversation. |
| `messages` not a list | `422` 'messages': input should be a valid list. |
| Prompt too long | `400` Estimated input token count (318947) exceeds the model limit (262143). |

Two things to know.

The token count in that last error is an **estimate** made by the endpoint, and it
will not match your local tokenizer exactly. A prompt you calculated as fitting
inside the advertised context can still be rejected. Leave headroom rather than
aiming at the limit.

A message with `content: null` is accepted with `200` instead of being rejected.
Validate your message objects in your own code.

## Rate limits

Read them from the response headers rather than assuming a number:

```python
import requests
r = requests.post(
    f"{base_url}/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={"model": "qwen3-8-27b", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
)
print({k: v for k, v in r.headers.items() if k.lower().startswith("x-ratelimit")})
```

On `429`, back off and retry with a bounded number of attempts.
[Module 01](../01_Inference_APIs/) prints these headers so you can see your own
limits.
