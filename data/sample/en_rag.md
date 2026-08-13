# Multilingual Retrieval

A multilingual embedding model maps semantically related text from different languages into a shared vector space. In a cross-lingual RAG system, a query written in one language can therefore retrieve evidence written in another language.

## Top-K retrieval

Top-K controls how many candidate chunks are passed from retrieval to generation. A very small K may miss useful evidence, while a very large K can introduce noise and consume more context tokens.
