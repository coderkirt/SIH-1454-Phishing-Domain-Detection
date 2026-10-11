from app.search import assess_facts


def test_erp_host_uses_login_portal_rule():
    result = assess_facts({
        "url": "https://erp.psit.ac.in/",
        "hostname": "erp.psit.ac.in",
        "registered_domain": "psit.ac.in",
        "path": "/",
        "login_portal": True,
        "lookalike": False,
        "https": True,
        "heuristic_tags": [],
        "local_activity": {"status": "observed", "scans": 2},
    })
    assert result["status"] == "ok"
    assert result["rule_id"] == "login-portal-hygiene"
    assert result["suspicion_score"] == 0
