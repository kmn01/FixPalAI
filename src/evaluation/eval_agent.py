"""Evaluation Agent: log interactions to SQLite for analysis."""

import os
import sqlite3
from datetime import datetime
from pathlib import Path

EVAL_DB_PATH = os.getenv("EVAL_DB_PATH", "eval.db")
_schema_initialized = False


def _get_connection() -> sqlite3.Connection:
    """Get SQLite connection and ensure schema exists."""
    global _schema_initialized
    path = Path(EVAL_DB_PATH)
    conn = sqlite3.connect(str(path))
    if not _schema_initialized:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                domain TEXT NOT NULL,
                image_provided INTEGER NOT NULL,
                rating INTEGER,
                notes TEXT
            )
        """)
        conn.commit()
        _schema_initialized = True
    return conn


def log_interaction(
    prompt: str,
    response: str,
    domain: str = "general",
    image_provided: bool = False,
    rating: int | None = None,
    notes: str | None = None,
) -> None:
    """Log an interaction (prompt, response, domain) to the eval database."""
    try:
        conn = _get_connection()
        conn.execute(
            """
            INSERT INTO interactions (created_at, prompt, response, domain, image_provided, rating, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                prompt,
                response,
                domain,
                1 if image_provided else 0,
                rating,
                notes,
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass  # Silent fail - don't break app if eval DB fails
