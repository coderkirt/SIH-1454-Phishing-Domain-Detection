"""Record PhishEye page opens. Dedup same client + URL within 10 minutes."""

from datetime import datetime, timedelta
from typing import Dict, Optional

from app.database.connection import get_db_connection
from app.services.url_normalize import normalize_url

DEDUP_MINUTES = 10
WINDOW_DAYS = 30


def record_visit(
    url: str,
    client_id: str,
    user_id: Optional[int] = None,
    *,
    conn=None,
    now: Optional[datetime] = None,
) -> Dict:
    client = (client_id or "").strip()
    if len(client) < 8 or len(client) > 80:
        return {"recorded": False, "deduped": False, "reason": "invalid_client_id"}

    raw = (url or "").strip()
    if raw.lower().startswith(("javascript:", "data:", "file:", "about:")):
        return {"recorded": False, "deduped": False, "reason": "invalid_url"}
    info = normalize_url(raw)
    normalized = (info.get("normalized_full_url") or raw or "").strip()
    if not normalized or not normalized.lower().startswith(("http://", "https://")):
        return {"recorded": False, "deduped": False, "reason": "invalid_url"}
    domain = (info.get("registered_domain") or "").strip().lower()
    stamp = now or datetime.utcnow()
    since = (stamp - timedelta(minutes=DEDUP_MINUTES)).isoformat(sep=" ", timespec="seconds")
    opened_at = stamp.isoformat(sep=" ", timespec="seconds")

    own_conn = conn is None
    if own_conn:
        conn = get_db_connection()
    try:
        existing = conn.execute(
            """
            SELECT id FROM url_visits
            WHERE client_id = ? AND normalized_url = ? AND opened_at >= ?
            ORDER BY id DESC LIMIT 1
            """,
            (client, normalized, since),
        ).fetchone()
        if existing:
            return {"recorded": False, "deduped": True, "visit_id": existing["id"], "normalized_url": normalized}

        cursor = conn.execute(
            """
            INSERT INTO url_visits (normalized_url, registered_domain, client_id, user_id, opened_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (normalized[:500], domain[:200], client, user_id, opened_at),
        )
        if own_conn:
            conn.commit()
        return {
            "recorded": True,
            "deduped": False,
            "visit_id": cursor.lastrowid,
            "normalized_url": normalized,
        }
    finally:
        if own_conn:
            conn.close()


def count_visits_30d(
    url: str = "",
    domain: str = "",
    *,
    conn=None,
    now: Optional[datetime] = None,
) -> Dict:
    info = normalize_url(url or "")
    registered = (domain or info.get("registered_domain") or "").strip().lower()
    normalized = (info.get("normalized_full_url") or "").strip()
    since = ((now or datetime.utcnow()) - timedelta(days=WINDOW_DAYS)).isoformat(sep=" ", timespec="seconds")

    own_conn = conn is None
    if own_conn:
        conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS opens,
                COUNT(DISTINCT client_id) AS users_opened
            FROM url_visits
            WHERE opened_at >= ?
              AND (
                    (? != '' AND normalized_url = ?)
                 OR (? != '' AND registered_domain = ?)
              )
            """,
            (since, normalized, normalized, registered, registered),
        ).fetchone()
    finally:
        if own_conn:
            conn.close()

    return {
        "opens": int((row["opens"] if row else 0) or 0),
        "users_opened": int((row["users_opened"] if row else 0) or 0),
    }
