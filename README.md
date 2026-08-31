# CryptoPulse AI

CryptoPulse AI is an explainable FinTech market-intelligence project for analysing cryptocurrency news sentiment, identifying market-relevant events, and investigating how those signals relate to subsequent price, volume, and volatility changes.

The project begins with Bitcoin and Ethereum. It is designed as a research and decision-support tool, not a trading bot or source of financial advice.

## Why this project exists

Crypto sentiment projects often stop at word clouds or positive/negative labels. Those outputs do not show which asset the sentiment concerns, whether duplicate stories distorted the result, when the information became available, or whether sentiment had any measurable relationship with later market behaviour.

CryptoPulse AI will build a reproducible pipeline from source data to an explainable, time-aware sentiment index and market-impact analysis.

## Planned v1.0 capabilities

- Collect permitted Bitcoin and Ethereum news and OHLCV market data
- Preserve source, publication, retrieval, and processing timestamps
- Validate, clean, and deduplicate incoming articles
- Detect which crypto asset each statement concerns
- Compare a transparent VADER baseline with a financial-language model
- Evaluate models using a human-labelled test set
- Classify market-relevant events such as regulation, security incidents, adoption, and protocol changes
- Produce hourly and daily sentiment indices with evidence coverage
- Compare sentiment with subsequent returns, volume, and volatility using chronological evaluation
- Explain individual classifications and aggregate signals
- Provide an interactive dashboard and downloadable research reports

## Responsible boundary

CryptoPulse AI will not claim that sentiment causes price changes, guarantees returns, or provides personalised investment advice. v1.0 will not execute trades or connect to exchange accounts.

See the [project requirements](docs/PROJECT_REQUIREMENTS.md), [development roadmap](docs/ROADMAP.md), [decision log](docs/DECISIONS.md), and [responsible-use policy](docs/RESPONSIBLE_USE.md).

## Local Python setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

The virtual environment and installed packages are ignored by Git.

## Validate the Phase 2 sample

The repository contains a small, entirely synthetic dataset for testing the contracts. From the repository root:

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.validation data/sample
python -m unittest discover -s tests -v
```

See the [data dictionary](docs/DATA_DICTIONARY.md) and [sample-data policy](data/README.md).

## External connectors

Phase 3 provides a NewsAPI adapter for permitted news metadata and a public Coinbase Exchange adapter for exchange-specific BTC/USD and ETH/USD candles. Automated tests use offline fake responses and never consume live API quota.

See the [connector setup, provenance, and limitations](docs/DATA_CONNECTORS.md). Copy `.env.example` to `.env` only when you are ready to test NewsAPI with your own development key.

## Data quality and deduplication

Phase 4 creates model-ready text without overwriting raw observations, assigns visible quality flags, and groups exact or near-duplicate stories using documented lexical thresholds. The generated reports show every grouping decision.

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.preprocessing
```

See [preprocessing and quality design](docs/PREPROCESSING_AND_QUALITY.md).

## VADER sentiment baseline

Phase 5 evaluates a versioned VADER baseline against target-specific annotations. Reports include class-wise metrics, confusion matrices, deduplicated evaluation, the locked test split, and individual error examples. Synthetic sample metrics verify the pipeline and are not performance claims.

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.sentiment
```

See the [VADER baseline](docs/VADER_BASELINE.md) and [annotation guidelines](docs/ANNOTATION_GUIDELINES.md).

## Financial-language model comparison

Phase 6 adds a revision-pinned, optional FinBERT adapter and compares it with VADER using the
same annotations, deduplication policy, and test split. It also measures multiclass Brier score
and expected calibration error. The synthetic sample validates the pipeline but cannot establish
which model is better.

```powershell
python -m pip install -e ".[ml]"
$env:PYTHONPATH="src"
python -m cryptopulse.finbert
```

See the [FinBERT comparison methodology and licence boundary](docs/FINBERT_COMPARISON.md).

## Asset-specific evidence

Phase 7 resolves explicit Bitcoin and Ethereum aliases, separates contrastive multi-asset clauses,
and supplies target-specific evidence to both sentiment models. Missing and ambiguous targets are
reported rather than hidden.

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.entity_resolution
```

See the [entity-resolution methodology and limitations](docs/ENTITY_RESOLUTION.md).

## Current status

**Phase 7 - Asset-specific sentiment and entity resolution: complete**

Implementation continues in Phase 8 with explainable market-event classification.

## License

Original project code and documentation are licensed under the [MIT License](LICENSE). Third-party datasets, APIs, models, news content, and trademarks remain subject to their own licences and terms.
