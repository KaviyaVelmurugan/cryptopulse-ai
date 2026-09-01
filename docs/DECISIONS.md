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

## D-018: Separate analytical reports from operational state

**Decision:** Keep reproducible CSV/JSON reports as v1 analytical artefacts and use a migrated
SQLite database for run history, stage status, failures, and overlap protection.

**Reason:** This provides a zero-service local application foundation without pretending SQLite is
the final concurrent warehouse. PostgreSQL remains the explicit hosted upgrade path.

## D-019: Make evidence and data state visible in the dashboard

**Decision:** Display sentiment direction, evidence coverage, supporting event text, data
freshness, and research limitations as separate interface elements. Run in an explicitly labelled
synthetic-demo mode unless a backend URL is configured.

**Reason:** A polished interface must not make sparse or synthetic evidence appear production-ready.
Separating these concepts lets a reviewer inspect why a score exists and understand what it cannot
prove.

## D-020: Keep v1 alerts local and informational

**Decision:** Evaluate configurable sentiment, evidence-coverage, and event conditions in the
browser. Store the rule locally, retain no personal contact details, and use observation language
instead of trading language.

**Reason:** This demonstrates a useful alert workflow without introducing notification delivery,
exchange access, personalisation, or an implied recommendation. Server-side delivery and user
accounts require a separate security and consent design.

## D-021: Export only derived research data

**Decision:** The dashboard CSV contains aggregate index fields and excludes article text. The PDF
workflow uses the browser's standards-based print/save function.

**Reason:** Derived outputs are sufficient for analysis and portfolio review while avoiding
unnecessary redistribution of provider-controlled content. Browser printing keeps the v1 report
portable without adding a server-side document service.

## D-022: Monitor distributions without claiming production drift detection

**Decision:** Track article warnings, duplicates, sentiment mean, evidence coverage, and freshness
against a versioned synthetic reference. Label that reference as pipeline validation only.

**Reason:** The mechanics of monitoring should be testable now, but a meaningful production
baseline can only be learned from a sufficiently large, representative and approved live dataset.

## D-023: Keep containers non-root and deployment optional

**Decision:** Supply separate API and dashboard images, non-root runtime users, health checks,
read-only Compose filesystems, and no embedded credentials. Do not automatically publish images.

**Reason:** Reproducibility and safer defaults improve the portfolio project without creating a
public service or expanding its financial-risk boundary.

## D-024: Block unapproved FinBERT production promotion

**Decision:** Record the exact optional FinBERT revision in a model registry and mark production
approval blocked until its upstream licence and performance on representative human-labelled data
are reviewed.

**Reason:** A reproducible model is not automatically legally or statistically suitable for
production use.

## D-025: Keep personal publication assets outside the repository

**Decision:** Commit technical release documentation and reusable diagrams to GitHub, but store the
LinkedIn draft, Medium draft and beginner/interview guide in a separate local deliverables folder.

**Reason:** GitHub should explain and reproduce the software. Personal publishing drafts and the
downloadable study guide belong to their intended platforms and should remain editable without
changing the source repository.

## D-026: Release v1.0 only after hosted CI verification

**Decision:** Prepare release notes and a tag checklist but leave the actual GitHub tag and release
creation to the repository owner after the pushed commit passes GitHub Actions.

**Reason:** A release tag should identify a remotely verified commit. Local success cannot prove
that GitHub container and security jobs completed on the hosted runner.
