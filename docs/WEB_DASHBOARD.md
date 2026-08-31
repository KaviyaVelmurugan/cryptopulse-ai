# Web dashboard

## Purpose

Phase 12 turns the analytical outputs from earlier phases into an evidence-first research
interface. A reviewer can switch between Bitcoin and Ethereum, select hourly or daily windows,
inspect sentiment and evidence coverage, see the events behind a signal, and understand why market
inference may be withheld.

The dashboard is for research and decision support. It does not forecast guaranteed returns,
recommend trades, or connect to an exchange account.

## Technology choices

- **Next.js App Router:** supplies the web application structure and a production build path.
- **React:** manages the interactive asset and resolution controls.
- **TypeScript:** keeps API responses and dashboard state aligned with explicit contracts.
- **CSS and SVG:** provide a lightweight responsive interface and accessible chart without a large
  visualisation dependency.
- **Vitest:** verifies the deterministic transformation helpers used by the chart and metrics.

## Run the demonstration

From the repository root:

```powershell
npm install
npm run dev
```

Open `http://localhost:3000`. Without additional configuration, the interface displays committed
synthetic data and shows a **Synthetic demo** status. This is intentional: the repository can be
reviewed without API keys or live services, while never implying that the sample is current market
data.

## Connect the Phase 11 API

Use two PowerShell terminals from the repository root.

Terminal 1:

```powershell
python -m pip install -e ".[api]"
$env:PYTHONPATH="src"
python -m cryptopulse.api
```

Terminal 2:

```powershell
$env:NEXT_PUBLIC_API_BASE_URL="http://127.0.0.1:8000"
npm run dev
```

The dashboard requests `/api/v1/indices`, `/api/v1/events`, and
`/api/v1/research-summary`. If all requests succeed, the status changes to **API connected**. If a
configured API is unavailable, the interface returns to its labelled demonstration state. Local
browser origins are allowed by default; deployed origins must be set explicitly through
`CRYPTOPULSE_ALLOWED_ORIGINS`.

## Information design

- **Sentiment direction** remains separate from **evidence coverage**.
- The timeline exposes both measures instead of turning them into one unexplained score.
- Event cards show supporting text, matched terms, and evidence strength.
- The research panel suppresses inferential results when the minimum sample requirement is unmet.
- Data state and timestamp remain visible at the top of the analysis.

## Accessibility and responsive behaviour

Controls use native buttons, pressed-state attributes, visible focus styles, and descriptive group
labels. The chart includes a title and description for assistive technology. Layouts collapse for
smaller screens without removing research warnings or evidence details.

## Current limitations

- The committed dataset is synthetic and deliberately small.
- The chart displays analytical sentiment and coverage, not a full price overlay yet.
- API mode expects the Phase 11 generated reports to exist locally.
- The dashboard has helper-unit tests, but a full automated browser accessibility audit is planned
  for Phase 14.
- Authentication, hosted caching, PostgreSQL, and production observability remain future work.

These limitations are visible product boundaries, not hidden defects. Phase 13 adds downloadable
research outputs and responsibly worded informational alerts.
