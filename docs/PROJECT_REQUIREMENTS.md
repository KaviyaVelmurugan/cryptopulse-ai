# Project requirements

## 1. Product definition

**Product name:** CryptoPulse AI

**Category:** FinTech / crypto market intelligence / natural-language processing

**Primary user:** A market researcher, risk analyst, or informed crypto investor who wants to understand news sentiment without treating it as automatic trading advice.

### Problem

Cryptocurrency markets produce large volumes of fast-moving and repeated news. Simple sentiment notebooks usually analyse a small snapshot, apply general-language sentiment to an entire article, and present word clouds without validating financial meaning or subsequent market behaviour.

### Proposed solution

CryptoPulse AI collects permitted news and market observations, validates and deduplicates them, identifies the affected crypto asset and event, calculates explainable sentiment, aggregates it over time, and evaluates its relationship with later price, volume, and volatility changes.

### Product promise

> Help a user understand what the crypto news environment is saying about an asset, which events and sources drive that assessment, how reliable the available evidence is, and what the historical market relationship does or does not support.

## 2. Objectives

1. Move beyond document-level positive and negative labels to asset-specific sentiment.
2. Preserve point-in-time data so analysis does not accidentally use future information.
3. Compare advanced NLP with a transparent baseline and publish honest evaluation results.
4. Separate sentiment description, statistical association, forecasting, and causation.
5. Provide evidence for each classification and aggregate signal.
6. Create a reproducible public demo without redistributing restricted news content.
7. Build a production-oriented pipeline with tests, monitoring, security, and documentation.

## 3. Target users

### Primary persona: Crypto market researcher

- Monitors Bitcoin and Ethereum news
- Investigates major sentiment changes
- Compares sentiment with market observations
- Needs source links, timestamps, evidence, and methodological limitations
- Exports findings for research or reporting

### Secondary persona: Risk analyst

- Watches regulatory, security, exchange, and protocol events
- Needs alerts supported by traceable evidence
- Values reliability and uncertainty more than automatic predictions

### Future persona: Quantitative researcher

- Tests whether sentiment adds information beyond market baselines
- Requires point-in-time datasets, walk-forward validation, transaction-cost assumptions, and experiment tracking
- This persona will be partially supported in v2.0, not fully in the MVP

## 4. Core user journey

1. The system retrieves permitted Bitcoin and Ethereum news and market data.
2. The ingestion pipeline records publication, retrieval, and processing timestamps.
3. Validation reports missing fields, malformed timestamps, source failures, and stale data.
4. Deduplication groups syndicated or substantially similar stories.
5. Entity resolution determines which asset or protocol the text concerns.
6. A baseline and domain model calculate target-specific sentiment.
7. Event classification identifies the market topic and supporting text.
8. Time-decayed aggregation produces hourly and daily sentiment indices.
9. Market-impact analysis aligns each signal with only later market observations.
10. The dashboard shows trends, evidence, uncertainty, model comparison, and limitations.
11. The user exports a reproducible research report rather than an automatic trade order.

## 5. MVP functional requirements

### FR-01: News ingestion

The system must:

- Use an approved API or redistributable sample dataset
- Support Bitcoin and Ethereum queries
- Preserve headline, description where licensed, URL, source, author, language, publication time, and retrieval time
- Handle pagination, rate limits, retries, and partial failures
- Never commit API secrets

### FR-02: Market-data ingestion

The system must retrieve or load timestamped Bitcoin and Ethereum OHLCV observations and preserve provider, symbol, quote currency, interval, timezone, and retrieval time.

### FR-03: Data validation and deduplication

The pipeline must:

- Validate required columns, types, ranges, timestamps, and identifiers
- Normalise timestamps to UTC
- Remove API truncation artefacts from model input
- Detect exact URL duplicates and near-duplicate stories
- Preserve raw observations separately from processed features

### FR-04: Asset and event detection

The system must identify the asset discussed and distinguish ambiguous symbols from ordinary language. Initial event categories are:

- Regulation and legal action
- Security breach or exploit
- Exchange incident
- Institutional adoption or partnership
- Protocol upgrade or technical change
- Listing or delisting
- Macroeconomic event
- Market commentary
- Other or insufficient evidence

### FR-05: Sentiment models

The system must:

- Implement VADER as a transparent baseline
- Evaluate a financial-language transformer against the same labelled examples
- Return negative, neutral, and positive probabilities or scores
- Preserve model and preprocessing versions
- Expose the relevant text evidence

### FR-06: Evaluation

