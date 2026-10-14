import { describe, it, expect } from "vitest";
import {
  analyticalQueries,
  getChartData,
  getStatsSummary,
  formatMs,
  transactionalQueries,
} from "../../src/domain/usecases/TransformResults";
import type {
  BenchmarkResult,
  QueryResult,
} from "../../src/domain/entities/BenchmarkResult";

const timing = (median: number) => ({
  runs_ms: [median],
  median_ms: median,
  p95_ms: median * 1.05,
  min_ms: median * 0.95,
  max_ms: median * 1.1,
});

const makeQuery = (id: string, oltpMs: number, olapMs: number): QueryResult => ({
  id,
  group: "analytical",
  question: `Question for ${id}`,
  result_rows: 100,
  oltp: timing(oltpMs),
  olap: timing(olapMs),
  speedup: oltpMs / olapMs,
});

const mockResult: BenchmarkResult = {
  schema_version: 1,
  profile: "full",
  official: true,
  generated_at: "2026-10-13T01:00:00Z",
  dataset: {
    source: "NYC 311",
    rows: 5_000_000,
    first_created_at: "2024-01-01T00:00:00",
    last_created_at: "2025-06-10T09:03:00",
  },
  environment: {
    os: "macOS",
    cpu: "arm",
    cores: 10,
    memory_gb: 16,
    python: "3.13.9",
    postgresql: "17.11",
    postgresql_runtime: "docker",
    postgresql_settings: { shared_buffers: "128MB" },
    duckdb: "1.5.6",
    duckdb_runtime: "embedded",
    duckdb_settings: { threads: "10" },
  },
  method: { warmup_runs: 1, measured_runs: 10, timer: "perf_counter" },
  queries: [
    makeQuery("q1_volume_by_type", 2400, 30),
    makeQuery("q2_top_types_per_zip", 1200, 20),
  ],
  significance: {
    evaluated: true,
    rule: "OLAP 3x in 2/3",
    queries_meeting_3x: 2,
    analytical_queries: 2,
    reached: true,
  },
};

describe("getChartData", () => {
  it("extracts short labels from query ids", () => {
    const data = getChartData(mockResult.queries);
    expect(data).toHaveLength(2);
    expect(data[0].label).toBe("q1");
    expect(data[1].label).toBe("q2");
  });

  it("maps median times and speedup", () => {
    const data = getChartData(mockResult.queries);
    expect(data[0].oltp).toBe(2400);
    expect(data[0].olap).toBe(30);
    expect(data[0].speedup).toBe(80);
  });

  it("preserves the question text", () => {
    const data = getChartData(mockResult.queries);
    expect(data[0].question).toBe("Question for q1_volume_by_type");
  });

  it("returns an empty array for empty input", () => {
    expect(getChartData([])).toEqual([]);
  });
});

describe("getStatsSummary", () => {
  it("computes min, max and average speedup", () => {
    const stats = getStatsSummary(mockResult);
    expect(stats.totalQueries).toBe(2);
    expect(stats.dataVolume).toBe(5_000_000);
    expect(stats.minSpeedup).toBe(60);
    expect(stats.maxSpeedup).toBe(80);
    expect(stats.avgSpeedup).toBe(70);
    expect(stats.significanceReached).toBe(true);
  });

  it("handles significance not reached", () => {
    const modified = {
      ...mockResult,
      significance: { ...mockResult.significance, reached: false },
    };
    expect(getStatsSummary(modified).significanceReached).toBe(false);
  });

  it("handles null significance", () => {
    const modified = {
      ...mockResult,
      significance: { ...mockResult.significance, reached: null },
    };
    expect(getStatsSummary(modified).significanceReached).toBe(false);
  });
});

describe("formatMs", () => {
  it("formats large numbers with separators", () => {
    const result = formatMs(2373.8);
    expect(result).toContain("2");
    expect(result).toContain("ms");
  });

  it("formats small numbers", () => {
    const result = formatMs(5.5);
    expect(result).toContain("5.5");
    expect(result).toContain("ms");
  });

  it("handles zero", () => {
    expect(formatMs(0)).toContain("0");
  });
});

describe("transactional operations", () => {
  const lookup: QueryResult = {
    ...makeQuery("t1_lookup_by_id", 0.5, 4),
    group: "transactional",
  };
  const mixed = [...mockResult.queries, lookup];

  it("splits the queries by group", () => {
    expect(analyticalQueries(mixed)).toHaveLength(2);
    expect(transactionalQueries(mixed)).toEqual([lookup]);
  });

  it("keeps transactional operations out of the chart data", () => {
    expect(getChartData(mixed).map((row) => row.label)).toEqual(["q1", "q2"]);
  });

  it("does not let a transactional speedup below 1 distort the summary", () => {
    const summary = getStatsSummary({ ...mockResult, queries: mixed });
    expect(summary.totalQueries).toBe(2);
    expect(summary.minSpeedup).toBe(60);
  });
});
