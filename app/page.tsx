"use client";

import { useEffect, useMemo, useState } from "react";
import { buildPath, evaluateAlerts, formatUtcTime, humanize, indicesToCsv, latestEvidencePoint, sentimentTone } from "@/lib/dashboard";
import { demoEvents, demoIndices, demoResearch } from "@/lib/demo-data";
import type { AlertRule, Asset, EventPrediction, IndexPoint, ResearchSummary, Resolution } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

function SentimentChart({ points, asset }: { points: IndexPoint[]; asset: Asset }) {
  const values = points.map((point) => Number(point.sentiment_index));
  const coverage = points.map((point) => Number(point.evidence_coverage));
  const width = 720;
  const height = 250;
  return (
    <div className="chart-wrap">
      <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby="chart-title chart-desc">
        <title id="chart-title">{`${humanize(asset)} sentiment and evidence coverage`}</title>
        <desc id="chart-desc">Sentiment ranges from negative one to positive one. Coverage is shown as columns.</desc>
        <defs>
          <linearGradient id="line-gradient" x1="0" x2="1">
            <stop offset="0" stopColor="#8b5cf6" />
            <stop offset="1" stopColor="#30d5c8" />
          </linearGradient>
        </defs>
        {[18, 80, 142, 204].map((y) => <line key={y} x1="18" x2="702" y1={y} y2={y} className="grid-line" />)}
        <line x1="18" x2="702" y1="125" y2="125" className="zero-line" />
        {coverage.map((value, index) => {
          const x = 18 + (points.length === 1 ? 342 : index * 684 / (points.length - 1));
          return <rect key={`${points[index].aggregate_id}-coverage`} x={x - 14} y={232 - value * 72} width="28"
            height={value * 72} rx="6" className="coverage-bar" />;
        })}
        <path d={buildPath(values, width, height)} className="sentiment-line" />
        {values.map((value, index) => {
          const x = 18 + (values.length === 1 ? 342 : index * 684 / (values.length - 1));
          const y = 18 + (1 - (Math.max(-1, Math.min(1, value)) + 1) / 2) * 214;
          return <circle key={points[index].aggregate_id} cx={x} cy={y} r="5" className={`chart-dot ${sentimentTone(value)}`} />;
        })}
      </svg>
      <div className="chart-labels" aria-hidden="true">
        {points.map((point) => <span key={point.aggregate_id}>{formatUtcTime(point.window_start)}</span>)}
      </div>
      <div className="legend"><span><i className="legend-line" />Sentiment index</span><span><i className="legend-bar" />Evidence coverage</span></div>
    </div>
  );
}

function EventCard({ event }: { event: EventPrediction }) {
  const strength = Math.round(Number(event.evidence_strength) * 100);
  return (
    <article className="event-card">
      <div className="event-meta"><span className={`event-icon ${event.primary_event_label}`}>◆</span><span>{humanize(event.primary_event_label)}</span></div>
      <p>{event.evidence_text}</p>
      <div className="term-list">{event.matched_terms.split("|").map((term) => <span key={term}>{humanize(term.split(":").at(-1) ?? term)}</span>)}</div>
      <div className="strength"><span>Evidence strength</span><strong>{strength}%</strong><div><i style={{ width: `${strength}%` }} /></div></div>
    </article>
  );
}

