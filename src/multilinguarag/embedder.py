from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

from .config import Settings


class Qwen3Embedder:
    """Dense multilingual embeddings using Qwen3-Embedding.

    Qwen recommends a query instruction/prompt for query embeddings while document
    embeddings are encoded without the query prompt.
    """

    def __init__(self, cfg: Settings):
        kwargs: dict[str, object] = {}
        if cfg.embedding_device != "auto":
            kwargs["device"] = cfg.embedding_device
        self.model = SentenceTransformer(cfg.embed_model, **kwargs)

    @property
    def dimension(self) -> int:
        dim = self.model.get_sentence_embedding_dimension()
        if dim is None:
            raise RuntimeError("Could not determine embedding dimension.")
        return int(dim)

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray:
        return self.model.encode(
            list(texts),
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 8,
        )

    def embed_query(self, query: str) -> list[float]:
        vector = self.model.encode(
            [query],
            prompt_name="query",
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]
        return vector.tolist()
