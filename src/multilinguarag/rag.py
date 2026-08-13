from __future__ import annotations

from pathlib import Path

from .config import Settings, settings
from .embedder import Qwen3Embedder
from .generator import OpenAIGenerator
from .ingestion import DocumentIngestor
from .models import RetrievedChunk
from .vectorstore import QdrantStore


class MultiLinguaRAG:
    def __init__(self, cfg: Settings = settings):
        self.cfg = cfg
        self.embedder = Qwen3Embedder(cfg)
        self.store = QdrantStore(cfg, self.embedder.dimension)
        self.store.ensure_collection()

    def ingest(self, path: str | Path, recreate: bool = False) -> int:
        ingestor = DocumentIngestor(self.cfg)
        chunks = ingestor.chunk_path(path)
        if recreate:
            self.store.ensure_collection(recreate=True)
        vectors = self.embedder.embed_documents([chunk.text for chunk in chunks])
        self.store.upsert(chunks, vectors)
        return len(chunks)

    def retrieve(self, question: str, k: int | None = None) -> list[RetrievedChunk]:
        query_vector = self.embedder.embed_query(question)
        return self.store.search(query_vector, k or self.cfg.top_k)

    def answer(self, question: str, k: int | None = None) -> tuple[str, list[RetrievedChunk]]:
        chunks = self.retrieve(question, k=k)
        if not chunks:
            return "No relevant context was retrieved.", []
        if not self.cfg.openai_api_key:
            return (
                "Generation is disabled because OPENAI_API_KEY is not configured. "
                "The retrieved evidence is shown below.",
                chunks,
            )
        answer = OpenAIGenerator(self.cfg).generate(question, chunks)
        return answer, chunks
