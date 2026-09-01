"""Operational quality, drift, freshness, and configuration monitoring."""

from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from statistics import fmean
from typing import Mapping


BASELINE_VERSION = "1.0.0"


def validate_runtime_environment(
    environment: Mapping[str, str] | None = None,
) -> dict[str, list[str] | str]:
    env = environment or os.environ
    mode = env.get("CRYPTOPULSE_ENV", "development").strip().lower()
    errors: list[str] = []
    warnings: list[str] = []
    if mode not in {"development", "test", "production"}:
        errors.append("CRYPTOPULSE_ENV must be development, test, or production")
    origins = [item.strip() for item in env.get("CRYPTOPULSE_ALLOWED_ORIGINS", "").split(",") if item.strip()]
    if mode == "production" and (not origins or "*" in origins):
        errors.append("production requires explicit CRYPTOPULSE_ALLOWED_ORIGINS")
    news_key = env.get("NEWS_API_KEY", "")
    if news_key == "replace_with_your_development_key":
        warnings.append("NEWS_API_KEY is still the documented placeholder")
    if not news_key:
        warnings.append("NEWS_API_KEY is absent; live news ingestion is unavailable")
    return {"status": "invalid" if errors else "valid", "mode": mode, "errors": errors, "warnings": warnings}


def _read_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def generate_monitoring_report(
    project_root: Path,
    *,
    generated_at: datetime | None = None,
) -> dict[str, object]:
    root = project_root.resolve()
    generated_at = generated_at or datetime.now(UTC)
    if generated_at.tzinfo is None or generated_at.utcoffset() != UTC.utcoffset(generated_at):
        raise ValueError("monitoring timestamp must use UTC")
    baseline = _read_json(root / "config" / "monitoring_baseline.json")
    registry = _read_json(root / "config" / "model_registry.json")
    quality = _read_json(root / "reports" / "data_quality" / "summary.json")
    indices = _read_csv(root / "reports" / "index" / "sentiment_index.csv")
    hourly = [row for row in indices if row["resolution"] == "1h"]
    total_articles = int(quality["total_articles"])
    duplicate_rate = int(quality["duplicate_articles"]) / total_articles if total_articles else 0.0
    warning_rate = int(quality["articles_with_warnings"]) / total_articles if total_articles else 0.0
    sentiment_mean = fmean(float(row["sentiment_index"]) for row in hourly) if hourly else 0.0
    coverage_mean = fmean(float(row["evidence_coverage"]) for row in hourly) if hourly else 0.0
    calculated = [datetime.fromisoformat(row["calculated_at"].replace("Z", "+00:00")) for row in indices]
    newest = max(calculated) if calculated else None
    freshness_hours = (generated_at - newest).total_seconds() / 3600 if newest else None
    thresholds = baseline["thresholds"]
    reference = baseline["reference"]
    checks = {
        "article_warning_rate": {"value": warning_rate, "limit": thresholds["maximum_warning_rate"], "status": "warning" if warning_rate > thresholds["maximum_warning_rate"] else "ok"},
        "duplicate_rate": {"value": duplicate_rate, "limit": thresholds["maximum_duplicate_rate"], "status": "warning" if duplicate_rate > thresholds["maximum_duplicate_rate"] else "ok"},
        "sentiment_mean_drift": {"value": abs(sentiment_mean - reference["hourly_sentiment_mean"]), "limit": thresholds["maximum_sentiment_mean_shift"], "status": "warning" if abs(sentiment_mean - reference["hourly_sentiment_mean"]) > thresholds["maximum_sentiment_mean_shift"] else "ok"},
        "coverage_mean_drift": {"value": abs(coverage_mean - reference["hourly_coverage_mean"]), "limit": thresholds["maximum_coverage_mean_shift"], "status": "warning" if abs(coverage_mean - reference["hourly_coverage_mean"]) > thresholds["maximum_coverage_mean_shift"] else "ok"},
        "freshness": {"value_hours": freshness_hours, "limit_hours": thresholds["maximum_freshness_hours"], "status": "warning" if freshness_hours is None or freshness_hours > thresholds["maximum_freshness_hours"] else "ok"},
    }
    report = {
        "status": "warning" if any(item["status"] == "warning" for item in checks.values()) else "ok",
        "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
        "baseline_version": baseline["version"],
        "baseline_scope": baseline["scope"],
        "model_registry": registry,
        "observations": {"articles": total_articles, "hourly_index_points": len(hourly)},
        "checks": checks,
        "environment": validate_runtime_environment(),
        "warning": "Synthetic baseline validates monitoring mechanics; it is not a production market baseline.",
    }
    output = root / "reports" / "monitoring" / "monitoring_summary.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CryptoPulse operational monitoring report")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--validate-environment", action="store_true")
    args = parser.parse_args()
    if args.validate_environment:
        result = validate_runtime_environment()
        print(json.dumps(result, indent=2))
        if result["status"] == "invalid":
            raise SystemExit(2)
        return
    print(json.dumps(generate_monitoring_report(args.project_root), indent=2))
