"""
app/db.py — SQLite lesson history for PathShala Offline (Phase 3.4)

Schema:
  lessons(id, timestamp, language, grade, subject, question, answer, word_count, qc_passed)

All operations are synchronous (SQLite on-device, no server needed).
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/lessons.db")


def _conn() -> sqlite3.Connection:
    """Open (or create) the lessons database and return a connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row  # dict-like rows
    return con


def init_db() -> None:
    """Create tables if they don't exist. Safe to call on every startup."""
    with _conn() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS lessons (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT    NOT NULL,
                language    TEXT    NOT NULL DEFAULT 'English',
                grade       TEXT    NOT NULL DEFAULT 'Grade 10',
                subject     TEXT    NOT NULL DEFAULT 'Mathematics',
                question    TEXT    NOT NULL,
                answer      TEXT    NOT NULL,
                word_count  INTEGER NOT NULL DEFAULT 0,
                qc_passed   INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_lessons_ts ON lessons(timestamp DESC)"
        )
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_lessons_lang ON lessons(language)"
        )


def save_lesson(
    question: str,
    answer: str,
    language: str = "English",
    grade: str = "Grade 10",
    subject: str = "Mathematics",
    word_count: int = 0,
    qc_passed: bool = False,
) -> int:
    """Insert a lesson record. Returns the new row id."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as con:
        cur = con.execute(
            """
            INSERT INTO lessons
                (timestamp, language, grade, subject, question, answer, word_count, qc_passed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (ts, language, grade, subject, question, answer, word_count, int(qc_passed)),
        )
        return cur.lastrowid


def get_lessons(
    limit: int = 50,
    language: str | None = None,
    search: str | None = None,
) -> list[dict]:
    """
    Fetch recent lessons (newest first).
    Optionally filter by language and/or keyword search in question/answer.
    """
    query = "SELECT * FROM lessons"
    params: list = []
    conditions: list[str] = []

    if language:
        conditions.append("language = ?")
        params.append(language)

    if search and search.strip():
        conditions.append("(question LIKE ? OR answer LIKE ?)")
        kw = f"%{search.strip()}%"
        params.extend([kw, kw])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY timestamp DESC, id DESC LIMIT ?"
    params.append(limit)

    with _conn() as con:
        rows = con.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_lesson_count() -> int:
    """Return total number of saved lessons."""
    with _conn() as con:
        return con.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]


def delete_lesson(lesson_id: int) -> None:
    """Delete a single lesson by id."""
    with _conn() as con:
        con.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))


def clear_all_lessons() -> None:
    """Permanently delete all lesson history (for reset)."""
    with _conn() as con:
        con.execute("DELETE FROM lessons")
