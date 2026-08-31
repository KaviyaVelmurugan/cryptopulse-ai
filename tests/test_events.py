from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from cryptopulse.contracts import AssetId, CleanedNewsArticle, EventLabel
from cryptopulse.events import ExplainableEventClassifier, generate_event_reports
from cryptopulse.validation import validate_event_prediction


ROOT = Path(__file__).resolve().parents[1]
WHEN = datetime(2026, 1, 7, tzinfo=UTC)


def cleaned(text: str) -> CleanedNewsArticle:
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


class EventClassifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.classifier = ExplainableEventClassifier()

    def score(self, text: str):
        return self.classifier.score(cleaned(text), AssetId.BITCOIN, predicted_at=WHEN)

    def test_security_incident_is_explained(self) -> None:
        result = self.score("A Bitcoin protocol exploit caused a serious security incident.")
        self.assertEqual(result.primary_event_label, EventLabel.SECURITY_INCIDENT)
        self.assertIn("security_incident:exploit", result.matched_terms)
        self.assertGreater(result.evidence_strength, 0)

    def test_regulation_and_adoption_examples(self) -> None:
        regulation = self.score("A committee scheduled a hearing on Bitcoin custody rules.")
        adoption = self.score("A payment provider expanded a Bitcoin settlement pilot to merchants.")
        self.assertEqual(regulation.primary_event_label, EventLabel.REGULATION_LEGAL)
        self.assertEqual(adoption.primary_event_label, EventLabel.ADOPTION_PARTNERSHIP)

    def test_multiple_strong_events_are_preserved(self) -> None:
        result = self.score(
            "A Bitcoin exchange outage left withdrawals suspended after a security incident, exploit, and breach."
        )
        self.assertEqual(result.primary_event_label, EventLabel.SECURITY_INCIDENT)
        self.assertIn(EventLabel.EXCHANGE_INCIDENT, result.predicted_labels)

    def test_unknown_event_is_not_forced(self) -> None:
        result = self.score("Bitcoin was mentioned in a short general bulletin.")
        self.assertEqual(result.primary_event_label, EventLabel.INSUFFICIENT_EVIDENCE)
        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(result.matched_terms, ())
        self.assertIs(validate_event_prediction(result), result)

    def test_identity_is_time_independent(self) -> None:
        article = cleaned("Bitcoin liquidity and market volatility increased.")
        first = self.classifier.score(article, AssetId.BITCOIN, predicted_at=WHEN)
        second = self.classifier.score(
            article, AssetId.BITCOIN, predicted_at=datetime(2026, 2, 1, tzinfo=UTC)
        )
        self.assertEqual(first.prediction_id, second.prediction_id)


class EventReportTests(unittest.TestCase):
    def test_sample_reports_are_generated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            metrics = generate_event_reports(
                ROOT / "data" / "sample" / "news_articles.csv",
                ROOT / "data" / "sample" / "annotations.csv",
                output,
                predicted_at=WHEN,
            )
            self.assertEqual(metrics["all_records"].sample_count, 7)
            self.assertEqual(metrics["deduplicated_records"].sample_count, 6)
            self.assertEqual(metrics["locked_test_split"].sample_count, 2)
            self.assertIn("security_incident", metrics["locked_test_split"].per_class)
            saved = json.loads((output / "event_metrics.json").read_text(encoding="utf-8"))
            self.assertIn("not performance claims", saved["warning"])
            self.assertTrue((output / "event_predictions.csv").exists())
            self.assertTrue((output / "event_errors.csv").exists())


if __name__ == "__main__":
    unittest.main()
