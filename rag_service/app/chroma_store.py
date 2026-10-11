"""ChromaDB store for PHISHEYE phishing knowledge retrieval.

Handles:
- Persistent ChromaDB client initialization
- Collection lifecycle (creation, indexing, resetting)
- Batch upsert of chunked documents and metadata
- Filtered semantic similarity retrieval using local embeddings
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions

from app.chunker import Chunk, chunk_corpus
from app.config import settings
from app.corpus import CorpusDocument, load_corpus

logger = logging.getLogger(__name__)


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
        metadata={"hnsw:space": "cosine", "description": "PHISHEYE phishing knowledge base"},
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


def ingest_corpus(
    docs: Optional[List[CorpusDocument]] = None,
    reset: bool = False,
    persist_dir: Optional[Path] = None,
    collection_name: Optional[str] = None,
    batch_size: int = 50,
) -> Dict[str, Any]:
    """Index all documents from the corpus into ChromaDB.

    Args:
        docs: Optional list of CorpusDocument. If None, loaded via load_corpus().
        reset: If True, delete and recreate collection before ingesting.
        persist_dir: Optional override for Chroma persistence path.
        collection_name: Optional override for collection name.
        batch_size: Number of chunks per ChromaDB add/upsert call.

    Returns:
        Summary dict containing counts and collection metadata.
    """
    client = get_client(persist_dir=persist_dir)
    name = collection_name or settings.COLLECTION_NAME

    if reset:
        try:
            client.delete_collection(name=name)
            logger.info("Deleted existing collection '%s'", name)
        except Exception:
            pass  # Collection did not exist

    collection = get_or_create_collection(client=client, collection_name=name)

    if docs is None:
        docs = load_corpus()

    chunks = chunk_corpus(docs)
    if not chunks:
        raise ValueError("No chunks were generated from the corpus")

    # Ingest in batches
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        ids = [c.chunk_id for c in batch]
        documents = [c.text for c in batch]
        metadatas = [c.metadata for c in batch]

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

    stats = {
        "status": "success",
        "collection_name": name,
        "persist_dir": str(persist_dir or settings.CHROMA_PERSIST_DIR),
        "total_documents": len(docs),
        "total_chunks": len(chunks),
        "indexed_chunks": collection.count(),
        "categories": {
            cat: sum(1 for c in chunks if c.category == cat)
            for cat in {c.category for c in chunks}
        },
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
