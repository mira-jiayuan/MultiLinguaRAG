from __future__ import annotations

from openai import OpenAI

from .config import Settings
from .models import RetrievedChunk

ANSWER_LANGUAGES = {
    "auto": "Auto (same as query)",
    "zh": "Simplified Chinese",
    "ja": "Japanese",
    "en": "English",
}

BASE_SYSTEM_INSTRUCTIONS = """You are MultiLinguaRAG, a grounded cross-lingual knowledge assistant.
Use only the supplied retrieved context to answer the user's question.
The source language, query language, and answer language may be different.
Cite evidence inline using [S1], [S2], etc.
If the supplied context is insufficient, clearly say that the knowledge base does not contain enough information.
Do not invent sources, page numbers, quotations, or facts.
Preserve technical meaning when transferring information across languages."""


def normalize_answer_language(answer_language: str | None) -> str:
    value = (answer_language or "auto").strip().lower()
    aliases = {
        "auto": "auto",
        "same": "auto",
        "same-as-query": "auto",
        "zh": "zh",
        "cn": "zh",
        "chinese": "zh",
        "中文": "zh",
        "ja": "ja",
        "jp": "ja",
        "japanese": "ja",
        "日本語": "ja",
        "en": "en",
        "english": "en",
    }
    if value not in aliases:
        raise ValueError(
            f"Unsupported answer language: {answer_language!r}. "
            "Use one of: auto, zh, ja, en."
        )
    return aliases[value]


def build_generation_instructions(answer_language: str | None = "auto") -> str:
    lang = normalize_answer_language(answer_language)
    if lang == "zh":
        output_rule = (
            "Write the final answer in natural Simplified Chinese, regardless of the "
            "language of the question or retrieved sources."
        )
    elif lang == "ja":
        output_rule = (
            "Write the final answer in natural Japanese, regardless of the language of "
            "the question or retrieved sources. Prefer clear, professional Japanese "
            "suitable for academic or teaching-assistant work."
        )
    elif lang == "en":
        output_rule = (
            "Write the final answer in natural English, regardless of the language of "
            "the question or retrieved sources."
        )
    else:
        output_rule = (
            "Write the final answer in the same language as the user's question."
        )

    return BASE_SYSTEM_INSTRUCTIONS + "\n\nOutput language rule:\n" + output_rule


def generation_disabled_message(answer_language: str | None = "auto") -> str:
    lang = normalize_answer_language(answer_language)
    if lang == "zh":
        return "未配置 OPENAI_API_KEY，因此暂时只展示检索到的证据，未生成最终答案。"
    if lang == "ja":
        return "OPENAI_API_KEY が設定されていないため、生成は無効です。検索された根拠のみを表示します。"
    if lang == "en":
        return "Generation is disabled because OPENAI_API_KEY is not configured. Retrieved evidence is shown below."
    return (
        "Generation is disabled because OPENAI_API_KEY is not configured. "
        "The retrieved evidence is shown below."
    )


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

    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        answer_language: str | None = "auto",
    ) -> str:
        context = build_context(chunks)
        response = self.client.responses.create(
            model=self.cfg.openai_model,
            instructions=build_generation_instructions(answer_language),
            input=f"Question:\n{question}\n\nRetrieved context:\n{context}",
        )
        return response.output_text.strip()
