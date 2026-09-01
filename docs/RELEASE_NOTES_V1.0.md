# CryptoPulse AI v1.0.0

CryptoPulse AI is an evidence-first cryptocurrency news-sentiment research application for Bitcoin
and Ethereum. It turns permitted news metadata into target-specific sentiment, explainable market
events, coverage-aware indices and chronological research outputs, then exposes them through a
read-only API and responsive dashboard.

## Highlights

- Inspect supporting evidence instead of receiving only a positive/negative label
- Keep model confidence separate from quantity and diversity of evidence
- Downweight duplicate stories and repeated sources
- Preserve point-in-time timestamps to reduce research leakage
- Refuse inferential conclusions when the sample is too small
- Reproduce the stack locally through Python, Node.js or Docker
- Verify changes through CI, dependency audits and secret scanning

## Demonstration data

The repository ships with six synthetic articles, seven target annotations and eight market
candles. These records make the whole pipeline reproducible without API keys. They do not establish
real-world accuracy, predictive value or profitability.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
$env:PYTHONPATH="src"
python -m cryptopulse.operations
npm install
npm run dev
```

Open `http://localhost:3000`.

## Release checklist for the repository owner

1. Push the Phase 15 commit and confirm both GitHub Actions workflows pass.
2. Review screenshots and links on GitHub.
3. Create tag `v1.0.0` from the verified `main` commit.
4. Create a GitHub release titled `CryptoPulse AI v1.0.0` and paste these notes.
5. Do not attach private data, `.env` files, model weights or provider-controlled article text.

## Known limitations

The data is synthetic and tiny; English and BTC/ETH only; FinBERT production rights remain
unconfirmed; drift thresholds are illustrative; the local API is unauthenticated; SQLite is not a
concurrent production warehouse; and no causal or trading claim is supported.
