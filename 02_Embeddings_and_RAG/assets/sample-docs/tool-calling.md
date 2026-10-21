# Tool calling

Tool calling lets a model ask your application to run a function and then use the
result. The model never executes anything. It returns a request, your code decides
whether to honour it, and you send the result back.

## The loop

1. Send the conversation along with a `tools` array describing your functions.
2. If the response has `tool_calls`, the model wants one or more functions run.
3. Execute them yourself, after validating the arguments.
4. Append the assistant message, then one `tool` message per call, each carrying the
   matching `tool_call_id`.
5. Send the conversation again. Repeat until the model answers with no tool calls.

Cap the number of trips around that loop. A model that gets stuck will otherwise
repeat the same call indefinitely.

## tool_choice

The `tool_choice` parameter controls whether the model may call a function.

| Value | Behaviour |
|---|---|
| `auto` | The model decides. This is the default |
| `none` | No tool calls. The model answers with text |
| `required` | The model must call some tool |
| A named function | The model must call that specific function |

All four work on qwen3-8-27b. On gemma-4-26b-a4b-it, `none`, `required`,
and named selection are unreliable.

## Parallel calls

A model can request several tool calls in one turn, for example looking up two cities
at once. Each call has its own `tool_call_id`, and you must return one `tool` message
for each. Returning fewer will confuse the next turn.

## Structured output and tools together

Do not set `response_format` on a request where the model still needs to call a tool.

A JSON schema in `response_format` constrains every token the model can produce. That
means the model cannot emit a tool call while the schema is active. If the values the
schema requires are only available through a tool, the model is stuck: it cannot call
the tool, and it cannot fill in the fields. It stalls, pads the output with
whitespace until it reaches `max_tokens`, and returns `finish_reason: length`. The
whole output budget is billed and nothing useful comes back.

The fix is ordering. Run the tool loop with no `response_format`. Once the tool
results are in the conversation, make one more request that adds the schema. Tools
may stay attached on that final request, because the model no longer needs to call
anything. Setting `tool_choice` to `required` is another way out, since it forces the
tool call instead of the schema.

## Tool errors

No model on this endpoint reliably recovers when a tool returns an error. In testing,
all three chat models either repeated the identical failing call or gave up entirely.

Do not expect the model to handle failure. Validate arguments before executing
anything, return errors as structured data the model can read, cap the loop, and put
retry logic in your own code.
