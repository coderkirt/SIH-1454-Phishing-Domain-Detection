from app.services.rag_client import collect_facts


def test_sso_host_is_login_portal():
    facts = collect_facts(
        "https://sso.campus.edu/cas",
        features={"hostname": "sso.campus.edu", "registered_domain": "campus.edu", "path": "/cas"},
    )
    assert facts["login_portal"] is True


def test_plain_marketing_host_is_not_login_portal():
    facts = collect_facts(
        "https://news.example.com/about",
        features={"hostname": "news.example.com", "registered_domain": "example.com", "path": "/about"},
    )
    assert facts["login_portal"] is False
    assert facts["lookalike"] is False
