import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface ChartRow {
  label: string;
  question: string;
  oltp: number;
  olap: number;
  speedup: number;
}

interface Props {
  data: ChartRow[];
}

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: ChartRow }>;
}) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className="custom-tooltip">
      <p className="tooltip-question">{row.question}</p>
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
}

export function SpeedupChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={360}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 4, right: 24, bottom: 4, left: 40 }}
      >
        <CartesianGrid
          strokeDasharray="3 3"
          stroke="var(--color-border)"
          horizontal={false}
        />
        <XAxis
          type="number"
          scale="log"
          domain={["auto", "auto"]}
          tickFormatter={(v: number) => `${v.toLocaleString()} ms`}
          stroke="var(--color-text-secondary)"
          fontSize={12}
        />
        <YAxis
          type="category"
          dataKey="label"
          width={36}
          stroke="var(--color-text-secondary)"
          fontSize={12}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: 13 }}
          formatter={(value: string) => (
            <span style={{ color: "var(--color-text)" }}>{value}</span>
          )}
        />
        <Bar
          dataKey="oltp"
          name="OLTP (PostgreSQL)"
          fill="var(--color-oltp)"
          radius={[0, 4, 4, 0]}
        />
        <Bar
          dataKey="olap"
          name="OLAP (DuckDB)"
          fill="var(--color-olap)"
          radius={[0, 4, 4, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
