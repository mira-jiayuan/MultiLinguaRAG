from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ChunkRecord:
    id: str
    text: str
    source: str
    page: int | None = None
    language: str = "unknown"
    headings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RetrievedChunk:
    text: str
    score: float
    source: str
    page: int | None
    language: str
    headings: list[str]

    @property
    def citation(self) -> str:
        page = f"p.{self.page}" if self.page is not None else "page n/a"
        return f"{self.source} · {page}"
