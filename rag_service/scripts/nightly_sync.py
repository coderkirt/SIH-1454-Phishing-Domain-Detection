"""Nightly knowledge synchronization, differential ingestion, and backup maintenance job.

Usage:
    python scripts/nightly_sync.py
    python scripts/nightly_sync.py --force-reembed
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add rag_service root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.backup import ChromaBackupManager
from app.chroma_store import get_collection_stats, incremental_ingest_corpus
from app.config import settings
from app.corpus import load_corpus


def main() -> int:
    parser = argparse.ArgumentParser(description="PHISHEYE Nightly Knowledge Sync & Backup Job")
    parser.add_argument(
        "--force-reembed",
        action="store_true",
        help="Force re-embedding of all documents regardless of version match",
    )
    args = parser.parse_args()

    t_start = time.perf_counter()
    now = datetime.now(timezone.utc)
    ts_str = now.strftime("%Y%m%d_%H%M%S")

    print("==================================================")
    print("  PHISHEYE Nightly Knowledge Sync & Backup Pipeline")
    print("==================================================")
    print(f"Timestamp:         {now.isoformat()}")
    print(f"Collection:        {settings.COLLECTION_NAME}")
    print(f"Embedding model:   {settings.EMBEDDING_MODEL} ({settings.EMBEDDING_VERSION})")
    print(f"Backup retention:  {settings.BACKUP_RETENTION_DAYS} days\n")

    # Step 1: Incremental Ingestion
    print("[1/4] Scanning corpus and executing incremental upsert...")
    docs = load_corpus()
    print(f"      Loaded {len(docs)} documents from {settings.CORPUS_DIR}")

    diff = incremental_ingest_corpus(docs=docs, force_reembed=args.force_reembed)
    print(f"      Added:     {len(diff.added_chunks)} chunks")
    print(f"      Updated:   {len(diff.updated_chunks)} chunks")
    print(f"      Unchanged: {diff.unchanged_chunks} chunks")
    print(f"      Deleted:   {len(diff.deleted_chunks)} stale chunks")
    print(f"      Total:     {diff.total_active_chunks} active chunks in collection")

    # Step 2: Write Diff Report
    reports_dir = settings.DATA_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_json = reports_dir / f"diff_report_{ts_str}.json"
    report_md = reports_dir / f"diff_report_{ts_str}.md"

    print(f"\n[2/4] Saving differential audit reports to {reports_dir.name}/...")
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(diff.to_dict(), f, indent=2)
    with open(report_md, "w", encoding="utf-8") as f:
        f.write(diff.summary_markdown())
    print(f"      Saved {report_json.name} and {report_md.name}")

    # Step 3: Create Automated Backup Snapshot
    backup_mgr = ChromaBackupManager()
    print(f"\n[3/4] Creating point-in-time backup snapshot...")
    manifest = backup_mgr.create_backup(tag="nightly", chunk_count=diff.total_active_chunks)
    print(f"      Created archive: {manifest.archive_filename}")
    print(f"      SHA-256 Checksum: {manifest.sha256_checksum[:16]}... ({manifest.size_bytes} bytes)")

    # Step 4: Enforce 30-day Retention Policy
    print(f"\n[4/4] Enforcing backup retention ({settings.BACKUP_RETENTION_DAYS} days)...")
    prune_res = backup_mgr.prune_backups(keep_min=3)
    print(f"      Pruned:   {prune_res['pruned_count']} expired backups")
    print(f"      Retained: {prune_res['retained_count']} valid backups")

    elapsed = time.perf_counter() - t_start
    print("\n==================================================")
    print(f"  Nightly Sync Completed Successfully in {elapsed:.2f}s!")
    print("==================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
