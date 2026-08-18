import sqlite3
import os

# Store threats.db inside the backend folder no matter where the app is started from
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_URL = os.path.join(BACKEND_DIR, "threats.db")


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize database with tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS url_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        url VARCHAR(500) NOT NULL,
        risk_level VARCHAR(20),
        risk_score FLOAT,
        ml_confidence FLOAT DEFAULT 0.0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS threats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        threat_type VARCHAR(50),
        threat_data TEXT,
        severity VARCHAR(20),
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_url ON url_checks(url)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON url_checks(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON url_checks(timestamp)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS content_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        source_type VARCHAR(30),
        url VARCHAR(500),
        risk_level VARCHAR(20),
        risk_score FLOAT,
        scam_risk FLOAT,
        confidence FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS extracted_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER,
        url VARCHAR(500),
        domain VARCHAR(200),
        risk_score FLOAT,
        classification VARCHAR(20),
        FOREIGN KEY(scan_id) REFERENCES content_scans(id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        url VARCHAR(500),
        domain VARCHAR(200),
        user_label VARCHAR(20),
        reason VARCHAR(300),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS domain_reputation (
        domain VARCHAR(200) PRIMARY KEY,
        scam_reports INTEGER DEFAULT 0,
        risky_reports INTEGER DEFAULT 0,
        safe_reports INTEGER DEFAULT 0,
        last_reported TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scan_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER,
        helpful INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_url ON user_reports(url)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_user ON user_reports(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_domain ON user_reports(domain)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_created ON user_reports(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_created ON content_scans(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_source ON content_scans(source_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_risk ON content_scans(risk_score)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_extracted_domain ON extracted_links(domain)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_extracted_url ON extracted_links(url)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_extracted_class ON extracted_links(classification)")

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
