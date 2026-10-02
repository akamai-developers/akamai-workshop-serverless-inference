# Module 02: Embeddings and RAG

[Workshop home](../README.md) · [Setup](../docs/00_prework.md) · [Endpoint reference](../docs/inference.md)

**30 minutes.** Make the model answer from your documents instead of from memory.

| Notebook | Covers | Time |
|---|---|---|
| [1_embeddings_basics.ipynb](1_embeddings_basics.ipynb) | Embeddings, cosine similarity, the two limits that shape every index | 10 min |
| [2_build_a_rag_index.ipynb](2_build_a_rag_index.ipynb) | Chunking, building an index, searching it, grounding an answer, refusing when there is no answer | 20 min |

Run them in order. The second builds on the first.

## Before you start

[Module 01](../01_Inference_APIs/), or at least a working `.env`.

## What you will build

A retrieval pipeline with no vector database and no framework. Chunks in a list,
vectors in a NumPy array, cosine similarity for search. At workshop scale that is not
a shortcut, it is the right answer. You reach for pgvector when the corpus stops
fitting in memory or has to survive a restart.

The documents in `assets/sample-docs/` describe this workshop's own endpoint, so every
answer you get back is real and checkable against
[the endpoint reference](../docs/inference.md).

## What you should take away

- Similarity is a ranking signal. A high score does not mean a chunk answers the
  question, and never means the answer is correct.
- Retrieval always returns its best chunks, however irrelevant. So a score threshold
  cannot tell you whether an answer exists.
- The refusal path comes from an explicit instruction in the system prompt, not from
  the scores. Test it deliberately.
- Use the same embedding model for documents and queries. Changing models means
  re-embedding everything.

The code here is also available as `workshop_utils/retrieval.py`, which module 04
imports rather than making you paste it again.

## Next

[Module 03: Platform Features](../03_Platform_Features/), or skip to
[Module 04: Agents](../04_Agents/) to turn this search function into a tool the model
calls on its own.
