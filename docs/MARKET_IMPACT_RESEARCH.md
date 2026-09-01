# Chronological market-impact research

## Research question

Phase 10 investigates whether a completed hourly sentiment index is associated with market
behaviour in the following hour. It measures description and association—not causation,
profitability, or investment suitability.

## Point-in-time alignment

An article can enter a signal only if it was processed no later than the signal window end. Each
eligible signal is joined to:

- the candle closing at the signal window end as a descriptive price reference; and
- the next completed hourly candle for future return, volume change, and range volatility.

The future candle must close and become retrievable strictly after the signal became available.
Tests reject future evidence and verify timestamp ordering. The candle-close reference does not
model executable latency, spread, fees, or slippage and must not be described as a backtest.

## Outcomes

- Forward return: `next close / reference close - 1`
- Future volume change: `next volume / reference volume - 1`
- Future range volatility: `(next high - next low) / next open`

## Evaluation design

Observations are ordered by signal time. The first 70% form the development period and the latest
30% form the held-out test period. No random split is used. A sentiment-sign direction baseline is
compared with a simple prior-return persistence baseline on the test period.

Pearson and Spearman correlations are displayed descriptively. Inferential tests require at least
30 observations. When eligible, the pipeline uses deterministic permutation p-values, percentile
bootstrap correlation intervals, and Benjamini-Hochberg correction across the three outcomes.
Direction accuracy additionally requires at least ten held-out observations before it is reported.

## Current result

Only three sample observations have both evidence and a subsequent candle. Therefore:

- correlations are descriptive diagnostics only;
- bootstrap intervals are not produced;
- permutation tests and p-values are not run;
- no statistical, predictive, causal, or trading claim is permitted.

An extreme correlation from three synthetic observations is unstable and should not be quoted as
project performance.

## Run

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.research
```

Outputs:

- `aligned_observations.csv`: point-in-time signal/outcome lineage
- `research_summary.json`: descriptive results, sample gate and baseline comparison
- `methodology.json`: machine-readable definitions and safeguards

## Limitations and future improvements

- Three synthetic observations are inadequate for inference.
- The current horizon is one hour and may not match how different event types affect markets.
- The demonstration uses exchange-specific candles, not consolidated market prices.
- Common market drivers can influence both news sentiment and prices.
- Publication and provider timestamps can contain delay or correction errors.
- No transaction costs, execution timing, liquidity constraints or portfolio rules are modelled.
- Larger research should use walk-forward evaluation, regime analysis and pre-registered hypotheses.
- Causal claims would require a separate identification strategy, not correlation.
