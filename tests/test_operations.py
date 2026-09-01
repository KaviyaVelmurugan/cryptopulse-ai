from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptopulse.operations import run_pipeline
from cryptopulse.service import DashboardService
from cryptopulse.storage import OperationalStore, PipelineBusyError


ROOT = Path(__file__).resolve().parents[1]
WHEN = datetime(2026, 1, 7, tzinfo=UTC)


class StorageTests(unittest.TestCase):
    def test_migrations_runs_and_locking_are_durable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "operations.db"
            store = OperationalStore(database)
            self.assertEqual(store.migrate(applied_at=WHEN), [1])
            self.assertEqual(store.migrate(applied_at=WHEN), [])
            store.start_run("run_one", started_at=WHEN, report_root=ROOT / "reports")
            with self.assertRaises(PipelineBusyError):
                store.start_run(
                    "run_two", started_at=WHEN + timedelta(minutes=1), report_root=ROOT / "reports"
                )
            store.update_stage("run_one", "index")
            store.finish_run("run_one", finished_at=WHEN + timedelta(minutes=2), succeeded=True)
            run = store.recent_runs(1)[0]
            self.assertEqual(run.status, "succeeded")
            self.assertEqual(run.current_stage, "complete")

    def test_stale_lock_can_be_recovered(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = OperationalStore(Path(directory) / "operations.db")
            store.migrate(applied_at=WHEN)
            store.start_run("abandoned", started_at=WHEN, report_root=ROOT / "reports")
            store.start_run(
                "replacement", started_at=WHEN + timedelta(hours=3), report_root=ROOT / "reports"
            )
            self.assertEqual(store.recent_runs(1)[0].run_id, "replacement")


class PipelineTests(unittest.TestCase):
    def test_complete_pipeline_records_success(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "operations.db"
            run_id = run_pipeline(ROOT, database, clock=lambda: WHEN)
            run = OperationalStore(database).recent_runs(1)[0]
            self.assertEqual(run.run_id, run_id)
            self.assertEqual(run.status, "succeeded")
            self.assertTrue((ROOT / "reports" / "research" / "research_summary.json").exists())


class ServiceTests(unittest.TestCase):
    def test_filters_and_freshness_are_framework_independent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "operations.db"
            store = OperationalStore(database)
            store.migrate(applied_at=WHEN)
            service = DashboardService(ROOT, database)
            self.assertEqual(service.health()["status"], "ok")
            bitcoin_daily = service.indices("bitcoin", "1d")
            self.assertEqual(len(bitcoin_daily), 1)
            self.assertTrue(all(row["asset_id"] == "bitcoin" for row in bitcoin_daily))
            self.assertTrue(all(row["target_asset_id"] == "ethereum" for row in service.events("ethereum")))
            self.assertEqual(service.monitoring_summary()["baseline_version"], "1.0.0")
            ready = service.readiness(now=datetime(2026, 1, 6, 10, tzinfo=UTC))
            self.assertEqual(ready["status"], "ready")
            stale = service.readiness(now=datetime(2026, 2, 6, tzinfo=UTC))
            self.assertEqual(stale["status"], "stale")

    def test_invalid_filters_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = DashboardService(ROOT, Path(directory) / "operations.db")
            with self.assertRaises(ValueError):
                service.indices("dogecoin", "1h")
            with self.assertRaises(ValueError):
                service.indices("bitcoin", "weekly")


if __name__ == "__main__":
    unittest.main()
