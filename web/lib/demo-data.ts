import type { EventPrediction, IndexPoint, ResearchSummary } from "./types";

const point = (
  id: string, asset: "bitcoin" | "ethereum", start: string, sentiment: number,
  evidence: number, coverage: number, event: string,
): IndexPoint => ({
  aggregate_id: id,
  resolution: "1h",
  asset_id: asset,
  window_start: start,
  window_end: new Date(new Date(start).getTime() + 3_600_000).toISOString(),
  sentiment_index: sentiment.toFixed(6),
  evidence_count: String(evidence),
  independent_source_count: String(evidence),
  duplicate_group_count: String(evidence ? 1 : 0),
  evidence_coverage: coverage.toFixed(6),
  leading_event: event,
  aggregation_version: "1.1.0",
  calculated_at: "2026-01-06T09:26:00Z",
});

export const demoIndices: IndexPoint[] = [
  point("btc-08", "bitcoin", "2026-01-05T08:00:00Z", 0.612169, 2, 0.333333, "adoption_partnership"),
  point("btc-09", "bitcoin", "2026-01-05T09:00:00Z", 0, 0, 0, ""),
  point("btc-10", "bitcoin", "2026-01-05T10:00:00Z", 0.1779, 1, 0.333333, "regulation_legal"),
  point("btc-11", "bitcoin", "2026-01-05T11:00:00Z", 0, 0, 0, ""),
  point("btc-12", "bitcoin", "2026-01-05T12:00:00Z", 0.296, 1, 0.333333, "market_commentary"),
  point("eth-08", "ethereum", "2026-01-05T08:00:00Z", 0, 0, 0, ""),
  point("eth-09", "ethereum", "2026-01-05T09:00:00Z", -0.0772, 1, 0.333333, "security_incident"),
  point("eth-10", "ethereum", "2026-01-05T10:00:00Z", 0, 0, 0, ""),
  point("eth-11", "ethereum", "2026-01-05T11:00:00Z", 0.4767, 1, 0.333333, "protocol_technical"),
  point("eth-12", "ethereum", "2026-01-05T12:00:00Z", -0.3182, 1, 0.333333, "market_commentary"),
  { ...point("btc-day", "bitcoin", "2026-01-05T00:00:00Z", 0.440209, 4, 0.6, "adoption_partnership"), resolution: "1d" },
  { ...point("eth-day", "ethereum", "2026-01-05T00:00:00Z", 0.12793, 3, 0.6, "protocol_technical"), resolution: "1d" },
];

const event = (
  id: string, asset: "bitcoin" | "ethereum", label: string, strength: number,
  evidence: string, terms: string,
): EventPrediction => ({
  prediction_id: id,
  article_id: id.replace("event-", "news-"),
  target_asset_id: asset,
  primary_event_label: label,
  predicted_labels: label,
  confidence: "1.000000",
  evidence_strength: strength.toFixed(6),
  matched_terms: terms,
  evidence_text: evidence,
});

export const demoEvents: EventPrediction[] = [
  event("event-btc-adoption", "bitcoin", "adoption_partnership", 0.353,
    "Payment network expands Bitcoin settlement pilot with regional merchants.",
    "settlement pilot|payment provider"),
  event("event-btc-regulation", "bitcoin", "regulation_legal", 0.293,
    "Committee announced a hearing covering custody rules for Bitcoin.", "hearing|custody rules|committee"),
  event("event-btc-market", "bitcoin", "market_commentary", 0.333,
    "Market note found stable Bitcoin liquidity.", "liquidity|market note"),
  event("event-eth-security", "ethereum", "security_incident", 0.333,
    "Test-network exploit delayed an Ethereum upgrade during a security review.", "exploit|security incident"),
  event("event-eth-protocol", "ethereum", "protocol_technical", 0.476,
    "Ethereum client update improved test performance and reduced finality delays.",
    "client update|client release|finality"),
  event("event-eth-market", "ethereum", "market_commentary", 0.167,
    "Ethereum liquidity weakened during the observed hour.", "liquidity"),
];

export const demoResearch: ResearchSummary = {
  warning: "Association is not causation, and these results are not trading advice.",
  sample_count: 3,
  development_count: 2,
  test_count: 1,
  inference_status: "not_run_requires_at_least_30_observations",
  correlations_are_descriptive_only: true,
  correlations: {
    forward_return: { pearson: -0.984405, spearman: -1 },
    future_volume_change: { pearson: 0.553821, spearman: 0.5 },
    future_range_volatility: { pearson: -0.660227, spearman: -0.5 },
  },
};
