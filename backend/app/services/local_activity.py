"""PhishEye's own 30-day scan and report counts for a URL or domain.

These are not global website traffic. Zero activity is unknown, not safe.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

from app.database.connection import get_db_connection
from app.services.url_normalize import normalize_url
from app.services.visit_service import count_visits_30d


WINDOW_DAYS = 30


def empty_activity(domain: str = "") -> Dict:
    return {
        "window_days": WINDOW_DAYS,
        "domain": domain or "",
        "normalized_url": "",
        "scans": 0,
        "signed_in_users": 0,
        "high_risk_scans": 0,
        "scam_reports": 0,
        "risky_reports": 0,
        "safe_reports": 0,
        "opens": 0,
        "users_opened": 0,
        "this_browser_opens": 0,
        "this_browser_status": "unavailable",
        "status": "unknown",
    }


def get_local_activity_30d(
    url: str = "",
    domain: str = "",
    *,
    conn=None,
    now: Optional[datetime] = None,
    this_browser_opens: Optional[int] = None,
    this_browser_status: Optional[str] = None,
) -> Dict:
    """Count local scans and user reports in the last 30 days."""
    info = normalize_url(url or "")
    registered = (domain or info.get("registered_domain") or "").strip().lower()
    normalized = (info.get("normalized_full_url") or "").strip()
    raw = (info.get("original") or url or "").strip()
    payload = empty_activity(registered)
    payload["normalized_url"] = normalized or raw
    visits = {"opens": 0, "users_opened": 0}

    own_conn = conn is None
    if own_conn:
        conn = get_db_connection()
    try:
        since = (now or datetime.utcnow()) - timedelta(days=WINDOW_DAYS)
        since_s = since.isoformat(sep=" ", timespec="seconds")
        host_http = f"http://{registered}" if registered else ""
        host_https = f"https://{registered}" if registered else ""
        www_http = f"http://www.{registered}" if registered else ""
        www_https = f"https://www.{registered}" if registered else ""

        scan_row = conn.execute(
            """
            SELECT
                COUNT(*) AS scans,
                COUNT(DISTINCT CASE WHEN user_id IS NOT NULL THEN user_id END) AS signed_in_users,
                SUM(CASE WHEN UPPER(risk_level) IN ('HIGH', 'CRITICAL') THEN 1 ELSE 0 END) AS high_risk_scans
            FROM url_checks
            WHERE timestamp >= ?
              AND (
                    (? != '' AND (url = ? OR url = ?))
                 OR (? != '' AND (
                        url = ? OR url = ? OR url = ? OR url = ?
                     OR url LIKE ? || '/%'
                     OR url LIKE ? || '/%'
                     OR url LIKE ? || '/%'
                     OR url LIKE ? || '/%'
                 ))
              )
            """,
            (
                since_s,
                raw, raw, normalized,
                registered,
                host_http, host_https, www_http, www_https,
                host_http, host_https, www_http, www_https,
            ),
        ).fetchone()

        extra_scans = conn.execute(
            """
            SELECT
                COUNT(*) AS scans,
                SUM(CASE WHEN UPPER(classification) IN ('HIGH', 'CRITICAL') THEN 1 ELSE 0 END) AS high_risk_scans
            FROM extracted_links
            WHERE scan_id IN (SELECT id FROM content_scans WHERE created_at >= ?)
              AND (
                    (? != '' AND url = ?)
                 OR (? != '' AND (
                        domain = ?
                     OR url = ? OR url = ? OR url = ? OR url = ?
                     OR url LIKE ? || '/%'
                     OR url LIKE ? || '/%'
                     OR url LIKE ? || '/%'
                     OR url LIKE ? || '/%'
                 ))
              )
            """,
            (
                since_s,
                normalized or raw, normalized or raw,
                registered, registered,
                host_http, host_https, www_http, www_https,
                host_http, host_https, www_http, www_https,
            ),
        ).fetchone()

        try:
            visits = count_visits_30d(url, registered, conn=conn, now=now)
        except Exception:
            visits = {"opens": 0, "users_opened": 0}

        reports = conn.execute(
            """
            SELECT
                SUM(CASE WHEN LOWER(user_label) = 'scam' THEN 1 ELSE 0 END) AS scam_reports,
                SUM(CASE WHEN LOWER(user_label) = 'risky' THEN 1 ELSE 0 END) AS risky_reports,
                SUM(CASE WHEN LOWER(user_label) = 'safe' THEN 1 ELSE 0 END) AS safe_reports
            FROM user_reports
            WHERE created_at >= ?
              AND (
                    (? != '' AND (url = ? OR url = ?))
                 OR (? != '' AND domain = ?)
              )
            """,
            (since_s, raw, raw, normalized, registered, registered),
        ).fetchone()
    finally:
        if own_conn:
            conn.close()

    scans = int((scan_row["scans"] if scan_row else 0) or 0) + int((extra_scans["scans"] if extra_scans else 0) or 0)
    high_risk = int((scan_row["high_risk_scans"] if scan_row else 0) or 0) + int(
        (extra_scans["high_risk_scans"] if extra_scans else 0) or 0
    )
    payload.update({
        "scans": scans,
        "signed_in_users": int((scan_row["signed_in_users"] if scan_row else 0) or 0),
        "high_risk_scans": high_risk,
        "scam_reports": int((reports["scam_reports"] if reports else 0) or 0),
        "risky_reports": int((reports["risky_reports"] if reports else 0) or 0),
        "safe_reports": int((reports["safe_reports"] if reports else 0) or 0),
        "opens": int(visits.get("opens") or 0),
        "users_opened": int(visits.get("users_opened") or 0),
    })
    if this_browser_status in {"observed", "unknown", "unavailable"}:
        payload["this_browser_status"] = this_browser_status
        payload["this_browser_opens"] = max(0, int(this_browser_opens or 0))
    elif this_browser_opens is not None:
        opens_here = max(0, int(this_browser_opens))
        payload["this_browser_opens"] = opens_here
        payload["this_browser_status"] = "observed" if opens_here else "unknown"
    observed = (
        payload["scans"]
        or payload["scam_reports"]
        or payload["risky_reports"]
        or payload["safe_reports"]
        or payload["opens"]
        or payload["this_browser_opens"]
    )
    payload["status"] = "observed" if observed else "unknown"
    return payload
