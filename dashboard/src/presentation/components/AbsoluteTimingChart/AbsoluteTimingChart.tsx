import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { QueryResult } from "@domain/entities/BenchmarkResult";

interface Props {
  queries: QueryResult[];
}

interface Row {
  label: string;
  question: string;
  oltp: number;
  olap: number;
  speedup: number;
}

export function AbsoluteTimingChart({ queries }: Props) {
  const data: Row[] = queries.map((q) => ({
    label: q.id.split("_")[0],
    question: q.question,
    oltp: Math.round(q.oltp.median_ms),
    olap: Math.round(q.olap.median_ms),
    speedup: q.speedup,
  }));

  return (
    <div>
      <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", margin: "0 0 12px" }}>
        Median execution time in milliseconds (linear scale). The visual gap makes the speedup
        tangible: OLAP bars are nearly invisible next to the OLTP ones.
      </p>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 8, right: 24, bottom: 8, left: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
          <XAxis
            dataKey="label"
            stroke="var(--color-text-secondary)"
            fontSize={12}
          />
          <YAxis
            tickFormatter={(v: number) => `${v.toLocaleString()} ms`}
            stroke="var(--color-text-secondary)"
            fontSize={11}
            width={76}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const row = payload[0].payload as Row;
              return (
                <div className="custom-tooltip">
                  <p className="tooltip-question">{row.label.toUpperCase()}</p>
                  <p style={{ fontSize: "0.75rem", margin: "0 0 6px", color: "var(--color-text-secondary)" }}>
                    {row.question}
                  </p>
                  <div className="tooltip-row">
                    <span className="tooltip-label">OLTP</span>
                    <span>{row.oltp.toLocaleString()} ms</span>
                  </div>
                  <div className="tooltip-row">
                    <span className="tooltip-label">OLAP</span>
                    <span>{row.olap.toLocaleString()} ms</span>
                  </div>
                  <div className="tooltip-speedup">{row.speedup.toFixed(1)}x faster</div>
                </div>
              );
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: 13 }}
            formatter={(v: string) => <span style={{ color: "var(--color-text)" }}>{v}</span>}
          />
          <Bar dataKey="oltp" name="OLTP (PostgreSQL)" fill="var(--color-oltp)" radius={[4, 4, 0, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill="var(--color-oltp)" fillOpacity={0.85} />
            ))}
          </Bar>
          <Bar dataKey="olap" name="OLAP (DuckDB)" fill="var(--color-olap)" radius={[4, 4, 0, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill="var(--color-olap)" fillOpacity={0.85} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
