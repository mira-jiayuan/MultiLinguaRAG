from __future__ import annotations

import hashlib
from pathlib import Path

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

from .config import Settings
from .language import detect_language
from .models import ChunkRecord

SUPPORTED_SUFFIXES = {
    ".pdf", ".docx", ".pptx", ".xlsx", ".md", ".txt", ".html", ".htm", ".csv"
}


class DocumentIngestor:
    def __init__(self, cfg: Settings):
        self.cfg = cfg
        hf_tokenizer = AutoTokenizer.from_pretrained(cfg.embed_model)
        tokenizer = HuggingFaceTokenizer(
            tokenizer=hf_tokenizer,
            max_tokens=cfg.chunk_max_tokens,
        )
        self.converter = DocumentConverter()
        self.chunker = HybridChunker(tokenizer=tokenizer, merge_peers=True)

    def discover(self, path: str | Path) -> list[Path]:
        p = Path(path)
        if p.is_file():
            return [p]
        if not p.exists():
            raise FileNotFoundError(p)
        return sorted(
            item for item in p.rglob("*")
            if item.is_file() and item.suffix.lower() in SUPPORTED_SUFFIXES
        )

    @staticmethod
    def _page_of(chunk) -> int | None:
        try:
            for item in chunk.meta.doc_items:
                if item.prov:
                    return int(item.prov[0].page_no)
        except (AttributeError, IndexError, TypeError, ValueError):
            return None
        return None

    @staticmethod
    def _source_of(chunk, fallback: Path) -> str:
        try:
            if chunk.meta.origin and chunk.meta.origin.filename:
                return str(chunk.meta.origin.filename)
        except AttributeError:
            pass
        return fallback.name

    def chunk_file(self, file_path: str | Path) -> list[ChunkRecord]:
        file_path = Path(file_path)
        document = self.converter.convert(file_path).document
        records: list[ChunkRecord] = []

        for idx, chunk in enumerate(self.chunker.chunk(dl_doc=document)):
            text = self.chunker.contextualize(chunk=chunk).strip()
            if not text:
                continue
            source = self._source_of(chunk, file_path)
            raw_id = f"{source}:{idx}:{text}".encode("utf-8")
            chunk_id = hashlib.sha256(raw_id).hexdigest()[:32]
            headings = list(getattr(chunk.meta, "headings", None) or [])
            records.append(
                ChunkRecord(
                    id=chunk_id,
                    text=text,
                    source=source,
                    page=self._page_of(chunk),
                    language=detect_language(text),
                    headings=headings,
                )
            )
        return records

    def chunk_path(self, path: str | Path) -> list[ChunkRecord]:
        all_chunks: list[ChunkRecord] = []
        for file_path in self.discover(path):
            all_chunks.extend(self.chunk_file(file_path))
        return all_chunks
