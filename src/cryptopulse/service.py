"""Read-only dashboard service independent of the HTTP framework."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from . import __version__
from .contracts import AssetId
from .storage import OperationalStore


REQUIRED_REPORTS = (
    "index/sentiment_index.csv",
    "events/event_predictions.csv",
    "research/research_summary.json",
)


class DashboardService:
    def __init__(self, project_root: Path, database_path: Path) -> None:
        self.project_root = project_root.resolve()
        self.report_root = self.project_root / "reports"
        self.store = OperationalStore(database_path.resolve())

    def health(self) -> dict[str, object]:
        return {"status": "ok", "service": "cryptopulse-ai", "version": __version__}

    def readiness(
        self,
        *,
        now: datetime | None = None,
        stale_after: timedelta = timedelta(hours=26),
    ) -> dict[str, object]:
        now = now or datetime.now(UTC)
        missing = [name for name in REQUIRED_REPORTS if not (self.report_root / name).exists()]
        runs = self.store.recent_runs(10) if self.store.database_path.exists() else []
        last_success = next((run for run in runs if run.status == "succeeded"), None)
        if missing:
            return {"status": "not_ready", "missing_reports": missing, "last_success": None}
        index_rows = self._read_csv("index/sentiment_index.csv")
        timestamps = [
            datetime.fromisoformat(row["calculated_at"].replace("Z", "+00:00"))
            for row in index_rows if row.get("calculated_at")
        ]
        data_timestamp = max(timestamps) if timestamps else None
        stale = data_timestamp is None or now - data_timestamp > stale_after
        return {
            "status": "stale" if stale else "ready",
            "missing_reports": [],
            "data_timestamp": data_timestamp.isoformat().replace("+00:00", "Z") if data_timestamp else None,
            "stale_after_hours": stale_after.total_seconds() / 3600,
            "last_success": last_success.finished_at if last_success else None,
        }

    def indices(self, asset: str | None = None, resolution: str | None = None) -> list[dict[str, str]]:
        if asset is not None:
            AssetId(asset)
        if resolution not in {None, "1h", "1d"}:
            raise ValueError("resolution must be 1h or 1d")
        return [
            row for row in self._read_csv("index/sentiment_index.csv")
            if (asset is None or row["asset_id"] == asset)
            and (resolution is None or row["resolution"] == resolution)
        ]

    def events(self, asset: str | None = None) -> list[dict[str, str]]:
        if asset is not None:
            AssetId(asset)
        return [
            row for row in self._read_csv("events/event_predictions.csv")
            if asset is None or row["target_asset_id"] == asset
        ]

    def research_summary(self) -> dict[str, object]:
        with (self.report_root / "research" / "research_summary.json").open(encoding="utf-8") as stream:
            return json.load(stream)

    def monitoring_summary(self) -> dict[str, object]:
        path = self.report_root / "monitoring" / "monitoring_summary.json"
        if not path.exists():
            return {"status": "unavailable", "warning": "Run the pipeline to generate monitoring."}
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)

    def recent_runs(self, limit: int = 10) -> list[dict[str, object]]:
        return [
            {
                "run_id": run.run_id,
                "started_at": run.started_at,
                "finished_at": run.finished_at,
                "status": run.status,
                "current_stage": run.current_stage,
                "error_message": run.error_message,
            }
            for run in self.store.recent_runs(limit)
        ]

    def _read_csv(self, relative_path: str) -> list[dict[str, str]]:
        with (self.report_root / relative_path).open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))
