from app.services.decision_engine import calculate_final_risk
from app.services.feed_cache import build_domain_index, parse_domain_lines, parse_url_lines
from app.services.threat_intel import (
    build_feed_index,
    lookup_openphish,
    lookup_phishing_army,
    lookup_phishtank,
    lookup_threat_intelligence,
    lookup_urlhaus,
    match_against_index,
)
from app.services.url_normalize import normalize_url


FEED_URL = "https://phish.example.test/login/account"


def test_openphish_exact_match():
    index = build_feed_index([FEED_URL])
    result = lookup_openphish(normalize_url(FEED_URL), index=index)
    assert result["found"] is True
    assert result["status"] == "confirmed_malicious"
    assert result["match_type"] in {"exact_url", "normalized_url"}


def test_openphish_normalized_match():
    index = build_feed_index([FEED_URL])
    user = "https://PHISH.EXAMPLE.TEST/login/account/?session=123"
    result = lookup_openphish(normalize_url(user), index=index)
    assert result["found"] is True
    assert result["status"] == "confirmed_malicious"
    assert result["match_type"] in {"normalized_url", "exact_url"}


def test_openphish_no_match():
    index = build_feed_index([FEED_URL])
    result = lookup_openphish(normalize_url("https://innocuous.example.test/home"), index=index)
    assert result["found"] is False
    assert result["status"] == "no_match"
    assert result["status"] != "confirmed_malicious"


def test_openphish_api_failure():
    def boom():
        raise RuntimeError("feed down")

    result = lookup_openphish(normalize_url("https://phish.example.test/login"), fetch_lines=boom)
    assert result["status"] == "unavailable"
    assert result["match_type"] == "unavailable"


def test_phishtank_exact_match():
    result = lookup_phishtank(
        normalize_url(FEED_URL),
        query=lambda url: {"results": {"in_database": True, "valid": True, "verified": True}},
    )
    assert result["found"] is True
    assert result["status"] == "confirmed_malicious"


def test_phishtank_normalized_match():
    result = lookup_phishtank(
        normalize_url("https://PHISH.EXAMPLE.TEST/login/account/"),
        query=lambda url: {"results": {"in_database": "true", "valid": "true"}},
    )
    assert result["found"] is True


def test_phishtank_no_match():
    result = lookup_phishtank(
        normalize_url("https://ok.example.test/"),
        query=lambda url: {"results": {"in_database": False}},
    )
    assert result["status"] == "no_match"
    assert result["found"] is False


def test_phishtank_api_failure():
    def boom(_url):
        raise RuntimeError("timeout")

    result = lookup_phishtank(normalize_url(FEED_URL), query=boom)
    assert result["status"] == "unavailable"


def test_urlhaus_exact_match():
    result = lookup_urlhaus(
        normalize_url(FEED_URL),
        query=lambda url: {"query_status": "ok", "threat": "malware_download", "url": FEED_URL},
    )
    assert result["found"] is True
    assert result["status"] == "confirmed_malicious"


def test_urlhaus_normalized_match():
    result = lookup_urlhaus(
        normalize_url("HTTPS://phish.example.test/login/account?x=1"),
        query=lambda url: {"query_status": "found", "url_status": "online"},
    )
    assert result["found"] is True


def test_urlhaus_no_match():
    result = lookup_urlhaus(
        normalize_url("https://ok.example.test/"),
        query=lambda url: {"query_status": "no_results"},
    )
    assert result["status"] == "no_match"


def test_urlhaus_api_failure():
    def boom(_url):
        raise RuntimeError("rate limit")

    result = lookup_urlhaus(normalize_url(FEED_URL), query=boom)
    assert result["status"] == "unavailable"


def test_no_match_is_not_safe_label():
    intel = lookup_threat_intelligence(
        "https://ok.example.test/",
        providers={
            "openphish_index": build_feed_index([]),
            "phishtank": lambda url: {"results": {"in_database": False}},
            "urlhaus": lambda url: {"query_status": "no_results"},
            "gsb": lambda url: [],
        },
    )
    assert intel["overall_status"] == "no_match"
    assert intel["confirmed"] is False
    assert intel["summary"] != "SAFE"


