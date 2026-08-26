# Crypto sentiment annotation guidelines

## Purpose

Annotations provide the reference labels used to evaluate sentiment and event models. They must represent the text available at annotation time, not later price movement or the annotator's personal view of an asset.

## Unit of annotation

Each row labels one `article_id` and one `target_asset_id`. A multi-asset article receives a separate row for each relevant asset because the same text can be positive about Bitcoin and negative about Ethereum.

## Investor-oriented sentiment labels

### Positive

The available text presents evidence reasonably favourable to the target asset's adoption, security, utility, liquidity, regulatory position, technical operation, or market access.

### Negative

The available text presents evidence reasonably unfavourable to the target asset, such as an exploit, service failure, legal restriction, technical delay, loss of access, or weakening liquidity.

### Neutral

The text is primarily factual, balanced, uncertain, procedural, or contains insufficient directional evidence for the target asset.

Neutral does not mean the article is unimportant.

## Annotation rules

1. Read only the preserved headline and permitted summary.
2. Identify the target asset before assigning sentiment.
3. Copy the shortest sufficient evidence span.
4. Label the author's reported information, while distinguishing quotations and speculation.
5. Do not use future price movement to decide the label.
6. Do not infer facts missing from the text.
7. Use `insufficient_evidence` for the event when the available text cannot support an event category.
8. Escalate ambiguous cases for adjudication rather than forcing agreement.

## Multi-asset example

Text: `Bitcoin liquidity remained stable while Ethereum liquidity weakened.`

- Bitcoin: neutral, evidence `Bitcoin liquidity remained stable`
- Ethereum: negative, evidence `Ethereum liquidity weakened`

This example demonstrates why one document-level VADER score cannot provide target-specific sentiment.

## Event labels

- `regulation_legal`
- `security_incident`
- `exchange_incident`
- `adoption_partnership`
- `protocol_technical`
- `listing_delisting`
- `macroeconomic`
- `market_commentary`
- `other`
- `insufficient_evidence`

## Quality workflow for a real evaluation set

1. Two reviewers label the same records independently.
2. Agreement is measured separately for sentiment and event labels.
3. Disagreements are adjudicated with a recorded reason.
4. Near-duplicate groups stay within one dataset split.
5. The test split is locked before model comparison.
6. Label corrections create a new annotation version rather than silently replacing history.

The Phase 2 annotations are synthetic examples for pipeline verification. They are too small to support model-performance claims.
