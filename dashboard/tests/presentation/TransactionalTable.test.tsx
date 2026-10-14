import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import { TransactionalTable } from "../../src/presentation/components/TransactionalTable";
import type { QueryResult } from "../../src/domain/entities/BenchmarkResult";
import { renderWithI18n } from "../utils";

const timing = (ms: number) => ({
  runs_ms: [ms],
  median_ms: ms,
  p95_ms: ms,
  min_ms: ms,
  max_ms: ms,
});

const operation = (id: string, oltpMs: number, olapMs: number): QueryResult => ({
  id,
  group: "transactional",
  question: `Question for ${id}`,
  result_rows: 1,
  oltp: timing(oltpMs),
  olap: timing(olapMs),
  speedup: oltpMs / olapMs,
});

describe("TransactionalTable", () => {
  it("lists each operation with both timings", () => {
    renderWithI18n(<TransactionalTable operations={[operation("t1_lookup_by_id", 0.4, 12)]} />);
    expect(screen.getByText("t1")).toBeInTheDocument();
    expect(screen.getByText("0.40")).toBeInTheDocument();
    expect(screen.getByText("12.00")).toBeInTheDocument();
  });

  it("names OLTP as the winner when it is faster", () => {
    renderWithI18n(<TransactionalTable operations={[operation("t1_lookup_by_id", 1, 20)]} />);
    expect(screen.getByText("OLTP wins, 20x")).toBeInTheDocument();
  });

  it("names OLAP as the winner when it is faster", () => {
    renderWithI18n(<TransactionalTable operations={[operation("t2_insert_request", 8, 2)]} />);
    expect(screen.getByText("OLAP wins, 4x")).toBeInTheDocument();
  });

  it("is translated", () => {
    renderWithI18n(<TransactionalTable operations={[operation("t1_lookup_by_id", 1, 20)]} />, "es");
    expect(screen.getByText("Gana OLTP, 20x")).toBeInTheDocument();
  });
});
