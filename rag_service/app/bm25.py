"""Sparse lexical retrieval using the BM25Okapi ranking algorithm.

Complements dense semantic vector search by prioritizing exact keyword matches,
brand names, specific terminology (e.g. 'KYC', 'quishing', 'T1566'), and threat tags.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any, Callable, Dict, List, Optional, Tuple

from app.chunker import Chunk


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric tokens.
    
    Preserves hyphenated and underscored technical tokens (e.g., 't1566.002', 'urgency_detected').
    """
    text = text.lower()
    # Find tokens of letters, digits, underscores, dots, hyphens (min len 2)
    tokens = re.findall(r"\b[a-z0-9][a-z0-9_\.\-]*[a-z0-9]\b|[a-z0-9]", text)
    # Filter common short English stopwords
    stopwords = {
        "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of",
        "with", "by", "from", "is", "are", "was", "were", "it", "this", "that",
        "be", "as", "if", "into", "has", "have", "had", "will", "would",
        "you", "your", "yours", "we", "our", "ours", "i", "me", "my", "they", "their",
    }
    return [t for t in tokens if t not in stopwords and len(t) > 1]


class BM25Index:
    """Okapi BM25 sparse index over knowledge chunks."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[Chunk] = []
        self.doc_ids: List[str] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_term_freqs: List[Counter] = []
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.num_docs: int = 0

    def fit(self, chunks: List[Chunk]) -> BM25Index:
        """Build the inverted index and calculate IDF values for all chunks."""
        self.chunks = list(chunks)
        self.doc_ids = [c.chunk_id for c in self.chunks]
        self.num_docs = len(self.chunks)

        self.doc_term_freqs = []
        self.doc_lengths = []
        self.doc_freqs = Counter()

        for chunk in self.chunks:
            tokens = tokenize(chunk.text)
            self.doc_lengths.append(len(tokens))
            tf = Counter(tokens)
            self.doc_term_freqs.append(tf)
            for term in tf.keys():
                self.doc_freqs[term] += 1

        self.avg_doc_len = sum(self.doc_lengths) / max(1, self.num_docs)

        # Standard BM25 IDF: ln(1 + (N - df + 0.5) / (df + 0.5))
        self.idf = {}
        for term, df in self.doc_freqs.items():
            self.idf[term] = math.log(1.0 + (self.num_docs - df + 0.5) / (df + 0.5))

        return self

    def score_doc(self, query_tokens: List[str], doc_idx: int) -> float:
        """Calculate the BM25 score for a specific document against query tokens."""
        doc_len = self.doc_lengths[doc_idx]
        tf = self.doc_term_freqs[doc_idx]
        score = 0.0

        len_norm = 1.0 - self.b + self.b * (doc_len / max(1e-6, self.avg_doc_len))

        for q in query_tokens:
            if q not in tf:
                continue
            f = tf[q]
            idf = self.idf.get(q, 0.0)
            numerator = f * (self.k1 + 1.0)
            denominator = f + self.k1 * len_norm
            score += idf * (numerator / denominator)

        return score

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_fn: Optional[Callable[[Chunk], bool]] = None,
    ) -> List[Dict[str, Any]]:
        """Search the BM25 index and return the top ranked chunks with scores.
        
        Args:
            query: The search query string.
            n_results: Number of top results to return.
            filter_fn: Optional boolean predicate to filter candidate chunks.

        Returns:
            List of dicts: {"chunk_id": str, "score": float, "chunk": Chunk, "metadata": dict, "text": str}
        """
        query_tokens = tokenize(query)
        if not query_tokens or self.num_docs == 0:
            return []

        scored: List[Tuple[int, float]] = []
        for idx in range(self.num_docs):
            chunk = self.chunks[idx]
            if filter_fn is not None and not filter_fn(chunk):
                continue
            s = self.score_doc(query_tokens, idx)
            if s > 0.0:
                scored.append((idx, s))

        # Sort descending by BM25 score
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:n_results]

        results: List[Dict[str, Any]] = []
        for idx, score in top:
            chunk = self.chunks[idx]
            results.append({
                "chunk_id": chunk.chunk_id,
                "score": round(score, 4),
                "text": chunk.text,
                "metadata": chunk.metadata,
                "chunk": chunk,
            })

        return results
