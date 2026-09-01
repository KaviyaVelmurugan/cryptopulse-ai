"""Repeatable pipeline orchestration with structured operational history."""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from .entity_resolution import generate_entity_report
from .events import generate_event_reports
from .indexing import generate_index_reports
from .monitoring import generate_monitoring_report
from .preprocessing import generate_quality_reports
from .research import generate_research_reports
from .sentiment import generate_vader_reports
from .storage import OperationalStore
from .validation import load_csv, parse_annotation_row, validate_dataset_directory


Clock = Callable[[], datetime]


def utc_now() -> datetime:
    return datetime.now(UTC)


def emit_log(level: str, event: str, **fields: object) -> None:
    print(json.dumps({"level": level, "event": event, **fields}, sort_keys=True))


def run_pipeline(
    project_root: Path,
    database_path: Path,
    *,
    clock: Clock = utc_now,
) -> str:
    project_root = project_root.resolve()
    data = project_root / "data" / "sample"
    reports = project_root / "reports"
    store = OperationalStore(database_path.resolve())
    started_at = clock()
    store.migrate(applied_at=started_at)
    run_id = f"run_{uuid.uuid4().hex}"
    store.start_run(run_id, started_at=started_at, report_root=reports)
    emit_log("info", "pipeline_started", run_id=run_id)
    try:
        annotations = load_csv(data / "annotations.csv", parse_annotation_row, "annotations")
        predicted_at = max(item.created_at for item in annotations)
        stages: tuple[tuple[str, Callable[[], object]], ...] = (
            ("validate", lambda: validate_dataset_directory(data)),
            ("quality", lambda: generate_quality_reports(
                data / "news_articles.csv", reports / "data_quality"
            )),
            ("entities", lambda: generate_entity_report(
                data / "news_articles.csv", reports / "entity_resolution" / "target_evidence.csv"
            )),
            ("sentiment", lambda: generate_vader_reports(
                data / "news_articles.csv", data / "annotations.csv", reports / "sentiment",
                predicted_at=predicted_at,
            )),
            ("events", lambda: generate_event_reports(
                data / "news_articles.csv", data / "annotations.csv", reports / "events",
                predicted_at=predicted_at,
            )),
            ("index", lambda: generate_index_reports(
                data / "news_articles.csv", data / "annotations.csv", reports / "index"
            )),
            ("research", lambda: generate_research_reports(
                data / "news_articles.csv", data / "annotations.csv",
                data / "market_candles.csv", reports / "research",
            )),
            ("monitoring", lambda: generate_monitoring_report(project_root, generated_at=clock())),
        )
        for stage, action in stages:
            store.update_stage(run_id, stage)
            emit_log("info", "stage_started", run_id=run_id, stage=stage)
            action()
            emit_log("info", "stage_succeeded", run_id=run_id, stage=stage)
        store.finish_run(run_id, finished_at=clock(), succeeded=True)
        emit_log("info", "pipeline_succeeded", run_id=run_id)
        return run_id
    except Exception as error:
        message = f"{type(error).__name__}: {error}"[:1000]
        store.finish_run(run_id, finished_at=clock(), succeeded=False, error_message=message)
        emit_log("error", "pipeline_failed", run_id=run_id, error=message)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the complete CryptoPulse AI pipeline")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--database", type=Path, default=Path("var/cryptopulse.db"))
    args = parser.parse_args()
    run_id = run_pipeline(args.project_root, args.database)
    print(f"Pipeline completed: {run_id}")


if __name__ == "__main__":
    main()
