# Backend, operational database, and scheduling

## Architecture

Phase 11 adds a small read-only application boundary around the research outputs:

1. The pipeline validates data and regenerates reports in dependency order.
2. SQLite stores migrations, pipeline locks, stage progress, failures, and run history.
3. The framework-independent service reads versioned reports and applies query validation.
4. The optional FastAPI layer exposes the service to the future web dashboard.
5. A scheduler entry point can run the same pipeline once or at a local interval.

Report files remain the reproducible analytical artefacts. SQLite is currently an operational
control database, not the long-term analytical warehouse.

## Run the complete pipeline

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.operations
```

This creates `var/cryptopulse.db`, which is intentionally ignored by Git. Structured JSON log lines
show stage start, success, and failure. The operational database records the same lifecycle.

Only one pipeline can own the `main_pipeline` lock. A second run fails clearly. A lock older than
two hours is recovered and its abandoned run is marked failed.

## Run once through the scheduler

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.scheduler --once
```

For repeated local development runs:

```powershell
python -m cryptopulse.scheduler --interval-minutes 60
```

For deployment, use the platform's managed scheduler to invoke `cryptopulse-pipeline`. Managed
scheduling provides better restarts, observability, credentials, and process supervision than a
permanent loop inside the application.

## Start the development API

Install the optional API dependencies:

```powershell
python -m pip install -e ".[api]"
$env:PYTHONPATH="src"
python -m cryptopulse.api
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API documentation.

Endpoints:

- `GET /health`: process health and application version
- `GET /ready`: report availability and data freshness
- `GET /api/v1/indices?asset=bitcoin&resolution=1h`
- `GET /api/v1/events?asset=ethereum`
- `GET /api/v1/research-summary`
- `GET /api/v1/runs?limit=10`

The demonstration reports contain January 2026 synthetic data, so readiness correctly reports
`stale` when evaluated at the current date. Health and readiness are different: a process can be
healthy while its data is stale.

## Database migrations

Numbered SQL migrations are stored under `src/cryptopulse/migrations/`. Applied versions are
recorded in `schema_migrations`, making startup migration idempotent. Phase 11 uses SQLite because
it requires no external service for local development.

PostgreSQL is the intended hosted database when domain observations move from reports into a
concurrent multi-user deployment. That migration should use a production migration tool and retain
the same explicit schema-version discipline.

## Safety and limitations

- The API is read-only but does not yet implement authentication or rate limiting.
- Report replacement is not yet transactional across all files.
- SQLite is not intended for horizontally scaled writers.
- The local scheduler does not provide distributed coordination or automatic process restart.
- Domain data still resides in CSV/JSON reports rather than normalized database tables.
- Live connector credentials and API secrets remain outside the repository.
- Production deployment needs TLS, origin controls, request logs, metrics, backups, and security review.

## Interview explanation

“I separated analytical artefacts from operational state. A versioned pipeline regenerates reports,
while SQLite tracks migrations, locks, stage progress and failures. The API layer is read-only and
framework-independent underneath FastAPI. Health and freshness are separate, and overlapping jobs
are prevented. PostgreSQL and managed scheduling are clear deployment upgrades rather than being
pretended inside a local demo.”
