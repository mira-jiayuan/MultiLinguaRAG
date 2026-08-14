# MultiLinguaRAG Interview Guide

## 🔥 Core story in 30 seconds

MultiLinguaRAG is a cross-lingual RAG system in which the **knowledge-source language, query language, and answer language are independent**. Documents are parsed with Docling, chunked with HybridChunker, embedded with Qwen3-Embedding, and indexed in Qdrant. At query time, the system retrieves the most semantically relevant evidence across Chinese, Japanese, and English. The user can then choose a target output language—for example, English source documents, a Chinese question, and a Japanese grounded answer with citations back to the original English sources.

## 🎯 Technical questions

### 1. What is the main design idea of this project?
The project decouples three language roles: source language, query language, and answer language. Retrieval finds semantically relevant evidence regardless of language, while generation separately controls the final response language.

### 2. How can a Chinese query retrieve an English or Japanese document?
Qwen3-Embedding maps semantically related multilingual text into a shared vector space. The Chinese query vector can therefore be close to an English or Japanese document vector when they express the same meaning.

### 3. Why not translate all documents into Chinese or Japanese before indexing?
Pre-translating the entire corpus increases preprocessing cost, creates translated duplicates, and may introduce translation errors before retrieval. A multilingual embedding model allows retrieval from the original sources while preserving provenance.

### 4. How can a Chinese query produce a Japanese answer?
Retrieval and generation are separate stages. The Chinese query is used to retrieve evidence first. The generation prompt then explicitly instructs the LLM to express the grounded answer in Japanese.

### 5. Does selecting Japanese output change the retrieval results?
Not in V1. Retrieval is driven by the query embedding and semantic similarity. The target answer language is applied after retrieval, during generation. This clean separation makes the pipeline easier to reason about and evaluate.

### 6. How do citations work when the output language differs from the source language?
Each retrieved Qdrant point retains original metadata such as source filename, page number, language, and section. The generated answer cites [S1], [S2], etc., which map back to the original source evidence—not to a translated copy.

### 7. Why is this useful in a real workflow?
One example is multilingual teaching assistance: source materials may be English research papers, the user may formulate questions more efficiently in Chinese, while the final teaching notes or explanations need to be delivered in Japanese.

### 8. What is the difference between cross-lingual retrieval and multilingual generation?
Cross-lingual retrieval means the query and retrieved document can be in different languages. Multilingual generation means the output can be produced in a selected target language. MultiLinguaRAG supports both.

### 9. Why use Docling HybridChunker instead of fixed-length character splitting?
HybridChunker respects document structure and applies tokenizer-aware refinement, helping preserve meaningful sections while keeping chunks within the embedding model's input budget.

### 10. Why should chunking use the embedding model's tokenizer?
The embedding model consumes tokens, not characters. Using the same tokenizer makes chunk-size constraints correspond to the model's real input representation.

### 11. What is stored in Qdrant?
Each point stores a dense vector plus payload metadata including the original chunk text, source filename, page number when available, source language, and section headings.

### 12. What is Top-K?
Top-K is the number of retrieved chunks. A K that is too small can miss evidence; a K that is too large can introduce noise, increase context cost, and reduce generation focus.

### 13. Does RAG eliminate hallucination?
No. RAG can reduce unsupported answers, but parsing, chunking, retrieval, or generation can still fail. Citations and visible retrieved evidence make those failures easier to inspect.

### 14. How would you evaluate the project?
Separate retrieval evaluation from generation evaluation. For retrieval, use labeled cross-lingual query-source pairs and report Recall@K and MRR. For generation, evaluate groundedness, citation correctness, terminology preservation, and semantic consistency across target languages.

### 15. Why does V1 not include BM25, reranking, or agents?
V1 intentionally isolates the core Indexing → Retrieval → Generation pipeline. A simple dense baseline is easier to debug, evaluate, and explain before adding more advanced retrieval components.

## 💼 HR / non-technical questions

### “What did you build?”
I built a multilingual knowledge assistant that can use source documents in one language, accept a question in another language, and generate a grounded answer in a third language while preserving citations to the original evidence.

### “What problem does it solve?”
It reduces friction in multilingual knowledge work. For example, a user can read and index English academic sources, ask questions in Chinese, and directly obtain Japanese material for teaching or communication without manually translating the whole corpus first.

### “What is the most distinctive feature?”
The source language, query language, and answer language are independently configurable rather than being forced to match.

### “How do you know it works?”
I would evaluate cross-lingual retrieval with labeled query-source pairs using Recall@K/MRR, then evaluate generated answers separately for groundedness, citation correctness, and cross-language semantic consistency.
