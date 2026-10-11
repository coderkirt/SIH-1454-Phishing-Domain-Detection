"""ChromaDB store for PHISHEYE phishing knowledge retrieval.

Handles:
- Persistent ChromaDB client initialization
- Collection lifecycle (creation, indexing, resetting)
- Batch upsert of chunked documents and metadata
- Filtered semantic similarity retrieval using local embeddings
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions

from app.chunker import Chunk, chunk_corpus
from app.config import settings
from app.corpus import CorpusDocument, load_corpus

logger = logging.getLogger(__name__)


class EmbeddingVersionMismatchError(RuntimeError):
    """Raised when existing collection embedding model or version does not match active settings."""
    pass


@dataclass
class IngestionDiffReport:
    """Detailed differential report for an incremental ingestion run."""
    added_chunks: List[str] = field(default_factory=list)
    updated_chunks: List[str] = field(default_factory=list)
    unchanged_chunks: int = 0
    deleted_chunks: List[str] = field(default_factory=list)
    total_active_chunks: int = 0
    elapsed_seconds: float = 0.0
    embedding_model: str = ""
    embedding_version: str = ""
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "added_count": len(self.added_chunks),
            "updated_count": len(self.updated_chunks),
            "unchanged_count": self.unchanged_chunks,
            "deleted_count": len(self.deleted_chunks),
            "total_active_chunks": self.total_active_chunks,
            "added_chunks": self.added_chunks,
            "updated_chunks": self.updated_chunks,
            "deleted_chunks": self.deleted_chunks,
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "embedding_model": self.embedding_model,
            "embedding_version": self.embedding_version,
            "timestamp": self.timestamp,
        }

    def summary_markdown(self) -> str:
        return (
            f"### Ingestion Diff Report ({self.timestamp})\n"
            f"- **Added**: {len(self.added_chunks)} chunks\n"
            f"- **Updated**: {len(self.updated_chunks)} chunks\n"
            f"- **Unchanged**: {self.unchanged_chunks} chunks\n"
            f"- **Deleted**: {len(self.deleted_chunks)} stale chunks\n"
            f"- **Total Active**: {self.total_active_chunks} chunks\n"
            f"- **Model**: `{self.embedding_model}` ({self.embedding_version})\n"
            f"- **Elapsed**: {self.elapsed_seconds:.2f}s\n"
        )


_default_client: Optional[ClientAPI] = None
_default_collection: Optional[Collection] = None


def get_embedding_function():
    """Return the embedding function for the Chroma collection."""
    # Uses local ONNX all-MiniLM-L6-v2 (fast, 384-dim, no external API keys required)
    return embedding_functions.DefaultEmbeddingFunction()


def get_client(persist_dir: Optional[Path] = None) -> ClientAPI:
    """Return a persistent ChromaDB client instance."""
    global _default_client
    path = persist_dir or settings.CHROMA_PERSIST_DIR
    path.mkdir(parents=True, exist_ok=True)
    if _default_client is None or persist_dir is not None:
        client = chromadb.PersistentClient(path=str(path))
        if persist_dir is None:
            _default_client = client
        return client
    return _default_client


def get_or_create_collection(
    client: Optional[ClientAPI] = None,
    collection_name: Optional[str] = None,
) -> Collection:
    """Get or create the knowledge collection with distance metric set to cosine."""
    cli = client or get_client()
    name = collection_name or settings.COLLECTION_NAME
    ef = get_embedding_function()
    collection = cli.get_or_create_collection(
        name=name,
        embedding_function=ef,
        metadata={
            "hnsw:space": "cosine",
            "description": "PHISHEYE phishing knowledge base",
            "embedding_model": settings.EMBEDDING_MODEL,
            "embedding_version": settings.EMBEDDING_VERSION,
        },
    )
    return collection


def get_collection(
    client: Optional[ClientAPI] = None,
    collection_name: Optional[str] = None,
) -> Collection:
    """Get an existing knowledge collection, raising an error if it does not exist."""
    cli = client or get_client()
    name = collection_name or settings.COLLECTION_NAME
    ef = get_embedding_function()
    return cli.get_collection(name=name, embedding_function=ef)


def delete_document_chunks(
    doc_id: str,
    client: Optional[ClientAPI] = None,
    collection_name: Optional[str] = None,
) -> int:
    """Delete all indexed chunks for a given doc_id from ChromaDB."""
    collection = get_collection(client=client, collection_name=collection_name)
    existing = collection.get(where={"doc_id": doc_id})
    ids = existing.get("ids", []) if existing else []
    if ids:
        collection.delete(ids=ids)
        logger.info("Deleted %d chunks for doc_id '%s'", len(ids), doc_id)
    return len(ids)


def incremental_ingest_corpus(
    docs: Optional[List[CorpusDocument]] = None,
    client: Optional[ClientAPI] = None,
    collection_name: Optional[str] = None,
    persist_dir: Optional[Path] = None,
    batch_size: int = 50,
    force_reembed: bool = False,
) -> IngestionDiffReport:
    """Incrementally upsert documents into ChromaDB.

    Skips unmodified chunks (by content hash), updates modified chunks,
    inserts new chunks, and removes stale chunks for modified documents.
    """
    cli = client or get_client(persist_dir=persist_dir)
    name = collection_name or settings.COLLECTION_NAME

    collection = get_or_create_collection(client=cli, collection_name=name)

    # Embedding model and version compatibility check
    col_meta = collection.metadata or {}
    indexed_model = col_meta.get("embedding_model")
    indexed_version = col_meta.get("embedding_version")

    if (
        collection.count() > 0
        and indexed_model
        and (indexed_model != settings.EMBEDDING_MODEL or (indexed_version and indexed_version != settings.EMBEDDING_VERSION))
    ):
        if not force_reembed:
            raise EmbeddingVersionMismatchError(
                f"Collection '{name}' was indexed with model '{indexed_model}' ({indexed_version}), "
                f"but current runtime expects '{settings.EMBEDDING_MODEL}' ({settings.EMBEDDING_VERSION}). "
                f"Pass force_reembed=True or run with --reset to re-index."
            )
        else:
            cli.delete_collection(name=name)
            collection = get_or_create_collection(client=cli, collection_name=name)

    t0 = time.perf_counter()

    if docs is None:
        docs = load_corpus()

    new_chunks = chunk_corpus(docs)
    if not new_chunks:
        raise ValueError("No chunks were generated from the corpus")

    new_chunks_map = {c.chunk_id: c for c in new_chunks}
    doc_ids_in_batch = {doc.id for doc in docs}

    # Fetch existing chunk IDs and content hashes
    existing_data = collection.get(include=["metadatas"])
    existing_ids = existing_data.get("ids", []) if existing_data else []
    existing_metas = existing_data.get("metadatas", []) if existing_data else []

    existing_map: Dict[str, Dict[str, Any]] = {}
    for cid, meta in zip(existing_ids, existing_metas):
        existing_map[cid] = meta or {}

    added: List[Chunk] = []
    updated: List[Chunk] = []
    unchanged_count = 0

    for chunk in new_chunks:
        if chunk.chunk_id not in existing_map:
            added.append(chunk)
        else:
            old_hash = existing_map[chunk.chunk_id].get("content_hash", "")
            if not old_hash or old_hash != chunk.content_hash:
                updated.append(chunk)
            else:
                unchanged_count += 1

    # Detect stale chunks to delete
    stale_ids = [
        cid
        for cid, meta in existing_map.items()
        if meta.get("doc_id") in doc_ids_in_batch and cid not in new_chunks_map
    ]

    if stale_ids:
        collection.delete(ids=stale_ids)
        logger.info("Deleted %d stale chunks from collection '%s'", len(stale_ids), name)

    # Upsert added and updated chunks
    to_upsert = added + updated
    for i in range(0, len(to_upsert), batch_size):
        batch = to_upsert[i : i + batch_size]
        collection.upsert(
            ids=[c.chunk_id for c in batch],
            documents=[c.text for c in batch],
            metadatas=[c.metadata for c in batch],
        )

    elapsed = time.perf_counter() - t0
    report = IngestionDiffReport(
        added_chunks=[c.chunk_id for c in added],
        updated_chunks=[c.chunk_id for c in updated],
        unchanged_chunks=unchanged_count,
        deleted_chunks=stale_ids,
        total_active_chunks=collection.count(),
        elapsed_seconds=elapsed,
        embedding_model=settings.EMBEDDING_MODEL,
        embedding_version=settings.EMBEDDING_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    return report


def ingest_corpus(
    docs: Optional[List[CorpusDocument]] = None,
    reset: bool = False,
    persist_dir: Optional[Path] = None,
    collection_name: Optional[str] = None,
    batch_size: int = 50,
    force_reembed: bool = False,
) -> Dict[str, Any]:
    """Index all documents from the corpus into ChromaDB.

    Args:
        docs: Optional list of CorpusDocument. If None, loaded via load_corpus().
        reset: If True, delete and recreate collection before ingesting.
        persist_dir: Optional override for Chroma persistence path.
        collection_name: Optional override for collection name.
        batch_size: Number of chunks per ChromaDB add/upsert call.
        force_reembed: If True, force re-embedding on model mismatch.

    Returns:
        Summary dict containing counts, collection metadata, and diff report.
    """
    client = get_client(persist_dir=persist_dir)
    name = collection_name or settings.COLLECTION_NAME

    if reset:
        try:
            client.delete_collection(name=name)
            logger.info("Deleted existing collection '%s'", name)
        except Exception:
            pass  # Collection did not exist

    diff_report = incremental_ingest_corpus(
        docs=docs,
        client=client,
        collection_name=name,
        persist_dir=persist_dir,
        batch_size=batch_size,
        force_reembed=force_reembed or reset,
    )

    if docs is None:
        docs = load_corpus()
    chunks = chunk_corpus(docs)

    stats = {
        "status": "success",
        "collection_name": name,
        "persist_dir": str(persist_dir or settings.CHROMA_PERSIST_DIR),
        "total_documents": len(docs),
        "total_chunks": len(chunks),
        "indexed_chunks": diff_report.total_active_chunks,
        "categories": {
            cat: sum(1 for c in chunks if c.category == cat)
            for cat in {c.category for c in chunks}
        },
        "diff_report": diff_report.to_dict(),
    }
    return stats


def query_similar(
    query_text: str,
    n_results: int = 5,
    where: Optional[Dict[str, Any]] = None,
    client: Optional[ClientAPI] = None,
    collection_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Perform filtered dense vector search against the Chroma knowledge collection.

    Args:
        query_text: Natural language query or threat indicator text.
        n_results: Maximum number of chunks to return.
        where: Optional ChromaDB metadata filter dictionary.
        client: Optional client override.
        collection_name: Optional collection override.

    Returns:
        List of result dictionaries sorted by similarity score (descending).
    """
    collection = get_or_create_collection(client=client, collection_name=collection_name)
    total_count = collection.count()
    if total_count == 0:
        return []

    fetch_k = min(n_results, total_count)
    query_args: Dict[str, Any] = {
        "query_texts": [query_text],
        "n_results": fetch_k,
    }
    if where:
        query_args["where"] = where

    raw = collection.query(**query_args)

    results: List[Dict[str, Any]] = []
    if not raw or not raw.get("ids") or not raw["ids"][0]:
        return results

    ids = raw["ids"][0]
    docs = raw.get("documents", [[]])[0]
    metas = raw.get("metadatas", [[]])[0]
    distances = raw.get("distances", [[]])[0] if raw.get("distances") else [0.0] * len(ids)

    for chunk_id, doc_text, meta, dist in zip(ids, docs, metas, distances):
        # Convert cosine distance to similarity score in [0.0, 1.0]
        # In cosine space: distance is 1 - cosine_similarity, so similarity = 1 - distance
        sim_score = max(0.0, min(1.0, 1.0 - float(dist)))
        results.append({
            "chunk_id": chunk_id,
            "text": doc_text,
            "metadata": meta,
            "distance": float(dist),
            "score": round(sim_score, 4),
        })

    # Sort descending by score
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def get_collection_stats(
    client: Optional[ClientAPI] = None,
    collection_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Return runtime statistics for the knowledge collection."""
    try:
        col = get_collection(client=client, collection_name=collection_name)
        count = col.count()
    except Exception:
        count = 0
    return {
        "collection_name": collection_name or settings.COLLECTION_NAME,
        "persist_dir": str(settings.CHROMA_PERSIST_DIR),
        "count": count,
    }
