# Development roadmap

Each phase begins with an explanation of its purpose, technology choices, output, limitations, and interview relevance before implementation.

## Phase 1 - Product definition

**Status:** Complete

- Define the problem, users, product promise, and research questions
- Set MVP capabilities and explicit exclusions
- Define functional, engineering, model, and financial-research success criteria
- Establish responsible-use boundaries
- Add the MIT licence and documentation foundation

**Exit criterion:** The project has a defensible scope and does not imply trading performance before evidence exists.

## Phase 2 - Repository foundation and data contracts

**Status:** Complete

- Create the Python package and application structure
- Define news, market, annotation, prediction, event, and aggregate schemas
- Add deterministic sample data
- Implement validation and data-quality tests
- Add dependency management and development commands

**Exit criterion:** Valid sample data loads reproducibly and invalid data produces understandable errors.

## Phase 3 - News and market-data connectors

**Status:** Planned

- Implement provider interfaces
- Add one approved news source and one OHLCV source
- Add pagination, retries, rate-limit handling, and idempotency
- Preserve point-in-time provenance

**Exit criterion:** The pipeline can update both sources without leaking secrets or duplicating observations.

## Phase 4 - Cleaning and deduplication

**Status:** Planned

- Normalise text and timestamps
- Detect language and remove provider artefacts
- Group exact and near-duplicate stories
- Publish data-quality reports

**Exit criterion:** Duplicate and malformed observations cannot silently distort downstream results.

## Phase 5 - Baseline sentiment and annotation

**Status:** Planned

- Implement VADER baseline
- Define annotation guidelines
- Create and review a labelled evaluation set
- Establish evaluation metrics and error taxonomy

**Exit criterion:** The baseline has reproducible, honestly reported performance on unseen labelled examples.

## Phase 6 - Financial-language model comparison

**Status:** Planned

- Add a suitable licensed financial-language model
- Evaluate it against VADER
- Measure class performance and calibration
- Version preprocessing and inference outputs

**Exit criterion:** Model selection is based on evidence rather than complexity.

## Phase 7 - Asset-specific sentiment and entity resolution

**Status:** Planned

- Detect crypto assets, organisations, people, and locations
- Resolve ambiguous tickers and aliases
- Assign sentiment to the correct target rather than the entire document
- Display supporting sentences

**Exit criterion:** Multi-asset articles can express different sentiment toward different targets.

## Phase 8 - Event classification

**Status:** Planned

- Implement the event taxonomy
- Create an explainable baseline
- Evaluate event labels and multi-label cases
- Add event evidence to the dashboard contract

**Exit criterion:** Users can identify what kind of event drove a sentiment change.

## Phase 9 - Time-series sentiment index

**Status:** Planned

- Define hourly and daily aggregation
- Incorporate recency, confidence, source independence, and duplicate groups
- Separate confidence from evidence coverage
- Add sensitivity tests for weighting choices

**Exit criterion:** Every index value is reproducible and traceable to source observations.

## Phase 10 - Market-impact research

**Status:** Planned

- Align signals with later returns, volume, and volatility
- Add simple financial baselines
- Use chronological and walk-forward evaluation
- Measure uncertainty and guard against multiple-testing claims

**Exit criterion:** Research results are leakage-free and clearly separate association from causation.

## Phase 11 - Backend, database, and scheduling

**Status:** Planned

- Add FastAPI service boundaries
- Add PostgreSQL or a suitable development database
- Schedule ingestion and processing
- Implement migrations, health checks, logs, and freshness metrics

**Exit criterion:** The pipeline operates repeatedly rather than only inside a notebook.

## Phase 12 - Web dashboard

**Status:** Planned

- Build the Next.js and TypeScript interface
- Add sentiment/price timelines, event drivers, source evidence, and model comparison
- Add accessible filters and responsive layouts
- Add methodology and data-freshness views

**Exit criterion:** A reviewer can understand and investigate a signal without reading source code.

## Phase 13 - Reports and alerts

**Status:** Planned

- Export permitted derived datasets to CSV
- Generate research reports for PDF
- Add configurable informational alerts
- Prevent alert language from becoming investment advice

**Exit criterion:** Outputs are shareable, traceable, and responsibly worded.

## Phase 14 - MLOps, quality, and security

**Status:** Planned

- Add experiment and model version tracking
- Monitor data quality, drift, latency, failures, and freshness
- Add Docker, CI, automated tests, and dependency checks
- Complete security, privacy, and licence review

**Exit criterion:** A new contributor can reproduce and safely operate the project.

## Phase 15 - Release and publication

**Status:** Planned

- Add architecture diagram, screenshots, model card, data sheet, and API documentation
- Tag the v1.0 GitHub release
- Prepare LinkedIn and Medium articles
- Create a separate downloadable interview guide

**Exit criterion:** The project is understandable, reproducible, and portfolio-ready without unsupported claims.

## Future versions

### v1.1 - Reliability and usability

- Broader tests, accessibility audit, stronger connector resilience, and better reporting

### v2.0 - Validated intelligence

- Creator-authorised or licensed additional sources, multilingual evaluation, multimodal inputs, model calibration, and stronger event analysis

### v3.0 - Advanced research platform

- On-chain and derivatives signals, regime analysis, portfolio research, governance, and controlled paper-trading experiments
