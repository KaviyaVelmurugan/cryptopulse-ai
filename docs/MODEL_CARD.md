# Model card

## System identity

**System:** CryptoPulse AI v1.0

**Purpose:** Explainable Bitcoin and Ethereum news-sentiment research
**Status:** Portfolio-grade research application; not approved for trading or financial advice

## Model components

### VADER baseline

- Package: `vaderSentiment` constrained to `>=3.3.2,<4`
- Role: active transparent sentiment baseline
- Input: target-specific supporting text, not an undifferentiated full article
- Output: negative, neutral or positive label; compound score; class proportions
- Thresholds: negative at or below `-0.05`, positive at or above `0.05`

### Optional FinBERT comparison

- Model: `ProsusAI/finbert`
- Pinned revision: `4556d13015211d73dccd3fdd39d39232506f3e43`
- Role: optional offline comparison using the same labelled split
- Production approval: **blocked** until upstream weight licensing and representative real-data
  performance are confirmed

### Explainable deterministic components

- Asset evidence resolver: v1.0.0
- Weighted multi-label event rules: v1.0.0
- Sentiment aggregation: v1.1.0
- Monitoring baseline: v1.0.0

## Intended use

- Investigate the direction and evidence behind BTC/ETH news sentiment
- Compare transparent and financial-language sentiment approaches
- Study descriptive relationships with strictly later market observations
- Demonstrate evidence lineage, chronological evaluation and responsible product boundaries

## Out-of-scope use

- Buy, sell or hold recommendations
- Guaranteed return, price or volatility forecasting
- Automated trading, portfolio allocation or personalised advice
- Causal claims that news sentiment produced a market movement
- Decisions involving credit, employment, insurance or legal eligibility

## Evaluation

The committed sample has six synthetic articles, seven target annotations and eight market candles.
Its metrics validate code paths only. The VADER reports expose accuracy, macro F1, class metrics,
confusion matrices, duplicate-aware evaluation and a locked split, but these tiny synthetic values
must not be presented as real-world model performance.

Inferential market tests require at least 30 aligned observations. The committed sample has three,
so confidence intervals, permutation tests and corrected significance results are intentionally
withheld.

## Risks and mitigations

| Risk | v1.0 mitigation | Remaining limitation |
|---|---|---|
| One article mentions multiple assets | Target-specific evidence extraction | Rule-based aliases cover only BTC/ETH |
| Syndicated stories inflate sentiment | Duplicate groups and source weighting | Near-duplicate thresholds need live tuning |
| High confidence looks like broad evidence | Coverage shown separately | Users may still overinterpret polished charts |
| Future information leaks into research | Retrieval/processing timestamps and chronological alignment | Provider timestamps may still contain errors |
| Domain/model bias | Baseline comparison and class-wise reports | Representative multilingual labels are absent |
| Model or data drift | Versioned synthetic drift mechanics | Real production baseline is not yet available |

## Human oversight

Users must inspect evidence text, source diversity, timestamps, data-state labels and research
warnings before interpreting a signal. A human reviewer owns any downstream decision. Alerts mean
only that configured analytical conditions were observed.

## Versioning and monitoring

Component approval state is recorded in `config/model_registry.json`. Row-level analytical outputs
retain model, preprocessing, evidence and aggregation versions. Phase 14 monitoring checks quality,
mean distribution shift and freshness against an explicitly synthetic reference.
