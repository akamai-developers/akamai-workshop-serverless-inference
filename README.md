# Getting started with Akamai Cloud Inference

> ### $300 in free credit for Akamai Cloud
> Sign up here: **[http://login.linode.com/signup?promo=akm-dev-git-300-72326-P153](http://login.linode.com/signup?promo=akm-dev-git-300-72326-P153)**

Call a model, build retrieval over your own documents, and put both into an agent.
Four modules of runnable notebooks, about two hours end to end, or 35 minutes for the
lightning path. You need an Akamai Cloud account and an inference key. You do not
need a GPU, and the workshop itself creates no cloud resources.

Akamai Cloud Inference serves open models behind an OpenAI-compatible API. If you
have written code against the OpenAI SDK, change the base URL and the key and your
code runs. The workshop starts there, then covers the rest of the platform:
embeddings, image input, reasoning mode, structured output, and tool calling.

## Start here

1. **[Get an API key](docs/get-an-api-key.md)** for Akamai Cloud Inference.
2. **[Set up your laptop](docs/00_prework.md)** before the session.
3. **[Call your first model](01_Inference_APIs/)** and watch the request go out.
4. **[Build retrieval](02_Embeddings_and_RAG/)** over your own documents.

## Modules

| Module | What you build | Time |
|---|---|---|
| [01 Inference APIs](01_Inference_APIs/) | Your first request, streaming, sampling, error handling | 25 min |
| [02 Embeddings and RAG](02_Embeddings_and_RAG/) | A retrieval index that answers from your documents and cites them | 30 min |
| [03 Platform Features](03_Platform_Features/) | Image input, reasoning mode, and typed JSON output | 25 min |
| [04 Agents](04_Agents/) | A tool-calling loop, then an agent that searches and answers | 45 min |
| [deploy](deploy/) | The agent running on a Linode, optional | 30 min |

Short on time? Run module 01 and the first notebook of module 02. That is 35 minutes
and you will have called a model and built a working index. Modules 02, 03, and 04
are independent once 01 is done.

## Find what you need

| Topic | Guide |
|---|---|
| Getting an account and a key | [Get an API key](docs/get-an-api-key.md) |
| Python, the virtual environment, and `.env` | [Setup](docs/00_prework.md) |
| Models, limits, and request shapes | [Endpoint reference](docs/inference.md) |
| Something broke | [Troubleshooting](docs/troubleshooting.md) |
| Running the workshop for a group | [Instructor guide](docs/instructor.md) |

The sample documents in modules 02 and 04 describe this workshop's own endpoint, so
the agent you build answers real questions about the platform. Model availability and
limits can change. Confirm anything load bearing against the
[official documentation](https://techdocs.akamai.com/cloud-computing/docs/ai-inference).

Clear notebook outputs before sharing or committing them. They can contain your
prompts and your results, and output cells are easy to forget.
