import type { IndexPoint } from "./types";

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
