# Limits and error handling

## Context windows

The context window is the total of input and output tokens for a single request.

| Model | Context window |
|---|---|
| qwen3-8-27b | 32,768 |
| gemma-4-26b-a4b-it | 262,143 |
| qwen3-embedding-8b | 8,192 |

A prompt that is too long returns HTTP 400 with a message naming both numbers, for
example "Estimated input token count (318947) exceeds the model limit (262143)."

The word estimated matters. The endpoint estimates the token count itself, and that
estimate will not match a local tokenizer exactly. A prompt you calculated as fitting
inside the advertised window can still be rejected. Leave headroom rather than aiming
at the limit.

## Error codes

| Code | Cause |
|---|---|
| 400 | The request was understood but cannot be served, usually a prompt over the context limit |
| 401 | The API key is missing, wrong, or has whitespace around it |
| 404 | The model name does not exist, or the base URL is missing its /v1 suffix |
| 422 | The request body is malformed or a field has the wrong type |
| 429 | Rate limited. Back off and retry a bounded number of times |

Error messages on this endpoint are specific and quote the values involved. A bad
JSON body returns "Invalid JSON in request body at character 78." A missing model
field returns "Missing required parameter: 'model'." An empty messages array returns
"Cannot apply chat template to an empty conversation." A messages field that is not a
list returns "'messages': input should be a valid list."

## A 404 on every single request

The most common cause is a base URL without the `/v1` suffix. The correct base URL is
`https://api.akamai-inference.com/v1`. Leaving off `/v1` produces a 404 that looks
like a bad model name and is not.

## Checking a response before you use it

Always read `finish_reason` before you use the content of a response.

A `finish_reason` of `stop` means the model finished normally. A value of `length`
means the answer was cut off because it hit `max_tokens`, and the content is
incomplete. A value of `tool_calls` means the model wants you to run a function, and
the content will be empty by design.

Parsing a truncated response as JSON will fail, so check `finish_reason` before
calling `json.loads`.

## Validation gaps

A chat message with `content` set to null is accepted with HTTP 200 rather than being
rejected. Validate your message objects in your own code rather than relying on the
endpoint to catch malformed ones.

## Rate limits

Rate limit information comes back in response headers beginning with `x-ratelimit`.
Read those headers rather than assuming a fixed number, because limits depend on the
account. On a 429, back off and retry with a bounded number of attempts rather than
retrying forever.
