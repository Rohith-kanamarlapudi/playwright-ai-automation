"""
Selector Memory

Tracks which selectors have historically passed or failed.

The stability score can later be used by the strategy/code-generation
agents to prioritize reliable selectors.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(os.getenv("DB_PATH", "db/runs.db"))

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS selector_memory (

    selector TEXT PRIMARY KEY,

    times_used INTEGER DEFAULT 0,

    times_passed INTEGER DEFAULT 0,

    times_failed INTEGER DEFAULT 0,

    last_seen TEXT

);
"""


def _connect():

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sqlite3.connect(str(DB_PATH))


def init_selector_memory():
    """
    Create selector history table.
    """

    with _connect() as conn:

        conn.execute(CREATE_TABLE)

        conn.commit()


def record_selector_result(
    selector: str,
    passed: bool,
):
    """
    Record whether a selector passed or failed.
    """

    now = datetime.now().isoformat()

    with _connect() as conn:

        conn.execute(
            """
            INSERT INTO selector_memory
            (
                selector,
                times_used,
                times_passed,
                times_failed,
                last_seen
            )
            VALUES (?,1,?,?,?)

            ON CONFLICT(selector)

            DO UPDATE SET

                times_used = times_used + 1,

                times_passed = times_passed + ?,

                times_failed = times_failed + ?,

                last_seen = ?
            """,
            (
                selector,
                int(passed),
                int(not passed),
                now,
                int(passed),
                int(not passed),
                now,
            ),
        )

        conn.commit()


def get_selector_score(
    selector: str,
) -> float:
    """
    Returns selector stability.

    1.0 -> always passed

    0.0 -> always failed

    0.5 -> no history
    """

    with _connect() as conn:

        row = conn.execute(
            """
            SELECT
                times_passed,
                times_failed
            FROM selector_memory
            WHERE selector=?
            """,
            (selector,),
        ).fetchone()

    if row is None:

        return 0.5

    passed, failed = row

    total = passed + failed

    if total == 0:

        return 0.5

    return passed / total


def get_all_selector_scores():
    """
    Useful for debugging and API endpoints.
    """

    with _connect() as conn:

        rows = conn.execute(
            """
            SELECT *
            FROM selector_memory
            ORDER BY times_used DESC
            """
        ).fetchall()

    return rows