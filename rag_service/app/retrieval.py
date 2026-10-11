"""Hybrid retrieval engine combining dense vector search and sparse BM25 with RRF.

Implements:
- Dense semantic vector search via ChromaDB (all-MiniLM-L6-v2)
- Sparse lexical search via BM25Okapi
- Reciprocal Rank Fusion (RRF) rank-merging algorithm
- Pre-filtering and signal boosting for detected brands, threat tags, and categories
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set

from app.bm25 import BM25Index
from app.chroma_store import get_or_create_collection, query_similar
from app.chunker import Chunk, chunk_corpus
from app.config import settings
from app.corpus import load_corpus

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    chunk_id: str
    doc_id: str
    doc_title: str
    section_title: str
    category: str
    source: str
    source_url: str
    last_verified: str
    text: str
    score: float
    dense_rank: Optional[int] = None
    sparse_rank: Optional[int] = None
    dense_score: Optional[float] = None
    sparse_score: Optional[float] = None
    matched_signals: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "doc_title": self.doc_title,
            "section_title": self.section_title,
            "category": self.category,
            "source": self.source,
            "source_url": self.source_url,
            "last_verified": self.last_verified,
            "text": self.text,
            "score": self.score,
            "dense_rank": self.dense_rank,
            "sparse_rank": self.sparse_rank,
            "dense_score": self.dense_score,
            "sparse_score": self.sparse_score,
            "matched_signals": self.matched_signals,
        }


def compute_rrf_score(
    dense_rank: Optional[int],
    sparse_rank: Optional[int],
    k: int = 60,
    w_dense: float = 0.6,
    w_sparse: float = 0.4,
) -> float:
    """Calculate Reciprocal Rank Fusion score from 1-indexed ranks."""
    score = 0.0
    if dense_rank is not None:
        score += w_dense / (k + dense_rank)
    if sparse_rank is not None:
        score += w_sparse / (k + sparse_rank)
    return score


class HybridRetriever:
    """Orchestrates dense (Chroma) and sparse (BM25) searches with RRF reranking."""

    def __init__(
        self,
        bm25_index: Optional[BM25Index] = None,
        k_rrf: int = settings.RRF_K,
        w_dense: float = settings.DENSE_WEIGHT,
        w_sparse: float = settings.SPARSE_WEIGHT,
    ):
        self.k_rrf = k_rrf
        self.w_dense = w_dense
        self.w_sparse = w_sparse
        self.chunks_by_id: Dict[str, Chunk] = {}

        if bm25_index is None:
            self._init_indices()
        else:
            self.bm25_index = bm25_index
            self.chunks_by_id = {c.chunk_id: c for c in bm25_index.chunks}

    def _init_indices(self) -> None:
        """Load corpus chunks and build in-memory BM25 index."""
        docs = load_corpus()
        chunks = chunk_corpus(docs)
        self.chunks_by_id = {c.chunk_id: c for c in chunks}
        self.bm25_index = BM25Index().fit(chunks)

    def retrieve(
        self,
        query: str,
        brands: Optional[List[str]] = None,
        threat_tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        channels: Optional[List[str]] = None,
        top_k: int = settings.TOP_K,
        candidate_pool: int = 20,
        signal_boost: float = 1.25,
        hard_filter: bool = False,
    ) -> List[RetrievedChunk]:
        """Perform filtered hybrid retrieval with RRF.

        Args:
            query: Scan query text or threat description.
            brands: Detected brand keywords to filter/boost (e.g., ['sbi']).
            threat_tags: Detected threat tags to filter/boost (e.g., ['urgency_detected']).
            categories: Specific categories to filter by (e.g., ['playbook']).
            channels: Specific delivery channels (e.g., ['sms', 'email']).
            top_k: Final number of ranked chunks to return.
            candidate_pool: Number of top candidates to fetch from each retriever.
            signal_boost: Multiplier applied to RRF score when metadata matches detected signals.
            hard_filter: If True, strictly excludes chunks that do not match filters.

        Returns:
            List of RetrievedChunk sorted by RRF score descending.
        """
        target_brands = {b.lower().strip() for b in (brands or []) if b.strip()}
        target_tags = {t.lower().strip() for t in (threat_tags or []) if t.strip()}
        target_categories = {c.lower().strip() for c in (categories or []) if c.strip()}
        target_channels = {ch.lower().strip() for ch in (channels or []) if ch.strip()}

        # 1. Define Filter Predicate for Sparse / Local checks
        def matches_filter(meta: Dict[str, Any]) -> bool:
            if not hard_filter:
                return True
            if target_categories:
                cat = str(meta.get("category", "")).lower()
                if cat not in target_categories:
                    return False
            if target_brands:
                chunk_brands = set(meta.get("brands", []))
                if not (chunk_brands & target_brands):
                    return False
            if target_tags:
                chunk_tags = set(meta.get("threat_tags", []))
                if not (chunk_tags & target_tags):
                    return False
            if target_channels:
                chunk_channels = set(meta.get("channels", []))
                if not (chunk_channels & target_channels):
                    return False
            return True

        # 2. Dense Vector Retrieval (ChromaDB)
        # Use metadata where filter if hard filtering by category
        where_filter: Optional[Dict[str, Any]] = None
        if hard_filter and target_categories and len(target_categories) == 1:
            where_filter = {"category": list(target_categories)[0]}

        dense_candidates = query_similar(
            query_text=query,
            n_results=candidate_pool,
            where=where_filter,
        )

        # 3. Sparse Lexical Retrieval (BM25)
        sparse_filter_fn = (lambda c: matches_filter(c.metadata)) if hard_filter else None
        sparse_candidates = self.bm25_index.search(
            query=query,
            n_results=candidate_pool,
            filter_fn=sparse_filter_fn,
        )

        # 4. Map Candidates and Compute Reciprocal Rank Fusion
        dense_rank_map: Dict[str, Tuple[int, float, Dict[str, Any]]] = {}
        for rank_idx, res in enumerate(dense_candidates, start=1):
            chunk_id = res["chunk_id"]
            dense_rank_map[chunk_id] = (rank_idx, res["score"], res["metadata"])

        sparse_rank_map: Dict[str, Tuple[int, float, Dict[str, Any]]] = {}
        for rank_idx, res in enumerate(sparse_candidates, start=1):
            chunk_id = res["chunk_id"]
            sparse_rank_map[chunk_id] = (rank_idx, res["score"], res["metadata"])

        # Union of all candidate chunk IDs
        all_candidate_ids: Set[str] = set(dense_rank_map.keys()) | set(sparse_rank_map.keys())

        # If hard_filter is active, filter candidates
        if hard_filter:
            all_candidate_ids = {
                cid for cid in all_candidate_ids
                if (cid in self.chunks_by_id and matches_filter(self.chunks_by_id[cid].metadata))
            }

        retrieved: List[RetrievedChunk] = []

        for cid in all_candidate_ids:
            chunk = self.chunks_by_id.get(cid)
            if chunk is None:
                continue

            dense_info = dense_rank_map.get(cid)
            sparse_info = sparse_rank_map.get(cid)

            dense_rank = dense_info[0] if dense_info else None
            dense_score = dense_info[1] if dense_info else None
            sparse_rank = sparse_info[0] if sparse_info else None
            sparse_score = sparse_info[1] if sparse_info else None

            # Compute baseline RRF score
            rrf_score = compute_rrf_score(
                dense_rank=dense_rank,
                sparse_rank=sparse_rank,
                k=self.k_rrf,
                w_dense=self.w_dense,
                w_sparse=self.w_sparse,
            )

            # Signal Matching & Boosting
            matched_signals: List[str] = []
            chunk_meta = chunk.metadata
            chunk_brands = set(chunk_meta.get("brands", []))
            chunk_tags = set(chunk_meta.get("threat_tags", []))
            chunk_channels = set(chunk_meta.get("channels", []))

            common_brands = target_brands & chunk_brands
            for b in common_brands:
                if b != "_none_":
                    matched_signals.append(f"brand:{b}")

            common_tags = target_tags & chunk_tags
            for t in common_tags:
                if t != "_none_":
                    matched_signals.append(f"tag:{t}")

            common_channels = target_channels & chunk_channels
            for ch in common_channels:
                if ch != "_none_":
                    matched_signals.append(f"channel:{ch}")

            # Apply soft boost if signals matched
            final_score = rrf_score
            if matched_signals and signal_boost > 1.0:
                # Add boost proportional to signal match strength
                boost_factor = 1.0 + (signal_boost - 1.0) * min(2.0, len(matched_signals))
                final_score *= boost_factor

            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    doc_title=chunk.doc_title,
                    section_title=chunk.section_title,
                    category=chunk.category,
                    source=chunk_meta.get("source", ""),
                    source_url=chunk_meta.get("source_url", ""),
                    last_verified=chunk_meta.get("last_verified", ""),
                    text=chunk.text,
                    score=round(final_score, 6),
                    dense_rank=dense_rank,
                    sparse_rank=sparse_rank,
                    dense_score=round(dense_score, 4) if dense_score is not None else None,
                    sparse_score=round(sparse_score, 4) if sparse_score is not None else None,
                    matched_signals=matched_signals,
                    metadata=chunk.metadata,
                )
            )

        # 5. Sort descending by fused RRF score
        retrieved.sort(key=lambda r: r.score, reverse=True)

        if not hard_filter and top_k >= 3 and len(retrieved) > top_k:
            categories_in_top = {r.category for r in retrieved[:top_k]}
            # If playbook is absent from top_k, ensure top matching playbook is included
            if "playbook" not in categories_in_top:
                top_playbook = next((r for r in retrieved[top_k:] if r.category == "playbook"), None)
                if top_playbook is not None:
                    cat_counts: Dict[str, int] = {}
                    for r in retrieved[:top_k]:
                        cat_counts[r.category] = cat_counts.get(r.category, 0) + 1
                    crowded_cat = max(cat_counts, key=cat_counts.get)
                    if cat_counts[crowded_cat] > 1:
                        # Find the lowest-scoring index of crowded_cat to replace
                        replace_idx = min(
                            [i for i in range(top_k) if retrieved[i].category == crowded_cat],
                            key=lambda i: retrieved[i].score,
                        )
                        diversified = list(retrieved[:top_k])
                        diversified[replace_idx] = top_playbook
                        return diversified

        return retrieved[:top_k]


_default_retriever: Optional[HybridRetriever] = None


def get_retriever() -> HybridRetriever:
    """Get or create singleton HybridRetriever."""
    global _default_retriever
    if _default_retriever is None:
        _default_retriever = HybridRetriever()
    return _default_retriever
