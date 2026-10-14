import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import type { QueryResult } from "@domain/entities/BenchmarkResult";

interface Props {
  queries: QueryResult[];
}

interface RunPoint {
  x: number;
  y: number;
  label: string;
}

function buildPoints(queries: QueryResult[]): { oltp: RunPoint[]; olap: RunPoint[] } {
  const oltp: RunPoint[] = [];
  const olap: RunPoint[] = [];
  queries.forEach((q, i) => {
    const label = q.id.split("_")[0];
    q.oltp.runs_ms.forEach((t) => oltp.push({ x: i + 0.85, y: t, label }));
    q.olap.runs_ms.forEach((t) => olap.push({ x: i + 1.15, y: t, label }));
  });
  return { oltp, olap };
}

function CustomDot(props: { cx?: number; cy?: number; fill?: string }) {
  const { cx = 0, cy = 0, fill } = props;
  return <circle cx={cx} cy={cy} r={3.5} fill={fill} fillOpacity={0.65} stroke="none" />;
}

export function RunDistributionChart({ queries }: Props) {
  const { oltp, olap } = buildPoints(queries);
  const ticks = queries.map((_, i) => i + 1);
  const labels = queries.map((q) => q.id.split("_")[0]);

  return (
    <div>
      <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", margin: "0 0 12px" }}>
        Each dot = one of the 10 measured runs. Y-axis is logarithmic — gaps look small but
        represent orders of magnitude.
      </p>
      <ResponsiveContainer width="100%" height={320}>
        <ScatterChart margin={{ top: 8, right: 24, bottom: 8, left: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis
            type="number"
            dataKey="x"
            domain={[0.5, queries.length + 0.5]}
            ticks={ticks}
            tickFormatter={(v: number) => labels[Math.round(v) - 1] ?? ""}
            stroke="var(--color-text-secondary)"
            fontSize={12}
          />
          <YAxis
            type="number"
            dataKey="y"
            scale="log"
            domain={["auto", "auto"]}
            tickFormatter={(v: number) => `${v >= 1000 ? `${(v / 1000).toFixed(1)}s` : `${Math.round(v)}ms`}`}
            stroke="var(--color-text-secondary)"
            fontSize={11}
            width={52}
          />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            content={({ payload }) => {
              if (!payload?.length) return null;
              const pt = payload[0].payload as RunPoint;
              return (
                <div className="custom-tooltip">
                  <p className="tooltip-question">{pt.label}</p>
                  <div className="tooltip-row">
                    <span className="tooltip-label">Time</span>
                    <span>{pt.y.toFixed(1)} ms</span>
                  </div>
                </div>
              );
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: 13 }}
            formatter={(v: string) => <span style={{ color: "var(--color-text)" }}>{v}</span>}
          />
          {/* median reference lines per query */}
          {queries.map((q, i) => (
            <ReferenceLine
              key={`oltp-med-${i}`}
              x={i + 0.85}
              stroke="var(--color-oltp)"
              strokeWidth={8}
              strokeOpacity={0.25}
              segment={[
                { x: i + 0.7, y: q.oltp.median_ms },
                { x: i + 1.0, y: q.oltp.median_ms },
              ]}
            />
          ))}
          <Scatter
            name="OLTP (PostgreSQL)"
            data={oltp}
            fill="var(--color-oltp)"
            shape={<CustomDot />}
          />
          <Scatter
            name="OLAP (DuckDB)"
            data={olap}
            fill="var(--color-olap)"
            shape={<CustomDot />}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
