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

## Current status

**Phase 1 - Product definition: complete**

Implementation begins in Phase 2 with the repository structure, data contracts, and deterministic sample data.

## License

Original project code and documentation are licensed under the [MIT License](LICENSE). Third-party datasets, APIs, models, news content, and trademarks remain subject to their own licences and terms.