export default function Dashboard() {
  const [asset, setAsset] = useState<Asset>("bitcoin");
  const [resolution, setResolution] = useState<Resolution>("1h");
  const [indices, setIndices] = useState<IndexPoint[]>(demoIndices);
  const [events, setEvents] = useState<EventPrediction[]>(demoEvents);
  const [research, setResearch] = useState<ResearchSummary>(demoResearch);
  const [source, setSource] = useState<"api" | "demo">("demo");
  const [alertRule, setAlertRule] = useState<AlertRule>({ sentimentMagnitude: 0.3, minimumCoverage: 0.3, eventCategory: "" });

  useEffect(() => {
    if (!API_BASE) return;
    const controller = new AbortController();
    Promise.all([
      fetch(`${API_BASE}/api/v1/indices`, { signal: controller.signal }).then((response) => {
        if (!response.ok) throw new Error("Index API unavailable");
        return response.json() as Promise<IndexPoint[]>;
      }),
      fetch(`${API_BASE}/api/v1/events`, { signal: controller.signal }).then((response) => {
        if (!response.ok) throw new Error("Event API unavailable");
        return response.json() as Promise<EventPrediction[]>;
      }),
      fetch(`${API_BASE}/api/v1/research-summary`, { signal: controller.signal }).then((response) => {
        if (!response.ok) throw new Error("Research API unavailable");
        return response.json() as Promise<ResearchSummary>;
      }),
    ]).then(([nextIndices, nextEvents, nextResearch]) => {
      setIndices(nextIndices); setEvents(nextEvents); setResearch(nextResearch); setSource("api");
    }).catch(() => setSource("demo"));
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const saved = window.localStorage.getItem("cryptopulse-alert-rule");
    if (!saved) return;
    let parsed: AlertRule;
    try { parsed = JSON.parse(saved) as AlertRule; } catch { window.localStorage.removeItem("cryptopulse-alert-rule"); return; }
    const frame = window.requestAnimationFrame(() => setAlertRule(parsed));
    return () => window.cancelAnimationFrame(frame);
  }, []);

  const visiblePoints = useMemo(() => indices.filter((point) => point.asset_id === asset && point.resolution === resolution), [indices, asset, resolution]);
  const visibleEvents = useMemo(() => events.filter((event) => event.target_asset_id === asset).slice(0, 3), [events, asset]);
  const latest = latestEvidencePoint(visiblePoints);
  const sentiment = Number(latest?.sentiment_index ?? 0);
  const coverage = Number(latest?.evidence_coverage ?? 0);
  const evidence = Number(latest?.evidence_count ?? 0);
  const alertFindings = useMemo(() => evaluateAlerts(indices, events, alertRule).slice(-5).reverse(), [indices, events, alertRule]);

  const updateAlertRule = (next: AlertRule) => {
    setAlertRule(next);
    window.localStorage.setItem("cryptopulse-alert-rule", JSON.stringify(next));
  };

  const downloadCsv = () => {
    const blob = new Blob([indicesToCsv(indices)], { type: "text/csv;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "cryptopulse-derived-sentiment-index.csv";
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return (
    <main>
      <header className="topbar">
        <a href="#overview" className="brand" aria-label="CryptoPulse AI home"><span className="brand-mark">CP</span><span>CryptoPulse <b>AI</b></span></a>
        <nav aria-label="Primary navigation"><a href="#overview">Overview</a><a href="#drivers">Event drivers</a><a href="#research">Research</a><a href="#outputs">Reports & alerts</a></nav>
        <span className={`live-pill ${source}`}><i />{source === "api" ? "API connected" : "Synthetic demo"}</span>
      </header>

      <section className="hero" id="overview">
        <div><p className="eyebrow">Explainable crypto market intelligence</p><h1>Read the signal.<br /><em>Inspect the evidence.</em></h1>
          <p className="hero-copy">Target-specific Bitcoin and Ethereum sentiment, event context, and chronological market research—without trading claims.</p></div>
        <div className="hero-note"><span>Research boundary</span><strong>Association ≠ causation</strong><p>Three synthetic observations validate the pipeline, not market performance.</p></div>
      </section>

      <section className="control-row" aria-label="Dashboard filters">
        <div className="segmented" role="group" aria-label="Asset">
          {(["bitcoin", "ethereum"] as Asset[]).map((item) => <button key={item} className={asset === item ? "active" : ""} onClick={() => setAsset(item)} aria-pressed={asset === item}><span className={`coin ${item}`}>{item === "bitcoin" ? "₿" : "Ξ"}</span>{humanize(item)}</button>)}
        </div>
        <div className="segmented compact" role="group" aria-label="Resolution">
          {(["1h", "1d"] as Resolution[]).map((item) => <button key={item} className={resolution === item ? "active" : ""} onClick={() => setResolution(item)} aria-pressed={resolution === item}>{item === "1h" ? "Hourly" : "Daily"}</button>)}
        </div>
        <p className="updated">Data timestamp <strong>06 Jan 2026, 09:26 UTC</strong><span className="stale-tag">Stale demo data</span></p>
      </section>

      <section className="metric-grid" aria-label="Latest evidence summary">
        <article><span>Latest sentiment</span><strong className={sentimentTone(sentiment)}>{sentiment > 0 ? "+" : ""}{sentiment.toFixed(3)}</strong><small>Range −1 to +1</small></article>
        <article><span>Evidence coverage</span><strong>{Math.round(coverage * 100)}%</strong><small>{evidence} article{evidence === 1 ? "" : "s"} in window</small></article>
        <article><span>Leading event</span><strong className="text-metric">{humanize(latest?.leading_event ?? "")}</strong><small>Target-specific evidence</small></article>
        <article><span>Index version</span><strong className="text-metric">v{latest?.aggregation_version ?? "1.1.0"}</strong><small>Fully reproducible</small></article>
      </section>

      <section className="panel chart-panel"><div className="panel-heading"><div><p className="eyebrow">Signal timeline</p><h2>{humanize(asset)} sentiment</h2></div><p>Coverage is shown separately so a strong score never implies broad evidence.</p></div>
        {visiblePoints.length ? <SentimentChart points={visiblePoints} asset={asset} /> : <div className="empty-state">No observations match this filter.</div>}
      </section>

      <section id="drivers" className="section-block"><div className="section-title"><div><p className="eyebrow">Why the signal moved</p><h2>Event drivers</h2></div><p>Every label exposes the terms and sentences that supported it.</p></div>
        <div className="event-grid">{visibleEvents.map((event) => <EventCard event={event} key={event.prediction_id} />)}</div>
      </section>

      <section id="research" className="research-panel">
        <div><p className="eyebrow">Chronological market research</p><h2>Evidence before conclusions.</h2><p>{research.warning}</p>
          <div className="sample-count"><strong>{research.sample_count}</strong><span>aligned observations<br /><b>30 required for inference</b></span></div></div>
        <div className="research-card"><span className="warning-icon">!</span><div><strong>Inference intentionally withheld</strong><p>Permutation tests, confidence intervals, and direction accuracy are suppressed because the minimum sample requirements are not met.</p><code>{research.inference_status}</code></div></div>
      </section>

      <section id="outputs" className="outputs-section">
        <div className="section-title"><div><p className="eyebrow">Shareable, traceable outputs</p><h2>Reports and informational alerts</h2></div><p>Export permitted derived values or record a research condition—never a trading instruction.</p></div>
        <div className="output-grid">
          <article className="export-card"><span className="card-number">01</span><h3>Derived data export</h3><p>Download the versioned sentiment index without copyrighted article text.</p><button className="action-button" onClick={downloadCsv}>Download CSV</button></article>
          <article className="export-card"><span className="card-number">02</span><h3>Research report</h3><p>Open your browser print dialog and choose “Save as PDF” for a concise interview-ready snapshot.</p><button className="action-button secondary" onClick={() => window.print()}>Print / Save PDF</button></article>
        </div>
        <div className="alert-panel">
          <div className="alert-config"><p className="eyebrow">Local alert rule</p><h3>Choose the evidence conditions</h3><p>Saved only in this browser. No exchange or notification account is connected.</p>
            <label>Minimum sentiment magnitude <strong>{alertRule.sentimentMagnitude.toFixed(2)}</strong><input type="range" min="0.1" max="0.8" step="0.05" value={alertRule.sentimentMagnitude} onChange={(event) => updateAlertRule({ ...alertRule, sentimentMagnitude: Number(event.target.value) })} /></label>
            <label>Minimum evidence coverage <strong>{Math.round(alertRule.minimumCoverage * 100)}%</strong><input type="range" min="0" max="1" step="0.1" value={alertRule.minimumCoverage} onChange={(event) => updateAlertRule({ ...alertRule, minimumCoverage: Number(event.target.value) })} /></label>
            <label>Required event category<select value={alertRule.eventCategory} onChange={(event) => updateAlertRule({ ...alertRule, eventCategory: event.target.value })}><option value="">Any category</option><option value="regulation_legal">Regulation / legal</option><option value="security_incident">Security incident</option><option value="adoption_partnership">Adoption / partnership</option><option value="protocol_technical">Protocol / technical</option><option value="market_commentary">Market commentary</option></select></label>
          </div>
          <div className="alert-history"><div className="alert-heading"><div><p className="eyebrow">Evaluation result</p><h3>{alertFindings.length} condition{alertFindings.length === 1 ? "" : "s"} met</h3></div><span>Informational only</span></div>
            {alertFindings.length ? <ol>{alertFindings.map((finding) => <li key={finding.id} className={finding.severity}><i /><div><strong>{finding.title}</strong><p>{finding.explanation}</p><time>{new Date(finding.observedAt).toISOString().replace("T", " ").slice(0, 16)} UTC</time></div></li>)}</ol> : <div className="alert-empty">No observation currently meets every configured condition.</div>}
          </div>
        </div>
      </section>

      <section id="methodology" className="method-grid">
        <div><p className="eyebrow">Built for scrutiny</p><h2>Methodology at a glance</h2><p>Every transformation is versioned, tested, and traceable to its evidence.</p></div>
        <ol><li><span>01</span><div><strong>Target evidence</strong><p>Resolve Bitcoin or Ethereum before sentiment scoring.</p></div></li><li><span>02</span><div><strong>Independent weighting</strong><p>Cap duplicate stories and repeated sources.</p></div></li><li><span>03</span><div><strong>Point-in-time research</strong><p>Use only evidence processed before each signal closes.</p></div></li></ol>
      </section>

      <footer><div className="brand"><span className="brand-mark">CP</span><span>CryptoPulse AI</span></div><p>Research and decision support only. Not financial advice.</p><a href="#overview">Back to top ↑</a></footer>
    </main>
  );
}
