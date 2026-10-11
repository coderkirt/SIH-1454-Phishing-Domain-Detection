"""Synchronize live threat intelligence feeds, hash provenance, and update corpus.

Usage:
    python scripts/sync_feeds.py             # Fetch feeds, deduplicate, and write to corpus/live_feeds/
    python scripts/sync_feeds.py --ingest    # Fetch feeds and re-index ChromaDB automatically
    python scripts/sync_feeds.py --dry-run   # Preview feeds and hashes without writing files
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Add rag_service root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chroma_store import ingest_corpus
from app.config import settings
from app.connectors import CertInConnector, CisaConnector, UrlhausConnector
from app.corpus import CorpusDocument, load_corpus
from app.provenance import FeedDeduplicator, compute_source_hash, get_current_iso_timestamp


CONNECTORS = [
    CisaConnector(),
    CertInConnector(),
    UrlhausConnector(),
]


def serialize_to_markdown(doc: CorpusDocument) -> str:
    """Format a CorpusDocument back into standardized Markdown with front-matter."""
    brands_str = f"[{', '.join(doc.brands)}]" if doc.brands else "[]"
    tags_str = f"[{', '.join(doc.threat_tags)}]" if doc.threat_tags else "[]"
    channels_str = f"[{', '.join(doc.channels)}]" if doc.channels else "[]"
    mitre_str = f"[{', '.join(doc.mitre)}]" if doc.mitre else "[]"

    front_matter = [
        "---",
        f"id: {doc.id}",
        f"title: {doc.title}",
        f"category: {doc.category}",
        f"source: {doc.source}",
        f"source_url: {doc.source_url}",
        f"last_verified: {doc.last_verified}",
        f"language: {doc.language}",
        f"region: {doc.region}",
        f"channels: {channels_str}",
        f"brands: {brands_str}",
        f"threat_tags: {tags_str}",
        f"mitre: {mitre_str}",
        f"fetched_at: {doc.fetched_at}",
        f"source_hash: {doc.source_hash}",
        f"license: {doc.license}",
        f"version: {doc.version}",
        f"summary: {doc.summary}",
        "---",
        "",
        doc.body.strip(),
        "",
    ]
    return "\n".join(front_matter)


async def sync_all_feeds(dry_run: bool = False, auto_ingest: bool = False) -> int:
    print("==================================================")
    print("  PHISHEYE Live Threat Intelligence Feed Sync")
    print("==================================================")
    print(f"Target directory: {settings.CORPUS_DIR / 'live_feeds'}")
    print(f"Registered feeds: {len(CONNECTORS)}")
    print(f"Dry run mode:     {dry_run}\n")

    live_dir = settings.CORPUS_DIR / "live_feeds"
    live_dir.mkdir(parents=True, exist_ok=True)

    dedup = FeedDeduplicator(similarity_threshold=0.85)

    # First, register all existing corpus documents into deduplicator
    existing_docs = load_corpus()
    for d in existing_docs:
        dedup.is_duplicate(d.id, d.body)
    print(f"Loaded {len(existing_docs)} existing corpus docs into deduplication index.\n")

    fetched_count = 0
    new_count = 0
    duplicate_count = 0

    for connector in CONNECTORS:
        print(f"[*] Polling feed: {connector.name} ({connector.source_id})...")
        try:
            docs = await connector.fetch_feed()
            print(f"    Retrieved {len(docs)} documents from upstream.")

            for doc in docs:
                fetched_count += 1
                is_dup, canonical_id, sim = dedup.is_duplicate(doc.id, doc.body)

                if is_dup:
                    print(f"    [SKIP] Near-duplicate of '{canonical_id}' (similarity: {sim:.2f}): {doc.id}")
                    duplicate_count += 1
                    continue

                new_count += 1
                print(f"    [NEW]  {doc.id} ({doc.title[:50]}...)")
                print(f"           Hash: {doc.source_hash[:16]}... | License: {doc.license}")

                if not dry_run:
                    file_path = live_dir / f"{doc.id}.md"
                    content = serialize_to_markdown(doc)
                    file_path.write_text(content, encoding="utf-8")

        except Exception as exc:
            print(f"    [ERROR] Failed syncing feed {connector.name}: {exc}")

    print("\n--------------------------------------------------")
    print(f"Sync Results: {fetched_count} fetched, {new_count} new, {duplicate_count} skipped (duplicates)")

    if auto_ingest and not dry_run:
        print("\n[*] Updating ChromaDB vector store with refreshed corpus...")
        refreshed_docs = load_corpus()
        stats = ingest_corpus(docs=refreshed_docs, reset=False)
        print(f"    ChromaDB updated! Total indexed chunks: {stats['indexed_chunks']}")

    print("==================================================")
    print("  Feed Synchronization Complete!")
    print("==================================================")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize live threat intelligence feeds")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and verify without writing files")
    parser.add_argument("--ingest", action="store_true", help="Automatically re-index ChromaDB after sync")
    args = parser.parse_args()

    return asyncio.run(sync_all_feeds(dry_run=args.dry_run, auto_ingest=args.ingest))


if __name__ == "__main__":
    raise SystemExit(main())