def test_trusted_domain_does_not_burn_unrelated_path():
    index = build_feed_index(["https://sites.google.com/view/scam-kit"])
    hit = match_against_index(normalize_url("https://www.google.com/search?q=mail"), index)
    assert hit["match_type"] == "no_match"


def test_google_homepage_not_flagged_for_query_only_dump_hit():
    index = build_feed_index([
        "https://www.google.com/?shortlink=u95g39zq&pid=my_media",
        "https://www.google.com/share.google?q=abc123",
        "https://www.google.com/url?q=https://evil.example.test",
    ])
    home = match_against_index(normalize_url("https://www.google.com"), index)
    search = match_against_index(normalize_url("https://www.google.com/search?q=mail"), index)
    assert home["match_type"] == "no_match"
    assert search["match_type"] == "no_match"


def test_google_phishing_path_still_matches():
    listed = "https://www.google.com/share.google?q=abc123"
    index = build_feed_index([listed])
    hit = match_against_index(normalize_url(listed), index)
    assert hit["match_type"] in {"exact_url", "normalized_url"}
    other = match_against_index(normalize_url("https://www.google.com/share.google?q=other"), index)
    assert other["match_type"] == "no_match"
    sites = match_against_index(
        normalize_url("https://sites.google.com/view/business-badge/captcha"),
        build_feed_index(["https://sites.google.com/view/business-badge/captcha"]),
    )
    assert sites["match_type"] in {"exact_url", "normalized_url"}


def test_youtube_watch_and_github_not_burned_by_other_dump_rows():
    index = build_feed_index([
        "https://www.youtube.com/watch?v=PhishVideoId99",
        "https://www.youtube.com/?feature=phish",
        "https://github.com/evil-actor/steal-tokens",
        "https://github.com/login?return_to=https://evil.example.test",
    ])
    youtube = match_against_index(
        normalize_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        index,
    )
    youtube_home = match_against_index(normalize_url("https://www.youtube.com"), index)
    github_home = match_against_index(normalize_url("https://github.com"), index)
    github_login = match_against_index(normalize_url("https://github.com/login"), index)
    listed_repo = match_against_index(
        normalize_url("https://github.com/evil-actor/steal-tokens"),
        index,
    )
    assert youtube["match_type"] == "no_match"
    assert youtube_home["match_type"] == "no_match"
    assert github_home["match_type"] == "no_match"
    assert github_login["match_type"] == "no_match"
    assert listed_repo["match_type"] in {"exact_url", "normalized_url"}


def test_path_prefix_matches_query_variant():
    index = build_feed_index([FEED_URL])
    hit = match_against_index(normalize_url("https://phish.example.test/login/account?session=123"), index)
    assert hit["match_type"] in {"normalized_url", "exact_url"}


def test_decision_engine_intel_overrides_low_ml():
    intel = lookup_threat_intelligence(
        FEED_URL,
        providers={
            "openphish_index": build_feed_index([FEED_URL]),
            "phishtank": lambda url: {"results": {"in_database": False}},
            "urlhaus": lambda url: {"query_status": "no_results"},
            "gsb": lambda url: [],
        },
    )
    decision = calculate_final_risk(
        threat_intelligence=intel,
        heuristic_score=8,
        ml_score=8,
        heuristic_tags=[],
        heuristic_reasons=["Looks ordinary"],
        url_features=normalize_url(FEED_URL),
    )
    assert decision["classification"] == "CONFIRMED_MALICIOUS"
    assert decision["safe"] is False
    assert decision["risk_level"] in {"HIGH", "CRITICAL"}
    assert decision["risk_score"] >= 70


def test_urlhaus_public_feed_match_without_api():
    result = lookup_urlhaus(
        normalize_url(FEED_URL),
        index=build_feed_index([FEED_URL]),
    )
    assert result["found"] is True
    assert result["status"] == "confirmed_malicious"
    assert "feed match" in result["detail"]


def test_urlhaus_feed_lines_match():
    result = lookup_urlhaus(
        normalize_url("https://PHISH.EXAMPLE.TEST/login/account/?x=1"),
        fetch_lines=lambda: [FEED_URL],
    )
    assert result["found"] is True
    assert result["status"] == "confirmed_malicious"


def test_phishing_army_hostname_match():
    index = build_domain_index(["evil-phish.test"])
    result = lookup_phishing_army(
        normalize_url("https://login.evil-phish.test/bank"),
        index=index,
    )
    assert result["found"] is True
    assert result["status"] == "confirmed_malicious"
    assert result["match_type"] in {"hostname", "registered_domain"}


