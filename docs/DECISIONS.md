# Decision log

## D-001: Build an original implementation

**Decision:** Use the referenced crypto sentiment notebook only for problem analysis. Do not copy its code, outputs, notebook structure, data, or branding.

**Reason:** The project must demonstrate independent product and engineering decisions that can be defended in an interview.

## D-002: Build market intelligence before prediction

**Decision:** v1.0 will first describe and evaluate sentiment and market relationships. It will not begin as a price predictor or trading bot.

**Reason:** Sentiment classification quality and point-in-time data correctness must be established before forecasting claims are meaningful.

## D-003: Begin with Bitcoin and Ethereum

**Decision:** Limit the initial assets to BTC and ETH.

**Reason:** A narrow scope permits better data quality, annotation, entity resolution, and evaluation than superficial coverage of many tokens.

## D-004: Preserve three timestamps

**Decision:** Store publication, retrieval, and processing timestamps separately in UTC.

**Reason:** Publication timestamps alone may be corrected or delayed. Point-in-time research needs to know when the system actually received and processed information.

## D-005: Use VADER as a baseline, not the final model

**Decision:** Implement VADER first and compare a financial-language model using the same labelled test set.

**Reason:** An advanced model is valuable only if it measurably improves on a transparent, inexpensive baseline.

## D-006: Use target-specific sentiment

**Decision:** Sentiment will be assigned to an identified asset and supported by relevant text spans.

**Reason:** One article can be positive about one asset and negative about another; document-level sentiment can hide that distinction.

## D-007: Deduplicate before aggregation

**Decision:** Exact and near-duplicate stories will share a duplicate group and will not receive independent full weight.

**Reason:** Syndication can make one event look like broad independent market sentiment.

## D-008: Separate confidence from evidence coverage

**Decision:** Model probability or confidence and the quantity/diversity of evidence will be displayed separately.

**Reason:** A confident classification of one article is not strong market-wide evidence.

## D-009: Require chronological evaluation

**Decision:** Market-impact and future forecasting experiments must use chronological or walk-forward validation.

**Reason:** Random splits can expose models to future language, events, and market regimes, creating unrealistic results.

## D-010: Separate association, prediction, and causation

**Decision:** Each analysis will state whether it measures description, association, predictive value, or causal impact.

**Reason:** A sentiment/return correlation neither guarantees future returns nor proves that news caused a market move.

## D-011: Use permitted content only

**Decision:** Connectors must follow provider terms. The public repository will contain only original, synthetic, licensed, or otherwise permitted data.

**Reason:** News content and social data have ownership, licence, privacy, and redistribution constraints.

## D-012: No trade execution in v1.0

**Decision:** The application will not access exchange accounts or place orders.

**Reason:** Execution introduces materially greater financial, security, operational, and regulatory risk than a research dashboard.
