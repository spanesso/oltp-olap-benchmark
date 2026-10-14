const STEPS = [
  { label: "NYC 311 API", sub: "Socrata" },
  { label: "Staging", sub: "PostgreSQL" },
  { label: "OLTP Model", sub: "3NF, 8 tables" },
  { label: "OLAP Model", sub: "Star schema, DuckDB" },
  { label: "Benchmark", sub: "6 queries, 10 runs" },
  { label: "Results", sub: "JSON + Markdown" },
];

export function PipelineDiagram() {
  return (
    <div className="pipeline" role="img" aria-label="Data pipeline from API to results">
      {STEPS.map((step, i) => (
        <div key={step.label} style={{ display: "contents" }}>
          {i > 0 && <span className="pipeline-arrow" aria-hidden="true">&#x2192;</span>}
          <div className="pipeline-step">
            <span className="pipeline-step-label">{step.label}</span>
            <span className="pipeline-step-sub">{step.sub}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
