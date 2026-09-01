from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from cryptopulse.monitoring import generate_monitoring_report, validate_runtime_environment


ROOT = Path(__file__).resolve().parents[1]


class EnvironmentTests(unittest.TestCase):
    def test_production_rejects_missing_or_wildcard_origins(self) -> None:
        result = validate_runtime_environment({"CRYPTOPULSE_ENV": "production", "CRYPTOPULSE_ALLOWED_ORIGINS": "*"})
        self.assertEqual(result["status"], "invalid")
        self.assertTrue(result["errors"])

    def test_development_can_run_without_live_news_key(self) -> None:
        result = validate_runtime_environment({"CRYPTOPULSE_ENV": "development"})
        self.assertEqual(result["status"], "valid")
        self.assertTrue(result["warnings"])


class MonitoringTests(unittest.TestCase):
    def test_report_is_versioned_and_exposes_quality_drift_and_freshness(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config").mkdir()
            (root / "reports" / "data_quality").mkdir(parents=True)
            (root / "reports" / "index").mkdir(parents=True)
            (root / "config" / "monitoring_baseline.json").write_text(
                (ROOT / "config" / "monitoring_baseline.json").read_text(encoding="utf-8"), encoding="utf-8"
            )
            (root / "config" / "model_registry.json").write_text(
                (ROOT / "config" / "model_registry.json").read_text(encoding="utf-8"), encoding="utf-8"
            )
            (root / "reports" / "data_quality" / "summary.json").write_text(
                json.dumps({"total_articles": 10, "duplicate_articles": 2, "articles_with_warnings": 0}), encoding="utf-8"
            )
            (root / "reports" / "index" / "sentiment_index.csv").write_text(
                "aggregate_id,resolution,sentiment_index,evidence_coverage,calculated_at\n"
                "one,1h,0.12,0.20,2026-01-07T00:00:00Z\n", encoding="utf-8"
            )
            report = generate_monitoring_report(root, generated_at=datetime(2026, 1, 7, 1, tzinfo=UTC))
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["baseline_version"], "1.0.0")
            self.assertIn("active_sentiment_baseline", report["model_registry"])
            self.assertEqual(set(report["checks"]), {"article_warning_rate", "duplicate_rate", "sentiment_mean_drift", "coverage_mean_drift", "freshness"})


if __name__ == "__main__":
    unittest.main()
