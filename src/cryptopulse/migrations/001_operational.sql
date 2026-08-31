CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('running', 'succeeded', 'failed')),
    current_stage TEXT NOT NULL,
    error_message TEXT,
    report_root TEXT NOT NULL,
    application_version TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started_at
ON pipeline_runs(started_at DESC);

CREATE TABLE IF NOT EXISTS pipeline_locks (
    lock_name TEXT PRIMARY KEY,
    owner_run_id TEXT NOT NULL,
    acquired_at TEXT NOT NULL
);
