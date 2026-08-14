from multilinguarag.generator import (
    build_context,
    build_generation_instructions,
    normalize_answer_language,
)
from multilinguarag.models import RetrievedChunk


def test_context_has_source_labels():
    chunks = [
        RetrievedChunk(
            text="RAG retrieves evidence.",
            score=0.9,
            source="demo.md",
            page=1,
            language="en",
            headings=["RAG"],
        )
    ]
    context = build_context(chunks)
    assert "[S1]" in context
    assert "demo.md" in context


def test_target_language_can_differ_from_query_and_source():
    instructions = build_generation_instructions("ja")
    assert "natural Japanese" in instructions
    assert "source language, query language, and answer language may be different" in instructions


def test_answer_language_aliases():
    assert normalize_answer_language("Japanese") == "ja"
    assert normalize_answer_language("中文") == "zh"
    assert normalize_answer_language("English") == "en"
    assert normalize_answer_language("auto") == "auto"
