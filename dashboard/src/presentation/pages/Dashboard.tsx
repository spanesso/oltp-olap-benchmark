import { useBenchmarkData } from "@presentation/hooks/useBenchmarkData";
import { getChartData, getStatsSummary } from "@domain/usecases/TransformResults";
import { StatTile } from "@presentation/components/StatTile";
import { SpeedupChart } from "@presentation/components/SpeedupChart";
import { QueryTable } from "@presentation/components/QueryTable";
import { EnvironmentCard } from "@presentation/components/EnvironmentCard";
import { PipelineDiagram } from "@presentation/components/PipelineDiagram";
import { ExplainPanel } from "@presentation/components/ExplainPanel";

export function Dashboard() {
  const { data, loading, error } = useBenchmarkData();

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
      <header className="dashboard-header">
        <h1>OLTP vs OLAP Benchmark</h1>
        <p>
          {data.dataset.source} &mdash;{" "}
          {data.dataset.rows.toLocaleString()} rows &mdash; {data.profile}{" "}
          profile
        </p>
      </header>

      <div className="stats-row">
        <StatTile label="Queries" value={stats.totalQueries} />
        <StatTile label="Data volume" value={stats.dataVolume} unit="rows" />
        <StatTile
          label="Min speedup"
          value={`${stats.minSpeedup.toFixed(1)}x`}
          accent="var(--color-speedup)"
        />
        <StatTile
          label="Max speedup"
          value={`${stats.maxSpeedup.toFixed(1)}x`}
          accent="var(--color-speedup)"
        />
        <StatTile
          label="Significance"
          value={stats.significanceReached ? "Reached" : "Not reached"}
          accent={
            stats.significanceReached ? "var(--color-olap)" : "var(--color-oltp)"
          }
        />
      </div>

      <section className="section">
        <h2 className="section-title">Pipeline</h2>
        <PipelineDiagram />
      </section>

      <section className="section">
        <h2 className="section-title">Speedup by query (log scale)</h2>
        <SpeedupChart data={chartData} />
      </section>

      <section className="section">
        <h2 className="section-title">Detailed results</h2>
        <QueryTable data={chartData} />
      </section>

      <section className="section">
        <h2 className="section-title">Execution plans</h2>
        <ExplainPanel queries={data.queries} />
      </section>

      <section className="section">
        <h2 className="section-title">Environment</h2>
        <EnvironmentCard environment={data.environment} />
      </section>

      <footer style={{ textAlign: "center", padding: "24px 0 32px", color: "var(--color-text-secondary)", fontSize: "0.75rem" }}>
        Generated {new Date(data.generated_at).toLocaleDateString()} &mdash;{" "}
        {data.method.measured_runs} measured runs, {data.method.warmup_runs}{" "}
        warmup
      </footer>
    </div>
  );
}