def test_phishing_army_skips_trusted_google():
    index = build_domain_index(["google.com", "www.google.com"])
    result = lookup_phishing_army(
        normalize_url("https://www.google.com/search?q=mail"),
        index=index,
    )
    assert result["found"] is False
    assert result["status"] == "no_match"


def test_isolated_lookup_does_not_need_live_feeds():
    intel = lookup_threat_intelligence(
        "https://ok.example.test/",
        providers={
            "openphish_index": build_feed_index([]),
            "phishtank": lambda url: {"results": {"in_database": False}},
            "urlhaus": lambda url: {"query_status": "no_results"},
            "gsb": lambda url: [],
        },
    )
    names = {row["provider"] for row in intel["providers"]}
    assert "Phishing Army" not in names
    assert intel["overall_status"] == "no_match"


def test_parse_public_feed_formats():
    assert parse_url_lines("# comment\nhttps://a.test/x\nnot-a-url") == ["https://a.test/x"]
    assert "evil.test" in parse_domain_lines("# Phishing Army\nevil.test\nwww.evil.test")


def test_phishtank_unverified_report_is_not_clean():
    result = lookup_phishtank(
        normalize_url("https://central.saude1.lovable.app/"),
        query=lambda url: {"results": {"in_database": True, "verified": False, "phish_id": 99}},
    )
    assert result["found"] is True
    assert result["status"] == "reported_malicious"
    intel = lookup_threat_intelligence(
        "https://central.saude1.lovable.app/",
        providers={
            "openphish_index": build_feed_index([]),
            "phishtank": lambda url: {"results": {"in_database": True, "verified": False}},
            "urlhaus": lambda url: {"query_status": "no_results"},
            "gsb": lambda url: [],
        },
    )
    assert intel["overall_status"] == "reported_malicious"
    decision = calculate_final_risk(
        threat_intelligence=intel,
        heuristic_score=0,
        ml_score=0,
        heuristic_tags=[],
        heuristic_reasons=[],
        url_features=normalize_url("https://central.saude1.lovable.app/"),
    )
    assert decision["safe"] is False
    assert decision["risk_level"] in {"MEDIUM", "HIGH", "CRITICAL"}
    assert decision["classification"] != "CONFIRMED_MALICIOUS"


def test_phishtank_dump_miss_still_flags_unverified_live_report():
    """Suspected PhishTank listings are not in the verified dump."""
    result = lookup_phishtank(
        normalize_url("https://suspected-phish.test/login"),
        index=build_feed_index([]),
        query=lambda url: {"results": {"in_database": True, "verified": "n", "valid": "y"}},
    )
    assert result["found"] is True
    assert result["status"] == "reported_malicious"


def test_phishtank_y_n_flags_are_parsed():
    confirmed = lookup_phishtank(
        normalize_url(FEED_URL),
        query=lambda url: {"results": {"in_database": "y", "verified": "y", "valid": "y"}},
    )
    assert confirmed["status"] == "confirmed_malicious"
    suspected = lookup_phishtank(
        normalize_url("https://suspected-phish.test/login"),
        query=lambda url: {"results": {"in_database": "yes", "verified": "no"}},
    )
    assert suspected["status"] == "reported_malicious"


def test_phishtank_registered_domain_dump_match():
    index = build_feed_index(["https://phish-bank.test/paypal/login"])
    hit = match_against_index(normalize_url("https://login.phish-bank.test/"), index)
    assert hit["match_type"] == "registered_domain"
    sibling = match_against_index(normalize_url("https://innocuous.example.test/home"), build_feed_index([FEED_URL]))
    assert sibling["match_type"] == "no_match"
    result = lookup_phishtank(normalize_url("https://www.phish-bank.test/home"), index=index)
    assert result["found"] is True
    assert result["status"] == "confirmed_malicious"


def test_free_host_health_name_is_flagged():
    from app.services.url_checker import _free_host_signal

    hit = _free_host_signal(normalize_url("https://central.saude1.lovable.app/"))
    assert hit is not None
    assert hit["points"] >= 30
    benign = _free_host_signal(normalize_url("https://my-notes.lovable.app/"))
    assert benign is None
