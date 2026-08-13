from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    embed_model: str = os.getenv("EMBED_MODEL", "Qwen/Qwen3-Embedding-0.6B")
    embedding_device: str = os.getenv("EMBEDDING_DEVICE", "auto")
    chunk_max_tokens: int = int(os.getenv("CHUNK_MAX_TOKENS", "512"))
    top_k: int = int(os.getenv("TOP_K", "5"))
    qdrant_path: Path = Path(os.getenv("QDRANT_PATH", "storage/qdrant"))
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "multilinguarag")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.5")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None


settings = Settings()
