# Embeddings and retrieval

An embedding turns text into a list of numbers. Text with similar meaning produces
vectors that point in similar directions, which lets you rank documents by relevance
without matching keywords.

## The embedding model

`qwen3-embedding-4b` is the only embedding model on this endpoint. It returns 2,560
dimensions per vector and accepts up to 8,192 tokens across all the inputs in one
request.

The `dimensions` parameter is rejected with HTTP 400. The model has no Matryoshka
representation, which means its vectors cannot be truncated to a shorter length
without degrading them. If you need smaller vectors, choose a different model rather
than slicing these.

## Chunking

Long documents have to be split before embedding, for two reasons. The request has an
8,192 token budget, and a vector that averages an entire document is too vague to
rank well against a specific question.

Split on paragraph boundaries rather than at a fixed character count, so sentences
stay intact. A chunk cut mid sentence embeds badly. Carrying a small overlap between
neighbouring chunks helps when an answer straddles a boundary.

Chunks of roughly 500 to 1,000 characters work well for documentation.

## Cosine similarity

Similarity between two vectors is their dot product divided by the product of their
lengths. The result runs from -1 to 1, and higher means more similar.

Cosine similarity is a ranking signal and nothing more. A high score means a chunk is
topically close to the question. It does not mean the chunk answers the question, and
it certainly does not mean the answer is correct. Always show the user which source
an answer came from.

## Building an index

A retrieval index needs no database at workshop scale. Keep the chunks in a list and
their vectors in a single array, in the same order, so position `i` in one matches
position `i` in the other. To search, embed the question and compute its similarity
against every stored vector, then take the highest scoring few.

Use the same embedding model for documents and for queries. Vectors produced by
different models are not comparable. Changing models means re-embedding everything.

## Grounding an answer

Retrieval on its own returns chunks, not answers. To answer a question, put the top
chunks into the prompt as context and instruct the model to answer only from what it
was given.

Include the source filename with each chunk so the model can cite it, and tell the
model explicitly to say it does not know when the context does not contain the
answer. Without that instruction a model will usually invent something plausible
rather than admit the gap. Test the no answer case deliberately, because it is the
one most people skip.
