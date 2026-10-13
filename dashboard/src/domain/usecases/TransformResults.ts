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

export function getChartData(queries: QueryResult[]): ChartDatum[] {
  return queries.map((q) => ({
    label: q.id.split("_")[0],
    question: q.question,
    oltp: q.oltp.median_ms,
    olap: q.olap.median_ms,
    speedup: q.speedup,
  }));
}

export function getStatsSummary(result: BenchmarkResult): StatsSummary {
  const speedups = result.queries.map((q) => q.speedup);
  const sum = speedups.reduce((a, b) => a + b, 0);
  return {
    totalQueries: result.queries.length,
    dataVolume: result.dataset.rows,
    minSpeedup: Math.min(...speedups),
    maxSpeedup: Math.max(...speedups),
    avgSpeedup: speedups.length > 0 ? sum / speedups.length : 0,
    significanceReached: result.significance.reached === true,
  };
}

export function formatMs(ms: number): string {
  if (ms >= 1000) {
    return `${ms.toLocaleString("en-US", { maximumFractionDigits: 1 })} ms`;
  }
  return `${ms.toLocaleString("en-US", { maximumFractionDigits: 1 })} ms`;
}
