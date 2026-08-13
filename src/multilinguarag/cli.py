from __future__ import annotations

import argparse

from .rag import MultiLinguaRAG


def ingest_main() -> None:
    parser = argparse.ArgumentParser(description="Index documents into MultiLinguaRAG.")
    parser.add_argument("path", help="File or directory to ingest")
    parser.add_argument("--recreate", action="store_true", help="Recreate the Qdrant collection")
    args = parser.parse_args()

    rag = MultiLinguaRAG()
    count = rag.ingest(args.path, recreate=args.recreate)
    print(f"Indexed {count} chunks.")


def query_main() -> None:
    parser = argparse.ArgumentParser(description="Query MultiLinguaRAG.")
    parser.add_argument("question")
    parser.add_argument("--top-k", type=int, default=None)
    args = parser.parse_args()

    rag = MultiLinguaRAG()
    answer, chunks = rag.answer(args.question, k=args.top_k)
    print("\nANSWER\n------")
    print(answer)
    print("\nSOURCES\n-------")
    for idx, chunk in enumerate(chunks, start=1):
        print(f"[S{idx}] {chunk.citation} | score={chunk.score:.4f} | lang={chunk.language}")
