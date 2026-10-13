import { useState } from "react";
import type { QueryResult } from "@domain/entities/BenchmarkResult";

interface Props {
  queries: QueryResult[];
}

export function ExplainPanel({ queries }: Props) {
  const hasPlans = queries.some((q) => q.oltp_explain || q.olap_explain);
  const [selected, setSelected] = useState(queries[0]?.id ?? "");
  const query = queries.find((q) => q.id === selected);

  if (!hasPlans) {
    return (
      <div className="explain-empty">
        No execution plans available. Re-run the benchmark to capture EXPLAIN
        ANALYZE output.
      </div>
    );
  }

  return (
    <div>
      <select
        className="explain-select"
        value={selected}
        onChange={(e) => setSelected(e.target.value)}
        aria-label="Select query to view execution plan"
      >
        {queries.map((q) => (
          <option key={q.id} value={q.id}>
            {q.id.split("_")[0]} — {q.question}
          </option>
        ))}
      </select>

      <div className="explain-grid">
        <div className="explain-block">
          <div className="explain-block-header oltp">PostgreSQL (OLTP)</div>
          {query?.oltp_explain ? (
            <pre className="explain-code">{query.oltp_explain}</pre>
          ) : (
            <div className="explain-empty">No plan captured</div>
          )}
        </div>
        <div className="explain-block">
          <div className="explain-block-header olap">DuckDB (OLAP)</div>
          {query?.olap_explain ? (
            <pre className="explain-code">{query.olap_explain}</pre>
          ) : (
            <div className="explain-empty">No plan captured</div>
          )}
        </div>
      </div>
    </div>
  );
}
