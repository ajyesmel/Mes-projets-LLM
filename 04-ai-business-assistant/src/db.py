"""Persistance SQLite : conversations et journal des appels LLM."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "assistant.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS interactions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id   INTEGER NOT NULL REFERENCES conversations(id),
    task              TEXT NOT NULL,
    input_text        TEXT NOT NULL,
    output_text       TEXT,
    model             TEXT NOT NULL,
    latency_ms        INTEGER,
    prompt_tokens     INTEGER,
    completion_tokens INTEGER,
    status            TEXT NOT NULL CHECK (status IN ('ok', 'error')),
    error_message     TEXT,
    created_at        TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def get_connection(db_path=DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path=DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA)


def create_conversation(title: str, db_path=DB_PATH) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO conversations (title, created_at) VALUES (?, ?)",
            (title, _now()),
        )
        return cur.lastrowid


def log_interaction(
    conversation_id: int,
    task: str,
    input_text: str,
    model: str,
    status: str,
    output_text: str | None = None,
    latency_ms: int | None = None,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    error_message: str | None = None,
    db_path=DB_PATH,
) -> int:
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO interactions
               (conversation_id, task, input_text, output_text, model,
                latency_ms, prompt_tokens, completion_tokens,
                status, error_message, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (conversation_id, task, input_text, output_text, model,
             latency_ms, prompt_tokens, completion_tokens,
             status, error_message, _now()),
        )
        return cur.lastrowid


def list_conversations(db_path=DB_PATH) -> list[dict]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM conversations ORDER BY id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_interactions(conversation_id: int, db_path=DB_PATH) -> list[dict]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM interactions WHERE conversation_id = ? ORDER BY id",
            (conversation_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_stats(db_path=DB_PATH) -> dict:
    """Statistiques globales, toutes tâches confondues."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            """SELECT COUNT(*)                                   AS total,
                      COALESCE(SUM(status = 'error'), 0)         AS errors,
                      COALESCE(AVG(latency_ms), 0)               AS avg_latency_ms,
                      COALESCE(SUM(prompt_tokens), 0)            AS prompt_tokens,
                      COALESCE(SUM(completion_tokens), 0)        AS completion_tokens
               FROM interactions"""
        ).fetchone()
    return dict(row)


def get_stats_by_task(db_path=DB_PATH) -> list[dict]:
    """Statistiques détaillées, une ligne par type de tâche."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """SELECT task,
                      COUNT(*)                            AS total,
                      COALESCE(SUM(status = 'error'), 0)  AS errors,
                      COALESCE(AVG(latency_ms), 0)         AS avg_latency_ms
               FROM interactions
               GROUP BY task"""
        ).fetchall()
    return [dict(r) for r in rows]

