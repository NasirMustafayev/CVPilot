"""
SQLite persistence for users (hackathon-friendly, no external DB).
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(os.getenv("DATABASE_PATH", Path(__file__).parent / "cvpilot.db"))


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                display_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('hr', 'candidate')),
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                workspace TEXT NOT NULL CHECK (workspace IN ('hr', 'candidate')),
                cv_filename TEXT NOT NULL,
                candidate_name TEXT,
                role_title TEXT NOT NULL,
                job_description TEXT NOT NULL,
                overall_score REAL NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_analyses_user_workspace
            ON analyses (user_id, workspace, created_at DESC)
            """
        )


def get_user_by_email(email: str) -> Optional[dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash, display_name, role, created_at FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, email, display_name, role, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def create_user(
    email: str,
    password_hash: str,
    display_name: str,
    role: str,
) -> dict[str, Any]:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (email, password_hash, display_name, role, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (email.strip().lower(), password_hash, display_name.strip(), role, created_at),
        )
        user_id = cursor.lastrowid
    user = get_user_by_id(user_id)
    if not user:
        raise RuntimeError("Failed to create user")
    return user


def save_analysis(
    user_id: int,
    workspace: str,
    cv_filename: str,
    role_title: str,
    job_description: str,
    overall_score: float,
    result: dict[str, Any],
    candidate_name: Optional[str] = None,
) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    payload = json.dumps(result)
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analyses (
                user_id, workspace, cv_filename, candidate_name,
                role_title, job_description, overall_score, result_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                workspace,
                cv_filename,
                candidate_name,
                role_title,
                job_description,
                overall_score,
                payload,
                created_at,
            ),
        )
        return int(cursor.lastrowid)


def list_analyses(
    user_id: int,
    workspace: Optional[str] = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    query = """
        SELECT id, workspace, cv_filename, candidate_name, role_title,
               overall_score, created_at
        FROM analyses
        WHERE user_id = ?
    """
    params: list[Any] = [user_id]
    if workspace:
        query += " AND workspace = ?"
        params.append(workspace)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_analysis(user_id: int, analysis_id: int) -> Optional[dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT id, user_id, workspace, cv_filename, candidate_name,
                   role_title, job_description, overall_score, result_json, created_at
            FROM analyses
            WHERE id = ? AND user_id = ?
            """,
            (analysis_id, user_id),
        ).fetchone()
    if not row:
        return None
    data = dict(row)
    data["result"] = json.loads(data.pop("result_json"))
    return data


def delete_analyses(user_id: int, workspace: Optional[str] = None) -> int:
    with get_db() as conn:
        if workspace:
            cursor = conn.execute(
                "DELETE FROM analyses WHERE user_id = ? AND workspace = ?",
                (user_id, workspace),
            )
        else:
            cursor = conn.execute(
                "DELETE FROM analyses WHERE user_id = ?",
                (user_id,),
            )
        return cursor.rowcount
