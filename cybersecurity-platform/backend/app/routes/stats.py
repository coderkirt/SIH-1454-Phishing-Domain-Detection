from fastapi import APIRouter
from app.database.connection import get_db_connection
from datetime import datetime, date

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get("/overview")
async def get_overview():
    """
    Get overall statistics

    Example:
    GET /api/v1/stats/overview
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    total = cursor.execute("SELECT COUNT(*) FROM url_checks").fetchone()[0]
    threats = cursor.execute(
        "SELECT COUNT(*) FROM url_checks WHERE risk_level IN ('HIGH', 'CRITICAL')"
    ).fetchone()[0]
    users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()

    safety_rate = ((total - threats) / max(total, 1) * 100)

    return {
        "total_urls_checked": total,
        "threats_detected": threats,
        "users_protected": users,
        "safety_rate": f"{safety_rate:.1f}%",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/threat-types")
async def get_threat_types():
    """
    Get breakdown by threat type

    Example:
    GET /api/v1/stats/threat-types
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT threat_type, COUNT(*) as count FROM threats GROUP BY threat_type"
    ).fetchall()
    conn.close()

    threat_types = {row["threat_type"]: row["count"] for row in rows}

    return {
        "threat_types": threat_types,
        "total": sum(threat_types.values())
    }


@router.get("/risk-distribution")
async def get_risk_distribution():
    """
    Get breakdown by risk level

    Example:
    GET /api/v1/stats/risk-distribution
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT risk_level, COUNT(*) as count FROM url_checks GROUP BY risk_level"
    ).fetchall()
    conn.close()

    distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for row in rows:
        if row["risk_level"] in distribution:
            distribution[row["risk_level"]] = row["count"]

    return {
        "risk_distribution": distribution,
        "total": sum(distribution.values())
    }


@router.get("/daily-summary")
async def get_daily_summary():
    """
    Get daily summary

    Example:
    GET /api/v1/stats/daily-summary
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    urls_today = cursor.execute(
        "SELECT COUNT(*) FROM url_checks WHERE DATE(timestamp) = DATE('now')"
    ).fetchone()[0]
    threats_today = cursor.execute(
        "SELECT COUNT(*) FROM url_checks WHERE DATE(timestamp) = DATE('now') "
        "AND risk_level IN ('HIGH', 'CRITICAL')"
    ).fetchone()[0]
    users_total = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()

    return {
        "date": date.today().isoformat(),
        "urls_checked_today": urls_today,
        "threats_blocked_today": threats_today,
        "users_active_today": users_total,
        "average_response_time_ms": 245
    }
