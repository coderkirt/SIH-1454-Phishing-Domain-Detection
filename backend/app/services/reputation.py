"""Community reports. One authenticated user cannot flood a domain."""

from datetime import datetime, timedelta
from typing import Dict, Optional
from app.database.connection import get_db_connection


def add_report(user_id: Optional[int], url: str, domain: str, label: str, reason: str = "") -> Dict:
    label = (label or "").lower().strip()
    if label not in {"scam", "risky", "safe"}:
        raise ValueError("label must be scam, risky, or safe")
    if not user_id:
        raise PermissionError("Sign in to submit a community report.")

    conn = get_db_connection()
    cursor = conn.cursor()
    since = (datetime.utcnow() - timedelta(hours=24)).isoformat(sep=" ")
    recent = cursor.execute(
        "SELECT id FROM user_reports WHERE user_id = ? AND url = ? AND created_at >= ?",
        (user_id, url, since),
    ).fetchone()
    if recent:
        conn.close()
        raise ValueError("You already reported this URL in the last 24 hours.")

    today_count = cursor.execute(
        "SELECT COUNT(*) FROM user_reports WHERE user_id = ? AND created_at >= ?",
        (user_id, since),
    ).fetchone()[0]
    if today_count >= 20:
        conn.close()
        raise ValueError("Daily report limit reached.")

    cursor.execute(
        "INSERT INTO user_reports (user_id, url, domain, user_label, reason) VALUES (?, ?, ?, ?, ?)",
        (user_id, url[:500], (domain or "")[:200], label, (reason or "")[:300]),
    )
    cursor.execute(
        """
        INSERT INTO domain_reputation (domain, scam_reports, risky_reports, safe_reports, last_reported)
        VALUES (?, 0, 0, 0, CURRENT_TIMESTAMP)
        ON CONFLICT(domain) DO UPDATE SET last_reported = CURRENT_TIMESTAMP
        """,
        (domain,),
    )
    column = {"scam": "scam_reports", "risky": "risky_reports", "safe": "safe_reports"}[label]
    cursor.execute(
        f"UPDATE domain_reputation SET {column} = {column} + 1, last_reported = CURRENT_TIMESTAMP WHERE domain = ?",
        (domain,),
    )
    conn.commit()
    conn.close()
    return get_reputation(domain)


def get_reputation(domain: str) -> Dict:
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM domain_reputation WHERE domain = ?",
        (domain,),
    ).fetchone()
    conn.close()
    if not row:
        return {
            "domain": domain,
            "total_reports": 0,
            "scam_reports": 0,
            "risky_reports": 0,
            "safe_reports": 0,
            "reputation_score": 0,
            "community_trust": "Unknown",
            "summary": "No community reports yet.",
        }
    data = dict(row)
    total = data["scam_reports"] + data["risky_reports"] + data["safe_reports"]
    data["total_reports"] = total
    if total == 0:
        data["reputation_score"] = 0
        data["community_trust"] = "Unknown"
        data["summary"] = "No community reports yet."
        return data
    # Scam-heavy domains raise risk; this is not proof.
    data["reputation_score"] = int(min(100, (data["scam_reports"] * 70 + data["risky_reports"] * 40) / max(total, 1)))
    if total >= 5 and data["scam_reports"] / total >= 0.7:
        data["community_trust"] = "Low"
        data["summary"] = "Community reports indicate elevated risk. This is not proof."
    elif total >= 3:
        data["community_trust"] = "Mixed"
        data["summary"] = "Some community reports exist. Treat them as one signal only."
    else:
        data["community_trust"] = "Limited"
        data["summary"] = "Too few independent reports to treat this as strong evidence."
    return data
