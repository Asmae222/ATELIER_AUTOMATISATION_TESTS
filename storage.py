"""
storage.py — Persistance SQLite : sauvegarde et lecture des runs
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "runs.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée la table si elle n'existe pas."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                api       TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                passed    INTEGER,
                failed    INTEGER,
                total     INTEGER,
                error_rate REAL,
                latency_avg REAL,
                latency_p95 REAL,
                availability REAL,
                tests_json TEXT
            )
        """)
        conn.commit()


def save_run(run: dict):
    """Enregistre un run complet en base."""
    s = run["summary"]
    with _connect() as conn:
        conn.execute("""
            INSERT INTO runs
              (api, timestamp, passed, failed, total, error_rate,
               latency_avg, latency_p95, availability, tests_json)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            run["api"],
            run["timestamp"],
            s["passed"],
            s["failed"],
            s["total"],
            s["error_rate"],
            s["latency_ms_avg"],
            s["latency_ms_p95"],
            s["availability"],
            json.dumps(run["tests"])
        ))
        conn.commit()


def list_runs(limit: int = 20) -> list:
    """Retourne les N derniers runs (du plus récent au plus ancien)."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "api": row["api"],
            "timestamp": row["timestamp"],
            "summary": {
                "passed": row["passed"],
                "failed": row["failed"],
                "total": row["total"],
                "error_rate": row["error_rate"],
                "latency_ms_avg": row["latency_avg"],
                "latency_ms_p95": row["latency_p95"],
                "availability": row["availability"],
            },
            "tests": json.loads(row["tests_json"])
        })
    return result


def get_last_run() -> dict | None:
    runs = list_runs(limit=1)
    return runs[0] if runs else None
