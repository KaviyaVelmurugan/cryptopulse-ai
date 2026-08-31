# VADER sentiment baseline

## Role in CryptoPulse AI

VADER is a rule-based general-language sentiment model. CryptoPulse AI uses it as an inexpensive, transparent baseline that future models must beat on the same locked evaluation set.

The standard compound thresholds are:

- Positive: `compound >= 0.05`
- Neutral: `-0.05 < compound < 0.05`
- Negative: `compound <= -0.05`

The compound score ranges from -1 to +1. VADER's negative, neutral, and positive values are lexical proportions, not calibrated class probabilities. CryptoPulse therefore stores them in a dedicated `VaderBaselineScore` instead of mislabelling them as model probabilities.

## Target handling

Phase 7 supplies VADER with target-specific sentences and contrastive clauses. A multi-asset
article therefore receives separate evidence inputs for Bitcoin and Ethereum. Missing or ambiguous
targets are explicitly flagged by the entity resolver rather than silently treated as resolved.

## Evaluation views

- `all_records`: every annotation row
- `deduplicated_records`: one row per duplicate group, target, and split
- `locked_test_split`: only the preassigned test rows

The report includes class support, true positives, false positives, false negatives, precision, recall, F1, macro F1, accuracy, confusion matrices, and individual errors.

Deduplicated results are essential because syndicated stories must not multiply their influence on evaluation or future sentiment indices.

## Limitations

- The lexicon is not trained specifically for finance or cryptocurrency.
- Neutral journalistic wording can hide financially important direction.
- Asset tickers, protocol terminology, and event context may be misunderstood.
- Rule-based evidence extraction can miss indirect references and cross-sentence context.
- Standard thresholds were not calibrated on CryptoPulse data.
- The synthetic evaluation sample is far too small for performance claims.

## Generate the reports

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.sentiment
```

Outputs are written under `reports/sentiment/`.
