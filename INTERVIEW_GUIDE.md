# MultiLinguaRAG Interview Guide

Use this file to review the project before an interview. Do not memorize wording mechanically; be able to explain the data flow in your own words.

## 🔥 Core story in 30 seconds

MultiLinguaRAG is a compact cross-lingual RAG system for Chinese, Japanese, and English documents. Documents are parsed with Docling, structure-aware chunks are produced with HybridChunker, chunks and queries are embedded with Qwen3-Embedding, and Qdrant retrieves the Top-K most similar chunks. The retrieved evidence is passed to an LLM, which is instructed to answer only from the evidence and cite the original sources.

## 🎯 Technical questions you should be ready for

### 1. What is the difference between RAG and directly asking an LLM?
RAG adds an external retrieval step. The model receives task-relevant evidence at inference time, so the answer can use private or updated knowledge that is not guaranteed to exist in model parameters.

### 2. Why use a multilingual embedding model?
A multilingual embedding model can map semantically similar Chinese, Japanese, and English text into a shared vector space. That enables cross-lingual retrieval, such as a Chinese query retrieving a Japanese source.

### 3. Why does this project use the Qwen3 query prompt only for queries?
Qwen3-Embedding is instruction-aware. Its model documentation recommends query-side prompting while documents are encoded normally. This helps align a search query with candidate documents.

### 4. Why use Docling HybridChunker instead of fixed 500-character splitting?
HybridChunker first respects document structure and then applies tokenizer-aware refinement. The goal is to preserve meaningful sections while keeping each chunk within the embedding model's token budget.

### 5. Why should the chunker use the embedding model's tokenizer?
The embedding model consumes tokens, not characters. Using the same tokenizer makes the chunk-size constraint correspond to the model's actual input representation rather than an approximate character count.

### 6. What is stored in Qdrant?
Each point stores a dense vector plus payload metadata: original chunk text, source filename, page number when available, language label, and section headings.

### 7. Why cosine similarity?
The project normalizes Qwen3 embeddings and uses cosine similarity to rank vectors by semantic direction. It is a common dense retrieval metric and is supported directly by Qdrant.

### 8. What does Top-K mean? What happens if K is too small or too large?
Top-K is the number of retrieved chunks. Too small can reduce recall and miss evidence; too large can inject irrelevant context, increase token cost, and make generation less focused.

### 9. Does RAG eliminate hallucination?
No. RAG can reduce unsupported answers, but failure can still happen if parsing, chunking, retrieval, or generation is wrong. Grounding instructions and citations make errors easier to inspect but do not guarantee factuality.

### 10. What is the most important multilingual experiment for this project?
Cross-lingual retrieval: test zh→ja, ja→en, and en→zh query-document pairs, and report whether the correct source appears in Recall@K.

### 11. Why is there no reranker / BM25 / agent in V1?
V1 intentionally isolates the core RAG pipeline. A simple dense baseline is easier to debug and evaluate. Advanced retrieval should be added only after the baseline is measured.

### 12. How would you improve this project next?
Add a multilingual evaluation set first, then compare dense-only retrieval with hybrid retrieval and reranking. Other extensions include metadata filtering and parent-child retrieval.

## 💼 HR / non-technical questions

### “What did you build?”
I built a multilingual document QA system that lets users ask questions in Chinese, Japanese, or English and retrieve evidence across languages before generating a cited answer.

### “What was the hardest part?”
A strong answer should mention one concrete engineering trade-off you actually tested after running the project—for example chunk size, model download/memory, cross-lingual retrieval quality, or citation metadata preservation.

### “How do you know it works?”
Do not answer “the demo looks good.” Explain that you would build a labeled multilingual retrieval set and measure Recall@K / MRR, then separately evaluate answer groundedness and citation correctness.
