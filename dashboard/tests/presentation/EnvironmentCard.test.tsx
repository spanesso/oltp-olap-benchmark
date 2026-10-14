import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { EnvironmentCard } from "../../src/presentation/components/EnvironmentCard";
import type { Environment } from "../../src/domain/entities/BenchmarkResult";

const environment: Environment = {
  os: "macOS",
  cpu: "Apple M1 Pro",
  cores: 10,
  memory_gb: 16,
  python: "3.13.9",
  postgresql: "17.11 on aarch64",
  postgresql_runtime: "Docker container",
  postgresql_settings: { shared_buffers: "128MB", work_mem: "4MB" },
  duckdb: "1.5.6",
  duckdb_runtime: "embedded",
  duckdb_settings: { threads: "10" },
};

describe("EnvironmentCard", () => {
  it("summarizes the machine", () => {
    render(<EnvironmentCard environment={environment} />);
    expect(screen.getByText(/Apple M1 Pro, 10 cores, 16 GB RAM/)).toBeInTheDocument();
  });

  it("lists the settings of both engines", () => {
    render(<EnvironmentCard environment={environment} />);
    expect(screen.getByText("shared_buffers")).toBeInTheDocument();
    expect(screen.getByText("128MB")).toBeInTheDocument();
    expect(screen.getByText("threads")).toBeInTheDocument();
  });

  it("names each engine with its version", () => {
    render(<EnvironmentCard environment={environment} />);
    expect(screen.getByText("PostgreSQL 17.11")).toBeInTheDocument();
    expect(screen.getByText("DuckDB 1.5.6")).toBeInTheDocument();
  });
});
