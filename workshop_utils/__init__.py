"""Helpers shared between modules.

Module 02 builds everything here from scratch, cell by cell, so you can see how it
works. Module 04 imports it instead of making you paste the code again.
"""

from workshop_utils.retrieval import Index, build_index, chunk_text, load_corpus, search

__all__ = ["Index", "build_index", "chunk_text", "load_corpus", "search"]
