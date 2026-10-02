# Models served by Akamai Cloud Inference

The endpoint serves four models. List them at any time with a GET to `/v1/models`.

That endpoint returns only an id, an object type, a creation timestamp, and an owner.
It does not report context windows and it does not report which features a model
supports. Everything below comes from measuring the endpoint. To confirm a context
limit yourself, send a prompt that is far too long and read the number out of the
HTTP 400 that comes back.

## qwen3-8b

A general purpose chat model with a context window of 32,768 tokens. This is the
default model for most work. It handles tool calling in every mode, returns valid
JSON arguments, and can request several tool calls in a single turn. It also has an
optional reasoning mode.

Use qwen3-8b for chat, for tool calling, and for anything where the model needs to
work through a problem in steps.

## qwen3-4b

The same kind of model as qwen3-8b, smaller and cheaper, with the same context window
of 32,768 tokens. It passes the same tool calling tests as qwen3-8b. It is measurably
slower than qwen3-8b on multi-step tool work despite being the smaller model.

Use qwen3-4b when cost matters more than quality, for simple classification, short
summaries, and extraction from small inputs.

## gemma-4-26b-a4b-it

The only model on this endpoint that accepts image input, and the one with the
largest context window at 262,143 tokens. That is eight times the context of either
Qwen model, which makes it the right choice for long documents.

Images must be sent as base64 data URLs. The endpoint will not fetch an image from a
remote URL.

Do not use gemma-4-26b-a4b-it for tool calling. It fails several tool_choice modes,
and it can return an empty message after you send a tool result back. In testing it
called the same tool ten times in a row instead of reading the result it already had.
Use qwen3-8b for tools and gemma-4-26b-a4b-it only for images and long context.

## qwen3-embedding-4b

The only embedding model. It returns vectors of 2,560 dimensions and accepts up to
8,192 tokens across all the inputs in a single request.

Use the same embedding model for your documents and for your queries. If you change
embedding models, you have to re-embed every document, because vectors from different
models cannot be compared.

## Choosing a model

| Task | Model |
|---|---|
| Chat, tool calling, agents | qwen3-8b |
| Cheap classification or extraction | qwen3-4b |
| Image input | gemma-4-26b-a4b-it |
| Documents longer than 32,768 tokens | gemma-4-26b-a4b-it |
| Embeddings and retrieval | qwen3-embedding-4b |

The `/v1/models` endpoint reports context windows but does not report which features
a model supports. Capability information comes from testing, not from the API.
