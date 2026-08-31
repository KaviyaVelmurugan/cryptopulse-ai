import { describe, expect, it } from "vitest";
import { buildPath, formatUtcTime, humanize, sentimentTone } from "./dashboard";

describe("dashboard presentation helpers", () => {
  it("humanizes event labels", () => {
    expect(humanize("security_incident")).toBe("Security Incident");
  });

  it("classifies sentiment using documented thresholds", () => {
    expect(sentimentTone(0.2)).toBe("positive");
    expect(sentimentTone(-0.2)).toBe("negative");
    expect(sentimentTone(0.01)).toBe("neutral");
  });

  it("builds bounded SVG paths", () => {
    expect(buildPath([-2, 0, 2], 300, 160)).toBe("M18.00,142.00 L150.00,80.00 L282.00,18.00");
  });

  it("formats chart times deterministically in UTC", () => {
    expect(formatUtcTime("2026-01-05T08:00:00Z")).toBe("08:00");
  });
});
