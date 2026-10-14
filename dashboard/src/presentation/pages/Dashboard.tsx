import { useBenchmarkData } from "@presentation/hooks/useBenchmarkData";
import {
  getChartData,
  getStatsSummary,
  transactionalQueries,
} from "@domain/usecases/TransformResults";
import { useExperiments } from "@presentation/hooks/useExperiments";
import { StatTile } from "@presentation/components/StatTile";
import { SpeedupChart } from "@presentation/components/SpeedupChart";
import { QueryTable } from "@presentation/components/QueryTable";
import { EnvironmentCard } from "@presentation/components/EnvironmentCard";
import { PipelineDiagram } from "@presentation/components/PipelineDiagram";
import { ExplainPanel } from "@presentation/components/ExplainPanel";
import { LiveRunButton } from "@presentation/components/LiveRunButton";
import { AbsoluteTimingChart } from "@presentation/components/AbsoluteTimingChart";
import { SpeedupRadarChart } from "@presentation/components/SpeedupRadarChart";
import { BoroughMap } from "@presentation/components/BoroughMap";
import { SchemaViewer } from "@presentation/components/SchemaViewer";
import { ExperimentsPanel } from "@presentation/components/ExperimentsPanel";
import { TransactionalTable } from "@presentation/components/TransactionalTable";
import { ApiColumnsTable } from "@presentation/components/ApiColumnsTable";
import { LanguageToggle } from "@presentation/components/LanguageToggle";
import { useI18n } from "@/i18n";

const WHY_ITEMS = [
  { labelKey: "intro_why_volume_label", textKey: "intro_why_volume" },
  { labelKey: "intro_why_dims_label",   textKey: "intro_why_dims"   },
  { labelKey: "intro_why_api_label",    textKey: "intro_why_api"    },
  { labelKey: "intro_why_time_label",   textKey: "intro_why_time"   },
] as const;

