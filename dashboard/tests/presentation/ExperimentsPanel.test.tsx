import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import { ExperimentsPanel } from "../../src/presentation/components/ExperimentsPanel";
import type { ExperimentsReport } from "../../src/domain/entities/Experiments";
import { renderWithI18n } from "../utils";

const spread = (median: number) => ({
  medians_ms: [median],
  median_ms: median,
  min_ms: median,
  max_ms: median,
  cv_percent: 4.2,
  range_percent: 9.1,
});
const ratio = (median: number) => ({ median, min: median - 1, max: median + 1 });

const report: ExperimentsReport = {
  schema_version: 1,
  profile: "full",
  generated_at: "2026-10-14T18:00:00Z",
  method: { repeats: 3, warmup_runs: 1, measured_runs: 10 },
  cells: [
    { key: "normalized_postgres", label: "Normalized on PostgreSQL", engine: "postgres", schema: "normalized" },
    { key: "star_duckdb", label: "Star on DuckDB", engine: "duckdb", schema: "star" },
  ],
  queries: [
    {
      id: "q1_volume_by_type_month_borough",
      question: "How many?",
      result_rows: 10,
      cells: { normalized_postgres: spread(2500), star_duckdb: spread(40) },
      effects: {
        engine_on_normalized: ratio(45),
        engine_on_star: ratio(24),
        schema_on_postgres: ratio(2.7),
        schema_on_duckdb: ratio(1.4),
        combined: ratio(62),
      },
    },
  ],
  repeatability: { limit_percent: 20, series: 24, within_limit: 20, worst: 63.4 },
};

describe("ExperimentsPanel", () => {
  it("shows the effect of each factor for every query", () => {
    renderWithI18n(<ExperimentsPanel report={report} />);
    expect(screen.getByText("45x")).toBeInTheDocument();
    expect(screen.getByText("2.7x")).toBeInTheDocument();
    expect(screen.getByText("62x")).toBeInTheDocument();
  });

  it("shows the minimum and maximum next to each ratio", () => {
    renderWithI18n(<ExperimentsPanel report={report} />);
    expect(screen.getByText("44–46")).toBeInTheDocument();
  });

  it("shows the median time of each model", () => {
    renderWithI18n(<ExperimentsPanel report={report} />);
    expect(screen.getByText("Normalized on PostgreSQL")).toBeInTheDocument();
    expect(screen.getByText("2,500.0")).toBeInTheDocument();
    expect(screen.getByText("40.0")).toBeInTheDocument();
  });

  it("states how repeatable the measurements were", () => {
    renderWithI18n(<ExperimentsPanel report={report} />);
    expect(
      screen.getByText(/20 of 24 series stayed within 20% across 3 repetitions/),
    ).toBeInTheDocument();
  });

  it("is translated", () => {
    renderWithI18n(<ExperimentsPanel report={report} />, "es");
    expect(screen.getByText("Motor (normalizado)")).toBeInTheDocument();
  });
});
