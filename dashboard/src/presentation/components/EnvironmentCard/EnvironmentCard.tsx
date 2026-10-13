interface EnvironmentInfo {
  os: string;
  cpu: string;
  cores: number;
  memory_gb: number;
  python: string;
  postgresql: string;
  postgresql_runtime: string;
  postgresql_settings: Record<string, string>;
  duckdb: string;
  duckdb_runtime: string;
  duckdb_settings: Record<string, string>;
}

interface Props {
  environment: EnvironmentInfo;
}

export function EnvironmentCard({ environment }: Props) {
  return (
    <div>
      <p style={{ fontSize: "0.8125rem", color: "var(--color-text-secondary)", margin: "0 0 16px" }}>
        {environment.cpu}, {environment.cores} cores, {environment.memory_gb} GB RAM
        &mdash; Python {environment.python}
      </p>
      <div className="env-grid">
        <div className="env-panel">
          <h3 style={{ color: "var(--color-oltp)" }}>
            PostgreSQL {environment.postgresql.split(" ")[0]}
          </h3>
          <dl>
            <dt>Runtime</dt>
            <dd>{environment.postgresql_runtime}</dd>
            {Object.entries(environment.postgresql_settings).map(([key, val]) => (
              <dl key={key} style={{ display: "contents" }}>
                <dt>{key}</dt>
                <dd>{val}</dd>
              </dl>
            ))}
          </dl>
        </div>
        <div className="env-panel">
          <h3 style={{ color: "var(--color-olap)" }}>
            DuckDB {environment.duckdb}
          </h3>
          <dl>
            <dt>Runtime</dt>
            <dd>{environment.duckdb_runtime}</dd>
            {Object.entries(environment.duckdb_settings).map(([key, val]) => (
              <dl key={key} style={{ display: "contents" }}>
                <dt>{key}</dt>
                <dd>{val}</dd>
              </dl>
            ))}
          </dl>
        </div>
      </div>
    </div>
  );
}
