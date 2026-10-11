"""Corpus loader: parse, clean, and validate curated Markdown knowledge docs.

Each corpus document is a Markdown file with YAML-style front matter
(simple ``key: value`` lines; lists written as ``[a, b, c]``). The loader
normalizes whitespace, validates metadata against the controlled vocabularies
shared with the PHISHEYE backend, and returns ``CorpusDocument`` objects.

No external dependencies — importable by the ingest pipeline, the API service,
and standalone validation scripts alike.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"

CATEGORIES = {"playbook", "brand_guidance", "threat_report", "taxonomy"}
CHANNELS = {"email", "sms", "voice", "social", "web", "qr", "app", "print"}

# Controlled vocabularies — keep aligned with the PHISHEYE backend:
# backend/app/services/brand_detector.py (BRANDS)
# backend/app/services/psychology.py (CATEGORIES) + url_checker.py tags.
KNOWN_BRANDS = {
    "sbi", "hdfc", "icici", "axis", "paypal", "amazon", "google", "youtube",
    "github", "microsoft", "apple", "paytm", "phonepe", "irctc", "flipkart",
    "whatsapp", "instagram", "facebook", "netflix", "uidai", "incometax",
    "fedex", "dhl", "linkedin", "naukri",
}
KNOWN_THREAT_TAGS = {
    # psychology.py categories
    "urgency_detected", "fear_tactics", "authority_impersonation", "coercion",
    "financial_pressure", "credential_pressure", "countdown", "greed_bait",
    "secrecy", "emotional_manipulation",
    # url_checker / pipeline tags
    "brand_impersonation", "sender_mismatch", "shortened_url",
    "domain_not_found", "new_domain", "phishing", "suspicious_tld", "ip_url",
    "no_https", "dangerous_executable",
}

REQUIRED_FIELDS = ("id", "title", "category", "source", "source_url",
                   "last_verified", "summary")
LIST_FIELDS = ("channels", "brands", "threat_tags", "mitre")


class CorpusError(ValueError):
    """Raised when a corpus document fails validation."""


@dataclass
class CorpusDocument:
    id: str
    title: str
    category: str
    source: str
    source_url: str
    last_verified: str
    summary: str
    language: str = "en"
    region: str = "global"
    channels: List[str] = field(default_factory=list)
    brands: List[str] = field(default_factory=list)
    threat_tags: List[str] = field(default_factory=list)
    mitre: List[str] = field(default_factory=list)
    severity: str = "medium"
    tactics: List[str] = field(default_factory=list)
    iocs: List[str] = field(default_factory=list)
    first_seen: str = "2024-01-01"
    official_domains: List[str] = field(default_factory=list)
    subdomain_rules: List[str] = field(default_factory=list)
    phishing_patterns: List[str] = field(default_factory=list)
    logo_phash: str = ""
    contact_channels: List[str] = field(default_factory=list)
    never_does: List[str] = field(default_factory=list)
    regulatory_notes: str = ""
    published_at: str = ""
    publisher: str = ""
    report_url: str = ""
    edition: str = ""
    key_stats: List[str] = field(default_factory=list)
    top_targets: List[str] = field(default_factory=list)
    top_ttps: List[str] = field(default_factory=list)
    page_count: int = 1
    fetched_at: str = ""
    source_hash: str = ""
    license: str = "Public Domain / Synthesized"
    version: int = 1
    body: str = ""
    path: str = ""

    @property
    def word_count(self) -> int:
        return len(self.body.split())


_FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.S)


def _parse_scalar(raw: str) -> object:
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("\"'") for item in inner.split(",") if item.strip()]
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1].strip()
    return raw


def _clean_body(text: str) -> str:
    """Normalize whitespace and strip markdown noise without losing meaning."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)          # collapse blank runs
    text = re.sub(r"[ \t]{2,}", " ", text)          # collapse inline spaces
    text = re.sub(r"[*_]{1,2}([^*_\n]+)[*_]{1,2}", r"\1", text)  # bold/italic
    text = re.sub(r"`([^`\n]+)`", r"\1", text)      # inline code
    return text.strip()


