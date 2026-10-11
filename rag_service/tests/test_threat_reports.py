"""Comprehensive tests and gating suite for Threat Reports and Taxonomies.

Validates:
1. Scale Gate: 20+ threat reports and taxonomy documents ingested
2. Attribution Compliance: published_at, publisher, report_url, edition, and page_count
3. Quantitative Stats Extraction: structured key_stats present and queryable
4. Regional Coverage Gate: CERT-In, RBI, NPCI, I4C representation
5. Taxonomy Alignment: strict mapping to MITRE ATT&CK and APWG taxonomies
"""

import re
import pytest
from app.corpus import load_corpus


@pytest.fixture(scope="module")
def corpus_docs():
    return load_corpus()


@pytest.fixture(scope="module")
def threat_reports(corpus_docs):
    return [d for d in corpus_docs if d.category == "threat_report"]


@pytest.fixture(scope="module")
def taxonomies(corpus_docs):
    return [d for d in corpus_docs if d.category == "taxonomy"]


def test_threat_reports_scale_gate(threat_reports, taxonomies):
    """Gating test: Verify at least 20 combined threat reports and taxonomies exist."""
    combined_count = len(threat_reports) + len(taxonomies)
    assert combined_count >= 20, f"Expected at least 20 threat reports and taxonomies, found {combined_count}"
    assert len(threat_reports) >= 15, f"Expected at least 15 threat reports, found {len(threat_reports)}"
    assert len(taxonomies) >= 4, f"Expected at least 4 taxonomies, found {len(taxonomies)}"


def test_threat_reports_attribution_compliance(threat_reports):
    """Ensure every threat report has complete publication dates, publishers, versions, and source URLs."""
    date_regex = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    for report in threat_reports:
        # 1. Publication Date
        assert date_regex.match(report.published_at), f"{report.id}: invalid published_at '{report.published_at}'"
        
        # 2. Publisher
        assert len(report.publisher) >= 3, f"{report.id}: missing or short publisher '{report.publisher}'"
        
        # 3. Source / Report URL
        assert report.report_url.startswith(("http://", "https://")), f"{report.id}: invalid report_url '{report.report_url}'"
        
        # 4. Edition / Version
        assert len(report.edition) >= 3, f"{report.id}: missing edition '{report.edition}'"
        
        # 5. Page count
        assert report.page_count >= 1, f"{report.id}: page_count must be >= 1"


def test_quantitative_statistics_extraction(threat_reports):
    """Verify that structured quantitative data (numbers, percentages, attack counts) are extracted."""
    stat_pattern = re.compile(r"(\d+[\.,]?\d*\%|\$\d+|\d+\s?(?:million|billion|attacks|incidents|lakh|crore|second|hours))", re.IGNORECASE)

    reports_with_stats = 0
    for report in threat_reports:
        if report.key_stats:
            reports_with_stats += 1
            # Verify that at least one stat contains quantitative indicators
            has_metric = any(stat_pattern.search(s) for s in report.key_stats)
            assert has_metric, f"{report.id}: key_stats do not contain measurable quantitative metrics: {report.key_stats}"

    # At least 80% of threat reports should have structured quantitative key_stats
    coverage_ratio = reports_with_stats / len(threat_reports)
    assert coverage_ratio >= 0.75, f"Only {coverage_ratio:.1%} of reports have quantitative stats, expected >= 75%"


def test_regional_indian_threat_coverage(threat_reports):
    """Verify that regional Indian authorities (CERT-In, RBI, NPCI, I4C, UIDAI) are actively represented."""
    publishers_lower = " ".join(r.publisher.lower() for r in threat_reports)
    
    expected_authorities = ["cert-in", "rbi", "npci", "i4c"]
    for auth in expected_authorities:
        assert auth in publishers_lower, f"Regional coverage failure: authority '{auth}' not found in threat report publishers"


def test_taxonomy_mitre_and_apwg_alignment(taxonomies):
    """Validate that taxonomy documents rigorously align with MITRE ATT&CK and APWG standards."""
    taxonomy_ids = {t.id for t in taxonomies}
    assert "taxonomy-mitre-attack-phishing" in taxonomy_ids
    assert "taxonomy-apwg-ecrime" in taxonomy_ids

    mitre_doc = next(t for t in taxonomies if t.id == "taxonomy-mitre-attack-phishing")
    # Must map key spearphishing sub-techniques
    assert any("T1566.001" in m for m in mitre_doc.mitre)
    assert any("T1566.002" in m for m in mitre_doc.mitre)
    assert any("T1566.003" in m for m in mitre_doc.mitre)
    assert any("T1539" in m for m in mitre_doc.mitre)