export function Dashboard() {
  const { data, loading, error, running, runError, triggerLiveRun } = useBenchmarkData();
  const { t } = useI18n();
  const experiments = useExperiments();

  if (loading) {
    return <div className="loading">Loading benchmark results&hellip;</div>;
  }

  if (error || !data) {
    return <div className="error-msg">{error ?? "No data available"}</div>;
  }

  const chartData = getChartData(data.queries);
  const stats = getStatsSummary(data);
  const transactional = transactionalQueries(data.queries);

  return (
    <div className="dashboard">
      {/* ── Header ── */}
      <header className="dashboard-header">
        <div>
          <h1>{t("header_title")}</h1>
          <p>
            {data.dataset.source} &mdash;{" "}
            {data.dataset.rows.toLocaleString()} {t("header_rows")} &mdash; {data.profile}{" "}
            {t("header_profile")}
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <LanguageToggle />
          <LiveRunButton running={running} onRun={triggerLiveRun} runError={runError} />
        </div>
      </header>

      {/* ── Stats ── */}
      <div className="stats-row">
        <StatTile label={t("stat_queries")} value={stats.totalQueries} />
        <StatTile label={t("stat_volume")} value={stats.dataVolume} unit={t("stat_volume_unit")} />
        <StatTile
          label={t("stat_min_speedup")}
          value={`${stats.minSpeedup.toFixed(1)}x`}
          accent="var(--color-speedup)"
        />
        <StatTile
          label={t("stat_max_speedup")}
          value={`${stats.maxSpeedup.toFixed(1)}x`}
          accent="var(--color-speedup)"
        />
        <StatTile
          label={t("stat_significance")}
          value={stats.significanceReached ? t("stat_reached") : t("stat_not_reached")}
          accent={stats.significanceReached ? "var(--color-olap)" : "var(--color-oltp)"}
        />
      </div>

      {/* ── 1. Introduction ── */}
      <section className="section">
        <h2 className="section-title">{t("intro_title")}</h2>
        <div style={{ maxWidth: 780, lineHeight: 1.7, color: "var(--color-text-secondary)" }}>
          <p style={{ marginBottom: 12 }}>{t("intro_p1")}</p>
          <p style={{ marginBottom: 16 }}>{t("intro_p2")}</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
            {WHY_ITEMS.map(({ labelKey, textKey }) => (
              <div
                key={labelKey}
                style={{
                  background: "var(--color-surface)",
                  border: "1px solid var(--border)",
                  borderRadius: 8,
                  padding: "12px 16px",
                }}
              >
                <div style={{ fontWeight: 700, color: "var(--color-speedup)", marginBottom: 4, fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                  {t(labelKey)}
                </div>
                <div style={{ fontSize: "0.9rem" }}>{t(textKey)}</div>
              </div>
            ))}
          </div>

          {/* ── API URL + params ── */}
          <div style={{ marginTop: 24 }}>
            <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>
              {t("intro_api_endpoint")}
            </div>
            <pre style={{
              background: "var(--color-surface)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              padding: "14px 16px",
              fontSize: "0.78rem",
              overflowX: "auto",
              lineHeight: 1.7,
              margin: 0,
            }}>{`GET https://data.cityofnewyork.us/resource/erm2-nwe9.json
  ?$select=unique_key,created_date,closed_date,agency,agency_name,
           complaint_type,descriptor,borough,incident_zip,
           community_board,open_data_channel_type,status
  &$where=created_date >= '2024-01-01' AND created_date < '2026-01-01'
  &$order=created_date, unique_key
  &$limit=50000
X-App-Token: <SOCRATA_APP_TOKEN>`}</pre>
            <p style={{ fontSize: "0.8rem", marginTop: 8, color: "var(--color-text-secondary)" }}>
              {t("intro_api_pagination")}
            </p>
          </div>

          {/* ── JSON record example ── */}
          <div style={{ marginTop: 20 }}>
            <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>
              {t("intro_json_example")}
            </div>
            <pre style={{
              background: "var(--color-surface)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              padding: "14px 16px",
              fontSize: "0.78rem",
              overflowX: "auto",
              lineHeight: 1.7,
              margin: 0,
            }}>{`{
  "unique_key":             "62458321",
  "created_date":           "2024-03-15T10:30:00.000",
  "closed_date":            "2024-03-17T14:00:00.000",
  "agency":                 "NYPD",
  "agency_name":            "New York City Police Dept",
  "complaint_type":         "Noise - Residential",
  "descriptor":             "Loud Music/Party",
  "borough":                "BROOKLYN",
  "incident_zip":           "11201",
  "community_board":        "01 BROOKLYN",
  "open_data_channel_type": "PHONE",
  "status":                 "Closed"
}`}</pre>
          </div>
        </div>
      </section>

      {/* ── 2. API columns ── */}
      <section className="section">
        <h2 className="section-title">{t("api_columns_title")}</h2>
        <ApiColumnsTable />
      </section>

      {/* ── 3. Schema diagrams ── */}
      <section className="section">
        <h2 className="section-title">{t("schema_title")}</h2>
        <SchemaViewer />
      </section>

      {/* ── 4. Pipeline ── */}
      <section className="section">
        <h2 className="section-title">{t("section_pipeline")}</h2>
        <PipelineDiagram />
      </section>

      {/* ── 5. Speedup chart ── */}
      <section className="section">
        <h2 className="section-title">{t("section_speedup")}</h2>
        <SpeedupChart data={chartData} />
      </section>

      {/* ── 6. Results table ── */}
      <section className="section">
        <h2 className="section-title">{t("section_results")}</h2>
        <QueryTable data={chartData} />
      </section>

      {/* ── Transactional operations (only when they were measured) ── */}
      {transactional.length > 0 && (
        <section className="section">
          <h2 className="section-title">{t("tx_title")}</h2>
          <TransactionalTable operations={transactional} />
        </section>
      )}

      {/* ── Schema vs engine experiments (only when the experiments ran) ── */}
      {experiments && (
        <section className="section">
          <h2 className="section-title">{t("section_experiments")}</h2>
          <ExperimentsPanel report={experiments} />
        </section>
      )}

      {/* ── 7. Absolute timing ── */}
      <section className="section">
        <h2 className="section-title">{t("section_absolute")}</h2>
        <AbsoluteTimingChart queries={data.queries} />
      </section>

      {/* ── 8. Radar ── */}
      <section className="section">
        <h2 className="section-title">{t("section_radar")}</h2>
        <SpeedupRadarChart queries={data.queries} />
      </section>

      {/* ── 9. Borough map ── */}
      <section className="section">
        <h2 className="section-title">{t("section_map")}</h2>
        <BoroughMap />
      </section>

      {/* ── 10. Execution plans ── */}
      <section className="section">
        <h2 className="section-title">{t("section_explain")}</h2>
        <ExplainPanel queries={data.queries} />
      </section>

      {/* ── 11. Environment ── */}
      <section className="section">
        <h2 className="section-title">{t("section_env")}</h2>
        <EnvironmentCard environment={data.environment} />
      </section>

      <footer style={{ textAlign: "center", padding: "24px 0 32px", color: "var(--color-text-secondary)", fontSize: "0.75rem" }}>
        {t("footer_generated")} {new Date(data.generated_at).toLocaleDateString()} &mdash;{" "}
        {data.method.measured_runs} {t("footer_runs")}, {data.method.warmup_runs}{" "}
        {t("footer_warmup")}
      </footer>
    </div>
  );
}
