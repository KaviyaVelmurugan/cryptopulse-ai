# Explainable market-event classification

## Purpose

Sentiment describes direction; event classification describes the underlying development.
CryptoPulse AI uses events to distinguish, for example, a negative security incident from a
negative regulatory action. This context will later support time-series aggregation and
market-impact research.

## Taxonomy

The v1 taxonomy includes regulation/legal, security incidents, exchange incidents,
adoption/partnerships, protocol/technical changes, listings/delistings, macroeconomic events,
market commentary, other, and insufficient evidence.

`insufficient_evidence` is a deliberate abstention. The classifier does not force a meaningful
event when its rules find inadequate evidence. `other` is reserved for a clearly evidenced event
that falls outside the named categories and therefore normally requires human review.

## Baseline design

The baseline assigns documented weights to phrases associated with each event. It operates on
the target-specific evidence created in Phase 7. The highest-scoring category becomes the primary
event, while other sufficiently strong categories are preserved as secondary labels.

Every prediction contains:

- primary and secondary event labels;
- matched terms grouped by event;
- the exact evidence text;
- relative confidence among detected event types;
- evidence strength relative to the rule inventory; and
- classifier, preprocessing, and evidence-extraction versions.

Confidence and evidence strength are intentionally different. A category can dominate all other
categories while still having only one weak piece of evidence.

## Evaluation

Reports measure primary-label accuracy, multi-label hit rate, macro F1 over classes represented
in each evaluation slice, and a complete confusion matrix. Results are produced for all records,
deduplicated records, and the locked test split.

The current synthetic sample matches the rules closely and therefore produces perfect accuracy.
This validates integration, not real-world quality. The result must not be used in a résumé,
article, or interview as a production-performance claim.

## Run

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.events
```

Outputs are written to `reports/events/`.

## Limitations and v2 improvements

- The labelled sample is tiny, synthetic, and lacks several taxonomy classes.
- Keyword rules can miss paraphrases, emerging terminology, negation, and implied events.
- Rule weights are expert choices rather than learned or calibrated probabilities.
- Secondary events do not yet have independent human multi-label annotations.
- A future model should be compared using a larger chronological, double-reviewed dataset.
- Rules should remain as an interpretable fallback even after a trained classifier is added.

## Interview explanation

“I separated event type from sentiment because positive or negative alone does not explain market
context. I built an abstaining, multi-label rule baseline whose matched evidence is visible. I
evaluate primary accuracy and whether the human event appears anywhere in the predicted label set.
The synthetic sample proves the pipeline, while a real model decision requires broader annotations.”
