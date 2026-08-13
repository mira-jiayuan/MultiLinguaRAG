from __future__ import annotations

from openai import OpenAI

from .config import Settings
from .models import RetrievedChunk

SYSTEM_INSTRUCTIONS = """You are MultiLinguaRAG, a grounded multilingual knowledge assistant.
Use only the supplied retrieved context to answer.
Answer in the same language as the user's question unless the user asks otherwise.
Cite evidence inline using [S1], [S2], etc.
If the supplied context is insufficient, clearly say that the knowledge base does not contain enough information.
Do not invent sources, page numbers, or facts."""


def build_context(chunks: list[RetrievedChunk]) -> str:
    blocks = []
    for idx, chunk in enumerate(chunks, start=1):
        heading = " / ".join(chunk.headings) if chunk.headings else "n/a"
        blocks.append(
            f"[S{idx}] source={chunk.source}; page={chunk.page or 'n/a'}; "
            f"language={chunk.language}; section={heading}\n{chunk.text}"
        )
    return "\n\n".join(blocks)


class OpenAIGenerator:
    def __init__(self, cfg: Settings):
        if not cfg.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        self.cfg = cfg
        self.client = OpenAI(api_key=cfg.openai_api_key)

    def generate(self, question: str, chunks: list[RetrievedChunk]) -> str:
        context = build_context(chunks)
        response = self.client.responses.create(
            model=self.cfg.openai_model,
            instructions=SYSTEM_INSTRUCTIONS,
            input=f"Question:\n{question}\n\nRetrieved context:\n{context}",
        )
        return response.output_text.strip()
