from __future__ import annotations

from pathlib import Path

import streamlit as st

from multilinguarag.language import detect_language
from multilinguarag.rag import MultiLinguaRAG

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ANSWER_LANGUAGE_OPTIONS = {
    "Auto — same as query": "auto",
    "中文": "zh",
    "日本語": "ja",
    "English": "en",
}

st.set_page_config(page_title="MultiLinguaRAG", page_icon="🌏", layout="wide")
st.title("🌏 MultiLinguaRAG")
st.caption(
    "Source language, query language, and answer language are independent. "
    "Upload multilingual documents, ask in any supported language, and choose the output language."
)


@st.cache_resource
def get_rag() -> MultiLinguaRAG:
    return MultiLinguaRAG()


with st.sidebar:
    st.header("Knowledge base")
    st.caption("Documents may be Chinese, Japanese, English, or a mixture of them.")
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
    st.subheader("Answer settings")
    answer_language_label = st.selectbox(
        "Answer language",
        options=list(ANSWER_LANGUAGE_OPTIONS.keys()),
        index=0,
        help=(
            "This is independent of both the document language and the language used in the query. "
            "For example: English documents + Chinese query + Japanese answer."
        ),
    )
    answer_language = ANSWER_LANGUAGE_OPTIONS[answer_language_label]

    st.divider()
    st.markdown("**V1 pipeline**")
    st.markdown("Docling → HybridChunker → Qwen3-Embedding → Qdrant → Top-K → LLM")

st.info(
    "Example workflow: **English papers → ask in Chinese → generate a grounded Japanese answer**. "
    "The same retrieved evidence is cited regardless of the selected output language."
)

question = st.chat_input("Ask in Chinese, Japanese, or English…")

if question:
    query_language = detect_language(question)

    with st.chat_message("user"):
        st.write(question)
        st.caption(f"Detected query language: {query_language.upper()}")

    with st.chat_message("assistant"):
        with st.spinner("Retrieving evidence and generating answer..."):
            answer, chunks = get_rag().answer(
                question,
                answer_language=answer_language,
            )
        st.write(answer)
        st.caption(f"Answer language setting: {answer_language_label}")

        if chunks:
            st.markdown("### Sources")
            for idx, chunk in enumerate(chunks, start=1):
                st.markdown(
                    f"**[S{idx}] {chunk.citation}**  \n"
                    f"Similarity: `{chunk.score:.4f}` · Source language: `{chunk.language}`"
                )
                with st.expander(f"Retrieved chunk S{idx}"):
                    if chunk.headings:
                        st.caption("Section: " + " / ".join(chunk.headings))
                    st.write(chunk.text)
