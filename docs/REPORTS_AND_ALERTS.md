# Reports and informational alerts

## What Phase 13 adds

Phase 13 makes CryptoPulse AI results easier to share and revisit. The web dashboard now provides a
derived-data CSV, a print-ready research report, configurable evidence conditions, and a short alert
evaluation history.

## CSV export

**Download CSV** creates `cryptopulse-derived-sentiment-index.csv` from the index currently loaded
by the dashboard. It contains windows, asset, resolution, sentiment, evidence counts, coverage,
leading event, and aggregation version. It deliberately excludes article text and provider-owned
content.

The export records analytical observations, not trade signals. A recipient still needs the project
methodology and data-state label to interpret it correctly.

## PDF report

**Print / Save PDF** opens the operating system's print dialog. Choose **Save as PDF** to create a
portable report. Print-specific styles remove interactive controls, retain the evidence and
research-warning sections, use a light background, and reduce page breaks inside cards.

This approach produces a downloadable local file without uploading report contents to another
service.

## Informational alert rules

An alert rule has three transparent conditions:

1. minimum absolute sentiment magnitude;
2. minimum evidence coverage;
3. an optional required event category.

Every selected condition must be met. The resulting record states the observed values and time.
The rule is saved only in browser local storage; it is not transmitted to the backend and does not
send email, SMS, push, or trading instructions.

The phrase **research signal observed** means that a configured threshold matched historical or
current input data. It does not mean that price will rise or fall.

## Verification

Unit tests cover CSV field selection, alert threshold evaluation, and responsible wording. The
dashboard is also checked through a production build and interactive browser review.

## Limitations and Phase 14 upgrades

- Alert evaluation occurs only while the dashboard is open.
- Alert history is derived from the currently loaded dataset rather than persisted as an audit log.
- Browser-local rules do not sync across devices.
- PDF pagination depends slightly on the browser and operating system.
- No identity, delivery preferences, rate limiting, or notification consent model exists yet.

Phase 14 can add authenticated server-side rules, durable audit records, delivery controls,
observability, automated accessibility checks, and deployment security review.
