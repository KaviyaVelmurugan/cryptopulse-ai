# Data connectors

## Purpose

Connectors translate provider-specific responses into CryptoPulse AI's versioned contracts. Downstream validation, NLP, aggregation, and UI code consume internal records rather than vendor JSON.

## NewsAPI

**Endpoint:** `GET https://newsapi.org/v2/everything`

**Authentication:** `NEWS_API_KEY` sent in the `X-Api-Key` request header.

The connector queries Bitcoin or Ethereum, searches only titles and descriptions, requests English results ordered by publication time, and supports bounded pagination. It does not use the provider's `content` field because that field is documented as truncated.

Required retained fields include source name, URL, publication time, retrieval time, target asset, and licence-review status. Records missing a headline, description, source, URL, or valid timestamp are skipped with a warning rather than silently entering the dataset.

NewsAPI development access and production use are subject to the provider's current plan and terms. Do not redistribute article text without confirming permission.

## Coinbase Exchange candles

**Endpoint:** `GET https://api.exchange.coinbase.com/products/{product_id}/candles`

The connector supports `BTC-USD` and `ETH-USD` with `1h` or `1d` intervals. Coinbase candle data is exchange-specific and must not be described as the price or volume of the entire global crypto market.

Requests are limited to 300 buckets. Returned OHLCV values are validated, incomplete current intervals are excluded, and empty intervals may be absent because the exchange publishes no candle when there are no ticks.

## Reliability design

- Stable IDs make repeated ingestion idempotent.
- HTTP 429 and 5xx responses receive bounded exponential retries.
- Authentication failures are distinguished from rate limits and provider-format errors.
- API keys are never placed in query strings or committed files.
- A maximum page count prevents uncontrolled API consumption.
- Connector warnings preserve partial-success information.
- Tests use fake JSON transports and do not call live providers.

## Local setup

1. Create a NewsAPI development key at the provider's website.
2. Copy `.env.example` to `.env`.
3. Replace the placeholder with your key.
4. Do not commit `.env` or paste the key into screenshots, issues, logs, or chat messages.

Phase 3 implements the adapters and offline tests. A later phase will schedule them and persist raw provider responses under an access-controlled data policy.
