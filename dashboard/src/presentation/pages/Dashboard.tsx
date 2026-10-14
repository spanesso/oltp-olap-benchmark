import { useBenchmarkData } from "@presentation/hooks/useBenchmarkData";
import { getChartData, getStatsSummary } from "@domain/usecases/TransformResults";
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

  if (loading) {
    return <div className="loading">Loading benchmark results&hellip;</div>;
  }

  if (error || !data) {
    return <div className="error-msg">{error ?? "No data available"}</div>;
  }

  const chartData = getChartData(data.queries);
  const stats = getStatsSummary(data);

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
