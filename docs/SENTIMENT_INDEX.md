# Hourly and daily sentiment index

## Purpose

Phase 9 turns individual target-specific predictions into a time series while preserving the
evidence behind every point. The index ranges from `-1` to `+1` and describes weighted sentiment
in a time window. It is not a forecast, price target, trading instruction, or causal estimate.

## Calculation

For each article-target pair, the v1 index uses the VADER compound score as its directional
sentiment value. An article enters a window only when its processing timestamp is no later than
the window end. The article weight is:

`confidence proxy × recency × duplicate weight × source weight`

The index is the sum of weighted sentiment contributions divided by the sum of weights. Empty
windows receive an index value of zero together with zero evidence and zero coverage; consumers
must use the evidence fields to distinguish “no evidence” from genuinely balanced sentiment.

### Confidence proxy

The confidence weight is `max(abs(VADER compound), 0.10)`. This is a documented heuristic, not a
calibrated model probability. It prevents a neutral-looking article from receiving zero weight
while giving stronger lexical direction more influence.

### Recency

Evidence decays exponentially toward the end of its window. The default half-life is one hour for
hourly indices and twelve hours for daily indices. Sensitivity reports also test a shorter daily
half-life and no-recency weighting.

### Duplicate and source independence

Articles in the same duplicate group divide a total group weight, preventing syndication from
being counted as independent confirmation. Multiple articles from the same source similarly divide
their source weight inside a window.

### Evidence coverage

Coverage is separate from sentiment direction:

`min(unique duplicate groups / configured target groups, 1)`

The demonstration targets are three independent groups per hour and five per day. These values
must be validated against real ingestion volume before production use. Independent-source count,
duplicate-group count and raw evidence count are also published separately.

## Traceability

`index_contributions.csv` records each article's sentiment, confidence, recency, duplicate, source,
combined weight, weighted contribution and event category. An aggregate can therefore be rebuilt
without guessing how it was calculated.

## Reports

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.indexing
```

Outputs:

- `sentiment_index.csv`: hourly and daily index points, including empty windows
- `index_contributions.csv`: complete article-level lineage
- `index_sensitivity.csv`: alternative weighting scenarios
- `methodology.json`: versioned machine-readable assumptions

## Limitations and improvements

- All current articles and outputs are synthetic.
- VADER compound magnitude is not calibrated confidence.
- Coverage targets are design parameters, not empirically established thresholds.
- Source weighting treats source names as independent identities and does not detect common ownership.
- Duplicate detection can produce false matches or misses.
- One high-impact event may matter more than several ordinary articles; v1 does not estimate impact.
- Phase 10 must test relationships with later market behaviour chronologically and without leakage.
- A future version should compare VADER and calibrated FinBERT indices on real labelled evidence.
