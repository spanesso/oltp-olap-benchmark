import type { BenchmarkResult, QueryResult } from "../entities/BenchmarkResult";

export interface ChartDatum {
  label: string;
  question: string;
  oltp: number;
  olap: number;
  speedup: number;
}

export interface StatsSummary {
  totalQueries: number;
  dataVolume: number;
  minSpeedup: number;
  maxSpeedup: number;
  avgSpeedup: number;
  significanceReached: boolean;
}

export const ANALYTICAL = "analytical";

export function analyticalQueries(queries: QueryResult[]): QueryResult[] {
  return queries.filter((q) => q.group === ANALYTICAL);
}

export function transactionalQueries(queries: QueryResult[]): QueryResult[] {
  return queries.filter((q) => q.group !== ANALYTICAL);
}

export function getChartData(queries: QueryResult[]): ChartDatum[] {
  return analyticalQueries(queries).map((q) => ({
    label: q.id.split("_")[0],
    question: q.question,
    oltp: q.oltp.median_ms,
    olap: q.olap.median_ms,
    speedup: q.speedup,
  }));
}

export function getStatsSummary(result: BenchmarkResult): StatsSummary {
  const analytical = analyticalQueries(result.queries);
  const speedups = analytical.map((q) => q.speedup);
  const sum = speedups.reduce((a, b) => a + b, 0);
  return {
    totalQueries: analytical.length,
    dataVolume: result.dataset.rows,
    minSpeedup: Math.min(...speedups),
    maxSpeedup: Math.max(...speedups),
    avgSpeedup: speedups.length > 0 ? sum / speedups.length : 0,
    significanceReached: result.significance.reached === true,
  };
}

export function formatMs(ms: number): string {
  return `${ms.toLocaleString("en-US", { maximumFractionDigits: 1 })} ms`;
}
