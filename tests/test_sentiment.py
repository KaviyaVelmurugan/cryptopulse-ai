from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from cryptopulse.contracts import AssetId, CleanedNewsArticle, SentimentLabel
from cryptopulse.sentiment import VaderBaseline, evaluate, generate_vader_reports, label_from_compound


ROOT = Path(__file__).resolve().parents[1]


class ThresholdTests(unittest.TestCase):
    def test_standard_vader_boundaries(self) -> None:
        self.assertEqual(label_from_compound(-0.05), SentimentLabel.NEGATIVE)
        self.assertEqual(label_from_compound(-0.0499), SentimentLabel.NEUTRAL)
        self.assertEqual(label_from_compound(0.0499), SentimentLabel.NEUTRAL)
        self.assertEqual(label_from_compound(0.05), SentimentLabel.POSITIVE)

    def test_invalid_compound_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            label_from_compound(1.01)


class VaderTests(unittest.TestCase):
    def test_positive_and_negative_language(self) -> None:
        baseline = VaderBaseline()
        base = dict(
            article_id="news_test",
            cleaned_headline="",
            cleaned_summary="",
            detected_language="en",
            language_confidence=1.0,
            quality_flags=(),
            preprocessing_version="1.0.0",
        )
        positive = CleanedNewsArticle(model_text="The upgrade was excellent and successful.", **base)
        negative = CleanedNewsArticle(model_text="The exploit was terrible and caused severe losses.", **base)
        when = datetime(2026, 1, 1, tzinfo=UTC)
        self.assertEqual(
            baseline.score(positive, AssetId.BITCOIN, predicted_at=when).predicted_label,
            SentimentLabel.POSITIVE,
        )
        self.assertEqual(
            baseline.score(negative, AssetId.BITCOIN, predicted_at=when).predicted_label,
            SentimentLabel.NEGATIVE,
        )

    def test_prediction_id_is_stable(self) -> None:
        article = CleanedNewsArticle(
            article_id="news_test",
            cleaned_headline="Stable market",
            cleaned_summary="The market was stable.",
            model_text="Stable market. The market was stable.",
            detected_language="en",
            language_confidence=1.0,
            quality_flags=(),
            preprocessing_version="1.0.0",
        )
        baseline = VaderBaseline()
        first = baseline.score(article, AssetId.BITCOIN, predicted_at=datetime(2026, 1, 1, tzinfo=UTC))
        second = baseline.score(article, AssetId.BITCOIN, predicted_at=datetime(2026, 2, 1, tzinfo=UTC))
        self.assertEqual(first.prediction_id, second.prediction_id)


class EvaluationTests(unittest.TestCase):
    def test_empty_evaluation_is_defined(self) -> None:
        metrics = evaluate([], {})
        self.assertEqual(metrics.sample_count, 0)
        self.assertEqual(metrics.macro_f1, 0.0)

    def test_reports_are_generated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            metrics = generate_vader_reports(
                ROOT / "data" / "sample" / "news_articles.csv",
                ROOT / "data" / "sample" / "annotations.csv",
                output,
                predicted_at=datetime(2026, 1, 7, tzinfo=UTC),
            )
            self.assertEqual(metrics["all_records"].sample_count, 7)
            self.assertEqual(metrics["deduplicated_records"].sample_count, 6)
            self.assertEqual(metrics["locked_test_split"].sample_count, 2)
            for filename in (
                "vader_predictions.csv", "vader_metrics.json", "vader_confusion_matrix.csv",
                "vader_error_analysis.csv",
            ):
                self.assertTrue((output / filename).exists())


if __name__ == "__main__":
    unittest.main()
