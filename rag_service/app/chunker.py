"""Markdown section chunker for the PHISHEYE RAG knowledge corpus.

Splits each validated CorpusDocument into:
1. An Overview Chunk summarizing the document, metadata, and key takeaways.
2. Section Chunks preserving individual markdown headings (e.g., 'Warning signs for analysts',
   'Recurring lures', 'Recommended user guidance') with contextual document prefixes.

Produces typed Chunk objects with metadata formatted for ChromaDB indexing and filtering.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.config import settings
from app.corpus import CorpusDocument


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    doc_title: str
    category: str
    section_title: str
    chunk_type: str  # "overview" or "section"
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_index: int = 0
    char_start: int = 0
    char_end: int = 0
    paragraph_index: int = 0
    embedding_model: str = ""
    embedding_version: str = ""
    content_hash: str = ""

    @property
    def word_count(self) -> int:
        return len(self.text.split())


def _slugify(text: str) -> str:
    """Convert text to a clean URL-friendly slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def chunk_document(doc: CorpusDocument) -> List[Chunk]:
    """Chunk a single CorpusDocument into an overview chunk and section chunks."""
    chunks: List[Chunk] = []

    # Prepare base metadata common to all chunks of this document
    base_metadata: Dict[str, Any] = {
        "doc_id": doc.id,
        "doc_title": doc.title,
        "category": doc.category,
        "source": doc.source,
        "source_url": doc.source_url,
        "last_verified": doc.last_verified,
        "language": doc.language,
        "region": doc.region,
        "path": doc.path,
        "license": doc.license,
        "source_hash": doc.source_hash,
        "fetched_at": doc.fetched_at,
        "version": doc.version,
        "severity": doc.severity,
        "first_seen": doc.first_seen,
        # ChromaDB requires non-empty lists for list-type metadata
        "brands": doc.brands if doc.brands else ["_none_"],
        "threat_tags": doc.threat_tags if doc.threat_tags else ["_none_"],
        "channels": doc.channels if doc.channels else ["_none_"],
        "mitre": doc.mitre if doc.mitre else ["_none_"],
        "tactics": doc.tactics if doc.tactics else ["_none_"],
        "iocs": doc.iocs if doc.iocs else ["_none_"],
        "official_domains": doc.official_domains if doc.official_domains else ["_none_"],
        "logo_phash": doc.logo_phash if doc.logo_phash else "",
        "regulatory_notes": doc.regulatory_notes if doc.regulatory_notes else "",
        # Comma-separated strings for lexical filtering and text dumps
        "brands_csv": ",".join(doc.brands),
        "threat_tags_csv": ",".join(doc.threat_tags),
        "channels_csv": ",".join(doc.channels),
        "mitre_csv": ",".join(doc.mitre),
        "tactics_csv": ",".join(doc.tactics),
        "iocs_csv": ",".join(doc.iocs),
        "official_domains_csv": ",".join(doc.official_domains),
        "never_does_csv": "; ".join(doc.never_does),
        "published_at": doc.published_at if doc.published_at else "",
        "publisher": doc.publisher if doc.publisher else "",
        "edition": doc.edition if doc.edition else "",
        "report_url": doc.report_url if doc.report_url else "",
        "key_stats_csv": "; ".join(doc.key_stats),
        "top_targets_csv": ", ".join(doc.top_targets),
        "top_ttps_csv": ", ".join(doc.top_ttps),
    }

    # 1. Overview Chunk
    overview_text_parts = [
        f"{doc.title} ({doc.category.replace('_', ' ').title()})",
        f"Source: {doc.source}",
        f"Summary: {doc.summary}",
    ]
    if doc.published_at:
        overview_text_parts.append(f"Published: {doc.published_at} ({doc.edition}) by {doc.publisher}")
    if doc.key_stats:
        overview_text_parts.append(f"Key Threat Statistics: {'; '.join(doc.key_stats)}")
    if doc.top_targets:
        overview_text_parts.append(f"Primary Targeted Sectors: {', '.join(doc.top_targets)}")
    if doc.brands:
        overview_text_parts.append(f"Target Brands: {', '.join(doc.brands)}")
    if doc.official_domains:
        overview_text_parts.append(f"Official Verified Domains: {', '.join(doc.official_domains)}")
    if doc.never_does:
        overview_text_parts.append(f"Security Rules (Never Does): {'; '.join(doc.never_does)}")
    if doc.threat_tags:
        overview_text_parts.append(f"Threat Indicators: {', '.join(doc.threat_tags)}")
    if doc.channels:
        overview_text_parts.append(f"Observed Channels: {', '.join(doc.channels)}")
    if doc.mitre:
        overview_text_parts.append(f"ATT&CK Techniques: {', '.join(doc.mitre)}")

    overview_text = "\n".join(overview_text_parts)
    overview_hash = hashlib.sha256(re.sub(r"\s+", " ", overview_text.strip()).encode("utf-8")).hexdigest()
    overview_meta = dict(base_metadata)
    overview_meta.update({
        "chunk_id": f"{doc.id}#overview",
        "section_title": "Overview",
        "chunk_type": "overview",
        "chunk_index": 0,
        "char_start": 0,
        "char_end": len(overview_text),
        "paragraph_index": 0,
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_version": settings.EMBEDDING_VERSION,
        "content_hash": overview_hash,
    })

    chunks.append(
        Chunk(
            chunk_id=f"{doc.id}#overview",
            doc_id=doc.id,
            doc_title=doc.title,
            category=doc.category,
            section_title="Overview",
            chunk_type="overview",
            text=overview_text,
            metadata=overview_meta,
            chunk_index=0,
            char_start=0,
            char_end=len(overview_text),
            paragraph_index=0,
            embedding_model=settings.EMBEDDING_MODEL,
            embedding_version=settings.EMBEDDING_VERSION,
            content_hash=overview_hash,
        )
    )

    # 2. Section Chunks (split on markdown headings '## ')
    # Match any section starting with '## '
    raw_sections = re.split(r"(?m)^##\s+", doc.body)
    search_cursor = 0
    chunk_counter = 1
    para_counter = 1

    for raw in raw_sections:
        raw = raw.strip()
        if not raw:
            continue

        lines = raw.split("\n", 1)
        heading = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        if not body:
            continue

        section_slug = _slugify(heading) or "section"
        chunk_id = f"{doc.id}#{section_slug}"

        # Contextual prefix ensures embedding model knows document context
        section_text = (
            f"{doc.title} — {heading}\n"
            f"Category: {doc.category} | Source: {doc.source}\n\n"
            f"{body}"
        )

        sec_heading_pattern = f"## {heading}"
        pos = doc.body.find(sec_heading_pattern, search_cursor)
        if pos != -1:
            char_start = pos
            char_end = pos + len(raw) + 3
            search_cursor = char_end
        else:
            char_start = search_cursor
            char_end = char_start + len(raw)
            search_cursor = char_end

        sec_hash = hashlib.sha256(re.sub(r"\s+", " ", section_text.strip()).encode("utf-8")).hexdigest()

        section_meta = dict(base_metadata)
        section_meta.update({
            "chunk_id": chunk_id,
            "section_title": heading,
            "chunk_type": "section",
            "chunk_index": chunk_counter,
            "char_start": char_start,
            "char_end": char_end,
            "paragraph_index": para_counter,
            "embedding_model": settings.EMBEDDING_MODEL,
            "embedding_version": settings.EMBEDDING_VERSION,
            "content_hash": sec_hash,
        })

        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                doc_id=doc.id,
                doc_title=doc.title,
                category=doc.category,
                section_title=heading,
                chunk_type="section",
                text=section_text,
                metadata=section_meta,
                chunk_index=chunk_counter,
                char_start=char_start,
                char_end=char_end,
                paragraph_index=para_counter,
                embedding_model=settings.EMBEDDING_MODEL,
                embedding_version=settings.EMBEDDING_VERSION,
                content_hash=sec_hash,
            )
        )
        chunk_counter += 1
        para_counter += 1

    return chunks


def chunk_corpus(docs: List[CorpusDocument]) -> List[Chunk]:
    """Chunk an entire collection of CorpusDocument objects."""
    all_chunks: List[Chunk] = []
    seen_ids: set = set()

    for doc in docs:
        for chunk in chunk_document(doc):
            if chunk.chunk_id in seen_ids:
                # Disambiguate if duplicate section heading in same document
                i = 2
                while f"{chunk.chunk_id}-{i}" in seen_ids:
                    i += 1
                chunk.chunk_id = f"{chunk.chunk_id}-{i}"
                chunk.metadata["chunk_id"] = chunk.chunk_id

            seen_ids.add(chunk.chunk_id)
            all_chunks.append(chunk)

    return all_chunks
