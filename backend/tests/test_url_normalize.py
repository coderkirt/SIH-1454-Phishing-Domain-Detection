from app.services.url_normalize import normalize_url


def test_normalization_variants_are_stable():
    variants = [
        "https://example.test",
        "https://example.test/",
        "https://EXAMPLE.test/",
        "http://example.test:80/",
        "https://example.test:443/",
        "https://example.test/login#section",
    ]
    assert {normalize_url(item)["hostname"] for item in variants} == {"example.test"}
    assert normalize_url("https://example.test")["normalized_full_url"] == "https://example.test"
    assert normalize_url("https://example.test/")["normalized_full_url"] == "https://example.test"
    assert normalize_url("https://EXAMPLE.test/")["normalized_full_url"] == "https://example.test"
    login = normalize_url("https://example.test/login")
    login_q = normalize_url("https://example.test/login?abc=123")
    assert login["normalized_full_url"] == "https://example.test/login"
    assert login_q["normalized_full_url"] == "https://example.test/login"
    assert login_q["query"] == "abc=123"
    assert login["path"] == "/login"


def test_uppercase_brand_path_kept():
    info = normalize_url("https://PAYPAL.COM/login/")
    assert info["hostname"] == "paypal.com"
    assert info["registered_domain"] == "paypal.com"
    assert info["path"] == "/login"
    assert info["normalized_full_url"] == "https://paypal.com/login"


def test_encoding_and_www():
    info = normalize_url("https://WWW.Example.TEST/a%20b")
    assert info["hostname"] == "www.example.test"
    assert info["registered_domain"] == "example.test"
    assert info["path"] == "/a b"


def test_empty_url_is_invalid():
    info = normalize_url("")
    assert info["valid"] is False
    assert info["normalized_full_url"] == ""
