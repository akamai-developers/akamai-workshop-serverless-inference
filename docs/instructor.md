# Instructor guide

[Workshop home](../README.md) · [Setup](00_prework.md) · [Endpoint reference](inference.md)

How to run this for a group. Attendees do not need this page.

## Pick a path

| Path | Run | Time | Fits |
|---|---|---|---|
| Lightning | 01, then 02 notebook 1 | 35 min | A conference session or a lunch and learn |
| Guided | 01, 02, 04 | 1 hr 40 min | A half day, with 03 as homework |
| Full | 01 through 04 | 2 hr 5 min | Self serve |

Modules 02, 03, and 04 are independent once 01 is done. Each opens with a short setup
cell, so an attendee who skips 03 can still run 04. The only fixed order is inside 02
and 04, where the second notebook builds on the first.

Cut 03 first if you are short on time. Tool calling lands better with a developer
audience than image input, and 04 recaps the one thing it borrows from 03.

## Before the session

Send [get an API key](get-an-api-key.md) and [setup](00_prework.md) at least two days
ahead. Account verification is the single biggest cause of someone sitting idle, and
you cannot fix it from the room.

Ask attendees to run `python scripts/check_setup.py` and report failures before they
arrive. Then:

- Run every notebook yourself the morning of, against the live endpoint. Model
  availability changes.
- Confirm `curl $AKAMAI_BASE_URL/models` still lists the models the materials
  name. If a model was replaced, the model table in
  [the endpoint reference](inference.md#models) is the one place to correct.
- Have a key ready to lend. Someone will arrive without one.

## Teaching notes

**Module 01.** The first cell is a raw `requests.post` on purpose. Attendees see the
status code, the rate limit headers, and the JSON shape before any SDK hides them.
Then the same call through the OpenAI client with two lines changed. That swap is the
main idea of the whole workshop, so do not rush it.

**Module 02.** Resist adding a vector database. The index is a NumPy array and a
cosine similarity function, which is the point: attendees see that retrieval is
arithmetic, not infrastructure. The refusal case at the end matters more than the
happy path, because it is the one people skip and then ship without.

**Module 03.** Image input is base64 only. Someone will try a URL and get a `422`.
That is in the notebook as a deliberate step rather than a surprise.

**Module 04.** The agent runs the tool loop with no `response_format`, then adds it
on a final request. If you get asked why, the short answer is that a schema
constrains every token, so the model cannot emit a tool call while one is set. It
stalls and burns the output budget. Notebook 2 shows the failure before the fix.

## Model choices, and why

| Module | Model | Reason |
|---|---|---|
| 01, 02, 04 | `qwen3-8-27b` | Passes every tool calling mode. Fast |
| 03, image input only | `gemma-4-26b-a4b-it` | The only model that accepts images |
| 02 | `qwen3-embedding-8b` | The only embedding model |

Do not use `gemma-4-26b-a4b-it` for tool calling. It fails several `tool_choice`
modes and can return an empty message after a tool result. In testing it called the
same tool ten times in a row rather than reading the result. If an attendee swaps the
model and their agent breaks, this is why.

## Things that will come up

**"Can I use LangChain or an agent framework?"** Yes, for their own projects. The
workshop writes the loop by hand because the loop is the thing being taught.

**"Is this just OpenAI?"** It is the OpenAI API shape served by Akamai running open
models. The SDK swap in module 01 is the demonstration.

**"What does it cost?"** The workshop creates no cloud resources. Inference is billed
per token against their account. The optional [deploy](../deploy/) folder creates a
Linode and states its cost before creating it.

**"Why is the answer different each run?"** Default sampling. Module 01 covers
`temperature` and `seed`.

## After the session

Point attendees at [deploy](../deploy/) if they want the agent running somewhere, and
remind anyone who ran it to tear it down. Ask them to clear notebook outputs before
pushing their fork, since outputs can contain keys in tracebacks.
