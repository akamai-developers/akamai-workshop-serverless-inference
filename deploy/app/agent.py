"""The agent from module 04, as a module instead of notebook cells.

Same two phase design: run the tool loop with no response_format, then add the
schema on a final request once the tool results are in the conversation. Setting
response_format while the model still needs a tool makes the tool call impossible,
and the model either stalls or invents an answer.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field

from workshop_utils.retrieval import build_index, search as search_index

MODEL = "qwen3-8b"
CORPUS = Path(__file__).parent / "corpus"
MAX_TURNS = 5

SYSTEM = (
    "You answer questions about Akamai Cloud Inference. "
    "Search the documentation before answering any factual question. "
    "Answer only from what the search returns, and name the source file. "
    "If the documents do not contain the answer, say so plainly instead of guessing."
)

COMPACT = "Reply with compact JSON on a single line. Do not add whitespace or newlines."

TOOLS = [{
    "type": "function",
    "function": {
        "name": "search_documents",
        "description": (
            "Search the Akamai Cloud Inference documentation. Covers the available "
            "models and their context limits, rate limits and error codes, tool "
            "calling behaviour, and embeddings."
        ),
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "What to search for"}},
            "required": ["query"],
        },
    },
}]


class Answer(BaseModel):
    answer: str = Field(description="the answer, two sentences at most")
    answer_found: bool = Field(
        description="true only if the documents contained the answer, false if they did not"
    )
    sources: list[str] = Field(description="source filenames actually used, empty if none")


ANSWER_SCHEMA = {
    "type": "json_schema",
    "json_schema": {"name": "answer", "schema": Answer.model_json_schema()},
}


class Agent:
    """Holds the client and the index so the corpus is embedded once at startup."""

    def __init__(self) -> None:
        base_url = os.environ["AKAMAI_BASE_URL"].strip().rstrip("/")
        api_key = os.environ["AKAMAI_API_KEY"].strip()
        if not base_url.endswith("/v1"):
            raise RuntimeError(f"AKAMAI_BASE_URL is {base_url!r}, it must end in /v1")

        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=120.0)
        self.index = build_index(self.client, CORPUS)

    def _search(self, query: str) -> dict[str, Any]:
        hits = search_index(self.client, self.index, query, top_k=3)
        return {
            "results": [
                {"source": h["source"], "score": h["score"], "text": h["text"][:600]}
                for h in hits
            ]
        }

    def ask(self, question: str) -> Answer:
        messages: list[Any] = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
        ]

        # Phase one. Tool loop, no response_format.
        for _ in range(MAX_TURNS):
            reply = self.client.chat.completions.create(
                model=MODEL, messages=messages, tools=TOOLS,
                max_tokens=600, temperature=0.0,
            )
            msg = reply.choices[0].message
            if not msg.tool_calls:
                messages.append(msg)
                break
            messages.append(msg)
            for call in msg.tool_calls:
                args = json.loads(call.function.arguments)
                result = self._search(**args) if call.function.name == "search_documents" else {
                    "error": f"no such function {call.function.name!r}"
                }
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result),
                })
        else:
            raise RuntimeError(f"no answer after {MAX_TURNS} turns")

        # Phase two. The tool results are in the conversation, so the schema is safe.
        formatted = self.client.chat.completions.create(
            model=MODEL,
            messages=messages + [{
                "role": "user",
                "content": (
                    "Now format your answer as JSON. Set answer_found to false if the "
                    f"documents did not contain the answer. {COMPACT}"
                ),
            }],
            response_format=ANSWER_SCHEMA,
            max_tokens=500,
            temperature=0.0,
        )
        if formatted.choices[0].finish_reason != "stop":
            raise RuntimeError(
                f"formatting call ended with {formatted.choices[0].finish_reason}"
            )
        return Answer.model_validate_json(formatted.choices[0].message.content)
