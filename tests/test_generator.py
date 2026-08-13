from multilinguarag.generator import build_context
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
