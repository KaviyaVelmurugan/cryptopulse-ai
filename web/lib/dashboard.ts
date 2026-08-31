import type { AlertFinding, AlertRule, EventPrediction, IndexPoint } from "./types";

export const clamp = (value: number, minimum: number, maximum: number) =>
  Math.min(maximum, Math.max(minimum, value));

export const humanize = (value: string) =>
  value ? value.split("_").map((word) => word[0].toUpperCase() + word.slice(1)).join(" ") : "No event";

export const latestEvidencePoint = (points: IndexPoint[]) =>
  [...points].reverse().find((point) => Number(point.evidence_count) > 0) ?? points.at(-1);

export const sentimentTone = (value: number) =>
  value > 0.05 ? "positive" : value < -0.05 ? "negative" : "neutral";

export const formatUtcTime = (value: string) =>
  new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "UTC",
  }).format(new Date(value));

export const buildPath = (values: number[], width: number, height: number, padding = 18) => {
  if (!values.length) return "";
  const usableWidth = width - padding * 2;
  const usableHeight = height - padding * 2;
  return values.map((value, index) => {
    const x = padding + (values.length === 1 ? usableWidth / 2 : index * usableWidth / (values.length - 1));
    const y = padding + (1 - (clamp(value, -1, 1) + 1) / 2) * usableHeight;
    return `${index ? "L" : "M"}${x.toFixed(2)},${y.toFixed(2)}`;
  }).join(" ");
};

const csvCell = (value: string | number) => `"${String(value).replaceAll('"', '""')}"`;

export const indicesToCsv = (points: IndexPoint[]) => {
  const fields: (keyof IndexPoint)[] = [
    "window_start", "window_end", "asset_id", "resolution", "sentiment_index",
    "evidence_count", "independent_source_count", "evidence_coverage", "leading_event",
    "aggregation_version",
  ];
  return [fields.map(csvCell).join(","), ...points.map((point) => fields.map((field) => csvCell(point[field])).join(","))].join("\n");
};

export const evaluateAlerts = (
  points: IndexPoint[], events: EventPrediction[], rule: AlertRule,
): AlertFinding[] => points.flatMap((point) => {
  const sentiment = Number(point.sentiment_index);
  const coverage = Number(point.evidence_coverage);
  const matchingEvent = events.find((event) =>
    event.target_asset_id === point.asset_id
    && (!rule.eventCategory || event.primary_event_label === rule.eventCategory));
  const magnitudeMet = Math.abs(sentiment) >= rule.sentimentMagnitude;
  const coverageMet = coverage >= rule.minimumCoverage;
  const eventMet = !rule.eventCategory || Boolean(matchingEvent);
  if (!magnitudeMet || !coverageMet || !eventMet) return [];
  return [{
    id: `alert-${point.aggregate_id}-${rule.eventCategory || "any"}`,
    asset: point.asset_id,
    observedAt: point.window_end,
    title: `${humanize(point.asset_id)} research signal observed`,
    explanation: `Absolute sentiment ${Math.abs(sentiment).toFixed(3)} met ${rule.sentimentMagnitude.toFixed(2)} with ${Math.round(coverage * 100)}% evidence coverage${matchingEvent ? ` and ${humanize(matchingEvent.primary_event_label)} evidence` : ""}.`,
    severity: Math.abs(sentiment) >= 0.5 ? "attention" : "notice",
  } satisfies AlertFinding];
});
