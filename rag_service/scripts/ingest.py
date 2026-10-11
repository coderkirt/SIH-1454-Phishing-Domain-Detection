"""Ingest the PHISHEYE phishing knowledge corpus into ChromaDB.

Usage:
    python scripts/ingest.py              # Ingest or update chunks
    python scripts/ingest.py --reset      # Drop existing collection and re-index from scratch
    python scripts/ingest.py --verify     # Run verification test queries against the indexed collection
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Add rag_service root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chroma_store import get_collection_stats, ingest_corpus, query_similar
from app.config import settings
from app.corpus import CorpusError, load_corpus


VERIFICATION_QUERIES = [
    {
        "query": "Your SBI account will be blocked today due to pending KYC. Click link to verify.",
        "expected_brand": "sbi",
        "description": "Banking KYC lure",
    },
    {
        "query": "PayPal: You sent a payment of $450 to an unrecognized seller. Call support to dispute.",
        "expected_brand": "paypal",
        "description": "PayPal fake invoice / refund lure",
    },
    {
        "query": "Scan this QR code with your phone camera to validate your courier delivery package.",
        "expected_category": "playbook",
        "description": "Quishing / parcel scam lure",
    },
    {
        "query": "Income tax refund of Rs 15,400 approved. Submit bank account details on refund portal.",
        "expected_brand": "incometax",
        "description": "Government tax refund phishing",
    },
]


def run_verification() -> bool:
    """Run verification queries against the indexed collection to check retrieval quality."""
    print("\n--- Running Ingestion Verification Queries ---")
    all_ok = True

    for item in VERIFICATION_QUERIES:
        q = item["query"]
        t0 = time.perf_counter()
        results = query_similar(query_text=q, n_results=3)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        print(f"\n[Test] {item['description']}")
        print(f"  Query: \"{q[:75]}...\"")
        print(f"  Latency: {elapsed_ms:.1f}ms | Matches found: {len(results)}")

        if not results:
            print("  FAIL: No results returned")
            all_ok = False
            continue

        top = results[0]
        meta = top["metadata"]
        print(f"  Top Match: {top['chunk_id']} (Score: {top['score']:.4f})")
        print(f"  Doc: \"{meta.get('doc_title')}\" [{meta.get('category')}]")
        print(f"  Section: {meta.get('section_title')}")

        if top["score"] < 0.35:
            print(f"  WARNING: Top match score {top['score']:.4f} is lower than expected threshold (0.35)")

    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest phishing corpus into ChromaDB")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate the ChromaDB collection before ingesting",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run semantic test queries after ingestion to verify index health",
    )
    args = parser.parse_args()

    print("==================================================")
    print("  PHISHEYE RAG Knowledge Ingestion Pipeline")
    print("==================================================")
    print(f"Corpus directory:  {settings.CORPUS_DIR}")
    print(f"Chroma directory:  {settings.CHROMA_PERSIST_DIR}")
    print(f"Collection name:   {settings.COLLECTION_NAME}")
    print(f"Embedding model:   {settings.EMBEDDING_MODEL}")
    print(f"Reset mode:        {args.reset}\n")

    t_start = time.perf_counter()

    try:
        print("[1/3] Loading and validating markdown knowledge corpus...")
        docs = load_corpus()
        print(f"      Loaded {len(docs)} documents successfully.")
    except CorpusError as err:
        print(f"ERROR: Corpus validation failed: {err}")
        return 1

    try:
        print("[2/3] Chunking and indexing into ChromaDB...")
        stats = ingest_corpus(docs=docs, reset=args.reset)
        elapsed = time.perf_counter() - t_start
        print(f"      Ingested {stats['total_chunks']} chunks from {stats['total_documents']} documents in {elapsed:.2f}s")
        print(f"      Collection total count: {stats['indexed_chunks']} chunks")
        if "diff_report" in stats:
            dr = stats["diff_report"]
            print(f"      Diff Report: +{dr['added_count']} added | ~{dr['updated_count']} updated | ={dr['unchanged_count']} unchanged | -{dr['deleted_count']} deleted")
        print("\nChunks by category:")
        for cat, cnt in sorted(stats["categories"].items()):
            print(f"  - {cat:16s}: {cnt:3d} chunks")
    except Exception as exc:
        print(f"ERROR: Ingestion failed: {exc}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n[3/3] Collection health status:")
    col_stats = get_collection_stats()
    print(f"      Persist dir: {col_stats['persist_dir']}")
    print(f"      Chunk count: {col_stats['count']}")

    if args.verify or True:  # Run quick verification by default
        ok = run_verification()
        if not ok:
            print("\nWARNING: Some verification queries did not return results.")

    print("\n==================================================")
    print("  Ingestion into ChromaDB Complete! (Step 6 OK)")
    print("==================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
