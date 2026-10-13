import type { BenchmarkResult } from "../../domain/entities/BenchmarkResult";

export async function fetchBenchmarkResults(): Promise<BenchmarkResult> {
  const response = await fetch("/benchmark_full.json");
  if (!response.ok) {
    throw new Error(`Failed to load benchmark results: ${response.status}`);
  }
  return response.json();
}
