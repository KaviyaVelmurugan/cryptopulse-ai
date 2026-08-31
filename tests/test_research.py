from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from cryptopulse.indexing import build_index_evidence
from cryptopulse.research import (
    MIN_INFERENCE_SAMPLE,
    benjamini_hochberg,
    build_observations,
    generate_research_reports,
    pearson,
    spearman,
)
from cryptopulse.validation import load_csv, parse_annotation_row, parse_market_row, parse_news_row


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample"


class StatisticTests(unittest.TestCase):
    def test_correlations_handle_direction_and_ties(self) -> None:
        self.assertAlmostEqual(pearson([1, 2, 3], [2, 4, 6]), 1.0)
        self.assertAlmostEqual(spearman([1, 2, 3], [3, 2, 1]), -1.0)
        self.assertIsNone(pearson([1, 1], [2, 3]))

    def test_benjamini_hochberg_is_monotonic_and_bounded(self) -> None:
        adjusted = benjamini_hochberg({"a": 0.01, "b": 0.04, "c": 0.20})
        self.assertLessEqual(adjusted["a"], adjusted["b"])
        self.assertLessEqual(adjusted["b"], adjusted["c"])
        self.assertTrue(all(0 <= value <= 1 for value in adjusted.values()))


class AlignmentTests(unittest.TestCase):
    def test_sample_alignment_is_strictly_forward_and_chronological(self) -> None:
        articles = load_csv(SAMPLE / "news_articles.csv", parse_news_row, "news")
        annotations = load_csv(SAMPLE / "annotations.csv", parse_annotation_row, "annotations")
        candles = load_csv(SAMPLE / "market_candles.csv", parse_market_row, "market")
        calculated_at = max(item.created_at for item in annotations)
        observations = build_observations(
            build_index_evidence(articles, predicted_at=calculated_at),
            candles,
            calculated_at=calculated_at,
        )
        self.assertEqual(len(observations), 3)
        self.assertEqual([item.chronological_split for item in observations], [
            "development", "development", "test"
        ])
        for item in observations:
            self.assertLessEqual(item.signal_available_at, item.signal_window_end)
            self.assertGreater(item.outcome_available_at, item.signal_available_at)
            self.assertGreater(item.future_close, 0)

    def test_reports_refuse_inference_on_tiny_sample(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            summary = generate_research_reports(
                SAMPLE / "news_articles.csv",
                SAMPLE / "annotations.csv",
                SAMPLE / "market_candles.csv",
                output,
            )
            self.assertEqual(summary["sample_count"], 3)
            self.assertIn(str(MIN_INFERENCE_SAMPLE), summary["inference_status"])
            self.assertTrue(summary["correlations_are_descriptive_only"])
            self.assertEqual(summary["raw_permutation_p_values"], {})
            saved = json.loads((output / "research_summary.json").read_text(encoding="utf-8"))
            self.assertIn("not trading advice", saved["warning"])
            self.assertTrue((output / "aligned_observations.csv").exists())


if __name__ == "__main__":
    unittest.main()
