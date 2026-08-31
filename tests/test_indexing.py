from __future__ import annotations

import csv
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptopulse.contracts import AssetId, EventLabel
from cryptopulse.indexing import IndexEvidence, aggregate_window, floor_window, generate_index_reports


ROOT = Path(__file__).resolve().parents[1]
START = datetime(2026, 1, 5, 8, tzinfo=UTC)
END = START + timedelta(hours=1)
CALCULATED = datetime(2026, 1, 6, tzinfo=UTC)


def evidence(
    article_id: str,
    score: float,
    *,
    minutes: int,
    source: str,
    duplicate_group: str,
) -> IndexEvidence:
    return IndexEvidence(
        article_id,
        AssetId.BITCOIN,
        START + timedelta(minutes=minutes),
        START + timedelta(minutes=minutes),
        source,
        duplicate_group,
        score,
        max(abs(score), 0.1),
        EventLabel.MARKET_COMMENTARY,
    )


class WindowTests(unittest.TestCase):
    def test_flooring_is_deterministic(self) -> None:
        value = datetime(2026, 1, 5, 8, 37, 42, tzinfo=UTC)
        self.assertEqual(floor_window(value, "1h"), START)
        self.assertEqual(floor_window(value, "1d"), START.replace(hour=0))

    def test_empty_window_is_visible_with_zero_coverage(self) -> None:
        result = aggregate_window(
            [], AssetId.BITCOIN, START, END, calculated_at=CALCULATED,
            half_life=timedelta(hours=1), coverage_target=3,
        )
        self.assertEqual(result.aggregate.sentiment_index, 0.0)
        self.assertEqual(result.aggregate.evidence_count, 0)
        self.assertEqual(result.aggregate.evidence_coverage, 0.0)
        self.assertIsNone(result.leading_event)

    def test_article_processed_after_window_is_not_used(self) -> None:
        item = evidence("late", 0.8, minutes=30, source="wire", duplicate_group="dup_1")
        item = IndexEvidence(
            item.article_id, item.asset_id, item.published_at, END + timedelta(minutes=1),
            item.source_name, item.duplicate_group_id, item.sentiment_score,
            item.confidence_weight, item.primary_event,
        )
        result = aggregate_window(
            [item], AssetId.BITCOIN, START, END, calculated_at=CALCULATED,
            half_life=timedelta(hours=1), coverage_target=3,
        )
        self.assertEqual(result.aggregate.evidence_count, 0)

    def test_duplicate_articles_share_one_group_weight(self) -> None:
        rows = [
            evidence("a", 0.8, minutes=50, source="wire_a", duplicate_group="dup_1"),
            evidence("b", 0.8, minutes=50, source="wire_b", duplicate_group="dup_1"),
            evidence("c", -0.8, minutes=50, source="wire_c", duplicate_group="dup_2"),
        ]
        result = aggregate_window(
            rows, AssetId.BITCOIN, START, END, calculated_at=CALCULATED,
            half_life=timedelta(hours=1), coverage_target=3,
        )
        positive_weight = sum(
            item.combined_weight for item in result.contributions if item.article_id in {"a", "b"}
        )
        negative_weight = next(
            item.combined_weight for item in result.contributions if item.article_id == "c"
        )
        self.assertAlmostEqual(positive_weight, negative_weight, places=5)
        self.assertAlmostEqual(result.aggregate.sentiment_index, 0.0, places=5)

    def test_source_repetition_is_downweighted(self) -> None:
        rows = [
            evidence("a", 0.5, minutes=50, source="same", duplicate_group="dup_1"),
            evidence("b", 0.5, minutes=50, source="same", duplicate_group="dup_2"),
            evidence("c", -0.5, minutes=50, source="independent", duplicate_group="dup_3"),
        ]
        result = aggregate_window(
            rows, AssetId.BITCOIN, START, END, calculated_at=CALCULATED,
            half_life=timedelta(hours=1), coverage_target=3,
        )
        repeated = sum(
            item.combined_weight for item in result.contributions if item.article_id in {"a", "b"}
        )
        independent = next(item.combined_weight for item in result.contributions if item.article_id == "c")
        self.assertAlmostEqual(repeated, independent, places=5)


class ReportTests(unittest.TestCase):
    def test_reports_include_empty_windows_and_traceable_contributions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            counts = generate_index_reports(
                ROOT / "data" / "sample" / "news_articles.csv",
                ROOT / "data" / "sample" / "annotations.csv",
                output,
            )
            self.assertEqual(counts["index_rows"], 12)
            self.assertEqual(counts["contribution_rows"], 14)
            self.assertEqual(counts["sensitivity_rows"], 8)
            with (output / "sentiment_index.csv").open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertTrue(any(row["evidence_count"] == "0" for row in rows))
            for filename in (
                "sentiment_index.csv", "index_contributions.csv", "index_sensitivity.csv",
                "methodology.json",
            ):
                self.assertTrue((output / filename).exists())


if __name__ == "__main__":
    unittest.main()
