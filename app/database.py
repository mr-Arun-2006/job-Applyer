from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from app.config import JOB_APPLIER_DB


DB_PATH = Path(JOB_APPLIER_DB)


def _connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_key TEXT NOT NULL UNIQUE,
                source TEXT NOT NULL,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                location TEXT,
                official_url TEXT,
                application_url TEXT,
                description TEXT NOT NULL,
                match_score REAL,
                discovered_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_key TEXT NOT NULL,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                application_url TEXT NOT NULL,
                resume_path TEXT,
                cover_letter_path TEXT,
                status TEXT NOT NULL,
                error TEXT,
                applied_at TEXT,
                UNIQUE(job_key)
            );
            """
        )


def make_job_key(job: dict) -> str:
    raw = "|".join(
        [
            str(job.get("source", "")),
            str(job.get("source_job_id", "")),
            str(job.get("company", "")),
            str(job.get("title", "")),
            str(job.get("application_url") or job.get("official_url") or ""),
        ]
    ).strip().lower()
    return hashlib.sha256(raw.encode()).hexdigest()


def save_jobs(jobs: Iterable[dict]) -> int:
    now = datetime.now(UTC).isoformat()
    inserted = 0

    with _connection() as conn:
        for job in jobs:
            key = make_job_key(job)
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO jobs
                (job_key, source, company, title, location, official_url,
                 application_url, description, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    key,
                    job.get("source", ""),
                    job.get("company", ""),
                    job.get("title", ""),
                    job.get("location"),
                    job.get("official_url"),
                    job.get("application_url"),
                    job.get("description", ""),
                    now,
                ),
            )
            inserted += int(cur.rowcount > 0)

    return inserted


def has_application(job: dict) -> bool:
    key = make_job_key(job)

    with _connection() as conn:
        row = conn.execute(
            "SELECT status FROM applications WHERE job_key = ? LIMIT 1",
            (key,),
        ).fetchone()

    return bool(row and row["status"] in {"SUBMITTED", "APPLIED"})


def record_application(
    job: dict,
    resume_path: str | None,
    cover_letter_path: str | None,
    status: str,
    error: str | None = None,
) -> None:
    key = make_job_key(job)

    with _connection() as conn:
        conn.execute(
            """
            INSERT INTO applications
            (job_key, company, title, application_url, resume_path,
             cover_letter_path, status, error, applied_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_key) DO UPDATE SET
                resume_path=excluded.resume_path,
                cover_letter_path=excluded.cover_letter_path,
                status=excluded.status,
                error=excluded.error,
                applied_at=excluded.applied_at
            """,
            (
                key,
                job.get("company", ""),
                job.get("title", ""),
                job.get("application_url") or job.get("official_url") or "",
                resume_path,
                cover_letter_path,
                status,
                error,
                datetime.now(UTC).isoformat(),
            ),
        )
