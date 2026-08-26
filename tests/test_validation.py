from __future__ import annotations

import csv
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from cryptopulse.contracts import (
    AssetId,
    SentimentAggregate,
    SentimentLabel,
    SentimentPrediction,
)
from cryptopulse.validation import (
    DatasetValidationError,
    parse_market_row,
    parse_news_row,
    validate_aggregate,
    validate_dataset_directory,
    validate_prediction,
)


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample"


def first_row(filename: str) -> dict[str, str]:
    with (SAMPLE / filename).open("r", encoding="utf-8", newline="") as stream:
        return next(csv.DictReader(stream))


class ContractTests(unittest.TestCase):
    def test_news_parser_preserves_point_in_time_order(self) -> None:
        article = parse_news_row(first_row("news_articles.csv"))
        self.assertLessEqual(article.published_at, article.retrieved_at)
        self.assertLessEqual(article.retrieved_at, article.processed_at)
        self.assertEqual(article.asset_ids, (AssetId.BITCOIN,))

    def test_future_retrieval_is_rejected(self) -> None:
        row = first_row("news_articles.csv")
        row["retrieved_at"] = "2026-01-05T08:00:00Z"
        with self.assertRaisesRegex(ValueError, "published_at <= retrieved_at"):
            parse_news_row(row)

    def test_non_utc_timestamp_is_rejected(self) -> None:
        row = first_row("news_articles.csv")
        row["published_at"] = "2026-01-05T13:40:00+05:30"
        with self.assertRaisesRegex(ValueError, "UTC timezone"):
            parse_news_row(row)

    def test_invalid_market_range_is_rejected(self) -> None:
        row = first_row("market_candles.csv")
        row["high_price"] = "99999.00"
        with self.assertRaisesRegex(ValueError, "high_price"):
            parse_market_row(row)

    def test_multi_asset_article_is_supported(self) -> None:
        with (SAMPLE / "news_articles.csv").open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        article = parse_news_row(rows[-1])
        self.assertEqual(set(article.asset_ids), {AssetId.BITCOIN, AssetId.ETHEREUM})

    def test_sentiment_labels_are_explicit(self) -> None:
        self.assertEqual({item.value for item in SentimentLabel}, {"negative", "neutral", "positive"})

    def test_prediction_probabilities_must_match_label(self) -> None:
        prediction = SentimentPrediction(
            prediction_id="pred_001",
            article_id="news_001",
            target_asset_id=AssetId.BITCOIN,
            negative_probability=0.1,
            neutral_probability=0.2,
            positive_probability=0.7,
            predicted_label=SentimentLabel.NEGATIVE,
            evidence_text="successful settlement pilot",
            model_name="test-model",
            model_version="1",
            preprocessing_version="1",
            predicted_at=datetime(2026, 1, 6, tzinfo=UTC),
        )
        with self.assertRaisesRegex(ValueError, "highest probability"):
            validate_prediction(prediction)

    def test_aggregate_counts_cannot_exceed_evidence(self) -> None:
        aggregate = SentimentAggregate(
            aggregate_id="agg_001",
            asset_id=AssetId.BITCOIN,
            window_start=datetime(2026, 1, 5, tzinfo=UTC),
            window_end=datetime(2026, 1, 6, tzinfo=UTC),
            sentiment_index=0.25,
            evidence_count=2,
            independent_source_count=3,
            duplicate_group_count=2,
            evidence_coverage=0.5,
            aggregation_version="1",
            calculated_at=datetime(2026, 1, 6, 0, 1, tzinfo=UTC),
        )
        with self.assertRaisesRegex(ValueError, "independent_source_count"):
            validate_aggregate(aggregate)


class DatasetTests(unittest.TestCase):
    def test_complete_sample_dataset(self) -> None:
        self.assertEqual(
            validate_dataset_directory(SAMPLE),
            {"news_articles": 6, "market_candles": 8, "annotations": 7},
        )

    def test_unknown_annotation_article_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for filename in ("news_articles.csv", "market_candles.csv", "annotations.csv"):
                (target / filename).write_text(
                    (SAMPLE / filename).read_text(encoding="utf-8"), encoding="utf-8"
                )
            annotation_path = target / "annotations.csv"
            text = annotation_path.read_text(encoding="utf-8").replace("news_001", "news_missing", 1)
            annotation_path.write_text(text, encoding="utf-8")
            with self.assertRaises(DatasetValidationError) as context:
                validate_dataset_directory(target)
            self.assertIn("unknown article", str(context.exception))


if __name__ == "__main__":
    unittest.main()
