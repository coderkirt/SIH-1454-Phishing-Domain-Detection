from app.services.ssl_certs import inspect_tls
from app.services.url_checker import URLChecker
from app.services.warnings import build_technical_view


def test_tls_skips_http():
    result = inspect_tls("http://example.com")
    assert result["status"] == "http"
    assert result["checked"] is True


def test_tls_blocks_private_https():
    result = inspect_tls("https://127.0.0.1")
    assert result["status"] == "blocked"


def test_url_checker_includes_tls_fields():
    checker = URLChecker()
    result = checker.analyze("http://192.168.1.1/login")
    assert "tls" in result["details"]
    tech = build_technical_view(result)
    assert "tls_status" in tech
    assert "tls_label" in tech
