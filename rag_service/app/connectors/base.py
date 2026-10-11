"""Base class for live threat feed and advisory connectors."""

from __future__ import annotations

import abc
import logging
from typing import Any, Dict, List, Optional

from app.corpus import CorpusDocument
from app.provenance import compute_source_hash, get_current_iso_timestamp

logger = logging.getLogger(__name__)


class BaseFeedConnector(abc.ABC):
    """Abstract base class for all external threat advisory feed connectors."""

    def __init__(
        self,
        source_id: str,
        name: str,
        endpoint: str,
        license: str,
        category: str = "threat_report",
    ):
        self.source_id = source_id
        self.name = name
        self.endpoint = endpoint
        self.license = license
        self.category = category

    @abc.abstractmethod
    async def fetch_feed(self) -> List[CorpusDocument]:
        """Fetch upstream feed, parse contents, and return validated CorpusDocument objects."""
        raise NotImplementedError

    def build_document(
        self,
        doc_id: str,
        title: str,
        summary: str,
        body: str,
        source_url: str,
        last_verified: str,
        channels: Optional[List[str]] = None,
        brands: Optional[List[str]] = None,
        threat_tags: Optional[List[str]] = None,
        mitre: Optional[List[str]] = None,
        version: int = 1,
    ) -> CorpusDocument:
        """Helper to assemble a CorpusDocument with cryptographic provenance."""
        source_hash = compute_source_hash(body)
        fetched_at = get_current_iso_timestamp()

        return CorpusDocument(
            id=doc_id,
            title=title,
            category=self.category,
            source=self.name,
            source_url=source_url,
            last_verified=last_verified,
            summary=summary,
            language="en",
            region="global",
            channels=channels or ["email", "web"],
            brands=brands or [],
            threat_tags=threat_tags or ["phishing"],
            mitre=mitre or ["T1566"],
            fetched_at=fetched_at,
            source_hash=source_hash,
            license=self.license,
            version=version,
            body=body,
            path=f"live_feeds/{doc_id}.md",
        )
