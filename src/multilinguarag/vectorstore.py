from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from qdrant_client import QdrantClient, models

from .config import Settings
from .models import ChunkRecord, RetrievedChunk


class QdrantStore:
    def __init__(self, cfg: Settings, vector_size: int):
        self.cfg = cfg
        Path(cfg.qdrant_path).parent.mkdir(parents=True, exist_ok=True)
        self.client = QdrantClient(path=str(cfg.qdrant_path))
        self.vector_size = vector_size

    def _collection_names(self) -> set[str]:
        return {c.name for c in self.client.get_collections().collections}

    def ensure_collection(self, recreate: bool = False) -> None:
        name = self.cfg.qdrant_collection
        exists = name in self._collection_names()
        if recreate and exists:
            self.client.delete_collection(name)
            exists = False
        if not exists:
            self.client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE,
                ),
            )

    def upsert(self, chunks: Sequence[ChunkRecord], vectors) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")
        points = []
        for chunk, vector in zip(chunks, vectors, strict=True):
            points.append(
                models.PointStruct(
                    id=chunk.id,
                    vector=vector.tolist() if hasattr(vector, "tolist") else list(vector),
                    payload={
                        "text": chunk.text,
                        "source": chunk.source,
                        "page": chunk.page,
                        "language": chunk.language,
                        "headings": chunk.headings,
                    },
                )
            )
        if points:
            self.client.upsert(
                collection_name=self.cfg.qdrant_collection,
                points=points,
                wait=True,
            )

    def search(self, query_vector: list[float], k: int) -> list[RetrievedChunk]:
        response = self.client.query_points(
            collection_name=self.cfg.qdrant_collection,
            query=query_vector,
            limit=k,
            with_payload=True,
        )
        output: list[RetrievedChunk] = []
        for point in response.points:
            payload = point.payload or {}
            output.append(
                RetrievedChunk(
                    text=str(payload.get("text", "")),
                    score=float(point.score),
                    source=str(payload.get("source", "unknown")),
                    page=payload.get("page"),
                    language=str(payload.get("language", "unknown")),
                    headings=list(payload.get("headings", []) or []),
                )
            )
        return output
