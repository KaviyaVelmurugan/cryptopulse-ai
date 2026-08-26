# Preprocessing, quality, and deduplication

## Why this layer exists

Sentiment models are sensitive to text artefacts, while aggregate indices are sensitive to repeated stories. CryptoPulse AI therefore cleans and assesses data before inference and deduplicates before aggregation.

The original provider record remains unchanged. Cleaning creates a separate `CleanedNewsArticle` containing model-ready text, detected language, quality flags, and a preprocessing version.

## Deterministic cleaning

Version `1.0.0` performs:

- Unicode NFKC normalisation
- HTML entity decoding
- Zero-width and non-printable character removal
- Provider truncation-marker removal such as `[+123 chars]`
- Whitespace normalisation
- Headline and summary combination without forced lowercasing

Case is preserved because later transformer models may be case-sensitive. A separate lowercased comparison representation is used only for duplicate matching.

## Language baseline

Phase 4 uses a conservative, dependency-free English/unknown check based on script coverage and common English function words. It is a quality gate, not a general language-identification model. Uncertain records receive `language_unconfirmed` instead of a guessed language.

Production multilingual support requires a separately evaluated language model and labelled multilingual test data.

## Quality flags

- `provider_truncation_removed`
- `short_headline`
- `short_summary`
- `language_unconfirmed`
- `retrieval_lag_over_24h`
- `invalid_timestamp_order`

Flags do not automatically imply deletion. They let later stages decide whether to exclude, review, or retain a record.

## Duplicate detection

The baseline uses two explainable paths:

1. Canonical URLs that match exactly are grouped.
2. Stories sharing an asset and published within 48 hours are grouped only when both sequence similarity and token Jaccard similarity exceed documented thresholds.

Aliases such as `BTC`/`Bitcoin` and `ETH`/`Ethereum` are normalised for comparison. Common function words and synthetic-report boilerplate are excluded from the duplicate representation.

Every match report includes both metrics, publication distance, match type, and a sentence explaining why the pair passed. Group IDs are derived from sorted member IDs, so repeated runs and different input order produce the same result.

## Limitations

- Lexical similarity can miss paraphrases with different vocabulary.
- Generic event language can produce false positives.
- Thresholds are initial engineering hypotheses, not scientifically optimal values.
- Cross-language duplicates are not supported.
- URL canonicalisation does not yet remove every tracking parameter.

Later work can compare this baseline with sentence embeddings using a labelled duplicate/non-duplicate set. The baseline remains valuable for auditability and regression testing.

## Generate the reports

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.preprocessing
```

Outputs:

- `reports/data_quality/article_quality.csv`
- `reports/data_quality/duplicate_matches.csv`
- `reports/data_quality/summary.json`
