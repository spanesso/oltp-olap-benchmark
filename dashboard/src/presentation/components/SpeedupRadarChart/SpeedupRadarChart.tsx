import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import type { QueryResult } from "@domain/entities/BenchmarkResult";

interface Props {
  queries: QueryResult[];
}

export function SpeedupRadarChart({ queries }: Props) {
  const data = queries.map((q) => ({
    query: q.id.split("_")[0].toUpperCase(),
    Speedup: Math.round(q.speedup * 10) / 10,
    Threshold: 3,
  }));

  const maxSpeedup = Math.max(...queries.map((q) => q.speedup));
  const outerLimit = Math.ceil(maxSpeedup / 50) * 50;

  return (
    <div>
      <p style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)", margin: "0 0 12px" }}>
        Each axis = one analytical query. The dashed inner polygon is the 3× significance
        threshold. All 6 queries exceed it by a wide margin.
      </p>
      <ResponsiveContainer width="100%" height={360}>
        <RadarChart data={data} cx="50%" cy="50%" outerRadius="72%">
          <PolarGrid stroke="var(--color-border)" />
          <PolarAngleAxis
            dataKey="query"
            tick={{ fill: "var(--color-text-secondary)", fontSize: 13, fontWeight: 600 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, outerLimit]}
            tickCount={5}
            tick={{ fill: "var(--color-text-secondary)", fontSize: 10 }}
            tickFormatter={(v: number) => `${v}×`}
          />
          <Tooltip
            content={({ payload }) => {
              if (!payload?.length) return null;
              const d = payload[0].payload as { query: string; Speedup: number };
              return (
                <div className="custom-tooltip">
                  <div className="tooltip-row">
                    <span className="tooltip-label">{d.query}</span>
                    <span style={{ color: "var(--color-olap)", fontWeight: 600 }}>
                      {d.Speedup}×
                    </span>
                  </div>
                </div>
              );
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: 13 }}
            formatter={(v: string) => <span style={{ color: "var(--color-text)" }}>{v}</span>}
          />
          <Radar
            name="Significance threshold (3×)"
            dataKey="Threshold"
            stroke="var(--color-oltp)"
            strokeDasharray="5 3"
            fill="var(--color-oltp)"
            fillOpacity={0.08}
            dot={false}
          />
          <Radar
            name="OLAP speedup"
            dataKey="Speedup"
            stroke="var(--color-olap)"
            fill="var(--color-olap)"
            fillOpacity={0.25}
            dot={{ fill: "var(--color-olap)", r: 4 }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
