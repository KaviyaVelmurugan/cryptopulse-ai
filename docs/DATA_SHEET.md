# Data sheet

## Dataset summary

The public repository contains a small synthetic fixture designed to exercise CryptoPulse AI's
contracts and pipeline. It is not a historical market dataset and cannot support performance claims.

| File | Rows | Purpose |
|---|---:|---|
| `data/sample/news_articles.csv` | 6 | News provenance, multi-asset text and duplicate cases |
| `data/sample/annotations.csv` | 7 | Target-specific human-style sentiment/event labels |
| `data/sample/market_candles.csv` | 8 | Point-in-time BTC/USD and ETH/USD OHLCV alignment |

## Assets and time

- Assets: Bitcoin and Ethereum
- Market pairs: BTC/USD and ETH/USD
- Timestamps: UTC ISO 8601
- Preserved time concepts: publication, retrieval, processing, prediction and market-window time
- Language: English synthetic text

## Creation and consent

The fixture is original synthetic data created for software verification. It contains no real
person's private data, wallet address, exchange credentials or user profile. It should not be
interpreted as factual reporting about a real market event.

## Permitted use

- Contract validation and automated tests
- Demonstrating cleaning, duplicate grouping, target evidence and aggregation
- Reproducing dashboard and monitoring behaviour
- Education and portfolio review under the repository's MIT licence

## Prohibited interpretation

- Real-world model accuracy
- Backtested or expected investment performance
- Evidence that a sentiment signal predicts or causes returns
- A representative sample of crypto language, sources, countries or market regimes

## Quality controls

- Required fields and enumerations are versioned and validated
- UTC ordering prevents retrieval-before-publication and other invalid time sequences
- Duplicate and malformed observations receive explicit flags
- Dataset foreign keys and target relationships are checked
- Raw inputs are not overwritten by cleaned or model-generated fields

## Live-data extensions

NewsAPI and Coinbase adapters are available, but live collection is not committed. Anyone extending
the dataset must review provider terms, retention and redistribution rights, privacy, timestamp
quality, source representation and annotation consent before publication.

## Known limitations

- Very small and synthetic
- English only
- Only BTC and ETH
- No social-media, on-chain, order-book or derivatives data
- No adversarial, sarcasm-heavy or multilingual benchmark
- No representative production drift baseline

## Maintenance

Any change to the fixture must preserve deterministic tests, update this sheet when row counts or
scope change, and avoid introducing third-party text without explicit redistribution rights.
