# Asset-specific sentiment and entity resolution

## Problem

Document-level sentiment can assign the same result to every asset in an article. That is
incorrect when, for example, Bitcoin liquidity is stable while Ethereum liquidity weakens.
Phase 7 creates a separate evidence input for each target asset before sentiment inference.

## v1 approach

The resolver recognises explicit Bitcoin and Ethereum names and selected market aliases:

| Asset | Recognised forms |
|---|---|
| Bitcoin | Bitcoin, BTC, `$BTC`, XBT |
| Ethereum | Ethereum, Ether, ETH, `$ETH` |

Matches use token boundaries, so `ETH` is not detected inside words such as `method`. Text is
split into sentences and contrastive clauses introduced by words such as “while”, “whereas”,
and “but”. Only segments mentioning the requested target are sent to the sentiment model.

Each output records the resolved asset, aliases, mention count, selected evidence, resolution
status, quality flags, and resolver version. A missing target uses the full text only as an
explicitly flagged fallback; it is never silently treated as a successful resolution.

## Why rules before another ML model

The initial universe contains only Bitcoin and Ethereum. A versioned rule system is fast,
deterministic, testable, and easy to explain. It establishes a measurable baseline before a
crypto named-entity model is introduced. This avoids adding model complexity without evidence.

## Run the evidence report

```powershell
$env:PYTHONPATH="src"
python -m cryptopulse.entity_resolution
```

The output is `reports/entity_resolution/target_evidence.csv`.

## Limitations

- Indirect descriptions such as “the largest cryptocurrency” are not resolved.
- New assets and aliases require a versioned dictionary update.
- A ticker without crypto context can remain ambiguous.
- Pronouns and references spanning multiple sentences are not linked.
- Clause splitting does not provide full grammatical dependency parsing.
- Organisation, person, location, protocol, and exchange resolution remains future work.
- Rules should be evaluated on a larger human-labelled entity/evidence dataset.

## Interview explanation

“I found that whole-document sentiment was the wrong abstraction for multi-asset news. I added
a deterministic entity-resolution baseline that extracts target-specific evidence before model
inference. The output is auditable and flags missing or ambiguous targets. I would compare this
baseline with a crypto-domain NER model only after building a representative labelled set.”
