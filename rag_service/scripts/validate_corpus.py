"""Validate the curated corpus and print coverage statistics.

Usage: python scripts/validate_corpus.py
Exits non-zero if any document fails validation.
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.corpus import CorpusError, load_corpus  # noqa: E402


def main() -> int:
    try:
        docs = load_corpus()
    except CorpusError as exc:
        print(f"CORPUS INVALID: {exc}")
        return 1

    total_words = sum(d.word_count for d in docs)
    by_category = Counter(d.category for d in docs)
    by_channel = Counter(ch for d in docs for ch in d.channels)
    by_tag = Counter(tag for d in docs for tag in d.threat_tags)
    by_brand = Counter(b for d in docs for b in d.brands)

    print(f"Corpus OK: {len(docs)} documents, {total_words} words\n")
    print("By category:")
    for cat, n in sorted(by_category.items()):
        print(f"  {cat:16s} {n}")
    print("\nChannels (docs per channel):")
    for ch, n in by_channel.most_common():
        print(f"  {ch:10s} {n}")
    print("\nThreat-tag coverage (docs per tag):")
    for tag, n in by_tag.most_common():
        print(f"  {tag:24s} {n}")
    if by_brand:
        print("\nBrand coverage (docs per brand):")
        for brand, n in by_brand.most_common():
            print(f"  {brand:12s} {n}")
    uncovered = [
        d.id for d in docs if not d.threat_tags
    ]
    if uncovered:
        print(f"\nWARNING: documents without threat_tags: {uncovered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
