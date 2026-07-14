"""
SQLite schema for pipeline run history.
"""

CREATE_RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    run_id TEXT UNIQUE NOT NULL,

    target_url TEXT,

    llm_provider TEXT,

    llm_model TEXT,

    started_at TEXT NOT NULL,

    finished_at TEXT,

    status TEXT DEFAULT 'running',

    pages_crawled INTEGER DEFAULT 0,

    selectors_found INTEGER DEFAULT 0,

    tests_generated INTEGER DEFAULT 0,

    tests_passed INTEGER DEFAULT 0,

    tests_failed INTEGER DEFAULT 0,

    regen_count INTEGER DEFAULT 0,

    duration_seconds REAL,

    generated_code TEXT,

    generated_yaml TEXT,

    review_notes TEXT,

    edge_cases TEXT
);
"""