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

## D-013: Pin FinBERT and keep it optional

**Decision:** Compare VADER with `ProsusAI/finbert` at commit
`4556d13015211d73dccd3fdd39d39232506f3e43`, loaded only through the optional ML dependency group.

**Reason:** Revision pinning makes experiments reproducible. Optional dependencies keep the core
validation pipeline lightweight. The upstream repository does not declare a model licence, so the
weights are not redistributed and production rights must be confirmed separately.

## D-014: Use explainable entity rules as the first target resolver

**Decision:** Resolve explicit Bitcoin and Ethereum aliases and extract target-bearing clauses
before sending text to sentiment models. Missing and ambiguous targets must remain visible.

**Reason:** The small v1 asset universe does not justify an opaque NER dependency before a tested,
deterministic baseline exists. Evidence-first outputs are also easier to audit and demonstrate.

## D-015: Establish an abstaining multi-label event baseline

**Decision:** Begin event classification with versioned weighted rules, retain sufficiently strong
secondary categories, and return `insufficient_evidence` when no category reaches the threshold.

**Reason:** Event categories can overlap, and forcing a single unsupported answer hides uncertainty.
An explainable baseline makes later trained-model comparisons meaningful.

## D-016: Keep sentiment direction separate from evidence coverage

**Decision:** Publish a bounded weighted sentiment index alongside raw evidence, independent-source,
duplicate-group, and coverage values. Persist every article-level contribution and sensitivity case.

**Reason:** A strong sentiment value based on one story is not equivalent to broad independent
evidence. Visible weighting lineage prevents an aggregate from becoming an unexplained score.

## D-017: Suppress inference when market research is underpowered

**Decision:** Require at least 30 aligned observations before permutation tests, bootstrap
intervals, or multiple-testing correction. Always use chronological development/test ordering.

**Reason:** Tiny samples can produce extreme correlations by chance. A visible insufficient-sample
result is more credible than presenting unstable synthetic statistics as market evidence.
