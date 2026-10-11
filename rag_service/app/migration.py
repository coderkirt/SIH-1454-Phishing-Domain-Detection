"""Migration exporter for migrating PHISHEYE knowledge vectors from ChromaDB to Qdrant or PostgreSQL + pgvector.

Designed for production scale inflection points (>500,000 chunks) where a distributed
vector database (Qdrant cluster) or unified relational vector engine (PostgreSQL + pgvector)
is required.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.chroma_store import get_collection
from app.config import settings

logger = logging.getLogger(__name__)


class VectorMigrationExporter:
    """Exports indexed embeddings and metadata from ChromaDB to external vector stores."""

    def __init__(self, collection_name: Optional[str] = None, client: Optional[Any] = None):
        self.collection_name = collection_name or settings.COLLECTION_NAME
        self.collection = get_collection(client=client, collection_name=self.collection_name)

    def fetch_all_records(self) -> Dict[str, Any]:
        """Fetch all IDs, embeddings, documents, and metadatas from the Chroma collection."""
        data = self.collection.get(include=["embeddings", "documents", "metadatas"])
        return {
            "ids": data.get("ids", []),
            "embeddings": data.get("embeddings", []),
            "documents": data.get("documents", []),
            "metadatas": data.get("metadatas", []),
            "count": len(data.get("ids", [])),
        }

    def export_to_qdrant(self, output_path: Path) -> Dict[str, Any]:
        """Export all records to Qdrant PointStruct JSONL format and emit collection schema.

        Qdrant schema:
        - Points: {"id": "<uuid or int or str>", "vector": [...], "payload": {...}}
        - Collection config: vectors config with size 384 and distance 'Cosine'
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        records = self.fetch_all_records()
        points_exported = 0

        # Write Qdrant points JSONL
        with open(output_path, "w", encoding="utf-8") as f:
            for chunk_id, vec, doc_text, meta in zip(
                records["ids"],
                records["embeddings"],
                records["documents"],
                records["metadatas"],
            ):
                payload = dict(meta or {})
                payload["document_text"] = doc_text
                payload["chunk_id"] = chunk_id

                vec_list = vec.tolist() if hasattr(vec, "tolist") else (list(vec) if vec is not None else [])
                point = {
                    "id": chunk_id,
                    "vector": vec_list,
                    "payload": payload,
                }
                f.write(json.dumps(point) + "\n")
                points_exported += 1

        # Write Qdrant schema manifest
        schema_file = output_path.parent / f"{output_path.stem}_schema.json"
        schema_data = {
            "collection_name": self.collection_name,
            "vectors_config": {
                "size": 384,
                "distance": "Cosine",
                "on_disk": True,
            },
            "optimizers_config": {
                "indexing_threshold": 20000,
            },
            "hnsw_config": {
                "m": 16,
                "ef_construct": 100,
                "full_scan_threshold": 1000,
            },
            "total_points": points_exported,
        }
        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(schema_data, f, indent=2)

        return {
            "target": "qdrant",
            "points_file": str(output_path),
            "schema_file": str(schema_file),
            "total_points": points_exported,
            "embedding_dimension": 384,
        }

    def export_to_pgvector(self, output_path: Path, table_name: str = "phishing_knowledge_vectors") -> Dict[str, Any]:
        """Export all records to a self-contained PostgreSQL + pgvector SQL migration script.

        Emits:
        - CREATE EXTENSION IF NOT EXISTS vector;
        - CREATE TABLE ... with vector(384) column and JSONB metadata
        - HNSW cosine index for sub-millisecond approximate nearest neighbor retrieval
        - Batch INSERT statements
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        records = self.fetch_all_records()
        rows_exported = 0

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("-- ==========================================================\n")
            f.write(f"-- PHISHEYE Knowledge Corpus pgvector Migration Script\n")
            f.write(f"-- Target Table: {table_name}\n")
            f.write("-- ==========================================================\n\n")
            f.write("CREATE EXTENSION IF NOT EXISTS vector;\n\n")
            f.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
            f.write("    chunk_id VARCHAR(255) PRIMARY KEY,\n")
            f.write("    doc_id VARCHAR(255) NOT NULL,\n")
            f.write("    category VARCHAR(64) NOT NULL,\n")
            f.write("    document TEXT NOT NULL,\n")
            f.write("    embedding vector(384) NOT NULL,\n")
            f.write("    metadata JSONB NOT NULL,\n")
            f.write("    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n")
            f.write(");\n\n")
            f.write(f"CREATE INDEX IF NOT EXISTS {table_name}_embedding_hnsw_idx\n")
            f.write(f"    ON {table_name} USING hnsw (embedding vector_cosine_ops)\n")
            f.write("    WITH (m = 16, ef_construction = 64);\n\n")
            f.write(f"CREATE INDEX IF NOT EXISTS {table_name}_metadata_gin_idx\n")
            f.write(f"    ON {table_name} USING gin (metadata);\n\n")

            for chunk_id, vec, doc_text, meta in zip(
                records["ids"],
                records["embeddings"],
                records["documents"],
                records["metadatas"],
            ):
                meta_dict = meta or {}
                doc_id = meta_dict.get("doc_id", "unknown").replace("'", "''")
                category = meta_dict.get("category", "unknown").replace("'", "''")
                escaped_text = doc_text.replace("'", "''")
                escaped_meta = json.dumps(meta_dict).replace("'", "''")
                vec_list = vec.tolist() if hasattr(vec, "tolist") else (list(vec) if vec is not None else [])
                vec_str = "[" + ",".join(f"{float(x):.6f}" for x in vec_list) + "]"

                sql = (
                    f"INSERT INTO {table_name} (chunk_id, doc_id, category, document, embedding, metadata)\n"
                    f"VALUES ('{chunk_id}', '{doc_id}', '{category}', '{escaped_text}', '{vec_str}', '{escaped_meta}')\n"
                    f"ON CONFLICT (chunk_id) DO UPDATE SET\n"
                    f"    document = EXCLUDED.document,\n"
                    f"    embedding = EXCLUDED.embedding,\n"
                    f"    metadata = EXCLUDED.metadata;\n\n"
                )
                f.write(sql)
                rows_exported += 1

        return {
            "target": "pgvector",
            "sql_file": str(output_path),
            "table_name": table_name,
            "total_rows": rows_exported,
            "embedding_dimension": 384,
            "index_type": "HNSW (cosine)",
        }
