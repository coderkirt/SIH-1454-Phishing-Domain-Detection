"""Interactive test script for hybrid retrieval with RRF.

Usage:
    python scripts/test_retrieval.py --query "Your SBI account is locked" --brand sbi
    python scripts/test_retrieval.py --query "PayPal invoice paid call support" --brand paypal
    python scripts/test_retrieval.py --query "Scan QR code to pay parcel fee" --channel qr
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retrieval import get_retriever


def main() -> int:
    parser = argparse.ArgumentParser(description="Test filtered hybrid retrieval with RRF")
    parser.add_argument("--query", "-q", type=str, required=True, help="Search query text")
    parser.add_argument("--brand", "-b", type=str, default="", help="Detected brand (e.g., sbi, paypal)")
    parser.add_argument("--tag", "-t", type=str, default="", help="Threat tag (e.g., urgency_detected)")
    parser.add_argument("--category", "-c", type=str, default="", help="Category (e.g., playbook, brand_guidance)")
    parser.add_argument("--channel", type=str, default="", help="Delivery channel (e.g., sms, email, qr)")
    parser.add_argument("--k", type=int, default=3, help="Number of results to return")
    parser.add_argument("--hard", action="store_true", help="Apply hard filtering instead of soft boosting")
    args = parser.parse_args()

    brands = [args.brand] if args.brand else []
    threat_tags = [args.tag] if args.tag else []
    categories = [args.category] if args.category else []
    channels = [args.channel] if args.channel else []

    print("==================================================")
    print("  PHISHEYE Hybrid Retrieval (Dense + BM25 + RRF)")
    print("==================================================")
    print(f"Query:       \"{args.query}\"")
    print(f"Brand filter: {brands or 'None'}")
    print(f"Tag filter:   {threat_tags or 'None'}")
    print(f"Hard filter:  {args.hard}")
    print(f"Top-K:        {args.k}\n")

    retriever = get_retriever()

    t0 = time.perf_counter()
    results = retriever.retrieve(
        query=args.query,
        brands=brands,
        threat_tags=threat_tags,
        categories=categories,
        channels=channels,
        top_k=args.k,
        hard_filter=args.hard,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000

    print(f"Found {len(results)} matches in {elapsed_ms:.1f}ms:\n")

    for i, r in enumerate(results, 1):
        print(f"[{i}] {r.doc_title} — {r.section_title} ({r.category})")
        print(f"    RRF Score:    {r.score:.6f}")
        print(f"    Dense Rank:   {r.dense_rank or '-'} (score: {r.dense_score})")
        print(f"    Sparse Rank:  {r.sparse_rank or '-'} (score: {r.sparse_score})")
        print(f"    Signals:      {r.matched_signals or 'none'}")
        print(f"    Source:       {r.source} <{r.source_url}>")
        print(f"    Snippet:      {r.text[:120].strip()}...")
        print("-" * 50)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
