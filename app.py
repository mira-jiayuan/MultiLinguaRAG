from __future__ import annotations

from pathlib import Path

import streamlit as st

from multilinguarag.rag import MultiLinguaRAG

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="MultiLinguaRAG", page_icon="🌏", layout="wide")
st.title("🌏 MultiLinguaRAG")
st.caption("Chinese · Japanese · English cross-lingual retrieval with grounded answers and citations")


@st.cache_resource
def get_rag() -> MultiLinguaRAG:
    return MultiLinguaRAG()


with st.sidebar:
    st.header("Knowledge base")
    files = st.file_uploader(
        "Upload documents",
        type=["pdf", "md", "txt", "docx", "pptx", "xlsx", "html", "csv"],
        accept_multiple_files=True,
    )
    if st.button("Build / refresh index", type="primary", use_container_width=True):
        if not files:
            st.warning("Upload at least one document first.")
        else:
            for file in files:
                (UPLOAD_DIR / file.name).write_bytes(file.getbuffer())
            with st.spinner("Parsing, chunking and embedding documents..."):
                count = get_rag().ingest(UPLOAD_DIR, recreate=True)
            st.success(f"Indexed {count} chunks from {len(files)} file(s).")

    st.divider()
    st.markdown("**V1 pipeline**")
    st.markdown("Docling → HybridChunker → Qwen3-Embedding → Qdrant → Top-K → LLM")

question = st.chat_input("Ask in Chinese, Japanese, or English…")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving evidence..."):
            answer, chunks = get_rag().answer(question)
        st.write(answer)

        if chunks:
            st.markdown("### Sources")
            for idx, chunk in enumerate(chunks, start=1):
                st.markdown(
                    f"**[S{idx}] {chunk.citation}**  \n"
                    f"Similarity: `{chunk.score:.4f}` · Language: `{chunk.language}`"
                )
                with st.expander(f"Retrieved chunk S{idx}"):
                    if chunk.headings:
                        st.caption("Section: " + " / ".join(chunk.headings))
                    st.write(chunk.text)
