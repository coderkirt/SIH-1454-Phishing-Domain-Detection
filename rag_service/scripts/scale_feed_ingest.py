"""Scale ingestion pipeline for populating 10,000+ threat feed indicator chunks into ChromaDB.

Usage:
    python scripts/scale_feed_ingest.py --count 10000 --batch-size 250
    python scripts/scale_feed_ingest.py --count 5000 --collection feed_intelligence
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Add rag_service root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.feed_ingestion import (
    batch_upsert_chunks,
    build_chunk_from_indicator,
    generate_synthetic_feed_records,
)
from app.config import settings


def main() -> int:
    parser = argparse.ArgumentParser(description="PHISHEYE High-Scale Feed Ingestion Pipeline")
    parser.add_argument(
        "--count",
        type=int,
        default=10000,
        help="Number of threat feed indicator chunks to generate and index (default: 10000)",
    )
    parser.add_argument(
        "--collection",
        default="feed_intelligence",
        help="Target ChromaDB collection name (default: feed_intelligence)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=250,
        help="Batch size per Chroma upsert operation (default: 250)",
    )
    args = parser.parse_args()

    print("==================================================")
    print("  PHISHEYE High-Scale Threat Feed Ingestion Engine")
    print("==================================================")
    print(f"Target Chunk Count: {args.count}")
    print(f"Target Collection:  {args.collection}")
    print(f"Batch Size:         {args.batch_size}")
    print(f"Embedding Model:    {settings.EMBEDDING_MODEL} ({settings.EMBEDDING_VERSION})\n")

    t_start = time.perf_counter()

    # Step 1: Synthesize threat feed indicators
    print(f"[1/3] Generating {args.count} structured threat feed indicators...")
    indicators = generate_synthetic_feed_records(count=args.count)
    print(f"      Generated {len(indicators)} indicators across URLhaus, OpenPhish, PhishTank, CISA, CERT-In.")

    # Step 2: Format into Chunks with full provenance
    print("\n[2/3] Constructing typed Chunks with character offsets and SHA-256 provenance...")
    chunks = [build_chunk_from_indicator(ind, chunk_index=i) for i, ind in enumerate(indicators)]
    print(f"      Ready to index {len(chunks)} chunks.")

    # Step 3: Batch upsert into Chroma
    print(f"\n[3/3] Streaming batch upserts into Chroma collection '{args.collection}'...")

    def progress_callback(done: int, total: int):
        pct = (done / total) * 100
        print(f"      Progress: {done}/{total} ({pct:.1f}%) chunks indexed...", end="\r")

    stats = batch_upsert_chunks(
        chunks=chunks,
        collection_name=args.collection,
        batch_size=args.batch_size,
        progress_callback=progress_callback,
    )
    print()  # newline after carriage return

    total_elapsed = time.perf_counter() - t_start
    print("\n==================================================")
    print("  High-Scale Ingestion Complete!")
    print(f"  Upserted Chunks:   {stats['upserted_chunks']}")
    print(f"  Collection Total:  {stats['collection_total']}")
    print(f"  Throughput:        {stats['rate_chunks_per_sec']} chunks/sec")
    print(f"  Total Time:        {total_elapsed:.2f}s")
    print("==================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
