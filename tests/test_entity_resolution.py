from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from cryptopulse.contracts import AssetId, CleanedNewsArticle
from cryptopulse.entity_resolution import (
    extract_target_evidence,
    find_mentions,
    generate_entity_report,
)
from cryptopulse.sentiment import VaderBaseline


ROOT = Path(__file__).resolve().parents[1]


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


class MentionTests(unittest.TestCase):
    def test_names_symbols_and_aliases_resolve(self) -> None:
        mentions = find_mentions("Bitcoin, BTC and XBT rose; Ethereum, Ether and ETH fell.")
        self.assertEqual(sum(item.asset_id == AssetId.BITCOIN for item in mentions), 3)
        self.assertEqual(sum(item.asset_id == AssetId.ETHEREUM for item in mentions), 3)

    def test_symbols_do_not_match_inside_words(self) -> None:
        self.assertEqual(find_mentions("The method and ethnicity fields changed."), ())

    def test_lowercase_common_fragments_are_not_tickers(self) -> None:
        self.assertEqual(find_mentions("A method was selected for the batch."), ())


class EvidenceTests(unittest.TestCase):
    def test_multi_asset_clauses_have_different_evidence(self) -> None:
        article = cleaned(
            "Liquidity report. Bitcoin liquidity stayed stable while Ethereum liquidity weakened."
        )
        bitcoin = extract_target_evidence(article, AssetId.BITCOIN)
        ethereum = extract_target_evidence(article, AssetId.ETHEREUM)
        self.assertIn("Bitcoin liquidity stayed stable", bitcoin.evidence_text)
        self.assertNotIn("weakened", bitcoin.evidence_text)
        self.assertIn("Ethereum liquidity weakened", ethereum.evidence_text)
        self.assertNotIn("stayed stable", ethereum.evidence_text)
        self.assertIn("multi_asset_article", bitcoin.quality_flags)

    def test_vader_receives_target_specific_evidence(self) -> None:
        article = cleaned(
            "Liquidity report. Bitcoin liquidity stayed stable while Ethereum liquidity weakened."
        )
        model = VaderBaseline()
        when = datetime(2026, 1, 1, tzinfo=UTC)
        bitcoin = model.score(article, AssetId.BITCOIN, predicted_at=when)
        ethereum = model.score(article, AssetId.ETHEREUM, predicted_at=when)
        self.assertNotEqual(bitcoin.evidence_text, ethereum.evidence_text)
        self.assertNotIn("weakened", bitcoin.evidence_text)
        self.assertIn("weakened", ethereum.evidence_text)

    def test_missing_target_is_visible_and_uses_safe_fallback(self) -> None:
        article = cleaned("A general digital asset market report was published.")
        result = extract_target_evidence(article, AssetId.BITCOIN)
        self.assertEqual(result.resolution_status, "not_found_fallback_full_text")
        self.assertIn("target_not_mentioned", result.quality_flags)
        self.assertEqual(result.evidence_text, article.model_text)

    def test_ticker_without_crypto_context_is_marked_ambiguous(self) -> None:
        result = extract_target_evidence(cleaned("ETH announced a new research course."), AssetId.ETHEREUM)
        self.assertEqual(result.resolution_status, "ambiguous_ticker")
        self.assertIn("ticker_context_ambiguous", result.quality_flags)

    def test_sample_report_has_one_row_per_declared_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "target_evidence.csv"
            rows = generate_entity_report(ROOT / "data" / "sample" / "news_articles.csv", output)
            self.assertEqual(len(rows), 7)
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
