# Data dictionary

All schemas use semantic version `1.0.0`. All timestamps are ISO 8601 UTC timestamps. Empty strings are not accepted for required fields.

## News article

| Field | Type | Meaning |
|---|---|---|
| `article_id` | string | Stable internal ID beginning with `news_` |
| `headline` | string | Provider-supplied or permitted synthetic headline |
| `summary` | string | Permitted summary used for analysis |
| `source_name` | string | Publisher or feed name |
| `source_url` | URL | Traceable HTTP(S) source URL |
| `language` | string | ISO-style language code; v1 starts with `en` |
| `published_at` | UTC datetime | Time reported by the source |
| `retrieved_at` | UTC datetime | Time CryptoPulse first received the observation |
| `processed_at` | UTC datetime | Time the processing pipeline handled it |
| `asset_ids` | pipe-separated enum | One or more assets discussed: `bitcoin`, `ethereum` |
| `duplicate_group_id` | string | Group shared by syndicated or near-duplicate stories |
| `content_license` | string | Redistribution status or licence category |
| `is_synthetic` | boolean | Whether the record is fictional test data |
| `schema_version` | string | Contract version |

Required order: `published_at <= retrieved_at <= processed_at`.

## Market candle

| Field | Type | Meaning |
|---|---|---|
| `candle_id` | string | Stable internal ID beginning with `candle_` |
| `asset_id` | enum | `bitcoin` or `ethereum` |
| `symbol` | enum | `BTC` or `ETH`, consistent with the asset ID |
| `quote_currency` | string | v1 sample uses `USD` |
| `interval` | enum | `1h` or `1d` |
| `open_time` | UTC datetime | Inclusive beginning of the candle |
| `close_time` | UTC datetime | Exclusive end of the candle |
| `open_price` | positive number | First observed interval price |
| `high_price` | positive number | Highest interval price |
| `low_price` | positive number | Lowest interval price |
| `close_price` | positive number | Last observed interval price |
| `volume` | non-negative number | Provider-defined traded volume |
| `provider` | string | Market-data provider |
| `retrieved_at` | UTC datetime | Time CryptoPulse received the completed candle |
| `is_synthetic` | boolean | Whether the record is fictional test data |
| `schema_version` | string | Contract version |

Required order: `open_time < close_time <= retrieved_at`. The high and low must contain the open and close prices.

## Human annotation

| Field | Type | Meaning |
|---|---|---|
| `annotation_id` | string | Stable annotation ID |
| `article_id` | foreign key | Referenced news article |
| `target_asset_id` | enum | Asset whose sentiment is labelled |
| `sentiment_label` | enum | `negative`, `neutral`, or `positive` |
| `event_label` | enum | Market-event taxonomy defined in the requirements |
| `evidence_text` | string | Text span supporting the labels |
| `annotator_id` | string | Pseudonymous reviewer identifier |
| `annotation_round` | positive integer | Review or adjudication round |
| `dataset_split` | enum | `development`, `validation`, or locked `test` |
| `created_at` | UTC datetime | Annotation creation time |
| `schema_version` | string | Contract version |

An annotation target must appear in the referenced article's `asset_ids`.

## Sentiment prediction

Defined in `src/cryptopulse/contracts.py`. It stores target-specific class probabilities,
predicted label, evidence, model version, preprocessing version, evidence-resolution version,
and prediction time. The three probabilities must sum to approximately 1.0.

## Event prediction

The event prediction contract stores one primary event, zero or more secondary event labels,
relative confidence, evidence strength, matched rule terms, exact target evidence, and every
relevant processing version. `insufficient_evidence` represents an explicit abstention rather
than a forced event guess.

## Sentiment aggregate

The hourly/daily aggregate separates the sentiment index from evidence count, independent-source
count, duplicate-group count, and evidence coverage. Every aggregate has a deterministic identifier,
window boundaries, calculation timestamp, and aggregation version. Article-level weight lineage is
stored separately in the index contribution report.

## Market-research observation

Each observation joins one evidence-bearing hourly index to a reference candle and the strictly
later candle used for outcomes. It stores signal and outcome availability timestamps, sentiment,
coverage, forward return, future volume change, future range volatility, prior-candle return, and
the chronological development/test assignment.

## Operational pipeline run

The local operational database stores run ID, start and finish timestamps, status, current stage,
bounded failure text, report root, and application version. A separate lock table prevents
overlapping runs; applied SQL migration versions are recorded independently.
