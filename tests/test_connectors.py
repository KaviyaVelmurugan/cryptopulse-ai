from __future__ import annotations

import unittest
from io import BytesIO
from datetime import UTC, datetime
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from cryptopulse.connectors.base import FetchResult, RateLimitError, UrllibJsonTransport
from cryptopulse.connectors.coinbase import CoinbaseCandleConnector
from cryptopulse.connectors.newsapi import NewsApiConnector
from cryptopulse.contracts import AssetId


NOW = datetime(2026, 8, 26, 12, 0, tzinfo=UTC)


class FakeTransport:
    def __init__(self, responses: list[object]):
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def get_json(self, url, *, params, headers):
        self.calls.append({"url": url, "params": params, "headers": headers})
        return self.responses.pop(0)


class FakeHttpResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def news_payload(*articles, total=None):
    return {
        "status": "ok",
        "totalResults": len(articles) if total is None else total,
        "articles": list(articles),
    }


def article(url="https://example.com/story", published="2026-08-26T10:00:00Z"):
    return {
        "source": {"id": "example", "name": "Example News"},
        "author": "Reporter",
        "title": "Bitcoin settlement network expands",
        "description": "A payment network expanded its Bitcoin settlement programme.",
        "url": url,
        "publishedAt": published,
        "content": "This intentionally truncated provider field is not used. [+1200 chars]",
    }


class NewsApiConnectorTests(unittest.TestCase):
    def test_maps_article_and_keeps_key_out_of_query(self) -> None:
        transport = FakeTransport([news_payload(article())])
        connector = NewsApiConnector("secret-test-key", transport=transport, clock=lambda: NOW)
        result = connector.fetch(
            AssetId.BITCOIN,
            from_time=datetime(2026, 8, 26, 0, 0, tzinfo=UTC),
            to_time=datetime(2026, 8, 26, 11, 0, tzinfo=UTC),
        )
        self.assertIsInstance(result, FetchResult)
        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.records[0].asset_ids, (AssetId.BITCOIN,))
        self.assertNotIn("[+1200 chars]", result.records[0].summary)
        self.assertEqual(transport.calls[0]["headers"], {"X-Api-Key": "secret-test-key"})
        self.assertNotIn("apiKey", transport.calls[0]["params"])

    def test_stable_url_produces_idempotent_identifier(self) -> None:
        first = FakeTransport([news_payload(article("https://Example.com/story#section"))])
        second = FakeTransport([news_payload(article("https://example.com/story"))])
        kwargs = {
            "asset_id": AssetId.BITCOIN,
            "from_time": datetime(2026, 8, 26, 0, 0, tzinfo=UTC),
            "to_time": datetime(2026, 8, 26, 11, 0, tzinfo=UTC),
        }
        first_id = NewsApiConnector("key", transport=first, clock=lambda: NOW).fetch(**kwargs).records[0].article_id
        second_id = NewsApiConnector("key", transport=second, clock=lambda: NOW).fetch(**kwargs).records[0].article_id
        self.assertEqual(first_id, second_id)

    def test_paginates_until_total_is_collected(self) -> None:
        transport = FakeTransport(
            [
                news_payload(article("https://example.com/one"), total=2),
                news_payload(article("https://example.com/two"), total=2),
            ]
        )
        result = NewsApiConnector("key", transport=transport, clock=lambda: NOW).fetch(
            AssetId.ETHEREUM,
            from_time=datetime(2026, 8, 26, 0, 0, tzinfo=UTC),
            to_time=datetime(2026, 8, 26, 11, 0, tzinfo=UTC),
            page_size=1,
            max_pages=3,
        )
        self.assertEqual(len(result.records), 2)
        self.assertEqual([call["params"]["page"] for call in transport.calls], [1, 2])

    def test_invalid_article_becomes_warning(self) -> None:
        invalid = article()
        invalid["description"] = None
        result = NewsApiConnector(
            "key", transport=FakeTransport([news_payload(invalid)]), clock=lambda: NOW
        ).fetch(
            AssetId.BITCOIN,
            from_time=datetime(2026, 8, 26, 0, 0, tzinfo=UTC),
            to_time=datetime(2026, 8, 26, 11, 0, tzinfo=UTC),
        )
        self.assertEqual(result.records, ())
        self.assertEqual(len(result.warnings), 1)


class HttpTransportTests(unittest.TestCase):
    def test_transient_network_failure_is_retried(self) -> None:
        sleeps = []
        transport = UrllibJsonTransport(max_attempts=2, sleep=sleeps.append)
        with patch(
            "cryptopulse.connectors.base.urlopen",
            side_effect=[URLError("temporary"), FakeHttpResponse(b'{"status":"ok"}')],
        ):
            result = transport.get_json("https://example.com", params={}, headers={})
        self.assertEqual(result, {"status": "ok"})
        self.assertEqual(sleeps, [1.0])

    def test_repeated_rate_limit_has_specific_error(self) -> None:
        error = HTTPError("https://example.com", 429, "limited", {}, BytesIO())
        transport = UrllibJsonTransport(max_attempts=2, sleep=lambda _: None)
        with patch("cryptopulse.connectors.base.urlopen", side_effect=[error, error]):
            with self.assertRaises(RateLimitError):
                transport.get_json("https://example.com", params={}, headers={})


class CoinbaseConnectorTests(unittest.TestCase):
    def test_maps_and_orders_complete_candles(self) -> None:
        transport = FakeTransport(
            [[
                [1787738400, 109.0, 113.0, 110.0, 112.0, 25.0],
                [1787734800, 99.0, 111.0, 100.0, 110.0, 20.0],
            ]]
        )
        result = CoinbaseCandleConnector(transport=transport, clock=lambda: NOW).fetch(
            AssetId.BITCOIN,
            from_time=datetime(2026, 8, 26, 8, 0, tzinfo=UTC),
            to_time=datetime(2026, 8, 26, 11, 0, tzinfo=UTC),
            interval="1h",
        )
        self.assertEqual(len(result.records), 2)
        self.assertLess(result.records[0].open_time, result.records[1].open_time)
        self.assertEqual(result.records[0].provider, "coinbase_exchange")
        self.assertEqual(transport.calls[0]["params"]["granularity"], 3600)

    def test_incomplete_candle_is_skipped(self) -> None:
        start = int(datetime(2026, 8, 26, 11, 30, tzinfo=UTC).timestamp())
        result = CoinbaseCandleConnector(
            transport=FakeTransport([[[start, 99, 105, 100, 103, 5]]]), clock=lambda: NOW
        ).fetch(
            AssetId.ETHEREUM,
            from_time=datetime(2026, 8, 26, 11, 0, tzinfo=UTC),
            to_time=datetime(2026, 8, 26, 12, 0, tzinfo=UTC),
        )
        self.assertEqual(result.records, ())
        self.assertIn("not complete", result.warnings[0])

    def test_more_than_300_buckets_is_rejected(self) -> None:
        connector = CoinbaseCandleConnector(transport=FakeTransport([]), clock=lambda: NOW)
        with self.assertRaisesRegex(ValueError, "300"):
            connector.fetch(
                AssetId.BITCOIN,
                from_time=datetime(2026, 8, 1, tzinfo=UTC),
                to_time=datetime(2026, 8, 20, tzinfo=UTC),
                interval="1h",
            )


if __name__ == "__main__":
    unittest.main()
