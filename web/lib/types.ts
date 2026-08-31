export type Asset = "bitcoin" | "ethereum";
export type Resolution = "1h" | "1d";

export interface IndexPoint {
  aggregate_id: string;
  resolution: Resolution;
  asset_id: Asset;
  window_start: string;
  window_end: string;
  sentiment_index: string;
  evidence_count: string;
  independent_source_count: string;
  duplicate_group_count: string;
  evidence_coverage: string;
  leading_event: string;
  aggregation_version: string;
  calculated_at: string;
}

export interface EventPrediction {
  prediction_id: string;
  article_id: string;
  target_asset_id: Asset;
  primary_event_label: string;
  predicted_labels: string;
  confidence: string;
  evidence_strength: string;
  matched_terms: string;
  evidence_text: string;
}

export interface ResearchSummary {
  warning: string;
  sample_count: number;
  development_count: number;
  test_count: number;
  inference_status: string;
  correlations_are_descriptive_only: boolean;
  correlations: Record<string, { pearson: number | null; spearman: number | null }>;
}

export interface AlertRule {
  sentimentMagnitude: number;
  minimumCoverage: number;
  eventCategory: string;
}

export interface AlertFinding {
  id: string;
  asset: Asset;
  observedAt: string;
  title: string;
  explanation: string;
  severity: "notice" | "attention";
}
