import sqlite3
from datetime import datetime

DB_NAME = "quickfix.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS findings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_name TEXT,
        finding_title TEXT,
        severity TEXT,
        score REAL,
        affected_url TEXT,
        description TEXT,
        evidence TEXT,
        language TEXT,
        ai_result TEXT,
        status TEXT,
        created_at TEXT
    )
""")

    conn.commit()
    conn.close()


def insert_finding(application_name, finding_title, severity, score, affected_url,
                   description, evidence, language, ai_result):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO findings (
            application_name,
            finding_title,
            severity,
            score,
            affected_url,
            description,
            evidence,
            language,
            ai_result,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        application_name,
        finding_title,
        severity,
        score,
        affected_url,
        description,
        evidence,
        language,
        ai_result,
        "Open",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_all_findings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM findings ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows


def update_status(finding_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE findings
        SET status = ?
        WHERE id = ?
    """, (status, finding_id))

    conn.commit()
    conn.close()