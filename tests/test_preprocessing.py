from __future__ import annotations

import csv
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from cryptopulse.preprocessing import (
    clean_article,
    clean_text,
    deduplicate_articles,
    detect_language,
    generate_quality_reports,
)
from cryptopulse.validation import load_csv, parse_news_row


ROOT = Path(__file__).resolve().parents[1]
NEWS_PATH = ROOT / "data" / "sample" / "news_articles.csv"


def sample_articles():
    return load_csv(NEWS_PATH, parse_news_row, "news_articles")


class CleaningTests(unittest.TestCase):
    def test_unicode_whitespace_and_truncation_are_cleaned(self) -> None:
        text, removed = clean_text("  Bitcoin\u00a0rose…   [+123 chars]  ")
        self.assertEqual(text, "Bitcoin rose")
        self.assertTrue(removed)

    def test_original_article_is_not_modified(self) -> None:
        article = sample_articles()[0]
        original_summary = article.summary
        cleaned = clean_article(article)
        self.assertEqual(article.summary, original_summary)
        self.assertNotEqual(id(article), id(cleaned))

    def test_conservative_language_baseline(self) -> None:
        language, confidence = detect_language(
            "The Bitcoin network expanded while the market remained active."
        )
        self.assertEqual(language, "en")
        self.assertGreater(confidence, 0.8)
        self.assertEqual(detect_language("比特币市场")[0], "unknown")


class DeduplicationTests(unittest.TestCase):
    def test_syndicated_sample_stories_form_one_group(self) -> None:
        articles = sample_articles()
        cleaned = {article.article_id: clean_article(article) for article in articles}
        result = deduplicate_articles(articles, cleaned)
        self.assertEqual(result.group_by_article_id["news_001"], result.group_by_article_id["news_002"])
        self.assertTrue(
            any(
                {match.left_article_id, match.right_article_id} == {"news_001", "news_002"}
                for match in result.matches
            )
        )

    def test_unrelated_assets_are_not_compared_as_duplicates(self) -> None:
        articles = sample_articles()
        left = articles[0]
        right = replace(
            left,
            article_id="news_other_asset",
            asset_ids=(articles[2].asset_ids[0],),
            source_url="https://example.com/other",
        )
        cleaned = {item.article_id: clean_article(item) for item in (left, right)}
        result = deduplicate_articles([left, right], cleaned)
        self.assertNotEqual(result.group_by_article_id[left.article_id], result.group_by_article_id[right.article_id])

    def test_same_url_is_an_exact_duplicate(self) -> None:
        left = sample_articles()[0]
        right = replace(left, article_id="news_exact_copy", headline="Different display headline")
        cleaned = {item.article_id: clean_article(item) for item in (left, right)}
        result = deduplicate_articles([left, right], cleaned)
        self.assertEqual(result.matches[0].match_type, "exact_url")

    def test_group_ids_are_stable_when_input_order_changes(self) -> None:
        articles = sample_articles()
        cleaned = {article.article_id: clean_article(article) for article in articles}
        forward = deduplicate_articles(articles, cleaned).group_by_article_id
        backward = deduplicate_articles(list(reversed(articles)), cleaned).group_by_article_id
        self.assertEqual(forward, backward)


class ReportingTests(unittest.TestCase):
    def test_report_files_are_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            summary = generate_quality_reports(NEWS_PATH, output)
            self.assertEqual(summary.total_articles, 6)
            self.assertEqual(summary.duplicate_groups, 1)
            self.assertEqual(summary.duplicate_articles, 2)
            with (output / "article_quality.csv").open("r", encoding="utf-8", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 6)
            self.assertTrue((output / "duplicate_matches.csv").exists())
            self.assertTrue((output / "summary.json").exists())


if __name__ == "__main__":
    unittest.main()
