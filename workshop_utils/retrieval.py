"""The retrieval index built in module 02, as importable functions.

No vector database. Chunks in a list, vectors in a NumPy array, cosine similarity
for search. That is enough for a workshop corpus and it keeps the moving parts
visible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

EMBED_MODEL = "qwen3-embedding-4b"

# One embeddings request carries an 8,192 token budget across all of its inputs,
# so send the chunks in small batches rather than all at once.
BATCH_SIZE = 8


@dataclass
class Index:
    """Chunks and their vectors, kept in the same order."""

    chunks: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    vectors: np.ndarray | None = None

    def __len__(self) -> int:
        return len(self.chunks)


def load_corpus(directory: str | Path) -> list[tuple[str, str]]:
    """Every markdown file in a directory, as (filename, text) pairs."""
    paths = sorted(Path(directory).glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"no .md files in {directory}")
    return [(p.name, p.read_text(encoding="utf-8")) for p in paths]


def chunk_text(text: str, max_chars: int = 900, overlap: int = 120) -> list[str]:
    """Split on blank lines, then pack paragraphs up to max_chars.

    Splitting on paragraphs keeps sentences intact, which matters because a chunk
    cut mid-sentence embeds badly. The overlap carries a little context across the
    boundary so an answer that straddles two chunks is still findable.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if current and len(current) + len(para) + 2 > max_chars:
            chunks.append(current)
            current = (current[-overlap:] + "\n\n" + para) if overlap else para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        chunks.append(current)
    return chunks


def embed(client: Any, texts: list[str], model: str = EMBED_MODEL) -> np.ndarray:
    """Embed texts in batches and return one array of shape (len(texts), dims)."""
    vectors: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        response = client.embeddings.create(model=model, input=texts[i : i + BATCH_SIZE])
        vectors.extend(item.embedding for item in response.data)
    return np.array(vectors, dtype=np.float32)


def build_index(client: Any, directory: str | Path, model: str = EMBED_MODEL) -> Index:
    """Load, chunk, and embed a directory of markdown files."""
    index = Index()
    for name, text in load_corpus(directory):
        for chunk in chunk_text(text):
            index.chunks.append(chunk)
            index.sources.append(name)
    index.vectors = embed(client, index.chunks, model=model)
    return index


def search(
    client: Any, index: Index, query: str, top_k: int = 3, model: str = EMBED_MODEL
) -> list[dict[str, Any]]:
    """The top_k chunks most similar to the query, best first.

    Scores are cosine similarity, so they rank results. A high score does not mean
    the chunk answers the question, and it never means the answer is correct.
    """
    if index.vectors is None or not len(index):
        raise ValueError("index is empty, call build_index first")

    q = embed(client, [query], model=model)[0]
    norms = np.linalg.norm(index.vectors, axis=1) * np.linalg.norm(q)
    norms[norms == 0] = 1e-9
    scores = (index.vectors @ q) / norms

    best = np.argsort(scores)[::-1][:top_k]
    return [
        {
            "text": index.chunks[i],
            "source": index.sources[i],
            "score": round(float(scores[i]), 4),
        }
        for i in best
    ]