The project must maintain a human-labelled, versioned evaluation set separate from model-development data. It will report class counts, confusion matrix, precision, recall, macro F1, class-level F1, and calibration where probabilities are used.

### FR-07: Sentiment index

The system will calculate hourly and daily asset-level indices using documented rules for sentiment, confidence, recency, source independence, duplicate groups, and evidence volume. The index must display coverage separately from model confidence.

### FR-08: Market-impact analysis

The analysis must align sentiment with subsequent returns, volume, and realised volatility over documented horizons. Evaluation must be chronological or walk-forward and must prevent look-ahead leakage.

### FR-09: Dashboard

The dashboard will show:

- Current asset sentiment and evidence coverage
- Sentiment and price timelines
- Article and event drivers
- Positive, neutral, and negative distributions
- Source and freshness information
- Model comparison and error examples
- Market-impact research results
- Methodology and responsible-use warnings

### FR-10: Exports

Users can export permitted derived data and research summaries to CSV and PDF. Restricted full-text news content will not be redistributed.

## 6. Non-functional requirements

- **Reproducibility:** A deterministic sample dataset runs without paid credentials.
- **Point-in-time correctness:** Stored timestamps support leakage-free reconstruction.
- **Explainability:** Every aggregate result links to components and evidence.
- **Reliability:** Ingestion is idempotent and handles retries without duplicate records.
- **Security:** Secrets remain server-side; inputs and API responses are validated.
- **Privacy:** v1.0 does not profile individual social-media users.
- **Accessibility:** Core dashboard flows support keyboard use and readable contrast.
- **Performance:** A daily update should complete within the documented operating target.
- **Maintainability:** Connectors, validation, NLP, aggregation, analytics, APIs, and UI remain modular.
- **Observability:** Data freshness, failures, latency, and model distribution changes are measurable.

## 7. Explicit MVP exclusions

- Real-money or paper-trade execution
- Personalised investment advice
- Guaranteed return or price-direction claims
- Causal claims based only on correlation
- Private exchange-account connections
- Leverage, derivatives execution, or portfolio custody
- Unapproved web scraping
- Anonymous-user profiling or bot identification
- Full multilingual analysis
- Every cryptocurrency or token
- Fully autonomous model retraining

## 8. Initial research questions

1. Does a financial-language model outperform VADER on a labelled crypto-news test set?
2. How much does deduplication change the hourly and daily sentiment index?
3. Which event categories produce the largest sentiment changes?
4. Is sentiment associated with subsequent returns, volume, or volatility after strictly time-aligning the data?
5. Does sentiment add information beyond simple price and volume baselines?

These are research questions, not assumed conclusions.

## 9. Success criteria

### Product success

- A user can select Bitcoin or Ethereum and trace an aggregate sentiment result to its evidence.
- Duplicate stories do not receive independent weight.
- Model confidence and evidence coverage are clearly separated.
- The dashboard displays data freshness and methodology limitations.

### Engineering success

- A clean setup reproduces the sample pipeline.
- Data contracts and validation errors are documented.
- Automated tests cover critical transformations and leakage controls.
- No secret, restricted article corpus, or unsafe model file is committed.
- Ingestion can be rerun without creating duplicate logical records.

### Model success

- Evaluation uses a locked human-labelled test set.
- Performance is reported by class, not only as accuracy.
- The advanced model is adopted only if it measurably improves over VADER.
- Known error categories and model limitations are published.

### Financial-research success

- Every feature uses information available at or before the signal timestamp.
- Market outcomes begin strictly after the signal timestamp.
- Baseline comparisons and statistical uncertainty are reported.
- Results distinguish association from forecasting and causation.

## 10. Major risks and mitigations

| Risk | Mitigation |
|---|---|
| News licensing prevents redistribution | Store permitted metadata and publish synthetic or licensed samples |
| Duplicate stories inflate sentiment | Exact and semantic near-duplicate grouping |
| Model misunderstands crypto language | Labelled evaluation, error analysis, and domain-model comparison |
| Future information leaks into features | Point-in-time timestamps and chronological validation tests |
| Correlation is mistaken for causation | Careful terminology, baselines, uncertainty, and explicit disclaimers |
| API access becomes unavailable | Connector abstraction and deterministic offline samples |
| A source dominates the index | Source-independence limits and source-distribution reporting |
| Model or news distribution drifts | Versioning and scheduled data/model monitoring |

## 11. Definition of v1.0 complete

v1.0 is complete when a documented sample and supported live sources can pass through ingestion, validation, deduplication, asset and event detection, baseline and financial sentiment models, time-series aggregation, market-impact research, and an explainable dashboard in one tested workflow.
