"""
Thin SQLite wrapper for run history.
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

DB_PATH = Path(os.getenv("DB_PATH", "db/runs.db"))


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    from db.models import CREATE_RUNS_TABLE

    with _conn() as conn:
        conn.execute(CREATE_RUNS_TABLE)
        conn.commit()


def start_run(
    target_url: str = None,
    llm_provider: str = None,
    llm_model: str = None,
) -> str:
    """
    Create a new run record and return its run_id.
    """
    run_id = str(uuid.uuid4())

    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO runs
            (run_id, target_url, llm_provider, llm_model, started_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                run_id,
                target_url,
                llm_provider,
                llm_model,
                datetime.now().isoformat(),
            ),
        )
        conn.commit()

    return run_id


def finish_run(run_id: str, status: str, result: dict):
    """
    Update a run record when the pipeline finishes.
    """

    with _conn() as conn:
        conn.execute(
            """
            UPDATE runs SET
                status=?,
                finished_at=?,
                duration_seconds=?,
                pages_crawled=?,
                selectors_found=?,
                tests_generated=?,
                tests_passed=?,
                tests_failed=?,
                regen_count=?,
                generated_code=?,
                generated_yaml=?,
                review_notes=?,
                edge_cases=?
            WHERE run_id=?
            """,
            (
                status,
                datetime.now().isoformat(),
                result.get("duration_seconds"),
                result.get("pages_crawled", 0),
                result.get("selectors_found", 0),
                result.get("tests_generated", 0),
                result.get("tests_passed", 0),
                result.get("tests_failed", 0),
                result.get("regen_count", 0),
                result.get("generated_code", ""),
                result.get("generated_yaml", ""),
                result.get("review_notes", ""),
                json.dumps(result.get("edge_cases", [])),
                run_id,
            ),
        )

        conn.commit()


def get_runs(limit: int = 20) -> list:
    """
    Return the latest N runs.
    """

    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM runs ORDER BY started_at DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_run(run_id: str) -> dict:
    """
    Return one run by ID.
    """

    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM runs WHERE run_id=?",
            (run_id,),
        ).fetchone()

    return dict(row) if row else {}