# 🌏 MultiLinguaRAG

**A compact multilingual RAG knowledge assistant for Chinese, Japanese, and English documents.**

> V1 goal: make the core **Indexing → Retrieval → Generation** pipeline clear, inspectable, and portfolio-ready—without hiding it behind a large RAG framework.

## ✨ What it does

- Parses PDF / DOCX / PPTX / XLSX / Markdown / TXT / HTML / CSV with **Docling**.
- Uses **Docling HybridChunker** for structure-aware, tokenizer-aware chunks.
- Uses **Qwen3-Embedding-0.6B** for multilingual and cross-lingual dense retrieval.
- Stores vectors + source metadata in local **Qdrant**.
- Retrieves **Top-K** evidence with cosine similarity.
- Generates grounded answers through the **OpenAI Responses API** when an API key is configured.
- Shows deterministic source metadata and retrieved chunks in a **Streamlit** UI.

## 🧠 Core architecture

```text
Chinese / Japanese / English documents
                │
                ▼
             Docling
                │
                ▼
          HybridChunker
                │
                ▼
       Qwen3-Embedding-0.6B
                │
                ▼
             Qdrant
                ▲
                │
User query → Qwen3 query embedding
                │
                ▼
          Top-K retrieval
                │
                ▼
       Context + Question
                │
                ▼
               LLM
                │
                ▼
      Answer + source citations
```

## 🔥 Why this project is interesting

The key feature is **cross-lingual retrieval**, not simply storing three languages in one database.

Example:

```text
Knowledge base (Japanese):
「RAG は外部知識を検索して回答生成に利用する技術です。」

User query (Chinese):
“RAG 是什么？”

→ multilingual query embedding
→ retrieves the Japanese chunk
→ answers in Chinese and cites the Japanese source
```

Qwen3-Embedding supports 100+ languages and is designed for multilingual and cross-lingual retrieval. Its model documentation recommends using a query instruction/prompt for query embeddings; this repository follows that pattern.

## 🧰 Stack

| Layer | Technology |
|---|---|
| Document parsing | Docling 2.119.0 |
| Chunking | Docling HybridChunker |
| Embedding | Qwen/Qwen3-Embedding-0.6B |
| Embedding runtime | sentence-transformers 5.7.0 |
| Vector database | Qdrant Client 1.19.0 (local persistent mode) |
| Generation | OpenAI Python 3.0.0 / Responses API |
| UI | Streamlit 1.61.1 |
| Project management | uv + pyproject.toml |

## 🚀 Quick start

### 1. Install uv

Follow the official uv installation guide, then from this repository run:

```bash
uv sync
```

> The first local run of Qwen3-Embedding downloads model weights. That download is not included in this Git repository.

### 2. Configure environment

```bash
cp .env.example .env
```

`OPENAI_API_KEY` is optional. Without it, retrieval still works and the UI shows retrieved evidence, but answer generation is disabled.

### 3. Index the bundled multilingual sample documents

```bash
uv run multilinguarag-ingest data/sample --recreate
```

### 4. Test cross-lingual retrieval

Chinese query against multilingual documents:

```bash
uv run multilinguarag-query "多语言 embedding 为什么可以检索日文资料？"
```

Japanese query:

```bash
uv run multilinguarag-query "Top-K を大きくしすぎると何が起こりますか？"
```

### 5. Launch the web app

```bash
uv run streamlit run app.py
```

Then upload your own documents from the sidebar and rebuild the index.

## 📁 Repository structure

```text
MultiLinguaRAG/
├── app.py
├── data/
│   ├── sample/                 # small original demo corpus
│   └── uploads/                # ignored by Git
├── scripts/
│   ├── ingest.py
│   └── query.py
├── src/multilinguarag/
│   ├── config.py
│   ├── embedder.py
│   ├── generator.py
│   ├── ingestion.py
│   ├── language.py
│   ├── models.py
│   ├── rag.py
│   └── vectorstore.py
├── storage/                    # local Qdrant data, ignored by Git
├── tests/
├── INTERVIEW_GUIDE.md
├── .env.example
├── pyproject.toml
└── LICENSE
```

## 🔍 Important implementation choices

### 🔥 1. Structure-aware chunking
Fixed character splitting is intentionally not the primary chunker. Docling HybridChunker applies tokenizer-aware refinements on top of hierarchical document structure. The chunker is configured with the **same Hugging Face tokenizer used by the Qwen3 embedding model**.

### 🔥 2. Query and document embeddings are not encoded identically
Qwen3-Embedding documents are encoded normally, while queries use `prompt_name="query"` as recommended by the model card.

### 🔥 3. Citation metadata is stored with each vector
A Qdrant point includes the vector plus payload fields such as source, page, language, headings, and the original chunk text. This preserves the connection from retrieval result back to source evidence.

### 🔥 4. V1 is deliberately dense-only
No BM25, reranker, query rewriting, CRAG, Self-RAG, or agent routing is included in V1. The purpose is to establish a clean baseline that can be evaluated before adding complexity.

## 🎯 Interview questions

Before putting this project on a resume, be able to answer:

1. Why use RAG instead of only prompting an LLM?
2. How can a Chinese query retrieve a Japanese document?
3. Why use the embedding model's tokenizer for chunking?
4. Why use Qdrant instead of a plain list of vectors?
5. What is cosine similarity?
6. What is Top-K and what is its precision/recall trade-off?
7. Why does Qwen3 use a query prompt but not the same prompt for documents?
8. Why can RAG still hallucinate?
9. How would you evaluate cross-lingual retrieval?
10. What would you add after the dense V1 baseline?

See **[INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md)** for answer frameworks.

## 📊 Recommended evaluation before claiming results

Create labeled queries for:

- zh query → zh source
- ja query → ja source
- en query → en source
- **zh query → ja source**
- **ja query → en source**
- **en query → zh source**

Report retrieval metrics such as **Recall@K** and **MRR**. Do not put invented accuracy improvements in the README or resume.

## 🗺️ V2 ideas (optional)

Only after V1 is evaluated:

- multilingual reranker
- hybrid dense + sparse retrieval
- metadata filtering
- parent-child retrieval
- retrieval evaluation dashboard

## 📚 Primary references

- [Docling documentation](https://docling-project.github.io/docling/)
- [Docling Hybrid Chunking](https://docling-project.github.io/docling/_generated/examples/hybrid_chunking/)
- [Qwen3-Embedding-0.6B model card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)
- [Qdrant similarity search](https://qdrant.tech/documentation/search/search/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

## License

MIT for the code in this repository. Third-party libraries and model weights remain subject to their own licenses and terms.
