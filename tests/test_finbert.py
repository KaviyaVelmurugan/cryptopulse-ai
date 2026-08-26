from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from cryptopulse.contracts import AssetId, CleanedNewsArticle, SentimentLabel
from cryptopulse.finbert import (
    FINBERT_REVISION,
    FinBertBaseline,
    calibration,
    generate_comparison_reports,
)


ROOT = Path(__file__).resolve().parents[1]


class FakeRunner:
    def __call__(self, texts):
        outputs = []
        for text in texts:
            if "loss" in text.lower() or "exploit" in text.lower():
                scores = (0.8, 0.1, 0.1)
            elif "stable" in text.lower():
                scores = (0.1, 0.8, 0.1)
            else:
                scores = (0.1, 0.1, 0.8)
            outputs.append([
                {"label": "negative", "score": scores[0]},
                {"label": "neutral", "score": scores[1]},
                {"label": "positive", "score": scores[2]},
            ])
        return outputs


def article(text: str = "Protocol adoption increased.") -> CleanedNewsArticle:
    return CleanedNewsArticle(
        article_id="news_test",
        cleaned_headline=text,
        cleaned_summary="",
        model_text=text,
        detected_language="en",
        language_confidence=1.0,
        quality_flags=(),
        preprocessing_version="1.0.0",
    )


class FinBertTests(unittest.TestCase):
    def test_label_mapping_and_revision_are_recorded(self) -> None:
        result = FinBertBaseline(FakeRunner()).score_many(
            [(article(), AssetId.BITCOIN)], predicted_at=datetime(2026, 1, 1, tzinfo=UTC)
        )[0]
        self.assertEqual(result.predicted_label, SentimentLabel.POSITIVE)
        self.assertEqual(result.model_version, FINBERT_REVISION)
        self.assertAlmostEqual(
            result.negative_probability + result.neutral_probability + result.positive_probability,
            1.0,
        )

    def test_prediction_identity_is_target_specific_and_time_independent(self) -> None:
        model = FinBertBaseline(FakeRunner())
        first = model.score_many(
            [(article(), AssetId.BITCOIN)], predicted_at=datetime(2026, 1, 1, tzinfo=UTC)
        )[0]
        later = model.score_many(
            [(article(), AssetId.BITCOIN)], predicted_at=datetime(2026, 2, 1, tzinfo=UTC)
        )[0]
        ethereum = model.score_many(
            [(article(), AssetId.ETHEREUM)], predicted_at=datetime(2026, 1, 1, tzinfo=UTC)
        )[0]
        self.assertEqual(first.prediction_id, later.prediction_id)
        self.assertNotEqual(first.prediction_id, ethereum.prediction_id)

    def test_invalid_runner_output_is_rejected(self) -> None:
        def invalid(_texts):
            return [[{"label": "positive", "score": 1.0}]]

        with self.assertRaises(ValueError):
            FinBertBaseline(invalid).score_many(
                [(article(), AssetId.BITCOIN)], predicted_at=datetime(2026, 1, 1, tzinfo=UTC)
            )

    def test_comparison_reports_have_honest_warning(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            report = generate_comparison_reports(
                ROOT / "data" / "sample" / "news_articles.csv",
                ROOT / "data" / "sample" / "annotations.csv",
                output,
                predicted_at=datetime(2026, 1, 7, tzinfo=UTC),
                runner=FakeRunner(),
            )
            self.assertIn("not model-performance claims", report["warning"])
            saved = json.loads((output / "model_comparison.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["evaluations"]["locked_test_split"]["finbert"]["sample_count"], 2)
            self.assertTrue((output / "finbert_predictions.csv").exists())


if __name__ == "__main__":
    unittest.main()
