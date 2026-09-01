# API reference

The optional FastAPI service exposes read-only local research outputs. Install and start it with:

```powershell
python -m pip install -e ".[api]"
$env:PYTHONPATH="src"
python -m cryptopulse.api
```

Base URL: `http://127.0.0.1:8000`. Interactive OpenAPI documentation is available locally at
`/docs`. v1.0 has no authentication and must not be exposed publicly with private data.

## Endpoints

| Method | Path | Parameters | Purpose |
|---|---|---|---|
| GET | `/health` | none | Process liveness and application version |
| GET | `/ready` | none | Required reports, freshness and last successful run |
| GET | `/api/v1/indices` | `asset`, `resolution` | Sentiment indices and evidence coverage |
| GET | `/api/v1/events` | `asset` | Explainable target event predictions |
| GET | `/api/v1/research-summary` | none | Chronological research status and safeguards |
| GET | `/api/v1/monitoring` | none | Quality, drift, freshness and component registry |
| GET | `/api/v1/runs` | `limit` (1-100) | Recent pipeline execution history |

## Filters

- `asset`: `bitcoin` or `ethereum`
- `resolution`: `1h` or `1d`
- Invalid values return HTTP 422 with a readable detail message.

## Example requests

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/indices?asset=bitcoin&resolution=1h"
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/events?asset=ethereum"
Invoke-RestMethod http://127.0.0.1:8000/api/v1/monitoring
```

## Response interpretation

Numeric CSV-backed values may be represented as strings to preserve report fidelity. Timestamps are
UTC. `status: stale` means reports exist but exceed the freshness threshold; it does not mean the API
process is unhealthy. `inference_status` can deliberately report that tests were not run because the
minimum sample requirement was not met.

## Deployment boundary

Before public deployment add authentication, TLS, request limiting, central secret management,
structured access logs, retention rules and a platform-specific threat review. Do not add exchange
credentials or trade execution to this read-only API.
