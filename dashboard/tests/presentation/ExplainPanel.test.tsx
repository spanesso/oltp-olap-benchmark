import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ExplainPanel } from "../../src/presentation/components/ExplainPanel";
import type { QueryResult } from "../../src/domain/entities/BenchmarkResult";

const timing = (ms: number) => ({
  runs_ms: [ms],
  median_ms: ms,
  p95_ms: ms,
  min_ms: ms,
  max_ms: ms,
});

const withPlans: QueryResult[] = [
  {
    id: "q1_volume",
    group: "analytical",
    question: "How many?",
    result_rows: 100,
    oltp: timing(2400),
    olap: timing(30),
    speedup: 80,
    oltp_explain: "Seq Scan on service_request",
    olap_explain: "UNGROUPED_AGGREGATE",
  },
  {
    id: "q2_top",
    group: "analytical",
    question: "Top types?",
    result_rows: 50,
    oltp: timing(1200),
    olap: timing(20),
    speedup: 60,
    oltp_explain: "Hash Join",
    olap_explain: "HASH_GROUP_BY",
  },
];

const withoutPlans: QueryResult[] = [
  {
    id: "q1_volume",
    group: "analytical",
    question: "How many?",
    result_rows: 100,
    oltp: timing(2400),
    olap: timing(30),
    speedup: 80,
  },
];

describe("ExplainPanel", () => {
  it("shows empty message when no plans are available", () => {
    render(<ExplainPanel queries={withoutPlans} />);
    expect(screen.getByText(/No execution plans available/)).toBeInTheDocument();
  });

  it("renders explain plans for the selected query", () => {
    render(<ExplainPanel queries={withPlans} />);
    expect(screen.getByText("Seq Scan on service_request")).toBeInTheDocument();
    expect(screen.getByText("UNGROUPED_AGGREGATE")).toBeInTheDocument();
  });

  it("switches query via the select dropdown", async () => {
    const user = userEvent.setup();
    render(<ExplainPanel queries={withPlans} />);
    const select = screen.getByRole("combobox");
    await user.selectOptions(select, "q2_top");
    expect(screen.getByText("Hash Join")).toBeInTheDocument();
    expect(screen.getByText("HASH_GROUP_BY")).toBeInTheDocument();
  });

  it("shows OLTP and OLAP headers", () => {
    render(<ExplainPanel queries={withPlans} />);
    expect(screen.getByText("PostgreSQL (OLTP)")).toBeInTheDocument();
    expect(screen.getByText("DuckDB (OLAP)")).toBeInTheDocument();
  });
});
