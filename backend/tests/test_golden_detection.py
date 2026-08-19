from app.services.url_checker import URLChecker
from tests.intel_fixtures import failing_providers, offline_providers


LEGITIMATE = [
    "https://www.google.com",
    "https://github.com",
    "https://www.youtube.com",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
]

SUSPICIOUS = [
    "https://paypa1.com",
    "https://sbi-login.xyz",
]

CONFIRMED = [
    "https://phish.example.test/login/account",
    "https://PHISH.EXAMPLE.TEST/login/account/?session=123",
    "https://phish.example.test/login/account",
]


def _checker():
    return URLChecker()


def test_famous_sites_stay_low_when_feeds_list_other_paths():
    checker = _checker()
    providers = offline_providers(
        openphish_urls=[
            "https://www.youtube.com/watch?v=PhishVideoId99",
            "https://www.google.com/?shortlink=u95g39zq",
            "https://github.com/login?return_to=https://evil.example.test",
        ]
    )
    for url in (
        "https://www.google.com",
        "https://www.google.com/search?q=maps",
        "https://www.youtube.com",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://github.com",
        "https://github.com/login",
    ):
        result = checker.analyze(url, intel_providers=providers)
        assert result["risk_level"] == "LOW", url
        assert result["safe"] is True, url
        assert result["classification"] != "CONFIRMED_MALICIOUS", url


def test_legitimate_is_not_confirmed_malicious():
    checker = _checker()
    providers = offline_providers()
    for url in LEGITIMATE:
        result = checker.analyze(url, intel_providers=providers)
        assert result["classification"] != "CONFIRMED_MALICIOUS"
        assert result["risk_level"] == "LOW"
        assert result["safe"] is True
        assert "completely safe" not in (result["simple_view"]["warning"] or "").lower()
        assert "100%" not in (result["simple_view"]["warning"] or "")


def test_suspicious_is_not_safe():
    checker = _checker()
    providers = offline_providers()
    for url in SUSPICIOUS:
        result = checker.analyze(url, intel_providers=providers)
        assert result["safe"] is False
        assert result["risk_level"] in {"MEDIUM", "HIGH", "CRITICAL"}
        assert result["classification"] in {"SUSPICIOUS", "CONFIRMED_MALICIOUS"}


def test_confirmed_malicious_like_never_becomes_safe():
    checker = _checker()
    listed = "https://phish.example.test/login/account"
    providers = offline_providers(openphish_urls=[listed])
    for url in CONFIRMED:
        result = checker.analyze(url, intel_providers=providers)
        assert result["safe"] is False, url
        assert result["classification"] == "CONFIRMED_MALICIOUS", url
        assert result["risk_level"] in {"HIGH", "CRITICAL"}, url
        assert result["risk_score"] >= 70, url


def test_provider_failure_is_unavailable_not_safe_claim():
    checker = _checker()
    result = checker.analyze("https://unknown-brand.test/home", intel_providers=failing_providers())
    intel = result["details"]["threat_intelligence"]
    assert intel["overall_status"] == "unavailable"
    assert result["debug"]["openphish"] == "unavailable"
    assert result["debug"]["phishtank"] == "unavailable"
    assert result["debug"]["urlhaus"] == "unavailable"
    warning = (result["simple_view"]["warning"] or "").lower()
    assert "unavailable" in warning or "not a guarantee" in warning or "not" in warning


def test_debug_payload_present():
    result = _checker().analyze(
        "https://Example.test/login/?id=123",
        intel_providers=offline_providers(),
    )
    debug = result["debug"]
    assert debug["normalized_url"] == "https://example.test/login"
    assert debug["hostname"] == "example.test"
    assert "ml_probability" in debug
    assert debug["final_classification"]


def test_golden_decision_metrics():
    checker = _checker()
    listed = "https://phish.example.test/login/account"
    providers = offline_providers(openphish_urls=[listed])
    rows = []
    for url in LEGITIMATE:
        result = checker.analyze(url, intel_providers=providers)
        rows.append(("legit", result["safe"] is False))
    for url in SUSPICIOUS:
        result = checker.analyze(url, intel_providers=offline_providers())
        rows.append(("phishy", result["safe"] is False))
    for url in CONFIRMED:
        result = checker.analyze(url, intel_providers=providers)
        rows.append(("phishy", result["safe"] is False))

    false_positives = sum(1 for label, flagged in rows if label == "legit" and flagged)
    false_negatives = sum(1 for label, flagged in rows if label == "phishy" and not flagged)
    true_positives = sum(1 for label, flagged in rows if label == "phishy" and flagged)
    true_negatives = sum(1 for label, flagged in rows if label == "legit" and not flagged)
    precision = true_positives / max(true_positives + false_positives, 1)
    recall = true_positives / max(true_positives + false_negatives, 1)
    f1 = 0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    assert false_negatives == 0
    assert recall == 1
    assert true_negatives >= 1
    assert f1 >= 0.8
    assert precision >= 0.8
