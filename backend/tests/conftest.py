import os

# Pytest must not download OpenPhish / URLhaus / PhishTank dumps on import.
os.environ["PHISHEYE_SKIP_FEED_WARMUP"] = "1"

import pytest


@pytest.fixture(autouse=True)
def reset_intel_state(monkeypatch):
    from app.services import threat_intel
    from app.services import feed_cache

    def blocked(*_args, **_kwargs):
        raise RuntimeError("live feed download blocked in tests")

    threat_intel._lookup_cache.clear()
    threat_intel._openphish_state.update({"fetched_at": 0.0, "index": None, "error": None})
    feed_cache.reset_feed_memory()
    monkeypatch.setattr(threat_intel, "ENABLE_ONLINE_CHECKS", False)
    monkeypatch.setattr("app.services.feed_cache.download_text", blocked)
    yield
