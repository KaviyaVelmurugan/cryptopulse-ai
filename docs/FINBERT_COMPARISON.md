# FinBERT comparison

## What Phase 6 adds

Phase 6 adds an optional adapter for `ProsusAI/finbert`, a BERT model trained for
financial-text sentiment. It maps the model's positive, negative, and neutral outputs into
the same versioned prediction contract used throughout CryptoPulse AI. VADER and FinBERT
are evaluated against the same annotations, duplicate policy, and locked test split.

The exact upstream revision is pinned to
`4556d13015211d73dccd3fdd39d39232506f3e43`. This prevents an upstream model update from
silently changing a past experiment.

## Why both models are retained

VADER is fast, inexpensive, transparent, and useful as a minimum baseline. FinBERT can
represent financial language in context, but it is slower, larger, harder to explain, and
was not specifically trained on the language of crypto news. Complexity alone is not
evidence of superiority.

## Evaluation

The comparison reports accuracy, macro F1, class-wise precision/recall/F1, confusion
matrices, multiclass Brier score, and expected calibration error. Metrics are calculated for:

1. all labelled records;
2. one record per duplicate group, target, and split; and
3. the locked test split.

The committed sample is synthetic and extremely small. It validates code and report
contracts only. It cannot support a claim about either model's real-world quality.

## Running the real model

The model is deliberately optional because PyTorch and the model weights are large:

```powershell
python -m pip install -e ".[ml]"
$env:PYTHONPATH="src"
python -m cryptopulse.finbert
```

The first execution downloads the pinned model revision. Generated real comparison files
are written to `reports/model_comparison/`.

## Licence boundary

The upstream model repository does not declare a licence in its model metadata or include
a licence file as of this integration. The repository's MIT licence therefore covers only
CryptoPulse AI's original code and documentation—not the FinBERT weights. Do not distribute
the weights or use them commercially until the model's rights are confirmed with its owner.

## Known limitations

- The current input is full cleaned document text; asset-specific evidence extraction is Phase 7.
- Long text is truncated to the model's supported context window.
- FinBERT was trained on financial text, not a representative crypto-news corpus.
- The model supports English only in this phase.
- Confidence is not equivalent to correctness; calibration must be measured on sufficient data.
- CPU inference can be slow and production serving needs latency and memory measurement.
- The present annotations are synthetic, tiny, and not independently double-labelled.

## Interview explanation

“I retained VADER as a transparent baseline and added a revision-pinned financial transformer.
Both models use identical labelled slices and deduplication rules. I also measure probability
calibration, not only accuracy. The current synthetic sample proves reproducibility rather
than model quality, so selecting a production model requires a larger, human-reviewed,
chronological crypto-news test set.”