def parse_document(path: Path) -> CorpusDocument:
    raw = path.read_text(encoding="utf-8")
    match = _FRONT_MATTER_RE.match(raw)
    if not match:
        raise CorpusError(f"{path.name}: missing front matter (--- block)")

    meta: dict = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise CorpusError(f"{path.name}: malformed metadata line: {line!r}")
        meta[key.strip()] = _parse_scalar(value)

    body = _clean_body(match.group(2))
    doc_path = str(path.relative_to(CORPUS_DIR)).replace("\\", "/")

    # Generate deterministic SHA-256 hash if not in front-matter
    import hashlib
    raw_hash = meta.get("source_hash") or hashlib.sha256(body.encode("utf-8")).hexdigest()

    doc = CorpusDocument(
        id=str(meta.get("id", "")),
        title=str(meta.get("title", "")),
        category=str(meta.get("category", "")),
        source=str(meta.get("source", "")),
        source_url=str(meta.get("source_url", "")),
        last_verified=str(meta.get("last_verified", "")),
        summary=str(meta.get("summary", "")),
        language=str(meta.get("language", "en")),
        region=str(meta.get("region", "global")),
        channels=list(meta.get("channels", [])),
        brands=list(meta.get("brands", [])),
        threat_tags=list(meta.get("threat_tags", [])),
        mitre=list(meta.get("mitre", [])),
        severity=str(meta.get("severity", "medium")),
        tactics=list(meta.get("tactics", [])),
        iocs=list(meta.get("iocs", [])),
        first_seen=str(meta.get("first_seen", "2024-01-01")),
        official_domains=list(meta.get("official_domains", [])),
        subdomain_rules=list(meta.get("subdomain_rules", [])),
        phishing_patterns=list(meta.get("phishing_patterns", [])),
        logo_phash=str(meta.get("logo_phash", "")),
        contact_channels=list(meta.get("contact_channels", [])),
        never_does=list(meta.get("never_does", [])),
        regulatory_notes=str(meta.get("regulatory_notes", "")),
        published_at=str(meta.get("published_at", meta.get("last_verified", ""))),
        publisher=str(meta.get("publisher", meta.get("source", ""))),
        report_url=str(meta.get("report_url", meta.get("source_url", ""))),
        edition=str(meta.get("edition", "2025 Edition")),
        key_stats=list(meta.get("key_stats", [])),
        top_targets=list(meta.get("top_targets", [])),
        top_ttps=list(meta.get("top_ttps", [])),
        page_count=int(meta.get("page_count", 1)),
        fetched_at=str(meta.get("fetched_at", meta.get("last_verified", "") + "T00:00:00Z")),
        source_hash=str(raw_hash),
        license=str(meta.get("license", "Public Domain / Synthesized")),
        version=int(meta.get("version", 1)),
        body=body,
        path=doc_path,
    )
    _validate(doc)
    return doc


def _validate(doc: CorpusDocument) -> None:
    for name in REQUIRED_FIELDS:
        if not getattr(doc, name):
            raise CorpusError(f"{doc.path}: missing required field '{name}'")
    if doc.category not in CATEGORIES:
        raise CorpusError(f"{doc.path}: unknown category '{doc.category}'")
    if doc.severity not in {"low", "medium", "high", "critical"}:
        raise CorpusError(f"{doc.path}: invalid severity '{doc.severity}' (must be low, medium, high, or critical)")
    if not doc.source_url.startswith(("http://", "https://")):
        raise CorpusError(f"{doc.path}: source_url must be an http(s) URL")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", doc.last_verified):
        raise CorpusError(f"{doc.path}: last_verified must be YYYY-MM-DD")
    unknown_brands = set(doc.brands) - KNOWN_BRANDS
    if unknown_brands:
        raise CorpusError(f"{doc.path}: unknown brands {sorted(unknown_brands)}")
    unknown_tags = set(doc.threat_tags) - KNOWN_THREAT_TAGS
    if unknown_tags:
        raise CorpusError(f"{doc.path}: unknown threat_tags {sorted(unknown_tags)}")
    bad_channels = set(doc.channels) - CHANNELS
    if bad_channels:
        raise CorpusError(f"{doc.path}: unknown channels {sorted(bad_channels)}")
    if doc.word_count < 80:
        raise CorpusError(f"{doc.path}: body too short ({doc.word_count} words, min 80)")


def load_corpus(root: Optional[Path] = None) -> List[CorpusDocument]:
    """Load and validate every corpus document. Raises on the first error."""
    root = root or CORPUS_DIR
    docs: List[CorpusDocument] = []
    seen_ids: set = set()
    for path in sorted(root.rglob("*.md")):
        doc = parse_document(path)
        if doc.id in seen_ids:
            raise CorpusError(f"{doc.path}: duplicate id '{doc.id}'")
        seen_ids.add(doc.id)
        docs.append(doc)
    if not docs:
        raise CorpusError(f"no corpus documents found under {root}")
    return docs


if __name__ == "__main__":
    corpus = load_corpus()
    print(f"loaded {len(corpus)} documents OK")
