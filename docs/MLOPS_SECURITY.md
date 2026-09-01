# MLOps, quality, security, and reproducibility

## Phase 14 outcome

Phase 14 adds operational evidence around the existing research pipeline. It does not improve the
synthetic model score or turn the application into a trading system. It makes failures, stale data,
unsafe configuration, component versions, and distribution changes visible and reproducible.

## Monitoring

The pipeline now writes `reports/monitoring/monitoring_summary.json` after all analytical stages.
The report and `/api/v1/monitoring` endpoint expose:

- article warning rate;
- duplicate-article rate;
- mean hourly sentiment shift;
- mean evidence-coverage shift;
- report freshness;
- runtime-configuration warnings;
- the active model and component registry.

The reference in `config/monitoring_baseline.json` is deliberately labelled synthetic. Its purpose
is to test monitoring behaviour. A production baseline must be created from approved representative
data, reviewed for market regimes, and updated through a documented change process.

Run monitoring locally:

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.monitoring --project-root .
python -m cryptopulse.monitoring --validate-environment
```

## Model and experiment lineage

`config/model_registry.json` records the active transparent baseline, optional FinBERT revision,
entity resolver, event classifier, aggregation version, and approval state. Analytical CSV outputs
continue to carry prediction and preprocessing versions at row level.

FinBERT remains an optional comparison. It is blocked from production promotion until upstream
model-licence rights and performance on a representative human-labelled dataset are confirmed.

## Continuous integration

Every push and pull request runs:

- all Python unit tests and Ruff checks;
- monitoring-report generation;
- dashboard lint, unit tests, and production build;
- API and dashboard container builds.

A separate workflow audits Python and npm dependencies weekly and scans Git history for committed
secrets. Dependabot proposes monthly Python, npm, and GitHub Actions updates. These checks reduce
risk but do not replace human code review.

## Local Docker demonstration

Docker is optional. It does not publish the project.

```powershell
docker compose up --build
```

Then open `http://localhost:3000`; the API is available at `http://localhost:8000`. Stop with
`Ctrl+C`. The Compose configuration uses non-root users, read-only filesystems, temporary writable
directories, explicit local CORS, and a health-gated dashboard startup.

The ordinary VS Code demonstration remains supported through `npm run dev`.

## Security, privacy, and licence review

- No API key is committed; `.env` and common key-file extensions are ignored.
- v1.0 stores no user profiles, wallet addresses, exchange credentials, or trading permissions.
- Browser alert preferences remain local and contain no contact information.
- The API is read-only. Before public deployment it still requires authentication, TLS termination,
  request limits, durable secret management, logging retention rules, and a threat-model review.
- Raw or private provider content remains excluded from the repository and CSV exports.
- Project code is MIT licensed; third-party APIs, libraries, model weights, news and trademarks keep
  their own terms.

## Limitations

- Monitoring thresholds are illustrative because the bundled dataset is synthetic and tiny.
- Mean-shift checks cannot identify every type of language, source, concept, or market-regime drift.
- SQLite and local report files are not a high-concurrency production data platform.
- Passing CI or a dependency audit does not prove the absence of vulnerabilities.
- The supplied containers have been designed for reproducibility; a real deployment still needs
  platform-specific infrastructure and security review.
