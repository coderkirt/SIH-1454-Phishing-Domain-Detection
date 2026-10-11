"""CLI tool to export ChromaDB embeddings to Qdrant or PostgreSQL + pgvector.

Usage:
    python scripts/migrate_vectors.py --target qdrant --output data/migrations/qdrant_export.jsonl
    python scripts/migrate_vectors.py --target pgvector --output data/migrations/pgvector_export.sql
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add rag_service root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.migration import VectorMigrationExporter


def main() -> int:
    parser = argparse.ArgumentParser(description="Export ChromaDB knowledge vectors for migration")
    parser.add_argument(
        "--target",
        choices=["qdrant", "pgvector", "all"],
        default="all",
        help="Migration target database format",
    )
    parser.add_argument(
        "--output-dir",
        default="data/migrations",
        help="Directory to save migration artifacts",
    )
    args = parser.parse_args()

    out_dir = settings.BASE_DIR / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print("  PHISHEYE Knowledge Vector Migration Pipeline")
    print("==================================================")
    print(f"Source Collection: {settings.COLLECTION_NAME}")
    print(f"Target format:     {args.target}")
    print(f"Output directory:  {out_dir}\n")

    try:
        exporter = VectorMigrationExporter()
    except Exception as exc:
        print(f"ERROR: Failed to connect to ChromaDB: {exc}")
        return 1

    if args.target in ("qdrant", "all"):
        qdrant_file = out_dir / "qdrant_points.jsonl"
        print(f"[1/2] Exporting to Qdrant points ({qdrant_file.name})...")
        res = exporter.export_to_qdrant(qdrant_file)
        print(f"      Success! Exported {res['total_points']} points.")
        print(f"      Schema generated: {res['schema_file']}")

    if args.target in ("pgvector", "all"):
        pgvector_file = out_dir / "pgvector_dump.sql"
        print(f"\n[2/2] Exporting to PostgreSQL + pgvector ({pgvector_file.name})...")
        res = exporter.export_to_pgvector(pgvector_file)
        print(f"      Success! Exported {res['total_rows']} SQL insert statements.")
        print(f"      Target table: {res['table_name']} with HNSW cosine index.")

    print("\n==================================================")
    print("  Vector Migration Export Completed Successfully!")
    print("==================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
